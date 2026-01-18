# How to Set MAIL_PASSWORD for Email Verification

## 🚨 Current Status
Your app is showing: "Email verification is not configured, so your account has been automatically verified."

This means `MAIL_PASSWORD` is not set, so emails aren't being sent.

## ✅ Fix: Set MAIL_PASSWORD in Railway

### Step 1: Get Gmail App Password

1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Go to **App passwords**: https://myaccount.google.com/apppasswords
4. Select **Mail** and **Other (Custom name)**: "Funza Mama"
5. Click **Generate**
6. Copy the **16-character password** (looks like: `wloqvskriwrlzcrp`)

⚠️ **Important**: This is NOT your Gmail password! It's a special app password.

### Step 2: Set in Railway Dashboard

1. Go to: https://railway.app/dashboard
2. Select your **Web Service** (not the database)
3. Click **Variables** tab
4. Click **+ New Variable**
5. Add:
   - **Name**: `MAIL_PASSWORD`
   - **Value**: Paste your 16-character Gmail app password
6. Click **Add**
7. Railway will **automatically redeploy**

### Step 3: Verify

After Railway redeploys (2-3 minutes):
- Try registering a new user
- You should see: "Registration successful! Please check your email to verify your account."
- Check the user's inbox for the verification email

## 🧪 Test Locally

To test locally, create a `.env` file in your project root:

```env
MAIL_USERNAME=chemiatsalome@gmail.com
MAIL_PASSWORD=wloqvskriwrlzcrp
```

**Note**: `.env` is already in `.gitignore`, so it won't be committed to Git.

## 📧 Current Email Configuration

- **SMTP Server**: `smtp.gmail.com`
- **Port**: `587`
- **TLS**: Enabled
- **Username**: `chemiatsalome@gmail.com` (set in `config.py`)
- **Password**: ⚠️ **MUST BE SET** in Railway Variables or `.env`

Once `MAIL_PASSWORD` is set, email verification will work automatically!
