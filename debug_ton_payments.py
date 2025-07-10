#!/usr/bin/env python3
"""
Debug TON Payments Tool
Real-time debugging and monitoring for TON payment issues
"""

import asyncio
import logging
import time
from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TONPaymentDebugger:
    """Debug TON payment monitoring system"""
    
    def __init__(self):
        self.monitor = EnhancedTONPaymentMonitor()
        self.bot_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    
    async def debug_payment_flow(self, memo=None, amount=None, user_wallet=None):
        """Debug complete payment flow"""
        
        print("🔧 TON Payment Debug Tool")
        print("=" * 80)
        print(f"Bot wallet: {self.bot_wallet}")
        print(f"Debug time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Step 1: Check API connectivity
        print("\n🔍 Step 1: Testing API connectivity...")
        api_status = await self.test_api_connectivity()
        
        if not api_status:
            print("❌ API connectivity failed - cannot proceed")
            return False
        
        # Step 2: Get recent transactions
        print("\n📋 Step 2: Fetching recent transactions...")
        transactions = await self.get_recent_transactions()
        
        if not transactions:
            print("❌ No transactions found")
            return False
        
        # Step 3: Analyze transactions
        print("\n🔍 Step 3: Analyzing transactions...")
        await self.analyze_transactions(transactions, memo, amount, user_wallet)
        
        # Step 4: Test payment verification
        if memo and amount:
            print("\n🧪 Step 4: Testing payment verification...")
            await self.test_payment_verification_logic(memo, amount, user_wallet)
        
        return True
    
    async def test_api_connectivity(self):
        """Test API connectivity"""
        
        # Test TON Center API
        print("   Testing TON Center API...")
        try:
            data = await self.monitor.get_transactions_toncenter(self.bot_wallet, 5)
            if data:
                print(f"   ✅ TON Center API: Working ({len(data.get('result', []))} transactions)")
                ton_center_ok = True
            else:
                print("   ❌ TON Center API: Failed")
                ton_center_ok = False
        except Exception as e:
            print(f"   ❌ TON Center API: Exception - {e}")
            ton_center_ok = False
        
        # Test TON API
        print("   Testing TON API...")
        try:
            data = await self.monitor.get_transactions_tonapi(self.bot_wallet, 5)
            if data:
                print(f"   ✅ TON API: Working ({len(data.get('transactions', []))} transactions)")
                ton_api_ok = True
            else:
                print("   ❌ TON API: Failed")
                ton_api_ok = False
        except Exception as e:
            print(f"   ❌ TON API: Exception - {e}")
            ton_api_ok = False
        
        return ton_center_ok or ton_api_ok
    
    async def get_recent_transactions(self):
        """Get recent transactions for analysis"""
        
        try:
            data = await self.monitor.get_transactions_toncenter(self.bot_wallet, 20)
            if data:
                transactions = data.get('result', [])
                print(f"   ✅ Found {len(transactions)} recent transactions")
                return transactions
            else:
                print("   ❌ No transaction data")
                return []
        except Exception as e:
            print(f"   ❌ Error getting transactions: {e}")
            return []
    
    async def analyze_transactions(self, transactions, target_memo=None, target_amount=None, target_wallet=None):
        """Analyze transactions for payment patterns"""
        
        print(f"   Analyzing {len(transactions)} transactions...")
        
        # Statistics
        total_incoming = 0
        total_with_memo = 0
        total_amount_match = 0
        total_wallet_match = 0
        recent_payments = []
        
        for i, tx in enumerate(transactions):
            if not tx.get('in_msg'):
                continue
            
            total_incoming += 1
            
            # Extract transaction details
            memo = self.monitor.extract_memo_from_transaction(tx)
            sender = self.monitor.extract_sender_from_transaction(tx)
            amount = self.monitor.extract_amount_from_transaction(tx)
            
            if memo:
                total_with_memo += 1
            
            # Check if this is a 0.36 TON payment (typical test amount)
            if amount and amount == 0.36:
                recent_payments.append({
                    'memo': memo,
                    'sender': sender,
                    'amount': amount,
                    'index': i
                })
            
            # Check specific targets
            if target_memo and memo == target_memo:
                print(f"   🎯 Found target memo '{target_memo}' in transaction {i}")
                print(f"      Sender: {sender}")
                print(f"      Amount: {amount} TON")
                
                if target_amount and amount and abs(amount - target_amount) <= 0.1:
                    total_amount_match += 1
                    print(f"      ✅ Amount matches target: {target_amount} TON")
                
                if target_wallet:
                    wallet_formats = self.monitor.convert_address_formats(target_wallet)
                    if sender in wallet_formats:
                        total_wallet_match += 1
                        print(f"      ✅ Wallet matches target: {target_wallet}")
                    else:
                        print(f"      ❌ Wallet mismatch: expected {wallet_formats}, got {sender}")
        
        # Print statistics
        print(f"\n   📊 Transaction Analysis:")
        print(f"      Total transactions: {len(transactions)}")
        print(f"      Incoming transactions: {total_incoming}")
        print(f"      Transactions with memo: {total_with_memo}")
        print(f"      Recent 0.36 TON payments: {len(recent_payments)}")
        
        if target_memo:
            print(f"      Target memo matches: {1 if target_memo in [p['memo'] for p in recent_payments] else 0}")
        if target_amount:
            print(f"      Target amount matches: {total_amount_match}")
        if target_wallet:
            print(f"      Target wallet matches: {total_wallet_match}")
        
        # Show recent payments
        if recent_payments:
            print(f"\n   💳 Recent 0.36 TON payments:")
            for payment in recent_payments[:5]:
                print(f"      {payment['memo']}: {payment['amount']} TON from {payment['sender']}")
    
    async def test_payment_verification_logic(self, memo, amount, user_wallet):
        """Test payment verification logic"""
        
        print(f"   Testing verification for:")
        print(f"      Memo: {memo}")
        print(f"      Amount: {amount} TON")
        print(f"      User wallet: {user_wallet}")
        
        # Get transactions
        data = await self.monitor.get_transactions_toncenter(self.bot_wallet, 50)
        
        if not data:
            print("   ❌ No transaction data for verification test")
            return False
        
        transactions = data.get('result', [])
        user_wallet_formats = self.monitor.convert_address_formats(user_wallet) if user_wallet else []
        
        print(f"   User wallet formats: {user_wallet_formats}")
        
        # Test verification logic
        found_payment = False
        for tx in transactions:
            if not tx.get('in_msg'):
                continue
            
            tx_memo = self.monitor.extract_memo_from_transaction(tx)
            if not tx_memo or tx_memo != memo:
                continue
            
            tx_amount = self.monitor.extract_amount_from_transaction(tx)
            if not tx_amount:
                continue
            
            if abs(tx_amount - amount) <= 0.1:
                sender = self.monitor.extract_sender_from_transaction(tx)
                found_payment = True
                
                print(f"   🎯 Payment found:")
                print(f"      Memo: {tx_memo}")
                print(f"      Amount: {tx_amount} TON")
                print(f"      Sender: {sender}")
                
                # Test flexible verification
                sender_matches = sender in user_wallet_formats if user_wallet_formats else False
                
                print(f"   📋 Verification results:")
                print(f"      Memo match: ✅")
                print(f"      Amount match: ✅")
                print(f"      Sender match: {'✅' if sender_matches else '❌'}")
                
                if sender_matches:
                    print(f"   🎉 Payment would be verified with sender validation")
                else:
                    print(f"   ⚠️ Payment would be verified without sender validation (flexible mode)")
                
                print(f"   ✅ OVERALL: Payment would be CONFIRMED")
                return True
        
        if not found_payment:
            print(f"   ❌ No matching payment found")
            return False

async def main():
    """Main debug function"""
    
    debugger = TONPaymentDebugger()
    
    # Test with recent payment data
    print("🚀 Starting TON Payment Debug Session")
    
    # Option 1: General debug
    await debugger.debug_payment_flow()
    
    print("\n" + "=" * 80)
    print("🔍 Debug session complete")
    print("=" * 80)
    
    # Option 2: Specific payment debug (uncomment to test specific payments)
    # await debugger.debug_payment_flow(
    #     memo="LU0337",
    #     amount=0.36,
    #     user_wallet="UQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tpjk"
    # )

if __name__ == "__main__":
    asyncio.run(main())