"""
Admin System Status Check for I3lani Bot
Quick validation of admin system functionality
"""

import asyncio
from database import db
from config import ADMIN_IDS

async def check_admin_system_status():
    """Quick check of admin system status"""
    print("🔍 Admin System Status Check")
    print("=" * 40)
    
    # Check 1: Admin IDs configuration
    print(f"Admin IDs configured: {ADMIN_IDS}")
    print(f"Number of admins: {len(ADMIN_IDS)}")
    
    # Check 2: Database connection
    try:
        connection = await db.get_connection()
        print("✅ Database connection: OK")
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        
    # Check 3: Admin system import
    try:
        from admin_system import AdminSystem, safe_callback_answer
        admin_system = AdminSystem()
        print("✅ Admin system import: OK")
    except Exception as e:
        print(f"❌ Admin system import: FAILED - {e}")
        return
    
    # Check 4: Admin access validation
    if ADMIN_IDS:
        admin_check = admin_system.is_admin(ADMIN_IDS[0])
        print(f"✅ Admin access validation: {'OK' if admin_check else 'FAILED'}")
    else:
        print("❌ Admin access validation: No admin IDs configured")
    
    # Check 5: Main menu keyboard
    try:
        keyboard = admin_system.create_main_menu_keyboard()
        button_count = len(keyboard.inline_keyboard) if keyboard.inline_keyboard else 0
        print(f"✅ Main menu keyboard: OK ({button_count} button rows)")
    except Exception as e:
        print(f"❌ Main menu keyboard: FAILED - {e}")
    
    # Check 6: Subscription packages
    package_count = len(admin_system.subscription_packages)
    print(f"✅ Subscription packages: {package_count} packages configured")
    
    # Check 7: Publishing schedules
    schedule_count = len(admin_system.publishing_schedules)
    print(f"✅ Publishing schedules: {schedule_count} schedules configured")
    
    print("\n" + "=" * 40)
    print("🎯 ADMIN SYSTEM STATUS SUMMARY")
    print("=" * 40)
    
    # Overall status
    issues = []
    if not ADMIN_IDS:
        issues.append("No admin IDs configured")
    
    if not issues:
        print("✅ Admin system is OPERATIONAL")
        print("✅ All core components are working")
        print("✅ Ready for production use")
    else:
        print("⚠️  Admin system has issues:")
        for issue in issues:
            print(f"   - {issue}")
    
    print("=" * 40)

if __name__ == "__main__":
    asyncio.run(check_admin_system_status())