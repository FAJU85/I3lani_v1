#!/usr/bin/env python3
"""
Test Live TON Payment Monitoring
"""

import asyncio
import logging
import time
from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_live_monitoring():
    """Test the live monitoring system"""
    
    # Test parameters
    user_id = 123456789
    memo = "TEST1234"
    amount_ton = 0.36
    user_wallet = "UQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tpjk"
    bot_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    expiration_time = time.time() + 300  # 5 minutes test
    
    print("🔧 Testing Live TON Payment Monitoring")
    print("=" * 60)
    print(f"User ID: {user_id}")
    print(f"Memo: {memo}")
    print(f"Amount: {amount_ton} TON")
    print(f"User Wallet: {user_wallet}")
    print(f"Bot Wallet: {bot_wallet}")
    print(f"Test Duration: 5 minutes")
    print("=" * 60)
    
    # Create monitor instance
    monitor = EnhancedTONPaymentMonitor()
    
    # Test basic API calls first
    print("\n🔍 Testing API connectivity...")
    
    # Test TON Center API
    try:
        data = await monitor.get_transactions_toncenter(bot_wallet, 10)
        if data:
            print(f"✅ TON Center API: Working ({len(data.get('result', []))} transactions)")
        else:
            print("❌ TON Center API: Failed")
    except Exception as e:
        print(f"❌ TON Center API: Exception - {e}")
    
    # Test TON API
    try:
        data = await monitor.get_transactions_tonapi(bot_wallet, 10)
        if data:
            print(f"✅ TON API: Working ({len(data.get('transactions', []))} transactions)")
        else:
            print("❌ TON API: Failed")
    except Exception as e:
        print(f"❌ TON API: Exception - {e}")
    
    print("\n🚀 Starting monitoring simulation...")
    
    # Create a mock FSMContext for testing
    class MockState:
        def __init__(self):
            self.data = {}
        
        async def get_data(self):
            return self.data
        
        async def update_data(self, **kwargs):
            self.data.update(kwargs)
    
    state = MockState()
    
    # Monitor for 5 minutes (for testing)
    check_interval = 30  # Check every 30 seconds
    user_wallet_formats = monitor.convert_address_formats(user_wallet)
    
    print(f"User wallet formats: {user_wallet_formats}")
    
    check_number = 0
    while time.time() < expiration_time:
        check_number += 1
        remaining_minutes = int((expiration_time - time.time()) / 60)
        
        print(f"\n📡 Payment check #{check_number} - {remaining_minutes} minutes remaining")
        
        try:
            # Try TON Center API first
            print("   Attempting TON Center API call...")
            transactions_data = await monitor.get_transactions_toncenter(bot_wallet)
            
            if not transactions_data:
                # Fallback to TON API
                print("   TON Center failed, trying TON API...")
                transactions_data = await monitor.get_transactions_tonapi(bot_wallet)
            
            if not transactions_data:
                print("   ❌ Failed to get transactions from all APIs")
                await asyncio.sleep(check_interval)
                continue
            
            print("   ✅ Got transaction data from API")
            
            # Process transactions
            transactions = transactions_data.get('result', []) or transactions_data.get('transactions', [])
            
            if not transactions:
                print("   📭 No transactions found")
                await asyncio.sleep(check_interval)
                continue
            
            print(f"   📋 Found {len(transactions)} transactions to check")
            
            # Check each transaction
            for i, tx in enumerate(transactions[:5]):  # Check first 5 transactions
                # Skip if not an incoming transaction
                if not tx.get('in_msg'):
                    print(f"   Transaction {i+1}: No in_msg, skipping")
                    continue
                
                # Extract memo
                tx_memo = monitor.extract_memo_from_transaction(tx)
                print(f"   Transaction {i+1}: Memo = '{tx_memo}'")
                
                # Extract sender
                sender = monitor.extract_sender_from_transaction(tx)
                print(f"   Transaction {i+1}: Sender = '{sender}'")
                
                # Extract amount
                tx_amount = monitor.extract_amount_from_transaction(tx)
                print(f"   Transaction {i+1}: Amount = {tx_amount} TON")
                
                # Check if this matches our expected payment
                if tx_memo == memo:
                    print(f"   🎯 Found matching memo: {memo}")
                    
                    # Check sender
                    sender_matches = sender in user_wallet_formats
                    print(f"   Sender match: {'✅' if sender_matches else '❌'}")
                    
                    # Check amount
                    amount_matches = abs(tx_amount - amount_ton) <= 0.1 if tx_amount else False
                    print(f"   Amount match: {'✅' if amount_matches else '❌'}")
                    
                    if sender_matches and amount_matches:
                        print(f"\n🎉 PAYMENT VERIFIED!")
                        print(f"   Memo: {memo}")
                        print(f"   Amount: {tx_amount} TON")
                        print(f"   From: {sender}")
                        return True
                    else:
                        print(f"   ⚠️ Partial match - payment criteria not fully met")
            
            print(f"   No matching payments found in this batch")
            
            # Wait before next check
            await asyncio.sleep(check_interval)
            
        except Exception as e:
            print(f"   ❌ Error during check: {e}")
            await asyncio.sleep(check_interval)
    
    print(f"\n⏰ Monitoring test completed after 5 minutes")
    return False

if __name__ == "__main__":
    asyncio.run(test_live_monitoring())