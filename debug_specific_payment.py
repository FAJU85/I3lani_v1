#!/usr/bin/env python3
"""
Debug Specific Payment PY6480
Investigate why this payment wasn't confirmed
"""

import asyncio
import logging
from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_payment_py6480():
    """Debug specific payment PY6480"""
    
    print("🔍 Debugging Payment PY6480")
    print("=" * 50)
    
    monitor = EnhancedTONPaymentMonitor()
    bot_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    
    # Get recent transactions
    data = await monitor.get_transactions_toncenter(bot_wallet, 50)
    
    if not data:
        print("❌ No transaction data")
        return
    
    transactions = data.get('result', [])
    print(f"📋 Analyzing {len(transactions)} transactions for PY6480...")
    
    # Find PY6480 payment
    target_memo = "PY6480"
    found_payment = None
    
    for i, tx in enumerate(transactions):
        if not tx.get('in_msg'):
            continue
        
        memo = monitor.extract_memo_from_transaction(tx)
        if memo == target_memo:
            found_payment = tx
            sender = monitor.extract_sender_from_transaction(tx)
            amount = monitor.extract_amount_from_transaction(tx)
            
            print(f"\n🎯 Found PY6480 payment:")
            print(f"   Transaction index: {i}")
            print(f"   Memo: {memo}")
            print(f"   Sender: {sender}")
            print(f"   Amount: {amount} TON")
            print(f"   Expected amount: 0.36 TON")
            print(f"   Amount match: {'✅' if abs(amount - 0.36) <= 0.1 else '❌'}")
            
            # Test flexible verification logic
            if abs(amount - 0.36) <= 0.1:
                print(f"\n✅ Payment PY6480 would be CONFIRMED by flexible verification")
                print(f"   ✓ Memo matches: {memo}")
                print(f"   ✓ Amount matches: {amount} TON")
                print(f"   ✓ Sender: {sender}")
                print(f"\n🎉 CONCLUSION: Payment PY6480 should be automatically confirmed!")
                
                # Check if there might be a timing issue
                print(f"\n⏰ Checking timing issues...")
                print(f"   Transaction timestamp: {tx.get('utime', 'unknown')}")
                
                return True
            else:
                print(f"❌ Amount mismatch: expected 0.36, got {amount}")
                return False
    
    if not found_payment:
        print(f"❌ Payment with memo {target_memo} not found")
        return False

if __name__ == "__main__":
    asyncio.run(debug_payment_py6480())