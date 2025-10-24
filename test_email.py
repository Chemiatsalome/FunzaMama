#!/usr/bin/env python3
"""
Email Configuration Test Script for Funza Mama
Run this to test your email setup
"""

from app import app
from utils.email_service import EmailService

def test_email_configuration():
    """Test email configuration"""
    with app.app_context():
        email_service = EmailService()
        
        print("🔧 Testing Email Configuration...")
        print(f"SMTP Server: {email_service.smtp_server}")
        print(f"SMTP Port: {email_service.smtp_port}")
        print(f"Sender Email: {email_service.sender_email}")
        print(f"Password Configured: {'Yes' if email_service.sender_password else 'No'}")
        
        if not email_service.sender_password:
            print("\n❌ Email password not configured!")
            print("📧 To set up email verification:")
            print("1. Set MAIL_PASSWORD environment variable")
            print("2. Or update config.py with your email credentials")
            print("3. See EMAIL_SETUP.md for detailed instructions")
            return False
        
        print("\n🧪 Testing email sending...")
        try:
            success = email_service.send_verification_email(
                'test@example.com', 
                'Test User', 
                'test-token-123'
            )
            
            if success:
                print("✅ Email sent successfully!")
                print("📧 Check your email inbox for the verification message")
                return True
            else:
                print("❌ Failed to send email")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

if __name__ == "__main__":
    test_email_configuration()
