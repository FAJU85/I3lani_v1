import uuid
from datetime import datetime, timedelta
from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType
from config import PACKAGES, WELCOME_MESSAGE, PAYMENT_INSTRUCTIONS, ADMIN_IDS, CHANNEL_ID, TON_WALLET_ADDRESS
from models import Advertisement, AdContent, AdStatus, PaymentStatus, storage
from keyboards import get_package_keyboard, get_payment_keyboard, get_admin_approval_keyboard, get_package_details_keyboard
from scheduler import ScheduleManager
import logging

logger = logging.getLogger(__name__)

class AdStates(StatesGroup):
    waiting_for_ad = State()
    waiting_for_payment = State()
    waiting_for_admin_approval = State()

async def start_command(message: types.Message, state: FSMContext):
    """Handle /start command"""
    await state.finish()
    await message.reply(WELCOME_MESSAGE, parse_mode="Markdown")
    await AdStates.waiting_for_ad.set()

async def handle_ad_content(message: types.Message, state: FSMContext):
    """Handle ad content submission"""
    if not await AdStates.waiting_for_ad.check():
        return
    
    # Create ad content based on message type
    content = AdContent()
    
    if message.content_type == ContentType.TEXT:
        content.text = message.text
        content.content_type = "text"
    elif message.content_type == ContentType.PHOTO:
        content.photo_file_id = message.photo[-1].file_id
        content.caption = message.caption
        content.content_type = "photo"
    elif message.content_type == ContentType.VIDEO:
        content.video_file_id = message.video.file_id
        content.caption = message.caption
        content.content_type = "video"
    else:
        await message.reply("❌ Please send text, photo, or video content only.")
        return
    
    # Create advertisement
    ad_id = str(uuid.uuid4())
    ad = Advertisement(
        id=ad_id,
        user_id=message.from_user.id,
        username=message.from_user.username,
        content=content,
        package_id="",
        price=0.0,
        status=AdStatus.DRAFT,
        created_at=datetime.now(),
        payment_status=PaymentStatus.PENDING
    )
    
    # Save to storage
    storage.save_ad(ad)
    
    # Show package selection
    await message.reply(
        "✅ **Ad content received!**\n\n"
        "📦 **Choose your advertising package:**",
        reply_markup=get_package_keyboard(),
        parse_mode="Markdown"
    )

async def handle_package_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle package selection"""
    package_id = callback_query.data.replace("package_", "")
    
    if package_id not in PACKAGES:
        await callback_query.answer("❌ Invalid package")
        return
    
    package = PACKAGES[package_id]
    
    # Show package details
    details_text = f"""
📦 **{package['name']} Package**

💰 **Price:** {package['price']} TON
⏱ **Duration:** {package['duration_days']} days
📅 **Repost every:** {package['repost_frequency_days']} day(s)
📊 **Total posts:** {package['total_posts']}

Choose this package to proceed with payment.
"""
    
    await callback_query.message.edit_text(
        details_text,
        reply_markup=get_package_details_keyboard(package_id),
        parse_mode="Markdown"
    )
    await callback_query.answer()

async def handle_package_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle package confirmation"""
    package_id = callback_query.data.replace("confirm_package_", "")
    
    if package_id not in PACKAGES:
        await callback_query.answer("❌ Invalid package")
        return
    
    package = PACKAGES[package_id]
    user_id = callback_query.from_user.id
    
    # Get user's current ad
    ad = storage.get_user_current_ad(user_id)
    if not ad:
        await callback_query.answer("❌ No ad found. Please start over.")
        return
    
    # Update ad with package info
    ad.package_id = package_id
    ad.price = package['price']
    ad.total_posts = package['total_posts']
    ad.repost_frequency_days = package['repost_frequency_days']
    ad.status = AdStatus.WAITING_PAYMENT
    storage.save_ad(ad)
    
    # Show payment instructions
    payment_text = PAYMENT_INSTRUCTIONS.format(
        price=package['price'],
        wallet_address=TON_WALLET_ADDRESS
    )
    
    await callback_query.message.edit_text(
        payment_text,
        reply_markup=get_payment_keyboard(),
        parse_mode="Markdown"
    )
    await AdStates.waiting_for_payment.set()
    await callback_query.answer()

