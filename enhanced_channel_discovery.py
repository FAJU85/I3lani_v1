#!/usr/bin/env python3
"""
Enhanced Channel Discovery System
Comprehensive method to find ALL channels where bot is administrator
"""
import asyncio
import logging
from typing import List, Dict
from aiogram import Bot
from aiogram.types import Chat
from config import BOT_TOKEN
from database import Database
from channel_manager import ChannelManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedChannelDiscovery:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db
        self.channel_manager = ChannelManager(bot, db)
        self.discovered_channels = []
        
    async def discover_all_channels(self) -> List[Dict]:
        """Comprehensive channel discovery using multiple methods"""
        logger.info("🔍 Starting comprehensive channel discovery...")
        
        # Method 1: Get updates (recent interactions)
        await self._discover_from_updates()
        
        # Method 2: Check database channels
        await self._verify_database_channels()
        
        # Method 3: Try common pattern-based discovery
        await self._pattern_based_discovery()
        
        # Method 4: Get from bot's chat list (if available)
        await self._discover_from_chat_list()
        
        # Remove duplicates
        unique_channels = self._remove_duplicates()
        
        logger.info(f"✅ Total unique channels discovered: {len(unique_channels)}")
        return unique_channels
    
    async def _discover_from_updates(self):
        """Discover channels from recent bot updates"""
        try:
            logger.info("Method 1: Checking recent updates...")
            updates = await self.bot.get_updates(limit=100, timeout=1)
            
            for update in updates:
                if update.my_chat_member:
                    chat = update.my_chat_member.chat
                    if chat.type == 'channel':
                        await self._check_and_add_channel(chat)
                
                if update.channel_post:
                    chat = update.channel_post.chat
                    await self._check_and_add_channel(chat)
                    
        except Exception as e:
            logger.error(f"Error in update discovery: {e}")
    
    async def _verify_database_channels(self):
        """Verify all channels in database"""
        try:
            logger.info("Method 2: Verifying database channels...")
            channels = await self.db.get_channels(active_only=False)
            
            for channel in channels:
                channel_id = channel.get('telegram_channel_id', '')
                if channel_id:
                    try:
                        # Add @ if missing
                        if not channel_id.startswith('@') and not channel_id.startswith('-'):
                            channel_id = f"@{channel_id}"
                        
                        chat = await self.bot.get_chat(channel_id)
                        await self._check_and_add_channel(chat)
                    except Exception as e:
                        logger.debug(f"Could not verify {channel_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in database verification: {e}")
    
    async def _pattern_based_discovery(self):
        """Try common channel patterns"""
        try:
            logger.info("Method 3: Pattern-based discovery...")
            
            # Common patterns for channels
            patterns = [
                "i3lani", "i3lan", "e3lan", "e3lani",
                "five", "5", "sar", "Five_SAR",
                "smsh", "shop", "smart", "smshco",
                "tech", "news", "business", "ads", "market"
            ]
            
            # Try combinations
            for pattern in patterns:
                test_usernames = [
                    f"@{pattern}",
                    f"@{pattern}_channel",
                    f"@{pattern}_official",
                    f"@{pattern}sa",
                    f"@{pattern}_sa",
                    f"@sa{pattern}"
                ]
                
                for username in test_usernames:
                    try:
                        chat = await self.bot.get_chat(username)
                        await self._check_and_add_channel(chat)
                    except Exception:
                        # Expected for non-existent channels
                        pass
                        
        except Exception as e:
            logger.error(f"Error in pattern discovery: {e}")
    
    async def _discover_from_chat_list(self):
        """Try to get bot's chat list"""
        try:
            logger.info("Method 4: Checking bot's chat list...")
            
            # Get bot info
            bot_info = await self.bot.get_me()
            
            # Try to get chats where bot is member
            # Note: This is limited by Telegram API
            try:
                # Some bots can see their admin chats
                updates = await self.bot.get_updates(
                    allowed_updates=["my_chat_member", "channel_post"],
                    limit=100
                )
                
                for update in updates:
                    if hasattr(update, 'my_chat_member'):
                        chat = update.my_chat_member.chat
                        if chat.type == 'channel':
                            await self._check_and_add_channel(chat)
                            
            except Exception as e:
                logger.debug(f"Could not get full chat list: {e}")
                
        except Exception as e:
            logger.error(f"Error in chat list discovery: {e}")
    
    async def _check_and_add_channel(self, chat: Chat):
        """Check if bot is admin and add to discovered list"""
        try:
            # Get bot member info
            bot_member = await self.bot.get_chat_member(chat.id, self.bot.id)
            
            if bot_member.status == 'administrator':
                # Get channel details
                member_count = await self.bot.get_chat_member_count(chat.id)
                
                channel_info = {
                    'id': chat.id,
                    'title': chat.title,
                    'username': chat.username,
                    'type': chat.type,
                    'member_count': member_count,
                    'can_post': bot_member.can_post_messages,
                    'description': chat.description or ''
                }
                
                self.discovered_channels.append(channel_info)
                logger.info(f"✅ Found: {chat.title} (@{chat.username}) - {member_count} members")
                
                # Add to database if not exists
                if bot_member.can_post_messages:
                    await self.channel_manager.discover_channel_by_username(
                        f"@{chat.username}" if chat.username else str(chat.id)
                    )
                    
        except Exception as e:
            logger.debug(f"Not admin in {chat.title}: {e}")
    
    def _remove_duplicates(self) -> List[Dict]:
        """Remove duplicate channels"""
        seen = set()
        unique = []
        
        for channel in self.discovered_channels:
            channel_id = channel['id']
            if channel_id not in seen:
                seen.add(channel_id)
                unique.append(channel)
                
        return unique

async def main():
    """Run comprehensive channel discovery"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    
    try:
        discovery = EnhancedChannelDiscovery(bot, db)
        channels = await discovery.discover_all_channels()
        
        logger.info("\n" + "="*50)
        logger.info("DISCOVERED CHANNELS SUMMARY")
        logger.info("="*50)
        
        for i, channel in enumerate(channels, 1):
            logger.info(f"\n{i}. {channel['title']}")
            logger.info(f"   Username: @{channel['username'] or 'N/A'}")
            logger.info(f"   Members: {channel['member_count']:,}")
            logger.info(f"   Can Post: {'✅' if channel['can_post'] else '❌'}")
            
        logger.info(f"\n{'='*50}")
        logger.info(f"Total channels where bot is admin: {len(channels)}")
        logger.info("="*50)
        
        # Show channels in database
        db_channels = await db.get_channels(active_only=True)
        logger.info(f"\nActive channels in database: {len(db_channels)}")
        for ch in db_channels:
            logger.info(f"- {ch['name']} (@{ch['telegram_channel_id']})")
            
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())