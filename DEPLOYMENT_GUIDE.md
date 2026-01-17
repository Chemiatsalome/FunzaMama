# 🚀 Funza Mama Deployment Guide

This guide will help you deploy your Funza Mama Flask application to production.

## 📋 Table of Contents
1. [Recommended Platforms](#recommended-platforms)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deploy to Render (Recommended)](#deploy-to-render-recommended)
4. [Deploy to Railway](#deploy-to-railway)
5. [Deploy to Heroku](#deploy-to-heroku)
6. [Post-Deployment Steps](#post-deployment-steps)
7. [Troubleshooting](#troubleshooting)

---

## 🌟 Recommended Platforms

### 1. **Render** (⭐ Best for Beginners)
- ✅ Free tier available
- ✅ PostgreSQL database included
- ✅ Automatic HTTPS
- ✅ Easy environment variable management
- ✅ Simple deployment from GitHub
- ✅ Good documentation

### 2. **Railway**
- ✅ Very easy to use
- ✅ Free tier with $5 credit/month
- ✅ PostgreSQL included
- ✅ One-click deployment

### 3. **Heroku**
- ⚠️ No longer has free tier (paid only)
- ✅ Very mature platform
- ✅ Excellent documentation
- ✅ Add-ons marketplace

### 4. **DigitalOcean App Platform**
- ✅ Simple and scalable
- ✅ $5/month starting price
- ✅ Good performance

---

## ✅ Pre-Deployment Checklist

Before deploying, ensure you have:

- [x] All code committed to Git
- [x] `requirements.txt` includes all dependencies
- [x] `Procfile` exists (for Heroku/Render)
- [x] Environment variables documented
- [x] Database migrations ready
- [x] Static files organized
- [x] Email configuration ready
- [x] Debug mode disabled in production

---

## 🎯 Deploy to Render (Recommended)

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Ensure these files exist:**
   - ✅ `Procfile` (with capital P)
   - ✅ `requirements.txt`
   - ✅ `wsgi.py`

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended)
3. Connect your GitHub account

### Step 3: Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Name it: `funzamama-db`
3. Select **"Free"** plan
4. Choose your region
5. Click **"Create Database"**
6. **Copy the Internal Database URL** (you'll need this)

### Step 4: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select your `FunzaMama` repository
4. Configure:
   - **Name:** `funzamama-app`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free

### Step 5: Set Environment Variables

In your Render Web Service dashboard, go to **"Environment"** and add:

```bash
# Database
DATABASE_URL=<your-postgresql-internal-url-from-step-3>

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<generate-a-random-secret-key>
PORT=10000

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=chemiatsalome@gmail.com
MAIL_PASSWORD=<your-gmail-app-password>

# Server Configuration
SERVER_NAME=<your-app-name>.onrender.com
PREFERRED_URL_SCHEME=https
```

**To generate SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Build your app
   - Start the service

3. Wait for deployment to complete (5-10 minutes)

### Step 7: Initialize Database

1. Once deployed, open your app URL
2. The app will automatically create tables on first run
3. Or use Flask-Migrate:
   ```bash
   # In Render Shell (available in dashboard)
   flask db upgrade
   ```

### Step 8: Test Your Deployment

- ✅ Visit your app URL
- ✅ Test user registration
- ✅ Test email verification
- ✅ Test quiz functionality
- ✅ Check logs for errors

---

## 🚂 Deploy to Railway

### Step 1: Install Railway CLI (Optional)

```bash
npm i -g @railway/cli
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository

### Step 3: Add PostgreSQL

1. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway automatically provides `DATABASE_URL` environment variable

### Step 4: Set Environment Variables

In Railway dashboard → **"Variables"** tab, add:

```bash
FLASK_ENV=production
SECRET_KEY=<your-secret-key>
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=chemiatsalome@gmail.com
MAIL_PASSWORD=<your-gmail-app-password>
PREFERRED_URL_SCHEME=https
```

### Step 5: Deploy

Railway automatically detects your `Procfile` and deploys!

---

## 🟣 Deploy to Heroku

### Step 1: Install Heroku CLI

Download from [heroku.com/cli](https://devcenter.heroku.com/articles/heroku-cli)

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Create Heroku App

```bash
heroku create funzamama-app
```

### Step 4: Add PostgreSQL Add-on

```bash
heroku addons:create heroku-postgresql:mini
```

### Step 5: Set Environment Variables

```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=<your-secret-key>
heroku config:set MAIL_SERVER=smtp.gmail.com
heroku config:set MAIL_PORT=587
heroku config:set MAIL_USE_TLS=true
heroku config:set MAIL_USERNAME=chemiatsalome@gmail.com
heroku config:set MAIL_PASSWORD=<your-gmail-app-password>
heroku config:set PREFERRED_URL_SCHEME=https
```

### Step 6: Deploy

```bash
git push heroku main
```

### Step 7: Initialize Database

```bash
heroku run flask db upgrade
```

---

## 📝 Post-Deployment Steps

### 1. Update Email Configuration

Update `SERVER_NAME` in environment variables to match your deployment URL:
- Render: `your-app-name.onrender.com`
- Railway: `your-app-name.up.railway.app`
- Heroku: `your-app-name.herokuapp.com`

### 2. Test Email Functionality

1. Register a new user
2. Check email inbox for verification email
3. Test password reset functionality

### 3. Set Up Custom Domain (Optional)

1. In your platform dashboard, go to **"Custom Domains"**
2. Add your domain
3. Update DNS records as instructed
4. Update `SERVER_NAME` environment variable

### 4. Enable HTTPS

Most platforms (Render, Railway, Heroku) provide HTTPS automatically. Ensure:
- `PREFERRED_URL_SCHEME=https` is set
- All URLs use HTTPS

### 5. Monitor Your Application

- Check application logs regularly
- Set up error monitoring (Sentry, etc.)
- Monitor database usage
- Check email delivery rates

---

## 🔧 Troubleshooting

### Issue: Database Connection Error

**Solution:**
- Verify `DATABASE_URL` is set correctly
- Check if database is running
- Ensure database credentials are correct

### Issue: Static Files Not Loading

**Solution:**
- Ensure `static/` folder is in repository
- Check file paths in templates
- Verify `url_for('static', ...)` is used correctly

### Issue: Email Not Sending

**Solution:**
- Verify Gmail app password is correct
- Check SMTP settings
- Ensure environment variables are set
- Check application logs for SMTP errors

### Issue: Application Crashes on Startup

**Solution:**
- Check application logs
- Verify all dependencies in `requirements.txt`
- Ensure `Procfile` is correct
- Check for missing environment variables

### Issue: 500 Internal Server Error

**Solution:**
- Check application logs
- Verify database connection
- Check for missing environment variables
- Ensure all migrations are applied

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)

---

## 🎉 Success!

Once deployed, your Funza Mama application will be live and accessible to users worldwide!

**Remember to:**
- ✅ Keep your dependencies updated
- ✅ Monitor your application logs
- ✅ Backup your database regularly
- ✅ Keep your SECRET_KEY secure
- ✅ Update environment variables as needed

Good luck with your deployment! 🚀
