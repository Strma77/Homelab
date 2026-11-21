import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, request, redirect, render_template, g

# --- config (all overridable via env in docker-compose) ---
APP_TZ = ZoneInfo(os.environ.get("TZ", "Europe/Zagreb"))
DB_PATH = os.environ.get("DB_PATH", "/data/tasks.db")
REFRESH_SECONDS = int(os.environ.get("REFRESH_SECONDS", "30"))

RECURRENCES = ["daily", "weekly", "monthly", "once"]
GROUP_LABELS = {
    "daily": "Daily",
    "weekly": "Weekly",
    "monthly": "Monthly",
    "once": "One-off",
}

app = Flask(__name__)


# --- db plumbing ---
def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL;")
    return db


@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            recurrence   TEXT NOT NULL DEFAULT 'once',
            completed_at TEXT,
            position     INTEGER NOT NULL DEFAULT 0,
            created_at   TEXT NOT NULL
        );
        """
    )
    db.commit()
    db.close()


def now_local():
    return datetime.now(APP_TZ)


# --- the lazy-recurrence core ---
# A task is "done" only if its completion falls inside the CURRENT period
# for its recurrence type. No cron, no timer: daily tasks auto-reappear at
# midnight simply because "today" moved on.
def is_done(task, now):
    ts = task["completed_at"]
    if not ts:
        return False
    try:
        c = datetime.fromisoformat(ts)
    except ValueError:
        return False
    if c.tzinfo is None:
        c = c.replace(tzinfo=APP_TZ)
    rec = task["recurrence"]
    if rec == "once":
        return True
    if rec == "daily":
        return c.date() == now.date()
    if rec == "weekly":
        return c.isocalendar()[:2] == now.isocalendar()[:2]  # (iso_year, iso_week)
    if rec == "monthly":
        return (c.year, c.month) == (now.year, now.month)
    return False


def load_grouped():
    now = now_local()
    db = get_db()
    rows = db.execute("SELECT * FROM tasks ORDER BY position ASC, id ASC").fetchall()
    groups = {k: [] for k in RECURRENCES}
    for r in rows:
        groups[r["recurrence"]].append(
            {
                "id": r["id"],
                "title": r["title"],
                "recurrence": r["recurrence"],
                "done": is_done(r, now),
            }
        )
    ordered = [(k, GROUP_LABELS[k], groups[k]) for k in RECURRENCES]
    return ordered, now


# --- display panel (tablet) ---
@app.route("/")
def display():
    groups, now = load_grouped()
    return render_template("display.html", groups=groups, now=now, refresh=REFRESH_SECONDS)


@app.route("/toggle", methods=["POST"])
def toggle():
    task_id = request.form.get("id", type=int)
    if task_id is not None:
        db = get_db()
        row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is not None:
            now = now_local()
            if is_done(row, now):
                db.execute("UPDATE tasks SET completed_at=NULL WHERE id=?", (task_id,))
            else:
                db.execute(
                    "UPDATE tasks SET completed_at=? WHERE id=?",
                    (now.isoformat(), task_id),
                )
            db.commit()
    return redirect("/", code=303)  # POST/redirect/GET so a refresh never re-submits


# --- admin panel (phone/pc) ---
@app.route("/admin")
def admin():
    groups, now = load_grouped()
    return render_template(
        "admin.html", groups=groups, now=now, recurrences=RECURRENCES, labels=GROUP_LABELS
    )


@app.route("/admin/add", methods=["POST"])
def admin_add():
    title = (request.form.get("title") or "").strip()
    rec = request.form.get("recurrence", "once")
    if rec not in RECURRENCES:
        rec = "once"
    if title:
        db = get_db()
        maxpos = db.execute(
            "SELECT COALESCE(MAX(position), 0) FROM tasks WHERE recurrence=?", (rec,)
        ).fetchone()[0]
        db.execute(
            "INSERT INTO tasks (title, recurrence, completed_at, position, created_at) "
            "VALUES (?, ?, NULL, ?, ?)",
            (title, rec, maxpos + 1, now_local().isoformat()),
        )
        db.commit()
    return redirect("/admin", code=303)


@app.route("/admin/edit", methods=["POST"])
def admin_edit():
    task_id = request.form.get("id", type=int)
    title = (request.form.get("title") or "").strip()
    rec = request.form.get("recurrence", "once")
    if rec not in RECURRENCES:
        rec = "once"
    if task_id is not None and title:
        db = get_db()
        db.execute(
            "UPDATE tasks SET title=?, recurrence=? WHERE id=?", (title, rec, task_id)
        )
        db.commit()
    return redirect("/admin", code=303)


@app.route("/admin/reset", methods=["POST"])
def admin_reset():
    task_id = request.form.get("id", type=int)
    if task_id is not None:
        db = get_db()
        db.execute("UPDATE tasks SET completed_at=NULL WHERE id=?", (task_id,))
        db.commit()
    return redirect("/admin", code=303)


@app.route("/admin/delete", methods=["POST"])
def admin_delete():
    task_id = request.form.get("id", type=int)
    if task_id is not None:
        db = get_db()
        db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        db.commit()
    return redirect("/admin", code=303)


init_db()

if __name__ == "__main__":
    # dev only; the container runs gunicorn (see Dockerfile)
    app.run(host="0.0.0.0", port=8080, debug=True)
