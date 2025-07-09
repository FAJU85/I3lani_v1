"""
Haptic & Visual Effects System for I3lani Bot
Enhances user experience with interactive feedback
"""

import asyncio
import logging
import random
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InputFile, FSInputFile
from aiogram.enums import ParseMode
from database import db, get_user_language
from languages import get_text

logger = logging.getLogger(__name__)

class HapticVisualEffects:
    """Handles haptic feedback and visual effects for bot interactions"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.effect_cache = {}
        self.sticker_packs = {
            'success': [
                'CAACAgIAAxkBAAEBCiJjKQABqwABh4IAAUGwAAEAAhQAAYMAAhgAAgABYwABiQABmQABHwABAg',
                'CAACAgIAAxkBAAEBCiNjKQABqwABh4IAAUGwAAEAAhQAAYMAAhkAAgABYwABiQABmQABHwABAg',
            ],
            'celebration': [
                'CAACAgIAAxkBAAEBCiRjKQABqwABh4IAAUGwAAEAAhQAAYMAAhoAAgABYwABiQABmQABHwABAg',
                'CAACAgIAAxkBAAEBCiVjKQABqwABh4IAAUGwAAEAAhQAAYMAAhsAAgABYwABiQABmQABHwABAg',
            ],
            'thinking': [
                'CAACAgIAAxkBAAEBCiZjKQABqwABh4IAAUGwAAEAAhQAAYMAAhwAAgABYwABiQABmQABHwABAg',
            ],
            'motivational': [
                'CAACAgIAAxkBAAEBCidjKQABqwABh4IAAUGwAAEAAhQAAYMAAh0AAgABYwABiQABmQABHwABAg',
                'CAACAgIAAxkBAAEBCihjKQABqwABh4IAAUGwAAEAAhQAAYMAAh4AAgABYwABiQABmQABHwABAg',
            ],
            'reward': [
                'CAACAgIAAxkBAAEBCiljKQABqwABh4IAAUGwAAEAAhQAAYMAAh8AAgABYwABiQABmQABHwABAg',
                'CAACAgIAAxkBAAEBCikjKQABqwABh4IAAUGwAAEAAhQAAYMAAiAAAgABYwABiQABmQABHwABAg',
            ]
        }
    
    async def create_haptic_keyboard(self, buttons: list, effect_type: str = 'default') -> InlineKeyboardMarkup:
        """Create keyboard with haptic feedback effects"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for row in buttons:
            keyboard_row = []
            for button in row:
                # Add haptic effect data to callback
                callback_data = button.get('callback_data', '')
                if callback_data:
                    callback_data = f"haptic_{effect_type}_{callback_data}"
                
                # Apply visual styling based on effect type
                text = self._apply_visual_effects(button.get('text', ''), effect_type)
                
                keyboard_row.append(InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                ))
            keyboard.inline_keyboard.append(keyboard_row)
        
        return keyboard
    
    def _apply_visual_effects(self, text: str, effect_type: str) -> str:
        """Apply visual effects to button text"""
        effects = {
            'glow': f"✨ {text} ✨",
            'pulse': f"💫 {text} 💫",
            'shimmer': f"🌟 {text} 🌟",
            'highlight': f"🔥 {text} 🔥",
            'success': f"✅ {text} ✅",
            'reward': f"🎁 {text} 🎁",
            'game': f"🎮 {text} 🎮",
            'payment': f"💳 {text} 💳",
            'default': text
        }
        return effects.get(effect_type, text)
    
    async def send_haptic_message(self, chat_id: int, text: str, keyboard: InlineKeyboardMarkup = None, 
                                 effect_type: str = 'default', auto_sticker: str = None) -> Message:
        """Send message with haptic feedback and visual effects"""
        try:
            # Apply text effects
            enhanced_text = self._enhance_message_text(text, effect_type)
            
            # Send optional sticker first
            if auto_sticker and auto_sticker in self.sticker_packs:
                sticker_id = random.choice(self.sticker_packs[auto_sticker])
                try:
                    await self.bot.send_sticker(chat_id, sticker_id)
                except Exception as e:
                    logger.warning(f"Failed to send sticker: {e}")
            
            # Send main message
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=enhanced_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Trigger haptic feedback simulation
            await self._simulate_haptic_feedback(chat_id, effect_type)
            
            return message
            
        except Exception as e:
            logger.error(f"Error sending haptic message: {e}")
            # Fallback to normal message
            return await self.bot.send_message(chat_id, text, reply_markup=keyboard)
    
    def _enhance_message_text(self, text: str, effect_type: str) -> str:
        """Enhance message text with visual effects"""
        enhancements = {
            'success': f"🎉 **SUCCESS** 🎉\n\n{text}",
            'celebration': f"🎊 **CELEBRATION** 🎊\n\n{text}",
            'reward': f"🏆 **REWARD UNLOCKED** 🏆\n\n{text}",
            'game': f"🎮 **GAME MODE** 🎮\n\n{text}",
            'payment': f"💳 **PAYMENT** 💳\n\n{text}",
            'progress': f"📊 **PROGRESS** 📊\n\n{text}",
            'default': text
        }
        return enhancements.get(effect_type, text)
    
    async def _simulate_haptic_feedback(self, chat_id: int, effect_type: str):
        """Simulate haptic feedback through visual cues"""
        try:
            # Different feedback patterns for different effects
            patterns = {
                'button_press': [0.1],
                'success': [0.1, 0.1, 0.2],
                'celebration': [0.1, 0.1, 0.1, 0.3],
                'reward': [0.2, 0.2, 0.4],
                'game': [0.1, 0.2, 0.1],
                'payment': [0.3],
                'default': [0.1]
            }
            
            pattern = patterns.get(effect_type, [0.1])
            
            # Create visual feedback through typing indicators
            for duration in pattern:
                await self.bot.send_chat_action(chat_id, 'typing')
                await asyncio.sleep(duration)
                
        except Exception as e:
            logger.warning(f"Haptic feedback simulation failed: {e}")
    
    async def handle_haptic_callback(self, callback_query: CallbackQuery):
        """Handle callbacks with haptic effects"""
        try:
            # Parse haptic data from callback
            data = callback_query.data
            if not data.startswith('haptic_'):
                return False
            
            parts = data.split('_', 2)
            if len(parts) < 3:
                return False
            
            effect_type = parts[1]
            original_callback = parts[2]
            
            # Provide immediate haptic feedback
            await self._simulate_haptic_feedback(callback_query.message.chat.id, effect_type)
            
            # Update callback data for further processing
            callback_query.data = original_callback
            
            # Add visual effect to button press
            await self._show_button_press_effect(callback_query, effect_type)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling haptic callback: {e}")
            return False
    
    async def _show_button_press_effect(self, callback_query: CallbackQuery, effect_type: str):
        """Show visual effect when button is pressed"""
        try:
            # Create temporary visual feedback
            user_id = callback_query.from_user.id
            language = await get_user_language(user_id)
            
            feedback_messages = {
                'glow': await get_text('button_pressed_glow', language, '✨ Button activated ✨'),
                'pulse': await get_text('button_pressed_pulse', language, '💫 Processing... 💫'),
                'shimmer': await get_text('button_pressed_shimmer', language, '🌟 Loading... 🌟'),
                'success': await get_text('button_pressed_success', language, '✅ Success! ✅'),
                'reward': await get_text('button_pressed_reward', language, '🎁 Reward! 🎁'),
                'game': await get_text('button_pressed_game', language, '🎮 Game mode! 🎮'),
                'payment': await get_text('button_pressed_payment', language, '💳 Processing payment... 💳'),
                'default': await get_text('button_pressed_default', language, '⚡ Processing... ⚡')
            }
            
            feedback = feedback_messages.get(effect_type, feedback_messages['default'])
            
            # Show temporary feedback
            if hasattr(callback_query, 'answer'):
                await callback_query.answer(feedback, show_alert=False)
            else:
                logger.warning("Callback query does not have answer method")
            
        except Exception as e:
            logger.warning(f"Button press effect failed: {e}")
            await callback_query.answer()
    
    async def create_progress_bar_effect(self, current: int, total: int, width: int = 20) -> str:
        """Create animated progress bar with visual effects"""
        try:
            percentage = (current / total) * 100
            filled = int((current / total) * width)
            
            # Create progress bar with effects
            bar = ""
            for i in range(width):
                if i < filled:
                    if i == filled - 1:  # Last filled position gets special effect
                        bar += "🔥"
                    else:
                        bar += "🟢"
                else:
                    bar += "⬜"
            
            return f"📊 **Progress: {percentage:.1f}%**\n\n{bar}\n\n💫 {current}/{total} completed"
            
        except Exception as e:
            logger.error(f"Error creating progress bar: {e}")
            return f"Progress: {current}/{total}"
    
    async def send_celebration_effect(self, chat_id: int, message: str, celebration_type: str = 'success'):
        """Send celebration message with full effects"""
        try:
            # Send celebration sticker
            await self.send_haptic_message(
                chat_id=chat_id,
                text=message,
                effect_type='celebration',
                auto_sticker=celebration_type
            )
            
            # Additional celebration effects
            if celebration_type == 'reward':
                await asyncio.sleep(0.5)
                await self.bot.send_message(
                    chat_id,
                    "🎊🎉🎊🎉🎊🎉🎊🎉🎊\n**CONGRATULATIONS!**\n🎊🎉🎊🎉🎊🎉🎊🎉🎊"
                )
            
        except Exception as e:
            logger.error(f"Celebration effect failed: {e}")
    
    async def create_payment_effect_keyboard(self, buttons: list, language: str) -> InlineKeyboardMarkup:
        """Create payment keyboard with special effects"""
        enhanced_buttons = []
        
        for row in buttons:
            enhanced_row = []
            for button in row:
                # Enhance payment buttons
                text = button.get('text', '')
                callback = button.get('callback_data', '')
                
                if 'ton' in callback.lower():
                    text = f"💎 {text} 💎"
                elif 'stars' in callback.lower():
                    text = f"⭐ {text} ⭐"
                elif 'cancel' in callback.lower():
                    text = f"❌ {text} ❌"
                else:
                    text = f"💳 {text} 💳"
                
                enhanced_row.append({
                    'text': text,
                    'callback_data': callback
                })
            enhanced_buttons.append(enhanced_row)
        
        return await self.create_haptic_keyboard(enhanced_buttons, 'payment')
    
    async def create_game_effect_keyboard(self, buttons: list, language: str) -> InlineKeyboardMarkup:
        """Create game keyboard with special effects"""
        enhanced_buttons = []
        
        for row in buttons:
            enhanced_row = []
            for button in row:
                text = button.get('text', '')
                callback = button.get('callback_data', '')
                
                # Add game-specific effects
                if 'tap' in callback.lower():
                    text = f"🎯 {text} 🎯"
                elif 'progress' in callback.lower():
                    text = f"📊 {text} 📊"
                elif 'reward' in callback.lower():
                    text = f"🏆 {text} 🏆"
                elif 'share' in callback.lower():
                    text = f"🔗 {text} 🔗"
                else:
                    text = f"🎮 {text} 🎮"
                
                enhanced_row.append({
                    'text': text,
                    'callback_data': callback
                })
            enhanced_buttons.append(enhanced_row)
        
        return await self.create_haptic_keyboard(enhanced_buttons, 'game')

# Global instance
haptic_effects = None

def get_haptic_effects(bot: Bot = None) -> HapticVisualEffects:
    """Get global haptic effects instance"""
    global haptic_effects
    if haptic_effects is None and bot:
        haptic_effects = HapticVisualEffects(bot)
    return haptic_effects

async def send_enhanced_message(bot: Bot, chat_id: int, text: str, keyboard: InlineKeyboardMarkup = None, 
                               effect_type: str = 'default', auto_sticker: str = None) -> Message:
    """Convenience function for sending enhanced messages"""
    effects = get_haptic_effects(bot)
    if effects:
        return await effects.send_haptic_message(chat_id, text, keyboard, effect_type, auto_sticker)
    else:
        return await bot.send_message(chat_id, text, reply_markup=keyboard)