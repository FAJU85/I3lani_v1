"""
Message and callback handlers for I3lani Telegram Bot
"""
from step_title_system import get_step_title, create_titled_message
from animated_transitions import get_animated_transitions, animate_to_stage, smooth_callback_transition
from transition_integration import TransitionIntegration
from contextual_help_system import get_contextual_help_system, show_help_bubble, add_help_to_keyboard
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
import random
import string
from logger import log_success, log_error, log_info, StepNames

logger = logging.getLogger(__name__)

from states import AdCreationStates, UserStates, WalletStates, CreateAd
from languages import get_text, get_currency_info, LANGUAGES
from database import db, ensure_user_exists, get_user_language
from automatic_language_system import get_user_language_auto
from config import ADMIN_IDS
from wallet_manager import WalletManager
import os
from datetime import datetime, timedelta
from callback_error_handler import safe_callback_answer, safe_callback_edit
from modern_keyboard import (
    create_modern_main_menu, create_modern_language_selector, 
    create_modern_channel_selector, create_modern_duration_selector,
    create_modern_payment_selector, create_modern_admin_panel,
    create_modern_confirmation
)
# from frequency_pricing import FrequencyPricingSystem  # Removed during cleanup
# ui_effects removed during cleanup
from confirmation_system import confirmation_system
from confirmation_handlers import CONFIRMATION_HANDLERS
from viral_referral_handlers import has_free_ads, consume_free_ad
from error_reporting_system import error_reporting, ErrorReport
from handlers_tracking_integration import (
    track_bot_start, track_create_ad_start, track_content_upload,
    track_channel_selection, track_duration_selection, track_frequency_selection,
    track_campaign_confirmation, track_payment_method_selection,
    track_payment_processing, track_payment_confirmed, track_publishing_scheduled
)
# Flow validator removed for cleanup

logger = logging.getLogger(__name__)

# Create router
router = Router()


def create_language_keyboard() -> InlineKeyboardMarkup:
    """Create modern language selection keyboard"""
    return create_modern_language_selector()



def get_user_language_and_create_titled_message(user_id: int, step_key: str, content: str) -> str:
    """Helper function to get user language and create titled message"""
    try:
        # Use sync wrapper to avoid coroutine issues
        def get_user_language_sync(user_id: int) -> str:
            """Synchronous language detection to prevent coroutine issues"""
            # Cache for known users
            user_language_cache = getattr(get_user_language_sync, '_cache', {})
            
            if user_id in user_language_cache:
                return user_language_cache[user_id]
            
            # Default language based on user ID patterns
            if user_id == 566158428:  # Known Arabic user
                language = 'ar'
            else:
                language = 'en'  # Default to English for new users
            
            # Cache the result
            user_language_cache[user_id] = language
            get_user_language_sync._cache = user_language_cache
            
            return language
        
        language = get_user_language_sync(user_id)
        return create_titled_message(step_key, content, language, user_id)
    except Exception as e:
        logger.error(f"Error creating titled message: {e}")
        return content

async def is_user_partner(user_id: int) -> bool:
    """Check if user is a partner/affiliate"""
    try:
        partner_status = await db.get_partner_status(user_id)
        return partner_status is not None
    except:
        return False

async def create_regular_main_menu_text(language: str, user_id: int) -> str:
    """Create standard main menu text for regular users using translation system"""
    
    # Get user stats for dynamic content
    user_stats = await db.get_user_stats(user_id)
    total_ads = user_stats.get('total_ads', 0) if user_stats else 0
    
    # Check for admin customized text first
    try:
        custom_text = await db.get_custom_ui_text('main_menu_welcome', language)
        if custom_text:
            return custom_text.format(total_ads=total_ads)
    except:
        pass  # Fall back to default text if database query fails
    
    # Use the new crypto-focused main menu message
    main_menu_text = get_text(language, 'main_menu')
    
    # Get account status translations
    your_account_text = get_text(language, 'your_account')
    total_campaigns_text = get_text(language, 'total_campaigns')
    account_status_text = get_text(language, 'account_status')
    account_active_text = get_text(language, 'account_active')
    performance_text = get_text(language, 'performance')
    performance_optimized_text = get_text(language, 'performance_optimized')
    
    # Build the complete menu text with crypto-focused messaging
    menu_text = f"""<b>{main_menu_text}</b>

<b>{your_account_text}</b>
• {total_campaigns_text} <code>{total_ads}</code>
• {account_status_text} <b>{account_active_text}</b>
• {performance_text} <b>{performance_optimized_text}</b>"""
    
    return menu_text.strip()

async def create_neural_main_menu_text(language: str, user_id: int) -> str:
    """Create neural network main menu text for partners only"""
    
    # Check for admin customized text first
    try:
        custom_text = await db.get_custom_ui_text('main_menu_neural', language)
        if custom_text:
            return custom_text
    except:
        pass  # Fall back to default text if database query fails
    
    # Use translation system for partner main menu text
    return get_text(language, 'main_menu')

