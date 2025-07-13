#!/usr/bin/env python3
"""
Enhanced Stars Payment Handlers
Handlers for Stars payment processing
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from enhanced_stars_payment_system import get_enhanced_stars_system

logger = logging.getLogger(__name__)

# Create router
router = Router()

@router.callback_query(F.data.startswith("pay_stars_"))
async def stars_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Stars payment callback"""
    try:
        user_id = callback_query.from_user.id
        
        # Get payment data from callback
        payment_data = await state.get_data()
        
        # Process Stars payment
        stars_system = get_enhanced_stars_system()
        
        payment_info = {
            'user_id': user_id,
            'amount': payment_data.get('amount', 0),
            'currency': 'XTR',
            'payment_id': f"stars_{user_id}_{callback_query.message.message_id}",
            'payment_method': 'stars'
        }
        
        result = await stars_system.process_payment(payment_info)
        
        if result['success']:
            await callback_query.message.edit_text(
                f"✅ Stars payment processed successfully!\n"
                f"Campaign ID: {result['campaign_id']}\n"
                f"Amount: {result['amount']} USD"
            )
        else:
            await callback_query.message.edit_text(
                f"❌ Payment failed: {result['error']}"
            )
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Stars payment handler error: {e}")
        await callback_query.answer("Payment processing error", show_alert=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, state: FSMContext):
    """Handle successful Stars payment"""
    try:
        payment = message.successful_payment
        user_id = message.from_user.id
        
        # Process successful payment
        stars_system = get_enhanced_stars_system()
        
        payment_info = {
            'user_id': user_id,
            'amount': payment.total_amount / 100,  # Convert from Stars
            'currency': payment.currency,
            'payment_id': payment.telegram_payment_charge_id,
            'payment_method': 'stars'
        }
        
        result = await stars_system.process_payment(payment_info)
        
        if result['success']:
            await message.answer(
                f"✅ Payment confirmed!\n"
                f"Campaign: {result['campaign_id']}\n"
                f"Amount: {result['amount']} USD\n"
                f"Your ad campaign is now active!"
            )
        else:
            await message.answer(
                f"❌ Payment processing failed: {result['error']}"
            )
        
    except Exception as e:
        logger.error(f"Successful payment handler error: {e}")
        await message.answer("Payment confirmation error")

def setup_enhanced_stars_handlers(dp):
    """Setup enhanced Stars payment handlers"""
    dp.include_router(router)
    logger.info("Enhanced Stars payment handlers registered")