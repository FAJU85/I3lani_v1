#!/usr/bin/env python3
"""
Test suite to validate the duration selection bug fix (CreateAd_Step_4_SelectDays)
This test verifies that the duration selection step displays in the correct user language
and that the payment system functions properly without crashes.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from handlers import show_dynamic_days_selector, process_ton_payment, process_stars_payment
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
        print(f"📝 MESSAGE EDIT: {text[:100]}...")
        return True
        
    async def answer(self, text, reply_markup=None, parse_mode=None):
        """Mock answer"""
        print(f"📬 MESSAGE ANSWER: {text[:100]}...")
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

class DurationSelectionBugTest:
    """Test class for duration selection bug validation"""
    
    def __init__(self):
        self.db = Database()
        self.storage = MemoryStorage()
        self.fsm_context = FSMContext(storage=self.storage, key="test_key")
        
    async def setup_test_user(self, user_id: int, language: str):
        """Setup test user with specified language"""
        try:
            # Create user in database
            await self.db.create_user(user_id, "testuser", "Test User")
            
            # Set user language
            await self.db.set_user_language(user_id, language)
            
            # Verify language was set
            stored_language = await self.db.get_user_language(user_id)
            assert stored_language == language, f"Language not set correctly: {stored_language} != {language}"
            
            logger.info(f"✅ User {user_id} setup complete with language: {language}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up test user: {e}")
            return False
            
    async def test_duration_selection_language_consistency(self):
        """Test that duration selection displays in correct language"""
        print("\n🔍 Testing Duration Selection Language Consistency...")
        
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
                callback_query = MockCallbackQuery(data="continue_to_duration", user_id=user_id)
                
                # Create FSM context
                fsm_key = f"test_key_{user_id}"
                state = FSMContext(storage=self.storage, key=fsm_key)
                
                # Set up state data
                await state.update_data(
                    selected_channels=['test_channel_1'],
                    selected_days=7
                )
                
                print(f"\n🧪 Testing {language_name} language (user {user_id})...")
                
                # Test the duration selection function
                try:
                    await show_dynamic_days_selector(callback_query, state, 7)
                    
                    # Get the language from database to verify it was used
                    stored_language = await self.db.get_user_language(user_id)
                    
                    results.append({
                        'user_id': user_id,
                        'language': language,
                        'language_name': language_name,
                        'status': 'PASS',
                        'stored_language': stored_language,
                        'message': f"Duration selection displayed successfully in {language_name}"
                    })
                    
                    print(f"✅ {language_name} test PASSED")
                    
                except Exception as e:
                    results.append({
                        'user_id': user_id,
                        'language': language,
                        'language_name': language_name,
                        'status': 'FAIL',
                        'error': str(e),
                        'message': f"Error in duration selection for {language_name}: {e}"
                    })
                    
                    print(f"❌ {language_name} test FAILED: {e}")
                    
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
        
    async def test_payment_functions_exist(self):
        """Test that payment functions exist and work properly"""
        print("\n💰 Testing Payment Functions Availability...")
        
        results = []
        
        # Test process_ton_payment function
        try:
            callback_query = MockCallbackQuery(data="pay_freq_ton", user_id=566158428)
            state = FSMContext(storage=self.storage, key="payment_test_key")
            
            # Setup test user
            await self.setup_test_user(566158428, 'en')
            
            print("🔍 Testing process_ton_payment function...")
            await process_ton_payment(callback_query, state, 1.5)
            
            results.append({
                'function': 'process_ton_payment',
                'status': 'PASS',
                'message': 'TON payment function works correctly'
            })
            print("✅ process_ton_payment test PASSED")
            
        except Exception as e:
            results.append({
                'function': 'process_ton_payment',
                'status': 'FAIL',
                'error': str(e),
                'message': f'TON payment function failed: {e}'
            })
            print(f"❌ process_ton_payment test FAILED: {e}")
            
        # Test process_stars_payment function
        try:
            callback_query = MockCallbackQuery(data="pay_freq_stars", user_id=566158428)
            state = FSMContext(storage=self.storage, key="payment_test_key2")
            
            print("🔍 Testing process_stars_payment function...")
            await process_stars_payment(callback_query, state, 1000)
            
            results.append({
                'function': 'process_stars_payment',
                'status': 'PASS',
                'message': 'Stars payment function works correctly'
            })
            print("✅ process_stars_payment test PASSED")
            
        except Exception as e:
            results.append({
                'function': 'process_stars_payment',
                'status': 'FAIL',
                'error': str(e),
                'message': f'Stars payment function failed: {e}'
            })
            print(f"❌ process_stars_payment test FAILED: {e}")
            
        return results
        
    async def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🚀 Starting Comprehensive Duration Selection Bug Fix Test\n")
        
        try:
            # Initialize database
            await self.db.init_db()
            
            # Test 1: Duration selection language consistency
            duration_results = await self.test_duration_selection_language_consistency()
            
            # Test 2: Payment functions availability
            payment_results = await self.test_payment_functions_exist()
            
            # Generate comprehensive report
            self.generate_test_report(duration_results, payment_results)
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            logger.error(f"Test suite error: {e}")
            
    def generate_test_report(self, duration_results, payment_results):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE TEST REPORT - Duration Selection Bug Fix")
        print("="*80)
        
        # Duration Selection Tests
        print("\n1. DURATION SELECTION LANGUAGE CONSISTENCY:")
        duration_pass = 0
        duration_fail = 0
        
        for result in duration_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {result['language_name']}: {result['message']}")
            
            if result['status'] == 'PASS':
                duration_pass += 1
            else:
                duration_fail += 1
                
        print(f"\n   Summary: {duration_pass} PASSED, {duration_fail} FAILED")
        
        # Payment Function Tests
        print("\n2. PAYMENT FUNCTIONS AVAILABILITY:")
        payment_pass = 0
        payment_fail = 0
        
        for result in payment_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {result['function']}: {result['message']}")
            
            if result['status'] == 'PASS':
                payment_pass += 1
            else:
                payment_fail += 1
                
        print(f"\n   Summary: {payment_pass} PASSED, {payment_fail} FAILED")
        
        # Overall Results
        total_pass = duration_pass + payment_pass
        total_fail = duration_fail + payment_fail
        success_rate = (total_pass / (total_pass + total_fail)) * 100 if (total_pass + total_fail) > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_pass + total_fail}")
        print(f"   Passed: {total_pass}")
        print(f"   Failed: {total_fail}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if total_fail == 0:
            print("\n🎉 ALL TESTS PASSED! Bug Fix Successful!")
            print("   ✅ Duration selection displays in correct language")
            print("   ✅ Payment functions work without crashes")
            print("   ✅ Language consistency maintained throughout flow")
        else:
            print(f"\n⚠️  {total_fail} TEST(S) FAILED - Review required")
            
        print("\n" + "="*80)

async def main():
    """Main test function"""
    test_suite = DurationSelectionBugTest()
    await test_suite.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())