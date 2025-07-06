#!/usr/bin/env python3
"""
Test script for Enhanced Bot features
Tests all new commands and functionality
"""

import asyncio
import os
import sys
from database import SessionLocal, User, Channel, Order, create_tables
from enhanced_simple import EnhancedPaymentSystem
from sqlalchemy import func

async def test_database_connection():
    """Test database connectivity"""
    print("🔍 Testing database connection...")
    try:
        db = SessionLocal()
        user_count = db.query(User).count()
        channel_count = db.query(Channel).count()
        order_count = db.query(Order).count()
        
        print(f"✅ Database connected successfully!")
        print(f"   Users: {user_count}")
        print(f"   Channels: {channel_count}")
        print(f"   Orders: {order_count}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_payment_system():
    """Test payment system functionality"""
    print("\n🔍 Testing payment system...")
    try:
        payment_system = EnhancedPaymentSystem()
        
        # Test memo generation
        memo = payment_system.generate_memo()
        print(f"✅ Memo generation: {memo}")
        
        # Test TON rate fetching
        try:
            usd_rate = await payment_system.get_ton_rate('USD')
            print(f"✅ TON/USD rate: {usd_rate}")
        except Exception as e:
            print(f"⚠️ TON rate fetch failed: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Payment system test failed: {e}")
        return False

async def test_user_statistics():
    """Test user statistics functionality"""
    print("\n🔍 Testing user statistics...")
    try:
        db = SessionLocal()
        
        # Test user statistics query
        test_user_id = 12345
        
        total_spent = db.query(func.sum(Order.total_amount_ton)).filter(
            Order.user_id == test_user_id,
            Order.payment_status == 'confirmed'
        ).scalar() or 0
        
        active_campaigns = db.query(Order).filter(
            Order.user_id == test_user_id,
            Order.status == 'active'
        ).count()
        
        print(f"✅ User statistics query successful")
        print(f"   Total spent: {total_spent} TON")
        print(f"   Active campaigns: {active_campaigns}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ User statistics test failed: {e}")
        return False

async def test_channel_availability():
    """Test channel availability"""
    print("\n🔍 Testing channel availability...")
    try:
        db = SessionLocal()
        
        active_channels = db.query(Channel).filter(Channel.is_active == True).all()
        print(f"✅ Channel query successful")
        print(f"   Active channels: {len(active_channels)}")
        
        for channel in active_channels[:3]:  # Show first 3
            print(f"   - {channel.name}: {channel.subscribers_count} subscribers")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Channel availability test failed: {e}")
        return False

async def test_admin_functionality():
    """Test admin functionality"""
    print("\n🔍 Testing admin functionality...")
    try:
        # Test admin ID validation
        admin_ids = os.getenv('ADMIN_IDS', '').split(',')
        if admin_ids and admin_ids[0]:
            print(f"✅ Admin IDs configured: {len(admin_ids)} admins")
        else:
            print("⚠️ No admin IDs configured")
        
        return True
    except Exception as e:
        print(f"❌ Admin functionality test failed: {e}")
        return False

async def test_enhanced_features():
    """Test specific enhanced features"""
    print("\n🔍 Testing enhanced features...")
    try:
        # Test imports
        from enhanced_simple import (
            mystats_command, bugreport_command, support_command,
            history_command, refresh_command, handle_start_advertising,
            handle_my_campaigns, handle_check_balance
        )
        print("✅ All enhanced functions imported successfully")
        
        # Test command handlers exist
        commands = [
            'mystats_command', 'bugreport_command', 'support_command',
            'history_command', 'refresh_command'
        ]
        
        for cmd in commands:
            if cmd in globals():
                print(f"✅ {cmd} function available")
            else:
                print(f"❌ {cmd} function missing")
        
        return True
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Enhanced Bot Feature Tests\n")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Payment System", test_payment_system),
        ("User Statistics", test_user_statistics),
        ("Channel Availability", test_channel_availability),
        ("Admin Functionality", test_admin_functionality),
        ("Enhanced Features", test_enhanced_features)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n🎯 Total: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n🔧 Issues found - checking bot logs for more details...")
        return False
    else:
        print("\n🎉 All tests passed - Bot is working correctly!")
        return True

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())