"""Set one or more passwords from the command line.

Usage (run inside the ieee-tracker folder, with the app stopped or running):
    python set_password.py secretary NewSBpassword
    python set_password.py wie WIE2026 sscs Another123

Names: sscs  wie  cass  ras  pes  cs  secretary   ("secretary" = IEEE SB MITS)
"""
import os
import sqlite3
import sys

from werkzeug.security import generate_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("DB_PATH", os.path.join(BASE, "instance", "tracker.db"))

args = sys.argv[1:]
if not args or len(args) % 2:
    sys.exit(__doc__)

db = sqlite3.connect(DB)
for slug, pw in zip(args[::2], args[1::2]):
    if len(pw) < 6:
        print(f"{slug}: skipped, password must be at least 6 characters")
        continue
    cur = db.execute("UPDATE societies SET password_hash=? WHERE slug=?", (generate_password_hash(pw), slug))
    print(f"{slug}: updated" if cur.rowcount else f"{slug}: unknown name")
db.commit()
db.close()
