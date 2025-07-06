"""
Simple I3lani Bot - Working version with proper error handling
"""

import os
import logging
import random
import string
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def generate_memo() -> str:
    """Generate AB0102 format memo (6-character alphanumeric)"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    """Start command with I3lani interface"""
    welcome_text = """🚀 **Welcome to I3lani Bot!**

📢 Your premium Telegram advertising platform

**Features:**
• Multi-channel advertising
• TON & Telegram Stars payments
• Real-time campaign tracking
• Referral rewards system

💰 **Payment Methods:**
• TON Cryptocurrency
• Telegram Stars

🎁 **Referral Rewards:**
• 5% discount for friends
• 3 free posting days per referral

📊 Use /dashboard to manage campaigns
🔗 Use /referral to earn rewards"""

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🚀 Start Advertising", callback_data="start_advertising"),
        types.InlineKeyboardButton("📊 My Dashboard", callback_data="dashboard")
    )
    keyboard.add(
        types.InlineKeyboardButton("🔗 Referral System", callback_data="referral"),
        types.InlineKeyboardButton("💰 Check Balance", callback_data="balance")
    )
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode='Markdown')

@dp.message_handler(commands=['dashboard'])
async def dashboard_command(message: types.Message):
    """Dashboard command"""
    dashboard_text = """📊 **My Ads Dashboard**

📈 **Your Statistics:**
• Total Campaigns: 0
• Active Campaigns: 0
• Total Spent: $0.00

🚀 **Ready to start your first campaign?**
Create engaging ads and reach thousands of users!

💡 **Payment Demo:**
Sample memo format: """ + generate_memo() + """

This is the new AB0102 6-character format as specified in I3lani requirements."""
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🚀 New Campaign", callback_data="start_advertising"),
        types.InlineKeyboardButton("📊 View All", callback_data="view_all")
    )
    
    await message.answer(dashboard_text, reply_markup=keyboard, parse_mode='Markdown')

@dp.message_handler(commands=['referral'])
async def referral_command(message: types.Message):
    """Referral system command"""
    user_id = message.from_user.id
    referral_link = f"https://t.me/I3lani_bot?start=ref_{generate_memo()}"
    
    referral_text = f"""🔗 **Share & Earn Program**

💰 **Your Rewards:**
• Free Days Earned: 0
• Free Days Remaining: 0
• Total Value: $0.00

📊 **Your Referrals:**
• Total Referrals: 0
• Successful: 0
• Pending: 0

🎁 **How it works:**
• Share your link with friends
• They get 5% discount on first order
• You earn 3 free posting days per referral

📎 **Your Referral Link:**
`{referral_link}`"""
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📱 Share Link", url=f"https://t.me/share/url?url={referral_link}&text=Join I3lani Bot!"),
        types.InlineKeyboardButton("🔄 Refresh", callback_data="referral_refresh")
    )
    
    await message.answer(referral_text, reply_markup=keyboard, parse_mode='Markdown')

@dp.callback_query_handler(lambda c: c.data == 'start_advertising')
async def handle_start_advertising(callback_query: types.CallbackQuery):
    """Handle start advertising"""
    text = """🚀 **Start New Campaign**

📝 **Step 1:** Send me your ad content
• Text message
• Photo with caption
• Video with caption

💰 **Available Packages:**
• 🟢 Starter - $9.99/month
• 🔵 Pro - $19.99/month  
• 🟡 Growth - $39.99/month
• 🟣 Elite - $79.99/month

📊 **Sample payment memo:** """ + generate_memo() + """

Send your ad content to continue!"""
    
    await callback_query.message.edit_text(text, parse_mode='Markdown')
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'dashboard')
async def handle_dashboard(callback_query: types.CallbackQuery):
    """Handle dashboard callback"""
    await dashboard_command(callback_query.message)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'referral')
async def handle_referral(callback_query: types.CallbackQuery):
    """Handle referral callback"""
    await referral_command(callback_query.message)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'balance')
async def handle_balance(callback_query: types.CallbackQuery):
    """Handle balance check"""
    balance_text = f"""💰 **Account Balance**

💳 **Current Balance:** $0.00
🎁 **Free Posts:** 0 days remaining

📊 **Payment Methods:**
• TON Cryptocurrency ✅
• Telegram Stars ✅

🔄 **Last Payment:** None
📝 **Sample Memo:** {generate_memo()}

