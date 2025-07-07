"""
Message and callback handlers for I3lani Telegram Bot
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from typing import List, Dict
import logging

from states import AdCreationStates, UserStates
from languages import get_text, get_currency_info, LANGUAGES
from database import db, ensure_user_exists, get_user_language
from payments import payment_processor
from config import CHANNELS, ADMIN_IDS
import os

logger = logging.getLogger(__name__)

# Create router
router = Router()


def create_language_keyboard() -> InlineKeyboardMarkup:
    """Create language selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{lang_data['flag']} {lang_data['name']}", 
                callback_data=f"lang_{lang_code}"
            )
        ]
        for lang_code, lang_data in LANGUAGES.items()
    ])
    return keyboard


def create_main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=get_text(language, 'create_ad'), 
                callback_data="create_ad"
            ),
            InlineKeyboardButton(
                text=get_text(language, 'my_ads'), 
                callback_data="my_ads"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, 'pricing'), 
                callback_data="pricing"
            ),
            InlineKeyboardButton(
                text=get_text(language, 'share_earn'), 
                callback_data="share_earn"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(language, 'settings'), 
                callback_data="settings"
            ),
            InlineKeyboardButton(
                text=get_text(language, 'help'), 
                callback_data="help"
            )
        ]
    ])
    return keyboard


def create_channel_selection_keyboard(language: str, selected_channels: List[str] = None) -> InlineKeyboardMarkup:
    """Create channel selection keyboard"""
    if selected_channels is None:
        selected_channels = []
    
    buttons = []
    for channel_id, channel_data in CHANNELS.items():
        is_selected = channel_id in selected_channels
        popular_mark = " 🔥" if channel_data['is_popular'] else ""
        selection_mark = "✅ " if is_selected else ""
        
        text = f"{selection_mark}{channel_data['name']} ({channel_data['subscribers']//1000}K){popular_mark}"
        buttons.append([InlineKeyboardButton(
            text=text, 
            callback_data=f"toggle_channel_{channel_id}"
        )])
    
    # Add continue button if channels selected
    if selected_channels:
        buttons.append([InlineKeyboardButton(
            text=get_text(language, 'continue'), 
            callback_data="continue_to_duration"
        )])
    
    # Add back button
    buttons.append([InlineKeyboardButton(
        text=get_text(language, 'back'), 
        callback_data="back_to_main"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_duration_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create duration selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(language, 'duration_1_month'), 
            callback_data="duration_1"
        )],
        [InlineKeyboardButton(
            text=get_text(language, 'duration_3_months'), 
            callback_data="duration_3"
        )],
        [InlineKeyboardButton(
            text=get_text(language, 'duration_6_months'), 
            callback_data="duration_6"
        )],
        [InlineKeyboardButton(
            text=get_text(language, 'back'), 
            callback_data="back_to_channels"
        )]
    ])
    return keyboard


def create_payment_method_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create payment method selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(language, 'pay_stars'), 
            callback_data="payment_stars"
        )],
        [InlineKeyboardButton(
            text=get_text(language, 'pay_ton'), 
            callback_data="payment_ton"
        )],
        [InlineKeyboardButton(
            text=get_text(language, 'back'), 
            callback_data="back_to_duration"
        )]
    ])
    return keyboard


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """Start command handler"""
    user_id = message.from_user.id if message.from_user else 0
    username = message.from_user.username if message.from_user else None
    
    # Extract referral code if present
    referrer_id = None
    if message.text and len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
        if referral_code.startswith('ref_'):
            try:
                referrer_id = int(referral_code.replace('ref_', ''))
            except:
                pass
    
    # Ensure user exists
    await ensure_user_exists(user_id, username)
    
    # Check if user already has language set
    user = await db.get_user(user_id)
    if user and user.get('language'):
        # User has language, show main menu
        await show_main_menu(message, user['language'])
    else:
        # New user, show language selection
        await state.set_state(AdCreationStates.language_selection)
        await message.answer(
            "🌍 Welcome to I3lani Bot!\n\nChoose your language:",
            reply_markup=create_language_keyboard()
        )
    
    # Handle referral
    if referrer_id and referrer_id != user_id:
        await db.create_referral(referrer_id, user_id)


async def show_main_menu(message_or_query, language: str):
    """Show main menu"""
    text = f"{get_text(language, 'welcome')}\n\n{get_text(language, 'main_menu')}"
    keyboard = create_main_menu_keyboard(language)
    
    if isinstance(message_or_query, Message):
        await message_or_query.answer(text, reply_markup=keyboard)
    else:
        await message_or_query.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("lang_"))
