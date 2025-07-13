#!/usr/bin/env python3
"""
Test progressive pricing system with new base price and posts per day rates
"""

from quantitative_pricing_system import calculate_quantitative_price, get_posting_schedule

def test_progressive_pricing():
    """Test the progressive pricing system"""
    
    print("=== Progressive Pricing System Test ===")
    print("Testing new base price ($0.29 minimum) and progressive posts per day rates\n")
    
    test_cases = [1, 2, 3, 4, 5, 6, 7, 8, 10, 14, 21, 30, 60, 365]
    
    for days in test_cases:
        result = calculate_quantitative_price(days, 1)  # 1 channel
        schedule = get_posting_schedule(result['posts_per_day'])
        
        print(f"📊 {days} days:")
        print(f"  Posts per day: {result['posts_per_day']}")
        print(f"  Total posts: {result['total_posts']}")
        print(f"  Base price: ${result['base_price']:.2f}")
        print(f"  Discount: {result['discount_percentage']:.1f}%")
        print(f"  Final price: ${result['final_price']:.2f}")
        print(f"  TON: {result['ton_price']:.2f}")
        print(f"  Stars: {result['stars_price']}")
        print(f"  Schedule: {schedule}")
        print()

def test_minimum_base_price():
    """Test that base price is always at least $0.29"""
    
    print("=== Base Price Minimum Test ===")
    print("Ensuring all prices start from $0.29 minimum\n")
    
    for days in [1, 2, 3]:
        result = calculate_quantitative_price(days, 1)
        base_price = result['base_price']
        final_price = result['final_price']
        
        print(f"📊 {days} days:")
        print(f"  Base price: ${base_price:.2f} {'✅' if base_price >= 0.29 else '❌'}")
        print(f"  Final price: ${final_price:.2f} {'✅' if final_price >= 0.29 else '❌'}")
        print()

def test_progressive_posts_increase():
    """Test that posts per day increases progressively with days"""
    
    print("=== Progressive Posts Per Day Test ===")
    print("Testing that posts per day increases with campaign duration\n")
    
    test_cases = [1, 3, 5, 7, 10, 14, 21, 30, 60, 365]
    previous_posts = 0
    
    for days in test_cases:
        result = calculate_quantitative_price(days, 1)
        posts_per_day = result['posts_per_day']
        
        increase_check = "✅" if posts_per_day >= previous_posts else "❌"
        print(f"📊 {days} days: {posts_per_day} posts/day {increase_check}")
        
        previous_posts = posts_per_day
    
    print()

if __name__ == "__main__":
    test_progressive_pricing()
    test_minimum_base_price()
    test_progressive_posts_increase()