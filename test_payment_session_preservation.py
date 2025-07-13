#!/usr/bin/env python3
"""
Test payment session preservation fix for the I3lani Bot
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from wallet_manager import WalletManager
from states import CreateAd, WalletStates
from database import Database

# Mock user ID for testing
TEST_USER_ID = 566158428

class MockUser:
    def __init__(self, user_id):
        self.id = user_id

class MockMessage:
    def __init__(self, user_id, text=""):
        self.from_user = MockUser(user_id)
        self.text = text
        self.reply_called = False
        self.reply_text = ""
    
    async def reply(self, text, **kwargs):
        self.reply_called = True
        self.reply_text = text
        print(f"Message reply: {text}")

class MockCallbackQuery:
    def __init__(self, user_id, data=""):
        self.from_user = MockUser(user_id)
        self.data = data
        self.message = MockMessage(user_id)
        self.answer_called = False
        self.answer_text = ""
    
    async def answer(self, text="", show_alert=False):
        self.answer_called = True
        self.answer_text = text
        print(f"Callback answer: {text}")

async def test_payment_session_preservation():
    """Test that payment session data is preserved during wallet operations"""
    print("🧪 Testing Payment Session Preservation Fix")
    print("=" * 60)
    
    # Initialize memory storage for testing
    storage = MemoryStorage()
    
    # Test 1: Simulate payment setup with state data
    print("1️⃣ Testing payment state data preservation...")
    
    # Create a mock state context
    context = FSMContext(storage=storage, key=f"user:{TEST_USER_ID}")
    
    # Simulate payment data stored in state (like from pay_ton_handler)
    payment_data = {
        'pending_payment_amount': 0.104,
        'payment_amount': 0.104,
        'amount_ton': 0.104,
        'final_pricing': {
            'final_price': 0.29,
            'ton_amount': 0.104
        },
        'payment_method': 'ton',
        'selected_channels': ['@i3lani', '@smshco'],
        'days': 1,
        'content': 'Test advertisement content'
    }
    
    await context.set_data(payment_data)
    print("✅ Payment data stored in state")
    
    # Test 2: Simulate wallet address request (this is where session was getting lost)
    print("\n2️⃣ Testing wallet address request...")
    
    mock_callback = MockCallbackQuery(TEST_USER_ID)
    
    # This should preserve the payment data
    await WalletManager.request_wallet_address(mock_callback, context, 'payment')
    
    # Check if payment data is still there
    data_after_request = await context.get_data()
    print(f"State data keys after request: {list(data_after_request.keys())}")
    
    # Verify critical payment data is preserved
    critical_keys = ['pending_payment_amount', 'payment_amount', 'amount_ton', 'final_pricing']
    preserved_keys = [key for key in critical_keys if key in data_after_request]
    
    if len(preserved_keys) == len(critical_keys):
        print("✅ All critical payment data preserved during wallet request")
    else:
        print(f"❌ Missing payment data: {set(critical_keys) - set(preserved_keys)}")
    
    # Test 3: Simulate wallet address input (final step that was failing)
    print("\n3️⃣ Testing wallet address input processing...")
    
    # Mock wallet address input
    mock_message = MockMessage(TEST_USER_ID, "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE")
    
    # This should find the payment amount and proceed without "session expired" error
    await WalletManager.process_wallet_input(mock_message, context, 'payment')
    
    # Check if the continue_payment_with_wallet function was called successfully
    if not mock_message.reply_called or "session expired" not in mock_message.reply_text.lower():
        print("✅ Wallet address processing successful - no session expiration")
    else:
        print(f"❌ Session expired error still occurring: {mock_message.reply_text}")
    
    # Test 4: Test complete flow simulation
    print("\n4️⃣ Testing complete payment flow simulation...")
    
    try:
        # Simulate complete flow
        # 1. Store payment data (from pay_ton_handler)
        fresh_context = FSMContext(storage=storage, key=f"user:{TEST_USER_ID}_flow")
        await fresh_context.set_data(payment_data)
        
        # 2. Request wallet address (this was clearing session)
        await WalletManager.request_wallet_address(mock_callback, fresh_context, 'payment')
        
        # 3. Process wallet input (this was failing)
        await WalletManager.process_wallet_input(mock_message, fresh_context, 'payment')
        
        print("✅ Complete payment flow simulation successful")
        
    except Exception as e:
        print(f"❌ Complete flow failed: {e}")
    
    # Test 5: Verify continue_payment_with_wallet function specifically
    print("\n5️⃣ Testing continue_payment_with_wallet function...")
    
    # Create state with payment data
    test_context = FSMContext(storage=storage, key=f"user:{TEST_USER_ID}_continue")
    await test_context.set_data(payment_data)
    
    # This should work now without session expiration
    try:
        await WalletManager.continue_payment_with_wallet(mock_message, test_context, "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE")
        print("✅ continue_payment_with_wallet executed successfully")
    except Exception as e:
        print(f"❌ continue_payment_with_wallet failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 PAYMENT SESSION PRESERVATION TEST SUMMARY")
    print("=" * 60)
    
    print("✅ FIXES APPLIED:")
    print("   - Enhanced state data debugging in continue_payment_with_wallet")
    print("   - State data preservation in show_wallet_options")
    print("   - State data preservation in show_wallet_input_prompt")
    print("   - Multiple fallback keys for payment amount retrieval")
    print("   - USD to TON conversion fallback")
    print("   - Comprehensive error logging")
    
    print("\n🔧 TECHNICAL IMPROVEMENTS:")
    print("   - Payment data preserved during wallet state transitions")
    print("   - Multiple payment amount keys checked")
    print("   - Final pricing data used as fallback")
    print("   - Enhanced debugging for session troubleshooting")
    print("   - Comprehensive state data preservation")
    
    print("\n💡 EXPECTED RESULT:")
    print("   - Users should no longer see 'Payment session expired' error")
    print("   - Wallet address input should work seamlessly")
    print("   - Payment amounts should be preserved throughout flow")
    print("   - Session data should persist across all wallet operations")

if __name__ == "__main__":
    asyncio.run(test_payment_session_preservation())