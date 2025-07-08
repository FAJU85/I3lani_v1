#!/usr/bin/env python3
"""
Force comprehensive channel discovery
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from channel_manager import ChannelManager
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_comprehensive_discovery():
    """Run comprehensive channel discovery"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    
    channel_manager = ChannelManager(bot, db)
    
    try:
        logger.info("Starting comprehensive channel discovery...")
        
        # Run force discovery
        results = await channel_manager.force_full_channel_discovery()
        
        if 'error' not in results:
            logger.info("\n=== Discovery Results ===")
            logger.info(f"Total channels scanned: {results['total_scanned']}")
            logger.info(f"Newly discovered: {results['newly_discovered']}")
            logger.info(f"Already known: {results['already_known']}")
            logger.info(f"Failed attempts: {results['failed_attempts']}")
            
            if results['discovered_channels']:
                logger.info("\n🎯 Newly discovered channels:")
                for ch in results['discovered_channels']:
                    logger.info(f"  - {ch['name']} ({ch['username']}) - {ch['subscribers']} subscribers")
        else:
            logger.error(f"Discovery error: {results['error']}")
        
        # Show all active channels
        logger.info("\n=== All Active Channels ===")
        channels = await db.get_channels(active_only=True)
        for ch in channels:
            logger.info(f"✅ {ch['channel_name']} (@{ch['telegram_channel_id']}) - {ch['subscribers']} subscribers")
            
    except Exception as e:
        logger.error(f"Error running discovery: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(run_comprehensive_discovery())