#!/usr/bin/env python
"""
Quick test to see if app.py imports without blocking
Run this locally to verify: python test_app_import.py
"""

import sys
import time

print("Testing app import...")
start_time = time.time()

try:
    from app import app
    elapsed = time.time() - start_time
    print(f"✅ App imported successfully in {elapsed:.2f} seconds")
    print(f"✅ App object: {app}")
    print(f"✅ App name: {app.name}")
    sys.exit(0)
except Exception as e:
    elapsed = time.time() - start_time
    print(f"❌ App import failed after {elapsed:.2f} seconds")
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
