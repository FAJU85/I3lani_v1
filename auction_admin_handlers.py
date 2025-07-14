"""
Auction Admin Handlers for I3lani Bot
Admin interface for managing auction advertising system
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from auction_advertising_system import get_auction_system, AdStatus, AuctionStatus
from auction_scheduler import get_auction_scheduler
from database import Database
from languages import get_text

logger = logging.getLogger(__name__)

# Admin states
class AuctionAdminStates(StatesGroup):
    """States for auction admin operations"""
    reviewing_ad = State()
    setting_channel_quality = State()
    processing_withdrawal = State()

class AuctionAdminHandlers:
    """Handler class for auction admin operations"""
    
    def __init__(self, database: Database):
        self.db = database
        self.auction_system = get_auction_system()
        self.auction_scheduler = get_auction_scheduler()
        self.admin_ids = [566158428]  # Add admin user IDs
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    async def auction_admin_command(self, message: Message, state: FSMContext):
        """Main auction admin command"""
        user_id = message.from_user.id
        
        if not self.is_admin(user_id):
            await message.answer("❌ Access denied. Admin only.")
            return
        
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(text="📋 Review Pending Ads", callback_data="auction_admin_review_ads"),
            InlineKeyboardButton(text="🎯 Run Test Auction", callback_data="auction_admin_test_auction"),
            InlineKeyboardButton(text="📊 System Statistics", callback_data="auction_admin_stats"),
            InlineKeyboardButton(text="📺 Manage Channels", callback_data="auction_admin_channels"),
            InlineKeyboardButton(text="💸 Withdrawal Requests", callback_data="auction_admin_withdrawals"),
            InlineKeyboardButton(text="⚙️ System Settings", callback_data="auction_admin_settings")
        )
        keyboard.adjust(2)
        
        text = "🎯 **Auction Admin Panel**\n\n" \
               "Manage the auction advertising system:\n\n" \
               "📋 Review and approve ads\n" \
               "🎯 Run test auctions\n" \
               "📊 View system statistics\n" \
               "📺 Manage channels\n" \
               "💸 Process withdrawals\n" \
               "⚙️ Configure settings"
        
        await message.answer(text, reply_markup=keyboard.as_markup())
    
    async def handle_review_ads(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle ad review interface"""
        # Get pending ads
        pending_ads = await self.get_pending_ads()
        
        if not pending_ads:
            await callback_query.message.edit_text("✅ No pending ads to review!")
            return
        
        # Show first pending ad
        ad = pending_ads[0]
        await self.show_ad_for_review(callback_query.message, ad)
        await state.set_state(AuctionAdminStates.reviewing_ad)
    
    async def get_pending_ads(self) -> List[Dict]:
        """Get pending ads for review"""
        async with self.db.get_connection() as conn:
            async with conn.execute('''
                SELECT ad_id, advertiser_id, content, image_url, category,
                       bid_type, bid_amount, daily_budget, created_at
                FROM auction_ads 
                WHERE status = 'pending'
                ORDER BY created_at ASC
            ''') as cursor:
                rows = await cursor.fetchall()
                
                return [{
                    'ad_id': row[0],
                    'advertiser_id': row[1],
                    'content': row[2],
                    'image_url': row[3],
                    'category': row[4],
                    'bid_type': row[5],
                    'bid_amount': row[6],
                    'daily_budget': row[7],
                    'created_at': row[8]
                } for row in rows]
    
    async def show_ad_for_review(self, message: Message, ad: Dict):
        """Show ad for admin review"""
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(text="✅ Approve", callback_data=f"auction_approve_{ad['ad_id']}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"auction_reject_{ad['ad_id']}"),
            InlineKeyboardButton(text="⏭️ Next", callback_data="auction_admin_next_ad")
        )
        keyboard.adjust(2)
        
        text = f"📋 **Ad Review #{ad['ad_id']}**\n\n" \
               f"👤 Advertiser: {ad['advertiser_id']}\n" \
               f"📂 Category: {ad['category'].title()}\n" \
               f"💰 Bid Type: {ad['bid_type']}\n" \
               f"💵 Bid Amount: ${ad['bid_amount']:.2f}\n" \
               f"💳 Daily Budget: ${ad['daily_budget']:.2f}\n" \
               f"📅 Created: {ad['created_at']}\n\n" \
               f"📝 **Content:**\n{ad['content']}\n\n" \
               f"🖼️ Image: {'Yes' if ad['image_url'] else 'No'}"
        
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    
    async def handle_ad_action(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle ad approval/rejection"""
        action = callback_query.data.split("_")[1]
        ad_id = int(callback_query.data.split("_")[2])
        
        if action == "approve":
            await self.approve_ad(ad_id)
            await callback_query.answer("✅ Ad approved!")
        elif action == "reject":
            await self.reject_ad(ad_id)
            await callback_query.answer("❌ Ad rejected!")
        
        # Show next ad
        await self.handle_review_ads(callback_query, state)
    
    async def approve_ad(self, ad_id: int):
        """Approve an ad"""
        async with self.db.get_connection() as conn:
            await conn.execute('''
                UPDATE auction_ads 
                SET status = 'approved', updated_at = CURRENT_TIMESTAMP
                WHERE ad_id = ?
            ''', (ad_id,))
            await conn.commit()
    
    async def reject_ad(self, ad_id: int):
        """Reject an ad"""
        async with self.db.get_connection() as conn:
            await conn.execute('''
                UPDATE auction_ads 
                SET status = 'rejected', updated_at = CURRENT_TIMESTAMP
                WHERE ad_id = ?
            ''', (ad_id,))
            await conn.commit()
    
    async def handle_test_auction(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle test auction"""
        await callback_query.message.edit_text("🎯 Running test auction...")
        
        if self.auction_scheduler:
            results = await self.auction_scheduler.run_test_auction()
            
            if results:
                text = f"✅ **Test Auction Results**\n\n" \
                       f"📅 Date: {results['auction_date']}\n" \
                       f"🏆 Total Auctions: {results['total_auctions']}\n\n" \
                       f"**Results:**\n"
                
                for i, result in enumerate(results['results'][:5]):  # Show first 5
                    text += f"{i+1}. Channel: {result['channel_id']}\n" \
                           f"   Winner: Ad #{result['winning_ad_id']}\n" \
                           f"   Bid: ${result['winning_bid_amount']:.2f}\n\n"
                
                if len(results['results']) > 5:
                    text += f"... and {len(results['results']) - 5} more results"
            else:
                text = "❌ Test auction failed. Check logs for details."
        else:
            text = "❌ Auction scheduler not available"
        
        await callback_query.message.edit_text(text)
    
    async def handle_system_stats(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle system statistics"""
        stats = await self.get_system_stats()
        
        text = f"📊 **Auction System Statistics**\n\n" \
               f"🎯 **Ads:**\n" \
               f"   • Total: {stats['total_ads']}\n" \
               f"   • Pending: {stats['pending_ads']}\n" \
               f"   • Approved: {stats['approved_ads']}\n" \
               f"   • Active: {stats['active_ads']}\n\n" \
               f"📺 **Channels:**\n" \
               f"   • Total: {stats['total_channels']}\n" \
               f"   • Active: {stats['active_channels']}\n\n" \
               f"🏆 **Auctions:**\n" \
               f"   • Today: {stats['auctions_today']}\n" \
               f"   • This Week: {stats['auctions_week']}\n\n" \
               f"💰 **Revenue:**\n" \
               f"   • Total: ${stats['total_revenue']:.2f}\n" \
               f"   • This Month: ${stats['monthly_revenue']:.2f}\n\n" \
               f"💸 **Withdrawals:**\n" \
               f"   • Pending: {stats['pending_withdrawals']}\n" \
               f"   • Total Paid: ${stats['total_withdrawals']:.2f}"
        
        await callback_query.message.edit_text(text)
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {}
        
        async with self.db.get_connection() as conn:
            # Ad statistics
            async with conn.execute('SELECT COUNT(*) FROM auction_ads') as cursor:
                stats['total_ads'] = (await cursor.fetchone())[0]
            
            async with conn.execute('SELECT COUNT(*) FROM auction_ads WHERE status = "pending"') as cursor:
                stats['pending_ads'] = (await cursor.fetchone())[0]
            
            async with conn.execute('SELECT COUNT(*) FROM auction_ads WHERE status = "approved"') as cursor:
                stats['approved_ads'] = (await cursor.fetchone())[0]
            
            async with conn.execute('SELECT COUNT(*) FROM auction_ads WHERE status = "active"') as cursor:
                stats['active_ads'] = (await cursor.fetchone())[0]
            
            # Channel statistics
            async with conn.execute('SELECT COUNT(*) FROM auction_channels') as cursor:
                stats['total_channels'] = (await cursor.fetchone())[0]
            
            async with conn.execute('SELECT COUNT(*) FROM auction_channels WHERE is_active = TRUE') as cursor:
                stats['active_channels'] = (await cursor.fetchone())[0]
            
            # Auction statistics
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            async with conn.execute('SELECT COUNT(*) FROM daily_auctions WHERE DATE(auction_date) = ?', (today,)) as cursor:
                stats['auctions_today'] = (await cursor.fetchone())[0]
            
            async with conn.execute('SELECT COUNT(*) FROM daily_auctions WHERE DATE(auction_date) >= ?', (week_ago,)) as cursor:
                stats['auctions_week'] = (await cursor.fetchone())[0]
            
            # Revenue statistics
            async with conn.execute('SELECT SUM(revenue) FROM ad_performance') as cursor:
                result = await cursor.fetchone()
                stats['total_revenue'] = result[0] if result[0] else 0.0
            
            month_start = datetime.now().replace(day=1).date()
            async with conn.execute('SELECT SUM(revenue) FROM ad_performance WHERE DATE(date) >= ?', (month_start,)) as cursor:
                result = await cursor.fetchone()
                stats['monthly_revenue'] = result[0] if result[0] else 0.0
            
            # Withdrawal statistics
            async with conn.execute('SELECT COUNT(*) FROM withdrawal_requests WHERE status = "pending"') as cursor:
                stats['pending_withdrawals'] = (await cursor.fetchone())[0]
            
            async with conn.execute('SELECT SUM(amount) FROM withdrawal_requests WHERE status = "completed"') as cursor:
                result = await cursor.fetchone()
                stats['total_withdrawals'] = result[0] if result[0] else 0.0
        
        return stats
    
    async def handle_channel_management(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle channel management"""
        channels = await self.get_channels()
        
        text = f"📺 **Channel Management**\n\n"
        
        for i, channel in enumerate(channels[:10]):  # Show first 10
            status = "🟢" if channel['is_active'] else "🔴"
            text += f"{i+1}. {status} {channel['name']}\n" \
                   f"   Category: {channel['category']}\n" \
                   f"   Subscribers: {channel['subscribers']}\n" \
                   f"   Quality Score: {channel['quality_score']:.2f}\n\n"
        
        if len(channels) > 10:
            text += f"... and {len(channels) - 10} more channels"
        
        await callback_query.message.edit_text(text)
    
    async def get_channels(self) -> List[Dict]:
        """Get all channels"""
        async with self.db.get_connection() as conn:
            async with conn.execute('''
                SELECT channel_id, name, category, subscribers, 
                       quality_score, is_active
                FROM auction_channels
                ORDER BY subscribers DESC
            ''') as cursor:
                rows = await cursor.fetchall()
                
                return [{
                    'channel_id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'subscribers': row[3],
                    'quality_score': row[4],
                    'is_active': row[5]
                } for row in rows]
    
    async def handle_withdrawals(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle withdrawal requests"""
        withdrawals = await self.get_pending_withdrawals()
        
        if not withdrawals:
            await callback_query.message.edit_text("✅ No pending withdrawal requests!")
            return
        
        text = f"💸 **Pending Withdrawals**\n\n"
        
        for i, withdrawal in enumerate(withdrawals[:5]):  # Show first 5
            text += f"{i+1}. User: {withdrawal['user_id']}\n" \
                   f"   Amount: ${withdrawal['amount']:.2f}\n" \
                   f"   Method: {withdrawal['payment_method']}\n" \
                   f"   Requested: {withdrawal['requested_at']}\n\n"
        
        keyboard = InlineKeyboardBuilder()
        if withdrawals:
            keyboard.add(InlineKeyboardButton(
                text="💸 Process Withdrawals",
                callback_data="auction_admin_process_withdrawals"
            ))
        
        await callback_query.message.edit_text(text, reply_markup=keyboard.as_markup())
    
    async def get_pending_withdrawals(self) -> List[Dict]:
        """Get pending withdrawal requests"""
        async with self.db.get_connection() as conn:
            async with conn.execute('''
                SELECT withdrawal_id, user_id, amount, payment_method, 
                       payment_details, requested_at
                FROM withdrawal_requests
                WHERE status = 'pending'
                ORDER BY requested_at ASC
            ''') as cursor:
                rows = await cursor.fetchall()
                
                return [{
                    'withdrawal_id': row[0],
                    'user_id': row[1],
                    'amount': row[2],
                    'payment_method': row[3],
                    'payment_details': row[4],
                    'requested_at': row[5]
                } for row in rows]

def setup_auction_admin_handlers(dp, database: Database):
    """Setup auction admin handlers"""
    handlers = AuctionAdminHandlers(database)
    
    # Register handlers
    dp.message.register(handlers.auction_admin_command, Command("auctionadmin"))
    
    dp.callback_query.register(handlers.handle_review_ads, F.data == "auction_admin_review_ads")
    dp.callback_query.register(handlers.handle_test_auction, F.data == "auction_admin_test_auction")
    dp.callback_query.register(handlers.handle_system_stats, F.data == "auction_admin_stats")
    dp.callback_query.register(handlers.handle_channel_management, F.data == "auction_admin_channels")
    dp.callback_query.register(handlers.handle_withdrawals, F.data == "auction_admin_withdrawals")
    
    dp.callback_query.register(handlers.handle_ad_action, F.data.startswith("auction_approve_"))
    dp.callback_query.register(handlers.handle_ad_action, F.data.startswith("auction_reject_"))
    
    logger.info("✅ Auction admin handlers registered")