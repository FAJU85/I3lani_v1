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
                    
                    # Skip if we already processed this campaign
                    if campaign_id in campaigns_processed:
                        logger.info(f"⏭️ Skipping duplicate post for campaign {campaign_id}")
                        continue
                    
                    await self._publish_campaign_post(post)
                    campaigns_processed.add(campaign_id)
                    
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
            
            # Get verified content from post identity system
            post_metadata = await get_post_metadata(post_identity_id)
            
            if not post_metadata:
                logger.error(f"❌ No metadata found for post identity {post_identity_id}")
                return False
            
            # Use content from post identity (guarantees original content)
            content_to_publish = post_metadata.content_text
            media_url = post_metadata.content_image or post_metadata.content_video
            content_type = post_metadata.content_type
            
            logger.info(f"📤 Publishing {post_identity_id} to {channel_id}")
            logger.info(f"   Content: {content_to_publish[:50]}...")
            logger.info(f"   Type: {content_type}")
            
            # Publish based on content type
            message = None
            
            if content_type == 'photo' and media_url:
                message = await self.bot.send_photo(
                    chat_id=channel_id,
                    photo=media_url,
                    caption=content_to_publish
                )
            elif content_type == 'video' and media_url:
                message = await self.bot.send_video(
                    chat_id=channel_id,
                    video=media_url,
                    caption=content_to_publish
                )
            else:
                # Text only
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
                return True
            else:
                logger.error(f"❌ Failed to publish {post_identity_id} to {channel_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error publishing post with identity: {e}")
            await self._mark_post_failed(post_data['id'], str(e))
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
            
            # Prepare content data with exact user submission
            content_data = {
                'content': post_data['ad_content'],
                'content_type': post_data.get('content_type', 'text'),
                'media_url': post_data.get('media_url'),
                'ad_content': post_data['ad_content']
            }
            
            # Check if post identity already exists for this campaign (should be only one)
            from post_identity_system import post_identity_system
            existing_post = await post_identity_system.get_post_for_campaign(campaign_id)
            
            if existing_post:
                logger.info(f"✅ Using existing post identity for campaign {campaign_id}: {existing_post.post_id}")
                return existing_post.post_id
            
            # Create new post identity
            post_identity_id = await create_post_identity(
                campaign_id, user_id, advertiser_username,
                content_data, campaign_details
            )
            
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