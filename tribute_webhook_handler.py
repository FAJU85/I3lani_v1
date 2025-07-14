"""
Tribute.tg Webhook Handler for I3lani Bot
Handles incoming webhooks from Tribute.tg for orders and subscriptions
"""

import json
import hmac
import hashlib
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
from typing import Dict, Any

class TributeWebhookHandler:
    """
    Handles Tribute.tg webhook requests
    Processes orders and subscriptions in real-time
    """
    
    def __init__(self, app: Flask, tribute_integration, api_key: str):
        self.app = app
        self.tribute_integration = tribute_integration
        self.api_key = api_key
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes for webhook handling"""
        
        @self.app.route('/tribute/webhook', methods=['POST'])
        def handle_tribute_webhook():
            """Handle incoming Tribute.tg webhooks"""
            try:
                # Get request data
                body = request.get_data()
                signature = request.headers.get('trbt-signature', '')
                
                # Verify webhook signature
                if not self.verify_signature(body, signature):
                    return jsonify({"error": "Invalid signature"}), 401
                
                # Parse webhook data
                webhook_data = json.loads(body.decode('utf-8'))
                
                # Process webhook asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(
                        self.process_webhook(webhook_data)
                    )
                    return jsonify(result), 200
                finally:
                    loop.close()
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        
        @self.app.route('/tribute/status', methods=['GET'])
        def tribute_status():
            """Check Tribute integration status"""
            return jsonify({
                "status": "active",
                "integration": "tribute.tg",
                "supported_events": [
                    "new_subscription",
                    "cancelled_subscription",
                    "physical_order_created",
                    "physical_order_shipped",
                    "physical_order_canceled"
                ],
                "timestamp": datetime.now().isoformat()
            })
    
    def verify_signature(self, body: bytes, signature: str) -> bool:
        """Verify webhook signature using HMAC-SHA256"""
        expected_signature = hmac.new(
            self.api_key.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook based on event type"""
        event_name = webhook_data.get("name")
        
        if event_name in ["physical_order_created", "physical_order_shipped", "physical_order_canceled"]:
            return await self.tribute_integration.handle_order_webhook(webhook_data)
        elif event_name in ["new_subscription", "cancelled_subscription"]:
            return await self.tribute_integration.handle_subscription_webhook(webhook_data)
        else:
            return {"success": False, "error": f"Unknown event type: {event_name}"}

class TributeAdminPanel:
    """
    Admin panel integration for Tribute.tg management
    """
    
    def __init__(self, tribute_integration):
        self.tribute_integration = tribute_integration
    
    async def get_tribute_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for Tribute integration"""
        try:
            async with self.tribute_integration.db.get_connection() as conn:
                # Get order statistics
                order_stats = await conn.execute("""
                    SELECT 
                        COUNT(*) as total_orders,
                        SUM(total_amount) as total_revenue,
                        COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                        COUNT(CASE WHEN status = 'shipped' THEN 1 END) as shipped_orders,
                        COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_orders
                    FROM tribute_orders
                """).fetchone()
                
                # Get subscription statistics
                sub_stats = await conn.execute("""
                    SELECT 
                        COUNT(*) as total_subscriptions,
                        SUM(amount) as total_sub_revenue,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_subscriptions
                    FROM tribute_subscriptions
                """).fetchone()
                
                # Get recent orders
                recent_orders = await conn.execute("""
                    SELECT order_id, telegram_user_id, status, total_amount, currency, created_at
                    FROM tribute_orders
                    ORDER BY created_at DESC
                    LIMIT 10
                """).fetchall()
                
                # Get recent subscriptions
                recent_subs = await conn.execute("""
                    SELECT subscription_name, telegram_user_id, amount, currency, status, created_at
                    FROM tribute_subscriptions
                    ORDER BY created_at DESC
                    LIMIT 10
                """).fetchall()
                
                return {
                    "order_stats": dict(order_stats) if order_stats else {},
                    "subscription_stats": dict(sub_stats) if sub_stats else {},
                    "recent_orders": [dict(row) for row in recent_orders],
                    "recent_subscriptions": [dict(row) for row in recent_subs],
                    "status": "active",
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def create_tribute_admin_keyboard(self):
        """Create admin keyboard for Tribute management"""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📦 Orders Dashboard", callback_data="tribute_orders"),
                InlineKeyboardButton(text="💳 Subscriptions", callback_data="tribute_subscriptions")
            ],
            [
                InlineKeyboardButton(text="📊 Analytics", callback_data="tribute_analytics"),
                InlineKeyboardButton(text="⚙️ Settings", callback_data="tribute_settings")
            ],
            [
                InlineKeyboardButton(text="🔄 Sync Orders", callback_data="tribute_sync"),
                InlineKeyboardButton(text="🧪 Test Webhook", callback_data="tribute_test")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to Admin", callback_data="admin_main")
            ]
        ])
        
        return keyboard
    
    async def format_tribute_dashboard_text(self, dashboard_data: Dict[str, Any]) -> str:
        """Format dashboard data for display"""
        if "error" in dashboard_data:
            return f"❌ **Tribute Integration Error**\n\n{dashboard_data['error']}"
        
        order_stats = dashboard_data.get("order_stats", {})
        sub_stats = dashboard_data.get("subscription_stats", {})
        
        text = f"""🎯 **Tribute.tg Integration Dashboard**

