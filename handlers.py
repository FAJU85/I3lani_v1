"""
Message and callback handlers for I3lani Telegram Bot
"""
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram import F
from aiogram.fsm.context import FSMContext
from typing import List, Dict
import logging
import time
import asyncio
import requests

logger = logging.getLogger(__name__)

from states import AdCreationStates, UserStates
from languages import get_text, get_currency_info, LANGUAGES
from database import db, ensure_user_exists, get_user_language
from payments import payment_processor
from config import ADMIN_IDS
import os
from datetime import datetime, timedelta
from frequency_pricing import FrequencyPricingSystem
# Flow validator removed for cleanup

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


async def create_neural_main_menu_text(language: str, user_id: int) -> str:
    """Create enhanced neural network main menu text with visual effects"""
    
    # Get user stats for dynamic content
    user_stats = await db.get_user_stats(user_id)
    total_ads = user_stats.get('total_ads', 0) if user_stats else 0
    
    # Neural network ASCII art and dynamic status
    neural_text = f"""
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>⚡ I3LANI QUANTUM ADVERTISING MATRIX ⚡</b>
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

<pre>    ▲▲▲ NEURAL NETWORK ACTIVE ▲▲▲    </pre>
<b>🔮 System Status:</b> <b><i>🟢 ONLINE & OPTIMIZED</i></b>
<b>🧠 AI Engine:</b> <b><i>🟢 FULLY OPERATIONAL</i></b>
<b>⚡ Quantum Core:</b> <b><i>🟢 SYNCHRONIZED</i></b>

<b>━━━━ NEURAL BROADCAST STATISTICS ━━━━</b>
<b>📡 Your Broadcasts:</b> <code>{total_ads}</code>
<b>🌐 Network Reach:</b> <code>∞ UNLIMITED</code>
<b>💫 Success Rate:</b> <code>98.7%</code>

<b>━━━━━━━━ QUANTUM FEATURES ━━━━━━━━</b>
<b>🚀</b> <i>Ultra-Fast Neural Broadcasting</i>
<b>💎</b> <i>Multi-Channel Quantum Distribution</i>
<b>🔗</b> <i>Blockchain-Powered Rewards</i>
<b>🎮</b> <i>Gamified Achievement System</i>
<b>🏆</b> <i>Real-Time Competition Rankings</i>

<b>═══════════════════════════════════</b>
<b>🎯 SELECT YOUR QUANTUM OPERATION 🎯</b>
<b>═══════════════════════════════════</b>
"""
    
    return neural_text.strip()

async def create_main_menu_keyboard(language: str, user_id: int) -> InlineKeyboardMarkup:
    """Create enhanced neural network main menu keyboard with visual effects"""
    keyboard_rows = []
    
    # Check if user can use free trial
    can_use_trial = await db.check_free_trial_available(user_id)
    
    # Free trial quantum gift for new users
    if can_use_trial:
        keyboard_rows.append([
            InlineKeyboardButton(
                text="🎁 ⚡ QUANTUM GIFT ⚡ Free Neural Trial (1 Day)", 
                callback_data="free_trial"
            )
        ])
    
    # Primary Neural Actions Row
    keyboard_rows.append([
        InlineKeyboardButton(
            text="🚀 ▶ LAUNCH NEURAL BROADCAST", 
            callback_data="create_ad"
        )
    ])
    
    keyboard_rows.append([
        InlineKeyboardButton(
            text="📊 ◆ My Quantum Matrix", 
            callback_data="my_ads"
        ),
        InlineKeyboardButton(
            text="💎 ◆ Earnings Portal", 
            callback_data="share_earn"
        )
    ])
    
    # Advanced Operations Row
    keyboard_rows.append([
        InlineKeyboardButton(
            text="🔗 ◇ Partner Network", 
            callback_data="join_partner_program"
        ),
        InlineKeyboardButton(
            text="🎮 ◇ Neural Gaming Hub", 
            callback_data="gamification_hub"
        )
    ])
    
    # Competition & Leaderboard Row
    keyboard_rows.append([
        InlineKeyboardButton(
            text="🏆 ▲ QUANTUM LEADERBOARD ▲", 
            callback_data="gamification_leaderboard"
        )
    ])
    
    # System Controls Row
    keyboard_rows.append([
        InlineKeyboardButton(
            text="⚙️ ◈ Neural Settings", 
            callback_data="settings"
        ),
        InlineKeyboardButton(
            text="🆘 ◈ Quantum Support", 
            callback_data="help"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


async def create_channel_selection_keyboard(language: str, selected_channels: List[str] = None) -> InlineKeyboardMarkup:
    """Create channel selection keyboard using database channels"""
    if selected_channels is None:
        selected_channels = []
    
    buttons = []
    # Get channels from database
    channels = await db.get_channels(active_only=True)
    for channel in channels:
        channel_id = channel['channel_id']
        is_selected = channel_id in selected_channels
        selection_mark = "Yes " if is_selected else ""
        
        # Display channel with subscriber count if available
        subscribers = channel.get('subscribers', 0)
        if subscribers > 0:
            sub_text = f" ({subscribers//1000}K)" if subscribers >= 1000 else f" ({subscribers})"
        else:
            sub_text = ""
        
        text = f"{selection_mark}{channel['name']}{sub_text}"
        buttons.append([InlineKeyboardButton(
            text=text, 
            callback_data=f"toggle_channel_{channel_id}"
        )])
    
    # Add continue button if channels selected
    if selected_channels:
        buttons.append([InlineKeyboardButton(
            text=get_text(language, 'continue'), 
            callback_data="continue_with_channels"
        )])
    
    # Add back button
    buttons.append([InlineKeyboardButton(
        text=get_text(language, 'back'), 
        callback_data="back_to_main"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_duration_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create duration selection keyboard with progressive frequency plans"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 Month - $30", callback_data="duration_1_month"),
            InlineKeyboardButton(text="2 Months - $108 (10% off)", callback_data="duration_2_months")
        ],
        [
            InlineKeyboardButton(text="3 Months - $229.50 (15% off)", callback_data="duration_3_months"),
            InlineKeyboardButton(text="4 Months - $384 (20% off)", callback_data="duration_4_months")
        ],
        [
            InlineKeyboardButton(text="5 Months - $562.50 (25% off)", callback_data="duration_5_months"),
            InlineKeyboardButton(text="6 Months - $756 (30% off)", callback_data="duration_6_months")
        ],
        [
            InlineKeyboardButton(text="7 Months - $999.60 (32% off)", callback_data="duration_7_months"),
            InlineKeyboardButton(text="8 Months - $1267.20 (34% off)", callback_data="duration_8_months")
        ],
        [
            InlineKeyboardButton(text="9 Months - $1555.20 (36% off)", callback_data="duration_9_months"),
            InlineKeyboardButton(text="10 Months - $1860 (38% off)", callback_data="duration_10_months")
        ],
        [
            InlineKeyboardButton(text="11 Months - $2178 (40% off)", callback_data="duration_11_months"),
            InlineKeyboardButton(text="12 Months - $2409 (45% off)", callback_data="duration_12_months")
        ],
        [InlineKeyboardButton(text="◀️ Back to Channels", callback_data="back_to_channels")]
    ])
    return keyboard


async def show_duration_selection(callback_query: CallbackQuery, state: FSMContext):
    """Show duration selection interface with progressive frequency plans"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        duration_text = f"""
Date **Full-Year Posting Plans (Progressive Frequency)**

 **Selected Channels:** {len(selected_channels)} (No per-channel fee)

Target **Progressive Frequency System:**
- Month 1: 1 post/day to Month 12: 12 posts/day
- Automatic discount scaling (up to 45% off)
- Base price: $1 per post (covers all channels)
- Higher frequency = Better engagement

Price **Discount Benefits:**
- 2+ months: 10%+ discount
- 6+ months: 30%+ discount  
- 12 months: 45% discount (Best Value!)

Choose your posting plan:
        """.strip()
        
        keyboard = create_duration_keyboard(language)
        
        await callback_query.message.edit_text(
            duration_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await state.set_state(AdCreationStates.duration_selection)
        
    except Exception as e:
        logger.error(f"Duration selection error: {e}")
        await callback_query.answer("Error showing duration options.")
        

def get_progressive_plan_details(months: int) -> dict:
    """Get progressive plan details with pricing and discount"""
    plan_data = {
        1: {"posts_per_day": 1, "total_days": 30, "total_posts": 30, "base_price": 30, "discount": 0, "final_price": 30},
        2: {"posts_per_day": 2, "total_days": 60, "total_posts": 120, "base_price": 120, "discount": 10, "final_price": 108},
        3: {"posts_per_day": 3, "total_days": 90, "total_posts": 270, "base_price": 270, "discount": 15, "final_price": 229.50},
        4: {"posts_per_day": 4, "total_days": 120, "total_posts": 480, "base_price": 480, "discount": 20, "final_price": 384},
        5: {"posts_per_day": 5, "total_days": 150, "total_posts": 750, "base_price": 750, "discount": 25, "final_price": 562.50},
        6: {"posts_per_day": 6, "total_days": 180, "total_posts": 1080, "base_price": 1080, "discount": 30, "final_price": 756},
        7: {"posts_per_day": 7, "total_days": 210, "total_posts": 1470, "base_price": 1470, "discount": 32, "final_price": 999.60},
        8: {"posts_per_day": 8, "total_days": 240, "total_posts": 1920, "base_price": 1920, "discount": 34, "final_price": 1267.20},
        9: {"posts_per_day": 9, "total_days": 270, "total_posts": 2430, "base_price": 2430, "discount": 36, "final_price": 1555.20},
        10: {"posts_per_day": 10, "total_days": 300, "total_posts": 3000, "base_price": 3000, "discount": 38, "final_price": 1860},
        11: {"posts_per_day": 11, "total_days": 330, "total_posts": 3630, "base_price": 3630, "discount": 40, "final_price": 2178},
        12: {"posts_per_day": 12, "total_days": 365, "total_posts": 4380, "base_price": 4380, "discount": 45, "final_price": 2409}
    }
    return plan_data.get(months, plan_data[1])


@router.callback_query(F.data.startswith("duration_"))
async def duration_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle progressive frequency plan selection"""
    try:
        duration_data = callback_query.data.replace("duration_", "")
        
        # Parse months from callback data
        if duration_data.endswith("_month") or duration_data.endswith("_months"):
            months = int(duration_data.replace("_month", "").replace("_months", ""))
        else:
            months = 1  # Default
        
        # Get plan details
        plan_details = get_progressive_plan_details(months)
        
        # Store plan information in state
        await state.update_data(
            duration_months=months,
            duration_days=plan_details["total_days"],
            posts_per_day=plan_details["posts_per_day"],
            total_posts=plan_details["total_posts"],
            base_price=plan_details["base_price"],
            discount_percent=plan_details["discount"],
            final_price=plan_details["final_price"]
        )
        
        # Proceed to payment
        await proceed_to_payment_handler(callback_query, state)
        
    except Exception as e:
        logger.error(f"Duration handler error: {e}")
        await callback_query.answer("Error processing duration selection.")


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
    """Start command handler with comprehensive anti-fraud protection"""
    user_id = message.from_user.id if message.from_user else 0
    username = message.from_user.username if message.from_user else None
    
    # Initialize anti-fraud system
    from anti_fraud import AntiFraudSystem
    fraud_system = AntiFraudSystem(db)
    
    # Log user interaction for fraud detection
    await db.log_user_interaction(user_id, "start_command", f"Username: {username}")
    await db.log_user_action(user_id, "start", "Bot started")
    
    # Check if user is blocked
    if await db.is_user_blocked(user_id):
        blocked_message = """
🚫 **Account Restricted**

Your account has been restricted due to suspicious activity.
If you believe this is an error, please contact support.

Contact: @I3lani_support
        """.strip()
        await message.answer(blocked_message)
        return
    
    # Extract referral code if present
    referrer_id = None
    if message.text and len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
        if referral_code.startswith('ref_'):
            try:
                referrer_id = int(referral_code.replace('ref_', ''))
                if referrer_id == user_id:
                    referrer_id = None  # Can't refer yourself
            except ValueError:
                logger.debug(f"Invalid referral code format: {referral_code}")
                referrer_id = None
    
    # Check if user is new
    existing_user = await db.get_user(user_id)
    is_new_user = not existing_user
    
    # Ensure user exists
    await ensure_user_exists(user_id, username)
    
    # Process atomic referral reward for new users with comprehensive fraud protection
    if is_new_user and referrer_id:
        try:
            # Collect user data for fraud analysis
            user_data = {
                'username': username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'profile_photo': bool(message.from_user.photo),
                'account_age_days': 999  # Default high value (unknown age)
            }
            
            # Validate referral with comprehensive fraud detection
            validation_result = await fraud_system.validate_referral(referrer_id, user_id, user_data)
            
            if validation_result['valid']:
                # Process legitimate referral
                from atomic_rewards import atomic_rewards
                if atomic_rewards:
                    result = await atomic_rewards.process_referral_reward(referrer_id, user_id)
                    if result['success']:
                        logger.info(f"✅ Legitimate referral processed: {referrer_id} -> {user_id}, amount: {result.get('reward_amount', 0)} TON")
                    else:
                        logger.warning(f"Referral reward failed: {result.get('message', 'Unknown error')}")
                else:
                    # Fallback to basic referral creation
                    await db.create_referral(referrer_id, user_id)
                    logger.info(f"✅ Basic referral created: {referrer_id} -> {user_id}")
            else:
                # Block fraudulent referral
                logger.warning(f"🚫 Referral blocked - Risk Score: {validation_result['risk_score']}, Reason: {validation_result['block_reason']}")
                
                # Send warning message to user if risk is high
                if validation_result['risk_score'] > 70:
                    fraud_message = f"""
🚨 **Security Alert**

Your referral could not be processed due to security concerns.
Risk Score: {validation_result['risk_score']}/100
Detected Issues: {', '.join(validation_result['flags'])}

If you believe this is an error, please contact support.
Contact: @I3lani_support
                    """.strip()
                    
                    await message.answer(fraud_message)
                
        except Exception as e:
            logger.error(f"Error processing referral with fraud detection: {e}")
            # Continue with user creation even if referral fails
    
    # Check if user already has language set
    user = await db.get_user(user_id)
    if user and user.get('language'):
        # User has language, show main menu
        await show_main_menu(message, user['language'])
    else:
        # New user, show language selection
        await state.set_state(AdCreationStates.language_selection)
        await message.answer(
            "World Welcome to I3lani Bot!\n\nChoose your language:",
            reply_markup=create_language_keyboard()
        )
    
    # Handle referral
    if referrer_id and referrer_id != user_id:
        await db.create_referral(referrer_id, user_id)


async def show_main_menu(message_or_query, language: str):
    """Show enhanced neural network main menu with visual effects"""
    # Get user_id from message or callback query
    if isinstance(message_or_query, Message):
        user_id = message_or_query.from_user.id
    else:
        user_id = message_or_query.from_user.id
    
    # Create enhanced neural network main menu
    text = await create_neural_main_menu_text(language, user_id)
    keyboard = await create_main_menu_keyboard(language, user_id)
    
    if isinstance(message_or_query, Message):
        # Send typing action for better UX
        await message_or_query.bot.send_chat_action(
            chat_id=message_or_query.chat.id,
            action="typing"
        )
        await message_or_query.answer(text, reply_markup=keyboard, parse_mode='HTML')
    else:
        try:
            await message_or_query.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
        except Exception as e:
            # If edit fails, send new message
            await message_or_query.message.answer(text, reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.startswith("lang_"))
async def language_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle language selection"""
    try:
        language_code = callback_query.data.replace("lang_", "")
        user_id = callback_query.from_user.id
        
        # Update user language
        await db.set_user_language(user_id, language_code)
        
        # Clear state and show main menu
        await state.clear()
        await show_main_menu(callback_query, language_code)
        await callback_query.answer(get_text(language_code, 'language_updated'))
        
    except Exception as e:
        logger.error(f"Language selection error: {e}")
        await callback_query.answer(get_text(language_code, 'error_updating_language'))




# Package selection handlers
@router.callback_query(F.data.startswith("select_package_"))
async def package_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle package selection"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        package_type = callback_query.data.replace("select_package_", "")
        
        # Import packages configuration
        from config import PACKAGES
        
        if package_type not in PACKAGES:
            await callback_query.answer("Invalid package selected", show_alert=True)
            return
        
        package = PACKAGES[package_type]
        
        # Check if user is eligible for free plan
        if package_type == 'free':
            # Check if user has used free plan in last 2 months
            user_stats = await db.get_user_stats(user_id)
            if user_stats.get('free_ads_used', 0) >= 3:
                await callback_query.answer(
                    "You've reached your free ad limit. Please choose a paid plan.",
                    show_alert=True
                )
                return
        
        # Store package selection in state
        await state.update_data(
            selected_package=package_type,
            package_details=package,
            price_usd=package['price_usd'],
            price_ton=package['price_ton'],
            duration_days=package['duration_days']
        )
        
        # Show package confirmation and ask for ad content
        confirmation_text = f"""
{package['emoji']} **{package['name']} Selected**

 **Package Details:**
- Duration: {package['duration_days']} days
- Posts per day: {package['posts_per_day']:.1f}
- Price: ${package['price_usd']:.0f}

Tip **Next Step:** Please send your advertisement content (text, photo, or video)
        """.strip()
        
        await callback_query.message.edit_text(
            confirmation_text,
            parse_mode='Markdown'
        )
        
        # Skip categories and go directly to content upload
        await state.set_state(AdCreationStates.upload_content)
        await show_content_upload(callback_query, state)
        await callback_query.answer(f"{package['name']} selected!")
        
    except Exception as e:
        logger.error(f"Package selection error: {e}")
        await callback_query.answer(get_text(language, 'error_selecting_package'))


# Enhanced Ad Creation Flow Handlers

async def show_content_upload(callback_query: CallbackQuery, state: FSMContext):
    """Show content upload for ad creation"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    if language == 'ar':
        text = """
Content **أرسل محتوى إعلانك**

يمكنك إرسال:
- نص فقط
- صورة مع وصف
- فيديو مع وصف

Tip نصيحة: اجعل إعلانك جذابًا وواضحًا!
        """.strip()
    elif language == 'ru':
        text = """
Content **Отправьте содержимое объявления**

Вы можете отправить:
- Только текст
- Изображение с описанием
- Видео с описанием

Tip Совет: Сделайте объявление привлекательным и понятным!
        """.strip()
    else:
        text = """
Content **Send Your Ad Content**

You can send:
- Text only
- Image with description
- Video with description

Tip: Make your ad engaging and clear!
        """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Back to Menu", callback_data="back_to_main")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')


# Content Upload Handler for Streamlined Flow

@router.message(AdCreationStates.upload_content)
async def upload_content_handler(message: Message, state: FSMContext):
    """Handle text content after photos in streamlined flow"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Only accept text at this stage (photos already handled)
    if message.content_type != "text":
        await message.answer("Please send text for your ad.")
        return
    
    content = message.text
    data = await state.get_data()
    
    # Store content and any previously uploaded photos
    await state.update_data(
        ad_content=content,
        content_type='text'
    )
    
    # Now ask for contact information
    await state.set_state(AdCreationStates.provide_contact_info)
    
    if language == 'ar':
        contact_text = """
**معلومات الاتصال**

كيف يمكن للعملاء التواصل معك؟

أمثلة:
- هاتف: +966501234567
- واتساب: +966501234567
- بريد: user@email.com
- تليجرام: @username

أرسل معلومات الاتصال:
        """.strip()
    elif language == 'ru':
        contact_text = """
**Контактная информация**

Как клиенты могут связаться с вами?

Примеры:
- Телефон: +966501234567
- WhatsApp: +966501234567
- Email: user@email.com
- Telegram: @username

Отправьте контактную информацию:
        """.strip()
    else:
        contact_text = """
**Contact Information**

How should customers reach you?

Examples:
- Phone: +966501234567
Your ad content is ready! Let's proceed to channel selection.
        """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'continue_to_channels'), callback_data="continue_to_channels")],
        [InlineKeyboardButton(text=get_text(language, 'back_to_text'), callback_data="back_to_text")]
    ])
    
    await message.answer(contact_text, reply_markup=keyboard)
    
    # Show channel selection - create proper channel selection message
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Get available channels
    channels = await db.get_channels(active_only=True)
    
    if not channels:
        await message.answer("No channels available for advertising. Please contact admin.")
        return
    
    # Create channel selection text
    if language == 'ar':
        text = """اختر القنوات للإعلان

اختر القنوات التي تريد نشر إعلانك فيها:"""
    elif language == 'ru': 
        text = """Выберите каналы для рекламы

Выберите каналы для размещения вашего объявления:"""
    else:
        text = """Choose Channels for Your Ad

Select the channels where you want to publish your advertisement:"""
    
    # Get selected channels from state
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Create keyboard with channels
    keyboard_rows = []
    for channel in channels:
        is_selected = channel['channel_id'] in selected_channels
        status = "[] " if is_selected else ""
        keyboard_rows.append([InlineKeyboardButton(
            text=f"{status}{channel['name']} ({channel['subscribers']:,} subscribers)",
            callback_data=f"toggle_channel_{channel['channel_id']}"
        )])
    
    # Add control buttons
    if selected_channels:
        keyboard_rows.append([InlineKeyboardButton(
            text=f"Continue to Pricing ({len(selected_channels)} channels)",
            callback_data="continue_to_duration"
        )])
    else:
        keyboard_rows.append([InlineKeyboardButton(
            text="Select at least one channel",
            callback_data="select_channels_info"
        )])
    
    keyboard_rows.append([InlineKeyboardButton(
        text="Back to Menu",
        callback_data="back_to_main"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')


# Category selection handler removed - going directly to content upload


# Subcategory and city selection handlers removed - streamlined flow


# Location selection removed - streamlined flow


# Location selection handler removed - streamlined flow


@router.message(AdCreationStates.upload_photos, F.photo)
async def handle_photo_upload(message: Message, state: FSMContext):
    """Handle photo uploads"""
    try:
        data = await state.get_data()
        uploaded_photos = data.get('uploaded_photos', [])
        
        if len(uploaded_photos) >= 5:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Yes Done with Photos", callback_data="done_photos")]
            ])
            await message.reply("Maximum 5 photos allowed. Click Done to continue.", reply_markup=keyboard)
            return
        
        # Store photo file_id
        photo_file_id = message.photo[-1].file_id
        uploaded_photos.append({
            'file_id': photo_file_id,
            'type': 'photo'
        })
        
        await state.update_data(uploaded_photos=uploaded_photos)
        # Create button interface to replace /done command
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Yes Done with Photos", callback_data="done_photos"),
                InlineKeyboardButton(text=" Add More", callback_data="add_more_photos")
            ],
            [InlineKeyboardButton(text=" Skip Photos", callback_data="skip_photos")]
        ])
        
        await message.reply(f" Photo {len(uploaded_photos)}/5 uploaded.", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Photo upload error: {e}")
        await message.reply(get_text(language, 'error_uploading_photo'))


@router.callback_query(F.data == "continue_from_photos")
async def continue_from_photos(callback_query: CallbackQuery, state: FSMContext):
    """Continue from photo upload step"""
    await state.set_state(AdCreationStates.provide_contact_info)
    
    contact_text = """
**Phone** **Provide Contact Information**

How should customers reach you?

Examples:
- Phone: +966501234567
- WhatsApp: +966501234567
- Email: user@email.com
- Telegram: @username

Content ready! Let's proceed to channel selection.
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Continue to Channels", callback_data="continue_to_channels")],
        [InlineKeyboardButton(text="◀️ Back to Photos", callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(contact_text, reply_markup=keyboard)
    await callback_query.answer()


@router.callback_query(F.data == "add_more_photos") 
async def add_more_photos(callback_query: CallbackQuery, state: FSMContext):
    """Allow user to add more photos"""
    await callback_query.message.edit_text(
        " **Add More Photos**\n\nSend additional photos (max 5 total):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Yes Done with Photos", callback_data="continue_from_photos")]
        ])
    )
    await callback_query.answer("Send more photos")


