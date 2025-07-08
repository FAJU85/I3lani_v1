#!/usr/bin/env python3
"""
Fix bot conflict by stopping conflicting updates
"""
import asyncio
import logging
from aiogram import Bot
from aiogram.types import Update
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clear_pending_updates():
    """Clear all pending updates to resolve conflicts"""
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Get updates with offset -1 to mark all as read
        updates = await bot.get_updates(offset=-1)
        
        if updates:
            # Get the last update ID and skip all pending updates
            last_update_id = updates[-1].update_id
            await bot.get_updates(offset=last_update_id + 1)
            logger.info(f"Cleared {len(updates)} pending updates")
        else:
            logger.info("No pending updates to clear")
        
        await bot.close()
        logger.info("Bot updates cleared successfully")
        
    except Exception as e:
        logger.error(f"Error clearing updates: {e}")

if __name__ == "__main__":
    asyncio.run(clear_pending_updates())