"""IEEE SB MITS – Event Checklist Tracker (Flask + SQLite)."""
import os
import secrets
import sqlite3
import time
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, g, jsonify, request, session, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash

from checklists import EVENT_TYPES, MODES, PHASES, build_checklist

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)
DB_PATH = os.environ.get("DB_PATH", os.path.join(INSTANCE_DIR, "tracker.db"))

SOCIETIES = [
    ("sscs", "IEEE SSCS SBC MITS", "Solid-State Circuits Society", "#0ea5e9"),
    ("wie", "IEEE WIE AG MITS", "Women in Engineering", "#a855f7"),
    ("cass", "IEEE CASS SBC MITS", "Circuits and Systems Society", "#f59e0b"),
    ("ras", "IEEE RAS SBC MITS", "Robotics and Automation Society", "#10b981"),
    ("pes", "IEEE PES SBC MITS", "Power & Energy Society", "#ef4444"),
    ("cs", "IEEE CS SBC MITS", "Computer Society", "#6366f1"),
]
SECRETARY = ("secretary", "IEEE SB MITS", "Student Branch Overview", "#00629b")

app = Flask(__name__, static_folder="static", static_url_path="/static")


def _secret_key():
    env = os.environ.get("SECRET_KEY")
    if env:
        return env
    path = os.path.join(INSTANCE_DIR, "secret.key")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    with open(path) as f:
        return f.read().strip()


app.config.update(
    SECRET_KEY=_secret_key(),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)

