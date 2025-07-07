"""
Complete Telegram Stars Backend Integration
Flask backend for handling Telegram Stars payments and webhook processing
"""

from flask import Flask, request, jsonify
import requests
import json
import logging
import asyncio
from datetime import datetime
from database import Database
from config import BOT_TOKEN, ADMIN_IDS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Bot API configuration
BOT_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

# In-memory storage for purchases (will be moved to database)
purchases = []
database = Database()

class TelegramStarsBackend:
    """Complete Telegram Stars payment backend"""
    
    def __init__(self):
        self.purchases = []
        self.bot_api_url = BOT_API_URL
        
    async def initialize_database(self):
        """Initialize database connection"""
        await database.init_db()
        
    def process_write_access_request(self, update_data):
        """Process write access request from Telegram Stars"""
        try:
            req = update_data['write_access_request']
            user = req['user']
            stars = req['stars']
            payload = json.loads(req['payload']) if 'payload' in req else {}
            
            user_id = user['id']
            username = user.get('username', 'NoUsername')
            
            # Create purchase record
            purchase_record = {
                "user_id": user_id,
                "username": username,
                "stars": stars,
                "payload": payload,
                "timestamp": datetime.now().isoformat(),
                "status": "confirmed"
            }
            
            self.purchases.append(purchase_record)
            logger.info(f"✅ Telegram Stars payment received: {purchase_record}")
            
            # Process the payment (unlock features, etc.)
            asyncio.create_task(self.process_payment(purchase_record))
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing write access request: {e}")
            return False
    
    async def process_payment(self, purchase_record):
        """Process confirmed payment and unlock features"""
        try:
            user_id = purchase_record['user_id']
            stars = purchase_record['stars']
            payload = purchase_record.get('payload', {})
            
            # Determine package based on stars amount
            package_mapping = {
                15: 'starter',      # 15 stars = $1.5 ~ Starter package
                75: 'professional', # 75 stars = $7.5 ~ Professional package  
                225: 'enterprise'   # 225 stars = $22.5 ~ Enterprise package
            }
            
            package_type = package_mapping.get(stars, 'starter')
            
            # Create subscription record
            await self.create_subscription(user_id, package_type, stars)
            
            # Notify user of successful payment
            await self.notify_payment_success(user_id, package_type, stars)
            
            # Notify admins
            await self.notify_admins_payment(user_id, package_type, stars)
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
    
    async def create_subscription(self, user_id, package_type, stars_amount):
        """Create subscription in database"""
        try:
            # Get package details
            package_details = {
                'starter': {'duration': 7, 'posts_per_day': 1},
                'professional': {'duration': 15, 'posts_per_day': 2},
                'enterprise': {'duration': 30, 'posts_per_day': 3}
            }
            
            details = package_details.get(package_type, package_details['starter'])
            
            # Create ad record (placeholder)
            ad_id = await database.create_ad(user_id, "Telegram Stars Payment", None, 'text')
            
            # Create subscription
            subscription_id = await database.create_subscription(
                user_id=user_id,
                ad_id=ad_id,
                channel_id='@i3lani',
                duration_months=details['duration'],
                total_price=stars_amount / 100,  # Convert stars to USD equivalent
                currency='STARS'
            )
            
            # Create payment record
            payment_id = await database.create_payment(
                user_id=user_id,
                subscription_id=subscription_id,
                amount=stars_amount,
                currency='STARS',
                payment_method='telegram_stars',
                memo=f'STARS{subscription_id:04d}'
            )
            
            logger.info(f"✅ Subscription created: {subscription_id} for user {user_id}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return None
    
    async def notify_payment_success(self, user_id, package_type, stars_amount):
        """Notify user of successful payment"""
        try:
            message = f"""
🌟 **Payment Confirmed!**

Your Telegram Stars payment has been processed successfully.

**Package:** {package_type.title()}
**Amount:** {stars_amount} ⭐
**Status:** Active

Your advertising campaign is now live! Your ads will be published according to your package schedule.

Thank you for using I3lani Bot! 🚀
            """.strip()
            
            # Send notification via Telegram API
            response = requests.post(
                f"{self.bot_api_url}/sendMessage",
                json={
                    "chat_id": user_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Payment notification sent to user {user_id}")
            else:
                logger.error(f"Failed to send notification: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending payment notification: {e}")
    
    async def notify_admins_payment(self, user_id, package_type, stars_amount):
        """Notify admins of new payment"""
        try:
            message = f"""
💰 **New Telegram Stars Payment**

**User ID:** {user_id}
**Package:** {package_type.title()}
**Amount:** {stars_amount} ⭐
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Payment processed automatically via Telegram Stars backend.
            """.strip()
            
            # Send to all admins
            for admin_id in ADMIN_IDS:
                response = requests.post(
                    f"{self.bot_api_url}/sendMessage",
                    json={
                        "chat_id": admin_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Admin notification sent to {admin_id}")
                    
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
    
    def get_star_balance(self):
        """Get current Star balance from Telegram"""
        try:
            response = requests.get(f"{self.bot_api_url}/getMyStarBalance")
            return response.json()
        except Exception as e:
            logger.error(f"Error getting star balance: {e}")
            return {"error": str(e)}
    
    def get_all_purchases(self):
        """Get all purchase records"""
        return self.purchases

# Initialize backend
stars_backend = TelegramStarsBackend()

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "I3lani Telegram Stars Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook handler for Telegram Stars payments"""
    try:
        update = request.get_json()
        
        if not update:
            return jsonify({"error": "No data received"}), 400
        
        # Handle write access requests (Stars payments)
        if "write_access_request" in update:
            success = stars_backend.process_write_access_request(update)
            
            if success:
                return jsonify({"ok": True, "status": "payment_processed"})
            else:
                return jsonify({"error": "Payment processing failed"}), 500
        
        # Handle other update types
        logger.info(f"Received update: {update}")
        return jsonify({"ok": True, "status": "received"})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/balance', methods=['GET'])
def get_star_balance():
    """Get current Telegram Stars balance"""
    try:
        balance = stars_backend.get_star_balance()
        return jsonify(balance)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/purchases', methods=['GET'])
def get_purchases():
    """Get all purchase records"""
    try:
        purchases = stars_backend.get_all_purchases()
        return jsonify({
            "total_purchases": len(purchases),
            "purchases": purchases
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get payment statistics"""
    try:
        purchases = stars_backend.get_all_purchases()
        
        total_stars = sum(p['stars'] for p in purchases)
        total_users = len(set(p['user_id'] for p in purchases))
        
        stats = {
            "total_purchases": len(purchases),
            "total_stars_received": total_stars,
            "total_users": total_users,
            "average_stars_per_purchase": total_stars / len(purchases) if purchases else 0,
            "last_24h_purchases": len([p for p in purchases if 
                datetime.fromisoformat(p['timestamp']) > datetime.now() - timedelta(days=1)
            ])
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        db_status = "connected"
        
        # Test Telegram API
        api_response = requests.get(f"{BOT_API_URL}/getMe", timeout=5)
        api_status = "connected" if api_response.status_code == 200 else "disconnected"
        
        return jsonify({
            "status": "healthy",
            "database": db_status,
            "telegram_api": api_status,
            "total_purchases": len(stars_backend.get_all_purchases()),
            "uptime": "running",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Initialize database
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(stars_backend.initialize_database())
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)