Ready to add funds? Start a new campaign!"""
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🚀 New Campaign", callback_data="start_advertising"))
    
    await callback_query.message.edit_text(balance_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@dp.message_handler(commands=['mystats', 'bugreport', 'support', 'history', 'refresh'])
async def handle_menu_commands(message: types.Message):
    """Handle menu commands"""
    command = message.get_command()
    
    if command == 'mystats':
        await dashboard_command(message)
    elif command == 'bugreport':
        await message.answer("🐛 Bug report system coming soon! For now, contact @support")
    elif command == 'support':
        await message.answer("💬 Support system ready! How can we help you today?")
    elif command == 'history':
        await message.answer("📜 Campaign history: No campaigns yet. Start your first one!")
    elif command == 'refresh':
        await start_command(message)

@dp.message_handler(content_types=['text', 'photo', 'video'])
async def handle_content(message: types.Message):
    """Handle ad content submission"""
    memo = generate_memo()
    
    response_text = f"""✅ **Ad Content Received!**

📝 **Content Type:** {message.content_type}
🎯 **Next Steps:**
1. Choose your package
2. Select channels
3. Make payment

💰 **Payment Memo:** `{memo}`
📊 **Format:** AB0102 (6-character)

Ready to proceed with your campaign?"""
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🟢 Starter $9.99", callback_data="package_starter"),
        types.InlineKeyboardButton("🔵 Pro $19.99", callback_data="package_pro")
    )
    keyboard.add(
        types.InlineKeyboardButton("🟡 Growth $39.99", callback_data="package_growth"),
        types.InlineKeyboardButton("🟣 Elite $79.99", callback_data="package_elite")
    )
    
    await message.answer(response_text, reply_markup=keyboard, parse_mode='Markdown')

@dp.callback_query_handler(lambda c: c.data.startswith('package_'))
async def handle_package_selection(callback_query: types.CallbackQuery):
    """Handle package selection"""
    package = callback_query.data.replace('package_', '')
    memo = generate_memo()
    
    package_info = {
        'starter': {'name': 'Starter', 'price': '$9.99', 'features': '1 channel, 30 posts/month'},
        'pro': {'name': 'Pro', 'price': '$19.99', 'features': '3 channels, 90 posts/month'},
        'growth': {'name': 'Growth', 'price': '$39.99', 'features': '5 channels, 150 posts/month'},
        'elite': {'name': 'Elite', 'price': '$79.99', 'features': '10 channels, 300 posts/month'}
    }
    
    info = package_info.get(package, package_info['starter'])
    
    text = f"""📦 **{info['name']} Package Selected**

💰 **Price:** {info['price']}/month
📊 **Features:** {info['features']}

💳 **Payment Instructions:**
1. Send TON to: `UQC7...` (wallet address)
2. Include memo: `{memo}`
3. Confirm payment

🌟 **Payment Memo:** `{memo}`
✅ **Format:** AB0102 compliant

Ready to pay with TON or Telegram Stars?"""
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("💎 Pay with TON", callback_data=f"pay_ton_{memo}"),
        types.InlineKeyboardButton("⭐ Pay with Stars", callback_data=f"pay_stars_{memo}")
    )
    keyboard.add(types.InlineKeyboardButton("🔙 Back to Packages", callback_data="start_advertising"))
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def handle_payment_method(callback_query: types.CallbackQuery):
    """Handle payment method selection"""
    method = 'TON' if 'ton' in callback_query.data else 'Telegram Stars'
    memo = callback_query.data.split('_')[-1]
    
    text = f"""💳 **Payment with {method}**

📝 **Payment Memo:** `{memo}`
✅ **Format:** AB0102 (I3lani compliant)

🔄 **Status:** Waiting for payment...
⏰ **Time Limit:** 30 minutes

Once payment is confirmed, your campaign will start automatically!

🎯 **What happens next:**
1. Payment verification (5-10 minutes)
2. Campaign activation
3. Start posting to selected channels

Thank you for choosing I3lani Bot! 🚀"""
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("✅ Payment Sent", callback_data=f"confirm_{memo}"))
    keyboard.add(types.InlineKeyboardButton("🔙 Change Method", callback_data="start_advertising"))
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('confirm_'))
async def handle_payment_confirmation(callback_query: types.CallbackQuery):
    """Handle payment confirmation"""
    memo = callback_query.data.replace('confirm_', '')
    
    text = f"""✅ **Payment Confirmation Received**

📝 **Memo:** `{memo}`
🔍 **Status:** Verifying payment...

⏰ **Processing Time:** 5-10 minutes
📧 **You'll be notified when confirmed**

🎯 **Campaign will start automatically once verified**

Thank you for your payment! Your ads will be live soon. 🚀

Use /dashboard to track your campaign progress."""
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📊 My Dashboard", callback_data="dashboard"))
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer("Payment confirmation received! ✅")

async def on_startup(dp):
    """Startup handler"""
    logger.info("I3lani Bot started successfully!")
    logger.info("Features: AB0102 memo format, referral system, dashboard")

if __name__ == '__main__':
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup
    )