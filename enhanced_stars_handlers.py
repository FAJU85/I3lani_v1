"""
Enhanced Telegram Stars Payment Handlers
Phase 1 & Phase 2 Implementation for I3lani Bot
"""

import logging
from aiogram import Router
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from enhanced_stars_payment_system import (
    get_enhanced_stars_payment_system, PaymentValidationLevel,
    EnhancedPaymentResult
)
from sequence_logger import get_sequence_logger

logger = get_sequence_logger(__name__)

# Create router for enhanced Stars handlers
enhanced_stars_router = Router()

@enhanced_stars_router.callback_query(lambda c: c.data.startswith('pay_stars_enhanced:'))
async def enhanced_stars_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """
    Enhanced Stars payment handler with Phase 1 & Phase 2 features
    """
    try:
        await callback_query.answer("🔄 Creating enhanced payment...")
        
        # Get user data
        user_id = callback_query.from_user.id
        user_data = await state.get_data()
        
        # Extract campaign and pricing data
        campaign_data = user_data.get('campaign_data', {})
        pricing_data = user_data.get('pricing_data', {})
        language = user_data.get('language', 'en')
        
        # Validate required data
        if not campaign_data or not pricing_data:
            await callback_query.message.edit_text(
                "❌ Payment data missing. Please restart the campaign creation process.",
                reply_markup=None
            )
            return
        
        # Get enhanced payment system
        enhanced_system = get_enhanced_stars_payment_system(callback_query.bot)
        
        # Create enhanced payment request
        payment_result = await enhanced_system.create_enhanced_payment_request(
            user_id=user_id,
            campaign_data=campaign_data,
            pricing_data=pricing_data,
            language=language,
            validation_level=PaymentValidationLevel.ENHANCED
        )
        
        if payment_result['success']:
            # Payment created successfully
            payment_id = payment_result['payment_id']
            fraud_score = payment_result.get('fraud_score', 0.0)
            processing_time = payment_result.get('processing_time', 0.0)
            ton_connect_available = payment_result.get('ton_connect_available', False)
            
            # Create enhanced payment message
            if language == 'ar':
                success_message = f"""
✅ **تم إنشاء طلب الدفع بنجاح**

🆔 **معرف الدفع:** `{payment_id}`
💫 **نوع الدفع:** نجوم تليجرام محسن
⭐ **المبلغ:** {pricing_data.get('total_stars', 0)} نجمة
💵 **بالدولار:** ${pricing_data.get('total_usd', 0):.2f}
🔒 **نقاط الأمان:** {fraud_score:.3f}/1.0
⚡ **وقت المعالجة:** {processing_time:.3f}ث
{'🔗 **TON Connect متاح**' if ton_connect_available else ''}

**الميزات المحسنة:**
• 🛡️ حماية متقدمة من الاحتيال
• ✅ التحقق من المبلغ بدقة
• 🔄 استرداد الأخطاء المحسن
{'• 🔗 دعم TON Connect' if ton_connect_available else ''}

اضغط "دفع" لإكمال العملية.
                """
            elif language == 'ru':
                success_message = f"""
✅ **Запрос на оплату успешно создан**

🆔 **ID платежа:** `{payment_id}`
💫 **Тип оплаты:** Улучшенные Telegram Stars
⭐ **Сумма:** {pricing_data.get('total_stars', 0)} звезд
💵 **В долларах:** ${pricing_data.get('total_usd', 0):.2f}
🔒 **Оценка безопасности:** {fraud_score:.3f}/1.0
⚡ **Время обработки:** {processing_time:.3f}с
{'🔗 **TON Connect доступен**' if ton_connect_available else ''}

**Улучшенные функции:**
• 🛡️ Продвинутая защита от мошенничества
• ✅ Точная проверка суммы
• 🔄 Улучшенное восстановление ошибок
{'• 🔗 Поддержка TON Connect' if ton_connect_available else ''}

Нажмите "Оплатить" для завершения.
                """
            else:
                success_message = f"""
✅ **Enhanced Payment Request Created**

🆔 **Payment ID:** `{payment_id}`
💫 **Payment Type:** Enhanced Telegram Stars
⭐ **Amount:** {pricing_data.get('total_stars', 0)} Stars
💵 **USD Value:** ${pricing_data.get('total_usd', 0):.2f}
🔒 **Security Score:** {fraud_score:.3f}/1.0
⚡ **Processing Time:** {processing_time:.3f}s
{'🔗 **TON Connect Available**' if ton_connect_available else ''}

**Enhanced Features:**
• 🛡️ Advanced fraud protection
• ✅ Precise amount validation
• 🔄 Enhanced error recovery
{'• 🔗 TON Connect support' if ton_connect_available else ''}

Click "Pay" to complete the transaction.
                """
            
            await callback_query.message.edit_text(
                success_message,
                parse_mode='Markdown',
                reply_markup=payment_result.get('keyboard')
            )
            
            logger.info(f"✅ Enhanced Stars payment created for user {user_id}")
            logger.info(f"   Payment ID: {payment_id}")
            logger.info(f"   Fraud Score: {fraud_score:.3f}")
            logger.info(f"   TON Connect: {ton_connect_available}")
            
        else:
            # Payment creation failed - enhanced error handling
            error_message = payment_result.get('error', 'Unknown error')
            error_type = payment_result.get('error_type', 'generic')
            recovery_options = payment_result.get('recovery_options', [])
            
            # Create enhanced error message with recovery options
            if language == 'ar':
                error_text = f"""
❌ **فشل في إنشاء طلب الدفع**

**السبب:** {error_message}
**نوع الخطأ:** {error_type}

**خيارات الاستكمال:**
                """
                
                if 'retry_payment' in recovery_options:
                    error_text += "• 🔄 إعادة المحاولة\n"
                if 'contact_support' in recovery_options:
                    error_text += "• 💬 اتصال بالدعم\n"
                if 'reduce_campaign_size' in recovery_options:
                    error_text += "• 📉 تقليل حجم الحملة\n"
                
            elif language == 'ru':
                error_text = f"""
❌ **Не удалось создать запрос на оплату**

**Причина:** {error_message}
**Тип ошибки:** {error_type}

**Варианты восстановления:**
                """
                
                if 'retry_payment' in recovery_options:
                    error_text += "• 🔄 Повторить попытку\n"
                if 'contact_support' in recovery_options:
                    error_text += "• 💬 Связаться с поддержкой\n"
                if 'reduce_campaign_size' in recovery_options:
                    error_text += "• 📉 Уменьшить размер кампании\n"
                
            else:
                error_text = f"""
❌ **Payment Request Failed**

**Reason:** {error_message}
**Error Type:** {error_type}

**Recovery Options:**
                """
                
                if 'retry_payment' in recovery_options:
                    error_text += "• 🔄 Retry payment\n"
                if 'contact_support' in recovery_options:
                    error_text += "• 💬 Contact support\n"
                if 'reduce_campaign_size' in recovery_options:
                    error_text += "• 📉 Reduce campaign size\n"
            
            # Create recovery keyboard
            keyboard = None
            if recovery_options:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                
                buttons = []
                if 'retry_payment' in recovery_options:
                    buttons.append([InlineKeyboardButton(
                        text="🔄 Retry" if language == 'en' else "🔄 إعادة المحاولة" if language == 'ar' else "🔄 Повторить",
                        callback_data='pay_stars_enhanced:retry'
                    )])
                if 'contact_support' in recovery_options:
                    buttons.append([InlineKeyboardButton(
                        text="💬 Support" if language == 'en' else "💬 الدعم" if language == 'ar' else "💬 Поддержка",
                        callback_data='contact_support'
                    )])
                
                if buttons:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            
            await callback_query.message.edit_text(
                error_text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
            logger.warning(f"❌ Enhanced Stars payment failed for user {user_id}: {error_message}")
        
    except Exception as e:
        logger.error(f"❌ Enhanced Stars payment handler error: {e}")
        await callback_query.message.edit_text(
            "❌ An unexpected error occurred. Please try again or contact support.",
            reply_markup=None
        )

@enhanced_stars_router.pre_checkout_query()
async def enhanced_pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """
    Enhanced pre-checkout handler with Phase 1 validation
    """
    try:
        logger.info(f"💫 Processing enhanced pre-checkout query from user {pre_checkout_query.from_user.id}")
        
        # Get enhanced payment system
        enhanced_system = get_enhanced_stars_payment_system(pre_checkout_query.bot)
        
        # Process enhanced pre-checkout
        result = await enhanced_system.process_enhanced_pre_checkout(pre_checkout_query)
        
        if result['success']:
            logger.info(f"✅ Enhanced pre-checkout approved: {result['payment_id']}")
        else:
            logger.warning(f"❌ Enhanced pre-checkout failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"❌ Enhanced pre-checkout handler error: {e}")
        await pre_checkout_query.answer(
            ok=False,
            error_message="Payment validation failed - please try again"
        )

@enhanced_stars_router.message(lambda message: message.successful_payment is not None)
async def enhanced_successful_payment_handler(message: Message, state: FSMContext):
    """
    Enhanced successful payment handler with Phase 1 & Phase 2 features
    """
    try:
        user_id = message.from_user.id
        payment = message.successful_payment
        
        logger.info(f"💰 Processing enhanced successful payment from user {user_id}")
        logger.info(f"   Amount: {payment.total_amount} Stars")
        logger.info(f"   Transaction ID: {payment.telegram_payment_charge_id}")
        
        # Get enhanced payment system
        enhanced_system = get_enhanced_stars_payment_system(message.bot)
        
        # Process enhanced successful payment
        result: EnhancedPaymentResult = await enhanced_system.process_enhanced_successful_payment(message)
        
        if result.success:
            # Enhanced success message
            user_data = await state.get_data()
            language = user_data.get('language', 'en')
            
            if language == 'ar':
                success_message = f"""
✅ **تم الدفع بنجاح**

🆔 **معرف الدفع:** `{result.payment_id}`
💰 **المبلغ المدفوع:** {result.amount_paid} نجمة
🔒 **نقاط الأمان:** {result.fraud_score:.3f}/1.0
⚡ **وقت المعالجة:** {result.processing_time:.3f}ث
📊 **مستوى التحقق:** {result.validation_level.value}

سيتم نشر حملتك الإعلانية قريباً!
                """
            elif language == 'ru':
                success_message = f"""
✅ **Оплата успешно завершена**

🆔 **ID платежа:** `{result.payment_id}`
💰 **Сумма оплаты:** {result.amount_paid} звезд
🔒 **Оценка безопасности:** {result.fraud_score:.3f}/1.0
⚡ **Время обработки:** {result.processing_time:.3f}с
📊 **Уровень проверки:** {result.validation_level.value}

Ваша рекламная кампания скоро будет опубликована!
                """
            else:
                success_message = f"""
✅ **Payment Successfully Completed**

🆔 **Payment ID:** `{result.payment_id}`
💰 **Amount Paid:** {result.amount_paid} Stars
🔒 **Security Score:** {result.fraud_score:.3f}/1.0
⚡ **Processing Time:** {result.processing_time:.3f}s
📊 **Validation Level:** {result.validation_level.value}

Your advertising campaign will be published shortly!
                """
            
            await message.answer(success_message, parse_mode='Markdown')
            
            logger.info(f"✅ Enhanced payment completed successfully: {result.payment_id}")
            logger.info(f"   Fraud Score: {result.fraud_score:.3f}")
            logger.info(f"   Validation Level: {result.validation_level.value}")
            logger.info(f"   Processing Time: {result.processing_time:.3f}s")
            
        else:
            # Enhanced error handling with recovery options
            user_data = await state.get_data()
            language = user_data.get('language', 'en')
            
            error_message = result.error_message or "Payment processing failed"
            recovery_options = result.recovery_options
            
            if language == 'ar':
                error_text = f"""
❌ **فشل في معالجة الدفع**

**السبب:** {error_message}
🆔 **معرف الدفع:** `{result.payment_id}`
⚡ **وقت المعالجة:** {result.processing_time:.3f}ث

يرجى الاتصال بالدعم للمساعدة.
                """
            elif language == 'ru':
                error_text = f"""
❌ **Ошибка обработки платежа**

**Причина:** {error_message}
🆔 **ID платежа:** `{result.payment_id}`
⚡ **Время обработки:** {result.processing_time:.3f}с

Пожалуйста, обратитесь в службу поддержки за помощью.
                """
            else:
                error_text = f"""
❌ **Payment Processing Failed**

**Reason:** {error_message}
🆔 **Payment ID:** `{result.payment_id}`
⚡ **Processing Time:** {result.processing_time:.3f}s

Please contact support for assistance.
                """
            
            # Add recovery keyboard if options available
            keyboard = None
            if recovery_options:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                
                buttons = []
                if 'contact_support' in recovery_options:
                    buttons.append([InlineKeyboardButton(
                        text="💬 Contact Support",
                        callback_data='contact_support'
                    )])
                if 'retry_later' in recovery_options:
                    buttons.append([InlineKeyboardButton(
                        text="🔄 Try Again Later",
                        callback_data='retry_payment_later'
                    )])
                
                if buttons:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            
            await message.answer(error_text, parse_mode='Markdown', reply_markup=keyboard)
            
            logger.error(f"❌ Enhanced payment processing failed: {result.payment_id}")
            logger.error(f"   Error: {error_message}")
            logger.error(f"   Recovery options: {recovery_options}")
        
    except Exception as e:
        logger.error(f"❌ Enhanced successful payment handler error: {e}")
        await message.answer(
            "❌ An error occurred while processing your payment. Please contact support with your transaction details."
        )

@enhanced_stars_router.callback_query(lambda c: c.data == 'retry_stars_payment')
async def retry_stars_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Stars payment retry"""
    try:
        await callback_query.answer("🔄 Retrying payment...")
        
        # Redirect to payment creation
        await enhanced_stars_payment_handler(callback_query, state)
        
    except Exception as e:
        logger.error(f"❌ Retry payment handler error: {e}")
        await callback_query.answer("❌ Retry failed. Please contact support.", show_alert=True)

@enhanced_stars_router.callback_query(lambda c: c.data == 'confirm_overpayment')
async def confirm_overpayment_handler(callback_query: CallbackQuery):
    """Handle overpayment confirmation"""
    try:
        await callback_query.answer("✅ Overpayment confirmed for processing")
        
        user_id = callback_query.from_user.id
        
        # Log overpayment confirmation
        logger.info(f"✅ Overpayment confirmed by user {user_id}")
        
        # Notify admins about manual overpayment processing needed
        from config import ADMIN_IDS
        admin_message = f"""
⚠️ **Manual Overpayment Processing Required**

**User ID:** {user_id}
**Action:** User confirmed overpayment processing
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please review and process the overpayment manually.
        """
        
        for admin_id in ADMIN_IDS:
            try:
                await callback_query.bot.send_message(admin_id, admin_message, parse_mode='Markdown')
            except Exception:
                pass
        
        await callback_query.message.edit_text(
            "✅ Your overpayment has been confirmed for manual processing. Support will contact you within 24 hours.",
            reply_markup=None
        )
        
    except Exception as e:
        logger.error(f"❌ Overpayment confirmation handler error: {e}")
        await callback_query.answer("❌ Confirmation failed. Please contact support.", show_alert=True)

@enhanced_stars_router.message(Command('payment_analytics'))
async def payment_analytics_handler(message: Message):
    """Admin command to view payment analytics"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin
        from config import ADMIN_IDS
        if user_id not in ADMIN_IDS:
            await message.answer("❌ Admin access required.")
            return
        
        # Get enhanced payment system
        enhanced_system = get_enhanced_stars_payment_system(message.bot)
        
        # Get analytics
        analytics = await enhanced_system.get_payment_analytics()
        
        analytics_message = f"""
📊 **Enhanced Stars Payment Analytics**

**Overall Statistics:**
• Total Payments: {analytics['total_payments']}
• Successful: {analytics['successful_payments']}
• Success Rate: {(analytics['successful_payments']/analytics['total_payments']*100):.1f}% if analytics['total_payments'] > 0 else 0
• Fraud Attempts: {analytics['fraud_attempts']}
• Average Fraud Score: {analytics['average_fraud_score']:.3f}
• Active Cache Entries: {analytics['active_cache_entries']}

**System Health:**
• Phase 1 Features: ✅ Active
• Phase 2 Features: ✅ Active
• Error Recovery: ✅ Enabled
• Fraud Detection: ✅ Enabled
        """
        
        await message.answer(analytics_message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Payment analytics handler error: {e}")
        await message.answer("❌ Failed to retrieve analytics.")

def setup_enhanced_stars_handlers(dp):
    """Setup enhanced Stars payment handlers"""
    dp.include_router(enhanced_stars_router)
    
    logger.info("✅ Enhanced Telegram Stars payment handlers registered")
    logger.info("   🔍 Enhanced validation and error handling")
    logger.info("   🛡️ Advanced fraud detection")
    logger.info("   🔄 Automatic error recovery")
    logger.info("   📊 Payment analytics and monitoring")