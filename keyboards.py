from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PACKAGES
from languages import get_text, get_language_keyboard

def get_package_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for package selection"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for package_id, package_info in PACKAGES.items():
        button_text = f"{package_info['name']} - {package_info['price']} TON"
        keyboard.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"package_{package_id}"
            )
        )
    
    return keyboard

def get_payment_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for payment confirmation"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=get_text(user_id, "buttons.ive_paid"),
            callback_data="payment_sent"
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=get_text(user_id, "buttons.cancel"),
            callback_data="payment_cancel"
        )
    )
    return keyboard

def get_admin_approval_keyboard(ad_id: str, user_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for admin approval"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=get_text(user_id, "buttons.approve"),
            callback_data=f"approve_{ad_id}"
        ),
        InlineKeyboardButton(
            text=get_text(user_id, "buttons.reject"),
            callback_data=f"reject_{ad_id}"
        )
    )
    return keyboard

def get_package_details_keyboard(package_id: str, user_id: int) -> InlineKeyboardMarkup:
    """Create keyboard showing package details"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=get_text(user_id, "buttons.choose_package"),
            callback_data=f"confirm_package_{package_id}"
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=get_text(user_id, "buttons.back_to_packages"),
            callback_data="back_to_packages"
        )
    )
    return keyboard
