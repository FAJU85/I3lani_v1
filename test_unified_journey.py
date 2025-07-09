#!/usr/bin/env python3
"""
Test Unified Journey System
Validates that the user journey is consistent across all languages
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_journey import journey_engine, JourneyStep, get_unified_step, validate_journey
from languages import LANGUAGES, get_text
from logger import log_info, log_success, log_error, StepNames

def test_step_consistency():
    """Test that all steps work consistently across languages"""
    print("🧪 Testing Step Consistency Across Languages")
    print("=" * 60)
    
    test_user_id = 12345
    languages = ['en', 'ar', 'ru']
    
    # Test key steps
    test_steps = [
        JourneyStep.MAIN_MENU,
        JourneyStep.AD_CREATION_START,
        JourneyStep.AD_UPLOAD_PHOTOS,
        JourneyStep.AD_UPLOAD_TEXT,
        JourneyStep.AD_CHANNEL_SELECTION,
        JourneyStep.SETTINGS_MENU,
        JourneyStep.HELP_DISPLAY
    ]
    
    results = {
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    for step in test_steps:
        print(f"\n📋 Testing {step.value}...")
        
        step_results = {}
        
        for language in languages:
            try:
                content = get_unified_step(step, language, test_user_id)
                
                step_results[language] = {
                    'title': content['title'],
                    'description': content['description'],
                    'button_count': len(content['buttons']),
                    'button_actions': [btn['action'] for btn in content['buttons']]
                }
                
                print(f"   🌐 {language.upper()}: ✅ {len(content['buttons'])} buttons")
                
            except Exception as e:
                print(f"   🌐 {language.upper()}: ❌ Error: {e}")
                results['errors'].append(f"Step {step.value} failed for {language}: {e}")
                results['failed'] += 1
                continue
        
        # Validate consistency
        if len(step_results) == len(languages):
            # Check button count consistency
            button_counts = [result['button_count'] for result in step_results.values()]
            if len(set(button_counts)) == 1:
                print(f"   ✅ Button count consistent: {button_counts[0]}")
            else:
                print(f"   ❌ Button count inconsistent: {button_counts}")
                results['errors'].append(f"Step {step.value} has inconsistent button counts")
                results['failed'] += 1
                continue
            
            # Check button actions consistency
            action_sets = [set(result['button_actions']) for result in step_results.values()]
            if all(actions == action_sets[0] for actions in action_sets):
                print(f"   ✅ Button actions consistent")
                results['passed'] += 1
            else:
                print(f"   ❌ Button actions inconsistent")
                results['errors'].append(f"Step {step.value} has inconsistent button actions")
                results['failed'] += 1
        else:
            results['failed'] += 1
    
    print(f"\n📊 Step Consistency Results:")
    print(f"   ✅ Passed: {results['passed']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    if results['errors']:
        print(f"\n⚠️  Errors found:")
        for error in results['errors']:
            print(f"   - {error}")
    
    return results['failed'] == 0

def test_journey_flow():
    """Test journey flow consistency"""
    print("\n🔄 Testing Journey Flow Consistency")
    print("=" * 60)
    
    # Test flow paths
    flow_tests = [
        {
            'name': 'Ad Creation Flow',
            'path': [
                (JourneyStep.MAIN_MENU, 'create_ad'),
                (JourneyStep.AD_CREATION_START, 'upload_photos'),
                (JourneyStep.AD_UPLOAD_PHOTOS, 'skip_photos_to_text'),
                (JourneyStep.AD_UPLOAD_TEXT, 'continue_to_channels'),
                (JourneyStep.AD_CHANNEL_SELECTION, 'continue_to_duration'),
                (JourneyStep.AD_DURATION_SELECTION, 'continue_to_posts'),
                (JourneyStep.AD_POSTS_SELECTION, 'continue_to_payment'),
                (JourneyStep.AD_PAYMENT_SUMMARY, 'choose_payment_method'),
                (JourneyStep.AD_PAYMENT_METHOD, 'pay_ton')
            ]
        },
        {
            'name': 'Settings Flow',
            'path': [
                (JourneyStep.MAIN_MENU, 'settings'),
                (JourneyStep.SETTINGS_MENU, 'lang_ar'),
                (JourneyStep.MAIN_MENU, 'settings'),
                (JourneyStep.SETTINGS_MENU, 'back_to_main')
            ]
        },
        {
            'name': 'Help Flow',
            'path': [
                (JourneyStep.MAIN_MENU, 'help'),
                (JourneyStep.HELP_DISPLAY, 'back_to_main')
            ]
        }
    ]
    
    flow_results = {'passed': 0, 'failed': 0, 'errors': []}
    
    for flow_test in flow_tests:
        print(f"\n🛤️  Testing {flow_test['name']}...")
        
        flow_valid = True
        for i, (current_step, action) in enumerate(flow_test['path']):
            expected_next = flow_test['path'][i + 1][0] if i + 1 < len(flow_test['path']) else None
            
            if expected_next:
                actual_next = journey_engine.get_next_step(current_step, action)
                
                if actual_next == expected_next:
                    print(f"   ✅ {current_step.value} -> {action} -> {actual_next.value}")
                else:
                    print(f"   ❌ {current_step.value} -> {action} -> Expected: {expected_next.value}, Got: {actual_next}")
                    flow_valid = False
                    flow_results['errors'].append(f"Flow {flow_test['name']} failed at step {current_step.value}")
        
        if flow_valid:
            flow_results['passed'] += 1
            print(f"   ✅ {flow_test['name']} flow is valid")
        else:
            flow_results['failed'] += 1
            print(f"   ❌ {flow_test['name']} flow is invalid")
    
    print(f"\n📊 Journey Flow Results:")
    print(f"   ✅ Passed: {flow_results['passed']}")
    print(f"   ❌ Failed: {flow_results['failed']}")
    
    return flow_results['failed'] == 0

def test_language_translations():
    """Test that all required language keys exist"""
    print("\n🌐 Testing Language Translation Coverage")
    print("=" * 60)
    
    # Critical keys that must exist in all languages
    critical_keys = [
        'main_menu_description',
        'create_ad_step1_description',
        'create_ad_step2_title',
        'create_ad_step3_title',
        'create_ad_step4_title',
        'create_ad_step5_title',
        'settings_title',
        'settings_description',
        'help_title',
        'help_text',
        'back_to_main',
        'continue',
        'cancel',
        'confirm',
        'lang_english',
        'lang_arabic',
        'lang_russian'
    ]
    
    languages = ['en', 'ar', 'ru']
    translation_results = {'passed': 0, 'failed': 0, 'missing': []}
    
    for language in languages:
        print(f"\n🌐 Testing {language.upper()} translations...")
        
        missing_keys = []
        for key in critical_keys:
            text = get_text(language, key)
            if text == key:  # get_text returns key if translation missing
                missing_keys.append(key)
                print(f"   ❌ Missing: {key}")
            else:
                print(f"   ✅ {key}: \"{text[:30]}{'...' if len(text) > 30 else ''}\"")
        
        if missing_keys:
            translation_results['failed'] += 1
            translation_results['missing'].extend([(language, key) for key in missing_keys])
        else:
            translation_results['passed'] += 1
    
    print(f"\n📊 Translation Coverage Results:")
    print(f"   ✅ Languages with complete translations: {translation_results['passed']}")
    print(f"   ❌ Languages with missing translations: {translation_results['failed']}")
    
    if translation_results['missing']:
        print(f"\n⚠️  Missing translations:")
        for language, key in translation_results['missing']:
            print(f"   - {language}: {key}")
    
    return translation_results['failed'] == 0

def run_comprehensive_test():
    """Run all unified journey tests"""
    print("🎯 I3lani Bot Unified Journey Test Suite")
    print("=" * 80)
    
    # Log test start
    print("🔍 Starting unified journey test suite...")
    
    # Run validation
    print("\n🔍 Step 1: Journey Structure Validation")
    validation_result = validate_journey()
    structure_valid = validation_result['valid']
    
    # Run consistency tests
    print("\n🔍 Step 2: Step Consistency Test")
    consistency_valid = test_step_consistency()
    
    # Run flow tests
    print("\n🔍 Step 3: Journey Flow Test")
    flow_valid = test_journey_flow()
    
    # Run translation tests
    print("\n🔍 Step 4: Language Translation Test")
    translation_valid = test_language_translations()
    
    # Final results
    print("\n" + "=" * 80)
    print("🎯 UNIFIED JOURNEY TEST RESULTS")
    print("=" * 80)
    
    all_tests_passed = structure_valid and consistency_valid and flow_valid and translation_valid
    
    print(f"🏗️  Structure Validation: {'✅ PASSED' if structure_valid else '❌ FAILED'}")
    print(f"🔄 Step Consistency: {'✅ PASSED' if consistency_valid else '❌ FAILED'}")
    print(f"🛤️  Journey Flow: {'✅ PASSED' if flow_valid else '❌ FAILED'}")
    print(f"🌐 Language Coverage: {'✅ PASSED' if translation_valid else '❌ FAILED'}")
    
    if all_tests_passed:
        print(f"\n🎉 SUCCESS: Unified journey system is working correctly!")
        print(f"   - User journey is consistent across all languages")
        print(f"   - Step structure is identical for EN, AR, and RU")
        print(f"   - Navigation flows work as expected")
        print(f"   - All required translations are present")
        
        print("✅ Unified journey test suite completed successfully")
    else:
        print(f"\n⚠️  ISSUES FOUND: Unified journey system needs fixes")
        print(f"   - Review failed tests above")
        print(f"   - Fix missing translations")
        print(f"   - Ensure step structure consistency")
        
        print("❌ Unified journey test suite failed - check output above")
    
    return all_tests_passed

if __name__ == "__main__":
    success = run_comprehensive_test()
    
    if success:
        print(f"\n✅ All tests passed! The unified journey system is ready for deployment.")
        print(f"🚀 Users will now have consistent experience across all languages.")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed. Please review the output above.")
        sys.exit(1)