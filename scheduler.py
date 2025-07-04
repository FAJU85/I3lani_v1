import asyncio
from datetime import datetime, timedelta
from typing import List
from aiogram import Bot
from aiogram.types import InputMediaPhoto, InputMediaVideo
from config import CHANNEL_ID, PACKAGES
from models import Advertisement, AdStatus, storage
from languages import get_text
import logging

logger = logging.getLogger(__name__)

class ScheduleManager:
    """Manages scheduling and posting of advertisements"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.running = False
    
    async def schedule_first_post(self, ad: Advertisement):
        """Schedule the first post for an advertisement"""
        try:
            # Post immediately
            await self.post_ad_to_channel(ad)
            
            # Update ad status and schedule next repost
            ad.status = AdStatus.ACTIVE
            ad.first_post_at = datetime.now()
            ad.posts_count = 1
            
            # Calculate next repost time
            if ad.posts_count < ad.total_posts:
                ad.next_repost_at = datetime.now() + timedelta(days=ad.repost_frequency_days)
            else:
                ad.status = AdStatus.COMPLETED
                ad.next_repost_at = None
            
            storage.save_ad(ad)
            
            logger.info(f"First post scheduled for ad {ad.id}")
            
        except Exception as e:
            logger.error(f"Failed to schedule first post for ad {ad.id}: {e}")
    
    async def post_ad_to_channel(self, ad: Advertisement):
        """Post advertisement to the channel"""
        try:
            if ad.content.content_type == "text":
                await self.bot.send_message(
                    CHANNEL_ID,
                    ad.content.text,
                    parse_mode="Markdown"
                )
            elif ad.content.content_type == "photo":
                await self.bot.send_photo(
                    CHANNEL_ID,
                    ad.content.photo_file_id,
                    caption=ad.content.caption,
                    parse_mode="Markdown"
                )
            elif ad.content.content_type == "video":
                await self.bot.send_video(
                    CHANNEL_ID,
                    ad.content.video_file_id,
                    caption=ad.content.caption,
                    parse_mode="Markdown"
                )
            
            logger.info(f"Posted ad {ad.id} to channel")
            
        except Exception as e:
            logger.error(f"Failed to post ad {ad.id} to channel: {e}")
            raise
    
    async def process_reposts(self):
        """Process scheduled reposts"""
        try:
            active_ads = storage.get_active_ads()
            current_time = datetime.now()
            
            for ad in active_ads:
                # Check if it's time to repost
                if ad.next_repost_at and current_time >= ad.next_repost_at:
                    try:
                        # Post the ad
                        await self.post_ad_to_channel(ad)
                        
                        # Update post count and first post time
                        ad.posts_count += 1
                        if ad.first_post_at is None:
                            ad.first_post_at = current_time
                            # Send campaign started notification
                            await self.notify_campaign_started(ad)
                        else:
                            # Send ad posted notification  
                            await self.notify_ad_posted(ad)
                        
                        # Calculate next repost or complete
                        if ad.posts_count < ad.total_posts:
                            ad.next_repost_at = current_time + timedelta(days=ad.repost_frequency_days)
                        else:
                            ad.status = AdStatus.COMPLETED
                            ad.next_repost_at = None
                            # Send campaign completed notification
                            await self.notify_campaign_completed(ad)
                        
                        storage.save_ad(ad)
                        logger.info(f"Reposted ad {ad.id} ({ad.posts_count}/{ad.total_posts})")
                        
                    except Exception as e:
                        logger.error(f"Failed to repost ad {ad.id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in process_reposts: {e}")
    
    async def run_scheduler(self):
        """Main scheduler loop"""
        self.running = True
        logger.info("Scheduler started")
        
        while self.running:
            try:
                await self.process_reposts()
                # Check every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Scheduler stopped")
    
    async def get_active_campaigns_info(self) -> str:
        """Get information about active campaigns"""
        active_ads = storage.get_active_ads()
        
        if not active_ads:
            return "📊 **No active campaigns**"
        
        info_text = f"📊 **Active Campaigns: {len(active_ads)}**\n\n"
        
        for ad in active_ads:
            package = PACKAGES[ad.package_id]
            next_post = ad.next_repost_at.strftime('%Y-%m-%d %H:%M') if ad.next_repost_at else "Complete"
            
            info_text += f"🎯 **{package['name']}** - @{ad.username or 'Unknown'}\n"
            info_text += f"   📊 Posts: {ad.posts_count}/{ad.total_posts}\n"
            info_text += f"   ⏰ Next: {next_post}\n\n"
        
        return info_text
    
    async def notify_campaign_started(self, ad: Advertisement):
        """Notify user that campaign has started"""
        try:
            package = PACKAGES[ad.package_id]
            end_date = (ad.first_post_at + timedelta(days=package['duration_days'])).strftime('%Y-%m-%d')
            
            message = get_text(ad.user_id, "campaign_started",
                package_name=package['name'],
                duration_days=package['duration_days'],
                total_posts=ad.total_posts,
                frequency_days=ad.repost_frequency_days,
                end_date=end_date
            )
            
            await self.bot.send_message(ad.user_id, message, parse_mode="Markdown")
            logger.info(f"Sent campaign started notification to user {ad.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send campaign started notification: {e}")
    
    async def notify_ad_posted(self, ad: Advertisement):
        """Notify user that ad was posted"""
        try:
            remaining_posts = ad.total_posts - ad.posts_count
            if remaining_posts > 0:
                next_post_date = (datetime.now() + timedelta(days=ad.repost_frequency_days)).strftime('%Y-%m-%d')
                remaining_text = f"⏰ **{remaining_posts} posts remaining**"
            else:
                next_post_date = "Campaign completed"
                remaining_text = "🎯 **Campaign completed!**"
            
            message = get_text(ad.user_id, "ad_posted_notification",
                post_number=ad.posts_count,
                total_posts=ad.total_posts,
                next_post_date=next_post_date,
                remaining_posts_text=remaining_text
            )
            
            await self.bot.send_message(ad.user_id, message, parse_mode="Markdown")
            logger.info(f"Sent ad posted notification to user {ad.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send ad posted notification: {e}")
    
    async def notify_campaign_completed(self, ad: Advertisement):
        """Notify user that campaign is completed"""
        try:
            package = PACKAGES[ad.package_id]
            channel_name = CHANNEL_ID.replace("@", "") if CHANNEL_ID.startswith("@") else CHANNEL_ID
            
            message = get_text(ad.user_id, "campaign_completed",
                package_name=package['name'],
                posts_count=ad.posts_count,
                duration_days=package['duration_days'],
                channel_name=channel_name
            )
            
            await self.bot.send_message(ad.user_id, message, parse_mode="Markdown")
            logger.info(f"Sent campaign completed notification to user {ad.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send campaign completed notification: {e}")
