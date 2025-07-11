#!/usr/bin/env python3
"""
Animated Transition System for I3lani Bot
Provides smooth visual transitions between different bot stages and interactions
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from step_title_system import get_step_title, create_titled_message
from global_sequence_system import get_global_sequence_manager
from sequence_logger import get_sequence_logger

logger = get_sequence_logger(__name__)

class AnimatedTransitions:
    """Manages animated transitions between bot stages"""
    
    def __init__(self):
        self.transition_animations = {
            # Loading animations with different styles
            "loading_dots": ["⚪", "🔵", "🔵🔵", "🔵🔵🔵", "✅"],
            "loading_spinner": ["🌀", "🌀", "🌀", "✅"],
            "loading_progress": ["▫️▫️▫️", "▪️▫️▫️", "▪️▪️▫️", "▪️▪️▪️", "✅✅✅"],
            "loading_wave": ["〰️", "🌊", "🌊🌊", "✅"],
            
            # Stage-specific animations
            "menu_transition": ["🏠", "📋", "✨", "🎯"],
            "create_ad": ["✏️", "📝", "🎨", "📢"],
            "channel_selection": ["📺", "🔍", "✅", "📊"],
            "payment_processing": ["💳", "🔄", "⏳", "✅"],
            "publishing": ["📤", "🚀", "📡", "🎉"],
            
            # Language-specific animations
            "arabic_flow": ["🕌", "✨", "🌟", "✅"],
            "english_flow": ["🏛️", "✨", "🌟", "✅"],
            "russian_flow": ["🏰", "✨", "🌟", "✅"]
        }
        
        self.transition_messages = {
            "en": {
                "loading": "Loading...",
                "processing": "Processing...",
                "switching": "Switching to {}...",
                "preparing": "Preparing {}...",
                "finalizing": "Finalizing...",
                "complete": "Complete!"
            },
            "ar": {
                "loading": "جارٍ التحميل...",
                "processing": "جارٍ المعالجة...",
                "switching": "التبديل إلى {}...",
                "preparing": "جارٍ تحضير {}...",
                "finalizing": "اللمسة الأخيرة...",
                "complete": "تم!"
            },
            "ru": {
                "loading": "Загрузка...",
                "processing": "Обработка...",
                "switching": "Переход к {}...",
                "preparing": "Подготовка {}...",
                "finalizing": "Завершение...",
                "complete": "Готово!"
            }
        }
        
        self.stage_transitions = {
            "main_menu": {
                "animation": "menu_transition",
                "duration": 2.0,
                "steps": 4
            },
            "create_ad_start": {
                "animation": "create_ad",
                "duration": 2.5,
                "steps": 4
            },
            "select_channels": {
                "animation": "channel_selection", 
                "duration": 2.0,
                "steps": 4
            },
            "payment_processing": {
                "animation": "payment_processing",
                "duration": 3.0,
                "steps": 4
            },
            "publishing": {
                "animation": "publishing",
                "duration": 2.5,
                "steps": 4
            }
        }
    
    async def animate_stage_transition(self, 
                                     message_or_query: Union[Message, CallbackQuery],
                                     from_stage: str,
                                     to_stage: str,
                                     language: str = "en",
                                     user_id: int = None) -> bool:
        """Animate transition between two stages"""
        try:
            # Get bot and message objects
            if isinstance(message_or_query, CallbackQuery):
                bot = message_or_query.bot
                message = message_or_query.message
                chat_id = message.chat.id
            else:
                bot = message_or_query.bot
                message = message_or_query
                chat_id = message.chat.id
            
            # Get transition configuration
            transition_config = self.stage_transitions.get(to_stage, {
                "animation": "loading_dots",
                "duration": 2.0,
                "steps": 4
            })
            
            animation_frames = self.transition_animations[transition_config["animation"]]
            step_duration = transition_config["duration"] / len(animation_frames)
            
            # Get stage names for messages
            from_title = get_step_title(from_stage, language) if from_stage else ""
            to_title = get_step_title(to_stage, language)
            
            # Create transition message
            transition_text = self.transition_messages[language]["switching"].format(to_title)
            
            # Log transition start
            if user_id:
                manager = get_global_sequence_manager()
                sequence_id = manager.get_user_active_sequence(user_id)
                if sequence_id:
                    from sequence_logger import log_sequence_step
                    log_sequence_step(sequence_id, f"StageTransition_{from_stage}_to_{to_stage}", 
                                    "animated_transitions", {
                                        "from_stage": from_stage,
                                        "to_stage": to_stage,
                                        "language": language,
                                        "animation": transition_config["animation"]
                                    })
            
            # Animate through frames
            for i, frame in enumerate(animation_frames):
                if i == 0:
                    # First frame - show transition start
                    animated_text = f"{frame} {transition_text}"
                    
                    if isinstance(message_or_query, CallbackQuery):
                        await message.edit_text(animated_text)
                    else:
                        sent_message = await message.answer(animated_text)
                        message = sent_message
                        
                elif i == len(animation_frames) - 1:
                    # Last frame - transition complete
                    complete_text = f"{frame} {self.transition_messages[language]['complete']}"
                    await message.edit_text(complete_text)
                    
                else:
                    # Intermediate frames
                    animated_text = f"{frame} {transition_text}"
                    await message.edit_text(animated_text)
                
                # Wait for next frame
                if i < len(animation_frames) - 1:
                    await asyncio.sleep(step_duration)
            
            # Final pause before continuing
            await asyncio.sleep(0.5)
            
            logger.info(f"✅ Animated transition completed: {from_stage} → {to_stage}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in stage transition animation: {e}")
            return False
    
    async def animate_loading_sequence(self,
                                     message_or_query: Union[Message, CallbackQuery],
                                     operation: str,
                                     language: str = "en",
                                     animation_type: str = "loading_dots") -> bool:
        """Animate a loading sequence for operations"""
        try:
            # Get bot and message objects
            if isinstance(message_or_query, CallbackQuery):
                message = message_or_query.message
            else:
                message = message_or_query
            
            animation_frames = self.transition_animations.get(animation_type, 
                                                            self.transition_animations["loading_dots"])
            
            operation_text = self.transition_messages[language]["processing"]
            
            # Animate loading
            for i, frame in enumerate(animation_frames):
                if i == len(animation_frames) - 1:
                    # Last frame - complete
                    animated_text = f"{frame} {self.transition_messages[language]['complete']}"
                else:
                    animated_text = f"{frame} {operation_text}"
                
                if i == 0 and isinstance(message_or_query, Message):
                    # First frame for new message
                    sent_message = await message.answer(animated_text)
                    message = sent_message
                else:
                    await message.edit_text(animated_text)
                
                # Wait for next frame
                if i < len(animation_frames) - 1:
                    await asyncio.sleep(0.6)
            
            await asyncio.sleep(0.3)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in loading animation: {e}")
            return False
    
    async def fade_transition(self,
                            message: Message,
                            old_content: str,
                            new_content: str,
                            language: str = "en") -> bool:
        """Create a fade transition effect between content"""
        try:
            # Create fade frames
            fade_frames = [
                f"▓▓▓ {self.transition_messages[language]['loading']} ▓▓▓",
                f"▒▒▒ {self.transition_messages[language]['loading']} ▒▒▒",
                f"░░░ {self.transition_messages[language]['loading']} ░░░",
                f"⚪⚪⚪ {self.transition_messages[language]['finalizing']} ⚪⚪⚪"
            ]
            
            # Animate fade out
            for frame in fade_frames:
                await message.edit_text(frame)
                await asyncio.sleep(0.4)
            
            # Show new content
            await message.edit_text(new_content)
            
            logger.info("✅ Fade transition completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in fade transition: {e}")
            return False
    
    async def typing_simulation(self,
                              bot: Bot,
                              chat_id: int,
                              text: str,
                              duration: float = 2.0) -> bool:
        """Simulate typing with visual feedback"""
        try:
            # Send typing action
            await bot.send_chat_action(chat_id, "typing")
            
            # Create typing animation
            typing_frames = ["✏️", "✏️.", "✏️..", "✏️...", "✅"]
            frame_duration = duration / len(typing_frames)
            
            # Send initial typing message
            typing_msg = await bot.send_message(chat_id, f"{typing_frames[0]} {text}")
            
            # Animate typing
            for i, frame in enumerate(typing_frames[1:], 1):
                await typing_msg.edit_text(f"{frame} {text}")
                await asyncio.sleep(frame_duration)
            
            # Clean up typing message
            await typing_msg.delete()
            
            logger.info("✅ Typing simulation completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in typing simulation: {e}")
            return False
    
    async def progress_bar_animation(self,
                                   message: Message,
                                   operation: str,
                                   steps: int = 5,
                                   language: str = "en") -> bool:
        """Animate a progress bar for multi-step operations"""
        try:
            progress_frames = []
            for i in range(steps + 1):
                filled = "█" * i
                empty = "░" * (steps - i)
                percentage = int((i / steps) * 100)
                frame = f"[{filled}{empty}] {percentage}%"
                progress_frames.append(frame)
            
            operation_text = self.transition_messages[language]["processing"]
            
            # Animate progress bar
            for i, frame in enumerate(progress_frames):
                if i == 0:
                    text = f"{operation_text}\n{frame}"
                    sent_message = await message.answer(text)
                    message = sent_message
                else:
                    if i == len(progress_frames) - 1:
                        text = f"{self.transition_messages[language]['complete']}\n{frame}"
                    else:
                        text = f"{operation_text}\n{frame}"
                    
                    await message.edit_text(text)
                
                await asyncio.sleep(0.5)
            
            logger.info("✅ Progress bar animation completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in progress bar animation: {e}")
            return False
    
    async def stage_entry_animation(self,
                                  message_or_query: Union[Message, CallbackQuery],
                                  stage_key: str,
                                  content: str,
                                  language: str = "en",
                                  user_id: int = None,
                                  keyboard: Optional[InlineKeyboardMarkup] = None) -> bool:
        """Animate entry into a new stage with title and content"""
        try:
            # Get stage title
            stage_title = get_step_title(stage_key, language)
            
            # Create titled content
            if user_id:
                final_content = create_titled_message(stage_key, content, language, user_id)
            else:
                final_content = f"{stage_title}\n\n{content}"
            
            # Animate stage entry
            entry_frames = [
                f"🔄 {self.transition_messages[language]['preparing'].format(stage_title)}",
                f"⚡ {self.transition_messages[language]['loading']}",
                f"✨ {self.transition_messages[language]['finalizing']}",
                final_content
            ]
            
            # Get message object
            if isinstance(message_or_query, CallbackQuery):
                message = message_or_query.message
                is_callback = True
            else:
                message = message_or_query
                is_callback = False
            
            # Animate entry
            for i, frame in enumerate(entry_frames):
                if i == 0:
                    if is_callback:
                        await message.edit_text(frame)
                    else:
                        sent_message = await message.answer(frame)
                        message = sent_message
                elif i == len(entry_frames) - 1:
                    # Final frame with keyboard
                    if keyboard:
                        await message.edit_text(frame, reply_markup=keyboard, parse_mode='HTML')
                    else:
                        await message.edit_text(frame, parse_mode='HTML')
                else:
                    await message.edit_text(frame)
                
                # Wait between frames (except for last frame)
                if i < len(entry_frames) - 1:
                    await asyncio.sleep(0.6)
            
            logger.info(f"✅ Stage entry animation completed for: {stage_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in stage entry animation: {e}")
            return False
    
    def get_language_specific_animation(self, language: str) -> str:
        """Get language-specific animation style"""
        language_animations = {
            "ar": "arabic_flow",
            "en": "english_flow", 
            "ru": "russian_flow"
        }
        return language_animations.get(language, "english_flow")
    
    async def smooth_transition_with_callback(self,
                                            callback_query: CallbackQuery,
                                            new_content: str,
                                            keyboard: Optional[InlineKeyboardMarkup] = None,
                                            language: str = "en",
                                            stage_key: str = None) -> bool:
        """Smooth transition for callback queries with animation"""
        try:
            # Answer callback query first
            await callback_query.answer()
            
            # If stage_key provided, use stage entry animation
            if stage_key:
                user_id = callback_query.from_user.id
                return await self.stage_entry_animation(
                    callback_query, stage_key, new_content, language, user_id, keyboard
                )
            else:
                # Simple smooth transition
                transition_frame = f"🔄 {self.transition_messages[language]['loading']}"
                await callback_query.message.edit_text(transition_frame)
                await asyncio.sleep(0.5)
                
                if keyboard:
                    await callback_query.message.edit_text(new_content, reply_markup=keyboard, parse_mode='HTML')
                else:
                    await callback_query.message.edit_text(new_content, parse_mode='HTML')
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error in smooth callback transition: {e}")
            return False

# Global instance
animated_transitions = None

def get_animated_transitions() -> AnimatedTransitions:
    """Get global animated transitions instance"""
    global animated_transitions
    if animated_transitions is None:
        animated_transitions = AnimatedTransitions()
    return animated_transitions

# Convenience functions for common use cases
async def animate_to_stage(message_or_query: Union[Message, CallbackQuery],
                          to_stage: str,
                          content: str,
                          language: str = "en",
                          user_id: int = None,
                          keyboard: Optional[InlineKeyboardMarkup] = None,
                          from_stage: str = None) -> bool:
    """Animate transition to a new stage with content"""
    transitions = get_animated_transitions()
    
    # First animate the transition if from_stage provided
    if from_stage:
        await transitions.animate_stage_transition(
            message_or_query, from_stage, to_stage, language, user_id
        )
    
    # Then animate stage entry
    return await transitions.stage_entry_animation(
        message_or_query, to_stage, content, language, user_id, keyboard
    )

async def animate_loading(message_or_query: Union[Message, CallbackQuery],
                         operation: str,
                         language: str = "en",
                         animation_type: str = "loading_dots") -> bool:
    """Animate a loading operation"""
    transitions = get_animated_transitions()
    return await transitions.animate_loading_sequence(
        message_or_query, operation, language, animation_type
    )

async def smooth_callback_transition(callback_query: CallbackQuery,
                                   new_content: str,
                                   keyboard: Optional[InlineKeyboardMarkup] = None,
                                   language: str = "en",
                                   stage_key: str = None) -> bool:
    """Smooth transition for callback queries"""
    transitions = get_animated_transitions()
    return await transitions.smooth_transition_with_callback(
        callback_query, new_content, keyboard, language, stage_key
    )

if __name__ == "__main__":
    print("🎬 ANIMATED TRANSITIONS SYSTEM")
    print("=" * 40)
    
    transitions = get_animated_transitions()
    
    print(f"Available Animations: {len(transitions.transition_animations)}")
    print(f"Stage Transitions: {len(transitions.stage_transitions)}")
    print(f"Supported Languages: {list(transitions.transition_messages.keys())}")
    
    print("\n🎯 Animation Types:")
    for name, frames in transitions.transition_animations.items():
        print(f"  {name}: {' → '.join(frames)}")
    
    print("\n🎬 Animated Transitions System Ready")