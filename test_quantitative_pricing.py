#!/usr/bin/env python3
"""
Test Quantitative Pricing System
Comprehensive testing of the new mathematical pricing formulas
"""

from quantitative_pricing_system import QuantitativePricingCalculator
import json

def test_quantitative_pricing_system():
    """Test the quantitative pricing system with various scenarios"""
    
    print("=" * 70)
    print("🧮 QUANTITATIVE PRICING SYSTEM TEST")
    print("=" * 70)
    
    calculator = QuantitativePricingCalculator()
    
    # Test cases covering different scenarios
    test_cases = [
        # (days, channels, description)
        (1, 1, "Single day, single channel"),
        (2, 1, "Two days, single channel"),
        (3, 1, "Three days, single channel"),
        (5, 1, "Five days, single channel"),
        (7, 1, "One week, single channel"),
        (14, 1, "Two weeks, single channel"),
        (30, 1, "One month, single channel"),
        (90, 1, "Three months, single channel"),
        (365, 1, "One year, single channel"),
        (7, 2, "One week, two channels"),
        (30, 4, "One month, four channels"),
    ]
    
    print("\n📊 PRICING CALCULATIONS")
    print("-" * 70)
    print(f"{'Days':<5} {'Channels':<8} {'Posts/Day':<9} {'Discount':<8} {'Price':<10} {'TON':<8} {'Stars':<8}")
    print("-" * 70)
    
    for days, channels, description in test_cases:
        result = calculator.calculate_price(days, channels)
        
        print(f"{days:<5} {channels:<8} {result['posts_per_day']:<9} "
              f"{result['discount_percentage']:<7.1f}% "
              f"${result['final_price']:<9.2f} "
              f"{result['ton_price']:<7.2f} "
              f"{result['stars_price']:<8}")
    
    # Test posting schedules
    print("\n⏰ POSTING SCHEDULES")
    print("-" * 70)
    
    posts_per_day_options = [1, 2, 3, 4, 6, 8, 12]
    
    for posts_per_day in posts_per_day_options:
        schedule = calculator.calculate_posting_schedule(posts_per_day)
        print(f"{posts_per_day:2d} posts/day: {', '.join(schedule)}")
    
    # Test discount progression
    print("\n🎁 DISCOUNT PROGRESSION")
    print("-" * 70)
    
    milestone_days = [1, 5, 10, 20, 30, 60, 90, 180, 365]
    
    for days in milestone_days:
        discount = calculator.calculate_discount_percentage(days)
        print(f"{days:3d} days: {discount:5.1f}% discount")
    
    # Test validation
    print("\n✅ VALIDATION TESTS")
    print("-" * 70)
    
    validation_tests = [
        (1, 1, "Valid minimum"),
        (365, 12, "Valid maximum"),
        (0, 1, "Invalid days (too low)"),
        (366, 1, "Invalid days (too high)"),
        (30, 0, "Invalid posts per day (too low)"),
        (30, 13, "Invalid posts per day (too high)"),
    ]
    
    for days, posts_per_day, description in validation_tests:
        validation = calculator.validate_selection(days, posts_per_day)
        status = "✅ VALID" if validation['valid'] else "❌ INVALID"
        print(f"{description:<25}: {status}")
        
        if validation['errors']:
            for error in validation['errors']:
                print(f"  Error: {error}")
        
        if validation['warnings']:
            for warning in validation['warnings']:
                print(f"  Warning: {warning}")
    
    # Test pricing matrix
    print("\n📋 PRICING MATRIX (1 Channel)")
    print("-" * 70)
    
    matrix = calculator.get_pricing_matrix(channels=1, max_days=30)
    
    for pricing in matrix:
        print(f"{pricing['days']:2d} days: "
              f"{pricing['posts_per_day']:2d} posts/day, "
              f"{pricing['discount_percentage']:5.1f}% off, "
              f"${pricing['final_price']:6.2f}")
    
    # Test next discount milestones
    print("\n🎯 NEXT DISCOUNT MILESTONES")
    print("-" * 70)
    
    current_days_tests = [1, 5, 10, 25, 50, 100, 200]
    
    for current_days in current_days_tests:
        next_milestone = calculator.get_next_discount_milestone(current_days)
        if next_milestone[0]:
            print(f"At {current_days:3d} days: Next milestone at {next_milestone[0]:3d} days "
                  f"({next_milestone[1]:4.1f}% discount)")
        else:
            print(f"At {current_days:3d} days: Maximum discount reached")
    
    print("\n" + "=" * 70)
    print("🎉 QUANTITATIVE PRICING SYSTEM TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    test_quantitative_pricing_system()