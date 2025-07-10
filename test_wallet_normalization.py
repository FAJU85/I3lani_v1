#!/usr/bin/env python3
"""
Test script to verify wallet address normalization fixes the payment confirmation issue
"""

# Import the normalization function from handlers
from handlers import normalize_wallet_address

def test_wallet_normalization():
    """Test wallet address normalization function"""
    print("Testing wallet address normalization...")
    
    # Test case 1: EQ prefix to UQ conversion
    eq_address = "EQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tsUh"
    uq_address = "UQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tpjk"
    
    normalized_eq = normalize_wallet_address(eq_address)
    normalized_uq = normalize_wallet_address(uq_address)
    
    print(f"Original EQ address: {eq_address}")
    print(f"Normalized EQ address: {normalized_eq}")
    print(f"Original UQ address: {uq_address}")
    print(f"Normalized UQ address: {normalized_uq}")
    
    # Check if they match after normalization
    if normalized_eq == normalized_uq:
        print("✅ SUCCESS: Wallet addresses match after normalization!")
        print(f"   Both normalize to: {normalized_eq}")
    else:
        print("❌ FAILURE: Wallet addresses don't match after normalization")
        print(f"   EQ normalized to: {normalized_eq}")
        print(f"   UQ normalized to: {normalized_uq}")
    
    # Test case 2: Already UQ address should remain unchanged
    test_uq = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
    normalized_test = normalize_wallet_address(test_uq)
    
    print(f"\nTesting UQ address unchanged:")
    print(f"Original: {test_uq}")
    print(f"Normalized: {normalized_test}")
    
    if test_uq == normalized_test:
        print("✅ SUCCESS: UQ address remains unchanged")
    else:
        print("❌ FAILURE: UQ address was modified")
    
    # Test case 3: Empty/None address handling
    empty_result = normalize_wallet_address("")
    none_result = normalize_wallet_address(None)
    
    print(f"\nTesting edge cases:")
    print(f"Empty string: '{empty_result}'")
    print(f"None value: '{none_result}'")
    
    return True

if __name__ == "__main__":
    test_wallet_normalization()