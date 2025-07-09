#!/usr/bin/env python3
"""
Test suite to validate the pricing flow fix
This test verifies that channel selection now leads to dynamic day-based pricing
instead of the old progressive monthly plans.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from handlers import continue_with_channels_handler, show_dynamic_days_selector
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

class MockCallbackQuery:
    """Mock callback query for testing"""
    def __init__(self, data, user_id=566158431):
        self.data = data
        self.from_user = Mock()
        self.from_user.id = user_id
        self.from_user.username = "testuser"
        self.from_user.first_name = "Test"
        self.message = Mock()
        self.message.chat = Mock()
        self.message.chat.id = user_id
        self.bot = MockBot()
        self.id = "test_callback_id"
        
        # Mock answer method
        self.answer = AsyncMock()
        
        # Track edit_text calls
        self.edit_text_calls = []
        
        # Mock message.edit_text
        async def mock_edit_text(text, reply_markup=None, parse_mode=None):
            self.edit_text_calls.append({
                'text': text,
                'reply_markup': reply_markup,
                'parse_mode': parse_mode
            })
            return True
            
        self.message.edit_text = mock_edit_text

class PricingFlowTest:
    """Test class for pricing flow validation"""
    
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
            
    async def test_channel_selection_flow(self):
        """Test that channel selection leads to dynamic days selector"""
        print("\n🔍 Testing Channel Selection Flow...")
        
        results = []
        
        # Test user
        user_id = 566158431
        language = 'en'
        
        try:
            # Setup user
            await self.setup_test_user(user_id, language)
            
            # Create mock callback query
            callback_query = MockCallbackQuery(data="continue_with_channels", user_id=user_id)
            
            # Create FSM context
            fsm_key = f"test_key_{user_id}"
            state = FSMContext(storage=self.storage, key=fsm_key)
            
            # Set up state data with selected channels
            await state.update_data(
                selected_channels=['test_channel_1', 'test_channel_2']
            )
            
            print("\n🧪 Testing continue_with_channels_handler...")
            
            # Test the handler
            try:
                await continue_with_channels_handler(callback_query, state)
                
                # Check if edit_text was called
                assert len(callback_query.edit_text_calls) > 0, "No edit_text calls made"
                
                # Get the text that was displayed
                displayed_text = callback_query.edit_text_calls[0]['text']
                
                # Check for dynamic days selector indicators
                if "Step 1: Choose Campaign Duration" in displayed_text:
                    results.append({
                        'test': 'Channel Selection Flow',
                        'status': 'PASS',
                        'message': 'Correctly shows dynamic days selector'
                    })
                    print("✅ Dynamic days selector displayed correctly")
                elif "Full-Year Posting Plans" in displayed_text:
                    results.append({
                        'test': 'Channel Selection Flow',
                        'status': 'FAIL',
                        'message': 'Still showing old progressive monthly plans!'
                    })
                    print("❌ Still showing old progressive plans!")
                else:
                    results.append({
                        'test': 'Channel Selection Flow',
                        'status': 'UNKNOWN',
                        'message': 'Unexpected interface displayed'
                    })
                    print("⚠️ Unexpected interface displayed")
                
                # Print the displayed text for debugging
                print(f"\n📄 Displayed text preview:\n{displayed_text[:200]}...")
                
            except Exception as e:
                results.append({
                    'test': 'Channel Selection Flow',
                    'status': 'ERROR',
                    'error': str(e),
                    'message': f'Handler error: {e}'
                })
                print(f"❌ Handler error: {e}")
                
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            results.append({
                'test': 'Test Setup',
                'status': 'SETUP_FAIL',
                'error': str(e)
            })
            
        return results
        
    async def test_pricing_calculation(self):
        """Test that pricing calculation uses dynamic day-based system"""
        print("\n🔍 Testing Pricing Calculation...")
        
        results = []
        
        try:
            # Import the pricing system
            from frequency_pricing import FrequencyPricingSystem
            pricing_system = FrequencyPricingSystem()
            
            # Test pricing for different day values
            test_cases = [
                (1, 1),    # 1 day, 1 post/day
                (3, 2),    # 3 days, 2 posts/day
                (7, 4),    # 7 days, 4 posts/day
                (30, 10)   # 30 days, 10 posts/day
            ]
            
            for days, expected_posts_per_day in test_cases:
                pricing_data = pricing_system.calculate_pricing(days)
                
                if pricing_data['posts_per_day'] == expected_posts_per_day:
                    results.append({
                        'test': f'Pricing for {days} days',
                        'status': 'PASS',
                        'message': f'Correctly calculated {expected_posts_per_day} posts/day'
                    })
                    print(f"✅ {days} days = {expected_posts_per_day} posts/day (${pricing_data['final_cost_usd']:.2f})")
                else:
                    results.append({
                        'test': f'Pricing for {days} days',
                        'status': 'FAIL',
                        'message': f'Expected {expected_posts_per_day} posts/day, got {pricing_data["posts_per_day"]}'
                    })
                    print(f"❌ {days} days calculation failed")
                    
        except Exception as e:
            results.append({
                'test': 'Pricing Calculation',
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"❌ Pricing calculation error: {e}")
            
        return results
        
    def generate_test_report(self, flow_results, pricing_results):
        """Generate comprehensive test report"""
        print("\n" + "="*50)
        print("📊 PRICING FLOW FIX TEST REPORT")
        print("="*50)
        
        all_results = flow_results + pricing_results
        
        # Count results
        total_tests = len(all_results)
        passed = sum(1 for r in all_results if r.get('status') == 'PASS')
        failed = sum(1 for r in all_results if r.get('status') == 'FAIL')
        errors = sum(1 for r in all_results if r.get('status') in ['ERROR', 'SETUP_FAIL'])
        
        print(f"\n📈 Test Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️ Errors: {errors}")
        
        print(f"\n📋 Detailed Results:")
        for result in all_results:
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌',
                'ERROR': '⚠️',
                'SETUP_FAIL': '⚠️',
                'UNKNOWN': '❓'
            }.get(result.get('status', 'UNKNOWN'), '❓')
            
            print(f"\n{status_icon} {result.get('test', 'Unknown Test')}")
            print(f"   Status: {result.get('status', 'UNKNOWN')}")
            print(f"   Message: {result.get('message', 'No message')}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
        
        # Summary
        if failed == 0 and errors == 0:
            print(f"\n✅ ALL TESTS PASSED! The pricing flow fix is working correctly.")
            print("Users now see the dynamic day-based pricing instead of old monthly plans.")
        else:
            print(f"\n❌ ISSUES FOUND! Some tests failed or had errors.")
            print("The pricing flow may still have issues that need fixing.")
            
    async def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🚀 Starting Comprehensive Pricing Flow Test\n")
        
        try:
            # Initialize database
            await self.db.init_db()
            
            # Test 1: Channel selection flow
            flow_results = await self.test_channel_selection_flow()
            
            # Test 2: Pricing calculation
            pricing_results = await self.test_pricing_calculation()
            
            # Generate comprehensive report
            self.generate_test_report(flow_results, pricing_results)
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            logger.error(f"Test suite error: {e}")

async def main():
    """Run the test suite"""
    test = PricingFlowTest()
    await test.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())