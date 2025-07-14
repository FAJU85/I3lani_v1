"""
Advanced Channel Management System for I3lani Bot
Comprehensive channel detection, management, and administration
"""

import logging
import asyncio
from typing import List, Dict, Optional, Tuple
from aiogram import Bot
from aiogram.types import Chat, ChatMember, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from datetime import datetime, timedelta
import aiohttp
import json
import re

from database import db
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

class ChannelInfo:
    """Channel information container"""
    def __init__(self, channel_id: int, username: str, title: str, 
                 subscriber_count: int, is_active: bool = True, 
                 category: str = "general", description: str = ""):
        self.channel_id = channel_id
        self.username = username
        self.title = title
        self.subscriber_count = subscriber_count
        self.is_active = is_active
        self.category = category
        self.description = description
        self.last_updated = datetime.now()
        self.bot_is_admin = False
        self.can_post = False

class AdvancedChannelManager:
    """Advanced channel management with comprehensive features"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.discovered_channels: Dict[int, ChannelInfo] = {}
        self.scan_in_progress = False
        self.last_scan_time = None
        
    async def initialize_database(self):
        """Initialize advanced channel management database tables"""
        connection = await db.get_connection()
        cursor = await connection.cursor()
        
        # Enhanced channels table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS advanced_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER UNIQUE,
                username TEXT,
                title TEXT,
                subscriber_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                category TEXT DEFAULT 'general',
                description TEXT DEFAULT '',
                bot_is_admin BOOLEAN DEFAULT 0,
                can_post BOOLEAN DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Channel discovery log
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_discovery_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                username TEXT,
                title TEXT,
                discovery_method TEXT,
                discovery_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action_taken TEXT,
                admin_decision TEXT DEFAULT 'pending'
            )
        ''')
        
        # Channel statistics
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                date DATE,
                subscriber_count INTEGER,
                active_subscribers INTEGER,
                posts_count INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                FOREIGN KEY (channel_id) REFERENCES advanced_channels(channel_id)
            )
        ''')
        
        await connection.commit()
        await connection.close()
        logger.info("✅ Advanced channel management database initialized")
    
    async def auto_detect_new_channels(self) -> List[ChannelInfo]:
        """Automatically detect new channels where bot is admin"""
        if self.scan_in_progress:
            logger.info("🔄 Channel scan already in progress")
            return []
            
        self.scan_in_progress = True
        discovered = []
        
        try:
            logger.info("🔍 Starting automatic channel detection...")
            
            # Get bot information
            bot_info = await self.bot.get_me()
            
            # Method 1: Check existing channels for updates
            existing_channels = await self.get_all_channels()
            for channel in existing_channels:
                try:
                    updated_info = await self.get_channel_detailed_info(channel['channel_id'])
                    if updated_info:
                        discovered.append(updated_info)
                except Exception as e:
                    logger.warning(f"Could not update channel {channel['username']}: {e}")
            
            # Method 2: Scan for new channels (limited approach due to Telegram API restrictions)
            # Note: Full channel discovery requires specific API methods or manual addition
            
            logger.info(f"🎯 Auto-detection complete: {len(discovered)} channels processed")
            
        except Exception as e:
            logger.error(f"Error in auto-detection: {e}")
            
        finally:
            self.scan_in_progress = False
            self.last_scan_time = datetime.now()
            
        return discovered
    
    async def get_channel_detailed_info(self, channel_id: int) -> Optional[ChannelInfo]:
        """Get detailed information about a specific channel"""
        try:
            chat = await self.bot.get_chat(channel_id)
            
            # Get bot's admin status
            try:
                bot_member = await self.bot.get_chat_member(channel_id, self.bot.id)
                bot_is_admin = bot_member.status in ['administrator', 'creator']
                can_post = getattr(bot_member, 'can_post_messages', False) if bot_is_admin else False
            except:
                bot_is_admin = False
                can_post = False
            
            # Get subscriber count
            try:
                member_count = await self.bot.get_chat_member_count(channel_id)
            except:
                member_count = 0
            
            channel_info = ChannelInfo(
                channel_id=chat.id,
                username=chat.username or "",
                title=chat.title or "",
                subscriber_count=member_count,
                description=chat.description or "",
                category=self.classify_channel(chat.title, chat.description)
            )
            
            channel_info.bot_is_admin = bot_is_admin
            channel_info.can_post = can_post
            
            return channel_info
            
        except Exception as e:
            logger.error(f"Error getting channel info for {channel_id}: {e}")
            return None
    
    def classify_channel(self, title: str, description: str) -> str:
        """Automatically classify channel based on title and description"""
        content = f"{title} {description}".lower()
        
        # Classification keywords
        categories = {
            'business': ['business', 'عمل', 'تجارة', 'бизнес', 'company', 'startup'],
            'technology': ['tech', 'تقنية', 'технология', 'programming', 'software', 'ai'],
            'news': ['news', 'أخبار', 'новости', 'breaking', 'latest'],
            'entertainment': ['entertainment', 'ترفيه', 'развлечения', 'fun', 'games'],
            'education': ['education', 'تعليم', 'образование', 'learn', 'course'],
            'shopping': ['shop', 'shopping', 'تسوق', 'магазин', 'store', 'buy', 'sell'],
            'crypto': ['crypto', 'bitcoin', 'blockchain', 'عملة', 'криптовалюта'],
            'health': ['health', 'صحة', 'здоровье', 'medical', 'fitness'],
            'travel': ['travel', 'سفر', 'путешествие', 'tourism', 'trip'],
            'food': ['food', 'طعام', 'еда', 'restaurant', 'recipe', 'cooking']
        }
        
        for category, keywords in categories.items():
            if any(keyword in content for keyword in keywords):
                return category
                
        return 'general'
    
    async def search_channels_telegram(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for channels on Telegram (limited by API restrictions)"""
        # Note: Telegram Bot API has limited search capabilities
        # This is a placeholder for potential future implementation
        logger.warning("Direct channel search not available via Bot API")
        return []
    
    async def add_channel_to_database(self, channel_info: ChannelInfo, status: str = "pending") -> bool:
        """Add channel to database with admin approval status"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                INSERT OR REPLACE INTO advanced_channels 
                (channel_id, username, title, subscriber_count, is_active, category, 
                 description, bot_is_admin, can_post, status, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                channel_info.channel_id,
                channel_info.username,
                channel_info.title,
                channel_info.subscriber_count,
                channel_info.is_active,
                channel_info.category,
                channel_info.description,
                channel_info.bot_is_admin,
                channel_info.can_post,
                status,
                datetime.now()
            ))
            
            # Log discovery
            await cursor.execute('''
                INSERT INTO channel_discovery_log 
                (channel_id, username, title, discovery_method, action_taken)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                channel_info.channel_id,
                channel_info.username,
                channel_info.title,
                "auto_detection",
                "added_to_database"
            ))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Channel {channel_info.username} added to database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding channel to database: {e}")
            return False
    
    async def get_all_channels(self) -> List[Dict]:
        """Get all channels from database"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                SELECT channel_id, username, title, subscriber_count, is_active, 
                       category, description, bot_is_admin, can_post, status, last_updated
                FROM advanced_channels
                ORDER BY last_updated DESC
            ''')
            
            rows = await cursor.fetchall()
            await connection.close()
            
            channels = []
            for row in rows:
                channels.append({
                    'channel_id': row[0],
                    'username': row[1],
                    'title': row[2],
                    'subscriber_count': row[3],
                    'is_active': bool(row[4]),
                    'category': row[5],
                    'description': row[6],
                    'bot_is_admin': bool(row[7]),
                    'can_post': bool(row[8]),
                    'status': row[9],
                    'last_updated': row[10]
                })
            
            return channels
            
        except Exception as e:
            logger.error(f"Error getting channels: {e}")
            return []
    
    async def update_channel_status(self, channel_id: int, status: str) -> bool:
        """Update channel status (accept/reject)"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                UPDATE advanced_channels 
                SET status = ?, last_updated = ?
                WHERE channel_id = ?
            ''', (status, datetime.now(), channel_id))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Channel {channel_id} status updated to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating channel status: {e}")
            return False
    
    async def delete_channel(self, channel_id: int) -> bool:
        """Delete channel from database"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('DELETE FROM advanced_channels WHERE channel_id = ?', (channel_id,))
            await cursor.execute('DELETE FROM channel_discovery_log WHERE channel_id = ?', (channel_id,))
            await cursor.execute('DELETE FROM channel_statistics WHERE channel_id = ?', (channel_id,))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Channel {channel_id} deleted from database")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting channel: {e}")
            return False
    
    async def manual_add_channel(self, channel_identifier: str) -> Optional[ChannelInfo]:
        """Manually add channel by username or ID"""
        try:
            # Try to get channel info
            if channel_identifier.startswith('@'):
                chat = await self.bot.get_chat(channel_identifier)
            else:
                # Try as channel ID
                try:
                    channel_id = int(channel_identifier)
                    chat = await self.bot.get_chat(channel_id)
                except ValueError:
                    chat = await self.bot.get_chat(f"@{channel_identifier}")
            
            channel_info = await self.get_channel_detailed_info(chat.id)
            if channel_info:
                await self.add_channel_to_database(channel_info, "approved")
                return channel_info
            
        except Exception as e:
            logger.error(f"Error manually adding channel {channel_identifier}: {e}")
            
        return None
    
    async def get_channel_statistics(self, channel_id: int) -> Dict:
        """Get detailed statistics for a channel"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            # Get current channel info
            await cursor.execute('''
                SELECT * FROM advanced_channels WHERE channel_id = ?
            ''', (channel_id,))
            
            channel_data = await cursor.fetchone()
            
            if not channel_data:
                return {}
            
            # Get statistics history
            await cursor.execute('''
                SELECT date, subscriber_count, active_subscribers, posts_count, engagement_rate
                FROM channel_statistics 
                WHERE channel_id = ? 
                ORDER BY date DESC LIMIT 30
            ''', (channel_id,))
            
            stats_history = await cursor.fetchall()
            await connection.close()
            
            return {
                'channel_info': {
                    'channel_id': channel_data[1],
                    'username': channel_data[2],
                    'title': channel_data[3],
                    'subscriber_count': channel_data[4],
                    'category': channel_data[6],
                    'status': channel_data[10]
                },
                'statistics': [
                    {
                        'date': row[0],
                        'subscriber_count': row[1],
                        'active_subscribers': row[2],
                        'posts_count': row[3],
                        'engagement_rate': row[4]
                    } for row in stats_history
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting channel statistics: {e}")
            return {}
    
    async def create_channel_management_keyboard(self, page: int = 0) -> InlineKeyboardMarkup:
        """Create advanced channel management keyboard"""
        buttons = []
        
        # Main management buttons
        buttons.append([
            InlineKeyboardButton(text="🔍 Auto-Scan Channels", callback_data="adv_auto_scan"),
            InlineKeyboardButton(text="➕ Add Channel", callback_data="adv_add_channel")
        ])
        
        buttons.append([
            InlineKeyboardButton(text="✅ Approve Pending", callback_data="adv_approve_pending"),
            InlineKeyboardButton(text="❌ Reject Pending", callback_data="adv_reject_pending")
        ])
        
        buttons.append([
            InlineKeyboardButton(text="📊 Channel Statistics", callback_data="adv_channel_stats"),
            InlineKeyboardButton(text="🗑️ Delete Channel", callback_data="adv_delete_channel")
        ])
        
        buttons.append([
            InlineKeyboardButton(text="📋 All Channels", callback_data="adv_list_channels"),
            InlineKeyboardButton(text="🔄 Refresh", callback_data="adv_refresh")
        ])
        
        buttons.append([
            InlineKeyboardButton(text="🏠 Back to Admin", callback_data="admin_main")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    async def create_channel_list_keyboard(self, channels: List[Dict], page: int = 0) -> InlineKeyboardMarkup:
        """Create keyboard with channel list"""
        buttons = []
        
        # Show channels (5 per page)
        start_idx = page * 5
        end_idx = start_idx + 5
        page_channels = channels[start_idx:end_idx]
        
        for channel in page_channels:
            status_icon = "✅" if channel['status'] == 'approved' else "⏳" if channel['status'] == 'pending' else "❌"
            admin_icon = "👑" if channel['bot_is_admin'] else "👤"
            
            button_text = f"{status_icon} {admin_icon} {channel['title'][:20]}... ({channel['subscriber_count']})"
            buttons.append([
                InlineKeyboardButton(text=button_text, callback_data=f"adv_channel_detail_{channel['channel_id']}")
            ])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"adv_list_channels_{page-1}"))
        if end_idx < len(channels):
            nav_buttons.append(InlineKeyboardButton(text="➡️ Next", callback_data=f"adv_list_channels_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([
            InlineKeyboardButton(text="🔙 Back", callback_data="adv_channel_management")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    async def get_management_summary(self) -> str:
        """Get channel management summary"""
        try:
            channels = await self.get_all_channels()
            
            total_channels = len(channels)
            approved_channels = len([c for c in channels if c['status'] == 'approved'])
            pending_channels = len([c for c in channels if c['status'] == 'pending'])
            bot_admin_channels = len([c for c in channels if c['bot_is_admin']])
            total_subscribers = sum(c['subscriber_count'] for c in channels if c['status'] == 'approved')
            
            last_scan = "Never" if not self.last_scan_time else self.last_scan_time.strftime("%Y-%m-%d %H:%M")
            
            summary = f"""
🏢 <b>Advanced Channel Management</b>

📊 <b>Overview:</b>
• Total Channels: {total_channels}
• Approved: {approved_channels}
• Pending Review: {pending_channels}
• Bot Admin Rights: {bot_admin_channels}
• Total Subscribers: {total_subscribers:,}

🔍 <b>Auto-Scan Status:</b>
• Last Scan: {last_scan}
• Scan Status: {'🔄 In Progress' if self.scan_in_progress else '✅ Ready'}

🎯 <b>Available Actions:</b>
• Auto-detect new channels
• Approve/reject pending channels
• Add channels manually
• View detailed statistics
• Delete unwanted channels
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating management summary: {e}")
            return "❌ Error generating summary"

# Global instance
advanced_channel_manager = None

def get_advanced_channel_manager(bot: Bot) -> AdvancedChannelManager:
    """Get or create advanced channel manager instance"""
    global advanced_channel_manager
    if advanced_channel_manager is None:
        advanced_channel_manager = AdvancedChannelManager(bot)
    return advanced_channel_manager