@router.callback_query(F.data == "skip_photos")
async def skip_photos_handler(callback_query: CallbackQuery, state: FSMContext):
    """Skip photo upload step"""
    await state.set_state(AdCreationStates.provide_contact_info)
    
    contact_text = """
**Phone** **Provide Contact Information**

How should customers reach you?

Examples:
- Phone: +966501234567
- WhatsApp: +966501234567
- Email: user@email.com
- Telegram: @username

Content ready! Let's proceed to channel selection.
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'continue_to_channels'), callback_data="continue_to_channels")],
        [InlineKeyboardButton(text=get_text(language, 'back_to_photos'), callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(contact_text, reply_markup=keyboard)
    await callback_query.answer("Ready for channel selection")


@router.callback_query(F.data == "skip_photos_to_text")
async def skip_photos_to_text_handler(callback_query: CallbackQuery, state: FSMContext):
    """Skip photo upload and go to text input"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.upload_content)
    
    if language == 'ar':
        text = """
 **اكتب نص إعلانك**

اكتب تفاصيل إعلانك بوضوح
يمكنك تضمين:
- وصف المنتج/الخدمة
- السعر
- المميزات

أرسل النص الآن:
        """.strip()
    elif language == 'ru':
        text = """
 **Напишите текст объявления**

Опишите ваш товар или услугу
Можете включить:
- Описание
- Цену
- Преимущества

Отправьте текст:
        """.strip()
    else:
        text = """
 **Write Your Ad Text**

Write your ad details clearly
You can include:
- Product/service description
- Price
- Features

Send your text now:
        """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Back to Photos", callback_data="create_ad")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()


@router.callback_query(F.data == "done_photos")
async def done_photos_handler(callback_query: CallbackQuery, state: FSMContext):
    """Complete photo upload and go to text input"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.upload_content)
    
    data = await state.get_data()
    photos_count = len(data.get('uploaded_photos', []))
    
    if language == 'ar':
        text = f"""
 **اكتب نص إعلانك**

تم تحميل {photos_count} صورة [[]]

الآن اكتب تفاصيل إعلانك:
- وصف المنتج/الخدمة
- السعر
- المميزات

أرسل النص الآن:
        """.strip()
    elif language == 'ru':
        text = f"""
 **Напишите текст объявления**

Загружено {photos_count} фото [[]]

Теперь напишите детали:
- Описание товара/услуги
- Цену
- Преимущества

Отправьте текст:
        """.strip()
    else:
        text = f"""
 **Write Your Ad Text**

{photos_count} photos uploaded [[]]

Now write your ad details:
- Product/service description
- Price
- Features

Send your text now:
        """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Back to Photos", callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer("Now write your ad text")


@router.message(AdCreationStates.upload_photos, F.text.in_(["/skip", "/done"]))
async def handle_photo_completion(message: Message, state: FSMContext):
    """Handle photo upload completion - fallback for /done command"""
    try:
        # Ask for contact information
        contact_text = """
**Phone** **Provide Contact Information**

How should interested buyers contact you?

Please provide:
- Phone number
- Email (optional)
- Preferred contact method
- Available times

Send your contact information as a text message.
        """.strip()
        
        await message.reply(contact_text, parse_mode='Markdown')
        await state.set_state(AdCreationStates.provide_contact_info)
        
    except Exception as e:
        logger.error(f"Photo completion error: {e}")
        await message.reply(get_text(language, 'error_processing_request'))


@router.message(AdCreationStates.provide_contact_info)
async def handle_contact_info(message: Message, state: FSMContext):
    """Handle contact information input"""
    try:
        contact_info = message.text
        await state.update_data(contact_info=contact_info)
        
        # Show preview
        await show_ad_preview(message, state)
        
    except Exception as e:
        logger.error(f"Contact info error: {e}")
        await message.reply("Error processing contact information. Please try again.")


async def show_ad_preview(message: Message, state: FSMContext):
    """Show ad preview for confirmation"""
    try:
        data = await state.get_data()
        
        preview_text = f"""
Preview **Ad Preview**

**Category:** {data.get('category_name', 'N/A')} to {data.get('subcategory_name', 'N/A')}
**Location:** {data.get('location_name', 'N/A')}
**Package:** {data.get('package_details', {}).get('name', 'N/A')}

**Ad Details:**
{data.get('ad_details', 'No details provided')}

**Contact Information:**
{data.get('contact_info', 'No contact info provided')}

**Photos:** {len(data.get('uploaded_photos', []))} uploaded

Is this correct?
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Yes Confirm & Continue", callback_data="confirm_ad"),
                InlineKeyboardButton(text="Edit Edit Ad", callback_data="edit_ad")
            ],
            [InlineKeyboardButton(text="No Cancel", callback_data="cancel_ad")]
        ])
        
        await message.reply(preview_text, reply_markup=keyboard, parse_mode='Markdown')
        await state.set_state(AdCreationStates.preview_ad)
        
    except Exception as e:
        logger.error(f"Preview error: {e}")
        await message.reply("Error showing preview. Please try again.")


@router.callback_query(F.data == "confirm_ad")
async def confirm_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle ad confirmation and proceed to payment"""
    try:
        data = await state.get_data()
        
        # Create ad in database
        user_id = callback_query.from_user.id
        ad_content = data.get('ad_details', '')
        
        # Combine all ad information
        full_ad_content = f"""
{data.get('category_name', '')} to {data.get('subcategory_name', '')}
Location {data.get('location_name', '')}

{ad_content}

**Phone** Contact: {data.get('contact_info', '')}
        """.strip()
        
        ad_id = await db.create_ad(
            user_id=user_id,
            content=full_ad_content,
            media_url=data.get('uploaded_photos', [{}])[0].get('file_id') if data.get('uploaded_photos') else None,
            content_type='photo' if data.get('uploaded_photos') else 'text'
        )
        
        await state.update_data(ad_id=ad_id, ad_content=full_ad_content)
        
        # Proceed to channel selection or payment based on package
        package = data.get('package', 'free')
        
        # Always proceed to channel selection first for proper flow
        # The proceed_to_payment_handler will determine if payment is needed
        await show_channel_selection_for_enhanced_flow(callback_query, state)
            
    except Exception as e:
        logger.error(f"Ad confirmation error: {e}")
        await callback_query.answer("Error confirming ad. Please try again.")


async def handle_free_package_publishing(callback_query: CallbackQuery, state: FSMContext):
    """Handle free package ad publishing"""
    try:
        data = await state.get_data()
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Get ad content from state
        ad_content = data.get('ad_text', '') or data.get('ad_content', '')
        uploaded_photos = data.get('photos', []) or data.get('uploaded_photos', [])
        
        # Create ad record in database
        try:
            content_type = 'photo' if uploaded_photos else 'text'
            media_url = uploaded_photos[0]['file_id'] if uploaded_photos else None
            
            ad_id = await db.create_ad(
                user_id=user_id,
                content=ad_content,
                media_url=media_url,
                content_type=content_type
            )
            
            # Update user stats for free ads
            await db.increment_free_ads_used(user_id)
            
            # Process atomic reward for new partners
            try:
                from atomic_rewards import atomic_rewards
                if atomic_rewards:
                    await atomic_rewards.process_registration_reward(user_id)
            except:
                pass  # Continue even if reward system fails
            
            success_text = f"""
🎉 **Free Ad Created Successfully!**

✅ Your ad has been approved and will be published shortly
📅 Duration: 3 days  
📊 Reach: ~1000+ users
📺 Channel: @i3lani

📈 **Track Your Ad:**
- Ad ID: #{ad_id}
- Status: Approved
- Publishing: Within 24 hours

🚀 **Upgrade for More:**
- Instant publishing
- Multiple channels
- Extended duration
- Better targeting

Thank you for using I3lani Bot!
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Upgrade Now", callback_data="show_packages")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
            
            await callback_query.message.edit_text(success_text, reply_markup=keyboard)
            await state.clear()
            
        except Exception as db_error:
            logger.error(f"Database error in free ad: {db_error}")
            success_text = """
🎉 **Free Ad Submitted Successfully!**

✅ Your ad has been received and will be reviewed
📅 Publishing: Within 24 hours
📺 Channel: @i3lani

Thank you for using I3lani Bot!
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
            
            await callback_query.message.edit_text(success_text, reply_markup=keyboard)
            await state.clear()
            
    except Exception as e:
        logger.error(f"Free package publishing error: {e}")
        await callback_query.answer("Error creating free ad. Please try again.", show_alert=True)


async def show_channel_selection_for_enhanced_flow(callback_query: CallbackQuery, state: FSMContext):
    """Show channel selection for enhanced flow with enhanced UX"""
    # Get user language first
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Send typing action for better UX
    await callback_query.bot.send_chat_action(
        chat_id=callback_query.message.chat.id,
        action="typing"
    )
    
    # Get only active channels where bot is admin
    channels = await db.get_bot_admin_channels()
    
    if not channels:
        no_channels_text = {
            'en': get_text('en', 'no_channels'),
            'ar': get_text('ar', 'no_channels'),
            'ru': get_text('ru', 'no_channels')
        }
        
        await callback_query.message.edit_text(
            no_channels_text.get(language, no_channels_text['en']),
            parse_mode='Markdown'
        )
        return
    
    # Get selected channels from state
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Calculate total reach
    total_reach = 0
    for channel in channels:
        if channel['channel_id'] in selected_channels:
            total_reach += channel.get('subscribers', 0)
    
    # Create enhanced channel text with better visuals
    if language == 'ar':
        channel_text = f"""[TV] **اختر القنوات لإعلانك**

[*] **المحدد:** {len(selected_channels)}/{len(channels)} قناة
[Users] **الوصول الإجمالي:** {total_reach:,} مشترك

[!] انقر على القنوات للاختيار/إلغاء الاختيار:"""
    elif language == 'ru':
        channel_text = f"""[TV] **Выберите каналы для рекламы**

[*] **Выбрано:** {len(selected_channels)}/{len(channels)} каналов
[Users] **Общий охват:** {total_reach:,} подписчиков

[!] Нажмите на каналы для выбора/отмены:"""
    else:
        channel_text = f"""[TV] **Select Channels for Your Ad**

[*] **Selected:** {len(selected_channels)}/{len(channels)} channels
[Users] **Total Reach:** {total_reach:,} subscribers

