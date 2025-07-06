"""
I3lani Telegram Bot - Main Application
Complete implementation following the new guide
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import setup_handlers
from debug_system import init_debug_system, setup_debug_handlers
from debug_dashboard import init_dashboard, setup_dashboard_handlers

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
        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize debug system
        logger.info("Initializing debug system...")
        debug_system = init_debug_system(bot)
        logger.info("Debug system initialized successfully")
        
        # Initialize debug dashboard
        logger.info("Initializing debug dashboard...")
        dashboard = init_dashboard(bot)
        logger.info("Debug dashboard initialized successfully")
        
        # Setup handlers
        logger.info("Setting up handlers...")
        setup_handlers(dp)
        setup_debug_handlers(dp)
        setup_dashboard_handlers(dp)
        logger.info("Handlers setup completed")
        
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