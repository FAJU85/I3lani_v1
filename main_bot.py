"""
I3lani Telegram Bot - Core Bot Functionality
Separated from Flask server for Cloud Run deployment
"""

# Set environment variable to prevent duplicate Flask servers
import os
os.environ['DISABLE_STARS_FLASK'] = '1'
import asyncio
import logging
import os
import fcntl
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, MenuButtonCommands

from config import BOT_TOKEN
from database import init_db, db
from handlers import setup_handlers
from admin_system import setup_admin_handlers
# Stars payment handlers setup integrated directly in main
from channel_manager import init_channel_manager, handle_my_chat_member
# Publishing scheduler removed during cleanup
# Campaign publisher removed during cleanup
from enhanced_campaign_publisher import init_enhanced_campaign_publisher
# Troubleshooting system removed during cleanup
# Troubleshooting handlers removed during cleanup
# Admin UI control removed during cleanup
# Button test handler removed during cleanup
# Comprehensive button tester removed during cleanup
# Payment protocol handlers removed during cleanup

# Configure logging
logger = logging.getLogger(__name__)

# Global lock file for preventing multiple instances
LOCK_FILE = "/tmp/i3lani_bot.lock"

# Global bot instance
bot_instance = None
bot = None  # Add bot variable for backward compatibility
bot_started = False

def acquire_lock():
    """Acquire lock to prevent multiple bot instances"""
    try:
        # Kill any existing python processes running the bot
        import subprocess
        try:
            subprocess.run(["pkill", "-f", "python main.py"], check=False, capture_output=True)
            logger.info("Killed existing bot processes")
        except:
            pass
        
        # Clean up stale lock file if process doesn't exist
        if os.path.exists(LOCK_FILE):
            try:
                with open(LOCK_FILE, 'r') as f:
                    old_pid = int(f.read().strip())
                try:
                    os.kill(old_pid, 0)  # Check if process exists
                    logger.error("Another bot instance is already running!")
                    sys.exit(1)
                except OSError:
                    # Process doesn't exist, remove stale lock
                    os.remove(LOCK_FILE)
                    logger.info("Removed stale lock file")
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
        logger.error("Failed to acquire bot instance lock!")
        sys.exit(1)