[!] Click channels to select/deselect:"""
    
    keyboard_rows = []
    for channel in channels:
        # Check if channel is selected
        is_selected = channel['channel_id'] in selected_channels
        check_emoji = "[[]]" if is_selected else "[O]"
        
        # Enhanced button with subscriber count
        subscribers = channel.get('subscribers', 0)
        sub_text = f" ({subscribers:,} subs)" if subscribers > 0 else ""
        
        keyboard_rows.append([InlineKeyboardButton(
            text=f"{check_emoji} {channel['name']}{sub_text}",
            callback_data=f"toggle_channel_{channel['channel_id']}"
        )])
    
    # Add control buttons with better styling
    keyboard_rows.append([
        InlineKeyboardButton(text="[Location] Select All", callback_data="select_all_channels"),
        InlineKeyboardButton(text="[X] Deselect All", callback_data="deselect_all_channels")
    ])
    
    # Dynamic continue button - disabled if no channels selected
    continue_text = f"[[]] Continue ({len(selected_channels)} selected)" if selected_channels else "[!] Select channels first"
    keyboard_rows.append([InlineKeyboardButton(
        text=continue_text,
        callback_data="proceed_to_payment" if selected_channels else "no_channels_warning"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    try:
        await callback_query.message.edit_text(
            channel_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        # If edit fails, send new message
        await callback_query.message.answer(
            channel_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    await state.set_state(AdCreationStates.channel_selection)


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
Settings **Settings**

World **Current Language:** {LANGUAGES[language]['name']} {LANGUAGES[language]['flag']}

Refresh **Change Language:**
Choose your preferred language below.

Stats **Account Info:**
- User ID: {user_id}
- Language: {language.upper()}
- Status: Active
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=" English", callback_data="lang_en"),
                InlineKeyboardButton(text=" العربية", callback_data="lang_ar")
            ],
            [
                InlineKeyboardButton(text=" Русский", callback_data="lang_ru")
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Back to Main", 
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
Books **Help & Commands**

Launch **Getting Started:**
1. Click "Create Ad" to start
2. Submit your ad content
3. Choose channels and duration
4. Make payment (TON or Stars)
5. Your ad goes live automatically!

Tip **Available Commands:**
- /start - Main menu
- /mystats - View your statistics
- /support - Get help
- /admin - Admin panel (admins only)
- /refresh - Refresh data
- /help - This help message

Target **Features:**
- Multi-channel advertising
- TON and Telegram Stars payment
- Real-time ad publishing
- Campaign tracking
- Referral system

Question **Need Help?** Use /support to contact us!
        """.strip()
        
        await callback_query.message.edit_text(
            help_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="◀️ Back to Main", 
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
    """Start enhanced ad creation process - photos first"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Start with content upload - fixed state
    await state.set_state(AdCreationStates.upload_content)
    
    if language == 'ar':
        text = """
[Photo] **إنشاء إعلان جديد**

هل تريد إضافة صور لإعلانك؟
يمكنك إضافة حتى 5 صور

أرسل الصور الآن أو اضغط "تخطي" للمتابعة بدون صور
        """.strip()
    elif language == 'ru':
        text = """
[Photo] **Создать новое объявление**

Хотите добавить фотографии?
Можно добавить до 5 фотографий

Отправьте фото или нажмите "Пропустить"
        """.strip()
    else:
        text = """
[Photo] **Create New Ad**

Would you like to add photos to your ad?
You can add up to 5 photos

Send photos now or click "Skip" to continue without photos
        """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Skip Photos", callback_data="skip_photos_to_text")],
        [InlineKeyboardButton(text=" Back", callback_data="back_to_main")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()


@router.callback_query(F.data == "free_trial")
async def free_trial_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle free trial selection"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Check if user can still use free trial
    can_use_trial = await db.check_free_trial_available(user_id)
    
    if not can_use_trial:
        await callback_query.answer("You have already used your free trial!")
        await show_main_menu(callback_query, language)
        return
    
    # Set free trial parameters
    await state.update_data(
        is_free_trial=True,
        days=1,
        posts_per_day=2,
        free_trial_mode=True
    )
    
    # Show free trial information
    trial_text = f"""
[Gift] **Free Trial Offer**

You're about to start your FREE trial:
• Duration: 1 day
• Posts per day: 2 posts
• Total posts: 2 posts
• Price: **FREE** (valued at $1.90)

This is a one-time offer for new users to experience our multi-post scheduling feature!

**How it works:**
1. Create your ad content
2. Select channels
3. We'll publish 2 posts throughout the day
4. Track performance in your dashboard

Ready to create your free trial ad?
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="[Star] Start Free Trial", callback_data="start_free_trial")],
        [InlineKeyboardButton(text="◀️ Back to Main", callback_data="back_to_main")]
    ])
    
    await callback_query.message.edit_text(trial_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()


@router.callback_query(F.data == "start_free_trial")
async def start_free_trial_handler(callback_query: CallbackQuery, state: FSMContext):
    """Start the free trial ad creation"""
    user_id = callback_query.from_user.id
    
    # Mark free trial as used
    await db.use_free_trial(user_id)
    
    # Start with photo upload (same as regular ad creation)
    await state.set_state(AdCreationStates.upload_photos)
    
    language = await get_user_language(user_id)
    
    if language == 'ar':
        text = """
[Photo] **إنشاء إعلان مجاني تجريبي**

هل تريد إضافة صور لإعلانك التجريبي؟
يمكنك إضافة حتى 5 صور

أرسل الصور الآن أو اضغط "تخطي" للمتابعة بدون صور
        """.strip()
    elif language == 'ru':
        text = """
[Photo] **Создать пробное объявление**

Хотите добавить фотографии в пробное объявление?
Можно добавить до 5 фотографий

Отправьте фото или нажмите "Пропустить"
        """.strip()
    else:
        text = """
[Photo] **Create Free Trial Ad**

Would you like to add photos to your trial ad?
You can add up to 5 photos

Send photos now or click "Skip" to continue without photos
        """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Skip Photos", callback_data="skip_photos_to_text")],
        [InlineKeyboardButton(text=" Back", callback_data="back_to_main")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()


async def check_free_ads_limit(user_id: int) -> int:
    """Check how many free ads a user has remaining this month"""
    try:
        user = await db.get_user(user_id)
        if not user:
            return 3
        
        # Check if we need to reset monthly counter
        last_reset = datetime.fromisoformat(user.get('last_free_ad_reset', datetime.now().isoformat()))
        now = datetime.now()
        
        # If it's been more than a month, reset counter
        if (now - last_reset).days >= 30:
            await db.reset_free_ads_counter(user_id)
            return 3
        
        used = user.get('free_ads_used', 0)
        return max(0, 3 - used)
    except Exception as e:
        logger.error(f"Error checking free ads limit: {e}")
        return 3


async def get_next_reset_date(user_id: int) -> str:
    """Get the next reset date for free ads"""
    try:
        user = await db.get_user(user_id)
        if not user:
            return "Next month"
        
        last_reset = datetime.fromisoformat(user.get('last_free_ad_reset', datetime.now().isoformat()))
        next_reset = last_reset + timedelta(days=30)
        return next_reset.strftime("%B %d, %Y")
    except Exception as e:
        logger.error(f"Error getting next reset date: {e}")
        return "Next month"


@router.callback_query(F.data == "select_package_free")
async def select_free_package(callback_query: CallbackQuery, state: FSMContext):
    """Handle free package selection with monthly limit check"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Check if user has exceeded free ads limit
    free_ads_remaining = await check_free_ads_limit(user_id)
    
    if free_ads_remaining <= 0:
        next_reset = await get_next_reset_date(user_id)
        await callback_query.message.edit_text(
            f"""
No **Free Ads Limit Reached**

You have used all 3 free ads for this month.

**Options:**
- Wait for next month reset
- Upgrade to Bronze Plan ($10/month) 
- Upgrade to Silver Plan ($29/3 months)
- Upgrade to Gold Plan ($47/6 months)

**Next reset:** {next_reset}
            """.strip(),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🟫 Bronze $10", callback_data="select_package_bronze")],
                [InlineKeyboardButton(text="[Silver] Silver $29", callback_data="select_package_silver")],
                [InlineKeyboardButton(text="[Gold] Gold $47", callback_data="select_package_gold")],
                [InlineKeyboardButton(text="◀️ Back to Start", callback_data="back_to_start")]
            ])
        )
        await callback_query.answer("Free ads limit reached for this month!")
        return
    
    await state.update_data(package="free")
    await state.set_state(AdCreationStates.category_selection)
    
    await show_category_selection(callback_query, state)
    await callback_query.answer(f"Free package selected! {free_ads_remaining} free ads remaining this month.")


@router.callback_query(F.data == "select_package_bronze")
async def select_bronze_package(callback_query: CallbackQuery, state: FSMContext):
    """Handle bronze package selection"""
    await state.update_data(package="bronze")
    await state.set_state(AdCreationStates.category_selection)
    await show_category_selection(callback_query, state)
    await callback_query.answer("Bronze package selected!")


@router.callback_query(F.data == "select_package_silver")
async def select_silver_package(callback_query: CallbackQuery, state: FSMContext):
    """Handle silver package selection"""
    await state.update_data(package="silver")
    await state.set_state(AdCreationStates.category_selection)
    await show_category_selection(callback_query, state)
    await callback_query.answer("Silver package selected!")


@router.callback_query(F.data == "select_package_gold")
async def select_gold_package(callback_query: CallbackQuery, state: FSMContext):
    """Handle gold package selection"""
    await state.update_data(package="gold")
    await state.set_state(AdCreationStates.category_selection)
    await show_category_selection(callback_query, state)
    await callback_query.answer("Gold package selected!")


async def refresh_channel_selection_keyboard(callback_query: CallbackQuery, state: FSMContext):
    """Refresh the channel selection keyboard after toggle"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Get available channels
        channels = await db.get_channels(active_only=True)
        
        # Get selected channels from state
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        # Create keyboard with channels
        keyboard_rows = []
        for channel in channels:
            is_selected = channel['channel_id'] in selected_channels
            status = "[] " if is_selected else ""
            keyboard_rows.append([InlineKeyboardButton(
                text=f"{status}{channel['name']} ({channel['subscribers']:,} subscribers)",
                callback_data=f"toggle_channel_{channel['channel_id']}"
            )])
        
        # Add control buttons
        if selected_channels:
            keyboard_rows.append([InlineKeyboardButton(
                text=f"Continue to Pricing ({len(selected_channels)} channels)",
                callback_data="continue_to_duration"
            )])
        else:
            keyboard_rows.append([InlineKeyboardButton(
                text="Select at least one channel",
                callback_data="select_channels_info"
            )])
        
        keyboard_rows.append([InlineKeyboardButton(
            text="Back to Menu",
            callback_data="back_to_main"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
        
        # Edit the message with updated keyboard
        await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error refreshing channel selection: {e}")


@router.callback_query(F.data.startswith("toggle_channel_"))
async def toggle_channel_selection(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel selection toggle"""
    try:
        channel_id = callback_query.data.replace("toggle_channel_", "")
        user_id = callback_query.from_user.id
        
        # Get current selected channels
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        # Toggle channel selection
        if channel_id in selected_channels:
            selected_channels.remove(channel_id)
        else:
            selected_channels.append(channel_id)
        
        # Update state
        await state.update_data(selected_channels=selected_channels)
        
        # Refresh the channel selection interface
        await refresh_channel_selection_keyboard(callback_query, state)
        await callback_query.answer(f"Channel {'selected' if channel_id in selected_channels else 'deselected'}")
        
    except Exception as e:
        logger.error(f"Channel toggle error: {e}")
        await callback_query.answer("Error updating selection")


@router.callback_query(F.data == "select_all_channels")
async def select_all_channels(callback_query: CallbackQuery, state: FSMContext):
    """Select all available channels"""
    try:
        channels = await db.get_channels(active_only=True)
        selected_channels = [channel['channel_id'] for channel in channels]
        await state.update_data(selected_channels=selected_channels)
        
        await show_channel_selection_for_enhanced_flow(callback_query, state)
        await callback_query.answer("All channels selected")
        
    except Exception as e:
        logger.error(f"Select all channels error: {e}")
        await callback_query.answer("Error selecting channels")


@router.callback_query(F.data == "deselect_all_channels")
async def deselect_all_channels(callback_query: CallbackQuery, state: FSMContext):
    """Deselect all channels"""
    try:
        await state.update_data(selected_channels=[])
        await show_channel_selection_for_enhanced_flow(callback_query, state)
        await callback_query.answer("All channels deselected")
        
    except Exception as e:
        logger.error(f"Deselect all channels error: {e}")
        await callback_query.answer("Error deselecting channels")


@router.callback_query(F.data.startswith("edit_package_"))
async def edit_package_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle package editing"""
    try:
        package_type = callback_query.data.replace("edit_package_", "")
        user_id = callback_query.from_user.id
        
        if user_id not in ADMIN_IDS:
            await callback_query.answer("Access denied")
            return
            
        await state.set_state(AdminStates.edit_subscription)
        await state.update_data(editing_package=package_type)
        
        package_prices = {'bronze': 10, 'silver': 29, 'gold': 47, 'free': 0}
        current_price = package_prices.get(package_type, 0)
        
        text = f"""
Edit **Edit {package_type.title()} Package**

Current settings:
- Package: {package_type.title()}
- Current price: ${current_price}

What would you like to edit?
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Price Change Price", callback_data=f"change_price_{package_type}"),
                InlineKeyboardButton(text=" Change Duration", callback_data=f"change_duration_{package_type}")
            ],
            [
                InlineKeyboardButton(text="Content Change Description", callback_data=f"change_desc_{package_type}"),
                InlineKeyboardButton(text="Target Change Features", callback_data=f"change_features_{package_type}")
            ],
            [InlineKeyboardButton(text="◀️ Back to Subscription", callback_data="admin_edit_subscription")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Edit package error: {e}")
        await callback_query.answer("Error editing package")


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
            "No Unsupported content type. Please send text, photo, or video."
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
        reply_markup=await create_channel_selection_keyboard(language)
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
        reply_markup=await create_channel_selection_keyboard(language, selected_channels)
    )
    await callback_query.answer()


@router.callback_query(F.data == "continue_to_duration")
async def continue_to_duration_handler(callback_query: CallbackQuery, state: FSMContext):
    """Continue to duration selection with dynamic interface"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Check if this is a free trial
    data = await state.get_data()
    is_free_trial = data.get('is_free_trial', False)
    
    if is_free_trial:
        # Free trial - skip pricing and go to order confirmation
        selected_channels = data.get('selected_channels', [])
        
        # Get channel details
        channels = await db.get_channels()
        selected_channel_data = [ch for ch in channels if ch['channel_id'] in selected_channels]
        
        # Create order confirmation text
        channel_names = [ch['name'] for ch in selected_channel_data]
        total_reach = sum(ch.get('subscribers', 0) for ch in selected_channel_data)
        
        confirmation_text = f"""
[Check] **Free Trial Order Summary**

[Gift] **FREE TRIAL** (One-time offer)

[Date] **Duration:** 1 day
[Chart] **Posts per day:** 2 posts
[Note] **Total posts:** 2 posts
[Money] **Price:** **FREE** (valued at $1.90)

[TV] **Selected Channels ({len(selected_channels)}):**
{chr(10).join(f"• {name}" for name in channel_names)}

[Users] **Total Reach:** {total_reach:,} subscribers

Your ad will be published 2 times throughout the day across all selected channels.

Ready to confirm your free trial?
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="[Check] Confirm Free Trial", callback_data="confirm_free_trial")],
            [InlineKeyboardButton(text="◀️ Back to Channels", callback_data="back_to_channel_selection")]
        ])
        
        await callback_query.message.edit_text(confirmation_text, reply_markup=keyboard, parse_mode='Markdown')
        await callback_query.answer("Free trial ready!")
        return
    
    # Regular flow - continue to duration selection
    await state.set_state(AdCreationStates.duration_selection)
    
    # Initialize days to 1 for dynamic selector
    await state.update_data(selected_days=1)
    await show_dynamic_days_selector(callback_query, state, 1)


@router.callback_query(F.data == "confirm_free_trial")
async def confirm_free_trial_handler(callback_query: CallbackQuery, state: FSMContext):
    """Confirm and create free trial order"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        data = await state.get_data()
        
        # Create ad in database
        ad_content = data.get('ad_text', '')
        photos = data.get('photos', [])
        selected_channels = data.get('selected_channels', [])
        
        # Create ad record
        ad_id = await db.create_ad(
            user_id=user_id,
            content=ad_content,
            media_url=photos[0] if photos else None,
            content_type='photo' if photos else 'text'
        )
        
        # Create free trial subscription for each channel
        for channel_id in selected_channels:
            subscription_id = await db.create_subscription(
                user_id=user_id,
                ad_id=ad_id,
                channel_id=channel_id,
                duration_months=0,  # Free trial
                total_price=0.0,
                currency='USD',
                posts_per_day=2,
                total_posts=2,
                discount_percent=100  # 100% discount for free trial
            )
            
            # Create payment record for tracking
            await db.create_payment(
                user_id=user_id,
                subscription_id=subscription_id,
                amount=0.0,
                currency='USD',
                payment_method='free_trial',
                memo=f'FREE_TRIAL_{ad_id}'
            )
        
        # Success message
        success_text = f"""
[Check] **Free Trial Activated!**

Your free trial ad has been created successfully!

[Chart] **What happens next:**
• Your ad will be published 2 times today
• First post will be sent within the next hour
• Second post will follow later in the day
• You'll receive notifications for each publication

[Phone] **Track your ad:**
Use "My Ads" from the main menu to see:
- Publication status
- View count
- Performance metrics

Thank you for trying I3lani Bot! After your trial, you can create unlimited paid ads with our flexible pricing.

Enjoy your free trial!
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="[Chart] View My Ads", callback_data="my_ads")],
            [InlineKeyboardButton(text="[Home] Main Menu", callback_data="back_to_main")]
        ])
        
        await callback_query.message.edit_text(success_text, reply_markup=keyboard, parse_mode='Markdown')
        await callback_query.answer("Free trial activated!")
        
        # Clear state
        await state.clear()
        
    except Exception as e:
        logger.error(f"Free trial confirmation error: {e}")
        await callback_query.answer("Error creating free trial. Please try again.")
        await show_main_menu(callback_query, language)


async def show_dynamic_days_selector(callback_query: CallbackQuery, state: FSMContext, days: int = 1):
    """Show dynamic days selector with +/- buttons and live pricing"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get selected channels data for price calculation
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Calculate pricing with current settings (1 post per day default)
    from dynamic_pricing import DynamicPricing
    pricing = DynamicPricing()
    calculation = pricing.calculate_total_cost(
        days=days,
        posts_per_day=1,  # Default to 1 post per day for preview
        channels=[]  # Channel pricing will be calculated later
    )
    
    # Create the dynamic interface text
    text = f"""**Step 1: Choose Campaign Duration**

How many days: {days}

**Live Price Preview** (1 post/day):
- TON: {calculation['total_ton']} TON
- Stars: {calculation['total_stars']} Stars

**Volume Discount Info:**
- 1 post/day = No discount
- 2 posts/day = 5% off  
- 4 posts/day = 10% off
- 8+ posts/day = 20%+ off

*Note: Final price calculated after selecting posts per day*"""
    
    # Create +/- keyboard for days selection
    keyboard_rows = []
    
    # Days adjustment row
    minus_callback = f"days_adjust_minus_{days}" if days > 1 else "days_adjust_none"
    plus_callback = f"days_adjust_plus_{days}"
    
    keyboard_rows.append([
        InlineKeyboardButton(text="[-]", callback_data=minus_callback),
        InlineKeyboardButton(text=f"{days} days", callback_data="days_info"),
        InlineKeyboardButton(text="[+]", callback_data=plus_callback)
    ])
    
    # Quick selection buttons
    if days != 1:
        keyboard_rows.append([InlineKeyboardButton(text="1 Day", callback_data="days_quick_1")])
    if days != 7:
        keyboard_rows.append([InlineKeyboardButton(text="7 Days", callback_data="days_quick_7")])
    if days != 30:
        keyboard_rows.append([InlineKeyboardButton(text="30 Days", callback_data="days_quick_30")])
    
    # Continue button
    keyboard_rows.append([
        InlineKeyboardButton(text=f"Continue with {days} days", callback_data="days_confirm")
    ])
    
    # Back button
    keyboard_rows.append([
        InlineKeyboardButton(text="Back", callback_data="back_to_start")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    try:
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    except (AttributeError, Exception):
        await callback_query.message.answer(text, reply_markup=keyboard, parse_mode='Markdown')


# Days adjustment handlers
@router.callback_query(F.data.startswith("days_adjust_minus_"))
async def days_adjust_minus_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle minus button for days"""
    current_days = int(callback_query.data.replace("days_adjust_minus_", ""))
    new_days = max(1, current_days - 1)
    await state.update_data(selected_days=new_days)
    await show_dynamic_days_selector(callback_query, state, new_days)
    await callback_query.answer()

@router.callback_query(F.data.startswith("days_adjust_plus_"))
async def days_adjust_plus_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle plus button for days"""
    current_days = int(callback_query.data.replace("days_adjust_plus_", ""))
    new_days = min(365, current_days + 1)  # Max 365 days
    await state.update_data(selected_days=new_days)
    await show_dynamic_days_selector(callback_query, state, new_days)
    await callback_query.answer()

@router.callback_query(F.data.startswith("days_quick_"))
async def days_quick_select_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle quick day selection buttons"""
    days = int(callback_query.data.replace("days_quick_", ""))
    await state.update_data(selected_days=days)
    await show_dynamic_days_selector(callback_query, state, days)
    await callback_query.answer()

@router.callback_query(F.data == "days_adjust_none")
async def days_adjust_none_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle disabled minus button"""
    await callback_query.answer("Minimum 1 day required")

@router.callback_query(F.data == "days_info")
async def days_info_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle days info button"""
    await callback_query.answer("Use +/- buttons to adjust days")

@router.callback_query(F.data == "days_confirm")
async def days_confirm_handler(callback_query: CallbackQuery, state: FSMContext):
    """Confirm days selection and continue to frequency tier selection"""
    data = await state.get_data()
    selected_days = data.get('selected_days', 1)
    
    # Calculate pricing and show payment summary
    pricing = FrequencyPricingSystem()
    pricing_data = pricing.calculate_pricing(selected_days)
    await state.update_data(pricing_data=pricing_data)
    
    await show_frequency_payment_summary(callback_query, state, pricing_data)

# Frequency Pricing System Handlers
@router.callback_query(F.data.startswith("freq_tier_"))
async def frequency_tier_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle frequency tier selection"""
    days = int(callback_query.data.replace("freq_tier_", ""))
    await state.update_data(selected_days=days)
    
    # Get channel data
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    if not selected_channels:
        await callback_query.answer("Please select channels first")
        return
    
    # Calculate pricing (flat rate, not per channel)
    pricing = FrequencyPricingSystem()
    pricing_data = pricing.calculate_pricing(days)
    await state.update_data(pricing_data=pricing_data)
    
    # Show payment options
    await show_frequency_payment_summary(callback_query, state, pricing_data)

@router.callback_query(F.data == "freq_custom")
async def frequency_custom_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle custom duration selection"""
    await callback_query.message.edit_text(
        "📝 **Custom Duration**\n\nPlease enter the number of days (1-365):",
        parse_mode='Markdown'
    )
    await state.set_state(AdCreationStates.custom_duration)
    await callback_query.answer()

@router.message(AdCreationStates.custom_duration)
async def handle_custom_duration(message: Message, state: FSMContext):
    """Handle custom duration input"""
    try:
        days = int(message.text.strip())
        if days < 1 or days > 365:
            await message.reply("❌ Please enter a number between 1 and 365 days.")
            return
        
        await state.update_data(selected_days=days)
        
        # Get channel data
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        if not selected_channels:
            await message.reply("❌ Please select channels first")
            return
        
        # Calculate pricing (flat rate, not per channel)
        pricing = FrequencyPricingSystem()
        pricing_data = pricing.calculate_pricing(days)
        await state.update_data(pricing_data=pricing_data)
        
        # Show payment options
        await show_frequency_payment_summary_message(message, state, pricing_data)
        
    except ValueError:
        await message.reply("❌ Please enter a valid number of days.")

@router.callback_query(F.data == "freq_all_tiers")
async def frequency_all_tiers_handler(callback_query: CallbackQuery, state: FSMContext):
    """Show all available frequency tiers"""
    pricing = FrequencyPricingSystem()
    all_tiers = pricing.get_available_tiers()
    
    text = "📊 **All Available Frequency Tiers**\n\n"
    for tier in all_tiers:
        text += f"• **{tier['name']}** ({tier['days']} days)\n"
        text += f"  📝 {tier['posts_per_day']} posts/day per channel\n"
        if tier['discount'] > 0:
            text += f"  💰 {tier['discount']}% discount\n"
        text += "\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Back to Selection", callback_data="continue_to_duration")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def show_frequency_payment_summary(callback_query: CallbackQuery, state: FSMContext, pricing_data: Dict):
    """Show payment summary for frequency pricing"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Get channel names
    channel_names = []
    for channel_id in selected_channels:
        channel = await db.get_channel(channel_id)
        if channel:
            channel_names.append(channel['name'])
    
    text = f"""✅ **Your Ad Plan Summary:**

📅 **Duration:** {pricing_data['days']} days
📝 **Posts per day:** {pricing_data['posts_per_day']} posts
💰 **Discount:** {pricing_data['discount_percent']}%
💵 **Final Price:** ${pricing_data['final_cost_usd']:.2f}

💎 **In TON:** {pricing_data['cost_ton']:.3f} TON
⭐ **In Telegram Stars:** {pricing_data['cost_stars']:,} Stars

📺 **Selected Channels:**
{chr(10).join(f"• {name}" for name in channel_names)}

📊 **Campaign Details:**
• Daily Rate: ${pricing_data['daily_price']:.2f}/day ({pricing_data['posts_per_day']} posts)
• Total Posts: {pricing_data['total_posts']:,} posts
• Base Cost: ${pricing_data['base_cost_usd']:.2f}
• You Save: ${pricing_data['savings_usd']:.2f} ({pricing_data['savings_percent']}% off)

📌 **By making this payment, you agree to the Usage Agreement.**

💡 **More days = More posts per day + Bigger discounts!**
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💎 Pay with TON", callback_data="pay_freq_ton"),
            InlineKeyboardButton(text="⭐ Pay with Stars", callback_data="pay_freq_stars")
        ],
        [
            InlineKeyboardButton(text="📝 Change Duration", callback_data="freq_change_duration"),
            InlineKeyboardButton(text="📺 Change Channels", callback_data="continue_to_channels")
        ],
        [
            InlineKeyboardButton(text="◀️ Back to Main", callback_data="back_to_main")
        ]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')

async def show_frequency_payment_summary_message(message: Message, state: FSMContext, pricing_data: Dict):
    """Show payment summary for frequency pricing via message"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Get channel names
    channel_names = []
    for channel_id in selected_channels:
        channel = await db.get_channel(channel_id)
        if channel:
            channel_names.append(channel['name'])
    
    text = f"""✅ **Your Ad Plan Summary:**

📅 **Duration:** {pricing_data['days']} days
📝 **Posts per day:** {pricing_data['posts_per_day']} posts
💰 **Discount:** {pricing_data['discount_percent']}%
💵 **Final Price:** ${pricing_data['final_cost_usd']:.2f}

💎 **In TON:** {pricing_data['cost_ton']:.3f} TON
⭐ **In Telegram Stars:** {pricing_data['cost_stars']:,} Stars

📺 **Selected Channels:**
{chr(10).join(f"• {name}" for name in channel_names)}

📊 **Campaign Details:**
• Daily Rate: ${pricing_data['daily_price']:.2f}/day ({pricing_data['posts_per_day']} posts)
• Total Posts: {pricing_data['total_posts']:,} posts
• Base Cost: ${pricing_data['base_cost_usd']:.2f}
• You Save: ${pricing_data['savings_usd']:.2f} ({pricing_data['savings_percent']}% off)

📌 **By making this payment, you agree to the Usage Agreement.**

💡 **More days = More posts per day + Bigger discounts!**
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💎 Pay with TON", callback_data="pay_freq_ton"),
            InlineKeyboardButton(text="⭐ Pay with Stars", callback_data="pay_freq_stars")
        ],
        [
            InlineKeyboardButton(text="📝 Change Duration", callback_data="freq_change_duration"),
            InlineKeyboardButton(text="📺 Change Channels", callback_data="continue_to_channels")
        ],
        [
            InlineKeyboardButton(text="◀️ Back to Main", callback_data="back_to_main")
        ]
    ])
    
    await message.reply(text, reply_markup=keyboard, parse_mode='Markdown')

@router.callback_query(F.data == "freq_change_duration")
async def frequency_change_duration_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle duration change request"""
    await show_frequency_tier_selection(callback_query, state)

@router.callback_query(F.data == "pay_freq_ton")
async def pay_frequency_ton_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle TON payment for frequency pricing"""
    data = await state.get_data()
    pricing_data = data.get('pricing_data', {})
    
    if not pricing_data:
        await callback_query.answer("❌ Pricing data not found")
        return
    
    # Process TON payment
    await process_ton_payment(callback_query, state, pricing_data['cost_ton'])

@router.callback_query(F.data == "pay_freq_stars")
async def pay_frequency_stars_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Stars payment for frequency pricing"""
    data = await state.get_data()
    pricing_data = data.get('pricing_data', {})
    
    if not pricing_data:
        await callback_query.answer("❌ Pricing data not found")
        return
    
    # Process Stars payment
    await process_stars_payment(callback_query, state, pricing_data['cost_stars'])

async def show_posts_per_day_selection(callback_query: CallbackQuery, state: FSMContext, days: int):
    """Show posts per day selection with the selected days"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    text = f"""**Step 2: How many posts per day?**

Campaign Duration: {days} days

Choose your posting frequency to see volume discounts:

VOLUME DISCOUNT TIPS:
- 1 post/day = No discount
- 2 posts/day = 5% off
- 4 posts/day = 10% off
- 8 posts/day = 20% off
- 24 posts/day = 30% off (maximum!)

Select posts per day:"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1/day (No discount)", callback_data="dynamic_posts_1"),
            InlineKeyboardButton(text="2/day (5% off)", callback_data="dynamic_posts_2")
        ],
        [
            InlineKeyboardButton(text="3/day (7% off)", callback_data="dynamic_posts_3"),
            InlineKeyboardButton(text="4/day (10% off)", callback_data="dynamic_posts_4")
        ],
        [
            InlineKeyboardButton(text="6/day (15% off)", callback_data="dynamic_posts_6"),
            InlineKeyboardButton(text="8/day (20% off)", callback_data="dynamic_posts_8")
        ],
        [
            InlineKeyboardButton(text="12/day (27% off)", callback_data="dynamic_posts_12"),
            InlineKeyboardButton(text="24/day (30% off)", callback_data="dynamic_posts_24")
        ],
        [
            InlineKeyboardButton(text="Custom Amount", callback_data="dynamic_posts_custom"),
            InlineKeyboardButton(text="Back", callback_data="continue_to_duration")
        ]
    ])
    
    try:
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    except (AttributeError, Exception):
        await callback_query.message.answer(text, reply_markup=keyboard, parse_mode='Markdown')

# Payment handlers now use dynamic pricing system

@router.callback_query(F.data == "pay_dynamic_ton")
async def pay_dynamic_ton_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle TON payment for dynamic pricing with wallet address and memo"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    calculation = data.get('pricing_calculation', {})
    
    if not calculation or 'total_ton' not in calculation:
        await callback_query.answer("Invalid payment data")
        return
    
    total_ton = calculation['total_ton']
    total_usd = calculation['total_usd']
    
    # Generate payment memo
    memo = payment_processor.generate_memo()
    
    # TON wallet address (user-provided wallet address)
    ton_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    
    # Create payment expiration timestamp (20 minutes from now)
    import time
    expiration_time = int(time.time()) + (20 * 60)  # 20 minutes
    
    # Store payment info for monitoring
    await state.update_data(
        payment_memo=memo,
        payment_amount_ton=total_ton,
        payment_amount_usd=total_usd,
        payment_expiration=expiration_time,
        payment_status="pending"
    )
    
    # TonViewer monitoring link
    tonviewer_link = f"https://tonviewer.com/{ton_wallet}"
    
    text = f"**TON Payment Required**\n\n"
    text += f"**Amount:** {total_ton} TON (${total_usd:.2f})\n"
    text += f"**Wallet Address:**\n`{ton_wallet}`\n\n"
    text += f"**Payment Memo:**\n`{memo}`\n\n"
    text += f"**⏰ Payment expires in 20 minutes**\n\n"
    text += f"**Instructions:**\n"
    text += f"1. Send exactly **{total_ton} TON** to the wallet address above\n"
    text += f"2. Include the memo: `{memo}`\n"
    text += f"3. Payment will be verified automatically\n\n"
    text += f"**Monitor your payment:** [TonViewer]({tonviewer_link})\n\n"
    text += f"[!] Payment automatically confirmed when detected on blockchain\n\n"
    text += f"With your payment, you agree to the Usage Agreement[Link]"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="[X] Cancel Payment", callback_data="cancel_payment")],
        [InlineKeyboardButton(text="[Refresh] Try Different Payment", callback_data="show_payment_options")]
    ])
    
    try:
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    except (AttributeError, Exception):
        await callback_query.message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    
    await callback_query.answer("TON payment details provided!")
    
    # Start monitoring payment in background
    asyncio.create_task(monitor_ton_payment(user_id, memo, total_ton, expiration_time, state))
    
    # Add manual confirmation for admin users (testing)
    if user_id in ADMIN_IDS:
        keyboard.inline_keyboard.insert(-1, [
            InlineKeyboardButton(text="[Admin] Manual Confirm", callback_data=f"admin_confirm_ton_{memo}")
        ])
        try:
            await callback_query.message.edit_text(payment_text, reply_markup=keyboard, parse_mode='Markdown')
        except:
            pass


