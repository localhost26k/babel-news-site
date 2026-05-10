import datetime as dt
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from .constants import ABOUT_SECTION, ABOUT_TEXT, WRITER_SECTIONS
from .db import get_db
from .media import allowed_external_media_url, allowed_file, is_http_url, sanitize_body
from .security import (
    clear_login_failures,
    login_required,
    record_login_failure,
    too_many_login_attempts,
)


bp = Blueprint("site", __name__)


def _utc_timestamp():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _post_filters(section, sublabel):
    where = []
    params = []
    if section:
        where.append("section = ?")
        params.append(section)
    if sublabel:
        where.append("sublabel = ?")
        params.append(sublabel)
    return where, params


def _save_uploaded_media(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("نوع الملف غير مدعوم. استخدم صورة أو فيديو بالامتدادات المسموحة.")

    filename = secure_filename(file_storage.filename)
    if not filename:
        raise ValueError("اسم الملف غير صالح.")

    unique = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
    filename = f"{unique}_{uuid.uuid4().hex[:8]}_{filename}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    upload_folder.mkdir(parents=True, exist_ok=True)
    file_storage.save(upload_folder / filename)
    return f"{current_app.config['PUBLIC_UPLOAD_PREFIX']}/{filename}"


def _delete_local_media(media_path):
    if not media_path or is_http_url(media_path):
        return

    prefix = current_app.config["PUBLIC_UPLOAD_PREFIX"].strip("/") + "/"
    normalized = media_path.lstrip("/")
    if not normalized.startswith(prefix):
        return

    filename = normalized[len(prefix):]
    upload_folder = current_app.config["UPLOAD_FOLDER"].resolve()
    target = (upload_folder / filename).resolve()
    try:
        target.relative_to(upload_folder)
    except ValueError:
        return
    target.unlink(missing_ok=True)


@bp.route("/")
def index():
    section = request.args.get("section")
    sublabel = request.args.get("sub")
    about_text = ABOUT_TEXT if section == ABOUT_SECTION or sublabel == ABOUT_SECTION else None

    posts = []
    featured = []
    if not about_text:
        conn = get_db()
        try:
            query = "SELECT * FROM posts"
            where, params = _post_filters(section, sublabel)
            if where:
                query += " WHERE " + " AND ".join(where)
            query += " ORDER BY datetime(created_at) DESC LIMIT 20"
            posts = conn.execute(query, params).fetchall()
            featured = conn.execute(
                "SELECT * FROM posts WHERE featured = 1 "
                "ORDER BY datetime(created_at) DESC LIMIT 5"
            ).fetchall()
        finally:
            conn.close()

    return render_template(
        "index.html",
        posts=posts,
        featured=featured,
        active_section=section,
        active_sub=sublabel,
        about_text=about_text,
    )


@bp.route("/healthz")
def healthz():
    return {"status": "ok"}


@bp.route("/post/<int:pid>")
def post(pid):
    conn = get_db()
    try:
        p = conn.execute("SELECT * FROM posts WHERE id = ?", (pid,)).fetchone()
    finally:
        conn.close()
    if not p:
        return render_template("404.html"), 404
    return render_template("post.html", p=p)


@bp.route("/writer/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        try:
            if too_many_login_attempts(conn, username):
                conn.commit()
                flash("تم إيقاف محاولات الدخول مؤقتا. حاول مرة أخرى بعد 15 دقيقة.", "danger")
                return render_template("login.html"), 429

            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

            if user and check_password_hash(user["password_hash"], password):
                clear_login_failures(conn, username)
                conn.commit()
                session.clear()
                session.permanent = True
                session["writer"] = user["username"]
                flash("تم تسجيل الدخول بنجاح", "success")
                return redirect(url_for("site.dashboard"))

            record_login_failure(conn, username)
            conn.commit()
        finally:
            conn.close()
        flash("بيانات الدخول غير صحيحة", "danger")
    return render_template("login.html")


@bp.route("/writer/logout")
def logout():
    session.clear()
    flash("تم تسجيل الخروج", "info")
    return redirect(url_for("site.login"))


@bp.route("/writer")
@login_required
def dashboard():
    conn = get_db()
    try:
        posts = conn.execute(
            "SELECT id, title, section, sublabel, created_at, featured "
            "FROM posts ORDER BY datetime(created_at) DESC"
        ).fetchall()
    finally:
        conn.close()
    return render_template("dashboard.html", posts=posts)


@bp.route("/writer/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = sanitize_body(request.form.get("body", ""))
        section = request.form.get("section")
        sublabel = request.form.get("sublabel")
        featured = 1 if request.form.get("featured") == "on" else 0
        media_url = request.form.get("media_url", "").strip()
        upload = request.files.get("image")

        if not title or not body:
            flash("الرجاء إكمال جميع الحقول المطلوبة", "danger")
            return redirect(url_for("site.new_post"))
        if section == ABOUT_SECTION:
            flash("قسم «من نحن» ثابت ولا يقبل النشر من الكادر التحريري.", "danger")
            return redirect(url_for("site.new_post"))
        if section not in WRITER_SECTIONS or sublabel not in WRITER_SECTIONS.get(section, []):
            flash("يرجى اختيار قسم وتصنيف صحيحين.", "danger")
            return redirect(url_for("site.new_post"))
        if media_url and upload and upload.filename:
            flash("اختر إما رفع ملف أو رابط وسائط خارجي، وليس الاثنين معا.", "danger")
            return redirect(url_for("site.new_post"))

        image_path = None
        if media_url:
            if not allowed_external_media_url(media_url):
                flash("رابط الوسائط غير صالح. استخدم رابط YouTube أو رابط صورة/فيديو مباشر.", "danger")
                return redirect(url_for("site.new_post"))
            image_path = media_url
        elif upload and upload.filename:
            try:
                image_path = _save_uploaded_media(upload)
            except ValueError as exc:
                flash(str(exc), "danger")
                return redirect(url_for("site.new_post"))

        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO posts(title, body, section, sublabel, author, image_path, featured, created_at)
                   VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    title,
                    body,
                    section,
                    sublabel,
                    session.get("writer"),
                    image_path,
                    featured,
                    _utc_timestamp(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        flash("تم نشر الخبر بنجاح", "success")
        return redirect(url_for("site.dashboard"))

    return render_template("new_post.html", writer_sections=WRITER_SECTIONS)


@bp.route("/writer/delete/<int:pid>", methods=["POST"])
@login_required
def delete_post(pid):
    conn = get_db()
    try:
        post_row = conn.execute("SELECT image_path FROM posts WHERE id = ?", (pid,)).fetchone()
        conn.execute("DELETE FROM posts WHERE id = ?", (pid,))
        conn.commit()
    finally:
        conn.close()

    if post_row:
        _delete_local_media(post_row["image_path"])
    flash("تم حذف المنشور", "info")
    return redirect(url_for("site.dashboard"))


@bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
