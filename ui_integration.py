"""
UI Integration Helper for I3lani Bot
Integrates UI Control System with existing handlers
"""

import logging
from typing import Dict, Any
from ui_control_system import ui_control
from languages import get_text as fallback_get_text

logger = logging.getLogger(__name__)

async def get_ui_text(category: str, key: str, language: str = 'en', fallback_key: str = None) -> str:
    """
    Get UI text with fallback to original language system
    
    Args:
        category: UI category (e.g., 'main_menu_buttons', 'welcome_messages')
        key: Text key within the category
        language: Language code ('en', 'ar', 'ru')
        fallback_key: Fallback key for original language system
    
    Returns:
        Customized text or fallback text
    """
    try:
        # Try to get customized text first
        custom_text = await ui_control.get_text(category, key, language)
        
        # If we get a meaningful result, return it
        if custom_text and not custom_text.startswith(f"{category}_{key}"):
            return custom_text
        
        # Fall back to original language system if available
        if fallback_key:
            return fallback_get_text(language, fallback_key)
        
        # Last resort: return the custom text (which might be a default)
        return custom_text
        
    except Exception as e:
        logger.error(f"Error getting UI text: {e}")
        # Emergency fallback
        if fallback_key:
            return fallback_get_text(language, fallback_key)
        return f"{category}_{key}"

# Text mapping for easy migration
UI_TEXT_MAPPING = {
    # Main menu buttons
    'create_ad': ('main_menu_buttons', 'create_ad', 'create_ad'),
    'channel_partners': ('main_menu_buttons', 'channel_partners', 'channel_partners'),
    'share_win': ('main_menu_buttons', 'share_win', 'share_win'),
    'gaming_hub': ('main_menu_buttons', 'gaming_hub', 'gaming_hub'),
    'leaderboard': ('main_menu_buttons', 'leaderboard', 'leaderboard'),
    'language_settings': ('main_menu_buttons', 'language_settings', 'language'),
    'contact_support': ('main_menu_buttons', 'contact_support', 'contact_support'),
    
    # Welcome messages
    'welcome': ('welcome_messages', 'new_user_welcome', 'welcome'),
    'welcome_back': ('welcome_messages', 'returning_user', 'welcome_back'),
    
    # Navigation buttons
    'back_to_main': ('navigation_buttons', 'back_to_main', 'back_to_main'),
    'continue': ('navigation_buttons', 'continue', 'continue'),
    'cancel': ('navigation_buttons', 'cancel', 'cancel'),
    'try_again': ('navigation_buttons', 'try_again', 'try_again'),
    
    # Ad creation
    'send_ad_content': ('ad_creation', 'upload_content', 'send_ad_content'),
    'select_channels': ('ad_creation', 'select_channels', 'select_channels'),
    'content_received': ('ad_creation', 'content_received', 'content_received'),
    
    # Payment messages
    'select_payment_method': ('payment_messages', 'select_payment_method', 'select_payment_method'),
    'payment_processing': ('payment_messages', 'payment_processing', 'payment_processing'),
    'payment_successful': ('payment_messages', 'payment_successful', 'payment_successful'),
    
    # Error messages
    'error_occurred': ('error_messages', 'general_error', 'error_occurred'),
    'network_error': ('error_messages', 'network_error', 'network_error'),
    'payment_failed': ('error_messages', 'payment_failed', 'payment_failed'),
    
    # Success messages
    'ad_created': ('success_messages', 'ad_created', 'ad_created'),
    'settings_saved': ('success_messages', 'settings_saved', 'settings_saved'),
    'language_changed': ('success_messages', 'language_changed', 'language_changed'),
}

async def get_mapped_text(text_key: str, language: str = 'en') -> str:
    """
    Get text using the mapping system for easy migration
    
    Args:
        text_key: Original text key from language system
        language: Language code
    
    Returns:
        Customized or fallback text
    """
    if text_key in UI_TEXT_MAPPING:
        category, key, fallback_key = UI_TEXT_MAPPING[text_key]
        return await get_ui_text(category, key, language, fallback_key)
    else:
        # If not mapped, use original system
        return fallback_get_text(language, text_key)

# Helper functions for specific UI elements
async def get_button_text(button_key: str, language: str = 'en') -> str:
    """Get customized button text"""
    return await get_mapped_text(button_key, language)

async def get_message_text(message_key: str, language: str = 'en') -> str:
    """Get customized message text"""
    return await get_mapped_text(message_key, language)

async def get_error_text(error_key: str, language: str = 'en') -> str:
    """Get customized error message text"""
    return await get_mapped_text(error_key, language)

async def get_success_text(success_key: str, language: str = 'en') -> str:
    """Get customized success message text"""
    return await get_mapped_text(success_key, language)