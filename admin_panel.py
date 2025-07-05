"""
Enhanced Admin Panel for Telegram Ad Bot
Supports dynamic pricing, channel management, and bundle configuration
"""

from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import SessionLocal, AdminSettings, Channel, Bundle, Order, User
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AdminStates(StatesGroup):
    main_menu = State()
    channel_management = State()
    add_channel = State()
    edit_channel = State()
    bundle_management = State()
    add_bundle = State()
    edit_bundle = State()
    settings_management = State()
    edit_setting = State()

class AdminPanel:
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user and user.is_admin
        finally:
            db.close()
    
    async def show_admin_menu(self, message_or_query, edit_message: bool = False):
        """Show main admin menu"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("📊 Dashboard", callback_data="admin_dashboard"),
            InlineKeyboardButton("📺 Channels", callback_data="admin_channels")
        )
        keyboard.add(
            InlineKeyboardButton("📦 Bundles", callback_data="admin_bundles"),
            InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
        )
        keyboard.add(
            InlineKeyboardButton("💰 Payments", callback_data="admin_payments"),
            InlineKeyboardButton("📈 Analytics", callback_data="admin_analytics")
        )
        keyboard.add(
            InlineKeyboardButton("🔄 Refresh Rates", callback_data="admin_refresh_rates")
        )
        
        text = """
🔧 **Admin Panel**

Welcome to the administrative control panel.
Choose an option to manage your bot:

📊 **Dashboard** - Overview and statistics
📺 **Channels** - Manage advertising channels
📦 **Bundles** - Configure pricing bundles
⚙️ **Settings** - Bot configuration
💰 **Payments** - Payment monitoring
📈 **Analytics** - Performance metrics
"""
        
        if edit_message and hasattr(message_or_query, 'message'):
            await message_or_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await message_or_query.reply(text, reply_markup=keyboard, parse_mode="Markdown")
    
    async def show_dashboard(self, callback_query: types.CallbackQuery):
        """Show admin dashboard with statistics"""
        db = SessionLocal()
        try:
            # Get statistics
            total_users = db.query(User).count()
            total_orders = db.query(Order).count()
            active_orders = db.query(Order).filter(Order.status == 'active').count()
            total_revenue = db.query(Order).filter(Order.payment_status == 'confirmed').sum(Order.total_amount_ton) or 0
            
            # Recent orders
            recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
            
            text = f"""
📊 **Admin Dashboard**

👥 **Users:** {total_users}
📋 **Total Orders:** {total_orders}
🟢 **Active Campaigns:** {active_orders}
💰 **Total Revenue:** {total_revenue:.3f} TON

