"""
Comprehensive Translation Enhancement System for I3lani Bot
Provides automatic translation support across all bot interactions
"""

import logging
from typing import Dict, Any, Optional, Union
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from languages import get_text, get_language_info, DEFAULT_LANGUAGE, is_rtl_language

logger = logging.getLogger(__name__)

class AutoTranslationSystem:
    """
    Automatic translation system that enhances all bot interactions
    with seamless multilingual support
    """
    
    def __init__(self):
        self.supported_languages = ['en', 'ar', 'ru']
        logger.info("🌍 Auto-translation system initialized")
    
    async def get_user_language(self, user_id: int) -> str:
        """Get user language with fallback"""
        try:
            from database import db
            user = await db.get_user(user_id)
            if user and user.get('language'):
                return user['language']
        except Exception as e:
            logger.debug(f"Could not get user language: {e}")
        
        return DEFAULT_LANGUAGE
    
    def create_language_keyboard(self, current_language: str = None) -> InlineKeyboardMarkup:
        """Create language selection keyboard"""
        from languages import LANGUAGES
        
        buttons = []
        for lang_code, lang_info in LANGUAGES.items():
            button_text = f"{lang_info['flag']} {lang_info['name']}"
            if current_language == lang_code:
                button_text += " ✅"
            
            buttons.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"lang_{lang_code}"
            )])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def translate_text(self, text: str, target_language: str, context: str = None) -> str:
        """Translate text with context awareness"""
        # This is a simplified version - in a full implementation,
        # you would use a translation service or predefined mappings
        
        if target_language == 'en':
            return text
        
        # For now, return the text as-is since our translations
        # are handled by the get_text() function with predefined keys
        return text
    
    def format_message_rtl(self, text: str, language: str) -> str:
        """Format message for RTL languages"""
        if is_rtl_language(language):
            # Add RTL formatting if needed
            return f"‏{text}"
        return text
    
    async def send_translated_message(
        self, 
        chat_id: int, 
        message_key: str, 
        user_language: str = None,
        keyboard: InlineKeyboardMarkup = None,
        **format_kwargs
    ) -> str:
        """Send a message with automatic translation"""
        
        if not user_language:
            user_language = DEFAULT_LANGUAGE
        
        # Get translated text
        text = get_text(user_language, message_key, **format_kwargs)
        
        # Format for RTL if needed
        text = self.format_message_rtl(text, user_language)
        
        return text
    
    def translate_keyboard_buttons(
        self, 
        keyboard: InlineKeyboardMarkup, 
        language: str
    ) -> InlineKeyboardMarkup:
        """Translate keyboard button texts"""
        
        if language == DEFAULT_LANGUAGE:
            return keyboard
        
        # Translation mapping for common button texts
        button_translations = {
            'en': {
                'back': '⬅️ Back',
                'continue': '➡️ Continue',
                'cancel': '❌ Cancel',
                'confirm': '✅ Confirm',
                'main_menu': '🏠 Main Menu',
                'try_again': '🔄 Try Again',
                'contact_support': '📞 Contact Support'
            },
            'ar': {
                'back': '⬅️ رجوع',
                'continue': '➡️ متابعة',
                'cancel': '❌ إلغاء',
                'confirm': '✅ تأكيد',
                'main_menu': '🏠 القائمة الرئيسية',
                'try_again': '🔄 حاول مرة أخرى',
                'contact_support': '📞 اتصل بالدعم'
            },
            'ru': {
                'back': '⬅️ Назад',
                'continue': '➡️ Продолжить',
                'cancel': '❌ Отмена',
                'confirm': '✅ Подтвердить',
                'main_menu': '🏠 Главное меню',
                'try_again': '🔄 Попробовать снова',
                'contact_support': '📞 Связаться с поддержкой'
            }
        }
        
        translations = button_translations.get(language, button_translations['en'])
        
        # Create new keyboard with translated buttons
        new_keyboard = []
        
        for row in keyboard.inline_keyboard:
            new_row = []
            for button in row:
                # Try to translate button text
                original_text = button.text
                translated_text = original_text
                
                # Look for translation keys
                for key, translation in translations.items():
                    if key.lower() in original_text.lower():
                        translated_text = translation
                        break
                
                new_button = InlineKeyboardButton(
                    text=translated_text,
                    callback_data=button.callback_data,
                    url=button.url,
                    web_app=button.web_app
                )
                new_row.append(new_button)
            
            new_keyboard.append(new_row)
        
        return InlineKeyboardMarkup(inline_keyboard=new_keyboard)
    
    async def handle_language_change(
        self, 
        callback_query: CallbackQuery, 
        new_language: str
    ) -> bool:
        """Handle language change with comprehensive UI update"""
        try:
            user_id = callback_query.from_user.id
            
            # Update language in database
            from database import db
            success = await db.set_user_language(user_id, new_language)
            
            if success:
                # Send confirmation in new language
                confirmation_text = get_text(new_language, 'language_changed')
                
                await callback_query.message.edit_text(
                    confirmation_text,
                    reply_markup=None
                )
                
                # Small delay then show main menu in new language
                import asyncio
                await asyncio.sleep(1)
                
                # Show main menu in new language
                await self.show_main_menu_translated(callback_query, new_language)
                
                logger.info(f"✅ Language changed to {new_language} for user {user_id}")
                return True
            
        except Exception as e:
            logger.error(f"Error changing language: {e}")
            
        return False
    
    async def show_main_menu_translated(
        self, 
        callback_query: CallbackQuery, 
        language: str
    ):
        """Show main menu with full translation"""
        from enhanced_ui import create_main_menu_with_web3_ui
        
        try:
            # Get translated main menu
            main_menu_text = get_text(language, 'main_menu')
            
            # Create main menu keyboard with translations
            keyboard = create_main_menu_with_web3_ui(language)
            
            await callback_query.message.edit_text(
                main_menu_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error showing translated main menu: {e}")
            # Fallback to English
            fallback_text = get_text('en', 'main_menu')
            fallback_keyboard = create_main_menu_with_web3_ui('en')
            
            await callback_query.message.edit_text(
                fallback_text,
                reply_markup=fallback_keyboard,
                parse_mode='HTML'
            )

# Global instance
auto_translation = AutoTranslationSystem()

def init_translation_system():
    """Initialize the translation system"""
    global auto_translation
    auto_translation = AutoTranslationSystem()
    logger.info("🌍 Comprehensive translation system initialized")
    return auto_translation

# Helper functions for easy use in handlers
async def get_user_lang(user_id: int) -> str:
    """Quick helper to get user language"""
    return await auto_translation.get_user_language(user_id)

def t(key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """Quick translation helper"""
    return get_text(language, key, **kwargs)

async def send_translated(
    message_or_query: Union[Message, CallbackQuery],
    key: str,
    user_id: int = None,
    **kwargs
) -> str:
    """Send translated message helper"""
    if user_id is None:
        user_id = message_or_query.from_user.id
    
    language = await get_user_lang(user_id)
    text = get_text(language, key, **kwargs)
    
    if isinstance(message_or_query, Message):
        await message_or_query.answer(text, parse_mode='HTML')
    else:
        await message_or_query.message.edit_text(text, parse_mode='HTML')
    
    return text