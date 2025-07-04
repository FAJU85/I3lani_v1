from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PACKAGES

def get_package_keyboard() -> InlineKeyboardMarkup:
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

def get_payment_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for payment confirmation"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="✅ I've Paid",
            callback_data="payment_sent"
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="❌ Cancel",
            callback_data="payment_cancel"
        )
    )
    return keyboard

def get_admin_approval_keyboard(ad_id: str) -> InlineKeyboardMarkup:
    """Create keyboard for admin approval"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="✅ Approve",
            callback_data=f"approve_{ad_id}"
        ),
        InlineKeyboardButton(
            text="❌ Reject",
            callback_data=f"reject_{ad_id}"
        )
    )
    return keyboard

def get_package_details_keyboard(package_id: str) -> InlineKeyboardMarkup:
    """Create keyboard showing package details"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text="💳 Choose This Package",
            callback_data=f"confirm_package_{package_id}"
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="⬅️ Back to Packages",
            callback_data="back_to_packages"
        )
    )
    return keyboard
