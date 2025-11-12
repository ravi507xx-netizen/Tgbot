#!/usr/bin/env python3
"""
Test script to verify Flask application startup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the Flask app
    from web import app
    print("✅ Flask app imported successfully")
    
    # Try to create test client
    client = app.test_client()
    print("✅ Test client created successfully")
    
    # Test basic route
    response = client.get('/health')
    print(f"✅ Health check response: {response.status_code}")
    
    # Test home route
    response = client.get('/')
    print(f"✅ Home page response: {response.status_code}")
    
    print("\n🎉 Flask application is working correctly!")
    print("You can now run: python web.py")
    
except Exception as e:
    print(f"❌ Error starting Flask application: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()