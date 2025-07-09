"""
Enhanced Keyboard Effects for I3lani Bot
Creates interactive keyboards with visual and haptic feedback
"""

import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user_language
from languages import get_text

logger = logging.getLogger(__name__)

class EnhancedKeyboard:
    """Creates enhanced keyboards with visual effects"""
    
    @staticmethod
    def create_main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
        """Create main menu keyboard with enhanced effects"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✨ ➕ Create New Ad ➕ ✨",
                    callback_data="haptic_glow_create_ad"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💫 📄 My Ads 📄 💫",
                    callback_data="haptic_pulse_my_ads"
                ),
                InlineKeyboardButton(
                    text="🌟 💵 Pricing 💵 🌟",
                    callback_data="haptic_shimmer_pricing"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎮 Share & Earn Portal 🎮",
                    callback_data="haptic_game_share_earn"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏆 Rewards & Games 🏆",
                    callback_data="haptic_reward_gaming_hub"
                ),
                InlineKeyboardButton(
                    text="🤝 Partner Network 🤝",
                    callback_data="haptic_highlight_channel_partners"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Settings",
                    callback_data="haptic_default_settings"
                ),
                InlineKeyboardButton(
                    text="❓ Help",
                    callback_data="haptic_default_help"
                )
            ]
        ])
    
    @staticmethod
    def create_payment_keyboard(language: str) -> InlineKeyboardMarkup:
        """Create payment keyboard with enhanced effects"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💎 TON Cryptocurrency 💎",
                    callback_data="haptic_payment_pay_freq_ton"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Telegram Stars ⭐",
                    callback_data="haptic_payment_pay_freq_stars"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Change Duration",
                    callback_data="haptic_pulse_freq_change_duration"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Cancel",
                    callback_data="haptic_default_cancel_payment"
                )
            ]
        ])
    
    @staticmethod
    def create_viral_game_keyboard(progress: int, language: str) -> InlineKeyboardMarkup:
        """Create viral game keyboard with enhanced effects"""
        if progress < 99:
            return InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🎯 TAP TO PROGRESS 🎯",
                        callback_data="haptic_game_tap_progress"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📊 Check Progress 📊",
                        callback_data="haptic_pulse_check_progress"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Back to Main",
                        callback_data="haptic_default_back_to_main"
                    )
                ]
            ])
        else:
            return InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔗 Get Referral Link 🔗",
                        callback_data="haptic_shimmer_get_referral_link"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📈 Check My Referrals 📈",
                        callback_data="haptic_pulse_check_referrals"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏆 My Rewards 🏆",
                        callback_data="haptic_reward_check_rewards"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎁 Use Free Ad 🎁",
                        callback_data="haptic_success_use_free_ad"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Back to Main",
                        callback_data="haptic_default_back_to_main"
                    )
                ]
            ])
    
    @staticmethod
    def create_channel_selection_keyboard(channels: list, selected_channels: list, language: str) -> InlineKeyboardMarkup:
        """Create channel selection keyboard with enhanced effects"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for channel in channels:
            channel_id = channel.get('id')
            channel_name = channel.get('name', 'Unknown')
            subscribers = channel.get('subscribers', 0)
            
            # Visual indicator for selection
            if channel_id in selected_channels:
                text = f"✅ {channel_name} ({subscribers:,} subscribers)"
                callback = f"haptic_success_deselect_channel_{channel_id}"
            else:
                text = f"⭕ {channel_name} ({subscribers:,} subscribers)"
                callback = f"haptic_glow_select_channel_{channel_id}"
            
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(text=text, callback_data=callback)
            ])
        
        # Continue button
        if selected_channels:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text="✨ Continue to Duration ✨",
                    callback_data="haptic_pulse_continue_to_duration"
                )
            ])
        
        # Back button
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="⬅️ Back",
                callback_data="haptic_default_back_to_main"
            )
        ])
        
        return keyboard
    
    @staticmethod
    def create_duration_keyboard(language: str) -> InlineKeyboardMarkup:
        """Create duration selection keyboard with enhanced effects"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➖ Decrease Days ➖",
                    callback_data="haptic_pulse_decrease_days"
                ),
                InlineKeyboardButton(
                    text="➕ Increase Days ➕",
                    callback_data="haptic_pulse_increase_days"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 1 Day 🔥",
                    callback_data="haptic_highlight_quick_1_day"
                ),
                InlineKeyboardButton(
                    text="⭐ 7 Days ⭐",
                    callback_data="haptic_highlight_quick_7_days"
                ),
                InlineKeyboardButton(
                    text="💎 30 Days 💎",
                    callback_data="haptic_highlight_quick_30_days"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 Select Posts Per Day 🎯",
                    callback_data="haptic_shimmer_select_posts_per_day"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back to Channels",
                    callback_data="haptic_default_back_to_channels"
                )
            ]
        ])
    
    @staticmethod
    def create_confirmation_keyboard(language: str, action_type: str = 'default') -> InlineKeyboardMarkup:
        """Create confirmation keyboard with enhanced effects"""
        effect_map = {
            'payment': 'payment',
            'delete': 'highlight',
            'publish': 'success',
            'cancel': 'default'
        }
        
        effect = effect_map.get(action_type, 'default')
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ CONFIRM ✅",
                    callback_data=f"haptic_{effect}_confirm_action"
                ),
                InlineKeyboardButton(
                    text="❌ CANCEL ❌",
                    callback_data="haptic_default_cancel_action"
                )
            ]
        ])
    
    @staticmethod
    def create_language_keyboard() -> InlineKeyboardMarkup:
        """Create language selection keyboard with enhanced effects"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇺🇸 English ✨",
                    callback_data="haptic_glow_language_en"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇸🇦 العربية 🌟",
                    callback_data="haptic_shimmer_language_ar"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский 💫",
                    callback_data="haptic_pulse_language_ru"
                )
            ]
        ])
    
    @staticmethod
    def create_admin_keyboard(language: str) -> InlineKeyboardMarkup:
        """Create admin keyboard with enhanced effects"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Analytics Dashboard 📊",
                    callback_data="haptic_highlight_admin_analytics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔧 Channel Management 🔧",
                    callback_data="haptic_pulse_admin_channels"
                ),
                InlineKeyboardButton(
                    text="👥 User Management 👥",
                    callback_data="haptic_shimmer_admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Payment Settings 💳",
                    callback_data="haptic_payment_admin_payments"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Broadcast Message 📢",
                    callback_data="haptic_highlight_admin_broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back to Main",
                    callback_data="haptic_default_back_to_main"
                )
            ]
        ])
    
    @staticmethod
    def create_celebration_keyboard(language: str, celebration_type: str = 'success') -> InlineKeyboardMarkup:
        """Create celebration keyboard with enhanced effects"""
        if celebration_type == 'reward':
            return InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🎉 CLAIM REWARD 🎉",
                        callback_data="haptic_reward_claim_reward"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔗 Share Success 🔗",
                        callback_data="haptic_celebration_share_success"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🎮 Play Again 🎮",
                        callback_data="haptic_game_play_again"
                    )
                ]
            ])
        else:
            return InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✨ Continue ✨",
                        callback_data="haptic_success_continue"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Back to Main",
                        callback_data="haptic_default_back_to_main"
                    )
                ]
            ])

