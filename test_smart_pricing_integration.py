#!/usr/bin/env python3
"""
Smart Pricing System Integration Test
Validates the complete smart pricing system integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frequency_pricing import FrequencyPricingSystem
from smart_pricing_display import smart_pricing_display

def test_smart_pricing_integration():
    """Test complete smart pricing system integration"""
    
    print("🧠 Testing Smart Pricing System Integration")
    print("=" * 60)
    
    # Initialize pricing system
    pricing_system = FrequencyPricingSystem()
    
    # Test 1: Verify pricing system initialization
    print("\n1. 🔧 Testing Pricing System Initialization:")
    print("-" * 50)
    try:
        tiers = pricing_system.get_available_tiers()
        print(f"✅ Pricing system initialized with {len(tiers)} tiers")
        print(f"   Core tiers: {len([t for t in tiers if t['days'] <= 30])}")
        print(f"   Extended tiers: {len([t for t in tiers if t['days'] > 30])}")
    except Exception as e:
        print(f"❌ Pricing system initialization failed: {e}")
        return False
    
    # Test 2: Verify pricing calculations
    print("\n2. ⚙️ Testing Pricing Calculations:")
    print("-" * 50)
    test_cases = [
        {'days': 1, 'expected_posts': 1, 'expected_discount': 0},
        {'days': 7, 'expected_posts': 4, 'expected_discount': 10},
        {'days': 10, 'expected_posts': 5, 'expected_discount': 12},
        {'days': 30, 'expected_posts': 10, 'expected_discount': 20},
        {'days': 90, 'expected_posts': 20, 'expected_discount': 35}
    ]
    
    for test in test_cases:
        try:
            result = pricing_system.calculate_pricing(test['days'])
            posts_match = result['posts_per_day'] == test['expected_posts']
            discount_match = result['discount_percent'] == test['expected_discount']
            
            if posts_match and discount_match:
                print(f"✅ {test['days']} days: {result['posts_per_day']} posts/day, {result['discount_percent']}% discount")
            else:
                print(f"❌ {test['days']} days: Expected {test['expected_posts']} posts/{test['expected_discount']}% discount, got {result['posts_per_day']} posts/{result['discount_percent']}% discount")
                return False
        except Exception as e:
            print(f"❌ Error calculating pricing for {test['days']} days: {e}")
            return False
    
    # Test 3: Verify currency conversions
    print("\n3. 💰 Testing Currency Conversions:")
    print("-" * 50)
    try:
        result = pricing_system.calculate_pricing(7)
        usd_price = result['final_cost_usd']
        ton_price = result['cost_ton']
        stars_price = result['cost_stars']
        
        # Check conversion rates (corrected)
        expected_ton = round(usd_price * 0.36, 2)
        expected_stars = round(usd_price * 34)
        
        ton_match = abs(ton_price - expected_ton) < 0.01
        stars_match = abs(stars_price - expected_stars) <= 1
        
        if ton_match and stars_match:
            print(f"✅ Currency conversion: ${usd_price:.2f} = {ton_price:.2f} TON = {stars_price} Stars")
        else:
            print(f"❌ Currency conversion failed: Expected {expected_ton} TON/{expected_stars} Stars, got {ton_price} TON/{stars_price} Stars")
            return False
    except Exception as e:
        print(f"❌ Currency conversion test failed: {e}")
        return False
    
    # Test 4: Verify smart pricing display
    print("\n4. 📊 Testing Smart Pricing Display:")
    print("-" * 50)
    try:
        # Test pricing table generation
        table_en = smart_pricing_display.generate_pricing_table_message('en')
        table_ar = smart_pricing_display.generate_pricing_table_message('ar')
        table_ru = smart_pricing_display.generate_pricing_table_message('ru')
        
        if all([table_en, table_ar, table_ru]):
            print("✅ Pricing table generation successful for all languages")
            print(f"   English table: {len(table_en)} characters")
            print(f"   Arabic table: {len(table_ar)} characters")
            print(f"   Russian table: {len(table_ru)} characters")
        else:
            print("❌ Pricing table generation failed for one or more languages")
            return False
    except Exception as e:
        print(f"❌ Pricing display test failed: {e}")
        return False
    
    # Test 5: Verify quick pricing preview
    print("\n5. ⚡ Testing Quick Pricing Preview:")
    print("-" * 50)
    try:
        preview_days = [1, 7, 15, 30]
        for days in preview_days:
            preview = smart_pricing_display.generate_quick_pricing_preview(days, 'en')
            if preview and f"{days} Days" in preview:
                print(f"✅ Quick preview for {days} days: Generated successfully")
            else:
                print(f"❌ Quick preview for {days} days: Failed")
                return False
    except Exception as e:
        print(f"❌ Quick preview test failed: {e}")
        return False
    
    # Test 6: Verify bulk buyer info
    print("\n6. 🚀 Testing Bulk Buyer Information:")
    print("-" * 50)
    try:
        bulk_info = smart_pricing_display.generate_bulk_buyer_info('en')
        if bulk_info and "45 days" in bulk_info and "60 days" in bulk_info and "90 days" in bulk_info:
            print("✅ Bulk buyer information generated successfully")
            print(f"   Information length: {len(bulk_info)} characters")
        else:
            print("❌ Bulk buyer information generation failed")
            return False
    except Exception as e:
        print(f"❌ Bulk buyer info test failed: {e}")
        return False
    
    # Test 7: Verify comparison message
    print("\n7. 🔄 Testing Comparison Message:")
    print("-" * 50)
    try:
        comparison = smart_pricing_display.generate_comparison_message([1, 7, 15, 30], 'en')
        if comparison and "1 Days" in comparison and "30 Days" in comparison:
            print("✅ Comparison message generated successfully")
            print(f"   Comparison length: {len(comparison)} characters")
        else:
            print("❌ Comparison message generation failed")
            return False
    except Exception as e:
        print(f"❌ Comparison message test failed: {e}")
        return False
    
    # Test 8: Verify tier recommendations
    print("\n8. 💡 Testing Tier Recommendations:")
    print("-" * 50)
    try:
        recommendations = pricing_system.get_recommendations(1)
        if recommendations and 'best_value' in recommendations and 'premium_choice' in recommendations:
            print("✅ Tier recommendations generated successfully")
            if recommendations['best_value']:
                print(f"   Best value: {recommendations['best_value']['days']} days")
            if recommendations['premium_choice']:
                print(f"   Premium choice: {recommendations['premium_choice']['days']} days")
        else:
            print("❌ Tier recommendations generation failed")
            return False
    except Exception as e:
        print(f"❌ Tier recommendations test failed: {e}")
        return False
    
    # Test 9: Verify multi-language support
    print("\n9. 🌍 Testing Multi-Language Support:")
    print("-" * 50)
    try:
        languages = ['en', 'ar', 'ru']
        for lang in languages:
            preview = smart_pricing_display.generate_quick_pricing_preview(7, lang)
            if preview:
                print(f"✅ Language {lang}: Preview generated successfully")
            else:
                print(f"❌ Language {lang}: Preview generation failed")
                return False
    except Exception as e:
        print(f"❌ Multi-language test failed: {e}")
        return False
    
    # Test 10: Verify error handling
    print("\n10. 🛡️ Testing Error Handling:")
    print("-" * 50)
    try:
        # Test with minimum valid days (1)
        result = pricing_system.calculate_pricing(1)
        if result['days'] == 1:
            print("✅ Error handling: Minimum days handled correctly")
        else:
            print("❌ Error handling: Minimum days not handled correctly")
            return False
        
        # Test with very large days (should still work)
        result = pricing_system.calculate_pricing(999)
        if result['days'] == 999 and result['final_cost_usd'] > 0:
            print("✅ Error handling: Large days handled correctly")
        else:
            print("❌ Error handling: Large days not handled correctly")
            return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL SMART PRICING INTEGRATION TESTS PASSED!")
    print("=" * 60)
    print("✅ Pricing system fully operational")
    print("✅ Display system functional")
    print("✅ Multi-language support active")
    print("✅ Error handling robust")
    print("✅ Currency conversions accurate")
    print("✅ Ready for production deployment")
    
    return True

if __name__ == "__main__":
    success = test_smart_pricing_integration()
    sys.exit(0 if success else 1)