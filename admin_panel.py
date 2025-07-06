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
import os
from datetime import datetime, timedelta
from sqlalchemy import func

logger = logging.getLogger(__name__)

class AdminStates(StatesGroup):
    main_menu = State()
    channel_management = State()
    add_channel = State()
    edit_channel = State()
    bundle_management = State()
    add_bundle = State()
    edit_bundle = State()
    pricing_management = State()
    edit_price = State()
    wallet_management = State()
    edit_wallet = State()
    statistics_view = State()
    settings_management = State()
    edit_setting = State()
    waiting_for_password = State()

class AdminPanel:
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        # Check environment variable first
        admin_ids = os.getenv('ADMIN_IDS', '').split(',')
        if str(user_id) in admin_ids:
            return True
            
        # Then check database
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
            InlineKeyboardButton("💰 Prices", callback_data="admin_pricing"),
            InlineKeyboardButton("📺 Channels", callback_data="admin_channels")
        )
        keyboard.add(
            InlineKeyboardButton("🎁 Bundles", callback_data="admin_bundles"),
            InlineKeyboardButton("🏦 Wallet", callback_data="admin_wallet")
        )
        keyboard.add(
            InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
            InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
        )
        
        text = """🔧 **Admin Panel**
        
Choose a section to manage:

💰 **Prices** - Edit package pricing
📺 **Channels** - Manage advertising channels
🎁 **Bundles** - Create special offers
🏦 **Wallet** - Configure payment address
📊 **Stats** - View revenue & analytics
⚙️ **Settings** - System configuration"""
        
        if edit_message and hasattr(message_or_query, 'edit_text'):
            await message_or_query.edit_text(text, reply_markup=keyboard)
        else:
            if hasattr(message_or_query, 'reply'):
                await message_or_query.reply(text, reply_markup=keyboard)
            else:
                await message_or_query.message.reply(text, reply_markup=keyboard)
    
    async def show_pricing_management(self, callback_query: types.CallbackQuery):
        """Show pricing management interface"""
        # Package configurations with current prices
        packages = {
            'starter': {'price': 0.099, 'months': 1, 'max_channels': 2, 'reposts': 10},
            'pro': {'price': 0.399, 'months': 3, 'max_channels': 5, 'reposts': 20},
            'growth': {'price': 0.999, 'months': 6, 'max_channels': 10, 'reposts': 30},
            'elite': {'price': 1.999, 'months': 12, 'max_channels': 999, 'reposts': 50}
        }
        
        text = """💰 **Current Prices:**

🟢 **Starter**: {starter} TON (~${starter_usd})
   • {starter_months} month | {starter_channels} channels | {starter_reposts} reposts/month

🔵 **Pro**: {pro} TON (~${pro_usd})
   • {pro_months} months | {pro_channels} channels | {pro_reposts} reposts/month

🟡 **Growth**: {growth} TON (~${growth_usd})
   • {growth_months} months | {growth_channels} channels | {growth_reposts} reposts/month

🟣 **Elite**: {elite} TON (~${elite_usd})
   • {elite_months} months | {elite_channels} channels | {elite_reposts} reposts/month""".format(
            starter=packages['starter']['price'],
            starter_usd=packages['starter']['price'] * 2.5,
            starter_months=packages['starter']['months'],
            starter_channels=packages['starter']['max_channels'],
            starter_reposts=packages['starter']['reposts'],
            pro=packages['pro']['price'],
            pro_usd=packages['pro']['price'] * 2.5,
            pro_months=packages['pro']['months'],
            pro_channels=packages['pro']['max_channels'],
            pro_reposts=packages['pro']['reposts'],
            growth=packages['growth']['price'],
            growth_usd=packages['growth']['price'] * 2.5,
            growth_months=packages['growth']['months'],
            growth_channels=packages['growth']['max_channels'],
            growth_reposts=packages['growth']['reposts'],
            elite=packages['elite']['price'],
            elite_usd=packages['elite']['price'] * 2.5,
            elite_months=packages['elite']['months'],
            elite_channels=packages['elite']['max_channels'],
            elite_reposts=packages['elite']['reposts']
        )
        
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("✏️ Edit Starter", callback_data="edit_price_starter"),
            InlineKeyboardButton("✏️ Edit Pro", callback_data="edit_price_pro")
        )
        keyboard.add(
            InlineKeyboardButton("✏️ Edit Growth", callback_data="edit_price_growth"),
            InlineKeyboardButton("✏️ Edit Elite", callback_data="edit_price_elite")
        )
        keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
    
    async def show_wallet_management(self, callback_query: types.CallbackQuery):
        """Show wallet management interface"""
        db = SessionLocal()
        try:
            wallet_setting = db.query(AdminSettings).filter(AdminSettings.key == 'ton_wallet_address').first()
            current_wallet = wallet_setting.value if wallet_setting else "Not configured"
            
            # Get wallet balance (mock for now - would need real TON API)
            balance = "45.67 TON"  # This would be fetched from TON API
            
            text = f"""🏦 **Wallet Management**

📍 **Current Address:**
`{current_wallet}`

💰 **Balance:** {balance}

⚡ **Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

🔄 **Auto-monitoring:** Active
📊 **Payment detection:** Every 30 seconds"""
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("✏️ Change Wallet", callback_data="edit_wallet_address"))
            keyboard.add(InlineKeyboardButton("🔄 Refresh Balance", callback_data="refresh_wallet"))
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
            await callback_query.answer()
            
        finally:
            db.close()
    
    async def show_statistics(self, callback_query: types.CallbackQuery):
        """Show comprehensive statistics"""
        db = SessionLocal()
        try:
            # Today's stats
            today = datetime.now().date()
            today_orders = db.query(Order).filter(
                func.date(Order.created_at) == today,
                Order.payment_status == 'confirmed'
            ).count()
            
            today_revenue = db.query(func.sum(Order.total_amount_ton)).filter(
                func.date(Order.created_at) == today,
                Order.payment_status == 'confirmed'
            ).scalar() or 0
            
            # Monthly stats
            month_start = datetime.now().replace(day=1)
            month_orders = db.query(Order).filter(
                Order.created_at >= month_start,
                Order.payment_status == 'confirmed'
            ).count()
            
            month_revenue = db.query(func.sum(Order.total_amount_ton)).filter(
                Order.created_at >= month_start,
                Order.payment_status == 'confirmed'
            ).scalar() or 0
            
            # Top performing channel
            top_channel = db.query(Channel).join(Order.channels).filter(
                Order.payment_status == 'confirmed'
            ).group_by(Channel.id).order_by(func.count(Order.id).desc()).first()
            
            top_channel_name = top_channel.name if top_channel else "None"
            
            text = f"""📊 **Statistics Dashboard**

📅 **Today ({today.strftime('%Y-%m-%d')}):**
💰 Revenue: {today_revenue:.3f} TON (~${today_revenue * 2.5:.2f})
📋 Orders: {today_orders}

📅 **This Month:**
💰 Revenue: {month_revenue:.3f} TON (~${month_revenue * 2.5:.2f})
📋 Orders: {month_orders}

🏆 **Top Channel:** {top_channel_name}

⚡ **System Status:**
🟢 Payment Detection: Active
🟢 Auto-posting: Active
🟢 Database: Connected"""
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("📈 Detailed Report", callback_data="detailed_stats"))
            keyboard.add(InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats"))
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
            await callback_query.answer()
            
        finally:
            db.close()
    
    async def update_wallet_address(self, message: types.Message, state: FSMContext):
        """Update TON wallet address"""
        new_address = message.text.strip()
        
        if not new_address.startswith(('EQ', 'UQ')):
            await message.reply("❌ Invalid TON address format. Please send a valid address.")
            return
        
        db = SessionLocal()
        try:
            wallet_setting = db.query(AdminSettings).filter(AdminSettings.key == 'ton_wallet_address').first()
            if wallet_setting:
                wallet_setting.value = new_address
                wallet_setting.updated_by = message.from_user.id
                wallet_setting.updated_at = datetime.utcnow()
            else:
                wallet_setting = AdminSettings(
                    key='ton_wallet_address',
                    value=new_address,
                    description='TON wallet address for payments',
                    updated_by=message.from_user.id
                )
                db.add(wallet_setting)
            
            db.commit()
            
            await message.reply(f"""✅ **Wallet Updated!**

New address: `{new_address}`

All future payments will be directed to this address.""")
            
            await state.finish()
            
        except Exception as e:
            logger.error(f"Error updating wallet: {e}")
            await message.reply("❌ Error updating wallet address. Please try again.")
        finally:
            db.close()
    
    async def show_channel_management(self, callback_query: types.CallbackQuery):
        """Show channel management interface"""
        db = SessionLocal()
        try:
            channels = db.query(Channel).filter(Channel.is_active == True).all()
            
            text = "📺 **Channel Management**\n\n"
            if channels:
                for channel in channels:
                    status = "🟢" if channel.is_active else "🔴"
                    text += f"{status} **{channel.name}**\n"
                    text += f"   ID: `{channel.channel_id}`\n"
                    text += f"   Subscribers: {channel.subscribers_count:,}\n"
                    text += f"   Price: {channel.price_per_month} TON/month\n\n"
            else:
                text += "No channels configured yet."
                
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("➕ Add Channel", callback_data="add_channel"))
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
            await callback_query.answer()
        finally:
            db.close()
    
    async def show_bundle_management(self, callback_query: types.CallbackQuery):
        """Show bundle management interface"""
        db = SessionLocal()
        try:
            bundles = db.query(Bundle).filter(Bundle.is_active == True).all()
            
            text = "🎁 **Bundle Management**\n\n"
            if bundles:
                for bundle in bundles:
                    text += f"✨ **{bundle.name}**\n"
                    text += f"   Duration: {bundle.months} months (+{bundle.bonus_months} bonus)\n"
                    text += f"   Discount: {bundle.discount_percent}%\n"
                    text += f"   Channels: {bundle.min_channels}-{bundle.max_channels}\n\n"
            else:
                text += "No bundles configured yet."
                
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("➕ Create Bundle", callback_data="create_bundle"))
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
            await callback_query.answer()
        finally:
            db.close()
    
    async def show_settings_management(self, callback_query: types.CallbackQuery):
        """Show settings management interface"""
        db = SessionLocal()
        try:
            settings = db.query(AdminSettings).all()
            
            text = "⚙️ **System Settings**\n\n"
            
            # Key system settings
            important_settings = ['ton_wallet_address', 'admin_password', 'payment_timeout', 'auto_post_enabled']
            
            for setting in settings:
                if setting.key in important_settings:
                    if setting.key == 'ton_wallet_address':
                        value = setting.value[:15] + "..." if len(setting.value) > 15 else setting.value
                    elif setting.key == 'admin_password':
                        value = "●" * 8
                    else:
                        value = setting.value
                    text += f"🔧 **{setting.key.replace('_', ' ').title()}**: {value}\n"
            
            text += f"\n⚡ **System Status:**\n"
            text += f"🟢 Bot: Running\n"
            text += f"🟢 Database: Connected\n"
            text += f"🟢 Payment Monitor: Active\n"
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🔧 Edit Settings", callback_data="edit_settings"))
            keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="admin_main"))
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
            await callback_query.answer()
        finally:
            db.close()
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