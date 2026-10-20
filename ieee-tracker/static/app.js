/* IEEE SB MITS – Event Checklists (frontend) */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const app = $("#app");

const state = { me: null, meta: null, societies: [], filter: { soc: "all", status: "all" } };

const TYPE_INFO = {
  hackathon: "Timed build event with teams, mentors and judging",
  workshop: "Hands-on session led by a resource person",
  talk: "Guest lecture or expert session",
  inauguration: "Society launch or opening ceremony",
  flagship: "Your society's biggest event of the year",
  competition: "Contests, quizzes and design challenges",
  panel: "Moderated discussion with several experts",
  orientation: "Introduce the society to new students",
  webinar: "Online session with registration and recording",
  conference: "Papers, tracks, keynotes and proceedings",
  exhibition: "Project showcase with stalls",
};

const ICON = {
  lock: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
  plus: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></svg>',
  x: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  back: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>',
  out: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>',
  cal: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/></svg>',
  pin: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
  key: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/></svg>',
};

/* ---------- helpers ---------- */
async function api(path, opts = {}) {
  const res = await fetch("/api" + path, {
    method: opts.method || "GET",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-Requested-With": "ieee-tracker" },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  let data = null;
  try { data = await res.json(); } catch (_) { /* empty */ }
  if (res.status === 401 && state.me && path !== "/login") {
    state.me = null; location.hash = ""; render();
    throw new Error("Session expired. Please sign in again.");
  }
  if (!res.ok) throw new Error((data && data.error) || "Something went wrong.");
  return data;
}

let toastTimer;
function toast(msg, isErr = false) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "show" + (isErr ? " err" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.className = ""), 2800);
}

const todayISO = () => { const d = new Date(); return new Date(d - d.getTimezoneOffset() * 6e4).toISOString().slice(0, 10); };
const parseD = (s) => new Date(s + "T00:00:00");
const fmtShort = (s) => parseD(s).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
const fmtLong = (s) => parseD(s).toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "long", year: "numeric" });
const daysBetween = (a, b) => Math.round((parseD(a) - parseD(b)) / 864e5);
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const accStyle = (c) => `--acc:${esc(c || "#00629b")}`;

function openModal(html, narrow = false) {
  const root = $("#modal-root");
  root.innerHTML = `<div class="overlay" data-close><div class="modal ${narrow ? "narrow" : ""}" role="dialog" aria-modal="true">${html}</div></div>`;
  const ov = $(".overlay", root);
  ov.addEventListener("mousedown", (e) => { if (e.target === ov) closeModal(); });
  document.addEventListener("keydown", escClose);
  const first = $("input, textarea, button.type", root); if (first) first.focus();
  return $(".modal", root);
}
function escClose(e) { if (e.key === "Escape") closeModal(); }
function closeModal() { $("#modal-root").innerHTML = ""; document.removeEventListener("keydown", escClose); }

/* ---------- router ---------- */
window.addEventListener("hashchange", render);
async function boot() {
  app.innerHTML = '<div class="loading">Loading…</div>';
  try {
    state.me = await api("/me");
    if (state.me) state.meta = await api("/meta");
  } catch (_) { state.me = null; }
  render();
}

