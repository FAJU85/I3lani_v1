#!/usr/bin/env python3
"""
Test script to verify the smart day-based pricing algorithm
"""

from frequency_pricing import FrequencyPricingSystem

def test_pricing_algorithm():
    """Test the exact pricing specifications"""
    
    pricing = FrequencyPricingSystem()
    
    test_cases = [
        (1, 1, 0, 1.00, 1.00),      # 1 day, 1 post/day, 0%, $1.00 base, $1.00 final
        (3, 2, 5, 6.00, 5.70),      # 3 days, 2 posts/day, 5%, $6.00 base, $5.70 final  
        (5, 3, 7, 15.00, 13.95),    # 5 days, 3 posts/day, 7%, $15.00 base, $13.95 final
        (7, 4, 10, 28.00, 25.20),   # 7 days, 4 posts/day, 10%, $28.00 base, $25.20 final
        (10, 5, 12, 50.00, 44.00),  # 10 days, 5 posts/day, 12%, $50.00 base, $44.00 final
        (15, 6, 15, 90.00, 76.50),  # 15 days, 6 posts/day, 15%, $90.00 base, $76.50 final
        (20, 8, 18, 160.00, 131.20), # 20 days, 8 posts/day, 18%, $160.00 base, $131.20 final
        (30, 10, 20, 300.00, 240.00) # 30 days, 10 posts/day, 20%, $300.00 base, $240.00 final
    ]
    
    print("📘 I3lani Bot Pricing Algorithm Test")
    print("=" * 70)
    print(f"{'Days':<5} {'Posts/Day':<10} {'Discount':<8} {'Base Cost':<10} {'Final Price':<12} {'Status'}")
    print("-" * 70)
    
    all_passed = True
    
    for days, expected_posts, expected_discount, expected_base, expected_final in test_cases:
        result = pricing.calculate_pricing(days)
        
        # Check all values
        posts_match = result['posts_per_day'] == expected_posts
        discount_match = result['discount_percent'] == expected_discount
        base_match = abs(result['base_cost_usd'] - expected_base) < 0.01
        final_match = abs(result['final_cost_usd'] - expected_final) < 0.01
        
        status = "✅ PASS" if all([posts_match, discount_match, base_match, final_match]) else "❌ FAIL"
        if status == "❌ FAIL":
            all_passed = False
        
        print(f"{days:<5} {result['posts_per_day']:<10} {result['discount_percent']}%{'':<5} ${result['base_cost_usd']:<9.2f} ${result['final_cost_usd']:<11.2f} {status}")
        
        if status == "❌ FAIL":
            print(f"    Expected: {expected_posts} posts, {expected_discount}%, ${expected_base:.2f}, ${expected_final:.2f}")
            print(f"    Got:      {result['posts_per_day']} posts, {result['discount_percent']}%, ${result['base_cost_usd']:.2f}, ${result['final_cost_usd']:.2f}")
    
    print("-" * 70)
    
    if all_passed:
        print("🎉 All tests PASSED! Pricing algorithm is correct.")
    else:
        print("⚠️  Some tests FAILED. Check the pricing logic.")
    
    print("\n📊 Currency Conversion Test (30 days example):")
    result = pricing.calculate_pricing(30)
    print(f"USD: ${result['final_cost_usd']:.2f}")
    print(f"TON: {result['cost_ton']:.3f} TON (1 USD ≈ 0.36 TON)")
    print(f"Stars: {result['cost_stars']:,} Stars (1 USD = 34 Stars)")
    
    return all_passed

if __name__ == "__main__":
    test_pricing_algorithm()