📦 **Order Statistics:**
• Total Orders: {order_stats.get('total_orders', 0)}
• Total Revenue: ${order_stats.get('total_revenue', 0):.2f}
• Pending: {order_stats.get('pending_orders', 0)}
• Shipped: {order_stats.get('shipped_orders', 0)}
• Delivered: {order_stats.get('delivered_orders', 0)}

💳 **Subscription Statistics:**
• Active Subscriptions: {sub_stats.get('active_subscriptions', 0)}
• Total Subscriptions: {sub_stats.get('total_subscriptions', 0)}
• Subscription Revenue: ${sub_stats.get('total_sub_revenue', 0)/100:.2f}

📊 **Recent Activity:**
• Last Updated: {dashboard_data.get('last_updated', 'N/A')}
• Status: {dashboard_data.get('status', 'Unknown').title()}

Use the buttons below to manage your Tribute integration."""
        
        return text

# Integration with deployment server
def setup_tribute_integration(app: Flask, tribute_integration, api_key: str):
    """Setup Tribute integration with Flask app"""
    webhook_handler = TributeWebhookHandler(app, tribute_integration, api_key)
    return webhook_handler

# Admin handlers for Tribute integration
async def tribute_admin_callback(callback_query, state):
    """Handle Tribute admin callbacks"""
    from main_bot import bot
    
    data = callback_query.data
    
    if data == "tribute_orders":
        await show_tribute_orders(callback_query, state)
    elif data == "tribute_subscriptions":
        await show_tribute_subscriptions(callback_query, state)
    elif data == "tribute_analytics":
        await show_tribute_analytics(callback_query, state)
    elif data == "tribute_settings":
        await show_tribute_settings(callback_query, state)
    elif data == "tribute_sync":
        await sync_tribute_orders(callback_query, state)
    elif data == "tribute_test":
        await test_tribute_webhook(callback_query, state)

async def show_tribute_orders(callback_query, state):
    """Show Tribute orders dashboard"""
    # Implementation for orders dashboard
    pass

async def show_tribute_subscriptions(callback_query, state):
    """Show Tribute subscriptions dashboard"""
    # Implementation for subscriptions dashboard
    pass

async def show_tribute_analytics(callback_query, state):
    """Show Tribute analytics"""
    # Implementation for analytics dashboard
    pass

async def show_tribute_settings(callback_query, state):
    """Show Tribute settings"""
    # Implementation for settings management
    pass

async def sync_tribute_orders(callback_query, state):
    """Sync orders from Tribute API"""
    # Implementation for manual sync
    pass

async def test_tribute_webhook(callback_query, state):
    """Test Tribute webhook functionality"""
    # Implementation for webhook testing
    pass

"""
TRIBUTE INTEGRATION FEATURES:

1. **Real-time Order Processing**
   - Instant ad creation for new orders
   - Automatic campaign generation
   - Product promotion across channels

2. **Subscription Management**
   - Subscriber benefits and rewards
   - Free campaign allocation
   - Premium feature access

3. **Admin Dashboard**
   - Order and subscription analytics
   - Revenue tracking
   - Integration status monitoring

4. **Webhook Security**
   - HMAC-SHA256 signature verification
   - Secure payload processing
   - Error handling and logging

5. **Automated Workflows**
   - Order-to-ad automation
   - Subscription benefit granting
   - Cross-platform notifications

DEPLOYMENT REQUIREMENTS:
- TRIBUTE_API_KEY environment variable
- Webhook URL configuration in Tribute dashboard
- Database schema initialization
- Flask route integration
"""