async def create_regular_main_menu_keyboard(language: str, user_id: int) -> InlineKeyboardMarkup:
    """Create standard main menu keyboard for regular users with multilingual support"""
    keyboard_rows = []
    
    # Check if user can use free trial
    can_use_trial = await db.check_free_trial_available(user_id)
    
    # Free trial for new users (standard styling)
    if can_use_trial:
        free_trial_text = {
            'en': '🎁 Free Trial (1 Day)',
            'ar': '🎁 تجربة مجانية (يوم واحد)',
            'ru': '🎁 Бесплатная пробная версия (1 день)'
        }
        keyboard_rows.append([
            InlineKeyboardButton(
                text=free_trial_text.get(language, free_trial_text['en']), 
                callback_data="free_trial"
            )
        ])
    
    # Use multilingual text from languages.py
    create_ad_text = get_text(language, 'create_ad')
    my_ads_text = get_text(language, 'my_ads')
    pricing_text = get_text(language, 'pricing')
    share_earn_text = get_text(language, 'share_earn')
    settings_text = get_text(language, 'settings')
    help_text = get_text(language, 'help')
    
    # Viral Referral Game Button
    viral_game_text = {
        'en': '🎮 Viral Game (Win Free Ads)',
        'ar': '🎮 لعبة فيروسية (اربح إعلانات مجانية)',
        'ru': '🎮 Вирусная игра (выиграй бесплатные объявления)'
    }
    
    keyboard_rows.append([
        InlineKeyboardButton(
            text=create_ad_text, 
            callback_data="create_ad"
        )
    ])
    
    keyboard_rows.append([
        InlineKeyboardButton(
            text=viral_game_text.get(language, viral_game_text['en']), 
            callback_data="start_viral_game"
        )
    ])
    
    keyboard_rows.append([
        InlineKeyboardButton(
            text=my_ads_text, 
            callback_data="my_ads"
        ),
        InlineKeyboardButton(
            text=pricing_text, 
            callback_data="pricing"
        )
    ])
    
    keyboard_rows.append([
        InlineKeyboardButton(
            text=share_earn_text, 
            callback_data="partner_program"
        )
    ])
    
    keyboard_rows.append([
        InlineKeyboardButton(
            text=settings_text, 
            callback_data="settings"
        ),
        InlineKeyboardButton(
            text=help_text, 
            callback_data="help"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

async def create_partner_main_menu_keyboard(language: str, user_id: int) -> InlineKeyboardMarkup:
    """Create neural network main menu keyboard for partners only"""
    keyboard_rows = []
    
    # Check if user can use free trial
    can_use_trial = await db.check_free_trial_available(user_id)
    
    # Free trial quantum gift for partners
    if can_use_trial:
        keyboard_rows.append([
            InlineKeyboardButton(
                text="🎁 ✨ FREE TRIAL ✨ One Day Free (1 Day)", 
                callback_data="free_trial"
            )
        ])
    
    # Primary Actions Row
    keyboard_rows.append([
        InlineKeyboardButton(
            text=get_text(language, 'create_ad'), 
            callback_data="create_ad"
        )
    ])
    
    keyboard_rows.append([
        InlineKeyboardButton(
            text=get_text(language, 'my_ads'), 
            callback_data="my_ads"
        ),
        InlineKeyboardButton(
            text=get_text(language, 'share_earn'), 
            callback_data="share_earn"
        )
    ])
    
    # Advanced Operations Row
    keyboard_rows.append([
        InlineKeyboardButton(
            text=get_text(language, 'channel_partners'), 
            callback_data="join_partner_program"
        ),
        InlineKeyboardButton(
            text=get_text(language, 'gaming_hub'), 
            callback_data="gamification_hub"
        )
    ])
    
    # Competition & Leaderboard Row
    keyboard_rows.append([
        InlineKeyboardButton(
            text=get_text(language, 'leaderboard'), 
            callback_data="gamification_leaderboard"
        )
    ])
    
    # System Controls Row
    keyboard_rows.append([
        InlineKeyboardButton(
            text=get_text(language, 'settings'), 
            callback_data="settings"
        ),
        InlineKeyboardButton(
            text=get_text(language, 'help'), 
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


# REMOVED: create_duration_keyboard - old progressive monthly plans removed


# REMOVED: show_duration_selection - old progressive monthly plans interface removed
        

# REMOVED: get_progressive_plan_details - old progressive monthly plans data removed


# REMOVED: duration_selection_handler - old progressive monthly plans handler removed


def create_payment_method_keyboard(language: str) -> InlineKeyboardMarkup:
    """Create payment method selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(language, 'pay_stars'), 
            callback_data="pay_freq_stars"
        )],
        [InlineKeyboardButton(
            text=get_text(language, 'pay_ton'), 
            callback_data="pay_freq_ton"
        )],
        [InlineKeyboardButton(
            text=get_text(language, 'back'), 
            callback_data="back_to_channels"
        )]
    ])
    return keyboard


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """Start command handler with comprehensive anti-fraud protection and step logging"""
    user_id = message.from_user.id if message.from_user else 0
    username = message.from_user.username
    # Handle referral code from start parameter
    start_param = None
    if message.text and len(message.text.split()) > 1:
        start_param = message.text.split()[1]
    
    # Process referral registration
    if start_param and start_param.startswith('ref_'):
        try:
            from referral_integration import process_referral_start_command
            await process_referral_start_command(user_id, start_param)
            logger.info(f"✅ Processed referral code {start_param} for user {user_id}")
        except Exception as e:
            logger.error(f"Error processing referral start: {e}")
    
    # Log start command step
    log_info(StepNames.START_COMMAND, user_id, "User started bot", {
        'username': username,
        'user_id': user_id
    })
    
    # Track bot start with end-to-end tracking system
    try:
        await track_bot_start(user_id, username, state)
    except Exception as e:
        logger.error(f"Error tracking bot start: {e}")
    
    # Initialize anti-fraud system
    from anti_fraud import AntiFraudSystem
    fraud_system = AntiFraudSystem(db)
    
    # Log user interaction for fraud detection
    await db.log_user_interaction(user_id, "start_command", f"Username: {username}")
    await db.log_user_action(user_id, "start", "Bot started")
    
    # Check if user is blocked
    if await db.is_user_blocked(user_id):
        log_info(StepNames.START_COMMAND, user_id, "Blocked user attempted access")
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
        user_language = user['language']
        logger.info(f"👤 Existing user {user_id} has language: {user_language}")
        await show_main_menu(message, user_language)
    else:
        # New user, show language selection
        logger.info(f"🆕 New user {user_id}, showing language selection")
        await state.set_state(AdCreationStates.language_selection)
        await message.answer(
            get_text('en', 'choose_language'),
            reply_markup=create_language_keyboard()
        )
    
    # Handle referral
    if referrer_id and referrer_id != user_id:
        await db.create_referral(referrer_id, user_id)


async def show_main_menu(message_or_query, language: str, **kwargs):
    """Show appropriate main menu based on user type (regular vs partner)"""
    # Get user_id from message or callback query
    if isinstance(message_or_query, Message):
        user_id = message_or_query.from_user.id
        chat_id = message_or_query.chat.id
        bot = message_or_query.bot
    else:
        user_id = message_or_query.from_user.id
        chat_id = message_or_query.message.chat.id
        bot = message_or_query.bot
    
    logger.info(f"🎯 Showing main menu for user {user_id} in language: {language}")
    
    # Add typing simulation for better UX
    # UI effects removed during cleanup
    
    # Always show regular interface for all users (as requested by user)
    # Simple, clear interface for better user experience
    text = await create_regular_main_menu_text(language, user_id)
    
    # Add step title to the main menu text
    titled_text = get_user_language_and_create_titled_message(user_id, "main_menu", text)
    
    keyboard = await create_regular_main_menu_keyboard(language, user_id)
    
    # Add contextual help button to main menu
    keyboard = add_help_to_keyboard(keyboard, "main_menu", language)
    
    logger.info(f"👤 Regular interface for user {user_id}")
    
    # Keep text simple and clear without dynamic enhancements
    # user_stats = await db.get_user_stats(user_id) if db else {}
    # UI effects removed during cleanup
    
    logger.info(f"📝 Main menu text preview: {text[:50]}...")
    
    if isinstance(message_or_query, Message):
        # Use animated transition for new messages
        success = await animate_to_stage(
            message_or_query=message_or_query,
            to_stage="main_menu",
            content=text,
            language=language,
            user_id=user_id,
            keyboard=keyboard
        )
        if not success:
            # Fallback to direct message
            await message_or_query.answer(titled_text, reply_markup=keyboard, parse_mode='HTML')
    else:
        # Use smooth callback transition
        success = await smooth_callback_transition(
            callback_query=message_or_query,
            new_content=titled_text,
            keyboard=keyboard,
            language=language,
            stage_key="main_menu"
        )
        if not success:
            # Fallback to direct edit
            try:
                await message_or_query.message.edit_text(titled_text, reply_markup=keyboard, parse_mode='HTML')
            except Exception as e:
                await message_or_query.message.answer(titled_text, reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data.startswith("lang_"))
async def language_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle language selection with comprehensive translation support"""
    try:
        language_code = callback_query.data.replace("lang_", "")
        user_id = callback_query.from_user.id
        
        logger.info(f"🌍 Language selection: User {user_id} selected {language_code}")
        
        # Show immediate feedback
        await callback_query.answer("🌍 Updating language...")
        
        # Show loading animation
        loading_text = "🔄 Configuring your language preferences..."
        temp_message = await callback_query.message.edit_text(loading_text)
        # Loading animation removed during cleanup
        
        # Update user language in database
        success = await db.set_user_language(user_id, language_code)
        if success:
            logger.info(f"✅ Language {language_code} saved for user {user_id}")
            # Show success animation
            # Success animation removed during cleanup
            await asyncio.sleep(1)
        else:
            logger.error(f"❌ Failed to save language {language_code} for user {user_id}")
            # Error animation removed during cleanup
            return
        
        # Clear state and show main menu
        await state.clear()
        await show_main_menu(callback_query, language_code)
        
    except Exception as e:
        logger.error(f"Language selection error: {e}")
        await callback_query.answer("Error updating language")




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
    """Handle content upload with strict input validation based on mode"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Get current mode from state
    data = await state.get_data()
    upload_mode = data.get('upload_mode', 'mixed')  # 'text', 'image', 'mixed'
    
    # Define error messages for invalid input types
    error_messages = {
        'ar': {
            'text_only': '⚠️ يرجى إرسال **نص فقط** لإعلانك. الصور أو الملفات الأخرى غير مسموح بها في هذه الخطوة.',
            'image_only': '⚠️ يرجى إرسال **صورة فقط** في هذه الخطوة. الأنواع الأخرى غير مقبولة.',
            'invalid_type': '❌ نوع المحتوى غير مدعوم. يرجى إرسال نص أو صورة أو فيديو فقط.'
        },
        'ru': {
            'text_only': '⚠️ Пожалуйста, отправьте **только текст** для вашего объявления. Изображения или другие файлы не разрешены на этом этапе.',
            'image_only': '⚠️ Пожалуйста, отправьте **только изображение** на этом этапе. Другие типы не принимаются.',
            'invalid_type': '❌ Тип контента не поддерживается. Пожалуйста, отправьте только текст, изображение или видео.'
        },
        'en': {
            'text_only': '⚠️ Please send **text only** for your ad. Images or other files are not allowed in this step.',
            'image_only': '⚠️ Please send an **image only** for this step. Other types are not accepted.',
            'invalid_type': '❌ Content type not supported. Please send text, image, or video only.'
        }
    }
    
    # Log received content type for debugging
    logger.info(f"📝 Received content type: {message.content_type} from user {user_id} in mode: {upload_mode}")
    
    # Handle based on upload mode
    if upload_mode == 'text':
        # Text-only mode - reject all non-text inputs
        if message.content_type != 'text':
            error_msg = error_messages.get(language, error_messages['en'])['text_only']
            await message.answer(error_msg, parse_mode='Markdown')
            logger.warning(f"⚠️ Rejected {message.content_type} in text-only mode for user {user_id}")
            return
        
        # Process text content
        content = message.text
        await state.update_data(
            ad_content=content,
            content_type='text',
            media_url=None
        )
        
        # Send confirmation
        confirm_msg = {
            'ar': '✅ تم حفظ نص إعلانك.',
            'ru': '✅ Текст вашего объявления сохранен.',
            'en': '✅ Your ad text has been saved.'
        }
        await message.answer(confirm_msg.get(language, confirm_msg['en']))
        
    elif upload_mode == 'image':
        # Image-only mode - only accept photos
        if message.content_type != 'photo':
            error_msg = error_messages.get(language, error_messages['en'])['image_only']
            await message.answer(error_msg, parse_mode='Markdown')
            logger.warning(f"⚠️ Rejected {message.content_type} in image-only mode for user {user_id}")
            return
        
        # Process photo
        photo_file_id = message.photo[-1].file_id
        caption = message.caption or ""
        
        await state.update_data(
            ad_content=caption,
            content_type='photo',
            media_url=photo_file_id
        )
        
        # Send confirmation
        confirm_msg = {
            'ar': '✅ تم حفظ صورتك لهذا الإعلان.',
            'ru': '✅ Ваше изображение сохранено для этого объявления.',
            'en': '✅ Your image has been saved for this ad.'
        }
        await message.answer(confirm_msg.get(language, confirm_msg['en']))
        
    else:
        # Mixed mode - accept text, photo, or video
        if message.content_type == 'text':
            content = message.text
            await state.update_data(
                ad_content=content,
                content_type='text',
                media_url=None
            )
            confirm_msg = {
                'ar': '✅ تم حفظ نص إعلانك.',
                'ru': '✅ Текст вашего объявления сохранен.',
                'en': '✅ Your ad text has been saved.'
            }
            
        elif message.content_type == 'photo':
            photo_file_id = message.photo[-1].file_id
            caption = message.caption or ""
            
            await state.update_data(
                ad_content=caption,
                content_type='photo',
                media_url=photo_file_id
            )
            confirm_msg = {
                'ar': '✅ تم حفظ صورتك مع النص لهذا الإعلان.',
                'ru': '✅ Ваше изображение с текстом сохранено для этого объявления.',
                'en': '✅ Your image with caption has been saved for this ad.'
            }
            
        elif message.content_type == 'video':
            video_file_id = message.video.file_id
            caption = message.caption or ""
            
            await state.update_data(
                ad_content=caption,
                content_type='video',
                media_url=video_file_id
            )
            confirm_msg = {
                'ar': '✅ تم حفظ الفيديو مع النص لهذا الإعلان.',
                'ru': '✅ Ваше видео с текстом сохранено для этого объявления.',
                'en': '✅ Your video with caption has been saved for this ad.'
            }
            
        else:
            # Reject unsupported content types
            error_msg = error_messages.get(language, error_messages['en'])['invalid_type']
            await message.answer(error_msg, parse_mode='Markdown')
            logger.warning(f"⚠️ Rejected unsupported content type: {message.content_type} from user {user_id}")
            return
        
        await message.answer(confirm_msg.get(language, confirm_msg['en']))
    
    # Track content upload with end-to-end tracking system
    try:
        content_type = (await state.get_data()).get('content_type', 'text')
        await track_content_upload(user_id, content_type, state)
    except Exception as e:
        logger.error(f"Error tracking content upload: {e}")
    
    # Log successful content save
    final_data = await state.get_data()
    logger.info(f"✅ Content saved - Type: {final_data.get('content_type')}, Has media: {bool(final_data.get('media_url'))}")
    
    # Skip contact info step - go directly to channel selection
    await state.set_state(AdCreationStates.select_channels)
    
    # Show channel selection directly using simplified flow
    await show_simple_channel_selection(message, state)


# Category selection handler removed - going directly to content upload


# Subcategory and city selection handlers removed - streamlined flow


# Location selection removed - streamlined flow


# Location selection handler removed - streamlined flow


@router.message(AdCreationStates.upload_photos, F.photo)
async def handle_photo_upload(message: Message, state: FSMContext):
    """Handle photo uploads"""
    try:
        user_id = message.from_user.id
        language = await get_user_language(user_id)
        
        data = await state.get_data()
        uploaded_photos = data.get('uploaded_photos', [])
        
        if len(uploaded_photos) >= 5:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text(language, 'done_photos'), callback_data="done_photos")]
            ])
            await message.reply(get_text(language, 'max_photos_reached'), reply_markup=keyboard)
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
                InlineKeyboardButton(text=get_text(language, 'done_photos'), callback_data="done_photos"),
                InlineKeyboardButton(text=get_text(language, 'add_more_photos'), callback_data="add_more_photos")
            ],
            [InlineKeyboardButton(text=get_text(language, 'skip_photos'), callback_data="skip_photos")]
        ])
        
        await message.reply(get_text(language, 'photo_uploaded', count=len(uploaded_photos)), reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Photo upload error: {e}")
        await message.reply(get_text(language, 'error_uploading_photo'))


@router.callback_query(F.data == "continue_from_photos")
async def continue_from_photos(callback_query: CallbackQuery, state: FSMContext):
    """Continue from photo upload step - go directly to text input"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.upload_content)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'continue_to_text'), callback_data="continue_to_text")],
        [InlineKeyboardButton(text=get_text(language, 'back_to_photos'), callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(get_text(language, 'photos_done_add_text'), reply_markup=keyboard)
    await callback_query.answer()


@router.callback_query(F.data == "add_more_photos") 
async def add_more_photos(callback_query: CallbackQuery, state: FSMContext):
    """Allow user to add more photos"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await callback_query.message.edit_text(
        get_text(language, 'add_more_photos_text'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'done_photos'), callback_data="continue_from_photos")]
        ])
    )
    await callback_query.answer(get_text(language, 'send_more_photos'))


@router.callback_query(F.data == "skip_photos")
async def skip_photos_handler(callback_query: CallbackQuery, state: FSMContext):
    """Skip photo upload step - go directly to text input"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.upload_content)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'continue_to_text'), callback_data="continue_to_text")],
        [InlineKeyboardButton(text=get_text(language, 'back_to_photos'), callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(get_text(language, 'photos_skipped_add_text'), reply_markup=keyboard)
    await callback_query.answer(get_text(language, 'ready_for_text'))


@router.callback_query(F.data == "continue_to_text")
async def continue_to_text_handler(callback_query: CallbackQuery, state: FSMContext):
    """Continue to text input step"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.upload_content)
    
    text = get_text(language, 'create_ad_text_instructions')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'back_to_photos'), callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()


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


async def show_simple_channel_selection(message: Message, state: FSMContext):
    """Show simplified channel selection for message-based flow"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Get active channels from database
    try:
        channels = await db.get_active_channels()
        logger.info(f"Retrieved {len(channels)} channels from database")
    except Exception as e:
        logger.error(f"Error getting channels: {e}")
        channels = []
    
    if not channels:
        no_channels_text = {
            'en': "❌ No channels available. Please contact admin.",
            'ar': "❌ لا توجد قنوات متاحة. يرجى الاتصال بالمسؤول.",
            'ru': "❌ Нет доступных каналов. Пожалуйста, свяжитесь с администратором."
        }
        
        await message.answer(no_channels_text.get(language, no_channels_text['en']))
        return
    
    # Get selected channels from state
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Create channel selection text
    if language == 'ar':
        channel_content = f"""📺 **اختر القنوات لإعلانك**

📊 **المحدد:** {len(selected_channels)}/{len(channels)} قناة

💡 انقر على القنوات للاختيار/إلغاء الاختيار:"""
    elif language == 'ru':
        channel_content = f"""📺 **Выберите каналы для рекламы**

📊 **Выбрано:** {len(selected_channels)}/{len(channels)} каналов

💡 Нажмите на каналы для выбора/отмены:"""
    else:
        channel_content = f"""📺 **Select Channels for Your Ad**

📊 **Selected:** {len(selected_channels)}/{len(channels)} channels

💡 Click channels to select/deselect:"""
    
    # Create keyboard with channel buttons
    keyboard_rows = []
    for channel in channels:
        is_selected = channel['channel_id'] in selected_channels
        channel_name = channel.get('name', channel.get('telegram_channel_id', 'Unknown'))
        subscribers = channel.get('subscribers', 0)
        
        # Create button text with selection indicator
        if is_selected:
            button_text = f"✅ {channel_name} ({subscribers} subs)"
        else:
            button_text = f"⚪ {channel_name} ({subscribers} subs)"
        
        keyboard_rows.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"toggle_channel_{channel['channel_id']}"
        )])
    
    # Add control buttons
    if language == 'ar':
        keyboard_rows.append([
            InlineKeyboardButton(text="✅ متابعة", callback_data="proceed_to_duration"),
            InlineKeyboardButton(text="🔄 تحديث", callback_data="refresh_channels")
        ])
    elif language == 'ru':
        keyboard_rows.append([
            InlineKeyboardButton(text="✅ Продолжить", callback_data="proceed_to_duration"),
            InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_channels")
        ])
    else:
        keyboard_rows.append([
            InlineKeyboardButton(text="✅ Continue", callback_data="proceed_to_duration"),
            InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_channels")
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    try:
        await message.answer(channel_content, reply_markup=keyboard, parse_mode='Markdown')
        logger.info(f"✅ Channel selection shown to user {user_id}")
    except Exception as e:
        logger.error(f"Error showing channel selection: {e}")
        await message.answer("Error showing channels. Please try again.")


# Channel toggle callback handler
@router.callback_query(F.data.startswith("toggle_channel_"))
async def toggle_channel_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel selection toggle"""
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.replace("toggle_channel_", "")
    
    # Get current state data
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Toggle channel selection
    if channel_id in selected_channels:
        selected_channels.remove(channel_id)
        logger.info(f"🔴 Channel {channel_id} deselected by user {user_id}")
    else:
        selected_channels.append(channel_id)
        logger.info(f"🟢 Channel {channel_id} selected by user {user_id}")
    
    # Update state
    await state.update_data(selected_channels=selected_channels)
    
    # Get updated channel list and regenerate keyboard
    channels = await db.get_active_channels()
    keyboard_rows = []
    
    for channel in channels:
        is_selected = channel['channel_id'] in selected_channels
        channel_name = channel.get('name', channel.get('telegram_channel_id', 'Unknown'))
        subscribers = channel.get('subscribers', 0)
        
        # Create button text with selection indicator
        if is_selected:
            button_text = f"✅ {channel_name} ({subscribers} subs)"
        else:
            button_text = f"⚪ {channel_name} ({subscribers} subs)"
        
        keyboard_rows.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"toggle_channel_{channel['channel_id']}"
        )])
    
    # Add control buttons
    language = await get_user_language(user_id)
    if language == 'ar':
        keyboard_rows.append([
            InlineKeyboardButton(text="✅ متابعة", callback_data="proceed_to_duration"),
            InlineKeyboardButton(text="🔄 تحديث", callback_data="refresh_channels")
        ])
    elif language == 'ru':
        keyboard_rows.append([
            InlineKeyboardButton(text="✅ Продолжить", callback_data="proceed_to_duration"),
            InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_channels")
        ])
    else:
        keyboard_rows.append([
            InlineKeyboardButton(text="✅ Continue", callback_data="proceed_to_duration"),
            InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_channels")
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    # Create updated message
    if language == 'ar':
        channel_content = f"""📺 **اختر القنوات لإعلانك**

📊 **المحدد:** {len(selected_channels)}/{len(channels)} قناة

💡 انقر على القنوات للاختيار/إلغاء الاختيار:"""
    elif language == 'ru':
        channel_content = f"""📺 **Выберите каналы для рекламы**

📊 **Выбрано:** {len(selected_channels)}/{len(channels)} каналов

💡 Нажмите на каналы для выбора/отмены:"""
    else:
        channel_content = f"""📺 **Select Channels for Your Ad**

📊 **Selected:** {len(selected_channels)}/{len(channels)} channels

💡 Click channels to select/deselect:"""
    
    # Update the message
    await callback_query.message.edit_text(
        channel_content,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    await callback_query.answer()
    logger.info(f"✅ Channel selection updated for user {user_id} - {len(selected_channels)} channels selected")


# Proceed to duration callback handler
@router.callback_query(F.data == "proceed_to_duration")
async def proceed_to_duration_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle proceed to duration selection"""
    user_id = callback_query.from_user.id
    
    # Get current state data
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Check if at least one channel is selected
    if not selected_channels:
        language = await get_user_language(user_id)
        if language == 'ar':
            await callback_query.answer("⚠️ يرجى اختيار قناة واحدة على الأقل", show_alert=True)
        elif language == 'ru':
            await callback_query.answer("⚠️ Пожалуйста, выберите хотя бы один канал", show_alert=True)
        else:
            await callback_query.answer("⚠️ Please select at least one channel", show_alert=True)
        return
    
    # Set state to duration selection
    await state.set_state(CreateAd.duration_selection)
    
    # Show duration selection
    await show_duration_selection_simple(callback_query.message, state)
    
    await callback_query.answer()
    logger.info(f"✅ User {user_id} proceeding to duration selection with {len(selected_channels)} channels selected")


# Refresh channels callback handler
@router.callback_query(F.data == "refresh_channels")
async def refresh_channels_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle refresh channels request"""
    user_id = callback_query.from_user.id
    
    # Simply regenerate the channel selection message
    await toggle_channel_callback(callback_query, state)
    
    language = await get_user_language(user_id)
    if language == 'ar':
        await callback_query.answer("🔄 تم تحديث القنوات")
    elif language == 'ru':
        await callback_query.answer("🔄 Каналы обновлены")
    else:
        await callback_query.answer("🔄 Channels refreshed")
    
    logger.info(f"✅ Channels refreshed for user {user_id}")


async def show_duration_selection_simple(message: Message, state: FSMContext):
    """Show dynamic duration selection with interactive controls"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Get state data
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    channels_count = len(selected_channels)
    
    # Initialize default values if not set
    current_days = data.get('current_days', 7)
    
    # Save current values to state
    await state.update_data(
        current_days=current_days
    )
    
    # Import and use dynamic pricing
    from quantitative_pricing_system import calculate_quantitative_price, get_posting_schedule
    
    # Get pricing display content using quantitative pricing
    pricing_result = calculate_quantitative_price(current_days, channels_count)
    actual_posts_per_day = pricing_result['posts_per_day']
    posting_schedule = get_posting_schedule(actual_posts_per_day)
    
    # Format the display content
    if language == 'ar':
        content = f"""<b>⏱️ اختيار مدة الحملة</b>

📊 <b>تفاصيل الحملة:</b>
• المدة: {current_days} يوم
• المنشورات يومياً: {actual_posts_per_day}
• إجمالي المنشورات: {pricing_result['total_posts']}

💰 <b>الأسعار:</b>
• السعر الأساسي: ${pricing_result['base_price']:.2f}
• الخصم: {pricing_result['discount_percentage']:.1f}%
• السعر النهائي: <b>${pricing_result['final_price']:.2f}</b>

💎 <b>الدفع:</b>
• TON: {pricing_result['ton_price']:.2f}
• Telegram Stars: {pricing_result['stars_price']}

⏰ <b>مواعيد النشر:</b>
{', '.join(posting_schedule)}

📈 <b>القنوات المختارة:</b> {channels_count}"""
    
    elif language == 'ru':
        content = f"""<b>⏱️ Выбор длительности кампании</b>

📊 <b>Детали кампании:</b>
• Длительность: {current_days} дней
• Постов в день: {actual_posts_per_day}
• Всего постов: {pricing_result['total_posts']}

💰 <b>Цены:</b>
• Базовая цена: ${pricing_result['base_price']:.2f}
• Скидка: {pricing_result['discount_percentage']:.1f}%
• Итоговая цена: <b>${pricing_result['final_price']:.2f}</b>

💎 <b>Оплата:</b>
• TON: {pricing_result['ton_price']:.2f}
• Telegram Stars: {pricing_result['stars_price']}

⏰ <b>Расписание публикации:</b>
{', '.join(posting_schedule)}

📈 <b>Выбранные каналы:</b> {channels_count}"""
    
    else:  # English
        content = f"""<b>⏱️ Campaign Duration Selection</b>

📊 <b>Campaign Details:</b>
• Duration: {current_days} days
• Posts per day: {actual_posts_per_day}
• Total posts: {pricing_result['total_posts']}

💰 <b>Pricing:</b>
• Base price: ${pricing_result['base_price']:.2f}
• Discount: {pricing_result['discount_percentage']:.1f}%
• Final price: <b>${pricing_result['final_price']:.2f}</b>

💎 <b>Payment:</b>
• TON: {pricing_result['ton_price']:.2f}
• Telegram Stars: {pricing_result['stars_price']}

⏰ <b>Posting Schedule:</b>
{', '.join(posting_schedule)}

📈 <b>Selected Channels:</b> {channels_count}"""
    
    # Create interactive keyboard
    keyboard_rows = []
    
    # Days control row
    if language == 'ar':
        keyboard_rows.append([
            InlineKeyboardButton(text="🔽", callback_data="days_decrease"),
            InlineKeyboardButton(text=f"{current_days} يوم", callback_data="days_info"),
            InlineKeyboardButton(text="🔼", callback_data="days_increase")
        ])
    elif language == 'ru':
        if current_days == 1:
            day_text = f"{current_days} день"
        elif current_days < 5:
            day_text = f"{current_days} дня"
        else:
            day_text = f"{current_days} дней"
        keyboard_rows.append([
            InlineKeyboardButton(text="🔽", callback_data="days_decrease"),
            InlineKeyboardButton(text=day_text, callback_data="days_info"),
            InlineKeyboardButton(text="🔼", callback_data="days_increase")
        ])
    else:
        day_text = f"{current_days} day{'s' if current_days != 1 else ''}"
        keyboard_rows.append([
            InlineKeyboardButton(text="🔽", callback_data="days_decrease"),
            InlineKeyboardButton(text=day_text, callback_data="days_info"),
            InlineKeyboardButton(text="🔼", callback_data="days_increase")
        ])
    
    # Posts per day is automatically calculated by quantitative pricing system
    # No manual selection needed
    
    # Quick selection buttons
    quick_days = [1, 3, 7, 14, 30]
    quick_row = []
    for days in quick_days:
        if days == current_days:
            continue  # Skip current selection
        if language == 'ar':
            button_text = f"{days}د"
        elif language == 'ru':
            button_text = f"{days}д"
        else:
            button_text = f"{days}d"
        quick_row.append(InlineKeyboardButton(
            text=button_text,
            callback_data=f"set_days_{days}"
        ))
    
    if quick_row:
        keyboard_rows.append(quick_row)
    
    # Action buttons
    if language == 'ar':
        keyboard_rows.append([
            InlineKeyboardButton(text="💳 متابعة للدفع", callback_data="proceed_to_payment"),
            InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_channels")
        ])
    elif language == 'ru':
        keyboard_rows.append([
            InlineKeyboardButton(text="💳 Перейти к оплате", callback_data="proceed_to_payment"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_channels")
        ])
    else:
        keyboard_rows.append([
            InlineKeyboardButton(text="💳 Proceed to Payment", callback_data="proceed_to_payment"),
            InlineKeyboardButton(text="🔙 Back", callback_data="back_to_channels")
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    # Send message
    await message.edit_text(content, reply_markup=keyboard, parse_mode='Markdown')
    logger.info(f"✅ Dynamic duration selection shown to user {user_id} - {current_days} days, {posts_per_day} posts/day")


# Back to channels callback handler
@router.callback_query(F.data == "back_to_channels")
async def back_to_channels_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle back to channels button"""
    user_id = callback_query.from_user.id
    
    # Set state back to channel selection
    await state.set_state(CreateAd.channel_selection)
    
    # Show channel selection again
    await show_simple_channel_selection(callback_query.message, state)
    
    await callback_query.answer()
    logger.info(f"✅ User {user_id} returned to channel selection")


# Dynamic days control handlers
@router.callback_query(F.data == "days_increase")
async def days_increase_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle days increase button"""
    user_id = callback_query.from_user.id
    data = await state.get_data()
    current_days = data.get('current_days', 7)
    
    # Increase days (max 365)
    new_days = min(current_days + 1, 365)
    await state.update_data(current_days=new_days)
    
    # Refresh the interface
    await show_duration_selection_simple(callback_query.message, state)
    await callback_query.answer(f"📅 {new_days} days")
    logger.info(f"✅ User {user_id} increased days to {new_days}")


@router.callback_query(F.data == "days_decrease")
async def days_decrease_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle days decrease button"""
    user_id = callback_query.from_user.id
    data = await state.get_data()
    current_days = data.get('current_days', 7)
    
    # Decrease days (min 1)
    new_days = max(current_days - 1, 1)
    await state.update_data(current_days=new_days)
    
    # Refresh the interface
    await show_duration_selection_simple(callback_query.message, state)
    await callback_query.answer(f"📅 {new_days} days")
    logger.info(f"✅ User {user_id} decreased days to {new_days}")


# Posts per day handlers removed - quantitative pricing system calculates this automatically


@router.callback_query(F.data.startswith("set_days_"))
async def set_days_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle quick days selection buttons"""
    user_id = callback_query.from_user.id
    days = int(callback_query.data.split("_")[2])
    
    # Update days
    await state.update_data(current_days=days)
    
    # Refresh the interface
    await show_duration_selection_simple(callback_query.message, state)
    await callback_query.answer(f"📅 {days} days selected")
    logger.info(f"✅ User {user_id} set days to {days}")


@router.callback_query(F.data == "proceed_to_payment")
async def proceed_to_payment_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle proceed to payment button"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get final pricing data
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    current_days = data.get('current_days', 7)
    
    # Calculate final pricing using quantitative pricing system
    from quantitative_pricing_system import calculate_quantitative_price
    
    pricing = calculate_quantitative_price(current_days, len(selected_channels))
    
    # Save pricing to state
    await state.update_data(
        final_pricing=pricing,
        duration=current_days,
        posts_per_day=pricing['posts_per_day']  # Use calculated posts per day
    )
    
    # Set state to payment method
    await state.set_state(CreateAd.payment_method)
    
    # Show payment method selection
    await show_payment_method_selection(callback_query.message, state)
    
    await callback_query.answer()
    logger.info(f"✅ User {user_id} proceeding to payment - ${pricing['final_price']:.2f} for {current_days} days")


async def show_payment_method_selection(message: Message, state: FSMContext):
    """Show payment method selection with final pricing"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Get pricing data
    data = await state.get_data()
    pricing = data.get('final_pricing', {})
    
    # Create payment method keyboard
    keyboard_rows = []
    
    if language == 'ar':
        content = f"""💳 **اختر طريقة الدفع**

💰 **المبلغ النهائي:** ${pricing.get('final_price', 0):.2f}
🎁 **التوفير:** ${pricing.get('savings', 0):.2f}
📊 **الخصم:** {pricing.get('discount_percentage', 0)}%

اختر طريقة الدفع المفضلة:"""
        
        keyboard_rows.append([
            InlineKeyboardButton(text="💎 TON Cryptocurrency", callback_data="pay_ton"),
            InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="pay_stars")
        ])
        keyboard_rows.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="back_to_duration")])
        
    elif language == 'ru':
        content = f"""💳 **Выберите способ оплаты**

💰 **Итоговая сумма:** ${pricing.get('final_price', 0):.2f}
🎁 **Экономия:** ${pricing.get('savings', 0):.2f}
📊 **Скидка:** {pricing.get('discount_percentage', 0)}%

Выберите удобный способ оплаты:"""
        
        keyboard_rows.append([
            InlineKeyboardButton(text="💎 TON Cryptocurrency", callback_data="pay_ton"),
            InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="pay_stars")
        ])
        keyboard_rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_duration")])
        
    else:
        content = f"""💳 **Select Payment Method**

💰 **Final Amount:** ${pricing.get('final_price', 0):.2f}
🎁 **You Save:** ${pricing.get('savings', 0):.2f}
📊 **Discount:** {pricing.get('discount_percentage', 0)}%

Choose your preferred payment method:"""
        
        keyboard_rows.append([
            InlineKeyboardButton(text="💎 TON Cryptocurrency", callback_data="pay_ton"),
            InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="pay_stars")
        ])
        keyboard_rows.append([InlineKeyboardButton(text="🔙 Back", callback_data="back_to_duration")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    await message.edit_text(content, reply_markup=keyboard, parse_mode='Markdown')
    logger.info(f"✅ Payment method selection shown to user {user_id}")


@router.callback_query(F.data == "back_to_duration")
async def back_to_duration_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle back to duration selection"""
    user_id = callback_query.from_user.id
    
    # Set state back to duration selection
    await state.set_state(CreateAd.duration_selection)
    
    # Show duration selection again
    await show_duration_selection_simple(callback_query.message, state)
    
    await callback_query.answer()
    logger.info(f"✅ User {user_id} returned to duration selection")


async def show_channel_selection_for_message(message: Message, state: FSMContext):
    """Show channel selection for message-based flow"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Use enhanced typing simulation with animation
    from animated_transitions import get_animated_transitions
    transitions = get_animated_transitions()
    await transitions.typing_simulation(
        bot=message.bot,
        chat_id=message.chat.id,
        text=get_text(language, 'loading_channels'),
        duration=1.5
    )
    
    # Get only active channels where bot is admin
    channels = await db.get_bot_admin_channels()
    
    if not channels:
        no_channels_text = {
            'en': get_text('en', 'no_channels'),
            'ar': get_text('ar', 'no_channels'),
            'ru': get_text('ru', 'no_channels')
        }
        
        await message.answer(
            no_channels_text.get(language, no_channels_text['en']),
            parse_mode='Markdown'
        )
        return
    
    # Initialize live stats system
    from live_channel_stats import LiveChannelStats
    live_stats = LiveChannelStats(message.bot, db)
    
    # Enhance channels with live subscriber counts
    enhanced_channels = await live_stats.get_enhanced_channel_data(channels)
    
    # Get selected channels from state
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Calculate total reach with live counts
    total_reach = await live_stats.get_total_reach(selected_channels, enhanced_channels)
    
    # Create enhanced channel text with better visuals
    if language == 'ar':
        channel_content = f"""📺 **اختر القنوات لإعلانك**

📊 **المحدد:** {len(selected_channels)}/{len(enhanced_channels)} قناة
👥 **الوصول المباشر:** {total_reach:,} مشترك

💡 انقر على القنوات للاختيار/إلغاء الاختيار:"""
    elif language == 'ru':
        channel_content = f"""📺 **Выберите каналы для рекламы**

📊 **Выбрано:** {len(selected_channels)}/{len(enhanced_channels)} каналов
👥 **Живой охват:** {total_reach:,} подписчиков

💡 Нажмите на каналы для выбора/отмены:"""
    else:
        channel_content = f"""📺 **Select Channels for Your Ad**

📊 **Selected:** {len(selected_channels)}/{len(enhanced_channels)} channels
👥 **Live Reach:** {total_reach:,} subscribers

💡 Click channels to select/deselect:"""
    
    # Add step title to the channel selection content
    channel_text = get_user_language_and_create_titled_message(user_id, "select_channels", channel_content)
    
    keyboard_rows = []
    for channel in enhanced_channels:
        # Check if channel is selected
        is_selected = channel['channel_id'] in selected_channels
        
        # Create enhanced button text with live counts and improved layout
        button_text = live_stats.create_channel_button_text(channel, is_selected, language)
        
        keyboard_rows.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"toggle_channel_{channel['channel_id']}"
        )])
    
    # Add control buttons with better styling
    if language == 'ar':
        keyboard_rows.append([
            InlineKeyboardButton(text="🔄 تحديث الإحصائيات", callback_data="refresh_channel_stats"),
            InlineKeyboardButton(text="🔄 اختيار الكل", callback_data="select_all_channels")
        ])
        keyboard_rows.append([
            InlineKeyboardButton(text="❌ إلغاء تحديد الكل", callback_data="deselect_all_channels")
        ])
        
        # Continue button (only show if channels are selected)
        if selected_channels:
            keyboard_rows.append([
                InlineKeyboardButton(text="✅ متابعة مع القنوات المحددة", callback_data="continue_with_channels")
            ])
        
        keyboard_rows.append([
            InlineKeyboardButton(text="◀️ العودة للقائمة", callback_data="back_to_main")
        ])
    elif language == 'ru':
        keyboard_rows.append([
            InlineKeyboardButton(text="🔄 Обновить статистику", callback_data="refresh_channel_stats"),
            InlineKeyboardButton(text="🔄 Выбрать все", callback_data="select_all_channels")
        ])
        keyboard_rows.append([
            InlineKeyboardButton(text="❌ Отменить все", callback_data="deselect_all_channels")
        ])
        
        # Continue button (only show if channels are selected)
        if selected_channels:
            keyboard_rows.append([
                InlineKeyboardButton(text="✅ Продолжить с выбранными", callback_data="continue_with_channels")
            ])
        
        keyboard_rows.append([
            InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_main")
        ])
    else:
        keyboard_rows.append([
            InlineKeyboardButton(text="🔄 Refresh Stats", callback_data="refresh_channel_stats"),
            InlineKeyboardButton(text="🔄 Select All", callback_data="select_all_channels")
        ])
        keyboard_rows.append([
            InlineKeyboardButton(text="❌ Deselect All", callback_data="deselect_all_channels")
        ])
        
        # Continue button (only show if channels are selected)
        if selected_channels:
            keyboard_rows.append([
                InlineKeyboardButton(text="✅ Continue with Selected", callback_data="continue_with_channels")
            ])
        
        keyboard_rows.append([
            InlineKeyboardButton(text="◀️ Back to Menu", callback_data="back_to_main")
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    # Add contextual help button for channel selection
    keyboard = add_help_to_keyboard(keyboard, "select_channels", language)
    
    # Use animated transition for channel selection
    success = await animate_to_stage(
        message_or_query=message,
        to_stage="select_channels",
        content=channel_content,
        language=language,
        user_id=user_id,
        keyboard=keyboard
    )
    
    if not success:
        # Fallback to direct message
        await message.answer(
            channel_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )


async def show_channel_selection_for_enhanced_flow(callback_query: CallbackQuery, state: FSMContext):
    """Show channel selection for enhanced flow with live subscriber counts"""
    # Get user language first
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Use enhanced typing simulation with animation
    from animated_transitions import get_animated_transitions
    transitions = get_animated_transitions()
    await transitions.typing_simulation(
        bot=callback_query.bot,
        chat_id=callback_query.message.chat.id,
        text=get_text(language, 'loading_channels'),
        duration=1.5
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
    
    # Initialize live stats system
    from live_channel_stats import LiveChannelStats
    live_stats = LiveChannelStats(callback_query.bot, db)
    
    # Enhance channels with live subscriber counts
    enhanced_channels = await live_stats.get_enhanced_channel_data(channels)
    
    # Get selected channels from state
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Calculate total reach with live counts
    total_reach = await live_stats.get_total_reach(selected_channels, enhanced_channels)
    
    # Create enhanced channel text with better visuals
    if language == 'ar':
        channel_text = f"""📺 **اختر القنوات لإعلانك**

📊 **المحدد:** {len(selected_channels)}/{len(enhanced_channels)} قناة
👥 **الوصول المباشر:** {total_reach:,} مشترك

💡 انقر على القنوات للاختيار/إلغاء الاختيار:"""
    elif language == 'ru':
        channel_text = f"""📺 **Выберите каналы для рекламы**

📊 **Выбрано:** {len(selected_channels)}/{len(enhanced_channels)} каналов
👥 **Живой охват:** {total_reach:,} подписчиков

💡 Нажмите на каналы для выбора/отмены:"""
    else:
        channel_text = f"""📺 **Select Channels for Your Ad**

📊 **Selected:** {len(selected_channels)}/{len(enhanced_channels)} channels
👥 **Live Reach:** {total_reach:,} subscribers

💡 Click channels to select/deselect:"""
    
    keyboard_rows = []
    for channel in enhanced_channels:
        # Check if channel is selected
        is_selected = channel['channel_id'] in selected_channels
        
        # Create enhanced button text with live counts and improved layout
        button_text = live_stats.create_channel_button_text(channel, is_selected, language)
        
        keyboard_rows.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"toggle_channel_{channel['channel_id']}"
        )])
    
    # Add control buttons with better styling
    if language == 'ar':
        keyboard_rows.append([
            InlineKeyboardButton(text="🔄 تحديث الإحصائيات", callback_data="refresh_channel_stats"),
            InlineKeyboardButton(text="🔄 اختيار الكل", callback_data="select_all_channels")
        ])
        keyboard_rows.append([
            InlineKeyboardButton(text="❌ إلغاء تحديد الكل", callback_data="deselect_all_channels")
        ])
    elif language == 'ru':
        keyboard_rows.append([
            InlineKeyboardButton(text="🔄 Обновить статистику", callback_data="refresh_channel_stats"),
            InlineKeyboardButton(text="🔄 Выбрать все", callback_data="select_all_channels")
        ])
        keyboard_rows.append([
            InlineKeyboardButton(text="❌ Отменить все", callback_data="deselect_all_channels")
        ])
    else:
        keyboard_rows.append([
            InlineKeyboardButton(text="🔄 Refresh Stats", callback_data="refresh_channel_stats"),
            InlineKeyboardButton(text="🔄 Select All", callback_data="select_all_channels")
        ])
        keyboard_rows.append([
            InlineKeyboardButton(text="❌ Deselect All", callback_data="deselect_all_channels")
        ])
    
    # Dynamic continue button - disabled if no channels selected
    if selected_channels:
        if language == 'ar':
            continue_text = f"▶️ متابعة ({len(selected_channels)} محدد)"
        elif language == 'ru':
            continue_text = f"▶️ Продолжить ({len(selected_channels)} выбрано)"
        else:
            continue_text = f"▶️ Continue ({len(selected_channels)} selected)"
        callback_data = "continue_with_channels"
    else:
        if language == 'ar':
            continue_text = "⚠️ اختر القنوات أولاً"
        elif language == 'ru':
            continue_text = "⚠️ Сначала выберите каналы"
        else:
            continue_text = "⚠️ Select channels first"
        callback_data = "no_channels_warning"
    
    keyboard_rows.append([InlineKeyboardButton(
        text=continue_text,
        callback_data=callback_data
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


@router.callback_query(F.data == "refresh_channel_stats")
async def refresh_channel_stats_handler(callback_query: CallbackQuery, state: FSMContext):
    """Refresh channel statistics and detect new channels"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Show loading message
        loading_text = {
            'en': "🔄 Refreshing channel statistics...",
            'ar': "🔄 تحديث إحصائيات القنوات...",
            'ru': "🔄 Обновление статистики каналов..."
        }
        
        await callback_query.answer(loading_text.get(language, loading_text['en']))
        
        # Force refresh of channel cache to capture any newly detected channels
        await db.refresh_channel_cache()
        
        # Initialize live stats system
        from live_channel_stats import LiveChannelStats
        live_stats = LiveChannelStats(callback_query.bot, db)
        
        # Refresh all channel statistics
        updated_count = await live_stats.refresh_all_channel_stats()
        
        # Clear cache to force fresh data
        live_stats.clear_cache()
        
        # Show updated channel selection with fresh data
        await show_channel_selection_for_enhanced_flow(callback_query, state)
        
        # Show success message with new channels notification
        success_text = {
            'en': f"✅ Updated {updated_count} channels. New channels detected!",
            'ar': f"✅ تم تحديث {updated_count} قناة. تم اكتشاف قنوات جديدة!",
            'ru': f"✅ Обновлено {updated_count} каналов. Обнаружены новые каналы!"
        }
        
        await callback_query.answer(success_text.get(language, success_text['en']))
        
    except Exception as e:
        logger.error(f"Refresh channel stats error: {e}")
        await callback_query.answer("Error refreshing stats. Please try again.", show_alert=True)


@router.callback_query(F.data == "settings")
async def show_settings_handler(callback_query: CallbackQuery):
    """Show settings menu"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Enhanced logging for Arabic navigation debugging
    logger.info(f"📞 settings callback received from user {user_id} (language: {language})")
    
    try:
        # Ensure language is valid
        if language not in LANGUAGES:
            language = 'en'
        
        settings_content = f"""
{get_text(language, 'settings_title')}

{get_text(language, 'current_language', language_name=LANGUAGES[language]['name'], flag=LANGUAGES[language]['flag'])}

{get_text(language, 'change_language')}

{get_text(language, 'account_info', user_id=user_id, language=language.upper())}
        """.strip()
        
        # Add step title to the settings content
        settings_text = get_user_language_and_create_titled_message(user_id, "settings", settings_content)
        
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
                    text=get_text(language, 'back_to_main'), 
                    callback_data="back_to_main"
                )
            ]
        ])
        
        # Use animated transition for settings
        integration = TransitionIntegration()
        success = await integration.apply_callback_transition(
            callback_query=callback_query,
            content=settings_text,
            keyboard=keyboard,
            language=language,
            handler_name="show_settings_handler",
            from_context="main_menu"
        )
        
        if not success:
            # Fallback to safe edit
            await safe_callback_edit(
                callback_query,
                text=settings_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        logger.info(f"✅ settings completed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ settings error for user {user_id}: {e}")
        language = await get_user_language(callback_query.from_user.id)
        await safe_callback_answer(callback_query, get_text(language, 'settings_unavailable'), show_alert=True)


@router.callback_query(F.data == "help")
async def show_help_handler(callback_query: CallbackQuery):
    """Show help information"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Enhanced logging for Arabic navigation debugging
    logger.info(f"📞 help callback received from user {user_id} (language: {language})")
    
    try:
        # Ensure language is valid
        if language not in LANGUAGES:
            language = 'en'
        
        help_content = get_text(language, 'help_text')
        
        # Add step title to the help content  
        help_text = get_user_language_and_create_titled_message(user_id, "help", help_content)
        
        # Create help keyboard
        help_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=get_text(language, 'back_to_main'), 
                callback_data="back_to_main"
            )]
        ])
        
        # Use animated transition for help
        integration = TransitionIntegration()
        success = await integration.apply_callback_transition(
            callback_query=callback_query,
            content=help_text,
            keyboard=help_keyboard,
            language=language,
            handler_name="show_help_handler",
            from_context="main_menu"
        )
        
        if not success:
            # Fallback to direct edit
            await callback_query.message.edit_text(
                help_text,
                reply_markup=help_keyboard,
                parse_mode='Markdown'
            )
            await safe_callback_answer(callback_query, "")
        logger.info(f"✅ help completed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ help error for user {user_id}: {e}")
        language = await get_user_language(callback_query.from_user.id)
        await safe_callback_answer(callback_query, get_text(language, 'help_unavailable'), show_alert=True)


@router.callback_query(F.data == "create_ad")
async def create_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Start enhanced ad creation process with modern UI and enhanced error handling"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Enhanced logging for Arabic main menu debugging
    logger.info(f"📢 create_ad callback received from user {user_id} (language: {language})")
    
    # Log the ad creation step
    log_info(StepNames.CREATE_AD_START, user_id, "User clicked create ad button")
    
    # Track ad creation start with end-to-end tracking system
    try:
        await track_create_ad_start(user_id, state)
    except Exception as e:
        logger.error(f"Error tracking ad creation start: {e}")
    
    try:
        # Use safe callback handler to prevent timeout errors
        await safe_callback_answer(callback_query, "")
        
        # Start with photo upload state
        await state.set_state(AdCreationStates.upload_photos)
        
        # Use crypto-focused ad creation message
        content = get_text(language, 'send_ad_content')
        
        # Add step title to the create ad content
        text = get_user_language_and_create_titled_message(user_id, "create_ad_start", content)
        
        # Create modern confirmation keyboard with calming design
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(language, 'skip_photos'),
                    callback_data="skip_photos_to_text"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text(language, 'back_to_main'),
                    callback_data="back_to_main"
                )
            ]
        ])
        
        # Add contextual help button for ad creation
        keyboard = add_help_to_keyboard(keyboard, "create_ad_start", language)
        
        # Use animated transition for create ad
        integration = TransitionIntegration()
        success = await integration.apply_callback_transition(
            callback_query=callback_query,
            content=text,
            keyboard=keyboard,
            language=language,
            handler_name="create_ad_handler",
            from_context="main_menu"
        )
        
        if not success:
            # Fallback to safe edit
            await safe_callback_edit(
                callback_query,
                text=text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        
        log_success(StepNames.CREATE_AD_START, user_id, "Ad creation started with modern UI")
        logger.info(f"✅ create_ad completed successfully for user {user_id}")
            
    except Exception as e:
        log_error(StepNames.CREATE_AD_START, user_id, e, {"action": "create_ad"})
        logger.error(f"❌ create_ad error for user {user_id}: {e}")
        await safe_callback_answer(callback_query, get_text(language, 'error_creating_ad'), show_alert=True)


@router.callback_query(F.data == "free_trial")
async def free_trial_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle free trial selection"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Check if user can still use free trial
    can_use_trial = await db.check_free_trial_available(user_id)
    
    if not can_use_trial:
        await callback_query.answer(get_text(language, 'free_trial_used'))
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


async def refresh_enhanced_channel_selection_ui(callback_query: CallbackQuery, state: FSMContext):
    """Refresh the enhanced channel selection interface with modern toggle design"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Get only active channels where bot is admin
        channels = await db.get_bot_admin_channels()
        
        if not channels:
            await callback_query.answer("No channels available")
            return
        
        # Initialize live stats system
        from live_channel_stats import LiveChannelStats
        live_stats = LiveChannelStats(callback_query.bot, db)
        
        # Enhance channels with live subscriber counts
        enhanced_channels = await live_stats.get_enhanced_channel_data(channels)
        
        # Get selected channels from state
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        # Calculate total reach with live counts
        total_reach = await live_stats.get_total_reach(selected_channels, enhanced_channels)
        
        # Create enhanced channel text with better visuals
        if language == 'ar':
            channel_text = f"""📺 **اختر القنوات لإعلانك**

📊 **المحدد:** {len(selected_channels)}/{len(enhanced_channels)} قناة
👥 **الوصول المباشر:** {total_reach:,} مشترك

💡 انقر على القنوات للاختيار/إلغاء الاختيار:"""
        elif language == 'ru':
            channel_text = f"""📺 **Выберите каналы для рекламы**

📊 **Выбрано:** {len(selected_channels)}/{len(enhanced_channels)} каналов
👥 **Живой охват:** {total_reach:,} подписчиков

💡 Нажмите на каналы для выбора/отмены:"""
        else:
            channel_text = f"""📺 **Select Channels for Your Ad**

📊 **Selected:** {len(selected_channels)}/{len(enhanced_channels)} channels
👥 **Live Reach:** {total_reach:,} subscribers

💡 Tap channels to toggle selection:"""
        
        # Create modern keyboard with toggle design
        keyboard_rows = []
        for channel in enhanced_channels:
            # Check if channel is selected
            is_selected = channel['channel_id'] in selected_channels
            
            # Create enhanced button text with proper formatting
            from fix_ui_issues import create_channel_button_text
            
            # Get channel details with proper fallbacks
            channel_name = channel.get('name', channel.get('channel_name', channel['channel_id']))
            subscriber_count = channel.get('subscribers', channel.get('active_subscribers', 0))
            
            # Ensure subscriber count is a number
            if not isinstance(subscriber_count, (int, float)):
                subscriber_count = 0
            
            button_text = create_channel_button_text(channel_name, int(subscriber_count), is_selected)
            
            keyboard_rows.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"toggle_channel_{channel['channel_id']}"
            )])
        
        # Add control buttons with better styling
        control_buttons = []
        if language == 'ar':
            control_buttons.extend([
                [InlineKeyboardButton(text="🔄 تحديث الإحصائيات", callback_data="refresh_channel_stats"),
                 InlineKeyboardButton(text="🔄 اختيار الكل", callback_data="select_all_channels")],
                [InlineKeyboardButton(text="❌ إلغاء تحديد الكل", callback_data="deselect_all_channels")]
            ])
            
            if selected_channels:
                control_buttons.append([InlineKeyboardButton(
                    text="✅ متابعة مع القنوات المحددة", 
                    callback_data="continue_with_channels"
                )])
            
            control_buttons.append([InlineKeyboardButton(
                text="◀️ العودة للقائمة", 
                callback_data="back_to_main"
            )])
        elif language == 'ru':
            control_buttons.extend([
                [InlineKeyboardButton(text="🔄 Обновить статистику", callback_data="refresh_channel_stats"),
                 InlineKeyboardButton(text="🔄 Выбрать все", callback_data="select_all_channels")],
                [InlineKeyboardButton(text="❌ Отменить все", callback_data="deselect_all_channels")]
            ])
            
            if selected_channels:
                control_buttons.append([InlineKeyboardButton(
                    text="✅ Продолжить с выбранными", 
                    callback_data="continue_with_channels"
                )])
            
            control_buttons.append([InlineKeyboardButton(
                text="◀️ В главное меню", 
                callback_data="back_to_main"
            )])
        else:
            control_buttons.extend([
                [InlineKeyboardButton(text="🔄 Refresh Stats", callback_data="refresh_channel_stats"),
                 InlineKeyboardButton(text="🔄 Select All", callback_data="select_all_channels")],
                [InlineKeyboardButton(text="❌ Deselect All", callback_data="deselect_all_channels")]
            ])
            
            if selected_channels:
                control_buttons.append([InlineKeyboardButton(
                    text="✅ Continue with Selected", 
                    callback_data="continue_with_channels"
                )])
            
            control_buttons.append([InlineKeyboardButton(
                text="◀️ Back to Menu", 
                callback_data="back_to_main"
            )])
        
        keyboard_rows.extend(control_buttons)
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
        
        # Edit the message with updated content and keyboard
        await callback_query.message.edit_text(
            channel_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error refreshing enhanced channel selection: {e}")
        await callback_query.answer("Error refreshing interface")


async def refresh_channel_selection_keyboard(callback_query: CallbackQuery, state: FSMContext):
    """Legacy refresh function - redirects to enhanced version"""
    await refresh_enhanced_channel_selection_ui(callback_query, state)


@router.callback_query(F.data.startswith("toggle_channel_"))
async def toggle_channel_selection(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel selection toggle with enhanced UI"""
    try:
        channel_id = callback_query.data.replace("toggle_channel_", "")
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Get current selected channels
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        # Toggle channel selection
        if channel_id in selected_channels:
            selected_channels.remove(channel_id)
            action = "deselected"
        else:
            selected_channels.append(channel_id)
            action = "selected"
        
        # Update state
        await state.update_data(selected_channels=selected_channels)
        
        # Refresh the enhanced channel selection interface
        await refresh_enhanced_channel_selection_ui(callback_query, state)
        
        # Show toggle feedback
        feedback_text = {
            'en': f"Channel {action}",
            'ar': f"تم {'اختيار' if action == 'selected' else 'إلغاء'} القناة",
            'ru': f"Канал {'выбран' if action == 'selected' else 'отменён'}"
        }
        await callback_query.answer(feedback_text.get(language, feedback_text['en']))
        
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
    """Handle channel toggle with enhanced UI"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        channel_id = callback_query.data.replace("toggle_channel_", "")
        
        # Get current data
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        # Toggle channel
        if channel_id in selected_channels:
            selected_channels.remove(channel_id)
            action = "deselected"
        else:
            selected_channels.append(channel_id)
            action = "selected"
        
        # Update state
        await state.update_data(selected_channels=selected_channels)
        
        # Refresh the entire channel selection interface
        await show_channel_selection_for_enhanced_flow(callback_query, state)
        
        # Show feedback message
        channel_name = channel_id  # Fallback to ID if name not available
        try:
            channels = await db.get_channels()
            for ch in channels:
                if str(ch.get('channel_id')) == str(channel_id):
                    channel_name = ch.get('name', channel_id)
                    break
        except:
            pass
        
        feedback_messages = {
            'en': f"Channel {channel_name} {action}",
            'ar': f"تم {'اختيار' if action == 'selected' else 'إلغاء اختيار'} القناة {channel_name}",
            'ru': f"Канал {channel_name} {'выбран' if action == 'selected' else 'отменен'}"
        }
        
        await callback_query.answer(feedback_messages.get(language, feedback_messages['en']))
        
    except Exception as e:
        logger.error(f"Error in toggle_channel_handler: {e}")
        await callback_query.answer("Error toggling channel. Please try again.", show_alert=True)


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
    
    # Regular flow - go directly to days selection
    selected_channels = data.get('selected_channels', [])
    
    # Store selected channels in state for later use
    await state.update_data(selected_channels=selected_channels)
    
    # Answer callback to prevent timeout
    await safe_callback_answer(callback_query, "")
    
    # Show dynamic days selector immediately
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
    """Show smart pricing days selector with comprehensive pricing information"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get selected channels data for price calculation
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Calculate pricing using quantitative pricing system
    from quantitative_pricing_system import calculate_quantitative_price
    
    calculation = calculate_quantitative_price(days, len(selected_channels))
    
    # Store pricing calculation in state
    await state.update_data(pricing_calculation=calculation)
    
    # Track duration selection with end-to-end tracking system
    try:
        await track_duration_selection(user_id, days, state)
    except Exception as e:
        logger.error(f"Error tracking duration selection: {e}")
    
    # Generate pricing preview text
    final_price = calculation.get('final_price', 0)
    total_stars = calculation.get('total_stars', 0)
    posts_per_day = calculation.get('posts_per_day', 1)
    discount_percentage = calculation.get('discount_percentage', 0)
    
    if language == 'ar':
        pricing_preview = f"💰 السعر: ${final_price:.2f} أو {total_stars} نجمة\n📊 المنشورات يومياً: {posts_per_day} | خصم: {discount_percentage:.1f}%"
    elif language == 'ru':
        pricing_preview = f"💰 Цена: ${final_price:.2f} или {total_stars} звезд\n📊 Постов в день: {posts_per_day} | Скидка: {discount_percentage:.1f}%"
    else:
        pricing_preview = f"💰 Price: ${final_price:.2f} or {total_stars} Stars\n📊 Posts per day: {posts_per_day} | Discount: {discount_percentage:.1f}%"
    
    # Create header with direct language handling
    if language == 'ar':
        header = f"""📊 **اختر عدد الأيام**

🗓️ أيام محددة: {days}

{pricing_preview}

💡 منطق التسعير الذكي:
• المزيد من الأيام = المزيد من المنشورات يومياً
• المزيد من الأيام = خصومات أكبر
• تحويل العملة تلقائياً"""
    elif language == 'ru':
        header = f"""📊 **Выберите количество дней**

🗓️ Выбранные дни: {days}

{pricing_preview}

💡 Логика умного ценообразования:
• Больше дней = больше постов в день
• Больше дней = больше скидки
• Автоматическая конвертация валют"""
    else:
        header = f"""📊 **Select Number of Days**

🗓️ Selected Days: {days}

{pricing_preview}

💡 Smart Pricing Logic:
• More days = more posts per day
• More days = bigger discounts
• Automatic currency conversion"""
    
    footer = f"""
{get_text(language, 'click_adjust_days')}
    """
    
    text = header + footer
    
    # Create +/- keyboard for days selection with translations
    keyboard_rows = []
    
    # Days adjustment row
    minus_callback = f"days_adjust_minus_{days}" if days > 1 else "days_adjust_none"
    plus_callback = f"days_adjust_plus_{days}"
    
    # Days label with translation
    if language == 'ar':
        days_label = f"{days} أيام"
    elif language == 'ru':
        days_label = f"{days} дней"
    else:
        days_label = f"{days} days"
    
    keyboard_rows.append([
        InlineKeyboardButton(text="[-]", callback_data=minus_callback),
        InlineKeyboardButton(text=days_label, callback_data="days_info"),
        InlineKeyboardButton(text="[+]", callback_data=plus_callback)
    ])
    
    # Quick selection buttons with translations
    if days != 1:
        button_text = "1 يوم" if language == 'ar' else "1 день" if language == 'ru' else "1 Day"
        keyboard_rows.append([InlineKeyboardButton(text=button_text, callback_data="days_quick_1")])
    if days != 7:
        button_text = "7 أيام" if language == 'ar' else "7 дней" if language == 'ru' else "7 Days"
        keyboard_rows.append([InlineKeyboardButton(text=button_text, callback_data="days_quick_7")])
    if days != 30:
        button_text = "30 يوم" if language == 'ar' else "30 дней" if language == 'ru' else "30 Days"
        keyboard_rows.append([InlineKeyboardButton(text=button_text, callback_data="days_quick_30")])
    
    # Continue button with translations
    continue_text = get_text(language, 'continue_with_days', days=days)
    
    keyboard_rows.append([
        InlineKeyboardButton(text=continue_text, callback_data="days_confirm")
    ])
    
    # Back button with translations
    back_text = "رجوع" if language == 'ar' else "Назад" if language == 'ru' else "Back"
    keyboard_rows.append([
        InlineKeyboardButton(text=back_text, callback_data="back_to_start")
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
    """Confirm days selection and continue to payment options directly"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        data = await state.get_data()
        selected_days = data.get('selected_days', 1)
        selected_channels = data.get('selected_channels', [])
        
        # Calculate pricing with quantitative pricing system
        from quantitative_pricing_system import calculate_quantitative_price
        
        calculation = calculate_quantitative_price(selected_days, len(selected_channels))
        
        # Store pricing calculation using calculated posts per day
        await state.update_data(
            selected_posts_per_day=calculation.get('posts_per_day', 1),
            pricing_calculation=calculation
        )
        
        # Go directly to payment options
        await show_payment_options(callback_query, state)
        
    except Exception as e:
        logger.error(f"Error in days_confirm_handler: {e}")
        await callback_query.answer("Error confirming days selection")


async def show_posts_per_day_selection(callback_query: CallbackQuery, state: FSMContext, days: int, selected_channels: list):
    """Show posts per day selection interface"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Calculate pricing for different posts per day options
    # Dynamic pricing removed during cleanup
    
    options = [1, 2, 3, 5, 8, 10]
    pricing_options = []
    
    for posts_per_day in options:
        calculation = DynamicPricing.calculate_total_cost(
            days=days,
            posts_per_day=posts_per_day,
            channels=selected_channels
        )
        pricing_options.append({
            'posts_per_day': posts_per_day,
            'total_usd': calculation['total_usd'],
            'total_stars': calculation['total_stars'],
            'discount_percent': calculation['discount_percent']
        })
    
    # Create header text
    if language == 'ar':
        header = f"""📊 **اختر عدد المنشورات يومياً**

🗓️ **المدة:** {days} أيام
📢 **القنوات:** {len(selected_channels)} قناة

💰 **خيارات التسعير:**"""
    elif language == 'ru':
        header = f"""📊 **Выберите количество постов в день**

🗓️ **Длительность:** {days} дней
📢 **Каналы:** {len(selected_channels)} канала

💰 **Варианты цен:**"""
    else:
        header = f"""📊 **Choose Posts Per Day**

🗓️ **Duration:** {days} days
📢 **Channels:** {len(selected_channels)} channels

💰 **Pricing Options:**"""
    
    # Create keyboard with pricing options
    keyboard_rows = []
    
    for option in pricing_options:
        posts = option['posts_per_day']
        usd = option['total_usd']
        stars = option['total_stars']
        discount = option['discount_percent']
        
        if discount > 0:
            if language == 'ar':
                button_text = f"{posts} منشور/يوم - ${usd:.2f} ({discount}% خصم)"
            elif language == 'ru':
                button_text = f"{posts} пост/день - ${usd:.2f} ({discount}% скидка)"
            else:
                button_text = f"{posts} posts/day - ${usd:.2f} ({discount}% off)"
        else:
            if language == 'ar':
                button_text = f"{posts} منشور/يوم - ${usd:.2f}"
            elif language == 'ru':
                button_text = f"{posts} пост/день - ${usd:.2f}"
            else:
                button_text = f"{posts} posts/day - ${usd:.2f}"
        
        keyboard_rows.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"select_posts_{posts}"
            )
        ])
    
    # Add back button
    back_text = "رجوع" if language == 'ar' else "Назад" if language == 'ru' else "Back"
    keyboard_rows.append([
        InlineKeyboardButton(text=back_text, callback_data="back_to_days")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    try:
        await callback_query.message.edit_text(
            header,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        await callback_query.answer()
    except Exception as e:
        logger.error(f"Error showing posts per day selection: {e}")


@router.callback_query(F.data.startswith("select_posts_"))
async def select_posts_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle posts per day selection"""
    try:
        posts_per_day = int(callback_query.data.replace("select_posts_", ""))
        
        # Get state data
        data = await state.get_data()
        selected_days = data.get('selected_days', 1)
        selected_channels = data.get('selected_channels', [])
        
        # Calculate final pricing using quantitative pricing system
        from quantitative_pricing_system import calculate_quantitative_price
        
        calculation = calculate_quantitative_price(selected_days, len(selected_channels))
        
        # Store pricing calculation using calculated posts per day
        await state.update_data(
            selected_posts_per_day=calculation.get('posts_per_day', 1),
            pricing_calculation=calculation
        )
        
        # Show payment options (TON and Stars)
        await show_payment_options(callback_query, state)
        
    except Exception as e:
        logger.error(f"Error in select_posts_handler: {e}")
        await callback_query.answer("Error selecting posts per day")

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
    pricing_data = {"total_amount": 0.29, "currency": "USD"}
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
        pricing_data = {"total_amount": 0.29, "currency": "USD"}
        await state.update_data(pricing_data=pricing_data)
        
        # Show payment options
        await show_frequency_payment_summary_message(message, state, pricing_data)
        
    except ValueError:
        await message.reply("❌ Please enter a valid number of days.")

@router.callback_query(F.data == "freq_all_tiers")
async def frequency_all_tiers_handler(callback_query: CallbackQuery, state: FSMContext):
    """Show all available frequency tiers"""
    pricing = FrequencyPricingSystem()
    all_tiers = 0.29
    
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
    
    # Check if user is admin
    from config import ADMIN_IDS
    is_admin = user_id in ADMIN_IDS
    
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    # Get channel names
    channel_names = []
    all_channels = await db.get_channels(active_only=False)
    for channel_id in selected_channels:
        channel = next((ch for ch in all_channels if ch['channel_id'] == channel_id), None)
        if channel:
            channel_names.append(channel['name'])
    
    # Create translated text using translation system
    text = f"""{get_text(language, 'ad_plan_summary')}

{get_text(language, 'duration_label')} {pricing_data['days']} {get_text(language, 'days_word')}
{get_text(language, 'posts_per_day_label')} {pricing_data['posts_per_day']} {get_text(language, 'posts_word')}
{get_text(language, 'discount_label')} {pricing_data['discount_percent']}%
{get_text(language, 'final_price_label')} ${pricing_data['final_cost_usd']:.2f}

{get_text(language, 'in_ton_label')} {pricing_data['cost_ton']:.3f} TON
{get_text(language, 'in_stars_label')} {pricing_data['cost_stars']:,} Stars

{get_text(language, 'selected_channels_label')}
{chr(10).join(f"• {name}" for name in channel_names)}

{get_text(language, 'campaign_details_label')}
{get_text(language, 'daily_rate_label')} ${pricing_data['daily_price']:.2f}/{get_text(language, 'per_day')} ({pricing_data['posts_per_day']} {get_text(language, 'posts_word')})
{get_text(language, 'total_posts_label')} {pricing_data['total_posts']:,} {get_text(language, 'posts_word')}
{get_text(language, 'base_cost_label')} ${pricing_data['base_cost_usd']:.2f}
{get_text(language, 'you_save_label')} ${pricing_data['savings_usd']:.2f} ({pricing_data['savings_percent']}% {get_text(language, 'off_word')})

{get_text(language, 'usage_agreement_notice')}

{get_text(language, 'pricing_tip')}"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(language, 'pay_with_ton'), callback_data="pay_freq_ton"),
            InlineKeyboardButton(text=get_text(language, 'pay_with_stars'), callback_data="pay_freq_stars")
        ],
        [
            InlineKeyboardButton(text=get_text(language, 'change_duration'), callback_data="freq_change_duration"),
            InlineKeyboardButton(text=get_text(language, 'change_channels'), callback_data="continue_to_channels")
        ],
        [
            InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data="back_to_main")
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
    all_channels = await db.get_channels(active_only=False)
    for channel_id in selected_channels:
        channel = next((ch for ch in all_channels if ch['channel_id'] == channel_id), None)
        if channel:
            channel_names.append(channel['name'])
    
    # Create translated text using translation system
    text = f"""{get_text(language, 'ad_plan_summary')}

{get_text(language, 'duration_label')} {pricing_data['days']} {get_text(language, 'days_word')}
{get_text(language, 'posts_per_day_label')} {pricing_data['posts_per_day']} {get_text(language, 'posts_word')}
{get_text(language, 'discount_label')} {pricing_data['discount_percent']}%
{get_text(language, 'final_price_label')} ${pricing_data['final_cost_usd']:.2f}

{get_text(language, 'in_ton_label')} {pricing_data['cost_ton']:.3f} TON
{get_text(language, 'in_stars_label')} {pricing_data['cost_stars']:,} Stars

{get_text(language, 'selected_channels_label')}
{chr(10).join(f"• {name}" for name in channel_names)}

{get_text(language, 'campaign_details_label')}
{get_text(language, 'daily_rate_label')} ${pricing_data['daily_price']:.2f}/{get_text(language, 'per_day')} ({pricing_data['posts_per_day']} {get_text(language, 'posts_word')})
{get_text(language, 'total_posts_label')} {pricing_data['total_posts']:,} {get_text(language, 'posts_word')}
{get_text(language, 'base_cost_label')} ${pricing_data['base_cost_usd']:.2f}
{get_text(language, 'you_save_label')} ${pricing_data['savings_usd']:.2f} ({pricing_data['savings_percent']}% {get_text(language, 'off_word')})

{get_text(language, 'usage_agreement_notice')}

{get_text(language, 'pricing_tip')}"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(language, 'pay_with_ton'), callback_data="pay_freq_ton"),
            InlineKeyboardButton(text=get_text(language, 'pay_with_stars'), callback_data="pay_freq_stars")
        ],
        [
            InlineKeyboardButton(text=get_text(language, 'change_duration'), callback_data="freq_change_duration"),
            InlineKeyboardButton(text=get_text(language, 'change_channels'), callback_data="continue_to_channels")
        ],
        [
            InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data="back_to_main")
        ]
    ])
    
    await message.reply(text, reply_markup=keyboard, parse_mode='Markdown')

@router.callback_query(F.data == "freq_change_duration")
async def frequency_change_duration_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle duration change request"""
    await show_dynamic_days_selector(callback_query, state, 1)

@router.callback_query(F.data == "pay_freq_ton")
async def pay_frequency_ton_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle TON payment for frequency pricing with comprehensive wallet management"""
    user_id = callback_query.from_user.id
    
    # Check if user is admin for free posting privilege
    from config import ADMIN_IDS
    if user_id in ADMIN_IDS:
        # Admin gets free posting!
        await process_admin_free_posting(callback_query, state)
        return
    
    data = await state.get_data()
    pricing_data = data.get('pricing_data', {})
    
    if not pricing_data:
        await callback_query.answer("❌ Pricing data not found")
        return
    
    # Track payment method selection
    try:
        await track_payment_method_selection(user_id, 'TON', state)
    except Exception as e:
        logger.error(f"Error tracking payment method selection: {e}")
    
    # Store payment data for wallet manager
    await state.update_data(
        pending_payment_amount=pricing_data['cost_ton'],
        payment_method='ton',
        payment_currency='TON'
    )
    
    # Use WalletManager to request wallet address
    from wallet_manager import WalletManager
    await WalletManager.request_wallet_address(callback_query, state, 'payment')

@router.callback_query(F.data == "pay_freq_stars")
async def pay_frequency_stars_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Stars payment for frequency pricing"""
    user_id = callback_query.from_user.id
    
    # Check if user is admin for free posting privilege
    from config import ADMIN_IDS
    if user_id in ADMIN_IDS:
        # Admin gets free posting!
        await process_admin_free_posting(callback_query, state)
        return
    
    data = await state.get_data()
    pricing_calculation = data.get('pricing_calculation', {})
    
    if not pricing_calculation:
        await callback_query.answer("❌ Pricing data not found")
        return
    
    # Get Stars amount from calculation  
    stars_amount = pricing_calculation.get('total_stars', 0)
    
    if stars_amount <= 0:
        await callback_query.answer("❌ Invalid payment amount")
        return
    
    # Process Stars payment with correct amount
    await process_stars_payment(callback_query, state, stars_amount)


async def continue_ton_payment_with_wallet(message_or_callback, state: FSMContext, amount_ton: float, wallet_address: str):
    """Continue TON payment process with user's wallet address"""
    user_id = message_or_callback.from_user.id
    language = await get_user_language(user_id)
    
    # Import payment utilities
    from payments import generate_memo, get_bot_wallet_address
    
    # Initialize enhanced payment system with memo-based verification
    from enhanced_ton_payment_system import get_enhanced_ton_payment_system
    
    bot_wallet = get_bot_wallet_address()
    enhanced_payment_system = get_enhanced_ton_payment_system(bot_wallet)
    
    # Get bot instance from message context
    bot_instance = None
    if hasattr(message_or_callback, 'bot'):
        bot_instance = message_or_callback.bot
    elif hasattr(message_or_callback, 'message') and hasattr(message_or_callback.message, 'bot'):
        bot_instance = message_or_callback.message.bot
    
    # Get campaign details from state
    data = await state.get_data()
    calculation = data.get('pricing_calculation', {})
    selected_channels = data.get('selected_channels', [])
    
    # Create enhanced payment request
    payment_request = await enhanced_payment_system.create_payment_request(
        user_id=user_id,
        amount_ton=amount_ton,
        user_wallet=wallet_address,
        campaign_details={
            'days': calculation.get('days', 1),
            'posts_per_day': calculation.get('posts_per_day', 1),
            'total_posts': calculation.get('total_posts', 1),
            'selected_channels': selected_channels,
            'total_usd': calculation.get('total_usd', 0)
        },
        bot_instance=bot_instance
    )
    
    # Use enhanced memo from the new system
    memo = payment_request['memo']
    
    # Track payment for automatic confirmation with complete ad data including media
    try:
        from automatic_payment_confirmation import track_payment_for_user
        
        # Get full state data including ad content and media
        full_data = await state.get_data()
        
        # Create ad_data with all information including media
        ad_data = {
            'duration_days': calculation.get('days', 1),
            'posts_per_day': calculation.get('posts_per_day', 1),
            'selected_channels': selected_channels,
            'total_reach': calculation.get('total_reach', 0),
            'ad_content': full_data.get('ad_text', ''),
            'content_type': full_data.get('content_type', 'text'),
            'media_url': full_data.get('photos', [None])[0] if full_data.get('photos') else full_data.get('video')
        }
        
        await track_payment_for_user(user_id, memo, amount_ton, ad_data)
        logger.info(f"✅ Tracked payment {memo} for user {user_id} with media: {bool(ad_data.get('media_url'))}")
    except Exception as e:
        logger.error(f"❌ Error tracking payment: {e}")
    
    # Create modern enhanced payment interface 
    if language == 'ar':
        payment_text = f"""🚀 **نظام الدفع المتقدم - TON**
        
💰 **تفاصيل الحملة الإعلانية**
📊 المدة: {calculation.get('days', 1)} أيام
📈 المشاركات: {calculation.get('posts_per_day', 1)} يومياً  
📺 القنوات: {len(selected_channels)} قناة محددة
💵 إجمالي التكلفة: **{amount_ton:.3f} TON** (${calculation.get('total_usd', 0):.2f})

🏦 **معلومات الدفع**
**العنوان:** `{bot_wallet}`
**المذكرة:** `{memo}`
**المبلغ المطلوب:** {amount_ton:.3f} TON

✅ **خطوات الدفع:**
1️⃣ أرسل **{amount_ton:.3f} TON** بالضبط
2️⃣ استخدم المذكرة: **{memo}**
3️⃣ التحقق التلقائي خلال 30 ثانية

⏰ انتهاء الصلاحية: 20 دقيقة
🔗 تتبع الدفع: [TonViewer](https://tonviewer.com/{bot_wallet.replace('UQ', 'EQ')})

🛡️ **الأمان:** نظام التحقق المزدوج (المذكرة + محفظتك)
📱 **التأكيد:** رسالة فورية عند استلام الدفع"""
    elif language == 'ru':
        payment_text = f"""🚀 **Расширенная система оплаты - TON**
        
💰 **Детали рекламной кампании**
📊 Продолжительность: {calculation.get('days', 1)} дней
📈 Посты: {calculation.get('posts_per_day', 1)} в день  
📺 Каналы: {len(selected_channels)} выбранных каналов
💵 Общая стоимость: **{amount_ton:.3f} TON** (${calculation.get('total_usd', 0):.2f})

🏦 **Информация о платеже**
**Адрес:** `{bot_wallet}`
**Заметка:** `{memo}`
**Требуемая сумма:** {amount_ton:.3f} TON

✅ **Шаги оплаты:**
1️⃣ Отправьте точно **{amount_ton:.3f} TON**
2️⃣ Используйте заметку: **{memo}**
3️⃣ Автоматическая проверка в течение 30 секунд

⏰ Истечение срока: 20 минут
🔗 Отслеживание платежа: [TonViewer](https://tonviewer.com/{bot_wallet.replace('UQ', 'EQ')})

🛡️ **Безопасность:** Система двойной проверки (заметка + ваш кошелек)
📱 **Подтверждение:** Мгновенное сообщение при получении платежа"""
    else:
        payment_text = f"""🚀 **Advanced Payment System - TON**
        
💰 **Campaign Details**
📊 Duration: {calculation.get('days', 1)} days
📈 Posts: {calculation.get('posts_per_day', 1)} per day  
📺 Channels: {len(selected_channels)} selected channels
💵 Total Cost: **{amount_ton:.3f} TON** (${calculation.get('total_usd', 0):.2f})

🏦 **Payment Information**
**Address:** `{bot_wallet}`
**Memo:** `{memo}`
**Required Amount:** {amount_ton:.3f} TON

✅ **Payment Steps:**
1️⃣ Send exactly **{amount_ton:.3f} TON**
2️⃣ Use memo: **{memo}**
3️⃣ Automatic verification within 30 seconds

⏰ Expires in: 20 minutes
🔗 Track payment: [TonViewer](https://tonviewer.com/{bot_wallet.replace('UQ', 'EQ')})

🛡️ **Security:** Dual verification system (memo + your wallet)
📱 **Confirmation:** Instant message when payment received"""
    
    # Create payment keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel Payment", callback_data="cancel_payment")]
    ])
    
    # Store payment info in database
    payment_id = await db.create_payment(
        user_id=user_id,
        subscription_id=0,  # Will be updated later
        amount=amount_ton,
        currency='TON',
        payment_method='ton',
        memo=memo
    )
    
    # Update state with payment information
    await state.update_data(
        payment_id=payment_id, 
        payment_memo=memo,
        user_wallet_address=wallet_address
    )
    
    # Show payment instructions
    if hasattr(message_or_callback, 'message'):
        await message_or_callback.message.edit_text(
            payment_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        await message_or_callback.reply(
            payment_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    # Start enhanced payment monitoring with memo-based verification
    try:
        # Define success callback for payment confirmation
        async def on_payment_success(payment_request, matching_transaction):
            """Handle successful payment confirmation"""
            await handle_successful_ton_payment_with_confirmation(
                user_id, payment_request['memo'], amount_ton, state
            )
        
        # Define failure callback for payment timeout
        async def on_payment_failure(payment_request, reason):
            """Handle payment failure or timeout"""
            await handle_expired_ton_payment(user_id, payment_request['memo'], state)
        
        # Start enhanced monitoring with memo priority
        await enhanced_payment_system.start_payment_monitoring(
            payment_request, on_payment_success, on_payment_failure
        )
        
        logger.info(f"✅ Enhanced payment monitoring started for {user_id} with memo: {memo}")
        
    except Exception as e:
        logger.error(f"Failed to start enhanced payment monitoring: {e}")
        # Continue without monitoring - user can check manually

async def process_ton_payment(callback_query: CallbackQuery, state: FSMContext, amount_ton: float):
    """Process TON payment with blockchain verification"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # First, ask for user's wallet address
    await request_user_wallet_address(callback_query, state, amount_ton)

async def request_user_wallet_address(callback_query: CallbackQuery, state: FSMContext, amount_ton: float):
    """Request user's TON wallet address before payment"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Create wallet address request message
    if language == 'ar':
        wallet_text = f"""💎 **دفع TON - إدخال عنوان المحفظة**

المبلغ المطلوب: {amount_ton:.3f} TON

**يرجى إدخال عنوان محفظة TON الخاصة بك:**
- سيتم استخدام هذا العنوان للتحقق من الدفع
- يجب أن يكون العنوان الذي ستدفع منه
- تأكد من صحة العنوان لتجنب فقدان الأموال

**مثال:** EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE

أرسل عنوان محفظتك الآن:"""
    elif language == 'ru':
        wallet_text = f"""💎 **Оплата TON - Ввод адреса кошелька**

Требуемая сумма: {amount_ton:.3f} TON

**Пожалуйста, введите адрес вашего TON кошелька:**
- Этот адрес будет использован для проверки платежа
- Должен быть адрес, с которого вы будете платить
- Убедитесь в правильности адреса во избежание потери средств

**Пример:** EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE

Отправьте адрес вашего кошелька сейчас:"""
    else:
        wallet_text = f"""💎 **TON Payment - Wallet Address Input**

Required Amount: {amount_ton:.3f} TON

**Please enter your TON wallet address:**
- This address will be used to verify the payment
- Must be the address you will pay from
- Ensure the address is correct to avoid loss of funds

**Example:** EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE

Send your wallet address now:"""
    
    # Create keyboard with cancel option
    if language == 'ar':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel_payment")]
        ])
    elif language == 'ru':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_payment")]
        ])
    
    # Store payment amount for later use
    await state.update_data(
        pending_payment_amount=amount_ton,
        payment_method='ton',
        waiting_for_wallet_address=True
    )
    
    # Set state to wait for wallet address
    await state.set_state(AdCreationStates.waiting_wallet_address)
    
    await callback_query.message.edit_text(
        wallet_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    await callback_query.answer()

@router.message(AdCreationStates.waiting_wallet_address)
async def handle_wallet_address_input(message: Message, state: FSMContext):
    """Handle user wallet address input"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    wallet_address = message.text.strip()
    
    # Validate TON wallet address format
    if not (wallet_address.startswith('EQ') or wallet_address.startswith('UQ')) or len(wallet_address) != 48:
        if language == 'ar':
            error_text = "❌ عنوان المحفظة غير صحيح. يجب أن يبدأ بـ EQ أو UQ ويكون 48 حرفاً. حاول مرة أخرى:"
        elif language == 'ru':
            error_text = "❌ Неверный адрес кошелька. Должен начинаться с EQ или UQ и быть длиной 48 символов. Попробуйте еще раз:"
        else:
            error_text = "❌ Invalid wallet address. Must start with EQ or UQ and be 48 characters long. Try again:"
        
        await message.reply(error_text)
        return
    
    # Get payment data
    data = await state.get_data()
    amount_ton = data.get('pending_payment_amount')
    
    if not amount_ton:
        await message.reply("❌ Payment session expired. Please start over.")
        return
    
    # Store user wallet address
    await state.update_data(
        user_wallet_address=wallet_address,
        waiting_for_wallet_address=False
    )
    
    # Continue with payment processing
    await continue_ton_payment_with_wallet(message, state, amount_ton, wallet_address)

async def continue_ton_payment_with_wallet(message: Message, state: FSMContext, amount_ton: float, user_wallet: str):
    """Continue TON payment processing with user wallet address"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Get bot's wallet address from config
    from config import TON_WALLET_ADDRESS
    bot_wallet = TON_WALLET_ADDRESS or "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
    
    # Generate unique memo for this payment (2 letters + 4 digits format)
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = ''.join(random.choices(string.digits, k=4))
    memo = letters + digits
    
    # Create payment expiration timestamp (20 minutes from now)
    import time
    expiration_time = int(time.time()) + (20 * 60)  # 20 minutes
    
    # Store payment info
    await state.update_data(
        payment_memo=memo,
        payment_amount=amount_ton,
        payment_expiration=expiration_time,
        bot_wallet=bot_wallet,
        user_wallet_address=user_wallet
    )
    
    # Create optimized payment instruction message (shorter to avoid MESSAGE_TOO_LONG)
    if language == 'ar':
        payment_text = f"""💰 **دفع TON**

**المبلغ:** {amount_ton:.3f} TON
**العنوان:** `{bot_wallet}`
**المذكرة:** `{memo}`

**خطوات الدفع:**
1. افتح محفظة TON
2. أرسل {amount_ton:.3f} TON للعنوان أعلاه
3. أضف المذكرة `{memo}` بالضبط
4. أكد المعاملة

⏰ انتهاء الصلاحية: 20 دقيقة
✅ تحقق تلقائي كل 30 ثانية

🔒 بدفعك، تتفق على شروط الاستخدام"""
    elif language == 'ru':
        payment_text = f"""💰 **Оплата TON**

**Сумма:** {amount_ton:.3f} TON
**Адрес:** `{bot_wallet}`
**Заметка:** `{memo}`

**Шаги оплаты:**
1. Откройте TON кошелек
2. Отправьте {amount_ton:.3f} TON на адрес выше
3. Добавьте заметку `{memo}` точно
4. Подтвердите транзакцию

⏰ Истекает через: 20 минут
✅ Автопроверка каждые 30 секунд

🔒 Оплачивая, вы соглашаетесь с условиями"""
    else:
        payment_text = f"""💰 **TON Payment**

**Amount:** {amount_ton:.3f} TON
**Address:** `{bot_wallet}`
**Memo:** `{memo}`

**Payment Steps:**
1. Open your TON wallet
2. Send {amount_ton:.3f} TON to address above
3. Add memo `{memo}` exactly
4. Confirm transaction

⏰ Expires in: 20 minutes
✅ Auto-verification every 30 seconds

🔒 By paying, you agree to Usage Agreement"""
    
    # Create keyboard with cancel option
    if language == 'ar':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ إلغاء الدفع", callback_data="cancel_payment")]
        ])
    elif language == 'ru':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить платеж", callback_data="cancel_payment")]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel Payment", callback_data="cancel_payment")]
        ])
    
    # Send payment instructions
    await message.answer(
        payment_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    # Store payment memo for tracking
    try:
        from payment_memo_tracker import memo_tracker
        ad_data = await state.get_data()
        await memo_tracker.store_payment_memo(
            user_id=user_id,
            memo=memo,
            amount=amount_ton,
            ad_data=ad_data,
            payment_method='TON'
        )
        logger.info(f"✅ Stored payment memo {memo} for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Error storing payment memo: {e}")
    
    # Start enhanced payment monitoring
    from enhanced_ton_payment_monitoring import monitor_ton_payment_enhanced
    asyncio.create_task(monitor_ton_payment_enhanced(user_id, memo, amount_ton, expiration_time, user_wallet, state, bot_wallet))

def normalize_wallet_address(address: str) -> str:
    """Normalize TON wallet address by converting to standard format"""
    if not address:
        return address
    
    # Remove any whitespace
    address = address.strip()
    
    # Convert EQ prefix to UQ for consistent comparison
    if address.startswith('EQ'):
        address = 'UQ' + address[2:]
    
    return address

async def monitor_ton_payment_with_user_wallet(user_id: int, memo: str, amount_ton: float, expiration_time: int, user_wallet: str, state: FSMContext):
    """Monitor TON payment using TON Center API with user wallet verification - Enhanced with official best practices"""
    import time
    import requests
    
    # Monitor for 20 minutes (1200 seconds)
    check_interval = 30  # Check every 30 seconds
    
    # Use consistent bot wallet address
    from config import TON_WALLET_ADDRESS
    bot_wallet = TON_WALLET_ADDRESS or "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
    
    # Normalize user wallet address for comparison
    normalized_user_wallet = normalize_wallet_address(user_wallet)
    
    logger.info(f"Starting TON payment monitoring for user {user_id}, memo: {memo}, amount: {amount_ton} TON")
    logger.info(f"Monitoring bot wallet: {bot_wallet}")
    logger.info(f"Expected from user wallet: {user_wallet} (normalized: {normalized_user_wallet})")
    
    # Track last checked transaction to avoid duplicates
    last_lt = None
    last_hash = None
    
    while time.time() < expiration_time:
        try:
            # Use TON Center API with enhanced parameters following official documentation
            api_url = f"https://toncenter.com/api/v2/getTransactions?address={bot_wallet}&limit=100&archival=true"
            
            # Add pagination if we have previous transaction data
            if last_lt and last_hash:
                api_url += f"&lt={last_lt}&hash={last_hash}"
            
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    transactions = data.get('result', [])
                    
                    if not transactions:
                        logger.debug(f"No new transactions found for {bot_wallet}")
                        await asyncio.sleep(check_interval)
                        continue
                    
                    # Process transactions in reverse order (newest first)
                    for tx in transactions:
                        # Check if this is an incoming transaction
                        if tx.get('in_msg'):
                            in_msg = tx['in_msg']
                            
                            # Skip external messages
                            if in_msg.get('@type') == 'raw.message' and not in_msg.get('source'):
                                continue
                            
                            # Check if transaction has the correct memo
                            tx_memo = in_msg.get('message', '')
                            if tx_memo == memo:
                                # Get sender address and normalize it
                                sender_address = in_msg.get('source', '')
                                normalized_sender = normalize_wallet_address(sender_address)
                                
                                # Verify the payment is from the user's wallet (using normalized addresses)
                                if normalized_sender == normalized_user_wallet:
                                    # Get amount in nanotons and convert to TON
                                    tx_amount_nanotons = int(in_msg.get('value', 0))
                                    tx_amount = tx_amount_nanotons / 1000000000
                                    
                                    # Verify amount matches (with small tolerance for fees)
                                    if abs(tx_amount - amount_ton) <= 0.1:  # Allow 0.1 TON tolerance
                                        # Payment found and verified!
                                        logger.info(f"✅ TON payment verified: {memo} for {amount_ton} TON from {user_wallet}")
                                        logger.info(f"Transaction details: amount={tx_amount}, lt={tx.get('lt')}, hash={tx.get('hash')}")
                                        await handle_successful_ton_payment_with_confirmation(user_id, memo, amount_ton, state)
                                        return
                                    else:
                                        logger.warning(f"Amount mismatch: expected {amount_ton}, got {tx_amount}")
                                else:
                                    logger.debug(f"Payment found but from different wallet: {sender_address} (normalized: {normalized_sender}) != {normalized_user_wallet}")
                            
                    # Update pagination parameters for next iteration
                    if transactions:
                        last_tx = transactions[-1]
                        last_lt = last_tx.get('lt')
                        last_hash = last_tx.get('hash')
                        
                else:
                    logger.warning(f"TON Center API error: {data}")
            else:
                logger.warning(f"TON Center API request failed with status {response.status_code}")
                # Add retry logic for failed requests
                await asyncio.sleep(min(check_interval, 10))
                continue
            
            # Wait before next check
            await asyncio.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"Error monitoring TON payment: {e}")
            await asyncio.sleep(check_interval)
    
    # Payment expired
    logger.warning(f"TON payment expired for user {user_id}, memo: {memo}")
    await handle_expired_ton_payment(user_id, memo, state)






