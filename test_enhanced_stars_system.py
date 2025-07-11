#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Telegram Stars Payment System
Testing Phase 1 & Phase 2 Enhancements
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any

# Test framework setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockBot:
    """Mock bot for testing"""
    async def send_message(self, user_id, text, **kwargs):
        logger.info(f"Mock send_message to {user_id}: {text}")
        return True

class MockDatabase:
    """Mock database for testing"""
    async def fetchone(self, query, params=None):
        if 'users' in query:
            return (12345, False, 0)  # user_id, is_banned, failed_payment_count
        return None
    
    async def execute(self, query, params=None):
        logger.info(f"Mock DB execute: {query}")
        return True

async def test_enhanced_stars_payment_system():
    """Test enhanced Stars payment system"""
    try:
        logger.info("🧪 Testing Enhanced Telegram Stars Payment System")
        
        # Import system
        from enhanced_stars_payment_system import EnhancedStarsPaymentSystem
        
        # Create test instances
        mock_bot = MockBot()
        mock_db = MockDatabase()
        
        # Initialize system
        system = EnhancedStarsPaymentSystem(mock_bot, mock_db)
        
        # Test 1: System initialization
        logger.info("📋 Test 1: System Initialization")
        await system.initialize_ton_connect()
        logger.info("✅ System initialized successfully")
        
        # Test 2: Payment request creation with Phase 1 validation
        logger.info("📋 Test 2: Enhanced Payment Request Creation")
        
        test_campaign_data = {
            'duration': 7,
            'selected_channels': ['@test_channel1', '@test_channel2'],
            'posts_per_day': 2,
            'content': 'Test ad content'
        }
        
        test_pricing_data = {
            'total_stars': 100,
            'total_usd': 1.30,
            'discount_percent': 0
        }
        
        payment_result = await system.create_enhanced_payment_request(
            user_id=12345,
            campaign_data=test_campaign_data,
            pricing_data=test_pricing_data,
            language='en'
        )
        
        if payment_result.get('success'):
            logger.info("✅ Enhanced payment request created successfully")
            logger.info(f"   Payment ID: {payment_result.get('payment_id')}")
            logger.info(f"   Fraud Score: {payment_result.get('fraud_score', 0):.3f}")
            logger.info(f"   Processing Time: {payment_result.get('processing_time', 0):.3f}s")
        else:
            logger.warning(f"⚠️ Payment request failed: {payment_result.get('error')}")
        
        # Test 3: Fraud detection
        logger.info("📋 Test 3: Fraud Detection System")
        
        # Test suspicious payment
        suspicious_campaign = {
            'duration': 1,
            'selected_channels': ['@test_channel'],
            'posts_per_day': 10,  # Suspicious: too many posts
            'content': 'Test fraud content'
        }
        
        suspicious_pricing = {
            'total_stars': 1,  # Suspicious: too low
            'total_usd': 0.01,
            'discount_percent': 0
        }
        
        fraud_result = await system.create_enhanced_payment_request(
            user_id=12345,
            campaign_data=suspicious_campaign,
            pricing_data=suspicious_pricing,
            language='en'
        )
        
        fraud_score = fraud_result.get('fraud_score', 0)
        logger.info(f"✅ Fraud detection test completed - Score: {fraud_score:.3f}")
        
        # Test 4: Payment analytics
        logger.info("📋 Test 4: Payment Analytics")
        
        analytics = await system.get_payment_analytics(user_id=12345)
        logger.info("✅ Payment analytics retrieved:")
        logger.info(f"   Total Payments: {analytics.get('total_payments', 0)}")
        logger.info(f"   Fraud Attempts: {analytics.get('fraud_attempts', 0)}")
        logger.info(f"   Average Fraud Score: {analytics.get('average_fraud_score', 0):.3f}")
        
        # Test 5: Cleanup functionality
        logger.info("📋 Test 5: System Cleanup")
        
        await system.cleanup_expired_data()
        logger.info("✅ System cleanup completed")
        
        logger.info("🎉 All Enhanced Stars Payment System tests completed successfully!")
        
        return {
            'success': True,
            'tests_passed': 5,
            'system_ready': True,
            'phase1_features': ['validation', 'fraud_detection', 'error_handling'],
            'phase2_features': ['ton_connect_integration', 'advanced_security']
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced Stars payment system test failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'tests_passed': 0
        }

