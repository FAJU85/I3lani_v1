"""
Enhanced Channel Detection System for I3lani Bot
Comprehensive auto-detection of new channels with robust error handling
"""

import logging
from typing import Optional, Dict, List
from aiogram.types import ChatMemberUpdated, ChatMember
from aiogram import Router
from database import db

logger = logging.getLogger(__name__)

class EnhancedChannelDetector:
    """Enhanced channel detection with comprehensive coverage"""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.detection_stats = {
            'total_detected': 0,
            'successfully_added': 0,
            'failed_additions': 0,
            'duplicate_detections': 0
        }
    
    def set_bot(self, bot):
        """Set bot instance after initialization"""
        self.bot = bot
    
    async def handle_chat_member_update(self, update: ChatMemberUpdated) -> bool:
        """
        Handle my_chat_member updates with comprehensive detection
        """
        try:
            # Get chat and member info
            chat = update.chat
            new_member = update.new_chat_member
            old_member = update.old_chat_member
            
            # Log the update for debugging
            logger.info(f"🔍 Chat member update received:")
            logger.info(f"   Chat: {chat.title} ({chat.id})")
            logger.info(f"   Type: {chat.type}")
            logger.info(f"   Old status: {old_member.status if old_member else 'None'}")
            logger.info(f"   New status: {new_member.status if new_member else 'None'}")
            
            # Check if this is about our bot
            if not self.bot or new_member.user.id != self.bot.id:
                logger.debug("Update not about our bot, ignoring")
                return False
            
            # Check if bot became admin
            if (new_member.status == 'administrator' and 
                old_member.status != 'administrator'):
                
                logger.info(f"🚀 Bot became admin in {chat.title}")
                
                # Check if it's a channel or supergroup
                if chat.type in ['channel', 'supergroup']:
                    return await self._process_new_channel(chat, new_member)
                else:
                    logger.info(f"Chat {chat.title} is not a channel/supergroup (type: {chat.type})")
                    return False
            
            # Check if bot was removed from admin
            elif (old_member.status == 'administrator' and 
                  new_member.status != 'administrator'):
                
                logger.info(f"🔄 Bot removed from admin in {chat.title}")
                await self._handle_channel_removal(chat.id)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error handling chat member update: {e}")
            return False
    
    async def _process_new_channel(self, chat, member: ChatMember) -> bool:
        """Process newly detected channel"""
        try:
            # Check if bot has posting permissions
            can_post = getattr(member, 'can_post_messages', False)
            
            if not can_post:
                logger.warning(f"⚠️ Bot is admin in {chat.title} but cannot post messages")
                await self._notify_admin_insufficient_permissions(chat)
                return False
            
            # Check if channel already exists
            existing_channels = await db.get_channels(active_only=False)
            channel_exists = any(
                str(chat.id) == str(ch.get('telegram_channel_id', '')) or
                str(chat.id) == str(ch.get('channel_id', '')) or
                (chat.username and f"@{chat.username}" == str(ch.get('telegram_channel_id', '')))
                for ch in existing_channels
            )
            
            if channel_exists:
                logger.info(f"ℹ️ Channel {chat.title} already exists in database")
                self.detection_stats['duplicate_detections'] += 1
                return False
            
            # Get channel statistics
            try:
                member_count = await self.bot.get_chat_member_count(chat.id)
                logger.info(f"📊 Channel {chat.title} has {member_count} members")
            except Exception as e:
                logger.warning(f"⚠️ Could not get member count for {chat.title}: {e}")
                member_count = 0
            
            # Determine channel category
            category = self._determine_channel_category(chat.title, chat.description)
            
            # Add channel to database
            await db.add_channel_automatically(
                channel_id=str(chat.id),
                channel_name=chat.title,
                telegram_channel_id=f"@{chat.username}" if chat.username else str(chat.id),
                subscribers=member_count,
                active_subscribers=int(member_count * 0.45),
                total_posts=0,
                category=category,
                description=chat.description or f"Auto-detected channel: {chat.title}",
                base_price_usd=2.0
            )
            
            self.detection_stats['successfully_added'] += 1
            self.detection_stats['total_detected'] += 1
            
            logger.info(f"✅ Successfully added channel {chat.title} to database")
            
            # Send welcome message to channel
            await self._send_welcome_message(chat, member_count)
            
            # Notify admins
            await self._notify_admin_new_channel(chat, member_count, category)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing new channel {chat.title}: {e}")
            self.detection_stats['failed_additions'] += 1
            return False
    
    def _determine_channel_category(self, title: str, description: str) -> str:
        """Determine channel category based on title and description"""
        title_lower = title.lower() if title else ""
        desc_lower = description.lower() if description else ""
        
        # Shopping/Business categories
        if any(word in title_lower for word in ['shop', 'store', 'market', 'buy', 'sell', 'business']):
            return 'shopping'
        if any(word in desc_lower for word in ['shop', 'store', 'market', 'buy', 'sell', 'business']):
            return 'shopping'
        
        # Technology categories
        if any(word in title_lower for word in ['tech', 'code', 'programming', 'developer', 'it']):
            return 'technology'
        
        # News categories
        if any(word in title_lower for word in ['news', 'breaking', 'update', 'media']):
            return 'news'
        
        # Entertainment categories
        if any(word in title_lower for word in ['fun', 'meme', 'entertainment', 'game', 'movie']):
            return 'entertainment'
        
        # Education categories
        if any(word in title_lower for word in ['education', 'learn', 'course', 'study', 'school']):
            return 'education'
        
        # Default category
        return 'general'
    
    async def _send_welcome_message(self, chat, member_count: int) -> bool:
        """Send welcome message to newly detected channel"""
        try:
            welcome_message = f"""
🎉 **I3lani Bot is now active in this channel!**

This channel has been automatically detected and added to our advertising network.

📊 **Channel Information:**
• **Name:** {chat.title}
• **Subscribers:** {member_count:,}
• **Category:** {self._determine_channel_category(chat.title, chat.description)}
• **Base Ad Price:** $2.00

🚀 **What's Next:**
• Users can now select this channel for advertising campaigns
• Ads will be published automatically based on user selections
• Channel stats will be updated regularly

📞 **Support:** Contact @I3lani_bot for any questions
            """.strip()
            
            await self.bot.send_message(chat.id, welcome_message, parse_mode='Markdown')
            logger.info(f"✅ Welcome message sent to {chat.title}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Could not send welcome message to {chat.title}: {e}")
            return False
    
    async def _notify_admin_new_channel(self, chat, member_count: int, category: str) -> bool:
        """Notify admins about new channel detection"""
        try:
            # Get admin IDs from config
            admin_ids = [566158428, 7043475]  # Add your admin IDs here
            
            admin_message = f"""
🔔 **New Channel Detected!**

A new channel has been automatically detected and added to the advertising network.

📊 **Channel Details:**
• **Name:** {chat.title}
• **Username:** @{chat.username if chat.username else 'N/A'}
• **ID:** {chat.id}
• **Subscribers:** {member_count:,}
• **Category:** {category}
• **Status:** ✅ Active and ready for ads

🎯 **Auto-Detection Summary:**
• Total Detected: {self.detection_stats['total_detected']}
• Successfully Added: {self.detection_stats['successfully_added']}
• Failed Additions: {self.detection_stats['failed_additions']}
• Duplicate Detections: {self.detection_stats['duplicate_detections']}

The channel is now available for advertising campaigns.
            """.strip()
            
            for admin_id in admin_ids:
                try:
                    await self.bot.send_message(admin_id, admin_message, parse_mode='Markdown')
                    logger.info(f"✅ Admin notification sent to {admin_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not notify admin {admin_id}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error notifying admins: {e}")
            return False
    
    async def _notify_admin_insufficient_permissions(self, chat) -> bool:
        """Notify admins about insufficient permissions"""
        try:
            admin_ids = [566158428, 7043475]
            
            admin_message = f"""
⚠️ **Insufficient Permissions Detected**

Bot was added as admin to a channel but cannot post messages.

📊 **Channel Details:**
• **Name:** {chat.title}
• **Username:** @{chat.username if chat.username else 'N/A'}
• **ID:** {chat.id}

🔧 **Action Required:**
Please ensure the bot has "Post Messages" permission in this channel to enable automatic advertising.
            """.strip()
            
            for admin_id in admin_ids:
                try:
                    await self.bot.send_message(admin_id, admin_message, parse_mode='Markdown')
                except Exception as e:
                    logger.warning(f"⚠️ Could not notify admin {admin_id}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error notifying admins about permissions: {e}")
            return False
    
    async def _handle_channel_removal(self, chat_id: int) -> bool:
        """Handle channel removal from admin"""
        try:
            # Mark channel as inactive instead of deleting
            channels = await db.get_channels(active_only=False)
            
            for channel in channels:
                if str(chat_id) == str(channel.get('telegram_channel_id', '')) or \
                   str(chat_id) == str(channel.get('channel_id', '')):
                    
                    # Mark as inactive
                    await db.execute(
                        "UPDATE channels SET is_active = 0, last_updated = CURRENT_TIMESTAMP WHERE channel_id = ?",
                        (channel['channel_id'],)
                    )
                    
                    logger.info(f"✅ Marked channel {channel.get('name', 'Unknown')} as inactive")
                    
                    # Notify admins
                    await self._notify_admin_channel_removed(channel)
                    return True
            
            logger.warning(f"⚠️ Could not find channel {chat_id} to deactivate")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error handling channel removal: {e}")
            return False
    
    async def _notify_admin_channel_removed(self, channel: Dict) -> bool:
        """Notify admins about channel removal"""
        try:
            admin_ids = [566158428, 7043475]
            
            admin_message = f"""
🔄 **Channel Removed**

Bot was removed from admin of a channel. Channel has been marked as inactive.

📊 **Channel Details:**
• **Name:** {channel.get('name', 'Unknown')}
• **Username:** {channel.get('telegram_channel_id', 'Unknown')}
• **Status:** ❌ Inactive

The channel is no longer available for advertising campaigns.
            """.strip()
            
            for admin_id in admin_ids:
                try:
                    await self.bot.send_message(admin_id, admin_message, parse_mode='Markdown')
                except Exception as e:
                    logger.warning(f"⚠️ Could not notify admin {admin_id}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error notifying admins about removal: {e}")
            return False
    
    async def scan_existing_channels(self) -> List[Dict]:
        """Scan for existing channels where bot is admin but not in database"""
        try:
            logger.info("🔍 Scanning for existing channels where bot is admin...")
            
            detected_channels = []
            
            # This method has limitations due to Telegram API restrictions
            # We can only check channels we already know about
            # The main detection happens through my_chat_member updates
            
            logger.info("ℹ️ Existing channel scan completed")
            logger.info("💡 New channels will be detected automatically when bot is added as admin")
            
            return detected_channels
            
        except Exception as e:
            logger.error(f"❌ Error scanning existing channels: {e}")
            return []
    
    def get_detection_stats(self) -> Dict:
        """Get detection statistics"""
        return self.detection_stats.copy()

# Global instance
enhanced_detector = EnhancedChannelDetector()

# Router for handling updates
detection_router = Router()

@detection_router.my_chat_member()
async def handle_my_chat_member_update(update: ChatMemberUpdated):
    """Handle my_chat_member updates"""
    try:
        await enhanced_detector.handle_chat_member_update(update)
    except Exception as e:
        logger.error(f"❌ Error in my_chat_member handler: {e}")

def get_enhanced_detector() -> EnhancedChannelDetector:
    """Get the enhanced detector instance"""
    return enhanced_detector

def get_detection_router() -> Router:
    """Get the detection router"""
    return detection_router