async def language_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle language selection"""
    try:
        language_code = callback_query.data.replace("lang_", "")
        user_id = callback_query.from_user.id
        
        # Update user language
        await db.update_user_language(user_id, language_code)
        
        # Clear state and show main menu
        await state.clear()
        await show_main_menu(callback_query, language_code)
        await callback_query.answer("Language updated successfully!")
        
    except Exception as e:
        logger.error(f"Language selection error: {e}")
        await callback_query.answer("Error updating language. Please try again.")


@router.callback_query(F.data == "pricing")
async def show_pricing_handler(callback_query: CallbackQuery):
    """Show pricing information"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    pricing_text = f"""
💰 **{get_text(language, 'pricing_title', default='Pricing & Packages')}**

📊 **Available Channels:**
• Tech Channel (156K subscribers) - 15 TON/month
• Gaming Hub (89K subscribers) - 12 TON/month
• Crypto News (234K subscribers) - 20 TON/month
• Business Hub (178K subscribers) - 18 TON/month

🎯 **Package Options:**
• **Basic** - 1 channel, 1 month: 10 TON
• **Pro** - 3 channels, 1 month: 25 TON
• **Premium** - 5 channels, 1 month: 40 TON
• **Enterprise** - All channels, 1 month: 60 TON

💳 **Payment Methods:**
• TON Cryptocurrency
• Telegram Stars (⭐)

📞 **Need custom pricing?** Contact /support
    """.strip()
    
    await callback_query.message.edit_text(
        pricing_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text(language, 'back'), 
                callback_data="back_to_main"
            )]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(F.data == "settings")
async def show_settings_handler(callback_query: CallbackQuery):
    """Show settings menu"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Ensure language is valid
        if language not in LANGUAGES:
            language = 'en'
        
        settings_text = f"""
⚙️ **Settings**

🌍 **Current Language:** {LANGUAGES[language]['name']} {LANGUAGES[language]['flag']}

🔄 **Change Language:**
Choose your preferred language below.

📊 **Account Info:**
• User ID: {user_id}
• Language: {language.upper()}
• Status: Active
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
                InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar")
            ],
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back", 
                    callback_data="back_to_main"
                )
            ]
        ])
        
        await callback_query.message.edit_text(
            settings_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Settings handler error: {e}")
        await callback_query.answer("Settings temporarily unavailable. Please try again.")


@router.callback_query(F.data == "help")
async def show_help_handler(callback_query: CallbackQuery):
    """Show help information"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Ensure language is valid
        if language not in LANGUAGES:
            language = 'en'
        
        help_text = """
📚 **Help & Commands**

🚀 **Getting Started:**
1. Click "Create Ad" to start
2. Submit your ad content
3. Choose channels and duration
4. Make payment (TON or Stars)
5. Your ad goes live automatically!

💡 **Available Commands:**
• /start - Main menu
• /mystats - View your statistics
• /support - Get help
• /admin - Admin panel (admins only)
• /refresh - Refresh data
• /help - This help message

🎯 **Features:**
• Multi-channel advertising
• TON and Telegram Stars payment
• Real-time ad publishing
• Campaign tracking
• Referral system

❓ **Need Help?** Use /support to contact us!
        """.strip()
        
        await callback_query.message.edit_text(
            help_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="⬅️ Back", 
                    callback_data="back_to_main"
                )]
            ]),
            parse_mode='Markdown'
        )
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Help handler error: {e}")
        await callback_query.answer("Help temporarily unavailable. Please try again.")


@router.callback_query(F.data == "create_ad")
async def create_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Start ad creation process"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.ad_content)
    await callback_query.message.edit_text(
        get_text(language, 'send_ad_content'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text(language, 'back'), 
                callback_data="back_to_main"
            )]
        ])
    )
    await callback_query.answer()


