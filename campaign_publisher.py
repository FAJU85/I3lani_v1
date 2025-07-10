"""
Campaign Publisher for I3lani Bot
Automated system to execute scheduled campaign posts
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

logger = logging.getLogger(__name__)

class CampaignPublisher:
    """Automated campaign post publisher"""
    
    def __init__(self, bot: Bot, db_path: str = "bot.db"):
        self.bot = bot
        self.db_path = db_path
        self.running = False
        
    async def start(self):
        """Start the campaign publisher"""
        if self.running:
            logger.warning("Campaign publisher is already running")
            return
            
        self.running = True
        logger.info("🚀 Starting campaign publisher...")
        
        # Start the publishing loop
        asyncio.create_task(self._publishing_loop())
        logger.info("✅ Campaign publisher started successfully")
    
    async def stop(self):
        """Stop the campaign publisher"""
        self.running = False
        logger.info("🛑 Campaign publisher stopped")
    
    async def _publishing_loop(self):
        """Main publishing loop - runs every 60 seconds"""
        while self.running:
            try:
                await self._process_scheduled_posts()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"❌ Error in campaign publisher loop: {e}")
                await asyncio.sleep(60)  # Continue despite errors
    
    async def _process_scheduled_posts(self):
        """Process all scheduled posts that are due"""
        try:
            # Get posts that are due for publishing
            due_posts = await self._get_due_posts()
            
            if not due_posts:
                logger.debug("No campaign posts due for publishing")
                return
            
            logger.info(f"📋 Found {len(due_posts)} posts due for publishing")
            
            # Process each post
            for post in due_posts:
                try:
                    await self._publish_single_post(post)
                except Exception as e:
                    logger.error(f"❌ Error publishing post {post['id']}: {e}")
                    # Mark as failed but continue with other posts
                    await self._mark_post_failed(post['id'], str(e))
                    
        except Exception as e:
            logger.error(f"❌ Error processing scheduled posts: {e}")
    
    async def _get_due_posts(self) -> List[Dict]:
        """Get all posts that are scheduled and due for publishing"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get posts scheduled for now or past due
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                SELECT cp.*, c.ad_content, c.user_id, c.campaign_name
                FROM campaign_posts cp
                JOIN campaigns c ON cp.campaign_id = c.campaign_id
                WHERE cp.status = 'scheduled'
                AND cp.scheduled_time <= ?
                ORDER BY cp.scheduled_time ASC
                LIMIT 50
            """, (now,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Error getting due posts: {e}")
            return []
    
    async def _publish_single_post(self, post: Dict):
        """Publish a single scheduled post"""
        try:
            # Get channel information
            channel_username = post['channel_id']  # e.g., @i3lani
            campaign_id = post['campaign_id']
            ad_content = post['ad_content']
            post_id = post['id']
            
            # Format the content for posting
            formatted_content = self._format_post_content(ad_content, campaign_id)
            
            # Get actual channel ID for posting
            channel_info = await self._get_channel_info(channel_username)
            if not channel_info:
                raise Exception(f"Channel {channel_username} not found or not accessible")
            
            # Publish to channel
            await self.bot.send_message(
                chat_id=channel_info['telegram_channel_id'],
                text=formatted_content,
                parse_mode='HTML'
            )
            
            # Mark as published
            await self._mark_post_published(post_id)
            
            # Update campaign progress
            await self._update_campaign_progress(campaign_id)
            
            logger.info(f"✅ Published post {post_id} to {channel_username} for campaign {campaign_id}")
            
        except TelegramAPIError as e:
            if "chat not found" in str(e).lower():
                logger.error(f"❌ Channel {post['channel_id']} not accessible - marking as failed")
                await self._mark_post_failed(post['id'], f"Channel not accessible: {e}")
            else:
                logger.error(f"❌ Telegram API error publishing post {post['id']}: {e}")
                await self._mark_post_failed(post['id'], f"Telegram error: {e}")
        except Exception as e:
            logger.error(f"❌ Error publishing post {post['id']}: {e}")
            await self._mark_post_failed(post['id'], str(e))
    
    def _format_post_content(self, ad_content: str, campaign_id: str) -> str:
        """Format content for posting to channels"""
        return f"""📢 <b>Sponsored Advertisement</b>

{ad_content}

<i>📱 Advertise with @I3lani_bot</i>
<i>Campaign: {campaign_id}</i>"""
    
    async def _get_channel_info(self, channel_username: str) -> Optional[Dict]:
        """Get channel information from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Remove @ if present
            username = channel_username.replace('@', '')
            
            # Try different column names that might exist in the channels table
            cursor.execute("""
                SELECT * FROM channels 
                WHERE (name LIKE ? OR telegram_channel_id LIKE ?) AND is_active = 1
                LIMIT 1
            """, (f'%{username}%', f'%{username}%'))
            
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"❌ Error getting channel info for {channel_username}: {e}")
            return None
    
    async def _mark_post_published(self, post_id: int):
        """Mark a post as successfully published"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE campaign_posts 
                SET status = 'published', published_at = ?
                WHERE id = ?
            """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), post_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error marking post {post_id} as published: {e}")
    
    async def _mark_post_failed(self, post_id: int, error_message: str):
        """Mark a post as failed with error message"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE campaign_posts 
                SET status = 'failed', error_message = ?, published_at = ?
                WHERE id = ?
            """, (error_message, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), post_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error marking post {post_id} as failed: {e}")
    
    async def _update_campaign_progress(self, campaign_id: str):
        """Update campaign progress statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count published posts for this campaign
            cursor.execute("""
                SELECT COUNT(*) FROM campaign_posts 
                WHERE campaign_id = ? AND status = 'published'
            """, (campaign_id,))
            
            published_count = cursor.fetchone()[0]
            
            # Update campaign
            cursor.execute("""
                UPDATE campaigns 
                SET posts_published = ?, updated_at = ?
                WHERE campaign_id = ?
            """, (published_count, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), campaign_id))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Updated campaign {campaign_id} progress: {published_count} posts published")
            
        except Exception as e:
            logger.error(f"❌ Error updating campaign progress for {campaign_id}: {e}")
    
    async def execute_immediate_post(self, campaign_id: str):
        """Execute the next scheduled post immediately for testing"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get the next scheduled post
            cursor.execute("""
                SELECT cp.*, c.ad_content, c.user_id, c.campaign_name
                FROM campaign_posts cp
                JOIN campaigns c ON cp.campaign_id = c.campaign_id
                WHERE cp.campaign_id = ? AND cp.status = 'scheduled'
                ORDER BY cp.scheduled_time ASC
                LIMIT 1
            """, (campaign_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                logger.warning(f"No scheduled posts found for campaign {campaign_id}")
                return False
            
            post = dict(row)
            await self._publish_single_post(post)
            logger.info(f"✅ Immediately executed post for campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error executing immediate post for {campaign_id}: {e}")
            return False

# Global publisher instance
campaign_publisher = None

async def init_campaign_publisher(bot: Bot):
    """Initialize the campaign publisher"""
    global campaign_publisher
    
    try:
        campaign_publisher = CampaignPublisher(bot)
        await campaign_publisher.start()
        logger.info("✅ Campaign publisher initialized successfully")
        return campaign_publisher
    except Exception as e:
        logger.error(f"❌ Error initializing campaign publisher: {e}")
        return None

async def get_campaign_publisher() -> Optional[CampaignPublisher]:
    """Get the global campaign publisher instance"""
    return campaign_publisher