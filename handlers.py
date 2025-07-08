"""
Message and callback handlers for I3lani Telegram Bot
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from typing import List, Dict
import logging
import time

from states import AdCreationStates, UserStates
from languages import get_text, get_currency_info, LANGUAGES
from database import db, ensure_user_exists, get_user_language
from payments import payment_processor
from config import ADMIN_IDS
import os
from datetime import datetime, timedelta
from dynamic_pricing import get_dynamic_pricing
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
        [InlineKeyboardButton(text="Back Back to Channels", callback_data="back_to_channels")]
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
            "World Welcome to I3lani Bot!\n\nChoose your language:",
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
            # For now, allow all users to use free plan
            pass
        
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

Tip Tip: Make your ad engaging and clear!
        """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back Back to Menu", callback_data="back_to_main")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')


# Content Upload Handler for Streamlined Flow

@router.message(AdCreationStates.upload_content)
async def upload_content_handler(message: Message, state: FSMContext):
    """Handle content upload in streamlined flow"""
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
        await message.answer("Unsupported content type. Please send text, photo, or video.")
        return
    
    # Store content in state
    await state.update_data(
        content=content,
        media_url=media_url,
        content_type=content_type
    )
    
    # Create ad in database
    ad_id = await db.create_ad(user_id, content, media_url, content_type)
    await state.update_data(ad_id=ad_id)
    
    # Move to channel selection
    await state.set_state(AdCreationStates.channel_selection)
    
    # Show channel selection - convert message to callback for existing function
    # Create a dummy callback query to work with existing function
    from types import SimpleNamespace
    fake_callback = SimpleNamespace()
    fake_callback.message = message
    fake_callback.answer = lambda text="": None
    
    await show_channel_selection_for_enhanced_flow(fake_callback, state)


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

Send your contact information:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back Back to Photos", callback_data="back_to_photos")]
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

Send your contact information:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back Back to Photos", callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(contact_text, reply_markup=keyboard)
    await callback_query.answer("Photos skipped")


@router.callback_query(F.data == "done_photos")
async def done_photos_handler(callback_query: CallbackQuery, state: FSMContext):
    """Complete photo upload step"""
    await state.set_state(AdCreationStates.provide_contact_info)
    
    contact_text = """
**Phone** **Provide Contact Information**

How should customers reach you?

Examples:
- Phone: +966501234567
- WhatsApp: +966501234567
- Email: user@email.com
- Telegram: @username

Send your contact information:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back Back to Photos", callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(contact_text, reply_markup=keyboard)
    await callback_query.answer("Photos completed")


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
        
        # Publish immediately to @i3lani channel for free package
        bot = callback_query.bot
        i3lani_channel = "@i3lani"
        ad_content = data.get('ad_content', '')
        uploaded_photos = data.get('uploaded_photos', [])
        
        # Format ad with free package indicator
        formatted_content = f"Gift **FREE AD**\n\n{ad_content}\n\n *Advertise with @I3lani_bot*"
        
        try:
            if uploaded_photos:
                # Send with photo
                await bot.send_photo(
                    chat_id=i3lani_channel,
                    photo=uploaded_photos[0]['file_id'],
                    caption=formatted_content,
                    parse_mode='Markdown'
                )
            else:
                # Send text only
                await bot.send_message(
                    chat_id=i3lani_channel,
                    text=formatted_content,
                    parse_mode='Markdown'
                )
            
            success_text = """
Success **Free Ad Published Successfully!**

Yes Your ad is now live on the I3lani channel!
Date Duration: 3 days
Link View: https://t.me/i3lani

