# Switch to Resend API (Railway Email Solution)

## 🎯 What Changed & Why

### Problem
Railway **blocks outbound SMTP connections** (ports 587/465). Your app was trying to send emails via SMTP, which resulted in:
```
OSError: [Errno 101] Network is unreachable
```

### Solution
Switched to **Resend API** which uses HTTPS (port 443) - allowed on Railway.

## ✅ What I Did

1. **Added `resend` package** to `requirements.txt`
2. **Rewrote `EmailService`** to:
   - Use **Resend API** when `EMAIL_PROVIDER=resend` (Railway)
   - Fall back to **SMTP** for local development
   - Keep the same HTML email templates
   - Automatically detect Railway environment

## 🔧 Railway Variables Setup

### ❌ REMOVE These (SMTP - won't work on Railway):
```
MAIL_SERVER
MAIL_PORT
MAIL_USE_TLS
MAIL_USERNAME
MAIL_PASSWORD
```

### ✅ ADD These (Resend API):
```
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxx
MAIL_FROM=FunzaMama <onboarding@resend.dev>
```

## 📋 Step-by-Step Setup

### 1. Create Resend Account

1. Go to https://resend.com
2. Sign up (free tier available)
3. Verify your email

### 2. Get API Key

1. Go to **API Keys** section
2. Click **"Create API Key"**
3. Name it (e.g., "FunzaMama Production")
4. Copy the key (starts with `re_`)

### 3. Set Railway Variables

**Go to Railway Dashboard → Your Project → Web Service → Variables**

**Add these 3 variables:**
- `EMAIL_PROVIDER` = `resend`
- `RESEND_API_KEY` = `re_your_actual_api_key_here`
- `MAIL_FROM` = `FunzaMama <onboarding@resend.dev>`

**Remove these (if present):**
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USE_TLS`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`

### 4. Deploy

Railway will auto-deploy when you push changes. Or manually redeploy.

## 🧪 Testing

After deploying:

1. **Try signing up** a new user
2. **Check Railway logs** - should see:
   ```
   📧 Sending email via Resend API to user@example.com...
   ✅ Email sent successfully via Resend to user@example.com
   ```
3. **Check email inbox** - verification email should arrive

## 📊 How It Works

### On Railway (Production):
```
Your App → Resend API (HTTPS) → User's Email ✅
```

### Local Development (Optional SMTP):
```
Your App → SMTP (Gmail) → User's Email ✅
```

## 🔍 Email Provider Detection

The `EmailService` automatically detects:
- If `EMAIL_PROVIDER=resend` → Use Resend API
- If `EMAIL_PROVIDER=smtp` or not set → Use SMTP (local only)
- If `PORT` env var is set (Railway) → Suggests Resend

## 📝 Email Templates

**No changes needed!** The same beautiful HTML email templates are used for both Resend and SMTP.

## ⚠️ Important Notes

1. **Resend free tier**: 3,000 emails/month (plenty for testing)
2. **Domain verification**: Initially uses `onboarding@resend.dev`. To use your own domain:
   - Verify domain in Resend dashboard
   - Update `MAIL_FROM` to use your domain
3. **Local development**: Still works with SMTP if `EMAIL_PROVIDER=smtp` and `MAIL_PASSWORD` is set

## 🚨 Troubleshooting

### Emails Not Sending?

1. **Check `RESEND_API_KEY`**: Must be set and start with `re_`
2. **Check `EMAIL_PROVIDER`**: Must be `resend` (not `smtp`)
3. **Check Railway logs**: Look for Resend API errors
4. **Verify Resend account**: Make sure API key is active

### Still Seeing SMTP Errors?

- Make sure `EMAIL_PROVIDER=resend` is set
- Remove `MAIL_PASSWORD` variable (not needed anymore)
- Redeploy after changing variables

## ✅ Final Checklist

- [ ] Resend account created
- [ ] API key generated (starts with `re_`)
- [ ] Railway variables updated:
  - [ ] `EMAIL_PROVIDER=resend` ✅
  - [ ] `RESEND_API_KEY` set ✅
  - [ ] `MAIL_FROM` set ✅
  - [ ] Old SMTP variables removed ❌
- [ ] Code deployed to Railway
- [ ] Test signup - email received ✅

## 🎉 Result

- ✅ Emails send on Railway (via Resend API)
- ✅ No more "Network unreachable" errors
- ✅ Same beautiful email templates
- ✅ Works locally with SMTP (optional)

---

**Your emails will now work on Railway!** 🚀