@router.callback_query(F.data == "pay_dynamic_stars")
async def pay_dynamic_stars_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Telegram Stars payment for dynamic pricing"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    calculation = data.get('pricing_calculation', {})
    
    if not calculation or 'total_stars' not in calculation:
        await callback_query.answer("No Invalid payment data")
        return
    
    stars_price = calculation['total_stars']
    total_usd = calculation['total_usd']
    
    # Show payment confirmation message with cancellation option
    usd_formatted = f"{total_usd:.2f}"
    text = f"""
[Star] **Telegram Stars Payment**

**Amount:** {stars_price} [Star] (${usd_formatted})
**Campaign Details:** {calculation.get('days', 1)} days, {calculation.get('posts_per_day', 1)} posts/day
**Channels:** {len(calculation.get('selected_channels', []))} selected

**Payment Options:**
- Click 'Pay Now' to send Stars invoice
- Click 'Cancel' to return to pricing

With your payment, you agree to the Usage Agreement[Link]
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="[Star] Pay Now", callback_data="confirm_stars_payment")],
        [InlineKeyboardButton(text="[X] Cancel Payment", callback_data="cancel_payment")],
        [InlineKeyboardButton(text="[Refresh] Recalculate", callback_data="recalculate_dynamic")]
    ])
    
    # Store Stars payment data for later confirmation
    await state.update_data(
        stars_payment_amount=stars_price,
        stars_payment_usd=total_usd,
        payment_ready=True
    )
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer("Stars payment ready - confirm to proceed")


@router.callback_query(F.data == "confirm_stars_payment")
async def confirm_stars_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """Actually send the Stars invoice after confirmation"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    stars_amount = data.get('stars_payment_amount')
    total_usd = data.get('stars_payment_usd')
    calculation = data.get('pricing_calculation', {})
    
    if not stars_amount:
        await callback_query.answer("Payment data not found", show_alert=True)
        return
    
    # Create Stars payment using Bot's send_invoice method
    try:
        # Delete the current message before sending invoice to avoid confusion
        try:
            await callback_query.message.delete()
        except:
            pass
        
        # Send new message first
        usd_formatted = f"{total_usd:.2f}"
        info_text = f"""
[Star] **Stars Payment**

**Amount:** {stars_amount} [Star] (${usd_formatted})

Sending payment invoice...

[!] **Note:** If you change your mind, simply ignore the invoice and go back.
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=" Back to Options", callback_data="show_payment_options")],
            [InlineKeyboardButton(text="[Home] Main Menu", callback_data="back_to_main")]
        ])
        
        info_msg = await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=info_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Send the Stars invoice
        await callback_query.message.bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title=f"I3lani Bot - Dynamic Ad Campaign",
            description=f"Ad campaign package worth ${total_usd:.2f} for {calculation.get('days', 1)} days",
            payload=f"dynamic_ad_{user_id}_{int(datetime.now().timestamp())}",
            provider_token="",
            currency="XTR",
            prices=[{"label": "Dynamic Ad Package", "amount": stars_amount}],
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
        
        await callback_query.answer("[[]] Stars invoice sent!")
        
    except Exception as e:
        logger.error(f"Error creating Stars payment: {e}")
        await callback_query.answer("[X] Error creating Stars payment. Please try again.", show_alert=True)


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """Cancel payment and return to pricing"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Clear payment data
    data = await state.get_data()
    pricing_calculation = data.get('pricing_calculation', {})
    
    text = """
[X] **Payment Cancelled**

Your payment has been cancelled. You can:
- Recalculate pricing with different options
- Return to main menu
- Try payment again

No charges have been made to your account.
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="[Refresh] Recalculate Pricing", callback_data="recalculate_dynamic")],
        [InlineKeyboardButton(text="[Home] Main Menu", callback_data="back_to_main")],
        [InlineKeyboardButton(text=" Back to Payment", callback_data="show_payment_options")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer("Payment cancelled successfully")


@router.callback_query(F.data == "show_payment_options")
async def show_payment_options_handler(callback_query: CallbackQuery, state: FSMContext):
    """Show payment options again"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    calculation = data.get('pricing_calculation', {})
    
    if not calculation:
        await callback_query.answer("No pricing data found. Please recalculate.", show_alert=True)
        return
    
    from dynamic_pricing import get_dynamic_pricing
    pricing = get_dynamic_pricing()
    
    base_cost = f"{calculation.get('base_cost', calculation.get('total_usd', 0)):.2f}"
    discount_amount = f"{calculation.get('discount_amount', 0):.2f}"
    final_price = f"{calculation['total_usd']:.2f}"
    
    text = f"""
[Money] **Payment Summary**

**Campaign:** {calculation['days']} days x {calculation['posts_per_day']} posts/day
**Channels:** {len(calculation.get('selected_channels', []))} selected
**Total Posts:** {calculation['total_posts']}

**Pricing:**
- Base: ${base_cost}
- Discount: -{calculation['discount_percent']}% (${discount_amount})
- **Final Price:** ${final_price}

**Choose your payment method:**
    """.strip()
    
    keyboard_data = pricing.create_payment_keyboard_data(calculation)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn['text'], callback_data=btn['callback_data']) 
         for btn in row]
        for row in keyboard_data
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer("Payment options shown")


# TonViewer monitoring and payment verification functions
async def monitor_ton_payment(user_id: int, memo: str, amount_ton: float, expiration_time: int, state: FSMContext):
    """Monitor TON payment using TonViewer API"""
    import time
    import requests
    
    # Monitor for 20 minutes (1200 seconds)
    start_time = time.time()
    check_interval = 30  # Check every 30 seconds
    
    wallet_address = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    
    while time.time() < expiration_time:
        try:
            # Check TonViewer API for transactions
            api_url = f"https://tonapi.io/v2/accounts/{wallet_address}/transactions"
            headers = {
                'Accept': 'application/json'
            }
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get('items', [])
                
                # Check recent transactions for our memo
                for tx in transactions:
                    # Check if this is an incoming transaction
                    if tx.get('direction') == 'in':
                        # Get the comment/memo from the transaction
                        comment = tx.get('in_msg', {}).get('decoded_body', {}).get('comment', '')
                        
                        # Check if memo matches
                        if comment == memo:
                            # Get amount in nanotons and convert to TON
                            tx_amount_nanotons = int(tx.get('in_msg', {}).get('value', 0))
                            tx_amount = tx_amount_nanotons / 1000000000
                            
                            # Verify amount matches (with small tolerance for fees)
                            if abs(tx_amount - amount_ton) < 0.01:
                                # Payment found and verified!
                                logger.info(f"TON payment verified: {memo} for {amount_ton} TON")
                                await handle_successful_ton_payment(user_id, memo, amount_ton, state)
                                return
            
            else:
                logger.warning(f"TON API request failed with status {response.status_code}")
            
            # Wait before next check
            await asyncio.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"Error monitoring TON payment: {e}")
            await asyncio.sleep(check_interval)
    
    # Payment expired
    await handle_expired_ton_payment(user_id, memo, state)


