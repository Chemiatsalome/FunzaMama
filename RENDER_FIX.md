# 🔧 Fixing Render Deployment - Gunicorn Not Found

## Problem
Render is showing: `bash: line 1: gunicorn: command not found`

This means gunicorn isn't being installed during the build process.

## ✅ Solution

### Option 1: Fix Build Command in Render Dashboard (Recommended)

1. **Go to your Render Dashboard**
2. **Click on your Web Service**
3. **Go to "Settings" tab**
4. **Scroll to "Build & Deploy" section**
5. **Set these values:**

   **Build Command:**
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```

   **Start Command:**
   ```
   gunicorn app:app
   ```

6. **Save changes**
7. **Click "Manual Deploy" → "Deploy latest commit"**

### Option 2: Verify requirements.txt is Committed

Make sure your `requirements.txt` includes gunicorn and is committed to Git:

```bash
# Check if gunicorn is in requirements.txt
grep gunicorn requirements.txt

# If not, add it:
echo "gunicorn>=21.2.0" >> requirements.txt

# Commit and push:
git add requirements.txt
git commit -m "Add gunicorn to requirements"
git push origin main
```

### Option 3: Use render.yaml (Alternative)

I've created a `render.yaml` file for you. To use it:

1. **Commit the render.yaml file:**
   ```bash
   git add render.yaml
   git commit -m "Add render.yaml configuration"
   git push origin main
   ```

2. **In Render Dashboard:**
   - Go to your service → Settings
   - Enable "Auto-Deploy" if not already enabled
   - Render will use the render.yaml configuration

### Option 4: Check Python Version

Render might be using an incompatible Python version. Create `runtime.txt`:

```bash
# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Commit it:
git add runtime.txt
git commit -m "Specify Python version"
git push origin main
```

I've already created this file for you!

## 🔍 Debugging Steps

### 1. Check Build Logs

In Render Dashboard:
- Go to your service
- Click on "Logs" tab
- Look for the build process
- Check if `pip install -r requirements.txt` is running
- Verify gunicorn is being installed

### 2. Verify requirements.txt Format

Your `requirements.txt` should have:
```
gunicorn>=21.2.0
psycopg2-binary>=2.9.9
```

### 3. Test Build Command Locally

Test if the build works locally:

```bash
# Create a virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Verify gunicorn is installed
which gunicorn  # On Windows: where gunicorn
gunicorn --version
```

## 📝 Complete Render Configuration

### Environment Variables (Set in Render Dashboard)

Go to your service → Environment → Add these:

```bash
FLASK_ENV=production
DATABASE_URL=<your-postgresql-url>
SECRET_KEY=<your-secret-key>
PORT=10000
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=chemiatsalome@gmail.com
MAIL_PASSWORD=<your-gmail-app-password>
PREFERRED_URL_SCHEME=https
SERVER_NAME=<your-app-name>.onrender.com
```

### Build Settings

**Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```
gunicorn app:app
```

## ✅ After Fixing

1. **Redeploy:**
   - Go to Render Dashboard
   - Click "Manual Deploy" → "Deploy latest commit"
   - Watch the build logs

2. **Verify:**
   - Check build logs for "Successfully installed gunicorn"
   - Check that the service starts without errors
   - Visit your app URL

3. **Test:**
   - Home page loads
   - User registration works
   - Database connection works

## 🚨 Still Not Working?

If gunicorn still isn't found:

1. **Check Python version compatibility:**
   - Ensure Python 3.9+ is being used
   - Add `runtime.txt` with `python-3.11.0`

2. **Try alternative start command:**
   ```
   python -m gunicorn app:app
   ```

3. **Check for build errors:**
   - Look for any errors during `pip install`
   - Some packages might be failing to install
   - Check if all dependencies are compatible

4. **Contact Render Support:**
   - They're very helpful
   - Share your build logs
   - They can help debug the issue

## 💡 Pro Tips

1. **Always check build logs first** - they show what's happening
2. **Use explicit versions** in requirements.txt for stability
3. **Test locally first** - if it works locally, it should work on Render
4. **Keep requirements.txt updated** - remove unused packages

Good luck! 🚀
