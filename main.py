"""
I3lani Telegram Bot - Main Application
Complete implementation following the new guide
"""
import asyncio
import logging
import os
import fcntl
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db, db
from handlers import setup_handlers
# Debug system removed for cleanup
from admin_system import setup_admin_handlers
from stars_handler import init_stars_handler, setup_stars_handlers
from channel_manager import init_channel_manager, handle_my_chat_member
from publishing_scheduler import init_scheduler
from troubleshooting import init_troubleshooting_system
from troubleshooting_handlers import troubleshooting_router, init_troubleshooting_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global lock file for preventing multiple instances
LOCK_FILE = "/tmp/i3lani_bot.lock"

def acquire_lock():
    """Acquire lock to prevent multiple bot instances"""
    try:
        lock_fd = open(LOCK_FILE, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
        return lock_fd
    except IOError:
        logger.error("❌ Another bot instance is already running!")
        logger.error("💡 Please stop the existing instance before starting a new one")
        sys.exit(1)

async def main():
    """Main application entry point"""
    
    # Acquire lock to prevent multiple instances
    lock_fd = acquire_lock()
    logger.info("🔒 Bot instance lock acquired successfully")
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
        
        # Initialize channel incentives system
        logger.info("Initializing channel incentives system...")
        from channel_incentives import init_incentives
        init_incentives(db)
        
        # Initialize atomic rewards system
        logger.info("Initializing atomic rewards system...")
        from atomic_rewards import init_atomic_rewards
        init_atomic_rewards(db, bot)
        
        # Initialize content moderation system
        logger.info("Initializing content moderation system...")
        from content_moderation import init_content_moderation
        content_moderation = init_content_moderation(db, bot)
        logger.info("Content moderation system initialized successfully")
        
        # Initialize gamification system
        logger.info("Initializing gamification system...")
        from gamification import init_gamification
        gamification = init_gamification(db, bot)
        await gamification.initialize_gamification_tables()
        logger.info("Gamification system initialized successfully")
        
        # Initialize troubleshooting system
        logger.info("Initializing troubleshooting system...")
        troubleshooting_system = await init_troubleshooting_system(db, bot)
        init_troubleshooting_handlers(troubleshooting_system)
        dp.include_router(troubleshooting_router)
        logger.info("Troubleshooting system initialized successfully")
        
        # Initialize translation system
        logger.info("Initializing comprehensive translation system...")
        from translation_system import init_translation_system
        init_translation_system()
        logger.info("Translation system initialized successfully")
        
        # Initialize auto-deployment system
        logger.info("Initializing auto-deployment system...")
        try:
            from auto_deploy import init_auto_deploy
            auto_deploy = init_auto_deploy()
            if auto_deploy:
                logger.info("✅ Auto-deployment system initialized successfully")
            else:
                logger.warning("⚠️ Auto-deployment system failed to initialize")
        except ImportError:
            logger.info("📦 Auto-deployment system not available - install watchdog package")
        except Exception as e:
            logger.error(f"Auto-deployment initialization error: {e}")
        
        # Register chat member handler
        dp.my_chat_member.register(handle_my_chat_member)
        
        # Clean up invalid channels first
        logger.info("Syncing existing channels and auto-discovering...")
        cleaned_count = await db.clean_invalid_channels()
        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} invalid channels")
        
        # Auto-discover existing channels where bot is admin
        await channel_manager.sync_existing_channels()
        logger.info("✅ Automatic channel discovery completed at startup")
        
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
            BotCommand(command="admin", description="🔧 Admin Panel"),
            BotCommand(command="health", description="🏥 System Health (Admin)"),
            BotCommand(command="troubleshoot", description="🛠️ Troubleshooting (Admin)"),
            BotCommand(command="report_issue", description="📝 Report Issue")
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