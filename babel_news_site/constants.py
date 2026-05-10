IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
VIDEO_EXTENSIONS = {"mp4", "mov", "mkv", "webm"}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
}

ALLOWED_TAGS = [
    "br",
    "p",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "ul",
    "ol",
    "li",
    "a",
    "blockquote",
]
ALLOWED_ATTRS = {"a": ["href", "title", "target", "rel"]}

ABOUT_SECTION = "من نحن"
ABOUT_TEXT = (
    "وكالة عيون بابل الإخبارية - منصة إعلامية تهدف إلى نقل الأخبار المحلية "
    "والوطنية بكفاءة وشفافية، وتسليط الضوء على قضايا المجتمع في محافظة بابل "
    "والمنطقة المحيطة."
)

SECTIONS = {
    "اخبار": ["محلية", "عراقية", "دولية", "رياضة", "تكنولوجيا", "اقتصاد"],
    "تقارير": ["تحليل", "ميدانية", "رأي"],
    "وثائقيات": ["علمية", "تاريخية", "مجتمعية"],
    "برامج": ["مقابلات", "بودكاست", "منوعات"],
    "تنمية": ["الحديث الشريف لهذا اليوم", "حكمة اليوم", "حدث في مثل هذا اليوم"],
    "فقط في العراق": ["فقط في العراق"],
    ABOUT_SECTION: [ABOUT_SECTION],
}

WRITER_SECTIONS = {
    section: sublabels
    for section, sublabels in SECTIONS.items()
    if section != ABOUT_SECTION
}
