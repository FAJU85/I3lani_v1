"""
Enhanced Bot Features for I3lani Bot
Provides additional dynamic features and improvements
"""

import asyncio
from typing import Optional, Dict, List
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

class BotEnhancements:
    """Dynamic enhancements for better user experience"""
    
    @staticmethod
    async def send_progress_bar(message: Message, progress: int, total: int, text: str = "Processing") -> Optional[Message]:
        """Send or update a progress bar"""
        filled = int((progress / total) * 10)
        bar = "█" * filled + "░" * (10 - filled)
        percentage = int((progress / total) * 100)
        
        progress_text = f"""
{text}...

[{bar}] {percentage}%
{progress}/{total} completed
        """.strip()
        
        try:
            return await message.answer(progress_text)
        except Exception as e:
            logger.error(f"Error sending progress bar: {e}")
            return None
    
    @staticmethod
    async def update_progress_bar(msg: Message, progress: int, total: int, text: str = "Processing"):
        """Update existing progress bar message"""
        filled = int((progress / total) * 10)
        bar = "█" * filled + "░" * (10 - filled)
        percentage = int((progress / total) * 100)
        
        progress_text = f"""
{text}...

[{bar}] {percentage}%
{progress}/{total} completed
        """.strip()
        
        try:
            await msg.edit_text(progress_text)
        except Exception as e:
            logger.debug(f"Could not update progress bar: {e}")
    
    @staticmethod
    async def send_typing_animation(bot: Bot, chat_id: int, duration: float = 1.0):
        """Send typing animation for specified duration"""
        try:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(duration)
        except Exception as e:
            logger.debug(f"Could not send typing animation: {e}")
    
    @staticmethod
    async def create_dynamic_keyboard(buttons: List[Dict], columns: int = 2) -> InlineKeyboardMarkup:
        """Create dynamic keyboard with auto-layout"""
        keyboard_rows = []
        current_row = []
        
        for button in buttons:
            btn = InlineKeyboardButton(
                text=button.get('text', ''),
                callback_data=button.get('callback_data', '')
            )
            current_row.append(btn)
            
            if len(current_row) >= columns:
                keyboard_rows.append(current_row)
                current_row = []
        
        # Add remaining buttons
        if current_row:
            keyboard_rows.append(current_row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    @staticmethod
    async def send_countdown_timer(message: Message, seconds: int, text: str = "Time remaining"):
        """Send countdown timer message"""
        timer_msg = await message.answer(f"⏰ {text}: {seconds} seconds")
        
        for remaining in range(seconds - 1, -1, -1):
            await asyncio.sleep(1)
            try:
                await timer_msg.edit_text(f"⏰ {text}: {remaining} seconds")
            except:
                break
        
        return timer_msg
    
    @staticmethod
    async def animate_success(message: Message, success_text: str = "Success!"):
        """Animate success message"""
        animations = ["✨", "🎉", "✅", "🎊", "🌟"]
        
        msg = await message.answer(animations[0])
        
        for emoji in animations[1:]:
            await asyncio.sleep(0.3)
            try:
                await msg.edit_text(emoji)
            except:
                break
        
        await asyncio.sleep(0.3)
        try:
            await msg.edit_text(f"✅ **{success_text}**", parse_mode='Markdown')
        except:
            pass
        
        return msg
    
    @staticmethod
    async def smart_error_handler(
        callback_query: CallbackQuery,
        error_type: str,
        retry_action: Optional[str] = None,
        support_link: str = "@i3lani_support"
    ):
        """Smart error handling with context-aware messages"""
        error_messages = {
            'payment': "Payment processing error. Please check your payment details.",
            'network': "Network connection error. Please check your internet connection.",
            'channel': "Channel access error. The bot may not have admin rights.",
            'database': "Database error. Please try again in a few moments.",
            'general': "An unexpected error occurred. Please try again."
        }
        
        error_text = error_messages.get(error_type, error_messages['general'])
        
        keyboard_buttons = []
        if retry_action:
            keyboard_buttons.append([
                InlineKeyboardButton(text="🔄 Try Again", callback_data=retry_action)
            ])
        
        keyboard_buttons.extend([
            [InlineKeyboardButton(text="💬 Contact Support", url=f"https://t.me/{support_link.replace('@', '')}")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        full_error_text = f"""
❌ **Error**

{error_text}

What would you like to do?
        """.strip()
        
        try:
            await callback_query.message.edit_text(
                full_error_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            await callback_query.answer("Error occurred", show_alert=True)
        except Exception as e:
            logger.error(f"Error in smart error handler: {e}")
    
    @staticmethod
    async def create_step_indicator(current_step: int, total_steps: int, labels: Optional[List[str]] = None) -> str:
        """Create visual step indicator"""
        if not labels:
            labels = [f"Step {i+1}" for i in range(total_steps)]
        
        indicator = "📍 **Progress**\n\n"
        
        for i in range(total_steps):
            if i < current_step - 1:
                indicator += "✅ "
            elif i == current_step - 1:
                indicator += "🔵 "
            else:
                indicator += "⭕ "
            
            indicator += labels[i]
            
            if i < total_steps - 1:
                indicator += " → "
        
        return indicator
    
    @staticmethod
    async def format_money_display(amount: float, currency: str = "USD") -> str:
        """Format money amounts with proper display"""
        currency_symbols = {
            'USD': '$',
            'TON': '💎',
            'STARS': '⭐'
        }
        
        symbol = currency_symbols.get(currency, currency)
        
        if currency == 'STARS':
            return f"{int(amount):,} {symbol}"
        else:
            return f"{symbol}{amount:,.2f}"
    
    @staticmethod
    async def create_confirmation_dialog(
        message: Message,
        question: str,
        confirm_callback: str,
        cancel_callback: str,
        warning: Optional[str] = None
    ) -> Message:
        """Create confirmation dialog with warning"""
        text = f"❓ **{question}**"
        
        if warning:
            text += f"\n\n⚠️ _{warning}_"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes", callback_data=confirm_callback),
                InlineKeyboardButton(text="❌ No", callback_data=cancel_callback)
            ]
        ])
        
        return await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')


# Export enhancements
enhancements = BotEnhancements()