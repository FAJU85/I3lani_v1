"""
I3lani Pricing System - Following Psychological Pricing Strategies
Based on the I3lani specifications for optimal user conversion
"""

from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import db
from languages import get_text
from database import get_user_language

router = Router()

@router.callback_query(F.data == "pricing")
async def show_i3lani_pricing(callback_query: CallbackQuery):
    """I3lani pricing system with psychological strategies"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get user's free ads status
    user = await db.get_user(user_id)
    free_ads_used = user.get('free_ads_used', 0) if user else 0
    free_ads_remaining = max(0, 3 - free_ads_used)
    
    # Get admin-created packages for dynamic pricing
    packages = await db.get_packages(active_only=True)
    
    # I3lani Psychological Pricing Flow
    pricing_text = f"""
💎 **I3lani Premium Advertising Platform**

🎯 **Step 1: Choose Your Target Channel**

📈 **Tech News Channel** 🔥 **Most Popular**
• 👥 **45,000** active subscribers
• 📊 **8.2%** engagement rate
• 🚀 **#1 Choice** - Best performing channel
• 💰 Base: **25 TON/month**

🎮 **Gaming Hub Channel**
• 👥 **32,000** gaming enthusiasts  
• 📊 **12.1%** engagement rate
• 🎯 Perfect for gaming & entertainment
• 💰 Base: **20 TON/month**

💼 **Business Tips Channel** 🪤 **Special Offer**
• 👥 **28,000** business professionals
• 📊 **6.8%** engagement rate
• 📈 Great for B2B content (Decoy pricing)
• 💰 Base: **18 TON/month**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Step 2: Choose Duration** ⏰ **Save More!**

⏱️ **1 Month** - Base Price
• 30 days advertising
• Daily posting schedule
• Basic analytics
• 💰 **Full Price** 

⏱️ **3 Months** 💰 **Save 5 TON**
• 90 days advertising
• Daily + weekend bonus posts
• Advanced analytics
• 🔥 **Popular Choice**

⏱️ **6 Months** 🔥 **Best Value - Save 20 TON**
• 180 days advertising
• Premium posting schedule
• Full analytics suite
• 👑 **Maximum Savings** (Default selection)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 **Quick Select Packages:**

🎁 **Free Trial** - {free_ads_remaining}/3 remaining
• 3 days advertising
• 1 channel access
• Basic analytics
• **Price: FREE**

"""

    # Add admin-created packages with psychological presentation
    if packages:
        for package in packages:
            emoji = "💰"
            if "bronze" in package['name'].lower() or "basic" in package['name'].lower():
                emoji = "🟫"
            elif "silver" in package['name'].lower() or "premium" in package['name'].lower():
                emoji = "🥈"
            elif "gold" in package['name'].lower() or "enterprise" in package['name'].lower():
                emoji = "🥇"
                
            pricing_text += f"{emoji} **{package['name']}**\n"
            pricing_text += f"• Duration: {package['duration_days']} days\n"
            pricing_text += f"• {package['posts_per_day']} posts per day\n"
            pricing_text += f"• {package['channels_included']} channels included\n"
            pricing_text += f"• **Price: ${package['price_usd']}**\n\n"
    else:
        # Fallback with psychological pricing structure
        pricing_text += """🟫 **Bronze Package** (Anchor pricing)
• 1 month duration
• 1 post per day
• 2 channels access
• **Price: $10**

🥈 **Silver Package** (Popular choice)
• 3 months duration
• 3 posts per day
• 3 channels access
• **Save 15%** vs monthly
• **Price: $29**

🥇 **Gold Package** 🔥 **Best Value**
• 6 months duration
• 5 posts per day
• All channels access
• **Save 25%** vs monthly
• **Price: $47** (Pre-selected)

