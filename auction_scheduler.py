"""
Auction Scheduler for I3lani Bot
Daily auction system with automated posting and performance tracking
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List
import threading
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from auction_advertising_system import get_auction_system, AdStatus
from database import Database

logger = logging.getLogger(__name__)

class AuctionScheduler:
    def __init__(self, bot: Bot, database: Database):
        self.bot = bot
        self.db = database
        self.auction_system = None
        self.scheduler_thread = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize auction scheduler"""
        self.auction_system = await get_auction_system()
        logger.info("✅ Auction scheduler initialized")
        
    def start_scheduler(self):
        """Start the auction scheduler"""
        if self.is_running:
            logger.warning("⚠️ Auction scheduler already running")
            return
        
        self.is_running = True
        
        # Schedule daily auction at 9:00 AM
        schedule.every().day.at("09:00").do(self.run_daily_auction_job)
        
        # Schedule ad posting every 30 minutes
        schedule.every(30).minutes.do(self.post_scheduled_ads_job)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("✅ Auction scheduler started")
        logger.info("   📅 Daily auctions at 9:00 AM")
        logger.info("   📤 Ad posting every 30 minutes")
    
    def stop_scheduler(self):
        """Stop the auction scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("⏹️ Auction scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(60)
    
    def run_daily_auction_job(self):
        """Job wrapper for daily auction"""
        try:
            # Run auction in async context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_daily_auction())
            loop.close()
        except Exception as e:
            logger.error(f"❌ Daily auction job error: {e}")
    
    def post_scheduled_ads_job(self):
        """Job wrapper for posting scheduled ads"""
        try:
            # Run ad posting in async context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.post_scheduled_ads())
            loop.close()
        except Exception as e:
            logger.error(f"❌ Ad posting job error: {e}")
    
    async def run_daily_auction(self):
        """Run daily auction"""
        try:
            logger.info("🎯 Starting daily auction...")
            
            # Run auction
            results = await self.auction_system.run_daily_auction()
            
            # Count total matches
            total_matches = sum(len(category_results) for category_results in results.values())
            
            logger.info(f"✅ Daily auction completed: {total_matches} matches")
            
            # Notify admin about auction results
            await self.notify_admin_auction_results(results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Daily auction error: {e}")
            return {}
    
    async def post_scheduled_ads(self):
        """Post scheduled ads to channels"""
        try:
            logger.info("📤 Checking for scheduled ads...")
            
            # Get ads scheduled for posting
            current_time = datetime.now()
            
            async with self.auction_system.get_db_connection() as db:
                async with db.execute("""
                    SELECT ar.auction_id, ar.channel_id, ar.ad_id, ar.winning_bid,
                           aa.content, aa.image_url, aa.advertiser_id, aa.bid_type
                    FROM auction_results ar
                    JOIN auction_ads aa ON ar.ad_id = aa.ad_id
                    WHERE ar.scheduled_date <= ? AND aa.status = 'scheduled'
                """, (current_time.isoformat(),)) as cursor:
                    scheduled_ads = await cursor.fetchall()
            
            if not scheduled_ads:
                logger.info("📭 No ads scheduled for posting")
                return
            
            logger.info(f"📤 Found {len(scheduled_ads)} ads to post")
            
            # Post each ad
            for ad_data in scheduled_ads:
                await self.post_ad_to_channel(ad_data)
            
        except Exception as e:
            logger.error(f"❌ Error posting scheduled ads: {e}")
    
    async def post_ad_to_channel(self, ad_data):
        """Post individual ad to channel"""
        try:
            auction_id, channel_id, ad_id, winning_bid, content, image_url, advertiser_id, bid_type = ad_data
            
            # Create tracking URL if needed
            if bid_type == 'cpc':
                # For CPC ads, create trackable links
                tracking_url = await self.auction_system.create_tracking_url(ad_id, "https://t.me/i3lani_bot")
                content = f"{content}\n\n🔗 Learn more: {tracking_url}"
            
            # Post to channel
            try:
                if image_url:
                    # Post with image
                    await self.bot.send_photo(
                        chat_id=channel_id,
                        photo=image_url,
                        caption=content,
                        parse_mode='Markdown'
                    )
                else:
                    # Post text only
                    await self.bot.send_message(
                        chat_id=channel_id,
                        text=content,
                        parse_mode='Markdown'
                    )
                
                # Track impression
                await self.auction_system.track_impression(ad_id, channel_id)
                
                # Update ad status to active
                await self.auction_system.update_ad_status(ad_id, AdStatus.ACTIVE)
                
                # Calculate and distribute CPM revenue if applicable
                if bid_type == 'cpm':
                    await self.calculate_cpm_revenue(ad_id, channel_id, winning_bid)
                
                # Notify advertiser
                await self.notify_advertiser_ad_posted(advertiser_id, ad_id, channel_id)
                
                logger.info(f"✅ Posted ad {ad_id} to channel {channel_id}")
                
            except TelegramBadRequest as e:
                logger.error(f"❌ Telegram error posting ad {ad_id}: {e}")
                
                # Notify admin about posting failure
                await self.notify_admin_posting_error(ad_id, channel_id, str(e))
                
        except Exception as e:
            logger.error(f"❌ Error posting ad to channel: {e}")
    
    async def calculate_cpm_revenue(self, ad_id: str, channel_id: str, bid_amount: float):
        """Calculate CPM revenue (pay per 1000 impressions)"""
        try:
            # Get channel subscriber count for CPM calculation
            async with self.auction_system.get_db_connection() as db:
                async with db.execute("""
                    SELECT subscribers FROM auction_channels WHERE channel_id = ?
                """, (channel_id,)) as cursor:
                    result = await cursor.fetchone()
                    
                    if result:
                        subscribers = result[0]
                        # Calculate CPM payment (impressions = estimated reach = 45% of subscribers)
                        estimated_reach = int(subscribers * 0.45)
                        cpm_payment = (estimated_reach / 1000) * bid_amount
                        
                        # Distribute revenue
                        from decimal import Decimal
                        await self.auction_system.calculate_and_distribute_revenue(
                            ad_id, channel_id, Decimal(str(cpm_payment)), 'cpm'
                        )
                        
                        logger.info(f"💰 CPM revenue calculated: ${cpm_payment:.2f} for {estimated_reach} impressions")
                        
        except Exception as e:
            logger.error(f"❌ Error calculating CPM revenue: {e}")
    
    async def notify_admin_auction_results(self, results: Dict):
        """Notify admin about auction results"""
        try:
            admin_ids = [566158428]  # Default admin ID
            
            total_matches = sum(len(category_results) for category_results in results.values())
            
            message = f"""
