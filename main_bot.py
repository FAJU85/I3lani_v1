#!/usr/bin/env python3
"""
Core bot functionality for I3lani Bot
Separated from Flask server for Cloud Run deployment
"""
import asyncio
import logging
import os
import fcntl
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot_lock_manager import lock_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_bot():
    """Start the Telegram bot"""
    try:
        # Clean up any existing bot processes first
        logger.info("Cleaning up existing bot processes...")
        lock_manager.cleanup_all_bot_processes()
        
        # Acquire lock to ensure single instance
        if not lock_manager.acquire_lock():
            logger.error("Failed to acquire bot lock - another instance may be running")
            return
        
        # Import all required modules
        from config import BOT_TOKEN
        from database import init_db, db
        from handlers import setup_handlers
        from admin_system import setup_admin_handlers
        from stars_handler import init_stars_handler, setup_stars_handlers
        from channel_manager import init_channel_manager, handle_my_chat_member
        
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
        
        # Initialize Telegram Stars system
        logger.info("Initializing Telegram Stars payment system...")
        stars_handler = init_stars_handler(bot)
        logger.info("Telegram Stars system initialized successfully")
        
        # Setup handlers
        logger.info("Setting up handlers...")
        setup_handlers(dp)
        setup_admin_handlers(dp)
        setup_stars_handlers(dp)
        
        # Initialize channel manager
        logger.info("Initializing channel manager...")
        channel_manager = init_channel_manager(bot, db)
        
        # Initialize other systems
        try:
            from channel_incentives import init_incentives
            init_incentives(db)
            logger.info("Channel incentives system initialized")
        except Exception as e:
            logger.warning(f"Channel incentives initialization failed: {e}")
        
        try:
            from atomic_rewards import init_atomic_rewards
            init_atomic_rewards(db, bot)
            logger.info("Atomic rewards system initialized")
        except Exception as e:
            logger.warning(f"Atomic rewards initialization failed: {e}")
        
        try:
            from content_moderation import init_content_moderation
            content_moderation = init_content_moderation(db, bot)
            logger.info("Content moderation system initialized")
        except Exception as e:
            logger.warning(f"Content moderation initialization failed: {e}")
        
        try:
            from gamification import init_gamification
            gamification = init_gamification(db, bot)
            await gamification.initialize_gamification_tables()
            logger.info("Gamification system initialized")
        except Exception as e:
            logger.warning(f"Gamification initialization failed: {e}")
        
        try:
            from troubleshooting import init_troubleshooting_system
            from troubleshooting_handlers import troubleshooting_router, init_troubleshooting_handlers
            troubleshooting_system = await init_troubleshooting_system(db, bot)
            init_troubleshooting_handlers(troubleshooting_system)
            dp.include_router(troubleshooting_router)
            logger.info("Troubleshooting system initialized")
        except Exception as e:
            logger.warning(f"Troubleshooting initialization failed: {e}")
        
        try:
            from admin_ui_control import router as ui_control_router
            from button_test_handler import router as button_test_router
            from comprehensive_button_tester import router as comprehensive_button_router
            dp.include_router(ui_control_router)
            dp.include_router(button_test_router)
            dp.include_router(comprehensive_button_router)
            logger.info("UI control systems initialized")
        except Exception as e:
            logger.warning(f"UI control initialization failed: {e}")
        
        try:
            from translation_system import init_translation_system
            init_translation_system()
            logger.info("Translation system initialized")
        except Exception as e:
            logger.warning(f"Translation initialization failed: {e}")
        
        # Register chat member handler
        dp.my_chat_member.register(handle_my_chat_member)
        
        # Clean up and sync channels
        logger.info("Syncing existing channels...")
        try:
            cleaned_count = await db.clean_invalid_channels()
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} invalid channels")
            
            await channel_manager.sync_existing_channels()
            logger.info("Automatic channel discovery completed")
        except Exception as e:
            logger.warning(f"Channel sync failed: {e}")
        
        # Setup bot commands
        from aiogram.types import BotCommand, MenuButtonCommands
        await bot.set_my_commands([
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="dashboard", description="My Ads Dashboard"),
            BotCommand(command="mystats", description="My Statistics"),
            BotCommand(command="referral", description="Referral System"),
            BotCommand(command="support", description="Get Support"),
            BotCommand(command="help", description="Help & Guide"),
            BotCommand(command="admin", description="Admin Panel"),
            BotCommand(command="health", description="System Health (Admin)"),
            BotCommand(command="troubleshoot", description="Troubleshooting (Admin)"),
            BotCommand(command="report_issue", description="Report Issue")
        ])
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
        
        # Start polling without signal handlers (for threading compatibility)
        logger.info("Starting I3lani Bot...")
        logger.info("Bot Features:")
        logger.info("- Multi-language support (EN, AR, RU)")
        logger.info("- TON cryptocurrency and Telegram Stars")
        logger.info("- Multi-channel advertising")
        logger.info("- Referral system with rewards")
        logger.info("- Complete user dashboard")
        
        # Use polling without signal handlers for background thread compatibility
        await dp.start_polling(bot, handle_signals=False)
        
    except Exception as e:
        logger.error(f"Bot error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Clean up and release lock
        try:
            await bot.close()
        except:
            pass
        
        # Release the lock
        lock_manager.release_lock()
        logger.info("Bot lock released")

if __name__ == "__main__":
    asyncio.run(start_bot())