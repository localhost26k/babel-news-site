# وكالة عيون بابل

موقع أخبار عربي مبني بـ Flask و SQLite. تم ترتيب المشروع كحزمة Flask واضحة مع فصل الكود عن القوالب والملفات الثابتة والبيانات runtime.

## التشغيل المحلي

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

افتح:

```text
http://127.0.0.1:5000/
```

دخول الكادر التحريري:

```text
http://127.0.0.1:5000/writer/login
المستخدم الافتراضي: EOB
```

اضبط كلمة مرور الكاتب من متغير البيئة `DEFAULT_WRITER_PASSWORD`. لا تضع كلمة المرور الحقيقية داخل الملفات التي سترفعها للإنترنت.

## النشر

المشروع جاهز للنشر كتطبيق Flask عبر Gunicorn:

```text
gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

يوجد ملف `render.yaml` جاهز للنشر المجاني على Render كـ Blueprint. راجع `DEPLOYMENT.md` للخطوات الكاملة وملاحظات حدود الخطة المجانية.

إذا أردت إنشاء Web Service يدويا على Render أو Railway:

```text
Build command: pip install -r requirements.txt
Start command: gunicorn --bind 0.0.0.0:$PORT wsgi:app
Health check path: /healthz
```

متغيرات البيئة المطلوبة في لوحة الاستضافة:

```text
FLASK_SECRET_KEY=<قيمة عشوائية طويلة>
DEFAULT_WRITER_USER=EOB
DEFAULT_WRITER_PASSWORD=<كلمة مرور الكاتب>
SESSION_COOKIE_SECURE=1
```

إذا كان الموقع سيستخدم SQLite ورفع الصور/الفيديوهات، اربط قرصا دائما أو مساحة تخزين دائمة واضبط:

```text
BABEL_NEWS_DATABASE=/data/site.db
BABEL_NEWS_UPLOAD_FOLDER=/data/uploads
BABEL_NEWS_PUBLIC_UPLOAD_PREFIX=uploads
```

بدون تخزين دائم، قد تضيع قاعدة البيانات والملفات المرفوعة عند إعادة النشر على بعض منصات الاستضافة.

يمكن استخدام `.env.example` كمرجع للمتغيرات.

## البنية

```text
babel_news_site/
  babel_news_site/
    __init__.py       Flask app factory
    app.py            entry point compatible with old python app.py usage
    config.py         environment and filesystem config
    constants.py      sections and media allowlists
    db.py             SQLite schema and seed user
    media.py          upload, URL, YouTube, and body sanitizing helpers
    routes.py         public and writer routes
    security.py       login guard and CSRF protection
    static/           CSS, logo, uploads
    templates/        Jinja templates
  instance/site.db    local SQLite database
  tests/              unittest coverage for core behavior
  run.py              local development server
  wsgi.py             production WSGI entry
```

## الاختبارات

```powershell
python -m unittest discover -s tests
```
