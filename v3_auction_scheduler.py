"""
I3lani v3 Auction Scheduler
Daily auction system and ad posting automation
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import List, Dict
from aiogram import Bot
from aiogram.types import InputMediaPhoto, InputMediaVideo
import aiosqlite

from i3lani_v3_architecture import i3lani_v3

logger = logging.getLogger(__name__)

class V3AuctionScheduler:
    """Daily auction scheduler and ad posting system"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.auction_time = time(9, 0)  # 9:00 AM daily
        self.is_running = False
        self.posted_ads = set()  # Track posted ads to avoid duplicates
    
    async def start_scheduler(self):
        """Start the daily auction scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🕒 Starting I3lani v3 auction scheduler...")
        
        # Run initial auction if needed
        await self.check_and_run_auction()
        
        # Start daily scheduler
        asyncio.create_task(self.daily_auction_loop())
        
        # Start ad posting monitor
        asyncio.create_task(self.ad_posting_monitor())
    
    async def daily_auction_loop(self):
        """Daily auction loop"""
        while self.is_running:
            try:
                now = datetime.now()
                auction_datetime = datetime.combine(now.date(), self.auction_time)
                
                # If auction time has passed today, schedule for tomorrow
                if now > auction_datetime:
                    auction_datetime += timedelta(days=1)
                
                # Wait until auction time
                wait_seconds = (auction_datetime - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
                # Run auction
                await self.run_auction()
                
            except Exception as e:
                logger.error(f"❌ Error in daily auction loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def check_and_run_auction(self):
        """Check if auction needs to run today"""
        today = datetime.now().date()
        
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            # Check if auction already ran today
            async with db.execute("""
                SELECT COUNT(*) FROM ad_placements_v3 
                WHERE placement_date = ?
            """, (today,)) as cursor:
                result = await cursor.fetchone()
                
                if result[0] == 0:
                    logger.info("🔄 Running initial auction for today...")
                    await self.run_auction()
    
    async def run_auction(self):
        """Run the daily auction"""
        try:
            logger.info("🎯 Running daily auction...")
            
            # Run auction system
            placements = await i3lani_v3.auction.run_daily_auction()
            
            if placements:
                # Schedule ad posting
                await self.schedule_ad_posting(placements)
                
                # Update ad status to active
                await self.update_ad_status(placements)
                
                logger.info(f"✅ Auction completed: {len(placements)} ads scheduled")
            else:
                logger.info("ℹ️ No ads to auction today")
                
        except Exception as e:
            logger.error(f"❌ Auction error: {e}")
    
    async def schedule_ad_posting(self, placements: List[Dict]):
        """Schedule ad posting throughout the day"""
        # Post ads immediately after auction
        for placement in placements:
            try:
                await self.post_ad_to_channel(placement)
                await asyncio.sleep(5)  # 5-second delay between posts
            except Exception as e:
                logger.error(f"❌ Error posting ad {placement['ad_id']}: {e}")
    
    async def post_ad_to_channel(self, placement: Dict):
        """Post ad to specific channel"""
        try:
            channel_id = placement['channel_id']
            ad_id = placement['ad_id']
            content = placement['content']
            bid_type = placement['bid_type']
            
            # Create trackable link for CPC ads
            if bid_type == 'CPC':
                trackable_link = f"https://t.me/{(await self.bot.get_me()).username}?start=click_{placement['placement_id']}"
                content += f"\n\n👆 Click here: {trackable_link}"
            
            # Post ad
            message = await self.bot.send_message(
                chat_id=channel_id,
                text=content,
                parse_mode="HTML"
            )
            
            # Record impression
            await self.record_impression(placement['placement_id'])
            
            # Add to posted ads
            self.posted_ads.add(placement['placement_id'])
            
            logger.info(f"✅ Posted ad {ad_id} to channel {channel_id}")
            
        except Exception as e:
            logger.error(f"❌ Error posting ad to channel {channel_id}: {e}")
    
    async def update_ad_status(self, placements: List[Dict]):
        """Update ad status to active"""
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            ad_ids = [p['ad_id'] for p in placements]
            
            for ad_id in ad_ids:
                await db.execute("""
                    UPDATE ads_v3 SET status = 'active' WHERE ad_id = ?
                """, (ad_id,))
            
            await db.commit()
    
    async def record_impression(self, placement_id: str):
        """Record impression for ad placement"""
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            await db.execute("""
                UPDATE ad_placements_v3 
                SET impressions = impressions + 1
                WHERE placement_id = ?
            """, (placement_id,))
            await db.commit()
    
    async def record_click(self, placement_id: str):
        """Record click for ad placement"""
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            await db.execute("""
                UPDATE ad_placements_v3 
                SET clicks = clicks + 1
                WHERE placement_id = ?
            """, (placement_id,))
            await db.commit()
            
            # Calculate and distribute revenue
            await i3lani_v3.revenue.calculate_placement_revenue(placement_id, 0, 1)
    
    async def handle_click_tracking(self, user_id: int, placement_id: str):
        """Handle click tracking from trackable links"""
        try:
            await self.record_click(placement_id)
            
            # Send click confirmation to user
            await self.bot.send_message(
                chat_id=user_id,
                text="✅ Thank you for your interest! The advertiser has been notified."
            )
            
        except Exception as e:
            logger.error(f"❌ Error handling click tracking: {e}")
    
    async def ad_posting_monitor(self):
        """Monitor and post ads throughout the day"""
        while self.is_running:
            try:
                # Check for new placements to post
                today = datetime.now().date()
                
                async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
                    async with db.execute("""
                        SELECT p.placement_id, p.ad_id, p.channel_id, a.content, a.bid_type
                        FROM ad_placements_v3 p
                        JOIN ads_v3 a ON p.ad_id = a.ad_id
                        WHERE p.placement_date = ? AND p.placement_id NOT IN ({})
                    """.format(','.join(['?'] * len(self.posted_ads))), 
                    (today, *self.posted_ads)) as cursor:
                        unposted_placements = await cursor.fetchall()
                
                # Post any unposted ads
                for placement in unposted_placements:
                    placement_dict = {
                        'placement_id': placement[0],
                        'ad_id': placement[1],
                        'channel_id': placement[2],
                        'content': placement[3],
                        'bid_type': placement[4]
                    }
                    await self.post_ad_to_channel(placement_dict)
                    await asyncio.sleep(30)  # 30-second delay between posts
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Error in ad posting monitor: {e}")
                await asyncio.sleep(3600)
    
    async def get_auction_stats(self) -> Dict:
        """Get auction statistics"""
        today = datetime.now().date()
        
        async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
            # Today's placements
            async with db.execute("""
                SELECT COUNT(*) FROM ad_placements_v3 WHERE placement_date = ?
            """, (today,)) as cursor:
                todays_placements = (await cursor.fetchone())[0]
            
            # Total impressions today
            async with db.execute("""
                SELECT SUM(impressions) FROM ad_placements_v3 WHERE placement_date = ?
            """, (today,)) as cursor:
                todays_impressions = (await cursor.fetchone())[0] or 0
            
            # Total clicks today
            async with db.execute("""
                SELECT SUM(clicks) FROM ad_placements_v3 WHERE placement_date = ?
            """, (today,)) as cursor:
                todays_clicks = (await cursor.fetchone())[0] or 0
            
            # Total revenue today
            async with db.execute("""
                SELECT SUM(revenue) FROM ad_placements_v3 WHERE placement_date = ?
            """, (today,)) as cursor:
                todays_revenue = (await cursor.fetchone())[0] or 0
            
            return {
                'todays_placements': todays_placements,
                'todays_impressions': todays_impressions,
                'todays_clicks': todays_clicks,
                'todays_revenue': float(todays_revenue),
                'posted_ads': len(self.posted_ads)
            }
    
    async def stop_scheduler(self):
        """Stop the auction scheduler"""
        self.is_running = False
        logger.info("⏹️ Auction scheduler stopped")

# Global scheduler instance
auction_scheduler = None

def get_auction_scheduler(bot: Bot) -> V3AuctionScheduler:
    """Get or create auction scheduler instance"""
    global auction_scheduler
    if auction_scheduler is None:
        auction_scheduler = V3AuctionScheduler(bot)
    return auction_scheduler