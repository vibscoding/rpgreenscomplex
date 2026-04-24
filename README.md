# RP Greens Complex — Website

## Deploy to Railway (Free, 24/7)

### Step 1 — Create GitHub account
Go to https://github.com and sign up (free).

### Step 2 — Upload this project to GitHub
1. Go to https://github.com/new
2. Name it: `rp-greens-website`
3. Click **Create repository**
4. Click **uploading an existing file**
5. Drag and drop ALL files from this folder
6. Click **Commit changes**

### Step 3 — Deploy on Railway
1. Go to https://railway.app
2. Sign in with your GitHub account
3. Click **New Project → Deploy from GitHub repo**
4. Select `rp-greens-website`
5. Railway auto-detects Python and deploys!
6. Click **Settings → Generate Domain** → get your free public URL

### Step 4 — Set Environment Variables (optional but recommended)
In Railway → your project → **Variables**, add:
```
GMAIL_USER = srivastava.vibhuti@gmail.com
GMAIL_PASS = your_gmail_app_password
ADMIN_USER = admin
ADMIN_PASS = your_secure_password
SECRET_KEY = any_random_string_here
```

## Local Development
```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:8000
```

## Admin Panel
Visit: https://your-site.railway.app/admin
Default login: admin / rpgreens2026