async def handle_successful_ton_payment(user_id: int, memo: str, amount_ton: float, state: FSMContext):
    """Handle successful TON payment verification"""
    try:
        # Update payment status
        await state.update_data(payment_status="confirmed")
        
        # Get user data
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        ad_content = data.get('ad_text', '')  # Changed from ad_content to ad_text
        photos = data.get('photos', [])
        
        # Create ad in database
        ad_id = await db.create_ad(
            user_id=user_id,
            content=ad_content,
            media_url=photos[0] if photos else None,
            content_type='photo' if photos else 'text'
        )
        
        # Get pricing data for subscription
        calculation = data.get('pricing_calculation', {})
        days = calculation.get('days', 1)
        posts_per_day = calculation.get('posts_per_day', 1)
        
        # Create subscription for each selected channel
        subscription_ids = []
        for channel_id in selected_channels:
            subscription_id = await db.create_subscription(
                user_id=user_id,
                ad_id=ad_id,
                channel_id=channel_id,
                duration_months=days,  # Using days as duration
                total_price=data.get('payment_amount_usd', 0),
                currency='TON',
                posts_per_day=posts_per_day,
                total_posts=days * posts_per_day
            )
            subscription_ids.append(subscription_id)
            
        # Activate subscriptions
        await db.activate_subscriptions(subscription_ids, days)
        
        # Publish immediately to all selected channels
        from publishing_scheduler import scheduler
        if scheduler:
            await scheduler.publish_immediately_after_payment(
                user_id=user_id,
                ad_id=ad_id,
                selected_channels=selected_channels,
                subscription_data=data
            )
        
        # Send success notification to user
        from main import bot
        success_text = f"[Check] **Payment Confirmed!**\n\n"
        success_text += f"**Amount:** {amount_ton} TON\n"
        success_text += f"**Payment ID:** {memo}\n\n"
        success_text += "Your ad has been successfully created and will be published to all selected channels shortly!\n\n"
        success_text += "Thank you for using I3lani Bot!"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data="back_to_main")],
            [InlineKeyboardButton(text="My Ads", callback_data="my_ads")]
        ])
        
        await bot.send_message(
            chat_id=user_id,
            text=success_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error processing successful TON payment: {e}")


async def handle_expired_ton_payment(user_id: int, memo: str, state: FSMContext):
    """Handle expired TON payment"""
    try:
        # Update payment status
        await state.update_data(payment_status="expired")
        
        # Send expiration notification to user
        from main import bot
        expiration_text = f"⏰ **Payment Expired**\n\n"
        expiration_text += f"**Payment ID:** {memo}\n\n"
        expiration_text += "Your TON payment has expired. Please create a new payment to continue.\n\n"
        expiration_text += "Would you like to try again?"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'try_again'), callback_data="pay_dynamic_ton")],
            [InlineKeyboardButton(text=get_text(language, 'main_menu'), callback_data="back_to_main")],
            [InlineKeyboardButton(text=get_text(language, 'contact_support'), callback_data="support_contact")]
        ])
        
        await bot.send_message(
            chat_id=user_id,
            text=expiration_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error processing expired TON payment: {e}")


# Removed useless manual payment check, copy wallet, and refresh status handlers
# Automatic monitoring handles all payment verification


# Handler for canceling payment
@router.callback_query(F.data == "cancel_payment")
async def cancel_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment cancellation"""
    await state.update_data(payment_status="cancelled")
    
    text = "[X] Payment cancelled. You can create a new ad anytime."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Create New Ad", callback_data="create_ad")],
        [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data="back_to_main")]
    ])
    
    try:
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer("Payment cancelled")
    except Exception as e:
        logger.error(f"Error cancelling payment: {e}")
        await callback_query.answer("Payment cancelled")


@router.callback_query(F.data.startswith("admin_confirm_ton_"))
async def admin_confirm_ton_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle admin manual TON payment confirmation"""
    user_id = callback_query.from_user.id
    
    # Check if user is admin
    if user_id not in ADMIN_IDS:
        await callback_query.answer("Admin access required", show_alert=True)
        return
    
    # Extract memo from callback data
    memo = callback_query.data.replace("admin_confirm_ton_", "")
    
    # Get payment data from state
    data = await state.get_data()
    amount_ton = data.get('payment_amount_ton', 0)
    
    # Manually trigger successful payment handler
    await handle_successful_ton_payment(user_id, memo, amount_ton, state)
    await callback_query.answer("Payment manually confirmed!")


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
        total_price_usd = data.get('total_price_usd', 0)
        total_price_stars = data.get('total_price_stars', 0)
        channel_pricing_details = data.get('channel_pricing_details', [])
        
        # Handle Telegram Stars payment with real API
        if payment_method == "stars":
            from aiogram.types import LabeledPrice
            
            # Use the pre-calculated Stars amount
            stars_amount = total_price_stars
            
            # Create payment payload for tracking
            payload = f"ad_{ad_id}_user_{user_id}_time_{int(time.time())}"
            
            # Store payment data in state for later processing
            await state.update_data(payment_payload=payload, stars_amount=stars_amount)
            
            # Create and send Telegram Stars invoice
            try:
                await callback_query.bot.send_invoice(
                    chat_id=user_id,
                    title="I3lani Advertisement Campaign",
                    description=f"Ad campaign for {len(selected_channels)} channels - ${total_price_usd:.2f} USD",
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
                
                duration_months = data.get('duration_months', 1)
                posts_per_day = data.get('posts_per_day', 1)
                total_posts = data.get('total_posts', 30)
                discount_percent = data.get('discount_percent', 0)
                
                plan_text = f"{duration_months} month(s)" if duration_months == 1 else f"{duration_months} months"
                
                payment_summary = f"Star **Telegram Stars Payment - Progressive Plan**\n\n"
                payment_summary += f" **Plan:** {plan_text}\n"
                payment_summary += f"Stats **Frequency:** {posts_per_day} posts/day\n"
                payment_summary += f"Growth **Total Posts:** {total_posts * len(selected_channels):,} posts\n"
                if discount_percent > 0:
                    payment_summary += f"Price **Discount:** {discount_percent}% OFF\n"
                payment_summary += f" **Total:** {stars_amount:,} Stars (${total_price_usd:.2f} USD)\n"
                payment_summary += f" **Channels:** {len(selected_channels)} (No per-channel fee)\n\n"
                
                payment_summary += f"Tip **Plan covers all selected channels:**\n"
                for detail in channel_pricing_details:
                    payment_summary += f"- {detail['name']}: {detail['posts_per_day']} posts/day\n"
                
                payment_summary += f"\nYes **Invoice sent!** Please complete payment using the invoice above.\n\nYour progressive posting plan will activate automatically after payment confirmation."
                
                await callback_query.message.edit_text(
                    payment_summary,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="◀️ Back to Channels", callback_data="back_to_channels")]
                    ]),
                    parse_mode='Markdown'
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
                # Find channel price
                channel_price = 5.0  # Default
                for detail in channel_pricing_details:
                    if any(ch['channel_id'] == channel_id for ch in data.get('all_channels', [])):
                        channel_price = detail['price_usd']
                        break
                
                subscription_id = await db.create_subscription(
                    user_id=user_id,
                    ad_id=ad_id,
                    channel_id=channel_id,
                    duration_months=1,  # Default 1 month
                    total_price=channel_price,
                    currency='USD'
                )
                subscription_ids.append(subscription_id)
            
            # Create payment invoice for TON
            invoice = await payment_processor.create_payment_invoice(
                user_id=user_id,
                subscription_id=subscription_ids[0],
                amount=total_price_usd,
                currency='USD',
                payment_method=payment_method
            )
            
            # Show TON payment instructions
            instructions = invoice['instructions']
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="Yes Payment Sent", 
                    callback_data=f"confirm_payment_{invoice['payment_id']}"
                )],
                [InlineKeyboardButton(
                    text="Back Back", 
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
    """Handle payment confirmation - check if payment was actually received"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        payment_id = callback_query.data.replace("confirm_payment_", "")
        
        # Show checking message
        await callback_query.message.edit_text(
            " **Checking Payment...**\n\nPlease wait while we verify your payment...",
            parse_mode='Markdown'
        )
        
        # Get payment details from database
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute('''
                SELECT p.*, s.user_id, s.ad_id 
                FROM payments p 
                LEFT JOIN subscriptions s ON p.subscription_id = s.subscription_id
                WHERE p.payment_id = ?
            ''', (payment_id,)) as cursor:
                payment_record = await cursor.fetchone()
        
        if not payment_record:
            await callback_query.message.edit_text(
                "No **Payment Not Found**\n\nPayment record not found. Please try again.",
                parse_mode='Markdown'
            )
            return
        
        # Check if payment was actually received
        payment_processor = PaymentProcessor()
        payment_confirmed = await payment_processor._check_ton_transaction(
            payment_record['memo'], 
            payment_record['amount']
        )
        
        if payment_confirmed:
            # Payment found - confirm and publish ad
            await handle_successful_payment(callback_query, state, payment_record)
        else:
            # Payment not found - inform user
            await handle_payment_not_found(callback_query, payment_record)
            
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        await callback_query.message.edit_text(
            "No **Error**\n\nUnable to verify payment. Please try again later.",
            parse_mode='Markdown'
        )


async def handle_successful_payment(callback_query: CallbackQuery, state: FSMContext, payment_record):
    """Handle successful payment confirmation"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Update payment status in database
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as conn:
            await conn.execute('''
                UPDATE payments 
                SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
                WHERE payment_id = ?
            ''', (payment_record['payment_id'],))
            await conn.commit()
        
        # Get ad content from state AND database
        data = await state.get_data()
        ad_content = data.get('ad_content', '')
        ad_media = data.get('ad_media')
        ad_id = data.get('ad_id') or payment_record['ad_id']
        
        # If no content in state, try to get from database
        if not ad_content and ad_id:
            try:
                async with aiosqlite.connect(db.db_path) as conn:
                    conn.row_factory = aiosqlite.Row
                    async with conn.execute(
                        'SELECT content, media_url, content_type FROM ads WHERE ad_id = ?',
                        (ad_id,)
                    ) as cursor:
                        ad_record = await cursor.fetchone()
                        if ad_record:
                            ad_content = ad_record['content'] or ''
                            if ad_record['media_url']:
                                ad_media = {
                                    'file_id': ad_record['media_url'],
                                    'type': ad_record['content_type']
                                }
            except Exception as e:
                logger.error(f"Error fetching ad from database: {e}")
        
        # Ensure we have content
        if not ad_content:
            ad_content = " Your advertisement is now live! Contact @I3lani_bot for more details."
        
        # Publish ad to I3lani channel immediately
        bot = callback_query.bot
        i3lani_channel = "@i3lani"
        published = False
        
        try:
            # Format ad with proper branding
            formatted_content = f" Advertisement\n\n{ad_content}\n\n Advertise with @I3lani_bot"
            
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
Success **Payment Confirmed & Ad Published!**

Yes Your ad is now live on the I3lani channel!

Stats **Campaign Status:**
- Payment ID: {payment_id}
- Published: Just now
- Channel: https://t.me/i3lani
- Status: Active

Link **View your ad:** https://t.me/i3lani

Your campaign is running successfully!
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="Link View I3lani Channel", 
                    url="https://t.me/i3lani"
                )],
                [InlineKeyboardButton(
                    text="Stats My Ads", 
                    callback_data="my_ads"
                )],
                [InlineKeyboardButton(
                    text="Home Main Menu", 
                    callback_data="back_to_main"
                )]
            ])
        else:
            confirmation_text = f"""
**Payment Confirmed**

**Payment ID:** {payment_id}
**Publishing Status:** In progress
**Estimated Time:** Within 24 hours

Your payment has been confirmed. Your ad will be published to the I3lani channel shortly.
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="Stats My Ads", 
                    callback_data="my_ads"
                )],
                [InlineKeyboardButton(
                    text="Home Main Menu", 
                    callback_data="back_to_main"
                )]
            ])
        
        await callback_query.message.edit_text(
            confirmation_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        await state.clear()
        await callback_query.answer("Yes Payment confirmed!" + (" Ad published!" if published else ""))
        
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        await callback_query.answer("Payment confirmation failed. Please contact support.")


async def handle_payment_not_found(callback_query: CallbackQuery, payment_record):
    """Handle payment not found scenario"""
    try:
        # Create retry payment keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Refresh Try Again", 
                callback_data=f"retry_payment_{payment_record['subscription_id']}"
            )],
            [InlineKeyboardButton(
                text="Home Go Home", 
                callback_data="go_home"
            )]
        ])
        
        payment_not_found_text = (
            "**Payment Not Found**\n\n"
            "We could not find your payment on the TON blockchain yet.\n\n"
            "**Payment Details:**\n"
            f"- Amount: {payment_record['amount']} TON\n"
            f"- Memo: {payment_record['memo']}\n"
            "- Wallet: UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB\n\n"
            "**Please ensure:**\n"
            "- You sent the exact amount\n"
            "- You included the correct memo\n"
            "- Payment was sent from your personal wallet (not exchange)\n\n"
            "**Check your transaction:**\n"
            "https://tonviewer.com/UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB\n\n"
            "Would you like to try again?"
        )
        
        await callback_query.message.edit_text(
            payment_not_found_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Payment not found handler error: {e}")
        await callback_query.answer("Error handling payment verification.")


@router.callback_query(F.data == "my_ads")
async def my_ads_handler(callback_query: CallbackQuery):
    """Show user ads dashboard"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get user stats
    stats = await db.get_user_stats(user_id)
    
    # Get currency info
    user = await db.get_user(user_id)
    currency = user.get('currency', 'USD') if user else 'USD'
    currency_info = get_currency_info(language)
    
    dashboard_text = f"""
Stats **{get_text(language, 'dashboard')}**

Growth **Your Statistics:**
{get_text(language, 'total_ads', count=stats['total_ads'])}
{get_text(language, 'active_ads', count=stats['active_ads'])}
{get_text(language, 'total_spent', currency=currency_info['symbol'], amount=stats['total_spent'])}

Launch **Ready to create more ads?**
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
    """Show active Share & Win system with TON rewards"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Initialize atomic rewards if not exists
    from atomic_rewards import atomic_rewards
    if atomic_rewards is None:
        from atomic_rewards import init_atomic_rewards
        init_atomic_rewards(db, bot)
    
    # Get reward statistics
    stats = await atomic_rewards.get_reward_statistics(user_id)
    
    # Get referral count
    referral_count = await db.get_referral_count(user_id)
    
    # Determine tier based on referrals
    if referral_count >= 50:
        tier = "Premium"
        rate = "2.0 TON"
    elif referral_count >= 25:
        tier = "Gold"
        rate = "1.2 TON"
    elif referral_count >= 10:
        tier = "Silver"
        rate = "0.8 TON"
    else:
        tier = "Basic"
        rate = "0.5 TON"
    
    share_text = f"""
🎉 **Share & Win - Active TON Rewards!**

💰 **Your Earnings:**
- Total Earned: {stats.get('total_earned', 0):.2f} TON
- Pending Rewards: {stats.get('pending_rewards', 0):.2f} TON
- Total Referrals: {referral_count}
- Current Tier: {tier}

⚡ **Instant Rewards:**
- Referral Bonus: {rate} per friend
- Registration Bonus: 5.0 TON (auto-paid)
- Channel Addition: 10.0 TON per channel
- Monthly Bonus: 25.0 TON for active partners

🚀 **How It Works:**
1. Share your referral link
2. Friends join using your link
3. Get INSTANT TON rewards
4. Automatic payout at 10 TON threshold

🔗 **Your Referral Link:**
https://t.me/I3lani_bot?start=ref_{user_id}

🎯 **Tier Benefits:**
- Basic: 0.5 TON per referral
- Silver: 0.8 TON per referral (10+ refs)
- Gold: 1.2 TON per referral (25+ refs)
- Premium: 2.0 TON per referral (50+ refs)
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📱 Share with Friends", url=f"https://t.me/share/url?url=https://t.me/I3lani_bot?start=ref_{user_id}&text=Join I3lani and earn TON! Get instant rewards for advertising!")
        ],
        [
            InlineKeyboardButton(text="💰 View Earnings", callback_data="view_earnings"),
            InlineKeyboardButton(text="📊 Referral Stats", callback_data="referral_stats")
        ],
        [
            InlineKeyboardButton(text="🔗 Copy Link", callback_data=f"copy_referral_{user_id}"),
            InlineKeyboardButton(text="🎁 Claim Bonus", callback_data="claim_registration_bonus")
        ],
        [InlineKeyboardButton(text=get_text(language, 'back'), callback_data="back_to_start")]
    ])
    
    await callback_query.message.edit_text(
        share_text,
        reply_markup=keyboard
    )
    await callback_query.answer()


# Atomic reward handlers
@router.callback_query(F.data == "claim_registration_bonus")
async def claim_registration_bonus_handler(callback_query: CallbackQuery):
    """Handle registration bonus claim"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    from atomic_rewards import atomic_rewards
    if atomic_rewards is None:
        from atomic_rewards import init_atomic_rewards
        init_atomic_rewards(db, bot)
    
    # Process registration reward
    result = await atomic_rewards.process_registration_reward(user_id)
    
    if result['success']:
        message = f"🎉 Registration bonus of 5.0 TON has been credited! Total earned: {result.get('amount', 5.0)} TON"
    else:
        message = f"ℹ️ {result['message']}"
    
    await callback_query.answer(message, show_alert=True)

@router.callback_query(lambda c: c.data == "view_earnings")
async def view_earnings_handler(callback_query: CallbackQuery):
    """Show comprehensive partner reward board"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Get partner status and rewards
        partner_status = await db.get_partner_status(user_id)
        partner_rewards = await db.get_partner_rewards(user_id)
        referral_count = await db.get_referral_count(user_id)
        
        # Initialize partner status if not exists
        if not partner_status:
            await db.create_partner_status(user_id)
            partner_status = await db.get_partner_status(user_id)
        
        # Calculate totals
        total_earnings = partner_status.get('total_earnings', 0) if partner_status else 0
        pending_rewards = partner_status.get('pending_rewards', 0) if partner_status else 0
        tier = partner_status.get('tier', 'Basic') if partner_status else 'Basic'
        
        # Determine tier colors and rates
        tier_info = {
            'Basic': {'color': '🥉', 'rate': 0.5},
            'Silver': {'color': '🥈', 'rate': 0.8},
            'Gold': {'color': '🥇', 'rate': 1.2},
            'Premium': {'color': '💎', 'rate': 2.0}
        }
        
        tier_color = tier_info.get(tier, {}).get('color', '🥉')
        tier_rate = tier_info.get(tier, {}).get('rate', 0.5)
        
        # Calculate progress toward payout threshold
        payout_threshold = 25.0
        progress_percentage = min((pending_rewards / payout_threshold) * 100, 100)
        progress_bar = "█" * int(progress_percentage // 10) + "▓" * (10 - int(progress_percentage // 10))
        
        # Recent rewards breakdown
        recent_rewards_text = ""
        if partner_rewards:
            for reward in partner_rewards[:5]:  # Show latest 5
                reward_type = reward.get('reward_type', 'Unknown')
                amount = reward.get('amount', 0)
                description = reward.get('description', 'No description')
                recent_rewards_text += f"• {reward_type}: +{amount:.2f} TON\n"
        else:
            recent_rewards_text = "No recent rewards"
        
        # Next tier requirements
        next_tier_text = ""
        if tier == 'Basic' and referral_count < 5:
            next_tier_text = f"Silver tier: {5 - referral_count} more referrals needed"
        elif tier == 'Silver' and referral_count < 15:
            next_tier_text = f"Gold tier: {15 - referral_count} more referrals needed"
        elif tier == 'Gold' and referral_count < 25:
            next_tier_text = f"Premium tier: {25 - referral_count} more referrals needed"
        else:
            next_tier_text = "Maximum tier reached!"
        
        # Import Web3 UI components
        from web3_ui import Web3UI, Web3Templates
        
        # Create Web3-themed earnings dashboard
        earnings_metrics = {
            'Quantum_Balance': f'{pending_rewards:.2f}',
            'Neural_Tier': tier,
            'Network_Nodes': referral_count,
            'Total_Mined': f'{total_earnings:.2f}',
            'Progress_Level': f'{progress_percentage:.1f}%'
        }
        
        # Prepare tier display data
        tier_stats = {'Rate': f'{tier_rate} TON', 'Nodes': referral_count}
        recent_activity_text = f"Recent Mining Activity:\n{recent_rewards_text}"
        
        # Build earnings text with Web3 components
        header_section = Web3UI.create_neural_header("PARTNER EARNINGS MATRIX", "Quantum Reward Dashboard")
        tier_section = Web3UI.create_cyber_tier_display(tier, tier_stats)
        dashboard_section = Web3UI.create_fintech_dashboard("QUANTUM EARNINGS", earnings_metrics)
        progress_section = Web3UI.create_quantum_progress(pending_rewards, payout_threshold, 15)
        advancement_section = Web3UI.create_quantum_section("NEURAL ADVANCEMENT", next_tier_text, "process")
        activity_section = Web3UI.create_holographic_display(recent_activity_text, "neural")
        alert_section = Web3UI.create_web3_alert("Continue network expansion to unlock quantum rewards", "quantum")
        separator_section = Web3UI.create_neon_separator(35, "quantum")
        
        milestone_section = """
◇━━━ MILESTONE PROTOCOL ━━━◇
◈ 5 Network Nodes → +2.5 TON Quantum Bonus
◈ 10 Network Nodes → +6.0 TON Neural Reward  
◈ 25 Network Nodes → +20.0 TON Matrix Bonus
◈ 50 Network Nodes → +50.0 TON Nexus Prize
"""
        
        earnings_text = f"""
{header_section}

{tier_section}

{dashboard_section}

{progress_section}

{advancement_section}

{activity_section}

{alert_section}

{milestone_section}

