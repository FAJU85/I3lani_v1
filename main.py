import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from config import BOT_TOKEN, ADMIN_IDS, CHANNEL_ID, TON_WALLET_ADDRESS
from handlers import register_handlers
from languages import get_text
from scheduler import ScheduleManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Initialize scheduler
schedule_manager = ScheduleManager(bot)

class AdStates(StatesGroup):
    waiting_for_ad = State()
    waiting_for_payment = State()
    waiting_for_admin_approval = State()

async def on_startup(dp):
    """Initialize bot on startup"""
    logger.info("Bot started")
    # Start the scheduler
    asyncio.create_task(schedule_manager.run_scheduler())
    
    # Notify admins that bot is online
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, get_text(admin_id, "bot_online"))
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

async def on_shutdown(dp):
    """Cleanup on shutdown"""
    logger.info("Bot shutting down")
    await dp.storage.close()
    await dp.storage.wait_closed()

if __name__ == '__main__':
    # Register handlers
    register_handlers(dp, bot, schedule_manager)
    
    # Start bot
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )
