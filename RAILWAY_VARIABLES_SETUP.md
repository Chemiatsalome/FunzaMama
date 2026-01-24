# Railway Variables Setup Guide

## Understanding Railway Variables

Railway has **two types** of environment variables:

1. **Service Variables** - Scoped to a specific service
2. **Shared Variables** - Scoped to the entire project (shared across all services)

### The Warning You're Seeing

```
"graph of shared variable pointed to multiple services"
"Keep variables in sync across services"
```

This means Railway detected that **the same variable names** are being used in multiple services. Railway is **suggesting** to make them shared variables, but this is **optional** and **doesn't prevent emails from being sent**.

## Required Email Variables

For emails to work, you need these variables set:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MAIL_SERVER` | No | `smtp.gmail.com` | SMTP server hostname |
| `MAIL_PORT` | No | `587` | SMTP port |
| `MAIL_USE_TLS` | No | `true` | Enable TLS encryption |
| `MAIL_USERNAME` | **Yes** | `chemiatsalome@gmail.com` | Email address to send from |
| `MAIL_PASSWORD` | **Yes** | - | Gmail App Password (16 chars) |

**Critical**: `MAIL_PASSWORD` must be set or emails won't send!

## Setting Up Variables in Railway

### Option 1: Shared Variables (Recommended)

Shared variables are **project-level** and available to all services. This is cleaner if you have multiple services.

**Steps**:
1. Go to **Railway Dashboard** → Your Project
2. Click on **"Variables"** tab (project level, not service level)
3. Click **"New Variable"** or **"Add Variable"**
4. Add each variable:
   - `MAIL_SERVER` = `smtp.gmail.com`
   - `MAIL_PORT` = `587`
   - `MAIL_USE_TLS` = `true`
   - `MAIL_USERNAME` = `chemiatsalome@gmail.com`
   - `MAIL_PASSWORD` = `your-16-char-app-password` ⚠️ **REQUIRED**

**Benefits**:
- ✅ One place to manage variables
- ✅ Automatically synced across all services
- ✅ Eliminates the warning message
- ✅ Easier to maintain

### Option 2: Service Variables (Current Setup)

If variables are already set at the **service level**, that works too! You can:

**Keep them as-is** (they work fine)
- Just ignore the Railway warning
- It's informational only

**OR convert to shared** (cleaner):
1. Go to Project → **Variables** (project level)
2. Click **"Add Variable"** for each
3. Railway will prompt to "promote" existing service variables
4. Click **"Promote to Shared"** when prompted

## Your Current Variables (from what you showed)

Based on your list, you have these variables set (which is good!):

✅ `DATABASE_URL` - Database connection (auto-provided by Railway)
✅ `MAIL_PASSWORD` - Email password (required for sending)
✅ `MAIL_USERNAME` - Email username
✅ `MAIL_SERVER` - SMTP server
✅ `MAIL_PORT` - SMTP port
✅ `MAIL_USE_TLS` - TLS setting
✅ `SECRET_KEY` - Flask secret key
✅ `PREFERRED_URL_SCHEME` - URL scheme (https)

**These look correct!** ✅

## Troubleshooting Email Not Sending

### 1. Verify MAIL_PASSWORD is Set

**Most common issue**: `MAIL_PASSWORD` not set or incorrect.

Check in Railway:
1. Go to **Variables** tab
2. Look for `MAIL_PASSWORD`
3. Should be **16 characters** (Gmail App Password)
4. **No spaces** (Railway sometimes adds them, code strips them)

### 2. Check Railway Logs

Look for these messages in Railway logs:

**Good signs**:
```
📧 Attempting to send verification email...
✅ Verification email sent successfully to...
```

**Bad signs**:
```
⚠️ Email password not configured
❌ SMTP Authentication Error
❌ SMTP Error
```

### 3. Verify Gmail App Password

If using Gmail (`MAIL_USERNAME` ends with `@gmail.com`):

1. **Must be an App Password**, not regular password
2. **16 characters** (no spaces)
3. **2-Step Verification** must be enabled
4. Generate at: https://myaccount.google.com/apppasswords

### 4. Test Email Configuration

You can test locally (if you have Railway CLI) or check Railway logs when you try to sign up.

## Quick Fix: Create Shared Variables

To eliminate the warning and organize variables:

1. **Go to Railway Dashboard** → Your Project
2. **Click "Variables"** (top-level, not under a service)
3. **Click "New Variable"**
4. **Add these if missing**:
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=chemiatsalome@gmail.com
   MAIL_PASSWORD=your-16-char-password
   ```
5. **If variables already exist in service**, Railway will ask to **"Promote to Shared"** - click yes

## Important Notes

### The Warning Doesn't Block Emails

The "shared variables" warning is **just Railway suggesting better organization**. Your emails will still send if:
- ✅ `MAIL_PASSWORD` is set correctly
- ✅ `MAIL_USERNAME` is set correctly
- ✅ Variables are accessible to your app service

### Variable Priority

If a variable exists in **both** service and shared:
- **Service variable** takes priority (overrides shared)
- This is usually fine, but can cause confusion

### Recommendation

**Make email variables shared** because:
- They're used by the same service (your app)
- Easier to manage in one place
- Eliminates the warning
- Better organization

## Checklist

- [ ] `MAIL_PASSWORD` is set (16 characters, Gmail App Password)
- [ ] `MAIL_USERNAME` is set (your Gmail address)
- [ ] `MAIL_SERVER` is set (or defaults to `smtp.gmail.com`)
- [ ] `MAIL_PORT` is set (or defaults to `587`)
- [ ] `MAIL_USE_TLS` is set (or defaults to `true`)
- [ ] Variables are accessible to your app service
- [ ] Test by signing up a new user
- [ ] Check Railway logs for email sending errors

## Still Having Issues?

If emails still don't send after checking variables:

1. **Check Railway logs** for SMTP errors
2. **Verify Gmail App Password** is correct
3. **Test locally** with `test_email.py` script
4. **Check firewall** (Railway should allow outbound SMTP)
5. **Verify SMTP timeout** - we added 10s timeout, should be enough

---

**Remember**: The warning is just organizational. Focus on making sure `MAIL_PASSWORD` is set correctly! 🎯
