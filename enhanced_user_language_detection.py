#!/usr/bin/env python3
"""
Enhanced User Language Detection
Replaces manual language selection with automatic detection
"""

import logging
from typing import Dict, Optional, Any
from automatic_language_system import automatic_language_system, get_user_language_auto

logger = logging.getLogger(__name__)

class EnhancedUserLanguageDetection:
    """Enhanced language detection for seamless user experience"""
    
    def __init__(self):
        self.detection_cache = {}
        
    async def detect_and_set_language(self, user_id: int, text: str = None, context: Dict = None) -> str:
        """Detect language and set it for user"""
        try:
            # Check if user already has a language preference
            current_language = await get_user_language_auto(user_id)
            
            # If text provided, try to detect language
            if text:
                detected_language = await automatic_language_system.auto_detect_language(text)
                
                # If detected language is different and user hasn't set preference
                if detected_language != current_language and current_language == 'en':
                    await automatic_language_system.set_user_language(user_id, detected_language)
                    logger.info(f"🌍 Auto-detected language {detected_language} for user {user_id}")
                    return detected_language
            
            return current_language
            
        except Exception as e:
            logger.error(f"Error in language detection: {e}")
            return 'en'
    
    async def get_user_interface_language(self, user_id: int) -> str:
        """Get interface language for user"""
        return await get_user_language_auto(user_id)
    
    async def update_user_language_preference(self, user_id: int, language: str) -> bool:
        """Update user language preference"""
        try:
            await automatic_language_system.set_user_language(user_id, language)
            
            # Clear cache to force refresh
            await automatic_language_system.clear_language_cache(user_id)
            
            logger.info(f"🔄 Updated language preference for user {user_id}: {language}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating language preference: {e}")
            return False
    
    async def get_localized_response(self, user_id: int, message_key: str, **kwargs) -> str:
        """Get localized response for user"""
        return await automatic_language_system.localize_text(user_id, message_key, **kwargs)
    
    async def create_localized_keyboard(self, user_id: int, keyboard_config: Dict) -> Dict:
        """Create localized keyboard"""
        return await automatic_language_system.localize_keyboard(user_id, keyboard_config)

# Global instance
enhanced_language_detection = EnhancedUserLanguageDetection()

async def get_enhanced_user_language(user_id: int, text: str = None) -> str:
    """Get enhanced user language with detection"""
    return await enhanced_language_detection.detect_and_set_language(user_id, text)

async def get_localized_text(user_id: int, key: str, **kwargs) -> str:
    """Get localized text for user"""
    return await enhanced_language_detection.get_localized_response(user_id, key, **kwargs)