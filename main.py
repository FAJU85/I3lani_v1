"""
I3lani Telegram Bot - Main Application
Complete implementation following the new guide
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db, db
from handlers import setup_handlers
# Debug system removed for cleanup
from admin_system import setup_admin_handlers
from stars_handler import init_stars_handler, setup_stars_handlers
from channel_manager import init_channel_manager, handle_my_chat_member

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main application entry point"""
    try:
        # Initialize bot and dispatcher
        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Debug system removed for cleanup
        
        # Initialize Telegram Stars system
        logger.info("Initializing Telegram Stars payment system...")
        stars_handler = init_stars_handler(bot)
        logger.info("Telegram Stars system initialized successfully")
        
        # Setup handlers
        logger.info("Setting up handlers...")
        setup_handlers(dp)
        # Debug handlers removed for cleanup
        setup_admin_handlers(dp)
        setup_stars_handlers(dp)
        
        # Initialize channel manager
        logger.info("Initializing channel manager...")
        channel_manager = init_channel_manager(bot, db)
        
        # Register chat member handler
        dp.my_chat_member.register(handle_my_chat_member)
        
        # Clean up invalid channels first
        logger.info("Syncing existing channels...")
        cleaned_count = await db.clean_invalid_channels()
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} invalid channels")
        
        await channel_manager.sync_existing_channels()
        
        logger.info("Handlers setup completed")
        
        # Setup menu button
        from aiogram.types import BotCommand, MenuButtonCommands
        await bot.set_my_commands([
            BotCommand(command="start", description="🚀 Start the bot"),
            BotCommand(command="dashboard", description="📊 My Ads Dashboard"),
            BotCommand(command="mystats", description="📈 My Statistics"),
            BotCommand(command="referral", description="💰 Referral System"),
            BotCommand(command="support", description="🆘 Get Support"),
            BotCommand(command="help", description="❓ Help & Guide"),
            BotCommand(command="admin", description="🔧 Admin Panel")
        ])
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
        
        # Start polling
        logger.info("Starting I3lani Bot...")
        logger.info("Bot Features:")
        logger.info("- Multi-language support (EN, AR, RU)")
        logger.info("- AB0102 memo format payment system")
        logger.info("- TON cryptocurrency and Telegram Stars")
        logger.info("- Multi-channel advertising")
        logger.info("- Referral system with rewards")
        logger.info("- Complete user dashboard")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())