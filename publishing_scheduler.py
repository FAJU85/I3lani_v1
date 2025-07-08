"""
Publishing Scheduler for I3lani Bot
Handles automatic ad publishing to channels based on subscription plans
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import db
from aiogram import Bot

logger = logging.getLogger(__name__)

class PublishingScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.running = False
        self.scheduler_task = None
        
    async def start_scheduler(self):
        """Start the publishing scheduler"""
        if self.running:
            return
            
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("✅ Publishing scheduler started")
        
    async def stop_scheduler(self):
        """Stop the publishing scheduler"""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ Publishing scheduler stopped")
        
    async def _scheduler_loop(self):
        """Main scheduler loop - runs every hour"""
        while self.running:
            try:
                await self._process_pending_publications()
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
                
    async def _process_pending_publications(self):
        """Process all pending publications"""
        try:
            # Get active subscriptions that need posting
            active_subscriptions = await self._get_active_subscriptions()
            
            for subscription in active_subscriptions:
                await self._publish_subscription_ad(subscription)
                
        except Exception as e:
            logger.error(f"Error processing publications: {e}")
            
    async def _get_active_subscriptions(self) -> List[Dict]:
        """Get all active subscriptions that need posting today"""
        import aiosqlite
        
        subscriptions = []
        try:
            async with aiosqlite.connect(db.db_path) as conn:
                conn.row_factory = aiosqlite.Row
                
                # Get active subscriptions with their ad content
                query = '''
                    SELECT s.*, a.content, a.media_url, a.content_type, c.telegram_channel_id, c.name as channel_name
                    FROM subscriptions s
                    JOIN ads a ON s.ad_id = a.ad_id
                    JOIN channels c ON s.channel_id = c.channel_id
                    WHERE s.status = 'active'
                    AND DATE(s.start_date) <= DATE('now')
                    AND DATE(s.end_date) >= DATE('now')
                    AND c.active = 1
                '''
                
                async with conn.execute(query) as cursor:
                    rows = await cursor.fetchall()
                    subscriptions = [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting active subscriptions: {e}")
            
        return subscriptions
        
    async def _publish_subscription_ad(self, subscription: Dict):
        """Publish ad for a specific subscription"""
        try:
            # Check if we should post today based on posts_per_day
            posts_per_day = subscription.get('posts_per_day', 1)
            
            # For now, publish once per day regardless of posts_per_day
            # In future, this can be enhanced to support multiple posts per day
            if not await self._should_post_today(subscription):
                return
                
            # Get channel info
            channel_id = subscription['telegram_channel_id']
            ad_content = subscription['content']
            media_url = subscription.get('media_url')
            content_type = subscription.get('content_type', 'text')
            
            # Format ad content
            formatted_content = f"📢 Advertisement\n\n{ad_content}\n\n💎 Advertise with @I3lani_bot"
            
            # Publish to channel
            success = await self._publish_to_channel(
                channel_id, 
                formatted_content, 
                media_url, 
                content_type
            )
            
            if success:
                # Update last published time
                await self._update_last_published(subscription['subscription_id'])
                logger.info(f"✅ Published ad {subscription['ad_id']} to {subscription['channel_name']}")
            else:
                logger.error(f"❌ Failed to publish ad {subscription['ad_id']} to {subscription['channel_name']}")
                
        except Exception as e:
            logger.error(f"Error publishing subscription ad: {e}")
            
    async def _should_post_today(self, subscription: Dict) -> bool:
        """Check if we should post today for this subscription"""
        try:
            # Get last published date
            import aiosqlite
            
            async with aiosqlite.connect(db.db_path) as conn:
                async with conn.execute(
                    'SELECT last_published FROM subscriptions WHERE subscription_id = ?',
                    (subscription['subscription_id'],)
                ) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row or not row[0]:
                        return True  # Never published, should post
                        
                    last_published = datetime.fromisoformat(row[0])
                    today = datetime.now().date()
                    
                    # Check if last published was before today
                    return last_published.date() < today
                    
        except Exception as e:
            logger.error(f"Error checking if should post today: {e}")
            return False
            
    async def _publish_to_channel(self, channel_id: str, content: str, media_url: Optional[str], content_type: str) -> bool:
        """Publish content to a specific channel"""
        try:
            if media_url and content_type in ['photo', 'video']:
                if content_type == 'photo':
                    await self.bot.send_photo(
                        chat_id=channel_id,
                        photo=media_url,
                        caption=content,
                        parse_mode='Markdown'
                    )
                elif content_type == 'video':
                    await self.bot.send_video(
                        chat_id=channel_id,
                        video=media_url,
                        caption=content,
                        parse_mode='Markdown'
                    )
            else:
                # Text message
                await self.bot.send_message(
                    chat_id=channel_id,
                    text=content,
                    parse_mode='Markdown'
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Error publishing to channel {channel_id}: {e}")
            return False
            
    async def _update_last_published(self, subscription_id: int):
        """Update the last published timestamp for a subscription"""
        try:
            import aiosqlite
            
            async with aiosqlite.connect(db.db_path) as conn:
                await conn.execute(
                    'UPDATE subscriptions SET last_published = ? WHERE subscription_id = ?',
                    (datetime.now().isoformat(), subscription_id)
                )
                await conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating last published: {e}")
            
    async def publish_immediately_after_payment(self, user_id: int, ad_id: int, selected_channels: List[str], subscription_data: Dict):
        """Publish ad immediately after successful payment to all selected channels"""
        try:
            # Get ad content
            ad_content = subscription_data.get('ad_content', '')
            media_url = subscription_data.get('media_url')
            content_type = subscription_data.get('content_type', 'text')
            
            if not ad_content:
                # Fallback content
                ad_content = "Your advertisement is now live! Contact @I3lani_bot for more details."
                
            # Format content
            formatted_content = f"📢 Advertisement\n\n{ad_content}\n\n💎 Advertise with @I3lani_bot"
            
            # Publish to all selected channels
            published_channels = []
            failed_channels = []
            
            # Get channel details
            all_channels = await db.get_channels(active_only=True)
            
            for channel_id in selected_channels:
                # Find channel details
                channel_info = None
                for channel in all_channels:
                    if channel['channel_id'] == channel_id:
                        channel_info = channel
                        break
                        
                if not channel_info:
                    continue
                    
                # Publish to channel
                success = await self._publish_to_channel(
                    channel_info['telegram_channel_id'],
                    formatted_content,
                    media_url,
                    content_type
                )
                
                if success:
                    published_channels.append(channel_info['name'])
                else:
                    failed_channels.append(channel_info['name'])
                    
            # Log results
            if published_channels:
                logger.info(f"✅ Published ad {ad_id} to channels: {', '.join(published_channels)}")
            if failed_channels:
                logger.error(f"❌ Failed to publish ad {ad_id} to channels: {', '.join(failed_channels)}")
                
            return len(published_channels) > 0
            
        except Exception as e:
            logger.error(f"Error in immediate publishing: {e}")
            return False

# Global scheduler instance
scheduler = None

def init_scheduler(bot: Bot):
    """Initialize the global scheduler"""
    global scheduler
    scheduler = PublishingScheduler(bot)
    return scheduler