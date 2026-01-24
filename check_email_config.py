"""
Quick script to check email configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("EMAIL CONFIGURATION CHECK")
print("=" * 60)
print()

# Check environment variables
mail_server = os.environ.get('MAIL_SERVER')
mail_port = os.environ.get('MAIL_PORT')
mail_username = os.environ.get('MAIL_USERNAME')
mail_password = os.environ.get('MAIL_PASSWORD')
mail_use_tls = os.environ.get('MAIL_USE_TLS')

# Defaults from config.py
default_server = 'smtp.gmail.com'
default_port = 587
default_username = 'chemiatsalome@gmail.com'

print("Current Configuration:")
print("-" * 60)
print(f"MAIL_SERVER:     {mail_server or default_server} (env: {'SET' if mail_server else 'NOT SET'})")
print(f"MAIL_PORT:       {mail_port or default_port} (env: {'SET' if mail_port else 'NOT SET'})")
print(f"MAIL_USERNAME:   {mail_username or default_username} (env: {'SET' if mail_username else 'NOT SET'})")
print(f"MAIL_PASSWORD:   {'*' * len(mail_password) if mail_password else 'NOT SET'} (env: {'SET' if mail_password else 'NOT SET'})")
print(f"MAIL_USE_TLS:    {mail_use_tls or 'True'} (env: {'SET' if mail_use_tls else 'NOT SET'})")
print()

print("Configuration Analysis:")
print("-" * 60)

# Check password
if not mail_password:
    print("WARNING: MAIL_PASSWORD is not set!")
    print("  - Email features will NOT work")
    print("  - Set MAIL_PASSWORD in .env file (local) or environment variables (production)")
else:
    password_length = len(mail_password.strip())
    print(f"MAIL_PASSWORD is set (length: {password_length} characters)")
    if password_length == 16:
        print("  -> This looks like a Gmail App Password (correct length)")
    elif password_length < 8:
        print("  WARNING: Password seems too short (should be 16 chars for Gmail App Password)")
    else:
        print("  -> Password length is OK")

# Check username
final_username = mail_username or default_username
if '@gmail.com' in final_username:
    print(f"Email address is Gmail: {final_username}")
    print("  -> Using Gmail SMTP is correct (smtp.gmail.com)")
elif '@' in final_username:
    print(f"Email address: {final_username}")
    if 'office365' in final_username.lower() or 'outlook' in final_username.lower():
        print("  WARNING: Office 365 detected - may require special setup")
else:
    print(f"Email address may not be valid: {final_username}")

# Check server
final_server = mail_server or default_server
if final_server == 'smtp.gmail.com':
    print(f"SMTP Server: {final_server} (correct for Gmail)")
elif final_server == 'smtp.office365.com':
    print(f"SMTP Server: {final_server} (for Office 365)")
else:
    print(f"SMTP Server: {final_server} (custom)")

print()
print("=" * 60)
print("Summary:")
print("=" * 60)

issues = []
if not mail_password:
    issues.append("MAIL_PASSWORD is not set")

if issues:
    print("ISSUES FOUND:")
    for issue in issues:
        print(f"  - {issue}")
    print()
    print("To fix:")
    print("  1. For local development: Create .env file with MAIL_PASSWORD")
    print("  2. For production (Railway): Set MAIL_PASSWORD in Railway Dashboard -> Variables")
else:
    print("Configuration looks good!")

print()
