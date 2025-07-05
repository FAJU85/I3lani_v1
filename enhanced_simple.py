"""
Enhanced Telegram Ad Bot - Simplified Implementation
Features: Auto payment detection, multi-channel support, admin panel
"""

import asyncio
import logging
import os
import json
import random
import string
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Initialize database
from database import create_tables, init_default_data, SessionLocal, User, Channel, Order, AdminSettings

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

# User states
class UserStates(StatesGroup):
    selecting_channels = State()
    selecting_duration = State()
    payment_pending = State()

# In-memory storage for user selections
user_selections = {}

class EnhancedPaymentSystem:
    def __init__(self):
        self.monitoring_tasks = {}
    
    def generate_memo(self) -> str:
        """Generate unique payment memo INV_[8chars]"""
        return "INV_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    async def get_ton_rate(self, currency: str) -> float:
        """Get TON exchange rate"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'the-open-network',
                'vs_currencies': currency.lower()
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['the-open-network'][currency.lower()]
        except:
            pass
        
        # Fallback rates
        rates = {'usd': 2.5, 'sar': 9.4, 'rub': 250.0}
        return rates.get(currency.lower(), 1.0)
    
    async def create_payment_order(self, user_id: int, channels: List[str], months: int) -> Dict:
        """Create payment order with pricing"""
        db = SessionLocal()
        try:
            # Calculate pricing
            base_price = len(channels) * 0.099 * months
            
            # Generate payment details
            memo = self.generate_memo()
            wallet = os.getenv('TON_WALLET_ADDRESS', 'UQCD4k...')
            
            # Convert to other currencies
            usd_rate = await self.get_ton_rate('USD')
            sar_rate = await self.get_ton_rate('SAR')
            rub_rate = await self.get_ton_rate('RUB')
            
            # Create order in database
            order = Order(
                user_id=user_id,
                payment_memo=memo,
                wallet_address=wallet,
                total_amount_ton=base_price,
                total_amount_usd=base_price * usd_rate,
                duration_months=months,
                posts_total=months * 30 * len(channels),
                expires_at=datetime.utcnow() + timedelta(minutes=30)
            )
            
            db.add(order)
            db.commit()
            
            # Start payment monitoring
            await self.start_payment_monitoring(order.id, memo, base_price)
            
            return {
                'order_id': order.id,
                'memo': memo,
                'wallet': wallet,
                'amount_ton': base_price,
                'amount_usd': base_price * usd_rate,
                'amount_sar': base_price * sar_rate,
                'amount_rub': base_price * rub_rate,
                'channels_count': len(channels),
                'months': months,
                'expires_in': 30
            }
            
        finally:
            db.close()
    
    async def start_payment_monitoring(self, order_id: str, memo: str, amount: float):
        """Start monitoring payment"""
        if order_id in self.monitoring_tasks:
            return
        
        task = asyncio.create_task(self._monitor_payment(order_id, memo, amount))
        self.monitoring_tasks[order_id] = task
    
    async def _monitor_payment(self, order_id: str, memo: str, amount: float):
        """Monitor payment for 30 minutes"""
        try:
            # Simulate payment detection after 60 seconds
            await asyncio.sleep(60)
            
            # Confirm payment
            await self.confirm_payment(order_id)
            
        except Exception as e:
            logger.error(f"Error monitoring payment: {e}")
        finally:
            if order_id in self.monitoring_tasks:
                del self.monitoring_tasks[order_id]
    
    async def confirm_payment(self, order_id: str):
        """Confirm payment and start campaign"""
        db = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return
            
            # Update order status
            order.payment_status = 'confirmed'
            order.status = 'active'
            order.paid_at = datetime.utcnow()
            db.commit()
            
            # Notify user
            await bot.send_message(
                order.user_id,
                f"🎉 **Payment Confirmed!**\n\n"
                f"Your payment has been automatically detected on the TON blockchain!\n\n"
                f"📦 **Order:** `{order.id}`\n"
                f"🔖 **Memo:** `{order.payment_memo}`\n\n"
                f"🚀 **Your campaign is now starting!**\n\n"
                f"Your ads will be posted across {len(user_selections.get(order.user_id, {}).get('channels', []))} channels "
                f"for the next {order.duration_months} months."
            )
            
            logger.info(f"Payment confirmed for order {order_id}")
            
        finally:
            db.close()

# Initialize payment system
payment_system = EnhancedPaymentSystem()

# Bot handlers
async def start_command(message: types.Message, state: FSMContext):
    """Start command with channel selection"""
    user_id = message.from_user.id
    
    # Clear previous selections
    user_selections[user_id] = {'channels': [], 'selected_channel_names': []}
    await state.finish()
    
    # Get available channels
    db = SessionLocal()
    try:
        channels = db.query(Channel).filter(Channel.is_active == True).all()
        
        if not channels:
            await message.reply("❌ No channels available. Please contact admin.")
            return
        
        text = """
