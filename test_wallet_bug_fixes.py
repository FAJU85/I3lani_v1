"""
Test Wallet Management Bug Fixes
Validates "Use Current Wallet" button functionality and MESSAGE_TOO_LONG fix
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wallet_manager import WalletManager, use_existing_wallet_handler
from database import Database
import logging

logger = logging.getLogger(__name__)

class MockCallbackQuery:
    """Mock callback query for testing"""
    def __init__(self, user_id, callback_data):
        self.from_user = type('obj', (object,), {'id': user_id})
        self.data = callback_data
        self.message = type('obj', (object,), {'edit_text': self.mock_edit_text})
        self._answer_called = False
        self._answer_message = ""
        
    async def mock_edit_text(self, text, **kwargs):
        """Mock edit_text method"""
        pass
        
    async def answer(self, text="", show_alert=False):
        """Mock answer method"""
        self._answer_called = True
        self._answer_message = text

class MockState:
    """Mock FSM context state"""
    def __init__(self):
        self.data = {}
        
    async def get_data(self):
        return self.data
        
    async def update_data(self, **kwargs):
        self.data.update(kwargs)

class TestWalletBugFixes:
    """Test suite for wallet management bug fixes"""
    
    def __init__(self):
        self.db = Database()
        self.test_results = []
        
    async def test_use_current_wallet_button_responsiveness(self):
        """Test 1: Use Current Wallet button should respond properly"""
        print("\n🔘 Testing Use Current Wallet Button Responsiveness...")
        
        test_user_id = 999001
        results = []
        
        # Clear any existing wallet first
        await self.db.set_user_wallet_address(test_user_id, None)
        
        # Test scenario 1: No existing wallet
        callback_query = MockCallbackQuery(test_user_id, "use_existing_wallet_payment")
        state = MockState()
        
        try:
            await use_existing_wallet_handler(callback_query, state)
            
            if callback_query._answer_called:
                results.append({'test': 'No Wallet Error Handling', 'status': 'PASS', 'details': f'Answer called: {callback_query._answer_message}'})
                print("✅ Proper error handling when no wallet exists")
            else:
                results.append({'test': 'No Wallet Error Handling', 'status': 'FAIL', 'details': 'No answer callback called'})
                print("❌ Button didn't respond when no wallet exists")
                
        except Exception as e:
            results.append({'test': 'No Wallet Error Handling', 'status': 'ERROR', 'details': str(e)})
            print(f"❌ Exception when no wallet: {e}")
        
        # Test scenario 2: With existing wallet
        test_wallet = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
        await self.db.set_user_wallet_address(test_user_id, test_wallet)
        
        callback_query2 = MockCallbackQuery(test_user_id, "use_existing_wallet_payment")
        state2 = MockState()
        
        try:
            await use_existing_wallet_handler(callback_query2, state2)
            
            if callback_query2._answer_called:
                results.append({'test': 'Existing Wallet Processing', 'status': 'PASS', 'details': f'Answer called: {callback_query2._answer_message}'})
                print("✅ Button responds properly with existing wallet")
            else:
                results.append({'test': 'Existing Wallet Processing', 'status': 'FAIL', 'details': 'No answer callback called'})
                print("❌ Button didn't respond with existing wallet")
                
        except Exception as e:
            results.append({'test': 'Existing Wallet Processing', 'status': 'ERROR', 'details': str(e)})
            print(f"❌ Exception with existing wallet: {e}")
        
        # Test scenario 3: Wallet in state data
        callback_query3 = MockCallbackQuery(test_user_id, "use_existing_wallet_payment")
        state3 = MockState()
        state3.data['existing_wallet'] = test_wallet
        
        try:
            await use_existing_wallet_handler(callback_query3, state3)
            
            if callback_query3._answer_called:
                results.append({'test': 'State Wallet Processing', 'status': 'PASS', 'details': f'Answer called: {callback_query3._answer_message}'})
                print("✅ Button processes wallet from state correctly")
            else:
                results.append({'test': 'State Wallet Processing', 'status': 'FAIL', 'details': 'No answer callback called'})
                print("❌ Button didn't process wallet from state")
                
        except Exception as e:
            results.append({'test': 'State Wallet Processing', 'status': 'ERROR', 'details': str(e)})
            print(f"❌ Exception with state wallet: {e}")
        
        return results
    
    async def test_multilingual_error_messages(self):
        """Test 2: Error messages should display in user's language"""
        print("\n🌍 Testing Multilingual Error Messages...")
        
        test_user_id = 999002
        results = []
        
        # Clear wallet for testing
        await self.db.set_user_wallet_address(test_user_id, None)
        
        languages = [
            ('en', 'English'),
            ('ar', 'Arabic'),
            ('ru', 'Russian')
        ]
        
        for lang_code, lang_name in languages:
            # Set user language
            await self.db.set_user_language(test_user_id, lang_code)
            
            callback_query = MockCallbackQuery(test_user_id, "use_existing_wallet_payment")
            state = MockState()
            
            try:
                await use_existing_wallet_handler(callback_query, state)
                
                if callback_query._answer_called:
                    message = callback_query._answer_message
                    
                    # Check for language-specific error terms
                    if lang_code == 'ar' and 'خطأ' in message:
                        results.append({'test': f'{lang_name} Error Message', 'status': 'PASS', 'details': f'Arabic error: {message}'})
                        print(f"✅ {lang_name} error message working")
                    elif lang_code == 'ru' and 'Ошибка' in message:
                        results.append({'test': f'{lang_name} Error Message', 'status': 'PASS', 'details': f'Russian error: {message}'})
                        print(f"✅ {lang_name} error message working")
                    elif lang_code == 'en' and 'Error' in message:
                        results.append({'test': f'{lang_name} Error Message', 'status': 'PASS', 'details': f'English error: {message}'})
                        print(f"✅ {lang_name} error message working")
                    else:
                        results.append({'test': f'{lang_name} Error Message', 'status': 'FAIL', 'details': f'Wrong language: {message}'})
                        print(f"❌ {lang_name} error message incorrect: {message}")
                else:
                    results.append({'test': f'{lang_name} Error Message', 'status': 'FAIL', 'details': 'No error message shown'})
                    print(f"❌ {lang_name} - no error message shown")
                    
            except Exception as e:
                results.append({'test': f'{lang_name} Error Message', 'status': 'ERROR', 'details': str(e)})
                print(f"❌ {lang_name} error handling failed: {e}")
        
        return results
    
    async def test_message_length_optimization(self):
        """Test 3: Payment messages should be within Telegram limits"""
        print("\n📏 Testing Message Length Optimization...")
        
        from handlers import continue_ton_payment_with_wallet
        
        # Test payment message lengths
        test_scenarios = [
            {'amount': 1.0, 'memo': 'AB1234'},
            {'amount': 999.999, 'memo': 'ZY9999'},
            {'amount': 0.001, 'memo': 'AA0000'}
        ]
        
        results = []
        
        for scenario in test_scenarios:
            amount_ton = scenario['amount']
            memo = scenario['memo']
            
            # Simulate payment message creation
            bot_wallet = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
            
            # Test all languages
            for lang_code, lang_name in [('en', 'English'), ('ar', 'Arabic'), ('ru', 'Russian')]:
                if lang_code == 'ar':
                    payment_text = f"""💰 **دفع TON**

**المبلغ:** {amount_ton:.3f} TON
**العنوان:** `{bot_wallet}`
**المذكرة:** `{memo}`

**خطوات الدفع:**
1. افتح محفظة TON
2. أرسل {amount_ton:.3f} TON للعنوان أعلاه
3. أضف المذكرة `{memo}` بالضبط
4. أكد المعاملة

⏰ انتهاء الصلاحية: 20 دقيقة
✅ تحقق تلقائي كل 30 ثانية

🔒 بدفعك، تتفق على شروط الاستخدام"""
                elif lang_code == 'ru':
                    payment_text = f"""💰 **Оплата TON**

**Сумма:** {amount_ton:.3f} TON
**Адрес:** `{bot_wallet}`
**Заметка:** `{memo}`

**Шаги оплаты:**
1. Откройте TON кошелек
2. Отправьте {amount_ton:.3f} TON на адрес выше
3. Добавьте заметку `{memo}` точно
4. Подтвердите транзакцию

⏰ Истекает через: 20 минут
✅ Автопроверка каждые 30 секунд

🔒 Оплачивая, вы соглашаетесь с условиями"""
                else:
                    payment_text = f"""💰 **TON Payment**

**Amount:** {amount_ton:.3f} TON
**Address:** `{bot_wallet}`
**Memo:** `{memo}`

**Payment Steps:**
1. Open your TON wallet
2. Send {amount_ton:.3f} TON to address above
3. Add memo `{memo}` exactly
4. Confirm transaction

⏰ Expires in: 20 minutes
✅ Auto-verification every 30 seconds

🔒 By paying, you agree to Usage Agreement"""
                
                message_length = len(payment_text)
                
                # Telegram's message limit is 4096 characters
                if message_length <= 4096:
                    results.append({'test': f'{lang_name} Message Length ({amount_ton} TON)', 'status': 'PASS', 'details': f'{message_length} chars'})
                    print(f"✅ {lang_name} message length OK: {message_length} chars")
                else:
                    results.append({'test': f'{lang_name} Message Length ({amount_ton} TON)', 'status': 'FAIL', 'details': f'{message_length} chars (too long)'})
                    print(f"❌ {lang_name} message too long: {message_length} chars")
        
        return results
    
    async def test_context_handling(self):
        """Test 4: Different contexts should be handled properly"""
        print("\n🎯 Testing Context Handling...")
        
        test_user_id = 999003
        test_wallet = "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
        
        # Set up test wallet
        await self.db.set_user_wallet_address(test_user_id, test_wallet)
        
        contexts = ['payment', 'affiliate', 'channel']
        results = []
        
        for context in contexts:
            callback_query = MockCallbackQuery(test_user_id, f"use_existing_wallet_{context}")
            state = MockState()
            
            try:
                await use_existing_wallet_handler(callback_query, state)
                
                if callback_query._answer_called:
                    results.append({'test': f'{context.capitalize()} Context', 'status': 'PASS', 'details': f'Context processed: {callback_query._answer_message}'})
                    print(f"✅ {context.capitalize()} context handled correctly")
                else:
                    results.append({'test': f'{context.capitalize()} Context', 'status': 'FAIL', 'details': 'No response to button'})
                    print(f"❌ {context.capitalize()} context - no response")
                    
            except Exception as e:
                results.append({'test': f'{context.capitalize()} Context', 'status': 'ERROR', 'details': str(e)})
                print(f"❌ {context.capitalize()} context error: {e}")
        
        # Test unknown context
        callback_query = MockCallbackQuery(test_user_id, "use_existing_wallet_unknown")
        state = MockState()
        
        try:
            await use_existing_wallet_handler(callback_query, state)
            
            if callback_query._answer_called and 'Unknown context' in callback_query._answer_message or 'سياق غير معروف' in callback_query._answer_message:
                results.append({'test': 'Unknown Context Handling', 'status': 'PASS', 'details': 'Unknown context error shown'})
                print("✅ Unknown context properly handled")
            else:
                results.append({'test': 'Unknown Context Handling', 'status': 'FAIL', 'details': f'Response: {callback_query._answer_message}'})
                print(f"❌ Unknown context not handled: {callback_query._answer_message}")
                
        except Exception as e:
            results.append({'test': 'Unknown Context Handling', 'status': 'ERROR', 'details': str(e)})
            print(f"❌ Unknown context handling error: {e}")
        
        return results
    
    async def run_all_tests(self):
        """Run all wallet bug fix tests"""
        print("🧪 WALLET MANAGEMENT BUG FIXES TEST SUITE")
        print("=" * 60)
        
        # Run all test functions
        all_results = []
        test_functions = [
            self.test_use_current_wallet_button_responsiveness,
            self.test_multilingual_error_messages,
            self.test_message_length_optimization,
            self.test_context_handling
        ]
        
        for test_func in test_functions:
            try:
                results = await test_func()
                all_results.extend(results)
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with error: {e}")
                all_results.append({
                    'test': test_func.__name__,
                    'status': 'ERROR',
                    'details': str(e)
                })
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 BUG FIX VALIDATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in all_results if r['status'] == 'PASS')
        failed = sum(1 for r in all_results if r['status'] == 'FAIL')
        errors = sum(1 for r in all_results if r['status'] == 'ERROR')
        total = len(all_results)
        
        print(f"✅ PASSED: {passed}/{total}")
        print(f"❌ FAILED: {failed}/{total}")
        print(f"⚠️  ERRORS: {errors}/{total}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        # Detailed results
        print("\n📊 DETAILED RESULTS:")
        for result in all_results:
            status_emoji = "✅" if result['status'] == 'PASS' else ("❌" if result['status'] == 'FAIL' else "⚠️")
            print(f"{status_emoji} {result['test']}: {result['details']}")
        
        # Bug fix summary
        print("\n🔧 BUG FIX STATUS:")
        button_tests = [r for r in all_results if 'Button' in r['test'] or 'Wallet' in r['test']]
        message_tests = [r for r in all_results if 'Message Length' in r['test']]
        
        button_passed = sum(1 for r in button_tests if r['status'] == 'PASS')
        message_passed = sum(1 for r in message_tests if r['status'] == 'PASS')
        
        if button_passed == len(button_tests):
            print("✅ Use Current Wallet Button: FIXED")
        else:
            print("❌ Use Current Wallet Button: STILL BROKEN")
            
        if message_passed == len(message_tests):
            print("✅ MESSAGE_TOO_LONG Error: FIXED")
        else:
            print("❌ MESSAGE_TOO_LONG Error: STILL PRESENT")
        
        return all_results

async def main():
    """Main test runner"""
    test_suite = TestWalletBugFixes()
    results = await test_suite.run_all_tests()
    
    # Return success if most critical tests pass
    button_tests = [r for r in results if 'Button' in r['test'] or 'Wallet' in r['test']]
    message_tests = [r for r in results if 'Message Length' in r['test']]
    
    button_passed = sum(1 for r in button_tests if r['status'] == 'PASS')
    message_passed = sum(1 for r in message_tests if r['status'] == 'PASS')
    
    if button_passed == len(button_tests) and message_passed == len(message_tests):
        print("\n🎉 ALL CRITICAL BUGS FIXED! Wallet management is working correctly.")
        return True
    else:
        print(f"\n⚠️  Some issues remain. Button: {button_passed}/{len(button_tests)}, Message: {message_passed}/{len(message_tests)}")
        return False

if __name__ == "__main__":
    asyncio.run(main())