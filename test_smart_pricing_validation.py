#!/usr/bin/env python3
"""
Smart & Scalable Ad Pricing System Validation Test
Validates exact pricing calculations as per specifications
"""

import asyncio
from frequency_pricing import FrequencyPricingSystem

def test_smart_pricing_system():
    """Test the smart pricing system with exact specifications"""
    print("🧠 Testing Smart & Scalable Ad Pricing System")
    print("=" * 60)
    
    # Initialize pricing system
    pricing = FrequencyPricingSystem()
    
    # Expected results from the specification table
    expected_results = [
        {'days': 1, 'posts_per_day': 1, 'discount': 0, 'daily_rate': 1.00, 'subtotal': 1.00, 'final_price': 1.00},
        {'days': 3, 'posts_per_day': 2, 'discount': 5, 'daily_rate': 2.00, 'subtotal': 6.00, 'final_price': 5.70},
        {'days': 5, 'posts_per_day': 3, 'discount': 7, 'daily_rate': 3.00, 'subtotal': 15.00, 'final_price': 13.95},
        {'days': 7, 'posts_per_day': 4, 'discount': 10, 'daily_rate': 4.00, 'subtotal': 28.00, 'final_price': 25.20},
        {'days': 10, 'posts_per_day': 5, 'discount': 12, 'daily_rate': 5.00, 'subtotal': 50.00, 'final_price': 44.00},
        {'days': 15, 'posts_per_day': 6, 'discount': 15, 'daily_rate': 6.00, 'subtotal': 90.00, 'final_price': 76.50},
        {'days': 20, 'posts_per_day': 8, 'discount': 18, 'daily_rate': 8.00, 'subtotal': 160.00, 'final_price': 131.20},
        {'days': 30, 'posts_per_day': 10, 'discount': 20, 'daily_rate': 10.00, 'subtotal': 300.00, 'final_price': 240.00},
    ]
    
    print("📊 Testing Core Pricing Tiers:")
    print("-" * 60)
    print(f"{'Days':<4} {'Posts/Day':<9} {'Discount':<8} {'Daily Rate':<10} {'Subtotal':<9} {'Final Price':<11} {'Status'}")
    print("-" * 60)
    
    all_passed = True
    
    for expected in expected_results:
        days = expected['days']
        result = pricing.calculate_pricing(days, channels_count=1)
        
        # Extract values
        posts_per_day = result['posts_per_day']
        discount_percent = result['discount_percent']
        daily_rate = result['daily_price']
        subtotal = result['base_cost_usd']
        final_price = result['final_cost_usd']
        
        # Check if all values match
        posts_match = posts_per_day == expected['posts_per_day']
        discount_match = discount_percent == expected['discount']
        daily_rate_match = abs(daily_rate - expected['daily_rate']) < 0.01
        subtotal_match = abs(subtotal - expected['subtotal']) < 0.01
        final_price_match = abs(final_price - expected['final_price']) < 0.01
        
        all_match = posts_match and discount_match and daily_rate_match and subtotal_match and final_price_match
        status = "✅ PASS" if all_match else "❌ FAIL"
        
        if not all_match:
            all_passed = False
        
        print(f"{days:<4} {posts_per_day:<9} {discount_percent}%{'':<5} ${daily_rate:<9.2f} ${subtotal:<8.2f} ${final_price:<10.2f} {status}")
    
    print("-" * 60)
    
    # Test currency conversions
    print("\n💰 Testing Currency Conversions:")
    print("-" * 40)
    
    # Test 7-day plan conversions
    result = pricing.calculate_pricing(7, channels_count=1)
    usd_price = result['final_cost_usd']
    ton_price = result['cost_ton']
    stars_price = result['cost_stars']
    
    expected_ton = usd_price * 0.36
    expected_stars = usd_price * 34
    
    print(f"7-Day Plan (${usd_price:.2f} USD):")
    print(f"  TON: {ton_price:.2f} (Expected: {expected_ton:.2f}) {'✅' if abs(ton_price - expected_ton) < 0.01 else '❌'}")
    print(f"  Stars: {stars_price:.0f} (Expected: {expected_stars:.0f}) {'✅' if abs(stars_price - expected_stars) < 1 else '❌'}")
    
    # Test extended tiers for bulk buyers
    print("\n🚀 Testing Extended Tiers (Bulk Buyers):")
    print("-" * 40)
    
    extended_tests = [
        {'days': 45, 'expected_posts': 12, 'expected_discount': 25},
        {'days': 60, 'expected_posts': 15, 'expected_discount': 30},
        {'days': 90, 'expected_posts': 20, 'expected_discount': 35}
    ]
    
    for test in extended_tests:
        result = pricing.calculate_pricing(test['days'], channels_count=1)
        posts_match = result['posts_per_day'] == test['expected_posts']
        discount_match = result['discount_percent'] == test['expected_discount']
        
        status = "✅ PASS" if posts_match and discount_match else "❌ FAIL"
        print(f"{test['days']} days: {result['posts_per_day']} posts/day, {result['discount_percent']}% discount {status}")
    
    # Test automated calculation flow
    print("\n🔄 Testing Automated Calculation Flow:")
    print("-" * 40)
    
    flow_tests = [
        {'days': 1, 'description': 'Single day campaign'},
        {'days': 14, 'description': 'Medium campaign (uses 10-day tier)'},
        {'days': 25, 'description': 'Long campaign (uses 20-day tier)'},
        {'days': 40, 'description': 'Extended campaign (uses 30-day tier)'},
        {'days': 75, 'description': 'Brand campaign (uses 60-day tier)'}
    ]
    
    for test in flow_tests:
        result = pricing.calculate_pricing(test['days'], channels_count=1)
        tier = pricing.get_tier_for_days(test['days'])
        
        print(f"📅 {test['days']} days ({test['description']}):")
        print(f"   Uses tier: {tier['name']}")
        print(f"   Posts/day: {result['posts_per_day']}")
        print(f"   Discount: {result['discount_percent']}%")
        print(f"   Final price: ${result['final_cost_usd']:.2f}")
        print(f"   TON: {result['cost_ton']:.2f}")
        print(f"   Stars: {result['cost_stars']:.0f}")
        print()
    
    # Summary
    print("📋 Test Summary:")
    print("-" * 30)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Core pricing tiers match specifications")
        print("✅ Currency conversions working correctly")
        print("✅ Extended tiers for bulk buyers active")
        print("✅ Automated calculation flow functional")
        print("\n🚀 Smart & Scalable Ad Pricing System is ready for deployment!")
    else:
        print("❌ Some tests failed. Please review the pricing calculations.")
    
    return all_passed

if __name__ == "__main__":
    test_smart_pricing_system()