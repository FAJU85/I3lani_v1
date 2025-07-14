"""
I3lani v3 Integration Main
Complete integration with existing bot infrastructure
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from i3lani_v3_architecture import i3lani_v3
from v3_bot_commands import setup_v3_handlers
from v3_auction_scheduler import get_auction_scheduler
from v3_payment_integration import V3PaymentHandlers, get_payment_processor

logger = logging.getLogger(__name__)

class I3laniV3Integration:
    """Main integration class for I3lani v3"""
    
    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self.auction_scheduler = None
        self.payment_handlers = None
        self.is_initialized = False
    
    async def initialize_v3_system(self):
        """Initialize complete I3lani v3 system"""
        if self.is_initialized:
            return
        
        try:
            logger.info("🚀 Initializing I3lani v3 system...")
            
            # Initialize core architecture
            await i3lani_v3.initialize()
            
            # Initialize auction scheduler
            self.auction_scheduler = get_auction_scheduler(self.bot)
            await self.auction_scheduler.start_scheduler()
            
            # Initialize payment handlers
            self.payment_handlers = V3PaymentHandlers(self.bot)
            
            # Setup command handlers
            setup_v3_handlers(self.dp, self.bot)
            
            # Register payment handlers
            self.dp.callback_query.register(
                self.payment_handlers.handle_ton_payment_callback,
                lambda c: c.data.startswith(("pay_ton_", "ton_confirm_", "pay_stars_", "payment_cancel_"))
            )
            
            self.dp.message.register(
                self.payment_handlers.handle_stars_payment_success,
                lambda m: m.successful_payment is not None
            )
            
            # Register click tracking handler
            self.dp.message.register(
                self.handle_click_tracking,
                Command("start"),
                lambda m: m.text and "click_" in m.text
            )
            
            self.is_initialized = True
            
            logger.info("✅ I3lani v3 system initialized successfully")
            logger.info("   🎯 Auction system: Active")
            logger.info("   💰 Payment system: TON + Stars")
            logger.info("   👥 User roles: Advertiser, Channel Owner, Affiliate")
            logger.info("   🔄 Daily auctions: 9:00 AM")
            logger.info("   💸 Revenue sharing: 68% to channel owners")
            logger.info("   🎁 Affiliate commission: 5%")
            logger.info("   💎 Minimum withdrawal: $50")
            
        except Exception as e:
            logger.error(f"❌ V3 initialization error: {e}")
            raise
    
    async def handle_click_tracking(self, message: Message, state: FSMContext):
        """Handle click tracking from ads"""
        try:
            command_text = message.text
            if "click_" in command_text:
                placement_id = command_text.split("click_")[1]
                
                # Record click
                await self.auction_scheduler.handle_click_tracking(
                    user_id=message.from_user.id,
                    placement_id=placement_id
                )
                
        except Exception as e:
            logger.error(f"❌ Click tracking error: {e}")
    
    async def get_v3_stats(self):
        """Get I3lani v3 system statistics"""
        try:
            # Get auction stats
            auction_stats = await self.auction_scheduler.get_auction_stats()
            
            # Get system totals
            async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
                # Total users
                async with db.execute("SELECT COUNT(*) FROM users_v3") as cursor:
                    total_users = (await cursor.fetchone())[0]
                
                # Total channels
                async with db.execute("SELECT COUNT(*) FROM channels_v3 WHERE is_active = TRUE") as cursor:
                    total_channels = (await cursor.fetchone())[0]
                
                # Total ads
                async with db.execute("SELECT COUNT(*) FROM ads_v3") as cursor:
                    total_ads = (await cursor.fetchone())[0]
                
                # Total revenue
                async with db.execute("SELECT SUM(revenue) FROM ad_placements_v3") as cursor:
                    total_revenue = (await cursor.fetchone())[0] or 0
                
                # Active advertisers
                async with db.execute("SELECT COUNT(*) FROM users_v3 WHERE user_type = 'advertiser'") as cursor:
                    advertisers = (await cursor.fetchone())[0]
                
                # Active channel owners
                async with db.execute("SELECT COUNT(*) FROM users_v3 WHERE user_type = 'channel_owner'") as cursor:
                    channel_owners = (await cursor.fetchone())[0]
                
                # Active affiliates
                async with db.execute("SELECT COUNT(*) FROM users_v3 WHERE user_type = 'affiliate'") as cursor:
                    affiliates = (await cursor.fetchone())[0]
            
            return {
                'system_stats': {
                    'total_users': total_users,
                    'total_channels': total_channels,
                    'total_ads': total_ads,
                    'total_revenue': float(total_revenue),
                    'advertisers': advertisers,
                    'channel_owners': channel_owners,
                    'affiliates': affiliates
                },
                'auction_stats': auction_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Stats error: {e}")
            return None
    
    async def admin_approve_ad(self, ad_id: str, admin_id: int):
        """Admin function to approve ads"""
        try:
            async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
                # Update ad status
                await db.execute("""
                    UPDATE ads_v3 SET status = 'approved' WHERE ad_id = ?
                """, (ad_id,))
                
                # Get advertiser info
                async with db.execute("""
                    SELECT advertiser_id, content, category, bid_type, bid_amount
                    FROM ads_v3 WHERE ad_id = ?
                """, (ad_id,)) as cursor:
                    ad_info = await cursor.fetchone()
                
                if ad_info:
                    advertiser_id, content, category, bid_type, bid_amount = ad_info
                    
                    # Notify advertiser
                    await self.bot.send_message(
                        chat_id=advertiser_id,
                        text=f"✅ Ad Approved!\n\n"
                             f"🎯 Ad ID: {ad_id}\n"
                             f"📂 Category: {category}\n"
                             f"💰 Bid: ${bid_amount} {bid_type}\n\n"
                             f"Your ad will enter the next daily auction!"
                    )
                
                await db.commit()
                
                return {'success': True, 'message': 'Ad approved'}
                
        except Exception as e:
            logger.error(f"❌ Ad approval error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def admin_reject_ad(self, ad_id: str, admin_id: int, reason: str = ""):
        """Admin function to reject ads"""
        try:
            async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
                # Update ad status
                await db.execute("""
                    UPDATE ads_v3 SET status = 'rejected' WHERE ad_id = ?
                """, (ad_id,))
                
                # Get advertiser info
                async with db.execute("""
                    SELECT advertiser_id, content, category
                    FROM ads_v3 WHERE ad_id = ?
                """, (ad_id,)) as cursor:
                    ad_info = await cursor.fetchone()
                
                if ad_info:
                    advertiser_id, content, category = ad_info
                    
                    # Notify advertiser
                    await self.bot.send_message(
                        chat_id=advertiser_id,
                        text=f"❌ Ad Rejected\n\n"
                             f"🎯 Ad ID: {ad_id}\n"
                             f"📂 Category: {category}\n\n"
                             f"Reason: {reason or 'Policy violation'}\n\n"
                             f"You can create a new ad anytime."
                    )
                
                await db.commit()
                
                return {'success': True, 'message': 'Ad rejected'}
                
        except Exception as e:
            logger.error(f"❌ Ad rejection error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def force_run_auction(self):
        """Force run auction (admin function)"""
        try:
            if self.auction_scheduler:
                await self.auction_scheduler.run_auction()
                return {'success': True, 'message': 'Auction completed'}
            else:
                return {'success': False, 'error': 'Auction scheduler not initialized'}
                
        except Exception as e:
            logger.error(f"❌ Force auction error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def shutdown_v3_system(self):
        """Shutdown I3lani v3 system"""
        try:
            if self.auction_scheduler:
                await self.auction_scheduler.stop_scheduler()
            
            self.is_initialized = False
            logger.info("⏹️ I3lani v3 system shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ V3 shutdown error: {e}")

# Global integration instance
v3_integration = None

def get_v3_integration(bot: Bot, dp: Dispatcher) -> I3laniV3Integration:
    """Get or create V3 integration instance"""
    global v3_integration
    if v3_integration is None:
        v3_integration = I3laniV3Integration(bot, dp)
    return v3_integration

async def initialize_i3lani_v3(bot: Bot, dp: Dispatcher):
    """Initialize I3lani v3 system"""
    integration = get_v3_integration(bot, dp)
    await integration.initialize_v3_system()
    return integration