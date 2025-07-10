#!/usr/bin/env python3
"""
Critical Wallet Management Bug Fixes Validation
Tests the complete fix for "Use Current Wallet" button issues and MESSAGE_TOO_LONG problems
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wallet_manager import WalletManager
from database import get_user_language
from aiogram.types import CallbackQuery, Message, User
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from unittest.mock import Mock, AsyncMock
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestWalletCriticalBugFixes:
    """Test suite for critical wallet management bug fixes"""
    
    def __init__(self):
        self.storage = MemoryStorage()
        self.test_results = []
        self.user_id = 123456789
        self.test_wallet = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
        
    async def create_mock_callback_query(self, data: str = "use_existing_wallet_payment") -> CallbackQuery:
        """Create a mock CallbackQuery object"""
        callback_query = Mock(spec=CallbackQuery)
        callback_query.data = data
        callback_query.from_user = Mock(spec=User)
        callback_query.from_user.id = self.user_id
        callback_query.message = Mock()
        callback_query.message.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        callback_query.answer = AsyncMock()
        return callback_query
    
    async def create_mock_message(self, text: str = "test") -> Message:
        """Create a mock Message object"""
        message = Mock(spec=Message)
        message.text = text
        message.from_user = Mock(spec=User)
        message.from_user.id = self.user_id
        message.answer = AsyncMock()
        message.reply = AsyncMock()
        return message
    
    async def create_mock_state(self, data: dict = None) -> FSMContext:
        """Create a mock FSMContext object"""
        if data is None:
            data = {
                'existing_wallet': self.test_wallet,
                'pending_payment_amount': 5.0,
                'wallet_context': 'payment'
            }
        
        state = FSMContext(storage=self.storage, key=f"test_user_{self.user_id}")
        await state.update_data(**data)
        return state
    
    async def test_wallet_address_validation(self):
        """Test 1: Wallet address validation functionality"""
        try:
            # Test valid addresses
            valid_addresses = [
                "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE",
                "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
            ]
            
            for address in valid_addresses:
                assert WalletManager.validate_ton_address(address), f"Valid address {address} should pass validation"
            
            # Test invalid addresses
            invalid_addresses = [
                "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrS",  # Too short
                "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSEX",  # Too long
                "XXDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE",  # Wrong prefix
                "invalid_address"  # Completely invalid
            ]
            
            for address in invalid_addresses:
                assert not WalletManager.validate_ton_address(address), f"Invalid address {address} should fail validation"
            
            self.test_results.append("✅ Test 1 PASSED: Wallet address validation working correctly")
            return True
            
        except Exception as e:
            self.test_results.append(f"❌ Test 1 FAILED: Wallet address validation error - {e}")
            return False
    
    async def test_use_existing_wallet_button_responsiveness(self):
        """Test 2: Use Current Wallet button responsiveness (critical bug fix)"""
        try:
            # Create test objects
            callback_query = await self.create_mock_callback_query("use_existing_wallet_payment")
            state = await self.create_mock_state()
            
            # Import the handler directly
            from wallet_manager import use_existing_wallet_handler
            
            # Call the handler
            await use_existing_wallet_handler(callback_query, state)
            
            # Verify callback was answered (no timeout)
            assert callback_query.answer.called, "Callback should be answered to prevent timeout"
            
            # Verify no exceptions were raised
            self.test_results.append("✅ Test 2 PASSED: Use Current Wallet button responds without errors")
            return True
            
        except Exception as e:
            self.test_results.append(f"❌ Test 2 FAILED: Use Current Wallet button error - {e}")
            return False
    
    async def test_message_length_optimization(self):
        """Test 3: Payment message length optimization (MESSAGE_TOO_LONG fix)"""
        try:
            # Create test objects
            callback_query = await self.create_mock_callback_query("use_existing_wallet_payment")
            state = await self.create_mock_state()
            
            # Test the simplified payment message creation
            from wallet_manager import continue_payment_with_wallet
            
            # Call the function
            await continue_payment_with_wallet(callback_query, state, self.test_wallet)
            
            # Verify message was sent without exception
            assert callback_query.message.answer.called, "Payment message should be sent"
            
            # Get the message text that was sent
            call_args = callback_query.message.answer.call_args
            if call_args:
                message_text = call_args[0][0]  # First positional argument
                
                # Check message length (Telegram limit is 4096 characters)
                assert len(message_text) < 4096, f"Message length {len(message_text)} should be under 4096 characters"
                assert len(message_text) < 500, f"Optimized message length {len(message_text)} should be under 500 characters"
                
                # Verify essential information is present
                assert "TON" in message_text, "Message should contain TON"
                assert "Amount" in message_text or "المبلغ" in message_text or "Сумма" in message_text, "Message should contain amount"
                assert "Steps" in message_text or "خطوات" in message_text or "Шаги" in message_text, "Message should contain steps"
            
            self.test_results.append("✅ Test 3 PASSED: Payment message optimized and under character limit")
            return True
            
        except Exception as e:
            self.test_results.append(f"❌ Test 3 FAILED: Message length optimization error - {e}")
            return False
    
    async def test_callbackquery_vs_message_handling(self):
        """Test 4: CallbackQuery vs Message object handling"""
        try:
            # Test with CallbackQuery
            callback_query = await self.create_mock_callback_query()
            state = await self.create_mock_state()
            
            from wallet_manager import continue_payment_with_wallet
            
            # Should handle CallbackQuery without error
            await continue_payment_with_wallet(callback_query, state, self.test_wallet)
            
            # Test with Message
            message = await self.create_mock_message()
            state = await self.create_mock_state()
            
            # Should handle Message without error
            await continue_payment_with_wallet(message, state, self.test_wallet)
            
            self.test_results.append("✅ Test 4 PASSED: Both CallbackQuery and Message objects handled correctly")
            return True
            
        except Exception as e:
            self.test_results.append(f"❌ Test 4 FAILED: CallbackQuery vs Message handling error - {e}")
            return False
    
    async def test_multilingual_error_handling(self):
        """Test 5: Multilingual error handling and user feedback"""
        try:
            # Test all supported languages
            languages = ['en', 'ar', 'ru']
            
            for lang in languages:
                # Mock the language function
                original_get_user_language = get_user_language
                async def mock_get_user_language(user_id):
                    return lang
                
                # Temporarily replace the function
                import wallet_manager
                wallet_manager.get_user_language = mock_get_user_language
                
                try:
                    # Test error handling with no wallet
                    callback_query = await self.create_mock_callback_query()
                    state = await self.create_mock_state({'existing_wallet': None})
                    
                    from wallet_manager import use_existing_wallet_handler
                    await use_existing_wallet_handler(callback_query, state)
                    
                    # Should have called answer with error message
                    assert callback_query.answer.called, f"Error message should be shown for {lang}"
                    
                finally:
                    # Restore original function
                    wallet_manager.get_user_language = original_get_user_language
            
            self.test_results.append("✅ Test 5 PASSED: Multilingual error handling working correctly")
            return True
            
        except Exception as e:
            self.test_results.append(f"❌ Test 5 FAILED: Multilingual error handling error - {e}")
            return False
    
    async def test_comprehensive_wallet_flow(self):
        """Test 6: Complete wallet flow from selection to payment"""
        try:
            # Test complete flow: wallet selection -> payment processing -> monitoring
            callback_query = await self.create_mock_callback_query("use_existing_wallet_payment")
            state = await self.create_mock_state()
            
            # Step 1: Use existing wallet
            from wallet_manager import use_existing_wallet_handler
            await use_existing_wallet_handler(callback_query, state)
            
            # Step 2: Verify state was updated
            data = await state.get_data()
            assert 'payment_memo' in data, "Payment memo should be generated"
            assert 'payment_amount' in data, "Payment amount should be stored"
            assert 'payment_expiration' in data, "Payment expiration should be set"
            
            # Step 3: Verify payment message was sent
            assert callback_query.message.answer.called, "Payment instructions should be sent"
            
            self.test_results.append("✅ Test 6 PASSED: Complete wallet flow working correctly")
            return True
            
        except Exception as e:
            self.test_results.append(f"❌ Test 6 FAILED: Complete wallet flow error - {e}")
            return False
    
    async def run_all_tests(self):
        """Run all critical wallet management tests"""
        logger.info("🔧 Starting Critical Wallet Management Bug Fixes Validation...")
        
        tests = [
            self.test_wallet_address_validation,
            self.test_use_existing_wallet_button_responsiveness,
            self.test_message_length_optimization,
            self.test_callbackquery_vs_message_handling,
            self.test_multilingual_error_handling,
            self.test_comprehensive_wallet_flow
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
            except Exception as e:
                logger.error(f"Test failed with exception: {e}")
                self.test_results.append(f"❌ Test failed with exception: {e}")
        
        # Print detailed results
        logger.info("\n" + "="*80)
        logger.info("CRITICAL WALLET MANAGEMENT BUG FIXES VALIDATION RESULTS")
        logger.info("="*80)
        
        for result in self.test_results:
            logger.info(result)
        
        logger.info("="*80)
        logger.info(f"SUMMARY: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            logger.info("🎉 ALL CRITICAL WALLET BUGS FIXED! System is production-ready.")
        else:
            logger.warning(f"⚠️  {total-passed} critical issues still need attention.")
        
        logger.info("="*80)
        
        return passed == total

async def main():
    """Main test execution"""
    tester = TestWalletCriticalBugFixes()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ WALLET MANAGEMENT SYSTEM: FULLY OPERATIONAL")
        print("🔧 All critical bugs fixed:")
        print("   - Use Current Wallet button responsiveness ✓")
        print("   - MESSAGE_TOO_LONG error resolution ✓")
        print("   - CallbackQuery vs Message handling ✓")
        print("   - Multilingual error handling ✓")
        print("   - Complete payment flow integration ✓")
        print("\n🚀 System ready for production deployment!")
    else:
        print("\n❌ WALLET MANAGEMENT SYSTEM: NEEDS ATTENTION")
        print("🔧 Some critical issues remain - check logs above")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())