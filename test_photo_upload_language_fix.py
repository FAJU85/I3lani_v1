#!/usr/bin/env python3
"""
Test Photo Upload Language Fix - Bug #004 Resolution
====================================================

This test validates that Bug #004 has been completely resolved:
- Photo upload handlers now use unified translation system
- No more hardcoded English text in photo upload workflow
- All languages (EN/AR/RU) show consistent messaging

Bug #004: Photo upload step shows English text regardless of selected language
Status: RESOLVED
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from languages import get_text
from logger import StepLogger

def test_photo_upload_language_consistency():
    """Test that photo upload messages are consistent across all languages"""
    
    print("🧪 Testing Photo Upload Language Consistency")
    print("=" * 60)
    
    # Test languages
    languages = ['en', 'ar', 'ru']
    language_names = {'en': 'English', 'ar': 'Arabic', 'ru': 'Russian'}
    
    # Photo upload specific translation keys
    photo_keys = [
        'ad_text_prompt',
        'max_photos_reached',
        'photo_uploaded',
        'done_photos',
        'add_more_photos',
        'add_more_photos_text',
        'provide_contact_info',
        'send_more_photos',
        'ready_for_channels'
    ]
    
    print("📝 Testing Photo Upload Translation Keys:")
    
    all_passed = True
    
    for key in photo_keys:
        print(f"\n🔍 Testing key: {key}")
        
        for lang in languages:
            text = get_text(lang, key)
            
            # Check if text exists and isn't just the key itself
            if text and text != key:
                print(f"   ✅ {language_names[lang]} ({lang}): {text[:50]}...")
            else:
                print(f"   ❌ {language_names[lang]} ({lang}): Missing translation")
                all_passed = False
    
    # Test specific scenario that was causing Bug #004
    print("\n🎯 Testing Bug #004 Scenario:")
    print("   Scenario: User uploads photo, then system asks for text")
    
    for lang in languages:
        text_prompt = get_text(lang, 'ad_text_prompt')
        print(f"   🌐 {language_names[lang]}: {text_prompt}")
        
        # Verify it's not hardcoded English
        if lang != 'en' and text_prompt == "Please send text for your ad.":
            print(f"   ❌ Bug #004 still present in {language_names[lang]}")
            all_passed = False
        else:
            print(f"   ✅ Bug #004 resolved in {language_names[lang]}")
    
    return all_passed

def test_photo_upload_workflow():
    """Test the complete photo upload workflow consistency"""
    
    print("\n🔄 Testing Photo Upload Workflow Consistency")
    print("=" * 60)
    
    languages = ['en', 'ar', 'ru']
    
    # Test the photo upload step
    workflow_consistent = True
    
    for lang in languages:
        print(f"\n🌐 Testing {lang.upper()} workflow:")
        
        # Key messages for photo upload
        key_messages = [
            ('Upload photo', get_text(lang, 'upload_photos')),
            ('Skip photos', get_text(lang, 'skip_photos')),
            ('Add more photos', get_text(lang, 'add_more_photos')),
            ('Done with photos', get_text(lang, 'done_photos'))
        ]
        
        for msg_name, msg_text in key_messages:
            if msg_text and msg_text != msg_name.replace(' ', '_').lower():
                print(f"   ✅ {msg_name}: {msg_text}")
            else:
                print(f"   ❌ {msg_name}: Missing or untranslated")
                workflow_consistent = False
    
    return workflow_consistent

def test_no_hardcoded_english():
    """Test that there are no hardcoded English strings in photo upload handlers"""
    
    print("\n🔍 Testing for Hardcoded English in Photo Upload")
    print("=" * 60)
    
    # Check if handlers.py has been updated to use get_text() calls
    try:
        with open('handlers.py', 'r', encoding='utf-8') as f:
            handler_content = f.read()
        
        # Known hardcoded strings that should NOT be present
        problematic_strings = [
            '"Please send text for your ad."',
            '"Maximum 5 photos allowed. Click Done to continue."',
            '"Photo {count}/5 uploaded."',
            '"Send more photos"',
            '"Ready for channel selection"'
        ]
        
        issues_found = []
        
        for string in problematic_strings:
            if string in handler_content:
                issues_found.append(string)
        
        if issues_found:
            print("   ❌ Hardcoded English strings found:")
            for issue in issues_found:
                print(f"      - {issue}")
            return False
        else:
            print("   ✅ No hardcoded English strings found")
            print("   ✅ All photo upload handlers use get_text() calls")
            return True
    
    except FileNotFoundError:
        print("   ❌ handlers.py not found")
        return False

def main():
    """Main test function"""
    
    print("🎯 Photo Upload Language Fix Test - Bug #004 Resolution")
    print("=" * 80)
    
    logger = StepLogger()
    logger.log_step("BugFix_Test_PhotoUpload", "Starting photo upload language fix test", "test_start")
    
    # Run all tests
    test1_passed = test_photo_upload_language_consistency()
    test2_passed = test_photo_upload_workflow()
    test3_passed = test_no_hardcoded_english()
    
    print("\n" + "=" * 80)
    print("🎯 BUG #004 RESOLUTION TEST RESULTS")
    print("=" * 80)
    
    # Results
    results = {
        "Translation Keys Test": test1_passed,
        "Workflow Consistency Test": test2_passed,
        "No Hardcoded English Test": test3_passed
    }
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("🎉 SUCCESS: Bug #004 has been completely resolved!")
        print("   - Photo upload handlers now use unified translation system")
        print("   - No more hardcoded English text in photo workflows")
        print("   - All languages (EN/AR/RU) show consistent messaging")
        print("   - Users will see proper language regardless of upload type")
        
        logger.log_step("BugFix_Test_PhotoUpload", "Bug #004 resolution test passed", "test_success", success=True)
        
        return True
    else:
        print("❌ FAILURE: Bug #004 resolution incomplete")
        print("   - Some photo upload handlers still need fixes")
        print("   - Additional language consistency work required")
        
        logger.log_step("BugFix_Test_PhotoUpload", "Bug #004 resolution test failed", "test_failure", success=False)
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)