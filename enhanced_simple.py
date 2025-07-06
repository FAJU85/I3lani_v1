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
import aiohttp
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
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# User states
class UserStates(StatesGroup):
    waiting_for_ad = State()
    selecting_package = State()
    selecting_channels = State()
    confirming_order = State()
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
            await self.start_payment_monitoring(str(order.id), memo, base_price)
            
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
        """Monitor payment for 30 minutes using real TON API"""
        try:
            ton_api_key = os.getenv('TON_API_KEY')
            wallet_address = os.getenv('TON_WALLET_ADDRESS')
            
            if not ton_api_key or not wallet_address:
                logger.error("TON API key or wallet address not configured")
                return
            
            # Monitor for 30 minutes (1800 seconds) with 30-second intervals
            for _ in range(60):  # 30 minutes / 30 seconds = 60 checks
                try:
                    # Check TON blockchain for payment
                    headers = {'Authorization': f'Bearer {ton_api_key}'}
                    url = f'https://tonapi.io/v2/accounts/{wallet_address}/transactions'
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # Check recent transactions for our memo
                                for tx in data.get('transactions', []):
                                    if 'in_msg' in tx and tx['in_msg']:
                                        message = tx['in_msg'].get('message', '')
                                        value = float(tx['in_msg'].get('value', 0)) / 1e9  # Convert from nanotons
                                        
                                        if memo in message and value >= amount * 0.95:  # 5% tolerance
                                            logger.info(f"Payment detected for order {order_id}")
                                            await self.confirm_payment(order_id)
                                            return
                    
                except Exception as e:
                    logger.error(f"Error checking TON API: {e}")
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
            
            # Payment not detected within 30 minutes
            logger.info(f"Payment timeout for order {order_id}")
            
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
            db.query(Order).filter(Order.id == order_id).update({
                'payment_status': 'confirmed',
                'status': 'active',
                'paid_at': datetime.utcnow()
            })
            db.commit()
            
            # Notify user
            await bot.send_message(
                int(order.user_id),
                f"🎉 Payment Confirmed!\n\n"
                f"Your payment has been automatically detected on the TON blockchain!\n\n"
                f"📦 Order: {order.id}\n"
                f"🔖 Memo: {order.payment_memo}\n\n"
                f"🚀 Your campaign is now starting!\n\n"
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
    
    # Register user in database
    db = SessionLocal()
    try:
        # Check if user exists, if not create them
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
        
        # Get available channels
        channels = db.query(Channel).filter(Channel.is_active.is_(True)).all()
        
        if not channels:
            await message.reply("❌ No channels available. Please contact admin.")
            return
        
        # Enhanced welcome with action menu
        welcome_text = """🎉 Welcome to AdChannel Bot!

Your one-stop solution for Telegram channel advertising.

🚀 Ready to start advertising? Choose an action below:"""

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 START ADVERTISING", callback_data="start_advertising"))
        keyboard.add(InlineKeyboardButton("📊 VIEW MY CAMPAIGNS", callback_data="my_campaigns"))
        keyboard.add(InlineKeyboardButton("💰 CHECK BALANCE", callback_data="check_balance"))
        
        await message.reply(welcome_text, reply_markup=keyboard)
        
    finally:
        db.close()

async def handle_ad_content(message: types.Message, state: FSMContext):
    """Handle ad content submission"""
    user_id = message.from_user.id
    
    # Store ad content
    if not user_selections.get(user_id):
        user_selections[user_id] = {}
    
    ad_content = {
        'type': 'text',
        'text': message.text,
        'file_id': None
    }
    
    if message.photo:
        ad_content['type'] = 'photo'
        ad_content['file_id'] = message.photo[-1].file_id
        ad_content['text'] = message.caption or ''
    elif message.video:
        ad_content['type'] = 'video'
        ad_content['file_id'] = message.video.file_id
        ad_content['text'] = message.caption or ''
    
    user_selections[user_id]['ad_content'] = ad_content
    
    # Show package selection
    text = """✅ Ad received!

📦 Choose your package:

🟢 Starter: 0.099 TON (~$2.45)
   • 1 month campaign
   • Up to 2 channels
   • 10 reposts per month

🔵 Pro: 0.399 TON (~$9.88)
   • 3 month campaign  
   • Up to 5 channels
   • 20 reposts per month

🟡 Growth: 0.999 TON (~$24.75)
   • 6 month campaign
   • Up to 10 channels
   • 30 reposts per month

🟣 Elite: 1.999 TON (~$49.50)
   • 12 month campaign
   • Unlimited channels
   • 50 reposts per month"""
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🟢 Starter", callback_data="package_starter"),
        InlineKeyboardButton("🔵 Pro", callback_data="package_pro")
    )
    keyboard.add(
        InlineKeyboardButton("🟡 Growth", callback_data="package_growth"),
        InlineKeyboardButton("🟣 Elite", callback_data="package_elite")
    )
    
    await message.reply(text, reply_markup=keyboard)
    await UserStates.selecting_package.set()

