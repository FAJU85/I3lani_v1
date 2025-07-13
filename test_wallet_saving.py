#!/usr/bin/env python3
"""
Test script to verify wallet address saving functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from wallet_manager import WalletManager

async def test_wallet_saving():
    """Test wallet address saving functionality"""
    print("🧪 Testing Wallet Address Saving")
    print("=" * 50)
    
    # Initialize database
    db = Database()
    
    # Test user ID
    test_user_id = 566158428  # Using the user from the logs
    test_wallet = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
    
    # Test 1: Direct database wallet saving
    print("\n1️⃣ Testing direct database wallet saving...")
    try:
        result = await db.set_user_wallet(test_user_id, test_wallet)
        print(f"✅ Direct database save result: {result}")
    except Exception as e:
        print(f"❌ Direct database save failed: {e}")
    
    # Test 2: WalletManager saving
    print("\n2️⃣ Testing WalletManager wallet saving...")
    try:
        result = await WalletManager.set_user_wallet_address(test_user_id, test_wallet)
        print(f"✅ WalletManager save result: {result}")
    except Exception as e:
        print(f"❌ WalletManager save failed: {e}")
    
    # Test 3: Wallet retrieval
    print("\n3️⃣ Testing wallet retrieval...")
    try:
        saved_wallet = await WalletManager.get_user_wallet_address(test_user_id)
        if saved_wallet:
            print(f"✅ Retrieved wallet: {saved_wallet[:10]}...{saved_wallet[-8:]}")
        else:
            print("❌ No wallet found")
    except Exception as e:
        print(f"❌ Wallet retrieval failed: {e}")
    
    # Test 4: Wallet validation
    print("\n4️⃣ Testing wallet validation...")
    if WalletManager.validate_ton_address(test_wallet):
        print("✅ Wallet address validation passed")
    else:
        print("❌ Wallet address validation failed")
    
    # Test 5: Check if user exists
    print("\n5️⃣ Testing user existence...")
    try:
        user = await db.get_user(test_user_id)
        if user:
            print(f"✅ User exists: {user.get('username', 'Unknown')}")
            print(f"   Wallet in user data: {user.get('ton_wallet_address', 'None')}")
        else:
            print("❌ User not found")
    except Exception as e:
        print(f"❌ User check failed: {e}")
    
    print("\n🎯 Wallet Saving Test Summary:")
    print("=" * 50)
    print("If wallet saving is working correctly, you should see:")
    print("- Database save result: True")
    print("- WalletManager save result: True")
    print("- Retrieved wallet showing first 10 and last 8 characters")
    print("- Wallet validation: True")
    print("- User exists with wallet address in database")

if __name__ == "__main__":
    asyncio.run(test_wallet_saving())