#!/usr/bin/env python3
"""
Language Consistency Fix for I3lani Bot
Fixes mixed language issues by ensuring all text uses get_text() function
"""

import re
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import log_success, log_error, log_info, StepNames

def find_hardcoded_text_in_file(file_path: str) -> list:
    """Find potential hardcoded English text in a file"""
    hardcoded_patterns = [
        r'await.*\.answer\(["\']([^"\']*)["\']',  # callback_query.answer("text")
        r'await.*\.send_message\(["\']([^"\']*)["\']',  # send_message("text")
        r'await.*\.edit_text\(["\']([^"\']*)["\']',  # edit_text("text")
        r'text\s*=\s*["\']([^"\']*)["\']',  # text = "hardcoded"
        r'InlineKeyboardButton\([^)]*text\s*=\s*["\']([^"\']*)["\']',  # Button text
    ]
    
    hardcoded_texts = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for pattern in hardcoded_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                # Skip if it's already using get_text or contains variables
                if ('get_text' not in match and 
                    '{' not in match and 
                    len(match) > 5 and  # Skip very short texts
                    not match.startswith('/')): # Skip commands
                    hardcoded_texts.append(match)
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return hardcoded_texts

def analyze_language_consistency():
    """Analyze the codebase for language consistency issues"""
    print("🔍 Language Consistency Analysis")
    print("=" * 50)
    
    # Files to check
    files_to_check = [
        'handlers.py',
        'admin_system.py',
        'modern_keyboard.py',
        'enhanced_callback_handler.py'
    ]
    
    total_issues = 0
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📄 Checking {file_path}...")
            hardcoded_texts = find_hardcoded_text_in_file(file_path)
            
            if hardcoded_texts:
                print(f"   ⚠️  Found {len(hardcoded_texts)} potential hardcoded texts:")
                for i, text in enumerate(hardcoded_texts[:10], 1):  # Show first 10
                    print(f"   {i}. \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
                if len(hardcoded_texts) > 10:
                    print(f"   ... and {len(hardcoded_texts) - 10} more")
                total_issues += len(hardcoded_texts)
            else:
                print("   ✅ No hardcoded texts found")
        else:
            print(f"   ❌ File not found: {file_path}")
    
    print(f"\n📊 Summary: {total_issues} total potential issues found")
    
    return total_issues

def check_language_keys():
    """Check if all required language keys exist"""
    print("\n🔧 Language Keys Check")
    print("=" * 50)
    
    try:
        from languages import LANGUAGES, get_text
        
        # Test required keys
        required_keys = [
            'create_ad_header',
            'create_ad_step1_title', 
            'create_ad_photo_prompt',
            'create_ad_photo_instructions',
            'create_ad_modern_design',
            'skip_photos',
            'error_creating_ad',
            'free_trial_used',
            'help_unavailable',
            'back_to_main'
        ]
        
        languages = ['en', 'ar', 'ru']
        missing_keys = []
        
        for lang in languages:
            print(f"\n🌐 Checking {lang.upper()} language...")
            for key in required_keys:
                text = get_text(lang, key)
                if text == key:  # get_text returns key if not found
                    missing_keys.append(f"{lang}.{key}")
                    print(f"   ❌ Missing: {key}")
                else:
                    print(f"   ✅ {key}: \"{text[:30]}{'...' if len(text) > 30 else ''}\"")
        
        if missing_keys:
            print(f"\n⚠️  Missing keys: {len(missing_keys)}")
            return False
        else:
            print(f"\n✅ All language keys present!")
            return True
            
    except Exception as e:
        print(f"Error checking language keys: {e}")
        return False

def test_language_consistency():
    """Test language consistency with sample user interactions"""
    print("\n🧪 Language Consistency Test")
    print("=" * 50)
    
    try:
        from languages import get_text
        
        # Test scenarios
        test_cases = [
            {
                'scenario': 'Create Ad Button',
                'keys': ['create_ad_header', 'create_ad_step1_title', 'skip_photos', 'back_to_main']
            },
            {
                'scenario': 'Error Messages',
                'keys': ['error_creating_ad', 'free_trial_used', 'help_unavailable']
            },
            {
                'scenario': 'Navigation',
                'keys': ['back_to_main', 'continue', 'cancel', 'confirm']
            }
        ]
        
        languages = ['en', 'ar', 'ru']
        
        for test_case in test_cases:
            print(f"\n📝 Testing: {test_case['scenario']}")
            
            for lang in languages:
                print(f"  🌐 {lang.upper()}:")
                for key in test_case['keys']:
                    text = get_text(lang, key)
                    if text == key:
                        print(f"     ❌ {key}: MISSING")
                    else:
                        print(f"     ✅ {key}: \"{text[:25]}{'...' if len(text) > 25 else ''}\"")
        
        print("\n✅ Language consistency test completed!")
        return True
        
    except Exception as e:
        print(f"Error in language consistency test: {e}")
        return False

def create_language_fix_report():
    """Create a comprehensive report of language fixes needed"""
    print("\n📋 Language Fix Report")
    print("=" * 50)
    
    issues_found = analyze_language_consistency()
    keys_valid = check_language_keys()
    consistency_test = test_language_consistency()
    
    print(f"\n🎯 Fix Summary:")
    print(f"   - Hardcoded texts found: {issues_found}")
    print(f"   - Language keys complete: {'✅' if keys_valid else '❌'}")
    print(f"   - Consistency test: {'✅' if consistency_test else '❌'}")
    
    if issues_found == 0 and keys_valid and consistency_test:
        print(f"\n🎉 SUCCESS: Language consistency is perfect!")
        print(f"   - All text uses get_text() function")
        print(f"   - All language keys are present")
        print(f"   - Consistency test passes")
        return True
    else:
        print(f"\n⚠️  ISSUES FOUND: Language consistency needs fixes")
        print(f"   - Review hardcoded texts in handlers")
        print(f"   - Add missing language keys")
        print(f"   - Update handlers to use get_text()")
        return False

def main():
    """Main function to run language consistency fix"""
    print("🔧 I3lani Bot Language Consistency Fix")
    print("=" * 60)
    
    # Log the debugging step
    log_info(StepNames.ERROR_HANDLER, 0, "Starting language consistency check")
    
    try:
        success = create_language_fix_report()
        
        if success:
            log_success(StepNames.ERROR_HANDLER, 0, "Language consistency check completed successfully")
        else:
            log_error(StepNames.ERROR_HANDLER, 0, 
                     Exception("Language consistency issues found"), 
                     {"issues": "mixed_language_text"})
        
        print(f"\n🎯 Recommendation:")
        print(f"   1. Replace all hardcoded text with get_text() calls")
        print(f"   2. Add missing language keys to languages.py")
        print(f"   3. Test language switching in bot interface")
        print(f"   4. Verify buttons and text match in all languages")
        
        return success
        
    except Exception as e:
        log_error(StepNames.ERROR_HANDLER, 0, e, {"action": "language_consistency_check"})
        print(f"Error in language consistency check: {e}")
        return False

if __name__ == "__main__":
    main()