# ------------------------------------------------------------------ database
SCHEMA = """
CREATE TABLE IF NOT EXISTS societies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  subtitle TEXT,
  color TEXT,
  password_hash TEXT NOT NULL,
  is_secretary INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  society_id INTEGER NOT NULL REFERENCES societies(id),
  title TEXT NOT NULL,
  type TEXT NOT NULL,
  mode TEXT NOT NULL,
  event_date TEXT NOT NULL,
  venue TEXT,
  notes TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  phase TEXT NOT NULL,
  title TEXT NOT NULL,
  offset_days INTEGER,
  due_date TEXT,
  done INTEGER NOT NULL DEFAULT 0,
  done_at TEXT,
  custom INTEGER NOT NULL DEFAULT 0,
  position INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  author TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_event ON tasks(event_id);
CREATE INDEX IF NOT EXISTS idx_events_soc ON events(society_id);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    existing = {r[0] for r in db.execute("SELECT slug FROM societies")}
    created = []
    for slug, name, sub, color in SOCIETIES + [SECRETARY]:
        if slug in existing:
            # keep names/colours in sync with this file (passwords are untouched)
            db.execute("UPDATE societies SET name=?, subtitle=?, color=? WHERE slug=?", (name, sub, color, slug))
            continue
        is_sec = 1 if slug == "secretary" else 0
        pw = os.environ.get(f"PASSWORD_{slug.upper()}") or secrets.token_urlsafe(8)
        db.execute(
            "INSERT INTO societies (slug,name,subtitle,color,password_hash,is_secretary) "
            "VALUES (?,?,?,?,?,?)",
            (slug, name, sub, color, generate_password_hash(pw), is_sec),
        )
        created.append((name, pw))
    db.commit()
    db.close()
    if created:
        path = os.path.join(INSTANCE_DIR, "credentials.txt")
        with open(path, "a") as f:
            f.write(f"# Generated {datetime.now():%Y-%m-%d %H:%M}\n")
            for name, pw in created:
                f.write(f"{name}: {pw}\n")
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
        print("\n=== Initial passwords (saved to instance/credentials.txt) ===")
        for name, pw in created:
            print(f"  {name:28s} {pw}")
        print("Share each password only with that society. Change them from the Secretary space.\n")


# ------------------------------------------------------------------ auth helpers
_attempts = {}  # (ip, slug) -> (count, locked_until)
MAX_TRIES, LOCK_SECONDS = 5, 300


def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    return get_db().execute("SELECT * FROM societies WHERE id=?", (uid,)).fetchone()


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        user = current_user()
        if not user:
            return jsonify(error="Please sign in."), 401
        g.user = user
        return fn(*a, **kw)

    return wrapper


def secretary_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*a, **kw):
        if not g.user["is_secretary"]:
            return jsonify(error="Secretary access only."), 403
        return fn(*a, **kw)

    return wrapper


@app.before_request
def csrf_guard():
    # State-changing API calls must come from our own frontend.
    if request.method in ("POST", "PATCH", "PUT", "DELETE") and request.path.startswith("/api/"):
        if request.headers.get("X-Requested-With") != "ieee-tracker":
            return jsonify(error="Bad request."), 400


@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "same-origin"
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


# ------------------------------------------------------------------ data helpers
def today_str():
    return date.today().isoformat()


def event_stats(db, where="", params=()):
    """Return {event_id: (total, done, overdue)}."""
    rows = db.execute(
        f"""SELECT t.event_id,
                   COUNT(*) total,
                   SUM(t.done) done,
                   SUM(CASE WHEN t.done=0 AND t.due_date < ? THEN 1 ELSE 0 END) overdue
            FROM tasks t JOIN events e ON e.id=t.event_id {where}
            GROUP BY t.event_id""",
        (today_str(), *params),
    ).fetchall()
    return {r["event_id"]: (r["total"], r["done"] or 0, r["overdue"] or 0) for r in rows}


def serialize_event(e, stats, soc=None):
    total, done, overdue = stats.get(e["id"], (0, 0, 0))
    d = {
        "id": e["id"],
        "title": e["title"],
        "type": e["type"],
        "type_label": EVENT_TYPES.get(e["type"], e["type"]),
        "mode": e["mode"],
        "event_date": e["event_date"],
        "venue": e["venue"] or "",
        "notes": e["notes"] or "",
        "total": total,
        "done": done,
        "overdue": overdue,
        "percent": round(100 * done / total) if total else 0,
        "society_id": e["society_id"],
    }
    if soc is not None:
        d["society"] = {"slug": soc["slug"], "name": soc["name"], "color": soc["color"]}
    return d


def can_access_event(db, event_id):
    """Return event row if the signed-in user may see it, else None."""
    e = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not e:
        return None
    if g.user["is_secretary"] or e["society_id"] == g.user["id"]:
        return e
    return None


def own_event(db, event_id):
    """Event the signed-in account owns and may edit.

    A society edits its own events; the SB (secretary account) edits the SB's own
    events. Nobody can edit another account's events, including the secretary.
    """
    e = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    return e if e and e["society_id"] == g.user["id"] else None


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ routes: pages
@app.route("/")
def index():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "index.html")


# ------------------------------------------------------------------ routes: auth
@app.get("/api/societies")
def list_societies():
    rows = get_db().execute(
        "SELECT slug,name,subtitle,color,is_secretary FROM societies ORDER BY is_secretary DESC, id"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    slug = str(data.get("slug", ""))
    password = str(data.get("password", ""))
    key = (request.remote_addr, slug)
    count, locked_until = _attempts.get(key, (0, 0))
    if locked_until > time.time():
        wait = int(locked_until - time.time())
        return jsonify(error=f"Too many attempts. Try again in {wait // 60 + 1} min."), 429

    user = get_db().execute("SELECT * FROM societies WHERE slug=?", (slug,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        count += 1
        _attempts[key] = (count, time.time() + LOCK_SECONDS if count >= MAX_TRIES else 0)
        return jsonify(error="Incorrect password."), 401

    _attempts.pop(key, None)
    session.clear()
    session.permanent = True
    session["uid"] = user["id"]
    return jsonify(me_payload(user))


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


def me_payload(u):
    return {
        "slug": u["slug"],
        "name": u["name"],
        "subtitle": u["subtitle"],
        "color": u["color"],
        "is_secretary": bool(u["is_secretary"]),
    }


@app.get("/api/me")
def me():
    u = current_user()
    return jsonify(me_payload(u) if u else None)


@app.get("/api/meta")
@login_required
def meta():
    return jsonify(types=EVENT_TYPES, modes=MODES, phases=PHASES)


# ------------------------------------------------------------------ routes: events
@app.get("/api/events")
@login_required
def list_events():
    db = get_db()
    if g.user["is_secretary"]:
        # ?scope=sb -> the SB's own events; default -> every society's events
        own_only = request.args.get("scope") == "sb"
        op = "=" if own_only else "!="
        rows = db.execute(
            f"SELECT * FROM events WHERE society_id {op} ? ORDER BY event_date", (g.user["id"],)
        ).fetchall()
        stats = event_stats(db)
        socs = {s["id"]: s for s in db.execute("SELECT * FROM societies")}
        return jsonify([serialize_event(e, stats, socs[e["society_id"]]) for e in rows])
    rows = db.execute(
        "SELECT * FROM events WHERE society_id=? ORDER BY event_date", (g.user["id"],)
    ).fetchall()
    stats = event_stats(db, "WHERE e.society_id=?", (g.user["id"],))
    return jsonify([serialize_event(e, stats) for e in rows])


@app.post("/api/events")
@login_required
def create_event():
    d = request.get_json(silent=True) or {}
    title = str(d.get("title", "")).strip()[:150]
    etype, mode = d.get("type"), d.get("mode")
    ev_date = valid_date(d.get("event_date"))
    if not title or etype not in EVENT_TYPES or mode not in MODES or not ev_date:
        return jsonify(error="Title, type, mode and a valid date are required."), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO events (society_id,title,type,mode,event_date,venue,notes,created_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            g.user["id"], title, etype, mode, ev_date.isoformat(),
            str(d.get("venue", "")).strip()[:150], str(d.get("notes", "")).strip()[:1000],
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    eid = cur.lastrowid
    rows = []
    for pos, (phase, text, off) in enumerate(build_checklist(etype, mode)):
        rows.append((eid, phase, text, off, (ev_date + timedelta(days=off)).isoformat(), pos))
    db.executemany(
        "INSERT INTO tasks (event_id,phase,title,offset_days,due_date,position) VALUES (?,?,?,?,?,?)",
        rows,
    )
    db.commit()
    return jsonify(id=eid), 201


@app.get("/api/events/<int:eid>")
@login_required
def get_event(eid):
    db = get_db()
    e = can_access_event(db, eid)
    if not e:
        return jsonify(error="Not found."), 404
    stats = event_stats(db, "WHERE e.id=?", (eid,))
    soc = db.execute("SELECT * FROM societies WHERE id=?", (e["society_id"],)).fetchone()
    tasks = db.execute(
        "SELECT id,phase,title,due_date,done,done_at,custom FROM tasks WHERE event_id=? ORDER BY position,id",
        (eid,),
    ).fetchall()
    comments = db.execute(
        "SELECT id,author,body,created_at FROM comments WHERE event_id=? ORDER BY id", (eid,)
    ).fetchall()
    out = serialize_event(e, stats, soc)
    out["tasks"] = [dict(t, done=bool(t["done"]), custom=bool(t["custom"])) for t in tasks]
    out["comments"] = [dict(c) for c in comments]
    out["editable"] = e["society_id"] == g.user["id"]
    return jsonify(out)


@app.patch("/api/events/<int:eid>")
@login_required
def update_event(eid):
    db = get_db()
    e = own_event(db, eid)
    if not e:
        return jsonify(error="Not allowed."), 403
    d = request.get_json(silent=True) or {}
    title = str(d.get("title", e["title"])).strip()[:150] or e["title"]
    venue = str(d.get("venue", e["venue"] or "")).strip()[:150]
    notes = str(d.get("notes", e["notes"] or "")).strip()[:1000]
    new_date = valid_date(d.get("event_date")) if "event_date" in d else valid_date(e["event_date"])
    if not new_date:
        return jsonify(error="Invalid date."), 400
    db.execute(
        "UPDATE events SET title=?,venue=?,notes=?,event_date=? WHERE id=?",
        (title, venue, notes, new_date.isoformat(), eid),
    )
    if new_date.isoformat() != e["event_date"]:  # shift template deadlines
        for t in db.execute(
            "SELECT id,offset_days FROM tasks WHERE event_id=? AND offset_days IS NOT NULL", (eid,)
        ).fetchall():
            db.execute(
                "UPDATE tasks SET due_date=? WHERE id=?",
                ((new_date + timedelta(days=t["offset_days"])).isoformat(), t["id"]),
            )
    db.commit()
    return jsonify(ok=True)


@app.delete("/api/events/<int:eid>")
@login_required
def delete_event(eid):
    db = get_db()
    if not own_event(db, eid):
        return jsonify(error="Not allowed."), 403
    db.execute("DELETE FROM events WHERE id=?", (eid,))
    db.commit()
    return jsonify(ok=True)


# ------------------------------------------------------------------ routes: tasks
@app.post("/api/events/<int:eid>/tasks")
@login_required
def add_task(eid):
    db = get_db()
    e = own_event(db, eid)
    if not e:
        return jsonify(error="Not allowed."), 403
    d = request.get_json(silent=True) or {}
    title = str(d.get("title", "")).strip()[:200]
    phase = d.get("phase") if d.get("phase") in PHASES else "Pre-event"
    due = d.get("due_date")
    due = due if valid_date(due) else None
    if not title:
        return jsonify(error="Task title required."), 400
    pos = db.execute("SELECT COALESCE(MAX(position),0)+1 FROM tasks WHERE event_id=?", (eid,)).fetchone()[0]
    db.execute(
        "INSERT INTO tasks (event_id,phase,title,due_date,custom,position) VALUES (?,?,?,?,1,?)",
        (eid, phase, title, due, pos),
    )
    db.commit()
    return jsonify(ok=True), 201


def own_task(db, tid):
    return db.execute(
        "SELECT t.* FROM tasks t JOIN events e ON e.id=t.event_id WHERE t.id=? AND e.society_id=?",
        (tid, g.user["id"]),
    ).fetchone()


@app.patch("/api/tasks/<int:tid>")
@login_required
def update_task(tid):
    db = get_db()
    t = own_task(db, tid)
    if not t:
        return jsonify(error="Not allowed."), 403
    d = request.get_json(silent=True) or {}
    if "done" in d:
        done = 1 if d["done"] else 0
        db.execute(
            "UPDATE tasks SET done=?, done_at=? WHERE id=?",
            (done, datetime.now().isoformat(timespec="seconds") if done else None, tid),
        )
    if "due_date" in d:
        due = d["due_date"] if valid_date(d["due_date"]) else None
        db.execute("UPDATE tasks SET due_date=?, offset_days=NULL WHERE id=?", (due, tid))
    if "title" in d and str(d["title"]).strip():
        db.execute("UPDATE tasks SET title=? WHERE id=?", (str(d["title"]).strip()[:200], tid))
    db.commit()
    return jsonify(ok=True)


@app.delete("/api/tasks/<int:tid>")
@login_required
def delete_task(tid):
    db = get_db()
    if not own_task(db, tid):
        return jsonify(error="Not allowed."), 403
    db.execute("DELETE FROM tasks WHERE id=?", (tid,))
    db.commit()
    return jsonify(ok=True)


# ------------------------------------------------------------------ routes: comments
@app.post("/api/events/<int:eid>/comments")
@login_required
def add_comment(eid):
    db = get_db()
    if not can_access_event(db, eid):
        return jsonify(error="Not found."), 404
    body = str((request.get_json(silent=True) or {}).get("body", "")).strip()[:500]
    if not body:
        return jsonify(error="Comment is empty."), 400
    db.execute(
        "INSERT INTO comments (event_id,author,body,created_at) VALUES (?,?,?,?)",
        (eid, g.user["name"], body, datetime.now().isoformat(timespec="seconds")),
    )
    db.commit()
    return jsonify(ok=True), 201


# ------------------------------------------------------------------ routes: secretary
@app.get("/api/overview")
@secretary_required
def overview():
    db = get_db()
    stats = event_stats(db)
    out = []
    for s in db.execute("SELECT * FROM societies WHERE is_secretary=0 ORDER BY id"):
        evs = db.execute("SELECT * FROM events WHERE society_id=?", (s["id"],)).fetchall()
        total = done = overdue = 0
        upcoming = 0
        for e in evs:
            t, dn, od = stats.get(e["id"], (0, 0, 0))
            total, done, overdue = total + t, done + dn, overdue + od
            if e["event_date"] >= today_str():
                upcoming += 1
        out.append(
            {
                "slug": s["slug"], "name": s["name"], "subtitle": s["subtitle"], "color": s["color"],
                "events": len(evs), "upcoming": upcoming, "tasks": total, "done": done,
                "overdue": overdue, "percent": round(100 * done / total) if total else 0,
            }
        )
    return jsonify(out)


@app.post("/api/secretary/reset-password")
@secretary_required
def reset_password():
    d = request.get_json(silent=True) or {}
    slug, pw = str(d.get("slug", "")), str(d.get("password", ""))
    if len(pw) < 6:
        return jsonify(error="Password must be at least 6 characters."), 400
    db = get_db()
    cur = db.execute(
        "UPDATE societies SET password_hash=? WHERE slug=?", (generate_password_hash(pw), slug)
    )
    db.commit()
    if cur.rowcount == 0:
        return jsonify(error="Unknown society."), 404
    return jsonify(ok=True)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
