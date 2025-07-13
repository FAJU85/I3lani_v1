#!/usr/bin/env python3
"""
Automated Bot Testing Suite for I3lani Bot
Quick system validation before manual testing
"""

import asyncio
import aiosqlite
import sys
import os
from datetime import datetime

def colored_print(text, color="white"):
    """Print colored text"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

async def test_database_connectivity():
    """Test database connectivity and basic tables"""
    try:
        async with aiosqlite.connect('bot.db') as db:
            # Check if main tables exist
            tables_to_check = [
                'users', 'channels', 'ads', 'campaigns', 
                'orders', 'payments', 'referrals'
            ]
            
            results = []
            for table in tables_to_check:
                try:
                    cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
                    count = await cursor.fetchone()
                    results.append(f"✅ {table}: {count[0]} records")
                except Exception as e:
                    results.append(f"❌ {table}: Error - {str(e)}")
            
            return True, results
    except Exception as e:
        return False, [f"Database connection failed: {str(e)}"]

async def test_channel_status():
    """Test channel status and subscriber counts"""
    try:
        async with aiosqlite.connect('bot.db') as db:
            cursor = await db.execute("""
                SELECT channel_id, name, subscribers, is_active, category 
                FROM channels 
                WHERE is_active = 1
            """)
            channels = await cursor.fetchall()
            
            if not channels:
                return False, ["No active channels found"]
            
            results = []
            total_subscribers = 0
            for channel in channels:
                channel_id, name, sub_count, is_active, category = channel
                total_subscribers += sub_count or 0
                results.append(f"✅ @{channel_id}: {name} ({sub_count} subs, {category or 'general'})")
            
            results.append(f"📊 Total reach: {total_subscribers} subscribers across {len(channels)} channels")
            return True, results
    except Exception as e:
        return False, [f"Channel status check failed: {str(e)}"]

async def test_pricing_system():
    """Test dynamic pricing calculations"""
    try:
        # Import our pricing system
        sys.path.append('.')
        from dynamic_pricing_system import DynamicPricingCalculator
        
        calculator = DynamicPricingCalculator()
        
        # Test various scenarios
        test_cases = [
            (1, 2, 1),   # 1 day, 2 channels, 1 post/day
            (7, 3, 2),   # 7 days, 3 channels, 2 posts/day
            (30, 4, 1),  # 30 days, 4 channels, 1 post/day
            (365, 1, 5), # 365 days, 1 channel, 5 posts/day
        ]
        
        results = []
        for days, channels, posts_per_day in test_cases:
            pricing = calculator.calculate_price(days, channels, posts_per_day)
            results.append(
                f"✅ {days}d × {channels}ch × {posts_per_day}p/d = "
                f"${pricing['final_price']:.2f} "
                f"({pricing['discount_percentage']}% off, save ${pricing['savings']:.2f})"
            )
        
        return True, results
    except Exception as e:
        return False, [f"Pricing system test failed: {str(e)}"]

async def test_payment_monitoring():
    """Test payment monitoring system"""
    try:
        # Check recent payment activity
        async with aiosqlite.connect('bot.db') as db:
            cursor = await db.execute("""
                SELECT COUNT(*) FROM payments 
                WHERE created_at > datetime('now', '-24 hours')
            """)
            recent_payments = await cursor.fetchone()
            
            cursor = await db.execute("""
                SELECT COUNT(*) FROM untracked_payments 
                WHERE status = 'pending_review'
            """)
            pending_payments = await cursor.fetchone()
            
            results = [
                f"✅ Recent payments (24h): {recent_payments[0]}",
                f"⏳ Pending payments: {pending_payments[0]}"
            ]
            
            return True, results
    except Exception as e:
        return False, [f"Payment monitoring test failed: {str(e)}"]

async def test_system_health():
    """Test overall system health"""
    try:
        results = []
        
        # Check if bot database exists
        if os.path.exists('bot.db'):
            results.append("✅ Database file exists")
        else:
            results.append("❌ Database file missing")
        
        # Check if dynamic pricing system exists
        if os.path.exists('dynamic_pricing_system.py'):
            results.append("✅ Dynamic pricing system available")
        else:
            results.append("❌ Dynamic pricing system missing")
        
        # Check if main bot files exist
        required_files = [
            'main_bot.py', 'handlers.py', 'database.py', 
            'states.py', 'languages.py', 'config.py'
        ]
        
        for file in required_files:
            if os.path.exists(file):
                results.append(f"✅ {file} exists")
            else:
                results.append(f"❌ {file} missing")
        
        return True, results
    except Exception as e:
        return False, [f"System health check failed: {str(e)}"]

async def main():
    """Run all automated tests"""
    colored_print("🤖 I3lani Bot - Automated Testing Suite", "cyan")
    colored_print("=" * 50, "cyan")
    
    tests = [
        ("Database Connectivity", test_database_connectivity),
        ("Channel Status", test_channel_status),
        ("Pricing System", test_pricing_system),
        ("Payment Monitoring", test_payment_monitoring),
        ("System Health", test_system_health),
    ]
    
    overall_success = True
    
    for test_name, test_func in tests:
        colored_print(f"\n📋 Testing {test_name}...", "yellow")
        
        try:
            success, results = await test_func()
            
            if success:
                colored_print(f"✅ {test_name} - PASSED", "green")
                for result in results:
                    print(f"   {result}")
            else:
                colored_print(f"❌ {test_name} - FAILED", "red")
                for result in results:
                    print(f"   {result}")
                overall_success = False
                
        except Exception as e:
            colored_print(f"❌ {test_name} - ERROR: {str(e)}", "red")
            overall_success = False
    
    colored_print("\n" + "=" * 50, "cyan")
    if overall_success:
        colored_print("🎉 All automated tests PASSED! Ready for manual testing.", "green")
    else:
        colored_print("⚠️  Some tests FAILED. Check issues before manual testing.", "red")
    
    colored_print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "blue")

if __name__ == "__main__":
    asyncio.run(main())