function render() {
  if (!state.me) return renderLogin();
  const m = location.hash.match(/^#\/event\/(\d+)$/);
  if (m) return renderEvent(+m[1]);
  if (state.me.is_secretary) return location.hash === "#/sb" ? renderSociety(true) : renderSecretary();
  return renderSociety();
}

/* ---------- login ---------- */
async function renderLogin() {
  document.title = "Sign in · IEEE SB MITS";
  if (!state.societies.length) {
    try { state.societies = await api("/societies"); } catch (_) { /* retry below */ }
  }
  let selected = null;
  app.innerHTML = `
  <div class="login">
    <section class="login-hero">
      <div class="brand"><span class="brand-mark logo"><img src="/static/logo.png" alt="IEEE SB MITS logo"></span> IEEE SB MITS</div>
      <div>
        <h1>Nothing gets missed at an event.</h1>
        <p>A checklist for every kind of event, from the first permission letter to the final report. Each society keeps its own space.</p>
      </div>
      <div>
        <div class="hero-trace"><i class="on"></i><b class="on"></b><i class="on"></i><b></b><i></i><b></b><i></i></div>
        <div class="hero-labels" style="max-width:360px"><span>Planning</span><span>Pre-event</span><span>Event day</span><span>Post-event</span></div>
      </div>
    </section>
    <section class="login-panel">
      <form class="login-box" id="login-form" autocomplete="off">
        <h2>Open your space</h2>
        <p>Choose your society and enter its password.</p>
        <div class="soc-list" id="soc-list">
          ${state.societies.map((s) => `
            <button type="button" class="soc ${s.is_secretary ? "sec" : ""}" data-slug="${esc(s.slug)}" style="--c:${esc(s.color)}" aria-pressed="false">
              <span class="dot"></span><span><strong>${esc(s.name)}</strong><small>${esc(s.subtitle)}</small></span>
            </button>`).join("") || '<p class="form-error">Could not load societies. Refresh the page.</p>'}
        </div>
        <div class="field">
          <label for="pw">Password</label>
          <div class="pw">${ICON.lock}<input id="pw" class="input" type="password" placeholder="Society password" required></div>
        </div>
        <p class="form-error" id="login-err" role="alert"></p>
        <button class="btn primary" style="width:100%" id="login-btn" disabled>Enter space</button>
      </form>
    </section>
  </div>`;
  const form = $("#login-form"), btn = $("#login-btn");
  $("#soc-list").addEventListener("click", (e) => {
    const b = e.target.closest(".soc"); if (!b) return;
    selected = b.dataset.slug;
    $$(".soc").forEach((x) => x.setAttribute("aria-pressed", x === b));
    const c = getComputedStyle(b).getPropertyValue("--c");
    form.style.setProperty("--acc", c);
    btn.disabled = false; $("#pw").focus();
  });
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!selected) return;
    btn.disabled = true; $("#login-err").textContent = "";
    try {
      state.me = await api("/login", { method: "POST", body: { slug: selected, password: $("#pw").value } });
      state.meta = await api("/meta");
      location.hash = "";
      render();
    } catch (err) {
      $("#login-err").textContent = err.message; btn.disabled = false; $("#pw").select();
    }
  });
}

/* ---------- shared shell ---------- */
function shell(inner, title) {
  document.title = title + " · IEEE SB MITS";
  const me = state.me;
  app.innerHTML = `
  <div style="${accStyle(me.color)}">
    <header class="topbar"><div class="topbar-in">
      <span class="brand-mark logo"><img src="/static/logo.png" alt="IEEE SB MITS logo"></span>
      <div class="who"><strong>${esc(me.name)}</strong><small>${esc(me.subtitle)}</small></div>
      ${me.is_secretary ? `<nav class="nav" aria-label="Sections">
        <a href="#/" ${state.section !== "sb" ? 'aria-current="page"' : ""}>All societies</a>
        <a href="#/sb" ${state.section === "sb" ? 'aria-current="page"' : ""}>SB checklists</a>
      </nav>` : ""}
      <span class="spacer"></span>
      <button class="btn small ghost" id="logout">${ICON.out} Sign out</button>
    </div></header>
    <main class="page">${inner}</main>
  </div>`;
  $("#logout").onclick = async () => {
    await api("/logout", { method: "POST" }).catch(() => {});
    state.me = null; location.hash = ""; render();
  };
}

