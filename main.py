"""
I3lani Telegram Bot - Main Application
Complete implementation following the new guide
"""
import asyncio
import logging
import os
import fcntl
import sys
import threading
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from flask import Flask, jsonify, request

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
from admin_ui_control import router as ui_control_router
from button_test_handler import router as button_test_router
from comprehensive_button_tester import router as comprehensive_button_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global lock file for preventing multiple instances
LOCK_FILE = "/tmp/i3lani_bot.lock"

# Flask app for Cloud Run deployment
app = Flask(__name__)

# Global bot instance
bot_instance = None
bot_started = False

@app.route('/')
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        'status': 'ok',
        'service': 'I3lani Telegram Bot',
        'bot_status': 'running' if bot_started else 'starting',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Additional health endpoint"""
    return jsonify({
        'status': 'healthy',
        'bot_running': bot_started,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for Telegram"""
    try:
        if bot_instance:
            update = request.get_json()
            # Process webhook update if needed
            return jsonify({'status': 'processed'})
        return jsonify({'status': 'bot_not_ready'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Bot status endpoint"""
    return jsonify({
        'bot_started': bot_started,
        'uptime': datetime.now().isoformat(),
        'status': 'operational' if bot_started else 'initializing'
    })

def acquire_lock():
    """Acquire lock to prevent multiple bot instances"""
    try:
        # Kill any existing python processes running the bot
        import subprocess
        try:
            subprocess.run(["pkill", "-f", "python main.py"], check=False, capture_output=True)
            logger.info("🧹 Killed existing bot processes")
        except:
            pass
        
        # Clean up stale lock file if process doesn't exist
        if os.path.exists(LOCK_FILE):
            try:
                with open(LOCK_FILE, 'r') as f:
                    old_pid = int(f.read().strip())
                try:
                    os.kill(old_pid, 0)  # Check if process exists
                    logger.error("❌ Another bot instance is already running!")
                    sys.exit(1)
                except OSError:
                    # Process doesn't exist, remove stale lock
                    os.remove(LOCK_FILE)
                    logger.info("🧹 Removed stale lock file")
            except (ValueError, FileNotFoundError):
                # Invalid or missing lock file, remove it
                try:
                    os.remove(LOCK_FILE)
                except FileNotFoundError:
                    pass
        
        lock_fd = open(LOCK_FILE, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
        return lock_fd
    except IOError:
        logger.error("❌ Failed to acquire bot instance lock!")
        sys.exit(1)

async def init_bot():
    """Initialize and start the Telegram bot"""
    global bot_instance, bot_started
    
    # Force cleanup any existing bot processes
    import subprocess
    try:
        subprocess.run(["pkill", "-f", "python main.py"], capture_output=True, timeout=5)
        subprocess.run(["pkill", "-f", "aiogram"], capture_output=True, timeout=5)
        await asyncio.sleep(1)  # Wait for cleanup
    except:
        pass
    
    # Acquire lock to prevent multiple instances
    lock_fd = acquire_lock()
    logger.info("🔒 Bot instance lock acquired successfully")
    try:
        # Initialize bot and dispatcher
        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        bot = Bot(token=BOT_TOKEN)
        bot_instance = bot
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
        dp.include_router(ui_control_router)
        dp.include_router(button_test_router)
        dp.include_router(comprehensive_button_router)
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
        
        # Mark bot as started
        bot_started = True
        
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
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Mark bot as stopped
        bot_started = False
        
        # Clean up lock file
        try:
            if 'lock_fd' in locals():
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
                logger.info("🧹 Cleaned up lock file")
        except Exception as e:
            logger.error(f"Error cleaning up lock: {e}")
        
        # Close bot session properly
        try:
            await bot.close()
        except:
            pass

def run_flask_server():
    """Run Flask server for Cloud Run deployment"""
    try:
        logger.info("Starting Flask server on 0.0.0.0:5001...")
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

def run_bot():
    """Run bot in background thread"""
    try:
        logger.info("Starting bot in background thread...")
        asyncio.run(init_bot())
    except Exception as e:
        logger.error(f"Bot error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main application entry point - runs both Flask server and bot"""
    try:
        logger.info("🚀 Starting I3lani Bot application...")
        
        # Start bot in background thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("🤖 Bot started in background thread")
        
        # Add a small delay to ensure bot starts
        import time
        time.sleep(3)
        
        # Run Flask server in main thread (blocking)
        run_flask_server()
        
    except Exception as e:
        logger.error(f"Main application error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    try:
        # Configure logging for deployment
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('bot.log', mode='a')
            ]
        )
        
        logger.info("🚀 Starting I3lani Bot application...")
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)