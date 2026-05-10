from urllib.parse import parse_qs, urlsplit

import bleach

from .constants import (
    ALLOWED_ATTRS,
    ALLOWED_EXTENSIONS,
    ALLOWED_TAGS,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    YOUTUBE_HOSTS,
)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_http_url(value):
    if not value:
        return False
    parts = urlsplit(value.strip())
    return parts.scheme in {"http", "https"} and bool(parts.netloc)


def _safe_youtube_id(video_id):
    video_id = (video_id or "").strip()
    if not (6 <= len(video_id) <= 32):
        return ""
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    return video_id if all(ch in allowed for ch in video_id) else ""


def youtube_embed_url(value):
    if not is_http_url(value):
        return None

    parts = urlsplit(value.strip())
    host = (parts.netloc or "").lower()
    host_no_www = host[4:] if host.startswith("www.") else host
    if host not in YOUTUBE_HOSTS and host_no_www not in YOUTUBE_HOSTS:
        return None

    path = (parts.path or "").strip("/")
    video_id = ""
    if host_no_www == "youtu.be":
        video_id = path.split("/", 1)[0]
    elif path == "watch":
        video_id = parse_qs(parts.query).get("v", [""])[0]
    elif path.startswith(("shorts/", "embed/", "live/")):
        video_id = path.split("/", 1)[1].split("/", 1)[0]

    video_id = _safe_youtube_id(video_id)
    if not video_id:
        return None
    return f"https://www.youtube.com/embed/{video_id}"


def _media_ext(value):
    if not value:
        return ""
    path = urlsplit(value).path if is_http_url(value) else value
    path = (path or "").lower()
    return path.rsplit(".", 1)[1] if "." in path else ""


def media_kind(value):
    if not value:
        return None
    if youtube_embed_url(value):
        return "youtube"
    ext = _media_ext(value)
    if ext in VIDEO_EXTENSIONS:
        return "video"
    if ext in IMAGE_EXTENSIONS:
        return "image"
    return None


def media_src(value):
    if not value:
        return ""
    yt = youtube_embed_url(value)
    if yt:
        return yt
    if is_http_url(value):
        return value.strip()
    return "/" + value.lstrip("/")


def allowed_external_media_url(value):
    if not is_http_url(value):
        return False
    if youtube_embed_url(value):
        return True
    return _media_ext(value) in ALLOWED_EXTENSIONS


def sanitize_body(text):
    return bleach.clean(
        text or "",
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols={"http", "https", "mailto"},
        strip=True,
    ).strip()