🎯 **Daily Auction Results**

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total Matches**: {total_matches}

**Category Breakdown**:
"""
            
            for category, category_results in results.items():
                message += f"• {category.title()}: {len(category_results)} matches\n"
            
            message += f"""
**Next Steps**:
• Ads will be posted automatically over the next hour
• Channel owners will receive their revenue share
• Performance tracking is active

System operating normally! 🚀
"""
            
            for admin_id in admin_ids:
                try:
                    await self.bot.send_message(
                        admin_id,
                        message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"❌ Error notifying admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error sending admin notification: {e}")
    
    async def notify_advertiser_ad_posted(self, advertiser_id: int, ad_id: str, channel_id: str):
        """Notify advertiser that their ad was posted"""
        try:
            message = f"""
🎉 **Your Ad is Live!**

**Ad ID**: {ad_id}
**Channel**: {channel_id}
**Posted**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Your advertisement is now live and reaching targeted audiences. 

**Track Performance**:
• Use /stats to monitor clicks and impressions
• Real-time performance updates available
• Revenue sharing active for channel owners

Thank you for using I3lani! 🚀
"""
            
            await self.bot.send_message(
                advertiser_id,
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ Error notifying advertiser {advertiser_id}: {e}")
    
    async def notify_admin_posting_error(self, ad_id: str, channel_id: str, error: str):
        """Notify admin about posting errors"""
        try:
            admin_ids = [566158428]  # Default admin ID
            
            message = f"""
❌ **Ad Posting Error**

**Ad ID**: {ad_id}
**Channel**: {channel_id}
**Error**: {error}
**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Please check channel permissions and try manual posting if needed.
"""
            
            for admin_id in admin_ids:
                try:
                    await self.bot.send_message(
                        admin_id,
                        message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"❌ Error notifying admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error sending admin error notification: {e}")

# Global scheduler instance
auction_scheduler = None

async def initialize_auction_scheduler(bot: Bot, database: Database):
    """Initialize auction scheduler"""
    global auction_scheduler
    auction_scheduler = AuctionScheduler(bot, database)
    await auction_scheduler.initialize()
    auction_scheduler.start_scheduler()
    return auction_scheduler

def get_auction_scheduler():
    """Get auction scheduler instance"""
    return auction_scheduler