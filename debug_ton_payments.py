#!/usr/bin/env python3
"""
TON Payment Debug Tool
Real-time monitoring and debugging for TON payment verification
"""

import asyncio
import logging
import requests
import time
from datetime import datetime
from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TONPaymentDebugger:
    """Debug tool for TON payment monitoring"""
    
    def __init__(self):
        self.monitor = EnhancedTONPaymentMonitor()
        self.bot_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"  # Default bot wallet
        
    def get_current_time(self):
        """Get formatted current time"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    async def check_recent_transactions(self, limit=20):
        """Check recent transactions on bot wallet"""
        print(f"\n🔍 [{self.get_current_time()}] Checking recent transactions...")
        print(f"Bot wallet: {self.bot_wallet}")
        print("-" * 80)
        
        try:
            # Try TON Center API
            data = await self.monitor.get_transactions_toncenter(self.bot_wallet, limit)
            
            if not data:
                # Try TON API as fallback
                data = await self.monitor.get_transactions_tonapi(self.bot_wallet, limit)
            
            if not data:
                print("❌ No transaction data available from any API")
                return
            
            transactions = data.get('result', []) or data.get('transactions', [])
            
            if not transactions:
                print("📭 No recent transactions found")
                return
            
            print(f"📋 Found {len(transactions)} recent transactions:")
            print()
            
            for i, tx in enumerate(transactions[:10]):  # Show last 10
                if tx.get('in_msg'):
                    in_msg = tx['in_msg']
                    
                    # Extract details
                    sender = self.monitor.extract_sender_from_transaction(tx)
                    amount = self.monitor.extract_amount_from_transaction(tx)
                    memo = self.monitor.extract_memo_from_transaction(tx)
                    
                    # Get transaction time
                    tx_time = tx.get('utime', 0)
                    tx_datetime = datetime.fromtimestamp(tx_time) if tx_time else "Unknown"
                    
                    print(f"Transaction #{i+1}:")
                    print(f"  ⏰ Time: {tx_datetime}")
                    print(f"  👤 From: {sender[:20]}...{sender[-10:] if sender and len(sender) > 30 else sender}")
                    print(f"  💰 Amount: {amount} TON")
                    print(f"  📝 Memo: '{memo}'" if memo else "  📝 Memo: (none)")
                    print(f"  🔗 LT: {tx.get('lt', 'N/A')}")
                    print()
            
        except Exception as e:
            print(f"❌ Error checking transactions: {e}")
    
    async def monitor_for_specific_payment(self, expected_memo, expected_amount, user_wallet, timeout_minutes=20):
        """Monitor for a specific payment in real-time"""
        print(f"\n🎯 [{self.get_current_time()}] Starting payment monitoring...")
        print(f"Expected memo: {expected_memo}")
        print(f"Expected amount: {expected_amount} TON")
        print(f"Expected from wallet: {user_wallet}")
        print(f"Timeout: {timeout_minutes} minutes")
        print("-" * 80)
        
        user_wallet_formats = self.monitor.convert_address_formats(user_wallet)
        print(f"Checking wallet formats: {user_wallet_formats}")
        print()
        
        start_time = time.time()
        end_time = start_time + (timeout_minutes * 60)
        check_count = 0
        
        while time.time() < end_time:
            check_count += 1
            remaining_time = int((end_time - time.time()) / 60)
            
            print(f"🔄 Check #{check_count} - {remaining_time} minutes remaining...")
            
            try:
                # Get recent transactions
                data = await self.monitor.get_transactions_toncenter(self.bot_wallet, 50)
                
                if not data:
                    data = await self.monitor.get_transactions_tonapi(self.bot_wallet, 50)
                
                if data:
                    transactions = data.get('result', []) or data.get('transactions', [])
                    
                    for tx in transactions:
                        if not tx.get('in_msg'):
                            continue
                        
                        # Extract transaction details
                        sender = self.monitor.extract_sender_from_transaction(tx)
                        amount = self.monitor.extract_amount_from_transaction(tx)
                        memo = self.monitor.extract_memo_from_transaction(tx)
                        
                        # Check if this matches our expected payment
                        if memo == expected_memo:
                            print(f"🎯 Found matching memo: {memo}")
                            print(f"   From: {sender}")
                            print(f"   Amount: {amount} TON")
                            
                            # Check sender
                            sender_matches = sender in user_wallet_formats
                            print(f"   Sender match: {'✅' if sender_matches else '❌'}")
                            
                            # Check amount
                            amount_matches = abs(amount - expected_amount) <= 0.1 if amount else False
                            print(f"   Amount match: {'✅' if amount_matches else '❌'}")
                            
                            if sender_matches and amount_matches:
                                print(f"\n🎉 PAYMENT VERIFIED!")
                                print(f"   Memo: {memo}")
                                print(f"   Amount: {amount} TON")
                                print(f"   From: {sender}")
                                return True
                            else:
                                print(f"   ⚠️ Partial match - payment criteria not fully met")
                        
                else:
                    print("   ❌ Failed to get transaction data")
                
                # Wait before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"   ❌ Error during check: {e}")
                await asyncio.sleep(30)
        
        print(f"\n⏰ Monitoring timeout reached after {timeout_minutes} minutes")
        return False
    
    async def debug_current_state(self):
        """Debug current bot state and connections"""
        print(f"\n🔧 [{self.get_current_time()}] TON Payment Debug Status")
        print("=" * 80)
        
        # Test API endpoints
        print("🌐 Testing API endpoints...")
        
        # Test TON Center
        try:
            response = requests.get(f"https://toncenter.com/api/v2/getTransactions?address={self.bot_wallet}&limit=1", timeout=10)
            if response.status_code == 200:
                print("   ✅ TON Center API: Working")
            else:
                print(f"   ❌ TON Center API: Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ TON Center API: Exception - {e}")
        
        # Test TON API
        try:
            response = requests.get(f"https://tonapi.io/v2/blockchain/accounts/{self.bot_wallet}/transactions?limit=1", timeout=10)
            if response.status_code == 200:
                print("   ✅ TON API: Working")
            else:
                print(f"   ❌ TON API: Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ TON API: Exception - {e}")
        
        print()
        
        # Check recent activity
        await self.check_recent_transactions(10)

async def main():
    """Main debug interface"""
    debugger = TONPaymentDebugger()
    
    print("🔧 TON Payment Debug Tool")
    print("=" * 40)
    print("1. Check recent transactions")
    print("2. Monitor for specific payment")
    print("3. Debug current state")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                await debugger.check_recent_transactions()
            
            elif choice == "2":
                memo = input("Enter expected memo: ").strip()
                amount = float(input("Enter expected amount (TON): ").strip())
                wallet = input("Enter user wallet address: ").strip()
                timeout = int(input("Enter timeout (minutes, default 20): ").strip() or "20")
                
                await debugger.monitor_for_specific_payment(memo, amount, wallet, timeout)
            
            elif choice == "3":
                await debugger.debug_current_state()
            
            elif choice == "4":
                print("Exiting debug tool...")
                break
            
            else:
                print("Invalid choice. Please select 1-4.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())