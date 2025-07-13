#!/usr/bin/env python3
"""
Test mathematical pricing system according to user specifications
Formula: R = min(12, max(1, ⌊D/2.5⌋ + 1))
"""

import math
from quantitative_pricing_system import calculate_quantitative_price, get_posting_schedule

def test_mathematical_formula():
    """Test the mathematical formula R = min(12, max(1, ⌊D/2.5⌋ + 1))"""
    
    print("=== Mathematical Formula Test ===")
    print("Formula: R = min(12, max(1, ⌊D/2.5⌋ + 1))")
    print("Testing posts per day calculation\n")
    
    test_cases = [
        (1, 1),   # ⌊1/2.5⌋ + 1 = 0 + 1 = 1
        (2, 1),   # ⌊2/2.5⌋ + 1 = 0 + 1 = 1
        (3, 2),   # ⌊3/2.5⌋ + 1 = 1 + 1 = 2
        (4, 2),   # ⌊4/2.5⌋ + 1 = 1 + 1 = 2
        (5, 3),   # ⌊5/2.5⌋ + 1 = 2 + 1 = 3
        (6, 3),   # ⌊6/2.5⌋ + 1 = 2 + 1 = 3
        (7, 3),   # ⌊7/2.5⌋ + 1 = 2 + 1 = 3
        (8, 4),   # ⌊8/2.5⌋ + 1 = 3 + 1 = 4
        (10, 5),  # ⌊10/2.5⌋ + 1 = 4 + 1 = 5
        (30, 12), # ⌊30/2.5⌋ + 1 = 12 + 1 = 13, but min(12, 13) = 12
    ]
    
    for days, expected_posts in test_cases:
        result = calculate_quantitative_price(days, 1)
        calculated_posts = result['posts_per_day']
        
        # Manual calculation
        manual_calc = min(12, max(1, math.floor(days / 2.5) + 1))
        
        status = "✅" if calculated_posts == expected_posts == manual_calc else "❌"
        print(f"Days {days}: Expected={expected_posts}, Calculated={calculated_posts}, Manual={manual_calc} {status}")
    
    print()

def test_discount_formula():
    """Test discount formula δ = min(25%, D × 0.8%)"""
    
    print("=== Discount Formula Test ===")
    print("Formula: δ = min(25%, D × 0.8%)")
    print("Testing discount percentage calculation\n")
    
    test_cases = [
        (1, 0.8),    # 1 × 0.8% = 0.8%
        (2, 1.6),    # 2 × 0.8% = 1.6%
        (3, 2.4),    # 3 × 0.8% = 2.4%
        (5, 4.0),    # 5 × 0.8% = 4.0%
        (10, 8.0),   # 10 × 0.8% = 8.0%
        (30, 24.0),  # 30 × 0.8% = 24.0%
        (31, 24.8),  # 31 × 0.8% = 24.8%
        (32, 25.0),  # 32 × 0.8% = 25.6%, but min(25%, 25.6%) = 25%
        (50, 25.0),  # 50 × 0.8% = 40%, but min(25%, 40%) = 25%
    ]
    
    for days, expected_discount in test_cases:
        result = calculate_quantitative_price(days, 1)
        calculated_discount = result['discount_percentage']
        
        # Manual calculation
        manual_calc = min(25.0, days * 0.8)
        
        status = "✅" if abs(calculated_discount - expected_discount) < 0.1 and abs(manual_calc - expected_discount) < 0.1 else "❌"
        print(f"Days {days}: Expected={expected_discount}%, Calculated={calculated_discount}%, Manual={manual_calc}% {status}")
    
    print()

def test_price_calculation():
    """Test final price calculation Price = D × R × P₀ × (1 - δ)"""
    
    print("=== Price Calculation Test ===")
    print("Formula: Price = D × R × P₀ × (1 - δ)")
    print("P₀ = $0.29, Testing complete price calculation\n")
    
    test_cases = [
        (1, 1, 0.8, 0.29),    # 1 × 1 × 0.29 × (1 - 0.008) = 0.29 × 0.992 = 0.288 → $0.29 (minimum)
        (2, 1, 1.6, 0.57),    # 2 × 1 × 0.29 × (1 - 0.016) = 0.58 × 0.984 = 0.57
        (3, 2, 2.4, 1.70),    # 3 × 2 × 0.29 × (1 - 0.024) = 1.74 × 0.976 = 1.70
        (5, 3, 4.0, 4.18),    # 5 × 3 × 0.29 × (1 - 0.04) = 4.35 × 0.96 = 4.18
    ]
    
    for days, expected_posts, expected_discount, expected_price in test_cases:
        result = calculate_quantitative_price(days, 1)
        
        # Manual calculation
        posts_per_day = min(12, max(1, math.floor(days / 2.5) + 1))
        discount_pct = min(25.0, days * 0.8)
        base_price = days * posts_per_day * 0.29
        discounted_price = base_price * (1 - discount_pct / 100)
        final_price = max(0.29, discounted_price)
        
        status = "✅" if abs(result['final_price'] - expected_price) < 0.01 else "❌"
        print(f"Days {days}: Posts={result['posts_per_day']}, Discount={result['discount_percentage']:.1f}%, Price=${result['final_price']:.2f} (expected ${expected_price:.2f}) {status}")
    
    print()

def test_posting_schedule():
    """Test posting schedule generation"""
    
    print("=== Posting Schedule Test ===")
    print("Testing even distribution across 24 hours\n")
    
    test_cases = [
        (1, ['00:00']),
        (2, ['00:00', '12:00']),
        (3, ['00:00', '08:00', '16:00']),
        (4, ['00:00', '06:00', '12:00', '18:00']),
        (6, ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']),
        (12, ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']),
    ]
    
    for posts_per_day, expected_schedule in test_cases:
        schedule = get_posting_schedule(posts_per_day)
        status = "✅" if schedule == expected_schedule else "❌"
        print(f"{posts_per_day} posts/day: {schedule} {status}")
    
    print()

def test_complete_pricing_matrix():
    """Test complete pricing matrix as per user specifications"""
    
    print("=== Complete Pricing Matrix Test ===")
    print("Days | Posts/Day | Discount | Final Price | Posting Interval")
    print("-" * 60)
    
    for days in [1, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20, 30, 50]:
        result = calculate_quantitative_price(days, 1)
        schedule = get_posting_schedule(result['posts_per_day'])
        
        if len(schedule) == 1:
            interval = "Once daily"
        elif len(schedule) == 2:
            interval = "Every 12 hours"
        elif len(schedule) == 3:
            interval = "Every 8 hours"
        elif len(schedule) == 4:
            interval = "Every 6 hours"
        else:
            hours = 24 // len(schedule)
            interval = f"Every {hours} hours"
        
        print(f"{days:4d} | {result['posts_per_day']:9d} | {result['discount_percentage']:6.1f}% | ${result['final_price']:9.2f} | {interval}")

if __name__ == "__main__":
    test_mathematical_formula()
    test_discount_formula()
    test_price_calculation()
    test_posting_schedule()
    test_complete_pricing_matrix()