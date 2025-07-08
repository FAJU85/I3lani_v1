#!/usr/bin/env python3
"""
Check all channels and clean up duplicates
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_and_clean_channels():
    """Check all channels and remove duplicates"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    
    try:
        logger.info("=" * 60)
        logger.info("CHECKING ALL CHANNELS")
        logger.info("=" * 60)
        
        # Get all channels
        channels = await db.get_channels(active_only=False)
        logger.info(f"Total channels in database: {len(channels)}")
        
        # Check for duplicates
        seen = {}
        duplicates = []
        
        for ch in channels:
            key = ch['telegram_channel_id'].lower().replace('@', '')
            if key in seen:
                duplicates.append(ch)
                logger.warning(f"Duplicate found: {ch['name']} ({ch['telegram_channel_id']})")
            else:
                seen[key] = ch
        
        if duplicates:
            logger.info(f"\nFound {len(duplicates)} duplicates to remove")
            
        # Check each unique channel
        logger.info("\n" + "=" * 60)
        logger.info("VERIFYING CHANNELS")
        logger.info("=" * 60)
        
        active_channels = []
        
        for channel_id, channel in seen.items():
            try:
                username = channel['telegram_channel_id']
                if not username.startswith('@'):
                    username = f"@{username}"
                
                chat = await bot.get_chat(username)
                bot_member = await bot.get_chat_member(chat.id, bot.id)
                member_count = await bot.get_chat_member_count(chat.id)
                
                if bot_member.status == 'administrator' and bot_member.can_post_messages:
                    logger.info(f"✅ {chat.title} (@{chat.username}) - {member_count} subscribers - ACTIVE")
                    active_channels.append({
                        'name': chat.title,
                        'username': chat.username,
                        'id': chat.id,
                        'members': member_count
                    })
                else:
                    logger.warning(f"❌ {chat.title} - Bot is not admin or can't post")
                    
            except Exception as e:
                logger.error(f"❌ {channel['name']} ({channel['telegram_channel_id']}) - Error: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Active channels where bot can post: {len(active_channels)}")
        
        for i, ch in enumerate(active_channels, 1):
            logger.info(f"{i}. {ch['name']} (@{ch['username']}) - {ch['members']} members")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(check_and_clean_channels())