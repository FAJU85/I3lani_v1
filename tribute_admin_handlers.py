"""
Tribute.tg Admin Panel Handlers for I3lani Bot
Admin interface for managing Tribute integration
"""

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from admin_system import safe_callback_answer
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(lambda c: c.data == "admin_tribute")
async def admin_tribute_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Tribute integration management"""
    try:
        text = """🎯 **Tribute.tg Integration Dashboard**

**Status:** Ready for Configuration

**Available Features:**
• Physical product order automation
• Subscription-based premium features  
• Real-time webhook processing
• Cross-platform analytics
• Revenue sharing system

**Setup Required:**
1. Configure TRIBUTE_API_KEY in environment
2. Set webhook URL in Tribute dashboard
3. Initialize database schema
4. Test webhook integration

**Benefits:**
• Automatic ad campaigns for product orders
• Premium features for subscribers
• Additional revenue streams
• Enhanced user engagement

Use the buttons below to manage your Tribute integration."""
        
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
                InlineKeyboardButton(text="📋 Setup Guide", callback_data="tribute_setup_guide"),
                InlineKeyboardButton(text="🔙 Back to Admin", callback_data="admin_main")
            ]
        ])
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await safe_callback_answer(callback_query, "Tribute integration dashboard opened")
        
    except Exception as e:
        await safe_callback_answer(callback_query, f"Error: {str(e)}", show_alert=True)

@router.callback_query(lambda c: c.data == "admin_tribute_analytics")
async def admin_tribute_analytics_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Tribute analytics dashboard"""
    try:
        text = """📊 **Cross-Platform Analytics Dashboard**

**Tribute.tg Integration Metrics:**

📦 **Product Orders:**
• Total Orders: Setup Required
• Revenue Generated: Setup Required
• Conversion Rate: Setup Required

💳 **Subscriptions:**
• Active Subscriptions: Setup Required
• Monthly Revenue: Setup Required
• Churn Rate: Setup Required

🎯 **Ad Campaign Performance:**
• Orders → Campaigns: Setup Required
• Click-through Rate: Setup Required
• Revenue per Campaign: Setup Required

⚡ **Integration Status:**
• Webhook Status: Not configured
• API Connection: Not configured
• Database Schema: Not initialized

**Next Steps:**
1. Configure Tribute API key
2. Set up webhook endpoint
3. Initialize database tables
4. Test integration flow

Configure the integration to see detailed analytics."""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Configure Integration", callback_data="admin_tribute"),
                InlineKeyboardButton(text="📋 Setup Guide", callback_data="tribute_setup_guide")
            ],
            [
                InlineKeyboardButton(text="🔄 Refresh Data", callback_data="admin_tribute_analytics"),
                InlineKeyboardButton(text="🔙 Back to Admin", callback_data="admin_main")
            ]
        ])
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await safe_callback_answer(callback_query, "Tribute analytics dashboard opened")
        
    except Exception as e:
        await safe_callback_answer(callback_query, f"Error: {str(e)}", show_alert=True)

