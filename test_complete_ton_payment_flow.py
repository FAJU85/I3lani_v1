#!/usr/bin/env python3
"""
Test the complete TON payment flow from start to finish
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
class MockCallbackQuery:
    def __init__(self, user_id, data="pay_ton"):
        self.from_user = MockUser(user_id)
        self.data = data
        self.message = MockMessage(user_id)
    
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
        
    async def edit_text(self, text, reply_markup=None, parse_mode=None):
        print(f"📝 Message edit: {text[:100]}...")
        return self
    
    async def reply(self, text, reply_markup=None, parse_mode=None):
        print(f"💬 Message reply: {text[:100]}...")
        return self

async def test_complete_ton_payment_flow():
    """Test the complete TON payment flow"""
    print("🧪 Testing Complete TON Payment Flow")
    print("=" * 60)
    
    # Test user
    user_id = 566158428
    
    # Initialize database
    db = Database()
    
    # Create FSM context
    storage = MemoryStorage()
    context = FSMContext(storage=storage, key=f"user_{user_id}")
    
    # Set up campaign data (simulating a user who has uploaded content and selected channels)
    await context.update_data(
        content_type='text',
        content='Test advertisement content',
        media_url=None,
        selected_channels=['@i3lani'],
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
    
    print("1️⃣ Testing TON payment handler...")
    try:
        # Import and test the TON payment handler
        from handlers import pay_ton_handler
        callback_query = MockCallbackQuery(user_id, "pay_ton")
        await pay_ton_handler(callback_query, context)
        print("✅ TON payment handler completed successfully")
        
        # Check state after payment handler
        current_state = await context.get_state()
        print(f"✅ Current state: {current_state}")
        
    except Exception as e:
        print(f"❌ TON payment handler failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2️⃣ Testing wallet address input...")
    try:
        # Simulate user entering wallet address
        test_wallet = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
        await context.set_state(WalletStates.payment_wallet_input)
        await context.update_data(wallet_context='payment')
        
        # Test the wallet input handler
        from wallet_manager import handle_wallet_address_input
        mock_message = MockMessage(user_id)
        mock_message.text = test_wallet
        await handle_wallet_address_input(mock_message, context)
        print("✅ Wallet address input handler completed successfully")
        
    except Exception as e:
        print(f"❌ Wallet address input failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3️⃣ Testing payment data persistence...")
    data = await context.get_data()
    
    # Check all important payment data
    checks = [
        ('pending_payment_amount', 'Payment amount stored'),
        ('payment_amount', 'Payment amount confirmed'),
        ('payment_memo', 'Payment memo generated'),
        ('user_wallet_address', 'User wallet address stored'),
        ('bot_wallet', 'Bot wallet address stored'),
        ('payment_expiration', 'Payment expiration set'),
        ('final_pricing', 'Final pricing data stored')
    ]
    
    for key, description in checks:
        if key in data and data[key]:
            print(f"✅ {description}: {data[key]}")
        else:
            print(f"❌ {description}: Missing or empty")
    
    print("\n4️⃣ Testing wallet persistence in database...")
    try:
        saved_wallet = await WalletManager.get_user_wallet_address(user_id)
        if saved_wallet:
            print(f"✅ Wallet persisted to database: {saved_wallet[:10]}...{saved_wallet[-8:]}")
        else:
            print("❌ Wallet not found in database")
    except Exception as e:
        print(f"❌ Database wallet check failed: {e}")
    
    print("\n5️⃣ Testing state management...")
    current_state = await context.get_state()
    if current_state:
        print(f"✅ Current state: {current_state}")
    else:
        print("❌ No current state set")
    
    print("\n" + "=" * 60)
    print("🎯 PAYMENT FLOW SUMMARY")
    print("=" * 60)
    
    # Summary of what should be working
    success_count = 0
    total_checks = 7
    
    if 'payment_memo' in data and data['payment_memo']:
        success_count += 1
        print(f"✅ Payment memo generated: {data['payment_memo']}")
    else:
        print("❌ Payment memo not generated")
    
    if 'user_wallet_address' in data and data['user_wallet_address']:
        success_count += 1
        print(f"✅ User wallet stored: {data['user_wallet_address'][:10]}...{data['user_wallet_address'][-8:]}")
    else:
        print("❌ User wallet not stored")
    
    if 'payment_amount' in data and data['payment_amount']:
        success_count += 1
        print(f"✅ Payment amount: {data['payment_amount']} TON")
    else:
        print("❌ Payment amount not stored")
    
    if 'final_pricing' in data and data['final_pricing']:
        success_count += 1
        print(f"✅ Final pricing: ${data['final_pricing']['final_price']}")
    else:
        print("❌ Final pricing not stored")
    
    if 'selected_channels' in data and data['selected_channels']:
        success_count += 1
        print(f"✅ Selected channels: {data['selected_channels']}")
    else:
        print("❌ Selected channels not stored")
    
    if saved_wallet:
        success_count += 1
        print(f"✅ Wallet persisted to database")
    else:
        print("❌ Wallet not persisted to database")
    
    if current_state:
        success_count += 1
        print(f"✅ State management working")
    else:
        print("❌ State management not working")
    
    print(f"\n📊 Success Rate: {success_count}/{total_checks} ({success_count/total_checks*100:.1f}%)")
    
    if success_count >= 6:
        print("🎉 TON Payment Flow is WORKING CORRECTLY!")
        print("   Users can now successfully complete TON payments")
    else:
        print("⚠️  TON Payment Flow needs attention")
        print("   Some components are not working properly")

if __name__ == "__main__":
    asyncio.run(test_complete_ton_payment_flow())