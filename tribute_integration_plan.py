"""
Tribute.tg Integration Plan for I3lani Bot
Complete integration strategy for physical product orders and subscriptions
"""

import asyncio
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class TributeOrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class TributeWebhookEvent(Enum):
    """Webhook event types"""
    NEW_SUBSCRIPTION = "new_subscription"
    CANCELLED_SUBSCRIPTION = "cancelled_subscription"
    PHYSICAL_ORDER_CREATED = "physical_order_created"
    PHYSICAL_ORDER_SHIPPED = "physical_order_shipped"
    PHYSICAL_ORDER_CANCELED = "physical_order_canceled"

@dataclass
class TributeOrder:
    """Tribute order data structure"""
    id: int
    status: str
    fullName: str
    email: str
    phone: str
    telegramID: int
    address: Dict[str, str]
    locality: str
    fullAddress: str
    customerNote: str
    items: List[Dict[str, Any]]
    deliveryCost: float
    currency: str
    created: str

@dataclass
class TributeSubscription:
    """Tribute subscription data structure"""
    subscription_id: int
    subscription_name: str
    period_id: int
    period: str
    price: int
    amount: int
    currency: str
    user_id: int
    telegram_user_id: int
    channel_id: int
    channel_name: str
    expires_at: str

class TributeIntegration:
    """
    Complete Tribute.tg Integration System
    Handles orders, subscriptions, and webhooks
    """
    
    def __init__(self, api_key: str, webhook_url: str):
        self.api_key = api_key
        self.webhook_url = webhook_url
        self.base_url = "https://tribute.tg/api/v1"
        
    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """Verify webhook signature using HMAC-SHA256"""
        expected_signature = hmac.new(
            self.api_key.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    
    async def get_orders(self, 
                        last_order_id: Optional[str] = None,
                        status: Optional[List[str]] = None,
                        limit: int = 50,
                        page: int = 1) -> Dict[str, Any]:
        """Get orders list with pagination and filtering"""
        import aiohttp
        
        params = {
            "limit": limit,
            "page": page
        }
        
        if last_order_id:
            params["lastOrderId"] = last_order_id
        if status:
            params["status"] = status
            
        headers = {
            "Api-Key": self.api_key,
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/physical/orders",
                params=params,
                headers=headers
            ) as response:
                return await response.json()
    
    async def get_order_details(self, order_id: int) -> Dict[str, Any]:
        """Get detailed order information"""
        import aiohttp
        
        headers = {
            "Api-Key": self.api_key,
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/physical/orders/{order_id}",
                headers=headers
            ) as response:
                return await response.json()
    
    def parse_order_webhook(self, payload: Dict[str, Any]) -> TributeOrder:
        """Parse order webhook payload"""
        order_data = payload.get("payload", {})
        
        return TributeOrder(
            id=order_data.get("order_id"),
            status=order_data.get("status"),
            fullName="",  # Not included in webhook
            email="",     # Not included in webhook
            phone="",     # Not included in webhook
            telegramID=order_data.get("telegram_user_id"),
            address={},   # Not included in webhook
            locality="",  # Not included in webhook
            fullAddress=order_data.get("shipping_address", ""),
            customerNote="",  # Not included in webhook
            items=order_data.get("products", []),
            deliveryCost=0.0,  # Not included in webhook
            currency=order_data.get("currency"),
            created=order_data.get("created_at")
        )
    
    def parse_subscription_webhook(self, payload: Dict[str, Any]) -> TributeSubscription:
        """Parse subscription webhook payload"""
        sub_data = payload.get("payload", {})
        
        return TributeSubscription(
            subscription_id=sub_data.get("subscription_id"),
            subscription_name=sub_data.get("subscription_name"),
            period_id=sub_data.get("period_id"),
            period=sub_data.get("period"),
            price=sub_data.get("price"),
            amount=sub_data.get("amount"),
            currency=sub_data.get("currency"),
            user_id=sub_data.get("user_id"),
            telegram_user_id=sub_data.get("telegram_user_id"),
            channel_id=sub_data.get("channel_id"),
            channel_name=sub_data.get("channel_name"),
            expires_at=sub_data.get("expires_at")
        )

class TributeI3laniIntegration:
    """
    I3lani Bot Integration with Tribute.tg
    Enhanced advertising features with physical product support
    """
    
    def __init__(self, tribute_api: TributeIntegration, database):
        self.tribute_api = tribute_api
        self.db = database
        
    async def initialize_tribute_database(self):
        """Initialize Tribute integration database tables"""
        async with self.db.get_connection() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tribute_orders (
                    id INTEGER PRIMARY KEY,
                    order_id INTEGER UNIQUE NOT NULL,
                    telegram_user_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    shipping_address TEXT,
                    tracking_number TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tribute_subscriptions (
                    id INTEGER PRIMARY KEY,
                    subscription_id INTEGER UNIQUE NOT NULL,
                    telegram_user_id INTEGER NOT NULL,
                    subscription_name TEXT NOT NULL,
                    period TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    channel_name TEXT,
                    status TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tribute_product_ads (
                    id INTEGER PRIMARY KEY,
                    campaign_id TEXT NOT NULL,
                    order_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    ad_content TEXT NOT NULL,
                    channels TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            await conn.commit()
    
    async def handle_order_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order webhook and create advertising campaign"""
        event_type = webhook_data.get("name")
        order = self.tribute_api.parse_order_webhook(webhook_data)
        
        if event_type == TributeWebhookEvent.PHYSICAL_ORDER_CREATED.value:
            return await self.create_order_ad_campaign(order)
        elif event_type == TributeWebhookEvent.PHYSICAL_ORDER_SHIPPED.value:
            return await self.update_order_shipping_status(order)
        elif event_type == TributeWebhookEvent.PHYSICAL_ORDER_CANCELED.value:
            return await self.cancel_order_ad_campaign(order)
            
        return {"success": False, "error": "Unknown event type"}
    
    async def create_order_ad_campaign(self, order: TributeOrder) -> Dict[str, Any]:
        """Create advertising campaign for new product order"""
        try:
            # Generate ad content for the product
            ad_content = self.generate_product_ad_content(order)
            
            # Create campaign in I3lani system
            from campaign_management import create_campaign_from_payment
            
            campaign_data = {
                'user_id': order.telegramID,
                'content': ad_content,
                'content_type': 'text',
                'duration': 7,  # 7-day campaign for product orders
                'channels': ['@i3lani', '@smshco'],  # Default channels
                'posts_per_day': 1,
                'source': 'tribute_order',
                'tribute_order_id': order.id
            }
            
            campaign_id = await create_campaign_from_payment(campaign_data)
            
            # Store in database
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO tribute_orders 
                    (order_id, telegram_user_id, status, total_amount, currency, 
                     shipping_address, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order.id,
                    order.telegramID,
                    order.status,
                    sum(item.get('price', 0) * item.get('quantity', 1) for item in order.items),
                    order.currency,
                    order.fullAddress,
                    order.created,
                    datetime.now().isoformat()
                ))
                
                await conn.execute("""
                    INSERT INTO tribute_product_ads 
                    (campaign_id, order_id, product_name, ad_content, channels, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    campaign_id,
                    order.id,
                    ', '.join(item.get('name', '') for item in order.items),
                    ad_content,
                    json.dumps(['@i3lani', '@smshco']),
                    'active',
                    datetime.now().isoformat()
                ))
                
                await conn.commit()
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "message": "Product advertising campaign created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create campaign: {str(e)}"
            }
    
    def generate_product_ad_content(self, order: TributeOrder) -> str:
        """Generate advertising content for product order"""
        products = order.items
        if not products:
            return "🛒 New product available! Check it out!"
        
        product_names = [item.get('name', 'Product') for item in products]
        total_value = sum(item.get('price', 0) * item.get('quantity', 1) for item in products)
        
        if len(product_names) == 1:
            content = f"""🔥 **{product_names[0]}** Now Available!
            
💰 Starting from ${total_value/100:.2f} {order.currency.upper()}
🚚 Fast shipping available
⭐ Quality guaranteed

Order now and get it delivered to your door!"""
        else:
            content = f"""🛍️ **Amazing Product Bundle Available!**
            
📦 **Includes:**
{chr(10).join(f"• {name}" for name in product_names)}

💰 Total Value: ${total_value/100:.2f} {order.currency.upper()}
🚚 Fast shipping available
⭐ Quality guaranteed

Don't miss out on this amazing deal!"""
        
        return content
    
    async def update_order_shipping_status(self, order: TributeOrder) -> Dict[str, Any]:
        """Update order shipping status and notify user"""
        try:
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    UPDATE tribute_orders 
                    SET status = ?, updated_at = ?
                    WHERE order_id = ?
                """, (order.status, datetime.now().isoformat(), order.id))
                await conn.commit()
            
            # Send notification to user
            await self.send_shipping_notification(order)
            
            return {"success": True, "message": "Order status updated"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_shipping_notification(self, order: TributeOrder):
        """Send shipping notification to user"""
        from main_bot import bot
        
        message = f"""📦 **Shipping Update!**
        
Your order #{order.id} has been shipped!
📍 **Shipping Address:** {order.fullAddress}
🚚 **Status:** {order.status.title()}

Track your order for delivery updates."""
        
        try:
            await bot.send_message(
                chat_id=order.telegramID,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Failed to send shipping notification: {e}")
    
    async def handle_subscription_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription webhook events"""
        event_type = webhook_data.get("name")
        subscription = self.tribute_api.parse_subscription_webhook(webhook_data)
        
        if event_type == TributeWebhookEvent.NEW_SUBSCRIPTION.value:
            return await self.create_subscription_benefits(subscription)
        elif event_type == TributeWebhookEvent.CANCELLED_SUBSCRIPTION.value:
            return await self.cancel_subscription_benefits(subscription)
            
        return {"success": False, "error": "Unknown subscription event"}
    
    async def create_subscription_benefits(self, subscription: TributeSubscription) -> Dict[str, Any]:
        """Create subscription benefits for user"""
        try:
            # Store subscription in database
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO tribute_subscriptions 
                    (subscription_id, telegram_user_id, subscription_name, period, 
                     amount, currency, channel_name, status, expires_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    subscription.subscription_id,
                    subscription.telegram_user_id,
                    subscription.subscription_name,
                    subscription.period,
                    subscription.amount,
                    subscription.currency,
                    subscription.channel_name,
                    'active',
                    subscription.expires_at,
                    datetime.now().isoformat()
                ))
                await conn.commit()
            
            # Grant subscription benefits (e.g., free ad campaigns)
            await self.grant_subscription_benefits(subscription)
            
            return {"success": True, "message": "Subscription benefits granted"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def grant_subscription_benefits(self, subscription: TributeSubscription):
        """Grant benefits to subscription users"""
        from main_bot import bot
        
        # Calculate benefits based on subscription amount
        free_campaigns = max(1, subscription.amount // 1000)  # 1 free campaign per $10
        
        message = f"""🎉 **Subscription Activated!**
        
**{subscription.subscription_name}**
💰 Amount: ${subscription.amount/100:.2f} {subscription.currency.upper()}
⏰ Period: {subscription.period}
📺 Channel: {subscription.channel_name}

🎁 **Your Benefits:**
• {free_campaigns} free advertising campaigns
• Priority support
• Extended campaign duration

Use /campaigns to create your free campaigns!"""
        
        try:
            await bot.send_message(
                chat_id=subscription.telegram_user_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Failed to send subscription notification: {e}")

# Integration configuration
TRIBUTE_INTEGRATION_CONFIG = {
    "api_endpoint": "https://tribute.tg/api/v1",
    "webhook_events": [
        "new_subscription",
        "cancelled_subscription", 
        "physical_order_created",
        "physical_order_shipped",
        "physical_order_canceled"
    ],
    "supported_currencies": ["USD", "EUR", "GBP"],
    "default_campaign_duration": 7,
    "subscription_benefits": {
        "free_campaigns_per_dollar": 0.1,
        "extended_duration_multiplier": 1.5,
        "priority_support": True
    }
}

"""
INTEGRATION BENEFITS FOR I3LANI BOT:

1. **Physical Product Integration**
   - Automatic ad campaigns for new product orders
   - Product promotion across I3lani channels
   - Order tracking and shipping notifications

2. **Subscription System**
   - Reward loyal subscribers with free ad campaigns
   - Tiered benefits based on subscription amount
   - Extended campaign durations for subscribers

3. **Enhanced Revenue Streams**
   - Commission from product sales
   - Subscription-based advertising packages
   - Premium features for Tribute subscribers

4. **Cross-Platform Synergy**
   - Tribute content promotion via I3lani channels
   - I3lani users can discover Tribute products
   - Integrated payment and reward systems

5. **Advanced Analytics**
   - Track product promotion effectiveness
   - Monitor subscription engagement
   - Optimize ad performance across platforms

IMPLEMENTATION STEPS:
1. Add Tribute API key to environment variables
2. Set up webhook endpoints in Flask server
3. Initialize database tables for Tribute integration
4. Create admin panel for Tribute management
5. Test webhook integration with Tribute platform
"""