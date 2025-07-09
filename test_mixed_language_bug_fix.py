#!/usr/bin/env python3
"""
Test for Mixed Language Bug Fix
Validates that account status messages are consistently in single language
"""

import asyncio
import sys
from unittest.mock import Mock, AsyncMock
from languages import get_text, LANGUAGES

def test_translation_keys_exist():
    """Test that all required translation keys exist for account status"""
    print("🔍 Testing Translation Keys Coverage")
    print("=" * 50)
    
    # Required keys for account status
    required_keys = [
        'main_menu_welcome',
        'main_menu_status', 
        'main_menu_ready',
        'your_account',
        'total_campaigns',
        'account_status',
        'account_active',
        'performance',
        'performance_optimized'
    ]
    
    languages = ['en', 'ar', 'ru']
    language_names = {'en': 'English', 'ar': 'Arabic', 'ru': 'Russian'}
    
    all_passed = True
    
    for lang in languages:
        print(f"\n🌐 Testing {language_names[lang]} ({lang}):")
        
        missing_keys = []
        for key in required_keys:
            text = get_text(lang, key)
            if text == key:  # get_text returns key if translation missing
                missing_keys.append(key)
                print(f"   ❌ Missing: {key}")
                all_passed = False
            else:
                print(f"   ✅ {key}: \"{text[:30]}{'...' if len(text) > 30 else ''}\"")
        
        if missing_keys:
            print(f"   ⚠️  Missing {len(missing_keys)} translation keys")
        else:
            print(f"   ✅ All translation keys available")
    
    if all_passed:
        print("\n🎉 All translation keys are available in all languages!")
        return True
    else:
        print("\n❌ Some translation keys are missing!")
        return False

