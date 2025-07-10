"""
Enhanced Telegram Channel API Integration
Using official Telegram Bot API for improved channel management and statistics
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from aiogram import Bot
from aiogram.types import Chat, ChatMember, ChatMemberOwner, ChatMemberAdministrator
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from database import db
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class TelegramChannelAPI:
    """Enhanced Telegram Channel API integration for I3lani Bot"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        
    async def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive channel information using official Telegram API"""
        try:
            # Get basic chat info
            chat = await self.bot.get_chat(channel_id)
            
            # Get member count
            member_count = await self.bot.get_chat_member_count(channel_id)
            
            # Get administrators
            administrators = await self.bot.get_chat_administrators(channel_id)
            
            # Check if bot is admin
            bot_info = await self.bot.get_me()
            is_bot_admin = any(
                admin.user.id == bot_info.id and 
                isinstance(admin, (ChatMemberOwner, ChatMemberAdministrator))
                for admin in administrators
            )
            
            channel_info = {
                'id': chat.id,
                'username': chat.username,
                'title': chat.title,
                'description': chat.description,
                'member_count': member_count,
                'type': chat.type,
                'is_bot_admin': is_bot_admin,
                'invite_link': chat.invite_link,
                'administrators_count': len(administrators),
                'photo_url': None,
                'last_updated': datetime.now().isoformat()
            }
            
            # Get profile photo if available
            if chat.photo:
                try:
                    photo_file = await self.bot.get_file(chat.photo.big_file_id)
                    channel_info['photo_url'] = f"https://api.telegram.org/file/bot{self.bot.token}/{photo_file.file_path}"
                except Exception as e:
                    logger.warning(f"Could not get photo for channel {channel_id}: {e}")
            
            return channel_info
            
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            logger.error(f"Error getting channel info for {channel_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting channel info for {channel_id}: {e}")
            return None
    
    async def get_channel_statistics(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get enhanced channel statistics"""
        try:
            # Get basic info
            channel_info = await self.get_channel_info(channel_id)
            if not channel_info:
                return None
            
            # Calculate active subscribers (estimation based on channel type and size)
            total_subscribers = channel_info['member_count']
            active_rate = self._calculate_active_rate(total_subscribers)
            active_subscribers = int(total_subscribers * active_rate)
            
            # Get recent activity indicators
            recent_activity = await self._get_recent_activity(channel_id)
            
            # Determine channel category
            category = self._determine_channel_category(
                channel_info['title'], 
                channel_info['description']
            )
            
            statistics = {
                'channel_id': channel_id,
                'total_subscribers': total_subscribers,
                'active_subscribers': active_subscribers,
                'active_rate': active_rate,
                'category': category,
                'engagement_score': self._calculate_engagement_score(
                    total_subscribers, 
                    recent_activity
                ),
                'growth_trend': 'stable',  # Would need historical data
                'posting_frequency': recent_activity.get('posts_per_day', 0),
                'last_post_date': recent_activity.get('last_post_date'),
                'administrators_count': channel_info['administrators_count'],
                'updated_at': datetime.now().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting channel statistics for {channel_id}: {e}")
            return None
    
    async def verify_bot_admin_status(self, channel_id: str) -> bool:
        """Verify if bot has admin privileges in channel"""
        try:
            # Get bot info
            bot_info = await self.bot.get_me()
            
            # Get bot's membership status
            bot_member = await self.bot.get_chat_member(channel_id, bot_info.id)
            
            # Check if bot is administrator or owner
            return isinstance(bot_member, (ChatMemberOwner, ChatMemberAdministrator))
            
        except Exception as e:
            logger.error(f"Error verifying bot admin status for {channel_id}: {e}")
            return False
    
    async def get_channel_administrators(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get list of channel administrators"""
        try:
            administrators = await self.bot.get_chat_administrators(channel_id)
            
            admin_list = []
            for admin in administrators:
                admin_info = {
                    'user_id': admin.user.id,
                    'username': admin.user.username,
                    'first_name': admin.user.first_name,
                    'last_name': admin.user.last_name,
                    'status': admin.status,
                    'is_anonymous': getattr(admin, 'is_anonymous', False)
                }
                
                # Add specific permissions for administrators
                if isinstance(admin, ChatMemberAdministrator):
                    admin_info.update({
                        'can_be_edited': admin.can_be_edited,
                        'can_manage_chat': admin.can_manage_chat,
                        'can_delete_messages': admin.can_delete_messages,
                        'can_manage_video_chats': admin.can_manage_video_chats,
                        'can_restrict_members': admin.can_restrict_members,
                        'can_promote_members': admin.can_promote_members,
                        'can_change_info': admin.can_change_info,
                        'can_invite_users': admin.can_invite_users,
                        'can_post_messages': admin.can_post_messages,
                        'can_edit_messages': admin.can_edit_messages,
                        'can_pin_messages': admin.can_pin_messages
                    })
                
                admin_list.append(admin_info)
            
            return admin_list
            
        except Exception as e:
            logger.error(f"Error getting administrators for {channel_id}: {e}")
            return []
    
    async def scan_bot_admin_channels(self) -> List[Dict[str, Any]]:
        """Scan all channels where bot is administrator"""
        try:
            # Get existing channels from database
            existing_channels = await db.get_all_channels()
            
            verified_channels = []
            
            for channel in existing_channels:
                channel_id = channel.get('channel_id') or channel.get('username')
                if not channel_id:
                    continue
                
                # Verify bot admin status
                is_admin = await self.verify_bot_admin_status(channel_id)
                
                if is_admin:
                    # Get updated channel info
                    channel_info = await self.get_channel_info(channel_id)
                    if channel_info:
                        # Get statistics
                        stats = await self.get_channel_statistics(channel_id)
                        if stats:
                            channel_info.update(stats)
                        
                        verified_channels.append(channel_info)
                        
                        # Update database
                        await self._update_channel_in_database(channel_info)
                
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            
            return verified_channels
            
        except Exception as e:
            logger.error(f"Error scanning bot admin channels: {e}")
            return []
    
    async def _get_recent_activity(self, channel_id: str) -> Dict[str, Any]:
        """Get recent activity indicators (limited by Bot API)"""
        try:
            # Note: Bot API has limited access to channel statistics
            # This is a simplified implementation
            return {
                'posts_per_day': 1,  # Estimated
                'last_post_date': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting recent activity for {channel_id}: {e}")
            return {}
    
    def _calculate_active_rate(self, total_subscribers: int) -> float:
        """Calculate estimated active subscriber rate"""
        if total_subscribers < 100:
            return 0.8  # High engagement for small channels
        elif total_subscribers < 1000:
            return 0.6  # Good engagement for medium channels
        elif total_subscribers < 10000:
            return 0.45  # Average engagement for large channels
        else:
            return 0.3  # Lower engagement for very large channels
    
    def _determine_channel_category(self, title: str, description: str) -> str:
        """Determine channel category based on title and description"""
        content = f"{title or ''} {description or ''}".lower()
        
        # Arabic keywords
        if any(keyword in content for keyword in ['تقني', 'تكنولوجيا', 'tech', 'technology']):
            return 'technology'
        elif any(keyword in content for keyword in ['تسوق', 'shop', 'shopping', 'متجر']):
            return 'shopping'
        elif any(keyword in content for keyword in ['أخبار', 'news', 'إخبارية']):
            return 'news'
        elif any(keyword in content for keyword in ['ترفيه', 'entertainment', 'فن']):
            return 'entertainment'
        elif any(keyword in content for keyword in ['تعليم', 'education', 'تعلم']):
            return 'education'
        elif any(keyword in content for keyword in ['أعمال', 'business', 'تجارة']):
            return 'business'
        elif any(keyword in content for keyword in ['رياضة', 'sports', 'sport']):
            return 'sports'
        else:
            return 'general'
    
    def _calculate_engagement_score(self, subscribers: int, recent_activity: Dict) -> float:
        """Calculate engagement score based on various factors"""
        try:
            base_score = min(100, subscribers / 100)  # Base score from subscriber count
            activity_score = recent_activity.get('posts_per_day', 0) * 10
            return min(100, base_score + activity_score)
        except Exception:
            return 50.0  # Default score
    
    async def _update_channel_in_database(self, channel_info: Dict[str, Any]):
        """Update channel information in database"""
        try:
            await db.update_channel_stats(
                channel_id=channel_info['id'],
                subscribers=channel_info['member_count'],
                active_subscribers=channel_info.get('active_subscribers', 0),
                category=channel_info.get('category', 'general'),
                last_updated=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error updating channel in database: {e}")
    
    async def get_channel_invite_link(self, channel_id: str) -> Optional[str]:
        """Get or create channel invite link"""
        try:
            # Try to get existing invite link
            chat = await self.bot.get_chat(channel_id)
            if chat.invite_link:
                return chat.invite_link
            
            # Create new invite link if bot has permission
            invite_link = await self.bot.create_chat_invite_link(channel_id)
            return invite_link.invite_link
            
        except Exception as e:
            logger.error(f"Error getting invite link for {channel_id}: {e}")
            return None
    
    async def post_to_channel(self, channel_id: str, content: str, 
                             photo_urls: List[str] = None, 
                             video_url: str = None) -> bool:
        """Post content to channel"""
        try:
            if photo_urls:
                # Send photo with caption
                await self.bot.send_photo(
                    chat_id=channel_id,
                    photo=photo_urls[0],
                    caption=content,
                    parse_mode='HTML'
                )
            elif video_url:
                # Send video with caption
                await self.bot.send_video(
                    chat_id=channel_id,
                    video=video_url,
                    caption=content,
                    parse_mode='HTML'
                )
            else:
                # Send text message
                await self.bot.send_message(
                    chat_id=channel_id,
                    text=content,
                    parse_mode='HTML'
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error posting to channel {channel_id}: {e}")
            return False


# Global instance
telegram_channel_api = None

def get_telegram_channel_api(bot: Bot) -> TelegramChannelAPI:
    """Get or create TelegramChannelAPI instance"""
    global telegram_channel_api
    if not telegram_channel_api:
        telegram_channel_api = TelegramChannelAPI(bot)
    return telegram_channel_api