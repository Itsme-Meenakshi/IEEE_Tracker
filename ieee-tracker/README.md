# IEEE SB MITS – Event Checklist Tracker

Each of the 6 societies gets a password-protected space with tailored event checklists.
The Secretary space shows every society's progress, flags overdue tasks and can leave remarks.

## Run it locally

```bash
cd ieee-tracker
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

On the **first run** the app creates the database and prints a random password for each
society and for the Secretary. They are also saved in `instance/credentials.txt`.
Give each society only its own password. The Secretary can change any society's password
later from **Society passwords** on the overview page.

Want to choose passwords yourself? Set them before the first run:

```bash
PASSWORD_SSCS=... PASSWORD_WIE=... PASSWORD_CASS=... PASSWORD_RAS=... \
PASSWORD_PES=... PASSWORD_CS=... PASSWORD_SECRETARY=... python app.py
```

## Event types (checklist is tailored by type and by online / offline / hybrid)

Hackathon, Hands-on Workshop, Talk Session, Inauguration, Flagship Event, Competition,
Panel Discussion, Orientation, Webinar, Conference, Exhibition.

Every checklist has four phases: Planning, Pre-event, Event day, Post-event.
Deadlines are calculated from the event date and shift automatically if the date changes.
Societies can add, remove or edit tasks for their own events.

To change what a checklist contains, edit `checklists.py`.

## Who can do what

| | Society | Secretary |
|---|---|---|
| See own events | yes | all societies |
| Create / edit events, tick tasks | own events only | no (view only) |
| Post remarks on an event | yes | yes |
| See other societies' events | no | yes |
| Reset society passwords | no | yes |

## Put it online (so everyone can use it)

Any Python host works (Render, Railway, PythonAnywhere, a college server).

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

Set these environment variables on the host:

- `SECRET_KEY` – a long random string (keeps logins valid across restarts)
- `COOKIE_SECURE=1` – once the site is served over HTTPS
- `DB_PATH` – path on a **persistent disk** (SQLite is a single file; if the host wipes its disk on every deploy, your data goes with it)

Back up `tracker.db` regularly.

## Files

- `app.py` – Flask backend, database, login, permissions
- `checklists.py` – the checklist templates
- `static/` – the interface (`index.html`, `style.css`, `app.js`)
