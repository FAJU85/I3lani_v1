"""
I3lani v3 Admin Commands
Administrative interface for auction-based system
"""

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite
from datetime import datetime

from i3lani_v3_architecture import i3lani_v3
from v3_integration_main import get_v3_integration

logger = logging.getLogger(__name__)

class AdminStates(StatesGroup):
    """States for admin operations"""
    waiting_ad_approval = State()
    waiting_rejection_reason = State()

class V3AdminCommands:
    """I3lani v3 Admin Command Interface"""
    
    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self.integration = get_v3_integration(bot, dp)
        self.admin_ids = [566158428, 2013460438]  # Admin user IDs
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    async def admin_v3_command(self, message: Message, state: FSMContext):
        """Handle /adminv3 command"""
        if not self.is_admin(message.from_user.id):
            await message.answer("❌ Unauthorized access")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 System Stats", callback_data="admin_v3_stats")],
            [InlineKeyboardButton(text="✅ Approve Ads", callback_data="admin_v3_approve")],
            [InlineKeyboardButton(text="❌ Reject Ads", callback_data="admin_v3_reject")],
            [InlineKeyboardButton(text="🎯 Run Auction", callback_data="admin_v3_auction")],
            [InlineKeyboardButton(text="👥 User Management", callback_data="admin_v3_users")],
            [InlineKeyboardButton(text="📺 Channel Management", callback_data="admin_v3_channels")],
            [InlineKeyboardButton(text="💰 Financial Overview", callback_data="admin_v3_finance")]
        ])
        
        await message.answer(
            "🔧 I3lani v3 Admin Panel\n\n"
            "🎯 Auction-Based Advertising System\n"
            "💰 TON + Stars Payment Processing\n"
            "👥 Multi-Role User Management\n\n"
            "Select an option:",
            reply_markup=keyboard
        )
    
    async def admin_stats_callback(self, callback_query: CallbackQuery):
        """Handle admin stats callback"""
        if not self.is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Unauthorized")
            return
        
        stats = await self.integration.get_v3_stats()
        
        if stats:
            system_stats = stats['system_stats']
            auction_stats = stats['auction_stats']
            
            text = (
                f"📊 I3lani v3 System Statistics\n\n"
                f"👥 Total Users: {system_stats['total_users']}\n"
                f"   📢 Advertisers: {system_stats['advertisers']}\n"
                f"   📺 Channel Owners: {system_stats['channel_owners']}\n"
                f"   💰 Affiliates: {system_stats['affiliates']}\n\n"
                f"📺 Active Channels: {system_stats['total_channels']}\n"
                f"📢 Total Ads: {system_stats['total_ads']}\n"
                f"💰 Total Revenue: ${system_stats['total_revenue']:.2f}\n\n"
                f"🎯 Today's Auction:\n"
                f"   📋 Placements: {auction_stats['todays_placements']}\n"
                f"   👁️ Impressions: {auction_stats['todays_impressions']}\n"
                f"   👆 Clicks: {auction_stats['todays_clicks']}\n"
                f"   💰 Revenue: ${auction_stats['todays_revenue']:.2f}\n"
                f"   📤 Posted Ads: {auction_stats['posted_ads']}"
            )
        else:
            text = "❌ Unable to fetch statistics"
        
        await callback_query.message.edit_text(text)
        await callback_query.answer()
    
    async def admin_approve_callback(self, callback_query: CallbackQuery):
        """Handle admin approve ads callback"""
        if not self.is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Unauthorized")
            return
        
        # Get pending ads
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            async with db.execute("""
                SELECT ad_id, advertiser_id, content, category, bid_type, bid_amount, created_at
                FROM ads_v3 
                WHERE status = 'pending'
                ORDER BY created_at DESC
                LIMIT 10
            """) as cursor:
                pending_ads = await cursor.fetchall()
        
        if not pending_ads:
            await callback_query.message.edit_text("✅ No pending ads to approve")
            await callback_query.answer()
            return
        
        # Create approval keyboard
        keyboard = []
        for ad in pending_ads:
            ad_id, advertiser_id, content, category, bid_type, bid_amount, created_at = ad
            
            # Truncate content for display
            display_content = content[:30] + "..." if len(content) > 30 else content
            
            keyboard.append([
                InlineKeyboardButton(
                    text=f"✅ {ad_id}: {display_content}",
                    callback_data=f"approve_ad_{ad_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_v3_back")])
        
        await callback_query.message.edit_text(
            "✅ Pending Ads for Approval\n\n"
            "Click on an ad to approve it:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
    
    async def admin_reject_callback(self, callback_query: CallbackQuery):
        """Handle admin reject ads callback"""
        if not self.is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Unauthorized")
            return
        
        # Get pending ads
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            async with db.execute("""
                SELECT ad_id, advertiser_id, content, category, bid_type, bid_amount
                FROM ads_v3 
                WHERE status = 'pending'
                ORDER BY created_at DESC
                LIMIT 10
            """) as cursor:
                pending_ads = await cursor.fetchall()
        
        if not pending_ads:
            await callback_query.message.edit_text("✅ No pending ads to reject")
            await callback_query.answer()
            return
        
        # Create rejection keyboard
        keyboard = []
        for ad in pending_ads:
            ad_id, advertiser_id, content, category, bid_type, bid_amount = ad
            
            # Truncate content for display
            display_content = content[:30] + "..." if len(content) > 30 else content
            
            keyboard.append([
                InlineKeyboardButton(
                    text=f"❌ {ad_id}: {display_content}",
                    callback_data=f"reject_ad_{ad_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_v3_back")])
        
        await callback_query.message.edit_text(
            "❌ Pending Ads for Rejection\n\n"
            "Click on an ad to reject it:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
    
    async def handle_ad_approval(self, callback_query: CallbackQuery):
        """Handle individual ad approval"""
        if not self.is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Unauthorized")
            return
        
        ad_id = callback_query.data.replace("approve_ad_", "")
        
        result = await self.integration.admin_approve_ad(ad_id, callback_query.from_user.id)
        
        if result['success']:
            await callback_query.message.edit_text(
                f"✅ Ad Approved Successfully!\n\n"
                f"🎯 Ad ID: {ad_id}\n"
                f"📋 Status: Approved\n"
                f"🎯 Next: Will enter daily auction"
            )
        else:
            await callback_query.message.edit_text(
                f"❌ Approval Failed\n\n"
                f"Error: {result['error']}"
            )
        
        await callback_query.answer()
    
    async def handle_ad_rejection(self, callback_query: CallbackQuery):
        """Handle individual ad rejection"""
        if not self.is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Unauthorized")
            return
        
        ad_id = callback_query.data.replace("reject_ad_", "")
        
        result = await self.integration.admin_reject_ad(ad_id, callback_query.from_user.id, "Policy violation")
        
        if result['success']:
            await callback_query.message.edit_text(
                f"❌ Ad Rejected Successfully!\n\n"
                f"🎯 Ad ID: {ad_id}\n"
                f"📋 Status: Rejected\n"
                f"👤 Advertiser has been notified"
            )
        else:
            await callback_query.message.edit_text(
                f"❌ Rejection Failed\n\n"
                f"Error: {result['error']}"
            )
        
        await callback_query.answer()
    
    async def admin_auction_callback(self, callback_query: CallbackQuery):
        """Handle admin force auction callback"""
        if not self.is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Unauthorized")
            return
        
        await callback_query.message.edit_text(
            "🎯 Running Auction...\n\n"
            "Please wait while the auction system processes ads..."
        )
        
        result = await self.integration.force_run_auction()
        
        if result['success']:
            await callback_query.message.edit_text(
                "✅ Auction Completed Successfully!\n\n"
                "🎯 Ads have been matched to channels\n"
                "📤 Posting process initiated\n"
                "📊 Check stats for results"
            )
        else:
            await callback_query.message.edit_text(
                f"❌ Auction Failed\n\n"
                f"Error: {result['error']}"
            )
        
        await callback_query.answer()
    
    async def admin_users_callback(self, callback_query: CallbackQuery):
        """Handle admin user management callback"""
        if not self.is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Unauthorized")
            return
        
        # Get user statistics
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            async with db.execute("""
                SELECT user_type, COUNT(*) as count
                FROM users_v3
                GROUP BY user_type
            """) as cursor:
                user_types = await cursor.fetchall()
            
            async with db.execute("""
                SELECT user_id, username, user_type, balance_ton, created_at
                FROM users_v3
                ORDER BY created_at DESC
                LIMIT 10
            """) as cursor:
                recent_users = await cursor.fetchall()
        
        text = "👥 User Management\n\n"
        
        # User type breakdown
        for user_type, count in user_types:
            text += f"   {user_type}: {count}\n"
        
        text += "\n📋 Recent Users:\n"
        for user in recent_users:
            user_id, username, user_type, balance_ton, created_at = user
            text += f"   • {username or user_id} ({user_type})\n"
        
        await callback_query.message.edit_text(text)
        await callback_query.answer()
    
    async def admin_channels_callback(self, callback_query: CallbackQuery):
        """Handle admin channel management callback"""
        if not self.is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Unauthorized")
            return
        
        # Get channel statistics
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            async with db.execute("""
                SELECT category, COUNT(*) as count
                FROM channels_v3
                WHERE is_active = TRUE
                GROUP BY category
            """) as cursor:
                categories = await cursor.fetchall()
            
            async with db.execute("""
                SELECT channel_id, channel_name, category, subscribers, owner_id
                FROM channels_v3
                WHERE is_active = TRUE
                ORDER BY subscribers DESC
                LIMIT 10
            """) as cursor:
                top_channels = await cursor.fetchall()
        
        text = "📺 Channel Management\n\n"
        
        # Category breakdown
        text += "📂 Categories:\n"
        for category, count in categories:
            text += f"   {category}: {count}\n"
        
        text += "\n🔝 Top Channels:\n"
        for channel in top_channels:
            channel_id, channel_name, category, subscribers, owner_id = channel
            text += f"   • {channel_name}: {subscribers} subs\n"
        
        await callback_query.message.edit_text(text)
        await callback_query.answer()
    
    async def admin_finance_callback(self, callback_query: CallbackQuery):
        """Handle admin financial overview callback"""
        if not self.is_admin(callback_query.from_user.id):
            await callback_query.answer("❌ Unauthorized")
            return
        
        # Get financial statistics
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            # Total payments
            async with db.execute("""
                SELECT currency, SUM(amount) as total
                FROM payments_v3
                WHERE status = 'completed'
                GROUP BY currency
            """) as cursor:
                payments = await cursor.fetchall()
            
            # Total revenue
            async with db.execute("""
                SELECT SUM(revenue) as total_revenue
                FROM ad_placements_v3
            """) as cursor:
                total_revenue = (await cursor.fetchone())[0] or 0
            
            # Total commissions
            async with db.execute("""
                SELECT SUM(amount) as total_commissions
                FROM commissions_v3
            """) as cursor:
                total_commissions = (await cursor.fetchone())[0] or 0
            
            # Pending withdrawals
            async with db.execute("""
                SELECT COUNT(*) as pending_withdrawals, SUM(amount) as pending_amount
                FROM withdrawals_v3
                WHERE status = 'pending'
            """) as cursor:
                withdrawal_info = await cursor.fetchone()
        
        text = "💰 Financial Overview\n\n"
        
        text += "💳 Total Payments:\n"
        for currency, total in payments:
            text += f"   {currency}: {total:.8f}\n"
        
        text += f"\n💰 Total Revenue: ${total_revenue:.2f}\n"
        text += f"🎁 Total Commissions: ${total_commissions:.2f}\n"
        text += f"⏳ Pending Withdrawals: {withdrawal_info[0]} (${withdrawal_info[1] or 0:.2f})\n"
        
        await callback_query.message.edit_text(text)
        await callback_query.answer()

def setup_v3_admin_handlers(dp: Dispatcher, bot: Bot):
    """Setup I3lani v3 admin handlers"""
    admin_commands = V3AdminCommands(bot, dp)
    
    # Register handlers
    dp.message.register(admin_commands.admin_v3_command, Command("adminv3"))
    dp.callback_query.register(admin_commands.admin_stats_callback, lambda c: c.data == "admin_v3_stats")
    dp.callback_query.register(admin_commands.admin_approve_callback, lambda c: c.data == "admin_v3_approve")
    dp.callback_query.register(admin_commands.admin_reject_callback, lambda c: c.data == "admin_v3_reject")
    dp.callback_query.register(admin_commands.admin_auction_callback, lambda c: c.data == "admin_v3_auction")
    dp.callback_query.register(admin_commands.admin_users_callback, lambda c: c.data == "admin_v3_users")
    dp.callback_query.register(admin_commands.admin_channels_callback, lambda c: c.data == "admin_v3_channels")
    dp.callback_query.register(admin_commands.admin_finance_callback, lambda c: c.data == "admin_v3_finance")
    
    # Ad approval/rejection handlers
    dp.callback_query.register(admin_commands.handle_ad_approval, lambda c: c.data.startswith("approve_ad_"))
    dp.callback_query.register(admin_commands.handle_ad_rejection, lambda c: c.data.startswith("reject_ad_"))
    
    logger.info("✅ I3lani v3 admin handlers registered")