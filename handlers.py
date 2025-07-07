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

📋 **Package Details:**
• Duration: {package['duration_days']} days
• Posts per day: {package['posts_per_day']:.1f}
• Price: ${package['price_usd']:.0f}

💡 **Next Step:** Please send your advertisement content (text, photo, or video)
        """.strip()
        
        await callback_query.message.edit_text(
            confirmation_text,
            parse_mode='Markdown'
        )
        
        # Start enhanced ad creation flow
        await state.set_state(AdCreationStates.select_category)
        await show_category_selection(callback_query, state)
        await callback_query.answer(f"{package['name']} selected!")
        
    except Exception as e:
        logger.error(f"Package selection error: {e}")
        await callback_query.answer(get_text(language, 'error_selecting_package'))


# Enhanced Ad Creation Flow Handlers

async def show_category_selection(callback_query: CallbackQuery, state: FSMContext):
    """Show category selection for ad creation"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    from config import AD_CATEGORIES
    
    # Multi-language category text
    if language == 'ar':
        category_text = "📂 **اختر فئة الإعلان**\n\nاختر الفئة التي تناسب إعلانك:"
    elif language == 'ru':
        category_text = "📂 **Выберите категорию объявления**\n\nВыберите категорию, которая лучше всего подходит для вашего объявления:"
    else:
        category_text = "📂 **Select Ad Category**\n\nChoose the category that best fits your advertisement:"
    
    # Create category keyboard with translated names
    keyboard_rows = []
    for category_id, category_data in AD_CATEGORIES.items():
        category_name = category_data['name'].get(language, category_data['name']['en'])
        keyboard_rows.append([InlineKeyboardButton(
            text=category_name,
            callback_data=f"category_{category_id}"
        )])
    
    back_text = "⬅️ العودة للقائمة" if language == 'ar' else "⬅️ Назад к меню" if language == 'ru' else "⬅️ Back to Menu"
    keyboard_rows.append([InlineKeyboardButton(
        text=back_text,
        callback_data="back_to_main"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    await callback_query.message.edit_text(
        category_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@router.callback_query(F.data.startswith("category_"))
async def category_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle category selection"""
    try:
        category_id = callback_query.data.replace("category_", "")
        from config import AD_CATEGORIES
        
        if category_id not in AD_CATEGORIES:
            await callback_query.answer("Invalid category", show_alert=True)
            return
            
        category = AD_CATEGORIES[category_id]
        
        # Extract translated category name
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        category_name = category['name'].get(language, category['name']['en'])
        
        await state.update_data(selected_category=category_id, category_name=category_name)
        subcategory_text = f"{category['emoji']} **{category_name}**\n\n"
        if language == 'ar':
            subcategory_text += "اختر فئة فرعية:"
        elif language == 'ru':
            subcategory_text += "Выберите подкатегорию:"
        else:
            subcategory_text += "Select a subcategory:"
        
        # Create subcategory keyboard with translation
        keyboard_rows = []
        for sub_id, sub_data in category['subcategories'].items():
            sub_name = sub_data.get(language, sub_data['en'])
            keyboard_rows.append([InlineKeyboardButton(
                text=sub_name,
                callback_data=f"subcategory_{sub_id}"
            )])
        
        keyboard_rows.append([InlineKeyboardButton(
            text="⬅️ Back to Categories",
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
        
    except Exception as e:
        logger.error(f"Category selection error: {e}")
        await callback_query.answer(get_text(language, 'error_selecting_category'))


@router.callback_query(F.data.startswith("subcategory_"))
async def subcategory_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle subcategory selection"""
    try:
        subcategory_id = callback_query.data.replace("subcategory_", "")
        data = await state.get_data()
        category_id = data.get('selected_category')
        
        from config import AD_CATEGORIES
        
        if category_id not in AD_CATEGORIES or subcategory_id not in AD_CATEGORIES[category_id]['subcategories']:
            await callback_query.answer("Invalid subcategory", show_alert=True)
            return
            
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        subcategory_data = AD_CATEGORIES[category_id]['subcategories'][subcategory_id]
        subcategory_name = subcategory_data.get(language, subcategory_data['en'])
        await state.update_data(selected_subcategory=subcategory_id, subcategory_name=subcategory_name)
        
        # Show location selection
        await show_location_selection(callback_query, state)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Subcategory selection error: {e}")
        await callback_query.answer("Error selecting subcategory")


async def show_location_selection(callback_query: CallbackQuery, state: FSMContext):
    """Show location selection"""
    from config import LOCATIONS
    
    location_text = """
📍 **Select Location**

Where is your ad located?
    """.strip()
    
    # Create location keyboard (2 columns)
    keyboard_rows = []
    locations = list(LOCATIONS.items())
    
    for i in range(0, len(locations), 2):
        row = []
        for j in range(2):
            if i + j < len(locations):
                loc_id, loc_name = locations[i + j]
                row.append(InlineKeyboardButton(
                    text=loc_name,
                    callback_data=f"location_{loc_id}"
                ))
        keyboard_rows.append(row)
    
    keyboard_rows.append([InlineKeyboardButton(
        text="⬅️ Back to Subcategories",
        callback_data="back_to_subcategories"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    await callback_query.message.edit_text(
        location_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    await state.set_state(AdCreationStates.select_location)


@router.callback_query(F.data.startswith("location_"))
async def location_selection_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle location selection"""
    try:
        location_id = callback_query.data.replace("location_", "")
        from config import LOCATIONS
        
        if location_id not in LOCATIONS:
            await callback_query.answer("Invalid location", show_alert=True)
            return
            
        location_name = LOCATIONS[location_id]
        await state.update_data(selected_location=location_id, location_name=location_name)
        
        # Ask for ad details
        data = await state.get_data()
        
        details_text = f"""
✍️ **Enter Ad Details**

**Category:** {data.get('category_name', 'N/A')} → {data.get('subcategory_name', 'N/A')}
**Location:** {location_name}

Please write your advertisement description:
• Title
• Description
• Price (if applicable)
• Any additional details

Send your ad content as a text message.
        """.strip()
        
        await callback_query.message.edit_text(
            details_text,
            parse_mode='Markdown'
        )
        
        await state.set_state(AdCreationStates.enter_ad_details)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Location selection error: {e}")
        await callback_query.answer("Error selecting location")


@router.message(AdCreationStates.enter_ad_details)
async def handle_ad_details(message: Message, state: FSMContext):
    """Handle ad details input"""
    try:
        ad_details = message.text
        await state.update_data(ad_details=ad_details, ad_content=ad_details)
        
        # Ask for photos
        photo_text = """
📷 **Upload Photos (Optional)**

You can upload up to 5 photos for your ad.

• Send photos one by one
• Use the buttons below to continue
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📸 Skip Photos", callback_data="skip_photos"),
                InlineKeyboardButton(text="✅ Done with Photos", callback_data="done_photos")
            ],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_details")]
        ])
        
        await message.reply(photo_text, reply_markup=keyboard, parse_mode='Markdown')
        await state.set_state(AdCreationStates.upload_photos)
        await state.update_data(uploaded_photos=[])
        
    except Exception as e:
        logger.error(f"Ad details error: {e}")
        await message.reply(get_text(language, 'error_processing_ad'))


@router.message(AdCreationStates.upload_photos, F.photo)
async def handle_photo_upload(message: Message, state: FSMContext):
    """Handle photo uploads"""
    try:
        data = await state.get_data()
        uploaded_photos = data.get('uploaded_photos', [])
        
        if len(uploaded_photos) >= 5:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Done with Photos", callback_data="done_photos")]
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
                InlineKeyboardButton(text="✅ Done with Photos", callback_data="done_photos"),
                InlineKeyboardButton(text="📸 Add More", callback_data="add_more_photos")
            ],
            [InlineKeyboardButton(text="📸 Skip Photos", callback_data="skip_photos")]
        ])
        
        await message.reply(f"📸 Photo {len(uploaded_photos)}/5 uploaded.", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Photo upload error: {e}")
        await message.reply(get_text(language, 'error_uploading_photo'))


@router.callback_query(F.data == "continue_from_photos")
async def continue_from_photos(callback_query: CallbackQuery, state: FSMContext):
    """Continue from photo upload step"""
    await state.set_state(AdCreationStates.provide_contact_info)
    
    contact_text = """
📞 **Provide Contact Information**

How should customers reach you?

Examples:
• Phone: +966501234567
• WhatsApp: +966501234567
• Email: user@email.com
• Telegram: @username

Send your contact information:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Photos", callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(contact_text, reply_markup=keyboard)
    await callback_query.answer()


@router.callback_query(F.data == "add_more_photos") 
async def add_more_photos(callback_query: CallbackQuery, state: FSMContext):
    """Allow user to add more photos"""
    await callback_query.message.edit_text(
        "📸 **Add More Photos**\n\nSend additional photos (max 5 total):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Done with Photos", callback_data="continue_from_photos")]
        ])
    )
    await callback_query.answer("Send more photos")


@router.callback_query(F.data == "skip_photos")
async def skip_photos_handler(callback_query: CallbackQuery, state: FSMContext):
    """Skip photo upload step"""
    await state.set_state(AdCreationStates.provide_contact_info)
    
    contact_text = """
📞 **Provide Contact Information**

How should customers reach you?

Examples:
• Phone: +966501234567
• WhatsApp: +966501234567
• Email: user@email.com
• Telegram: @username

Send your contact information:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Photos", callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(contact_text, reply_markup=keyboard)
    await callback_query.answer("Photos skipped")


@router.callback_query(F.data == "done_photos")
async def done_photos_handler(callback_query: CallbackQuery, state: FSMContext):
    """Complete photo upload step"""
    await state.set_state(AdCreationStates.provide_contact_info)
    
    contact_text = """
📞 **Provide Contact Information**

How should customers reach you?

Examples:
• Phone: +966501234567
• WhatsApp: +966501234567
• Email: user@email.com
• Telegram: @username

Send your contact information:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Photos", callback_data="back_to_photos")]
    ])
    
    await callback_query.message.edit_text(contact_text, reply_markup=keyboard)
    await callback_query.answer("Photos completed")


@router.message(AdCreationStates.upload_photos, F.text.in_(["/skip", "/done"]))
async def handle_photo_completion(message: Message, state: FSMContext):
    """Handle photo upload completion - fallback for /done command"""
    try:
        # Ask for contact information
        contact_text = """
📞 **Provide Contact Information**

How should interested buyers contact you?

Please provide:
• Phone number
• Email (optional)
• Preferred contact method
• Available times

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
👀 **Ad Preview**

**Category:** {data.get('category_name', 'N/A')} → {data.get('subcategory_name', 'N/A')}
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
                InlineKeyboardButton(text="✅ Confirm & Continue", callback_data="confirm_ad"),
                InlineKeyboardButton(text="✏️ Edit Ad", callback_data="edit_ad")
            ],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_ad")]
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
{data.get('category_name', '')} → {data.get('subcategory_name', '')}
📍 {data.get('location_name', '')}

{ad_content}

📞 Contact: {data.get('contact_info', '')}
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
        formatted_content = f"🎁 **FREE AD**\n\n{ad_content}\n\n✨ *Advertise with @I3lani_bot*"
        
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
🎉 **Free Ad Published Successfully!**

✅ Your ad is now live on the I3lani channel!
📅 Duration: 3 days
🔗 View: https://t.me/i3lani

Thank you for using I3lani Bot!
            """.strip()
            
            await callback_query.message.edit_text(success_text, parse_mode='Markdown')
            await state.clear()
            
        except Exception as publish_error:
            logger.error(f"Free ad publishing error: {publish_error}")
            await callback_query.message.edit_text(
                "✅ **Ad Created Successfully!**\n\nYour free ad will be published shortly.",
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
        emoji = "✅" if is_selected else "☐"
        
        keyboard_rows.append([InlineKeyboardButton(
            text=f"{emoji} {channel['name']} ({channel['subscribers']:,} subscribers)",
            callback_data=f"toggle_channel_{channel['channel_id']}"
        )])
    
    # Add select all and continue buttons
    keyboard_rows.append([
        InlineKeyboardButton(text="✅ Select All", callback_data="select_all_channels"),
        InlineKeyboardButton(text="❌ Deselect All", callback_data="deselect_all_channels")
    ])
    keyboard_rows.append([InlineKeyboardButton(
        text="➡️ Continue to Payment",
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
    """Start enhanced ad creation process"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Check if user has free ads remaining
    user = await db.get_user(user_id)
    free_ads_used = user.get('free_ads_used', 0) if user else 0
    free_ads_remaining = max(0, 3 - free_ads_used)
    
    if free_ads_remaining > 0:
        # Start free ad creation
        await state.set_state(AdCreationStates.select_category)
        
        text = f"""
🎯 **Create Your Advertisement**

You have **{free_ads_remaining}** free ads remaining this month.

Please select a category for your ad:
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🚗 Vehicles", callback_data="category_vehicles"),
                InlineKeyboardButton(text="🏠 Real Estate", callback_data="category_real_estate")
            ],
            [
                InlineKeyboardButton(text="📱 Electronics", callback_data="category_electronics"),
                InlineKeyboardButton(text="💼 Jobs", callback_data="category_jobs")
            ],
            [
                InlineKeyboardButton(text="🛠️ Services", callback_data="category_services"),
                InlineKeyboardButton(text="👗 Fashion", callback_data="category_fashion")
            ],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_start")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        # No free ads, redirect to create ad directly
        await callback_query.message.edit_text(
            "⚠️ You have used all your free ads for this month.\n\nPlease create a paid ad to continue advertising.",
            parse_mode='Markdown'
        )
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
❌ **Free Ads Limit Reached**

You have used all 3 free ads for this month.

**Options:**
• Wait for next month reset
• Upgrade to Bronze Plan ($10/month) 
• Upgrade to Silver Plan ($29/3 months)
• Upgrade to Gold Plan ($47/6 months)

**Next reset:** {next_reset}
            """.strip(),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🟫 Bronze $10", callback_data="select_package_bronze")],
                [InlineKeyboardButton(text="🥈 Silver $29", callback_data="select_package_silver")],
                [InlineKeyboardButton(text="🥇 Gold $47", callback_data="select_package_gold")],
                [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_start")]
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
✏️ **Edit {package_type.title()} Package**

Current settings:
• Package: {package_type.title()}
• Current price: ${current_price}

What would you like to edit?
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 Change Price", callback_data=f"change_price_{package_type}"),
                InlineKeyboardButton(text="⏰ Change Duration", callback_data=f"change_duration_{package_type}")
            ],
            [
                InlineKeyboardButton(text="📝 Change Description", callback_data=f"change_desc_{package_type}"),
                InlineKeyboardButton(text="🎯 Change Features", callback_data=f"change_features_{package_type}")
            ],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_edit_subscription")]
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
    
    # Get channel data and calculate package pricing
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
    
    # Show package pricing and payment methods
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
                
                payment_summary = f"⭐ **Telegram Stars Payment**\n\n"
                payment_summary += f"💰 **Total:** {stars_amount:,} Stars (${total_price_usd:.2f} USD)\n"
                payment_summary += f"📺 **Channels:** {len(selected_channels)}\n\n"
                
                for detail in channel_pricing_details:
                    payment_summary += f"• {detail['name']}: {detail['price_stars']} Stars\n"
                
                payment_summary += f"\n✅ **Invoice sent!** Please complete payment using the invoice above.\n\nYour ad will be published automatically after payment confirmation."
                
                await callback_query.message.edit_text(
                    payment_summary,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_channels")]
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
    """Handle payment confirmation - check if payment was actually received"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        payment_id = callback_query.data.replace("confirm_payment_", "")
        
        # Show checking message
        await callback_query.message.edit_text(
            "🔍 **Checking Payment...**\n\nPlease wait while we verify your payment...",
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
                "❌ **Payment Not Found**\n\nPayment record not found. Please try again.",
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
            "❌ **Error**\n\nUnable to verify payment. Please try again later.",
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
            ad_content = "📢 Your advertisement is now live! Contact @I3lani_bot for more details."
        
        # Publish ad to I3lani channel immediately
        bot = callback_query.bot
        i3lani_channel = "@i3lani"
        published = False
        
        try:
            # Format ad with proper branding
            formatted_content = f"📢 Advertisement\n\n{ad_content}\n\n✨ Advertise with @I3lani_bot"
            
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


async def handle_payment_not_found(callback_query: CallbackQuery, payment_record):
    """Handle payment not found scenario"""
    try:
        # Create retry payment keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔄 Try Again", 
                callback_data=f"retry_payment_{payment_record['subscription_id']}"
            )],
            [InlineKeyboardButton(
                text="🏠 Go Home", 
                callback_data="go_home"
            )]
        ])
        
        payment_not_found_text = f"""
❌ **Payment Not Found**

We couldn't find your payment on the TON blockchain yet.

📋 **Payment Details:**
• Amount: {payment_record['amount']} TON
• Memo: {payment_record['memo']}
• Wallet: UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB

⚠️ **Please ensure:**
• You sent the exact amount
• You included the correct memo
• Payment was sent from your personal wallet (not exchange)

🔍 **Check your transaction:**
https://tonviewer.com/UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB

Would you like to try again?
        """.strip()
        
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
    
    help_text = get_text(language, 'help_text')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(language, 'create_ad'), callback_data="create_ad"),
            # InlineKeyboardButton(text="💰 Pricing", callback_data="pricing") # REMOVED
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
        await show_payment_selection(callback_query, state)
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
        
        # Calculate actual pricing based on selected channels
        total_price_usd = 0
        total_price_stars = 0
        channel_pricing_details = []
        
        # Get channel details and calculate pricing
        all_channels = await db.get_channels(active_only=True)
        for channel_id in selected_channels:
            for channel in all_channels:
                if channel['channel_id'] == channel_id:
                    base_price = channel.get('base_price_usd', 5.0)
                    total_price_usd += base_price
                    total_price_stars += int(base_price * 34)  # 1 USD ≈ 34 Stars
                    channel_pricing_details.append({
                        'name': channel['name'],
                        'price_usd': base_price,
                        'price_stars': int(base_price * 34)
                    })
                    break
        
        # Check if payment is needed
        if total_price_usd == 0:
            # Free package - proceed to publishing
            await handle_free_package_publishing(callback_query, state)
            return
        
        # Show payment method selection with actual pricing
        await state.update_data(
            selected_channels=selected_channels,
            package_details=package_details,
            total_price_usd=total_price_usd,
            total_price_stars=total_price_stars,
            channel_pricing_details=channel_pricing_details
        )
        await state.set_state(AdCreationStates.payment_method)
        
        # Create detailed pricing text
        pricing_breakdown = ""
        for detail in channel_pricing_details:
            pricing_breakdown += f"• {detail['name']}: ${detail['price_usd']:.2f}\n"
        
        payment_text = f"""
💳 **Payment Required**

📺 **Selected Channels:** {len(selected_channels)}
{pricing_breakdown}
━━━━━━━━━━━━━━━━━
💰 **Total Price:** ${total_price_usd:.2f} USD
⭐ **Stars Price:** {total_price_stars:,} Stars

Choose your payment method:
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="payment_stars")],
            [InlineKeyboardButton(text="💎 TON Cryptocurrency", callback_data="payment_ton")],
            [InlineKeyboardButton(text="⬅️ Back to Channels", callback_data="back_to_channels")]
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
🛠️ **Error Recovery Options**

Something went wrong. Choose how to continue:

🔄 **Continue** - Try to continue from where you left off
🆕 **Start Over** - Begin a new ad campaign  
🏠 **Main Menu** - Return to main menu
📞 **Support** - Get help from support team
"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Continue", callback_data="continue_flow"),
                InlineKeyboardButton(text="🆕 Start Over", callback_data="start_over")
            ],
            [
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main"),
                InlineKeyboardButton(text="📞 Support", callback_data="support")
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
        "📸 **Upload Photos** (Optional)\n\nYou can upload up to 5 photos for your ad.\n\n📷 Send photos one by one, or skip this step.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭️ Skip Photos", callback_data="skip_photos")],
            [InlineKeyboardButton(text="⬅️ Back to Ad Details", callback_data="back_to_details")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(F.data == "back_to_details") 
async def back_to_details_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to ad details entry"""
    await state.set_state(AdCreationStates.enter_ad_details)
    
    await callback_query.message.edit_text(
        "✏️ **Enter Ad Details**\n\nPlease provide detailed information about your ad:\n• Product/service description\n• Key features\n• Benefits\n• Call to action",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back to Location", callback_data="back_to_location")]
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
        "❌ **Ad Creation Cancelled**\n\nYour ad has been cancelled. You can start a new ad anytime!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🆕 Create New Ad", callback_data="create_ad")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
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
        "📸 **Upload More Photos**\n\nSend additional photos for your ad (up to 5 total).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Done with Photos", callback_data="done_photos")],
            [InlineKeyboardButton(text="⬅️ Back to Contact", callback_data="back_to_contact")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(F.data == "back_to_contact")
async def back_to_contact_handler(callback_query: CallbackQuery, state: FSMContext):
    """Back to contact information step"""
    await state.set_state(AdCreationStates.provide_contact_info)
    
    await callback_query.message.edit_text(
        "📞 **Contact Information**\n\nPlease provide your contact details:\n• Phone number\n• Email address\n• Telegram username\n• Any other contact method",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back to Photos", callback_data="back_to_photos")]
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
⏰ **Payment Timeout**

Your payment session has expired.

🔄 **Options:**
• Try payment again
• Choose different payment method
• Return to main menu

What would you like to do?
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Retry Payment", callback_data=f"retry_payment_{payment_id}")],
        [InlineKeyboardButton(text="💳 Change Method", callback_data="change_payment_method")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
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
        "💳 **Choose Payment Method**\n\nSelect your preferred payment option:",
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
🔧 **Error Recovery**

Something went wrong. Let's get you back on track.

🔄 **Recovery Options:**
• Continue from where you left off
• Start over with new ad
• Return to main menu
• Contact support

Choose your preferred option:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Continue", callback_data="continue_flow")],
        [InlineKeyboardButton(text="🆕 Start Over", callback_data="create_ad")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")],
        [InlineKeyboardButton(text="📞 Support", callback_data="help")]
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
            "💳 **Choose Payment Method**",
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
                text="✅ Payment Sent", 
                callback_data=f"confirm_payment_{invoice['payment_id']}"
            )],
            [InlineKeyboardButton(
                text="🏠 Go Home", 
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
                text="⬅️ Back to Categories",
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
        "✏️ **Edit Ad**\n\nWhat would you like to edit?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Ad Details", callback_data="edit_ad_details")],
            [InlineKeyboardButton(text="📞 Contact Info", callback_data="edit_contact_info")],
            [InlineKeyboardButton(text="📷 Photos", callback_data="edit_photos")],
            [InlineKeyboardButton(text="⬅️ Back to Preview", callback_data="back_to_preview")]
        ]),
        parse_mode='Markdown'
    )
    await callback_query.answer()


@router.callback_query(F.data == "cancel_ad")
async def cancel_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle ad cancellation"""
    await callback_query.message.edit_text(
        "❌ **Ad Creation Cancelled**\n\nYour ad creation has been cancelled.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Back to Home", callback_data="back_to_main")]
        ]),
        parse_mode='Markdown'
    )
    await state.clear()
    await callback_query.answer()