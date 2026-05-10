# Deployment

This project is ready to deploy on Render as a Flask app served by Gunicorn.

The included `render.yaml` is configured for Render's Free web service plan. It creates:

- a Python web service named `babel-news-site`
- a Free instance in the Frankfurt region
- generated secret configuration
- a `/healthz` health check

Important: this free setup does not include persistent disk storage. SQLite data and uploaded files can disappear after redeploys, restarts, or other filesystem resets. Use it for testing, previews, and learning the deployment flow.

If you later want the safer paid setup with persistent SQLite/uploads, copy `render.paid.yaml` over `render.yaml` before deploying or upgrade the service and attach a persistent disk.

The first free deploy uses a text brand in the header. Upload the logo asset later if you want the image header restored.

## 1. Upload To GitHub

Create a GitHub repository and upload the contents of this folder:

```text
C:\Users\dell\Desktop\PythonProject7\babel_news_site
```

Important: the repository root should contain files like:

```text
render.yaml
requirements.txt
wsgi.py
babel_news_site/
tests/
```

Do not upload the parent `PythonProject7` folder as the repository root unless you also configure Render's root directory.

The existing `.gitignore` keeps local runtime files out of GitHub, including:

- `.venv/`
- `.test_tmp/`
- `instance/site.db`
- `instance/.secret_key`
- uploaded media files
- real `.env` files

## 2. Create The Render Service

1. Open the Render Dashboard.
2. Click **New +**.
3. Choose **Blueprint**.
4. Connect the GitHub repository.
5. Render will read `render.yaml`.
6. When Render asks for `DEFAULT_WRITER_PASSWORD`, enter a strong password for the writer dashboard.
7. Click **Apply** or **Create Blueprint**.

Render will generate `FLASK_SECRET_KEY` automatically. Do not put real passwords in GitHub.

## 3. Expected Render Settings

If you create a normal Web Service manually instead of a Blueprint, use:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT wsgi:app
Health Check Path: /healthz
```

Use these environment variables:

```text
FLASK_SECRET_KEY=<long-random-secret>
DEFAULT_WRITER_USER=EOB
DEFAULT_WRITER_PASSWORD=<writer-password>
SESSION_COOKIE_SECURE=1
MAX_CONTENT_LENGTH=26214400
```

Choose the Free instance type.

For the paid persistent setup, add these extra environment variables:

```text
BABEL_NEWS_DATABASE=/data/site.db
BABEL_NEWS_UPLOAD_FOLDER=/data/uploads
BABEL_NEWS_PUBLIC_UPLOAD_PREFIX=uploads
```

Then attach a persistent disk:

```text
Mount path: /data
Size: 1 GB
```

Without persistent storage, SQLite data and uploaded media can disappear after redeploys on platforms with ephemeral filesystems.

## 4. After Deploy

Open the public Render URL, then visit:

```text
https://your-site.onrender.com/writer/login
```

Use:

```text
Username: EOB
Password: the DEFAULT_WRITER_PASSWORD value you entered in Render
```

## 5. Local Verification

Run tests before publishing:

```powershell
python -m unittest discover -s tests
```
