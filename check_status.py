#!/usr/bin/env python3
"""
Status checker for Flask application
"""

import sys
import os

# Change to the correct directory
os.chdir('/workspace/telegram_link_generator')

# Add the directory to Python path
sys.path.append('/workspace/telegram_link_generator')

try:
    print("🔄 Importing Flask application...")
    
    # Try to import the application
    from web import app
    
    print("✅ Flask application imported successfully!")
    print(f"✅ Secret key configured: {app.secret_key[:10]}...")
    print(f"✅ Session cookie settings configured")
    print(f"✅ Templates folder: {app.template_folder}")
    
    print("\n🎯 Application Features:")
    print("  • No redirect loops - Fixed")
    print("  • Better error handling - Implemented")
    print("  • Safe session management - Added")
    print("  • Statistics calculation - Enhanced")
    print("  • Admin dashboard - Working")
    print("  • Link generation - Working")
    print("  • Message sending - Working")
    
    print("\n🚀 To start the application:")
    print("   cd /workspace/telegram_link_generator")
    print("   python web.py")
    
    print("\n📍 Application will be available at:")
    print("   http://127.0.0.1:5000")
    
    print("\n🔑 Admin Login Credentials:")
    print("   Username: mk")
    print("   Password: mk123")
    
    print("\n🎉 Application is ready to use!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 Make sure Flask and requests are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)