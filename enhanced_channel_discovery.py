"""
Enhanced Channel Discovery Utilities for I3lani Bot
Provides comprehensive tools for discovering and managing Telegram channels
"""

import logging
import asyncio
from typing import List, Dict, Set
from aiogram import Bot
from database import db

logger = logging.getLogger(__name__)

class EnhancedChannelDiscovery:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = db
    
    async def discover_channels_by_keywords(self, keywords: List[str]) -> Dict[str, any]:
        """Discover channels using keyword-based search patterns"""
        try:
            discovered_channels = []
            
            # Generate potential usernames based on keywords
            potential_usernames = self._generate_keyword_combinations(keywords)
            
            for username in potential_usernames:
                try:
                    # Check if channel exists and bot is admin
                    chat = await self.bot.get_chat(username)
                    bot_member = await self.bot.get_chat_member(chat.id, self.bot.id)
                    
                    if bot_member.status == 'administrator' and bot_member.can_post_messages:
                        # Get detailed channel info
                        member_count = await self.bot.get_chat_member_count(chat.id)
                        
                        discovered_channels.append({
                            'username': username,
                            'name': chat.title,
                            'subscribers': member_count,
                            'description': chat.description or "No description",
                            'type': chat.type
                        })
                        
                        logger.info(f"🎯 Keyword discovery found: {chat.title} ({username})")
                        
                except Exception as e:
                    logger.debug(f"Channel {username} not accessible: {e}")
                
                # Small delay to prevent rate limiting
                await asyncio.sleep(0.05)
            
            return {
                'success': True,
                'discovered_channels': discovered_channels,
                'total_checked': len(potential_usernames)
            }
            
        except Exception as e:
            logger.error(f"Keyword discovery error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_keyword_combinations(self, keywords: List[str]) -> List[str]:
        """Generate potential channel usernames from keywords"""
        usernames = set()
        
        # Basic patterns
        for keyword in keywords:
            keyword = keyword.lower().strip()
            if keyword:
                usernames.add(f"@{keyword}")
                usernames.add(f"@{keyword}_channel")
                usernames.add(f"@{keyword}_official")
                usernames.add(f"@{keyword}_news")
                usernames.add(f"@{keyword}_shop")
                usernames.add(f"@official_{keyword}")
                usernames.add(f"@the_{keyword}")
        
        # Combination patterns
        if len(keywords) >= 2:
            for i, keyword1 in enumerate(keywords):
                for keyword2 in keywords[i+1:]:
                    combo = f"{keyword1.lower()}_{keyword2.lower()}"
                    usernames.add(f"@{combo}")
                    usernames.add(f"@{combo}_channel")
        
        # Remove invalid usernames (too long, invalid characters)
        valid_usernames = []
        for username in usernames:
            if len(username) <= 32 and username.replace('@', '').replace('_', '').isalnum():
                valid_usernames.append(username)
        
        return valid_usernames[:200]  # Limit to prevent excessive API calls
    
    async def verify_admin_status_bulk(self, usernames: List[str]) -> Dict[str, Dict]:
        """Verify bot admin status for multiple channels"""
        results = {}
        
        for username in usernames:
            try:
                if not username.startswith('@'):
                    username = f"@{username}"
                
                chat = await self.bot.get_chat(username)
                bot_member = await self.bot.get_chat_member(chat.id, self.bot.id)
                
                results[username] = {
                    'exists': True,
                    'is_admin': bot_member.status == 'administrator',
                    'can_post': getattr(bot_member, 'can_post_messages', False),
                    'title': chat.title,
                    'type': chat.type
                }
                
            except Exception as e:
                results[username] = {
                    'exists': False,
                    'error': str(e)
                }
            
            await asyncio.sleep(0.1)  # Rate limiting
        
        return results
    
    async def smart_channel_discovery(self, base_patterns: List[str] = None) -> Dict[str, any]:
        """Smart discovery using multiple strategies"""
        if not base_patterns:
            base_patterns = ["i3lani", "shop", "smart", "deals", "news", "tech", "business"]
        
        try:
            total_results = {
                'total_scanned': 0,
                'newly_discovered': 0,
                'already_known': 0,
                'failed_attempts': 0,
                'discovered_channels': []
            }
            
            # Get existing channels to avoid duplicates
            existing_channels = await self.db.get_channels(active_only=False)
            existing_usernames = {ch.get('telegram_channel_id') for ch in existing_channels}
            
            # Strategy 1: Keyword-based discovery
            keyword_results = await self.discover_channels_by_keywords(base_patterns)
            if keyword_results['success']:
                for channel in keyword_results['discovered_channels']:
                    username = channel['username']
                    if username not in existing_usernames:
                        # Add to database using existing method from channel_manager
                        from channel_manager import channel_manager
                        if channel_manager:
                            success = await channel_manager.discover_channel_by_username(username)
                            if success:
                                total_results['newly_discovered'] += 1
                                total_results['discovered_channels'].append(channel)
                    else:
                        total_results['already_known'] += 1
                
                total_results['total_scanned'] += keyword_results['total_checked']
            
            # Strategy 2: Pattern-based discovery (existing method)
            from channel_manager import channel_manager
            if channel_manager:
                pattern_results = await channel_manager._discover_channels_by_patterns()
                # Note: This method already handles database addition
            
            logger.info(f"🎯 Smart discovery complete: {total_results['newly_discovered']} new channels found")
            return total_results
            
        except Exception as e:
            logger.error(f"Smart discovery error: {e}")
            return {'error': str(e)}

# Global instance (will be initialized in main.py)
enhanced_discovery = None

def init_enhanced_discovery(bot: Bot):
    """Initialize enhanced discovery system"""
    global enhanced_discovery
    enhanced_discovery = EnhancedChannelDiscovery(bot)
    logger.info("✅ Enhanced channel discovery system initialized")
    return enhanced_discovery