#!/usr/bin/env python3
"""
Debug script to simulate exact user interaction flow
"""

import asyncio
from aiogram import Bot
from aiogram.types import User, Message, CallbackQuery, InlineKeyboardMarkup
from config import BOT_TOKEN
from handlers import handle_ad_content, handle_package_selection
from keyboards import get_package_keyboard
from models import InMemoryStorage
from handlers import AdStates
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, Dispatcher

class MockMessage:
    def __init__(self, user_id, text):
        self.from_user = User(id=user_id, is_bot=False, first_name="Test")
        self.text = text
        self.content_type = "text"
        
    async def reply(self, text, reply_markup=None, parse_mode=None):
        print(f"📤 Bot Reply: {text[:100]}...")
        if reply_markup:
            print(f"📋 Keyboard: {len(reply_markup.inline_keyboard)} rows")
            for row in reply_markup.inline_keyboard:
                for btn in row:
                    print(f"   - {btn.text} -> {btn.callback_data}")

class MockCallbackQuery:
    def __init__(self, user_id, data):
        self.from_user = User(id=user_id, is_bot=False, first_name="Test")
        self.data = data
        self.message = MockMessage(user_id, "")
        
    async def answer(self, text=""):
        print(f"⚡ Callback Answer: {text}")

async def test_user_flow():
    """Test the complete user flow"""
    print("🧪 TESTING COMPLETE USER FLOW")
    print("=" * 50)
    
    # Test user
    user_id = 123456
    
    # Initialize storage and states
    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    
    print("\n1. User submits ad content:")
    print("   User sends: 'This is my advertisement'")
    
    # Create mock message
    message = MockMessage(user_id, "This is my advertisement")
    
    # Set up FSM context
    context = FSMContext(storage, user_id, user_id)
    await context.set_state(AdStates.waiting_for_ad)
    
    try:
        # Call the handler
        await handle_ad_content(message, context)
        print("   ✅ Ad content handler completed")
    except Exception as e:
        print(f"   ❌ Ad content handler failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2. User clicks on package button:")
    print("   User clicks: 'Starter - 0.099 TON'")
    
    # Create mock callback query
    callback = MockCallbackQuery(user_id, "package_starter")
    
    try:
        # Call the package selection handler
        await handle_package_selection(callback, context)
        print("   ✅ Package selection handler completed")
    except Exception as e:
        print(f"   ❌ Package selection handler failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Testing package keyboard generation:")
    try:
        keyboard = get_package_keyboard(user_id)
        print(f"   ✅ Generated keyboard with {len(keyboard.inline_keyboard)} rows")
        
        # Test each button
        for row in keyboard.inline_keyboard:
            for btn in row:
                print(f"   📋 {btn.text} -> {btn.callback_data}")
                
                # Test callback data parsing
                package_id = btn.callback_data.replace("package_", "")
                print(f"      Package ID: {package_id}")
                
    except Exception as e:
        print(f"   ❌ Keyboard generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n4. Testing storage interaction:")
    from models import storage as global_storage
    
    # Check if ad was created
    ad = global_storage.get_user_current_ad(user_id)
    if ad:
        print(f"   ✅ Ad found: {ad.id}")
        print(f"   📝 Content: {ad.content.text}")
        print(f"   📦 Package: {ad.package_id}")
    else:
        print("   ❌ No ad found in storage")
    
    await bot.session.close()
    print("\n" + "=" * 50)
    print("🏁 USER FLOW TEST COMPLETED")

if __name__ == "__main__":
    asyncio.run(test_user_flow())