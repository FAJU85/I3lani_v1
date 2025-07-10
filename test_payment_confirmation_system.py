#!/usr/bin/env python3
"""
Test script to verify the enhanced payment confirmation system
Tests the complete payment flow including wallet normalization and multilingual confirmations
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from handlers import normalize_wallet_address
from languages import get_text
from database import Database

async def test_wallet_normalization():
    """Test wallet address normalization function"""
    print("🔧 Testing wallet address normalization...")
    
    # Test cases with different wallet formats
    test_cases = [
        {
            'input': 'EQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tsUh',
            'expected_prefix': 'UQ',
            'description': 'EQ prefix conversion'
        },
        {
            'input': 'UQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tpjk',
            'expected_prefix': 'UQ',
            'description': 'UQ prefix unchanged'
        },
        {
            'input': 'UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE',
            'expected_prefix': 'UQ',
            'description': 'Standard UQ wallet'
        }
    ]
    
    success_count = 0
    for i, test_case in enumerate(test_cases, 1):
        result = normalize_wallet_address(test_case['input'])
        expected_prefix = test_case['expected_prefix']
        
        if result and result.startswith(expected_prefix):
            print(f"✅ Test {i}: {test_case['description']} - PASSED")
            print(f"   Input: {test_case['input']}")
            print(f"   Output: {result}")
            success_count += 1
        else:
            print(f"❌ Test {i}: {test_case['description']} - FAILED")
            print(f"   Input: {test_case['input']}")
            print(f"   Expected prefix: {expected_prefix}")
            print(f"   Got: {result}")
    
    print(f"\n💯 Wallet normalization: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)

def test_multilingual_translations():
    """Test multilingual payment confirmation translations"""
    print("\n🌐 Testing multilingual payment confirmations...")
    
    languages = ['en', 'ar', 'ru']
    required_keys = [
        'ton_payment_confirmed',
        'payment_verified',
        'campaign_starting',
        'campaign_details_confirmed',
        'payment_amount_received',
        'campaign_will_run',
        'posting_frequency_confirmed',
        'channels_confirmed',
        'total_posts_confirmed',
        'publishing_notifications',
        'thank_you_choosing',
        'campaign_status_active'
    ]
    
    success_count = 0
    total_tests = len(languages) * len(required_keys)
    
    for lang in languages:
        lang_success = 0
        print(f"\n🌍 Testing {lang.upper()} translations:")
        
        for key in required_keys:
            text = get_text(lang, key)
            if text and text != key:  # Translation exists and is not just the key
                print(f"   ✅ {key}: {text[:50]}...")
                lang_success += 1
                success_count += 1
            else:
                print(f"   ❌ {key}: Missing translation")
        
        print(f"   📊 {lang.upper()}: {lang_success}/{len(required_keys)} translations available")
    
    print(f"\n💯 Translation coverage: {success_count}/{total_tests} translations available")
    return success_count == total_tests

async def test_database_connection():
    """Test database connection for payment storage"""
    print("\n🗄️ Testing database connection...")
    
    try:
        db = Database()
        await db.initialize()
        
        # Test creating a mock user for payment testing
        test_user_id = 999999999
        await db.create_user(test_user_id, "test_user", "en")
        
        # Test retrieving user
        user = await db.get_user(test_user_id)
        if user:
            print(f"✅ Database connection successful")
            print(f"   Created test user: {user}")
            
            # Clean up test user
            await db.execute("DELETE FROM users WHERE user_id = ?", (test_user_id,))
            print(f"   Cleaned up test user")
            
            return True
        else:
            print(f"❌ Database connection failed - user not found")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_payment_confirmation_formatting():
    """Test payment confirmation message formatting"""
    print("\n💬 Testing payment confirmation message formatting...")
    
    # Mock payment data
    mock_payment_data = {
        'amount_ton': 2.500,
        'days': 7,
        'posts_per_day': 4,
        'total_posts': 28,
        'selected_channels': ['Test Channel 1', 'Test Channel 2'],
        'language': 'en'
    }
    
    try:
        # Test English formatting
        language = 'en'
        confirmation_title = get_text(language, 'ton_payment_confirmed')
        payment_verified = get_text(language, 'payment_verified')
        campaign_starting = get_text(language, 'campaign_starting')
        
        if confirmation_title and payment_verified and campaign_starting:
            print("✅ English message formatting - PASSED")
            print(f"   Title: {confirmation_title}")
            print(f"   Verified: {payment_verified}")
            print(f"   Starting: {campaign_starting}")
        else:
            print("❌ English message formatting - FAILED")
            return False
        
        # Test Arabic formatting
        language = 'ar'
        confirmation_title_ar = get_text(language, 'ton_payment_confirmed')
        payment_verified_ar = get_text(language, 'payment_verified')
        
        if confirmation_title_ar and payment_verified_ar:
            print("✅ Arabic message formatting - PASSED")
            print(f"   Title: {confirmation_title_ar}")
            print(f"   Verified: {payment_verified_ar}")
        else:
            print("❌ Arabic message formatting - FAILED")
            return False
        
        # Test Russian formatting
        language = 'ru'
        confirmation_title_ru = get_text(language, 'ton_payment_confirmed')
        payment_verified_ru = get_text(language, 'payment_verified')
        
        if confirmation_title_ru and payment_verified_ru:
            print("✅ Russian message formatting - PASSED")
            print(f"   Title: {confirmation_title_ru}")
            print(f"   Verified: {payment_verified_ru}")
        else:
            print("❌ Russian message formatting - FAILED")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Message formatting test failed: {e}")
        return False

async def main():
    """Run all payment confirmation system tests"""
    print("🚀 Starting Payment Confirmation System Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Wallet normalization
    result1 = await test_wallet_normalization()
    test_results.append(("Wallet Normalization", result1))
    
    # Test 2: Multilingual translations
    result2 = test_multilingual_translations()
    test_results.append(("Multilingual Translations", result2))
    
    # Test 3: Database connection
    result3 = await test_database_connection()
    test_results.append(("Database Connection", result3))
    
    # Test 4: Message formatting
    result4 = test_payment_confirmation_formatting()
    test_results.append(("Message Formatting", result4))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30} | {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Payment confirmation system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)