function eventRow(e, showSociety) {
  const past = e.event_date < todayISO();
  const d = parseD(e.event_date);
  return `
  <button class="ev" data-id="${e.id}" style="${accStyle(e.society ? e.society.color : state.me.color)}">
    <div class="datebox"><b>${d.getDate()}</b><span>${d.toLocaleDateString("en-IN", { month: "short" })}</span></div>
    <div>
      <div class="ev-title">${esc(e.title)}</div>
      <div class="ev-meta">
        ${showSociety && e.society ? `<span class="chip soc-chip">${esc(e.society.name)}</span>` : ""}
        <span class="chip">${esc(e.type_label)}</span>
        <span class="chip">${esc(cap(e.mode))}</span>
        ${e.overdue ? `<span class="chip warn">${e.overdue} overdue</span>` : ""}
        ${!past && daysBetween(e.event_date, todayISO()) <= 7 && e.percent < 100 ? `<span class="chip warn">${daysBetween(e.event_date, todayISO()) === 0 ? "Today" : "In " + daysBetween(e.event_date, todayISO()) + " d"}</span>` : ""}
        ${e.percent === 100 ? '<span class="chip ok">Complete</span>' : ""}
      </div>
    </div>
    <div class="bar-wrap">
      <div class="bar-top"><span>${e.done} of ${e.total} tasks</span><span>${e.percent}%</span></div>
      <div class="bar ${e.percent === 100 ? "done" : ""}" style="--p:${e.percent}%"><i style="width:${e.percent}%"></i></div>
    </div>
  </button>`;
}

function bindRows() {
  $$(".ev").forEach((b) => (b.onclick = () => (location.hash = "#/event/" + b.dataset.id)));
}

function groupEvents(list, showSociety) {
  const t = todayISO();
  const up = list.filter((e) => e.event_date >= t).sort((a, b) => a.event_date.localeCompare(b.event_date));
  const past = list.filter((e) => e.event_date < t).sort((a, b) => b.event_date.localeCompare(a.event_date));
  return (
    (up.length ? `<div class="group-title">Upcoming</div>${up.map((e) => eventRow(e, showSociety)).join("")}` : "") +
    (past.length ? `<div class="group-title">Past events</div>${past.map((e) => eventRow(e, showSociety)).join("")}` : "")
  );
}

/* ---------- society dashboard ---------- */
async function renderSociety(isSB = false) {
  if (state.me.is_secretary) state.section = "sb";
  shell('<div class="loading">Loading events…</div>', isSB ? "SB checklists" : "Events");
  let events;
  try { events = await api("/events" + (isSB ? "?scope=sb" : "")); } catch (e) { return toast(e.message, true); }
  const t = todayISO();
  const upcoming = events.filter((e) => e.event_date >= t).length;
  const tasks = events.reduce((a, e) => a + e.total, 0), done = events.reduce((a, e) => a + e.done, 0);
  const overdue = events.reduce((a, e) => a + e.overdue, 0);
  shell(`
    <div class="page-head">
      <div><h2>${isSB ? "SB checklists" : "Your events"}</h2><p>${isSB ? "Events run by the Student Branch itself. These are kept apart from the societies' events." : "Pick an event type and the checklist is built for you."}</p></div>
      <button class="btn primary" id="new-ev">${ICON.plus} New event</button>
    </div>
    <div class="summary">
      <div class="sum"><b>${events.length}</b><span>Events</span></div>
      <div class="sum"><b>${upcoming}</b><span>Upcoming</span></div>
      <div class="sum"><b>${done}/${tasks}</b><span>Tasks done</span></div>
      <div class="sum ${overdue ? "alert" : ""}"><b>${overdue}</b><span>Overdue tasks</span></div>
    </div>
    ${events.length ? groupEvents(events, false) : `
      <div class="empty"><h3>No events yet</h3><p>${isSB ? "Add an SB event such as an inauguration, flagship or workshop and get a ready checklist." : "Create your first event and get a ready checklist for permissions, posters, certificates and reports."}</p>
      <button class="btn primary" id="new-ev2">${ICON.plus} Create an event</button></div>`}
  `, isSB ? "SB checklists" : "Events");
  bindRows();
  const open = () => newEventModal();
  $("#new-ev").onclick = open;
  if ($("#new-ev2")) $("#new-ev2").onclick = open;
}