📋 **Recent Orders:**
"""
            
            for order in recent_orders:
                status_emoji = {
                    'pending': '⏳',
                    'confirmed': '✅',
                    'active': '🚀',
                    'completed': '🎯',
                    'expired': '❌'
                }.get(order.payment_status, '❓')
                
                text += f"{status_emoji} {order.payment_memo} - {order.total_amount_ton:.3f} TON\n"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
            
            await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
        finally:
            db.close()
    
    async def show_channel_management(self, callback_query: types.CallbackQuery):
        """Show channel management interface"""
        db = SessionLocal()
        try:
            channels = db.query(Channel).all()
            
            text = "📺 **Channel Management**\n\n"
            
            if channels:
                for channel in channels:
                    status = "🟢" if channel.is_active else "🔴"
                    text += f"{status} **{channel.name}**\n"
                    text += f"   ID: `{channel.channel_id}`\n"
                    text += f"   Price: {channel.price_per_month:.3f} TON/month\n"
                    text += f"   Subscribers: {channel.subscribers_count:,}\n\n"
            else:
                text += "No channels configured yet.\n\n"
            
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton("➕ Add Channel", callback_data="admin_add_channel"),
                InlineKeyboardButton("✏️ Edit Channel", callback_data="admin_edit_channel")
            )
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
            
            await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
        finally:
            db.close()
    
    async def show_bundle_management(self, callback_query: types.CallbackQuery):
        """Show bundle management interface"""
        db = SessionLocal()
        try:
            bundles = db.query(Bundle).all()
            
            text = "📦 **Bundle Management**\n\n"
            
            if bundles:
                for bundle in bundles:
                    status = "🟢" if bundle.is_active else "🔴"
                    text += f"{status} **{bundle.name}**\n"
                    text += f"   Duration: {bundle.months} months"
                    if bundle.bonus_months > 0:
                        text += f" + {bundle.bonus_months} free"
                    text += "\n"
                    text += f"   Discount: {bundle.discount_percent}%\n"
                    text += f"   Channels: {bundle.min_channels}-{bundle.max_channels}\n\n"
            else:
                text += "No bundles configured yet.\n\n"
            
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton("➕ Add Bundle", callback_data="admin_add_bundle"),
                InlineKeyboardButton("✏️ Edit Bundle", callback_data="admin_edit_bundle")
            )
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
            
            await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
        finally:
            db.close()
    
    async def show_settings_management(self, callback_query: types.CallbackQuery):
        """Show settings management interface"""
        db = SessionLocal()
        try:
            settings = db.query(AdminSettings).all()
            
            text = "⚙️ **Bot Settings**\n\n"
            
            for setting in settings:
                text += f"**{setting.key.replace('_', ' ').title()}:**\n"
                text += f"   Value: `{setting.value}`\n"
                text += f"   {setting.description}\n\n"
            
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton("💳 Update Wallet", callback_data="admin_update_wallet"),
                InlineKeyboardButton("⏰ Payment Timeout", callback_data="admin_update_timeout")
            )
            keyboard.add(
                InlineKeyboardButton("🤖 Auto Approval", callback_data="admin_toggle_auto"),
                InlineKeyboardButton("🔙 Back", callback_data="admin_main")
            )
            
            await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
        finally:
            db.close()
    
    async def show_payment_monitoring(self, callback_query: types.CallbackQuery):
        """Show payment monitoring interface"""
        db = SessionLocal()
        try:
            from database import PaymentTracking
            
            # Get recent payments
            payments = db.query(PaymentTracking).order_by(PaymentTracking.created_at.desc()).limit(10).all()
            
            text = "💰 **Payment Monitoring**\n\n"
            
            if payments:
                for payment in payments:
                    status_emoji = "✅" if payment.confirmed_at else "⏳"
                    text += f"{status_emoji} **{payment.memo}**\n"
                    text += f"   Expected: {payment.expected_amount:.3f} TON\n"
                    text += f"   Received: {payment.received_amount:.3f} TON\n"
                    if payment.tx_hash:
                        text += f"   TX: `{payment.tx_hash[:20]}...`\n"
                    text += f"   Created: {payment.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            else:
                text += "No recent payments found.\n\n"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔄 Refresh", callback_data="admin_payments"))
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
            
            await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
        finally:
            db.close()
    
    async def update_wallet_address(self, message: types.Message, state: FSMContext):
        """Update TON wallet address"""
        new_wallet = message.text.strip()
        
        # Basic validation
        if not new_wallet or len(new_wallet) < 20:
            await message.reply("❌ Invalid wallet address. Please provide a valid TON wallet address.")
            return
        
        db = SessionLocal()
        try:
            setting = db.query(AdminSettings).filter(AdminSettings.key == 'ton_wallet_address').first()
            if setting:
                setting.value = new_wallet
                setting.updated_by = message.from_user.id
                setting.updated_at = datetime.utcnow()
            else:
                setting = AdminSettings(
                    key='ton_wallet_address',
                    value=new_wallet,
                    description='TON wallet address for receiving payments',
                    updated_by=message.from_user.id
                )
                db.add(setting)
            
            db.commit()
            
            await message.reply(
                f"✅ **Wallet Address Updated**\n\nNew address: `{new_wallet}`",
                parse_mode="Markdown"
            )
            
            await state.finish()
            await self.show_admin_menu(message)
        
        except Exception as e:
            logger.error(f"Error updating wallet address: {e}")
            await message.reply("❌ Error updating wallet address. Please try again.")
        finally:
            db.close()
    
    async def add_new_channel(self, message: types.Message, state: FSMContext):
        """Add new advertising channel"""
        try:
            lines = message.text.strip().split('\n')
            if len(lines) < 3:
                await message.reply(
                    "❌ Invalid format. Please provide:\n"
                    "Channel ID (e.g., @channel_name)\n"
                    "Channel Name\n"
                    "Price per month (TON)\n"
                    "Description (optional)"
                )
                return
            
            channel_id = lines[0].strip()
            name = lines[1].strip()
            price = float(lines[2].strip())
            description = lines[3].strip() if len(lines) > 3 else ""
            
            db = SessionLocal()
            try:
                # Check if channel already exists
                existing = db.query(Channel).filter(Channel.channel_id == channel_id).first()
                if existing:
                    await message.reply(f"❌ Channel {channel_id} already exists.")
                    return
                
                new_channel = Channel(
                    channel_id=channel_id,
                    name=name,
                    description=description,
                    price_per_month=price,
                    is_active=True
                )
                
                db.add(new_channel)
                db.commit()
                
                await message.reply(
                    f"✅ **Channel Added Successfully**\n\n"
                    f"📺 **{name}**\n"
                    f"ID: `{channel_id}`\n"
                    f"Price: {price:.3f} TON/month",
                    parse_mode="Markdown"
                )
                
                await state.finish()
                await self.show_admin_menu(message)
            
            finally:
                db.close()
        
        except ValueError:
            await message.reply("❌ Invalid price format. Please enter a valid number.")
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
            await message.reply("❌ Error adding channel. Please try again.")

# Admin command handlers
async def admin_command(message: types.Message, admin_panel: AdminPanel):
    """Handle /admin command"""
    if not await admin_panel.is_admin(message.from_user.id):
        await message.reply("❌ Access denied. You are not authorized to use admin commands.")
        return
    
    await admin_panel.show_admin_menu(message)

def register_admin_handlers(dp, bot):
    """Register admin handlers"""
    admin_panel = AdminPanel(bot)
    
    # Command handlers
    dp.register_message_handler(
        lambda message: admin_command(message, admin_panel),
        commands=['admin'],
        state="*"
    )
    
    # Callback handlers
    dp.register_callback_query_handler(
        admin_panel.show_dashboard,
        lambda c: c.data == "admin_dashboard",
        state="*"
    )
    
    dp.register_callback_query_handler(
        admin_panel.show_channel_management,
        lambda c: c.data == "admin_channels",
        state="*"
    )
    
    dp.register_callback_query_handler(
        admin_panel.show_bundle_management,
        lambda c: c.data == "admin_bundles",
        state="*"
    )
    
    dp.register_callback_query_handler(
        admin_panel.show_settings_management,
        lambda c: c.data == "admin_settings",
        state="*"
    )
    
    dp.register_callback_query_handler(
        admin_panel.show_payment_monitoring,
        lambda c: c.data == "admin_payments",
        state="*"
    )
    
    dp.register_callback_query_handler(
        lambda c: admin_panel.show_admin_menu(c, edit_message=True),
        lambda c: c.data == "admin_main",
        state="*"
    )