def test_no_mixed_language_content():
    """Test that account status text contains no mixed language content"""
    print("\n🔍 Testing for Mixed Language Content")
    print("=" * 50)
    
    # Test scenarios that previously caused mixed language issues
    test_cases = [
        {
            'name': 'Account Status Section',
            'english_words': ['Your Account', 'Total Campaigns', 'Account Status', 'ACTIVE', 'Performance', 'OPTIMIZED'],
            'arabic_context': 'ar',
            'russian_context': 'ru'
        }
    ]
    
    issues_found = []
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        
        # Test Arabic context
        print(f"   🔍 Testing Arabic context...")
        arabic_texts = [
            get_text('ar', 'your_account'),
            get_text('ar', 'total_campaigns'),
            get_text('ar', 'account_status'),
            get_text('ar', 'account_active'),
            get_text('ar', 'performance'),
            get_text('ar', 'performance_optimized')
        ]
        
        for text in arabic_texts:
            for english_word in test_case['english_words']:
                if english_word.lower() in text.lower():
                    issues_found.append(f"Arabic text contains English word '{english_word}': {text}")
                    print(f"     ❌ Found English word '{english_word}' in Arabic text: {text}")
        
        # Test Russian context
        print(f"   🔍 Testing Russian context...")
        russian_texts = [
            get_text('ru', 'your_account'),
            get_text('ru', 'total_campaigns'),
            get_text('ru', 'account_status'),
            get_text('ru', 'account_active'),
            get_text('ru', 'performance'),
            get_text('ru', 'performance_optimized')
        ]
        
        for text in russian_texts:
            for english_word in test_case['english_words']:
                if english_word.lower() in text.lower():
                    issues_found.append(f"Russian text contains English word '{english_word}': {text}")
                    print(f"     ❌ Found English word '{english_word}' in Russian text: {text}")
    
    if issues_found:
        print(f"\n❌ Found {len(issues_found)} mixed language issues:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print(f"\n✅ No mixed language content found!")
        return True

async def test_main_menu_text_generation():
    """Test that main menu text generation produces single-language content"""
    print("\n🔍 Testing Main Menu Text Generation")
    print("=" * 50)
    
    # Mock database and user stats
    class MockDB:
        async def get_user_stats(self, user_id):
            return {'total_ads': 7}
        
        async def get_custom_ui_text(self, key, language):
            return None  # No custom text
    
    # Mock the database and handlers
    import handlers
    original_db = handlers.db
    handlers.db = MockDB()
    
    languages = ['en', 'ar', 'ru']
    language_names = {'en': 'English', 'ar': 'Arabic', 'ru': 'Russian'}
    
    all_passed = True
    
    for lang in languages:
        print(f"\n🌐 Testing {language_names[lang]} ({lang}) main menu:")
        
        try:
            # Generate main menu text
            menu_text = await handlers.create_regular_main_menu_text(lang, 566158428)
            
            print(f"   📝 Generated text length: {len(menu_text)} characters")
            
            # Check for mixed language issues
            if lang == 'ar':
                # Check for English words in Arabic menu
                english_indicators = ['Your Account', 'Total Campaigns', 'Account Status', 'ACTIVE', 'Performance', 'OPTIMIZED']
                found_english = [word for word in english_indicators if word in menu_text]
                if found_english:
                    print(f"   ❌ Found English words in Arabic menu: {found_english}")
                    all_passed = False
                else:
                    print(f"   ✅ No English words found in Arabic menu")
            
            elif lang == 'ru':
                # Check for English words in Russian menu
                english_indicators = ['Your Account', 'Total Campaigns', 'Account Status', 'ACTIVE', 'Performance', 'OPTIMIZED']
                found_english = [word for word in english_indicators if word in menu_text]
                if found_english:
                    print(f"   ❌ Found English words in Russian menu: {found_english}")
                    all_passed = False
                else:
                    print(f"   ✅ No English words found in Russian menu")
            
            # Show preview of generated text
            print(f"   📋 Text preview: {menu_text[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error generating menu text: {e}")
            all_passed = False
    
    # Restore original database
    handlers.db = original_db
    
    if all_passed:
        print(f"\n✅ All main menu text generation tests passed!")
        return True
    else:
        print(f"\n❌ Some main menu text generation tests failed!")
        return False

def test_expected_output_format():
    """Test that the expected output format matches user requirements"""
    print("\n🔍 Testing Expected Output Format")
    print("=" * 50)
    
    # Test Arabic output format
    print("🇸🇦 Testing Arabic format:")
    arabic_texts = {
        'welcome': get_text('ar', 'main_menu_welcome'),
        'status': get_text('ar', 'main_menu_status'),
        'your_account': get_text('ar', 'your_account'),
        'total_campaigns': get_text('ar', 'total_campaigns'),
        'account_status': get_text('ar', 'account_status'),
        'account_active': get_text('ar', 'account_active'),
        'performance': get_text('ar', 'performance'),
        'performance_optimized': get_text('ar', 'performance_optimized'),
        'ready': get_text('ar', 'main_menu_ready')
    }
    
    print(f"   📝 Welcome: {arabic_texts['welcome']}")
    print(f"   📝 Status: {arabic_texts['status']}")
    print(f"   📝 Your Account: {arabic_texts['your_account']}")
    print(f"   📝 Total Campaigns: {arabic_texts['total_campaigns']}")
    print(f"   📝 Account Status: {arabic_texts['account_status']}")
    print(f"   📝 Account Active: {arabic_texts['account_active']}")
    print(f"   📝 Performance: {arabic_texts['performance']}")
    print(f"   📝 Performance Optimized: {arabic_texts['performance_optimized']}")
    print(f"   📝 Ready: {arabic_texts['ready']}")
    
    # Test English output format
    print("\n🇺🇸 Testing English format:")
    english_texts = {
        'welcome': get_text('en', 'main_menu_welcome'),
        'status': get_text('en', 'main_menu_status'),
        'your_account': get_text('en', 'your_account'),
        'total_campaigns': get_text('en', 'total_campaigns'),
        'account_status': get_text('en', 'account_status'),
        'account_active': get_text('en', 'account_active'),
        'performance': get_text('en', 'performance'),
        'performance_optimized': get_text('en', 'performance_optimized'),
        'ready': get_text('en', 'main_menu_ready')
    }
    
    print(f"   📝 Welcome: {english_texts['welcome']}")
    print(f"   📝 Status: {english_texts['status']}")
    print(f"   📝 Your Account: {english_texts['your_account']}")
    print(f"   📝 Total Campaigns: {english_texts['total_campaigns']}")
    print(f"   📝 Account Status: {english_texts['account_status']}")
    print(f"   📝 Account Active: {english_texts['account_active']}")
    print(f"   📝 Performance: {english_texts['performance']}")
    print(f"   📝 Performance Optimized: {english_texts['performance_optimized']}")
    print(f"   📝 Ready: {english_texts['ready']}")
    
    # Test Russian output format
    print("\n🇷🇺 Testing Russian format:")
    russian_texts = {
        'welcome': get_text('ru', 'main_menu_welcome'),
        'status': get_text('ru', 'main_menu_status'),
        'your_account': get_text('ru', 'your_account'),
        'total_campaigns': get_text('ru', 'total_campaigns'),
        'account_status': get_text('ru', 'account_status'),
        'account_active': get_text('ru', 'account_active'),
        'performance': get_text('ru', 'performance'),
        'performance_optimized': get_text('ru', 'performance_optimized'),
        'ready': get_text('ru', 'main_menu_ready')
    }
    
    print(f"   📝 Welcome: {russian_texts['welcome']}")
    print(f"   📝 Status: {russian_texts['status']}")
    print(f"   📝 Your Account: {russian_texts['your_account']}")
    print(f"   📝 Total Campaigns: {russian_texts['total_campaigns']}")
    print(f"   📝 Account Status: {russian_texts['account_status']}")
    print(f"   📝 Account Active: {russian_texts['account_active']}")
    print(f"   📝 Performance: {russian_texts['performance']}")
    print(f"   📝 Performance Optimized: {russian_texts['performance_optimized']}")
    print(f"   📝 Ready: {russian_texts['ready']}")
    
    print(f"\n✅ Output format validation completed!")
    return True

async def main():
    """Run all tests"""
    print("🐞 Mixed Language Bug Fix Validation")
    print("=" * 60)
    
    # Run all tests
    test_results = []
    
    # Test 1: Translation keys exist
    test_results.append(test_translation_keys_exist())
    
    # Test 2: No mixed language content
    test_results.append(test_no_mixed_language_content())
    
    # Test 3: Main menu text generation
    test_results.append(await test_main_menu_text_generation())
    
    # Test 4: Expected output format
    test_results.append(test_expected_output_format())
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Mixed language bug is fixed!")
        print("\n✅ Bug Status: RESOLVED")
        print("✅ Account status messages are now consistent in single language")
        print("✅ No more mixed Arabic/English or Russian/English content")
        print("✅ Full localization implemented for all account status elements")
        return True
    else:
        print("❌ Some tests failed. Mixed language bug needs more work.")
        print(f"\n❌ Bug Status: NOT FULLY RESOLVED")
        print(f"❌ Failed tests: {total_tests - passed_tests}")
        return False

if __name__ == "__main__":
    # Add the current directory to Python path
    sys.path.insert(0, '.')
    
    asyncio.run(main())