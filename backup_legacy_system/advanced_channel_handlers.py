"""
Advanced Channel Management Handlers for I3lani Bot
Handles all advanced channel management operations
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from advanced_channel_management import get_advanced_channel_manager
from admin_system import safe_callback_answer, safe_edit_message
from config import ADMIN_IDS
from states import AdminStates

logger = logging.getLogger(__name__)

class AdvancedChannelStates(StatesGroup):
    """Advanced channel management states"""
    waiting_for_channel_identifier = State()
    waiting_for_channel_search = State()
    waiting_for_channel_action = State()

# Router for advanced channel management
advanced_channel_router = Router()

@advanced_channel_router.callback_query(F.data == "adv_channel_management")
async def show_advanced_channel_management(callback_query: CallbackQuery, state: FSMContext):
    """Show advanced channel management interface"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        # Get bot instance from callback
        bot = callback_query.bot
        manager = get_advanced_channel_manager(bot)
        
        # Initialize database if needed
        await manager.initialize_database()
        
        # Get management summary
        summary = await manager.get_management_summary()
        
        # Create keyboard
        keyboard = await manager.create_channel_management_keyboard()
        
        await safe_edit_message(
            callback_query.message,
            summary,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Advanced channel management loaded")
        
    except Exception as e:
        logger.error(f"Error showing advanced channel management: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading channel management", show_alert=True)

@advanced_channel_router.callback_query(F.data == "adv_auto_scan")
async def auto_scan_channels(callback_query: CallbackQuery, state: FSMContext):
    """Auto-scan for new channels"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        bot = callback_query.bot
        manager = get_advanced_channel_manager(bot)
        
        # Start auto-scan
        await safe_callback_answer(callback_query, "🔍 Starting auto-scan...")
        
        # Update message to show scanning status
        await safe_edit_message(
            callback_query.message,
            "🔄 <b>Auto-Scanning Channels...</b>\n\n"
            "• Checking existing channels for updates\n"
            "• Detecting new channels where bot is admin\n"
            "• Gathering subscriber counts\n"
            "• Analyzing channel permissions\n\n"
            "⏳ This may take a few moments...",
            parse_mode='HTML'
        )
        
        # Perform auto-scan
        discovered_channels = await manager.auto_detect_new_channels()
        
        # Generate results
        if discovered_channels:
            results_text = f"✅ <b>Auto-Scan Complete</b>\n\n"
            results_text += f"📊 <b>Results:</b>\n"
            results_text += f"• Channels processed: {len(discovered_channels)}\n"
            results_text += f"• New channels found: {len([c for c in discovered_channels if c.channel_id not in [ch['channel_id'] for ch in await manager.get_all_channels()]])}\n\n"
            
            results_text += f"🔍 <b>Discovered Channels:</b>\n"
            for channel in discovered_channels[:5]:  # Show first 5
                admin_status = "👑 Admin" if channel.bot_is_admin else "👤 Member"
                results_text += f"• {channel.title} (@{channel.username}) - {channel.subscriber_count} subscribers - {admin_status}\n"
            
            if len(discovered_channels) > 5:
                results_text += f"• ... and {len(discovered_channels) - 5} more channels\n"
        else:
            results_text = "✅ <b>Auto-Scan Complete</b>\n\n"
            results_text += "📊 <b>No new channels found</b>\n\n"
            results_text += "All existing channels have been updated with latest information."
        
        # Create keyboard
        keyboard = await manager.create_channel_management_keyboard()
        
        await safe_edit_message(
            callback_query.message,
            results_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in auto-scan: {e}")
        await safe_callback_answer(callback_query, "❌ Error during auto-scan", show_alert=True)

@advanced_channel_router.callback_query(F.data == "adv_add_channel")
async def add_channel_prompt(callback_query: CallbackQuery, state: FSMContext):
    """Prompt for channel addition"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    await state.set_state(AdvancedChannelStates.waiting_for_channel_identifier)
    
    await safe_edit_message(
        callback_query.message,
        "➕ <b>Add New Channel</b>\n\n"
        "📝 <b>Send the channel identifier:</b>\n"
        "• Channel username (e.g., @mychannel)\n"
        "• Channel ID (e.g., -1001234567890)\n"
        "• Channel name (e.g., mychannel)\n\n"
        "🔍 <b>The bot will:</b>\n"
        "• Detect subscriber count\n"
        "• Check bot admin status\n"
        "• Classify channel category\n"
        "• Add to pending approval list\n\n"
        "💡 <b>Note:</b> Bot must be added to the channel first!",
        parse_mode='HTML'
    )
    
    await safe_callback_answer(callback_query, "Send channel identifier")

@advanced_channel_router.message(AdvancedChannelStates.waiting_for_channel_identifier)
async def process_channel_addition(message: Message, state: FSMContext):
    """Process channel addition"""
    user_id = message.from_user.id
    
    if user_id not in ADMIN_IDS:
        await message.answer("❌ Access denied")
        return
    
    try:
        bot = message.bot
        manager = get_advanced_channel_manager(bot)
        
        channel_identifier = message.text.strip()
        
        # Show processing message
        processing_msg = await message.answer(
            "🔄 <b>Processing Channel Addition...</b>\n\n"
            f"• Identifier: {channel_identifier}\n"
            "• Fetching channel information...\n"
            "• Checking bot permissions...\n"
            "• Analyzing channel data...",
            parse_mode='HTML'
        )
        
        # Add channel
        channel_info = await manager.manual_add_channel(channel_identifier)
        
        if channel_info:
            result_text = f"✅ <b>Channel Added Successfully!</b>\n\n"
            result_text += f"📊 <b>Channel Information:</b>\n"
            result_text += f"• Title: {channel_info.title}\n"
            result_text += f"• Username: @{channel_info.username}\n"
            result_text += f"• Subscribers: {channel_info.subscriber_count:,}\n"
            result_text += f"• Category: {channel_info.category.title()}\n"
            result_text += f"• Bot Admin: {'✅ Yes' if channel_info.bot_is_admin else '❌ No'}\n"
            result_text += f"• Can Post: {'✅ Yes' if channel_info.can_post else '❌ No'}\n"
            result_text += f"• Status: 🟢 Approved\n\n"
            result_text += f"🎯 <b>Channel is ready for advertising campaigns!</b>"
        else:
            result_text = f"❌ <b>Failed to Add Channel</b>\n\n"
            result_text += f"🔍 <b>Possible reasons:</b>\n"
            result_text += f"• Channel doesn't exist\n"
            result_text += f"• Bot is not added to the channel\n"
            result_text += f"• Channel is private and bot lacks access\n"
            result_text += f"• Invalid channel identifier\n\n"
            result_text += f"💡 <b>Please check and try again</b>"
        
        await processing_msg.edit_text(result_text, parse_mode='HTML')
        
        # Show management interface again
        keyboard = await manager.create_channel_management_keyboard()
        summary = await manager.get_management_summary()
        
        await message.answer(
            summary,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error processing channel addition: {e}")
        await message.answer(
            "❌ <b>Error Adding Channel</b>\n\n"
            f"Technical error occurred. Please try again or contact support.\n\n"
            f"Error: {str(e)[:100]}",
            parse_mode='HTML'
        )
    
    await state.clear()

@advanced_channel_router.callback_query(F.data == "adv_list_channels")
async def list_all_channels(callback_query: CallbackQuery, state: FSMContext):
    """List all channels with management options"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        bot = callback_query.bot
        manager = get_advanced_channel_manager(bot)
        
        channels = await manager.get_all_channels()
        
        if not channels:
            await safe_edit_message(
                callback_query.message,
                "📋 <b>No Channels Found</b>\n\n"
                "🔍 <b>To get started:</b>\n"
                "• Use 'Auto-Scan' to detect existing channels\n"
                "• Use 'Add Channel' to add channels manually\n"
                "• Make sure bot is added as admin to channels",
                reply_markup=await manager.create_channel_management_keyboard(),
                parse_mode='HTML'
            )
            await safe_callback_answer(callback_query, "No channels found")
            return
        
        # Create channel list
        list_text = f"📋 <b>All Channels ({len(channels)})</b>\n\n"
        
        for i, channel in enumerate(channels[:10], 1):  # Show first 10
            status_emoji = {
                'approved': '✅',
                'pending': '⏳',
                'rejected': '❌'
            }.get(channel['status'], '⚪')
            
            admin_emoji = '👑' if channel['bot_is_admin'] else '👤'
            
            list_text += f"{i}. {status_emoji} {admin_emoji} <b>{channel['title']}</b>\n"
            list_text += f"   • @{channel['username']} | {channel['subscriber_count']:,} subscribers\n"
            list_text += f"   • Category: {channel['category'].title()} | Status: {channel['status'].title()}\n\n"
        
        if len(channels) > 10:
            list_text += f"... and {len(channels) - 10} more channels\n\n"
        
        list_text += f"🎯 <b>Click on any channel for details</b>"
        
        keyboard = await manager.create_channel_list_keyboard(channels)
        
        await safe_edit_message(
            callback_query.message,
            list_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Channels list loaded")
        
    except Exception as e:
        logger.error(f"Error listing channels: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading channels", show_alert=True)

@advanced_channel_router.callback_query(F.data.startswith("adv_channel_detail_"))
async def show_channel_details(callback_query: CallbackQuery, state: FSMContext):
    """Show detailed information for a specific channel"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        channel_id = int(callback_query.data.split("_")[-1])
        bot = callback_query.bot
        manager = get_advanced_channel_manager(bot)
        
        stats = await manager.get_channel_statistics(channel_id)
        
        if not stats:
            await safe_callback_answer(callback_query, "❌ Channel not found", show_alert=True)
            return
        
        channel_info = stats['channel_info']
        
        # Create detailed view
        detail_text = f"📊 <b>Channel Details</b>\n\n"
        detail_text += f"🏷️ <b>Basic Information:</b>\n"
        detail_text += f"• Title: {channel_info['title']}\n"
        detail_text += f"• Username: @{channel_info['username']}\n"
        detail_text += f"• ID: {channel_info['channel_id']}\n"
        detail_text += f"• Category: {channel_info['category'].title()}\n"
        detail_text += f"• Status: {channel_info['status'].title()}\n\n"
        
        detail_text += f"📈 <b>Statistics:</b>\n"
        detail_text += f"• Subscribers: {channel_info['subscriber_count']:,}\n"
        
        if stats['statistics']:
            recent_stats = stats['statistics'][0]
            detail_text += f"• Active Subscribers: {recent_stats['active_subscribers']}\n"
            detail_text += f"• Posts Count: {recent_stats['posts_count']}\n"
            detail_text += f"• Engagement Rate: {recent_stats['engagement_rate']:.1f}%\n"
        
        detail_text += f"\n🔧 <b>Management Actions:</b>\n"
        detail_text += f"• Approve/Reject channel\n"
        detail_text += f"• Update channel information\n"
        detail_text += f"• Delete channel\n"
        detail_text += f"• View detailed statistics"
        
        # Create action keyboard
        buttons = [
            [
                InlineKeyboardButton(text="✅ Approve", callback_data=f"adv_approve_{channel_id}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"adv_reject_{channel_id}")
            ],
            [
                InlineKeyboardButton(text="🔄 Update Info", callback_data=f"adv_update_{channel_id}"),
                InlineKeyboardButton(text="🗑️ Delete", callback_data=f"adv_delete_{channel_id}")
            ],
            [
                InlineKeyboardButton(text="📊 Full Stats", callback_data=f"adv_stats_{channel_id}")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to List", callback_data="adv_list_channels")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await safe_edit_message(
            callback_query.message,
            detail_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Channel details loaded")
        
    except Exception as e:
        logger.error(f"Error showing channel details: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading channel details", show_alert=True)

@advanced_channel_router.callback_query(F.data.startswith("adv_approve_"))
async def approve_channel(callback_query: CallbackQuery, state: FSMContext):
    """Approve a channel"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        channel_id = int(callback_query.data.split("_")[-1])
        bot = callback_query.bot
        manager = get_advanced_channel_manager(bot)
        
        success = await manager.update_channel_status(channel_id, "approved")
        
        if success:
            await safe_callback_answer(callback_query, "✅ Channel approved successfully")
            
            # Refresh channel details
            await show_channel_details(callback_query, state)
        else:
            await safe_callback_answer(callback_query, "❌ Failed to approve channel", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error approving channel: {e}")
        await safe_callback_answer(callback_query, "❌ Error approving channel", show_alert=True)

@advanced_channel_router.callback_query(F.data.startswith("adv_reject_"))
async def reject_channel(callback_query: CallbackQuery, state: FSMContext):
    """Reject a channel"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        channel_id = int(callback_query.data.split("_")[-1])
        bot = callback_query.bot
        manager = get_advanced_channel_manager(bot)
        
        success = await manager.update_channel_status(channel_id, "rejected")
        
        if success:
            await safe_callback_answer(callback_query, "❌ Channel rejected")
            
            # Refresh channel details
            await show_channel_details(callback_query, state)
        else:
            await safe_callback_answer(callback_query, "❌ Failed to reject channel", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error rejecting channel: {e}")
        await safe_callback_answer(callback_query, "❌ Error rejecting channel", show_alert=True)

@advanced_channel_router.callback_query(F.data.startswith("adv_delete_"))
async def delete_channel(callback_query: CallbackQuery, state: FSMContext):
    """Delete a channel"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        channel_id = int(callback_query.data.split("_")[-1])
        bot = callback_query.bot
        manager = get_advanced_channel_manager(bot)
        
        success = await manager.delete_channel(channel_id)
        
        if success:
            await safe_callback_answer(callback_query, "🗑️ Channel deleted successfully")
            
            # Go back to channel list
            await list_all_channels(callback_query, state)
        else:
            await safe_callback_answer(callback_query, "❌ Failed to delete channel", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error deleting channel: {e}")
        await safe_callback_answer(callback_query, "❌ Error deleting channel", show_alert=True)

@advanced_channel_router.callback_query(F.data == "adv_refresh")
async def refresh_channel_management(callback_query: CallbackQuery, state: FSMContext):
    """Refresh channel management interface"""
    await show_advanced_channel_management(callback_query, state)

def setup_advanced_channel_handlers(dp):
    """Setup advanced channel management handlers"""
    dp.include_router(advanced_channel_router)
    logger.info("✅ Advanced channel management handlers registered")