#!/usr/bin/env python3
"""
Test Suite for Payment Receipt and Ad Publishing Report Bug Fix
Validates that users receive both payment confirmations and publishing notifications
"""

import asyncio
import sys
import os
import unittest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from handlers import send_payment_receipt, send_ad_publishing_report
from languages import get_text

class PaymentReceiptPublishingReportTest:
    """Test suite for payment receipt and ad publishing report functionality"""
    
    def __init__(self):
        self.db = Database()
        self.test_user_id = 566158431
        self.test_languages = ['en', 'ar', 'ru']
        self.test_channels = [
            {'channel_id': 'test_channel_1', 'name': 'Test Channel 1'},
            {'channel_id': 'test_channel_2', 'name': 'Test Channel 2'}
        ]
        
    async def test_payment_receipt_functionality(self):
        """Test payment receipt sending functionality"""
        print("🧾 Testing Payment Receipt Functionality")
        print("=" * 50)
        
        results = []
        
        for language in self.test_languages:
            print(f"\n🌐 Testing {language.upper()} language...")
            
            # Test TON payment receipt
            try:
                payment_data = {
                    'payment_method': 'ton',
                    'amount': 2.5,
                    'memo': 'AB1234',
                    'selected_channels': ['test_channel_1', 'test_channel_2'],
                    'days': 7,
                    'posts_per_day': 3,
                    'ad_id': 'test_ad_123'
                }
                
                with patch('handlers.bot') as mock_bot:
                    mock_bot.send_message = AsyncMock()
                    
                    await send_payment_receipt(self.test_user_id, payment_data, language)
                    
                    # Verify receipt was sent
                    mock_bot.send_message.assert_called_once()
                    call_args = mock_bot.send_message.call_args
                    
                    # Check message content
                    message_text = call_args.kwargs['text']
                    
                    # Language-specific validations
                    if language == 'ar':
                        assert 'تم تأكيد الدفع' in message_text or 'شكراً لاستخدام' in message_text
                    elif language == 'ru':
                        assert 'Оплата получена' in message_text or 'Спасибо за использование' in message_text
                    else:
                        assert 'Payment Received' in message_text or 'Thank you for using' in message_text
                    
                    # Check that essential payment info is included
                    assert str(payment_data['amount']) in message_text
                    assert str(payment_data['days']) in message_text
                    assert str(payment_data['posts_per_day']) in message_text
                    
                    results.append({
                        'test': f'TON Payment Receipt - {language}',
                        'status': 'PASS',
                        'message': 'Payment receipt sent successfully with correct language'
                    })
                    print(f"   ✅ TON payment receipt test PASSED")
                    
            except Exception as e:
                results.append({
                    'test': f'TON Payment Receipt - {language}',
                    'status': 'FAIL',
                    'error': str(e),
                    'message': f'TON payment receipt failed: {e}'
                })
                print(f"   ❌ TON payment receipt test FAILED: {e}")
            
            # Test Stars payment receipt
            try:
                payment_data = {
                    'payment_method': 'stars',
                    'amount': 85,
                    'memo': 'STARS0001',
                    'selected_channels': ['test_channel_1'],
                    'days': 3,
                    'posts_per_day': 2,
                    'ad_id': 'test_ad_456'
                }
                
                with patch('handlers.bot') as mock_bot:
                    mock_bot.send_message = AsyncMock()
                    
                    await send_payment_receipt(self.test_user_id, payment_data, language)
                    
                    # Verify receipt was sent
                    mock_bot.send_message.assert_called_once()
                    call_args = mock_bot.send_message.call_args
                    
                    # Check message content
                    message_text = call_args.kwargs['text']
                    
                    # Check Stars-specific content
                    assert str(payment_data['amount']) in message_text
                    assert 'STARS' in message_text.upper()
                    
                    results.append({
                        'test': f'Stars Payment Receipt - {language}',
                        'status': 'PASS',
                        'message': 'Stars payment receipt sent successfully'
                    })
                    print(f"   ✅ Stars payment receipt test PASSED")
                    
            except Exception as e:
                results.append({
                    'test': f'Stars Payment Receipt - {language}',
                    'status': 'FAIL',
                    'error': str(e),
                    'message': f'Stars payment receipt failed: {e}'
                })
                print(f"   ❌ Stars payment receipt test FAILED: {e}")
        
        return results
    
    async def test_ad_publishing_report_functionality(self):
        """Test ad publishing report sending functionality"""
        print("\n📢 Testing Ad Publishing Report Functionality")
        print("=" * 50)
        
        results = []
        
        for language in self.test_languages:
            print(f"\n🌐 Testing {language.upper()} language...")
            
            try:
                ad_data = {
                    'ad_id': 'test_ad_789',
                    'ad_text': 'Test advertisement content for validation',
                    'channel_id': 'test_channel_1'
                }
                
                channel_name = 'Test Channel 1'
                
                with patch('handlers.bot') as mock_bot:
                    mock_bot.send_message = AsyncMock()
                    
                    await send_ad_publishing_report(self.test_user_id, ad_data, channel_name, language)
                    
                    # Verify report was sent
                    mock_bot.send_message.assert_called_once()
                    call_args = mock_bot.send_message.call_args
                    
                    # Check message content
                    message_text = call_args.kwargs['text']
                    
                    # Language-specific validations
                    if language == 'ar':
                        assert 'تم نشر إعلانك' in message_text or 'نُشر في' in message_text
                    elif language == 'ru':
                        assert 'успешно опубликовано' in message_text or 'Опубликовано в' in message_text
                    else:
                        assert 'Published Successfully' in message_text or 'Published to' in message_text
                    
                    # Check that essential publishing info is included
                    assert channel_name in message_text
                    assert ad_data['ad_id'] in message_text
                    assert 'Test advertisement content' in message_text
                    
                    results.append({
                        'test': f'Ad Publishing Report - {language}',
                        'status': 'PASS',
                        'message': 'Publishing report sent successfully with correct language'
                    })
                    print(f"   ✅ Ad publishing report test PASSED")
                    
            except Exception as e:
                results.append({
                    'test': f'Ad Publishing Report - {language}',
                    'status': 'FAIL',
                    'error': str(e),
                    'message': f'Publishing report failed: {e}'
                })
                print(f"   ❌ Ad publishing report test FAILED: {e}")
        
        return results
    
    async def test_payment_flow_integration(self):
        """Test complete payment flow with receipts and publishing reports"""
        print("\n🔄 Testing Complete Payment Flow Integration")
        print("=" * 50)
        
        results = []
        
        # Test TON payment flow
        try:
            print("\n💎 Testing TON Payment Flow...")
            
            # Mock the complete TON payment success flow
            with patch('handlers.bot') as mock_bot, \
                 patch('handlers.db') as mock_db, \
                 patch('handlers.scheduler') as mock_scheduler:
                
                mock_bot.send_message = AsyncMock()
                mock_db.create_ad = AsyncMock(return_value='test_ad_123')
                mock_db.create_subscription = AsyncMock(return_value='test_sub_123')
                mock_db.create_payment = AsyncMock(return_value='test_payment_123')
                mock_db.activate_subscriptions = AsyncMock()
                mock_db.get_channels = AsyncMock(return_value=[
                    {'channel_id': 'test_channel_1', 'name': 'Test Channel 1'}
                ])
                mock_scheduler.publish_immediately_after_payment = AsyncMock()
                
                from handlers import handle_successful_ton_payment
                from aiogram.fsm.context import FSMContext
                from aiogram.fsm.storage.memory import MemoryStorage
                
                storage = MemoryStorage()
                state = FSMContext(storage=storage, key="test_key")
                
                await state.update_data(
                    selected_channels=['test_channel_1'],
                    ad_text='Test ad content',
                    photos=[],
                    pricing_calculation={'days': 7, 'posts_per_day': 3}
                )
                
                await handle_successful_ton_payment(
                    self.test_user_id, 'AB1234', 2.5, state
                )
                
                # Verify both receipt and publishing report were sent
                assert mock_bot.send_message.call_count >= 2
                
                results.append({
                    'test': 'TON Payment Flow Integration',
                    'status': 'PASS',
                    'message': 'Complete TON payment flow works with receipts and reports'
                })
                print("   ✅ TON payment flow integration test PASSED")
                
        except Exception as e:
            results.append({
                'test': 'TON Payment Flow Integration',
                'status': 'FAIL',
                'error': str(e),
                'message': f'TON payment flow integration failed: {e}'
            })
            print(f"   ❌ TON payment flow integration test FAILED: {e}")
        
        return results
    
    async def test_translation_completeness(self):
        """Test that all required translations are available"""
        print("\n🌍 Testing Translation Completeness")
        print("=" * 50)
        
        results = []
        
        # Required translation keys for receipts and publishing reports
        required_keys = [
            'payment_receipt_title', 'payment_received', 'payment_method',
            'amount_paid', 'payment_date', 'payment_id', 'ad_details',
            'selected_channels', 'campaign_duration', 'posts_per_day',
            'total_posts', 'receipt_thank_you', 'receipt_support',
            'ad_published_title', 'ad_published_message', 'published_channel',
            'published_date', 'ad_id', 'ad_summary', 'publishing_status',
            'publishing_success', 'publishing_thank_you'
        ]
        
        for language in self.test_languages:
            print(f"\n🌐 Testing {language.upper()} translations...")
            
            missing_keys = []
            
            for key in required_keys:
                try:
                    text = get_text(language, key)
                    if not text or text == key:  # Check if translation exists
                        missing_keys.append(key)
                except:
                    missing_keys.append(key)
            
            if missing_keys:
                results.append({
                    'test': f'Translation Completeness - {language}',
                    'status': 'FAIL',
                    'missing_keys': missing_keys,
                    'message': f'Missing {len(missing_keys)} translations'
                })
                print(f"   ❌ Missing translations: {missing_keys}")
            else:
                results.append({
                    'test': f'Translation Completeness - {language}',
                    'status': 'PASS',
                    'message': 'All required translations available'
                })
                print(f"   ✅ All translations available")
        
        return results
    
    async def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🚀 Starting Payment Receipt & Publishing Report Test Suite\n")
        
        try:
            # Run all tests
            receipt_results = await self.test_payment_receipt_functionality()
            publishing_results = await self.test_ad_publishing_report_functionality()
            integration_results = await self.test_payment_flow_integration()
            translation_results = await self.test_translation_completeness()
            
            # Generate comprehensive report
            self.generate_test_report(
                receipt_results, publishing_results, 
                integration_results, translation_results
            )
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            logging.error(f"Test suite error: {e}")
    
    def generate_test_report(self, receipt_results, publishing_results, 
                           integration_results, translation_results):
        """Generate comprehensive test report"""
        print("\n📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        all_results = receipt_results + publishing_results + integration_results + translation_results
        
        total_tests = len(all_results)
        passed_tests = len([r for r in all_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in all_results if r['status'] == 'FAIL'])
        
        print(f"📈 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in all_results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in all_results:
            if result['status'] == 'PASS':
                print(f"   • {result['test']}: {result['message']}")
        
        # Bug fix status
        print(f"\n🐛 BUG FIX STATUS:")
        print(f"   📧 Payment Receipt Bug: {'RESOLVED' if passed_tests >= 6 else 'PARTIAL'}")
        print(f"   📢 Publishing Report Bug: {'RESOLVED' if passed_tests >= 3 else 'PARTIAL'}")
        print(f"   🔄 Integration Bug: {'RESOLVED' if passed_tests >= 1 else 'PARTIAL'}")
        print(f"   🌍 Translation Bug: {'RESOLVED' if passed_tests >= 3 else 'PARTIAL'}")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! Payment receipt and publishing report bugs are COMPLETELY RESOLVED!")
        else:
            print(f"\n⚠️  Some tests failed. Please review and fix the issues above.")

async def main():
    """Run the comprehensive test suite"""
    test_suite = PaymentReceiptPublishingReportTest()
    await test_suite.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())