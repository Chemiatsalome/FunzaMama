# Switch to Resend Email API (Fix Railway SMTP Block)

## Why Switch?

**Railway blocks outbound SMTP** (ports 587/465) for security. This is why you're getting:
```
OSError: [Errno 101] Network is unreachable
```

**Solution**: Use Resend (email API over HTTPS) instead of SMTP.

## Quick Setup (5 minutes)

### 1. Create Resend Account

1. Go to **https://resend.com**
2. Sign up (free tier: 3,000 emails/month)
3. Get your **API Key** from dashboard

### 2. Add Railway Variables

In Railway Dashboard → Variables, add:

| Variable | Value |
|----------|-------|
| `RESEND_API_KEY` | `re_xxxxxxxxx` (from Resend dashboard) |
| `MAIL_FROM` | `FunzaMama <onboarding@resend.dev>` (or your verified domain) |

**Note**: You can remove `MAIL_PASSWORD` now (not needed with Resend)

### 3. Deploy

The code now automatically:
- ✅ Uses Resend on Railway (when `RESEND_API_KEY` is set)
- ✅ Uses SMTP locally (when `RESEND_API_KEY` is not set)

## How It Works

The `EmailService` class now detects the environment:

```python
# On Railway: Uses Resend API (HTTPS)
if os.environ.get('RESEND_API_KEY'):
    # Use Resend
else:
    # Use SMTP (local development)
```

## Testing

After deploying:
1. **Sign up** a new user
2. **Check Railway logs** - should see "Using Resend API" instead of SMTP
3. **Check email inbox** - should receive verification email

## Benefits

✅ Works on Railway (no SMTP blocking)
✅ Works locally (still uses SMTP for testing)
✅ No code changes needed in routes
✅ Same email templates and styling
✅ Free tier: 3,000 emails/month