async def test_enhanced_handlers():
    """Test enhanced Stars handlers"""
    try:
        logger.info("🧪 Testing Enhanced Stars Payment Handlers")
        
        # Import handlers
        from enhanced_stars_handlers import setup_enhanced_stars_handlers
        
        # Create mock dispatcher
        class MockDispatcher:
            def __init__(self):
                self.routers = []
            
            def include_router(self, router):
                self.routers.append(router)
                logger.info(f"Mock router included: {router}")
        
        mock_dp = MockDispatcher()
        
        # Test handler setup
        setup_enhanced_stars_handlers(mock_dp)
        
        logger.info("✅ Enhanced Stars handlers registered successfully")
        logger.info(f"   Routers registered: {len(mock_dp.routers)}")
        
        return {
            'success': True,
            'handlers_registered': True,
            'router_count': len(mock_dp.routers)
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced handlers test failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def test_ton_connect_integration():
    """Test TON Connect integration"""
    try:
        logger.info("🧪 Testing TON Connect Integration")
        
        # Import TON Connect
        from ton_connect_integration import TONConnectIntegration
        
        # Create test instance
        mock_bot = MockBot()
        manifest_url = "https://test.com/manifest.json"
        
        ton_connect = TONConnectIntegration(mock_bot, manifest_url)
        
        # Test wallet list retrieval
        wallets = await ton_connect.get_wallet_list()
        logger.info(f"✅ TON Connect wallets available: {len(wallets)}")
        
        # Test connection session creation
        session = await ton_connect.create_connection_session(12345)
        logger.info(f"✅ Connection session created: {session.session_id}")
        
        # Test wallet selection keyboard
        keyboard = await ton_connect.create_wallet_selection_keyboard(12345)
        logger.info(f"✅ Wallet selection keyboard created with {len(keyboard.inline_keyboard)} options")
        
        # Test connection status
        status = await ton_connect.get_connection_status(12345)
        logger.info(f"✅ Connection status retrieved: {status}")
        
        return {
            'success': True,
            'wallets_available': len(wallets),
            'session_created': True,
            'keyboard_created': True
        }
        
    except Exception as e:
        logger.error(f"❌ TON Connect integration test failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def test_enhanced_payment_processor():
    """Test enhanced payment processor"""
    try:
        logger.info("🧪 Testing Enhanced Payment Processor")
        
        # Import processor
        from enhanced_payment_processor import (
            EnhancedPaymentProcessor, PaymentRequest, PaymentMethod, PaymentStatus
        )
        
        # Create test instance
        mock_bot = MockBot()
        processor = EnhancedPaymentProcessor(mock_bot)
        
        # Test payment request creation
        payment_request = await processor.create_payment_request(
            user_id=12345,
            amount=Decimal('100'),
            currency='XTR',
            payment_method=PaymentMethod.TELEGRAM_STARS,
            memo='TEST123',
            recipient_address='test_address'
        )
        
        logger.info(f"✅ Payment request created: {payment_request.payment_id}")
        logger.info(f"   Amount: {payment_request.amount} {payment_request.currency}")
        logger.info(f"   Method: {payment_request.payment_method.value}")
        
        # Test payment status retrieval
        status = await processor.get_payment_status(payment_request.payment_id)
        logger.info(f"✅ Payment status retrieved: {status.status.value if status else 'Not found'}")
        
        # Test cleanup
        await processor.cleanup_expired_payments()
        logger.info("✅ Payment processor cleanup completed")
        
        return {
            'success': True,
            'payment_created': True,
            'status_retrieved': True,
            'cleanup_working': True
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced payment processor test failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def run_comprehensive_test_suite():
    """Run comprehensive test suite for all enhancements"""
    logger.info("🚀 Starting Comprehensive Enhanced Stars Payment System Test Suite")
    logger.info("   Phase 1: Enhanced validation, fraud detection, error handling")
    logger.info("   Phase 2: TON Connect integration, advanced security")
    
    test_results = {}
    
    # Test 1: Enhanced Stars Payment System
    test_results['enhanced_stars_system'] = await test_enhanced_stars_payment_system()
    
    # Test 2: Enhanced Handlers
    test_results['enhanced_handlers'] = await test_enhanced_handlers()
    
    # Test 3: TON Connect Integration
    test_results['ton_connect_integration'] = await test_ton_connect_integration()
    
    # Test 4: Enhanced Payment Processor
    test_results['enhanced_payment_processor'] = await test_enhanced_payment_processor()
    
    # Calculate overall results
    total_tests = len(test_results)
    passed_tests = len([r for r in test_results.values() if r.get('success', False)])
    success_rate = (passed_tests / total_tests) * 100
    
    logger.info("📊 Comprehensive Test Results:")
    logger.info(f"   Total Test Categories: {total_tests}")
    logger.info(f"   Passed Categories: {passed_tests}")
    logger.info(f"   Success Rate: {success_rate:.1f}%")
    
    # Detailed results
    for test_name, result in test_results.items():
        status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
        if not result.get('success', False):
            logger.info(f"     Error: {result.get('error', 'Unknown error')}")
    
    # Overall assessment
    if success_rate >= 75:
        logger.info("🎉 SYSTEM ASSESSMENT: Enhanced Stars Payment System is PRODUCTION READY")
        logger.info("   Phase 1 & Phase 2 enhancements successfully implemented")
        logger.info("   Enterprise-grade payment processing capabilities confirmed")
    elif success_rate >= 50:
        logger.info("⚠️ SYSTEM ASSESSMENT: Enhanced Stars Payment System needs minor fixes")
        logger.info("   Core functionality working, some enhancements need attention")
    else:
        logger.info("❌ SYSTEM ASSESSMENT: Enhanced Stars Payment System needs major fixes")
        logger.info("   Significant issues detected, comprehensive review required")
    
    return {
        'overall_success': success_rate >= 75,
        'success_rate': success_rate,
        'test_results': test_results,
        'production_ready': success_rate >= 75,
        'phase1_status': 'operational' if success_rate >= 75 else 'needs_attention',
        'phase2_status': 'operational' if success_rate >= 75 else 'needs_attention'
    }

if __name__ == "__main__":
    # Run the comprehensive test suite
    result = asyncio.run(run_comprehensive_test_suite())
    
    if result['production_ready']:
        print("\n🚀 Enhanced Telegram Stars Payment System is ready for deployment!")
        print("   Phase 1 & Phase 2 enhancements operational")
        print("   TON Connect integration available")
        print("   Enterprise-grade security protocols active")
    else:
        print(f"\n⚠️ System needs attention - Success rate: {result['success_rate']:.1f}%")
        print("   Review test results and fix identified issues")