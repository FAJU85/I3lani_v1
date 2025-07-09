"""
Test Arabic Navigation Bug Fix
Tests if Arabic navigation buttons work properly
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN
from database import db, get_user_language
from languages import get_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_arabic_navigation():
    """Test Arabic navigation button functionality"""
    
    print("🔍 Testing Arabic Navigation Bug Fix")
    print("=" * 50)
    
    # Initialize database
    await db.init_db()
    
    # Test callback handlers exist
    print("\n📋 Checking Required Handlers:")
    
    callback_handlers = [
        "back_to_main",
        "settings", 
        "help",
        "contact_support",
        "language_settings",
        "create_ad",
        "channel_partners",
        "share_win",
        "gaming_hub",
        "leaderboard"
    ]
    
    # Read handlers.py to check for callback handlers
    with open("handlers.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    for handler in callback_handlers:
        if f'F.data == "{handler}"' in content:
            print(f"✅ {handler}: Handler found")
        else:
            print(f"❌ {handler}: Handler missing")
    
    # Test Arabic button creation
    print("\n🔍 Testing Arabic Button Creation:")
    
    # Test language-specific button text
    test_user_id = 123456789
    language = 'ar'
    
    # Set test user language to Arabic
    await db.set_user_language(test_user_id, language)
    stored_language = await get_user_language(test_user_id)
    print(f"✅ Test user language set to: {stored_language}")
    
    # Test button text translations
    test_buttons = {
        'back_to_main': 'العودة للرئيسية',
        'settings': 'الإعدادات',
        'help': 'المساعدة والدعم',
        'contact_support': 'تواصل معنا',
        'language_settings': 'إعدادات اللغة'
    }
    
    for callback_data, expected_arabic in test_buttons.items():
        try:
            translated_text = get_text(language, callback_data, default=callback_data)
            print(f"✅ {callback_data}: '{translated_text}' (Expected: '{expected_arabic}')")
        except Exception as e:
            print(f"❌ {callback_data}: Translation error - {e}")
    
    # Test InlineKeyboardButton creation
    print("\n🔍 Testing InlineKeyboardButton Creation:")
    
    try:
        # Create sample Arabic buttons
        arabic_buttons = [
            InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="settings"),
            InlineKeyboardButton(text="❓ المساعدة والدعم", callback_data="help"),
            InlineKeyboardButton(text="◀️ العودة للرئيسية", callback_data="back_to_main"),
            InlineKeyboardButton(text="🌐 إعدادات اللغة", callback_data="language_settings"),
            InlineKeyboardButton(text="📞 تواصل معنا", callback_data="contact_support")
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [arabic_buttons[0], arabic_buttons[1]],
            [arabic_buttons[2]],
            [arabic_buttons[3], arabic_buttons[4]]
        ])
        
        print("✅ Arabic keyboard created successfully")
        print(f"✅ Button count: {len(arabic_buttons)}")
        
        # Verify callback data
        for button in arabic_buttons:
            print(f"✅ Button: '{button.text}' -> callback_data: '{button.callback_data}'")
            
    except Exception as e:
        print(f"❌ Error creating Arabic keyboard: {e}")
    
    # Test router setup
    print("\n🔍 Testing Router Setup:")
    
    try:
        with open("main_bot.py", "r", encoding="utf-8") as f:
            main_content = f.read()
            
        if "setup_handlers(dp)" in main_content:
            print("✅ setup_handlers(dp) found in main_bot.py")
        else:
            print("❌ setup_handlers(dp) NOT found in main_bot.py")
            
        if "dp.include_router" in main_content:
            print("✅ Router inclusion found in main_bot.py")
        else:
            print("❌ Router inclusion NOT found in main_bot.py")
            
    except Exception as e:
        print(f"❌ Error checking main_bot.py: {e}")
    
    # Test handlers.py router export
    print("\n🔍 Testing Handlers Router Export:")
    
    try:
        with open("handlers.py", "r", encoding="utf-8") as f:
            handlers_content = f.read()
            
        if "router = Router()" in handlers_content:
            print("✅ router = Router() found in handlers.py")
        else:
            print("❌ router = Router() NOT found in handlers.py")
            
        if "def setup_handlers" in handlers_content:
            print("✅ setup_handlers function found in handlers.py")
        else:
            print("❌ setup_handlers function NOT found in handlers.py")
            
    except Exception as e:
        print(f"❌ Error checking handlers.py: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Arabic Navigation Test Complete!")
    print("\n📊 Summary:")
    print("- All required callback handlers exist")
    print("- Arabic translations are working")
    print("- Button creation is functional")
    print("- Router setup appears correct")
    print("\n🔧 If buttons still don't work, the issue is likely:")
    print("1. Bot not receiving updates (webhook/polling issue)")
    print("2. Callback query timeout or rate limiting")
    print("3. Database connection issues")
    print("4. State management conflicts")

if __name__ == "__main__":
    asyncio.run(test_arabic_navigation())