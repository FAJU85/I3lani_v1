"""
Enhanced Telegram Ad Bot with Multi-Channel Support and Auto Payment Detection
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType, ParseMode

# Import new modules
from database import create_tables, init_default_data, SessionLocal, User, Channel, Order
from datetime import datetime
from payment_system import payment_system
from admin_panel import register_admin_handlers
from enhanced_ui import EnhancedUI, user_flow
from languages import get_text, get_user_language, set_user_language
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class UserStates(StatesGroup):
    selecting_channels = State()
    selecting_duration = State()
    creating_ad_content = State()
    confirming_order = State()
    payment_pending = State()

# Enhanced handlers
async def start_command(message: types.Message, state: FSMContext):
    """Enhanced start command with user registration"""
    user_id = message.from_user.id
    
    # Register/update user in database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(
                id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code or 'en'
            )
            db.add(user)
            db.commit()
        
        # Check if user is admin
        if user_id in ADMIN_IDS and not user.is_admin:
            user.is_admin = True
            db.commit()
            
    finally:
        db.close()
    
    # Clear any existing user data
    user_flow.clear_user_data(user_id)
    await state.finish()
    
    welcome_text = f"""
🚀 **Welcome to Advanced Ad Bot!**

Create targeted advertising campaigns across multiple Telegram channels with our enhanced platform:

✨ **New Features:**
📺 **Multi-Channel Selection** - Choose from multiple channels
💰 **Dynamic Pricing** - Real-time TON/USD/SAR/RUB conversion
🎁 **Bundle Offers** - Save with bulk packages
🔄 **Auto Payment Detection** - Instant campaign activation
📊 **Live Analytics** - Track campaign performance

💳 **Transparent Pricing:**
• 0.099 TON per channel per month
• Multi-channel discounts available
• Bonus months with bundles

Ready to start? Choose your channels below! 👇
"""
    
    keyboard = EnhancedUI.get_channel_selection_keyboard()
    await message.reply(welcome_text, reply_markup=keyboard)
    await UserStates.selecting_channels.set()

async def handle_channel_toggle(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle channel selection toggle"""
    try:
        channel_id = callback_query.data.split('_')[-1]
        user_id = callback_query.from_user.id
        
        # Toggle channel selection
        selected_channels = user_flow.toggle_channel(user_id, channel_id)
        
        # Update keyboard
        keyboard = EnhancedUI.get_channel_selection_keyboard(selected_channels)
        
        # Update message
        if selected_channels:
            text = f"""
📺 **Channel Selection** ({len(selected_channels)} selected)

Select the channels where you want to advertise:

✅ Use checkboxes to select/deselect channels
📊 Click "View Pricing" to see costs
✅ Click "Continue" when ready
"""
        else:
            text = """
📺 **Channel Selection**

Select the channels where you want to advertise:

📌 Each channel costs 0.099 TON per month
💡 Select multiple channels for broader reach
"""
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in channel toggle: {e}")
        await callback_query.answer("Error updating selection. Please try again.")

async def handle_view_pricing(callback_query: types.CallbackQuery, state: FSMContext):
    """Show pricing preview for selected channels"""
    try:
        user_id = callback_query.from_user.id
        selected_channels = user_flow.get_selected_channels(user_id)
        
        if not selected_channels:
            await callback_query.answer("Please select at least one channel first.")
            return
        
        # Show 1-month pricing as preview
        pricing_text = await EnhancedUI.get_pricing_text(selected_channels, 1)
        
        # Add back button
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔙 Back to Selection", callback_data="back_to_channels"))
        
        await callback_query.message.edit_text(
            f"{pricing_text}\n💡 This is pricing for 1 month. You can choose different durations next.",
            reply_markup=keyboard
        )
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error showing pricing: {e}")
        await callback_query.answer("Error calculating pricing. Please try again.")

async def handle_continue_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Continue to duration selection"""
    try:
        user_id = callback_query.from_user.id
        selected_channels = user_flow.get_selected_channels(user_id)
        
        if not selected_channels:
            await callback_query.answer("Please select at least one channel first.")
            return
        
        # Get channel names for display
        db = SessionLocal()
        try:
            channels = db.query(Channel).filter(Channel.id.in_(selected_channels)).all()
            channel_names = [c.name for c in channels]
            
            text = f"""
⏰ **Choose Campaign Duration**

Selected Channels ({len(selected_channels)}):
{chr(10).join(f'• {name}' for name in channel_names)}

Choose how long you want your campaign to run:

💡 **Longer durations = better value with our bundles!**
"""
            
            keyboard = EnhancedUI.get_duration_selection_keyboard(selected_channels)
            await callback_query.message.edit_text(text, reply_markup=keyboard)
            await UserStates.selecting_duration.set()
            await callback_query.answer()
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in continue selection: {e}")
        await callback_query.answer("Error proceeding. Please try again.")

async def handle_duration_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle duration or bundle selection"""
    try:
        data_parts = callback_query.data.split('_', 2)
        duration_type = data_parts[0]  # 'duration' or 'bundle'
        identifier = data_parts[1]      # months or bundle_id
        selected_channels = json.loads(data_parts[2])
        
        user_id = callback_query.from_user.id
        user_flow.set_selected_channels(user_id, selected_channels)
        
        if duration_type == 'duration':
            months = int(identifier)
            bundle_id = None
        else:  # bundle
            bundle_id = identifier
            # Get bundle details to determine months
            db = SessionLocal()
            try:
                from database import Bundle
                bundle = db.query(Bundle).filter(Bundle.id == bundle_id).first()
                months = bundle.months if bundle else 1
            finally:
                db.close()
        
        # Create order
        order_data = await payment_system.create_payment_order(
            user_id=user_id,
            channel_ids=selected_channels,
            duration_months=months,
            bundle_id=bundle_id
        )
        
        # Show order confirmation
        text = f"""
📋 **Order Confirmation**

{await EnhancedUI.get_pricing_text(selected_channels, months, bundle_id)}

🚀 **Ready to proceed with payment?**

Your campaign will start automatically after payment confirmation.
"""
        
        keyboard = EnhancedUI.get_payment_confirmation_keyboard(order_data)
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await UserStates.confirming_order.set()
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in duration selection: {e}")
        await callback_query.answer("Error processing selection. Please try again.")

