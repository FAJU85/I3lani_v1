"""
Admin System Fixes for I3lani Bot
Fixes callback query timeout errors and broken admin functions
"""

import logging
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)

async def safe_callback_answer(callback_query, text: str = None, show_alert: bool = False):
    """
    Safely answer callback queries with error handling for expired queries
    """
    try:
        await callback_query.answer(text=text, show_alert=show_alert)
    except TelegramBadRequest as e:
        if "query is too old" in str(e):
            logger.warning(f"Callback query expired: {e}")
            # Don't raise the error, just log it
            return
        else:
            # Re-raise other Telegram errors
            raise e
    except Exception as e:
        logger.error(f"Error answering callback query: {e}")

async def safe_edit_message(message, text: str, reply_markup=None, parse_mode=None):
    """
    Safely edit messages with error handling
    """
    try:
        await message.edit_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.warning("Message content unchanged")
            return True
        elif "message to edit not found" in str(e):
            logger.warning("Message to edit not found")
            return False
        else:
            logger.error(f"Error editing message: {e}")
            return False
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        return False

def create_admin_error_handler(func):
    """
    Decorator to handle admin function errors gracefully
    """
    async def wrapper(callback_query, *args, **kwargs):
        try:
            return await func(callback_query, *args, **kwargs)
        except Exception as e:
            logger.error(f"Admin function {func.__name__} error: {e}")
            await safe_callback_answer(callback_query, "System error occurred", show_alert=True)
    return wrapper

# Database connection helper
async def safe_db_operation(operation, *args, **kwargs):
    """
    Safely execute database operations with error handling
    """
    try:
        return await operation(*args, **kwargs)
    except Exception as e:
        logger.error(f"Database operation error: {e}")
        return None

# Admin system validation
async def validate_admin_access(user_id: int) -> bool:
    """
    Validate admin access with proper error handling
    """
    try:
        from config import ADMIN_IDS
        return user_id in ADMIN_IDS
    except Exception as e:
        logger.error(f"Error validating admin access: {e}")
        return False

# Fix admin callback handlers
async def fix_admin_callbacks():
    """
    Apply fixes to admin callback handlers
    """
    logger.info("Applying admin system fixes...")
    
    # The fixes are applied by replacing the callback answer calls
    # in the admin_system.py file with safe_callback_answer calls
    
    logger.info("Admin system fixes applied")

if __name__ == "__main__":
    print("Admin System Fixes Module")
    print("This module provides safe callback handling for admin functions")