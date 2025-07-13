"""
Multilingual Menu Integration System for I3lani Bot
Integrates main menu buttons, bot commands, and admin panel with language system
"""

import asyncio
import logging
from typing import Dict, List, Optional
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from database import db, get_user_language
from languages import get_text, LANGUAGES

logger = logging.getLogger(__name__)

class MultilingualMenuSystem:
    """Manages multilingual menu integration"""
    
    def __init__(self, bot):
        self.bot = bot
        self.default_language = 'en'
        self.supported_languages = ['en', 'ar', 'ru']
        
    def get_bot_commands_for_language(self, language: str) -> List[BotCommand]:
        """Get bot commands localized for specific language"""
        commands = {
            'en': [
                BotCommand(command="start", description="🚀 Start the bot"),
                BotCommand(command="dashboard", description="📊 My Ads Dashboard"),
                BotCommand(command="mystats", description="📈 My Statistics"),
                BotCommand(command="referral", description="🎯 Referral System"),
                BotCommand(command="support", description="💬 Get Support"),
                BotCommand(command="help", description="❓ Help & Guide"),
                BotCommand(command="admin", description="⚙️ Admin Panel"),
                BotCommand(command="health", description="🏥 System Health"),
                BotCommand(command="troubleshoot", description="🔧 Troubleshooting"),
                BotCommand(command="report_issue", description="🚨 Report Issue")
            ],
            'ar': [
                BotCommand(command="start", description="🚀 بدء تشغيل البوت"),
                BotCommand(command="dashboard", description="📊 لوحة إعلاناتي"),
                BotCommand(command="mystats", description="📈 إحصائياتي"),
                BotCommand(command="referral", description="🎯 نظام الإحالة"),
                BotCommand(command="support", description="💬 الحصول على الدعم"),
                BotCommand(command="help", description="❓ المساعدة والدليل"),
                BotCommand(command="admin", description="⚙️ لوحة الإدارة"),
                BotCommand(command="health", description="🏥 صحة النظام"),
                BotCommand(command="troubleshoot", description="🔧 استكشاف الأخطاء"),
                BotCommand(command="report_issue", description="🚨 الإبلاغ عن مشكلة")
            ],
            'ru': [
                BotCommand(command="start", description="🚀 Запустить бота"),
                BotCommand(command="dashboard", description="📊 Панель моих объявлений"),
                BotCommand(command="mystats", description="📈 Моя статистика"),
                BotCommand(command="referral", description="🎯 Реферальная система"),
                BotCommand(command="support", description="💬 Получить поддержку"),
                BotCommand(command="help", description="❓ Помощь и руководство"),
                BotCommand(command="admin", description="⚙️ Панель администратора"),
                BotCommand(command="health", description="🏥 Здоровье системы"),
                BotCommand(command="troubleshoot", description="🔧 Устранение неполадок"),
                BotCommand(command="report_issue", description="🚨 Сообщить о проблеме")
            ]
        }
        
        return commands.get(language, commands['en'])
    
    def get_main_menu_buttons_for_language(self, language: str) -> List[List[InlineKeyboardButton]]:
        """Get main menu buttons localized for specific language"""
        
        # Get localized text from languages.py
        create_ad_text = get_text(language, 'create_ad')
        my_ads_text = get_text(language, 'my_ads')
        pricing_text = get_text(language, 'pricing')
        share_earn_text = get_text(language, 'share_earn')
        settings_text = get_text(language, 'settings')
        help_text = get_text(language, 'help')
        
        # Create buttons with proper localization
        buttons = [
            [InlineKeyboardButton(text=create_ad_text, callback_data="create_ad")],
            [InlineKeyboardButton(text=my_ads_text, callback_data="my_ads")],
            [InlineKeyboardButton(text=pricing_text, callback_data="pricing")],
            [InlineKeyboardButton(text=share_earn_text, callback_data="share_earn")],
            [InlineKeyboardButton(text=settings_text, callback_data="settings")],
            [InlineKeyboardButton(text=help_text, callback_data="help")]
        ]
        
        return buttons
    
    def get_admin_panel_buttons_for_language(self, language: str) -> List[List[InlineKeyboardButton]]:
        """Get admin panel buttons localized for specific language"""
        
        admin_buttons = {
            'en': [
                [InlineKeyboardButton(text="📊 Statistics", callback_data="admin_statistics")],
                [InlineKeyboardButton(text="📢 Channel Management", callback_data="admin_channels")],
                [InlineKeyboardButton(text="💰 Price Management", callback_data="admin_packages")],
                [InlineKeyboardButton(text="📝 Subscription Management", callback_data="admin_subscriptions")],
                [InlineKeyboardButton(text="👥 User Management", callback_data="admin_users")],
                [InlineKeyboardButton(text="🔧 Bot Control", callback_data="admin_bot_control")],
                [InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_refresh")]
            ],
            'ar': [
                [InlineKeyboardButton(text="📊 الإحصائيات", callback_data="admin_statistics")],
                [InlineKeyboardButton(text="📢 إدارة القنوات", callback_data="admin_channels")],
                [InlineKeyboardButton(text="💰 إدارة الأسعار", callback_data="admin_packages")],
                [InlineKeyboardButton(text="📝 إدارة الاشتراكات", callback_data="admin_subscriptions")],
                [InlineKeyboardButton(text="👥 إدارة المستخدمين", callback_data="admin_users")],
                [InlineKeyboardButton(text="🔧 التحكم بالبوت", callback_data="admin_bot_control")],
                [InlineKeyboardButton(text="🔄 تحديث", callback_data="admin_refresh")]
            ],
            'ru': [
                [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_statistics")],
                [InlineKeyboardButton(text="📢 Управление каналами", callback_data="admin_channels")],
                [InlineKeyboardButton(text="💰 Управление ценами", callback_data="admin_packages")],
                [InlineKeyboardButton(text="📝 Управление подписками", callback_data="admin_subscriptions")],
                [InlineKeyboardButton(text="👥 Управление пользователями", callback_data="admin_users")],
                [InlineKeyboardButton(text="🔧 Управление ботом", callback_data="admin_bot_control")],
                [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh")]
            ]
        }
        
        return admin_buttons.get(language, admin_buttons['en'])
    
    async def set_multilingual_bot_commands(self):
        """Set bot commands for all supported languages"""
        try:
            # Set commands for each language
            for language in self.supported_languages:
                commands = self.get_bot_commands_for_language(language)
                
                # Set commands for specific language
                await self.bot.set_my_commands(
                    commands=commands,
                    language_code=language
                )
                
                logger.info(f"✅ Set {len(commands)} bot commands for language: {language}")
            
            # Set default commands (English)
            default_commands = self.get_bot_commands_for_language('en')
            await self.bot.set_my_commands(commands=default_commands)
            
            logger.info("✅ Multilingual bot commands set successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting multilingual bot commands: {e}")
            return False
    
    async def create_multilingual_main_menu(self, user_id: int) -> InlineKeyboardMarkup:
        """Create main menu with user's language"""
        try:
            # Get user's language
            user_language = await self.get_user_language_async(user_id)
            
            # Get localized buttons
            buttons = self.get_main_menu_buttons_for_language(user_language)
            
            return InlineKeyboardMarkup(inline_keyboard=buttons)
            
        except Exception as e:
            logger.error(f"❌ Error creating multilingual main menu: {e}")
            # Fallback to English
            buttons = self.get_main_menu_buttons_for_language('en')
            return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    async def create_multilingual_admin_panel(self, user_id: int) -> InlineKeyboardMarkup:
        """Create admin panel with user's language"""
        try:
            # Get user's language
            user_language = await self.get_user_language_async(user_id)
            
            # Get localized buttons
            buttons = self.get_admin_panel_buttons_for_language(user_language)
            
            return InlineKeyboardMarkup(inline_keyboard=buttons)
            
        except Exception as e:
            logger.error(f"❌ Error creating multilingual admin panel: {e}")
            # Fallback to English
            buttons = self.get_admin_panel_buttons_for_language('en')
            return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    async def get_user_language_async(self, user_id: int) -> str:
        """Get user language asynchronously"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute(
                "SELECT language FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            result = await cursor.fetchone()
            await connection.close()
            
            if result:
                return result[0]
            return self.default_language
            
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return self.default_language
    
    async def update_user_interface_language(self, user_id: int, new_language: str):
        """Update user interface language and refresh menus"""
        try:
            # Update user language in database
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute(
                "UPDATE users SET language = ? WHERE user_id = ?",
                (new_language, user_id)
            )
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Updated interface language to {new_language} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating interface language: {e}")
            return False
    
    def get_localized_text(self, language: str, key: str) -> str:
        """Get localized text with fallback"""
        try:
            return get_text(language, key)
        except Exception as e:
            logger.error(f"Error getting localized text {key} for {language}: {e}")
            return get_text('en', key)  # Fallback to English

# Global instance
multilingual_menu_system = None

def get_multilingual_menu_system(bot):
    """Get or create multilingual menu system instance"""
    global multilingual_menu_system
    if multilingual_menu_system is None:
        multilingual_menu_system = MultilingualMenuSystem(bot)
    return multilingual_menu_system

async def initialize_multilingual_menus(bot):
    """Initialize multilingual menu system"""
    menu_system = get_multilingual_menu_system(bot)
    success = await menu_system.set_multilingual_bot_commands()
    
    if success:
        logger.info("✅ Multilingual menu system initialized successfully")
    else:
        logger.error("❌ Failed to initialize multilingual menu system")
    
    return menu_system