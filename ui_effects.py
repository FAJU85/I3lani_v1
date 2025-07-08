"""
Dynamic UI Effects for I3lani Bot
Telegram-compatible hover-like effects and visual feedback
"""

import asyncio
import random
from typing import Optional, List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from languages import get_text

class UIEffects:
    """Handle dynamic UI effects and visual feedback"""
    
    def __init__(self):
        self.loading_frames = ["⏳", "⌛", "⏳", "⌛"]
        self.progress_chars = ["▱", "▰"]
        
    async def show_loading_animation(self, message: Message, text: str, duration: int = 3):
        """Show loading animation by editing message"""
        for i in range(duration * 2):
            frame = self.loading_frames[i % len(self.loading_frames)]
            try:
                await message.edit_text(f"{frame} {text}")
                await asyncio.sleep(0.5)
            except:
                break
    
    async def show_progress_bar(self, message: Message, current: int, total: int, text: str):
        """Show progress bar animation"""
        percentage = int((current / total) * 10)
        bar = "".join([self.progress_chars[1] if i < percentage else self.progress_chars[0] for i in range(10)])
        progress_text = f"{text}\n\n{bar} {current}/{total} ({int(current/total*100)}%)"
        
        try:
            await message.edit_text(progress_text)
        except:
            pass
    
    def create_animated_keyboard(self, language: str, buttons_data: List[dict], highlight_callback: str = None) -> InlineKeyboardMarkup:
        """Create keyboard with visual highlighting for active buttons"""
        keyboard_rows = []
        
        for row_data in buttons_data:
            row = []
            for button_data in row_data:
                text = button_data['text']
                callback = button_data['callback']
                
                # Add visual highlight for active button
                if callback == highlight_callback:
                    text = f"► {text} ◄"  # Visual highlight
                
                row.append(InlineKeyboardButton(text=text, callback_data=callback))
            keyboard_rows.append(row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    async def button_press_feedback(self, callback_query: CallbackQuery, feedback_text: str):
        """Show immediate feedback when button is pressed"""
        await callback_query.answer(feedback_text, show_alert=False)
    
    async def success_animation(self, message: Message, success_text: str):
        """Show success animation"""
        frames = [
            f"✨ {success_text}",
            f"⭐ {success_text}",
            f"🌟 {success_text}",
            f"✅ {success_text}"
        ]
        
        for frame in frames:
            try:
                await message.edit_text(frame)
                await asyncio.sleep(0.5)
            except:
                break
    
    async def error_shake_effect(self, message: Message, error_text: str):
        """Simulate shake effect for errors"""
        shake_frames = [
            f"❌ {error_text}",
            f"⚠️ {error_text}",
            f"❌ {error_text}",
            f"🔄 {error_text}"
        ]
        
        for frame in shake_frames:
            try:
                await message.edit_text(frame)
                await asyncio.sleep(0.3)
            except:
                break
    
    def create_dynamic_menu_text(self, base_text: str, user_stats: dict = None) -> str:
        """Create dynamic menu text with animated elements"""
        
        # Add pulsing effect indicators
        pulse_chars = ["◆", "◇", "◆", "◇"]
        pulse = pulse_chars[random.randint(0, 3)]
        
        # Add dynamic status indicators
        status_indicators = [
            "🟢 ONLINE",
            "🔥 ACTIVE", 
            "⚡ READY",
            "✨ OPTIMIZED"
        ]
        status = status_indicators[random.randint(0, 3)]
        
        enhanced_text = f"""
{pulse} <b>I3lani Dynamic Interface</b> {pulse}

<b>Status:</b> {status}
<b>Connection:</b> 🌐 STABLE

{base_text}

<i>💡 Tip: Click any button for instant action!</i>
        """.strip()
        
        return enhanced_text
    
    def create_hover_keyboard(self, language: str, buttons: List[dict], active_button: str = None) -> InlineKeyboardMarkup:
        """Create keyboard with hover-like visual effects"""
        keyboard_rows = []
        
        for button_row in buttons:
            row = []
            for button in button_row:
                text = button['text']
                callback = button['callback']
                
                # Add visual effects based on button type
                if 'primary' in button.get('type', ''):
                    text = f"🚀 {text}"
                elif 'success' in button.get('type', ''):
                    text = f"✅ {text}"
                elif 'warning' in button.get('type', ''):
                    text = f"⚠️ {text}"
                elif 'info' in button.get('type', ''):
                    text = f"ℹ️ {text}"
                
                # Highlight active button
                if callback == active_button:
                    text = f"🔸 {text} 🔸"
                
                row.append(InlineKeyboardButton(text=text, callback_data=callback))
            keyboard_rows.append(row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    async def typing_simulation(self, bot, chat_id: int, text: str, typing_speed: float = 0.1):
        """Simulate typing effect by sending chat action"""
        await bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Calculate typing duration based on text length
        typing_duration = len(text) * typing_speed
        if typing_duration > 5:  # Max 5 seconds
            typing_duration = 5
        elif typing_duration < 1:  # Min 1 second
            typing_duration = 1
            
        await asyncio.sleep(typing_duration)
    
    def add_button_animations(self, buttons: List[dict], interaction_type: str = 'default') -> List[dict]:
        """Add animation indicators to buttons"""
        animated_buttons = []
        
        for button in buttons:
            animated_button = button.copy()
            
            if interaction_type == 'loading':
                animated_button['text'] = f"⏳ {button['text']}"
            elif interaction_type == 'success':
                animated_button['text'] = f"✅ {button['text']}"
            elif interaction_type == 'processing':
                animated_button['text'] = f"🔄 {button['text']}"
            elif interaction_type == 'highlight':
                animated_button['text'] = f"🔥 {button['text']}"
            
            animated_buttons.append(animated_button)
        
        return animated_buttons
    
    async def fade_transition(self, message: Message, old_text: str, new_text: str):
        """Create fade-like transition effect"""
        transition_frames = [
            old_text,
            "━━━ ⚡ UPDATING ⚡ ━━━",
            "━━━ ✨ LOADING ✨ ━━━",
            new_text
        ]
        
        for frame in transition_frames:
            try:
                await message.edit_text(frame, parse_mode='HTML')
                await asyncio.sleep(0.4)
            except:
                pass
    
    def create_pulsing_text(self, text: str, pulse_char: str = "✨") -> str:
        """Add pulsing effect to text"""
        return f"{pulse_char} {text} {pulse_char}"
    
    def create_gradient_border(self, text: str) -> str:
        """Create gradient-like border effect"""
        border_chars = ["◢", "━", "◣", "┃", "◥", "━", "◤", "┃"]
        border = "".join(border_chars)
        
        return f"""
{border}
  {text}
{border}
        """.strip()

# Global UI effects instance
ui_effects = UIEffects()