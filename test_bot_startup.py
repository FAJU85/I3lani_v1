#!/usr/bin/env python3
"""
Test bot startup to identify issues
"""

import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BOT_TOKEN

async def test_bot():
    """Test basic bot functionality"""
    logger.info("Starting bot test...")
    
    # Create bot instance
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    try:
        # Test bot connection
        me = await bot.get_me()
        logger.info(f"✅ Bot connected: @{me.username} (ID: {me.id})")
        
        # Test simple message handler
        @dp.message()
        async def echo(message):
            await message.answer("Test response")
        
        logger.info("✅ Handler registered")
        
        # Start polling for a short time
        logger.info("Starting polling for 5 seconds...")
        
        # Create a task for polling
        polling_task = asyncio.create_task(dp.start_polling(bot))
        
        # Wait 5 seconds
        await asyncio.sleep(5)
        
        logger.info("✅ Bot ran successfully for 5 seconds")
        
        # Stop polling
        dp.stop_polling()
        await bot.close()
        
        logger.info("✅ Bot closed cleanly")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Bot test failed: {e}")
        import traceback
        traceback.print_exc()
        await bot.close()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot())
    if success:
        print("\n✅ BOT TEST PASSED - The bot can start successfully")
    else:
        print("\n❌ BOT TEST FAILED - There's an issue with bot startup")