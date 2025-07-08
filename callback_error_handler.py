"""
Callback Query Error Handler for I3lani Bot
Prevents freezing issues caused by callback query timeouts
"""
import logging
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)

async def safe_callback_answer(callback_query: CallbackQuery, text: str = None, show_alert: bool = False):
    """
    Safely answer callback query with timeout protection
    Prevents bot freezing from 'query is too old' errors
    """
    try:
        await callback_query.answer(text=text, show_alert=show_alert)
    except TelegramBadRequest as e:
        if "query is too old" in str(e) or "query ID is invalid" in str(e):
            logger.warning(f"Callback query timeout ignored: {e}")
            # Silently ignore timeout errors to prevent freezing
            return
        else:
            logger.error(f"Callback query error: {e}")
            # Re-raise other errors
            raise
    except Exception as e:
        logger.error(f"Unexpected callback answer error: {e}")
        # Ignore all callback answer errors to prevent freezing

async def safe_callback_edit(callback_query: CallbackQuery, text: str, reply_markup=None, parse_mode=None):
    """
    Safely edit callback query message with timeout protection
    """
    try:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        await safe_callback_answer(callback_query)
    except TelegramBadRequest as e:
        if "query is too old" in str(e) or "query ID is invalid" in str(e):
            logger.warning(f"Callback edit timeout ignored: {e}")
            # Try to send new message instead
            try:
                await callback_query.message.answer(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            except Exception as send_error:
                logger.error(f"Failed to send new message after timeout: {send_error}")
        else:
            logger.error(f"Callback edit error: {e}")
            raise
    except Exception as e:
        logger.error(f"Unexpected callback edit error: {e}")

def create_error_resistant_callback_handler(original_handler):
    """
    Decorator to make callback handlers resistant to timeout errors
    """
    async def wrapper(callback_query: CallbackQuery, *args, **kwargs):
        try:
            return await original_handler(callback_query, *args, **kwargs)
        except TelegramBadRequest as e:
            if "query is too old" in str(e) or "query ID is invalid" in str(e):
                logger.warning(f"Callback handler timeout ignored for {original_handler.__name__}: {e}")
                # Send a fresh message instead
                try:
                    await callback_query.message.answer(
                        "⚠️ Request timeout. Please try again.",
                        reply_markup=None
                    )
                except Exception as send_error:
                    logger.error(f"Failed to send timeout message: {send_error}")
            else:
                logger.error(f"Callback handler error in {original_handler.__name__}: {e}")
                await safe_callback_answer(callback_query, "An error occurred. Please try again.")
        except Exception as e:
            logger.error(f"Unexpected error in {original_handler.__name__}: {e}")
            await safe_callback_answer(callback_query, "An unexpected error occurred.")
    
    return wrapper

# Global error handler for all callback queries
async def global_callback_error_handler(callback_query: CallbackQuery, exception: Exception):
    """
    Global error handler for callback queries
    Prevents bot freezing from various callback errors
    """
    logger.error(f"Global callback error: {exception}")
    
    if isinstance(exception, TelegramBadRequest):
        if "query is too old" in str(exception) or "query ID is invalid" in str(exception):
            logger.warning("Callback query timeout - ignoring to prevent freezing")
            return
    
    # Try to inform user about the error
    try:
        await callback_query.answer("An error occurred. Please try again.", show_alert=True)
    except Exception as answer_error:
        logger.error(f"Failed to answer callback with error message: {answer_error}")