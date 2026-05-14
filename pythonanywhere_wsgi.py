"""
Sample PythonAnywhere WSGI file for this project.

Copy the contents of this file into the WSGI file linked from the
PythonAnywhere Web tab, then replace YOUR_USERNAME with your
PythonAnywhere username.
"""

import os
import sys
from pathlib import Path


USERNAME = os.environ.get("PYTHONANYWHERE_USERNAME", "YOUR_USERNAME")
PROJECT_DIR = Path(f"/home/{USERNAME}/babel-news-site")
DATA_DIR = Path(f"/home/{USERNAME}/babel-news-data")

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "uploads").mkdir(parents=True, exist_ok=True)

os.environ.setdefault("BABEL_NEWS_DATABASE", str(DATA_DIR / "site.db"))
os.environ.setdefault("BABEL_NEWS_UPLOAD_FOLDER", str(DATA_DIR / "uploads"))
os.environ.setdefault("BABEL_NEWS_PUBLIC_UPLOAD_PREFIX", "uploads")
os.environ.setdefault("SESSION_COOKIE_SECURE", "1")

# Set these in this file before importing the app, or in PythonAnywhere's
# environment variable support if your account has it available.
os.environ.setdefault("DEFAULT_WRITER_USER", "EOB")
os.environ.setdefault("DEFAULT_WRITER_PASSWORD", "CHANGE_THIS_PASSWORD")
os.environ.setdefault("FLASK_SECRET_KEY", "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET")

from babel_news_site import create_app  # noqa: E402


application = create_app()