function newEventModal() {
  const types = state.meta.types;
  let type = null, mode = "offline";
  const m = openModal(`
    <h2>New event</h2><p>What kind of event is it? We'll tailor the checklist.</p>
    <div class="type-grid">${Object.entries(types).map(([k, v]) => `
      <button type="button" class="type" data-type="${k}" aria-pressed="false"><strong>${esc(v)}</strong><small>${esc(TYPE_INFO[k] || "")}</small></button>`).join("")}
    </div>
    <div class="field"><label>Mode</label>
      <div class="seg" id="mode-seg">${state.meta.modes.map((x) => `<button type="button" data-mode="${x}" aria-pressed="${x === mode}">${x}</button>`).join("")}</div>
    </div>
    <div class="field"><label for="f-title">Event name</label><input id="f-title" class="input" maxlength="150" placeholder="e.g. Intro to Embedded Systems" required></div>
    <div class="row2">
      <div class="field"><label for="f-date">Date</label><input id="f-date" class="input" type="date" required></div>
      <div class="field"><label for="f-venue">Venue / platform</label><input id="f-venue" class="input" maxlength="150" placeholder="Seminar Hall / Google Meet"></div>
    </div>
    <div class="field"><label for="f-notes">Notes (optional)</label><textarea id="f-notes" class="textarea" maxlength="1000"></textarea></div>
    <p class="form-error" id="m-err" role="alert"></p>
    <div class="modal-actions"><button class="btn" id="m-cancel">Cancel</button><button class="btn primary" id="m-save">Create event</button></div>`);
  m.style.setProperty("--acc", state.me.color);
  $("#m-cancel", m).onclick = closeModal;
  m.addEventListener("click", (e) => {
    const tb = e.target.closest(".type");
    if (tb) {
      type = tb.dataset.type;
      $$(".type", m).forEach((x) => x.setAttribute("aria-pressed", x === tb));
      if (type === "webinar") setMode("online");
    }
    const mb = e.target.closest("[data-mode]");
    if (mb) setMode(mb.dataset.mode);
  });
  function setMode(v) { mode = v; $$("#mode-seg button", m).forEach((x) => x.setAttribute("aria-pressed", x.dataset.mode === v)); }
  $("#m-save", m).onclick = async () => {
    const body = { type, mode, title: $("#f-title", m).value, event_date: $("#f-date", m).value, venue: $("#f-venue", m).value, notes: $("#f-notes", m).value };
    if (!type) return ($("#m-err", m).textContent = "Choose an event type.");
    if (!body.title.trim() || !body.event_date) return ($("#m-err", m).textContent = "Add an event name and date.");
    try {
      const r = await api("/events", { method: "POST", body });
      closeModal(); location.hash = "#/event/" + r.id;
    } catch (err) { $("#m-err", m).textContent = err.message; }
  };
}

