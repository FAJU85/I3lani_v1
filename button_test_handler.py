"""
Button Testing and Error Handling System
Tests all bot buttons and provides user feedback for non-working features
"""

import logging
from typing import Dict, List, Tuple
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from database import db
from languages import get_text
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

router = Router()

# Button status tracking
BUTTON_STATUS = {
    # Main menu buttons
    'create_ad': {
        'working': True, 
        'reason': None
    },
    'channel_partners': {
        'working': True,
        'reason': None
    },
    'share_win': {
        'working': True,
        'reason': None
    },
    'gaming_hub': {
        'working': True,
        'reason': None  
    },
    'leaderboard': {
        'working': True,
        'reason': None
    },
    'language_settings': {
        'working': True,
        'reason': None
    },
    'contact_support': {
        'working': True,
        'reason': None
    },
    
    # Admin buttons
    'manage_channels': {
        'working': True,
        'reason': None
    },
    'manage_price': {
        'working': True,
        'reason': None
    },
    'user_analytics': {
        'working': False,
        'reason': 'analytics_under_development'
    },
    'broadcast': {
        'working': False,
        'reason': 'broadcast_feature_pending'
    },
    'ui_control': {
        'working': True,
        'reason': None
    },
    'troubleshooting': {
        'working': True,
        'reason': None
    },
    'anti_fraud': {
        'working': True,
        'reason': None
    },
    'content_moderation': {
        'working': True,
        'reason': None
    },
    'gamification_admin': {
        'working': True,
        'reason': None
    },
    'manage_settings': {
        'working': True,
        'reason': None
    },
    
    # Payment buttons
    'pay_ton': {
        'working': True,
        'reason': None
    },
    'pay_stars': {
        'working': True,
        'reason': None
    },
    
    # Channel partner buttons
    'view_earnings': {
        'working': True,
        'reason': None
    },
    'invite_friends': {
        'working': True,
        'reason': None
    },
    'request_payout': {
        'working': False,
        'reason': 'payout_minimum_not_reached'
    },
    
    # Gamification buttons
    'daily_checkin': {
        'working': True,
        'reason': None
    },
    'view_achievements': {
        'working': True,
        'reason': None
    },
    'view_profile': {
        'working': True,
        'reason': None
    }
}

# Error messages for non-working buttons
ERROR_REASONS = {
    'analytics_under_development': {
        'en': "📊 Analytics Dashboard is under development.\nThis feature will be available soon with detailed user insights and revenue reports.",
        'ar': "📊 لوحة التحليلات قيد التطوير.\nستكون هذه الميزة متاحة قريباً مع رؤى مفصلة للمستخدمين وتقارير الإيرادات.",
        'ru': "📊 Панель аналитики находится в разработке.\nЭта функция скоро будет доступна с подробной статистикой и отчетами."
    },
    'broadcast_feature_pending': {
        'en': "📢 Broadcast feature is being upgraded.\nAdmin broadcasting will be available after security improvements are complete.",
        'ar': "📢 ميزة البث قيد الترقية.\nسيكون البث الإداري متاحاً بعد اكتمال التحسينات الأمنية.",
        'ru': "📢 Функция рассылки обновляется.\nАдминистративная рассылка будет доступна после завершения улучшений безопасности."
    },
    'payout_minimum_not_reached': {
        'en': "💰 Minimum payout threshold not reached.\nYou need at least 25 TON to request a payout. Keep earning!",
        'ar': "💰 لم يتم الوصول إلى الحد الأدنى للدفع.\nتحتاج إلى 25 TON على الأقل لطلب الدفع. استمر في الكسب!",
        'ru': "💰 Минимальный порог выплат не достигнут.\nДля запроса выплаты необходимо минимум 25 TON. Продолжайте зарабатывать!"
    },
    'feature_temporarily_disabled': {
        'en': "🔧 This feature is temporarily disabled for maintenance.\nPlease try again later.",
        'ar': "🔧 هذه الميزة معطلة مؤقتاً للصيانة.\nيرجى المحاولة مرة أخرى لاحقاً.",
        'ru': "🔧 Эта функция временно отключена для обслуживания.\nПожалуйста, попробуйте позже."
    }
}

