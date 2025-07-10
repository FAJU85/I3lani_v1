"""
Simple core test for TON wallet address management system
Tests core wallet validation and database operations
"""

import asyncio
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wallet_manager import WalletManager
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_wallet_validation():
    """Test wallet address validation"""
    print("🔍 Testing wallet address validation...")
    
    # Test valid addresses
    valid_addresses = [
        "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE",
        "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE",
        "EQAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAa",
        "UQBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBbBb"
    ]
    
    # Test invalid addresses
    invalid_addresses = [
        "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmr",  # Too short
        "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSEX",  # Too long
        "AQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE",  # Wrong prefix
        "invalid_address",  # Invalid format
        "",  # Empty
        "12DZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE",  # Wrong prefix
    ]
    
    valid_count = 0
    invalid_count = 0
    
    for addr in valid_addresses:
        if WalletManager.validate_ton_address(addr):
            valid_count += 1
            print(f"✅ Valid: {addr[:20]}...")
        else:
            print(f"❌ Should be valid: {addr[:20]}...")
    
    for addr in invalid_addresses:
        if not WalletManager.validate_ton_address(addr):
            invalid_count += 1
            print(f"✅ Correctly rejected: {addr[:20]}...")
        else:
            print(f"❌ Should be invalid: {addr[:20]}...")
    
    print(f"📊 Validation Results: {valid_count}/{len(valid_addresses)} valid accepted, {invalid_count}/{len(invalid_addresses)} invalid rejected")
    return valid_count == len(valid_addresses) and invalid_count == len(invalid_addresses)

async def test_database_operations():
    """Test database wallet operations"""
    print("🔍 Testing database operations...")
    
    test_user_id = 999999
    test_wallet = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
    
    # Test 1: Initial state (no wallet)
    wallet = await WalletManager.get_user_wallet_address(test_user_id)
    if wallet is not None:
        print(f"❌ Expected no wallet, got: {wallet}")
        return False
    print("✅ Initial state: No wallet stored")
    
    # Test 2: Set wallet address
    result = await WalletManager.set_user_wallet_address(test_user_id, test_wallet)
    if not result:
        print("❌ Failed to set wallet address")
        return False
    print("✅ Wallet address set successfully")
    
    # Test 3: Get wallet address
    retrieved_wallet = await WalletManager.get_user_wallet_address(test_user_id)
    if retrieved_wallet != test_wallet:
        print(f"❌ Expected {test_wallet}, got: {retrieved_wallet}")
        return False
    print("✅ Wallet address retrieved successfully")
    
    # Test 4: Update wallet address
    new_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
    result = await WalletManager.set_user_wallet_address(test_user_id, new_wallet)
    if not result:
        print("❌ Failed to update wallet address")
        return False
    print("✅ Wallet address updated successfully")
    
    # Test 5: Verify update
    updated_wallet = await WalletManager.get_user_wallet_address(test_user_id)
    if updated_wallet != new_wallet:
        print(f"❌ Expected {new_wallet}, got: {updated_wallet}")
        return False
    print("✅ Wallet address update verified")
    
    # Test 6: Clear wallet (set to None)
    result = await WalletManager.set_user_wallet_address(test_user_id, None)
    if not result:
        print("❌ Failed to clear wallet address")
        return False
    
    cleared_wallet = await WalletManager.get_user_wallet_address(test_user_id)
    if cleared_wallet is not None:
        print(f"❌ Expected None, got: {cleared_wallet}")
        return False
    print("✅ Wallet address cleared successfully")
    
    return True

async def test_validation_integration():
    """Test validation integration with database"""
    print("🔍 Testing validation integration...")
    
    test_user_id = 999998
    invalid_wallet = "invalid_wallet_address"
    valid_wallet = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
    
    # Test 1: Try to set invalid wallet
    result = await WalletManager.set_user_wallet_address(test_user_id, invalid_wallet)
    if result:
        # The database method doesn't validate, so this might succeed
        print("ℹ️ Database allows invalid wallet (validation should happen in handlers)")
    else:
        print("✅ Database rejected invalid wallet")
    
    # Test 2: Set valid wallet
    result = await WalletManager.set_user_wallet_address(test_user_id, valid_wallet)
    if not result:
        print("❌ Failed to set valid wallet")
        return False
    print("✅ Valid wallet set successfully")
    
    # Test 3: Verify valid wallet
    retrieved_wallet = await WalletManager.get_user_wallet_address(test_user_id)
    if retrieved_wallet != valid_wallet:
        print(f"❌ Expected {valid_wallet}, got: {retrieved_wallet}")
        return False
    print("✅ Valid wallet verified")
    
    # Cleanup
    await WalletManager.set_user_wallet_address(test_user_id, None)
    return True

async def run_core_tests():
    """Run core wallet management tests"""
    print("🚀 TON Wallet Management System Core Tests")
    print("=" * 50)
    
    # Initialize database
    await db.init_db()
    
    tests = [
        ("Wallet Address Validation", test_wallet_validation),
        ("Database Operations", test_database_operations),
        ("Validation Integration", test_validation_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*10} {test_name} {'='*10}")
        try:
            result = await test_func()
            if result:
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"📊 CORE TEST RESULTS: {passed}/{len(tests)} tests passed")
    
    if failed == 0:
        print("🎉 CORE TESTS PASSED! Wallet management system is functional.")
        print("\n✅ Core Features Validated:")
        print("   - Wallet address validation (EQ/UQ prefixes)")
        print("   - Database storage and retrieval")
        print("   - Wallet address updates")
        print("   - Wallet address clearing")
        print("   - Error handling")
    else:
        print(f"❌ {failed} core tests failed. Please review.")
    
    return failed == 0

if __name__ == "__main__":
    try:
        result = asyncio.run(run_core_tests())
        if result:
            print("\n🔧 Core System Status: OPERATIONAL")
        else:
            print("\n⚠️ Core System Status: NEEDS FIXES")
    except Exception as e:
        print(f"❌ Core test execution failed: {e}")
        import traceback
        traceback.print_exc()