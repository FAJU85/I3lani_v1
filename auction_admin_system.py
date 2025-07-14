"""
Auction Admin System for I3lani Bot
Complete admin interface for auction-based advertising system
"""

import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import asyncio
from decimal import Decimal

from auction_advertising_system import get_auction_system, AdStatus, ChannelCategory, BidType
from database import Database

logger = logging.getLogger(__name__)

class AdminReviewStates(StatesGroup):
    reviewing_ad = State()
    reviewing_channel = State()

class AuctionAdminSystem:
    def __init__(self, bot, database: Database):
        self.bot = bot
        self.db = database
        self.auction_system = None
        self.admin_ids = [566158428]  # Default admin ID
        
    async def initialize(self):
        """Initialize auction admin system"""
        self.auction_system = await get_auction_system()
        
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    def create_admin_auction_menu(self) -> InlineKeyboardMarkup:
        """Create admin auction menu"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Review Ads", callback_data="admin_auction_review_ads"),
                InlineKeyboardButton(text="📺 Manage Channels", callback_data="admin_auction_channels")
            ],
            [
                InlineKeyboardButton(text="🎯 Run Auction", callback_data="admin_auction_run"),
                InlineKeyboardButton(text="📊 Auction Stats", callback_data="admin_auction_stats")
            ],
            [
                InlineKeyboardButton(text="💰 Revenue Report", callback_data="admin_auction_revenue"),
                InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_auction_settings")
            ],
            [
                InlineKeyboardButton(text="◀️ Back to Main", callback_data="admin_main_menu")
            ]
        ])
    
    async def show_auction_admin_menu(self, callback_query: CallbackQuery):
        """Show auction admin menu"""
        try:
            if not self.is_admin(callback_query.from_user.id):
                await callback_query.answer("❌ Admin access required", show_alert=True)
                return
            
            # Get system stats
            stats = await self.get_auction_system_stats()
            
            menu_text = f"""
🎯 **Auction Admin Dashboard**

**System Status**:
• Pending Ads: {stats['pending_ads']}
• Active Channels: {stats['active_channels']}
• Today's Revenue: ${stats['today_revenue']:.2f}
• Total Users: {stats['total_users']}

**Recent Activity**:
• Last Auction: {stats['last_auction']}
• Ads Published Today: {stats['ads_today']}
• New Channels Today: {stats['new_channels_today']}

