#!/usr/bin/env python3
"""
Quick TON API Debug - Check if APIs are working
"""

import asyncio
import requests
import json
from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor

async def test_ton_apis():
    """Test TON API endpoints"""
    bot_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    monitor = EnhancedTONPaymentMonitor()
    
    print("🔍 Testing TON API endpoints...")
    print(f"Bot wallet: {bot_wallet}")
    print("-" * 60)
    
    # Test TON Center API
    print("1. Testing TON Center API...")
    try:
        url = f"https://toncenter.com/api/v2/getTransactions?address={bot_wallet}&limit=10"
        response = requests.get(url, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('ok', False)}")
            if data.get('ok'):
                result = data.get('result', [])
                print(f"   Transactions found: {len(result)}")
                
                # Show first transaction structure
                if result:
                    tx = result[0]
                    print(f"   Sample transaction keys: {list(tx.keys())}")
                    if tx.get('in_msg'):
                        print(f"   in_msg keys: {list(tx['in_msg'].keys())}")
            else:
                print(f"   Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"   HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test TON API
    print("2. Testing TON API...")
    try:
        url = f"https://tonapi.io/v2/blockchain/accounts/{bot_wallet}/transactions?limit=10"
        headers = {'Accept': 'application/json', 'User-Agent': 'I3lani-Bot/1.0'}
        response = requests.get(url, headers=headers, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('transactions', [])
            print(f"   Transactions found: {len(transactions)}")
            
            # Show first transaction structure
            if transactions:
                tx = transactions[0]
                print(f"   Sample transaction keys: {list(tx.keys())}")
                if tx.get('in_msg'):
                    print(f"   in_msg keys: {list(tx['in_msg'].keys())}")
        else:
            print(f"   HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    
    # Test using monitor methods
    print("3. Testing monitor methods...")
    try:
        data1 = await monitor.get_transactions_toncenter(bot_wallet, 10)
        print(f"   TON Center via monitor: {'✅ Working' if data1 else '❌ Failed'}")
        
        data2 = await monitor.get_transactions_tonapi(bot_wallet, 10)
        print(f"   TON API via monitor: {'✅ Working' if data2 else '❌ Failed'}")
        
        # Test memo/amount extraction if we have data
        if data1:
            transactions = data1.get('result', [])
            if transactions:
                tx = transactions[0]
                memo = monitor.extract_memo_from_transaction(tx)
                amount = monitor.extract_amount_from_transaction(tx)
                sender = monitor.extract_sender_from_transaction(tx)
                
                print(f"   Sample extraction:")
                print(f"     Memo: {memo}")
                print(f"     Amount: {amount}")
                print(f"     Sender: {sender}")
        
    except Exception as e:
        print(f"   Exception: {e}")
    
    print()
    print("🔧 Debug complete!")

if __name__ == "__main__":
    asyncio.run(test_ton_apis())