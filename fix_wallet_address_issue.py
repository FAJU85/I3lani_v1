#!/usr/bin/env python3
"""
Fix wallet address normalization issue
"""

import asyncio
import requests
from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor

async def check_wallet_addresses():
    """Check wallet address differences"""
    
    bot_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    expected_user_wallet = "UQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tpjk"
    
    print("🔍 Checking wallet address issue...")
    print(f"Bot wallet: {bot_wallet}")
    print(f"Expected user wallet: {expected_user_wallet}")
    print("-" * 60)
    
    monitor = EnhancedTONPaymentMonitor()
    
    # Get recent transactions
    data = await monitor.get_transactions_toncenter(bot_wallet, 10)
    
    if not data:
        print("❌ No transaction data")
        return
    
    transactions = data.get('result', [])
    
    if not transactions:
        print("❌ No transactions found")
        return
    
    print(f"📋 Found {len(transactions)} transactions")
    print()
    
    # Check each transaction
    for i, tx in enumerate(transactions[:5]):
        if not tx.get('in_msg'):
            continue
        
        memo = monitor.extract_memo_from_transaction(tx)
        sender = monitor.extract_sender_from_transaction(tx)
        amount = monitor.extract_amount_from_transaction(tx)
        
        print(f"Transaction {i+1}:")
        print(f"  Memo: {memo}")
        print(f"  Sender: {sender}")
        print(f"  Amount: {amount} TON")
        
        # Check if sender matches expected (with format conversion)
        user_wallet_formats = monitor.convert_address_formats(expected_user_wallet)
        print(f"  Expected formats: {user_wallet_formats}")
        
        sender_matches = sender in user_wallet_formats
        print(f"  Sender match: {'✅' if sender_matches else '❌'}")
        
        # Check if we need to normalize the sender address
        if sender and sender.startswith('EQ'):
            # Convert to UQ format
            uq_sender = 'UQ' + sender[2:]
            print(f"  UQ format: {uq_sender}")
            
            # Check if UQ format matches
            uq_matches = uq_sender == expected_user_wallet
            print(f"  UQ match: {'✅' if uq_matches else '❌'}")
            
            # Also check if it's the same base58 part
            sender_base = sender[2:]
            expected_base = expected_user_wallet[2:]
            print(f"  Base58 sender: ...{sender_base[-10:]}")
            print(f"  Base58 expected: ...{expected_base[-10:]}")
            print(f"  Base58 match: {'✅' if sender_base == expected_base else '❌'}")
        
        print()
    
    # Test with actual payment memo
    print("🔍 Searching for recent payment memos...")
    for i, tx in enumerate(transactions):
        if not tx.get('in_msg'):
            continue
        
        memo = monitor.extract_memo_from_transaction(tx)
        if memo and len(memo) == 6:  # Our memo format
            sender = monitor.extract_sender_from_transaction(tx)
            amount = monitor.extract_amount_from_transaction(tx)
            
            print(f"Recent payment found:")
            print(f"  Memo: {memo}")
            print(f"  Sender: {sender}")
            print(f"  Amount: {amount} TON")
            
            # Test if monitoring would match this
            if amount == 0.36:
                print(f"  ✅ Amount matches expected 0.36 TON")
                
                # Check sender formats
                user_formats = monitor.convert_address_formats(expected_user_wallet)
                sender_formats = monitor.convert_address_formats(sender)
                
                print(f"  Expected formats: {user_formats}")
                print(f"  Sender formats: {sender_formats}")
                
                # Check if any format matches
                match_found = False
                for uf in user_formats:
                    if uf in sender_formats:
                        match_found = True
                        break
                
                print(f"  Format match: {'✅' if match_found else '❌'}")
                
                if not match_found:
                    print(f"  ⚠️ This payment would NOT be confirmed by current system")
                else:
                    print(f"  ✅ This payment WOULD be confirmed by current system")
            
            break

if __name__ == "__main__":
    asyncio.run(check_wallet_addresses())