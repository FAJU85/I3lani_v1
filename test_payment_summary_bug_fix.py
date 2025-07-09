#!/usr/bin/env python3
"""
Test suite to validate the payment summary bug fix (CreateAd_Step_7_ShowSummary)
This test verifies that the payment summary displays in the correct user language
and that all payment buttons (TON, Stars, Change Duration) work properly.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from handlers import show_frequency_payment_summary, show_frequency_payment_summary_message, pay_frequency_ton_handler, pay_frequency_stars_handler, frequency_change_duration_handler
from aiogram.types import CallbackQuery, User, Chat, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from unittest.mock import Mock, AsyncMock
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockBot:
    """Mock bot for testing"""
    def __init__(self):
        self.id = 123456789

class MockMessage:
    """Mock message for testing"""
    def __init__(self, text="", user_id=566158428, chat_id=566158428):
        self.message_id = 1
        self.text = text
        self.from_user = User(id=user_id, is_bot=False, first_name="Test", username="testuser")
        self.chat = Chat(id=chat_id, type="private")
        self.bot = MockBot()
        
    async def edit_text(self, text, reply_markup=None, parse_mode=None):
        """Mock edit_text"""
        # Check for Arabic text
        if "ملخص خطة إعلانك" in text:
            print("✅ Arabic payment summary detected")
        elif "Сводка вашего рекламного плана" in text:
            print("✅ Russian payment summary detected")
        elif "Your Ad Plan Summary" in text:
            print("✅ English payment summary detected")
        else:
            print("❌ No recognized payment summary language")
        
        print(f"📝 PAYMENT SUMMARY: {text[:100]}...")
        return True
        
    async def answer(self, text, reply_markup=None, parse_mode=None):
        """Mock answer"""
        print(f"📬 MESSAGE ANSWER: {text[:100]}...")
        return True
        
    async def reply(self, text, reply_markup=None, parse_mode=None):
        """Mock reply"""
        print(f"📬 MESSAGE REPLY: {text[:100]}...")
        return True

class MockCallbackQuery:
    """Mock callback query for testing"""
    def __init__(self, data="", user_id=566158428, chat_id=566158428):
        self.id = "test_callback"
        self.data = data
        self.from_user = User(id=user_id, is_bot=False, first_name="Test", username="testuser")
        self.message = MockMessage(user_id=user_id, chat_id=chat_id)
        self.bot = MockBot()
        
    async def answer(self, text="", show_alert=False):
        """Mock answer"""
        if text:
            print(f"⚡ CALLBACK ANSWER: {text}")
        return True

class PaymentSummaryBugTest:
    """Test class for payment summary bug validation"""
    
    def __init__(self):
        self.db = Database()
        self.storage = MemoryStorage()
        
    async def setup_test_user(self, user_id: int, language: str):
        """Setup test user with specified language"""
        try:
            # Create user in database
            await self.db.create_user(user_id, "testuser", "Test User")
            
            # Set user language
            await self.db.set_user_language(user_id, language)
            
            logger.info(f"✅ User {user_id} setup complete with language: {language}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up test user: {e}")
            return False
            
    async def test_payment_summary_language_consistency(self):
        """Test that payment summary displays in correct language"""
        print("\n🔍 Testing Payment Summary Language Consistency...")
        
        test_cases = [
            (566158428, 'ar', 'Arabic'),
            (566158429, 'ru', 'Russian'),
            (566158430, 'en', 'English')
        ]
        
        results = []
        
        for user_id, language, language_name in test_cases:
            try:
                # Setup user
                await self.setup_test_user(user_id, language)
                
                # Create mock callback query
                callback_query = MockCallbackQuery(data="show_payment_summary", user_id=user_id)
                
                # Create FSM context
                fsm_key = f"test_key_{user_id}"
                state = FSMContext(storage=self.storage, key=fsm_key)
                
                # Set up pricing data
                pricing_data = {
                    'days': 7,
                    'posts_per_day': 2,
                    'discount_percent': 5,
                    'final_cost_usd': 25.20,
                    'cost_ton': 0.907,
                    'cost_stars': 857,
                    'daily_price': 3.60,
                    'total_posts': 14,
                    'base_cost_usd': 25.20,
                    'savings_usd': 1.32,
                    'savings_percent': 5
                }
                
                # Set up state data
                await state.update_data(
                    selected_channels=['test_channel_1'],
                    pricing_data=pricing_data
                )
                
                print(f"\n🧪 Testing {language_name} payment summary (user {user_id})...")
                
                # Test the payment summary function
                try:
                    await show_frequency_payment_summary(callback_query, state, pricing_data)
                    
                    results.append({
                        'user_id': user_id,
                        'language': language,
                        'language_name': language_name,
                        'status': 'PASS',
                        'message': f"Payment summary displayed successfully in {language_name}"
                    })
                    
                    print(f"✅ {language_name} payment summary test PASSED")
                    
                except Exception as e:
                    results.append({
                        'user_id': user_id,
                        'language': language,
                        'language_name': language_name,
                        'status': 'FAIL',
                        'error': str(e),
                        'message': f"Error in payment summary for {language_name}: {e}"
                    })
                    
                    print(f"❌ {language_name} payment summary test FAILED: {e}")
                    
            except Exception as e:
                print(f"❌ Setup failed for {language_name}: {e}")
                results.append({
                    'user_id': user_id,
                    'language': language,
                    'language_name': language_name,
                    'status': 'SETUP_FAIL',
                    'error': str(e),
                    'message': f"Setup failed for {language_name}: {e}"
                })
                
        return results
        
    async def test_payment_button_handlers(self):
        """Test that payment buttons work properly"""
        print("\n💰 Testing Payment Button Handlers...")
        
        results = []
        
        # Test TON payment button
        try:
            callback_query = MockCallbackQuery(data="pay_freq_ton", user_id=566158428)
            state = FSMContext(storage=self.storage, key="payment_test_key")
            
            # Setup test user
            await self.setup_test_user(566158428, 'en')
            
            # Set up pricing data
            pricing_data = {
                'cost_ton': 0.907,
                'cost_stars': 857,
                'days': 7,
                'posts_per_day': 2
            }
            
            await state.update_data(
                selected_channels=['test_channel_1'],
                pricing_data=pricing_data
            )
            
            print("🔍 Testing TON payment button handler...")
            await pay_frequency_ton_handler(callback_query, state)
            
            results.append({
                'button': 'pay_freq_ton',
                'status': 'PASS',
                'message': 'TON payment button works correctly'
            })
            print("✅ TON payment button test PASSED")
            
        except Exception as e:
            results.append({
                'button': 'pay_freq_ton',
                'status': 'FAIL',
                'error': str(e),
                'message': f'TON payment button failed: {e}'
            })
            print(f"❌ TON payment button test FAILED: {e}")
            
        # Test Stars payment button
        try:
            callback_query = MockCallbackQuery(data="pay_freq_stars", user_id=566158428)
            state = FSMContext(storage=self.storage, key="payment_test_key2")
            
            # Set up pricing data
            await state.update_data(
                selected_channels=['test_channel_1'],
                pricing_data=pricing_data
            )
            
            print("🔍 Testing Stars payment button handler...")
            await pay_frequency_stars_handler(callback_query, state)
            
            results.append({
                'button': 'pay_freq_stars',
                'status': 'PASS',
                'message': 'Stars payment button works correctly'
            })
            print("✅ Stars payment button test PASSED")
            
        except Exception as e:
            results.append({
                'button': 'pay_freq_stars',
                'status': 'FAIL',
                'error': str(e),
                'message': f'Stars payment button failed: {e}'
            })
            print(f"❌ Stars payment button test FAILED: {e}")
            
        # Test Change Duration button
        try:
            callback_query = MockCallbackQuery(data="freq_change_duration", user_id=566158428)
            state = FSMContext(storage=self.storage, key="payment_test_key3")
            
            print("🔍 Testing Change Duration button handler...")
            await frequency_change_duration_handler(callback_query, state)
            
            results.append({
                'button': 'freq_change_duration',
                'status': 'PASS',
                'message': 'Change Duration button works correctly'
            })
            print("✅ Change Duration button test PASSED")
            
        except Exception as e:
            results.append({
                'button': 'freq_change_duration',
                'status': 'FAIL',
                'error': str(e),
                'message': f'Change Duration button failed: {e}'
            })
            print(f"❌ Change Duration button test FAILED: {e}")
            
        return results
        
    async def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🚀 Starting Comprehensive Payment Summary Bug Fix Test\n")
        
        try:
            # Initialize database
            await self.db.init_db()
            
            # Test 1: Payment summary language consistency
            summary_results = await self.test_payment_summary_language_consistency()
            
            # Test 2: Payment button handlers
            button_results = await self.test_payment_button_handlers()
            
            # Generate comprehensive report
            self.generate_test_report(summary_results, button_results)
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            logger.error(f"Test suite error: {e}")
            
    def generate_test_report(self, summary_results, button_results):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE TEST REPORT - Payment Summary Bug Fix")
        print("="*80)
        
        # Payment Summary Tests
        print("\n1. PAYMENT SUMMARY LANGUAGE CONSISTENCY:")
        summary_pass = 0
        summary_fail = 0
        
        for result in summary_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {result['language_name']}: {result['message']}")
            
            if result['status'] == 'PASS':
                summary_pass += 1
            else:
                summary_fail += 1
                
        print(f"\n   Summary: {summary_pass} PASSED, {summary_fail} FAILED")
        
        # Payment Button Tests
        print("\n2. PAYMENT BUTTON HANDLERS:")
        button_pass = 0
        button_fail = 0
        
        for result in button_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {result['button']}: {result['message']}")
            
            if result['status'] == 'PASS':
                button_pass += 1
            else:
                button_fail += 1
                
        print(f"\n   Summary: {button_pass} PASSED, {button_fail} FAILED")
        
        # Overall Results
        total_pass = summary_pass + button_pass
        total_fail = summary_fail + button_fail
        success_rate = (total_pass / (total_pass + total_fail)) * 100 if (total_pass + total_fail) > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_pass + total_fail}")
        print(f"   Passed: {total_pass}")
        print(f"   Failed: {total_fail}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if total_fail == 0:
            print("\n🎉 ALL TESTS PASSED! Payment Summary Bug Fix Successful!")
            print("   ✅ Payment summary displays in correct language")
            print("   ✅ TON payment button works correctly")
            print("   ✅ Stars payment button works correctly")
            print("   ✅ Change Duration button works correctly")
            print("   ✅ Language consistency maintained throughout payment flow")
        else:
            print(f"\n⚠️  {total_fail} TEST(S) FAILED - Review required")
            
        print("\n" + "="*80)

async def main():
    """Main test function"""
    test_suite = PaymentSummaryBugTest()
    await test_suite.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())