/* ---------- secretary overview ---------- */
async function renderSecretary() {
  state.section = "societies";
  shell('<div class="loading">Loading overview…</div>', "Overview");
  let overview, events;
  try { [overview, events] = await Promise.all([api("/overview"), api("/events")]); } catch (e) { return toast(e.message, true); }
  const f = state.filter, t = todayISO();
  let list = events.filter((e) => f.soc === "all" || e.society.slug === f.soc);
  if (f.status === "upcoming") list = list.filter((e) => e.event_date >= t);
  if (f.status === "overdue") list = list.filter((e) => e.overdue > 0);
  if (f.status === "complete") list = list.filter((e) => e.percent === 100);
  const totalOver = overview.reduce((a, s) => a + s.overdue, 0);
  shell(`
    <div class="page-head">
      <div><h2>All societies</h2><p>${events.length} events across ${overview.length} societies${totalOver ? ` · <b style="color:var(--warn)">${totalOver} overdue tasks</b>` : ""}</p></div>
      <button class="btn" id="pw-btn">${ICON.key} Society passwords</button>
    </div>
    <div class="soc-grid">${overview.map((s) => `
      <button class="soc-card" data-soc="${esc(s.slug)}" style="${accStyle(s.color)}" aria-pressed="${f.soc === s.slug}">
        <div><h3>${esc(s.name)}</h3><small>${esc(s.subtitle)}</small></div>
        <div class="bar-wrap"><div class="bar-top"><span>${s.done} of ${s.tasks} tasks</span><span>${s.percent}%</span></div>
          <div class="bar ${s.percent === 100 && s.tasks ? "done" : ""}" style="--p:${s.percent}%"><i style="width:${s.percent}%"></i></div></div>
        <div class="nums"><span><b>${s.events}</b> events</span><span><b>${s.upcoming}</b> upcoming</span><span class="${s.overdue ? "bad" : ""}"><b>${s.overdue}</b> overdue</span></div>
      </button>`).join("")}</div>
    <div class="filters">
      <button class="pill" data-soc="all" aria-pressed="${f.soc === "all"}">All societies</button>
      ${["all", "upcoming", "overdue", "complete"].map((x) => `<button class="pill" data-status="${x}" aria-pressed="${f.status === x}">${cap(x === "all" ? "any status" : x)}</button>`).join("")}
    </div>
    ${list.length ? groupEvents(list, true) : '<div class="empty" style="margin-top:18px"><h3>Nothing to show</h3><p>No events match these filters yet.</p></div>'}
  `, "Overview");
  bindRows();
  $$("[data-soc]").forEach((b) => (b.onclick = () => { state.filter.soc = state.filter.soc === b.dataset.soc && b.dataset.soc !== "all" ? "all" : b.dataset.soc; renderSecretary(); }));
  $$("[data-status]").forEach((b) => (b.onclick = () => { state.filter.status = b.dataset.status; renderSecretary(); }));
  $("#pw-btn").onclick = () => passwordsModal(overview);
}

function passwordsModal(socs) {
  const m = openModal(`
    <h2>Society passwords</h2><p>Set a new password for a society. Share it only with that society's team.</p>
    <div class="field"><label for="p-soc">Society</label><select id="p-soc" class="select">${socs.map((s) => `<option value="${esc(s.slug)}">${esc(s.name)}</option>`).join("")}</select></div>
    <div class="field"><label for="p-new">New password</label><input id="p-new" class="input" type="text" minlength="6" placeholder="At least 6 characters" autocomplete="off"></div>
    <p class="form-error" id="m-err" role="alert"></p>
    <div class="modal-actions"><button class="btn" id="m-cancel">Close</button><button class="btn primary" id="m-save">Update password</button></div>`, true);
  $("#m-cancel", m).onclick = closeModal;
  $("#m-save", m).onclick = async () => {
    try {
      await api("/secretary/reset-password", { method: "POST", body: { slug: $("#p-soc", m).value, password: $("#p-new", m).value } });
      $("#p-new", m).value = ""; toast("Password updated");
    } catch (err) { $("#m-err", m).textContent = err.message; }
  };
}