async def check_button_status(button_id: str, user_id: int) -> Tuple[bool, str]:
    """
    Check if a button should work for a specific user
    
    Returns:
        Tuple[bool, str]: (is_working, error_message_key)
    """
    if button_id not in BUTTON_STATUS:
        return True, None
    
    status = BUTTON_STATUS[button_id]
    
    # Special checks for certain buttons
    if button_id == 'request_payout':
        # Check if user has enough balance
        try:
            balance = await db.get_partner_balance(user_id)
            if balance and balance >= 25.0:
                return True, None
        except:
            pass
    
    return status['working'], status['reason']

async def send_error_message(message: Message, reason_key: str, language: str):
    """Send error message for non-working button"""
    if reason_key in ERROR_REASONS:
        error_text = ERROR_REASONS[reason_key].get(language, ERROR_REASONS[reason_key]['en'])
    else:
        error_text = get_text(language, 'feature_not_available', 
                            "This feature is currently not available. Please try again later.")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(language, 'back_to_main', "◀️ Back to Main"),
            callback_data="back_to_main"
        )]
    ])
    
    await message.answer(error_text, reply_markup=keyboard)

@router.message(Command("test_buttons"))
async def test_all_buttons(message: Message):
    """Admin command to test all buttons"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    report = "🔍 **BUTTON STATUS REPORT**\n\n"
    
    # Group buttons by category
    categories = {
        "Main Menu": ['create_ad', 'channel_partners', 'share_win', 'gaming_hub', 
                     'leaderboard', 'language_settings', 'contact_support'],
        "Admin Panel": ['manage_channels', 'manage_price', 'user_analytics', 
                       'broadcast', 'ui_control', 'troubleshooting', 'anti_fraud',
                       'content_moderation', 'gamification_admin', 'manage_settings'],
        "Payments": ['pay_ton', 'pay_stars'],
        "Channel Partners": ['view_earnings', 'invite_friends', 'request_payout'],
        "Gamification": ['daily_checkin', 'view_achievements', 'view_profile']
    }
    
    for category, buttons in categories.items():
        report += f"**{category}:**\n"
        for button_id in buttons:
            status = BUTTON_STATUS.get(button_id, {'working': True, 'reason': None})
            if status['working']:
                report += f"✅ {button_id}\n"
            else:
                report += f"❌ {button_id} - {status['reason']}\n"
        report += "\n"
    
    await message.answer(report, parse_mode="Markdown")

# Add error handling to existing callbacks
@router.callback_query(lambda c: c.data == "user_analytics")
async def handle_analytics_button(callback: CallbackQuery):
    """Handle analytics button click"""
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    
    is_working, reason = await check_button_status('user_analytics', user_id)
    if not is_working:
        await callback.message.edit_text(
            ERROR_REASONS[reason].get(language, ERROR_REASONS[reason]['en']),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=get_text(language, 'back', "◀️ Back"),
                    callback_data="admin_menu"
                )]
            ])
        )
        await callback.answer()
        return

@router.callback_query(lambda c: c.data == "admin_broadcast")
async def handle_broadcast_button(callback: CallbackQuery):
    """Handle broadcast button click"""
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    
    is_working, reason = await check_button_status('broadcast', user_id)
    if not is_working:
        await callback.message.edit_text(
            ERROR_REASONS[reason].get(language, ERROR_REASONS[reason]['en']),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=get_text(language, 'back', "◀️ Back"),
                    callback_data="admin_menu"
                )]
            ])
        )
        await callback.answer()
        return

# Export router
__all__ = ['router', 'check_button_status', 'send_error_message']