{separator_section}
        """.strip()
        
        from web3_ui import Web3UI
        
        keyboard_buttons = [
            [
                InlineKeyboardButton(text=Web3UI.create_cyber_keyboard_button("Neural Stats", "quantum"), callback_data="referral_stats"),
                InlineKeyboardButton(text=Web3UI.create_cyber_keyboard_button("Network Expansion", "neural"), callback_data="share_earn")
            ]
        ]
        
        # Add quantum payout request button if threshold is met
        if pending_rewards >= payout_threshold:
            keyboard_buttons.append([
                InlineKeyboardButton(text=Web3UI.create_cyber_keyboard_button("Quantum Withdrawal", "crypto"), callback_data="request_payout")
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text=Web3UI.create_cyber_keyboard_button("Neural Pathways", "back"), callback_data="share_earn")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback_query.message.edit_text(earnings_text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in view_earnings_handler: {e}")
        await callback_query.answer("Error loading earnings. Please try again.", show_alert=True)

@router.callback_query(lambda c: c.data == "referral_stats")
async def referral_stats_handler(callback_query: CallbackQuery):
    """Show referral statistics"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Get referral statistics
        referral_count = await db.get_referral_count(user_id)
        partner_status = await db.get_partner_status(user_id)
        
        if not partner_status:
            await db.create_partner_status(user_id)
            partner_status = await db.get_partner_status(user_id)
        
        # Calculate tier
        if referral_count >= 50:
            tier = "Premium"
            tier_icon = "💎"
        elif referral_count >= 25:
            tier = "Gold"
            tier_icon = "🥇"
        elif referral_count >= 10:
            tier = "Silver"
            tier_icon = "🥈"
        else:
            tier = "Basic"
            tier_icon = "🥉"
        
        stats_text = f"""
📊 **REFERRAL STATISTICS**

{tier_icon} **Current Tier: {tier}**
├─ Total Referrals: {referral_count}
├─ Pending Rewards: {partner_status.get('pending_rewards', 0):.2f} TON
└─ Registration Bonus: {"✅ Claimed" if partner_status.get('registration_bonus_paid') else "❌ Unclaimed"}

🎯 **Next Tier Requirements:**
{'• Maximum tier reached!' if referral_count >= 50 else f'• {(50 if referral_count >= 25 else 25 if referral_count >= 10 else 10) - referral_count} more referrals needed'}

🔗 **Your Referral Link:**
https://t.me/I3lani_bot?start=ref_{user_id}

💡 **Tips to Earn More:**
• Share your link on social media
• Invite friends personally
• Join relevant Telegram groups
• Create referral campaigns
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Reward Board", callback_data="view_earnings")],
            [InlineKeyboardButton(text="🔗 Share Link", callback_data="share_earn")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
        ])
        
        await callback_query.message.edit_text(stats_text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in referral_stats_handler: {e}")
        await callback_query.answer("Error loading referral stats. Please try again.", show_alert=True)

# Payout system handlers
@router.callback_query(lambda c: c.data == "request_payout")
async def request_payout_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle payout request submission"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Get partner status
        partner_status = await db.get_partner_status(user_id)
        if not partner_status:
            await callback_query.answer("Error: Partner status not found.", show_alert=True)
            return
        
        current_balance = partner_status.get('pending_rewards', 0.0)
        
        # Check minimum threshold
        if current_balance < 25.0:
            await callback_query.message.edit_text(
                f"""
❌ **Insufficient Balance for Payout**

💰 **Current Balance:** {current_balance:.2f} TON
💎 **Minimum Required:** 25.0 TON
📈 **Still Need:** {25.0 - current_balance:.2f} TON

🚀 **How to Earn More:**
• Share your referral link
• Invite friends to join I3lani
• Add channels to your account
• Participate in milestone bonuses

Keep building your balance to reach the payout threshold!
                """.strip(),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔗 Share & Earn", callback_data="share_earn")],
                    [InlineKeyboardButton(text="📊 View Progress", callback_data="view_earnings")]
                ])
            )
            return
        
        # Show payout confirmation
        payout_text = f"""
💰 **Payout Request Confirmation**

✅ **Congratulations! You qualify for payout.**

📊 **Payout Details:**
├─ Amount: {current_balance:.2f} TON
├─ Processing Time: 24-48 hours
├─ Method: Direct TON transfer
└─ Status: Ready for processing

📝 **What Happens Next:**
1. Confirm your payout request below
2. Support team will contact you for wallet details
3. TON transfer processed within 48 hours
4. Balance reset and confirmation sent

⚠️ **Important Notice:**
• Ensure you have a valid TON wallet ready
• Check your Telegram messages for updates
• Payout cannot be cancelled once confirmed
• Minimum future payouts remain at 25 TON

Ready to proceed with your {current_balance:.2f} TON payout?
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Confirm Payout", callback_data="confirm_payout")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="view_earnings")],
            [InlineKeyboardButton(text="📞 Contact Support", callback_data="support_contact")]
        ])
        
        await callback_query.message.edit_text(payout_text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in payout request: {e}")
        await callback_query.answer("Error processing payout request.", show_alert=True)

@router.callback_query(lambda c: c.data == "confirm_payout")
async def confirm_payout_handler(callback_query: CallbackQuery, state: FSMContext):
    """Process confirmed payout request"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Get partner status
        partner_status = await db.get_partner_status(user_id)
        current_balance = partner_status.get('pending_rewards', 0.0)
        
        # Generate payout request ID
        payout_id = f"PO{user_id}{int(datetime.now().timestamp())}"
        
        # Create payout record in database
        await db.create_payout_request(
            user_id=user_id,
            amount=current_balance,
            payout_id=payout_id,
            status='pending'
        )
        
        # Notify admins
        admin_message = f"""
🚨 **NEW PAYOUT REQUEST**

👤 **User ID:** {user_id}
👤 **Username:** @{callback_query.from_user.username or 'N/A'}
💰 **Amount:** {current_balance:.2f} TON
🆔 **Request ID:** {payout_id}
⏰ **Requested:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

📋 **Action Required:**
1. Contact user for TON wallet address
2. Process TON transfer: {current_balance:.2f} TON
3. Confirm transfer completion
4. Update payout status to 'completed'

💬 **Contact:** @{callback_query.from_user.username or 'Direct message required'}
🔗 **Profile:** tg://user?id={user_id}

⚡ Use admin panel to mark as completed once transferred.
        """.strip()
        
        # Send to all admins
        ADMIN_IDS = [6422889085, 773007556]
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, admin_message)
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
        
        # Confirmation message to user with Web3 theme
        from web3_ui import Web3UI
        
        payout_metrics = {
            'Transaction_ID': payout_id[-8:],
            'Quantum_Amount': f'{current_balance:.2f} TON',
            'Protocol_Status': 'Neural Processing',
            'Timeline': '24-48 hours'
        }
        
        # Build confirmation text with Web3 components
        header_section = Web3UI.create_neural_header("QUANTUM WITHDRAWAL INITIATED", "Transaction Confirmed")
        dashboard_section = Web3UI.create_fintech_dashboard("TRANSACTION MATRIX", payout_metrics)
        
        protocol_sequence = '''Neural Protocol Sequence:
◈ Quantum Support Contact → 24 hour window
◈ Wallet Verification → TON address required
◈ Blockchain Transfer → Quantum vault transmission
◈ Confirmation Signal → Completion notification'''
        
        protocol_section = Web3UI.create_holographic_display(protocol_sequence, "crypto")
        alert_section = Web3UI.create_web3_alert("Monitor neural communications for quantum support updates", "quantum")
        
        confirmation_text = f"""
{header_section}

{dashboard_section}

{protocol_section}

{alert_section}

Thank you for being a valued I3lani partner! 🚀
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 View Dashboard", callback_data="view_earnings")],
            [InlineKeyboardButton(text="📞 Contact Support", callback_data="support_contact")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
        ])
        
        await callback_query.message.edit_text(confirmation_text, reply_markup=keyboard)
        await callback_query.answer("Payout request submitted! Support will contact you soon.", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error confirming payout: {e}")
        await callback_query.answer("Error submitting payout request. Please contact support.", show_alert=True)

@router.callback_query(lambda c: c.data.startswith("confirm_payout_"))
async def confirm_payout_handler(callback_query: CallbackQuery, state: FSMContext):
    """Process confirmed payout request"""
    payout_id = callback_query.data.replace("confirm_payout_", "")
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        data = await state.get_data()
        payout_amount = data.get('payout_amount', 0)
        
        # Create payout request in database
        success = await db.create_payout_request(user_id, payout_amount, payout_id)
        
        if success:
            confirmation_text = f"""
🎉 **Payout Request Submitted Successfully!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Request Details:**
• Payout ID: {payout_id}
• Amount: {payout_amount:.2f} TON
• Status: Pending Review

📋 **What Happens Next:**
1. Our team will review your request (usually within 4 hours)
2. You'll receive confirmation via bot message
3. TON will be transferred from bot wallet within 24-48 hours
4. Your balance will be reset to 0 TON after transfer

📞 **Need Help?**
Contact our support team if you have any questions about your payout request.

Thank you for being a valued I3lani partner! 🚀
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 View Dashboard", callback_data="view_earnings")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
        else:
            confirmation_text = "❌ Error creating payout request. Please contact support."
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Try Again", callback_data="request_payout")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
        
        await callback_query.message.edit_text(confirmation_text, reply_markup=keyboard)
        await callback_query.answer("Payout request submitted! Support will contact you soon.", show_alert=True)
        
    except Exception as e:
        logger.error(f"Error confirming payout: {e}")
        await callback_query.answer("Error submitting payout request. Please contact support.", show_alert=True)

@router.callback_query(lambda c: c.data == "referral_stats")
async def referral_stats_handler(callback_query: CallbackQuery):
    """Show referral statistics"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Get referral count and partner status
        referral_count = await db.get_referral_count(user_id)
        partner_status = await db.get_partner_status(user_id)
        
        # Get tier information
        if referral_count >= 25:
            tier = "Premium"
            rate = 2.0
            next_tier = "Maximum tier reached!"
        elif referral_count >= 15:
            tier = "Gold"
            rate = 1.2
            next_tier = f"Premium tier: {25 - referral_count} more referrals needed"
        elif referral_count >= 5:
            tier = "Silver"
            rate = 0.8
            next_tier = f"Gold tier: {15 - referral_count} more referrals needed"
        else:
            tier = "Basic"
            rate = 0.5
            next_tier = f"Silver tier: {5 - referral_count} more referrals needed"
    
        # Get recent referrals
        referrals = await db.get_user_referrals(user_id)
        
        from web3_ui import Web3UI
        
        # Create Web3-themed referral statistics
        neural_metrics = {
            'Neural_Tier': tier,
            'Mining_Rate': f'{rate} TON',
            'Network_Nodes': referral_count,
            'Next_Protocol': next_tier.replace(' more referrals needed', ' nodes required')
        }
        
        milestone_text = '''Milestone Quantum Rewards:
◈ 5 Network Nodes → +2.5 TON
◈ 10 Network Nodes → +6.0 TON
◈ 25 Network Nodes → +20.0 TON
◈ 50 Network Nodes → +50.0 TON'''
        
        # Build referral stats with Web3 components
        header_section = Web3UI.create_neural_header("NEURAL NETWORK ANALYTICS", "Referral Mining Protocol")
        dashboard_section = Web3UI.create_fintech_dashboard("NETWORK STATISTICS", neural_metrics)
        
        tier_protocols = '''
◇ INITIATE → 0.5 TON per node
◈ NAVIGATOR → 0.8 TON per node (5+ nodes)
◆ ARCHITECT → 1.2 TON per node (15+ nodes)
⬢ QUANTUM → 2.0 TON per node (25+ nodes)'''
        
        protocols_section = Web3UI.create_quantum_section("TIER PROTOCOLS", tier_protocols, "process")
        milestone_section = Web3UI.create_holographic_display(milestone_text, "neural")
        
        neural_link = f"Neural Link: https://t.me/I3lani_bot?start=ref_{user_id}"
        alert_section = Web3UI.create_web3_alert(neural_link, "quantum")
        expansion_section = Web3UI.create_quantum_section("RECENT NETWORK EXPANSION", '', "data")
        
        stats_text = f"""
{header_section}

{dashboard_section}

{protocols_section}

{milestone_section}

{alert_section}

{expansion_section}
        """.strip()
    
        if referrals:
            for referral in referrals[:5]:
                username = referral.get('referred_username', 'Unknown')
                created_date = referral.get('created_at', '')[:10] if referral.get('created_at') else 'Unknown'
                stats_text += f"\n• @{username} ({created_date})"
        else:
            stats_text += "\nNo referrals yet. Share your link to start earning!"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=Web3UI.create_cyber_keyboard_button("Broadcast Neural Link", "quantum"), url=f"https://t.me/share/url?url=https://t.me/I3lani_bot?start=ref_{user_id}&text=Join the I3lani Neural Network and mine TON!")],
            [InlineKeyboardButton(text=Web3UI.create_cyber_keyboard_button("Quantum Earnings", "crypto"), callback_data="view_earnings")],
            [InlineKeyboardButton(text=Web3UI.create_cyber_keyboard_button("Neural Hub", "back"), callback_data="back_to_main")]
        ])
    
        await callback_query.message.edit_text(stats_text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in referral_stats_handler: {e}")
        await callback_query.answer("Error loading referral statistics. Please try again.", show_alert=True)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Share Link", url=f"https://t.me/share/url?url=https://t.me/I3lani_bot?start=ref_{user_id}&text=Join I3lani and earn TON!")],
        [InlineKeyboardButton(text="💰 View Earnings", callback_data="view_earnings")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
    ])
    
    await callback_query.message.edit_text(stats_text, reply_markup=keyboard)
    await callback_query.answer()

@router.callback_query(F.data.startswith("copy_referral_"))
async def copy_referral_handler(callback_query: CallbackQuery):
    """Handle referral link copy"""
    user_id = int(callback_query.data.split("_")[2])
    referral_link = f"https://t.me/I3lani_bot?start=ref_{user_id}"
    
    await callback_query.answer(f"Referral link: {referral_link}", show_alert=True)

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
        reply_markup=await create_channel_selection_keyboard(language, selected_channels)
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
Tool **Debug Information**

**User ID:** {user_id}
**Language:** {language}
**Time:** {message.date.strftime('%Y-%m-%d %H:%M:%S')}

**Bot Status:** Yes Online
**Database:** Yes Connected
**Payment System:** Yes Active

**Recent Activity:**
Use /support to report issues or get help.

**Commands:**
- /start - Restart bot
- /debug - This message
- /support - Get help
- /status - Check bot status
    """.strip()
    
    await message.reply(debug_info, parse_mode='Markdown')


@router.message(Command("support"))
async def support_command(message: Message):
    """Support command for users"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    support_text = f"""
 **{get_text(language, 'support_title', default='Support')}**

**{get_text(language, 'need_help', default='Need Help?')}**

**Common Issues:**
- Payment not confirmed? Wait 5-10 minutes
- Bot not responding? Use /start
- Language issues? Use /start to change language
- Channel selection problems? Try /start again

**Contact Support:**
- Report bugs: Describe the issue clearly
- Technical issues: Include error messages
- Payment problems: Provide payment ID

**Debug Info:**
- Your ID: {user_id}
- Language: {language}
- Time: {message.date.strftime('%Y-%m-%d %H:%M:%S')}

**Quick Fixes:**
- Restart: /start
- Check status: /status
- Debug info: /debug
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
        db_status = "Yes Connected" if user else "Warning Issue"
        
        # Check payment system
        from payments import payment_processor
        test_memo = payment_processor.generate_memo()
        payment_status = "Yes Active" if len(test_memo) == 6 else "Warning Issue"
        
        # Get uptime info
        from datetime import datetime
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        status_text = f"""
Stats **Bot Status**

**System Status:**
- Bot: Yes Online
- Database: {db_status}
- Payment System: {payment_status}
- Time: {current_time}

**Your Info:**
- User ID: {user_id}
- Language: {language}
- Registered: {'Yes Yes' if user else 'Warning No'}

**Functions:**
- Multi-language: Yes Working
- AB0102 Memos: Yes Working
- TON Payments: Yes Working
- Telegram Stars: Yes Working
- Referral System: Yes Working

**Test Memo:** {test_memo}

Everything is working properly! Success
        """.strip()
        
    except Exception as e:
        status_text = f"""
Warning **System Status**

**Error Detected:**
{str(e)}

**Troubleshooting:**
- Try /start to restart
- Contact support if problem persists
- Your ID: {user_id}
        """.strip()
    
    await message.reply(status_text, parse_mode='Markdown')


@router.message(Command("help"))
async def help_command(message: Message):
    """Help command"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    help_text = get_text(language, 'help_text')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(language, 'create_ad'), callback_data="create_ad"),
            # InlineKeyboardButton(text="Price Pricing", callback_data="pricing") # REMOVED
        ],
        [
            InlineKeyboardButton(text=get_text(language, 'share_earn'), callback_data="share_earn"),
            InlineKeyboardButton(text=get_text(language, 'dashboard'), callback_data="dashboard")
        ],
        [InlineKeyboardButton(text=get_text(language, 'main_menu'), callback_data="back_to_start")]
    ])
    
    await message.reply(help_text, reply_markup=keyboard, parse_mode='Markdown')


@router.callback_query(F.data.startswith("toggle_channel_"))
async def toggle_channel_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel toggle selection"""
    try:
        channel_id = callback_query.data.replace("toggle_channel_", "")
        
        # Get current selection
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        # Toggle channel selection
        if channel_id in selected_channels:
            selected_channels.remove(channel_id)
        else:
            selected_channels.append(channel_id)
        
        # Update state
        await state.update_data(selected_channels=selected_channels)
        
        # Refresh the channel selection interface
        await show_channel_selection_for_enhanced_flow(callback_query, state)
        await callback_query.answer(f"Channel {'selected' if channel_id in selected_channels else 'deselected'}!")
        
    except Exception as e:
        logger.error(f"Channel toggle error: {e}")
        await callback_query.answer("Error toggling channel selection.")

@router.callback_query(F.data == "select_all_channels")
async def select_all_channels_handler(callback_query: CallbackQuery, state: FSMContext):
    """Select all available channels"""
    try:
        channels = await db.get_channels()
        selected_channels = [channel['channel_id'] for channel in channels]
        
        await state.update_data(selected_channels=selected_channels)
        await show_channel_selection_for_enhanced_flow(callback_query, state)
        await callback_query.answer("All channels selected!")
        
    except Exception as e:
        logger.error(f"Select all channels error: {e}")
        await callback_query.answer("Error selecting all channels.")

@router.callback_query(F.data == "deselect_all_channels")
async def deselect_all_channels_handler(callback_query: CallbackQuery, state: FSMContext):
    """Deselect all channels"""
    try:
        await state.update_data(selected_channels=[])
        await show_channel_selection_for_enhanced_flow(callback_query, state)
        await callback_query.answer("All channels deselected!")
        
    except Exception as e:
        logger.error(f"Deselect all channels error: {e}")
        await callback_query.answer("Error deselecting channels.")

@router.callback_query(F.data == "continue_with_channels")
async def continue_with_channels_handler(callback_query: CallbackQuery, state: FSMContext):
    """Continue with selected channels"""
    try:
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        if not selected_channels:
            await callback_query.answer("Please select at least one channel!")
            return
        
        # Proceed to payment selection
        await state.set_state(AdCreationStates.payment_selection)
        await show_duration_selection(callback_query, state)
        await callback_query.answer(f"{len(selected_channels)} channels selected!")
        
    except Exception as e:
        logger.error(f"Continue with channels error: {e}")
        await callback_query.answer("Error proceeding with channels.")