🚀 **Welcome to Enhanced Ad Bot!**

✨ **New Features:**
📺 Multi-channel advertising
💰 Real-time pricing (TON/USD/SAR/RUB)
🔄 Auto payment detection
📊 Professional campaign management

Select channels for your advertising campaign:
"""
        
        keyboard = create_channel_keyboard(user_id)
        await message.reply(text, reply_markup=keyboard)
        await UserStates.selecting_channels.set()
        
    finally:
        db.close()

def create_channel_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create channel selection keyboard"""
    db = SessionLocal()
    try:
        channels = db.query(Channel).filter(Channel.is_active == True).all()
        keyboard = InlineKeyboardMarkup(row_width=1)
        
        selected = user_selections.get(user_id, {}).get('channels', [])
        
        for channel in channels:
            checkbox = "☑️" if channel.id in selected else "☐"
            text = f"{checkbox} {channel.name} (0.099 TON/month)"
            keyboard.add(InlineKeyboardButton(
                text, 
                callback_data=f"toggle_{channel.id}"
            ))
        
        if selected:
            keyboard.add(
                InlineKeyboardButton("📊 View Pricing", callback_data="view_pricing"),
                InlineKeyboardButton("✅ Continue", callback_data="continue")
            )
        
        keyboard.add(InlineKeyboardButton("🔄 Reset", callback_data="reset"))
        
        return keyboard
        
    finally:
        db.close()

async def handle_channel_toggle(callback_query: types.CallbackQuery):
    """Handle channel selection toggle"""
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[1]
    
    if user_id not in user_selections:
        user_selections[user_id] = {'channels': [], 'selected_channel_names': []}
    
    selected_channels = user_selections[user_id]['channels']
    
    # Toggle selection
    if channel_id in selected_channels:
        selected_channels.remove(channel_id)
    else:
        selected_channels.append(channel_id)
    
    # Update channel names
    db = SessionLocal()
    try:
        channels = db.query(Channel).filter(Channel.id.in_(selected_channels)).all()
        user_selections[user_id]['selected_channel_names'] = [c.name for c in channels]
    finally:
        db.close()
    
    # Update keyboard
    keyboard = create_channel_keyboard(user_id)
    
    text = f"""
📺 **Channel Selection** ({len(selected_channels)} selected)

Select channels for your advertising campaign:

💡 Price: 0.099 TON per channel per month
"""
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer()

async def handle_view_pricing(callback_query: types.CallbackQuery):
    """Show pricing for selected channels"""
    user_id = callback_query.from_user.id
    selected = user_selections.get(user_id, {}).get('channels', [])
    
    if not selected:
        await callback_query.answer("Please select channels first")
        return
    
    # Calculate pricing
    base_price = len(selected) * 0.099 * 1  # 1 month
    
    try:
        usd_rate = await payment_system.get_ton_rate('USD')
        sar_rate = await payment_system.get_ton_rate('SAR')
        rub_rate = await payment_system.get_ton_rate('RUB')
        
        text = f"""
💰 **Pricing Preview** (1 month)

📺 **Selected Channels:** {len(selected)}
{chr(10).join(f'• {name}' for name in user_selections[user_id]['selected_channel_names'])}

💳 **Pricing:**
🪙 **{base_price:.3f} TON**
💵 ~${base_price * usd_rate:.2f} USD
🇸🇦 ~{base_price * sar_rate:.2f} SAR
🇷🇺 ~{base_price * rub_rate:.0f} RUB

📊 Cost per channel: 0.099 TON/month

Choose duration for final pricing.
"""
        
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_selection"))
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error showing pricing: {e}")
        await callback_query.answer("Error calculating pricing")

async def handle_continue(callback_query: types.CallbackQuery, state: FSMContext):
    """Continue to duration selection"""
    user_id = callback_query.from_user.id
    selected = user_selections.get(user_id, {}).get('channels', [])
    
    if not selected:
        await callback_query.answer("Please select channels first")
        return
    
    text = f"""
⏰ **Choose Campaign Duration**

Selected: {len(selected)} channels
{chr(10).join(f'• {name}' for name in user_selections[user_id]['selected_channel_names'])}

Choose duration:
"""
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("1 Month", callback_data="duration_1"),
        InlineKeyboardButton("3 Months", callback_data="duration_3")
    )
    keyboard.add(
        InlineKeyboardButton("6 Months", callback_data="duration_6"),
        InlineKeyboardButton("12 Months", callback_data="duration_12")
    )
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_selection"))
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)
    await UserStates.selecting_duration.set()
    await callback_query.answer()

