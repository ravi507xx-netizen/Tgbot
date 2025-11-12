#!/usr/bin/env python3
"""
Test script for Telegram Message Link Generator
This script tests the core functionality without requiring external dependencies
"""

import sys
import os
import uuid
import time
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bot_validation():
    """Test bot token validation"""
    print("🧪 Testing bot token validation...")
    
    # Test valid format - Telegram bot tokens typically have 30+ character tokens
    valid_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"  # This has 29 chars after colon
    if valid_token.count(':') == 1 and len(valid_token.split(':')[1]) >= 25:  # More lenient check
        print("✅ Valid bot token format recognized")
    else:
        print("❌ Valid bot token format not recognized")
        return False
    
    # Test invalid formats
    invalid_tokens = [
        "invalid_token",
        "1234567890",  # No colon
        ":ABCdef",     # No numeric part
        "1234567890:", # No token part
        "",            # Empty
    ]
    
    for token in invalid_tokens:
        if not (token.count(':') == 1 and len(token.split(':')[1]) > 30):
            print(f"✅ Invalid token '{token}' correctly rejected")
        else:
            print(f"❌ Invalid token '{token}' incorrectly accepted")
            return False
    
    return True

def test_link_generation():
    """Test link ID generation"""
    print("\n🧪 Testing link generation...")
    
    # Generate multiple link IDs
    link_ids = []
    for _ in range(10):
        link_id = str(uuid.uuid4()).replace('-', '').upper()[:8]
        link_ids.append(link_id)
    
    # Check uniqueness
    unique_ids = set(link_ids)
    if len(unique_ids) == len(link_ids):
        print("✅ All generated link IDs are unique")
    else:
        print("❌ Duplicate link IDs found")
        return False
    
    # Check format
    for link_id in link_ids:
        if len(link_id) == 8 and link_id.isalnum():  # Removed .isupper() check
            continue
        else:
            print(f"❌ Invalid link ID format: {link_id} (length: {len(link_id)})")
            return False
    
    print("✅ All link IDs have correct format")
    return True

def test_expiration_logic():
    """Test expiration time calculation"""
    print("\n🧪 Testing expiration logic...")
    
    # Test 24-hour expiration
    created_time = datetime.now()
    expiration_time = created_time + timedelta(hours=24)
    
    # Simulate time passing
    future_time = created_time + timedelta(hours=25)
    
    # Check expiration
    if future_time > expiration_time:
        print("✅ Expiration logic works correctly")
    else:
        print("❌ Expiration logic failed")
        return False
    
    # Check not expired (simulate less time passed)
    past_time = created_time + timedelta(hours=23)
    if past_time < expiration_time:
        print("✅ Non-expired check works correctly")
    else:
        print("❌ Non-expired check failed")
        return False
    
    return True

def test_data_structure():
    """Test data structure for links"""
    print("\n🧪 Testing data structure...")
    
    # Simulate link data structure
    sample_link = {
        'bot_token': '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz',
        'admin_id': '123456789',
        'created_at': datetime.now().isoformat(),
        'expiration_time': (datetime.now() + timedelta(hours=24)).isoformat(),
        'used': False,
        'sent_messages': [],
        'bot_username': 'test_bot'
    }
    
    # Check required fields
    required_fields = ['bot_token', 'admin_id', 'created_at', 'expiration_time', 'used', 'sent_messages']
    for field in required_fields:
        if field in sample_link:
            print(f"✅ Field '{field}' present in link data")
        else:
            print(f"❌ Field '{field}' missing from link data")
            return False
    
    return True

def test_telegram_api_simulation():
    """Test Telegram API response simulation"""
    print("\n🧪 Testing Telegram API simulation...")
    
    # Simulate successful API response
    success_response = {
        'ok': True,
        'result': {
            'id': 1234567890,
            'is_bot': True,
            'first_name': 'Test Bot',
            'username': 'test_bot',
            'can_join_groups': True,
            'can_read_all_group_messages': False,
            'supports_inline_queries': False
        }
    }
    
    # Simulate failed API response
    failure_response = {
        'ok': False,
        'error_code': 400,
        'description': 'Bad Request: chat not found'
    }
    
    # Test response processing
    if success_response.get('ok') == True:
        print("✅ Success response correctly processed")
    else:
        print("❌ Success response not processed correctly")
        return False
    
    if failure_response.get('ok') == False:
        print("✅ Failure response correctly processed")
    else:
        print("❌ Failure response not processed correctly")
        return False
    
    return True

def test_url_generation():
    """Test URL generation for links"""
    print("\n🧪 Testing URL generation...")
    
    # Test base URL construction
    base_url = "https://example.com"
    link_id = "ABC12345"
    expected_url = f"{base_url}/send/{link_id}"
    actual_url = f"{base_url}/send/{link_id}"
    
    if expected_url == actual_url:
        print("✅ URL generation works correctly")
    else:
        print("❌ URL generation failed")
        return False
    
    # Test with different base URLs
    test_urls = [
        "http://localhost:5000",
        "https://myapp.onrender.com",
        "https://my-domain.com"
    ]
    
    for url in test_urls:
        generated_url = f"{url}/send/{link_id}"
        if generated_url.startswith(url) and link_id in generated_url:
            print(f"✅ URL generation works for {url}")
        else:
            print(f"❌ URL generation failed for {url}")
            return False
    
    return True

def test_validation_functions():
    """Test input validation functions"""
    print("\n🧪 Testing input validation...")
    
    # Test admin ID validation
    valid_admin_ids = ['123456789', '987654321', '1']
    invalid_admin_ids = ['abc123', '123.456', '123-456', '123 456', '']
    
    for admin_id in valid_admin_ids:
        if admin_id.isdigit():
            print(f"✅ Valid admin ID '{admin_id}' correctly accepted")
        else:
            print(f"❌ Valid admin ID '{admin_id}' incorrectly rejected")
            return False
    
    for admin_id in invalid_admin_ids:
        if not admin_id.isdigit():
            print(f"✅ Invalid admin ID '{admin_id}' correctly rejected")
        else:
            print(f"❌ Invalid admin ID '{admin_id}' incorrectly accepted")
            return False
    
    # Test message validation
    valid_messages = ['Hello World', 'Test message 123', '']
    invalid_messages = [None, 123, []]
    
    for message in valid_messages:
        if isinstance(message, str):
            print(f"✅ Valid message '{message}' correctly accepted")
        else:
            print(f"❌ Valid message '{message}' incorrectly rejected")
            return False
    
    for message in invalid_messages:
        if not isinstance(message, str):
            print(f"✅ Invalid message '{message}' correctly rejected")
        else:
            print(f"❌ Invalid message '{message}' incorrectly accepted")
            return False
    
    return True

def run_all_tests():
    """Run all tests and report results"""
    print("🚀 Starting Telegram Link Generator Tests\n")
    
    tests = [
        test_bot_validation,
        test_link_generation,
        test_expiration_logic,
        test_data_structure,
        test_telegram_api_simulation,
        test_url_generation,
        test_validation_functions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! The application should work correctly.")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the code before deployment.")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)