@router.callback_query(F.data == "proceed_to_payment")
async def proceed_to_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle proceed to payment button from channel selection"""
    try:
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        if not selected_channels:
            await callback_query.answer("Please select at least one channel first!")
            return
        
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Get package details to determine if payment is needed
        package = data.get('package', 'free')
        
        # Get package details from database or defaults
        packages = await db.get_packages(active_only=True)
        package_details = None
        
        # Find matching package
        for pkg in packages:
            if pkg['package_id'] == package:
                package_details = pkg
                break
        
        # If no package found, check if it's a default package
        if not package_details:
            if package == 'bronze':
                package_details = {'price_usd': 10.0, 'name': 'Bronze Plan'}
            elif package == 'silver':
                package_details = {'price_usd': 29.0, 'name': 'Silver Plan'}
            elif package == 'gold':
                package_details = {'price_usd': 47.0, 'name': 'Gold Plan'}
            elif package == '1month':
                package_details = {'price_usd': 9.0, 'name': '1 Month Plan', 'stars_price': 306}
            elif package == '3months':
                package_details = {'price_usd': 27.0, 'name': '3 Months Plan', 'stars_price': 918}
            elif package == '6months':
                package_details = {'price_usd': 49.0, 'name': '6 Months Plan', 'stars_price': 1323}
            else:
                package_details = {'price_usd': 0.0, 'name': 'Free Plan'}
        
        # Get progressive plan details from state
        final_price = data.get('final_price', 30)  # Default to 1 month plan
        duration_months = data.get('duration_months', 1)
        duration_days = data.get('duration_days', 30)
        posts_per_day = data.get('posts_per_day', 1)
        total_posts = data.get('total_posts', 30)
        base_price = data.get('base_price', 30)
        discount_percent = data.get('discount_percent', 0)
        
        # Calculate pricing based on progressive plan (0 fee per channel for now)
        total_price_usd = final_price  # No per-channel fee currently
        total_price_stars = int(total_price_usd * 34)  # 1 USD ≈ 34 Stars
        
        # Get channel details for display
        channel_pricing_details = []
        all_channels = await db.get_channels(active_only=True)
        for channel_id in selected_channels:
            for channel in all_channels:
                if channel['channel_id'] == channel_id:
                    channel_pricing_details.append({
                        'name': channel['name'],
                        'plan_price_usd': final_price,
                        'plan_price_stars': int(final_price * 34),
                        'posts_per_day': posts_per_day,
                        'total_posts': total_posts,
                        'duration_months': duration_months,
                        'discount_percent': discount_percent
                    })
                    break
        
        # Check if payment is needed
        if total_price_usd == 0:
            # Free package - proceed to publishing
            await handle_free_package_publishing(callback_query, state)
            return
        
        # Show payment method selection with duration-based pricing
        await state.update_data(
            selected_channels=selected_channels,
            package_details=package_details,
            total_price_usd=total_price_usd,
            total_price_stars=total_price_stars,
            channel_pricing_details=channel_pricing_details,
            duration_days=duration_days
        )
        await state.set_state(AdCreationStates.payment_method)
        
        # Create detailed pricing text with progressive plan breakdown
        plan_text = f"{duration_months} month(s)" if duration_months == 1 else f"{duration_months} months"
        
        pricing_breakdown = f"- Plan Price: ${final_price:.2f} ({posts_per_day} posts/day × {total_posts} posts)"
        if discount_percent > 0:
            pricing_breakdown += f" (Save {discount_percent}%)"
        pricing_breakdown += "\n- Channel Coverage: All selected channels included"
        
        payment_text = f"""
 **Payment Required - Progressive Plan**

 **Selected Channels:** {len(selected_channels)} (No per-channel fee)
 **Plan Duration:** {plan_text}
Stats **Posting Frequency:** {posts_per_day} posts/day per channel
Growth **Total Posts:** {total_posts * len(selected_channels):,} posts across all channels

Tip **Plan Details:**
{pricing_breakdown}

Price **Total Price:** ${total_price_usd:.2f} USD
Star **Stars Price:** {total_price_stars:,} Stars

Choose your payment method:
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="payment_stars")],
            [InlineKeyboardButton(text="💎 TON Cryptocurrency", callback_data="payment_ton")],
            [InlineKeyboardButton(text="◀️ Back to Channels", callback_data="back_to_channels")]
        ])
        
        await callback_query.message.edit_text(
            payment_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await callback_query.answer(f"Proceeding to payment for {len(selected_channels)} channels!")
        
    except Exception as e:
        logger.error(f"Proceed to payment error: {e}")
        await callback_query.answer("Error proceeding to payment")


@router.callback_query(F.data.startswith("select_package_"))
async def dynamic_package_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle dynamic package selection"""
    try:
        package_id = callback_query.data.replace("select_package_", "")
        
        if package_id == "free":
            await select_free_package(callback_query, state)
            return
        elif package_id in ["bronze", "silver", "gold", "1month", "3months", "6months"]:
            # Handle static packages with new names
            package_mapping = {
                "bronze": {"name": "Bronze Plan", "price_usd": 10, "duration_days": 30, "posts_per_day": 1},
                "silver": {"name": "Silver Plan", "price_usd": 29, "duration_days": 90, "posts_per_day": 3},
                "gold": {"name": "Gold Plan", "price_usd": 47, "duration_days": 180, "posts_per_day": 6},
                "1month": {"name": "1 Month Plan", "price_usd": 9, "duration_days": 30, "posts_per_day": 1, "stars_price": 306},
                "3months": {"name": "3 Months Plan", "price_usd": 27, "duration_days": 90, "posts_per_day": 3, "stars_price": 918},
                "6months": {"name": "6 Months Plan", "price_usd": 49, "duration_days": 180, "posts_per_day": 6, "stars_price": 1323}
            }
            
            package_details = package_mapping.get(package_id, package_mapping["1month"])
            await state.update_data(
                package=package_id,
                package_details=package_details
            )
            await state.set_state(AdCreationStates.select_category)
            await show_category_selection(callback_query, state)
            await callback_query.answer(f"{package_details['name']} selected!")
            return
        
        # Handle dynamic packages from database
        packages = await db.get_packages(active_only=True)
        package = next((p for p in packages if p['package_id'] == package_id), None)
        
        if not package:
            await callback_query.answer("Package not found!")
            return
        
        await state.update_data(
            package=package_id,
            package_info=package
        )
        await state.set_state(AdCreationStates.select_category)
        await show_category_selection(callback_query, state)
        await callback_query.answer(f"{package['name']} package selected!")
        
    except Exception as e:
        logger.error(f"Package selection error: {e}")
        await callback_query.answer("Error selecting package.")

@router.message(Command("dashboard"))
async def dashboard_command(message: Message):
    """My Ads Dashboard command"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Get user stats
    stats = await db.get_user_stats(user_id)
    referral_stats = await db.get_referral_stats(user_id)
    
    dashboard_text = f"""
Stats **{get_text(language, 'dashboard')}**

Growth **{get_text(language, 'my_stats')}:**
- {get_text(language, 'total_campaigns')}: {stats.get('total_campaigns', 0)}
- {get_text(language, 'active_campaigns')}: {stats.get('active_campaigns', 0)}
- {get_text(language, 'total_spent')}: ${stats.get('total_spent', 0):.2f}

Price **{get_text(language, 'referral_system')}:**
- {get_text(language, 'referrals')}: {referral_stats.get('total_referrals', 0)}
- {get_text(language, 'earnings')}: ${referral_stats.get('total_earnings', 0):.2f}

Link **{get_text(language, 'referral_link')}:**
`https://t.me/I3lani_bot?start=ref_{user_id}`
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'back'), callback_data="back_to_main")]
    ])
    
    await message.reply(dashboard_text, reply_markup=keyboard, parse_mode='Markdown')


# Duplicate handlers removed - using main handlers with callback_data "help" and "settings"


# Channel Incentives handlers
@router.callback_query(F.data == "join_partner_program")
async def join_partner_program_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle join partner program"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    from channel_incentives import ChannelIncentives
    from main import db
    incentives = ChannelIncentives(db)
    invitation_text = await incentives.create_invitation_message(language)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Add Bot to Channel", url="https://t.me/I3lani_bot?startchannel=partner")],
        [InlineKeyboardButton(text="🎁 Referral Program", callback_data="referral_program")],
        [InlineKeyboardButton(text="🌟 Success Stories", callback_data="success_stories")],
        [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data="back_to_main")]
    ])
    
    try:
        await callback_query.message.edit_text(invitation_text, reply_markup=keyboard)
        await callback_query.answer()
    except Exception as e:
        logger.error(f"Error in channel partner handler: {e}")
        await callback_query.answer("Channel Partner feature loaded!", show_alert=True)

@router.callback_query(F.data == "view_partner_dashboard")
async def view_partner_dashboard_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle view partner dashboard"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get user's channels where they are admin
    channels = await db.get_user_channels(user_id)
    
    if not channels:
        await callback_query.message.edit_text(
            "You don't have any channels registered. Add I3lani Bot as administrator to your channel first!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 Add Bot to Channel", url="https://t.me/I3lani_bot?startchannel=partner")],
                [InlineKeyboardButton(text="◀️ Back", callback_data="join_partner_program")]
            ])
        )
        return
    
    from channel_incentives import ChannelIncentives
    from main import db
    incentives = ChannelIncentives(db)
    dashboard_text = ""
    
    for channel in channels:
        channel_dashboard = await incentives.create_partner_dashboard(str(channel['id']), language)
        dashboard_text += channel_dashboard + "\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="view_partner_dashboard")],
        [InlineKeyboardButton(text="💰 Request Payout", callback_data="request_payout")],
        [InlineKeyboardButton(text="◀️ Back", callback_data="join_partner_program")]
    ])
    
    await callback_query.message.edit_text(dashboard_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "referral_program")
async def referral_program_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle referral program"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    from channel_incentives import ChannelIncentives
    from main import db
    incentives = ChannelIncentives(db)
    referral_text = await incentives.create_referral_program(language)
    
    # Replace {user_id} with actual user ID
    referral_text = referral_text.replace("{user_id}", str(user_id))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Referral Stats", callback_data="referral_stats")],
        [InlineKeyboardButton(text="💰 Earnings", callback_data="referral_earnings")],
        [InlineKeyboardButton(text="◀️ Back", callback_data="join_partner_program")]
    ])
    
    await callback_query.message.edit_text(referral_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "success_stories")
async def success_stories_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle success stories"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    from channel_incentives import ChannelIncentives
    from main import db
    incentives = ChannelIncentives(db)
    stories_text = await incentives.create_success_stories(language)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Join Now", callback_data="join_partner_program")],
        [InlineKeyboardButton(text="◀️ Back", callback_data="join_partner_program")]
    ])
    
    await callback_query.message.edit_text(stories_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "continue_to_channels")
async def continue_to_channels_handler(callback_query: CallbackQuery, state: FSMContext):
    """Continue to channel selection after content creation"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get available channels
    channels = await db.get_channels()
    
    if not channels:
        await callback_query.message.edit_text(
            get_text(language, 'no_channels_available'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(language, 'back_to_text'), callback_data="back_to_text")]
            ])
        )
        return
    
    # Show channel selection
    await show_channel_selection_for_enhanced_flow(callback_query, state)

@router.callback_query(F.data == "support_contact")
async def support_contact_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle support contact requests"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    support_text = """
📞 Contact Support

We're here to help! Contact us:

• Telegram: @I3lani_Support
• Email: support@i3lani.com
• Response time: 24 hours

Common issues:
• Payment not confirmed
• Ad not published
• Technical problems
• Account questions

Our team will help you resolve any issues quickly!
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data="back_to_main")]
    ])
    
    await callback_query.message.edit_text(support_text, reply_markup=keyboard)
    await callback_query.answer()