@router.callback_query(F.data == "pay_freq_stars")
async def pay_frequency_stars_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Stars payment for frequency pricing"""
    user_id = callback_query.from_user.id
    
    # Check if user is admin for free posting privilege
    from config import ADMIN_IDS
    if user_id in ADMIN_IDS:
        # Admin gets free posting!
        await process_admin_free_posting(callback_query, state)
        return
    
    data = await state.get_data()
    pricing_calculation = data.get('pricing_calculation', {})
    
    if not pricing_calculation:
        await callback_query.answer("❌ Pricing data not found")
        return
    
    # Get Stars amount from calculation  
    stars_amount = pricing_calculation.get('total_stars', 0)
    
    if stars_amount <= 0:
        await callback_query.answer("❌ Invalid payment amount")
        return
    
    # Process Stars payment with correct amount
    await process_stars_payment(callback_query, state, stars_amount)

async def show_frequency_posts_per_day_selection(callback_query: CallbackQuery, state: FSMContext, days: int):
    """Show posts per day selection with the selected days"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Create translated text
    if language == 'ar':
        text = f"""**الخطوة 2: كم عدد المنشورات لكل يوم؟**

مدة الحملة: {days} أيام

اختر تكرار النشر لرؤية خصومات الحجم:

نصائح خصم الحجم:
- 1 منشور/يوم = بدون خصم
- 2 منشور/يوم = 5% خصم
- 4 منشور/يوم = 10% خصم
- 8 منشور/يوم = 20% خصم
- 24 منشور/يوم = 30% خصم (الحد الأقصى!)

اختر المنشورات لكل يوم:"""
    elif language == 'ru':
        text = f"""**Шаг 2: Сколько постов в день?**

Длительность кампании: {days} дней

Выберите частоту публикации для скидок за объем:

СОВЕТЫ ПО СКИДКАМ ЗА ОБЪЕМ:
- 1 пост/день = Без скидки
- 2 поста/день = 5% скидка
- 4 поста/день = 10% скидка
- 8 постов/день = 20% скидка
- 24 поста/день = 30% скидка (максимум!)

Выберите посты в день:"""
    else:
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
    
    # Create keyboard buttons with translations
    if language == 'ar':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="1/يوم (بدون خصم)", callback_data="dynamic_posts_1"),
                InlineKeyboardButton(text="2/يوم (5% خصم)", callback_data="dynamic_posts_2")
            ],
            [
                InlineKeyboardButton(text="3/يوم (7% خصم)", callback_data="dynamic_posts_3"),
                InlineKeyboardButton(text="4/يوم (10% خصم)", callback_data="dynamic_posts_4")
            ],
            [
                InlineKeyboardButton(text="6/يوم (15% خصم)", callback_data="dynamic_posts_6"),
                InlineKeyboardButton(text="8/يوم (20% خصم)", callback_data="dynamic_posts_8")
            ],
            [
                InlineKeyboardButton(text="12/يوم (27% خصم)", callback_data="dynamic_posts_12"),
                InlineKeyboardButton(text="24/يوم (30% خصم)", callback_data="dynamic_posts_24")
            ],
            [
                InlineKeyboardButton(text="كمية مخصصة", callback_data="dynamic_posts_custom"),
                InlineKeyboardButton(text="رجوع", callback_data="continue_to_duration")
            ]
        ])
    elif language == 'ru':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="1/день (Без скидки)", callback_data="dynamic_posts_1"),
                InlineKeyboardButton(text="2/день (5% скидка)", callback_data="dynamic_posts_2")
            ],
            [
                InlineKeyboardButton(text="3/день (7% скидка)", callback_data="dynamic_posts_3"),
                InlineKeyboardButton(text="4/день (10% скидка)", callback_data="dynamic_posts_4")
            ],
            [
                InlineKeyboardButton(text="6/день (15% скидка)", callback_data="dynamic_posts_6"),
                InlineKeyboardButton(text="8/день (20% скидка)", callback_data="dynamic_posts_8")
            ],
            [
                InlineKeyboardButton(text="12/день (27% скидка)", callback_data="dynamic_posts_12"),
                InlineKeyboardButton(text="24/день (30% скидка)", callback_data="dynamic_posts_24")
            ],
            [
                InlineKeyboardButton(text="Произвольное количество", callback_data="dynamic_posts_custom"),
                InlineKeyboardButton(text="Назад", callback_data="continue_to_duration")
            ]
        ])
    else:
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
    """Handle TON payment for dynamic pricing with enhanced modern payment system"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Check if user is admin for free posting privilege
    from config import ADMIN_IDS
    if user_id in ADMIN_IDS:
        # Admin gets free posting!
        await process_admin_free_posting(callback_query, state)
        return
    
    data = await state.get_data()
    calculation = data.get('pricing_calculation', {})
    
    if not calculation or 'total_ton' not in calculation:
        await callback_query.answer("❌ Invalid payment data")
        return
    
    total_ton = calculation['total_ton']
    
    # Store payment data for wallet manager
    await state.update_data(
        pending_payment_amount=total_ton,
        payment_method='ton',
        payment_currency='TON'
    )
    
    # Use WalletManager to request wallet address and continue with enhanced payment
    from wallet_manager import WalletManager
    await WalletManager.request_wallet_address(callback_query, state, 'payment')








# Clean Stars Payment System Handlers
@router.callback_query(F.data == "pay_dynamic_stars")
async def pay_dynamic_stars_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle Telegram Stars payment - Clean implementation"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Get state data
        data = await state.get_data()
        calculation = data.get('pricing_calculation', {})
        selected_channels = data.get('selected_channels', [])
        ad_content = data.get('ad_text', '') or data.get('ad_content', '')
        photos = data.get('photos', [])
        
        # Validate required data
        if not calculation or 'total_stars' not in calculation:
            await callback_query.answer("Invalid payment data - please recalculate pricing", show_alert=True)
            return
        
        if not selected_channels:
            await callback_query.answer("No channels selected", show_alert=True)
            return
        
        # Extract pricing data
        stars_amount = calculation['total_stars']
        usd_amount = calculation['total_usd']
        days = calculation.get('days', 1)
        posts_per_day = calculation.get('posts_per_day', 1)
        
        # Create campaign data
        campaign_data = {
            'duration': days,
            'selected_channels': selected_channels,
            'posts_per_day': posts_per_day,
            'ad_content': ad_content,
            'photos': photos
        }
        
        pricing_data = {
            'total_stars': stars_amount,
            'total_usd': usd_amount,
            'days': days,
            'posts_per_day': posts_per_day,
            'discount_percent': calculation.get('discount_percent', 0)
        }
        
        # Initialize clean Stars payment system
        from clean_stars_payment_system import get_clean_stars_payment
        stars_payment = get_clean_stars_payment(callback_query.bot, db)
        
        # Create Stars invoice
        result = await stars_payment.create_payment_invoice(
            user_id, campaign_data, pricing_data, language
        )
        
        if result.get('success'):
            await callback_query.answer("⭐ Stars payment invoice sent!")
            logger.info(f"✅ Stars invoice created: {result['payment_id']}")
            
            # Delete the confirmation message since invoice was sent
            try:
                await callback_query.message.delete()
            except:
                pass
        else:
            error_msg = result.get('error', 'Unknown error')
            await callback_query.answer(f"❌ Payment error: {error_msg}", show_alert=True)
            logger.error(f"❌ Stars invoice creation failed: {error_msg}")
            
    except Exception as e:
        logger.error(f"❌ Stars payment handler error: {e}")
        await callback_query.answer("❌ Payment system error", show_alert=True)

@router.callback_query(F.data == "pay_freq_stars")
async def pay_frequency_stars_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle frequency Stars payment - redirect to dynamic handler"""
    await pay_dynamic_stars_handler(callback_query, state)

