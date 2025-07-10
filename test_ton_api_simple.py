#!/usr/bin/env python3
"""
Simple TON API Test - Check if basic API calls work
"""

import requests
import json

def test_simple_api():
    """Test basic API calls"""
    bot_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    
    print("Testing TON Center API...")
    try:
        url = f"https://toncenter.com/api/v2/getTransactions?address={bot_wallet}&limit=5"
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response OK: {data.get('ok')}")
            print(f"Result type: {type(data.get('result'))}")
            print(f"Result length: {len(data.get('result', []))}")
            
            if data.get('result'):
                tx = data['result'][0]
                print(f"First transaction keys: {list(tx.keys())}")
        else:
            print(f"Error response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\nTesting TON API...")
    try:
        url = f"https://tonapi.io/v2/blockchain/accounts/{bot_wallet}/transactions?limit=5"
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            print(f"Response keys: {list(data.keys())}")
            
            if data.get('transactions'):
                print(f"Transactions found: {len(data['transactions'])}")
                tx = data['transactions'][0]
                print(f"First transaction keys: {list(tx.keys())}")
        else:
            print(f"Error response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_simple_api()