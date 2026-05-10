import secrets
import time
from functools import wraps

from flask import abort, redirect, request, session, url_for


LOGIN_ATTEMPT_LIMIT = 5
LOGIN_ATTEMPT_WINDOW_SECONDS = 15 * 60


def _login_scope(username):
    remote_addr = request.remote_addr or "unknown"
    return username.casefold(), remote_addr


def csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf():
    token = session.get("_csrf_token")
    submitted = request.form.get("_csrf_token", "")
    if not token or not secrets.compare_digest(token, submitted):
        abort(400)


def csrf_protect():
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        validate_csrf()


def too_many_login_attempts(conn, username):
    cutoff = int(time.time()) - LOGIN_ATTEMPT_WINDOW_SECONDS
    normalized_username, remote_addr = _login_scope(username)
    conn.execute("DELETE FROM login_attempts WHERE failed_at < ?", (cutoff,))
    attempts = conn.execute(
        """SELECT COUNT(*) AS c
           FROM login_attempts
           WHERE username = ? AND remote_addr = ? AND failed_at >= ?""",
        (normalized_username, remote_addr, cutoff),
    ).fetchone()["c"]
    return attempts >= LOGIN_ATTEMPT_LIMIT


def record_login_failure(conn, username):
    normalized_username, remote_addr = _login_scope(username)
    conn.execute(
        "INSERT INTO login_attempts(username, remote_addr, failed_at) VALUES(?, ?, ?)",
        (normalized_username, remote_addr, int(time.time())),
    )


def clear_login_failures(conn, username):
    normalized_username, remote_addr = _login_scope(username)
    conn.execute(
        "DELETE FROM login_attempts WHERE username = ? AND remote_addr = ?",
        (normalized_username, remote_addr),
    )


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("writer"):
            return redirect(url_for("site.login"))
        return func(*args, **kwargs)

    return wrapper
