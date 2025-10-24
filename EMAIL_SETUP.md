# Email Configuration for Funza Mama

## 🚀 Quick Setup (Development)

For development, you can skip email verification by setting users as verified by default.

## 📧 Production Email Setup

### Option 1: Gmail SMTP (Recommended for testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. **Set Environment Variables**:
   ```bash
   export MAIL_USERNAME="your-email@gmail.com"
   export MAIL_PASSWORD="your-app-password"
   ```

### Option 2: Custom SMTP Server

Update `config.py` with your SMTP settings:
```python
MAIL_SERVER = 'your-smtp-server.com'
MAIL_PORT = 587
MAIL_USERNAME = 'your-email@domain.com'
MAIL_PASSWORD = 'your-password'
```

### Option 3: Email Service Providers

#### SendGrid
```python
MAIL_SERVER = 'smtp.sendgrid.net'
MAIL_PORT = 587
MAIL_USERNAME = 'apikey'
MAIL_PASSWORD = 'your-sendgrid-api-key'
```

#### Mailgun
```python
MAIL_SERVER = 'smtp.mailgun.org'
MAIL_PORT = 587
MAIL_USERNAME = 'your-mailgun-username'
MAIL_PASSWORD = 'your-mailgun-password'
```

## 🔧 Environment Variables

Create a `.env` file in your project root:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_USE_TLS=true
```

## 🧪 Testing Email Configuration

Run this test script to verify your email setup:
```python
from utils.email_service import EmailService
from app import app

with app.app_context():
    email_service = EmailService()
    success = email_service.send_verification_email(
        'test@example.com', 
        'Test User', 
        'test-token-123'
    )
    print(f"Email sent: {success}")
```

## 🚨 Troubleshooting

### Common Issues:
1. **"Authentication failed"**: Check your email/password
2. **"Connection refused"**: Check SMTP server and port
3. **"SSL/TLS error"**: Try different ports (587, 465, 25)

### Gmail Specific:
- Use App Passwords, not your regular password
- Enable "Less secure app access" (not recommended)
- Check if 2FA is enabled

## 🔒 Security Notes

- Never commit email credentials to version control
- Use environment variables for production
- Consider using email service providers for production
- Implement rate limiting for email sending
