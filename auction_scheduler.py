"""
Auction Scheduler for I3lani Bot
Handles daily auctions and ad posting automation
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading

from aiogram import Bot
from aiogram.types import InputMediaPhoto

from auction_advertising_system import get_auction_system, BidType
from database import Database

logger = logging.getLogger(__name__)

class AuctionScheduler:
    """Scheduler for daily auctions and ad posting"""
    
    def __init__(self, bot: Bot, database: Database):
        self.bot = bot
        self.db = database
        self.auction_system = get_auction_system()
        self.is_running = False
        self.scheduler_thread = None
    
    async def run_daily_auction(self):
        """Run daily auction process"""
        try:
            logger.info("🎯 Starting daily auction process...")
            
            # Run auction
            results = await self.auction_system.run_daily_auction()
            
            logger.info(f"✅ Daily auction completed: {results['total_auctions']} auctions")
            
            # Schedule ad posting
            await self.schedule_ad_posting(results['results'])
            
        except Exception as e:
            logger.error(f"❌ Daily auction failed: {e}")
    
    async def schedule_ad_posting(self, auction_results: List[Dict]):
        """Schedule ads for posting based on auction results"""
        try:
            logger.info(f"📅 Scheduling {len(auction_results)} ads for posting...")
            
            for result in auction_results:
                await self.post_winning_ad(result)
            
            logger.info("✅ All winning ads posted successfully")
            
        except Exception as e:
            logger.error(f"❌ Ad posting failed: {e}")
    
    async def post_winning_ad(self, auction_result: Dict):
        """Post winning ad to channel"""
        try:
            auction_id = auction_result['auction_id']
            channel_id = auction_result['channel_id']
            winning_ad_id = auction_result['winning_ad_id']
            
            # Get ad details
            ad_data = await self.get_ad_details(winning_ad_id)
            if not ad_data:
                logger.error(f"❌ No ad data found for ad {winning_ad_id}")
                return
            
            # Get channel details
            channel_data = await self.get_channel_details(channel_id)
            if not channel_data:
                logger.error(f"❌ No channel data found for channel {channel_id}")
                return
            
            telegram_channel_id = channel_data['telegram_channel_id']
            
            # Prepare ad content
            content = ad_data['content']
            image_url = ad_data['image_url']
            bid_type = ad_data['bid_type']
            
            # Add trackable link for CPC ads
            if bid_type == 'CPC':
                trackable_link = await self.auction_system.create_trackable_link(
                    winning_ad_id, channel_id, "https://example.com/landing"
                )
                content += f"\n\n🔗 {trackable_link}"
            
            # Post to channel
            if image_url:
                await self.bot.send_photo(
                    chat_id=telegram_channel_id,
                    photo=image_url,
                    caption=content
                )
            else:
                await self.bot.send_message(
                    chat_id=telegram_channel_id,
                    text=content
                )
            
            logger.info(f"✅ Posted ad {winning_ad_id} to channel {channel_id}")
            
            # Update ad status
            await self.update_ad_status(winning_ad_id, "active")
            
        except Exception as e:
            logger.error(f"❌ Failed to post ad {winning_ad_id}: {e}")
    
    async def get_ad_details(self, ad_id: int) -> Optional[Dict]:
        """Get ad details from database"""
        try:
            async with self.db.get_connection() as conn:
                async with conn.execute('''
                    SELECT ad_id, advertiser_id, content, image_url, 
                           category, bid_type, bid_amount, daily_budget
                    FROM auction_ads WHERE ad_id = ?
                ''', (ad_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        return {
                            'ad_id': row[0],
                            'advertiser_id': row[1],
                            'content': row[2],
                            'image_url': row[3],
                            'category': row[4],
                            'bid_type': row[5],
                            'bid_amount': row[6],
                            'daily_budget': row[7]
                        }
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error getting ad details: {e}")
            return None
    
    async def get_channel_details(self, channel_id: str) -> Optional[Dict]:
        """Get channel details from database"""
        try:
            async with self.db.get_connection() as conn:
                async with conn.execute('''
                    SELECT channel_id, owner_id, name, telegram_channel_id, 
                           category, subscribers
                    FROM auction_channels WHERE channel_id = ?
                ''', (channel_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        return {
                            'channel_id': row[0],
                            'owner_id': row[1],
                            'name': row[2],
                            'telegram_channel_id': row[3],
                            'category': row[4],
                            'subscribers': row[5]
                        }
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error getting channel details: {e}")
            return None
    
    async def update_ad_status(self, ad_id: int, status: str):
        """Update ad status in database"""
        try:
            async with self.db.get_connection() as conn:
                await conn.execute('''
                    UPDATE auction_ads 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE ad_id = ?
                ''', (status, ad_id))
                await conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error updating ad status: {e}")
    
    async def track_ad_performance(self):
        """Track performance of posted ads"""
        try:
            logger.info("📊 Tracking ad performance...")
            
            # Get active ads from yesterday
            yesterday = datetime.now().date() - timedelta(days=1)
            
            async with self.db.get_connection() as conn:
                async with conn.execute('''
                    SELECT da.winning_ad_id, da.channel_id, da.estimated_impressions
                    FROM daily_auctions da
                    WHERE DATE(da.auction_date) = ? AND da.status = 'completed'
                ''', (yesterday,)) as cursor:
                    active_ads = await cursor.fetchall()
            
            for ad_id, channel_id, estimated_impressions in active_ads:
                # Simulate performance tracking
                # In production, this would integrate with Telegram Analytics API
                # and link tracking services
                
                impressions = estimated_impressions
                clicks = max(1, int(impressions * 0.02))  # 2% CTR simulation
                
                # Update performance metrics
                await self.auction_system.update_performance_metrics(
                    ad_id, channel_id, impressions, clicks
                )
            
            logger.info(f"✅ Performance tracking completed for {len(active_ads)} ads")
            
        except Exception as e:
            logger.error(f"❌ Performance tracking failed: {e}")
    
    def start_scheduler(self):
        """Start the auction scheduler"""
        if self.is_running:
            logger.warning("⚠️ Scheduler already running")
            return
        
        self.is_running = True
        
        # Schedule daily auction at midnight
        schedule.every().day.at("00:00").do(lambda: asyncio.create_task(self.run_daily_auction()))
        
        # Schedule performance tracking at 2 AM
        schedule.every().day.at("02:00").do(lambda: asyncio.create_task(self.track_ad_performance()))
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("✅ Auction scheduler started")
    
    def stop_scheduler(self):
        """Stop the auction scheduler"""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("⏹️ Auction scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    async def run_test_auction(self):
        """Run a test auction for development"""
        try:
            logger.info("🧪 Running test auction...")
            
            # Create test data if needed
            await self._create_test_data()
            
            # Run auction
            results = await self.auction_system.run_daily_auction()
            
            logger.info(f"🧪 Test auction completed: {results}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Test auction failed: {e}")
            return None
    
    async def _create_test_data(self):
        """Create test data for development"""
        try:
            # This would create sample ads and channels for testing
            # Implementation depends on development needs
            pass
            
        except Exception as e:
            logger.error(f"❌ Failed to create test data: {e}")

# Global scheduler instance
auction_scheduler = None

def initialize_auction_scheduler(bot: Bot, database: Database):
    """Initialize the auction scheduler"""
    global auction_scheduler
    auction_scheduler = AuctionScheduler(bot, database)
    return auction_scheduler

def get_auction_scheduler() -> Optional[AuctionScheduler]:
    """Get the global auction scheduler instance"""
    return auction_scheduler

def start_auction_scheduler():
    """Start the auction scheduler"""
    if auction_scheduler:
        auction_scheduler.start_scheduler()
    else:
        logger.error("❌ Auction scheduler not initialized")

def stop_auction_scheduler():
    """Stop the auction scheduler"""
    if auction_scheduler:
        auction_scheduler.stop_scheduler()
    else:
        logger.error("❌ Auction scheduler not initialized")