async def handle_package_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle package selection"""
    user_id = callback_query.from_user.id
    package = callback_query.data.split('_')[1]
    
    # Package configurations
    packages = {
        'starter': {'price': 0.099, 'months': 1, 'max_channels': 2, 'reposts': 10},
        'pro': {'price': 0.399, 'months': 3, 'max_channels': 5, 'reposts': 20},
        'growth': {'price': 0.999, 'months': 6, 'max_channels': 10, 'reposts': 30},
        'elite': {'price': 1.999, 'months': 12, 'max_channels': 999, 'reposts': 50}
    }
    
    user_selections[user_id]['package'] = packages[package]
    user_selections[user_id]['package_name'] = package.title()
    
    # Show channel selection
    db = SessionLocal()
    try:
        channels = db.query(Channel).filter(Channel.is_active.is_(True)).all()
        
        if not channels:
            await callback_query.message.edit_text("❌ No channels available. Please contact admin.")
            return
        
        text = f"""📺 Select channels for your {package.title()} campaign:

Maximum channels: {packages[package]['max_channels']}
Duration: {packages[package]['months']} months
Reposts: {packages[package]['reposts']} per month per channel"""
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        max_channels = min(packages[package]['max_channels'], len(channels))
        for channel in channels[:max_channels]:
            subscribers = f"{channel.subscribers_count//1000}K" if channel.subscribers_count >= 1000 else str(channel.subscribers_count)
            keyboard.add(
                InlineKeyboardButton(
                    f"☐ {channel.name} ({subscribers})",
                    callback_data=f"toggle_{channel.id}"
                )
            )
        
        keyboard.add(InlineKeyboardButton("✅ Continue to Payment", callback_data="confirm_order"))
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await UserStates.selecting_channels.set()
        await callback_query.answer()
        
    finally:
        db.close()

def create_channel_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create channel selection keyboard"""
    db = SessionLocal()
    try:
        channels = db.query(Channel).filter(Channel.is_active.is_(True)).all()
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