/* ---------- event detail ---------- */
async function renderEvent(id) {
  shell('<div class="loading">Loading checklist…</div>', "Event");
  let ev;
  try { ev = await api("/events/" + id); } catch (e) { toast(e.message, true); location.hash = ""; return; }
  const t = todayISO();
  const editable = ev.editable;
  if (state.me.is_secretary) state.section = editable ? "sb" : "societies";
  const phases = state.meta.phases;
  const byPhase = Object.fromEntries(phases.map((p) => [p, ev.tasks.filter((x) => x.phase === p)]));
  const accent = ev.society ? ev.society.color : state.me.color;
  const nodes = phases.map((p, i) => {
    const list = byPhase[p], d = list.filter((x) => x.done).length;
    const full = list.length && d === list.length, part = d > 0 && !full;
    const prevFull = i > 0 && byPhase[phases[i - 1]].length && byPhase[phases[i - 1]].every((x) => x.done);
    return `<div class="tnode ${full ? "full" : part ? "part" : ""} ${prevFull ? "prev-done" : ""}"><span class="dot">${full ? ICON.check : ""}</span><b>${p}</b><small>${d}/${list.length}</small></div>`;
  }).join("");

  const taskHtml = (x) => {
    let due = "";
    if (x.done) due = `<span class="due">Done ${x.done_at ? fmtShort(x.done_at.slice(0, 10)) : ""}</span>`;
    else if (x.due_date) {
      const late = x.due_date < t;
      const n = daysBetween(t, x.due_date);
      due = `<span class="due ${late ? "late" : ""}">${late ? `Overdue ${n}d` : "Due " + fmtShort(x.due_date)}</span>`;
    }
    return `<div class="task ${x.done ? "done" : ""}" data-id="${x.id}">
      <input type="checkbox" class="check" ${x.done ? "checked" : ""} ${editable ? "" : "disabled"} aria-label="Mark done: ${esc(x.title)}">
      <span class="t">${esc(x.title)}${x.custom ? ' <span class="chip">Added</span>' : ""}</span>${due}
      ${editable ? `<button class="x" title="Remove task" aria-label="Remove task">${ICON.x}</button>` : "<span></span>"}
    </div>`;
  };

  shell(`
    <button class="btn small ghost back" id="back">${ICON.back} ${state.me.is_secretary ? (editable ? "SB checklists" : "All societies") : "All events"}</button>
    <div class="detail-head" style="${accStyle(accent)}">
      <div>
        <h2>${esc(ev.title)}</h2>
        <div class="detail-meta">
          ${ev.society ? `<span class="chip soc-chip">${esc(ev.society.name)}</span>` : ""}
          <span class="chip">${esc(ev.type_label)}</span><span class="chip">${esc(cap(ev.mode))}</span>
          <span>${ICON.cal} ${esc(fmtLong(ev.event_date))}</span>
          ${ev.venue ? `<span>${ICON.pin} ${esc(ev.venue)}</span>` : ""}
        </div>
      </div>
      ${editable ? '<button class="btn" id="edit-ev">Edit event</button>' : ""}
    </div>
    <div class="detail-grid" style="${accStyle(accent)}">
      <div>
        <div class="panel">
          <div class="bar-wrap"><div class="bar-top"><span>${ev.done} of ${ev.total} tasks complete</span><span>${ev.percent}%</span></div>
          <div class="bar ${ev.percent === 100 ? "done" : ""}" style="--p:${ev.percent}%"><i style="width:${ev.percent}%"></i></div></div>
          <div class="trace" style="margin-top:18px">${nodes}</div>
        </div>
        ${phases.map((p) => `
          <section class="phase"><div class="phase-head"><h3>${p}</h3><span>${byPhase[p].filter((x) => x.done).length}/${byPhase[p].length}</span></div>
          ${byPhase[p].map(taskHtml).join("") || '<p class="note" style="padding:8px 0">No tasks in this phase.</p>'}</section>`).join("")}
        ${editable ? `
        <form class="panel add-task" id="add-task" style="margin-top:22px">
          <input class="input" id="nt-title" maxlength="200" placeholder="Add your own task…" required>
          <select class="select" id="nt-phase" aria-label="Phase">${phases.map((p) => `<option ${p === "Pre-event" ? "selected" : ""}>${p}</option>`).join("")}</select>
          <input class="input" id="nt-due" type="date" style="width:150px" aria-label="Due date">
          <button class="btn primary">${ICON.plus} Add</button>
        </form>` : ""}
      </div>
      <aside>
        ${ev.notes ? `<div class="panel"><h3>Notes</h3><p class="note">${esc(ev.notes)}</p></div>` : ""}
        <div class="panel">
          <h3>${state.me.is_secretary && !editable ? "Secretary remarks" : "Remarks"}</h3>
          ${ev.comments.length ? ev.comments.map((c) => `<div class="comment"><b>${esc(c.author)}</b><small>${esc(fmtShort(c.created_at.slice(0, 10)))}</small><p>${esc(c.body)}</p></div>`).join("") : '<p class="note">No remarks yet.</p>'}
          <form class="comment-form" id="comment-form">
            <textarea class="textarea" id="c-body" maxlength="500" placeholder="${state.me.is_secretary && !editable ? "Leave a remark or reminder for this society…" : "Reply or add an update…"}" required></textarea>
            <button class="btn primary small" style="justify-self:end">Post</button>
          </form>
        </div>
      </aside>
    </div>`, ev.title);

  $("#back").onclick = () => (location.hash = state.me.is_secretary && editable ? "#/sb" : "");
  const reload = () => renderEvent(id);
  const keepScroll = async () => { const y = scrollY; await reload(); scrollTo(0, y); };

  $$(".task").forEach((row) => {
    const tid = row.dataset.id;
    const cb = $(".check", row); if (cb && !cb.disabled) cb.onchange = async () => {
      try { await api("/tasks/" + tid, { method: "PATCH", body: { done: cb.checked } }); keepScroll(); } catch (e) { toast(e.message, true); cb.checked = !cb.checked; }
    };
    const x = $(".x", row); if (x) x.onclick = async () => {
      try { await api("/tasks/" + tid, { method: "DELETE" }); keepScroll(); } catch (e) { toast(e.message, true); }
    };
  });
  if (editable) {
    $("#add-task").onsubmit = async (e) => {
      e.preventDefault();
      try {
        await api(`/events/${id}/tasks`, { method: "POST", body: { title: $("#nt-title").value, phase: $("#nt-phase").value, due_date: $("#nt-due").value || null } });
        keepScroll();
      } catch (err) { toast(err.message, true); }
    };
    $("#edit-ev").onclick = () => editEventModal(ev);
  }
  $("#comment-form").onsubmit = async (e) => {
    e.preventDefault();
    try { await api(`/events/${id}/comments`, { method: "POST", body: { body: $("#c-body").value } }); keepScroll(); } catch (err) { toast(err.message, true); }
  };
}