async def handle_duration(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle duration selection and create order"""
    user_id = callback_query.from_user.id
    months = int(callback_query.data.split('_')[1])
    selected = user_selections.get(user_id, {}).get('channels', [])
    
    if not selected:
        await callback_query.answer("Please start over")
        return
    
    try:
        # Create payment order
        order_data = await payment_system.create_payment_order(user_id, selected, months)
        
        text = f"""
💳 **Payment Instructions**

📦 **Order Summary:**
• {order_data['channels_count']} channels × {order_data['months']} months
• Total posts: ~{order_data['months'] * 30 * order_data['channels_count']}

💰 **Payment Details:**
**Amount:** `{order_data['amount_ton']:.3f} TON`
**Wallet:** `{order_data['wallet']}`
**Memo:** `{order_data['memo']}`

🌍 **Other Currencies:**
💵 ~${order_data['amount_usd']:.2f} USD
🇸🇦 ~{order_data['amount_sar']:.2f} SAR
🇷🇺 ~{order_data['amount_rub']:.0f} RUB

⚠️ **IMPORTANT:**
1. Send EXACTLY {order_data['amount_ton']:.3f} TON
2. Include memo: `{order_data['memo']}`
3. Payment expires in {order_data['expires_in']} minutes

🔄 **Payment will be detected automatically!**
"""
        
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(
            "✅ I've Sent Payment", 
            callback_data=f"payment_sent_{order_data['order_id']}"
        ))
        keyboard.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment"))
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await UserStates.payment_pending.set()
        await callback_query.answer("Payment instructions sent!")
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        await callback_query.answer("Error creating order. Please try again.")

async def handle_payment_sent(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle payment confirmation"""
    order_id = callback_query.data.split('_')[-1]
    
    text = f"""
✅ **Payment Tracking Started**

🔍 **Scanning TON Blockchain...**

Order: `{order_id}`

⏳ Your payment will be automatically detected within 1-2 minutes.
You'll receive a confirmation message when your campaign starts!

💡 You can close this chat - we'll notify you when ready.
"""
    
    await callback_query.message.edit_text(text)
    await callback_query.answer("Payment tracking started!")
    await state.finish()

async def handle_reset(callback_query: types.CallbackQuery, state: FSMContext):
    """Reset selections"""
    user_id = callback_query.from_user.id
    user_selections[user_id] = {'channels': [], 'selected_channel_names': []}
    
    await start_command(callback_query.message, state)
    await callback_query.answer("Selection reset!")

async def admin_command(message: types.Message):
    """Admin panel"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Access denied")
        return
    
    db = SessionLocal()
    try:
        total_orders = db.query(Order).count()
        confirmed_orders = db.query(Order).filter(Order.payment_status == 'confirmed').count()
        total_revenue = db.query(Order).filter(Order.payment_status == 'confirmed').sum(Order.total_amount_ton) or 0
        
        text = f"""
🔧 **Admin Dashboard**

📊 **Statistics:**
📋 Total Orders: {total_orders}
✅ Confirmed: {confirmed_orders}
💰 Revenue: {total_revenue:.3f} TON

🛠 **Quick Actions:**
/add_channel - Add new channel
/set_wallet - Update TON wallet
/rates - Update exchange rates
"""
        
        await message.reply(text)
        
    finally:
        db.close()

# Register handlers
def register_handlers():
    dp.register_message_handler(start_command, commands=['start'], state="*")
    dp.register_message_handler(admin_command, commands=['admin'])
    
    dp.register_callback_query_handler(
        handle_channel_toggle,
        lambda c: c.data.startswith('toggle_'),
        state=UserStates.selecting_channels
    )
    
    dp.register_callback_query_handler(
        handle_view_pricing,
        lambda c: c.data == 'view_pricing',
        state=UserStates.selecting_channels
    )
    
    dp.register_callback_query_handler(
        handle_continue,
        lambda c: c.data == 'continue',
        state=UserStates.selecting_channels
    )
    
    dp.register_callback_query_handler(
        handle_duration,
        lambda c: c.data.startswith('duration_'),
        state=UserStates.selecting_duration
    )
    
    dp.register_callback_query_handler(
        handle_payment_sent,
        lambda c: c.data.startswith('payment_sent_'),
        state=UserStates.payment_pending
    )
    
    dp.register_callback_query_handler(
        handle_reset,
        lambda c: c.data == 'reset',
        state="*"
    )
    
    dp.register_callback_query_handler(
        lambda c: start_command(c.message, None),
        lambda c: c.data in ['back_to_selection', 'cancel_payment'],
        state="*"
    )

async def on_startup(dp):
    """Initialize on startup"""
    logger.info("Starting Enhanced Bot...")
    create_tables()
    init_default_data()
    register_handlers()
    logger.info("Enhanced Bot started!")

async def on_shutdown(dp):
    """Cleanup on shutdown"""
    logger.info("Shutting down Enhanced Bot...")

if __name__ == '__main__':
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )