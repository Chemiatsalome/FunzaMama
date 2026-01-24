"""
Email Service with Resend API support for Railway (SMTP blocked) and SMTP fallback for local dev
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for, request, has_request_context
import secrets
import string
import os

# Try to import Resend - will work on Railway with resend package installed
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False


class EmailService:
    def __init__(self):
        # Detect email provider from environment variable
        self.email_provider = os.environ.get('EMAIL_PROVIDER', 'smtp').lower()
        
        # If on Railway (PORT is set), default to Resend if not explicitly set to smtp
        if os.environ.get('PORT') and self.email_provider == 'smtp':
            # Railway blocks SMTP - suggest Resend
            if not RESEND_AVAILABLE:
                print("⚠️ WARNING: Railway blocks SMTP. Install 'resend' package and set EMAIL_PROVIDER=resend")
        
        # Resend configuration (for Railway production)
        if self.email_provider == 'resend':
            if RESEND_AVAILABLE:
                resend.api_key = os.environ.get('RESEND_API_KEY')
                if not resend.api_key:
                    print("⚠️ WARNING: RESEND_API_KEY not set. Emails will fail.")
                self.from_email = os.environ.get('MAIL_FROM', 'FunzaMama <onboarding@resend.dev>')
            else:
                print("⚠️ WARNING: resend package not installed. Falling back to SMTP.")
                self.email_provider = 'smtp'
        
        # SMTP configuration (for local development or if Resend not available)
        if self.email_provider == 'smtp':
            self.smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            self.smtp_port = current_app.config.get('MAIL_PORT', 587)
            self.use_tls = current_app.config.get('MAIL_USE_TLS', True)
            self.sender_email = current_app.config.get('MAIL_USERNAME', 'noreply@funzamama.org')
            password = current_app.config.get('MAIL_PASSWORD', '') or ''
            self.sender_password = password.strip() if isinstance(password, str) else ''
    
    def _get_base_url(self):
        """Get base URL for email links - handles production and development"""
        server_name = current_app.config.get('SERVER_NAME')
        scheme = current_app.config.get('PREFERRED_URL_SCHEME', 'https')
        
        if server_name:
            if not server_name.startswith('http'):
                return f"{scheme}://{server_name}"
            return server_name
        
        railway_url = os.environ.get('RAILWAY_STATIC_URL') or os.environ.get('RAILWAY_PUBLIC_DOMAIN')
        if railway_url:
            if not railway_url.startswith('http'):
                return f"https://{railway_url}"
            return railway_url
        
        try:
            if has_request_context() and request:
                return f"{request.scheme}://{request.host}"
        except RuntimeError:
            pass
        
        port = os.environ.get('PORT')
        if port:
            return 'https://funzamama-app-production.up.railway.app'
        
        return 'http://localhost:10000'
    
    def generate_verification_token(self):
        """Generate a secure verification token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def _get_verification_url(self, verification_token):
        """Get verification URL"""
        try:
            return url_for('signup.verify_email', token=verification_token, _external=True)
        except RuntimeError:
            base_url = self._get_base_url()
            return f"{base_url}/verify-email/{verification_token}"
    
    def _get_reset_url(self, reset_token):
        """Get password reset URL"""
        try:
            return url_for('signup.reset_password', token=reset_token, _external=True)
        except RuntimeError:
            base_url = self._get_base_url()
            return f"{base_url}/reset-password/{reset_token}"
    
    def _get_verification_email_html(self, user_name, verification_url):
        """Get verification email HTML template"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Account - Funza Mama</title>
    <style>
        body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }}
        .container {{ background: linear-gradient(135deg, #F8BBD9 0%, #C084FC 50%, #E11D48 100%); border-radius: 20px; padding: 40px; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); }}
        .logo {{ font-size: 32px; font-weight: bold; color: white; margin-bottom: 20px; }}
        .content {{ background: white; border-radius: 15px; padding: 30px; margin: 20px 0; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #6B46C1, #C084FC); color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; margin: 20px 0; transition: transform 0.3s ease; }}
        .button:hover {{ transform: translateY(-2px); }}
        .footer {{ color: white; font-size: 14px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎯 Funza Mama</div>
        <div class="content">
            <h2>Welcome to Funza Mama, {user_name}!</h2>
            <p>Thank you for joining our community of learners dedicated to maternal and neonatal health education.</p>
            <p>To complete your registration and start your learning journey, please verify your email address by clicking the button below:</p>
            <a href="{verification_url}" class="button">Verify My Account</a>
            <p style="margin-top: 30px; color: #666; font-size: 14px;">If the button doesn't work, you can copy and paste this link into your browser:<br><a href="{verification_url}" style="color: #6B46C1; word-break: break-all;">{verification_url}</a></p>
            <p style="color: #666; font-size: 14px; margin-top: 20px;">This verification link will expire in 24 hours for security reasons.</p>
        </div>
        <div class="footer">
            <p>Empowering families through knowledge and play.</p>
            <p>© 2024 Funza Mama. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""
    
    def _get_reset_email_html(self, user_name, reset_url):
        """Get password reset email HTML template"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password - Funza Mama</title>
    <style>
        body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }}
        .container {{ background: linear-gradient(135deg, #F8BBD9 0%, #C084FC 50%, #E11D48 100%); border-radius: 20px; padding: 40px; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); }}
        .logo {{ font-size: 32px; font-weight: bold; color: white; margin-bottom: 20px; }}
        .content {{ background: white; border-radius: 15px; padding: 30px; margin: 20px 0; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #E11D48, #F8BBD9); color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; margin: 20px 0; transition: transform 0.3s ease; }}
        .button:hover {{ transform: translateY(-2px); }}
        .footer {{ color: white; font-size: 14px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎯 Funza Mama</div>
        <div class="content">
            <h2>Password Reset Request</h2>
            <p>Hello {user_name},</p>
            <p>We received a request to reset your password for your Funza Mama account.</p>
            <p>If you made this request, click the button below to reset your password:</p>
            <a href="{reset_url}" class="button">Reset My Password</a>
            <p style="margin-top: 30px; color: #666; font-size: 14px;">If the button doesn't work, you can copy and paste this link into your browser:<br><a href="{reset_url}" style="color: #E11D48; word-break: break-all;">{reset_url}</a></p>
            <p style="color: #666; font-size: 14px; margin-top: 20px;">This reset link will expire in 1 hour for security reasons.</p>
            <p style="color: #666; font-size: 14px;">If you didn't request this password reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>Empowering families through knowledge and play.</p>
            <p>© 2024 Funza Mama. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""
    
    def send_verification_email(self, user_email, user_name, verification_token):
        """Send email verification link - uses Resend API on Railway, SMTP locally"""
        verification_url = self._get_verification_url(verification_token)
        
        # Use Resend API (Railway production)
        if self.email_provider == 'resend' and RESEND_AVAILABLE:
            return self._send_resend_email(
                to=user_email,
                subject="Verify Your Funza Mama Account",
                html=self._get_verification_email_html(user_name, verification_url),
                text=f"Welcome to Funza Mama, {user_name}!\n\nPlease verify your email: {verification_url}"
            )
        
        # Fallback to SMTP (local development)
        return self._send_smtp_verification_email(user_email, user_name, verification_url)
    
    def send_password_reset_email(self, user_email, user_name, reset_token):
        """Send password reset email - uses Resend API on Railway, SMTP locally"""
        reset_url = self._get_reset_url(reset_token)
        
        # Use Resend API (Railway production)
        if self.email_provider == 'resend' and RESEND_AVAILABLE:
            return self._send_resend_email(
                to=user_email,
                subject="Reset Your Funza Mama Password",
                html=self._get_reset_email_html(user_name, reset_url),
                text=f"Password Reset Request\n\nHello {user_name},\n\nReset your password: {reset_url}"
            )
        
        # Fallback to SMTP (local development)
        return self._send_smtp_reset_email(user_email, user_name, reset_url)
    
    def _send_resend_email(self, to, subject, html, text):
        """Send email via Resend API"""
        try:
            if not resend.api_key:
                print("❌ RESEND_API_KEY not set. Cannot send email.")
                return False
            
            print(f"📧 Sending email via Resend API to {to}...")
            
            params = {
                "from": self.from_email,
                "to": [to],
                "subject": subject,
                "html": html,
                "text": text
            }
            
            email = resend.Emails.send(params)
            
            if email:
                print(f"✅ Email sent successfully via Resend to {to}")
                return True
            else:
                print(f"❌ Failed to send email via Resend to {to}")
                return False
                
        except Exception as e:
            print(f"❌ Resend API error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _send_smtp_verification_email(self, user_email, user_name, verification_url):
        """Send verification email via SMTP (local development only)"""
        try:
            if not self.sender_password:
                print("⚠️ MAIL_PASSWORD not set. Cannot send SMTP email.")
                print(f"Verification URL for {user_email}: {verification_url}")
                return False
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "Verify Your Funza Mama Account"
            message["From"] = self.sender_email
            message["To"] = user_email
            message.set_charset('utf-8')
            
            html_content = self._get_verification_email_html(user_name, verification_url)
            text_content = f"""Welcome to Funza Mama, {user_name}!

Thank you for joining our community. Please verify your email:
{verification_url}

This link expires in 24 hours."""
            
            text_part = MIMEText(text_content, "plain", "utf-8")
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(text_part)
            message.attach(html_part)
            
            context = ssl.create_default_context()
            print(f"📧 Sending SMTP email to {user_email}...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, user_email, message.as_bytes())
            
            print(f"✅ SMTP email sent successfully to {user_email}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _send_smtp_reset_email(self, user_email, user_name, reset_url):
        """Send password reset email via SMTP (local development only)"""
        try:
            if not self.sender_password:
                print("⚠️ MAIL_PASSWORD not set. Cannot send SMTP email.")
                print(f"Reset URL for {user_email}: {reset_url}")
                return False
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your Funza Mama Password"
            message["From"] = self.sender_email
            message["To"] = user_email
            
            html_content = self._get_reset_email_html(user_name, reset_url)
            text_content = f"""Password Reset Request - Funza Mama

Hello {user_name},

Reset your password: {reset_url}

This link expires in 1 hour."""
            
            text_part = MIMEText(text_content, "plain", "utf-8")
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(text_part)
            message.attach(html_part)
            
            context = ssl.create_default_context()
            print(f"📧 Sending SMTP password reset email to {user_email}...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, user_email, message.as_bytes())
            
            print(f"✅ SMTP password reset email sent successfully to {user_email}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP error: {e}")
            import traceback
            traceback.print_exc()
            return False