Choose an option:
"""
            
            await callback_query.message.edit_text(
                menu_text,
                reply_markup=self.create_admin_auction_menu(),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ Error showing auction admin menu: {e}")
            await callback_query.answer("❌ Error loading menu")
    
    async def get_auction_system_stats(self) -> dict:
        """Get auction system statistics"""
        try:
            async with self.auction_system.get_db_connection() as db:
                # Get pending ads count
                async with db.execute("SELECT COUNT(*) FROM auction_ads WHERE status = 'pending'") as cursor:
                    pending_ads = (await cursor.fetchone())[0]
                
                # Get active channels count
                async with db.execute("SELECT COUNT(*) FROM auction_channels WHERE is_verified = 1") as cursor:
                    active_channels = (await cursor.fetchone())[0]
                
                # Get today's revenue
                today = datetime.now().date()
                async with db.execute("""
                    SELECT COALESCE(SUM(amount), 0) FROM earnings_log 
                    WHERE DATE(created_at) = ?
                """, (today,)) as cursor:
                    today_revenue = (await cursor.fetchone())[0]
                
                # Get total users
                async with db.execute("SELECT COUNT(*) FROM user_balances") as cursor:
                    total_users = (await cursor.fetchone())[0]
                
                # Get last auction date
                async with db.execute("""
                    SELECT MAX(created_at) FROM auction_results
                """) as cursor:
                    last_auction_row = await cursor.fetchone()
                    last_auction = last_auction_row[0] if last_auction_row[0] else "Never"
                
                # Get ads published today
                async with db.execute("""
                    SELECT COUNT(*) FROM auction_ads 
                    WHERE status = 'active' AND DATE(updated_at) = ?
                """, (today,)) as cursor:
                    ads_today = (await cursor.fetchone())[0]
                
                # Get new channels today
                async with db.execute("""
                    SELECT COUNT(*) FROM auction_channels 
                    WHERE DATE(created_at) = ?
                """, (today,)) as cursor:
                    new_channels_today = (await cursor.fetchone())[0]
                
                return {
                    'pending_ads': pending_ads,
                    'active_channels': active_channels,
                    'today_revenue': today_revenue,
                    'total_users': total_users,
                    'last_auction': last_auction,
                    'ads_today': ads_today,
                    'new_channels_today': new_channels_today
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting auction stats: {e}")
            return {
                'pending_ads': 0,
                'active_channels': 0,
                'today_revenue': 0,
                'total_users': 0,
                'last_auction': "Error",
                'ads_today': 0,
                'new_channels_today': 0
            }
    
    async def show_pending_ads(self, callback_query: CallbackQuery):
        """Show pending ads for review"""
        try:
            if not self.is_admin(callback_query.from_user.id):
                await callback_query.answer("❌ Admin access required", show_alert=True)
                return
            
            async with self.auction_system.get_db_connection() as db:
                async with db.execute("""
                    SELECT ad_id, advertiser_id, content, image_url, category, bid_type, bid_amount, created_at
                    FROM auction_ads 
                    WHERE status = 'pending'
                    ORDER BY created_at DESC
                    LIMIT 10
                """) as cursor:
                    ads = await cursor.fetchall()
            
            if not ads:
                await callback_query.message.edit_text(
                    "✅ No pending ads to review!",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="◀️ Back", callback_data="admin_auction_menu")]
                    ])
                )
                return
            
            # Create ads list
            ads_text = "📋 **Pending Ads for Review**\n\n"
            keyboard = []
            
            for ad in ads:
                ad_id, advertiser_id, content, image_url, category, bid_type, bid_amount, created_at = ad
                
                ads_text += f"**{ad_id}**\n"
                ads_text += f"👤 Advertiser: {advertiser_id}\n"
                ads_text += f"📂 Category: {category.title()}\n"
                ads_text += f"💰 Bid: ${bid_amount} ({bid_type.upper()})\n"
                ads_text += f"📝 Content: {content[:100]}{'...' if len(content) > 100 else ''}\n"
                ads_text += f"🖼️ Image: {'✅' if image_url else '❌'}\n"
                ads_text += f"📅 Created: {created_at[:10]}\n\n"
                
                keyboard.append([
                    InlineKeyboardButton(text=f"Review {ad_id}", callback_data=f"admin_review_ad_{ad_id}")
                ])
            
            keyboard.append([
                InlineKeyboardButton(text="◀️ Back", callback_data="admin_auction_menu")
            ])
            
            await callback_query.message.edit_text(
                ads_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ Error showing pending ads: {e}")
            await callback_query.answer("❌ Error loading ads")
    
    async def show_ad_review(self, callback_query: CallbackQuery, ad_id: str):
        """Show individual ad for review"""
        try:
            if not self.is_admin(callback_query.from_user.id):
                await callback_query.answer("❌ Admin access required", show_alert=True)
                return
            
            async with self.auction_system.get_db_connection() as db:
                async with db.execute("""
                    SELECT ad_id, advertiser_id, content, image_url, category, bid_type, bid_amount, created_at
                    FROM auction_ads 
                    WHERE ad_id = ?
                """, (ad_id,)) as cursor:
                    ad = await cursor.fetchone()
            
            if not ad:
                await callback_query.answer("❌ Ad not found", show_alert=True)
                return
            
            ad_id, advertiser_id, content, image_url, category, bid_type, bid_amount, created_at = ad
            
            review_text = f"""
📋 **Ad Review: {ad_id}**

**Advertiser ID**: {advertiser_id}
**Category**: {category.title()}
**Bid Type**: {bid_type.upper()}
**Bid Amount**: ${bid_amount}
**Created**: {created_at}

**Content**:
{content}

**Image**: {'✅ Included' if image_url else '❌ No image'}

