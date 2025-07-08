#!/usr/bin/env python3
"""
Force comprehensive channel discovery
This will find ALL channels where bot is administrator
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from database import Database
from channel_manager import ChannelManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def force_discover_all_channels():
    """Force discovery of ALL channels where bot is admin"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    channel_manager = ChannelManager(bot, db)
    
    try:
        logger.info("=" * 60)
        logger.info("FORCING COMPREHENSIVE CHANNEL DISCOVERY")
        logger.info("=" * 60)
        
        # Run the force discovery
        results = await channel_manager.force_full_channel_discovery()
        
        logger.info(f"\n📊 Discovery Results:")
        logger.info(f"Total channels scanned: {results.get('total_scanned', 0)}")
        logger.info(f"Newly discovered: {results.get('newly_discovered', 0)}")
        logger.info(f"Already known: {results.get('already_known', 0)}")
        logger.info(f"Failed attempts: {results.get('failed_attempts', 0)}")
        
        if results.get('discovered_channels'):
            logger.info(f"\n✅ Newly discovered channels:")
            for ch in results['discovered_channels']:
                logger.info(f"- {ch['name']} (@{ch['username']}) - {ch['subscribers']} subscribers")
        
        # Show all active channels
        logger.info("\n" + "=" * 60)
        logger.info("ALL ACTIVE CHANNELS IN DATABASE")
        logger.info("=" * 60)
        
        channels = await db.get_channels(active_only=True)
        for i, ch in enumerate(channels, 1):
            logger.info(f"{i}. {ch['name']} (@{ch['telegram_channel_id']}) - {ch['subscribers']} subscribers")
        
        logger.info(f"\n✅ Total active channels: {len(channels)}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(force_discover_all_channels())