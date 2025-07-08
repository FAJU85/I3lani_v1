"""
Complete Telegram Stars Handler Integration
Combines aiogram bot handlers with Flask backend webhook processing
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
import requests
from threading import Thread

from aiogram import Bot, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from flask import Flask, request, jsonify

from config import BOT_TOKEN, ADMIN_IDS, CHANNEL_ID
from database import Database
# Stars configuration inline
STARS_PACKAGE_PRICES = {
    'bronze': {'name': '1 Month', 'price_stars': 306, 'price_usd': 9, 'duration_days': 30},
    'silver': {'name': '3 Months', 'price_stars': 918, 'price_usd': 27, 'duration_days': 90},
    'gold': {'name': '6 Months', 'price_stars': 1323, 'price_usd': 49, 'duration_days': 180}
}

def get_package_by_stars(stars_amount):
    """Get package by stars amount"""
    for package_id, package in STARS_PACKAGE_PRICES.items():
        if package['price_stars'] == stars_amount:
            return package_id, package
    return None, None

def convert_stars_to_usd(stars_amount):
    """Convert stars to USD"""
    return stars_amount / 34  # 34 stars per USD

def get_invoice_config(package_id):
    """Get invoice configuration for package"""
    if package_id in STARS_PACKAGE_PRICES:
        package = STARS_PACKAGE_PRICES[package_id]
        return {
            'title': f"I3lani Bot - {package['name']}",
            'description': f"Premium advertising package for {package['duration_days']} days",
            'payload': f"package_{package_id}",
            'provider_token': "",
            'currency': "XTR",
            'prices': [{"label": package['name'], "amount": package['price_stars']}]
        }
    return None

# Webhook configuration
WEBHOOK_CONFIG = {
    'host': '0.0.0.0',
    'port': 5001,
    'debug': False,
    'threaded': True
}

from languages import get_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router for Stars handlers
stars_router = Router()

class TelegramStarsHandler:
    """Complete Telegram Stars payment handler"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.database = Database()
        self.bot_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}'
        self.purchases = []
        self.flask_app = None
        
    async def initialize(self):
        """Initialize the Stars handler"""
        try:
            await self.database.init_db()
            self.setup_flask_backend()
            logger.info("✅ Telegram Stars handler initialized")
        except Exception as e:
            logger.error(f"Error initializing Stars handler: {e}")
    
    def setup_flask_backend(self):
        """Setup Flask backend for webhook handling"""
        self.flask_app = Flask(__name__)
        
        @self.flask_app.route('/health')
        def health_check():
            """Health check endpoint for troubleshooting system"""
            return {'status': 'ok', 'timestamp': datetime.now().isoformat()}, 200
        
        @self.flask_app.route('/', methods=['GET'])
        def home():
            return jsonify({
                "service": "I3lani Telegram Stars Backend",
                "status": "running",
                "packages": list(STARS_PACKAGE_PRICES.keys()),
                "version": "1.0.0"
            })
        
        @self.flask_app.route('/webhook', methods=['POST'])
        def webhook():
            try:
                update = request.get_json()
                if "write_access_request" in update:
                    success = asyncio.run(self.handle_write_access_request(update))
                    return jsonify({"ok": success})
                return jsonify({"ok": True})
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.flask_app.route('/balance', methods=['GET'])
        def get_balance():
            return jsonify(self.get_stars_balance())
        
        @self.flask_app.route('/stats', methods=['GET'])
        def get_stats():
            return jsonify(self.get_payment_stats())
        
        # Start Flask in separate thread only if not disabled
        if not os.environ.get('DISABLE_STARS_FLASK'):
            def run_flask():
                self.flask_app.run(
                    host=WEBHOOK_CONFIG['host'],
                    port=WEBHOOK_CONFIG['port'],
                    debug=WEBHOOK_CONFIG['debug'],
                    threaded=WEBHOOK_CONFIG['threaded']
                )
            
            Thread(target=run_flask, daemon=True).start()
            logger.info(f"✅ Flask backend started on port {WEBHOOK_CONFIG['port']}")
        else:
            logger.info("✅ Flask backend disabled - using main deployment server")
    
    async def create_stars_invoice(self, user_id: int, package_id: str, ad_content: str = None):
        """Create Telegram Stars invoice"""
        try:
            # Get package configuration
            package = STARS_PACKAGE_PRICES[package_id]
            invoice_config = get_invoice_config(package_id)
            
            # Create payload
            payload = {
                'user_id': user_id,
                'package_id': package_id,
                'ad_content': ad_content or 'Default content',
                'timestamp': datetime.now().isoformat()
            }
            
            # Prepare invoice data
            invoice_data = {
                'chat_id': user_id,
                'payload': json.dumps(payload),
                **invoice_config
            }
            
            # Send invoice
            response = requests.post(
                f"{self.bot_api_url}/sendInvoice",
                json=invoice_data
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Stars invoice created for user {user_id}")
                return True
            else:
                logger.error(f"Failed to create Stars invoice: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating Stars invoice: {e}")
            return False
    
    async def handle_write_access_request(self, update_data: Dict[str, Any]):
        """Handle write access request from Telegram Stars"""
        try:
            req = update_data['write_access_request']
            user = req['user']
            stars = req['stars']
            
            user_id = user['id']
            username = user.get('username', 'NoUsername')
            
            # Get package by stars amount
            package = get_package_by_stars(stars)
            
            # Create purchase record
            purchase_record = {
                'user_id': user_id,
                'username': username,
                'package_id': package['id'],
                'stars_amount': stars,
                'usd_value': convert_stars_to_usd(stars),
                'timestamp': datetime.now().isoformat(),
                'status': 'confirmed'
            }
            
            self.purchases.append(purchase_record)
            logger.info(f"✅ Stars payment received: {purchase_record}")
            
            # Process payment
            await self.process_stars_payment(purchase_record)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling write access request: {e}")
            return False
    
    async def process_stars_payment(self, purchase_record: Dict[str, Any]):
        """Process confirmed Stars payment"""
        try:
            user_id = purchase_record['user_id']
            package_id = purchase_record['package_id']
            stars_amount = purchase_record['stars_amount']
            
            # Get package details
            package = STARS_PACKAGE_PRICES[package_id]
            
            # Create ad record
            ad_id = await self.database.create_ad(
                user_id=user_id,
                content=f"Telegram Stars payment - {package['name']}",
                media_url=None,
                content_type='text'
            )
            
            # Create subscription
            subscription_id = await self.database.create_subscription(
                user_id=user_id,
                ad_id=ad_id,
                channel_id=CHANNEL_ID,
                duration_months=package['duration_days'],
                total_price=package['usd_value'],
                currency='STARS'
            )
            
            # Create payment record
            payment_id = await self.database.create_payment(
                user_id=user_id,
                subscription_id=subscription_id,
                amount=stars_amount,
                currency='STARS',
                payment_method='telegram_stars',
                memo=f'STARS{subscription_id:04d}'
            )
            
            # Send confirmation
            await self.send_stars_confirmation(user_id, package_id, stars_amount)
            
            # Notify admins
            await self.notify_admins_stars_payment(user_id, package_id, stars_amount)
            
            logger.info(f"✅ Stars payment processed: subscription {subscription_id}")
            
        except Exception as e:
            logger.error(f"Error processing Stars payment: {e}")
    
    async def send_stars_confirmation(self, user_id: int, package_id: str, stars_amount: int):
        """Send Stars payment confirmation"""
        try:
            package = STARS_PACKAGE_PRICES[package_id]
            
            text = f"""
🌟 **Telegram Stars Payment Confirmed!**

**Package:** {package['name']}
**Amount:** {stars_amount} ⭐
**USD Value:** ${package['usd_value']}
**Duration:** {package['duration_days']} days
**Posts per Day:** {package['posts_per_day']}

Your advertising campaign is now active!

📊 Track progress: /mystats
📝 Create new ad: /start
💬 Get support: /support

Thank you for choosing I3lani Bot! 🚀
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 My Stats", callback_data="show_stats")],
                [InlineKeyboardButton(text="📝 New Ad", callback_data="create_ad")],
                [InlineKeyboardButton(text="🏠 Menu", callback_data="main_menu")]
            ])
            
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error sending Stars confirmation: {e}")
    
    async def notify_admins_stars_payment(self, user_id: int, package_id: str, stars_amount: int):
        """Notify admins of Stars payment"""
        try:
            package = STARS_PACKAGE_PRICES[package_id]
            
            text = f"""
🌟 **New Telegram Stars Payment**

**User:** {user_id}
**Package:** {package['name']}
**Amount:** {stars_amount} ⭐
**USD Value:** ${package['usd_value']}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Payment processed automatically.
            """.strip()
            
            for admin_id in ADMIN_IDS:
                try:
                    await self.bot.send_message(
                        chat_id=admin_id,
                        text=text,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error notifying admins: {e}")
    
    def get_stars_balance(self):
        """Get current Stars balance"""
        try:
            response = requests.get(f"{self.bot_api_url}/getMyStarBalance")
            if response.status_code == 200:
                return response.json()
            return {"error": "Failed to get balance"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_payment_stats(self):
        """Get payment statistics"""
        try:
            total_stars = sum(p['stars_amount'] for p in self.purchases)
            total_usd = sum(p['usd_value'] for p in self.purchases)
            
            return {
                'total_payments': len(self.purchases),
                'total_stars': total_stars,
                'total_usd_value': total_usd,
                'unique_users': len(set(p['user_id'] for p in self.purchases))
            }
        except Exception as e:
            return {"error": str(e)}

# Global handler instance
stars_handler = None

@stars_router.callback_query(lambda c: c.data.startswith('pay_stars_'))
async def handle_stars_payment(callback_query: CallbackQuery, state: FSMContext):
    """Handle Stars payment selection"""
    try:
        package_id = callback_query.data.replace('pay_stars_', '')
        user_id = callback_query.from_user.id
        
        # Get user's ad content from state
        data = await state.get_data()
        ad_content = data.get('ad_content', 'Default ad content')
        
        # Create Stars invoice
        success = await stars_handler.create_stars_invoice(user_id, package_id, ad_content)
        
        if success:
            await callback_query.answer("✅ Stars invoice created!")
            
            package = STARS_PACKAGE_PRICES[package_id]
            text = f"""
⭐ **Telegram Stars Payment**

**Package:** {package['name']}
**Price:** {package['stars']} ⭐
**Duration:** {package['duration_days']} days

Payment invoice has been sent to you.
Please complete the payment to activate your campaign.

With your payment, you agree to the Usage Agreement🔗
            """.strip()
            
            await callback_query.message.edit_text(
                text=text,
                parse_mode='Markdown'
            )
        else:
            await callback_query.answer("❌ Failed to create invoice")
            
    except Exception as e:
        logger.error(f"Error handling Stars payment: {e}")
        await callback_query.answer("❌ Payment error")

@stars_router.message(Command('stars_balance'))
async def stars_balance_command(message: Message):
    """Get current Stars balance"""
    try:
        balance = stars_handler.get_stars_balance()
        
        if 'error' in balance:
            text = f"❌ Error getting balance: {balance['error']}"
        else:
            text = f"⭐ **Current Stars Balance:** {balance.get('balance', 'N/A')} stars"
        
        await message.reply(text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting Stars balance: {e}")
        await message.reply("❌ Error retrieving balance")

@stars_router.message(Command('stars_stats'))
async def stars_stats_command(message: Message):
    """Get Stars payment statistics"""
    try:
        stats = stars_handler.get_payment_stats()
        
        if 'error' in stats:
            text = f"❌ Error getting stats: {stats['error']}"
        else:
            text = f"""
📊 **Telegram Stars Statistics**

**Total Payments:** {stats['total_payments']}
**Total Stars:** {stats['total_stars']} ⭐
**Total USD Value:** ${stats['total_usd_value']:.2f}
**Unique Users:** {stats['unique_users']}
            """.strip()
        
        await message.reply(text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting Stars stats: {e}")
        await message.reply("❌ Error retrieving statistics")

def init_stars_handler(bot: Bot):
    """Initialize Telegram Stars handler"""
    global stars_handler
    stars_handler = TelegramStarsHandler(bot)
    
    # Initialize asynchronously
    asyncio.create_task(stars_handler.initialize())
    
    logger.info("✅ Telegram Stars handler initialized")
    return stars_handler

def setup_stars_handlers(dp):
    """Setup Stars handlers"""
    dp.include_router(stars_router)
    logger.info("✅ Telegram Stars handlers registered")