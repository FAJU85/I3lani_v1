"""
Integrated Telegram Stars Payment System
Combined aiogram bot + Flask backend approach for complete Stars payment handling
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
from threading import Thread
import requests
from flask import Flask, request, jsonify

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN, ADMIN_IDS, CHANNEL_ID
from database import Database
from languages import get_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramStarsHandler:
    """Complete Telegram Stars payment handler"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.database = Database()
        self.purchases = []
        self.bot_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}'
        
        # Package pricing in Stars
        self.package_prices = {
            'starter': {'stars': 15, 'usd': 1.5, 'duration': 7, 'posts_per_day': 1},
            'professional': {'stars': 75, 'usd': 7.5, 'duration': 15, 'posts_per_day': 2},
            'enterprise': {'stars': 225, 'usd': 22.5, 'duration': 30, 'posts_per_day': 3}
        }
    
    async def create_stars_invoice(self, user_id: int, package_type: str, ad_content: str = None):
        """Create Telegram Stars invoice"""
        try:
            package = self.package_prices.get(package_type, self.package_prices['starter'])
            
            # Create invoice payload
            payload = {
                'user_id': user_id,
                'package': package_type,
                'ad_content': ad_content or 'Default ad content',
                'timestamp': datetime.now().isoformat()
            }
            
            # Create invoice
            invoice_data = {
                'chat_id': user_id,
                'title': f'I3lani - {package_type.title()} Package',
                'description': f'Premium advertising package - {package["duration"]} days, {package["posts_per_day"]} posts/day',
                'payload': json.dumps(payload),
                'provider_token': '',  # Empty for Stars
                'currency': 'XTR',  # Telegram Stars currency
                'prices': [{'label': f'{package_type.title()} Package', 'amount': package['stars']}],
                'max_tip_amount': 0,
                'suggested_tip_amounts': [],
                'photo_url': 'https://i.imgur.com/I3lani-logo.png',  # Optional logo
                'photo_size': 512,
                'photo_width': 512,
                'photo_height': 512,
                'need_name': False,
                'need_phone_number': False,
                'need_email': False,
                'need_shipping_address': False,
                'send_phone_number_to_provider': False,
                'send_email_to_provider': False,
                'is_flexible': False
            }
            
            # Send invoice
            response = requests.post(
                f"{self.bot_api_url}/sendInvoice",
                json=invoice_data
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Stars invoice created for user {user_id}, package {package_type}")
                return True
            else:
                logger.error(f"Failed to create Stars invoice: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating Stars invoice: {e}")
            return False
    
    async def handle_pre_checkout_query(self, pre_checkout_query):
        """Handle pre-checkout query for Stars payment"""
        try:
            query_id = pre_checkout_query.id
            
            # Always approve Stars payments
            response = requests.post(
                f"{self.bot_api_url}/answerPreCheckoutQuery",
                json={
                    'pre_checkout_query_id': query_id,
                    'ok': True
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Pre-checkout approved for query {query_id}")
                return True
            else:
                logger.error(f"Failed to approve pre-checkout: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling pre-checkout: {e}")
            return False
    
    async def handle_successful_payment(self, message: Message):
        """Handle successful Stars payment"""
        try:
            payment = message.successful_payment
            user_id = message.from_user.id
            
            # Parse payload
            payload = json.loads(payment.invoice_payload)
            package_type = payload['package']
            ad_content = payload.get('ad_content', 'Default ad content')
            
            # Create purchase record
            purchase_record = {
                'user_id': user_id,
                'username': message.from_user.username or 'NoUsername',
                'package': package_type,
                'stars_amount': payment.total_amount,
                'currency': payment.currency,
                'payload': payload,
                'telegram_payment_charge_id': payment.telegram_payment_charge_id,
                'provider_payment_charge_id': payment.provider_payment_charge_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'confirmed'
            }
            
            self.purchases.append(purchase_record)
            logger.info(f"✅ Stars payment successful: {purchase_record}")
            
            # Process the payment
            await self.process_successful_payment(purchase_record, ad_content)
            
            # Send confirmation message
            await self.send_payment_confirmation(user_id, package_type, payment.total_amount)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling successful payment: {e}")
            return False
    
    async def process_successful_payment(self, purchase_record: Dict[str, Any], ad_content: str):
        """Process confirmed Stars payment"""
        try:
            user_id = purchase_record['user_id']
            package_type = purchase_record['package']
            stars_amount = purchase_record['stars_amount']
            
            # Get package details
            package_details = self.package_prices[package_type]
            
            # Create ad in database
            ad_id = await self.database.create_ad(
                user_id=user_id,
                content=ad_content,
                media_url=None,
                content_type='text'
            )
            
            # Create subscription
            subscription_id = await self.database.create_subscription(
                user_id=user_id,
                ad_id=ad_id,
                channel_id=CHANNEL_ID,
                duration_months=package_details['duration'],
                total_price=package_details['usd'],
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
            
            # Publish ad immediately
            await self.publish_ad_to_channel(ad_content, user_id, package_type)
            
            # Notify admins
            await self.notify_admins_stars_payment(user_id, package_type, stars_amount)
            
            logger.info(f"✅ Stars payment processed: subscription {subscription_id}")
            
        except Exception as e:
            logger.error(f"Error processing Stars payment: {e}")
    
    async def publish_ad_to_channel(self, ad_content: str, user_id: int, package_type: str):
        """Publish ad to the main channel"""
        try:
            # Format ad content
            formatted_content = f"""
🚀 **Sponsored Content**

{ad_content}

─────────────────────────
📢 Advertise with us: @I3lani_bot
            """.strip()
            
            # Send to channel
            await self.bot.send_message(
                chat_id=CHANNEL_ID,
                text=formatted_content,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Ad published to channel for user {user_id}, package {package_type}")
            
        except Exception as e:
            logger.error(f"Error publishing ad to channel: {e}")
    
    async def send_payment_confirmation(self, user_id: int, package_type: str, stars_amount: int):
        """Send payment confirmation to user"""
        try:
            package = self.package_prices[package_type]
            
            text = f"""
🌟 **Payment Confirmed!**

Thank you for your Telegram Stars payment!

**Package:** {package_type.title()}
**Amount:** {stars_amount} ⭐
**Duration:** {package['duration']} days
**Posts per Day:** {package['posts_per_day']}

Your ad has been published to our channel immediately!

📊 Track your campaign: /mystats
🔄 View history: /history
💬 Need help: /support

Thank you for choosing I3lani Bot! 🚀
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 My Statistics", callback_data="show_stats")],
                [InlineKeyboardButton(text="📝 Create New Ad", callback_data="create_ad")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
            ])
            
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            
            logger.info(f"✅ Payment confirmation sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending payment confirmation: {e}")
    
    async def notify_admins_stars_payment(self, user_id: int, package_type: str, stars_amount: int):
        """Notify admins of new Stars payment"""
        try:
            text = f"""
🌟 **New Telegram Stars Payment**

**User ID:** {user_id}
**Package:** {package_type.title()}
**Amount:** {stars_amount} ⭐
**USD Value:** ${self.package_prices[package_type]['usd']}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Payment processed automatically via Telegram Stars.
Ad has been published to the channel.
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
    
    async def create_payment_keyboard(self, package_type: str):
        """Create payment method selection keyboard"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Pay with Telegram Stars", callback_data=f"pay_stars_{package_type}")],
            [InlineKeyboardButton(text="💎 Pay with TON", callback_data=f"pay_ton_{package_type}")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="select_package")]
        ])
        return keyboard
    
    def get_stars_balance(self):
        """Get current Telegram Stars balance"""
        try:
            response = requests.get(f"{self.bot_api_url}/getMyStarBalance")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get stars balance: {response.text}")
                return {"error": "Failed to get balance"}
        except Exception as e:
            logger.error(f"Error getting stars balance: {e}")
            return {"error": str(e)}
    
    def get_payment_stats(self):
        """Get payment statistics"""
        try:
            total_stars = sum(p['stars_amount'] for p in self.purchases)
            total_usd = sum(self.package_prices[p['package']]['usd'] for p in self.purchases)
            
            stats = {
                'total_payments': len(self.purchases),
                'total_stars': total_stars,
                'total_usd_value': total_usd,
                'unique_users': len(set(p['user_id'] for p in self.purchases)),
                'package_breakdown': {}
            }
            
            for package in ['starter', 'professional', 'enterprise']:
                count = len([p for p in self.purchases if p['package'] == package])
                stats['package_breakdown'][package] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting payment stats: {e}")
            return {"error": str(e)}

# Flask backend integration
def create_stars_backend_app(stars_handler: TelegramStarsHandler):
    """Create Flask backend app for Stars webhook handling"""
    app = Flask(__name__)
    
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            "service": "I3lani Telegram Stars Backend",
            "status": "running",
            "version": "1.0.0"
        })
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Handle Telegram Stars webhook"""
        try:
            update = request.get_json()
            
            if "write_access_request" in update:
                # Handle write access request
                success = asyncio.run(handle_write_access_request(update, stars_handler))
                return jsonify({"ok": success})
            
            return jsonify({"ok": True})
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/balance', methods=['GET'])
    def get_balance():
        return jsonify(stars_handler.get_stars_balance())
    
    @app.route('/stats', methods=['GET'])
    def get_stats():
        return jsonify(stars_handler.get_payment_stats())
    
    return app

async def handle_write_access_request(update_data: Dict[str, Any], stars_handler: TelegramStarsHandler):
    """Handle write access request from Telegram"""
    try:
        req = update_data['write_access_request']
        user = req['user']
        stars = req['stars']
        
        # Process as successful payment
        fake_message = type('Message', (), {
            'from_user': type('User', (), {
                'id': user['id'],
                'username': user.get('username', 'NoUsername')
            })(),
            'successful_payment': type('Payment', (), {
                'total_amount': stars,
                'currency': 'XTR',
                'invoice_payload': json.dumps({
                    'user_id': user['id'],
                    'package': 'starter',  # Default package
                    'ad_content': 'Stars payment content'
                }),
                'telegram_payment_charge_id': f'stars_{stars}_{user["id"]}',
                'provider_payment_charge_id': 'stars_provider'
            })()
        })()
        
        return await stars_handler.handle_successful_payment(fake_message)
        
    except Exception as e:
        logger.error(f"Error handling write access request: {e}")
        return False

# Initialize the system
def init_telegram_stars_system(bot: Bot):
    """Initialize complete Telegram Stars system"""
    stars_handler = TelegramStarsHandler(bot)
    
    # Create Flask backend
    backend_app = create_stars_backend_app(stars_handler)
    
    # Start Flask backend in separate thread
    def run_backend():
        backend_app.run(host='0.0.0.0', port=5001, debug=False)
    
    backend_thread = Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    logger.info("✅ Telegram Stars system initialized with Flask backend")
    return stars_handler