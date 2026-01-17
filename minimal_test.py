#!/usr/bin/env python
"""
Minimal test to verify Flask app can start and bind to port
Run: python minimal_test.py
"""

from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return {'status': 'ok', 'message': 'Minimal test works!'}

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Starting minimal Flask app on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
    print(f"✅ Server started on http://0.0.0.0:{port}")