@router.callback_query(lambda c: c.data == "tribute_setup_guide")
async def tribute_setup_guide_handler(callback_query: CallbackQuery, state: FSMContext):
    """Show Tribute setup guide"""
    try:
        text = """📋 **Tribute.tg Integration Setup Guide**

**Step 1: Get API Key**
1. Go to Tribute Creator Dashboard
2. Click Settings (⋯) → API Keys
3. Generate new API key
4. Copy the key

**Step 2: Configure Environment**
Add to your environment variables:
```
TRIBUTE_API_KEY=your_api_key_here
TRIBUTE_WEBHOOK_URL=https://your-domain.com/tribute/webhook
```

**Step 3: Set Webhook URL**
1. In Tribute dashboard, go to webhook settings
2. Set URL: `https://your-domain.com/tribute/webhook`
3. Enable events: orders, subscriptions
4. Save configuration

**Step 4: Test Integration**
1. Use admin panel to test webhook
2. Create test order in Tribute
3. Verify campaign creation
4. Check analytics data

**Support:**
• Documentation: See TRIBUTE_INTEGRATION_GUIDE.md
• Testing: Use webhook test button
• Monitoring: Check integration status

The integration will automatically:
• Create ad campaigns for new orders
• Grant premium features to subscribers
• Process real-time webhooks
• Track cross-platform analytics"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎯 Back to Integration", callback_data="admin_tribute"),
                InlineKeyboardButton(text="🔙 Back to Admin", callback_data="admin_main")
            ]
        ])
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await safe_callback_answer(callback_query, "Setup guide displayed")
        
    except Exception as e:
        await safe_callback_answer(callback_query, f"Error: {str(e)}", show_alert=True)

@router.callback_query(lambda c: c.data == "tribute_orders")
async def tribute_orders_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Tribute orders dashboard"""
    try:
        text = """📦 **Tribute Orders Dashboard**

**Recent Orders:**
• No orders configured yet
• Setup integration to see order data

**Order Statistics:**
• Total Orders: 0
• Pending Orders: 0
• Shipped Orders: 0
• Revenue Generated: $0.00

**Campaign Generation:**
• Orders → Campaigns: 0
• Success Rate: N/A
• Average Campaign Duration: N/A

**Next Steps:**
1. Configure Tribute API key
2. Set up webhook endpoint
3. Create test order
4. Monitor campaign generation

Orders will automatically generate advertising campaigns when configured."""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Configure Integration", callback_data="admin_tribute"),
                InlineKeyboardButton(text="🔄 Refresh Orders", callback_data="tribute_orders")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to Integration", callback_data="admin_tribute")
            ]
        ])
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await safe_callback_answer(callback_query, "Orders dashboard displayed")
        
    except Exception as e:
        await safe_callback_answer(callback_query, f"Error: {str(e)}", show_alert=True)

@router.callback_query(lambda c: c.data == "tribute_subscriptions")
async def tribute_subscriptions_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Tribute subscriptions dashboard"""
    try:
        text = """💳 **Tribute Subscriptions Dashboard**

**Active Subscriptions:**
• No subscriptions configured yet
• Setup integration to see subscription data

**Subscription Statistics:**
• Total Subscriptions: 0
• Active Subscriptions: 0
• Monthly Revenue: $0.00
• Churn Rate: N/A

**Premium Benefits:**
• Free campaigns granted: 0
• Premium features activated: 0
• Subscriber retention: N/A

**Next Steps:**
1. Configure Tribute API key
2. Set up webhook endpoint
3. Create subscription tiers
4. Monitor subscriber benefits

Subscriptions will automatically grant premium features when configured."""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Configure Integration", callback_data="admin_tribute"),
                InlineKeyboardButton(text="🔄 Refresh Subscriptions", callback_data="tribute_subscriptions")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to Integration", callback_data="admin_tribute")
            ]
        ])
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await safe_callback_answer(callback_query, "Subscriptions dashboard displayed")
        
    except Exception as e:
        await safe_callback_answer(callback_query, f"Error: {str(e)}", show_alert=True)

@router.callback_query(lambda c: c.data == "tribute_test")
async def tribute_test_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Tribute webhook testing"""
    try:
        text = """🧪 **Tribute Webhook Testing**

**Test Status:** Ready for Configuration

**Available Tests:**
• Webhook signature verification
• Order creation simulation
• Subscription event processing
• Campaign generation testing
• Database integration validation

**Test Results:**
• Webhook endpoint: Not configured
• API connection: Not configured
• Database schema: Not initialized
• Campaign generation: Not tested

**How to Test:**
1. Configure API key and webhook URL
2. Create test order in Tribute dashboard
3. Monitor webhook delivery
4. Verify campaign creation
5. Check user notifications

**Debugging Tools:**
• Webhook payload logging
• Error tracking and reporting
• Performance monitoring
• Integration status checks

Setup the integration to enable webhook testing."""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Configure Integration", callback_data="admin_tribute"),
                InlineKeyboardButton(text="📋 Setup Guide", callback_data="tribute_setup_guide")
            ],
            [
                InlineKeyboardButton(text="🔄 Refresh Test Status", callback_data="tribute_test"),
                InlineKeyboardButton(text="🔙 Back to Integration", callback_data="admin_tribute")
            ]
        ])
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await safe_callback_answer(callback_query, "Test dashboard displayed")
        
    except Exception as e:
        await safe_callback_answer(callback_query, f"Error: {str(e)}", show_alert=True)

# Setup function to register handlers
def setup_tribute_admin_handlers(dp):
    """Setup Tribute admin handlers"""
    dp.include_router(router)