# Enhanced keyboard factory
def create_enhanced_keyboard(keyboard_type: str, language: str = 'en', **kwargs) -> InlineKeyboardMarkup:
    """Factory function for creating enhanced keyboards"""
    try:
        if keyboard_type == 'main_menu':
            return EnhancedKeyboard.create_main_menu_keyboard(language)
        elif keyboard_type == 'payment':
            return EnhancedKeyboard.create_payment_keyboard(language)
        elif keyboard_type == 'viral_game':
            progress = kwargs.get('progress', 0)
            return EnhancedKeyboard.create_viral_game_keyboard(progress, language)
        elif keyboard_type == 'channel_selection':
            channels = kwargs.get('channels', [])
            selected = kwargs.get('selected_channels', [])
            return EnhancedKeyboard.create_channel_selection_keyboard(channels, selected, language)
        elif keyboard_type == 'duration':
            return EnhancedKeyboard.create_duration_keyboard(language)
        elif keyboard_type == 'confirmation':
            action_type = kwargs.get('action_type', 'default')
            return EnhancedKeyboard.create_confirmation_keyboard(language, action_type)
        elif keyboard_type == 'language':
            return EnhancedKeyboard.create_language_keyboard()
        elif keyboard_type == 'admin':
            return EnhancedKeyboard.create_admin_keyboard(language)
        elif keyboard_type == 'celebration':
            celebration_type = kwargs.get('celebration_type', 'success')
            return EnhancedKeyboard.create_celebration_keyboard(language, celebration_type)
        else:
            logger.warning(f"Unknown keyboard type: {keyboard_type}")
            return InlineKeyboardMarkup(inline_keyboard=[])
            
    except Exception as e:
        logger.error(f"Error creating enhanced keyboard: {e}")
        return InlineKeyboardMarkup(inline_keyboard=[])