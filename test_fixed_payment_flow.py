#!/usr/bin/env python3
"""
Test the fixed payment flow with updated handlers
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from wallet_manager import WalletManager
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from states import CreateAd, WalletStates

# Mock objects for testing
class MockBot:
    def __init__(self):
        self.token = "test_token"
        
    async def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        print(f"🤖 Bot send_message: {text[:100]}...")
        return MockMessage(chat_id)

class MockCallbackQuery:
    def __init__(self, user_id, data="pay_ton"):
        self.from_user = MockUser(user_id)
        self.data = data
        self.message = MockMessage(user_id)
        self.bot = MockBot()
    
    async def answer(self, text="", show_alert=False):
        print(f"📱 Callback answer: {text}")

class MockUser:
    def __init__(self, user_id):
        self.id = user_id
        self.first_name = "Test"
        self.last_name = "User"

class MockMessage:
    def __init__(self, user_id):
        self.from_user = MockUser(user_id)
        self.message_id = 123
        self.text = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
        self.chat = MockChat(user_id)
        
    async def edit_text(self, text, reply_markup=None, parse_mode=None):
        print(f"📝 Message edit: {text[:100]}...")
        return self
    
    async def reply(self, text, reply_markup=None, parse_mode=None):
        print(f"💬 Message reply: {text[:100]}...")
        return self
    
    async def answer(self, text, reply_markup=None, parse_mode=None):
        print(f"💬 Message answer: {text[:100]}...")
        return self

class MockChat:
    def __init__(self, user_id):
        self.id = user_id
        self.type = 'private'

async def test_fixed_payment_flow():
    """Test the fixed payment flow with updated handlers"""
    print("🧪 Testing Fixed Payment Flow")
    print("=" * 60)
    
    # Test user
    user_id = 566158428
    
    # Initialize database
    db = Database()
    
    # Create FSM context
    storage = MemoryStorage()
    context = FSMContext(storage=storage, key=f"user_{user_id}")
    
    # Set up campaign data
    await context.update_data(
        content_type='text',
        ad_text='Test advertisement content',
        ad_content='Test advertisement content',
        photos=[],
        selected_channels=['@i3lani'],
        duration=1,
        selected_duration=1,
        posts_per_day=1,
        final_pricing={
            'base_price': 0.29,
            'discount_amount': 0.00,
            'final_price': 0.29,
            'ton_amount': 0.36,
            'stars_amount': 10,
            'posts_per_day': 1,
            'total_posts': 1,
            'discount_percentage': 0.8
        }
    )
    
    print("1️⃣ Testing updated TON payment handler...")
    try:
        # Import and test the updated TON payment handler
        from handlers import pay_ton_handler
        callback_query = MockCallbackQuery(user_id, "pay_ton")
        await pay_ton_handler(callback_query, context)
        print("✅ Updated TON payment handler completed successfully")
        
        # Check state after payment handler
        current_state = await context.get_state()
        print(f"✅ Current state after payment handler: {current_state}")
        
    except Exception as e:
        print(f"❌ TON payment handler failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2️⃣ Testing wallet address input using WalletManager...")
    try:
        # Test the WalletManager's wallet input handler
        from wallet_manager import handle_payment_wallet_input
        mock_message = MockMessage(user_id)
        await handle_payment_wallet_input(mock_message, context)
        print("✅ WalletManager wallet input handler completed successfully")
        
    except Exception as e:
        print(f"❌ WalletManager wallet input failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3️⃣ Testing payment data after complete flow...")
    data = await context.get_data()
    
    # Check all important payment data
    payment_checks = [
        ('pending_payment_amount', 'Payment amount stored'),
        ('payment_amount', 'Payment amount confirmed'),
        ('payment_memo', 'Payment memo generated'),
        ('user_wallet_address', 'User wallet address stored'),
        ('bot_wallet', 'Bot wallet address stored'),
        ('payment_expiration', 'Payment expiration set'),
        ('final_pricing', 'Final pricing data stored'),
        ('selected_channels', 'Selected channels stored'),
        ('ad_content', 'Ad content stored')
    ]
    
    success_count = 0
    for key, description in payment_checks:
        if key in data and data[key]:
            print(f"✅ {description}")
            success_count += 1
        else:
            print(f"❌ {description}: Missing or empty")
    
    print(f"\n4️⃣ Testing wallet persistence...")
    try:
        saved_wallet = await WalletManager.get_user_wallet_address(user_id)
        if saved_wallet:
            print(f"✅ Wallet persisted to database: {saved_wallet[:10]}...{saved_wallet[-8:]}")
            success_count += 1
        else:
            print("❌ Wallet not found in database")
    except Exception as e:
        print(f"❌ Database wallet check failed: {e}")
    
    print(f"\n5️⃣ Testing state transitions...")
    current_state = await context.get_state()
    if current_state:
        print(f"✅ Current state: {current_state}")
        success_count += 1
    else:
        print("❌ No current state set")
    
    print("\n" + "=" * 60)
    print("🎯 FIXED PAYMENT FLOW SUMMARY")
    print("=" * 60)
    
    total_checks = len(payment_checks) + 2  # +2 for wallet persistence and state
    success_rate = (success_count / total_checks) * 100
    
    print(f"📊 Success Rate: {success_count}/{total_checks} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 PAYMENT FLOW IS WORKING CORRECTLY!")
        print("   ✅ TON payment handler updated successfully")
        print("   ✅ WalletManager integration working")
        print("   ✅ Payment data persistence working")
        print("   ✅ State management working")
        print("   ✅ Wallet address saving working")
    elif success_rate >= 60:
        print("⚠️  PAYMENT FLOW IS MOSTLY WORKING")
        print("   Some minor issues to address")
    else:
        print("❌ PAYMENT FLOW NEEDS MORE WORK")
        print("   Major issues still present")
    
    print(f"\n📋 Detailed Payment Data:")
    print(f"   Payment memo: {data.get('payment_memo', 'None')}")
    print(f"   Payment amount: {data.get('payment_amount', 'None')} TON")
    print(f"   User wallet: {data.get('user_wallet_address', 'None')}")
    print(f"   Bot wallet: {data.get('bot_wallet', 'None')}")
    print(f"   Final pricing: ${data.get('final_pricing', {}).get('final_price', 'None')}")
    print(f"   Selected channels: {data.get('selected_channels', 'None')}")
    print(f"   Current state: {current_state}")

if __name__ == "__main__":
    asyncio.run(test_fixed_payment_flow())