#!/usr/bin/env python3
"""
Test script to verify the Flask application works correctly
"""

import os
import sys
import requests
import time

# Change to the correct directory
os.chdir('/workspace/telegram_link_generator')

# Add the directory to Python path
sys.path.append('/workspace/telegram_link_generator')

try:
    # Import Flask app
    from web import app
    
    print("✅ Flask app imported successfully")
    
    # Test the app configuration
    with app.app_context():
        print(f"✅ Secret key configured: {app.secret_key[:10]}...")
        print(f"✅ Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"✅ Session cookie secure: {app.config.get('SESSION_COOKIE_SECURE', 'Not set')}")
    
    # Start the app in test mode
    print("🚀 Starting Flask application...")
    
    # Create a test client
    client = app.test_client()
    
    print("📝 Testing routes...")
    
    # Test home route
    response = client.get('/')
    print(f"Home route: {response.status_code}")
    
    # Test admin login route
    response = client.get('/admin')
    print(f"Admin login route: {response.status_code}")
    
    # Test health check
    response = client.get('/health')
    print(f"Health check route: {response.status_code}")
    
    print("🎉 All tests passed! The Flask app should work correctly.")
    print("🌐 To start the app, run: python web.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure Flask and requests are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)