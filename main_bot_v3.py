"""
I3lani v3 Main Bot
Complete V3 auction-based system
"""

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# V3 System Imports
from v3_integration_main import initialize_i3lani_v3
from v3_main_handlers import setup_v3_handlers
from v3_admin_commands import setup_v3_admin_handlers

logger = logging.getLogger(__name__)

async def main():
    """Main function with V3 system only"""
    try:
        # Bot configuration
        BOT_TOKEN = "8198376763:AAGNqJ7ZJoQczTNKDJk9eRLVpgFuQo3EaJU"
        
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN not found")
            return
        
        # Initialize bot and dispatcher
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        logger.info("🚀 Starting I3lani v3 Auction-Based Bot...")
        
        # Initialize V3 system
        logger.info("Initializing I3lani v3 system...")
        v3_integration = await initialize_i3lani_v3(bot, dp)
        
        # Setup V3 handlers
        logger.info("Setting up V3 handlers...")
        setup_v3_handlers(dp, bot)
        setup_v3_admin_handlers(dp, bot)
        
        # Set bot commands
        from aiogram.types import BotCommand
        commands = [
            BotCommand(command="start", description="🚀 Start I3lani v3"),
            BotCommand(command="profile", description="👤 User Profile"),
            BotCommand(command="statistics", description="📊 View Statistics"),
            BotCommand(command="help", description="❓ Get Help"),
            BotCommand(command="adminv3", description="🔧 Admin Panel (V3)")
        ]
        await bot.set_my_commands(commands)
        
        logger.info("✅ I3lani v3 bot initialization complete")
        logger.info("   🎯 Auction system: Daily at 9:00 AM")
        logger.info("   💰 Payment methods: TON + Telegram Stars")
        logger.info("   👥 User roles: Advertiser, Channel Owner, Affiliate")
        logger.info("   💸 Revenue sharing: 68% to channel owners")
        logger.info("   🎁 Affiliate commission: 5%")
        logger.info("   💎 Minimum withdrawal: $50")
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Bot startup error: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