async def handle_back_to_packages(callback_query: types.CallbackQuery):
    """Handle back to packages button"""
    await callback_query.message.edit_text(
        "📦 **Choose your advertising package:**",
        reply_markup=get_package_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

async def handle_payment_sent(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle payment confirmation from user"""
    user_id = callback_query.from_user.id
    ad = storage.get_user_current_ad(user_id)
    
    if not ad:
        await callback_query.answer("❌ No ad found. Please start over.")
        return
    
    # Update ad status
    ad.status = AdStatus.PAYMENT_PENDING
    storage.save_ad(ad)
    
    # Notify user
    await callback_query.message.edit_text(
        "✅ **Payment notification received!**\n\n"
        "⏳ Your payment is being verified by our admin team.\n"
        "You will be notified once it's approved.\n\n"
        "📊 **Ad Details:**\n"
        f"📦 Package: {PACKAGES[ad.package_id]['name']}\n"
        f"💰 Price: {ad.price} TON\n"
        f"📅 Posts: {ad.total_posts}",
        parse_mode="Markdown"
    )
    
    # Notify admins
    await notify_admins_for_approval(callback_query.bot, ad)
    
    await AdStates.waiting_for_admin_approval.set()
    await callback_query.answer()

async def handle_payment_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle payment cancellation"""
    user_id = callback_query.from_user.id
    ad = storage.get_user_current_ad(user_id)
    
    if ad:
        storage.delete_ad(ad.id)
    
    await callback_query.message.edit_text(
        "❌ **Payment cancelled**\n\n"
        "Your ad has been cancelled. Send /start to create a new ad.",
        parse_mode="Markdown"
    )
    await state.finish()
    await callback_query.answer()

async def notify_admins_for_approval(bot: Bot, ad: Advertisement):
    """Notify admins about pending payment approval"""
    package = PACKAGES[ad.package_id]
    
    admin_text = f"""
🔔 **New Payment Pending Approval**

👤 **User:** @{ad.username or 'Unknown'} (ID: {ad.user_id})
📦 **Package:** {package['name']}
💰 **Price:** {ad.price} TON
🕒 **Submitted:** {ad.created_at.strftime('%Y-%m-%d %H:%M:%S')}

**Ad Content:**
{ad.content.text or ad.content.caption or 'Media content'}

💳 **Wallet:** `{TON_WALLET_ADDRESS}`

Please verify payment on tonviewer.com and approve/reject below.
"""
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                admin_text,
                reply_markup=get_admin_approval_keyboard(ad.id),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

async def handle_admin_approval(callback_query: types.CallbackQuery, bot: Bot, schedule_manager: ScheduleManager):
    """Handle admin approval/rejection"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("❌ Not authorized")
        return
    
    action, ad_id = callback_query.data.split("_", 1)
    ad = storage.get_ad(ad_id)
    
    if not ad:
        await callback_query.answer("❌ Ad not found")
        return
    
    if action == "approve":
        # Approve the ad
        ad.status = AdStatus.APPROVED
        ad.payment_status = PaymentStatus.CONFIRMED
        ad.approved_at = datetime.now()
        storage.save_ad(ad)
        
        # Schedule first post
        await schedule_manager.schedule_first_post(ad)
        
        # Notify user
        try:
            await bot.send_message(
                ad.user_id,
                "✅ **Payment Approved!**\n\n"
                "Your ad has been approved and will be posted shortly.\n"
                f"📊 **Total posts scheduled:** {ad.total_posts}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {ad.user_id}: {e}")
        
        # Update admin message
        await callback_query.message.edit_text(
            f"✅ **Ad Approved** by @{callback_query.from_user.username}\n\n"
            f"Ad ID: {ad.id}\n"
            f"User: @{ad.username or 'Unknown'}\n"
            f"Package: {PACKAGES[ad.package_id]['name']}\n"
            f"Approved at: {ad.approved_at.strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown"
        )
        
    elif action == "reject":
        # Reject the ad
        ad.status = AdStatus.REJECTED
        ad.payment_status = PaymentStatus.REJECTED
        storage.save_ad(ad)
        
        # Notify user
        try:
            await bot.send_message(
                ad.user_id,
                "❌ **Payment Rejected**\n\n"
                "Your payment could not be verified. Please contact support if you believe this is an error.",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {ad.user_id}: {e}")
        
        # Update admin message
        await callback_query.message.edit_text(
            f"❌ **Ad Rejected** by @{callback_query.from_user.username}\n\n"
            f"Ad ID: {ad.id}\n"
            f"User: @{ad.username or 'Unknown'}\n"
            f"Package: {PACKAGES[ad.package_id]['name']}\n"
            f"Rejected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown"
        )
    
    await callback_query.answer()

async def admin_stats_command(message: types.Message):
    """Show admin statistics"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Not authorized")
        return
    
    all_ads = list(storage.advertisements.values())
    
    stats_text = f"""
📊 **Bot Statistics**

📈 **Total Ads:** {len(all_ads)}
⏳ **Pending Payment:** {len([ad for ad in all_ads if ad.status == AdStatus.PAYMENT_PENDING])}
✅ **Active:** {len([ad for ad in all_ads if ad.status == AdStatus.ACTIVE])}
✅ **Completed:** {len([ad for ad in all_ads if ad.status == AdStatus.COMPLETED])}
❌ **Rejected:** {len([ad for ad in all_ads if ad.status == AdStatus.REJECTED])}

💰 **Revenue:** {sum(ad.price for ad in all_ads if ad.payment_status == PaymentStatus.CONFIRMED):.3f} TON
"""
    
    await message.reply(stats_text, parse_mode="Markdown")

def register_handlers(dp: Dispatcher, bot: Bot, schedule_manager: ScheduleManager):
    """Register all handlers"""
    
    # Command handlers
    dp.register_message_handler(start_command, commands=['start'], state="*")
    dp.register_message_handler(admin_stats_command, commands=['stats'])
    
    # Content handlers
    dp.register_message_handler(handle_ad_content, content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO], state=AdStates.waiting_for_ad)
    
    # Callback handlers
    dp.register_callback_query_handler(handle_package_selection, Text(startswith="package_"))
    dp.register_callback_query_handler(handle_package_confirmation, Text(startswith="confirm_package_"))
    dp.register_callback_query_handler(handle_back_to_packages, Text(equals="back_to_packages"))
    dp.register_callback_query_handler(handle_payment_sent, Text(equals="payment_sent"))
    dp.register_callback_query_handler(handle_payment_cancel, Text(equals="payment_cancel"))
    dp.register_callback_query_handler(
        lambda callback_query: handle_admin_approval(callback_query, bot, schedule_manager),
        Text(startswith=["approve_", "reject_"])
    )
