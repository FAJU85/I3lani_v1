"""
Button Fix Validation System
Tests and validates all button callbacks to ensure they work correctly
"""

import asyncio
import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN
from database import db, get_user_language
from languages import get_text

logger = logging.getLogger(__name__)

async def validate_button_functionality():
    """Validate that all main button callbacks are properly registered"""
    
    print("🔍 Button Functionality Validation")
    print("=" * 50)
    
    # Test callback handlers in handlers.py
    test_callbacks = [
        "create_ad",
        "back_to_main", 
        "language_settings",
        "contact_support",
        "help",
        "channel_partners",
        "share_win",
        "gaming_hub",
        "leaderboard"
    ]
    
    print("\n📋 Testing Main Button Callbacks:")
    
    for callback in test_callbacks:
        try:
            # Check if callback exists in handlers.py
            with open("handlers.py", "r", encoding="utf-8") as f:
                content = f.read()
                if f'F.data == "{callback}"' in content:
                    print(f"✅ {callback}: Handler found")
                else:
                    print(f"❌ {callback}: Handler NOT found")
        except Exception as e:
            print(f"❌ {callback}: Error checking - {e}")
    
    print("\n🔍 Testing Router Registration:")
    
    # Check if router is properly included in dispatcher
    try:
        with open("main_bot.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "setup_handlers(dp)" in content:
                print("✅ setup_handlers(dp) found in main_bot.py")
            else:
                print("❌ setup_handlers(dp) NOT found in main_bot.py")
    except Exception as e:
        print(f"❌ Error checking main_bot.py: {e}")
    
    # Check handlers.py setup function
    try:
        with open("handlers.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "dp.include_router(router)" in content:
                print("✅ dp.include_router(router) found in handlers.py")
            else:
                print("❌ dp.include_router(router) NOT found in handlers.py")
    except Exception as e:
        print(f"❌ Error checking handlers.py: {e}")
    
    print("\n🔍 Testing Bot Connection:")
    
    # Test bot connection
    try:
        bot = Bot(token=BOT_TOKEN)
        me = await bot.get_me()
        print(f"✅ Bot connected: @{me.username} (ID: {me.id})")
        await bot.session.close()
    except Exception as e:
        print(f"❌ Bot connection error: {e}")
    
    print("\n🔍 Testing Database Connection:")
    
    # Test database connection
    try:
        await db.init_db()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Button validation completed!")
    print("If all tests pass, buttons should work correctly.")

if __name__ == "__main__":
    asyncio.run(validate_button_functionality())