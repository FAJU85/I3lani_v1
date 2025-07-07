"""
Channel Management System for I3lani Bot
Automatically manages channels when bot becomes admin or loses admin privileges
"""

import logging
from typing import Optional, Dict, List
from aiogram import Bot
from aiogram.types import ChatMemberUpdated, Chat, ChatMember
from database import Database, db

logger = logging.getLogger(__name__)

class ChannelManager:
    def __init__(self, bot: Bot, database: Database):
        self.bot = bot
        self.db = database
    
    async def handle_bot_status_change(self, chat_member_updated: ChatMemberUpdated):
        """Handle when bot's status changes in a channel"""
        try:
            chat = chat_member_updated.chat
            old_status = chat_member_updated.old_chat_member.status
            new_status = chat_member_updated.new_chat_member.status
            
            # Only handle channels, not groups or private chats
            if chat.type not in ['channel', 'supergroup']:
                return
            
            # Check if bot became admin
            if old_status in ['left', 'member', 'restricted'] and new_status == 'administrator':
                await self.add_channel_as_admin(chat, chat_member_updated.new_chat_member)
            
            # Check if bot lost admin privileges
            elif old_status == 'administrator' and new_status in ['left', 'member', 'restricted']:
                await self.remove_channel_admin(chat)
                
        except Exception as e:
            logger.error(f"Error handling bot status change: {e}")
    
    async def add_channel_as_admin(self, chat: Chat, chat_member: ChatMember):
        """Add channel when bot becomes admin"""
        try:
            # Check if bot can post messages
            if not chat_member.can_post_messages:
                logger.warning(f"Bot added as admin to {chat.title} but cannot post messages")
                return
            
            # Get channel information
            channel_id = str(chat.id)
            channel_name = chat.title or f"Channel {channel_id}"
            telegram_channel_id = chat.username if chat.username else channel_id
            
            # Try to get subscriber count
            subscribers = 0
            try:
                chat_info = await self.bot.get_chat(chat.id)
                subscribers = chat_info.members_count or 0
            except:
                subscribers = 0
            
            # Add channel to database
            await self.db.add_channel_automatically(
                channel_id=channel_id,
                channel_name=channel_name,
                telegram_channel_id=telegram_channel_id,
                subscribers=subscribers,
                base_price_usd=5.0  # Default price
            )
            
            logger.info(f"✅ Channel '{channel_name}' added automatically (ID: {channel_id})")
            
            # Send welcome message to channel
            welcome_message = f"""
🎉 **I3lani Bot is now active in this channel!**

This channel is now available for advertisements through @I3lani_bot.

📊 **Channel Stats:**
• Name: {channel_name}
• Subscribers: {subscribers:,}
• Base Price: $5.00 per ad

Users can now select this channel when creating ads through the bot.
            """.strip()
            
            try:
                await self.bot.send_message(chat.id, welcome_message, parse_mode='Markdown')
            except:
                pass  # Ignore if can't send message
                
        except Exception as e:
            logger.error(f"Error adding channel as admin: {e}")
    
    async def remove_channel_admin(self, chat: Chat):
        """Remove channel when bot loses admin privileges"""
        try:
            telegram_channel_id = chat.username if chat.username else str(chat.id)
            
            # Deactivate channel in database
            await self.db.remove_channel_automatically(telegram_channel_id)
            
            logger.info(f"❌ Channel '{chat.title}' removed from active channels")
            
        except Exception as e:
            logger.error(f"Error removing channel admin: {e}")
    
    async def sync_existing_channels(self):
        """Sync existing channels where bot is admin"""
        try:
            # This method can be called on bot startup to sync existing channels
            # For now, we'll rely on the automatic detection when status changes
            pass
            
        except Exception as e:
            logger.error(f"Error syncing existing channels: {e}")
    
    async def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Get detailed channel information"""
        try:
            chat = await self.bot.get_chat(channel_id)
            return {
                'id': str(chat.id),
                'title': chat.title,
                'username': chat.username,
                'type': chat.type,
                'members_count': getattr(chat, 'members_count', 0),
                'description': getattr(chat, 'description', '')
            }
        except Exception as e:
            logger.error(f"Error getting channel info for {channel_id}: {e}")
            return None
    
    async def update_channel_stats(self, channel_id: str):
        """Update channel statistics"""
        try:
            chat = await self.bot.get_chat(channel_id)
            subscribers = getattr(chat, 'members_count', 0)
            
            # Update database
            async with self.db.get_connection() as conn:
                await conn.execute('''
                    UPDATE channels 
                    SET subscribers = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE telegram_channel_id = ? OR channel_id = ?
                ''', (subscribers, channel_id, channel_id))
                await conn.commit()
                
            logger.info(f"Updated stats for channel {channel_id}: {subscribers} subscribers")
            
        except Exception as e:
            logger.error(f"Error updating channel stats: {e}")


# Global channel manager instance
channel_manager = None

def init_channel_manager(bot: Bot, database: Database):
    """Initialize channel manager"""
    global channel_manager
    channel_manager = ChannelManager(bot, database)
    return channel_manager

async def handle_my_chat_member(chat_member_updated: ChatMemberUpdated):
    """Handler for my_chat_member updates"""
    if channel_manager:
        await channel_manager.handle_bot_status_change(chat_member_updated)