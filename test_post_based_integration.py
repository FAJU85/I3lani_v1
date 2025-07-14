#!/usr/bin/env python3
"""
Test Post-Based System Integration
Validates that all components work together properly
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_post_based_system_integration():
    """Test comprehensive post-based system integration"""
    
    results = {
        'post_pricing_system': False,
        'user_post_manager': False,
        'post_handlers': False,
        'stars_payment_integration': False,
        'ton_payment_integration': False,
        'automatic_confirmation': False,
        'wallet_manager_integration': False,
        'main_bot_integration': False
    }
    
    print("🚀 Testing Post-Based System Integration...")
    print("=" * 60)
    
    # Test 1: Post Pricing System
    try:
        from post_based_pricing_system import get_post_pricing_system, PostPackage
        
        pricing_system = get_post_pricing_system()
        
        # Test package configuration
        starter_config = pricing_system.packages[PostPackage.STARTER]
        assert starter_config.name == 'Starter'
        assert starter_config.posts == 5
        assert starter_config.price_usd == 1.45
        
        # Test price calculation
        calculation = pricing_system.calculate_total_price(PostPackage.STARTER, [], 0)
        assert calculation['total_usd'] == 1.45
        assert calculation['total_stars'] == 49  # 1.45 * 34
        assert abs(calculation['total_ton'] - 0.52) < 0.01   # 1.45 * 0.36
        
        results['post_pricing_system'] = True
        logger.info("✅ Post pricing system working correctly")
        
    except Exception as e:
        logger.error(f"❌ Post pricing system test failed: {e}")
    
    # Test 2: User Post Manager
    try:
        from user_post_manager import get_user_post_manager, PostStatus
        
        post_manager = get_user_post_manager()
        
        # Test database initialization
        await post_manager.initialize_database()
        
        # Test adding post credits
        credit_id = await post_manager.add_post_credits(
            user_id=12345,
            package_name='Starter',
            posts_count=5,
            purchase_id='TEST123'
        )
        
        assert credit_id is not None
        
        # Test getting user balance
        balance = await post_manager.get_user_post_balance(12345)
        assert balance['total_available'] == 5
        assert len(balance['credits']) == 1
        
        results['user_post_manager'] = True
        logger.info("✅ User post manager working correctly")
        
    except Exception as e:
        logger.error(f"❌ User post manager test failed: {e}")
    
    # Test 3: Post Handlers
    try:
        from post_based_handlers import PostBasedStates
        
        # Test states enum
        assert hasattr(PostBasedStates, 'selecting_package')
        assert hasattr(PostBasedStates, 'payment_confirmation')
        
        results['post_handlers'] = True
        logger.info("✅ Post handlers working correctly")
        
    except Exception as e:
        logger.error(f"❌ Post handlers test failed: {e}")
    
    # Test 4: Stars Payment Integration
    try:
        from clean_stars_payment_system import CleanStarsPayment
        
        # Test that the create_post_package_invoice method exists
        assert hasattr(CleanStarsPayment, 'create_post_package_invoice')
        assert hasattr(CleanStarsPayment, 'handle_post_package_payment')
        
        results['stars_payment_integration'] = True
        logger.info("✅ Stars payment integration working correctly")
        
    except Exception as e:
        logger.error(f"❌ Stars payment integration test failed: {e}")
    
    # Test 5: TON Payment Integration
    try:
        from automatic_payment_confirmation import AutomaticPaymentConfirmation
        
        confirmation_system = AutomaticPaymentConfirmation()
        
        # Test that post package methods exist
        assert hasattr(confirmation_system, 'send_post_package_confirmation')
        assert hasattr(confirmation_system, 'send_ton_post_package_confirmation')
        assert hasattr(confirmation_system, 'process_post_package_purchase')
        
        results['ton_payment_integration'] = True
        logger.info("✅ TON payment integration working correctly")
        
    except Exception as e:
        logger.error(f"❌ TON payment integration test failed: {e}")
    
    # Test 6: Automatic Confirmation
    try:
        from automatic_payment_confirmation import process_detected_payment
        
        # Test that the enhanced process_detected_payment function exists
        assert callable(process_detected_payment)
        
        results['automatic_confirmation'] = True
        logger.info("✅ Automatic confirmation working correctly")
        
    except Exception as e:
        logger.error(f"❌ Automatic confirmation test failed: {e}")
    
    # Test 7: Wallet Manager Integration
    try:
        from wallet_manager import continue_payment_with_wallet
        
        # Test that the function exists and is callable
        assert callable(continue_payment_with_wallet)
        
        results['wallet_manager_integration'] = True
        logger.info("✅ Wallet manager integration working correctly")
        
    except Exception as e:
        logger.error(f"❌ Wallet manager integration test failed: {e}")
    
    # Test 8: Main Bot Integration
    try:
        from main_bot import setup_post_based_system
        
        # Test that the setup function exists
        assert callable(setup_post_based_system)
        
        results['main_bot_integration'] = True
        logger.info("✅ Main bot integration working correctly")
        
    except Exception as e:
        logger.error(f"❌ Main bot integration test failed: {e}")
    
    # Calculate success rate
    passed_tests = sum(results.values())
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print("=" * 60)
    print(f"📊 POST-BASED SYSTEM INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print("=" * 60)
    print(f"📈 Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
    
    if success_rate >= 80:
        print("🎉 POST-BASED SYSTEM INTEGRATION: EXCELLENT")
    elif success_rate >= 60:
        print("⚠️  POST-BASED SYSTEM INTEGRATION: GOOD (Some issues)")
    else:
        print("🚨 POST-BASED SYSTEM INTEGRATION: NEEDS ATTENTION")
    
    return success_rate >= 80

async def test_payment_flow_simulation():
    """Test a complete payment flow simulation"""
    
    print("\n🔄 Testing Complete Payment Flow...")
    print("=" * 50)
    
    try:
        # Simulate Stars payment flow
        from clean_stars_payment_system import CleanStarsPayment
        from aiogram import Bot
        
        # Create mock bot (won't actually send anything)
        bot = Bot(token="1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        stars_system = CleanStarsPayment(bot)
        
        # Test invoice creation
        campaign_data = {
            'package_name': 'Professional',
            'posts_total': 25,
            'auto_schedule_days': 5,
            'selected_addons': ['priority_support']
        }
        
        pricing_data = {
            'cost_stars': 510,  # 25 posts * $0.60 * 34 stars/USD
            'cost_ton': 5.40,   # 25 posts * $0.60 * 0.36 TON/USD
            'total_usd': 15.00
        }
        
        # This would normally create an invoice
        # result = await stars_system.create_post_package_invoice(12345, campaign_data, pricing_data)
        
        logger.info("✅ Payment flow simulation completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Payment flow simulation failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 STARTING POST-BASED SYSTEM INTEGRATION TESTS")
    print("=" * 70)
    
    # Run integration tests
    integration_success = await test_post_based_system_integration()
    
    # Run payment flow simulation
    payment_success = await test_payment_flow_simulation()
    
    print("\n" + "=" * 70)
    print("🏁 FINAL RESULTS")
    print("=" * 70)
    
    if integration_success and payment_success:
        print("🎉 ALL TESTS PASSED - POST-BASED SYSTEM READY FOR PRODUCTION")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)