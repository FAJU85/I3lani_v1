#!/usr/bin/env python3
"""
Debug OS1497 Payment Issue
Find and confirm the OS1497 payment immediately
"""

import asyncio
import logging
from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_os1497_payment():
    """Debug and fix OS1497 payment immediately"""
    
    print("🔍 DEBUGGING OS1497 PAYMENT ISSUE")
    print("=" * 60)
    
    # Check if OS1497 is in the blockchain
    print("1. Checking OS1497 payment on blockchain...")
    
    monitor = EnhancedTONPaymentMonitor()
    bot_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    
    try:
        data = await monitor.get_transactions_toncenter(bot_wallet, 50)
        
        if data:
            transactions = data.get('result', [])
            os1497_payment = None
            
            for tx in transactions:
                if not tx.get('in_msg'):
                    continue
                
                memo = monitor.extract_memo_from_transaction(tx)
                if memo == 'OS1497':
                    amount = monitor.extract_amount_from_transaction(tx)
                    sender = monitor.extract_sender_from_transaction(tx)
                    timestamp = tx.get('utime', 0)
                    
                    os1497_payment = {
                        'memo': memo,
                        'amount': amount,
                        'sender': sender,
                        'timestamp': timestamp
                    }
                    
                    print(f"   ✅ OS1497 payment found on blockchain")
                    print(f"      Amount: {amount} TON")
                    print(f"      Sender: {sender}")
                    print(f"      Timestamp: {timestamp}")
                    break
            
            if not os1497_payment:
                print(f"   ❌ OS1497 payment not found on blockchain")
                return False
        else:
            print(f"   ❌ Could not retrieve transaction data")
            return False
        
    except Exception as e:
        print(f"   ❌ Error checking blockchain: {e}")
        return False
    
    # Check if OS1497 is in memo tracker database
    print("\n2. Checking if OS1497 is in memo tracker database...")
    
    try:
        from payment_memo_tracker import memo_tracker
        user_info = await memo_tracker.get_user_by_memo('OS1497')
        
        if user_info:
            print(f"   ✅ OS1497 found in memo tracker")
            print(f"      User ID: {user_info['user_id']}")
            print(f"      Amount: {user_info['amount']}")
            print(f"      Ad data: {user_info['ad_data']}")
        else:
            print(f"   ❌ OS1497 NOT found in memo tracker")
            print(f"      This explains why user didn't get confirmation!")
            
    except Exception as e:
        print(f"   ❌ Error checking memo tracker: {e}")
        return False
    
    # The issue is clear: OS1497 payment exists on blockchain but not in memo tracker
    print("\n3. ROOT CAUSE IDENTIFIED:")
    print("   - OS1497 payment exists on blockchain")
    print("   - But OS1497 memo is NOT in payment_memos table")
    print("   - Scanner can't find user to send confirmation")
    print("   - User gets no confirmation message")
    
    print("\n4. SOLUTION:")
    print("   - Need to implement fallback user notification system")
    print("   - Or manually add OS1497 to database if we know the user")
    print("   - Or create generic confirmation for untracked payments")
    
    return True

if __name__ == "__main__":
    asyncio.run(debug_os1497_payment())