#!/usr/bin/env python3
"""
Test the stage completion API endpoint directly
"""

import requests
import json

def test_api_endpoint():
    """Test the stage completion API endpoint"""
    
    try:
        # Test the API endpoint
        url = "http://127.0.0.1:10000/admin/api/charts/stage-completion"
        
        # You'll need to login first to get a session cookie
        # For now, let's just test if the endpoint exists
        print("Testing API endpoint...")
        print(f"URL: {url}")
        
        # This will fail without authentication, but we can see the response
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_endpoint()
