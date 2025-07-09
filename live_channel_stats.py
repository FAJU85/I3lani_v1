"""
Live Channel Statistics System for I3lani Bot
Provides real-time subscriber counts and enhanced channel display
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from aiogram import Bot
from database import Database

logger = logging.getLogger(__name__)

class LiveChannelStats:
    def __init__(self, bot: Bot, database: Database):
        self.bot = bot
        self.db = database
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        
    async def get_live_subscriber_count(self, channel_id: str) -> int:
        """Get live subscriber count from Telegram API with caching"""
        try:
            # Check cache first
            cache_key = f"subs_{channel_id}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                    return cached_data['count']
            
            # Fetch from Telegram API
            try:
                chat = await self.bot.get_chat(channel_id)
                subscriber_count = getattr(chat, 'members_count', 0)
                
                # Cache the result
                self.cache[cache_key] = {
                    'count': subscriber_count,
                    'timestamp': datetime.now()
                }
                
                return subscriber_count
                
            except Exception as api_error:
                logger.warning(f"Failed to get live count for {channel_id}: {api_error}")
                # Fallback to database
                return await self._get_database_subscriber_count(channel_id)
                
        except Exception as e:
            logger.error(f"Error getting live subscriber count: {e}")
            return 0
    
    async def _get_database_subscriber_count(self, channel_id: str) -> int:
        """Get subscriber count from database as fallback"""
        try:
            channels = await self.db.get_channels(active_only=True)
            for channel in channels:
                if (channel.get('channel_id') == channel_id or 
                    channel.get('telegram_channel_id') == channel_id):
                    return channel.get('subscribers', 0)
            return 0
        except Exception as e:
            logger.error(f"Error getting database subscriber count: {e}")
            return 0
    
    async def get_enhanced_channel_data(self, channels: List[Dict]) -> List[Dict]:
        """Enhance channel data with live subscriber counts"""
        enhanced_channels = []
        
        for channel in channels:
            try:
                # Get live subscriber count
                channel_id = channel.get('telegram_channel_id') or channel.get('channel_id')
                live_count = await self.get_live_subscriber_count(channel_id)
                
                # Update database if count changed significantly
                db_count = channel.get('subscribers', 0)
                if abs(live_count - db_count) > max(10, db_count * 0.1):  # 10+ or 10% change
                    await self._update_database_count(channel_id, live_count)
                
                # Create enhanced channel data
                enhanced_channel = channel.copy()
                enhanced_channel['live_subscribers'] = live_count
                enhanced_channel['subscribers'] = live_count  # Update current count
                enhanced_channels.append(enhanced_channel)
                
            except Exception as e:
                logger.error(f"Error enhancing channel {channel.get('name', 'Unknown')}: {e}")
                # Use original data if enhancement fails
                enhanced_channels.append(channel)
        
        return enhanced_channels
    
    async def _update_database_count(self, channel_id: str, new_count: int):
        """Update database with new subscriber count"""
        try:
            import aiosqlite
            async with aiosqlite.connect(self.db.db_path) as db:
                await db.execute('''
                    UPDATE channels 
                    SET subscribers = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE channel_id = ? OR telegram_channel_id = ?
                ''', (new_count, channel_id, channel_id))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error updating database count: {e}")
    
    def format_channel_name_with_scroll(self, name: str, max_length: int = 25, language: str = 'en') -> str:
        """Format channel name with scrolling for long names"""
        if len(name) <= max_length:
            return name
        
        # Implement scrolling based on language direction
        if language == 'ar':
            # Arabic - scroll rightward (RTL)
            return f"{name[:max_length-3]}... →"
        else:
            # English/Russian - scroll leftward (LTR)
            return f"← ...{name[-(max_length-3):]}"
    
    def create_channel_button_text(self, channel: Dict, is_selected: bool, language: str = 'en') -> str:
        """Create enhanced channel button text with improved layout"""
        name = channel.get('name', 'Unknown Channel')
        live_count = channel.get('live_subscribers', channel.get('subscribers', 0))
        
        # Format name with scrolling if needed
        formatted_name = self.format_channel_name_with_scroll(name, 25, language)
        
        # Selection indicator
        indicator = "✅" if is_selected else "⭕"
        
        # Create multi-line button text (name on top, count below)
        if live_count > 0:
            count_text = f"{live_count:,} subscribers"
            if language == 'ar':
                count_text = f"{live_count:,} مشترك"
            elif language == 'ru':
                count_text = f"{live_count:,} подписчиков"
            
            button_text = f"{indicator} {formatted_name}\n📊 {count_text}"
        else:
            button_text = f"{indicator} {formatted_name}\n📊 No data"
        
        return button_text
    
    async def get_total_reach(self, selected_channels: List[str], all_channels: List[Dict]) -> int:
        """Calculate total reach for selected channels with live counts"""
        total = 0
        for channel in all_channels:
            channel_id = channel.get('channel_id')
            if channel_id in selected_channels:
                total += channel.get('live_subscribers', channel.get('subscribers', 0))
        return total
    
    async def refresh_all_channel_stats(self):
        """Refresh statistics for all channels"""
        try:
            channels = await self.db.get_channels(active_only=True)
            updated_count = 0
            
            for channel in channels:
                channel_id = channel.get('telegram_channel_id') or channel.get('channel_id')
                old_count = channel.get('subscribers', 0)
                new_count = await self.get_live_subscriber_count(channel_id)
                
                if new_count != old_count:
                    await self._update_database_count(channel_id, new_count)
                    updated_count += 1
                    logger.info(f"Updated {channel.get('name')}: {old_count} → {new_count}")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            
            logger.info(f"Refreshed stats for {len(channels)} channels, {updated_count} updated")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error refreshing channel stats: {e}")
            return 0
    
    def clear_cache(self):
        """Clear the subscriber count cache"""
        self.cache.clear()
        logger.info("Subscriber count cache cleared")
    
    async def get_channel_analytics(self, channel_id: str) -> Dict:
        """Get comprehensive channel analytics"""
        try:
            live_count = await self.get_live_subscriber_count(channel_id)
            
            # Get historical data from database
            channels = await self.db.get_channels(active_only=True)
            channel_data = None
            for ch in channels:
                if (ch.get('channel_id') == channel_id or 
                    ch.get('telegram_channel_id') == channel_id):
                    channel_data = ch
                    break
            
            if not channel_data:
                return {'error': 'Channel not found'}
            
            db_count = channel_data.get('subscribers', 0)
            growth = live_count - db_count
            growth_percent = (growth / db_count * 100) if db_count > 0 else 0
            
            return {
                'name': channel_data.get('name'),
                'live_subscribers': live_count,
                'database_subscribers': db_count,
                'growth': growth,
                'growth_percent': growth_percent,
                'active_estimate': int(live_count * 0.45),
                'category': channel_data.get('category', 'general'),
                'last_updated': channel_data.get('last_updated'),
                'base_price': channel_data.get('base_price_usd', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting channel analytics: {e}")
            return {'error': str(e)}