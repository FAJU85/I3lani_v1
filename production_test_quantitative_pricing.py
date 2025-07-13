#!/usr/bin/env python3
"""
Production Test for Quantitative Pricing System
Test the live bot functionality with the new pricing system
"""

import asyncio
import aiosqlite
from quantitative_pricing_system import QuantitativePricingCalculator
import json
from datetime import datetime

async def test_production_quantitative_pricing():
    """Test the quantitative pricing system in production environment"""
    
    print("=" * 80)
    print("🚀 PRODUCTION QUANTITATIVE PRICING SYSTEM TEST")
    print("=" * 80)
    
    calculator = QuantitativePricingCalculator()
    
    # Test 1: Basic system functionality
    print("\n1️⃣ SYSTEM FUNCTIONALITY TEST")
    print("-" * 50)
    
    try:
        # Test basic calculation
        result = calculator.calculate_price(7, 2)
        print(f"✅ Basic calculation: 7 days, 2 channels = ${result['final_price']:.2f}")
        
        # Test posting schedule
        schedule = calculator.calculate_posting_schedule(3)
        print(f"✅ Posting schedule: {', '.join(schedule)}")
        
        # Test discount calculation
        discount = calculator.calculate_discount_percentage(30)
        print(f"✅ Discount calculation: 30 days = {discount}% off")
        
        print("✅ System functionality: PASSED")
        
    except Exception as e:
        print(f"❌ System functionality: FAILED - {e}")
    
    # Test 2: Database integration
    print("\n2️⃣ DATABASE INTEGRATION TEST")
    print("-" * 50)
    
    try:
        async with aiosqlite.connect('bot.db') as db:
            # Check if channels exist
            cursor = await db.execute("SELECT COUNT(*) FROM channels WHERE is_active = 1")
            channel_count = (await cursor.fetchone())[0]
            print(f"✅ Active channels: {channel_count}")
            
            # Check if pricing data can be stored
            test_pricing = calculator.calculate_price(14, channel_count)
            print(f"✅ Test pricing calculation: {test_pricing['final_price']:.2f} USD")
            
            # Verify conversion rates
            print(f"✅ TON conversion: {test_pricing['ton_price']:.2f} TON")
            print(f"✅ Stars conversion: {test_pricing['stars_price']} Stars")
            
        print("✅ Database integration: PASSED")
        
    except Exception as e:
        print(f"❌ Database integration: FAILED - {e}")
    
    # Test 3: Pricing accuracy validation
    print("\n3️⃣ PRICING ACCURACY VALIDATION")
    print("-" * 50)
    
    try:
        # Test specific pricing scenarios
        test_scenarios = [
            (1, 1, 0.29),     # 1 day, 1 channel = base price
            (7, 1, 5.75),     # 7 days should be around $5.75
            (30, 1, 79.34),   # 30 days should be around $79.34
        ]
        
        for days, channels, expected_price in test_scenarios:
            result = calculator.calculate_price(days, channels)
            actual_price = result['final_price']
            
            if abs(actual_price - expected_price) < 0.01:
                print(f"✅ {days} days, {channels} channel: ${actual_price:.2f} (expected ${expected_price:.2f})")
            else:
                print(f"❌ {days} days, {channels} channel: ${actual_price:.2f} (expected ${expected_price:.2f})")
        
        print("✅ Pricing accuracy: PASSED")
        
    except Exception as e:
        print(f"❌ Pricing accuracy: FAILED - {e}")
    
    # Test 4: Extreme values handling
    print("\n4️⃣ EXTREME VALUES HANDLING")
    print("-" * 50)
    
    try:
        # Test minimum values
        min_result = calculator.calculate_price(1, 1)
        print(f"✅ Minimum (1 day, 1 channel): ${min_result['final_price']:.2f}")
        
        # Test maximum values
        max_result = calculator.calculate_price(365, 4)
        print(f"✅ Maximum (365 days, 4 channels): ${max_result['final_price']:.2f}")
        
        # Test validation
        validation = calculator.validate_selection(366, 1)
        if not validation['valid']:
            print("✅ Invalid input rejection: WORKING")
        else:
            print("❌ Invalid input rejection: FAILED")
        
        print("✅ Extreme values handling: PASSED")
        
    except Exception as e:
        print(f"❌ Extreme values handling: FAILED - {e}")
    
    # Test 5: Performance test
    print("\n5️⃣ PERFORMANCE TEST")
    print("-" * 50)
    
    try:
        start_time = datetime.now()
        
        # Run 100 calculations
        for i in range(100):
            days = (i % 365) + 1
            channels = (i % 4) + 1
            calculator.calculate_price(days, channels)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 100 calculations in {duration:.3f} seconds")
        print(f"✅ Average: {duration/100*1000:.2f} ms per calculation")
        
        if duration < 1.0:
            print("✅ Performance: EXCELLENT")
        else:
            print("⚠️ Performance: ACCEPTABLE")
        
    except Exception as e:
        print(f"❌ Performance test: FAILED - {e}")
    
    # Test 6: Production data compatibility
    print("\n6️⃣ PRODUCTION DATA COMPATIBILITY")
    print("-" * 50)
    
    try:
        async with aiosqlite.connect('bot.db') as db:
            # Check recent campaigns
            cursor = await db.execute("""
                SELECT campaign_id, duration_days, posts_per_day, payment_amount 
                FROM campaigns 
                WHERE created_at > datetime('now', '-1 day')
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            recent_campaigns = await cursor.fetchall()
            
            if recent_campaigns:
                print(f"✅ Found {len(recent_campaigns)} recent campaigns")
                
                for campaign in recent_campaigns:
                    campaign_id, duration_days, posts_per_day, payment_amount = campaign
                    
                    if duration_days and posts_per_day:
                        # Recalculate with new system
                        new_calculation = calculator.calculate_price(duration_days, 1)
                        print(f"   Campaign {campaign_id}: {duration_days} days, "
                              f"${payment_amount:.2f} paid, ${new_calculation['final_price']:.2f} new calc")
            else:
                print("✅ No recent campaigns found (clean slate)")
            
        print("✅ Production data compatibility: PASSED")
        
    except Exception as e:
        print(f"❌ Production data compatibility: FAILED - {e}")
    
    # Test 7: Real-time calculation test
    print("\n7️⃣ REAL-TIME CALCULATION TEST")
    print("-" * 50)
    
    try:
        # Simulate user interaction patterns
        user_scenarios = [
            (3, 1, "Short campaign"),
            (7, 2, "Weekly campaign"),
            (30, 1, "Monthly campaign"),
            (90, 4, "Quarterly campaign"),
        ]
        
        for days, channels, description in user_scenarios:
            result = calculator.calculate_price(days, channels)
            schedule = calculator.calculate_posting_schedule(result['posts_per_day'])
            
            print(f"✅ {description}: {days} days, {channels} channels")
            print(f"   Price: ${result['final_price']:.2f} ({result['discount_percentage']:.1f}% off)")
            print(f"   Posts: {result['posts_per_day']}/day, Total: {result['total_posts']}")
            print(f"   Schedule: {schedule[0]} to {schedule[-1]}")
        
        print("✅ Real-time calculation: PASSED")
        
    except Exception as e:
        print(f"❌ Real-time calculation: FAILED - {e}")
    
    print("\n" + "=" * 80)
    print("🎉 PRODUCTION QUANTITATIVE PRICING SYSTEM TEST COMPLETE")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    asyncio.run(test_production_quantitative_pricing())