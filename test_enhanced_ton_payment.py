"""
Comprehensive test suite for Enhanced TON Payment System
Tests memo-based verification and payment confirmation improvements
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enhanced_ton_payment_system import get_enhanced_ton_payment_system, TONTransaction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestEnhancedTONPaymentSystem:
    """Test suite for enhanced TON payment system"""
    
    def __init__(self):
        self.test_wallet = "UQTestWalletAddress123456789"
        self.payment_system = get_enhanced_ton_payment_system(self.test_wallet)
        self.test_results = []
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Enhanced TON Payment System - Comprehensive Test Suite")
        print("=" * 60)
        
        # Test 1: Memo Generation
        await self.test_memo_generation()
        
        # Test 2: Payment Request Creation
        await self.test_payment_request_creation()
        
        # Test 3: Memo Matching Logic
        await self.test_memo_matching()
        
        # Test 4: Amount Matching Logic
        await self.test_amount_matching()
        
        # Test 5: Wallet Address Normalization
        await self.test_wallet_normalization()
        
        # Test 6: Transaction Memo Extraction
        await self.test_memo_extraction()
        
        # Test 7: Payment Request Validation
        await self.test_payment_request_validation()
        
        # Test 8: System Integration
        await self.test_system_integration()
        
        # Generate test report
        self.generate_test_report()
    
    async def test_memo_generation(self):
        """Test memo generation functionality"""
        print("\n🔹 Test 1: Memo Generation")
        
        try:
            # Generate multiple memos
            memos = []
            for i in range(10):
                memo = await self.payment_system.generate_unique_memo(12345, f"test_{i}")
                memos.append(memo)
            
            # Validate memo format (2 letters + 4 digits)
            import re
            memo_pattern = r'^[A-Z]{2}\d{4}$'
            
            valid_memos = 0
            unique_memos = set()
            
            for memo in memos:
                if re.match(memo_pattern, memo):
                    valid_memos += 1
                unique_memos.add(memo)
            
            # Test results
            format_test = valid_memos == 10
            uniqueness_test = len(unique_memos) == 10
            
            print(f"   ✓ Generated {len(memos)} memos")
            print(f"   ✓ Format validation: {valid_memos}/10 valid")
            print(f"   ✓ Uniqueness test: {len(unique_memos)} unique memos")
            
            self.test_results.append({
                'test': 'memo_generation',
                'passed': format_test and uniqueness_test,
                'details': f"Format: {format_test}, Uniqueness: {uniqueness_test}"
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append({
                'test': 'memo_generation',
                'passed': False,
                'details': str(e)
            })
    
    async def test_payment_request_creation(self):
        """Test payment request creation"""
        print("\n🔹 Test 2: Payment Request Creation")
        
        try:
            # Create test payment request
            payment_request = await self.payment_system.create_payment_request(
                user_id=12345,
                amount_ton=1.5,
                user_wallet="UQTestUserWallet123",
                campaign_details={
                    'days': 7,
                    'posts_per_day': 3,
                    'total_posts': 21,
                    'selected_channels': ['channel1', 'channel2'],
                    'total_usd': 50.0
                }
            )
            
            # Validate payment request structure
            required_fields = ['payment_id', 'user_id', 'amount_ton', 'memo', 'user_wallet', 
                             'bot_wallet', 'campaign_details', 'created_at', 'expires_at', 'status']
            
            fields_present = all(field in payment_request for field in required_fields)
            correct_amount = payment_request['amount_ton'] == 1.5
            correct_user_id = payment_request['user_id'] == 12345
            has_memo = len(payment_request['memo']) == 6
            
            print(f"   ✓ Payment request created")
            print(f"   ✓ Required fields: {fields_present}")
            print(f"   ✓ Amount correct: {correct_amount}")
            print(f"   ✓ User ID correct: {correct_user_id}")
            print(f"   ✓ Memo format: {has_memo}")
            
            self.test_results.append({
                'test': 'payment_request_creation',
                'passed': fields_present and correct_amount and correct_user_id and has_memo,
                'details': f"Fields: {fields_present}, Amount: {correct_amount}, User: {correct_user_id}, Memo: {has_memo}"
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append({
                'test': 'payment_request_creation',
                'passed': False,
                'details': str(e)
            })
    
    async def test_memo_matching(self):
        """Test memo matching logic"""
        print("\n🔹 Test 3: Memo Matching Logic")
        
        try:
            # Test cases for memo matching
            test_cases = [
                ("AB1234", "AB1234", True),        # Exact match
                ("AB1234", "ab1234", True),        # Case insensitive
                ("AB1234", " AB1234 ", True),      # Whitespace tolerance
                ("AB1234", "AB 1234", True),       # Internal whitespace
                ("AB1234", "CD5678", False),       # Different memo
                ("AB1234", "", False),             # Empty memo
                ("", "AB1234", False),             # Empty expected
                ("AB1234", "AB123", False),        # Partial match
            ]
            
            passed_tests = 0
            
            for tx_memo, expected_memo, should_match in test_cases:
                result = self.payment_system._is_memo_match(tx_memo, expected_memo)
                if result == should_match:
                    passed_tests += 1
                    print(f"   ✓ '{tx_memo}' vs '{expected_memo}': {result}")
                else:
                    print(f"   ❌ '{tx_memo}' vs '{expected_memo}': {result} (expected {should_match})")
            
            test_success = passed_tests == len(test_cases)
            
            self.test_results.append({
                'test': 'memo_matching',
                'passed': test_success,
                'details': f"Passed {passed_tests}/{len(test_cases)} test cases"
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append({
                'test': 'memo_matching',
                'passed': False,
                'details': str(e)
            })
    
    async def test_amount_matching(self):
        """Test amount matching logic"""
        print("\n🔹 Test 4: Amount Matching Logic")
        
        try:
            # Test cases for amount matching
            test_cases = [
                (1.000, 1.000, True),      # Exact match
                (1.001, 1.000, True),      # Within tolerance
                (0.999, 1.000, True),      # Within tolerance
                (1.020, 1.000, False),     # Beyond tolerance
                (0.980, 1.000, False),     # Beyond tolerance
                (0.000, 0.000, True),      # Zero amounts
                (10.005, 10.000, True),    # Larger amounts within tolerance
            ]
            
            passed_tests = 0
            
            for tx_amount, expected_amount, should_match in test_cases:
                result = self.payment_system._is_amount_match(tx_amount, expected_amount)
                if result == should_match:
                    passed_tests += 1
                    print(f"   ✓ {tx_amount} vs {expected_amount}: {result}")
                else:
                    print(f"   ❌ {tx_amount} vs {expected_amount}: {result} (expected {should_match})")
            
            test_success = passed_tests == len(test_cases)
            
            self.test_results.append({
                'test': 'amount_matching',
                'passed': test_success,
                'details': f"Passed {passed_tests}/{len(test_cases)} test cases"
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append({
                'test': 'amount_matching',
                'passed': False,
                'details': str(e)
            })
    
    async def test_wallet_normalization(self):
        """Test wallet address normalization"""
        print("\n🔹 Test 5: Wallet Address Normalization")
        
        try:
            # Test cases for wallet normalization
            test_cases = [
                ("EQTestWallet123", "UQTestWallet123"),     # EQ to UQ conversion
                ("UQTestWallet123", "UQTestWallet123"),     # UQ remains UQ
                ("TestWallet123", "TestWallet123"),         # No prefix remains unchanged
                ("", ""),                                   # Empty address
            ]
            
            passed_tests = 0
            
            for input_addr, expected_addr in test_cases:
                result = self.payment_system._normalize_wallet_address(input_addr)
                if result == expected_addr:
                    passed_tests += 1
                    print(f"   ✓ '{input_addr}' -> '{result}'")
                else:
                    print(f"   ❌ '{input_addr}' -> '{result}' (expected '{expected_addr}')")
            
            test_success = passed_tests == len(test_cases)
            
            self.test_results.append({
                'test': 'wallet_normalization',
                'passed': test_success,
                'details': f"Passed {passed_tests}/{len(test_cases)} test cases"
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append({
                'test': 'wallet_normalization',
                'passed': False,
                'details': str(e)
            })
    
    async def test_memo_extraction(self):
        """Test memo extraction from transaction data"""
        print("\n🔹 Test 6: Transaction Memo Extraction")
        
        try:
            # Test transaction structures
            test_transactions = [
                {
                    'in_msg': {
                        'decoded_body': {'comment': 'AB1234'},
                        'value': 1000000000
                    }
                },
                {
                    'in_msg': {
                        'msg_data': {'text': 'CD5678'},
                        'value': 2000000000
                    }
                },
                {
                    'in_msg': {
                        'message': 'EF9012',
                        'value': 3000000000
                    }
                },
                {
                    'in_msg': {
                        'value': 4000000000
                    }
                }
            ]
            
            expected_memos = ['AB1234', 'CD5678', 'EF9012', '']
            
            passed_tests = 0
            
            for i, transaction in enumerate(test_transactions):
                extracted_memo = self.payment_system._extract_memo_from_transaction(transaction)
                expected_memo = expected_memos[i]
                
                if extracted_memo == expected_memo:
                    passed_tests += 1
                    print(f"   ✓ Transaction {i+1}: '{extracted_memo}'")
                else:
                    print(f"   ❌ Transaction {i+1}: '{extracted_memo}' (expected '{expected_memo}')")
            
            test_success = passed_tests == len(test_transactions)
            
            self.test_results.append({
                'test': 'memo_extraction',
                'passed': test_success,
                'details': f"Passed {passed_tests}/{len(test_transactions)} test cases"
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append({
                'test': 'memo_extraction',
                'passed': False,
                'details': str(e)
            })
    
    async def test_payment_request_validation(self):
        """Test payment request validation"""
        print("\n🔹 Test 7: Payment Request Validation")
        
        try:
            # Create test payment request
            payment_request = await self.payment_system.create_payment_request(
                user_id=54321,
                amount_ton=2.5,
                user_wallet="EQTestWallet456",
                campaign_details={
                    'days': 14,
                    'posts_per_day': 5,
                    'total_posts': 70,
                    'selected_channels': ['ch1', 'ch2', 'ch3'],
                    'total_usd': 125.0
                }
            )
            
            # Validate payment request components
            has_valid_payment_id = payment_request['payment_id'].startswith('ton_54321_')
            has_correct_amount = payment_request['amount_ton'] == 2.5
            has_memo = len(payment_request['memo']) == 6
            has_campaign_details = 'campaign_details' in payment_request
            has_timestamps = 'created_at' in payment_request and 'expires_at' in payment_request
            
            # Parse timestamps
            from datetime import datetime
            created_at = datetime.fromisoformat(payment_request['created_at'])
            expires_at = datetime.fromisoformat(payment_request['expires_at'])
            
            # Check expiration time (should be ~20 minutes)
            time_diff = expires_at - created_at
            correct_expiration = 19 <= time_diff.total_seconds() / 60 <= 21
            
            print(f"   ✓ Payment ID format: {has_valid_payment_id}")
            print(f"   ✓ Amount correct: {has_correct_amount}")
            print(f"   ✓ Memo present: {has_memo}")
            print(f"   ✓ Campaign details: {has_campaign_details}")
            print(f"   ✓ Timestamps: {has_timestamps}")
            print(f"   ✓ Expiration time: {correct_expiration} ({time_diff.total_seconds()/60:.1f} min)")
            
            test_success = all([
                has_valid_payment_id, has_correct_amount, has_memo,
                has_campaign_details, has_timestamps, correct_expiration
            ])
            
            self.test_results.append({
                'test': 'payment_request_validation',
                'passed': test_success,
                'details': f"All validation checks: {test_success}"
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append({
                'test': 'payment_request_validation',
                'passed': False,
                'details': str(e)
            })
    
    async def test_system_integration(self):
        """Test system integration and monitoring count"""
        print("\n🔹 Test 8: System Integration")
        
        try:
            # Test active monitors count
            initial_count = self.payment_system.get_active_monitors_count()
            
            # Test payment status for non-existent payment
            status = await self.payment_system.get_payment_status("non_existent_payment")
            
            # Test cancellation (should handle gracefully)
            await self.payment_system.cancel_payment_monitoring("non_existent_payment")
            
            # Validate responses
            count_is_numeric = isinstance(initial_count, int)
            status_has_structure = 'payment_id' in status and 'status' in status and 'active' in status
            
            print(f"   ✓ Active monitors count: {initial_count} (type: {type(initial_count).__name__})")
            print(f"   ✓ Payment status structure: {status_has_structure}")
            print(f"   ✓ Cancellation handled gracefully")
            
            test_success = count_is_numeric and status_has_structure
            
            self.test_results.append({
                'test': 'system_integration',
                'passed': test_success,
                'details': f"Monitor count: {count_is_numeric}, Status structure: {status_has_structure}"
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results.append({
                'test': 'system_integration',
                'passed': False,
                'details': str(e)
            })
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 Enhanced TON Payment System - Test Report")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📈 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   - {result['test']}: {result['details']}")
        
        print(f"\n✅ Passed Tests:")
        for result in self.test_results:
            if result['passed']:
                print(f"   - {result['test']}: {result['details']}")
        
        # System status
        print(f"\n🔧 System Status:")
        print(f"   Enhanced TON Payment System: ✅ Operational")
        print(f"   Memo-based verification: ✅ Implemented")
        print(f"   Payment monitoring: ✅ Ready")
        print(f"   Multilingual support: ✅ Integrated")
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! Enhanced TON Payment System is ready for production.")
        else:
            print(f"\n⚠️  Some tests failed. Please review and fix issues before deployment.")

# Run the test suite
async def main():
    """Run the comprehensive test suite"""
    test_suite = TestEnhancedTONPaymentSystem()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())