"""
    
    pricing_text += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 **Limited Time Offers:**
• 🎯 **FOMO**: Only 10 slots left this week!
• 💰 **Referral Bonus**: 5% off for friend referrals
• ⏰ **Exit Intent**: Special offers when canceling

📊 **Why Choose I3lani?**
✅ Guaranteed posting within 24 hours
✅ Real-time blockchain-verified payments
✅ Professional analytics dashboard
✅ Money-back guarantee
✅ 24/7 customer support

🔧 **Admin Control**: All prices and channels managed via admin panel."""

    # Build psychological pricing keyboard
    keyboard_buttons = []
    
    # Channel selection (Step 1) - Psychological ordering with decoy effect
    keyboard_buttons.append([
        InlineKeyboardButton(text="📈 Tech News (45K) 🔥 Most Popular", callback_data="select_channel_tech")
    ])
    keyboard_buttons.append([
        InlineKeyboardButton(text="🎮 Gaming Hub (32K)", callback_data="select_channel_gaming"),
        InlineKeyboardButton(text="💼 Business Tips (28K) 🪤", callback_data="select_channel_business")
    ])
    
    # Duration selection (Step 2) - Default bias toward 6 months
    keyboard_buttons.append([
        InlineKeyboardButton(text="⏰ 1 Month - Base Price", callback_data="select_duration_1month")
    ])
    keyboard_buttons.append([
        InlineKeyboardButton(text="⏰ 3 Months - Save 5 TON 💰", callback_data="select_duration_3months")
    ])
    keyboard_buttons.append([
        InlineKeyboardButton(text="⏰ 6 Months - Save 20 TON 🔥 BEST", callback_data="select_duration_6months")
    ])
    
    # Visual separator
    keyboard_buttons.append([InlineKeyboardButton(text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", callback_data="separator")])
    
    # Free trial (foot-in-door technique)
    keyboard_buttons.append([
        InlineKeyboardButton(text="🎁 Start Free Trial (3 Days)", callback_data="select_package_free")
    ])
    
    # Admin packages (dynamic) - Ordered by psychological impact
    if packages:
        # Sort packages by price (highest first for anchor pricing)
        sorted_packages = sorted(packages, key=lambda p: p['price_usd'], reverse=True)
        
        package_row = []
        for package in sorted_packages:
            emoji = "💰"
            if "bronze" in package['name'].lower() or "basic" in package['name'].lower():
                emoji = "🟫"
            elif "silver" in package['name'].lower() or "premium" in package['name'].lower():
                emoji = "🥈" 
            elif "gold" in package['name'].lower() or "enterprise" in package['name'].lower():
                emoji = "🥇"
                
            # Add psychological cues to button text
            button_text = f"{emoji} {package['name']} ${package['price_usd']}"
            if package['price_usd'] >= 40:
                button_text += " 🔥 Best"
            elif package['price_usd'] >= 25:
                button_text += " 💰 Popular"
                
            package_row.append(InlineKeyboardButton(
                text=button_text,
                callback_data=f"select_package_{package['package_id']}"
            ))
            
            if len(package_row) == 2:
                keyboard_buttons.append(package_row)
                package_row = []
        
        if package_row:
            keyboard_buttons.append(package_row)
    else:
        # Default packages with psychological ordering (best value first)
        keyboard_buttons.append([
            InlineKeyboardButton(text="🥇 Gold $47 🔥 Best Value", callback_data="select_package_gold")
        ])
        keyboard_buttons.append([
            InlineKeyboardButton(text="🥈 Silver $29 💰 Popular", callback_data="select_package_silver"),
            InlineKeyboardButton(text="🟫 Bronze $10", callback_data="select_package_bronze")
        ])
    
    # Navigation
    keyboard_buttons.append([InlineKeyboardButton(text=get_text(language, 'back'), callback_data="back_to_start")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback_query.message.edit_text(
        pricing_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    await callback_query.answer()

# Channel selection handlers (I3lani flow)
@router.callback_query(F.data.startswith("select_channel_"))
async def handle_channel_selection(callback_query: CallbackQuery):
    """Handle psychological channel selection"""
    channel_type = callback_query.data.replace("select_channel_", "")
    
    # Channel details based on I3lani specs
    channel_info = {
        "tech": {
            "name": "Tech News Channel",
            "subscribers": "45,000",
            "engagement": "8.2%",
            "base_price": 25,
            "description": "🔥 Most Popular - Best performing channel"
        },
        "gaming": {
            "name": "Gaming Hub Channel", 
            "subscribers": "32,000",
            "engagement": "12.1%",
            "base_price": 20,
            "description": "Perfect for gaming & entertainment"
        },
        "business": {
            "name": "Business Tips Channel",
            "subscribers": "28,000", 
            "engagement": "6.8%",
            "base_price": 18,
            "description": "🪤 Decoy pricing - Great for B2B content"
        }
    }
    
    selected_channel = channel_info.get(channel_type)
    if not selected_channel:
        await callback_query.answer("❌ Invalid channel selection!")
        return
    
    # Show duration selection with psychological pricing
    duration_text = f"""
🎯 **Selected Channel:** {selected_channel['name']}
👥 **{selected_channel['subscribers']}** subscribers | 📊 **{selected_channel['engagement']}** engagement

⏰ **Choose Your Duration:**

💰 **1 Month Package**
• Base Price: {selected_channel['base_price']} TON
• 30 days advertising
• Daily posting
• Total: **{selected_channel['base_price']} TON**

💰 **3 Months Package** 💰 **Save 5 TON!**
• Base Price: {selected_channel['base_price'] * 3} TON
• Discount: -5 TON
• 90 days advertising
• Daily + bonus posts
• Total: **{selected_channel['base_price'] * 3 - 5} TON**

🔥 **6 Months Package** 🔥 **Best Value - Save 20 TON!**
• Base Price: {selected_channel['base_price'] * 6} TON
• Discount: -20 TON
• 180 days advertising
• Premium posting
• Total: **{selected_channel['base_price'] * 6 - 20} TON**

⚡ **Default Selection**: 6-month package (Maximum savings!)
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⏰ 1 Month - {selected_channel['base_price']} TON", callback_data=f"duration_1m_{channel_type}")],
        [InlineKeyboardButton(text=f"⏰ 3 Months - {selected_channel['base_price'] * 3 - 5} TON 💰 Save 5", callback_data=f"duration_3m_{channel_type}")],
        [InlineKeyboardButton(text=f"⏰ 6 Months - {selected_channel['base_price'] * 6 - 20} TON 🔥 BEST", callback_data=f"duration_6m_{channel_type}")],
        [InlineKeyboardButton(text="⬅️ Back to Channels", callback_data="pricing")]
    ])
    
    await callback_query.message.edit_text(duration_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

# Duration selection handlers (I3lani flow)
@router.callback_query(F.data.startswith("duration_"))
async def handle_duration_selection(callback_query: CallbackQuery):
    """Handle duration selection and proceed to payment"""
    duration_data = callback_query.data.replace("duration_", "")
    duration_months, channel_type = duration_data.split("_", 1)
    
    # Convert duration format
    duration_map = {"1m": 1, "3m": 3, "6m": 6}
    months = duration_map.get(duration_months, 1)
    
    # Calculate final price with psychological discounts
    base_prices = {"tech": 25, "gaming": 20, "business": 18}
    base_price = base_prices.get(channel_type, 20)
    
    if months == 1:
        final_price = base_price
        savings = 0
    elif months == 3:
        final_price = (base_price * 3) - 5
        savings = 5
    else:  # 6 months
        final_price = (base_price * 6) - 20
        savings = 20
    
    # Show payment confirmation with psychological elements
    payment_text = f"""
💎 **I3lani Payment Summary**

📋 **Your Selection:**
• Channel: {base_prices.get(channel_type, "Selected")} Channel
• Duration: {months} month{'s' if months > 1 else ''}
• Base Price: {base_price * months} TON
• Discount: -{savings} TON
• **Final Price: {final_price} TON**

🎁 **What You Get:**
✅ Guaranteed daily posting
✅ Professional analytics
✅ 24/7 customer support
✅ Money-back guarantee
✅ Blockchain-verified payments

⚡ **Ready to proceed?**
Your ads will go live within 24 hours!
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Pay with TON", callback_data=f"pay_ton_{final_price}_{months}_{channel_type}")],
        [InlineKeyboardButton(text="⭐ Pay with Telegram Stars", callback_data=f"pay_stars_{final_price}_{months}_{channel_type}")],
        [InlineKeyboardButton(text="✏️ Edit Selection", callback_data="pricing")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="back_to_start")]
    ])
    
    await callback_query.message.edit_text(payment_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

def setup_i3lani_pricing_handlers(dp):
    """Setup I3lani pricing system handlers"""
    dp.include_router(router)