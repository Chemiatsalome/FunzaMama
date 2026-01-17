# 🚂 Railway Deployment Guide for Funza Mama

Railway is an excellent choice for deployment! It offers:
- ✅ **Free tier with $5 credit/month** (usually enough for small-medium apps)
- ✅ **Very easy setup** - just connect GitHub
- ✅ **PostgreSQL included** - no separate database setup needed
- ✅ **Automatic HTTPS** - SSL certificates included
- ✅ **Simple environment variables** - easy to manage
- ✅ **No credit card required** for free tier

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [x] Code is pushed to GitHub
- [x] `requirements.txt` includes all dependencies
- [x] `Procfile` exists (Railway can auto-detect, but it's good to have)
- [x] `app.py` has `debug=False` for production
- [x] Environment variables are documented

---

## 🚀 Step-by-Step Railway Deployment

### Step 1: Push Code to GitHub

If you haven't already:

```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 2: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (recommended - easiest way)
4. Authorize Railway to access your repositories

### Step 3: Create New Project

1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select your **FunzaMama** repository
4. Railway will automatically detect it's a Python project

### Step 4: Add PostgreSQL Database

1. In your project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically:
   - Creates the database
   - Provides `DATABASE_URL` environment variable
   - Connects it to your app

**Note:** The `DATABASE_URL` is automatically available to your app - no manual setup needed!

### Step 5: Configure Your Web Service

Railway should have automatically created a web service. If not:

1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repository again
3. Railway will detect it's a web service

### Step 6: Set Environment Variables

1. Click on your **Web Service** (not the database)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** and add each:

```bash
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
PREFERRED_URL_SCHEME=https
```

**To generate SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

**Important:** 
- Use your **Gmail App Password** (not regular password) for `MAIL_PASSWORD`
- The `DATABASE_URL` is automatically set by Railway - **don't add it manually**

### Step 7: Configure Build Settings (Optional)

Railway usually auto-detects, but you can verify:

1. Click on your **Web Service**
2. Go to **"Settings"** tab
3. Under **"Build Command"**, it should be:
   ```
   pip install -r requirements.txt
   ```
4. Under **"Start Command"**, it should be:
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```

If these aren't set, add them manually.

**⚠️ IMPORTANT: Clear Build Cache**
If you're having deployment issues, clear the build cache:
1. Go to **Settings** → **Build & Deploy**
2. Click **"Clear Build Cache"** or **"Redeploy"** → **"Clear cache and redeploy"**
3. This ensures Railway uses your latest configuration files

### Step 8: Deploy!

1. Railway automatically deploys when you:
   - Push to your main branch, OR
   - Click **"Deploy"** in the dashboard

2. Watch the deployment logs:
   - Click on your **Web Service**
   - Go to **"Deployments"** tab
   - Click on the latest deployment
   - Watch the build logs

3. Wait for deployment to complete (5-10 minutes)

### Step 9: Get Your App URL

1. Once deployed, Railway provides a URL like:
   ```
   https://your-app-name.up.railway.app
   ```

2. To get a custom domain (optional):
   - Go to **"Settings"** → **"Networking"**
   - Add your custom domain
   - Update DNS as instructed

### Step 10: Initialize Database

1. Railway provides a **"Shell"** feature:
   - Click on your **Web Service**
   - Go to **"Deployments"** tab
   - Click **"..."** → **"Open Shell"**

2. In the shell, run:
   ```bash
   flask db upgrade
   ```
   
   Or if you don't have migrations:
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   ```

3. Your database tables will be created automatically!

### Step 11: Test Your Deployment

Visit your Railway URL and test:
- ✅ Home page loads
- ✅ User registration works
- ✅ Email verification (check your email)
- ✅ Login works
- ✅ Quiz functionality
- ✅ Avatar uploads
- ✅ Profile page

---

## 💰 Railway Pricing

### Free Tier:
- **$5 credit/month** (usually enough for small-medium apps)
- PostgreSQL database included
- Automatic HTTPS
- Unlimited deployments
- 500 hours of usage/month

### If You Need More:
- **Hobby Plan:** $5/month (if you exceed free tier)
- **Pro Plan:** $20/month (for production apps)

**For most apps, the free tier is sufficient!**

---

## 🔧 Railway-Specific Tips

### 1. Monitor Usage

1. Go to **"Settings"** → **"Usage"**
2. Check your monthly credit usage
3. Railway shows real-time usage

### 2. View Logs

1. Click on your **Web Service**
2. Go to **"Deployments"** tab
3. Click on any deployment to see logs
4. Or use **"Logs"** tab for real-time logs

### 3. Environment Variables

- Railway automatically provides `DATABASE_URL`
- All variables are encrypted
- You can add/remove variables anytime
- Changes trigger automatic redeployment

### 4. Custom Domain

1. Go to **"Settings"** → **"Networking"**
2. Click **"Custom Domain"**
3. Add your domain
4. Update DNS records as shown
5. Railway handles SSL automatically

### 5. Database Management

- Railway provides a database URL
- You can connect using any PostgreSQL client
- Use Railway's **"Data"** tab to view database
- Or use **"Shell"** to run SQL commands

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Check:**
- All dependencies in `requirements.txt`
- Python version compatibility
- Build logs for specific errors

**Solution:**
- Check Railway deployment logs
- Ensure `requirements.txt` is up to date
- Try building locally first: `pip install -r requirements.txt`

### Issue: App Crashes on Startup

**Check:**
- Environment variables are set
- Database connection works
- Port is set correctly (Railway uses `PORT` env var)

**Solution:**
- Check application logs in Railway
- Verify all environment variables
- Ensure `DATABASE_URL` is available (Railway sets it automatically)

### Issue: Database Connection Error

**Solution:**
- Railway automatically provides `DATABASE_URL`
- Ensure `FLASK_ENV=production` is set
- Check that database service is running
- Verify database is connected to your web service

### Issue: Static Files Not Loading

**Solution:**
- Ensure `static/` folder is in repository
- Check file paths in templates
- Verify `url_for('static', ...)` is used correctly
- Check Railway logs for 404 errors

### Issue: Email Not Sending

**Solution:**
- Verify Gmail app password is correct
- Check `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS` are set
- Ensure `MAIL_USERNAME` and `MAIL_PASSWORD` are correct
- Check Railway logs for SMTP errors

### Issue: Out of Credits

**Solution:**
- Check usage in **"Settings"** → **"Usage"**
- Optimize your app (reduce memory usage)
- Consider upgrading to Hobby plan ($5/month)
- Or switch to Render/Heroku if needed

---

## 📊 Monitoring Your App

### View Logs:
1. Click on your **Web Service**
2. Go to **"Logs"** tab for real-time logs
3. Or **"Deployments"** → Click deployment → View logs

### Monitor Usage:
1. Go to **"Settings"** → **"Usage"**
2. See real-time credit usage
3. Track database size, bandwidth, etc.

### Check Health:
- Railway automatically monitors your app
- Failed deployments are marked
- You'll get notifications for issues

---

## 🎯 Next Steps After Deployment

1. **Test Everything:**
   - User registration
   - Email verification
   - Quiz functionality
   - File uploads

2. **Set Up Custom Domain** (optional):
   - Add domain in Railway settings
   - Update DNS records
   - Update `SERVER_NAME` if needed

3. **Monitor Performance:**
   - Check logs regularly
   - Monitor usage
   - Optimize if needed

4. **Backup Database:**
   - Railway provides automatic backups
   - Or export manually using Railway Shell

---

## 🎉 Success!

Your Funza Mama app is now live on Railway! 🚂

**Your app URL will be:**
```
https://your-app-name.up.railway.app
```

**Remember:**
- ✅ Monitor your usage (free tier has $5/month credit)
- ✅ Check logs regularly
- ✅ Keep dependencies updated
- ✅ Backup your database
- ✅ Keep your SECRET_KEY secure

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway Discord Community](https://discord.gg/railway)
- [Railway Pricing](https://railway.app/pricing)

---

## 💡 Pro Tips

1. **Optimize for Free Tier:**
   - Use efficient database queries
   - Optimize static file sizes
   - Cache when possible

2. **Use Railway's Features:**
   - Automatic deployments on git push
   - Environment variable management
   - Database backups

3. **Monitor Costs:**
   - Check usage dashboard regularly
   - Set up usage alerts if needed
   - Optimize before upgrading

Good luck with your deployment! 🚀
