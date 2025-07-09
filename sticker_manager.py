"""
Sticker Manager for I3lani Bot
Handles automatic sticker sending for enhanced user experience
"""

import logging
import random
from aiogram import Bot
from aiogram.types import Message
from database import get_user_language

logger = logging.getLogger(__name__)

class StickerManager:
    """Manages automatic sticker sending for various bot interactions"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        
        # Sticker sets for different occasions
        self.sticker_sets = {
            'welcome': [
                # Welcome and greeting stickers
                '👋', '🎉', '✨', '🌟', '💫'
            ],
            'success': [
                # Success and achievement stickers
                '✅', '🎯', '🏆', '🎖️', '🥇'
            ],
            'celebration': [
                # Celebration and party stickers
                '🎊', '🎉', '🥳', '🎆', '🎇'
            ],
            'thinking': [
                # Thinking and processing stickers
                '🤔', '💭', '⚡', '🔄', '⏳'
            ],
            'money': [
                # Money and payment stickers
                '💰', '💵', '💳', '💎', '🪙'
            ],
            'game': [
                # Gaming and fun stickers
                '🎮', '🎯', '🎲', '🎪', '🎨'
            ],
            'reward': [
                # Reward and gift stickers
                '🎁', '🏅', '🎖️', '🏆', '💝'
            ],
            'motivational': [
                # Motivational and encouraging stickers
                '💪', '🚀', '⭐', '🌟', '✨'
            ],
            'love': [
                # Love and appreciation stickers
                '❤️', '💕', '💖', '😍', '🥰'
            ],
            'warning': [
                # Warning and caution stickers
                '⚠️', '🚨', '⛔', '🔴', '❌'
            ]
        }
    
    async def send_context_sticker(self, chat_id: int, context: str, language: str = 'en'):
        """Send appropriate sticker based on context"""
        try:
            sticker_emoji = self._get_context_sticker(context)
            if sticker_emoji:
                # Convert emoji to sticker message
                await self.bot.send_message(chat_id, sticker_emoji)
                
        except Exception as e:
            logger.warning(f"Failed to send context sticker: {e}")
    
    def _get_context_sticker(self, context: str) -> str:
        """Get appropriate sticker emoji for context"""
        context_mapping = {
            'welcome': random.choice(self.sticker_sets['welcome']),
            'start': random.choice(self.sticker_sets['welcome']),
            'success': random.choice(self.sticker_sets['success']),
            'payment_success': random.choice(self.sticker_sets['success']),
            'ad_created': random.choice(self.sticker_sets['success']),
            'celebration': random.choice(self.sticker_sets['celebration']),
            'reward_unlocked': random.choice(self.sticker_sets['reward']),
            'referral_success': random.choice(self.sticker_sets['celebration']),
            'game_win': random.choice(self.sticker_sets['reward']),
            'progress_complete': random.choice(self.sticker_sets['success']),
            'thinking': random.choice(self.sticker_sets['thinking']),
            'processing': random.choice(self.sticker_sets['thinking']),
            'loading': random.choice(self.sticker_sets['thinking']),
            'money': random.choice(self.sticker_sets['money']),
            'payment': random.choice(self.sticker_sets['money']),
            'ton_payment': random.choice(self.sticker_sets['money']),
            'stars_payment': random.choice(self.sticker_sets['money']),
            'game': random.choice(self.sticker_sets['game']),
            'gaming': random.choice(self.sticker_sets['game']),
            'viral_game': random.choice(self.sticker_sets['game']),
            'reward': random.choice(self.sticker_sets['reward']),
            'gift': random.choice(self.sticker_sets['reward']),
            'free_ad': random.choice(self.sticker_sets['reward']),
            'motivational': random.choice(self.sticker_sets['motivational']),
            'encourage': random.choice(self.sticker_sets['motivational']),
            'keep_going': random.choice(self.sticker_sets['motivational']),
            'love': random.choice(self.sticker_sets['love']),
            'thank_you': random.choice(self.sticker_sets['love']),
            'appreciation': random.choice(self.sticker_sets['love']),
            'warning': random.choice(self.sticker_sets['warning']),
            'error': random.choice(self.sticker_sets['warning']),
            'failed': random.choice(self.sticker_sets['warning']),
        }
        
        return context_mapping.get(context, None)
    
    async def send_sequence_stickers(self, chat_id: int, sequence: list, delay: float = 0.5):
        """Send a sequence of stickers with delay"""
        try:
            import asyncio
            
            for sticker_context in sequence:
                await self.send_context_sticker(chat_id, sticker_context)
                await asyncio.sleep(delay)
                
        except Exception as e:
            logger.error(f"Failed to send sticker sequence: {e}")
    
    async def send_celebration_sequence(self, chat_id: int, celebration_type: str = 'success'):
        """Send celebration sticker sequence"""
        sequences = {
            'success': ['success', 'celebration', 'motivational'],
            'reward': ['reward', 'celebration', 'love'],
            'payment': ['money', 'success', 'thank_you'],
            'game_win': ['game', 'reward', 'celebration'],
            'referral': ['love', 'reward', 'celebration'],
            'progress': ['motivational', 'success', 'celebration']
        }
        
        sequence = sequences.get(celebration_type, ['success', 'celebration'])
        await self.send_sequence_stickers(chat_id, sequence)
    
    async def send_progress_sticker(self, chat_id: int, progress: int):
        """Send progress-based sticker"""
        if progress < 25:
            await self.send_context_sticker(chat_id, 'motivational')
        elif progress < 50:
            await self.send_context_sticker(chat_id, 'encourage')
        elif progress < 75:
            await self.send_context_sticker(chat_id, 'keep_going')
        elif progress < 99:
            await self.send_context_sticker(chat_id, 'success')
        else:
            await self.send_celebration_sequence(chat_id, 'progress')
    
    async def send_payment_stickers(self, chat_id: int, payment_method: str):
        """Send payment-specific stickers"""
        if payment_method.lower() == 'ton':
            await self.send_context_sticker(chat_id, 'ton_payment')
        elif payment_method.lower() == 'stars':
            await self.send_context_sticker(chat_id, 'stars_payment')
        else:
            await self.send_context_sticker(chat_id, 'payment')
    
    async def send_viral_game_stickers(self, chat_id: int, action: str):
        """Send viral game specific stickers"""
        game_actions = {
            'start': 'game',
            'progress': 'motivational',
            'tap': 'game',
            'referral': 'love',
            'reward': 'reward',
            'complete': 'celebration'
        }
        
        context = game_actions.get(action, 'game')
        await self.send_context_sticker(chat_id, context)
    
    async def send_admin_stickers(self, chat_id: int, admin_action: str):
        """Send admin-specific stickers"""
        admin_actions = {
            'analytics': 'thinking',
            'broadcast': 'motivational',
            'settings': 'success',
            'user_management': 'love',
            'channel_management': 'success'
        }
        
        context = admin_actions.get(admin_action, 'success')
        await self.send_context_sticker(chat_id, context)

# Global sticker manager instance
sticker_manager = None

def get_sticker_manager(bot: Bot = None) -> StickerManager:
    """Get global sticker manager instance"""
    global sticker_manager
    if sticker_manager is None and bot:
        sticker_manager = StickerManager(bot)
    return sticker_manager

async def send_auto_sticker(bot: Bot, chat_id: int, context: str, language: str = 'en'):
    """Convenience function for sending automatic stickers"""
    manager = get_sticker_manager(bot)
    if manager:
        await manager.send_context_sticker(chat_id, context, language)