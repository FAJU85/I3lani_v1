"""
Confirmation Handlers for I3lani Bot
Handles all confirmation callbacks and user interactions
"""

import asyncio
import logging
from typing import Dict, Any
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from languages import get_text
from database import db
from confirmation_system import confirmation_system
from callback_error_handler import safe_callback_answer, safe_callback_edit
# from frequency_pricing import FrequencyPricingSystem  # Removed during cleanup
# Payment processor import removed during cleanup
from states import AdCreationStates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

async def handle_confirm_ad_submission(callback_query: CallbackQuery, state: FSMContext):
    """Handle ad submission confirmation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Get state data
        state_data = await state.get_data()
        ad_data = state_data.get('ad_data', {})
        pricing_data = state_data.get('pricing_data', {})
        
        # Log confirmation
        await confirmation_system.log_confirmation_action(
            user_id=user_id,
            action_type='ad_submission',
            confirmed=True,
            data=ad_data
        )
        
        # Send confirmation message
        await safe_callback_answer(callback_query, get_text(language, 'action_confirmed'))
        
        # Proceed to payment
        await show_payment_selection(callback_query, state, ad_data, pricing_data)
        
    except Exception as e:
        logger.error(f"Error handling ad submission confirmation: {e}")
        await safe_callback_answer(callback_query, get_text(language, 'error_confirming_ad'))

async def handle_cancel_ad_submission(callback_query: CallbackQuery, state: FSMContext):
    """Handle ad submission cancellation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Log cancellation
        await confirmation_system.log_confirmation_action(
            user_id=user_id,
            action_type='ad_submission',
            confirmed=False
        )
        
        # Send cancellation message
        await safe_callback_answer(callback_query, get_text(language, 'action_cancelled'))
        
        # Return to main menu
        from handlers import show_main_menu
        await show_main_menu(callback_query.message, language, user_id)
        
    except Exception as e:
        logger.error(f"Error handling ad submission cancellation: {e}")
        await safe_callback_answer(callback_query, "Error processing cancellation")

async def handle_edit_ad_submission(callback_query: CallbackQuery, state: FSMContext):
    """Handle edit ad submission request"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Send edit options
        edit_text = {
            'en': """✏️ <b>Edit Advertisement</b>
            
What would you like to edit?
• Content (text/photos)
• Channel selection
• Duration and frequency
• Start over completely""",
            'ar': """✏️ <b>تعديل الإعلان</b>
            
ماذا تريد تعديل؟
• المحتوى (نص/صور)
• اختيار القنوات
• المدة والتكرار
• البدء من جديد""",
            'ru': """✏️ <b>Редактировать объявление</b>
            
