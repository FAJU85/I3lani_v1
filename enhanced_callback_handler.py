"""
Enhanced callback handler with timeout protection and modern keyboard integration
Fixes the "query is too old" errors and provides smooth user experience
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from logger import log_success, log_error, log_info, StepNames

logger = logging.getLogger(__name__)

class EnhancedCallbackHandler:
    """
    Enhanced callback handler with timeout protection and graceful error handling
    Prevents "query is too old" errors and provides smooth user experience
    """
    
    def __init__(self):
        self.callback_cache: Dict[str, Dict] = {}
        self.last_cleanup = datetime.now()
        
    async def safe_callback_answer(self, callback_query: CallbackQuery, 
                                 text: str = None, 
                                 show_alert: bool = False,
                                 user_id: int = None) -> bool:
        """
        Safely answer callback query with timeout protection
        
        Args:
            callback_query: The callback query to answer
            text: Optional text to show
            show_alert: Whether to show as alert
            user_id: User ID for logging
            
        Returns:
            bool: True if successful, False if failed
        """
        try:
            # Check if callback is too old (more than 30 seconds)
            if self._is_callback_too_old(callback_query):
                if user_id:
                    log_info(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, 
                           "Callback query too old, skipping answer")
                return False
            
            # Try to answer the callback
            await callback_query.answer(text=text, show_alert=show_alert)
            
            if user_id:
                log_success(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, 
                          "Callback answered successfully")
            
            return True
            
        except TelegramBadRequest as e:
            if "query is too old" in str(e) or "query ID is invalid" in str(e):
                if user_id:
                    log_info(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, 
                           f"Callback timeout handled gracefully: {str(e)}")
                return False
            else:
                if user_id:
                    log_error(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, e)
                raise
                
        except Exception as e:
            if user_id:
                log_error(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, e)
            logger.error(f"Unexpected error in callback answer: {e}")
            return False
    
    async def safe_callback_edit(self, callback_query: CallbackQuery, 
                               text: str,
                               reply_markup=None,
                               parse_mode: str = None,
                               user_id: int = None) -> bool:
        """
        Safely edit callback query message with timeout protection
        
        Args:
            callback_query: The callback query
            text: New text content
            reply_markup: New keyboard markup
            parse_mode: Parse mode for text
            user_id: User ID for logging
            
        Returns:
            bool: True if successful, False if failed
        """
        try:
            # Check if callback is too old
            if self._is_callback_too_old(callback_query):
                if user_id:
                    log_info(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, 
                           "Callback too old, sending new message instead")
                
                # Send new message instead of editing
                await callback_query.message.chat.send_message(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
                return True
            
            # Try to edit the message
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            
            if user_id:
                log_success(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, 
                          "Message edited successfully")
            
            return True
            
        except TelegramBadRequest as e:
            if "query is too old" in str(e) or "query ID is invalid" in str(e):
                if user_id:
                    log_info(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, 
                           "Callback timeout, sending new message")
                
                # Send new message as fallback
                try:
                    await callback_query.message.chat.send_message(
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode=parse_mode
                    )
                    return True
                except Exception as fallback_error:
                    if user_id:
                        log_error(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, fallback_error)
                    return False
            else:
                if user_id:
                    log_error(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, e)
                raise
                
        except Exception as e:
            if user_id:
                log_error(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, e)
            logger.error(f"Unexpected error in callback edit: {e}")
            return False
    
    async def handle_callback_with_retry(self, callback_query: CallbackQuery, 
                                       handler_func: Callable,
                                       max_retries: int = 3,
                                       user_id: int = None) -> bool:
        """
        Handle callback with retry logic for better reliability
        
        Args:
            callback_query: The callback query
            handler_func: The handler function to execute
            max_retries: Maximum number of retries
            user_id: User ID for logging
            
        Returns:
            bool: True if successful, False if failed
        """
        for attempt in range(max_retries):
            try:
                # Answer the callback first
                await self.safe_callback_answer(callback_query, user_id=user_id)
                
                # Execute the handler
                await handler_func(callback_query)
                
                if user_id:
                    log_success(StepNames.ERROR_HANDLER, user_id, 
                              f"Callback handled successfully on attempt {attempt + 1}")
                
                return True
                
            except TelegramBadRequest as e:
                if "query is too old" in str(e) and attempt < max_retries - 1:
                    if user_id:
                        log_info(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, 
                               f"Callback timeout on attempt {attempt + 1}, retrying...")
                    
                    # Wait before retry
                    await asyncio.sleep(1)
                    continue
                else:
                    if user_id:
                        log_error(StepNames.ERROR_CALLBACK_TIMEOUT, user_id, e)
                    return False
                    
            except Exception as e:
                if user_id:
                    log_error(StepNames.ERROR_HANDLER, user_id, e)
                return False
        
        return False
    
    def _is_callback_too_old(self, callback_query: CallbackQuery) -> bool:
        """
        Check if callback query is too old (more than 30 seconds)
        
        Args:
            callback_query: The callback query to check
            
        Returns:
            bool: True if too old, False otherwise
        """
        try:
            # Get message date
            message_date = callback_query.message.date
            current_time = datetime.now()
            
            # Calculate age
            age = current_time - message_date
            
            # Consider callback too old if more than 30 seconds
            return age.total_seconds() > 30
            
        except Exception:
            # If we can't determine age, assume it's not too old
            return False
    
    def cache_callback_data(self, callback_id: str, data: Dict[str, Any]):
        """Cache callback data for recovery"""
        self.callback_cache[callback_id] = {
            'data': data,
            'timestamp': datetime.now()
        }
        
        # Clean old cache entries
        self._cleanup_cache()
    
    def get_cached_callback_data(self, callback_id: str) -> Optional[Dict[str, Any]]:
        """Get cached callback data"""
        cache_entry = self.callback_cache.get(callback_id)
        if cache_entry:
            # Check if cache is still valid (within 5 minutes)
            if datetime.now() - cache_entry['timestamp'] < timedelta(minutes=5):
                return cache_entry['data']
        return None
    
    def _cleanup_cache(self):
        """Clean up old cache entries"""
        now = datetime.now()
        
        # Only cleanup every 5 minutes
        if now - self.last_cleanup < timedelta(minutes=5):
            return
        
        # Remove entries older than 10 minutes
        cutoff_time = now - timedelta(minutes=10)
        keys_to_remove = [
            key for key, value in self.callback_cache.items()
            if value['timestamp'] < cutoff_time
        ]
        
        for key in keys_to_remove:
            del self.callback_cache[key]
        
        self.last_cleanup = now

# Global enhanced callback handler instance
enhanced_callback_handler = EnhancedCallbackHandler()

# Convenience functions
async def safe_answer_callback(callback_query: CallbackQuery, 
                             text: str = None, 
                             show_alert: bool = False,
                             user_id: int = None) -> bool:
    """Safely answer callback query"""
    return await enhanced_callback_handler.safe_callback_answer(
        callback_query, text, show_alert, user_id
    )

async def safe_edit_callback(callback_query: CallbackQuery, 
                           text: str,
                           reply_markup=None,
                           parse_mode: str = None,
                           user_id: int = None) -> bool:
    """Safely edit callback query message"""
    return await enhanced_callback_handler.safe_callback_edit(
        callback_query, text, reply_markup, parse_mode, user_id
    )

async def handle_callback_with_retry(callback_query: CallbackQuery, 
                                   handler_func: Callable,
                                   max_retries: int = 3,
                                   user_id: int = None) -> bool:
    """Handle callback with retry logic"""
    return await enhanced_callback_handler.handle_callback_with_retry(
        callback_query, handler_func, max_retries, user_id
    )

def cache_callback_data(callback_id: str, data: Dict[str, Any]):
    """Cache callback data"""
    enhanced_callback_handler.cache_callback_data(callback_id, data)

def get_cached_callback_data(callback_id: str) -> Optional[Dict[str, Any]]:
    """Get cached callback data"""
    return enhanced_callback_handler.get_cached_callback_data(callback_id)