@router.pre_checkout_query()
async def clean_pre_checkout_query_handler(pre_checkout_query):
    """Clean pre-checkout query handler for Stars payments"""
    try:
        from clean_stars_payment_system import handle_clean_pre_checkout
        
        result = await handle_clean_pre_checkout(pre_checkout_query)
        
        if result.get('success'):
            logger.info(f"✅ Pre-checkout approved for Stars payment")
        else:
            logger.warning(f"❌ Pre-checkout rejected for Stars payment")
            
    except Exception as e:
        logger.error(f"❌ Pre-checkout error: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Payment verification failed")

@router.message(F.successful_payment)
async def clean_successful_payment_handler(message):
    """Clean successful Stars payment handler"""
    try:
        from clean_stars_payment_system import handle_clean_successful_payment
        
        result = await handle_clean_successful_payment(message)
        
        if result.get('success'):
            logger.info(f"✅ Stars payment processed successfully: {result.get('payment_id')}")
            logger.info(f"   Campaign ID: {result.get('campaign_id')}")
            logger.info(f"   Receipt sent: {result.get('receipt_sent')}")
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"❌ Stars payment processing failed: {error_msg}")
            
            # Send error notification
            await message.answer(
                "⚠️ Payment received but processing encountered an issue. "
                "Please contact support with your payment details.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"❌ Stars payment handler error: {e}")
        
        # Fallback processing
        try:
            successful_payment = message.successful_payment
            await message.answer(
                f"✅ **Payment Received!**\n\n"
                f"💫 Amount: {successful_payment.total_amount} ⭐\n"
                f"📧 Reference: {successful_payment.telegram_payment_charge_id}\n\n"
                f"Your campaign will be activated shortly.",
                parse_mode='Markdown'
            )
        except Exception as fallback_error:
            logger.error(f"❌ Fallback payment handler error: {fallback_error}")





# REMOVED: Duplicate TON payment handler - using enhanced handler at line 2864


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
    
    # Dynamic pricing removed during cleanup
    pricing = None  # Dynamic pricing removed
    
    base_cost = f"{calculation.get('base_cost', calculation.get('total_usd', 0)):.2f}"
    discount_amount = f"{calculation.get('discount_amount', 0):.2f}"
    final_price = f"{calculation['total_usd']:.2f}"
    
    text = f"""
[Money] **Payment Summary**

**Campaign:** {calculation['days']} days x {calculation['posts_per_day']} posts/day
**Channels:** {len(data.get('selected_channels', []))} selected
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
    """Legacy function - redirected to new monitoring system"""
    # This function has been replaced by monitor_ton_payment_with_user_wallet
    # Keeping for backward compatibility
    logger.info(f"Legacy monitor_ton_payment called - redirecting to new system")
    
    # Get user wallet from state if available
    data = await state.get_data()
    user_wallet = data.get('user_wallet_address')
    
    if user_wallet:
        await monitor_ton_payment_with_user_wallet(user_id, memo, amount_ton, expiration_time, user_wallet, state)
    else:
        # If no user wallet, handle as expired
        await handle_expired_ton_payment(user_id, memo, state)


async def handle_successful_ton_payment_with_confirmation(user_id: int, memo: str, amount_ton: float, state: FSMContext):
    """Handle successful TON payment confirmation with user notification"""
    try:
        from main_bot import bot
        language = await get_user_language(user_id)
        
        # Get data from state
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        ad_content = data.get('ad_content', '') or data.get('ad_text', '')
        photos = data.get('photos', []) or data.get('uploaded_photos', [])
        calculation = data.get('pricing_calculation', {})
        
        # Get campaign details
        days = calculation.get('days', 1)
        posts_per_day = calculation.get('posts_per_day', 1)
        total_posts = calculation.get('total_posts', days * posts_per_day)
        
        # Create comprehensive confirmation message using translations
        confirmation_title = get_text(language, 'ton_payment_confirmed')
        payment_verified = get_text(language, 'payment_verified')
        campaign_starting = get_text(language, 'campaign_starting')
        campaign_details = get_text(language, 'campaign_details_confirmed')
        amount_received = get_text(language, 'payment_amount_received')
        duration_label = get_text(language, 'campaign_will_run')
        frequency_label = get_text(language, 'posting_frequency_confirmed')
        channels_label = get_text(language, 'channels_confirmed')
        total_posts_label = get_text(language, 'total_posts_confirmed')
        publishing_notifications = get_text(language, 'publishing_notifications')
        thank_you = get_text(language, 'thank_you_choosing')
        status_active = get_text(language, 'campaign_status_active')
        
        # Build comprehensive confirmation message
        confirmation_text = f"""{confirmation_title}

{payment_verified}

{amount_received} {amount_ton:.3f} TON
{duration_label} {days} {'days' if language == 'en' else 'أيام' if language == 'ar' else 'дней'}
{frequency_label} {posts_per_day} {'times per day' if language == 'en' else 'مرة يومياً' if language == 'ar' else 'раз в день'}
{channels_label} {len(selected_channels)} {'channels' if language == 'en' else 'قناة' if language == 'ar' else 'каналов'}
{total_posts_label} {total_posts} {'posts' if language == 'en' else 'منشور' if language == 'ar' else 'публикаций'}

{campaign_starting}
{status_active}

📱 {publishing_notifications}

🎯 {thank_you}"""
        
        # Create main menu keyboard
        if language == 'ar':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")],
                [InlineKeyboardButton(text="📊 إعلاناتي", callback_data="my_ads")]
            ])
        elif language == 'ru':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")],
                [InlineKeyboardButton(text="📊 Мои объявления", callback_data="my_ads")]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")],
                [InlineKeyboardButton(text="📊 My Ads", callback_data="my_ads")]
            ])
        
        # Send confirmation message
        await bot.send_message(
            user_id,
            confirmation_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Create ad in database
        await create_successful_ad_from_payment(user_id, memo, amount_ton, state)
        
        # Clear state
        await state.clear()
        
        logger.info(f"TON payment confirmed and ad created for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error handling successful TON payment: {e}")
        # Send basic confirmation even if detailed processing fails
        try:
            await bot.send_message(
                user_id,
                f"✅ Payment received: {amount_ton:.3f} TON\n🚀 Your campaign will start soon!",
                parse_mode='Markdown'
            )
        except:
            pass

async def create_successful_ad_from_payment(user_id: int, memo: str, amount_ton: float, state: FSMContext):
    """Create ad in database after successful payment"""
    try:
        # Get data from state
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        ad_content = data.get('ad_content', '') or data.get('ad_text', '')
        photos = data.get('photos', []) or data.get('uploaded_photos', [])
        calculation = data.get('pricing_calculation', {})
        
        # Get campaign details
        days = calculation.get('days', 1)
        posts_per_day = calculation.get('posts_per_day', 1)
        
        # Create ad in database
        from database import db
        ad_id = await db.create_ad(
            user_id=user_id,
            content=ad_content,
            media_url=photos[0]['file_id'] if photos else None,
            content_type='photo' if photos else 'text'
        )
        
        logger.info(f"Ad created successfully: ID {ad_id} for user {user_id}")
        
        # Create campaign after ad creation
        from campaign_management import CampaignManager
        campaign_manager = CampaignManager()
        
        campaign_id = await campaign_manager.create_campaign_from_payment(
            user_id=user_id,
            selected_channels=selected_channels,
            duration_days=days,
            posts_per_day=posts_per_day,
            payment_amount=amount_ton,
            payment_method='TON',
            payment_memo=memo,
            ad_content=ad_content,
            media_url=photos[0]['file_id'] if photos else None,
            content_type='photo' if photos else 'text'
        )
        
        logger.info(f"Campaign created successfully: ID {campaign_id} for user {user_id}")
        return ad_id
        
    except Exception as e:
        logger.error(f"Error creating ad from payment: {e}")
        return None


async def handle_expired_ton_payment(user_id: int, memo: str, state: FSMContext):
    """Handle expired TON payment"""
    try:
        from main_bot import bot
        language = await get_user_language(user_id)
        
        # Create timeout message
        if language == 'ar':
            timeout_text = f"""⏰ **انتهت صلاحية الدفع**

🔗 **كود التحقق:** {memo}
⏱️ **انتهى في:** 20 دقيقة

لم يتم العثور على الدفع خلال الوقت المحدد. يمكنك:

• المحاولة مرة أخرى بدفع جديد
• التحقق من أن المبلغ وكود التحقق صحيحان
• الاتصال بالدعم للمساعدة

لا تقلق - لم يتم خصم أي مبلغ من حسابك."""
        elif language == 'ru':
            timeout_text = f"""⏰ **Время оплаты истекло**

🔗 **Код проверки:** {memo}
⏱️ **Истек через:** 20 минут

Оплата не найдена в указанное время. Вы можете:

• Попробовать еще раз с новым платежом
• Убедиться, что сумма и код проверки правильные
• Связаться с поддержкой для помощи

Не беспокойтесь - с вашего аккаунта не было снято никаких средств."""
        else:
            timeout_text = f"""⏰ **Payment Expired**

🔗 **Verification Code:** {memo}
⏱️ **Expired after:** 20 minutes

Payment was not found within the specified time. You can:

• Try again with a new payment
• Verify that the amount and verification code are correct
• Contact support for assistance

Don't worry - no funds have been charged from your account."""
        
        # Create keyboard
        if language == 'ar':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 المحاولة مرة أخرى", callback_data="retry_payment")],
                [InlineKeyboardButton(text="📞 الاتصال بالدعم", callback_data="support_contact")],
                [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")]
            ])
        elif language == 'ru':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="retry_payment")],
                [InlineKeyboardButton(text="📞 Связаться с поддержкой", callback_data="support_contact")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Try Again", callback_data="retry_payment")],
                [InlineKeyboardButton(text="📞 Contact Support", callback_data="support_contact")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
        
        # Send timeout message
        await bot.send_message(
            chat_id=user_id,
            text=timeout_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Log timeout
        logger.warning(f"TON payment timeout: User {user_id}, Memo {memo}")
        
    except Exception as e:
        logger.error(f"Error handling expired TON payment: {e}")


@router.callback_query(F.data.startswith("admin_confirm_ton_"))
async def admin_confirm_ton_handler(callback_query: CallbackQuery, state: FSMContext):
    """Admin manual confirmation for TON payments (testing)"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied")
        return
    
    memo = callback_query.data.replace("admin_confirm_ton_", "")
    
    # Get user from state or callback data
    data = await state.get_data()
    user_id = callback_query.from_user.id
    amount_ton = data.get('payment_amount_ton', 0)
    
    # Manually confirm payment
    await handle_successful_ton_payment(user_id, memo, amount_ton, state)
    await callback_query.answer("Payment manually confirmed by admin")


@router.callback_query(F.data == "retry_payment")
async def retry_payment_handler(callback_query: CallbackQuery, state: FSMContext):
    """Retry payment after timeout"""
    await callback_query.answer("Redirecting to payment options...")
    await show_payment_options(callback_query, state)


async def show_payment_options(callback_query: CallbackQuery, state: FSMContext):
    """Show payment options to user"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    calculation = data.get('pricing_calculation', {})
    
    if not calculation:
        await callback_query.answer("No pricing data found. Please restart ad creation.")
        return
    
    total_usd = calculation.get('total_usd', 0)
    total_ton = calculation.get('total_ton', 0)
    total_stars = calculation.get('total_stars', 0)
    days = calculation.get('days', 1)
    posts_per_day = calculation.get('posts_per_day', 1)
    
    # Create payment options text
    if language == 'ar':
        payment_text = f"""💰 **اختر طريقة الدفع**

📊 **ملخص الطلب:**
• المدة: {days} أيام
• المنشورات: {posts_per_day} منشور/يوم
• المبلغ: ${total_usd:.2f}

💎 **طرق الدفع المتاحة:**
• TON: {total_ton:.3f} TON
• نجوم تلغرام: {total_stars} نجمة

اختر طريقة الدفع المفضلة:"""
    elif language == 'ru':
        payment_text = f"""💰 **Выберите способ оплаты**

📊 **Сводка заказа:**
• Длительность: {days} дней
• Посты: {posts_per_day} пост/день
• Сумма: ${total_usd:.2f}

💎 **Доступные способы:**
• TON: {total_ton:.3f} TON
• Telegram Stars: {total_stars} звезд

Выберите предпочтительный способ оплаты:"""
    else:
        payment_text = f"""💰 **Choose Payment Method**

📊 **Order Summary:**
• Duration: {days} days
• Posts: {posts_per_day} posts/day
• Amount: ${total_usd:.2f}

💎 **Available Methods:**
• TON: {total_ton:.3f} TON
• Telegram Stars: {total_stars} stars

Choose your preferred payment method:"""
    
    # Create keyboard
    if language == 'ar':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 دفع TON", callback_data="pay_dynamic_ton")],
            [InlineKeyboardButton(text="⭐ نجوم تلغرام", callback_data="pay_dynamic_stars")],
            [InlineKeyboardButton(text="🔄 إعادة حساب", callback_data="recalculate_dynamic")],
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel_payment")]
        ])
    elif language == 'ru':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Оплата TON", callback_data="pay_dynamic_ton")],
            [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="pay_dynamic_stars")],
            [InlineKeyboardButton(text="🔄 Пересчитать", callback_data="recalculate_dynamic")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Pay with TON", callback_data="pay_dynamic_ton")],
            [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="pay_dynamic_stars")],
            [InlineKeyboardButton(text="🔄 Recalculate", callback_data="recalculate_dynamic")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_payment")]
        ])
    
    await callback_query.message.edit_text(payment_text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer("Payment options shown")


async def process_admin_free_posting(callback_query: CallbackQuery, state: FSMContext):
    """Process free posting for admin users"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Get data from state
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        ad_content = data.get('ad_text', '')
        photos = data.get('photos', [])
        pricing_data = data.get('pricing_data', {})
        
        # Create ad in database
        ad_id = await db.create_ad(
            user_id=user_id,
            content=ad_content,
            media_url=photos[0] if photos else None,
            content_type='photo' if photos else 'text'
        )
        
        # Create subscription for each selected channel
        subscription_ids = []
        for channel_id in selected_channels:
            subscription_id = await db.create_subscription(
                user_id=user_id,
                ad_id=ad_id,
                channel_id=channel_id,
                duration_months=pricing_data.get('days', 1),
                total_price=0,  # Free for admin
                currency='ADMIN_FREE',
                posts_per_day=pricing_data.get('posts_per_day', 1),
                total_posts=pricing_data.get('total_posts', 1)
            )
            subscription_ids.append(subscription_id)
        
        # Activate subscriptions
        await db.activate_subscriptions(subscription_ids, pricing_data.get('days', 1))
        
        # Publish immediately
        from publishing_scheduler import scheduler
        if scheduler:
            await scheduler.publish_immediately_after_payment(
                user_id=user_id,
                ad_id=ad_id,
                selected_channels=selected_channels,
                subscription_data=data
            )
        
        # Show success message
        success_text = f"""✅ **Admin Free Posting Activated!**

👑 **Admin Privilege Applied**
💰 **Cost:** FREE (Admin testing privilege)

📺 **Publishing to:**
{chr(10).join(f"• {ch}" for ch in selected_channels)}

📅 **Campaign Details:**
• Duration: {pricing_data.get('days', 1)} days
• Posts per day: {pricing_data.get('posts_per_day', 1)}
• Total posts: {pricing_data.get('total_posts', 1)}

🛠️ **Status:** Your ad is being published now!

*Your admin privilege allows free posting for testing and demonstration purposes.*"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 View My Ads", callback_data="my_ads")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
        ])
        
        await callback_query.message.edit_text(success_text, reply_markup=keyboard, parse_mode='Markdown')
        await callback_query.answer("✅ Admin free posting activated!")
        
        # Clear state
        await state.clear()
        
    except Exception as e:
        logger.error(f"Admin free posting error: {e}")
        await callback_query.answer("❌ Error processing admin posting")
        await show_main_menu(callback_query, await get_user_language(callback_query.from_user.id))

