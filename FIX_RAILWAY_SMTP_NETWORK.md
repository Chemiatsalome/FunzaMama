# Fix Railway SMTP Network Error

## Problem

```
OSError: [Errno 101] Network is unreachable
```

Railway cannot connect to Gmail's SMTP server (`smtp.gmail.com:587`).

## Why This Happens

Railway's network may be blocking outbound SMTP connections on port 587, or there may be DNS/network configuration issues.

## Solutions

### Option 1: Try Port 465 with SSL (Recommended First)

Gmail supports both:
- **Port 587** with TLS (STARTTLS)
- **Port 465** with SSL (direct SSL)

Try changing to port 465:

**In Railway Dashboard → Variables**:
- Set `MAIL_PORT` = `465`
- Set `MAIL_USE_TLS` = `false` (SSL doesn't use STARTTLS)

Then update `utils/email_service.py` to support SSL on port 465.

### Option 2: Use SendGrid (Best for Production)

SendGrid is email service designed for cloud platforms and works reliably on Railway.

**Benefits**:
- ✅ Free tier: 100 emails/day
- ✅ Designed for cloud platforms
- ✅ Reliable on Railway
- ✅ Better deliverability
- ✅ No SMTP blocking issues

**Setup**:
1. Sign up at https://sendgrid.com (free tier)
2. Create API Key
3. Set Railway Variables:
   ```
   MAIL_SERVER=smtp.sendgrid.net
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=apikey
   MAIL_PASSWORD=your-sendgrid-api-key
   ```

### Option 3: Use Mailgun

Another email service provider that works well on Railway.

**Setup**:
1. Sign up at https://mailgun.com (free tier: 5,000 emails/month)
2. Get SMTP credentials
3. Set Railway Variables:
   ```
   MAIL_SERVER=smtp.mailgun.org
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-mailgun-username
   MAIL_PASSWORD=your-mailgun-password
   ```

### Option 4: Check Railway Network Settings

1. **Check if Railway allows outbound SMTP**:
   - Some Railway regions may block port 587
   - Try a different Railway region if available

2. **Check DNS resolution**:
   - Railway should resolve `smtp.gmail.com`
   - Check Railway logs for DNS errors

3. **Verify Gmail App Password**:
   - Ensure you're using App Password, not regular password
   - 2-Step Verification must be enabled

## Quick Test: Port 465 with SSL

Try this first - it's the easiest fix:

1. **Update Railway Variables**:
   ```
   MAIL_PORT=465
   MAIL_USE_TLS=false
   ```

2. **Update `utils/email_service.py`** to support SSL:
   ```python
   # Change SMTP connection to support SSL on port 465
   if self.smtp_port == 465:
       # Use SMTP_SSL for port 465
       context = ssl.create_default_context()
       server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10)
   else:
       # Use regular SMTP with STARTTLS for port 587
       server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
       if self.use_tls:
           server.starttls(context=context)
   ```

## Recommended Solution

**For Production**: Use **SendGrid** - it's designed for cloud platforms and works reliably on Railway.

**For Quick Fix**: Try **port 465 with SSL** first - no external service needed.

## Testing

After applying fix:

1. **Try password reset** again
2. **Check Railway logs** - should see successful SMTP connection
3. **Check email inbox** - should receive email

---

**Note**: The application context fix is working correctly - the email thread has proper Flask context. The only issue now is Railway's network connectivity to Gmail SMTP.
