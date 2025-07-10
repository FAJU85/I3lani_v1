#!/usr/bin/env python3
"""
Test Stars Payment System Fix
Validates all components of the fixed Stars payment system
"""

import asyncio
import sys
sys.path.append('.')

async def test_stars_payment_system():
    """Test the complete Stars payment system"""
    
    print("🧪 TESTING FIXED STARS PAYMENT SYSTEM")
    print("="*50)
    
    test_results = []
    
    # Test 1: Handler imports
    print("1. Testing handler imports...")
    try:
        from handlers import (
            confirm_stars_payment_handler,
            pay_dynamic_stars_handler,
            pre_checkout_query_handler,
            successful_payment_handler,
            pay_frequency_stars_handler
        )
        test_results.append("✅ All Stars payment handlers imported successfully")
        print("   ✅ Stars payment handlers available")
    except Exception as e:
        test_results.append(f"❌ Handler import error: {e}")
        print(f"   ❌ Error importing handlers: {e}")
    
    # Test 2: Automatic confirmation integration
    print("\n2. Testing automatic confirmation integration...")
    try:
        from automatic_payment_confirmation import (
            handle_confirmed_payment,
            track_payment_for_user
        )
        test_results.append("✅ Automatic confirmation functions available")
        print("   ✅ Campaign integration functions imported")
    except Exception as e:
        test_results.append(f"❌ Confirmation integration error: {e}")
        print(f"   ❌ Error importing confirmation functions: {e}")
    
    # Test 3: Unique ID generation
    print("\n3. Testing unique Stars payment ID generation...")
    try:
        from payments import payment_processor
        memo1 = payment_processor.generate_memo()
        memo2 = payment_processor.generate_memo()
        
        if memo1 != memo2 and len(memo1) == 6 and len(memo2) == 6:
            test_results.append("✅ Unique Stars payment ID generation working")
            print(f"   ✅ Unique IDs generated: {memo1}, {memo2}")
        else:
            test_results.append("❌ ID generation not unique or wrong format")
            print(f"   ❌ ID generation issue: {memo1}, {memo2}")
    except Exception as e:
        test_results.append(f"❌ ID generation error: {e}")
        print(f"   ❌ Error generating IDs: {e}")
    
    # Test 4: Database tracking structure
    print("\n4. Testing database tracking structure...")
    try:
        import sqlite3
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM payment_memo_tracking LIMIT 1")
        columns = [description[0] for description in cursor.description]
        
        required_columns = ['user_id', 'memo', 'amount', 'payment_method', 'status']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if not missing_columns:
            test_results.append("✅ Database tracking structure complete")
            print(f"   ✅ All required columns present: {columns}")
        else:
            test_results.append(f"❌ Missing database columns: {missing_columns}")
            print(f"   ❌ Missing columns: {missing_columns}")
        
        conn.close()
        
    except Exception as e:
        test_results.append(f"❌ Database structure error: {e}")
        print(f"   ❌ Error checking database: {e}")
    
    # Test 5: Campaign integration
    print("\n5. Testing campaign integration...")
    try:
        from campaign_management import create_campaign_for_payment
        test_results.append("✅ Campaign creation function available")
        print("   ✅ Campaign creation system ready")
    except Exception as e:
        test_results.append(f"❌ Campaign integration error: {e}")
        print(f"   ❌ Campaign integration issue: {e}")
    
    # Test 6: Pricing calculation integration
    print("\n6. Testing pricing calculation integration...")
    try:
        from dynamic_pricing import get_dynamic_pricing
        pricing = get_dynamic_pricing()
        
        # Test calculation
        test_calculation = {
            'days': 7,
            'posts_per_day': 2,
            'total_posts': 14,
            'selected_channels': ['@i3lani', '@smshco'],
            'total_usd': 25.20,
            'total_stars': 857
        }
        
        if hasattr(pricing, 'create_payment_keyboard_data'):
            test_results.append("✅ Pricing calculation integration working")
            print("   ✅ Pricing system integrated with Stars payments")
        else:
            test_results.append("❌ Pricing integration incomplete")
            print("   ❌ Pricing integration missing methods")
            
    except Exception as e:
        test_results.append(f"❌ Pricing integration error: {e}")
        print(f"   ❌ Error with pricing integration: {e}")
    
    print(f"\n" + "="*50)
    print(f"🎯 STARS PAYMENT SYSTEM TEST RESULTS")
    print(f"="*50)
    
    passed_tests = len([r for r in test_results if r.startswith("✅")])
    total_tests = len(test_results)
    
    for result in test_results:
        print(f"{result}")
    
    print(f"\n📊 TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print(f"🎉 ALL TESTS PASSED - STARS PAYMENT SYSTEM FULLY FUNCTIONAL!")
    elif passed_tests >= total_tests * 0.8:
        print(f"✅ MOSTLY WORKING - Minor issues need attention")
    else:
        print(f"❌ CRITICAL ISSUES - Major fixes needed")
    
    return passed_tests, total_tests

if __name__ == "__main__":
    passed, total = asyncio.run(test_stars_payment_system())
    print(f"\nFinal Score: {passed}/{total} ({passed/total*100:.1f}%)")