"""
Test script to verify email configuration
Run this to test if your email settings are working correctly
"""
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from utils.email_service import EmailService

def test_email_config():
    """Test email configuration"""
    # Create a test request context for URL generation
    with app.app_context():
        # Set up a test request context for url_for to work
        with app.test_request_context(base_url='http://localhost:10000'):
            email_service = EmailService()
        
        print("=" * 60)
        print("EMAIL CONFIGURATION TEST")
        print("=" * 60)
        print(f"SMTP Server: {email_service.smtp_server}")
        print(f"SMTP Port: {email_service.smtp_port}")
        print(f"Use TLS: {email_service.use_tls}")
        print(f"Sender Email: {email_service.sender_email}")
        print(f"Password Set: {'Yes' if email_service.sender_password else 'No'}")
        print(f"Password Length: {len(email_service.sender_password) if email_service.sender_password else 0}")
        print("=" * 60)
        
        # Test sending a verification email
        test_email = input("\nEnter a test email address to send to (or press Enter to skip): ").strip()
        
        if test_email:
            print(f"\n📧 Attempting to send test email to {test_email}...")
            token = email_service.generate_verification_token()
            success = email_service.send_verification_email(
                test_email,
                "Test User",
                token
            )
            
            if success:
                print("\n✅ SUCCESS! Email sent successfully!")
                print("Check your inbox for the verification email.")
            else:
                print("\n❌ FAILED! Email could not be sent.")
                print("Check the error messages above for details.")
        else:
            print("\nSkipping email send test. Configuration check complete.")

if __name__ == "__main__":
    test_email_config()
