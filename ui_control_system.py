#!/usr/bin/env python3
"""
UI Control System
User interface control and management system
"""

import logging
from typing import Dict, List, Optional, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

class UIControlSystem:
    """UI control and management system"""
    
    def __init__(self):
        self.ui_states = {}
        self.keyboard_cache = {}
        self.ui_themes = {
            'default': {
                'primary_color': '🔵',
                'secondary_color': '⚪',
                'success_color': '🟢',
                'warning_color': '🟡',
                'error_color': '🔴'
            },
            'crypto': {
                'primary_color': '💎',
                'secondary_color': '⭐',
                'success_color': '✅',
                'warning_color': '⚠️',
                'error_color': '❌'
            }
        }
    
    def create_dynamic_keyboard(self, buttons: List[Dict], theme: str = 'default') -> InlineKeyboardMarkup:
        """Create dynamic keyboard with theme support"""
        try:
            keyboard = []
            theme_config = self.ui_themes.get(theme, self.ui_themes['default'])
            
            for button_row in buttons:
                row = []
                for button in button_row:
                    # Apply theme colors
                    text = button.get('text', '')
                    if button.get('type') == 'primary':
                        text = f"{theme_config['primary_color']} {text}"
                    elif button.get('type') == 'success':
                        text = f"{theme_config['success_color']} {text}"
                    elif button.get('type') == 'warning':
                        text = f"{theme_config['warning_color']} {text}"
                    elif button.get('type') == 'error':
                        text = f"{theme_config['error_color']} {text}"
                    
                    row.append(InlineKeyboardButton(
                        text=text,
                        callback_data=button.get('callback_data', 'noop')
                    ))
                
                keyboard.append(row)
            
            return InlineKeyboardMarkup(inline_keyboard=keyboard)
            
        except Exception as e:
            logger.error(f"Error creating dynamic keyboard: {e}")
            return InlineKeyboardMarkup(inline_keyboard=[])
    
    def get_ui_state(self, user_id: int) -> Dict:
        """Get UI state for user"""
        return self.ui_states.get(user_id, {})
    
    def set_ui_state(self, user_id: int, state: Dict):
        """Set UI state for user"""
        self.ui_states[user_id] = state
    
    def create_pagination_keyboard(self, items: List, page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
        """Create pagination keyboard"""
        try:
            keyboard = []
            
            # Calculate pagination
            total_pages = (len(items) + per_page - 1) // per_page
            start_idx = page * per_page
            end_idx = min(start_idx + per_page, len(items))
            
            # Add items for current page
            for i in range(start_idx, end_idx):
                item = items[i]
                keyboard.append([
                    InlineKeyboardButton(
                        text=item.get('text', f'Item {i+1}'),
                        callback_data=item.get('callback_data', f'item_{i}')
                    )
                ])
            
            # Add pagination controls
            if total_pages > 1:
                nav_row = []
                if page > 0:
                    nav_row.append(InlineKeyboardButton(
                        text="⬅️ Previous",
                        callback_data=f"page_{page-1}"
                    ))
                
                nav_row.append(InlineKeyboardButton(
                    text=f"📄 {page+1}/{total_pages}",
                    callback_data="page_info"
                ))
                
                if page < total_pages - 1:
                    nav_row.append(InlineKeyboardButton(
                        text="Next ➡️",
                        callback_data=f"page_{page+1}"
                    ))
                
                keyboard.append(nav_row)
            
            return InlineKeyboardMarkup(inline_keyboard=keyboard)
            
        except Exception as e:
            logger.error(f"Error creating pagination keyboard: {e}")
            return InlineKeyboardMarkup(inline_keyboard=[])
    
    def create_confirmation_keyboard(self, confirm_data: str, cancel_data: str = "cancel") -> InlineKeyboardMarkup:
        """Create confirmation keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Confirm", callback_data=confirm_data),
                InlineKeyboardButton(text="❌ Cancel", callback_data=cancel_data)
            ]
        ])
    
    def create_back_keyboard(self, back_data: str = "back") -> InlineKeyboardMarkup:
        """Create simple back keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data=back_data)]
        ])
    
    def format_status_message(self, title: str, items: List[Dict], theme: str = 'default') -> str:
        """Format status message with theme"""
        try:
            theme_config = self.ui_themes.get(theme, self.ui_themes['default'])
            
            message = f"<b>{title}</b>\n\n"
            
            for item in items:
                status = item.get('status', 'unknown')
                name = item.get('name', 'Unknown')
                value = item.get('value', '')
                
                # Apply status colors
                if status == 'success':
                    icon = theme_config['success_color']
                elif status == 'warning':
                    icon = theme_config['warning_color']
                elif status == 'error':
                    icon = theme_config['error_color']
                else:
                    icon = theme_config['secondary_color']
                
                message += f"{icon} <b>{name}</b>: {value}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting status message: {e}")
            return f"<b>{title}</b>\n\nError formatting message"
    
    def cache_keyboard(self, key: str, keyboard: InlineKeyboardMarkup):
        """Cache keyboard for reuse"""
        self.keyboard_cache[key] = keyboard
    
    def get_cached_keyboard(self, key: str) -> Optional[InlineKeyboardMarkup]:
        """Get cached keyboard"""
        return self.keyboard_cache.get(key)
    
    def clear_cache(self):
        """Clear keyboard cache"""
        self.keyboard_cache.clear()

# Global instance
ui_control_system = UIControlSystem()

def get_ui_control_system() -> UIControlSystem:
    """Get UI control system instance"""
    return ui_control_system