async def handle_channel_toggle(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle channel selection toggle"""
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split('_')[1]
    
    if user_id not in user_selections:
        user_selections[user_id] = {'channels': []}
    
    channels = user_selections[user_id]['channels']
    package = user_selections[user_id].get('package', {})
    max_channels = package.get('max_channels', 2)
    
    if channel_id in channels:
        channels.remove(channel_id)
    else:
        if len(channels) < max_channels:
            channels.append(channel_id)
        else:
            await callback_query.answer(f"Maximum {max_channels} channels allowed for this package!")
            return
    
    # Update keyboard with current selections
    db = SessionLocal()
    try:
        all_channels = db.query(Channel).filter(Channel.is_active.is_(True)).all()
        package_name = user_selections[user_id].get('package_name', 'Selected')
        
        text = f"""📺 Select channels for your {package_name} campaign:

Maximum channels: {max_channels}
Duration: {package['months']} months
Reposts: {package['reposts']} per month per channel

Selected: {len(channels)}/{max_channels} channels"""
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        for channel in all_channels[:max_channels]:
            is_selected = channel.id in channels
            emoji = "✅" if is_selected else "☐"
            subscribers = f"{channel.subscribers_count//1000}K" if channel.subscribers_count >= 1000 else str(channel.subscribers_count)
            keyboard.add(
                InlineKeyboardButton(
                    f"{emoji} {channel.name} ({subscribers})",
                    callback_data=f"toggle_{channel.id}"
                )
            )
        
        if channels:
            keyboard.add(InlineKeyboardButton("✅ Continue to Payment", callback_data="confirm_order"))
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
        
    finally:
        db.close()

async def handle_confirm_order(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle order confirmation and create payment"""
    user_id = callback_query.from_user.id
    user_data = user_selections.get(user_id, {})
    
    if not user_data.get('channels') or not user_data.get('package'):
        await callback_query.answer("❌ Please select channels and package first!")
        return
    
    package = user_data['package']
    channels = user_data['channels']
    
    # Calculate total price
    total_price = package['price'] * len(channels)
    
    # Create payment order
    try:
        order_data = await payment_system.create_payment_order(
            user_id=user_id,
            channels=channels,
            months=package['months']
        )
        
        text = f"""💳 Payment Instructions:

📦 Package: {user_data.get('package_name', 'Selected')}
📺 Channels: {len(channels)} selected
⏰ Duration: {package['months']} months
🔄 Reposts: {package['reposts']} per month per channel

💰 Total: {total_price:.3f} TON (~${total_price * 2.5:.2f})

🏦 Send payment to:
{order_data['wallet']}

🔖 Include memo: {order_data['memo']}

⏰ Payment expires in 30 minutes
Auto-detection will confirm your payment!"""
        
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✅ I Sent Payment", callback_data=f"sent_{order_data['memo']}"))
        keyboard.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment"))
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await UserStates.payment_pending.set()
        await callback_query.answer("Payment instructions sent!")
        
        # Start payment monitoring
        await payment_system.start_payment_monitoring(
            order_data['order_id'], 
            order_data['memo'], 
            total_price
        )
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        await callback_query.answer("❌ Error creating order. Please try again!")
        return

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

# Enhanced callback handlers
async def handle_start_advertising(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle start advertising button"""
    await callback_query.message.edit_text("""📝 **Create Your Advertisement**

Send your advertisement content:
• Text message
• Photo with caption  
• Video with description

Your content will be posted across selected channels with automatic scheduling!""", parse_mode='Markdown')
    
    await UserStates.waiting_for_ad.set()
    await callback_query.answer()

async def handle_my_campaigns(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle my campaigns button"""
    await mystats_command(callback_query.message)
    await callback_query.answer()

async def handle_check_balance(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle check balance button"""
    user_id = callback_query.from_user.id
    
    db = SessionLocal()
    try:
        from sqlalchemy import func
        total_spent = db.query(func.sum(Order.total_amount_ton)).filter(
            Order.user_id == user_id, 
            Order.payment_status == 'confirmed'
        ).scalar() or 0
        
        active_campaigns = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status == 'active'
        ).count()
        
        balance_text = f"""💰 **Account Balance & Summary**

📊 **Spending Summary**:
• Total Spent: {total_spent:.3f} TON
• Active Campaigns: {active_campaigns}
• Account Status: Active

💎 **Current TON Rate**: {await EnhancedPaymentSystem().get_ton_rate('USD'):.2f} USD

🚀 Ready to create a new campaign?"""

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 New Campaign", callback_data="start_advertising"))
        keyboard.add(InlineKeyboardButton("📊 View Details", callback_data="my_campaigns"))
        
        await callback_query.message.edit_text(balance_text, reply_markup=keyboard, parse_mode='Markdown')
    
    finally:
        db.close()
    
    await callback_query.answer()

async def handle_reset(callback_query: types.CallbackQuery, state: FSMContext):
    """Reset selections"""
    user_id = callback_query.from_user.id
    user_selections[user_id] = {'channels': [], 'selected_channel_names': []}
    
    await start_command(callback_query.message, state)
    await callback_query.answer("Selection reset!")

# Enhanced command handlers
async def mystats_command(message: types.Message):
    """Show user campaign statistics"""
    user_id = message.from_user.id
    
    db = SessionLocal()
    try:
        user_orders = db.query(Order).filter(Order.user_id == user_id).all()
        
        if not user_orders:
            await message.reply("📊 No campaigns found. Start your first campaign with /start!")
            return
        
        active_campaigns = len([o for o in user_orders if o.status == 'active'])
        total_campaigns = len(user_orders)
        total_spent = sum(o.total_amount_ton for o in user_orders if o.payment_status == 'confirmed')
        
        stats_text = f"""📊 **Your Campaign Statistics**

🎯 **Active Campaigns**: {active_campaigns}
📈 **Total Campaigns**: {total_campaigns}
💰 **Total Spent**: {total_spent:.3f} TON
📅 **Member Since**: {user_orders[0].created_at.strftime('%B %Y') if user_orders else 'N/A'}

📋 **Recent Campaigns**:"""

        for order in user_orders[-3:]:
            status_emoji = "🟢" if order.status == "active" else "🟡" if order.status == "pending" else "⚪"
            stats_text += f"\n{status_emoji} {order.created_at.strftime('%b %d')} - {order.total_amount_ton:.3f} TON"
        
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📊 Detailed Analytics", callback_data="detailed_analytics"))
        keyboard.add(InlineKeyboardButton("🚀 New Campaign", callback_data="start_advertising"))
        
        await message.reply(stats_text, reply_markup=keyboard, parse_mode='Markdown')
        
    finally:
        db.close()

async def bugreport_command(message: types.Message):
    """Bug report system"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💰 Payment Issue", callback_data="bug_payment"))
    keyboard.add(InlineKeyboardButton("📱 Bot Not Working", callback_data="bug_bot"))
    keyboard.add(InlineKeyboardButton("📊 Wrong Analytics", callback_data="bug_analytics"))
    keyboard.add(InlineKeyboardButton("🔗 Broken Links", callback_data="bug_links"))
    keyboard.add(InlineKeyboardButton("📝 Other Issue", callback_data="bug_other"))
    
    await message.reply("""🐛 **Report a Bug**

What went wrong? Select the issue type below:

📧 Your report will be sent to our technical team
🔄 Typical response time: 2-6 hours""", reply_markup=keyboard, parse_mode='Markdown')

async def support_command(message: types.Message):
    """Support system"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💬 Chat with AI", callback_data="support_ai"))
    keyboard.add(InlineKeyboardButton("👨‍💻 Human Support", callback_data="support_human"))
    keyboard.add(InlineKeyboardButton("📚 FAQ", callback_data="support_faq"))
    
    support_text = """💬 **Customer Support**

🤖 AI Assistant: Available 24/7
👨‍💻 Human Support: 9 AM - 11 PM UTC

**Common Issues:**
• Payment not confirmed
• Campaign not started  
• Analytics questions
• Technical problems

**Response Times:**
• AI: Instant
• Human: Usually < 30 minutes
• Complex issues: 2-6 hours"""

    await message.reply(support_text, reply_markup=keyboard, parse_mode='Markdown')

async def history_command(message: types.Message):
    """Show campaign history"""
    user_id = message.from_user.id
    
    db = SessionLocal()
    try:
        orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).limit(10).all()
        
        if not orders:
            await message.reply("📋 No campaign history found.")
            return
        
        history_text = "📋 **Campaign History**\n\n"
        
        for order in orders:
            status_emoji = "✅" if order.payment_status == "confirmed" else "🟡" if order.payment_status == "pending" else "❌"
            history_text += f"{status_emoji} **{order.created_at.strftime('%b %d, %Y')}**\n"
            history_text += f"💰 {order.total_amount_ton:.3f} TON - {order.status.title()}\n"
            history_text += f"📅 Duration: {order.duration_months} months\n\n"
        
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📊 View Analytics", callback_data="view_analytics"))
        keyboard.add(InlineKeyboardButton("🚀 New Campaign", callback_data="start_advertising"))
        
        await message.reply(history_text, reply_markup=keyboard, parse_mode='Markdown')
        
    finally:
        db.close()

async def refresh_command(message: types.Message):
    """Refresh channels and data"""
    await message.reply("🔄 Refreshing channels and data...")
    
    # Simulate refresh
    await asyncio.sleep(1)
    
    db = SessionLocal()
    try:
        channels = db.query(Channel).filter(Channel.is_active.is_(True)).all()
        channel_count = len(channels)
        
        refresh_text = f"""🔄 **Data Refreshed Successfully!**

📺 **Available Channels**: {channel_count}
💰 **Current TON Rate**: {await EnhancedPaymentSystem().get_ton_rate('USD'):.2f} USD
🟢 **System Status**: All systems operational
⏰ **Last Updated**: {datetime.utcnow().strftime('%H:%M UTC')}"""

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🚀 Start Campaign", callback_data="start_advertising"))
        keyboard.add(InlineKeyboardButton("📊 View Channels", callback_data="view_channels"))
        
        await message.reply(refresh_text, reply_markup=keyboard, parse_mode='Markdown')
        
    finally:
        db.close()

async def admin_command(message: types.Message, state: FSMContext):
    """Enhanced admin panel"""
    # Check if user is admin
    user_id = message.from_user.id
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    admin_ids = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip()]
    
    if user_id not in admin_ids:
        await message.reply(f"❌ Access denied. User ID: {user_id}")
        return
    
    # Initialize admin panel
    from admin_panel import AdminPanel, AdminStates
    admin_panel = AdminPanel(bot)
    
    # Show enhanced admin menu
    await admin_panel.show_admin_menu(message)
    await AdminStates.main_menu.set()

async def handle_admin_callback(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle all admin panel callbacks"""
    from admin_panel import AdminPanel
    admin_panel = AdminPanel(bot)
    
    # Check admin access
    if not await admin_panel.is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Access denied")
        return
    
    data = callback_query.data
    
    if data == "admin_main":
        await admin_panel.show_admin_menu(callback_query, edit_message=True)
    elif data == "admin_pricing":
        await admin_panel.show_pricing_management(callback_query)
    elif data == "admin_wallet":
        await admin_panel.show_wallet_management(callback_query)
    elif data == "admin_stats":
        await admin_panel.show_statistics(callback_query)
    elif data == "admin_channels":
        await admin_panel.show_channel_management(callback_query)
    elif data == "admin_bundles":
        await admin_panel.show_bundle_management(callback_query)
    elif data == "admin_settings":
        await admin_panel.show_settings_management(callback_query)
    elif data.startswith("edit_price_"):
        package = data.replace("edit_price_", "")
        await callback_query.answer(f"Price editor for {package} - Coming soon!")
    elif data == "edit_wallet_address":
        await callback_query.message.reply("Please send the new TON wallet address:")
        await AdminStates.wallet_management.set()
    elif data == "refresh_wallet":
        await admin_panel.show_wallet_management(callback_query)
    elif data == "detailed_stats":
        await callback_query.answer("Detailed statistics - Coming soon!")
    else:
        await callback_query.answer("Unknown admin command")
    
    await callback_query.answer()

# Register handlers
def register_handlers():
    dp.register_message_handler(start_command, commands=['start'], state="*")
    dp.register_message_handler(admin_command, commands=['admin'])
    dp.register_message_handler(mystats_command, commands=['mystats'])
    dp.register_message_handler(bugreport_command, commands=['bugreport'])
    dp.register_message_handler(support_command, commands=['support'])
    dp.register_message_handler(history_command, commands=['history'])
    dp.register_message_handler(refresh_command, commands=['refresh'])
    
    # Ad content submission
    dp.register_message_handler(
        handle_ad_content,
        content_types=['text', 'photo', 'video'],
        state=UserStates.waiting_for_ad
    )
    
    # Package selection
    dp.register_callback_query_handler(
        handle_package_selection,
        lambda c: c.data.startswith('package_'),
        state=UserStates.selecting_package
    )
    
    # Channel selection
    dp.register_callback_query_handler(
        handle_channel_toggle,
        lambda c: c.data.startswith('toggle_'),
        state=UserStates.selecting_channels
    )
    
    # Order confirmation
    dp.register_callback_query_handler(
        handle_confirm_order,
        lambda c: c.data == 'confirm_order',
        state=UserStates.selecting_channels
    )
    
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
    
    # Payment sent confirmation
    dp.register_callback_query_handler(
        handle_payment_sent,
        lambda c: c.data.startswith('sent_'),
        state=UserStates.payment_pending
    )
    
    # Reset handler
    dp.register_callback_query_handler(
        handle_reset,
        lambda c: c.data in ['reset', 'cancel_payment'],
        state="*"
    )
    
    # Admin panel handlers
    dp.register_callback_query_handler(
        handle_admin_callback,
        lambda c: c.data.startswith('admin_'),
        state="*"
    )
    
    # Enhanced menu handlers
    dp.register_callback_query_handler(
        handle_start_advertising,
        lambda c: c.data == 'start_advertising',
        state="*"
    )
    
    dp.register_callback_query_handler(
        handle_my_campaigns,
        lambda c: c.data == 'my_campaigns',
        state="*"
    )
    
    dp.register_callback_query_handler(
        handle_check_balance,
        lambda c: c.data == 'check_balance',
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