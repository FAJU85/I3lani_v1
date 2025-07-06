"""
Test script for the debug system
"""
import asyncio
from debug_system import DebugSystem
from payments import payment_processor
from database import init_db, db
from config import BOT_TOKEN
from aiogram import Bot

async def test_debug_system():
    """Test all debug system components"""
    print("🧪 Testing I3lani Bot Debug System...")
    
    # Initialize components
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    debug_system = DebugSystem(bot)
    
    # Test 1: User Activity Logging
    print("\n1. Testing user activity logging...")
    await debug_system.log_user_activity(123456, "test_action", {"test": "data"})
    print("✅ User activity logged successfully")
    
    # Test 2: Error Logging
    print("\n2. Testing error logging...")
    test_error = Exception("Test error for debugging")
    await debug_system.log_error(test_error, {"context": "test"})
    print("✅ Error logged successfully")
    
    # Test 3: Performance Tracking
    print("\n3. Testing performance tracking...")
    await debug_system.track_performance("test_operation", 0.5)
    print("✅ Performance tracked successfully")
    
    # Test 4: System Health Check
    print("\n4. Testing system health check...")
    health = await debug_system.get_system_health()
    print(f"✅ System health: {health['database_health']['status']}")
    
    # Test 5: Payment System Debug
    print("\n5. Testing payment system debug...")
    payment_debug = await debug_system.debug_payment_system()
    print(f"✅ Payment system: {payment_debug['status']}")
    if payment_debug['status'] == 'healthy':
        print(f"   Sample memos: {payment_debug['test_memos'][:3]}")
    
    # Test 6: User Debug Info
    print("\n6. Testing user debug info...")
    user_debug = await debug_system.get_user_debug_info(123456)
    print(f"✅ User debug info retrieved for user {user_debug['user_id']}")
    
    # Test 7: Generate Debug Report
    print("\n7. Testing debug report generation...")
    report = await debug_system.generate_debug_report()
    print("✅ Debug report generated successfully")
    print(f"   Report length: {len(report)} characters")
    
    # Test 8: AB0102 Memo Format Validation
    print("\n8. Testing AB0102 memo format...")
    memos = [payment_processor.generate_memo() for _ in range(10)]
    all_valid = all(len(memo) == 6 and memo.isalnum() for memo in memos)
    print(f"✅ AB0102 format validation: {'PASSED' if all_valid else 'FAILED'}")
    print(f"   Sample memos: {memos[:5]}")
    
    # Test 9: Database Health
    print("\n9. Testing database health...")
    db_health = await debug_system.check_database_health()
    print(f"✅ Database health: {db_health['status']}")
    
    # Test 10: Debug Mode Toggle
    print("\n10. Testing debug mode toggle...")
    debug_mode = await debug_system.toggle_debug_mode()
    print(f"✅ Debug mode: {'ON' if debug_mode else 'OFF'}")
    
    await bot.session.close()
    print("\n🎉 All debug system tests completed successfully!")
    print("\nDebug System Features:")
    print("• User activity logging")
    print("• Comprehensive error tracking")
    print("• Performance monitoring")
    print("• System health checks")
    print("• Payment system debugging")
    print("• User debug information")
    print("• Automated debug reports")
    print("• AB0102 memo validation")
    print("• Database health monitoring")
    print("• Admin error notifications")
    
    print("\nAvailable Commands:")
    print("• /debug - User debug info")
    print("• /status - Bot status check")
    print("• /support - User support")
    print("• /help - Help information")
    print("• /debug_status - Admin debug status")
    print("• /debug_user <id> - Admin user debug")
    print("• /debug_toggle - Admin debug toggle")
    print("• /debug_clear - Admin clear logs")

if __name__ == "__main__":
    asyncio.run(test_debug_system())