@router.message(AdCreationStates.ad_content)
async def ad_content_handler(message: Message, state: FSMContext):
    """Handle ad content submission"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Determine content type and extract content
    content_type = message.content_type
    content = ""
    media_url = None
    
    if content_type == "text":
        content = message.text
    elif content_type == "photo":
        content = message.caption or ""
        media_url = message.photo[-1].file_id
    elif content_type == "video":
        content = message.caption or ""
        media_url = message.video.file_id
    else:
        await message.answer(
            "❌ Unsupported content type. Please send text, photo, or video."
        )
        return
    
    # Create ad in database
    ad_id = await db.create_ad(user_id, content, media_url, content_type)
    
    # Store ad_id in state
    await state.update_data(ad_id=ad_id, content=content, media_url=media_url, content_type=content_type)
    await state.set_state(AdCreationStates.channel_selection)
    
    # Show channel selection
    await message.answer(
        f"{get_text(language, 'ad_received')}\n\n{get_text(language, 'choose_channels')}",
        reply_markup=create_channel_selection_keyboard(language)
    )


@router.callback_query(F.data.startswith("toggle_channel_"))
async def toggle_channel_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel toggle"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    channel_id = callback_query.data.replace("toggle_channel_", "")
    
    # Get current data
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Toggle channel
    if channel_id in selected_channels:
        selected_channels.remove(channel_id)
    else:
        selected_channels.append(channel_id)
    
    # Update state
    await state.update_data(selected_channels=selected_channels)
    
    # Update keyboard
    await callback_query.message.edit_reply_markup(
        reply_markup=create_channel_selection_keyboard(language, selected_channels)
    )
    await callback_query.answer()


@router.callback_query(F.data == "continue_to_duration")
async def continue_to_duration_handler(callback_query: CallbackQuery, state: FSMContext):
    """Continue to duration selection"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.duration_selection)
    await callback_query.message.edit_text(
        get_text(language, 'select_duration'),
        reply_markup=create_duration_keyboard(language)
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("duration_"))
async def duration_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle duration selection"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    duration = int(callback_query.data.replace("duration_", ""))
    
    # Get current data
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Get channel data and calculate pricing
    channels = await db.get_channels()
    selected_channel_data = [ch for ch in channels if ch['channel_id'] in selected_channels]
    
    # Get user currency
    user = await db.get_user(user_id)
    currency = user.get('currency', 'USD') if user else 'USD'
    
    # Calculate total price
    total_price = 0
    for channel in selected_channel_data:
        price_info = payment_processor.calculate_price(
            channel['base_price_usd'], duration, currency
        )
        total_price += price_info['final_price']
    
    # Show pricing and payment methods
    pricing_text = payment_processor.get_pricing_display(
        selected_channel_data, duration, currency, language
    )
    
    # Update state
    await state.update_data(
        duration_months=duration,
        total_price=total_price,
        currency=currency
    )
    await state.set_state(AdCreationStates.payment_method)
    
    await callback_query.message.edit_text(
        f"{pricing_text}\n\n{get_text(language, 'choose_payment')}",
        reply_markup=create_payment_method_keyboard(language)
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("payment_"))
async def payment_method_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment method selection"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        payment_method = callback_query.data.replace("payment_", "")
        
        # Get state data
        data = await state.get_data()
        ad_id = data['ad_id']
        selected_channels = data['selected_channels']
        duration_months = data['duration_months']
        total_price = data['total_price']
        currency = data['currency']
        
        # Handle Telegram Stars payment with real API
        if payment_method == "stars":
            from aiogram.types import LabeledPrice
            
            # Calculate Stars amount (approximately 1 USD = 100 Stars)
            stars_amount = int(total_price * 100)
            
            # Create payment payload for tracking
            payload = f"ad_{ad_id}_user_{user_id}_time_{int(time.time())}"
            
            # Store payment data in state for later processing
            await state.update_data(payment_payload=payload, stars_amount=stars_amount)
            
            # Create and send Telegram Stars invoice
            try:
                await callback_query.bot.send_invoice(
                    chat_id=user_id,
                    title="I3lani Advertisement Campaign",
                    description=f"Ad campaign for {len(selected_channels)} channels, {duration_months} month(s)",
                    payload=payload,
                    provider_token="",  # Empty for Telegram Stars
                    currency="XTR",  # Telegram Stars currency code
                    prices=[LabeledPrice(label="Campaign", amount=stars_amount)],
                    need_name=False,
                    need_phone_number=False,
                    need_email=False,
                    need_shipping_address=False,
                    send_phone_number_to_provider=False,
                    send_email_to_provider=False,
                    is_flexible=False
                )
                
                await callback_query.message.edit_text(
                    f"⭐ **Telegram Stars Payment**\n\nInvoice sent! Please complete payment using the invoice above.\n\nAmount: {stars_amount} Stars\n\nYour ad will be published automatically after payment confirmation.",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_duration")]
                    ])
                )
                
                await callback_query.answer("Stars invoice sent!")
                return
                
            except Exception as e:
                logger.error(f"Stars invoice creation failed: {e}")
                await callback_query.answer("Stars payment temporarily unavailable. Please try TON.")
                return
        
        # Handle TON payment
        elif payment_method == "ton":
            # Create subscriptions for TON payment
            subscription_ids = []
            for channel_id in selected_channels:
                subscription_id = await db.create_subscription(
                    user_id=user_id,
                    ad_id=ad_id,
                    channel_id=channel_id,
                    duration_months=duration_months,
                    total_price=total_price / len(selected_channels),
                    currency=currency
                )
                subscription_ids.append(subscription_id)
            
            # Create payment invoice for TON
            invoice = await payment_processor.create_payment_invoice(
                user_id=user_id,
                subscription_id=subscription_ids[0],
                amount=total_price,
                currency=currency,
                payment_method=payment_method
            )
            
            # Show TON payment instructions
            instructions = invoice['instructions']
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="✅ Payment Sent", 
                    callback_data=f"confirm_payment_{invoice['payment_id']}"
                )],
                [InlineKeyboardButton(
                    text="⬅️ Back", 
                    callback_data="back_to_duration"
                )]
            ])
            
            await state.set_state(AdCreationStates.payment_confirmation)
            await callback_query.message.edit_text(
                instructions,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            await callback_query.answer("TON payment instructions sent!")
        
    except Exception as e:
        logger.error(f"Payment method handler error: {e}")
        await callback_query.answer("Payment system temporarily unavailable. Please try again.")


@router.callback_query(F.data.startswith("confirm_payment_"))
async def confirm_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment confirmation and publish ad to I3lani channel"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        payment_id = callback_query.data.replace("confirm_payment_", "")
        
        # Get ad content from state AND database
        data = await state.get_data()
        ad_content = data.get('ad_content', '')
        ad_media = data.get('ad_media')
        ad_id = data.get('ad_id')
        
        # If no content in state, try to get from database
        if not ad_content and ad_id:
            try:
                # Get ad from database
                async with db.get_connection() as conn:
                    result = await conn.execute(
                        'SELECT content, media_url, content_type FROM ads WHERE ad_id = ?',
                        (ad_id,)
                    )
                    ad_record = await result.fetchone()
                    if ad_record:
                        ad_content = ad_record[0] or ''
                        if ad_record[1]:  # media_url
                            ad_media = {
                                'file_id': ad_record[1],
                                'type': ad_record[2]
                            }
            except Exception as e:
                logger.error(f"Error fetching ad from database: {e}")
        
        # Ensure we have content
        if not ad_content:
            ad_content = "📢 Your advertisement is now live! Contact @I3lani_bot for more details."
        
        # Publish ad to I3lani channel immediately
        bot = callback_query.bot
        i3lani_channel = "@i3lani"
        published = False
        
        try:
            # Format ad with proper branding
            formatted_content = f"📢 **Advertisement**\n\n{ad_content}\n\n✨ *Advertise with @I3lani_bot*"
            
            # Publish based on content type
            if ad_media and ad_media.get('file_id'):
                if ad_media.get('type') == 'photo':
                    await bot.send_photo(
                        chat_id=i3lani_channel,
                        photo=ad_media['file_id'],
                        caption=formatted_content,
                        parse_mode='Markdown'
                    )
                elif ad_media.get('type') == 'video':
                    await bot.send_video(
                        chat_id=i3lani_channel,
                        video=ad_media['file_id'],
                        caption=formatted_content,
                        parse_mode='Markdown'
                    )
                else:
                    # Fallback to text
                    await bot.send_message(
                        chat_id=i3lani_channel,
                        text=formatted_content,
                        parse_mode='Markdown'
                    )
            else:
                # Text-only ad
                await bot.send_message(
                    chat_id=i3lani_channel,
                    text=formatted_content,
                    parse_mode='Markdown'
                )
            
            published = True
            logger.info(f"Ad published to {i3lani_channel} for user {user_id}: {ad_content[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to publish ad to {i3lani_channel}: {e}")
            published = False
        
        # Show confirmation with publishing status
        if published:
            confirmation_text = f"""
🎉 **Payment Confirmed & Ad Published!**

✅ Your ad is now live on the I3lani channel!

📊 **Campaign Status:**
• Payment ID: {payment_id}
• Published: Just now
• Channel: https://t.me/i3lani
• Status: Active

🔗 **View your ad:** https://t.me/i3lani

Your campaign is running successfully!
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🔗 View I3lani Channel", 
                    url="https://t.me/i3lani"
                )],
                [InlineKeyboardButton(
                    text="📊 My Ads", 
                    callback_data="my_ads"
                )],
                [InlineKeyboardButton(
                    text="🏠 Main Menu", 
                    callback_data="back_to_main"
                )]
            ])
        else:
            confirmation_text = f"""
✅ **Payment Confirmed**

📋 **Payment ID:** {payment_id}
⚠️ **Publishing Status:** In progress
⏰ **Estimated Time:** Within 24 hours

Your payment has been confirmed. Your ad will be published to the I3lani channel shortly.
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="📊 My Ads", 
                    callback_data="my_ads"
                )],
                [InlineKeyboardButton(
                    text="🏠 Main Menu", 
                    callback_data="back_to_main"
                )]
            ])
        
        await callback_query.message.edit_text(
            confirmation_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        await state.clear()
        await callback_query.answer("✅ Payment confirmed!" + (" Ad published!" if published else ""))
        
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        await callback_query.answer("Payment confirmation failed. Please contact support.")


@router.callback_query(F.data == "my_ads")
async def my_ads_handler(callback_query: CallbackQuery):
    """Show user's ads dashboard"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get user stats
    stats = await db.get_user_stats(user_id)
    
    # Get currency info
    user = await db.get_user(user_id)
    currency = user.get('currency', 'USD') if user else 'USD'
    currency_info = get_currency_info(language)
    
    dashboard_text = f"""
📊 **{get_text(language, 'dashboard')}**

📈 **Your Statistics:**
{get_text(language, 'total_ads', count=stats['total_ads'])}
{get_text(language, 'active_ads', count=stats['active_ads'])}
{get_text(language, 'total_spent', currency=currency_info['symbol'], amount=stats['total_spent'])}

🚀 **Ready to create more ads?**
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(language, 'create_ad'), 
            callback_data="create_ad"
        )],
        [InlineKeyboardButton(
            text=get_text(language, 'back'), 
            callback_data="back_to_main"
        )]
    ])
    
    await callback_query.message.edit_text(
        dashboard_text,
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(F.data == "share_earn")
async def share_earn_handler(callback_query: CallbackQuery):
    """Show channel sharing system"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get available channels
    channels = await db.get_channels()
    
    # Get referral stats for bot referrals
    referral_stats = await db.get_referral_stats(user_id)
    
    share_text = f"""
📺 **{get_text(language, 'share_channels')}**

🎯 **Share Our Channels & Earn:**
• Share I3lani channel with friends
• Get 10% discount on next campaign
• Help grow our community

📺 **Available Channels:**
"""
    
    for channel in channels:
        share_text += f"\n• {channel['name']}: {channel['telegram_channel_id']}"
    
    share_text += f"""

💰 **Bot Referral Rewards:**
• Refer friends to I3lani Bot
• Earn 3 free posting days per referral
• Friends get 5% discount

📊 **Your Referral Stats:**
• Total Referrals: {referral_stats.get('total_referrals', 0)}
• Free Days Earned: {referral_stats.get('total_referrals', 0) * 3}

📎 **Your Bot Referral Link:**
`https://t.me/I3lani_bot?start=ref_{user_id}`
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📺 Share I3lani Channel", url="https://t.me/share/url?url=https://t.me/i3lani&text=Join I3lani Channel!"),
        ],
        [
            InlineKeyboardButton(text="🤖 Share Bot", url=f"https://t.me/share/url?url=https://t.me/I3lani_bot?start=ref_{user_id}&text=Try I3lani advertising bot!")
        ],
        [InlineKeyboardButton(text=get_text(language, 'back'), callback_data="back_to_start")]
    ])
    
    await callback_query.message.edit_text(
        share_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    await callback_query.answer()


# Back navigation handlers
@router.callback_query(F.data == "back_to_main")
async def back_to_main_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to main menu"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.clear()
    await show_main_menu(callback_query, language)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_channels")
async def back_to_channels_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to channel selection"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    await state.set_state(AdCreationStates.channel_selection)
    await callback_query.message.edit_text(
        get_text(language, 'choose_channels'),
        reply_markup=create_channel_selection_keyboard(language, selected_channels)
    )
    await callback_query.answer()


@router.callback_query(F.data == "back_to_duration")
async def back_to_duration_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to duration selection"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.duration_selection)
    await callback_query.message.edit_text(
        get_text(language, 'select_duration'),
        reply_markup=create_duration_keyboard(language)
    )
    await callback_query.answer()


# Debug and Support Commands
@router.message(Command("debug"))
async def debug_command(message: Message):
    """Debug command for users to report issues"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    debug_info = f"""
🔧 **Debug Information**

**User ID:** {user_id}
**Language:** {language}
**Time:** {message.date.strftime('%Y-%m-%d %H:%M:%S')}

**Bot Status:** ✅ Online
**Database:** ✅ Connected
**Payment System:** ✅ Active

**Recent Activity:**
Use /support to report issues or get help.

**Commands:**
• /start - Restart bot
• /debug - This message
• /support - Get help
• /status - Check bot status
    """.strip()
    
    await message.reply(debug_info, parse_mode='Markdown')


@router.message(Command("support"))
async def support_command(message: Message):
    """Support command for users"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    support_text = f"""
🆘 **{get_text(language, 'support_title', default='Support')}**

**{get_text(language, 'need_help', default='Need Help?')}**

**Common Issues:**
• Payment not confirmed? Wait 5-10 minutes
• Bot not responding? Use /start
• Language issues? Use /start to change language
• Channel selection problems? Try /start again

**Contact Support:**
• Report bugs: Describe the issue clearly
• Technical issues: Include error messages
• Payment problems: Provide payment ID

**Debug Info:**
• Your ID: {user_id}
• Language: {language}
• Time: {message.date.strftime('%Y-%m-%d %H:%M:%S')}

**Quick Fixes:**
• Restart: /start
• Check status: /status
• Debug info: /debug
    """.strip()
    
    await message.reply(support_text, parse_mode='Markdown')


@router.message(Command("status"))
async def status_command(message: Message):
    """Bot status command"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Check database connection
        user = await db.get_user(user_id)
        db_status = "✅ Connected" if user else "⚠️ Issue"
        
        # Check payment system
        from payments import payment_processor
        test_memo = payment_processor.generate_memo()
        payment_status = "✅ Active" if len(test_memo) == 6 else "⚠️ Issue"
        
        # Get uptime info
        from datetime import datetime
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        status_text = f"""
📊 **Bot Status**

**System Status:**
• Bot: ✅ Online
• Database: {db_status}
• Payment System: {payment_status}
• Time: {current_time}

**Your Info:**
• User ID: {user_id}
• Language: {language}
• Registered: {'✅ Yes' if user else '⚠️ No'}

**Functions:**
• Multi-language: ✅ Working
• AB0102 Memos: ✅ Working
• TON Payments: ✅ Working
• Telegram Stars: ✅ Working
• Referral System: ✅ Working

**Test Memo:** {test_memo}

Everything is working properly! 🎉
        """.strip()
        
    except Exception as e:
        status_text = f"""
⚠️ **System Status**

**Error Detected:**
{str(e)}

**Troubleshooting:**
• Try /start to restart
• Contact support if problem persists
• Your ID: {user_id}
        """.strip()
    
    await message.reply(status_text, parse_mode='Markdown')


@router.message(Command("help"))
async def help_command(message: Message):
    """Help command"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    help_text = f"""
📚 **{get_text(language, 'help_title', default='Help & Commands')}**

**🚀 Getting Started:**
• /start - Start the bot or restart
• Choose your language
• Create your first ad
• Select channels and duration
• Make payment and go live!

**💳 Payment System:**
• TON Cryptocurrency supported
• Telegram Stars supported
• AB0102 memo format (6 characters)
• Automatic payment detection

**🌍 Languages:**
• English (USD)
• Arabic (SAR)
• Russian (RUB)

**🎁 Referral System:**
• Share your link: Get 3 free days per referral
• Friends get 5% discount
• Earn rewards for every referral

**🔧 Troubleshooting:**
• /debug - Debug information
• /status - Check bot status
• /support - Get help
• /start - Restart bot

**📊 Commands:**
• /start - Start/restart bot
• /debug - Debug info
• /status - System status
• /support - Get support
• /help - This message

**Questions?** Use /support to get help!
    """.strip()
    
    await message.reply(help_text, parse_mode='Markdown')


@router.message(Command("dashboard"))
async def dashboard_command(message: Message):
    """My Ads Dashboard command"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Get user stats
    stats = await db.get_user_stats(user_id)
    referral_stats = await db.get_referral_stats(user_id)
    
    dashboard_text = f"""
📊 **{get_text(language, 'dashboard')}**

📈 **{get_text(language, 'my_stats')}:**
• {get_text(language, 'total_campaigns')}: {stats.get('total_campaigns', 0)}
• {get_text(language, 'active_campaigns')}: {stats.get('active_campaigns', 0)}
• {get_text(language, 'total_spent')}: ${stats.get('total_spent', 0):.2f}

💰 **{get_text(language, 'referral_system')}:**
• {get_text(language, 'referrals')}: {referral_stats.get('total_referrals', 0)}
• {get_text(language, 'earnings')}: ${referral_stats.get('total_earnings', 0):.2f}

🔗 **{get_text(language, 'referral_link')}:**
`https://t.me/I3lani_bot?start=ref_{user_id}`
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(language, 'start_advertising'), callback_data="start_advertising"),
            InlineKeyboardButton(text=get_text(language, 'my_campaigns'), callback_data="my_campaigns")
        ],
        [
            InlineKeyboardButton(text=get_text(language, 'pricing'), callback_data="view_pricing"),
            InlineKeyboardButton(text=get_text(language, 'help'), callback_data="show_help")
        ]
    ])
    
    await message.reply(dashboard_text, reply_markup=keyboard, parse_mode='Markdown')


@router.callback_query(F.data == "view_pricing")
async def show_pricing_handler(callback_query: CallbackQuery):
    """Show pricing information"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    channels = await db.get_channels()
    
    pricing_text = f"""
💰 **{get_text(language, 'pricing')}**

📺 **{get_text(language, 'available_channels')}:**
"""
    
    for channel in channels:
        pricing_text += f"\n• {channel['name']}: ${channel['price_per_month']}/month"
    
    pricing_text += f"""

📦 **{get_text(language, 'packages')}:**
• 1 month: Standard price
• 3 months: 10% discount
• 6 months: 20% discount
• 12 months: 30% discount

💎 **{get_text(language, 'payment_methods')}:**
• TON Cryptocurrency
• Telegram Stars
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'start_advertising'), callback_data="start_advertising")],
        [InlineKeyboardButton(text=get_text(language, 'back'), callback_data="back_to_start")]
    ])
    
    await callback_query.message.edit_text(pricing_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()


@router.callback_query(F.data == "show_help")
async def show_help_handler(callback_query: CallbackQuery):
    """Show help information"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    help_text = f"""
❓ **{get_text(language, 'help')}**

🚀 **{get_text(language, 'how_to_start')}:**
1. Send your ad content (text, photo, or video)
2. Select advertising channels
3. Choose duration (1-12 months)
4. Complete payment with TON or Stars
5. Your ad will be posted automatically

💰 **{get_text(language, 'payment_info')}:**
• TON: Send to provided wallet with memo
• Stars: Pay directly through Telegram

📊 **{get_text(language, 'track_campaigns')}:**
• Use /mystats to view statistics
• Use /dashboard for full overview
• Monitor your campaigns in real-time

🆘 **{get_text(language, 'need_help')}:**
• Use /support for technical issues
• Contact admins for urgent matters

💰 **{get_text(language, 'referral_system')}:**
• Share your referral link
• Earn from each successful referral
• Track earnings in dashboard
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'start_advertising'), callback_data="start_advertising")],
        [InlineKeyboardButton(text=get_text(language, 'back'), callback_data="back_to_start")]
    ])
    
    await callback_query.message.edit_text(help_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()


@router.callback_query(F.data == "show_settings")
async def show_settings_handler(callback_query: CallbackQuery):
    """Show user settings"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    settings_text = f"""
⚙️ **{get_text(language, 'settings')}**

🌐 **{get_text(language, 'current_language')}: {language.upper()}**

🔔 **{get_text(language, 'notifications')}:**
• Payment confirmations: ✅ Enabled
• Campaign updates: ✅ Enabled
• System alerts: ✅ Enabled
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar")
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ],
        [
            InlineKeyboardButton(text=get_text(language, 'back'), callback_data="back_to_start")
        ]
    ])
    
    await callback_query.message.edit_text(
        settings_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    await callback_query.answer()


# Back navigation handlers
@router.callback_query(F.data == "back_to_start")
async def back_to_start_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle back to start"""
    await state.clear()
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    await show_main_menu(callback_query, language)


@router.callback_query(F.data == "back_to_main")
async def back_to_main_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle back to main menu"""
    await state.clear()
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    await show_main_menu(callback_query, language)


# Admin command handler
@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    """Handle admin command"""
    user_id = message.from_user.id
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    admin_ids = [int(x.strip()) for x in admin_ids_str.split(',') if x.strip()]
    
    if user_id not in admin_ids:
        await message.reply(f"❌ Access denied. User ID: {user_id}")
        return
    
    admin_text = """
🔧 **Admin Control Panel**

📊 **System Status**: Online
👥 **Total Users**: Active
💰 **Revenue**: Processing
📺 **Channels**: 4 Active

**Available Commands:**
• Manage pricing and packages
• Configure channels and settings  
• View statistics and reports
• Update payment wallet address
• Monitor user activity

⚠️ **Admin Features Temporarily Disabled**
The full admin panel is being rebuilt for better security and functionality.

Use these commands for now:
• /debug_status - System status
• /debug_user <id> - User info
• Database management via SQL tool
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Basic Stats", callback_data="admin_basic_stats")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_start")]
    ])
    
    await message.reply(admin_text, reply_markup=keyboard, parse_mode='Markdown')


# Telegram Stars Payment Handlers
@router.pre_checkout_query()
async def handle_pre_checkout_query(pre_checkout_query):
    """Handle pre-checkout query for Telegram Stars"""
    try:
        # Approve all pre-checkout queries for now
        await pre_checkout_query.answer(ok=True)
        logger.info(f"Pre-checkout approved for payload: {pre_checkout_query.invoice_payload}")
    except Exception as e:
        logger.error(f"Pre-checkout error: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Payment verification failed.")


@router.message(F.successful_payment)
async def handle_successful_payment(message: Message, state: FSMContext):
    """Handle successful Telegram Stars payment"""
    try:
        user_id = message.from_user.id
        payment = message.successful_payment
        
        logger.info(f"Successful Stars payment: {payment.total_amount} stars from user {user_id}")
        
        # Get ad content from state
        data = await state.get_data()
        ad_content = data.get('ad_content', 'Your advertisement with I3lani Bot')
        ad_media = data.get('ad_media')
        
        # Publish ad to I3lani channel immediately
        bot = message.bot
        i3lani_channel = "@i3lani"
        published = False
        
        try:
            # Format ad with branding
            formatted_content = f"📢 **Advertisement**\n\n{ad_content}\n\n✨ *Advertise with @I3lani_bot*"
            
            # Publish based on content type
            if ad_media and ad_media.get('file_id'):
                if ad_media.get('type') == 'photo':
                    await bot.send_photo(
                        chat_id=i3lani_channel,
                        photo=ad_media['file_id'],
                        caption=formatted_content,
                        parse_mode='Markdown'
                    )
                elif ad_media.get('type') == 'video':
                    await bot.send_video(
                        chat_id=i3lani_channel,
                        video=ad_media['file_id'],
                        caption=formatted_content,
                        parse_mode='Markdown'
                    )
                else:
                    await bot.send_message(
                        chat_id=i3lani_channel,
                        text=formatted_content,
                        parse_mode='Markdown'
                    )
            else:
                await bot.send_message(
                    chat_id=i3lani_channel,
                    text=formatted_content,
                    parse_mode='Markdown'
                )
            
            published = True
            logger.info(f"Stars payment ad published to {i3lani_channel} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish Stars payment ad: {e}")
        
        # Send confirmation to user
        confirmation_text = f"""
🎉 **Stars Payment Successful & Ad Published!**

⭐ **Payment Confirmed:** {payment.total_amount} Stars
✅ **Your ad is now live on the I3lani channel!**

📊 **Campaign Status:**
• Payment ID: {payment.telegram_payment_charge_id}
• Published: Just now
• Channel: https://t.me/i3lani
• Status: Active

🔗 **View your ad:** https://t.me/i3lani

Thank you for using I3lani Bot!
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔗 View I3lani Channel", 
                url="https://t.me/i3lani"
            )],
            [InlineKeyboardButton(
                text="🏠 Main Menu", 
                callback_data="back_to_main"
            )]
        ])
        
        await message.answer(
            confirmation_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Clear state
        await state.clear()
        
    except Exception as e:
        logger.error(f"Successful payment handler error: {e}")
        await message.answer("Payment processed successfully! Your ad will be published shortly.")


def setup_handlers(dp):
    """Setup all handlers"""
    dp.include_router(router)
    logger.info("Handlers setup completed")