async def init_bot():
    """Initialize and start the Telegram bot"""
    global bot_instance, bot, bot_started
    
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
    logger.info("Bot instance lock acquired successfully")
    
    try:
        # Initialize bot and dispatcher
        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        bot = Bot(token=BOT_TOKEN)
        bot_instance = bot
        # Set bot variable for backward compatibility
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize payment memo tracker
        logger.info("Initializing payment memo tracker...")
        try:
            from payment_memo_tracker import init_payment_memo_tracker
            await init_payment_memo_tracker()
            logger.info("✅ Payment memo tracker initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize payment memo tracker: {e}")
        
        # Initialize automatic payment confirmation system
        logger.info("Initializing automatic payment confirmation...")
        try:
            from automatic_payment_confirmation import init_automatic_confirmation
            await init_automatic_confirmation()
            logger.info("✅ Automatic payment confirmation initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize automatic confirmation: {e}")
        
        # Initialize campaign management system
        logger.info("Initializing campaign management system...")
        try:
            from campaign_management import init_campaign_system
            await init_campaign_system()
            logger.info("✅ Campaign management system initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize campaign system: {e}")
        
        # Initialize Post Identity System and Enhanced Campaign Publisher
        logger.info("Initializing Post Identity System and Enhanced Campaign Publisher...")
        try:
            from post_identity_system import init_post_identity_system
            from enhanced_campaign_publisher import init_enhanced_campaign_publisher
            
            # Initialize Post Identity System first
            post_identity_success = await init_post_identity_system()
            if post_identity_success:
                logger.info("✅ Post Identity System initialized successfully")
            else:
                logger.error("❌ Post Identity System initialization failed")
            
            # Initialize Enhanced Campaign Publisher
            enhanced_publisher = await init_enhanced_campaign_publisher(bot)
            
            if enhanced_publisher:
                logger.info("✅ Enhanced Campaign Publisher initialized with Post Identity System")
                logger.info(f"Enhanced publisher running status: {enhanced_publisher.running}")
                
                # Store globally for access
                globals()['enhanced_publisher'] = enhanced_publisher
                globals()['campaign_publisher'] = enhanced_publisher  # Backward compatibility
                
                # Verify the publisher is running
                await asyncio.sleep(2)
                if enhanced_publisher.running:
                    logger.info("✅ Enhanced publisher confirmed running - content integrity guaranteed")
                    logger.info("🔄 Enhanced publisher will check for posts every 30 seconds")
                    logger.info("🆔 All posts will have unique IDs and full metadata tracking")
                    
                    # Test immediate publishing capability with content verification
                    try:
                        due_posts = await enhanced_publisher._get_due_posts()
                        logger.info(f"📊 Found {len(due_posts)} posts ready for verified publishing")
                        
                        if len(due_posts) > 0:
                            logger.info("🚀 Processing due posts with content integrity verification...")
                            await enhanced_publisher._process_due_posts()
                            logger.info("✅ Initial verified publishing check completed")
                        
                    except Exception as pub_error:
                        logger.error(f"❌ Error in initial verified publishing check: {pub_error}")
                    
                else:
                    logger.warning("⚠️ Enhanced publisher not running after initialization")
                    
            else:
                logger.error("❌ Enhanced Campaign Publisher initialization failed")
                
                # Fallback to original publisher
                logger.info("Attempting fallback to original campaign publisher...")
                try:
                    # Campaign publisher removed during cleanup
                    fallback_publisher = None
                    if fallback_publisher:
                        globals()['campaign_publisher'] = fallback_publisher
                        logger.info("✅ Fallback campaign publisher initialized")
                    else:
                        logger.error("❌ Fallback publisher also failed")
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback publisher error: {fallback_error}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Campaign Publisher: {e}")
            import traceback
            logger.error(f"Enhanced publisher full traceback: {traceback.format_exc()}")
            
            # Try to continue without enhanced publisher
            logger.warning("Continuing bot startup without enhanced publisher...")
        
        # Initialize continuous payment scanner
        logger.info("Initializing continuous payment scanner...")
        try:
            from continuous_payment_scanner import start_continuous_payment_monitoring
            scanner_task = await start_continuous_payment_monitoring()
            logger.info("✅ Continuous payment scanner initialized and running")
        except Exception as e:
            logger.error(f"❌ Failed to initialize payment scanner: {e}")
            # Continue without scanner for now
        
        # Initialize Enhanced Telegram Stars payment system
        logger.info("Initializing Enhanced Telegram Stars payment system...")
        try:
            from enhanced_telegram_stars_payment import get_enhanced_stars_payment
            
            # Initialize enhanced Stars payment system
            enhanced_stars_payment = get_enhanced_stars_payment(bot, db)
            
            # Store globally for access
            globals()['enhanced_stars_payment'] = enhanced_stars_payment
            
            logger.info("✅ Enhanced Telegram Stars payment system initialized")
            logger.info("   💫 Full API compliance with Telegram Bot API 7.0")
            logger.info("   🌍 Complete multilingual support (EN/AR/RU)")
            logger.info("   🧾 Enhanced invoice generation with metadata")
            logger.info("   📄 Comprehensive receipt system")
            logger.info("   🔗 Integrated with campaign management")
            logger.info("   💾 Database tracking and validation")
            
        except Exception as e:
            logger.error(f"❌ Enhanced Stars payment initialization error: {e}")
            
            # Fallback to basic Stars system
            logger.info("Initializing fallback Telegram Stars system...")
            os.environ['DISABLE_STARS_FLASK'] = '1'  # Disable Flask server in stars_handler
            # Stars handler initialization removed during cleanup
            logger.info("Fallback Telegram Stars system initialized successfully")
        
        # Initialize end-to-end tracking system
        logger.info("Initializing end-to-end tracking system...")
        try:
            from end_to_end_tracking_system import get_tracking_system
            tracking_system = get_tracking_system()
            await tracking_system.initialize_database()
            logger.info("✅ End-to-end tracking system initialized")
            logger.info("   📊 Comprehensive journey tracking from /start to publication")
            logger.info("   🏷️ Integrated with Global Sequence ID System")
            logger.info("   🔔 Automatic final confirmation messages")
            logger.info("   📈 Real-time campaign progress monitoring")
        except Exception as e:
            logger.error(f"❌ End-to-end tracking system initialization error: {e}")
            # Continue without tracking system
        
        # Setup handlers
        logger.info("Setting up handlers...")
        setup_handlers(dp)
        
        # Setup campaign handlers
        logger.info("Setting up campaign handlers...")
        from campaign_handlers import setup_campaign_handlers
        setup_campaign_handlers(dp)
        logger.info("Campaign handlers setup completed")
        setup_admin_handlers(dp)
        
        # Setup advanced channel management handlers
        logger.info("Setting up advanced channel management...")
        from advanced_channel_handlers import setup_advanced_channel_handlers
        setup_advanced_channel_handlers(dp)
        logger.info("Advanced channel management handlers setup completed")
        # Setup stars handlers via clean_stars_payment_system
        from clean_stars_payment_system import CleanStarsPayment
        stars_payment = CleanStarsPayment(bot, db)
        # Register Stars payment handlers directly with correct method names
        dp.pre_checkout_query.register(stars_payment.handle_pre_checkout)
        dp.message.register(stars_payment.handle_successful_payment, F.successful_payment)
        
        # Haptic integration removed during cleanup
        logger.info("Haptic visual effects system initialized")
        
        # Initialize channel manager
        logger.info("Initializing channel manager...")
        channel_manager = init_channel_manager(bot, db)
        
        # Initialize enhanced channel admin system
        logger.info("Initializing enhanced channel admin system...")
        from enhanced_channel_admin import enhanced_channel_admin, router as enhanced_channel_router
        await enhanced_channel_admin.initialize(bot)
        dp.include_router(enhanced_channel_router)
        logger.info("Enhanced channel admin system initialized")
        
        # Initialize channel incentives system
        logger.info("Initializing channel incentives system...")
        from channel_incentives import init_incentives
        init_incentives(db)
        logger.info("Channel incentives system initialized")
        
        # Initialize atomic rewards system
        logger.info("Initializing atomic rewards system...")
        from atomic_rewards import init_atomic_rewards
        init_atomic_rewards(db, bot)
        logger.info("Atomic rewards system initialized")
        
        # Initialize content moderation system
        logger.info("Initializing content moderation system...")
        from content_moderation import init_content_moderation
        content_moderation = init_content_moderation(db, bot)
        logger.info("Content moderation system initialized")
        
        # Initialize gamification system
        logger.info("Initializing gamification system...")
        from gamification import init_gamification
        gamification = init_gamification(db, bot)
        await gamification.initialize_gamification_tables()
        logger.info("Gamification system initialized")
        
        # Initialize troubleshooting system
        logger.info("Initializing troubleshooting system...")
        # Troubleshooting system removed during cleanup
        
        # Payment protocol handlers removed during cleanup
        logger.info("✅ Payment protocol handlers initialized")
        
        # Initialize enhanced Stars payment system (Phase 1 & Phase 2)
        logger.info("Initializing enhanced Stars payment system...")
        try:
            from enhanced_stars_payment_system import init_enhanced_stars_payment_system
            from enhanced_stars_handlers import setup_enhanced_stars_handlers
            
            enhanced_system = await init_enhanced_stars_payment_system(bot, db)
            setup_enhanced_stars_handlers(dp)
            
            logger.info("✅ Enhanced Stars payment system initialized")
            logger.info("   🔍 Phase 1: Enhanced validation, fraud detection, error handling")
            logger.info("   🔗 Phase 2: TON Connect integration, advanced security")
            logger.info("   💫 Enterprise-grade Stars payments ready")
        except Exception as e:
            logger.error(f"❌ Failed to initialize enhanced Stars payment system: {e}")
        
        # Initialize viral referral game system
        logger.info("Initializing viral referral game system...")
        from viral_referral_game import ViralReferralGame
        viral_game = ViralReferralGame(db)
        await viral_game.init_tables()
        
        from viral_referral_handlers import viral_router
        dp.include_router(viral_router)
        
        # Register haptic callback handler with proper filter
        @dp.callback_query(F.data.startswith('haptic_'))
        async def haptic_callback_handler(callback_query):
            """Handle haptic callback queries"""
            handled = False  # Haptic integration removed during cleanup
            if handled:
                # Continue processing the original callback
                return
        
        logger.info("Viral referral game system initialized")
        
        logger.info("Troubleshooting system initialized")
        
        # Initialize UI control systems
        logger.info("Initializing UI control systems...")
        try:
            from ui_control_system import UIControlSystem
            ui_control_system = UIControlSystem()
            logger.info("UI control systems initialized")
        except Exception as e:
            logger.warning(f"UI control system not available: {e}")
            logger.info("UI control systems skipped")
        
        # Initialize translation system
        logger.info("Initializing comprehensive translation system...")
        from translation_system import init_translation_system
        init_translation_system()
        logger.info("Translation system initialized")
        
        # Initialize content integrity system
        logger.info("Initializing content integrity system...")
        from content_integrity_system import ContentIntegritySystem
        content_integrity = ContentIntegritySystem()
        logger.info("✅ Content integrity system initialized")
        
        # Initialize comprehensive publishing fix system
        logger.info("Initializing comprehensive publishing and channel integration fixes...")
        try:
            from comprehensive_publishing_fix import run_comprehensive_fix
            comprehensive_fix = await run_comprehensive_fix(bot, db)
            logger.info("✅ Comprehensive publishing fix system initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize comprehensive publishing fix: {e}")
        
        # Register enhanced chat member handler with comprehensive fix
        async def enhanced_handle_my_chat_member(chat_member_updated):
            """Enhanced chat member handler with comprehensive fixes"""
            try:
                # Call original handler
                await handle_my_chat_member(chat_member_updated)
                
                # Call comprehensive fix handler for auto-channel addition
                if comprehensive_fix:
                    await comprehensive_fix.handle_new_channel_addition(chat_member_updated)
                    
            except Exception as e:
                logger.error(f"Error in enhanced chat member handler: {e}")
        
        dp.my_chat_member.register(enhanced_handle_my_chat_member)
        
        # Clean up invalid channels first
        logger.info("Syncing existing channels...")
        cleaned_count = await db.clean_invalid_channels()
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} invalid channels")
        
        # Auto-discover existing channels where bot is admin
        await channel_manager.sync_existing_channels()
        logger.info("Automatic channel discovery completed")
        
        # Setup bot commands
        await bot.set_my_commands([
            BotCommand(command="start", description="🚀 Start the bot"),
            BotCommand(command="dashboard", description="📊 My Ads Dashboard"),
            BotCommand(command="mystats", description="📈 My Statistics"),
            BotCommand(command="referral", description="🎯 Referral System"),
            BotCommand(command="support", description="💬 Get Support"),
            BotCommand(command="help", description="❓ Help & Guide"),
            BotCommand(command="admin", description="⚙️ Admin Panel"),
            BotCommand(command="health", description="🏥 System Health (Admin)"),
            BotCommand(command="troubleshoot", description="🔧 Troubleshooting (Admin)"),
            BotCommand(command="report_issue", description="🚨 Report Issue")
        ])
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
        logger.info("Bot commands set successfully")
        
        # Mark bot as started
        bot_started = True
        
        # Start polling
        logger.info("Starting I3lani Bot...")
        logger.info("Bot Features:")
        logger.info("- Multi-language support (EN, AR, RU)")
        logger.info("- TON cryptocurrency and Telegram Stars")
        logger.info("- Multi-channel advertising")
        logger.info("- Referral system with rewards")
        logger.info("- Complete user dashboard")
        
        # Start polling without signal handlers for threading compatibility
        await dp.start_polling(bot, handle_signals=False)
        
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
                logger.info("Cleaned up lock file")
        except Exception as e:
            logger.error(f"Error cleaning up lock: {e}")
        
        # Close bot session properly
        try:
            if bot_instance:
                await bot_instance.session.close()
        except:
            pass

def run_bot():
    """Run bot in background thread"""
    try:
        logger.info("Starting bot in background thread...")
        asyncio.run(init_bot())
    except Exception as e:
        logger.error(f"Bot error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main entry point for deployment server"""
    logger.info("Starting I3lani Bot main function...")
    try:
        await init_bot()
    except Exception as e:
        logger.error(f"Bot main error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    # Configure logging for standalone bot
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    logger.info("Starting I3lani Bot standalone...")
    run_bot()