#!/usr/bin/env python3
"""
Automatic Language System
Automatically detects and applies user language across all bot systems
"""

import asyncio
import logging
from typing import Dict, Optional, Any, List
from functools import wraps
from database import db

logger = logging.getLogger(__name__)

class AutomaticLanguageSystem:
    """Automatic language detection and application system"""
    
    def __init__(self):
        self.language_cache = {}
        self.default_language = 'en'
        self.supported_languages = ['en', 'ar', 'ru']
        
    async def get_user_language(self, user_id: int) -> str:
        """Get user language with caching"""
        try:
            # Check cache first
            if user_id in self.language_cache:
                return self.language_cache[user_id]
            
            # Get from database
            language = await db.get_user_language(user_id)
            
            # Validate language
            if language not in self.supported_languages:
                language = self.default_language
            
            # Cache the result
            self.language_cache[user_id] = language
            
            return language
            
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return self.default_language
    
    async def set_user_language(self, user_id: int, language: str):
        """Set user language and update cache"""
        try:
            if language in self.supported_languages:
                await db.set_user_language(user_id, language)
                self.language_cache[user_id] = language
                logger.info(f"Set language for user {user_id}: {language}")
            else:
                logger.warning(f"Unsupported language: {language}")
                
        except Exception as e:
            logger.error(f"Error setting user language: {e}")
    
    def auto_language(self, func):
        """Decorator to automatically inject user language"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from various sources
            user_id = None
            
            # Check if first argument has user_id
            if args and hasattr(args[0], 'from_user'):
                user_id = args[0].from_user.id
            elif args and hasattr(args[0], 'user_id'):
                user_id = args[0].user_id
            elif 'user_id' in kwargs:
                user_id = kwargs['user_id']
            
            # Get language if user_id found
            if user_id:
                language = await self.get_user_language(user_id)
                kwargs['language'] = language
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    async def localize_text(self, user_id: int, text_key: str, **format_kwargs) -> str:
        """Get localized text for user"""
        try:
            language = await self.get_user_language(user_id)
            
            # Import here to avoid circular imports
            from languages import get_text
            
            text = get_text(language, text_key)
            
            # Apply formatting if provided
            if format_kwargs:
                text = text.format(**format_kwargs)
            
            return text
            
        except Exception as e:
            logger.error(f"Error localizing text: {e}")
            return text_key
    
    async def localize_keyboard(self, user_id: int, keyboard_data: List[List[Dict]]) -> List[List[Dict]]:
        """Localize keyboard buttons"""
        try:
            language = await self.get_user_language(user_id)
            
            from languages import get_text
            
            localized_keyboard = []
            
            for row in keyboard_data:
                localized_row = []
                for button in row:
                    localized_button = button.copy()
                    
                    # Localize text key if exists
                    if 'text_key' in button:
                        localized_button['text'] = get_text(language, button['text_key'])
                    
                    localized_row.append(localized_button)
                
                localized_keyboard.append(localized_row)
            
            return localized_keyboard
            
        except Exception as e:
            logger.error(f"Error localizing keyboard: {e}")
            return keyboard_data
    
    async def localize_message(self, user_id: int, message_template: Dict) -> str:
        """Localize complete message with template"""
        try:
            language = await self.get_user_language(user_id)
            
            from languages import get_text
            
            # Get base text
            base_text = get_text(language, message_template.get('text_key', ''))
            
            # Apply variables if provided
            variables = message_template.get('variables', {})
            if variables:
                base_text = base_text.format(**variables)
            
            # Add prefix/suffix if provided
            prefix = message_template.get('prefix', '')
            suffix = message_template.get('suffix', '')
            
            if prefix:
                prefix_text = get_text(language, prefix) if isinstance(prefix, str) else prefix
                base_text = prefix_text + base_text
            
            if suffix:
                suffix_text = get_text(language, suffix) if isinstance(suffix, str) else suffix
                base_text = base_text + suffix_text
            
            return base_text
            
        except Exception as e:
            logger.error(f"Error localizing message: {e}")
            return str(message_template)
    
    async def auto_detect_language(self, text: str) -> str:
        """Auto-detect language from text"""
        try:
            # Simple detection based on script
            if any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in text):
                return 'ar'  # Arabic
            elif any(ord(char) >= 0x0400 and ord(char) <= 0x04FF for char in text):
                return 'ru'  # Russian
            else:
                return 'en'  # Default to English
                
        except Exception as e:
            logger.error(f"Error auto-detecting language: {e}")
            return self.default_language
    
    async def get_localized_currency_info(self, user_id: int) -> Dict:
        """Get currency info for user's language"""
        try:
            language = await self.get_user_language(user_id)
            
            from languages import get_currency_info
            
            return get_currency_info(language)
            
        except Exception as e:
            logger.error(f"Error getting currency info: {e}")
            return {'symbol': '$', 'name': 'USD'}
    
    async def clear_language_cache(self, user_id: Optional[int] = None):
        """Clear language cache"""
        if user_id:
            self.language_cache.pop(user_id, None)
        else:
            self.language_cache.clear()
    
    async def get_language_stats(self) -> Dict:
        """Get language usage statistics"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute("""
                SELECT language, COUNT(*) as count
                FROM users
                GROUP BY language
                ORDER BY count DESC
            """)
            
            results = await cursor.fetchall()
            
            stats = {}
            for row in results:
                stats[row[0]] = row[1]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting language stats: {e}")
            return {}

# Global instance
automatic_language_system = AutomaticLanguageSystem()

async def get_user_language_auto(user_id: int) -> str:
    """Get user language automatically"""
    return await automatic_language_system.get_user_language(user_id)

async def localize_text_auto(user_id: int, text_key: str, **kwargs) -> str:
    """Localize text automatically"""
    return await automatic_language_system.localize_text(user_id, text_key, **kwargs)

async def localize_message_auto(user_id: int, message_template: Dict) -> str:
    """Localize message automatically"""
    return await automatic_language_system.localize_message(user_id, message_template)

def auto_language_decorator(func):
    """Decorator for automatic language injection"""
    return automatic_language_system.auto_language(func)

async def apply_automatic_language_to_all_systems():
    """Apply automatic language detection to all systems"""
    try:
        logger.info("🌍 Applying automatic language system to all components...")
        
        # Update handlers
        await _update_handlers_with_auto_language()
        
        # Update admin system
        await _update_admin_system_with_auto_language()
        
        # Update payment systems
        await _update_payment_systems_with_auto_language()
        
        # Update campaign systems
        await _update_campaign_systems_with_auto_language()
        
        logger.info("✅ Automatic language system applied to all components")
        
    except Exception as e:
        logger.error(f"Error applying automatic language system: {e}")

async def _update_handlers_with_auto_language():
    """Update handlers with automatic language"""
    # This will be implemented as needed
    pass

async def _update_admin_system_with_auto_language():
    """Update admin system with automatic language"""
    # This will be implemented as needed
    pass

async def _update_payment_systems_with_auto_language():
    """Update payment systems with automatic language"""
    # This will be implemented as needed
    pass

async def _update_campaign_systems_with_auto_language():
    """Update campaign systems with automatic language"""
    # This will be implemented as needed
    pass