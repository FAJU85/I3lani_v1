#!/usr/bin/env python3
"""
Payment Amount Validator - Protocol Enforcement System
Handles incorrect payment amounts with proper validation and user messaging
"""

import logging
from typing import Dict, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
import sqlite3
import json
from datetime import datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from languages import get_text
from global_sequence_system import get_global_sequence_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentAmountValidator:
    """Validates payment amounts and handles incorrect payments"""
    
    def __init__(self, bot: Bot, db_path: str = "bot.db"):
        self.bot = bot
        self.db_path = db_path
        self.tolerance = Decimal('0.01')  # 0.01 TON tolerance for comparison
        
    def validate_payment_amount(self, received_amount: float, expected_amount: float, memo: str) -> Dict:
        """
        Validate payment amount against expected amount
        Returns: {
            'valid': bool,
            'status': str,  # 'exact', 'underpayment', 'overpayment'
            'difference': float,
            'action': str,  # 'confirm', 'reject', 'manual_review'
            'reason': str
        }
        """
        try:
            # Convert to Decimal for precise comparison
            received = Decimal(str(received_amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            expected = Decimal(str(expected_amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            difference = received - expected
            
            logger.info(f"💰 Payment amount validation for memo {memo}")
            logger.info(f"   Expected: {expected} TON")
            logger.info(f"   Received: {received} TON")
            logger.info(f"   Difference: {difference} TON")
            
            # Exact amount (within tolerance)
            if abs(difference) <= self.tolerance:
                return {
                    'valid': True,
                    'status': 'exact',
                    'difference': float(difference),
                    'action': 'confirm',
                    'reason': 'Payment amount matches expected amount'
                }
            
            # Underpayment - Less than required
            elif difference < 0:
                return {
                    'valid': False,
                    'status': 'underpayment',
                    'difference': float(difference),
                    'action': 'reject',
                    'reason': f'Payment is {abs(difference)} TON less than required'
                }
            
            # Overpayment - More than required
            else:
                return {
                    'valid': False,
                    'status': 'overpayment',
                    'difference': float(difference),
                    'action': 'manual_review',
                    'reason': f'Payment is {difference} TON more than required'
                }
                
        except Exception as e:
            logger.error(f"❌ Error validating payment amount: {e}")
            return {
                'valid': False,
                'status': 'error',
                'difference': 0.0,
                'action': 'reject',
                'reason': f'Validation error: {str(e)}'
            }
    
    async def handle_invalid_payment(self, user_id: int, memo: str, validation_result: Dict, 
                                   received_amount: float, expected_amount: float) -> bool:
        """Handle invalid payment amounts with appropriate user messaging"""
        try:
            # Get user language
            user_language = await self._get_user_language(user_id)
            
            # Log the invalid payment for audit
            await self._log_invalid_payment(user_id, memo, validation_result, received_amount, expected_amount)
            
            if validation_result['status'] == 'underpayment':
                await self._handle_underpayment(user_id, memo, validation_result, received_amount, expected_amount, user_language)
            elif validation_result['status'] == 'overpayment':
                await self._handle_overpayment(user_id, memo, validation_result, received_amount, expected_amount, user_language)
            else:
                await self._handle_error_payment(user_id, memo, validation_result, user_language)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling invalid payment: {e}")
            return False
    
    async def _handle_underpayment(self, user_id: int, memo: str, validation_result: Dict,
                                 received_amount: float, expected_amount: float, language: str):
        """Handle underpayment scenario - payment is less than required"""
        try:
            shortage = abs(validation_result['difference'])
            
            # Create multilingual message
            if language == 'ar':
                message_text = f"""⚠️ **مبلغ الدفع أقل من المطلوب**

💰 **المبلغ المستلم:** {received_amount} TON
💰 **المبلغ المطلوب:** {expected_amount} TON
❌ **النقص:** {shortage} TON

🔄 **الإجراء المطلوب:**
يرجى إرسال المبلغ الكامل المطلوب لإتمام الحملة الإعلانية.

📋 **رمز الدفع:** {memo}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **تحتاج مساعدة؟** اتصل بالدعم الفني."""

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💳 دفع المبلغ الكامل", callback_data=f"retry_payment_{memo}")],
                    [InlineKeyboardButton(text="💬 اتصل بالدعم", callback_data="contact_support")],
                    [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")]
                ])
                
            elif language == 'ru':
                message_text = f"""⚠️ **Сумма платежа меньше требуемой**

💰 **Получено:** {received_amount} TON
💰 **Требуется:** {expected_amount} TON
❌ **Недостаток:** {shortage} TON

🔄 **Необходимое действие:**
Пожалуйста, отправьте полную требуемую сумму для завершения рекламной кампании.

📋 **Код платежа:** {memo}
⏰ **Время:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **Нужна помощь?** Свяжитесь с поддержкой."""

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💳 Оплатить полную сумму", callback_data=f"retry_payment_{memo}")],
                    [InlineKeyboardButton(text="💬 Связаться с поддержкой", callback_data="contact_support")],
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
                
            else:  # English
                message_text = f"""⚠️ **Payment Amount is Less Than Required**

💰 **Amount Received:** {received_amount} TON
💰 **Amount Required:** {expected_amount} TON
❌ **Shortage:** {shortage} TON

🔄 **Required Action:**
Please send the full required amount to proceed with your advertising campaign.

📋 **Payment Code:** {memo}
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **Need Help?** Contact support."""

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💳 Pay Full Amount", callback_data=f"retry_payment_{memo}")],
                    [InlineKeyboardButton(text="💬 Contact Support", callback_data="contact_support")],
                    [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
                ])
            
            # Send message to user
            await self.bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            logger.info(f"📩 Underpayment notification sent to user {user_id} for memo {memo}")
            
        except Exception as e:
            logger.error(f"❌ Error handling underpayment: {e}")
    
    async def _handle_overpayment(self, user_id: int, memo: str, validation_result: Dict,
                                received_amount: float, expected_amount: float, language: str):
        """Handle overpayment scenario - payment is more than required"""
        try:
            excess = validation_result['difference']
            
            # Create multilingual message
            if language == 'ar':
                message_text = f"""⚠️ **مبلغ الدفع أكثر من المطلوب**

💰 **المبلغ المستلم:** {received_amount} TON
💰 **المبلغ المطلوب:** {expected_amount} TON
➕ **الزيادة:** {excess} TON

🔄 **الإجراء المطلوب:**
تم استلام مبلغ أكبر من المطلوب. يرجى التواصل مع الدعم أو تأكيد رغبتك في المتابعة.

📋 **رمز الدفع:** {memo}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **تحتاج مساعدة؟** اتصل بالدعم الفني."""

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ متابعة بالمبلغ الزائد", callback_data=f"confirm_overpayment_{memo}")],
                    [InlineKeyboardButton(text="💬 اتصل بالدعم", callback_data="contact_support")],
                    [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")]
                ])
                
            elif language == 'ru':
                message_text = f"""⚠️ **Сумма платежа больше требуемой**

💰 **Получено:** {received_amount} TON
💰 **Требуется:** {expected_amount} TON
➕ **Избыток:** {excess} TON

🔄 **Необходимое действие:**
Получена сумма больше требуемой. Пожалуйста, свяжитесь с поддержкой или подтвердите желание продолжить.

📋 **Код платежа:** {memo}
⏰ **Время:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **Нужна помощь?** Свяжитесь с поддержкой."""

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Продолжить с избытком", callback_data=f"confirm_overpayment_{memo}")],
                    [InlineKeyboardButton(text="💬 Связаться с поддержкой", callback_data="contact_support")],
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
                
            else:  # English
                message_text = f"""⚠️ **Payment Amount is More Than Required**

💰 **Amount Received:** {received_amount} TON
💰 **Amount Required:** {expected_amount} TON
➕ **Excess:** {excess} TON

🔄 **Required Action:**
A higher amount than required was received. Please contact support or confirm if you want to proceed.

📋 **Payment Code:** {memo}
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **Need Help?** Contact support."""

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Proceed with Excess", callback_data=f"confirm_overpayment_{memo}")],
                    [InlineKeyboardButton(text="💬 Contact Support", callback_data="contact_support")],
                    [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
                ])
            
            # Send message to user
            await self.bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            logger.info(f"📩 Overpayment notification sent to user {user_id} for memo {memo}")
            
        except Exception as e:
            logger.error(f"❌ Error handling overpayment: {e}")
    
    async def _handle_error_payment(self, user_id: int, memo: str, validation_result: Dict, language: str):
        """Handle payment validation errors"""
        try:
            # Create multilingual error message
            if language == 'ar':
                message_text = f"""❌ **خطأ في التحقق من الدفع**

🔍 **السبب:** {validation_result['reason']}
📋 **رمز الدفع:** {memo}
⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **يرجى التواصل مع الدعم الفني لحل هذه المشكلة.**"""
                
            elif language == 'ru':
                message_text = f"""❌ **Ошибка проверки платежа**

🔍 **Причина:** {validation_result['reason']}
📋 **Код платежа:** {memo}
⏰ **Время:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **Пожалуйста, свяжитесь с поддержкой для решения этой проблемы.**"""
                
            else:  # English
                message_text = f"""❌ **Payment Validation Error**

🔍 **Reason:** {validation_result['reason']}
📋 **Payment Code:** {memo}
⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **Please contact support to resolve this issue.**"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💬 Contact Support", callback_data="contact_support")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
            
            # Send message to user
            await self.bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            logger.info(f"📩 Error notification sent to user {user_id} for memo {memo}")
            
        except Exception as e:
            logger.error(f"❌ Error handling payment error: {e}")
    
    async def _log_invalid_payment(self, user_id: int, memo: str, validation_result: Dict,
                                 received_amount: float, expected_amount: float):
        """Log invalid payment for audit purposes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create payment_validation_log table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_validation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    memo TEXT NOT NULL,
                    expected_amount REAL NOT NULL,
                    received_amount REAL NOT NULL,
                    difference REAL NOT NULL,
                    status TEXT NOT NULL,
                    action TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert log entry
            cursor.execute("""
                INSERT INTO payment_validation_log (
                    user_id, memo, expected_amount, received_amount, difference, 
                    status, action, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, memo, expected_amount, received_amount, 
                validation_result['difference'], validation_result['status'],
                validation_result['action'], validation_result['reason']
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📝 Invalid payment logged for audit: {memo}")
            
        except Exception as e:
            logger.error(f"❌ Error logging invalid payment: {e}")
    
    async def _get_user_language(self, user_id: int) -> str:
        """Get user's preferred language"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 'en'
            
        except Exception as e:
            logger.error(f"❌ Error getting user language: {e}")
            return 'en'
    
    async def get_expected_payment_amount(self, user_id: int, memo: str) -> Optional[float]:
        """Get expected payment amount for memo from tracking system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT amount FROM payment_memo_tracking 
                WHERE user_id = ? AND memo = ? AND status = 'pending'
            """, (user_id, memo))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Error getting expected payment amount: {e}")
            return None

# Global instance
payment_amount_validator = None

def get_payment_amount_validator(bot: Bot) -> PaymentAmountValidator:
    """Get or create payment amount validator instance"""
    global payment_amount_validator
    if payment_amount_validator is None:
        payment_amount_validator = PaymentAmountValidator(bot)
    return payment_amount_validator

async def validate_payment_amount(bot: Bot, user_id: int, memo: str, 
                                received_amount: float, expected_amount: float) -> Dict:
    """Validate payment amount - main entry point"""
    validator = get_payment_amount_validator(bot)
    return validator.validate_payment_amount(received_amount, expected_amount, memo)

async def handle_invalid_payment_amount(bot: Bot, user_id: int, memo: str, 
                                      validation_result: Dict, received_amount: float, 
                                      expected_amount: float) -> bool:
    """Handle invalid payment amount - main entry point"""
    validator = get_payment_amount_validator(bot)
    return await validator.handle_invalid_payment(
        user_id, memo, validation_result, received_amount, expected_amount
    )

if __name__ == "__main__":
    print("🔧 Payment Amount Validator - Protocol Enforcement System")
    print("Handles incorrect payment amounts with proper validation and messaging")