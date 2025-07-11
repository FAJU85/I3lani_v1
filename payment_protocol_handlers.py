#!/usr/bin/env python3
"""
Payment Protocol Handlers
Handles retry payment and confirm overpayment callbacks
"""

import logging
from typing import Dict, Optional

from aiogram import Bot, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from languages import get_text
from handlers import get_user_language

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(lambda c: c.data and c.data.startswith('retry_payment_'))
async def handle_retry_payment(callback_query: CallbackQuery, state: FSMContext):
    """Handle retry payment callback"""
    try:
        user_id = callback_query.from_user.id
        memo = callback_query.data.replace('retry_payment_', '')
        
        logger.info(f"🔄 Retry payment request from user {user_id} for memo {memo}")
        
        # Get user language
        user_language = await get_user_language(user_id)
        
        # Create retry payment message
        if user_language == 'ar':
            retry_text = f"""🔄 **إعادة محاولة الدفع**

📋 **رمز الدفع:** {memo}

يرجى إرسال المبلغ الكامل المطلوب لإتمام الحملة الإعلانية.

💡 **نصائح للدفع:**
• تأكد من إدخال المبلغ الصحيح
• استخدم نفس رمز الدفع: {memo}
• تحقق من رصيد محفظتك

🔄 **هل تريد إعادة بدء عملية الدفع؟**"""

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 إعادة بدء الدفع", callback_data=f"restart_payment_{memo}")],
                [InlineKeyboardButton(text="💬 اتصل بالدعم", callback_data="contact_support")],
                [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")]
            ])
            
        elif user_language == 'ru':
            retry_text = f"""🔄 **Повторная попытка платежа**

📋 **Код платежа:** {memo}

Пожалуйста, отправьте полную требуемую сумму для завершения рекламной кампании.

💡 **Советы по оплате:**
• Убедитесь, что вводите правильную сумму
• Используйте тот же код платежа: {memo}
• Проверьте баланс вашего кошелька

🔄 **Хотите начать процесс оплаты заново?**"""

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Начать платеж заново", callback_data=f"restart_payment_{memo}")],
                [InlineKeyboardButton(text="💬 Связаться с поддержкой", callback_data="contact_support")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
            
        else:  # English
            retry_text = f"""🔄 **Retry Payment**

📋 **Payment Code:** {memo}

Please send the full required amount to proceed with your advertising campaign.

💡 **Payment Tips:**
• Make sure you enter the correct amount
• Use the same payment code: {memo}
• Check your wallet balance

🔄 **Want to restart the payment process?**"""

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Restart Payment", callback_data=f"restart_payment_{memo}")],
                [InlineKeyboardButton(text="💬 Contact Support", callback_data="contact_support")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
        
        await callback_query.message.edit_text(
            text=retry_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        await callback_query.answer()
        logger.info(f"✅ Retry payment interface shown to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error handling retry payment: {e}")
        await callback_query.answer("Error processing retry payment request")

@router.callback_query(lambda c: c.data and c.data.startswith('confirm_overpayment_'))
async def handle_confirm_overpayment(callback_query: CallbackQuery, state: FSMContext):
    """Handle confirm overpayment callback"""
    try:
        user_id = callback_query.from_user.id
        memo = callback_query.data.replace('confirm_overpayment_', '')
        
        logger.info(f"✅ Overpayment confirmation from user {user_id} for memo {memo}")
        
        # Get user language
        user_language = await get_user_language(user_id)
        
        # Process overpayment confirmation
        try:
            # Find the payment details
            import sqlite3
            conn = sqlite3.connect("bot.db")
            cursor = conn.cursor()
            
            # Check for overpayment in validation log
            cursor.execute("""
                SELECT received_amount, expected_amount, difference 
                FROM payment_validation_log 
                WHERE user_id = ? AND memo = ? AND status = 'overpayment'
                ORDER BY created_at DESC LIMIT 1
            """, (user_id, memo))
            
            payment_data = cursor.fetchone()
            conn.close()
            
            if payment_data:
                received_amount, expected_amount, excess = payment_data
                
                # Create confirmation message
                if user_language == 'ar':
                    confirm_text = f"""✅ **تأكيد الدفع الزائد**

📋 **رمز الدفع:** {memo}
💰 **المبلغ المستلم:** {received_amount} TON
💰 **المبلغ المطلوب:** {expected_amount} TON
➕ **الزيادة:** {excess} TON

🎉 **تم تأكيد الدفع!**
سيتم إنشاء حملتك الإعلانية بالمبلغ الزائد.

⏱️ **الخطوات التالية:**
• إنشاء الحملة الإعلانية
• جدولة النشر التلقائي
• إرسال تأكيد الحملة

🙏 **شكراً لك على الدفع الإضافي!**"""
                    
                elif user_language == 'ru':
                    confirm_text = f"""✅ **Подтверждение переплаты**

📋 **Код платежа:** {memo}
💰 **Получено:** {received_amount} TON
💰 **Требовалось:** {expected_amount} TON
➕ **Избыток:** {excess} TON

🎉 **Платеж подтвержден!**
Ваша рекламная кампания будет создана с избыточной суммой.

⏱️ **Следующие шаги:**
• Создание рекламной кампании
• Планирование автоматической публикации
• Отправка подтверждения кампании

🙏 **Спасибо за дополнительный платеж!**"""
                    
                else:  # English
                    confirm_text = f"""✅ **Overpayment Confirmed**

📋 **Payment Code:** {memo}
💰 **Amount Received:** {received_amount} TON
💰 **Amount Required:** {expected_amount} TON
➕ **Excess:** {excess} TON

🎉 **Payment Confirmed!**
Your advertising campaign will be created with the excess amount.

⏱️ **Next Steps:**
• Create advertising campaign
• Schedule automatic publishing
• Send campaign confirmation

🙏 **Thank you for the additional payment!**"""
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 My Campaigns", callback_data="my_campaigns")],
                    [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
                ])
                
                await callback_query.message.edit_text(
                    text=confirm_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
                # Process the overpayment as a valid payment
                try:
                    from automatic_payment_confirmation import handle_confirmed_payment
                    
                    payment_data = {
                        'user_id': user_id,
                        'memo': memo,
                        'amount': received_amount,
                        'currency': 'TON',
                        'payment_method': 'blockchain'
                    }
                    
                    await handle_confirmed_payment(payment_data)
                    logger.info(f"✅ Overpayment processed as valid payment for user {user_id}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing overpayment: {e}")
                    
            else:
                # No payment data found
                if user_language == 'ar':
                    error_text = "❌ لم يتم العثور على بيانات الدفع. يرجى المحاولة مرة أخرى."
                elif user_language == 'ru':
                    error_text = "❌ Данные о платеже не найдены. Пожалуйста, попробуйте еще раз."
                else:
                    error_text = "❌ Payment data not found. Please try again."
                
                await callback_query.message.edit_text(error_text)
                
        except Exception as e:
            logger.error(f"❌ Error processing overpayment confirmation: {e}")
            await callback_query.answer("Error processing overpayment confirmation")
            
        await callback_query.answer()
        logger.info(f"✅ Overpayment confirmation processed for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error handling overpayment confirmation: {e}")
        await callback_query.answer("Error processing overpayment confirmation")

@router.callback_query(lambda c: c.data and c.data.startswith('restart_payment_'))
async def handle_restart_payment(callback_query: CallbackQuery, state: FSMContext):
    """Handle restart payment callback"""
    try:
        user_id = callback_query.from_user.id
        memo = callback_query.data.replace('restart_payment_', '')
        
        logger.info(f"🔄 Restart payment request from user {user_id} for memo {memo}")
        
        # Get user language
        user_language = await get_user_language(user_id)
        
        # Create restart payment message
        if user_language == 'ar':
            restart_text = f"""🔄 **إعادة بدء عملية الدفع**

📋 **رمز الدفع السابق:** {memo}

سيتم إنشاء رمز دفع جديد لحملتك الإعلانية.

🔄 **هل تريد المتابعة؟**"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ إنشاء رمز دفع جديد", callback_data="create_new_payment")],
                [InlineKeyboardButton(text="💬 اتصل بالدعم", callback_data="contact_support")],
                [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")]
            ])
            
        elif user_language == 'ru':
            restart_text = f"""🔄 **Перезапуск процесса оплаты**

📋 **Предыдущий код платежа:** {memo}

Будет создан новый код платежа для вашей рекламной кампании.

🔄 **Хотите продолжить?**"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Создать новый код платежа", callback_data="create_new_payment")],
                [InlineKeyboardButton(text="💬 Связаться с поддержкой", callback_data="contact_support")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
            
        else:  # English
            restart_text = f"""🔄 **Restart Payment Process**

📋 **Previous Payment Code:** {memo}

A new payment code will be created for your advertising campaign.

🔄 **Want to continue?**"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Create New Payment Code", callback_data="create_new_payment")],
                [InlineKeyboardButton(text="💬 Contact Support", callback_data="contact_support")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
        
        await callback_query.message.edit_text(
            text=restart_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        await callback_query.answer()
        logger.info(f"✅ Restart payment interface shown to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error handling restart payment: {e}")
        await callback_query.answer("Error processing restart payment request")

def setup_payment_protocol_handlers(dp):
    """Setup payment protocol handlers"""
    dp.include_router(router)
    logger.info("✅ Payment protocol handlers registered")

if __name__ == "__main__":
    print("🔧 Payment Protocol Handlers - Retry and Overpayment Management")
    print("Handles user interactions for incorrect payment amounts")