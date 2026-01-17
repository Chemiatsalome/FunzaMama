# Email Setup Guide for Funza Mama

## Current Issue: SMTP Authentication Error (535)

The error `535, b'5.7.3 Authentication unsuccessful` means Office 365 is rejecting your credentials.

## Solutions

### Option 1: Use Gmail (Recommended - Easier Setup)

Gmail is often easier to configure than Office 365.

#### Steps:
1. **Create a Gmail account** (or use an existing one)
2. **Enable 2-Step Verification**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification
3. **Generate App Password**:
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Other (Custom name)"
   - Enter "Funza Mama" as the name
   - Click "Generate"
   - Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)
4. **Update config.py**:
   ```python
   MAIL_SERVER = 'smtp.gmail.com'
   MAIL_USERNAME = 'your-email@gmail.com'
   MAIL_PASSWORD = 'your-16-char-app-password'  # Remove spaces
   ```

### Option 2: Fix Office 365 Authentication

Office 365 often requires special setup:

#### Steps:
1. **Check if MFA is enabled**:
   - If yes, you MUST use an App Password
   - Go to [Microsoft Account Security](https://account.microsoft.com/security)
   - Create an App Password for "Mail"

2. **Enable SMTP AUTH** (if disabled):
   - This might require admin access
   - Office 365 admin center > Exchange admin center
   - Authentication > SMTP AUTH must be enabled

3. **Try different authentication**:
   - Some Office 365 accounts require OAuth2 (more complex)
   - Or use a different email service

### Option 3: Use a Dedicated Email Service

Consider using:
- **SendGrid** (Free tier: 100 emails/day)
- **Mailgun** (Free tier: 5,000 emails/month)
- **Amazon SES** (Very cheap, pay-as-you-go)

## Quick Test

After updating your credentials, test with:
```bash
python test_email.py
```

## Current Configuration

- **SMTP Server**: `smtp.gmail.com` (changed from Office 365)
- **Port**: 587
- **TLS**: Enabled
- **Username**: Update in `config.py`
- **Password**: Use APP PASSWORD (not regular password)

## Troubleshooting

### Still getting authentication errors?
1. ✅ Make sure you're using an **APP PASSWORD**, not your regular password
2. ✅ For Gmail: Enable 2-Step Verification first
3. ✅ Remove spaces from the app password
4. ✅ Check that SMTP is enabled for your account
5. ✅ Try a different email provider (Gmail is usually easiest)

### For Office 365 specifically:
- Office 365 may have SMTP disabled by default
- Requires admin to enable SMTP AUTH
- May need to use OAuth2 instead of basic auth
- Consider using Gmail or a dedicated email service instead
