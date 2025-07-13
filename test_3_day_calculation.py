#!/usr/bin/env python3
"""
Test 3-day calculation to verify correct implementation
"""

import math
from quantitative_pricing_system import QuantitativePricingCalculator

calc = QuantitativePricingCalculator()

# Test 3 days calculation
days = 3
channels = 1  # Single channel test

print('=== 3-Day Campaign Analysis ===')
print(f'Days: {days}')
print()

# Step 1: Posts per day calculation
posts_per_day = calc.calculate_posts_per_day(days)
print(f'Posts per day formula: R = min(12, max(1, ⌊{days}/2.5⌋ + 1))')
print(f'                     = min(12, max(1, ⌊{days/2.5}⌋ + 1))')
print(f'                     = min(12, max(1, {math.floor(days/2.5)} + 1))')
print(f'                     = min(12, max(1, {math.floor(days/2.5) + 1}))')
print(f'                     = {posts_per_day}')
print()

# Step 2: Discount calculation
discount = calc.calculate_discount_percentage(days)
print(f'Discount formula: δ = min(25%, {days} × 0.8%)')
print(f'                = min(25%, {days * 0.8}%)')
print(f'                = {discount}%')
print()

# Step 3: Price calculation
result = calc.calculate_price(days, channels)
print(f'Base price: {days} days × {posts_per_day} posts/day × {channels} channels × $0.29')
print(f'          = {days * posts_per_day * channels * 0.29:.2f}')
print()
print(f'Final price: ${result["base_price"]:.2f} × (1 - {discount/100:.3f})')
print(f'           = ${result["base_price"]:.2f} × {1 - discount/100:.3f}')
print(f'           = ${result["final_price"]:.2f}')
print()

# Step 4: Schedule
schedule = calc.calculate_posting_schedule(posts_per_day)
print(f'Posting schedule for {posts_per_day} posts/day: {schedule}')
print()

# Step 5: Total posts
total_posts = days * posts_per_day * channels
print(f'Total posts: {days} days × {posts_per_day} posts/day × {channels} channels = {total_posts}')
print()

# Step 6: Currency conversion
print(f'TON price: ${result["final_price"]:.2f} × 0.36 = {result["ton_price"]:.2f} TON')
print(f'Stars price: ${result["final_price"]:.2f} × 34 = {result["stars_price"]} Stars')
print()

# Verify expected values
print('=== VERIFICATION ===')
print(f'Expected posts per day: 2 (actual: {posts_per_day}) - {"✅" if posts_per_day == 2 else "❌"}')
print(f'Expected total posts: 6 (actual: {total_posts}) - {"✅" if total_posts == 6 else "❌"}')
print(f'Expected base price: $1.74 (actual: ${result["base_price"]:.2f}) - {"✅" if abs(result["base_price"] - 1.74) < 0.01 else "❌"}')
print(f'Expected final price: $1.70 (actual: ${result["final_price"]:.2f}) - {"✅" if abs(result["final_price"] - 1.70) < 0.01 else "❌"}')
print(f'Expected TON: 0.61 (actual: {result["ton_price"]:.2f}) - {"✅" if abs(result["ton_price"] - 0.61) < 0.01 else "❌"}')
print(f'Expected Stars: 58 (actual: {result["stars_price"]}) - {"✅" if result["stars_price"] == 58 else "❌"}')
print(f'Expected schedule: ["00:00", "12:00"] (actual: {schedule}) - {"✅" if schedule == ["00:00", "12:00"] else "❌"}')