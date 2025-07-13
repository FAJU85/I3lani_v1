#!/usr/bin/env python3
"""
Comprehensive Publishing Fix System
Fixes all publishing-related issues
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ComprehensivePublishingFix:
    """Comprehensive publishing fix system"""
    
    def __init__(self, bot=None, db=None):
        self.bot = bot
        self.db = db
        self.publishing_queue = []
        self.fix_status = {}
    
    async def run_comprehensive_fix(self):
        """Run comprehensive publishing fixes"""
        try:
            logger.info("Starting comprehensive publishing fix...")
            
            # Fix 1: Reschedule overdue posts
            await self._fix_overdue_posts()
            
            # Fix 2: Repair broken campaign links
            await self._fix_broken_campaigns()
            
            # Fix 3: Update channel integration
            await self._fix_channel_integration()
            
            # Fix 4: Validate content integrity
            await self._validate_content_integrity()
            
            logger.info("Comprehensive publishing fix completed")
            return True
            
        except Exception as e:
            logger.error(f"Comprehensive publishing fix error: {e}")
            return False
    
    async def _fix_overdue_posts(self):
        """Fix overdue posts by rescheduling them"""
        try:
            if not self.db:
                return
            
            # Get overdue posts
            connection = await self.db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute("""
                SELECT id, campaign_id, scheduled_time, content, content_type
                FROM campaign_posts 
                WHERE status = 'scheduled' AND scheduled_time < ?
                ORDER BY scheduled_time ASC
                LIMIT 100
            """, (datetime.now(),))
            
            overdue_posts = await cursor.fetchall()
            
            if overdue_posts:
                logger.info(f"Found {len(overdue_posts)} overdue posts")
                
                # Reschedule overdue posts
                for post in overdue_posts:
                    new_time = datetime.now() + timedelta(minutes=1)
                    await cursor.execute("""
                        UPDATE campaign_posts 
                        SET scheduled_time = ?, status = 'scheduled'
                        WHERE id = ?
                    """, (new_time, post[0]))
                
                await connection.commit()
                logger.info(f"Rescheduled {len(overdue_posts)} overdue posts")
            
        except Exception as e:
            logger.error(f"Error fixing overdue posts: {e}")
    
    async def _fix_broken_campaigns(self):
        """Fix broken campaign links"""
        try:
            if not self.db:
                return
            
            # Check for campaigns without posts
            connection = await self.db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute("""
                SELECT c.id, c.user_id, c.content, c.content_type, c.channels
                FROM campaigns c
                LEFT JOIN campaign_posts cp ON c.id = cp.campaign_id
                WHERE cp.id IS NULL AND c.status = 'active'
            """)
            
            broken_campaigns = await cursor.fetchall()
            
            if broken_campaigns:
                logger.info(f"Found {len(broken_campaigns)} broken campaigns")
                
                # Create missing posts for broken campaigns
                for campaign in broken_campaigns:
                    campaign_id, user_id, content, content_type, channels = campaign
                    
                    # Create posts for each channel
                    if channels:
                        for channel in channels.split(','):
                            await cursor.execute("""
                                INSERT INTO campaign_posts 
                                (campaign_id, channel_id, content, content_type, scheduled_time, status)
                                VALUES (?, ?, ?, ?, ?, 'scheduled')
                            """, (
                                campaign_id,
                                channel.strip(),
                                content,
                                content_type,
                                datetime.now() + timedelta(minutes=2),
                            ))
                
                await connection.commit()
                logger.info(f"Fixed {len(broken_campaigns)} broken campaigns")
            
        except Exception as e:
            logger.error(f"Error fixing broken campaigns: {e}")
    
    async def _fix_channel_integration(self):
        """Fix channel integration issues"""
        try:
            # Verify channel connections
            if self.bot:
                from channel_manager import init_channel_manager
                channel_manager = init_channel_manager(self.bot, self.db)
                
                # Sync channels
                await channel_manager.sync_existing_channels()
                logger.info("Channel integration fixed")
            
        except Exception as e:
            logger.error(f"Error fixing channel integration: {e}")
    
    async def _validate_content_integrity(self):
        """Validate content integrity"""
        try:
            if not self.db:
                return
            
            connection = await self.db.get_connection()
            cursor = await connection.cursor()
            
            # Check for posts without content
            await cursor.execute("""
                SELECT id, campaign_id FROM campaign_posts 
                WHERE content IS NULL OR content = ''
            """)
            
            empty_posts = await cursor.fetchall()
            
            if empty_posts:
                logger.warning(f"Found {len(empty_posts)} posts with empty content")
                
                # Mark them as failed
                for post in empty_posts:
                    await cursor.execute("""
                        UPDATE campaign_posts 
                        SET status = 'failed', error_message = 'Empty content'
                        WHERE id = ?
                    """, (post[0],))
                
                await connection.commit()
            
        except Exception as e:
            logger.error(f"Error validating content integrity: {e}")
    
    async def handle_new_channel_addition(self, chat_member_updated):
        """Handle new channel addition"""
        try:
            # Check if bot was added as admin
            if (chat_member_updated.new_chat_member.status == 'administrator' and
                chat_member_updated.old_chat_member.status != 'administrator'):
                
                chat = chat_member_updated.chat
                
                # Add channel to database
                if self.db:
                    await self.db.add_channel(
                        channel_id=chat.id,
                        username=chat.username or "",
                        title=chat.title or "",
                        category="general",
                        price_per_day=2.0,
                        subscriber_count=0
                    )
                
                logger.info(f"Added new channel: {chat.title} ({chat.username})")
            
        except Exception as e:
            logger.error(f"Error handling new channel addition: {e}")
    
    def get_fix_status(self) -> Dict:
        """Get fix status"""
        return self.fix_status

# Global instance
comprehensive_fix = None

async def run_comprehensive_fix(bot=None, db=None):
    """Run comprehensive publishing fix"""
    global comprehensive_fix
    comprehensive_fix = ComprehensivePublishingFix(bot, db)
    await comprehensive_fix.run_comprehensive_fix()
    return comprehensive_fix

def get_comprehensive_fix():
    """Get comprehensive fix instance"""
    return comprehensive_fix