"""
I3lani v3 Main Handlers
Replaces legacy handlers with V3 auction-based system
"""

from aiogram import Router, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from v3_bot_commands import V3BotCommands
from v3_admin_commands import V3AdminCommands
from v3_payment_integration import V3PaymentHandlers

class V3MainHandlers:
    """Main handler integration for V3 system"""
    
    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self.v3_commands = V3BotCommands(bot, dp)
        self.v3_admin = V3AdminCommands(bot, dp)
        self.v3_payments = V3PaymentHandlers(bot)
    
    def setup_all_handlers(self):
        """Setup all V3 handlers"""
        # Register V3 command handlers
        self.v3_commands.setup_handlers()
        
        # Register V3 admin handlers
        from v3_admin_commands import setup_v3_admin_handlers
        setup_v3_admin_handlers(self.dp, self.bot)
        
        # Register V3 payment handlers
        self.dp.callback_query.register(
            self.v3_payments.handle_ton_payment_callback,
            lambda c: c.data.startswith(("pay_ton_", "ton_confirm_", "pay_stars_", "payment_cancel_"))
        )
        
        self.dp.message.register(
            self.v3_payments.handle_stars_payment_success,
            lambda m: m.successful_payment is not None
        )

def setup_v3_handlers(dp: Dispatcher, bot: Bot):
    """Setup all V3 handlers - replaces legacy handler setup"""
    handlers = V3MainHandlers(bot, dp)
    handlers.setup_all_handlers()
    return handlers
