import datetime as dt
import os
import secrets
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
INSTANCE_DIR = PROJECT_ROOT / "instance"


def _int_from_env(name, default):
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _secret_key():
    configured = os.environ.get("FLASK_SECRET_KEY") or os.environ.get("SECRET_KEY")
    if configured:
        return configured

    secret_path = INSTANCE_DIR / ".secret_key"
    try:
        if secret_path.exists():
            saved = secret_path.read_text(encoding="utf-8").strip()
            if saved:
                return saved

        INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        generated = secrets.token_urlsafe(48)
        secret_path.write_text(generated, encoding="utf-8")
        return generated
    except OSError:
        return secrets.token_urlsafe(48)


class Config:
    SECRET_KEY = _secret_key()
    DATABASE = Path(os.environ.get("BABEL_NEWS_DATABASE", INSTANCE_DIR / "site.db"))
    UPLOAD_FOLDER = Path(os.environ.get("BABEL_NEWS_UPLOAD_FOLDER", APP_DIR / "static" / "uploads"))
    PUBLIC_UPLOAD_PREFIX = os.environ.get("BABEL_NEWS_PUBLIC_UPLOAD_PREFIX", "static/uploads").strip("/")
    MAX_CONTENT_LENGTH = _int_from_env("MAX_CONTENT_LENGTH", 25 * 1024 * 1024)
    DEFAULT_WRITER_USER = os.environ.get("DEFAULT_WRITER_USER", "EOB")
    DEFAULT_WRITER_PASSWORD = os.environ.get("DEFAULT_WRITER_PASSWORD")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    PERMANENT_SESSION_LIFETIME = dt.timedelta(hours=2)
