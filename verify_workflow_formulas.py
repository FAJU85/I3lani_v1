#!/usr/bin/env python3
"""
Verify that our implementation matches the provided workflow formulas exactly
"""

import math

def calculate_pricing(days):
    """User-provided workflow formula"""
    posts_per_day = min(12, max(1, int(days / 2.5) + 1))
    discount = min(25.0, days * 0.8)
    base_price = days * posts_per_day * 0.29
    final_price = base_price * (1 - discount / 100)
    
    return {
        'posts_per_day': posts_per_day,
        'total_posts': days * posts_per_day,
        'base_price': base_price,
        'discount': discount,
        'final_price': final_price,
        'ton_price': final_price * 0.36,
        'stars_price': int(final_price * 34),
        'schedule': generate_schedule(posts_per_day)
    }

def generate_schedule(posts_per_day):
    """User-provided schedule formula"""
    if posts_per_day == 1: return ["00:00"]
    interval = 24 / posts_per_day
    return [f"{int(i * interval):02d}:{int((i * interval % 1) * 60):02d}" 
            for i in range(posts_per_day)]

# Import our implementation
from quantitative_pricing_system import calculate_quantitative_price, get_posting_schedule

def test_formula_compatibility():
    """Test that our implementation matches the workflow formulas"""
    test_cases = [1, 3, 7, 30, 365]
    
    print("=== Formula Compatibility Test ===")
    print("Testing against user-provided workflow formulas\n")
    
    for days in test_cases:
        # User workflow formula
        workflow_result = calculate_pricing(days)
        
        # Our implementation
        our_result = calculate_quantitative_price(days, 1)  # 1 channel
        our_schedule = get_posting_schedule(our_result['posts_per_day'])
        
        # Compare results
        print(f"📊 {days} days:")
        print(f"  Posts per day: {workflow_result['posts_per_day']} vs {our_result['posts_per_day']} {'✅' if workflow_result['posts_per_day'] == our_result['posts_per_day'] else '❌'}")
        print(f"  Total posts: {workflow_result['total_posts']} vs {our_result['total_posts']} {'✅' if workflow_result['total_posts'] == our_result['total_posts'] else '❌'}")
        print(f"  Base price: ${workflow_result['base_price']:.2f} vs ${our_result['base_price']:.2f} {'✅' if abs(workflow_result['base_price'] - our_result['base_price']) < 0.01 else '❌'}")
        print(f"  Discount: {workflow_result['discount']:.1f}% vs {our_result['discount_percentage']:.1f}% {'✅' if abs(workflow_result['discount'] - our_result['discount_percentage']) < 0.1 else '❌'}")
        print(f"  Final price: ${workflow_result['final_price']:.2f} vs ${our_result['final_price']:.2f} {'✅' if abs(workflow_result['final_price'] - our_result['final_price']) < 0.01 else '❌'}")
        print(f"  TON price: {workflow_result['ton_price']:.2f} vs {our_result['ton_price']:.2f} {'✅' if abs(workflow_result['ton_price'] - our_result['ton_price']) < 0.01 else '❌'}")
        print(f"  Stars price: {workflow_result['stars_price']} vs {our_result['stars_price']} {'✅' if workflow_result['stars_price'] == our_result['stars_price'] else '❌'}")
        print(f"  Schedule: {workflow_result['schedule']} vs {our_schedule} {'✅' if workflow_result['schedule'] == our_schedule else '❌'}")
        print()

if __name__ == "__main__":
    test_formula_compatibility()