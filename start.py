#!/usr/bin/env python
"""
Explicit startup script for Render
This ensures the app starts and binds to the port correctly
"""
import os
import sys

# Set port from environment
port = int(os.environ.get('PORT', 10000))
host = '0.0.0.0'

print(f"🚀 Starting Funza Mama app on {host}:{port}")
print(f"📋 PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
print(f"📋 FLASK_ENV: {os.environ.get('FLASK_ENV', 'NOT SET')}")

try:
    # Import app
    print("📦 Importing app...")
    from app import app
    print("✅ App imported successfully")
    
    # Verify app object
    print(f"✅ App object: {app}")
    print(f"✅ App name: {app.name}")
    
    # Start with explicit binding
    print(f"🌐 Binding to {host}:{port}...")
    app.run(host=host, port=port, debug=False)
    
except Exception as e:
    print(f"❌ Error starting app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
