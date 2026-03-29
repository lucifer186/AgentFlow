import sqlite3

DB_PATH = "tasks.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        priority TEXT DEFAULT 'medium',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        tags TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

# ── Task helpers ──────────────────────────────────────────
def add_task(title, description="", priority="medium"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)",
        (title, description, priority)
    )
    conn.commit()
    conn.close()
    return f"Task '{title}' added successfully."

def get_tasks(status=None):
    conn = get_connection()
    if status:
        rows = conn.execute("SELECT * FROM tasks WHERE status=?", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return rows

def update_task_status(task_id, status):
    conn = get_connection()
    conn.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
    conn.commit()
    conn.close()
    return f"Task {task_id} marked as '{status}'."

def delete_task(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return f"Task {task_id} deleted."

# ── Schedule helpers ──────────────────────────────────────
def add_schedule(title, date, time="", description=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO schedules (title, date, time, description) VALUES (?, ?, ?, ?)",
        (title, date, time, description)
    )
    conn.commit()
    conn.close()
    return f"Schedule '{title}' on {date} added."

def get_schedules():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM schedules ORDER BY date").fetchall()
    conn.close()
    return rows

def delete_schedule(schedule_id):
    conn = get_connection()
    conn.execute("DELETE FROM schedules WHERE id=?", (schedule_id,))
    conn.commit()
    conn.close()
    return f"Schedule {schedule_id} deleted."

# ── Notes helpers ─────────────────────────────────────────
def add_note(title, content="", tags=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
        (title, content, tags)
    )
    conn.commit()
    conn.close()
    return f"Note '{title}' saved."

def get_notes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM notes ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows

def delete_note(note_id):
    conn = get_connection()
    conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()
    return f"Note {note_id} deleted."