Что вы хотите отредактировать?
• Контент (текст/фото)
• Выбор каналов
• Продолжительность и частота
• Начать заново"""
        }
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(language, 'edit_content', 'Edit Content'),
                    callback_data="edit_content"
                ),
                InlineKeyboardButton(
                    text=get_text(language, 'edit_channels', 'Edit Channels'),
                    callback_data="edit_channels"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text(language, 'edit_duration', 'Edit Duration'),
                    callback_data="edit_duration"
                ),
                InlineKeyboardButton(
                    text=get_text(language, 'start_over', 'Start Over'),
                    callback_data="start_over"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text(language, 'back_to_confirmation', 'Back to Confirmation'),
                    callback_data="back_to_confirmation"
                )
            ]
        ])
        
        await safe_callback_edit(
            callback_query,
            edit_text.get(language, edit_text['en']),
            keyboard
        )
        
    except Exception as e:
        logger.error(f"Error handling edit ad submission: {e}")
        await safe_callback_answer(callback_query, "Error opening edit options")

async def handle_confirm_payment_processing(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment processing confirmation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Get state data
        state_data = await state.get_data()
        payment_data = state_data.get('payment_data', {})
        
        # Log confirmation
        await confirmation_system.log_confirmation_action(
            user_id=user_id,
            action_type='payment_processing',
            confirmed=True,
            data=payment_data
        )
        
        # Send confirmation message
        await safe_callback_answer(callback_query, get_text(language, 'action_confirmed'))
        
        # Process payment
        await process_confirmed_payment(callback_query, state, payment_data)
        
    except Exception as e:
        logger.error(f"Error handling payment confirmation: {e}")
        await safe_callback_answer(callback_query, "Error processing payment")

async def handle_cancel_payment_processing(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment processing cancellation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Log cancellation
        await confirmation_system.log_confirmation_action(
            user_id=user_id,
            action_type='payment_processing',
            confirmed=False
        )
        
        # Send cancellation message
        await safe_callback_answer(callback_query, get_text(language, 'action_cancelled'))
        
        # Return to payment method selection
        await show_payment_method_selection(callback_query, state)
        
    except Exception as e:
        logger.error(f"Error handling payment cancellation: {e}")
        await safe_callback_answer(callback_query, "Error processing cancellation")

async def handle_confirm_channel_selection(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel selection confirmation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Get state data
        state_data = await state.get_data()
        selected_channels = state_data.get('selected_channels', [])
        
        # Log confirmation
        await confirmation_system.log_confirmation_action(
            user_id=user_id,
            action_type='channel_selection',
            confirmed=True,
            data={'selected_channels': selected_channels}
        )
        
        # Send confirmation message
        await safe_callback_answer(callback_query, get_text(language, 'action_confirmed'))
        
        # Proceed to duration selection
        await show_duration_selection(callback_query, state)
        
    except Exception as e:
        logger.error(f"Error handling channel selection confirmation: {e}")
        await safe_callback_answer(callback_query, "Error confirming channel selection")

async def handle_cancel_channel_selection(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel selection cancellation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Log cancellation
        await confirmation_system.log_confirmation_action(
            user_id=user_id,
            action_type='channel_selection',
            confirmed=False
        )
        
        # Send cancellation message
        await safe_callback_answer(callback_query, get_text(language, 'action_cancelled'))
        
        # Return to channel selection
        from handlers import show_channel_selection_for_enhanced_flow
        await show_channel_selection_for_enhanced_flow(callback_query, state)
        
    except Exception as e:
        logger.error(f"Error handling channel selection cancellation: {e}")
        await safe_callback_answer(callback_query, "Error processing cancellation")

async def handle_confirm_ad_deletion(callback_query: CallbackQuery, state: FSMContext):
    """Handle ad deletion confirmation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Get state data
        state_data = await state.get_data()
        ad_id = state_data.get('ad_id_to_delete')
        
        if not ad_id:
            await safe_callback_answer(callback_query, "Error: No ad selected for deletion")
            return
        
        # Log confirmation
        await confirmation_system.log_confirmation_action(
            user_id=user_id,
            action_type='ad_deletion',
            confirmed=True,
            data={'ad_id': ad_id}
        )
        
        # Delete the ad
        await db.delete_ad(ad_id)
        
        # Send confirmation message
        success_message = {
            'en': '✅ Advertisement deleted successfully!',
            'ar': '✅ تم حذف الإعلان بنجاح!',
            'ru': '✅ Объявление успешно удалено!'
        }
        
        await safe_callback_answer(callback_query, success_message.get(language, success_message['en']))
        
        # Return to ads dashboard
        await show_ads_dashboard(callback_query, state)
        
    except Exception as e:
        logger.error(f"Error handling ad deletion confirmation: {e}")
        await safe_callback_answer(callback_query, "Error deleting ad")

async def handle_cancel_ad_deletion(callback_query: CallbackQuery, state: FSMContext):
    """Handle ad deletion cancellation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Log cancellation
        await confirmation_system.log_confirmation_action(
            user_id=user_id,
            action_type='ad_deletion',
            confirmed=False
        )
        
        # Send cancellation message
        await safe_callback_answer(callback_query, get_text(language, 'action_cancelled'))
        
        # Return to ads dashboard
        await show_ads_dashboard(callback_query, state)
        
    except Exception as e:
        logger.error(f"Error handling ad deletion cancellation: {e}")
        await safe_callback_answer(callback_query, "Error processing cancellation")

# Helper functions
async def show_payment_selection(callback_query: CallbackQuery, state: FSMContext, ad_data: Dict, pricing_data: Dict):
    """Show payment method selection after ad confirmation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Store data for payment processing
        await state.update_data({
            'ad_data': ad_data,
            'pricing_data': pricing_data,
            'payment_step': 'method_selection'
        })
        
        # Import here to avoid circular imports
        # from frequency_pricing import FrequencyPricingSystem  # Removed during cleanup
        pricing_system = None  # Frequency pricing removed during cleanup
        
        # Show payment method selection
        await pricing_system.show_payment_methods(callback_query, state, pricing_data)
        
    except Exception as e:
        logger.error(f"Error showing payment selection: {e}")

async def show_duration_selection(callback_query: CallbackQuery, state: FSMContext):
    """Show duration selection after channel confirmation"""
    try:
        # Import here to avoid circular imports
        # from frequency_pricing import FrequencyPricingSystem  # Removed during cleanup
        pricing_system = None  # Frequency pricing removed during cleanup
        
        # Show duration selection
        await pricing_system.show_dynamic_days_selector(callback_query, state)
        
    except Exception as e:
        logger.error(f"Error showing duration selection: {e}")

