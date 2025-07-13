#!/usr/bin/env python3
"""
Test the exact user payment flow to identify the wallet saving issue
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

# Mock callback query for testing
class MockCallbackQuery:
    def __init__(self, user_id, data="use_existing_wallet_payment"):
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

async def test_user_payment_flow():
    """Test the exact user payment flow that's causing issues"""
    print("🧪 Testing User Payment Flow")
    print("=" * 60)
    
    # Use the actual user ID from the logs
    user_id = 566158428
    test_wallet = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
    
    # Initialize database
    db = Database()
    
    # Create FSM context
    storage = MemoryStorage()
    context = FSMContext(storage=storage, key=f"user_{user_id}")
    
    # Simulate payment data from earlier in the flow
    await context.update_data(
        pending_payment_amount=0.36,
        payment_amount=0.36,
        final_pricing={'ton_amount': 0.36, 'final_price': 1.0},
        payment_method='ton'
    )
    
    print(f"\n1️⃣ Testing wallet address existence for user {user_id}...")
    existing_wallet = await WalletManager.get_user_wallet_address(user_id)
    if existing_wallet:
        print(f"✅ Found existing wallet: {existing_wallet[:10]}...{existing_wallet[-8:]}")
    else:
        print("❌ No existing wallet found")
    
    print(f"\n2️⃣ Simulating user clicking 'Use existing wallet' button...")
    callback_query = MockCallbackQuery(user_id, "use_existing_wallet_payment")
    
    # Test the use_existing_wallet_handler
    try:
        from wallet_manager import use_existing_wallet_handler
        await use_existing_wallet_handler(callback_query, context)
        print("✅ Use existing wallet handler completed successfully")
    except Exception as e:
        print(f"❌ Use existing wallet handler failed: {e}")
    
    print(f"\n3️⃣ Testing payment continuation with existing wallet...")
    try:
        from wallet_manager import continue_payment_with_wallet
        await continue_payment_with_wallet(callback_query, context, existing_wallet)
        print("✅ Payment continuation completed successfully")
    except Exception as e:
        print(f"❌ Payment continuation failed: {e}")
    
    print(f"\n4️⃣ Testing payment data after continuation...")
    data = await context.get_data()
    payment_memo = data.get('payment_memo')
    user_wallet = data.get('user_wallet_address')
    
    if payment_memo:
        print(f"✅ Payment memo generated: {payment_memo}")
    else:
        print("❌ No payment memo found")
    
    if user_wallet:
        print(f"✅ User wallet address stored: {user_wallet[:10]}...{user_wallet[-8:]}")
    else:
        print("❌ No user wallet address in state")
    
    print(f"\n5️⃣ Testing wallet retrieval after the flow...")
    final_wallet = await WalletManager.get_user_wallet_address(user_id)
    if final_wallet:
        print(f"✅ Final wallet check: {final_wallet[:10]}...{final_wallet[-8:]}")
    else:
        print("❌ Wallet not found after flow")
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS:")
    print("=" * 60)
    
    if existing_wallet and final_wallet:
        print("✅ Wallet is being saved correctly")
        print("💡 The issue might be in the user interface flow")
        print("   User may need to select 'Use existing wallet' option")
        print("   Or the bot might not be showing the wallet options properly")
    else:
        print("❌ Wallet saving is not working properly")
        print("💡 Need to debug the wallet storage mechanism")
    
    print(f"\n📊 Final State Data:")
    final_data = await context.get_data()
    for key, value in final_data.items():
        if 'wallet' in key.lower() or 'payment' in key.lower():
            print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_user_payment_flow())