function editEventModal(ev) {
  const m = openModal(`
    <h2>Edit event</h2><p class="hint" style="margin:0 0 16px">Changing the date shifts the deadlines of the standard tasks.</p>
    <div class="field"><label for="e-title">Event name</label><input id="e-title" class="input" maxlength="150" value="${esc(ev.title)}"></div>
    <div class="row2">
      <div class="field"><label for="e-date">Date</label><input id="e-date" class="input" type="date" value="${esc(ev.event_date)}"></div>
      <div class="field"><label for="e-venue">Venue / platform</label><input id="e-venue" class="input" maxlength="150" value="${esc(ev.venue)}"></div>
    </div>
    <div class="field"><label for="e-notes">Notes</label><textarea id="e-notes" class="textarea" maxlength="1000">${esc(ev.notes)}</textarea></div>
    <p class="form-error" id="m-err" role="alert"></p>
    <div class="modal-actions"><button class="btn danger left" id="m-del">Delete event</button><button class="btn" id="m-cancel">Cancel</button><button class="btn primary" id="m-save">Save changes</button></div>`);
  m.style.setProperty("--acc", state.me.color);
  $("#m-cancel", m).onclick = closeModal;
  $("#m-save", m).onclick = async () => {
    try {
      await api("/events/" + ev.id, { method: "PATCH", body: { title: $("#e-title", m).value, event_date: $("#e-date", m).value, venue: $("#e-venue", m).value, notes: $("#e-notes", m).value } });
      closeModal(); renderEvent(ev.id); toast("Saved");
    } catch (err) { $("#m-err", m).textContent = err.message; }
  };
  $("#m-del", m).onclick = async () => {
    if (!confirm("Delete this event and its whole checklist? This can't be undone.")) return;
    try { await api("/events/" + ev.id, { method: "DELETE" }); closeModal(); location.hash = state.me.is_secretary ? "#/sb" : ""; toast("Event deleted"); } catch (err) { $("#m-err", m).textContent = err.message; }
  };
}

boot();