async def show_payment_method_selection(callback_query: CallbackQuery, state: FSMContext):
    """Show payment method selection"""
    try:
        # Import here to avoid circular imports
        # from frequency_pricing import FrequencyPricingSystem  # Removed during cleanup
        pricing_system = None  # Frequency pricing removed during cleanup
        
        # Get pricing data from state
        state_data = await state.get_data()
        pricing_data = state_data.get('pricing_data', {})
        
        # Show payment methods
        await pricing_system.show_payment_methods(callback_query, state, pricing_data)
        
    except Exception as e:
        logger.error(f"Error showing payment method selection: {e}")

async def show_ads_dashboard(callback_query: CallbackQuery, state: FSMContext):
    """Show user's ads dashboard"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Get user's ads
        ads = await db.get_user_ads(user_id)
        
        dashboard_text = {
            'en': f"""📊 <b>My Advertisements</b>
            
<b>Total Ads:</b> {len(ads)}
<b>Active Ads:</b> {len([ad for ad in ads if ad.get('status') == 'active'])}
<b>Completed Ads:</b> {len([ad for ad in ads if ad.get('status') == 'completed'])}

Select an ad to view details or create a new one.""",
            'ar': f"""📊 <b>إعلاناتي</b>
            
<b>إجمالي الإعلانات:</b> {len(ads)}
<b>الإعلانات النشطة:</b> {len([ad for ad in ads if ad.get('status') == 'active'])}
<b>الإعلانات المكتملة:</b> {len([ad for ad in ads if ad.get('status') == 'completed'])}

اختر إعلان لعرض التفاصيل أو إنشاء إعلان جديد.""",
            'ru': f"""📊 <b>Мои объявления</b>
            
<b>Всего объявлений:</b> {len(ads)}
<b>Активных объявлений:</b> {len([ad for ad in ads if ad.get('status') == 'active'])}
<b>Завершенных объявлений:</b> {len([ad for ad in ads if ad.get('status') == 'completed'])}

Выберите объявление для просмотра деталей или создайте новое."""
        }
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(language, 'create_ad'),
                    callback_data="create_ad"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text(language, 'back_to_main'),
                    callback_data="main_menu"
                )
            ]
        ])
        
        await safe_callback_edit(
            callback_query,
            dashboard_text.get(language, dashboard_text['en']),
            keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing ads dashboard: {e}")

async def process_confirmed_payment(callback_query: CallbackQuery, state: FSMContext, payment_data: Dict):
    """Process payment after confirmation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Get payment method and amount
        payment_method = payment_data.get('payment_method', 'ton')
        amount = payment_data.get('amount', 0)
        
        # Create payment invoice
        # Payment processor removed during cleanup
        invoice_data = {'instructions': f'Payment of {amount} {payment_method}'}  # Simplified payment data
        
        # Show payment instructions
        await show_payment_instructions(callback_query, state, invoice_data)
        
    except Exception as e:
        logger.error(f"Error processing confirmed payment: {e}")
        await safe_callback_answer(callback_query, "Error processing payment")

async def show_payment_instructions(callback_query: CallbackQuery, state: FSMContext, invoice_data: Dict):
    """Show payment instructions after confirmation"""
    try:
        user_id = callback_query.from_user.id
        language = await db.get_user_language(user_id)
        
        # Build payment instructions text
        instructions_text = invoice_data.get('instructions', 'Payment instructions not available')
        
        # Create payment keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(language, 'cancel'),
                    callback_data="cancel_payment"
                )
            ]
        ])
        
        await safe_callback_edit(
            callback_query,
            instructions_text,
            keyboard
        )
        
    except Exception as e:
        logger.error(f"Error showing payment instructions: {e}")

# Register all confirmation handlers
CONFIRMATION_HANDLERS = {
    'confirm_ad_submission': handle_confirm_ad_submission,
    'cancel_ad_submission': handle_cancel_ad_submission,
    'edit_ad_submission': handle_edit_ad_submission,
    'confirm_payment_processing': handle_confirm_payment_processing,
    'cancel_payment_processing': handle_cancel_payment_processing,
    'confirm_channel_selection': handle_confirm_channel_selection,
    'cancel_channel_selection': handle_cancel_channel_selection,
    'confirm_ad_deletion': handle_confirm_ad_deletion,
    'cancel_ad_deletion': handle_cancel_ad_deletion,
}