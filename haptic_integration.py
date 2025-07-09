"""
Haptic Integration for I3lani Bot
Integrates haptic and visual effects into existing handlers
"""

import logging
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from haptic_visual_effects import get_haptic_effects, send_enhanced_message
from enhanced_keyboard_effects import create_enhanced_keyboard
from sticker_manager import get_sticker_manager, send_auto_sticker

logger = logging.getLogger(__name__)

class HapticIntegration:
    """Integrates haptic effects into bot handlers"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.haptic_effects = get_haptic_effects(bot)
        self.sticker_manager = get_sticker_manager(bot)
    
    async def handle_haptic_callback(self, callback_query: CallbackQuery):
        """Handle all haptic callback queries"""
        try:
            # Check if this is a haptic callback
            if not callback_query.data.startswith('haptic_'):
                return False
            
            # Process haptic effects
            await self.haptic_effects.handle_haptic_callback(callback_query)
            
            # Extract original callback data
            parts = callback_query.data.split('_', 2)
            if len(parts) >= 3:
                effect_type = parts[1]
                original_callback = parts[2]
                
                # Send contextual sticker
                await self._send_contextual_sticker(callback_query.message.chat.id, effect_type, original_callback)
                
                # Update callback for further processing
                callback_query.data = original_callback
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling haptic callback: {e}")
            return False
    
    async def _send_contextual_sticker(self, chat_id: int, effect_type: str, callback_data: str):
        """Send contextual sticker based on effect type and callback"""
        try:
            sticker_context = self._get_sticker_context(effect_type, callback_data)
            if sticker_context:
                await self.sticker_manager.send_context_sticker(chat_id, sticker_context)
        except Exception as e:
            logger.warning(f"Failed to send contextual sticker: {e}")
    
    def _get_sticker_context(self, effect_type: str, callback_data: str) -> str:
        """Determine sticker context based on effect and callback"""
        # Map effect types to sticker contexts
        effect_mapping = {
            'success': 'success',
            'celebration': 'celebration',
            'reward': 'reward',
            'payment': 'payment',
            'game': 'game',
            'glow': 'motivational',
            'pulse': 'thinking',
            'shimmer': 'success',
            'highlight': 'motivational'
        }
        
        # Map callback data to specific contexts
        if 'payment' in callback_data:
            return 'payment'
        elif 'create_ad' in callback_data:
            return 'motivational'
        elif 'reward' in callback_data:
            return 'reward'
        elif 'game' in callback_data or 'viral' in callback_data:
            return 'game'
        elif 'success' in callback_data:
            return 'success'
        
        return effect_mapping.get(effect_type, 'success')
    
    async def send_enhanced_main_menu(self, chat_id: int, language: str):
        """Send enhanced main menu with haptic effects"""
        try:
            # Create enhanced keyboard
            keyboard = create_enhanced_keyboard('main_menu', language)
            
            # Enhanced welcome message
            welcome_text = f"""
🎯 **I3lani Advertising Platform**
✨ *Professional advertising made simple* ✨

🚀 **Platform Features:**
• 💫 Smart ad creation tools
• 📈 Multi-channel distribution  
• 💎 Real-time analytics
• 🔥 Professional targeting

💼 **Ready to grow your business?**
            """
            
            # Send with haptic effects
            await send_enhanced_message(
                bot=self.bot,
                chat_id=chat_id,
                text=welcome_text,
                keyboard=keyboard,
                effect_type='glow',
                auto_sticker='welcome'
            )
            
        except Exception as e:
            logger.error(f"Error sending enhanced main menu: {e}")
    
    async def send_enhanced_payment_menu(self, chat_id: int, language: str, payment_data: dict):
        """Send enhanced payment menu with haptic effects"""
        try:
            # Create enhanced payment keyboard
            keyboard = create_enhanced_keyboard('payment', language)
            
            # Enhanced payment text
            payment_text = f"""
💳 **Payment Protocol Activated**

🎯 **Campaign Details:**
• Duration: {payment_data.get('duration', 'N/A')} days
• Channels: {payment_data.get('channels', 'N/A')}
• Total Posts: {payment_data.get('total_posts', 'N/A')}
• Total Cost: ${payment_data.get('total_cost', 'N/A')}

💎 **Select your payment method:**
            """
            
            # Send with payment effects
            await send_enhanced_message(
                bot=self.bot,
                chat_id=chat_id,
                text=payment_text,
                keyboard=keyboard,
                effect_type='payment',
                auto_sticker='payment'
            )
            
        except Exception as e:
            logger.error(f"Error sending enhanced payment menu: {e}")
    
    async def send_enhanced_viral_game(self, chat_id: int, language: str, user_data: dict):
        """Send enhanced viral game interface with haptic effects"""
        try:
            progress = user_data.get('progress', 0)
            referral_count = user_data.get('referral_count', 0)
            
            # Create enhanced game keyboard
            keyboard = create_enhanced_keyboard('viral_game', language, progress=progress)
            
            # Enhanced game text
            if progress < 99:
                game_text = f"""
🎮 **Viral Referral Game**

📊 **Your Progress:**
{await self.haptic_effects.create_progress_bar_effect(progress, 100)}

