#!/usr/bin/env python3
"""
Add @Five_SAR channel to the bot database
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from database import Database
from channel_manager import ChannelManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_five_sar():
    """Add @Five_SAR channel"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    channel_manager = ChannelManager(bot, db)
    
    try:
        channel_username = "@Five_SAR"
        logger.info(f"Adding {channel_username} to bot database...")
        
        # Use channel manager to discover and add the channel
        result = await channel_manager.discover_channel_by_username(channel_username)
        
        if result:
            logger.info("✅ Channel added successfully!")
            
            # Show all channels now
            logger.info("\n=== All Active Channels ===")
            channels = await db.get_channels(active_only=True)
            for ch in channels:
                logger.info(f"• {ch['name']} (@{ch['telegram_channel_id']}) - {ch['subscribers']} subscribers")
        else:
            logger.error("Failed to add channel")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(add_five_sar())