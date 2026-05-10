import datetime as dt
from pathlib import Path

from flask import Flask

from .config import Config
from .constants import SECTIONS
from .db import init_db
from .media import media_kind, media_src
from .routes import bp
from .security import csrf_protect, csrf_token


def create_app(config_object=Config, **overrides):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    app.config.update(overrides)

    app.config["UPLOAD_FOLDER"] = Path(app.config["UPLOAD_FOLDER"])
    app.config["DATABASE"] = Path(app.config["DATABASE"])
    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["DATABASE"].parent.mkdir(parents=True, exist_ok=True)

    app.jinja_env.globals.update(
        csrf_token=csrf_token,
        media_kind=media_kind,
        media_src=media_src,
    )

    @app.context_processor
    def inject_globals():
        return {"sections": SECTIONS, "current_year": dt.date.today().year}

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    app.before_request(csrf_protect)
    app.register_blueprint(bp)

    with app.app_context():
        init_db()

    return app
