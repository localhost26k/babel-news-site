import sqlite3
import secrets

from flask import current_app
from werkzeug.security import generate_password_hash


SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS login_attempts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    remote_addr TEXT NOT NULL,
    failed_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_scope
ON login_attempts(username, remote_addr, failed_at);

CREATE TABLE IF NOT EXISTS posts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    section TEXT NOT NULL,
    sublabel TEXT NOT NULL,
    author TEXT,
    image_path TEXT,
    featured INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);
"""


def get_db():
    db_path = current_app.config["DATABASE"]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _initial_writer_password():
    configured = current_app.config.get("DEFAULT_WRITER_PASSWORD")
    if configured:
        return configured

    password_path = current_app.config["DATABASE"].parent / ".initial_writer_password"
    if password_path.exists():
        saved = password_path.read_text(encoding="utf-8").strip()
        if saved:
            return saved

    generated = secrets.token_urlsafe(18)
    password_path.write_text(generated, encoding="utf-8")
    return generated


def init_db():
    conn = get_db()
    try:
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if count == 0:
            username = current_app.config["DEFAULT_WRITER_USER"]
            password = _initial_writer_password()
            conn.execute(
                "INSERT INTO users(username, password_hash) VALUES(?, ?)",
                (username, generate_password_hash(password)),
            )
        conn.commit()
    finally:
        conn.close()
