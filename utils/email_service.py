import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for
import secrets
import string

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"  # Change to your SMTP server
        self.smtp_port = 587
        self.sender_email = current_app.config.get('MAIL_USERNAME', 'noreply@funzamama.org')
        self.sender_password = current_app.config.get('MAIL_PASSWORD', '')
        
    def generate_verification_token(self):
        """Generate a secure verification token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def send_verification_email(self, user_email, user_name, verification_token):
        """Send email verification link"""
        try:
            # Check if email credentials are configured
            if not self.sender_password:
                print(f"Email not configured. Verification URL for {user_email}: {url_for('auth.verify_email', token=verification_token, _external=True)}")
                return False
                
            # Create verification URL
            verification_url = url_for('auth.verify_email', token=verification_token, _external=True)
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Verify Your Funza Mama Account"
            message["From"] = self.sender_email
            message["To"] = user_email
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verify Your Account - Funza Mama</title>
                <style>
                    body {{
                        font-family: 'Inter', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f8f9fa;
                    }}
                    .container {{
                        background: linear-gradient(135deg, #F8BBD9 0%, #C084FC 50%, #E11D48 100%);
                        border-radius: 20px;
                        padding: 40px;
                        text-align: center;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                    }}
                    .logo {{
                        font-size: 32px;
                        font-weight: bold;
                        color: white;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        background: white;
                        border-radius: 15px;
                        padding: 30px;
                        margin: 20px 0;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #6B46C1, #C084FC);
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 50px;
                        font-weight: bold;
                        margin: 20px 0;
                        transition: transform 0.3s ease;
                    }}
                    .button:hover {{
                        transform: translateY(-2px);
                    }}
                    .footer {{
                        color: white;
                        font-size: 14px;
                        margin-top: 20px;
                    }}
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
                        
                        <p style="margin-top: 30px; color: #666; font-size: 14px;">
                            If the button doesn't work, you can copy and paste this link into your browser:<br>
                            <a href="{verification_url}" style="color: #6B46C1; word-break: break-all;">{verification_url}</a>
                        </p>
                        
                        <p style="color: #666; font-size: 14px; margin-top: 20px;">
                            This verification link will expire in 24 hours for security reasons.
                        </p>
                    </div>
                    <div class="footer">
                        <p>Empowering families through knowledge and play.</p>
                        <p>© 2024 Funza Mama. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text content
            text_content = f"""
            Welcome to Funza Mama, {user_name}!
            
            Thank you for joining our community of learners dedicated to maternal and neonatal health education.
            
            To complete your registration and start your learning journey, please verify your email address by visiting this link:
            
            {verification_url}
            
            This verification link will expire in 24 hours for security reasons.
            
            Best regards,
            The Funza Mama Team
            
            Empowering families through knowledge and play.
            © 2024 Funza Mama. All rights reserved.
            """
            
            # Attach parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, user_email, message.as_string())
            
            return True
            
        except Exception as e:
            print(f"Error sending verification email: {e}")
            return False
    
    def send_password_reset_email(self, user_email, user_name, reset_token):
        """Send password reset email"""
        try:
            # Check if email credentials are configured
            if not self.sender_password:
                print(f"Email not configured. Reset URL for {user_email}: {url_for('auth.reset_password', token=reset_token, _external=True)}")
                return False
                
            # Create reset URL
            reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your Funza Mama Password"
            message["From"] = self.sender_email
            message["To"] = user_email
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Reset Your Password - Funza Mama</title>
                <style>
                    body {{
                        font-family: 'Inter', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f8f9fa;
                    }}
                    .container {{
                        background: linear-gradient(135deg, #F8BBD9 0%, #C084FC 50%, #E11D48 100%);
                        border-radius: 20px;
                        padding: 40px;
                        text-align: center;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                    }}
                    .logo {{
                        font-size: 32px;
                        font-weight: bold;
                        color: white;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        background: white;
                        border-radius: 15px;
                        padding: 30px;
                        margin: 20px 0;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #E11D48, #F8BBD9);
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 50px;
                        font-weight: bold;
                        margin: 20px 0;
                        transition: transform 0.3s ease;
                    }}
                    .button:hover {{
                        transform: translateY(-2px);
                    }}
                    .footer {{
                        color: white;
                        font-size: 14px;
                        margin-top: 20px;
                    }}
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
                        
                        <p style="margin-top: 30px; color: #666; font-size: 14px;">
                            If the button doesn't work, you can copy and paste this link into your browser:<br>
                            <a href="{reset_url}" style="color: #E11D48; word-break: break-all;">{reset_url}</a>
                        </p>
                        
                        <p style="color: #666; font-size: 14px; margin-top: 20px;">
                            This reset link will expire in 1 hour for security reasons.
                        </p>
                        
                        <p style="color: #666; font-size: 14px;">
                            If you didn't request this password reset, please ignore this email.
                        </p>
                    </div>
                    <div class="footer">
                        <p>Empowering families through knowledge and play.</p>
                        <p>© 2024 Funza Mama. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text content
            text_content = f"""
            Password Reset Request - Funza Mama
            
            Hello {user_name},
            
            We received a request to reset your password for your Funza Mama account.
            
            If you made this request, visit this link to reset your password:
            
            {reset_url}
            
            This reset link will expire in 1 hour for security reasons.
            
            If you didn't request this password reset, please ignore this email.
            
            Best regards,
            The Funza Mama Team
            
            Empowering families through knowledge and play.
            © 2024 Funza Mama. All rights reserved.
            """
            
            # Attach parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, user_email, message.as_string())
            
            return True
            
        except Exception as e:
            print(f"Error sending password reset email: {e}")
            return False