**Review Actions**:
"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Approve", callback_data=f"admin_approve_ad_{ad_id}"),
                    InlineKeyboardButton(text="❌ Reject", callback_data=f"admin_reject_ad_{ad_id}")
                ],
                [
                    InlineKeyboardButton(text="📝 View Full Content", callback_data=f"admin_view_ad_{ad_id}")
                ],
                [
                    InlineKeyboardButton(text="◀️ Back to Reviews", callback_data="admin_auction_review_ads")
                ]
            ])
            
            await callback_query.message.edit_text(
                review_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ Error showing ad review: {e}")
            await callback_query.answer("❌ Error loading ad")
    
    async def approve_ad(self, callback_query: CallbackQuery, ad_id: str):
        """Approve an ad"""
        try:
            if not self.is_admin(callback_query.from_user.id):
                await callback_query.answer("❌ Admin access required", show_alert=True)
                return
            
            # Update ad status
            await self.auction_system.update_ad_status(ad_id, AdStatus.APPROVED)
            
            # Get advertiser ID to notify
            async with self.auction_system.get_db_connection() as db:
                async with db.execute("""
                    SELECT advertiser_id FROM auction_ads WHERE ad_id = ?
                """, (ad_id,)) as cursor:
                    result = await cursor.fetchone()
                    
                    if result:
                        advertiser_id = result[0]
                        
                        # Notify advertiser
                        try:
                            await self.bot.send_message(
                                advertiser_id,
                                f"""
🎉 **Ad Approved!**

Your ad **{ad_id}** has been approved and is now eligible for daily auctions.

**Next Steps**:
• Your ad will participate in the next daily auction
• You'll be notified when it's published
• Use /stats to track performance

Good luck with your campaign! 🚀
""",
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"❌ Error notifying advertiser: {e}")
            
            await callback_query.message.edit_text(
                f"✅ **Ad Approved**: {ad_id}\n\nThe advertiser has been notified and the ad is now eligible for auctions.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="◀️ Back to Reviews", callback_data="admin_auction_review_ads")]
                ]),
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Ad {ad_id} approved by admin {callback_query.from_user.id}")
            
        except Exception as e:
            logger.error(f"❌ Error approving ad: {e}")
            await callback_query.answer("❌ Error approving ad")
    
    async def reject_ad(self, callback_query: CallbackQuery, ad_id: str):
        """Reject an ad"""
        try:
            if not self.is_admin(callback_query.from_user.id):
                await callback_query.answer("❌ Admin access required", show_alert=True)
                return
            
            # Update ad status
            await self.auction_system.update_ad_status(ad_id, AdStatus.REJECTED)
            
            # Get advertiser ID to notify
            async with self.auction_system.get_db_connection() as db:
                async with db.execute("""
                    SELECT advertiser_id FROM auction_ads WHERE ad_id = ?
                """, (ad_id,)) as cursor:
                    result = await cursor.fetchone()
                    
                    if result:
                        advertiser_id = result[0]
                        
                        # Notify advertiser
                        try:
                            await self.bot.send_message(
                                advertiser_id,
                                f"""
❌ **Ad Rejected**

Your ad **{ad_id}** has been rejected and will not participate in auctions.

**Common reasons for rejection**:
• Inappropriate content
• Misleading information
• Violation of platform policies

You can create a new ad with /createad if you'd like to try again.

Contact support if you have questions.
""",
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"❌ Error notifying advertiser: {e}")
            
            await callback_query.message.edit_text(
                f"❌ **Ad Rejected**: {ad_id}\n\nThe advertiser has been notified.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="◀️ Back to Reviews", callback_data="admin_auction_review_ads")]
                ]),
                parse_mode='Markdown'
            )
            
            logger.info(f"❌ Ad {ad_id} rejected by admin {callback_query.from_user.id}")
            
        except Exception as e:
            logger.error(f"❌ Error rejecting ad: {e}")
            await callback_query.answer("❌ Error rejecting ad")
    
    async def run_manual_auction(self, callback_query: CallbackQuery):
        """Run manual auction"""
        try:
            if not self.is_admin(callback_query.from_user.id):
                await callback_query.answer("❌ Admin access required", show_alert=True)
                return
            
            await callback_query.message.edit_text(
                "🎯 **Running Auction...**\n\nPlease wait while the system processes all categories...",
                parse_mode='Markdown'
            )
            
            # Run auction
            results = await self.auction_system.run_daily_auction()
            
            # Create results summary
            total_matches = sum(len(category_results) for category_results in results.values())
            
            results_text = f"""
🎯 **Auction Complete!**

**Results Summary**:
• Total Matches: {total_matches}
• Categories Processed: {len(results)}

**Category Breakdown**:
"""
            
            for category, category_results in results.items():
                results_text += f"• {category.title()}: {len(category_results)} matches\n"
            
            results_text += f"""
**Next Steps**:
• Scheduled ads will be published automatically
• Channel owners will receive their revenue share
• Advertisers will be notified of placements

Auction completed successfully! 🚀
"""
            
            await callback_query.message.edit_text(
                results_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="◀️ Back", callback_data="admin_auction_menu")]
                ]),
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Manual auction run by admin {callback_query.from_user.id}: {total_matches} matches")
            
        except Exception as e:
            logger.error(f"❌ Error running manual auction: {e}")
            await callback_query.answer("❌ Error running auction")
    
    async def show_auction_stats(self, callback_query: CallbackQuery):
        """Show detailed auction statistics"""
        try:
            if not self.is_admin(callback_query.from_user.id):
                await callback_query.answer("❌ Admin access required", show_alert=True)
                return
            
            async with self.auction_system.get_db_connection() as db:
                # Get comprehensive stats
                stats = {}
                
                # Total ads by status
                async with db.execute("""
                    SELECT status, COUNT(*) FROM auction_ads GROUP BY status
                """) as cursor:
                    stats['ads_by_status'] = dict(await cursor.fetchall())
                
                # Total channels by category
                async with db.execute("""
                    SELECT category, COUNT(*) FROM auction_channels GROUP BY category
                """) as cursor:
                    stats['channels_by_category'] = dict(await cursor.fetchall())
                
                # Revenue statistics
                async with db.execute("""
                    SELECT 
                        COUNT(*) as total_earnings,
                        SUM(amount) as total_revenue,
                        AVG(amount) as avg_earning
                    FROM earnings_log
                """) as cursor:
                    revenue_stats = await cursor.fetchone()
                    stats['revenue'] = {
                        'total_earnings': revenue_stats[0] or 0,
                        'total_revenue': revenue_stats[1] or 0,
                        'avg_earning': revenue_stats[2] or 0
                    }
                
                # Top performing categories
                async with db.execute("""
                    SELECT category, SUM(amount) as revenue
                    FROM earnings_log el
                    JOIN auction_ads aa ON el.ad_id = aa.ad_id
                    GROUP BY category
                    ORDER BY revenue DESC
                    LIMIT 5
                """) as cursor:
                    stats['top_categories'] = await cursor.fetchall()
            
            stats_text = f"""
📊 **Auction Statistics**

**📋 Ads Overview**:
"""
            
            for status, count in stats['ads_by_status'].items():
                stats_text += f"• {status.title()}: {count}\n"
            
            stats_text += f"""
**📺 Channels by Category**:
"""
            
            for category, count in stats['channels_by_category'].items():
                stats_text += f"• {category.title()}: {count}\n"
            
            stats_text += f"""
**💰 Revenue Statistics**:
• Total Earnings: {stats['revenue']['total_earnings']}
• Total Revenue: ${stats['revenue']['total_revenue']:.2f}
• Average Earning: ${stats['revenue']['avg_earning']:.2f}

**🏆 Top Categories by Revenue**:
"""
            
            for category, revenue in stats['top_categories']:
                stats_text += f"• {category.title()}: ${revenue:.2f}\n"
            
            await callback_query.message.edit_text(
                stats_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_auction_stats")],
                    [InlineKeyboardButton(text="◀️ Back", callback_data="admin_auction_menu")]
                ]),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ Error showing auction stats: {e}")
            await callback_query.answer("❌ Error loading stats")

