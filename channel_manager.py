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
from telegram_channel_api import get_telegram_channel_api

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
                # Get who added the bot
                added_by_user_id = chat_member_updated.from_user.id if chat_member_updated.from_user else None
                await self.add_channel_as_admin(chat, chat_member_updated.new_chat_member, added_by_user_id)
            
            # Check if bot lost admin privileges
            elif old_status == 'administrator' and new_status in ['left', 'member', 'restricted']:
                await self.remove_channel_admin(chat)
                
        except Exception as e:
            logger.error(f"Error handling bot status change: {e}")
    
    async def add_channel_as_admin(self, chat: Chat, chat_member: ChatMember, added_by_user_id: int = None):
        """Add channel when bot becomes admin with detailed analysis using Telegram API"""
        try:
            # Check if bot can post messages
            if not chat_member.can_post_messages:
                logger.warning(f"Bot added as admin to {chat.title} but cannot post messages")
                return
            
            # Get enhanced channel information using Telegram API
            telegram_api = get_telegram_channel_api(self.bot)
            channel_info = await telegram_api.get_channel_info(str(chat.id))
            
            if not channel_info:
                logger.error(f"Could not get channel info for {chat.title}")
                return
            
            # Get detailed statistics
            channel_stats = await telegram_api.get_channel_statistics(str(chat.id))
            
            # Extract information
            channel_id = str(chat.id)
            channel_name = channel_info['title'] or f"Channel {channel_id}"
            telegram_channel_id = channel_info['username'] if channel_info['username'] else channel_id
            description = channel_info['description'] or ""
            subscribers = channel_info['member_count']
            active_subscribers = channel_stats['active_subscribers'] if channel_stats else int(subscribers * 0.45)
            category = channel_stats['category'] if channel_stats else 'general'
            
            # Try to estimate post count by getting recent messages
            total_posts = await self._estimate_post_count(chat.id) if hasattr(self, '_estimate_post_count') else 0
            
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
            
            # Notify admin about new channel
            await self._notify_admin_new_channel(chat, subscribers, added_by_user_id)
            
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
    
    async def _notify_admin_new_channel(self, chat: Chat, subscribers: int, added_by_user_id: int = None):
        """Notify admin when bot is added to a new channel"""
        try:
            from config import ADMIN_IDS
            from datetime import datetime
            
            # Get who added the bot (if available)
            added_by_username = "Unknown"
            if added_by_user_id:
                try:
                    user = await self.bot.get_chat_member(chat.id, added_by_user_id)
                    added_by_username = f"@{user.user.username}" if user.user.username else f"User ID: {added_by_user_id}"
                except:
                    added_by_username = f"User ID: {added_by_user_id}"
            
            # Format notification message
            notification = f"""✅ **New Channel Detected!**

The bot was added as admin in:
📢 **Channel:** {chat.title}
🔗 **Username:** @{chat.username if chat.username else 'Private'}
🆔 **ID:** `{chat.id}`
👥 **Subscribers:** {subscribers:,}
👤 **Added by:** {added_by_username}
🕒 **Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

🛠️ **Status:** Ready for testing
💰 **Your Access:** Free posting (Admin privilege)

👑 **Admin Benefits:**
• Post unlimited ads for FREE in this channel
• Test all bot features without payment
• Priority support and exclusive access"""
            
            # Send to all admins
            for admin_id in ADMIN_IDS:
                try:
                    await self.bot.send_message(
                        admin_id,
                        notification,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Could not notify admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error notifying admin about new channel: {e}")
    
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
        """Comprehensive channel discovery using multiple methods"""
        discovered_count = 0
        
        # Method 1: Check known channels
        known_channels = [
            "@smshco",  # Already confirmed
            "@i3lani",  # Main channel
            "@Five_SAR",  # Five SAR channel
            # Add more channels here where bot is admin
        ]
        
        for channel_username in known_channels:
            if await self._try_discover_single_channel(channel_username):
                discovered_count += 1
        
        # Method 2: Try common channel patterns and variations
        # This helps find channels with common naming patterns
        patterns = await self._generate_potential_channel_patterns()
        
        for pattern in patterns:
            if await self._try_discover_single_channel(pattern):
                discovered_count += 1
                if discovered_count >= 50:  # Limit to prevent excessive API calls
                    break
        
        return discovered_count
    
    async def _generate_potential_channel_patterns(self) -> List[str]:
        """Generate potential channel usernames based on common patterns"""
        patterns = []
        
        # Common prefixes and suffixes for channels
        base_names = ["i3lani", "shop", "news", "tech", "business", "deals", "offers", 
                     "3lani", "e3lani", "i3lan", "e3lan", "a3lan", "i3lany", "e3lany",
                     "smart", "smshco", "ads", "market", "store", "sale", "promo"]
        suffixes = ["", "_channel", "_official", "_news", "_deals", "_shop", "_tech", "_main",
                   "_sa", "_ksa", "_saudi", "_arab", "_me", "_bot", "_ads", "_market"]
        prefixes = ["", "official_", "the_", "new_", "best_"]
        
        for base in base_names:
            for prefix in prefixes:
                for suffix in suffixes:
                    username = f"@{prefix}{base}{suffix}"
                    if len(username) <= 32:  # Telegram username limit
                        patterns.append(username)
        
        # Also try some numbered variations
        for base in ["i3lani", "shop"]:
            for i in range(1, 10):
                patterns.extend([f"@{base}{i}", f"@{base}_{i}"])
        
        return patterns[:100]  # Limit to first 100 patterns
    
    async def _try_discover_single_channel(self, channel_username: str) -> bool:
        """Try to discover and add a single channel"""
        try:
            # Check if channel already exists in database
            channels = await self.db.get_channels(active_only=False)
            if any(ch.get('telegram_channel_id') == channel_username for ch in channels):
                return False
            
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
                    return True
                
        except Exception as e:
            logger.debug(f"Channel {channel_username} not accessible or not admin: {e}")
        
        return False
    
    async def discover_multiple_channels(self, usernames: List[str]) -> Dict[str, bool]:
        """Discover multiple channels at once"""
        results = {}
        
        for username in usernames:
            username = username.strip()
            if username:
                results[username] = await self.discover_channel_by_username(username)
        
        return results
    
    async def force_full_channel_discovery(self) -> Dict[str, any]:
        """Force a comprehensive channel discovery scan"""
        try:
            logger.info("🚀 Starting comprehensive channel discovery...")
            
            results = {
                'total_scanned': 0,
                'newly_discovered': 0,
                'already_known': 0,
                'failed_attempts': 0,
                'discovered_channels': []
            }
            
            # Get existing channels to avoid duplicates
            existing_channels = await self.db.get_channels(active_only=False)
            existing_usernames = {ch.get('telegram_channel_id') for ch in existing_channels}
            
            # Generate comprehensive list of potential channels
            potential_channels = await self._generate_potential_channel_patterns()
            
            # Add known channels and variations
            known_channels = [
                "@smshco", "@i3lani", "@shop_smart", "@i3lani_news",
                "@i3lani_official", "@i3lani_main", "@i3lani_ads", "@i3lani_channel",
                "@i3lani_ksa", "@i3lani_sa", "@i3lani_saudi", "@i3lani_arab",
                "@i3lani_market", "@i3lani_deals", "@i3lani_offers", "@i3lani_promo",
                "@i3lani_shop", "@i3lani_store", "@i3lani_buy", "@i3lani_sell",
                "@i3lani_tech", "@i3lani_business", "@i3lani_trade",
                "@3lani", "@e3lani", "@a3lani", "@i3lan", "@e3lan",
                "@smshco_official", "@smshco_ksa", "@smart_shop", "@smart_shop_sa"
            ]
            potential_channels.extend(known_channels)
            
            for channel_username in potential_channels:
                results['total_scanned'] += 1
                
                if channel_username in existing_usernames:
                    results['already_known'] += 1
                    continue
                
                try:
                    # Try to get channel info
                    chat = await self.bot.get_chat(channel_username)
                    bot_member = await self.bot.get_chat_member(chat.id, self.bot.id)
                    
                    if bot_member.status == 'administrator' and bot_member.can_post_messages:
                        # Get subscriber count
                        member_count = await self.bot.get_chat_member_count(chat.id)
                        
                        # Auto-detect category
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
                            description=chat.description or f"Force-discovered {category} channel",
                            base_price_usd=base_price
                        )
                        
                        if success:
                            results['newly_discovered'] += 1
                            results['discovered_channels'].append({
                                'username': channel_username,
                                'name': chat.title,
                                'subscribers': member_count,
                                'category': category
                            })
                            logger.info(f"🎯 Force-discovered: {chat.title} ({channel_username}) - {member_count:,} subscribers")
                        
                except Exception as e:
                    results['failed_attempts'] += 1
                    logger.debug(f"Channel {channel_username} not accessible or not admin: {e}")
                
                # Add small delay to prevent rate limiting
                await asyncio.sleep(0.1)
            
            logger.info(f"🏁 Discovery complete: {results['newly_discovered']} new channels found out of {results['total_scanned']} scanned")
            return results
            
        except Exception as e:
            logger.error(f"Error in force channel discovery: {e}")
            return {'error': str(e)}
    
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
            
            # Get real subscriber count using proper API method
            try:
                subscribers = await self.bot.get_chat_member_count(chat.id)
            except Exception:
                # Fallback to get_chat_members_count if the above fails
                try:
                    subscribers = await self.bot.get_chat_members_count(chat.id)
                except Exception:
                    subscribers = 0
            
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