🎯 **How to Play:**
• Tap the button to build progress
• Reach 99% to unlock referral system
• Invite 3 friends to win 1 month free ads!

💫 **Keep going - you're doing great!**
                """
            else:
                game_text = f"""
🏆 **Progress Complete!**

✅ **Status:** Ready for referrals
👥 **Friends Invited:** {referral_count}/3
🎁 **Free Ads:** {'Unlocked!' if referral_count >= 3 else 'Not yet unlocked'}

🔗 **Share your link and invite friends!**
                """
            
            # Send with game effects
            await send_enhanced_message(
                bot=self.bot,
                chat_id=chat_id,
                text=game_text,
                keyboard=keyboard,
                effect_type='game',
                auto_sticker='game'
            )
            
        except Exception as e:
            logger.error(f"Error sending enhanced viral game: {e}")
    
    async def send_enhanced_success_message(self, chat_id: int, language: str, success_type: str, message: str):
        """Send enhanced success message with celebration effects"""
        try:
            # Create celebration keyboard
            keyboard = create_enhanced_keyboard('celebration', language, celebration_type=success_type)
            
            # Enhanced success text
            success_text = f"""
🎉 **{success_type.upper()} ACHIEVED!** 🎉

✨ {message} ✨

🎊 **Congratulations!** 🎊
            """
            
            # Send with celebration effects
            await send_enhanced_message(
                bot=self.bot,
                chat_id=chat_id,
                text=success_text,
                keyboard=keyboard,
                effect_type='celebration',
                auto_sticker='celebration'
            )
            
            # Send celebration sticker sequence
            await self.sticker_manager.send_celebration_sequence(chat_id, success_type)
            
        except Exception as e:
            logger.error(f"Error sending enhanced success message: {e}")
    
    async def send_enhanced_channel_selection(self, chat_id: int, language: str, channels: list, selected: list):
        """Send enhanced channel selection with haptic effects"""
        try:
            # Create enhanced channel keyboard
            keyboard = create_enhanced_keyboard('channel_selection', language, 
                                              channels=channels, selected_channels=selected)
            
            # Enhanced channel text
            total_reach = sum(channel.get('subscribers', 0) for channel in channels)
            selected_reach = sum(channel.get('subscribers', 0) for channel in channels 
                               if channel.get('id') in selected)
            
            channel_text = f"""
📡 **Channel Selection Hub**

🎯 **Available Channels:** {len(channels)}
📊 **Total Reach:** {total_reach:,} subscribers
✅ **Selected:** {len(selected)} channels
🎪 **Selected Reach:** {selected_reach:,} subscribers

💫 **Choose your broadcasting channels:**
            """
            
            # Send with shimmer effects
            await send_enhanced_message(
                bot=self.bot,
                chat_id=chat_id,
                text=channel_text,
                keyboard=keyboard,
                effect_type='shimmer',
                auto_sticker='thinking'
            )
            
        except Exception as e:
            logger.error(f"Error sending enhanced channel selection: {e}")
    
    async def send_enhanced_duration_selection(self, chat_id: int, language: str, current_days: int = 1):
        """Send enhanced duration selection with haptic effects"""
        try:
            # Create enhanced duration keyboard
            keyboard = create_enhanced_keyboard('duration', language)
            
            # Enhanced duration text
            duration_text = f"""
⏰ **Duration Selection**

📅 **Current Selection:** {current_days} days
💰 **Estimated Cost:** ${current_days * 1.0:.2f}
📈 **Posts Per Day:** {min(current_days, 20)}

🎯 **Adjust your campaign duration:**
            """
            
            # Send with pulse effects
            await send_enhanced_message(
                bot=self.bot,
                chat_id=chat_id,
                text=duration_text,
                keyboard=keyboard,
                effect_type='pulse',
                auto_sticker='thinking'
            )
            
        except Exception as e:
            logger.error(f"Error sending enhanced duration selection: {e}")
    
    async def send_enhanced_confirmation(self, chat_id: int, language: str, action_type: str, details: dict):
        """Send enhanced confirmation dialog with haptic effects"""
        try:
            # Create enhanced confirmation keyboard
            keyboard = create_enhanced_keyboard('confirmation', language, action_type=action_type)
            
            # Enhanced confirmation text
            confirmation_text = f"""
⚠️ **Confirmation Required**

🎯 **Action:** {action_type.title()}
📋 **Details:**
            """
            
            # Add details
            for key, value in details.items():
                confirmation_text += f"• {key.title()}: {value}\n"
            
            confirmation_text += f"""
❗ **This action cannot be undone.**
🤔 **Are you sure you want to proceed?**
            """
            
            # Send with highlight effects
            await send_enhanced_message(
                bot=self.bot,
                chat_id=chat_id,
                text=confirmation_text,
                keyboard=keyboard,
                effect_type='highlight',
                auto_sticker='warning'
            )
            
        except Exception as e:
            logger.error(f"Error sending enhanced confirmation: {e}")

# Global integration instance
haptic_integration = None

def get_haptic_integration(bot: Bot = None) -> HapticIntegration:
    """Get global haptic integration instance"""
    global haptic_integration
    if haptic_integration is None and bot:
        haptic_integration = HapticIntegration(bot)
    return haptic_integration