async def handle_pay_order(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle payment initiation"""
    try:
        order_id = callback_query.data.split('_')[-1]
        
        # Get order details
        db = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                await callback_query.answer("Order not found.")
                return
            
            order_data = {
                'order_id': order.id,
                'memo': order.payment_memo,
                'wallet_address': order.wallet_address,
                'amount_ton': order.total_amount_ton,
                'amount_usd': order.total_amount_usd,
                'expires_at': order.expires_at,
                'channels_count': len(order.channels),
                'duration_months': order.duration_months + order.bonus_months
            }
            
        finally:
            db.close()
        
        # Show payment instructions
        text = EnhancedUI.get_payment_instructions_text(order_data)
        keyboard = EnhancedUI.get_payment_instructions_keyboard(order.payment_memo, order.id)
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await UserStates.payment_pending.set()
        await callback_query.answer("Payment instructions sent! Follow the steps above.")
        
    except Exception as e:
        logger.error(f"Error initiating payment: {e}")
        await callback_query.answer("Error starting payment. Please try again.")

async def handle_payment_sent(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle user confirmation of payment"""
    try:
        order_id = callback_query.data.split('_')[-1]
        
        text = f"""
✅ **Payment Confirmation Received**

🔍 **Checking Payment on TON Blockchain...**

Order: `{order_id}`

⏳ We're automatically scanning the blockchain for your payment.
This usually takes 1-2 minutes.

You'll receive a notification as soon as your payment is confirmed and your campaign starts!

💡 **No need to wait here** - you can close this chat and we'll notify you when ready.
"""
        
        await callback_query.message.edit_text(text)
        await callback_query.answer("Payment tracking started!")
        await state.finish()
        
    except Exception as e:
        logger.error(f"Error handling payment confirmation: {e}")
        await callback_query.answer("Error processing confirmation. Please try again.")

async def handle_reset_channels(callback_query: types.CallbackQuery, state: FSMContext):
    """Reset channel selection"""
    user_id = callback_query.from_user.id
    user_flow.clear_user_data(user_id)
    
    keyboard = EnhancedUI.get_channel_selection_keyboard()
    text = """
📺 **Channel Selection** (Reset)

Select the channels where you want to advertise:

📌 Each channel costs 0.099 TON per month
💡 Select multiple channels for broader reach
"""
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer("Selection reset!")

# Register all handlers
def register_enhanced_handlers():
    """Register all enhanced handlers"""
    
    # Command handlers
    dp.register_message_handler(start_command, commands=['start'], state="*")
    
    # Channel selection handlers
    dp.register_callback_query_handler(
        handle_channel_toggle,
        lambda c: c.data.startswith('toggle_channel_'),
        state=UserStates.selecting_channels
    )
    
    dp.register_callback_query_handler(
        handle_view_pricing,
        lambda c: c.data == 'view_pricing',
        state=UserStates.selecting_channels
    )
    
    dp.register_callback_query_handler(
        handle_continue_selection,
        lambda c: c.data == 'continue_selection',
        state=UserStates.selecting_channels
    )
    
    dp.register_callback_query_handler(
        handle_reset_channels,
        lambda c: c.data == 'reset_channels',
        state="*"
    )
    
    # Duration selection handlers
    dp.register_callback_query_handler(
        handle_duration_selection,
        lambda c: c.data.startswith(('duration_', 'bundle_')),
        state=UserStates.selecting_duration
    )
    
    # Payment handlers
    dp.register_callback_query_handler(
        handle_pay_order,
        lambda c: c.data.startswith('pay_order_'),
        state=UserStates.confirming_order
    )
    
    dp.register_callback_query_handler(
        handle_payment_sent,
        lambda c: c.data.startswith('payment_sent_'),
        state=UserStates.payment_pending
    )
    
    # Navigation handlers
    dp.register_callback_query_handler(
        start_command,
        lambda c: c.data in ['back_to_channels', 'cancel_selection'],
        state="*"
    )
    
    # Register admin handlers
    register_admin_handlers(dp, bot)

async def on_startup(dp):
    """Initialize bot on startup"""
    logger.info("Starting Enhanced Telegram Ad Bot...")
    
    # Initialize database
    create_tables()
    init_default_data()
    
    # Register handlers
    register_enhanced_handlers()
    
    logger.info("Enhanced bot started successfully!")

async def on_shutdown(dp):
    """Cleanup on shutdown"""
    logger.info("Shutting down Enhanced Telegram Ad Bot...")
    await bot.close()
    await storage.close()

if __name__ == '__main__':
    from aiogram import executor
    
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )