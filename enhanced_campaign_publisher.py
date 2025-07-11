#!/usr/bin/env python3
"""
Enhanced Campaign Publisher with Post Identity System
Ensures published content exactly matches user submissions
"""

import asyncio
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

from post_identity_system import (
    post_identity_system, create_post_identity, get_post_metadata, 
    log_publication, verify_campaign_integrity
)
from handlers_tracking_integration import track_publishing_started, track_publishing_complete

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCampaignPublisher:
    """Enhanced campaign publisher with content integrity verification"""
    
    def __init__(self, bot_instance, db_path: str = "bot.db"):
        self.bot = bot_instance
        self.db_path = db_path
        self.running = False
        self.check_interval = 30  # seconds
        
    async def start(self):
        """Start the enhanced campaign publisher"""
        if self.running:
            logger.warning("Enhanced campaign publisher already running")
            return
            
        self.running = True
        logger.info("🚀 Enhanced Campaign Publisher started with Post Identity System")
        
        # Start background publishing loop
        asyncio.create_task(self._publishing_loop())
        
    async def stop(self):
        """Stop the enhanced campaign publisher"""
        self.running = False
        logger.info("🛑 Enhanced Campaign Publisher stopped")
        
    async def _publishing_loop(self):
        """Main publishing loop with content verification"""
        while self.running:
            try:
                await self._process_due_posts()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error in publishing loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _process_due_posts(self):
        """Process posts that are due for publishing - ONE POST PER CAMPAIGN"""
        try:
            due_posts = await self._get_due_posts()
            
            if due_posts:
                logger.info(f"📋 Processing {len(due_posts)} due posts")
                
                # Group by campaign to ensure one post per campaign
                campaigns_processed = set()
                
                for post in due_posts:
                    campaign_id = post['campaign_id']
                    user_id = post['user_id']
                    
                    # Skip if we already processed this campaign
                    if campaign_id in campaigns_processed:
                        logger.info(f"⏭️ Skipping duplicate post for campaign {campaign_id}")
                        continue
                    
                    # Track publishing started for this campaign
                    if campaign_id not in campaigns_processed:
                        try:
                            await track_publishing_started(user_id, campaign_id)
                        except Exception as e:
                            logger.error(f"Error tracking publishing started: {e}")
                    
                    # Publish the post
                    success = await self._publish_campaign_post(post)
                    campaigns_processed.add(campaign_id)
                    
                    # Check if campaign is complete and trigger final confirmation
                    if success:
                        await self._check_campaign_completion(campaign_id, user_id)
                    
        except Exception as e:
            logger.error(f"❌ Error processing due posts: {e}")
    
    async def _get_due_posts(self) -> List[Dict]:
        """Get posts that are due for publishing"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                SELECT cp.*, c.ad_content, c.user_id, 
                       COALESCE(c.content_type, 'text') as content_type, 
                       c.media_url, c.campaign_metadata
                FROM campaign_posts cp
                JOIN campaigns c ON cp.campaign_id = c.campaign_id
                WHERE cp.status = 'scheduled' 
                AND cp.scheduled_time <= ?
                ORDER BY cp.scheduled_time ASC
                LIMIT 10
            """, (current_time,))
            
            posts = []
            for row in cursor.fetchall():
                posts.append(dict(row))
            
            conn.close()
            return posts
            
        except Exception as e:
            logger.error(f"❌ Error getting due posts: {e}")
            return []
    
    async def _publish_campaign_post(self, post_data: Dict):
        """Publish the single post for a campaign with full identity tracking"""
        try:
            campaign_id = post_data['campaign_id']
            channel_id = post_data['channel_id']
            user_id = post_data['user_id']
            post_id = post_data['id']
            
            # Get or create THE post identity for this campaign (one-to-one)
            post_identity_id = await self._ensure_campaign_post_identity(post_data)
            
            if not post_identity_id:
                logger.error(f"❌ Failed to create post identity for campaign {campaign_id}")
                return False
            
            # FIXED: Get content directly from current campaign (not from post identity system)
            # This ensures we publish the exact content from the current campaign
            content_to_publish = post_data['ad_content']
            media_url = post_data.get('media_url')
            content_type = post_data.get('content_type', 'text')
            
            logger.info(f"🎯 CONTENT VERIFICATION - Using content directly from campaign {campaign_id}")
            logger.info(f"   Campaign content: {content_to_publish[:100]}...")
            logger.info(f"   Media URL: {media_url}")
            logger.info(f"   Content Type: {content_type}")
            
            # Verify we have the correct content
            if not content_to_publish:
                logger.error(f"❌ No content found for campaign {campaign_id}")
                return False
            
            logger.info(f"📤 Publishing {post_identity_id} to {channel_id}")
            logger.info(f"   Content: {content_to_publish[:50]}...")
            logger.info(f"   Type: {content_type}")
            
            # Publish based on content type with enhanced media handling
            message = None
            
            logger.info(f"🎬 Publishing content type '{content_type}' with media: {bool(media_url)}")
            
            if content_type in ['photo', 'image', 'text+photo', 'text+image'] and media_url:
                logger.info(f"📸 Publishing photo to {channel_id}")
                message = await self.bot.send_photo(
                    chat_id=channel_id,
                    photo=media_url,
                    caption=content_to_publish
                )
            elif content_type in ['video', 'text+video'] and media_url:
                logger.info(f"🎥 Publishing video to {channel_id}")
                message = await self.bot.send_video(
                    chat_id=channel_id,
                    video=media_url,
                    caption=content_to_publish
                )
            elif content_type in ['image_only', 'photo_only'] and media_url:
                logger.info(f"📸 Publishing image only to {channel_id}")
                message = await self.bot.send_photo(
                    chat_id=channel_id,
                    photo=media_url
                )
            elif content_type in ['video_only'] and media_url:
                logger.info(f"🎥 Publishing video only to {channel_id}")
                message = await self.bot.send_video(
                    chat_id=channel_id,
                    video=media_url
                )
            else:
                # Text only or fallback
                logger.info(f"💬 Publishing text only to {channel_id}")
                message = await self.bot.send_message(
                    chat_id=channel_id,
                    text=content_to_publish
                )
            
            if message:
                # Log the publication with content verification
                channel_name = await self._get_channel_name(channel_id)
                
                await log_publication(
                    post_identity_id,
                    channel_id,
                    channel_name,
                    message.message_id,
                    content_to_publish
                )
                
                # Mark original post as published
                await self._mark_post_published(post_id)
                
                logger.info(f"✅ Successfully published {post_identity_id} to {channel_id}")
                
                # Log per-channel publishing success
                await self._log_channel_publishing_success(
                    campaign_id, channel_id, message.message_id, 
                    content_type, media_url
                )
                
                return True
            else:
                logger.error(f"❌ Failed to publish {post_identity_id} to {channel_id}")
                
                # Log per-channel publishing failure
                await self._log_channel_publishing_failure(
                    campaign_id, channel_id, content_type, "No message returned"
                )
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Error publishing post with identity: {e}")
            await self._mark_post_failed(post_data['id'], str(e))
            
            # Log per-channel publishing failure
            await self._log_channel_publishing_failure(
                post_data['campaign_id'], 
                post_data['channel_id'], 
                post_data.get('content_type', 'unknown'), 
                str(e)
            )
            
            return False
    
    async def _ensure_campaign_post_identity(self, post_data: Dict) -> Optional[str]:
        """Ensure campaign has its single post identity (one-to-one relationship)"""
        try:
            campaign_id = post_data['campaign_id']
            user_id = post_data['user_id']
            
            # Get user information
            advertiser_username = await self._get_user_username(user_id)
            
            # Get campaign details
            campaign_details = await self._get_campaign_details(campaign_id)
            
            # FIXED: Use content directly from current campaign data
            content_data = {
                'content': post_data['ad_content'],
                'content_type': post_data.get('content_type', 'text'),
                'media_url': post_data.get('media_url'),
                'ad_content': post_data['ad_content']
            }
            
            logger.info(f"🎯 CREATING POST IDENTITY with current campaign content:")
            logger.info(f"   Campaign ID: {campaign_id}")
            logger.info(f"   Content: {content_data['content'][:100]}...")
            logger.info(f"   Content Type: {content_data['content_type']}")
            logger.info(f"   Media URL: {content_data['media_url']}")
            
            # Always create a new post identity for this publishing cycle
            # This ensures we don't use old/cached content
            post_identity_id = await create_post_identity(
                campaign_id, user_id, advertiser_username,
                content_data, campaign_details
            )
            
            if post_identity_id:
                logger.info(f"✅ Created new post identity {post_identity_id} for campaign {campaign_id}")
            else:
                logger.error(f"❌ Failed to create post identity for campaign {campaign_id}")
            
            return post_identity_id
            
        except Exception as e:
            logger.error(f"❌ Error ensuring post identity: {e}")
            return None
    
    async def _find_post_identity_by_campaign_and_content(self, campaign_id: str, content: str) -> Optional[str]:
        """Find existing post identity by campaign and content"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT post_id FROM post_identity 
                WHERE campaign_id = ? AND content_text = ?
                LIMIT 1
            """, (campaign_id, content))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Error finding post identity: {e}")
            return None
    
    async def _check_campaign_completion(self, campaign_id: str, user_id: int):
        """Check if campaign is complete and trigger final confirmation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign post statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_posts,
                    COUNT(CASE WHEN status = 'published' THEN 1 END) as published_posts,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_posts,
                    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_posts
                FROM campaign_posts
                WHERE campaign_id = ?
            """, (campaign_id,))
            
            stats = cursor.fetchone()
            
            if stats:
                total_posts, published_posts, failed_posts, scheduled_posts = stats
                
                # Check if all posts are completed (published or failed)
                if scheduled_posts == 0 and total_posts > 0:
                    logger.info(f"✅ Campaign {campaign_id} completed: {published_posts} published, {failed_posts} failed")
                    
                    # Track publishing completion
                    try:
                        await track_publishing_complete(user_id, campaign_id)
                    except Exception as e:
                        logger.error(f"Error tracking publishing complete: {e}")
                    
                    # Update campaign status
                    cursor.execute("""
                        UPDATE campaigns 
                        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                        WHERE campaign_id = ?
                    """, (campaign_id,))
                    conn.commit()
                    
                    logger.info(f"🎉 Campaign {campaign_id} marked as completed and final confirmation sent")
                
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error checking campaign completion: {e}")
    
    async def _get_user_username(self, user_id: int) -> str:
        """Get user username for post identity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] else f"user_{user_id}"
            
        except Exception as e:
            logger.error(f"❌ Error getting username: {e}")
            return f"user_{user_id}"
    
    async def _get_campaign_details(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign details for post identity"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT duration_days, posts_per_day, selected_channels, total_reach
                FROM campaigns WHERE campaign_id = ?
            """, (campaign_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'duration_days': row['duration_days'],
                    'posts_per_day': row['posts_per_day'],
                    'selected_channels': json.loads(row['selected_channels']) if row['selected_channels'] else [],
                    'total_reach': row['total_reach']
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign details: {e}")
            return {}
    
    async def _get_channel_name(self, channel_id: str) -> str:
        """Get channel name for logging"""
        try:
            chat = await self.bot.get_chat(channel_id)
            return chat.title or channel_id
        except:
            return channel_id
    
    async def _mark_post_published(self, post_id: int):
        """Mark post as published in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE campaign_posts 
                SET status = 'published', published_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (post_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error marking post published: {e}")
    
    async def _mark_post_failed(self, post_id: int, error_message: str):
        """Mark post as failed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE campaign_posts 
                SET status = 'failed', error_message = ?
                WHERE id = ?
            """, (error_message, post_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error marking post failed: {e}")
    
    async def _log_channel_publishing_success(self, campaign_id: str, channel_id: str, message_id: int, content_type: str, media_url: str = None):
        """Log successful channel publishing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_publishing_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    message_id INTEGER,
                    content_type TEXT,
                    media_url TEXT,
                    status TEXT DEFAULT 'success',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Log the success
            cursor.execute("""
                INSERT INTO channel_publishing_logs 
                (campaign_id, channel_id, message_id, content_type, media_url, status)
                VALUES (?, ?, ?, ?, ?, 'success')
            """, (campaign_id, channel_id, message_id, content_type, media_url))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Logged successful publishing to {channel_id} for campaign {campaign_id}")
            
        except Exception as e:
            logger.error(f"❌ Error logging channel publishing success: {e}")
    
    async def _log_channel_publishing_failure(self, campaign_id: str, channel_id: str, content_type: str, error_message: str):
        """Log failed channel publishing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS channel_publishing_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    message_id INTEGER,
                    content_type TEXT,
                    media_url TEXT,
                    status TEXT DEFAULT 'success',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Log the failure
            cursor.execute("""
                INSERT INTO channel_publishing_logs 
                (campaign_id, channel_id, content_type, status, error_message)
                VALUES (?, ?, ?, 'failed', ?)
            """, (campaign_id, channel_id, content_type, error_message))
            
            conn.commit()
            conn.close()
            
            logger.info(f"❌ Logged failed publishing to {channel_id} for campaign {campaign_id}: {error_message}")
            
        except Exception as e:
            logger.error(f"❌ Error logging channel publishing failure: {e}")
    
    async def verify_campaign_content_integrity(self, campaign_id: str) -> Dict[str, Any]:
        """Verify content integrity for a campaign"""
        return await verify_campaign_integrity(campaign_id)
    
    async def republish_campaign_with_verified_content(self, campaign_id: str) -> bool:
        """Republish campaign ensuring content integrity"""
        try:
            logger.info(f"🔄 Republishing campaign {campaign_id} with verified content")
            
            # Get all posts for campaign
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Reset failed posts to scheduled for republishing
            cursor.execute("""
                UPDATE campaign_posts 
                SET status = 'scheduled', scheduled_time = CURRENT_TIMESTAMP
                WHERE campaign_id = ? AND status = 'failed'
            """, (campaign_id,))
            
            conn.commit()
            conn.close()
            
            # Process the republishing
            await self._process_due_posts()
            
            logger.info(f"✅ Republishing completed for campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error republishing campaign: {e}")
            return False

# Global enhanced publisher instance
enhanced_publisher = None

async def init_enhanced_campaign_publisher(bot_instance):
    """Initialize enhanced campaign publisher"""
    global enhanced_publisher
    
    try:
        # Initialize Post Identity System first
        from post_identity_system import init_post_identity_system
        await init_post_identity_system()
        
        # Create enhanced publisher
        enhanced_publisher = EnhancedCampaignPublisher(bot_instance)
        
        # Start it
        await enhanced_publisher.start()
        
        logger.info("✅ Enhanced Campaign Publisher initialized with Post Identity System")
        return enhanced_publisher
        
    except Exception as e:
        logger.error(f"❌ Error initializing enhanced publisher: {e}")
        return None

async def get_enhanced_publisher():
    """Get enhanced publisher instance"""
    return enhanced_publisher

if __name__ == "__main__":
    async def test_enhanced_publisher():
        # Test initialization
        print("Testing Enhanced Campaign Publisher...")
        
        # Mock bot instance for testing
        class MockBot:
            async def send_message(self, chat_id, text):
                print(f"Mock: Sending to {chat_id}: {text[:50]}...")
                return type('Message', (), {'message_id': 123})()
        
        publisher = EnhancedCampaignPublisher(MockBot())
        await publisher.start()
        
        print("Enhanced publisher test completed")
        
        await publisher.stop()
    
    asyncio.run(test_enhanced_publisher())