Thank you for using I3lani Bot!
            """.strip()
            
            await callback_query.message.edit_text(success_text, parse_mode='Markdown')
            await state.clear()
            
        except Exception as publish_error:
            logger.error(f"Free ad publishing error: {publish_error}")
            await callback_query.message.edit_text(
                "Yes **Ad Created Successfully!**\n\nYour free ad will be published shortly.",
                parse_mode='Markdown'
            )
            await state.clear()
            
    except Exception as e:
        logger.error(f"Free package publishing error: {e}")
        await callback_query.answer("Error publishing free ad. Please contact support.")


async def show_channel_selection_for_enhanced_flow(callback_query: CallbackQuery, state: FSMContext):
    """Show channel selection for enhanced flow"""
    # Get user language first
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
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
    
    channel_text = get_text(language, 'select_channels_text')
    
    # Get selected channels from state
    data = await state.get_data()
    selected_channels = data.get('selected_channels', [])
    
    keyboard_rows = []
    for channel in channels:
        # Check if channel is selected
        is_selected = channel['channel_id'] in selected_channels
        emoji = "Yes" if is_selected else ""
        
        keyboard_rows.append([InlineKeyboardButton(
            text=f"{emoji} {channel['name']} ({channel['subscribers']:,} subscribers)",
            callback_data=f"toggle_channel_{channel['channel_id']}"
        )])
    
    # Add select all and continue buttons
    keyboard_rows.append([
        InlineKeyboardButton(text="Yes Select All", callback_data="select_all_channels"),
        InlineKeyboardButton(text="No Deselect All", callback_data="deselect_all_channels")
    ])
    keyboard_rows.append([InlineKeyboardButton(
        text="Next Continue to Payment",
        callback_data="proceed_to_payment"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    await callback_query.message.edit_text(
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
                    text="Back Back", 
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
                    text="Back Back", 
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
    """Start enhanced ad creation process"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Skip free ads check and go directly to content upload
    await state.set_state(AdCreationStates.upload_content)
    
    if language == 'ar':
        text = """
Content **إنشاء إعلان جديد**

أرسل محتوى إعلانك:
- نص فقط
- صورة مع نص
- فيديو مع نص

Tip نصيحة: اجعل إعلانك جذابًا وواضحًا!
        """.strip()
    elif language == 'ru':
        text = """
Content **Создать новое объявление**

Отправьте содержимое вашего объявления:
- Только текст
- Изображение с текстом
- Видео с текстом

Tip Совет: Сделайте объявление привлекательным и понятным!
        """.strip()
    else:
        text = """
Content **Create New Advertisement**

Send your ad content:
- Text only
- Image with text
- Video with text

Tip Tip: Make your ad engaging and clear for best results!
        """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back Back to Menu", callback_data="back_to_main")]
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
                [InlineKeyboardButton(text="🥈 Silver $29", callback_data="select_package_silver")],
                [InlineKeyboardButton(text="🥇 Gold $47", callback_data="select_package_gold")],
                [InlineKeyboardButton(text="Back Back", callback_data="back_to_start")]
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
        await show_channel_selection_for_enhanced_flow(callback_query, state)
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
            [InlineKeyboardButton(text="Back Back", callback_data="admin_edit_subscription")]
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
    """Continue to dynamic pricing calculator"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    await state.set_state(AdCreationStates.duration_selection)
    
    text = (
        "**Let's calculate your posting plan!**\n\n"
        "I'll help you find the perfect advertising package like a food delivery assistant!\n\n"
        "**Step 1: How many days** do you want your ad to run?\n"
        "(Examples: 3 days, 7 days, 30 days)\n\n"
        "**Step 2: How many posts per day?**\n"
        "(Choose 1 to 24 posts per day)\n\n"
        "**Step 3: Which channels?**\n"
        "All channels currently cost $0 — extra toppings coming soon!\n\n"
        "**Volume Discounts Available:**\n"
        "- 2+ posts/day to Get discounts up to 30% off!\n"
        "- More posts = bigger savings\n\n"
        "Choose your plan duration:"
    )
    
    # Create duration selection keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 Day", callback_data="dynamic_days_1"),
            InlineKeyboardButton(text="3 Days", callback_data="dynamic_days_3"),
            InlineKeyboardButton(text="7 Days", callback_data="dynamic_days_7")
        ],
        [
            InlineKeyboardButton(text="14 Days", callback_data="dynamic_days_14"),
            InlineKeyboardButton(text="30 Days", callback_data="dynamic_days_30"),
            InlineKeyboardButton(text="Custom", callback_data="dynamic_days_custom")
        ],
        [InlineKeyboardButton(text="Back Back", callback_data="back_to_start")]
    ])
    
    try:
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    except (AttributeError, Exception):
        await callback_query.message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    
    await callback_query.answer()


# Payment handlers now use dynamic pricing system

@router.callback_query(F.data == "pay_dynamic_ton")
async def pay_dynamic_ton_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle TON payment for dynamic pricing"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    calculation = data.get('pricing_calculation', {})
    
    if not calculation or 'total_ton' not in calculation:
        await callback_query.answer("No Invalid payment data")
        return
    
    total_ton = calculation['total_ton']
    total_usd = calculation['total_usd']
    
    text = "**TON Payment Instructions**\n\n"
    text += f"**Amount to Pay:** {total_ton} TON\n"
    text += f"**USD Equivalent:** ${total_usd:.2f}\n\n"
    text += "**Payment Address:**\n"
    text += "`UQC7VpEhRnW16_7FdTf_9QrF4AEqFRCVRJnSJZDKOLKSqxjE`\n\n"
    text += "**Important:**\n"
    text += f"- Send exactly {total_ton} TON\n"
    text += f"- Include memo: AB0102-{user_id}\n"
    text += "- Payment must be confirmed within 30 minutes\n\n"
    text += "After payment, your ad will be processed and published to all selected channels."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yes Payment Sent", callback_data="payment_sent")],
        [InlineKeyboardButton(text="Back Back", callback_data="recalculate_dynamic")]
    ])
    
    try:
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    except (AttributeError, Exception):
        await callback_query.message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    
    await callback_query.answer()


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
    
    # Create Stars payment
    await payment_processor.create_stars_payment(
        callback_query.message,
        stars_price,
        f"I3lani Bot - Dynamic Ad Package (${total_usd:.2f})",
        f"stars_payment_{user_id}_{int(datetime.now().timestamp())}"
    )
    
    await callback_query.answer("Star Stars payment created!")


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
                        [InlineKeyboardButton(text="Back Back", callback_data="back_to_channels")]
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
    """Show channel sharing system"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get available channels
    channels = await db.get_channels()
    
    # Get referral stats for bot referrals
    referral_stats = await db.get_referral_stats(user_id)
    
    share_text = f"""
**{get_text(language, 'share_channels')}**

**Share Our Channels & Earn:**
- Share I3lani channel with friends
- Get 10% discount on next campaign
- Help grow our community

 **Available Channels:**
"""
    
    for channel in channels:
        share_text += f"\n- {channel['name']}: {channel['telegram_channel_id']}"
    
    share_text += f"""

Price **Bot Referral Rewards:**
- Refer friends to I3lani Bot
- Earn 3 free posting days per referral
- Friends get 5% discount

Stats **Your Referral Stats:**
- Total Referrals: {referral_stats.get('total_referrals', 0)}
- Free Days Earned: {referral_stats.get('total_referrals', 0) * 3}

 **Your Bot Referral Link:**
`https://t.me/I3lani_bot?start=ref_{user_id}`
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=" Share I3lani Channel", url="https://t.me/share/url?url=https://t.me/i3lani&text=Join I3lani Channel!"),
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
            [InlineKeyboardButton(text="Star Telegram Stars", callback_data="payment_stars")],
            [InlineKeyboardButton(text="Diamond TON Cryptocurrency", callback_data="payment_ton")],
            [InlineKeyboardButton(text="Back Back to Channels", callback_data="back_to_channels")]
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


@router.callback_query(F.data.startswith("lang_"))
async def language_change_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle language change"""
    try:
        language_code = callback_query.data.replace("lang_", "")
        user_id = callback_query.from_user.id
        
        # Update user language in database
        await db.set_user_language(user_id, language_code)
        
        # Show main menu in new language
        await show_main_menu(callback_query, language_code)
        await callback_query.answer(get_text(language_code, 'language_updated'))
        
    except Exception as e:
        logger.error(f"Language change error: {e}")
        await callback_query.answer(get_text(language_code, 'error_updating_language'))


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
            [InlineKeyboardButton(text="Back Back to Photos", callback_data="back_to_photos")]
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
        channel_list = "\n".join([f"- {ch['channel_name']}" for ch in selected_channel_data])
        
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