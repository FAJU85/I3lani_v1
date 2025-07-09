"""
Modern Inline Keyboard System for I3lani Bot
Psychologically calming and safe user experience with modern aesthetics
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Optional, Tuple
import json
from logger import log_success, log_error, log_info, StepNames

class ModernKeyboard:
    """
    Modern inline keyboard with psychologically calming design
    
    Design Principles:
    - Soft, clean aesthetics with rounded corners
    - Calming color palette (#F4F7FB background, #FFFFFF keys)
    - Intuitive layout with ample spacing
    - Clear visual hierarchy and readability
    - Emotionally comforting user experience
    """
    
    def __init__(self, theme: str = "light"):
        self.theme = theme
        self.colors = self._get_color_palette(theme)
        
    def _get_color_palette(self, theme: str) -> Dict[str, str]:
        """Get color palette based on theme"""
        if theme == "dark":
            return {
                "background": "#1E1E2A",
                "key_default": "#2C2F3A",
                "key_border": "#3A3F4A",
                "font_color": "#F5F5F5",
                "primary_action": "#3B82F6",
                "pressed_overlay": "#404654",
                "shadow": "rgba(0,0,0,0.15)"
            }
        else:  # light theme
            return {
                "background": "#F4F7FB",
                "key_default": "#FFFFFF",
                "key_border": "#DDE3EB",
                "font_color": "#1A1A1A",
                "primary_action": "#2563EB",
                "pressed_overlay": "#E0E7EF",
                "shadow": "rgba(0,0,0,0.06)"
            }
    
    def create_main_menu_keyboard(self, language: str = "en", user_id: int = None) -> InlineKeyboardMarkup:
        """Create modern main menu keyboard with calming design"""
        
        # Log keyboard creation
        if user_id:
            log_info(StepNames.MAIN_MENU, user_id, "Creating modern main menu keyboard", {
                "language": language,
                "theme": self.theme
            })
        
        # Define menu items with modern styling
        menu_items = self._get_main_menu_items(language)
        
        builder = InlineKeyboardBuilder()
        
        # Add menu items with proper spacing and layout
        for item in menu_items:
            if item.get("full_width", False):
                # Full width button for primary actions
                builder.add(InlineKeyboardButton(
                    text=f"🎯 {item['text']}",
                    callback_data=item['callback_data']
                ))
                builder.adjust(1)  # Force new row
            else:
                # Regular button
                builder.add(InlineKeyboardButton(
                    text=item['text'],
                    callback_data=item['callback_data']
                ))
        
        # Adjust layout for optimal spacing (2 buttons per row for most items)
        builder.adjust(2, 2, 1, 1)
        
        return builder.as_markup()
    
    def create_language_selection_keyboard(self, user_id: int = None) -> InlineKeyboardMarkup:
        """Create modern language selection keyboard"""
        
        if user_id:
            log_info(StepNames.LANGUAGE_SELECTION, user_id, "Creating language selection keyboard")
        
        languages = [
            {"flag": "🇺🇸", "name": "English", "code": "en"},
            {"flag": "🇸🇦", "name": "العربية", "code": "ar"},
            {"flag": "🇷🇺", "name": "Русский", "code": "ru"}
        ]
        
        builder = InlineKeyboardBuilder()
        
        for lang in languages:
            builder.add(InlineKeyboardButton(
                text=f"{lang['flag']} {lang['name']}",
                callback_data=f"lang_{lang['code']}"
            ))
        
        # Single column layout for language selection
        builder.adjust(1)
        
        return builder.as_markup()
    
    def create_channel_selection_keyboard(self, channels: List[Dict], 
                                        selected_channels: List[str] = None, 
                                        language: str = "en", 
                                        user_id: int = None) -> InlineKeyboardMarkup:
        """Create modern channel selection keyboard with visual indicators"""
        
        if user_id:
            log_info(StepNames.SELECT_CHANNELS, user_id, "Creating channel selection keyboard", {
                "channels_count": len(channels),
                "selected_count": len(selected_channels or [])
            })
        
        selected_channels = selected_channels or []
        builder = InlineKeyboardBuilder()
        
        # Add channel buttons with selection indicators
        for channel in channels:
            channel_id = str(channel.get('id', ''))
            channel_name = channel.get('name', 'Unknown Channel')
            subscribers = channel.get('subscribers', 0)
            
            # Visual selection indicator
            indicator = "✅" if channel_id in selected_channels else "⭕"
            
            # Format button text with subscriber count
            button_text = f"{indicator} {channel_name}"
            if subscribers > 0:
                button_text += f" ({subscribers:,})"
            
            builder.add(InlineKeyboardButton(
                text=button_text,
                callback_data=f"toggle_channel_{channel_id}"
            ))
        
        # Add control buttons
        builder.add(InlineKeyboardButton(
            text="🔄 Refresh Channels",
            callback_data="refresh_channels"
        ))
        
        if selected_channels:
            builder.add(InlineKeyboardButton(
                text="✨ Continue to Duration",
                callback_data="proceed_to_duration"
            ))
        
        builder.add(InlineKeyboardButton(
            text="◀️ Back to Main Menu",
            callback_data="back_to_main"
        ))
        
        # Adjust layout: 1 column for channels, 2 for controls
        channel_count = len(channels)
        builder.adjust(*([1] * channel_count + [2, 1] if selected_channels else [1] * channel_count + [2]))
        
        return builder.as_markup()
    
    def create_duration_selector_keyboard(self, current_days: int = 1, 
                                        language: str = "en", 
                                        user_id: int = None) -> InlineKeyboardMarkup:
        """Create modern duration selector with counter interface"""
        
        if user_id:
            log_info(StepNames.SELECT_DAYS, user_id, "Creating duration selector keyboard", {
                "current_days": current_days
            })
        
        builder = InlineKeyboardBuilder()
        
        # Counter controls
        builder.add(InlineKeyboardButton(
            text="➖",
            callback_data="duration_decrease"
        ))
        
        builder.add(InlineKeyboardButton(
            text=f"📅 {current_days} days",
            callback_data="duration_current"
        ))
        
        builder.add(InlineKeyboardButton(
            text="➕",
            callback_data="duration_increase"
        ))
        
        # Quick selection buttons
        quick_options = [1, 7, 30, 90]
        for days in quick_options:
            if days != current_days:
                builder.add(InlineKeyboardButton(
                    text=f"{days}d",
                    callback_data=f"duration_quick_{days}"
                ))
        
        # Control buttons
        builder.add(InlineKeyboardButton(
            text="✨ Continue to Posts",
            callback_data="proceed_to_posts"
        ))
        
        builder.add(InlineKeyboardButton(
            text="◀️ Back to Channels",
            callback_data="back_to_channels"
        ))
        
        # Layout: counter row, quick options, controls
        builder.adjust(3, len([d for d in quick_options if d != current_days]), 1, 1)
        
        return builder.as_markup()
    
    def create_payment_method_keyboard(self, amount_usd: float, 
                                     language: str = "en", 
                                     user_id: int = None) -> InlineKeyboardMarkup:
        """Create modern payment method selection keyboard"""
        
        if user_id:
            log_info(StepNames.PAYMENT_METHOD_SELECTION, user_id, "Creating payment method keyboard", {
                "amount_usd": amount_usd
            })
        
        builder = InlineKeyboardBuilder()
        
        # Payment methods with modern styling
        payment_methods = self._get_payment_methods(language, amount_usd)
        
        for method in payment_methods:
            builder.add(InlineKeyboardButton(
                text=method['text'],
                callback_data=method['callback_data']
            ))
        
        # Back button
        builder.add(InlineKeyboardButton(
            text="◀️ Back to Summary",
            callback_data="back_to_summary"
        ))
        
        # Two columns for payment methods, full width for back
        builder.adjust(2, 1)
        
        return builder.as_markup()
    
    def create_admin_keyboard(self, language: str = "en", 
                            user_id: int = None) -> InlineKeyboardMarkup:
        """Create modern admin panel keyboard"""
        
        if user_id:
            log_info(StepNames.ADMIN_MAIN_MENU, user_id, "Creating admin panel keyboard")
        
        builder = InlineKeyboardBuilder()
        
        # Admin menu items
        admin_items = self._get_admin_menu_items(language)
        
        for item in admin_items:
            builder.add(InlineKeyboardButton(
                text=item['text'],
                callback_data=item['callback_data']
            ))
        
        # Back to main menu
        builder.add(InlineKeyboardButton(
            text="◀️ Back to Main Menu",
            callback_data="back_to_main"
        ))
        
        # 2x2 grid layout for admin options
        builder.adjust(2, 2, 2, 1)
        
        return builder.as_markup()
    
    def create_confirmation_keyboard(self, confirm_text: str, 
                                   cancel_text: str,
                                   confirm_callback: str,
                                   cancel_callback: str,
                                   user_id: int = None) -> InlineKeyboardMarkup:
        """Create modern confirmation dialog keyboard"""
        
        if user_id:
            log_info(StepNames.ERROR_HANDLER, user_id, "Creating confirmation keyboard")
        
        builder = InlineKeyboardBuilder()
        
        # Confirmation buttons with clear visual distinction
        builder.add(InlineKeyboardButton(
            text=f"✅ {confirm_text}",
            callback_data=confirm_callback
        ))
        
        builder.add(InlineKeyboardButton(
            text=f"❌ {cancel_text}",
            callback_data=cancel_callback
        ))
        
        # Side by side layout
        builder.adjust(2)
        
        return builder.as_markup()
    
    def _get_main_menu_items(self, language: str) -> List[Dict]:
        """Get main menu items based on language"""
        
        items = {
            "en": [
                {"text": "📝 Create New Ad", "callback_data": "create_ad", "full_width": True},
                {"text": "📊 My Ads", "callback_data": "my_ads"},
                {"text": "💎 Share & Earn", "callback_data": "share_earn"},
                {"text": "🏆 Gaming Hub", "callback_data": "gaming_hub"},
                {"text": "🤝 Channel Partners", "callback_data": "channel_partners"},
                {"text": "🌐 Language", "callback_data": "change_language"}
            ],
            "ar": [
                {"text": "📝 إنشاء إعلان جديد", "callback_data": "create_ad", "full_width": True},
                {"text": "📊 إعلاناتي", "callback_data": "my_ads"},
                {"text": "💎 شارك واربح", "callback_data": "share_earn"},
                {"text": "🏆 مركز الألعاب", "callback_data": "gaming_hub"},
                {"text": "🤝 شركاء القنوات", "callback_data": "channel_partners"},
                {"text": "🌐 اللغة", "callback_data": "change_language"}
            ],
            "ru": [
                {"text": "📝 Создать объявление", "callback_data": "create_ad", "full_width": True},
                {"text": "📊 Мои объявления", "callback_data": "my_ads"},
                {"text": "💎 Поделиться и заработать", "callback_data": "share_earn"},
                {"text": "🏆 Игровой центр", "callback_data": "gaming_hub"},
                {"text": "🤝 Партнеры каналов", "callback_data": "channel_partners"},
                {"text": "🌐 Язык", "callback_data": "change_language"}
            ]
        }
        
        return items.get(language, items["en"])
    
    def _get_payment_methods(self, language: str, amount_usd: float) -> List[Dict]:
        """Get payment methods with localized text"""
        
        # Calculate conversions
        amount_ton = round(amount_usd * 0.36, 3)
        amount_stars = int(amount_usd * 34)
        
        methods = {
            "en": [
                {
                    "text": f"💎 TON ({amount_ton} TON)",
                    "callback_data": "payment_ton"
                },
                {
                    "text": f"⭐ Stars ({amount_stars} ⭐)",
                    "callback_data": "payment_stars"
                }
            ],
            "ar": [
                {
                    "text": f"💎 TON ({amount_ton} TON)",
                    "callback_data": "payment_ton"
                },
                {
                    "text": f"⭐ نجوم ({amount_stars} ⭐)",
                    "callback_data": "payment_stars"
                }
            ],
            "ru": [
                {
                    "text": f"💎 TON ({amount_ton} TON)",
                    "callback_data": "payment_ton"
                },
                {
                    "text": f"⭐ Звезды ({amount_stars} ⭐)",
                    "callback_data": "payment_stars"
                }
            ]
        }
        
        return methods.get(language, methods["en"])
    
    def _get_admin_menu_items(self, language: str) -> List[Dict]:
        """Get admin menu items"""
        
        items = {
            "en": [
                {"text": "📋 Channel Management", "callback_data": "admin_channels"},
                {"text": "👥 User Management", "callback_data": "admin_users"},
                {"text": "📊 Statistics", "callback_data": "admin_stats"},
                {"text": "⚙️ Settings", "callback_data": "admin_settings"},
                {"text": "🎨 UI Control", "callback_data": "admin_ui_control"},
                {"text": "🔧 Troubleshooting", "callback_data": "admin_troubleshoot"}
            ],
            "ar": [
                {"text": "📋 إدارة القنوات", "callback_data": "admin_channels"},
                {"text": "👥 إدارة المستخدمين", "callback_data": "admin_users"},
                {"text": "📊 الإحصائيات", "callback_data": "admin_stats"},
                {"text": "⚙️ الإعدادات", "callback_data": "admin_settings"},
                {"text": "🎨 تحكم الواجهة", "callback_data": "admin_ui_control"},
                {"text": "🔧 استكشاف الأخطاء", "callback_data": "admin_troubleshoot"}
            ],
            "ru": [
                {"text": "📋 Управление каналами", "callback_data": "admin_channels"},
                {"text": "👥 Управление пользователями", "callback_data": "admin_users"},
                {"text": "📊 Статистика", "callback_data": "admin_stats"},
                {"text": "⚙️ Настройки", "callback_data": "admin_settings"},
                {"text": "🎨 Управление интерфейсом", "callback_data": "admin_ui_control"},
                {"text": "🔧 Устранение неполадок", "callback_data": "admin_troubleshoot"}
            ]
        }
        
        return items.get(language, items["en"])

# Global keyboard instance
modern_keyboard = ModernKeyboard()

# Convenience functions
def create_modern_main_menu(language: str = "en", user_id: int = None) -> InlineKeyboardMarkup:
    """Create modern main menu keyboard"""
    return modern_keyboard.create_main_menu_keyboard(language, user_id)

def create_modern_language_selector(user_id: int = None) -> InlineKeyboardMarkup:
    """Create modern language selection keyboard"""
    return modern_keyboard.create_language_selection_keyboard(user_id)

def create_modern_channel_selector(channels: List[Dict], 
                                 selected: List[str] = None, 
                                 language: str = "en", 
                                 user_id: int = None) -> InlineKeyboardMarkup:
    """Create modern channel selection keyboard"""
    return modern_keyboard.create_channel_selection_keyboard(channels, selected, language, user_id)

def create_modern_duration_selector(current_days: int = 1, 
                                  language: str = "en", 
                                  user_id: int = None) -> InlineKeyboardMarkup:
    """Create modern duration selector keyboard"""
    return modern_keyboard.create_duration_selector_keyboard(current_days, language, user_id)

def create_modern_payment_selector(amount_usd: float, 
                                 language: str = "en", 
                                 user_id: int = None) -> InlineKeyboardMarkup:
    """Create modern payment method keyboard"""
    return modern_keyboard.create_payment_method_keyboard(amount_usd, language, user_id)

def create_modern_admin_panel(language: str = "en", 
                            user_id: int = None) -> InlineKeyboardMarkup:
    """Create modern admin panel keyboard"""
    return modern_keyboard.create_admin_keyboard(language, user_id)

def create_modern_confirmation(confirm_text: str, 
                             cancel_text: str,
                             confirm_callback: str,
                             cancel_callback: str,
                             user_id: int = None) -> InlineKeyboardMarkup:
    """Create modern confirmation dialog"""
    return modern_keyboard.create_confirmation_keyboard(
        confirm_text, cancel_text, confirm_callback, cancel_callback, user_id
    )

# CSS styling information for reference
KEYBOARD_STYLES = {
    "light_theme": {
        "background": "#F4F7FB",
        "key_default": "#FFFFFF",
        "key_border": "#DDE3EB",
        "font_color": "#1A1A1A",
        "primary_action": "#2563EB",
        "pressed_overlay": "#E0E7EF",
        "shadow": "rgba(0,0,0,0.06)",
        "border_radius": "12px",
        "font_family": "Noto Sans, SF Pro",
        "font_size": "16-18px",
        "spacing": "4px"
    },
    "dark_theme": {
        "background": "#1E1E2A",
        "key_default": "#2C2F3A",
        "key_border": "#3A3F4A",
        "font_color": "#F5F5F5",
        "primary_action": "#3B82F6",
        "pressed_overlay": "#404654",
        "shadow": "rgba(0,0,0,0.15)",
        "border_radius": "12px",
        "font_family": "Noto Sans, SF Pro",
        "font_size": "16-18px",
        "spacing": "4px"
    }
}