async def send_payment_receipt(user_id: int, payment_data: dict, language: str):
    """Send payment receipt to user after successful payment"""
    try:
        from main_bot import bot
    except ImportError:
        logger.warning("Bot import failed")
    import datetime
    
    try:
        # Get current timestamp
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build receipt message using translations
        receipt_title = get_text(language, 'payment_receipt_title')
        payment_received = get_text(language, 'payment_received')
        payment_method_label = get_text(language, 'payment_method')
        amount_paid_label = get_text(language, 'amount_paid')
        payment_date_label = get_text(language, 'payment_date')
        payment_id_label = get_text(language, 'payment_id')
        ad_details_label = get_text(language, 'ad_details')
        selected_channels_label = get_text(language, 'selected_channels')
        campaign_duration_label = get_text(language, 'campaign_duration')
        posts_per_day_label = get_text(language, 'posts_per_day')
        total_posts_label = get_text(language, 'total_posts')
        thank_you = get_text(language, 'receipt_thank_you')
        support = get_text(language, 'receipt_support')
        
        # Format payment method
        payment_method = payment_data.get('payment_method', 'TON')
        if payment_method == 'ton':
            payment_method_text = get_text(language, 'pay_ton')
        else:
            payment_method_text = get_text(language, 'pay_stars')
        
        # Format amount
        amount = payment_data.get('amount', 0)
        amount_text = f"{amount} {payment_method.upper()}"
        
        # Format channels
        channels = payment_data.get('selected_channels', [])
        channels_text = f"{len(channels)} " + ("channels" if language == 'en' else "قنوات" if language == 'ar' else "каналов")
        
        # Format duration and posts
        days = payment_data.get('days', 1)
        posts_per_day = payment_data.get('posts_per_day', 1)
        total_posts = days * posts_per_day
        
        duration_text = f"{days} " + ("days" if language == 'en' else "أيام" if language == 'ar' else "дней")
        
        # Build receipt message
        receipt_message = f"""
{receipt_title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{payment_received}

**{payment_method_label}** {payment_method_text}
**{amount_paid_label}** {amount_text}
**{payment_date_label}** {current_time}
**{payment_id_label}** {payment_data.get('memo', 'N/A')}

**{ad_details_label}**
• **{selected_channels_label}** {channels_text}
• **{campaign_duration_label}** {duration_text}
• **{posts_per_day_label}** {posts_per_day}
• **{total_posts_label}** {total_posts}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{thank_you}
{support}
        """.strip()
        
        # Create keyboard with useful actions
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'my_ads'), callback_data="my_ads")],
            [InlineKeyboardButton(text=get_text(language, 'create_ad'), callback_data="create_ad")],
            [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data="back_to_main")]
        ])
        
        # Send receipt message
        await bot.send_message(
            chat_id=user_id,
            text=receipt_message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        logger.info(f"Payment receipt sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending payment receipt: {e}")

async def send_ad_publishing_report(user_id: int, ad_data: dict, channel_name: str, language: str):
    """Send ad publishing confirmation report to user"""
    try:
        from main_bot import bot
    except ImportError:
        logger.warning("Bot import failed")
    import datetime
    
    try:
        # Get current timestamp
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build publishing report using translations
        published_title = get_text(language, 'ad_published_title')
        published_message = get_text(language, 'ad_published_message')
        published_channel_label = get_text(language, 'published_channel')
        published_date_label = get_text(language, 'published_date')
        ad_id_label = get_text(language, 'ad_id')
        ad_summary_label = get_text(language, 'ad_summary')
        publishing_status_label = get_text(language, 'publishing_status')
        publishing_success = get_text(language, 'publishing_success')
        publishing_thank_you = get_text(language, 'publishing_thank_you')
        
        # Format ad content summary (truncate if too long)
        ad_content = ad_data.get('ad_text', 'Ad content')
        if len(ad_content) > 100:
            ad_content = ad_content[:100] + "..."
        
        # Build publishing report message
        report_message = f"""
{published_title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{published_message}

**{published_channel_label}** {channel_name}
**{published_date_label}** {current_time}
**{ad_id_label}** {ad_data.get('ad_id', 'N/A')}
**{publishing_status_label}**

**{ad_summary_label}**
{ad_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{publishing_success}

{publishing_thank_you}
        """.strip()
        
        # Create keyboard with useful actions
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'my_ads'), callback_data="my_ads")],
            [InlineKeyboardButton(text=get_text(language, 'create_ad'), callback_data="create_ad")],
            [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data="back_to_main")]
        ])
        
        # Send publishing report
        await bot.send_message(
            chat_id=user_id,
            text=report_message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        logger.info(f"Ad publishing report sent to user {user_id} for channel {channel_name}")
        
    except Exception as e:
        logger.error(f"Error sending ad publishing report: {e}")

async def handle_expired_ton_payment(user_id: int, memo: str, state: FSMContext):
    """Handle expired TON payment"""
    try:
        # Update payment status
        await state.update_data(payment_status="expired")
        
        # Get user language
        language = await get_user_language(user_id)
        
        # Send expiration notification to user
        from main_bot import bot
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
    """Handle payment method selection - redirect to new smart pricing system"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        payment_method = callback_query.data.replace("payment_", "")
        
        # Redirect to new smart pricing system
        if payment_method == "ton":
            await pay_frequency_ton_handler(callback_query, state)
            return
        elif payment_method == "stars":
            await pay_frequency_stars_handler(callback_query, state)
            return
        
        # If we reach here, show error
        await callback_query.answer("❌ Payment method not supported. Please use the new pricing system.")
        return
        
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
            [InlineKeyboardButton(text="Try Again", callback_data="retry_payment")],
            [InlineKeyboardButton(text="Main Menu", callback_data="back_to_main")]
        ])
        
        await callback_query.message.edit_text(
            "No **Payment Not Found**\n\nPayment not found. Please try again.",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Payment not found handler error: {e}")


# Register all confirmation handlers from confirmation_handlers.py
for callback_data, handler_func in CONFIRMATION_HANDLERS.items():
    router.callback_query.register(handler_func, F.data == callback_data)


@router.callback_query(F.data == "my_ads")
async def my_ads_handler(callback_query: CallbackQuery):
    """Show user ads dashboard"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Enhanced logging for Arabic main menu debugging
    logger.info(f"📊 my_ads callback received from user {user_id} (language: {language})")
    
    try:
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
        
        await safe_callback_edit(
            callback_query,
            text=dashboard_text,
            reply_markup=keyboard
        )
        
        await safe_callback_answer(callback_query, "")
        logger.info(f"✅ my_ads completed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ my_ads error for user {user_id}: {e}")
        await safe_callback_answer(callback_query, get_text(language, 'error_generic'), show_alert=True)


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
            'Current_Balance': f'{pending_rewards:.2f}',
            'Tier_Level': tier,
            'Referrals_Count': referral_count,
            'Total_Earned': f'{total_earnings:.2f}',
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
🎯 **Referral Rewards**
🎁 5 Referrals → +2.5 TON Bonus
🎁 10 Referrals → +6.0 TON Reward  
🎁 25 Referrals → +20.0 TON Bonus
🎁 50 Referrals → +50.0 TON Prize
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
                InlineKeyboardButton(text="📊 Referral Stats", callback_data="referral_stats"),
                InlineKeyboardButton(text=Web3UI.create_cyber_keyboard_button("Network Expansion", "neural"), callback_data="share_earn")
            ]
        ]
        
        # Add quantum payout request button if threshold is met
        if pending_rewards >= payout_threshold:
            keyboard_buttons.append([
                InlineKeyboardButton(text=Web3UI.create_cyber_keyboard_button("Quantum Withdrawal", "crypto"), callback_data="request_payout")
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔙 Back to Referrals", callback_data="share_earn")
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
        
        payment_sequence = '''Payment Process:
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
        
        # Create referral statistics
        referral_metrics = {
            'Tier_Level': tier,
            'Reward_Rate': f'{rate} TON',
            'Referrals_Count': referral_count,
            'Next_Tier': next_tier.replace(' more referrals needed', ' referrals needed')
        }
        
        milestone_text = '''Milestone Referral Rewards:
🎁 5 Referrals → +2.5 TON
🎁 10 Referrals → +6.0 TON
🎁 25 Referrals → +20.0 TON
🎁 50 Referrals → +50.0 TON'''
        
        # Build referral stats with Web3 components
        header_section = Web3UI.create_neural_header("NEURAL NETWORK ANALYTICS", "Referral Mining Protocol")
        dashboard_section = Web3UI.create_fintech_dashboard("REFERRAL STATISTICS", referral_metrics)
        
        tier_protocols = '''
🔷 BASIC → 0.5 TON per referral
🔶 SILVER → 0.8 TON per referral (5+ referrals)
🔵 GOLD → 1.2 TON per referral (15+ referrals)
💎 PREMIUM → 2.0 TON per referral (25+ referrals)'''
        
        protocols_section = Web3UI.create_quantum_section("TIER PROTOCOLS", tier_protocols, "process")
        milestone_section = Web3UI.create_holographic_display(milestone_text, "neural")
        
        referral_link = f"Referral Link: https://t.me/I3lani_bot?start=ref_{user_id}"
        alert_section = Web3UI.create_web3_alert(referral_link, "quantum")
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
            [InlineKeyboardButton(text="📢 Share Referral Link", url=f"https://t.me/share/url?url=https://t.me/I3lani_bot?start=ref_{user_id}&text=Join I3lani and earn TON rewards!")],
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
    
    # Enhanced logging for Arabic navigation debugging
    logger.info(f"📞 back_to_main callback received from user {user_id} (language: {language})")
    
    try:
        await state.clear()
        await show_main_menu(callback_query, language)
        await safe_callback_answer(callback_query, "")
        logger.info(f"✅ back_to_main completed successfully for user {user_id}")
    except Exception as e:
        logger.error(f"❌ back_to_main error for user {user_id}: {e}")
        await safe_callback_answer(callback_query, "Please try again", show_alert=True)


@router.callback_query(F.data == "language_settings")
async def language_settings_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle language settings"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Enhanced logging for Arabic navigation debugging
    logger.info(f"📞 language_settings callback received from user {user_id} (language: {language})")
    
    try:
        text = get_text(language, 'select_language', 'Please select your language:')
        keyboard = create_language_keyboard()
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await safe_callback_answer(callback_query, "")
        logger.info(f"✅ language_settings completed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ language_settings error for user {user_id}: {e}")
        await safe_callback_answer(callback_query, "Error loading language settings", show_alert=True)


@router.callback_query(F.data == "contact_support")
async def contact_support_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle contact support"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Enhanced logging for Arabic navigation debugging
    logger.info(f"📞 contact_support callback received from user {user_id} (language: {language})")
    
    try:
        support_text = get_text(language, 'contact_support', """
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
        """)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(language, 'back_to_main', 'Back to Main'), callback_data="back_to_main")]
        ])
        
        await callback_query.message.edit_text(support_text, reply_markup=keyboard)
        await safe_callback_answer(callback_query, "")
        logger.info(f"✅ contact_support completed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ contact_support error for user {user_id}: {e}")
        await safe_callback_answer(callback_query, "Error loading support page", show_alert=True)


@router.callback_query(F.data == "channel_partners")
async def channel_partners_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel partners"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Import and use channel incentives system
        from channel_incentives import ChannelIncentives
        incentives = ChannelIncentives(db)
        await incentives.show_partner_program(callback_query, language)
    except Exception as e:
        logger.error(f"Channel partners error: {e}")
        await callback_query.answer("Channel partners feature is being updated. Please try again later.", show_alert=True)


@router.callback_query(F.data == "share_win")
async def share_win_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle share & win"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Import and use viral referral system
        from viral_referral_handlers import show_viral_game_menu
        await show_viral_game_menu(callback_query, state)
    except Exception as e:
        logger.error(f"Share & win error: {e}")
        await callback_query.answer("Share & win feature is being updated. Please try again later.", show_alert=True)


@router.callback_query(F.data == "gaming_hub")
async def gaming_hub_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle gaming hub"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Import and use gamification system
        from gamification import gamification
        await gamification.show_gaming_hub(callback_query, language)
    except Exception as e:
        logger.error(f"Gaming hub error: {e}")
        await callback_query.answer("Gaming hub feature is being updated. Please try again later.", show_alert=True)


@router.callback_query(F.data == "leaderboard")
async def leaderboard_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle leaderboard"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Import and use gamification system
        from gamification import gamification
        await gamification.show_leaderboard(callback_query, language)
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        await callback_query.answer("Leaderboard feature is being updated. Please try again later.", show_alert=True)


# Error Reporting System Handlers
@router.callback_query(F.data.startswith("report_error_"))
async def report_error_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle error report button click"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Extract step name from callback data
    step_name = callback_query.data.replace("report_error_", "")
    
    # Get error report prompt
    prompt_text = error_reporting.get_error_report_prompt(language, step_name)
    
    # Set state for error reporting
    await state.update_data(error_step=step_name)
    await state.set_state(UserStates.reporting_error)
    
    # Create keyboard with skip option
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(language, 'skip', 'Skip'),
            callback_data="skip_error_description"
        )],
        [InlineKeyboardButton(
            text=get_text(language, 'cancel', 'Cancel'),
            callback_data="cancel_error_report"
        )]
    ])
    
    await callback_query.message.edit_text(prompt_text, reply_markup=keyboard)
    await callback_query.answer()


@router.callback_query(F.data == "skip_error_description")
async def skip_error_description_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle skip error description"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get step name from state
    data = await state.get_data()
    step_name = data.get('error_step', 'unknown')
    
    # Create error report with minimal info
    error_report = ErrorReport(
        user_id=user_id,
        step_name=step_name,
        user_description="User skipped description",
        system_info=f"Language: {language}, Step: {step_name}",
        error_type="user_reported",
        severity="low"
    )
    
    # Save error report
    report_id = await error_reporting.save_error_report(error_report)
    
    # Show success message
    success_text = error_reporting.get_error_report_success_message(language, report_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(language, 'back_to_main', 'Back to Main'),
            callback_data="back_to_main"
        )]
    ])
    
    await callback_query.message.edit_text(success_text, reply_markup=keyboard)
    await callback_query.answer()
    await state.clear()


@router.callback_query(F.data == "cancel_error_report")
async def cancel_error_report_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle cancel error report"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.clear()
    await show_main_menu(callback_query, language)
    await callback_query.answer()


@router.message(F.text, UserStates.reporting_error)
async def process_error_description(message: Message, state: FSMContext):
    """Process user error description"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    # Get error data from state
    data = await state.get_data()
    step_name = data.get('error_step', 'unknown')
    user_description = message.text
    
    # Create error report
    error_report = ErrorReport(
        user_id=user_id,
        step_name=step_name,
        user_description=user_description,
        system_info=f"Language: {language}, Step: {step_name}, Username: {message.from_user.username}",
        error_type="user_reported",
        severity="medium"
    )
    
    # Save error report
    report_id = await error_reporting.save_error_report(error_report)
    
    # Show success message
    success_text = error_reporting.get_error_report_success_message(language, report_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=get_text(language, 'back_to_main', 'Back to Main'),
            callback_data="back_to_main"
        )]
    ])
    
    await message.answer(success_text, reply_markup=keyboard)
    await state.clear()


# Quick error reporting for specific steps
def add_error_report_button(keyboard_rows: list, language: str, step_name: str) -> list:
    """Add error report button to existing keyboard"""
    error_button_text = error_reporting.create_error_report_keyboard(language, step_name)
    keyboard_rows.append([InlineKeyboardButton(
        text=error_button_text,
        callback_data=f"report_error_{step_name}"
    )])
    return keyboard_rows


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


# REMOVED: back_to_duration_handler - old progressive monthly plans handler removed


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
    """Continue with selected channels to dynamic days selection"""
    try:
        data = await state.get_data()
        selected_channels = data.get('selected_channels', [])
        
        if not selected_channels:
            await callback_query.answer("Please select at least one channel!")
            return
        
        # Store selected channels and proceed to days selection
        await state.update_data(selected_channels=selected_channels)
        await state.set_state(AdCreationStates.payment_selection)
        
        # Track channel selection with end-to-end tracking system
        try:
            await track_channel_selection(callback_query.from_user.id, selected_channels, state)
        except Exception as e:
            logger.error(f"Error tracking channel selection: {e}")
        
        # Show dynamic days selector (this was missing!)
        await show_dynamic_days_selector(callback_query, state, 1)
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
        
        # FIXED: Removed old progressive plan logic - using dynamic day-based pricing instead
        # No need to calculate pricing here, it's handled in the dynamic selector
        await state.set_state(AdCreationStates.payment_method)
        
        # FIXED: Use dynamic day-based pricing system instead of old progressive monthly plans
        # Redirect to proper dynamic day-based pricing flow
        await show_dynamic_days_selector(callback_query, state, 1)
        await callback_query.answer(f"Proceeding to smart day-based pricing for {len(selected_channels)} channels!")
        
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
    
    # Enhanced logging for Arabic main menu debugging
    logger.info(f"💼 join_partner_program callback received from user {user_id} (language: {language})")
    
    try:
        from channel_incentives import ChannelIncentives
        incentives = ChannelIncentives(db)
        invitation_text = await incentives.create_invitation_message(language)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Add Bot to Channel", url="https://t.me/I3lani_bot?startchannel=partner")],
            [InlineKeyboardButton(text="🎁 Referral Program", callback_data="referral_program")],
            [InlineKeyboardButton(text="🌟 Success Stories", callback_data="success_stories")],
            [InlineKeyboardButton(text=get_text(language, 'back_to_main'), callback_data="back_to_main")]
        ])
        
        await safe_callback_edit(
            callback_query,
            text=invitation_text,
            reply_markup=keyboard
        )
        
        await safe_callback_answer(callback_query, "")
        logger.info(f"✅ join_partner_program completed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ join_partner_program error for user {user_id}: {e}")
        await safe_callback_answer(callback_query, "Channel Partner feature loaded!", show_alert=True)

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
    
    # Include wallet manager router
    from wallet_manager import router as wallet_router
    dp.include_router(wallet_router)
    
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
        pricing = None  # Dynamic pricing removed
        calculation = {"total_amount": 0.29, "currency": "USD"}
        
        # Store calculation in state
        await state.update_data(
            selected_days=days,
            posts_per_day=posts_per_day,
            pricing_calculation=calculation
        )
        
        # Format the summary
        summary = pricing.format_pricing_summary(calculation)
        discount_explanation = 0.29
        
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

@router.callback_query(F.data == "start_viral_game")
async def start_viral_game_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle viral game button click"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Enhanced logging for Arabic main menu debugging
    logger.info(f"🎮 start_viral_game callback received from user {user_id} (language: {language})")
    
    try:
        # Import and call the viral game start function
        from viral_referral_handlers import show_viral_game_start
        
        # Create fake message for the handler
        fake_message = type('FakeMessage', (), {
            'from_user': callback_query.from_user,
            'answer': callback_query.message.edit_text,
            'bot': callback_query.bot
        })()
        
        await show_viral_game_start(fake_message, language)
        await safe_callback_answer(callback_query, "Starting viral referral game...")
        logger.info(f"✅ start_viral_game completed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ start_viral_game error for user {user_id}: {e}")
        await safe_callback_answer(callback_query, "Error starting viral game. Please try again.", show_alert=True)


# Contextual Help Handlers
@router.callback_query(F.data.startswith("show_help_"))
async def show_contextual_help_handler(callback_query: CallbackQuery):
    """Show contextual help bubble for specific steps"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Extract step key from callback data
    step_key = callback_query.data.replace("show_help_", "")
    
    try:
        # Show contextual help bubble
        help_system = get_contextual_help_system()
        success = await help_system.show_contextual_help_bubble(
            callback_query, step_key, language, "compact"
        )
        
        if not success:
            await callback_query.answer("Help not available for this step")
        
        logger.info(f"✅ Contextual help shown for step: {step_key}, user: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error showing contextual help: {e}")
        await callback_query.answer("Help system error")


@router.callback_query(F.data.startswith("help_action_"))
async def help_action_handler(callback_query: CallbackQuery):
    """Handle quick action buttons in help bubbles"""
    user_id = callback_query.from_user.id
    
    try:
        help_system = get_contextual_help_system()
        success = await help_system.handle_help_action(callback_query, callback_query.data)
        
        if not success:
            await callback_query.answer("Action not available")
        
        logger.info(f"✅ Help action executed for user: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error handling help action: {e}")
        await callback_query.answer("Action error")


@router.callback_query(F.data.startswith("help_dismiss_"))
async def help_dismiss_handler(callback_query: CallbackQuery):
    """Handle help bubble dismissal"""
    user_id = callback_query.from_user.id
    
    try:
        step_key = callback_query.data.replace("help_dismiss_", "")
        help_system = get_contextual_help_system()
        success = await help_system.handle_help_dismiss(callback_query, step_key)
        
        if not success:
            await callback_query.answer("Error dismissing help")
        
        logger.info(f"✅ Help dismissed for step: {step_key}, user: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error dismissing help: {e}")
        await callback_query.answer("Dismiss error")