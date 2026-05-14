# Deployment

This project is ready to deploy on Render as a Flask app served by Gunicorn.

## PythonAnywhere Free Setup

PythonAnywhere is a better free fit for this project than Render Free if you
want SQLite posts and uploaded files to survive restarts. The free account has a
small persistent disk quota, so do not upload very large videos directly.

### 1. Create The Account

Create a free Beginner account at PythonAnywhere. Your free URL will be:

```text
https://YOUR_USERNAME.pythonanywhere.com
```

Free accounts currently provide one web app and 512 MiB of private file storage.

### 2. Open A Bash Console

In PythonAnywhere, open **Consoles** -> **Bash**, then run:

```bash
git clone https://github.com/localhost26k/babel-news-site.git ~/babel-news-site
cd ~/babel-news-site
mkvirtualenv --python=/usr/bin/python3.13 babel-news-site
pip install -r requirements.txt
mkdir -p ~/babel-news-data/uploads
```

### 3. Configure The Web App

1. Go to the **Web** tab.
2. Click **Add a new web app**.
3. Choose **Manual configuration**.
4. Pick the same Python version you used for the virtualenv.
5. In **Virtualenv**, enter:

```text
/home/YOUR_USERNAME/.virtualenvs/babel-news-site
```

6. Open the WSGI file link in the **Code** section.
7. Replace its contents with the contents of `pythonanywhere_wsgi.py`.
8. Replace every `YOUR_USERNAME` with your PythonAnywhere username.
9. Replace these placeholder values:

```python
os.environ.setdefault("DEFAULT_WRITER_PASSWORD", "CHANGE_THIS_PASSWORD")
os.environ.setdefault("FLASK_SECRET_KEY", "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET")
```

Use a real writer password and a long random secret key.

### 4. Static Files

In the **Static files** section of the Web tab, add:

```text
URL: /static/
Directory: /home/YOUR_USERNAME/babel-news-site/babel_news_site/static/
```

Uploaded media is served by Flask from `/uploads/...`, so it does not need a
static files mapping.

### 5. Reload

Click the green **Reload** button on the Web tab, then open:

```text
https://YOUR_USERNAME.pythonanywhere.com/writer/login
```

Use:

```text
Username: EOB
Password: the DEFAULT_WRITER_PASSWORD value you set in the WSGI file
```

### 6. Update Later

When I push changes to GitHub, update PythonAnywhere from a Bash console:

```bash
cd ~/babel-news-site
git pull
workon babel-news-site
pip install -r requirements.txt
```

Then click **Reload** in the Web tab.

Your persistent data lives outside the repo here:

```text
/home/YOUR_USERNAME/babel-news-data/site.db
/home/YOUR_USERNAME/babel-news-data/uploads/
```

Do not delete that folder unless you intentionally want to delete posts/uploads.

The included `render.yaml` is configured for Render's Free web service plan. It creates:

- a Python web service named `babel-news-site`
- a Free instance in the Frankfurt region
- generated secret configuration
- a `/healthz` health check

Important: this free setup does not include persistent disk storage. SQLite data and uploaded files can disappear after redeploys, restarts, or other filesystem resets. Use it for testing, previews, and learning the deployment flow.

If you later want the safer paid setup with persistent SQLite/uploads, copy `render.paid.yaml` over `render.yaml` before deploying or upgrade the service and attach a persistent disk.

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
