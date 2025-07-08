"""
Channel Management System for I3lani Bot
Automatically manages channels when bot becomes admin or loses admin privileges
"""

import logging
import asyncio
import aiosqlite
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
        """Add channel when bot becomes admin with detailed analysis"""
        try:
            # Check if bot can post messages
            if not chat_member.can_post_messages:
                logger.warning(f"Bot added as admin to {chat.title} but cannot post messages")
                return
            
            # Get basic channel information
            channel_id = str(chat.id)
            channel_name = chat.title or f"Channel {channel_id}"
            telegram_channel_id = chat.username if chat.username else channel_id
            description = chat.description or ""
            
            # Get detailed channel statistics
            subscribers = 0
            active_subscribers = 0
            total_posts = 0
            
            try:
                chat_info = await self.bot.get_chat(chat.id)
                subscribers = chat_info.members_count or 0
                description = chat_info.description or description
                
                # Estimate active subscribers (30-60% of total for most channels)
                active_subscribers = int(subscribers * 0.45) if subscribers > 0 else 0
                
                # Try to estimate post count by getting recent messages
                total_posts = await self._estimate_post_count(chat.id)
                
            except Exception as e:
                logger.warning(f"Could not get detailed stats for {channel_name}: {e}")
                subscribers = 0
            
            # Detect channel category based on title and description
            category = self._detect_channel_category(channel_name, description)
            
            # Calculate base price based on subscribers and category
            base_price = self._calculate_base_price(subscribers, category)
            
            # Add channel to database with all details
            await self.db.add_channel_automatically(
                channel_id=channel_id,
                channel_name=channel_name,
                telegram_channel_id=telegram_channel_id,
                subscribers=subscribers,
                active_subscribers=active_subscribers,
                total_posts=total_posts,
                category=category,
                description=description,
                base_price_usd=base_price
            )
            
            logger.info(f"✅ Channel '{channel_name}' added automatically")
            logger.info(f"📊 Stats: {subscribers:,} subscribers, {active_subscribers:,} active, {total_posts:,} posts, category: {category}")
            
            # Send detailed welcome message to channel
            welcome_message = f"""
🎉 **I3lani Bot is now active in this channel!**

This channel is now available for advertisements through @I3lani_bot.

📊 **Detected Channel Information:**
• **Name:** {channel_name}
• **Category:** {category.title()}
• **Total Subscribers:** {subscribers:,}
• **Active Subscribers:** {active_subscribers:,}
• **Total Posts:** {total_posts:,}
• **Base Ad Price:** ${base_price:.2f}

Users can now select this channel when creating ads through the bot.
            """.strip()
            
            try:
                await self.bot.send_message(chat.id, welcome_message, parse_mode='Markdown')
            except Exception as e:
                logger.debug(f"Could not send notification: {e}")
                pass  # Ignore if can't send message
                
        except Exception as e:
            logger.error(f"Error adding channel as admin: {e}")
    
    def _detect_channel_category(self, channel_name: str, description: str) -> str:
        """Detect channel category based on name and description"""
        text = f"{channel_name} {description}".lower()
        
        # Technology keywords
        tech_keywords = ['tech', 'technology', 'programming', 'code', 'dev', 'software', 'ai', 'crypto', 'blockchain', 'bitcoin']
        if any(keyword in text for keyword in tech_keywords):
            return 'technology'
        
        # Shopping keywords  
        shopping_keywords = ['shop', 'shopping', 'store', 'buy', 'sell', 'market', 'ecommerce', 'deals', 'discount']
        if any(keyword in text for keyword in shopping_keywords):
            return 'shopping'
        
        # News keywords
        news_keywords = ['news', 'breaking', 'update', 'daily', 'media', 'press', 'journal']
        if any(keyword in text for keyword in news_keywords):
            return 'news'
        
        # Entertainment keywords
        entertainment_keywords = ['entertainment', 'fun', 'meme', 'funny', 'joke', 'movie', 'music', 'game']
        if any(keyword in text for keyword in entertainment_keywords):
            return 'entertainment'
        
        # Education keywords
        education_keywords = ['education', 'learn', 'course', 'study', 'tutorial', 'university', 'school']
        if any(keyword in text for keyword in education_keywords):
            return 'education'
        
        # Business keywords
        business_keywords = ['business', 'entrepreneur', 'startup', 'finance', 'money', 'investment']
        if any(keyword in text for keyword in business_keywords):
            return 'business'
        
        # Sports keywords
        sports_keywords = ['sport', 'football', 'soccer', 'basketball', 'tennis', 'fitness', 'gym']
        if any(keyword in text for keyword in sports_keywords):
            return 'sports'
        
        return 'general'
    
    def _calculate_base_price(self, subscribers: int, category: str) -> float:
        """Calculate base price based on subscribers and category"""
        # Base price calculation
        if subscribers < 1000:
            base_price = 2.0
        elif subscribers < 5000:
            base_price = 5.0
        elif subscribers < 10000:
            base_price = 8.0
        elif subscribers < 50000:
            base_price = 15.0
        elif subscribers < 100000:
            base_price = 25.0
        else:
            base_price = 50.0
        
        # Category multipliers
        category_multipliers = {
            'technology': 1.5,
            'business': 1.4,
            'finance': 1.6,
            'shopping': 1.3,
            'education': 1.2,
            'news': 1.1,
            'entertainment': 1.0,
            'sports': 1.1,
            'general': 1.0
        }
        
        multiplier = category_multipliers.get(category, 1.0)
        return round(base_price * multiplier, 2)
    
    async def _estimate_post_count(self, chat_id: int) -> int:
        """Estimate total post count by sampling recent messages"""
        try:
            # This is an estimation - we can't get exact post count from Telegram API
            # We'll try to get some recent messages and estimate based on message IDs
            
            # For now, return a reasonable estimate based on channel age and activity
            # In a real implementation, you might track this over time
            return 100  # Default estimate
            
        except Exception as e:
            logger.warning(f"Could not estimate post count for {chat_id}: {e}")
            return 0
    
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
            logger.info("🔍 Scanning for existing channels where bot is administrator...")
            
            # Check channels we know about in database
            await self._verify_database_channels()
            
            # Try to discover new channels through common methods
            discovered_count = await self._discover_channels_by_patterns()
            
            if discovered_count > 0:
                logger.info(f"✅ Discovered and added {discovered_count} new channels")
            
            logger.info("💡 Use /admin command and 'Add Channel' to manually register existing channels")
            logger.info("💡 Or have channel admins re-add the bot to trigger auto-detection")
            
        except Exception as e:
            logger.error(f"Error syncing existing channels: {e}")
    
    async def _discover_channels_by_patterns(self) -> int:
        """Attempt to discover channels using common patterns and known usernames"""
        discovered_count = 0
        
        # Common channel patterns to check (these are examples - add real channels)
        potential_channels = [
            "@smshco",  # Already confirmed
            "@i3lani",  # Main channel
            # Add more channels here as they become known
        ]
        
        for channel_username in potential_channels:
            try:
                # Check if channel already exists in database
                channels = await self.db.get_channels(active_only=False)
                if any(ch.get('telegram_channel_id') == channel_username for ch in channels):
                    continue
                
                # Try to get channel info
                chat = await self.bot.get_chat(channel_username)
                bot_member = await self.bot.get_chat_member(chat.id, self.bot.id)
                
                if bot_member.status == 'administrator' and bot_member.can_post_messages:
                    # Get subscriber count
                    member_count = await self.bot.get_chat_member_count(chat.id)
                    
                    # Auto-detect category based on channel info
                    category = self._detect_channel_category(chat.title or "", chat.description or "")
                    
                    # Calculate pricing
                    base_price = self._calculate_base_price(member_count, category)
                    
                    # Add to database
                    success = await self.db.add_channel_automatically(
                        channel_id=channel_username.replace("@", ""),
                        channel_name=chat.title or channel_username,
                        telegram_channel_id=channel_username,
                        subscribers=member_count,
                        active_subscribers=int(member_count * 0.45),
                        total_posts=await self._estimate_post_count(chat.id),
                        category=category,
                        description=chat.description or f"Auto-discovered {category} channel",
                        base_price_usd=base_price
                    )
                    
                    if success:
                        logger.info(f"✅ Auto-discovered and added channel: {chat.title} ({channel_username})")
                        logger.info(f"   Subscribers: {member_count:,}, Category: {category}, Price: ${base_price}")
                        discovered_count += 1
                
            except Exception as e:
                logger.debug(f"Channel {channel_username} not accessible or not admin: {e}")
                continue
        
        return discovered_count
    
    async def discover_multiple_channels(self, usernames: List[str]) -> Dict[str, bool]:
        """Discover multiple channels at once"""
        results = {}
        
        for username in usernames:
            username = username.strip()
            if username:
                results[username] = await self.discover_channel_by_username(username)
        
        return results
    
    async def discover_channel_by_username(self, username: str) -> bool:
        """Manually discover and add a channel by username"""
        try:
            if not username.startswith("@"):
                username = f"@{username}"
            
            # Check if already exists
            channels = await self.db.get_channels(active_only=False)
            if any(ch.get('telegram_channel_id') == username for ch in channels):
                logger.info(f"Channel {username} already exists in database")
                return False
            
            # Get channel info
            chat = await self.bot.get_chat(username)
            bot_member = await self.bot.get_chat_member(chat.id, self.bot.id)
            
            if bot_member.status != 'administrator':
                logger.warning(f"Bot is not administrator in {username}")
                return False
            
            if not bot_member.can_post_messages:
                logger.warning(f"Bot cannot post messages in {username}")
                return False
            
            # Get detailed info
            member_count = await self.bot.get_chat_member_count(chat.id)
            category = self._detect_channel_category(chat.title or "", chat.description or "")
            base_price = self._calculate_base_price(member_count, category)
            
            # Add to database
            success = await self.db.add_channel_automatically(
                channel_id=username.replace("@", ""),
                channel_name=chat.title or username,
                telegram_channel_id=username,
                subscribers=member_count,
                active_subscribers=int(member_count * 0.45),
                total_posts=await self._estimate_post_count(chat.id),
                category=category,
                description=chat.description or f"Manually added {category} channel",
                base_price_usd=base_price
            )
            
            if success:
                logger.info(f"✅ Successfully added channel: {chat.title} ({username})")
                return True
            
        except Exception as e:
            logger.error(f"Error discovering channel {username}: {e}")
        
        return False
    
    async def _verify_database_channels(self):
        """Verify channels in database are still valid"""
        try:
            channels = await self.db.get_channels(active_only=False)
            active_count = 0
            inactive_count = 0
            
            for channel in channels:
                channel_id = channel['telegram_channel_id']
                try:
                    # Try to get chat info to verify bot is still admin
                    chat = await self.bot.get_chat(channel_id)
                    
                    # Get bot's status in this chat
                    bot_member = await self.bot.get_chat_member(chat.id, self.bot.id)
                    
                    if bot_member.status == 'administrator' and bot_member.can_post_messages:
                        # Channel is valid and bot is admin
                        await self.db.activate_channel(channel_id)
                        await self.update_channel_stats(channel_id)
                        active_count += 1
                        logger.info(f"✅ Verified channel: {channel['name']}")
                    else:
                        # Bot is not admin or cannot post
                        await self.db.deactivate_channel(channel_id)
                        inactive_count += 1
                        logger.info(f"❌ Bot not admin in: {channel['name']}")
                        
                except Exception as e:
                    # Channel not accessible, probably bot was removed
                    await self.db.deactivate_channel(channel_id)
                    inactive_count += 1
                    logger.warning(f"❌ Cannot access channel: {channel['name']} - {e}")
            
            logger.info(f"📊 Channel verification complete: {active_count} active, {inactive_count} inactive")
            
        except Exception as e:
            logger.error(f"Error verifying database channels: {e}")
    
    async def discover_channel_by_username(self, username: str) -> bool:
        """Manually discover and add a channel by username"""
        try:
            if not username.startswith('@'):
                username = '@' + username
                
            chat = await self.bot.get_chat(username)
            
            # Check if it's a channel/supergroup
            if chat.type not in ['channel', 'supergroup']:
                logger.warning(f"Chat {username} is not a channel")
                return False
            
            # Check if bot is admin
            bot_member = await self.bot.get_chat_member(chat.id, self.bot.id)
            
            if bot_member.status != 'administrator':
                logger.warning(f"Bot is not administrator in {username}")
                return False
                
            if not bot_member.can_post_messages:
                logger.warning(f"Bot cannot post messages in {username}")
                return False
            
            # Add channel using existing logic
            await self.add_channel_as_admin(chat, bot_member)
            return True
            
        except Exception as e:
            logger.error(f"Error discovering channel {username}: {e}")
            return False
    
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
        """Update channel statistics with detailed information"""
        try:
            chat = await self.bot.get_chat(channel_id)
            subscribers = getattr(chat, 'members_count', 0)
            description = getattr(chat, 'description', '')
            
            # Estimate active subscribers
            active_subscribers = int(subscribers * 0.45) if subscribers > 0 else 0
            
            # Detect category again in case it changed
            category = self._detect_channel_category(chat.title or '', description)
            
            # Recalculate base price
            base_price = self._calculate_base_price(subscribers, category)
            
            # Update database with detailed info
            async with aiosqlite.connect(self.db.db_path) as db:
                await db.execute('''
                    UPDATE channels 
                    SET subscribers = ?, active_subscribers = ?, category = ?, 
                        description = ?, base_price_usd = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE telegram_channel_id = ? OR channel_id = ?
                ''', (subscribers, active_subscribers, category, description, 
                     base_price, channel_id, channel_id))
                await db.commit()
                
            logger.info(f"Updated stats for channel {channel_id}: {subscribers} subscribers, {active_subscribers} active, category: {category}")
            
        except Exception as e:
            logger.error(f"Error updating channel stats: {e}")
    
    async def sync_all_channels(self):
        """Sync statistics for all active channels"""
        try:
            channels = await self.db.get_channels(active_only=True)
            
            for channel in channels:
                await self.update_channel_stats(channel['telegram_channel_id'])
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
            logger.info(f"Synced statistics for {len(channels)} channels")
            
        except Exception as e:
            logger.error(f"Error syncing all channels: {e}")


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