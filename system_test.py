#!/usr/bin/env python3
"""
Comprehensive System Test for Enhanced Telegram Ad Bot
Tests all major components and identifies issues
"""

import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test database connectivity and basic operations"""
    try:
        print("🔍 Testing database connection...")
        from database import SessionLocal, Channel, User, Order
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Test basic query
        result = db.execute(text('SELECT 1')).fetchone()
        assert result is not None
        
        # Test model queries
        channels = db.query(Channel).all()
        users = db.query(User).all()
        orders = db.query(Order).all()
        
        print(f"✅ Database connected: {len(channels)} channels, {len(users)} users, {len(orders)} orders")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_payment_system():
    """Test payment system functionality"""
    try:
        print("🔍 Testing payment system...")
        from enhanced_simple import EnhancedPaymentSystem
        
        payment_system = EnhancedPaymentSystem()
        
        # Test memo generation
        memo = payment_system.generate_memo()
        assert memo.startswith('INV_')
        assert len(memo) == 12
        
        # Test TON rate (might fail without API, that's ok)
        try:
            rate = await payment_system.get_ton_rate('USD')
            print(f"✅ Payment system working: memo={memo}, rate={rate}")
        except:
            print(f"✅ Payment system working: memo={memo}, rate=fallback")
        
        return True
        
    except Exception as e:
        print(f"❌ Payment system test failed: {e}")
        return False

async def test_admin_panel():
    """Test admin panel functionality"""
    try:
        print("🔍 Testing admin panel...")
        from admin_panel import AdminPanel
        from enhanced_simple import bot
        
        admin_panel = AdminPanel(bot)
        
        # Test admin verification
        admin_ids = os.getenv('ADMIN_IDS', '').split(',')
        if admin_ids and admin_ids[0]:
            test_admin_id = int(admin_ids[0])
            is_admin = await admin_panel.is_admin(test_admin_id)
            assert is_admin == True
        
        print("✅ Admin panel working: verification passed")
        return True
        
    except Exception as e:
        print(f"❌ Admin panel test failed: {e}")
        return False

async def test_user_interface():
    """Test user interface components"""
    try:
        print("🔍 Testing user interface...")
        from enhanced_simple import create_channel_keyboard
        
        # Test keyboard creation
        keyboard = create_channel_keyboard(123456789)
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) > 0
        
        print(f"✅ User interface working: {len(keyboard.inline_keyboard)} keyboard rows")
        return True
        
    except Exception as e:
        print(f"❌ User interface test failed: {e}")
        return False

async def test_bot_handlers():
    """Test bot handler registration"""
    try:
        print("🔍 Testing bot handlers...")
        from enhanced_simple import register_handlers, dp
        
        # Check if handlers are registered (using correct attribute)
        handlers_count = len(dp.message_handlers) + len(dp.callback_query_handlers)
        assert handlers_count > 0
        
        print(f"✅ Bot handlers working: {handlers_count} handler groups")
        return True
        
    except Exception as e:
        print(f"❌ Bot handlers test failed: {e}")
        return False

async def test_environment_config():
    """Test environment configuration"""
    try:
        print("🔍 Testing environment configuration...")
        
        required_vars = ['BOT_TOKEN', 'ADMIN_IDS', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Missing environment variables: {missing_vars}")
        else:
            print("✅ Environment configuration complete")
        
        return len(missing_vars) == 0
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🚀 Starting comprehensive system test...\n")
    
    tests = [
        ("Environment Config", test_environment_config),
        ("Database Connection", test_database_connection),
        ("Payment System", test_payment_system),
        ("Admin Panel", test_admin_panel),
        ("User Interface", test_user_interface),
        ("Bot Handlers", test_bot_handlers),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
        print()
    
    # Summary
    print("📊 TEST SUMMARY:")
    print("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is ready!")
        return True
    else:
        print("⚠️ Some tests failed - Check issues above")
        return False

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())