# Global admin instance
auction_admin = None

def setup_auction_admin_handlers(dp, bot, database):
    """Setup auction admin handlers"""
    global auction_admin
    auction_admin = AuctionAdminSystem(bot, database)
    
    # Register callbacks
    dp.callback_query.register(
        auction_admin.show_auction_admin_menu,
        lambda c: c.data == "admin_auction_menu"
    )
    
    dp.callback_query.register(
        auction_admin.show_pending_ads,
        lambda c: c.data == "admin_auction_review_ads"
    )
    
    dp.callback_query.register(
        lambda c: auction_admin.show_ad_review(c, c.data.split('_')[-1]),
        lambda c: c.data.startswith("admin_review_ad_")
    )
    
    dp.callback_query.register(
        lambda c: auction_admin.approve_ad(c, c.data.split('_')[-1]),
        lambda c: c.data.startswith("admin_approve_ad_")
    )
    
    dp.callback_query.register(
        lambda c: auction_admin.reject_ad(c, c.data.split('_')[-1]),
        lambda c: c.data.startswith("admin_reject_ad_")
    )
    
    dp.callback_query.register(
        auction_admin.run_manual_auction,
        lambda c: c.data == "admin_auction_run"
    )
    
    dp.callback_query.register(
        auction_admin.show_auction_stats,
        lambda c: c.data == "admin_auction_stats"
    )
    
    logger.info("✅ Auction admin handlers registered")

async def initialize_auction_admin():
    """Initialize auction admin system"""
    global auction_admin
    if auction_admin:
        await auction_admin.initialize()
        logger.info("✅ Auction admin system initialized")