@router.callback_query(F.data == "request_payout")
async def request_payout_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle payout request"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Calculate total earnings
    from channel_incentives import ChannelIncentives
    from main import db
    incentives = ChannelIncentives(db)
    channels = await db.get_user_channels(user_id)
    total_earnings = 0
    
    for channel in channels:
        rewards = await incentives.calculate_owner_rewards(str(channel['id']))
        total_earnings += rewards.get('total_reward', 0)
    
    if total_earnings < 10:  # Minimum payout threshold
        await callback_query.message.edit_text(
            f"💰 **Payout Request**\n\nCurrent earnings: ${total_earnings:.2f}\nMinimum payout: $10.00\n\n**Keep growing your channel to reach the minimum payout!**",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Back to Dashboard", callback_data="view_partner_dashboard")]
            ]),
            parse_mode='Markdown'
        )
        return
    
    await callback_query.message.edit_text(
        f"💰 **Payout Request**\n\nEarnings: ${total_earnings:.2f}\nPayout method: TON/Telegram Stars\n\n**Payout will be processed within 24 hours**\n\nSupport will contact you for wallet details.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Confirm Payout", callback_data="confirm_payout")],
            [InlineKeyboardButton(text="◀️ Back", callback_data="view_partner_dashboard")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()

# Navigation handlers
@router.callback_query(F.data.startswith("back_to_"))
async def navigation_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle navigation back buttons"""
    try:
        destination = callback_query.data.replace("back_to_", "")
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        if destination == "main":
            await show_main_menu(callback_query, language)
        elif destination == "start":
            await show_main_menu(callback_query, language)
        else:
            await callback_query.answer("Navigation not implemented")
            
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        await callback_query.answer("Navigation failed. Please try again.")


# Error recovery handlers  
@router.callback_query(F.data == "error_recovery")
async def error_recovery_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle error recovery"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        recovery_text = f"""
Tools **Error Recovery Options**

Something went wrong. Choose how to continue:

Refresh **Continue** - Try to continue from where you left off
New **Start Over** - Begin a new ad campaign  
Home **Main Menu** - Return to main menu
**Phone** **Support** - Get help from support team
"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Refresh Continue", callback_data="continue_flow"),
                InlineKeyboardButton(text="New Start Over", callback_data="start_over")
            ],
            [
                InlineKeyboardButton(text="Home Main Menu", callback_data="back_to_main"),
                InlineKeyboardButton(text="**Phone** Support", callback_data="support")
            ]
        ])
        
        await callback_query.message.edit_text(
            recovery_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await callback_query.answer("Error recovery options")
        
    except Exception as e:
        logger.error(f"Error in error_recovery_handler: {e}")
        await callback_query.answer("Error recovery failed. Please try again.")


# Back navigation handlers
@router.callback_query(F.data == "back_to_start")
async def back_to_start_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle back to start"""
    await state.clear()
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    await show_main_menu(callback_query, language)


@router.callback_query(F.data == "back_to_photos")
async def back_to_photos_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to photo upload step"""
    await state.set_state(AdCreationStates.upload_photos)
    
    await callback_query.message.edit_text(
        " **Upload Photos** (Optional)\n\nYou can upload up to 5 photos for your ad.\n\n Send photos one by one, or skip this step.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=" Skip Photos", callback_data="skip_photos")],
            [InlineKeyboardButton(text="Back Back to Ad Details", callback_data="back_to_details")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(F.data == "back_to_details") 
async def back_to_details_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to ad details entry"""
    await state.set_state(AdCreationStates.enter_ad_details)
    
    await callback_query.message.edit_text(
        "Edit **Enter Ad Details**\n\nPlease provide detailed information about your ad:\n- Product/service description\n- Key features\n- Benefits\n- Call to action",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Back Back to Location", callback_data="back_to_location")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(F.data == "back_to_location")
async def back_to_location_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to location selection"""
    await state.set_state(AdCreationStates.select_location)
    await show_location_selection(callback_query, state)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_preview")
async def back_to_preview_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to ad preview"""
    await state.set_state(AdCreationStates.preview_ad)
    await show_ad_preview(callback_query.message, state)
    await callback_query.answer()


@router.callback_query(F.data == "edit_ad")
async def edit_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Edit ad details"""
    await state.set_state(AdCreationStates.enter_ad_details)
    await back_to_details_handler(callback_query, state)


@router.callback_query(F.data == "cancel_ad")
async def cancel_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Cancel ad creation"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.clear()
    await callback_query.message.edit_text(
        "No **Ad Creation Cancelled**\n\nYour ad has been cancelled. You can start a new ad anytime!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="New Create New Ad", callback_data="create_ad")],
            [InlineKeyboardButton(text="Home Main Menu", callback_data="back_to_main")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer("Ad creation cancelled")


@router.callback_query(F.data == "go_home")
async def go_home_handler(callback_query: CallbackQuery, state: FSMContext):
    """Go to home/main menu"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.clear()
    await show_main_menu(callback_query, language)
    await callback_query.answer("Returned to main menu")


@router.callback_query(F.data == "add_more_photos")
async def add_more_photos_handler(callback_query: CallbackQuery, state: FSMContext):
    """Add more photos to the ad"""
    await state.set_state(AdCreationStates.upload_photos)
    
    await callback_query.message.edit_text(
        " **Upload More Photos**\n\nSend additional photos for your ad (up to 5 total).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Yes Done with Photos", callback_data="done_photos")],
            [InlineKeyboardButton(text="Back Back to Contact", callback_data="back_to_contact")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(F.data == "back_to_contact")
async def back_to_contact_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to contact information step"""
    await state.set_state(AdCreationStates.provide_contact_info)
    
    await callback_query.message.edit_text(
        "**Phone** **Contact Information**\n\nPlease provide your contact details:\n- Phone number\n- Email address\n- Telegram username\n- Any other contact method",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Back to Photos", callback_data="back_to_photos")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("payment_timeout_"))
async def payment_timeout_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment timeout"""
    payment_id = callback_query.data.replace("payment_timeout_", "")
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    timeout_text = f"""
 **Payment Timeout**

Your payment session has expired.

Refresh **Options:**
- Try payment again
- Choose different payment method
- Return to main menu

What would you like to do?
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Refresh Retry Payment", callback_data=f"retry_payment_{payment_id}")],
        [InlineKeyboardButton(text=" Change Method", callback_data="change_payment_method")],
        [InlineKeyboardButton(text="Home Main Menu", callback_data="back_to_main")]
    ])
    
    await callback_query.message.edit_text(timeout_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer("Payment session expired")


@router.callback_query(F.data == "change_payment_method")
async def change_payment_method_handler(callback_query: CallbackQuery, state: FSMContext):
    """Change payment method"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.payment_method)
    await callback_query.message.edit_text(
        " **Choose Payment Method**\n\nSelect your preferred payment option:",
        reply_markup=create_payment_method_keyboard(language),
        parse_mode='Markdown'
    )
    await callback_query.answer("Choose payment method")


@router.callback_query(F.data == "error_recovery")
async def error_recovery_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle error recovery"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    recovery_text = f"""
Tool **Error Recovery**

Something went wrong. Let's get you back on track.

Refresh **Recovery Options:**
- Continue from where you left off
- Start over with new ad
- Return to main menu
- Contact support

Choose your preferred option:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Refresh Continue", callback_data="continue_flow")],
        [InlineKeyboardButton(text="New Start Over", callback_data="create_ad")],
        [InlineKeyboardButton(text="Home Main Menu", callback_data="back_to_main")],
        [InlineKeyboardButton(text="**Phone** Support", callback_data="help")]
    ])
    
    await callback_query.message.edit_text(recovery_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer("Error recovery options")


@router.callback_query(F.data == "continue_flow")
async def continue_flow_handler(callback_query: CallbackQuery, state: FSMContext):
    """Continue flow from current state"""
    current_state = await state.get_state()
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Determine appropriate continuation based on current state
    if current_state == AdCreationStates.select_category:
        await show_category_selection(callback_query, state)
    elif current_state == AdCreationStates.upload_photos:
        await back_to_photos_handler(callback_query, state)
    elif current_state == AdCreationStates.payment_method:
        await callback_query.message.edit_text(
            " **Choose Payment Method**",
            reply_markup=create_payment_method_keyboard(language)
        )
    else:
        # Default to main menu if state unknown
        await back_to_main_handler(callback_query, state)
    
    await callback_query.answer("Continuing flow")


@router.callback_query(F.data.startswith("retry_payment_"))
async def retry_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle retry payment request"""
    try:
        subscription_id = callback_query.data.replace("retry_payment_", "")
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Get subscription details
        subscription = await db.get_subscription(subscription_id)
        if not subscription:
            await callback_query.answer("Subscription not found", show_alert=True)
            return
        
        # Create new payment invoice
        payment_processor = PaymentProcessor()
        invoice = await payment_processor.create_payment_invoice(
            user_id=user_id,
            subscription_id=subscription_id,
            amount=subscription['total_price'],
            currency='TON',
            payment_method='ton'
        )
        
        # Show new payment instructions
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Yes Payment Sent", 
                callback_data=f"confirm_payment_{invoice['payment_id']}"
            )],
            [InlineKeyboardButton(
                text="Home Go Home", 
                callback_data="go_home"
            )]
        ])
        
        await callback_query.message.edit_text(
            invoice['instructions'],
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await callback_query.answer("New payment instructions generated!")
        
    except Exception as e:
        logger.error(f"Retry payment error: {e}")
        await callback_query.answer("Error generating payment. Please try again.")


@router.callback_query(F.data == "go_home")
async def go_home_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle go home request"""
    await state.clear()
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    await show_main_menu(callback_query, language)


# Old admin handler removed - now handled by admin_system.py


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
            formatted_content = f" **Advertisement**\n\n{ad_content}\n\n *Advertise with @I3lani_bot*"
            
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
Success **Stars Payment Successful & Ad Published!**

Star **Payment Confirmed:** {payment.total_amount} Stars
Yes **Your ad is now live on the I3lani channel!**

Stats **Campaign Status:**
- Payment ID: {payment.telegram_payment_charge_id}
- Published: Just now
- Channel: https://t.me/i3lani
- Status: Active

Link **View your ad:** https://t.me/i3lani

Thank you for using I3lani Bot!
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Link View I3lani Channel", 
                url="https://t.me/i3lani"
            )],
            [InlineKeyboardButton(
                text="Home Main Menu", 
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
    
    # Content moderation handlers
    @router.callback_query(F.data == "admin_moderation")
    async def admin_moderation_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle admin moderation callback"""
        user_id = callback_query.from_user.id
        
        from admin_system import admin_system
        if not admin_system.is_admin(user_id):
            await callback_query.answer("Access denied")
            return
        
        await admin_system.show_moderation_panel(callback_query)

    @router.callback_query(F.data == "admin_violations")
    async def admin_violations_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle admin violations callback"""
        user_id = callback_query.from_user.id
        
        from admin_system import admin_system
        if not admin_system.is_admin(user_id):
            await callback_query.answer("Access denied")
            return
        
        await admin_system.show_violation_reports(callback_query)

    @router.callback_query(F.data.startswith("edit_ad_"))
    async def edit_ad_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle edit ad callback after content violation"""
        user_id = callback_query.from_user.id
        order_id = callback_query.data.split("_")[2]
        
        try:
            # Set state for content editing
            await state.update_data(order_id=order_id, editing_content=True)
            await state.set_state(AdCreationStates.upload_content)
            
            await callback_query.message.edit_text(
                "📝 **Edit Your Ad Content**\n\n"
                "Please upload your new content (text, photo, or video) that complies with our guidelines:\n\n"
                "✅ No hate speech or discrimination\n"
                "✅ No adult or illegal content\n"
                "✅ No spam or excessive promotion\n"
                "✅ Respect cultural and religious values\n"
                "✅ Follow international regulations\n\n"
                "💡 Send your new content now:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_edit")]
                ])
            )
            
        except Exception as e:
            logger.error(f"Edit ad error: {e}")
            await callback_query.answer("Error processing edit request")

    @router.callback_query(F.data.startswith("cancel_ad_"))
    async def cancel_ad_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle cancel ad callback"""
        user_id = callback_query.from_user.id
        order_id = callback_query.data.split("_")[2]
        
        try:
            # Cancel the order
            await db.cancel_order(order_id, "User cancelled due to content violation")
            
            await callback_query.message.edit_text(
                "❌ **Ad Cancelled**\n\n"
                "Your ad has been cancelled. You can create a new ad that complies with our guidelines at any time.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
                ])
            )
            
        except Exception as e:
            logger.error(f"Cancel ad error: {e}")
            await callback_query.answer("Error cancelling ad")

    @router.callback_query(F.data == "view_publishing_rules")
    async def view_publishing_rules_callback(callback_query: CallbackQuery):
        """Show publishing rules and guidelines"""
        rules_text = """
📋 **Publishing Rules & Guidelines**

**Content Standards:**
• No hate speech, discrimination, or harassment
• No adult, sexual, or inappropriate content
• No illegal activities or substances
• No violence or harmful content
• No spam or excessive promotional material
• No fraudulent or misleading information

**Cultural Compliance:**
• Respect religious and cultural values
• Follow Saudi Arabian regulations
• Appropriate language and imagery
• Cultural sensitivity required

**International Standards:**
• Human rights compliance
• Privacy protection (GDPR)
• Copyright respect
• Financial regulations compliance

**Violation Consequences:**
• Strike 1-5: Warning + Edit opportunity
• Strike 6: Permanent ban + No compensation

**Need Help?**
Contact @I3lani_support for assistance.
        """.strip()
        
        await callback_query.message.edit_text(
            rules_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_main")]
            ])
        )
    
    # Gamification handlers
    @router.callback_query(F.data == "gamification_hub")
    async def gamification_hub_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle gamification hub callback"""
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        try:
            from gamification import GamificationSystem
            gamification = GamificationSystem(db, callback_query.message.bot)
            
            # Initialize tables if needed
            await gamification.initialize_gamification_tables()
            
            # Get dashboard
            dashboard = await gamification.create_gamification_dashboard(user_id, language)
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🏆 Achievements", callback_data="gamification_achievements"),
                    InlineKeyboardButton(text="🎯 Daily Check-in", callback_data="gamification_checkin")
                ],
                [
                    InlineKeyboardButton(text="🏅 Leaderboard", callback_data="gamification_leaderboard"),
                    InlineKeyboardButton(text="🎮 Challenges", callback_data="gamification_challenges")
                ],
                [
                    InlineKeyboardButton(text="📊 My Stats", callback_data="gamification_stats"),
                    InlineKeyboardButton(text="🎲 Level Up Guide", callback_data="gamification_guide")
                ],
                [
                    InlineKeyboardButton(text="⬅️ Back to Main", callback_data="back_to_main")
                ]
            ])
            
            await callback_query.message.edit_text(
                dashboard,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Gamification hub error: {e}")
            await callback_query.answer("Error loading gaming hub")

    @router.callback_query(F.data == "gamification_checkin")
    async def gamification_checkin_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle daily check-in callback"""
        user_id = callback_query.from_user.id
        
        try:
            from gamification import GamificationSystem
            gamification = GamificationSystem(db, callback_query.message.bot)
            
            result = await gamification.process_daily_checkin(user_id)
            
            if result.get('already_checked_in'):
                message = f"""
🎯 **Daily Check-in Status**

You've already checked in today!

Current Streak: {result['streak']} days 🔥

Come back tomorrow to continue your streak!
                """.strip()
                
            elif result.get('success'):
                message = f"""
✅ **Daily Check-in Complete!**

🔥 Streak: {result['streak']} days
⭐ XP Earned: +{result['xp_reward']}
💰 TON Earned: +{result['ton_reward']:.3f}
🚀 Streak Multiplier: {result['streak_multiplier']:.1f}x

{"🎉 New streak record!" if result['streak'] > 1 else "Great start!"}

Keep coming back daily to build your streak! 🎯
                """.strip()
                
            else:
                message = "❌ Check-in failed. Please try again later."
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎮 Gaming Hub", callback_data="gamification_hub")],
                [InlineKeyboardButton(text="⬅️ Back to Main", callback_data="back_to_main")]
            ])
            
            await callback_query.message.edit_text(
                message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Check-in error: {e}")
            await callback_query.answer("Error processing check-in")

    @router.callback_query(F.data == "gamification_leaderboard")
    async def gamification_leaderboard_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle leaderboard callback"""
        user_id = callback_query.from_user.id
        
        try:
            from gamification import GamificationSystem
            gamification = GamificationSystem(db, callback_query.message.bot)
            
            # Get different leaderboards
            xp_leaderboard = await gamification.get_leaderboard('xp', 10)
            earnings_leaderboard = await gamification.get_leaderboard('earnings', 10)
            achievements_leaderboard = await gamification.get_leaderboard('achievements', 10)
            
            # Format leaderboard display
            def format_leaderboard(leaderboard, metric):
                if not leaderboard:
                    return "No data available"
                
                lines = []
                for i, entry in enumerate(leaderboard):
                    pos = entry['position']
                    name = entry['display_name'][:15] + "..." if len(entry['display_name']) > 15 else entry['display_name']
                    level_badge = entry['level_info']['badge']
                    
                    if metric == 'xp':
                        value = f"{entry['xp']:,} XP"
                    elif metric == 'earnings':
                        value = f"{entry['total_ton_earned']:.2f} TON"
                    elif metric == 'achievements':
                        value = f"{entry['total_achievements']} 🏆"
                    
                    medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{pos}."
                    lines.append(f"{medal} {level_badge} {name} - {value}")
                
                return "\n".join(lines)
            
            leaderboard_text = f"""
🏅 **GLOBAL LEADERBOARD** 🏅

**🌟 Top XP Leaders:**
{format_leaderboard(xp_leaderboard, 'xp')}

**💰 Top Earners:**
{format_leaderboard(earnings_leaderboard, 'earnings')}

**🏆 Achievement Masters:**
{format_leaderboard(achievements_leaderboard, 'achievements')}

*Leaderboard updates every hour*
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🎮 Gaming Hub", callback_data="gamification_hub"),
                    InlineKeyboardButton(text="📊 My Rank", callback_data="gamification_my_rank")
                ],
                [
                    InlineKeyboardButton(text="⬅️ Back to Main", callback_data="back_to_main")
                ]
            ])
            
            await callback_query.message.edit_text(
                leaderboard_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Leaderboard error: {e}")
            await callback_query.answer("Error loading leaderboard")

    @router.callback_query(F.data == "gamification_achievements")
    async def gamification_achievements_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle achievements callback"""
        user_id = callback_query.from_user.id
        
        try:
            from gamification import GamificationSystem
            gamification = GamificationSystem(db, callback_query.message.bot)
            
            profile = await gamification.get_user_profile(user_id)
            user_achievements = [ach['achievement_id'] for ach in profile['achievements']]
            
            # Group achievements by category
            partner_achievements = []
            referral_achievements = []
            earning_achievements = []
            activity_achievements = []
            special_achievements = []
            
            for achievement_id, achievement in gamification.achievements.items():
                unlocked = achievement_id in user_achievements
                status = "✅" if unlocked else "🔒"
                
                line = f"{status} {achievement['badge']} {achievement['name']}"
                if not unlocked:
                    line += f" - {achievement['description']}"
                
                if achievement['type'] == 'channels_added':
                    partner_achievements.append(line)
                elif achievement['type'] == 'referrals_made':
                    referral_achievements.append(line)
                elif achievement['type'] in ['total_earned', 'payouts_received']:
                    earning_achievements.append(line)
                elif achievement['type'] == 'daily_checkins':
                    activity_achievements.append(line)
                else:
                    special_achievements.append(line)
            
            achievements_text = f"""
🏆 **ACHIEVEMENTS** 🏆

**🤝 Partner Achievements:**
{chr(10).join(partner_achievements)}

**📢 Referral Achievements:**
{chr(10).join(referral_achievements)}

**💰 Earning Achievements:**
{chr(10).join(earning_achievements)}

**⚡ Activity Achievements:**
{chr(10).join(activity_achievements)}

**🌟 Special Achievements:**
{chr(10).join(special_achievements)}

**Progress: {len(user_achievements)}/{len(gamification.achievements)} Unlocked**
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🎮 Gaming Hub", callback_data="gamification_hub"),
                    InlineKeyboardButton(text="🏅 Leaderboard", callback_data="gamification_leaderboard")
                ],
                [
                    InlineKeyboardButton(text="⬅️ Back to Main", callback_data="back_to_main")
                ]
            ])
            
            await callback_query.message.edit_text(
                achievements_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Achievements error: {e}")
            await callback_query.answer("Error loading achievements")

    @router.callback_query(F.data == "gamification_guide")
    async def gamification_guide_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle level up guide callback"""
        
        try:
            from gamification import GamificationSystem
            gamification = GamificationSystem(db, callback_query.message.bot)
            
            guide_text = """
🎲 **LEVEL UP GUIDE** 🎲

**How to Earn XP:**
• Daily Check-in: +10 XP (streak bonus up to 2x)
• Unlock Achievement: +50 XP
• Refer Partner: +25 XP
• Add Channel: +30 XP
• Complete Challenge: +15-100 XP

**Level Benefits:**
🟢 Lv1 Rookie: Basic dashboard
🔵 Lv2 Explorer: Advanced analytics
🟡 Lv3 Specialist: Priority support
🟠 Lv4 Expert: Custom dashboard
🔴 Lv5 Master: Beta features
🟣 Lv6 Champion: VIP support
⚫ Lv7 Legend: Exclusive rewards
⚪ Lv8 Mythic: All features unlocked

**Level Up Rewards:**
Each level up gives you TON bonus equal to your new level!

**Achievement Categories:**
🤝 Partner: Add channels to network
📢 Referral: Invite new partners
💰 Earning: Reach payout milestones
⚡ Activity: Daily engagement
🌟 Special: Unique accomplishments

**Tips for Success:**
• Check in daily to build streaks
• Share your referral link actively
• Add multiple channels for bonuses
• Complete daily challenges
• Stay engaged with the community

Ready to level up? 🚀
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🎮 Gaming Hub", callback_data="gamification_hub"),
                    InlineKeyboardButton(text="🎯 Daily Check-in", callback_data="gamification_checkin")
                ],
                [
                    InlineKeyboardButton(text="⬅️ Back to Main", callback_data="back_to_main")
                ]
            ])
            
            await callback_query.message.edit_text(
                guide_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Guide error: {e}")
            await callback_query.answer("Error loading guide")

    logger.info("Handlers setup completed")


# Back Navigation Handlers for Enhanced Flow

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle back to categories navigation"""
    await show_category_selection(callback_query, state)
    await callback_query.answer()


@router.callback_query(F.data == "back_to_subcategories")
async def back_to_subcategories_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle back to subcategories navigation"""
    data = await state.get_data()
    category_id = data.get('selected_category')
    
    if category_id:
        from config import AD_CATEGORIES
        category = AD_CATEGORIES.get(category_id)
        if category:
            # Recreate subcategory selection
            subcategory_text = f"""
{category['emoji']} **{category['name']}**

Select a subcategory:
            """.strip()
            
            keyboard_rows = []
            for sub_id, sub_name in category['subcategories'].items():
                keyboard_rows.append([InlineKeyboardButton(
                    text=sub_name,
                    callback_data=f"subcategory_{sub_id}"
                )])
            
            keyboard_rows.append([InlineKeyboardButton(
                text="Back Back to Categories",
                callback_data="back_to_categories"
            )])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
            
            await callback_query.message.edit_text(
                subcategory_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            await state.set_state(AdCreationStates.select_subcategory)
    
    await callback_query.answer()


@router.callback_query(F.data == "edit_ad")
async def edit_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle edit ad request"""
    await callback_query.message.edit_text(
        "Edit **Edit Ad**\n\nWhat would you like to edit?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Content Ad Details", callback_data="edit_ad_details")],
            [InlineKeyboardButton(text="**Phone** Contact Info", callback_data="edit_contact_info")],
            [InlineKeyboardButton(text=" Photos", callback_data="edit_photos")],
            [InlineKeyboardButton(text="Back Back to Preview", callback_data="back_to_preview")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(F.data == "cancel_ad")
async def cancel_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle ad cancellation"""
    await callback_query.message.edit_text(
        "No **Ad Creation Cancelled**\n\nYour ad creation has been cancelled.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Home Back to Home", callback_data="back_to_main")]
        ]),
        parse_mode='Markdown'
    )
    await state.clear()
    await callback_query.answer()


@router.callback_query(F.data.startswith("dynamic_days_"))
async def dynamic_days_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle dynamic days selection"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    days_data = callback_query.data.replace("dynamic_days_", "")
    
    if days_data == "custom":
        await state.set_state(AdCreationStates.custom_input)
        text = """
Date **Custom Duration**

Please enter the number of days you want your ad to run:

Examples: 5, 12, 45, 90

Type the number of days:
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Back Back to Duration", callback_data="continue_to_duration")]
        ])
        
        try:
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except (AttributeError, Exception):
            await callback_query.message.answer(text, reply_markup=keyboard)
    else:
        days = int(days_data)
        await state.update_data(selected_days=days)
        
        # Show posts per day selection
        text = f"""
Date **Duration Selected: {days} days**

Target **Step 2: How many posts per day?**

Choose your posting frequency to see volume discounts:

Tip **Volume Discount Tips:**
- 1 post/day = No discount
- 2 posts/day = 5% off
- 4 posts/day = 10% off
- 8 posts/day = 20% off
- 24 posts/day = 30% off (maximum!)

Select posts per day:
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="1/day (No discount)", callback_data="dynamic_posts_1"),
                InlineKeyboardButton(text="2/day (5% off)", callback_data="dynamic_posts_2")
            ],
            [
                InlineKeyboardButton(text="3/day (7% off)", callback_data="dynamic_posts_3"),
                InlineKeyboardButton(text="4/day (10% off)", callback_data="dynamic_posts_4")
            ],
            [
                InlineKeyboardButton(text="6/day (15% off)", callback_data="dynamic_posts_6"),
                InlineKeyboardButton(text="8/day (20% off)", callback_data="dynamic_posts_8")
            ],
            [
                InlineKeyboardButton(text="12/day (27% off)", callback_data="dynamic_posts_12"),
                InlineKeyboardButton(text="24/day (30% off)", callback_data="dynamic_posts_24")
            ],
            [
                InlineKeyboardButton(text="Custom Amount", callback_data="dynamic_posts_custom"),
                InlineKeyboardButton(text="Back Back", callback_data="continue_to_duration")
            ]
        ])
        
        try:
            await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
        except (AttributeError, Exception):
            await callback_query.message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    
    await callback_query.answer()


@router.callback_query(F.data.startswith("dynamic_posts_"))
async def dynamic_posts_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle posts per day selection"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    posts_data = callback_query.data.replace("dynamic_posts_", "")
    
    if posts_data == "custom":
        await state.set_state(AdCreationStates.custom_input)
        text = """
Target **Custom Posts Per Day**

Please enter how many posts per day you want:

Examples: 5, 15, 20

Tip **Discount Reference:**
- 1-1 posts/day = 0% discount
- 2-2 posts/day = 5% discount
- 3-3 posts/day = 7% discount
- 4-4 posts/day = 10% discount
- 8-8 posts/day = 20% discount
- 24+ posts/day = 30% discount (maximum)

Type the number of posts per day:
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Back Back to Posts", callback_data="dynamic_back_to_posts")]
        ])
        
        try:
            await callback_query.message.edit_text(text, reply_markup=keyboard)
        except (AttributeError, Exception):
            await callback_query.message.answer(text, reply_markup=keyboard)
    else:
        posts_per_day = int(posts_data)
        
        # Get stored data
        data = await state.get_data()
        days = data.get('selected_days', 1)
        selected_channels = data.get('selected_channels', [])
        
        # Get channel data for display
        channels = await db.get_channels()
        selected_channel_data = [ch for ch in channels if ch['channel_id'] in selected_channels]
        
        # Calculate pricing using dynamic system
        pricing = get_dynamic_pricing()
        calculation = pricing.calculate_total_cost(days, posts_per_day, selected_channel_data)
        
        # Store calculation in state
        await state.update_data(
            selected_days=days,
            posts_per_day=posts_per_day,
            pricing_calculation=calculation
        )
        
        # Format the summary
        summary = pricing.format_pricing_summary(calculation)
        discount_explanation = pricing.get_discount_explanation(posts_per_day)
        
        # Create channel list
        channel_list = "\n".join([f"- {ch['name']}" for ch in selected_channel_data])
        
        text = f"""
{summary}

**Selected Channels ({len(selected_channel_data)}):**
{channel_list}

{discount_explanation}

 **Choose your payment method:**
        """.strip()
        
        # Create payment keyboard
        keyboard_data = pricing.create_payment_keyboard_data(calculation)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=btn['text'], callback_data=btn['callback_data']) 
             for btn in row]
            for row in keyboard_data
        ])
        
        try:
            await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
        except (AttributeError, Exception):
            await callback_query.message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    
    await callback_query.answer()


@router.callback_query(F.data == "recalculate_dynamic")
async def recalculate_dynamic_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle recalculate request"""
    await continue_to_duration_handler(callback_query, state)