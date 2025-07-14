"""
AdSense-Like Handlers for I3lani Bot
Handles auction-based ad placements, bidding, and performance tracking
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from typing import Dict, List

from adsense_system_architecture import adsense_system, AdBid, AdPlacement
from database import db
from languages import get_text

logger = logging.getLogger(__name__)
router = Router()

class AdSenseStates(StatesGroup):
    """States for AdSense workflow"""
    browsing_channels = State()
    selecting_channel = State()
    setting_bid_amount = State()
    setting_bid_type = State()
    setting_duration = State()
    setting_content = State()
    setting_media = State()
    setting_budget = State()
    confirming_bid = State()
    viewing_performance = State()

@router.message(Command("browse_channels"))
async def browse_channels_command(message: Message, state: FSMContext):
    """Browse available channels for ad placement"""
    try:
        user_id = message.from_user.id
        user_language = await db.get_user_language(user_id)
        
        # Get available channels
        channels = await adsense_system.get_available_channels()
        
        if not channels:
            await message.answer(get_text(user_language, "no_channels_available"))
            return
        
        text = get_text(user_language, "available_channels_header")
        keyboard = []
        
        for channel in channels[:10]:  # Show first 10 channels
            # Format channel info
            channel_info = f"📺 {channel.channel_name}\n"
            channel_info += f"👥 {channel.subscribers:,} subscribers\n"
            channel_info += f"📊 {channel.category.title()}\n"
            channel_info += f"💰 CPC: ${channel.suggested_cpc:.3f} | CPM: ${channel.suggested_cpm:.2f}\n"
            channel_info += f"🎯 Available slots: {channel.available_slots}\n"
            
            text += f"\n{channel_info}"
            
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🎯 Bid on {channel.channel_name}",
                    callback_data=f"bid_channel_{channel.channel_id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(
                text=get_text(user_language, "filter_by_category"),
                callback_data="filter_categories"
            )
        ])
        
        keyboard.append([
            InlineKeyboardButton(
                text=get_text(user_language, "back_to_main"),
                callback_data="back_to_main"
            )
        ])
        
        await message.answer(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
        await state.set_state(AdSenseStates.browsing_channels)
        
    except Exception as e:
        logger.error(f"Error browsing channels: {e}")
        await message.answer(get_text(user_language, "error_occurred"))

@router.callback_query(F.data.startswith("bid_channel_"))
async def handle_bid_channel(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel selection for bidding"""
    try:
        user_id = callback_query.from_user.id
        user_language = await db.get_user_language(user_id)
        
        channel_id = callback_query.data.replace("bid_channel_", "")
        
        # Get channel details
        channels = await adsense_system.get_available_channels()
        selected_channel = next((ch for ch in channels if ch.channel_id == channel_id), None)
        
        if not selected_channel:
            await callback_query.answer(get_text(user_language, "channel_not_found"))
            return
        
        # Store channel selection
        await state.update_data(selected_channel=selected_channel)
        
        text = f"""🎯 **Bidding for {selected_channel.channel_name}**

📊 **Channel Statistics:**
• Subscribers: {selected_channel.subscribers:,}
• Category: {selected_channel.category.title()}
• Average Engagement: {selected_channel.avg_engagement:.1f}%
• Available Slots: {selected_channel.available_slots}

💰 **Suggested Pricing:**
• Cost Per Click (CPC): ${selected_channel.suggested_cpc:.3f}
• Cost Per Mille (CPM): ${selected_channel.suggested_cpm:.2f}

Choose your bidding strategy:"""
        
        keyboard = [
            [
                InlineKeyboardButton(
                    text="💎 CPC Bidding (Pay per click)",
                    callback_data="bid_type_cpc"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👀 CPM Bidding (Pay per 1000 views)",
                    callback_data="bid_type_cpm"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back to Channels",
                    callback_data="back_to_channels"
                )
            ]
        ]
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await state.set_state(AdSenseStates.selecting_channel)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error handling bid channel: {e}")
        await callback_query.answer(get_text(user_language, "error_occurred"))

@router.callback_query(F.data.startswith("bid_type_"))
async def handle_bid_type(callback_query: CallbackQuery, state: FSMContext):
    """Handle bid type selection (CPC or CPM)"""
    try:
        user_id = callback_query.from_user.id
        user_language = await db.get_user_language(user_id)
        
        bid_type = callback_query.data.replace("bid_type_", "")
        data = await state.get_data()
        selected_channel = data.get('selected_channel')
        
        if not selected_channel:
            await callback_query.answer(get_text(user_language, "session_expired"))
            return
        
        await state.update_data(bid_type=bid_type)
        
        if bid_type == "cpc":
            text = f"""💎 **CPC Bidding for {selected_channel.channel_name}**

You'll pay for each click on your ad.

💰 **Suggested CPC**: ${selected_channel.suggested_cpc:.3f}
📊 **Minimum bid**: ${selected_channel.suggested_cpc * Decimal('0.8'):.3f}

Enter your bid amount per click (USD):"""
        else:  # CPM
            text = f"""👀 **CPM Bidding for {selected_channel.channel_name}**

You'll pay for every 1000 impressions (views).

💰 **Suggested CPM**: ${selected_channel.suggested_cpm:.2f}
📊 **Minimum bid**: ${selected_channel.suggested_cpm * Decimal('0.8'):.2f}

Enter your bid amount per 1000 views (USD):"""
        
        keyboard = [
            [
                InlineKeyboardButton(
                    text="💡 Use suggested amount",
                    callback_data=f"use_suggested_{bid_type}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back to bid type",
                    callback_data=f"bid_channel_{selected_channel.channel_id}"
                )
            ]
        ]
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await state.set_state(AdSenseStates.setting_bid_amount)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error handling bid type: {e}")
        await callback_query.answer(get_text(user_language, "error_occurred"))

@router.callback_query(F.data.startswith("use_suggested_"))
async def handle_use_suggested(callback_query: CallbackQuery, state: FSMContext):
    """Handle using suggested bid amount"""
    try:
        user_id = callback_query.from_user.id
        user_language = await db.get_user_language(user_id)
        
        bid_type = callback_query.data.replace("use_suggested_", "")
        data = await state.get_data()
        selected_channel = data.get('selected_channel')
        
        if not selected_channel:
            await callback_query.answer(get_text(user_language, "session_expired"))
            return
        
        # Use suggested amount
        if bid_type == "cpc":
            bid_amount = selected_channel.suggested_cpc
        else:  # CPM
            bid_amount = selected_channel.suggested_cpm
        
        await state.update_data(bid_amount=bid_amount)
        
        # Move to duration selection
        await show_duration_selection(callback_query, state, selected_channel, bid_type, bid_amount)
        
    except Exception as e:
        logger.error(f"Error using suggested amount: {e}")
        await callback_query.answer(get_text(user_language, "error_occurred"))

@router.message(AdSenseStates.setting_bid_amount)
async def handle_bid_amount_input(message: Message, state: FSMContext):
    """Handle manual bid amount input"""
    try:
        user_id = message.from_user.id
        user_language = await db.get_user_language(user_id)
        
        try:
            bid_amount = Decimal(message.text)
            if bid_amount <= 0:
                raise ValueError("Bid amount must be positive")
        except (ValueError, TypeError):
            await message.answer(get_text(user_language, "invalid_amount"))
            return
        
        data = await state.get_data()
        selected_channel = data.get('selected_channel')
        bid_type = data.get('bid_type')
        
        if not selected_channel or not bid_type:
            await message.answer(get_text(user_language, "session_expired"))
            return
        
        # Validate minimum bid
        if bid_type == "cpc":
            min_bid = selected_channel.suggested_cpc * Decimal('0.8')
        else:
            min_bid = selected_channel.suggested_cpm * Decimal('0.8')
        
        if bid_amount < min_bid:
            await message.answer(
                f"⚠️ Minimum bid is ${min_bid:.3f}. Please enter a higher amount."
            )
            return
        
        await state.update_data(bid_amount=bid_amount)
        
        # Move to duration selection
        await show_duration_selection_message(message, state, selected_channel, bid_type, bid_amount)
        
    except Exception as e:
        logger.error(f"Error handling bid amount: {e}")
        await message.answer(get_text(user_language, "error_occurred"))

async def show_duration_selection(callback_query: CallbackQuery, state: FSMContext, 
                                 selected_channel, bid_type: str, bid_amount: Decimal):
    """Show duration selection interface"""
    try:
        text = f"""⏰ **Campaign Duration for {selected_channel.channel_name}**

💰 **Your bid**: ${bid_amount:.3f} per {bid_type.upper()}

Select how long you want your ad to run:"""
        
        keyboard = [
            [
                InlineKeyboardButton(text="⚡ 1 hour", callback_data="duration_1"),
                InlineKeyboardButton(text="🔥 6 hours", callback_data="duration_6")
            ],
            [
                InlineKeyboardButton(text="🌟 12 hours", callback_data="duration_12"),
                InlineKeyboardButton(text="🚀 24 hours", callback_data="duration_24")
            ],
            [
                InlineKeyboardButton(text="💎 48 hours", callback_data="duration_48"),
                InlineKeyboardButton(text="👑 72 hours", callback_data="duration_72")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to bid amount", callback_data="back_to_bid_amount")
            ]
        ]
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await state.set_state(AdSenseStates.setting_duration)
        
    except Exception as e:
        logger.error(f"Error showing duration selection: {e}")

async def show_duration_selection_message(message: Message, state: FSMContext, 
                                        selected_channel, bid_type: str, bid_amount: Decimal):
    """Show duration selection interface via message"""
    try:
        text = f"""⏰ **Campaign Duration for {selected_channel.channel_name}**

💰 **Your bid**: ${bid_amount:.3f} per {bid_type.upper()}

Select how long you want your ad to run:"""
        
        keyboard = [
            [
                InlineKeyboardButton(text="⚡ 1 hour", callback_data="duration_1"),
                InlineKeyboardButton(text="🔥 6 hours", callback_data="duration_6")
            ],
            [
                InlineKeyboardButton(text="🌟 12 hours", callback_data="duration_12"),
                InlineKeyboardButton(text="🚀 24 hours", callback_data="duration_24")
            ],
            [
                InlineKeyboardButton(text="💎 48 hours", callback_data="duration_48"),
                InlineKeyboardButton(text="👑 72 hours", callback_data="duration_72")
            ]
        ]
        
        await message.answer(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await state.set_state(AdSenseStates.setting_duration)
        
    except Exception as e:
        logger.error(f"Error showing duration selection: {e}")

@router.callback_query(F.data.startswith("duration_"))
async def handle_duration_selection(callback_query: CallbackQuery, state: FSMContext):
    """Handle duration selection"""
    try:
        user_id = callback_query.from_user.id
        user_language = await db.get_user_language(user_id)
        
        duration_hours = int(callback_query.data.replace("duration_", ""))
        await state.update_data(duration_hours=duration_hours)
        
        text = f"""✍️ **Create Your Ad Content**

Your ad will run for {duration_hours} hours.

Please send your ad content (text message):

📝 **Tips for effective ads:**
• Keep it short and engaging
• Include a clear call-to-action
• Use emojis to attract attention
• Add your contact information or links"""
        
        keyboard = [
            [
                InlineKeyboardButton(
                    text="🔙 Back to duration",
                    callback_data="back_to_duration"
                )
            ]
        ]
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await state.set_state(AdSenseStates.setting_content)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error handling duration selection: {e}")
        await callback_query.answer(get_text(user_language, "error_occurred"))

@router.message(AdSenseStates.setting_content)
async def handle_content_input(message: Message, state: FSMContext):
    """Handle ad content input"""
    try:
        user_id = message.from_user.id
        user_language = await db.get_user_language(user_id)
        
        content = message.text
        if not content or len(content.strip()) < 10:
            await message.answer("⚠️ Please enter at least 10 characters for your ad content.")
            return
        
        await state.update_data(content=content)
        
        text = f"""💰 **Set Your Maximum Budget**

Your ad content: "{content[:100]}..."

Enter your maximum budget for this campaign (USD):

💡 **Budget calculation:**
• Your bid amount will be deducted from this budget
• Campaign stops when budget is exhausted
• Minimum budget: $5.00"""
        
        keyboard = [
            [
                InlineKeyboardButton(text="💡 Suggest budget", callback_data="suggest_budget")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to content", callback_data="back_to_content")
            ]
        ]
        
        await message.answer(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await state.set_state(AdSenseStates.setting_budget)
        
    except Exception as e:
        logger.error(f"Error handling content input: {e}")
        await message.answer(get_text(user_language, "error_occurred"))

@router.callback_query(F.data == "suggest_budget")
async def handle_suggest_budget(callback_query: CallbackQuery, state: FSMContext):
    """Suggest budget based on bid type and duration"""
    try:
        data = await state.get_data()
        bid_amount = data.get('bid_amount')
        bid_type = data.get('bid_type')
        duration_hours = data.get('duration_hours')
        selected_channel = data.get('selected_channel')
        
        if not all([bid_amount, bid_type, duration_hours, selected_channel]):
            await callback_query.answer("Session expired. Please start over.")
            return
        
        # Calculate suggested budget
        if bid_type == "cpc":
            # Estimate clicks based on channel size and engagement
            estimated_clicks = int(selected_channel.subscribers * 0.01 * duration_hours / 24)
            suggested_budget = bid_amount * estimated_clicks
        else:  # CPM
            # Estimate impressions based on channel size
            estimated_impressions = int(selected_channel.subscribers * 0.1 * duration_hours / 24)
            suggested_budget = bid_amount * (estimated_impressions / 1000)
        
        # Ensure minimum budget
        suggested_budget = max(suggested_budget, Decimal('5.00'))
        
        await state.update_data(max_budget=suggested_budget)
        
        await show_bid_confirmation(callback_query, state, data, suggested_budget)
        
    except Exception as e:
        logger.error(f"Error suggesting budget: {e}")
        await callback_query.answer("Error calculating budget")

@router.message(AdSenseStates.setting_budget)
async def handle_budget_input(message: Message, state: FSMContext):
    """Handle manual budget input"""
    try:
        user_id = message.from_user.id
        user_language = await db.get_user_language(user_id)
        
        try:
            max_budget = Decimal(message.text)
            if max_budget < Decimal('5.00'):
                raise ValueError("Budget too low")
        except (ValueError, TypeError):
            await message.answer("⚠️ Please enter a valid budget amount (minimum $5.00)")
            return
        
        await state.update_data(max_budget=max_budget)
        
        data = await state.get_data()
        await show_bid_confirmation_message(message, state, data, max_budget)
        
    except Exception as e:
        logger.error(f"Error handling budget input: {e}")
        await message.answer(get_text(user_language, "error_occurred"))

async def show_bid_confirmation(callback_query: CallbackQuery, state: FSMContext, 
                               data: Dict, max_budget: Decimal):
    """Show bid confirmation"""
    try:
        selected_channel = data.get('selected_channel')
        bid_type = data.get('bid_type')
        bid_amount = data.get('bid_amount')
        duration_hours = data.get('duration_hours')
        content = data.get('content')
        
        text = f"""✅ **Confirm Your Bid**

📺 **Channel**: {selected_channel.channel_name}
💰 **Bid Type**: {bid_type.upper()}
💎 **Bid Amount**: ${bid_amount:.3f}
⏰ **Duration**: {duration_hours} hours
💰 **Max Budget**: ${max_budget:.2f}

📝 **Ad Content**: "{content[:100]}..."

🎯 **Next Steps:**
1. Your bid will enter the auction
2. If you win, your ad will be published
3. You'll only pay when users interact with your ad

Confirm your bid?"""
        
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Confirm Bid", callback_data="confirm_bid"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_bid")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to budget", callback_data="back_to_budget")
            ]
        ]
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await state.set_state(AdSenseStates.confirming_bid)
        
    except Exception as e:
        logger.error(f"Error showing bid confirmation: {e}")

async def show_bid_confirmation_message(message: Message, state: FSMContext, 
                                      data: Dict, max_budget: Decimal):
    """Show bid confirmation via message"""
    try:
        selected_channel = data.get('selected_channel')
        bid_type = data.get('bid_type')
        bid_amount = data.get('bid_amount')
        duration_hours = data.get('duration_hours')
        content = data.get('content')
        
        text = f"""✅ **Confirm Your Bid**

📺 **Channel**: {selected_channel.channel_name}
💰 **Bid Type**: {bid_type.upper()}
💎 **Bid Amount**: ${bid_amount:.3f}
⏰ **Duration**: {duration_hours} hours
💰 **Max Budget**: ${max_budget:.2f}

📝 **Ad Content**: "{content[:100]}..."

🎯 **Next Steps:**
1. Your bid will enter the auction
2. If you win, your ad will be published
3. You'll only pay when users interact with your ad

Confirm your bid?"""
        
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Confirm Bid", callback_data="confirm_bid"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_bid")
            ]
        ]
        
        await message.answer(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await state.set_state(AdSenseStates.confirming_bid)
        
    except Exception as e:
        logger.error(f"Error showing bid confirmation: {e}")

@router.callback_query(F.data == "confirm_bid")
async def handle_confirm_bid(callback_query: CallbackQuery, state: FSMContext):
    """Handle bid confirmation"""
    try:
        user_id = callback_query.from_user.id
        user_language = await db.get_user_language(user_id)
        
        data = await state.get_data()
        selected_channel = data.get('selected_channel')
        bid_type = data.get('bid_type')
        bid_amount = data.get('bid_amount')
        duration_hours = data.get('duration_hours')
        content = data.get('content')
        max_budget = data.get('max_budget')
        
        # Create bid object
        bid = AdBid(
            advertiser_id=user_id,
            channel_id=selected_channel.channel_id,
            bid_amount=bid_amount,
            bid_type=bid_type,
            duration_hours=duration_hours,
            content=content,
            media_url=None,
            target_clicks=None,
            target_impressions=None,
            max_budget=max_budget,
            created_at=datetime.now()
        )
        
        # Place bid
        bid_id = await adsense_system.place_bid(bid)
        
        text = f"""🎉 **Bid Placed Successfully!**

🎯 **Bid ID**: {bid_id}
📺 **Channel**: {selected_channel.channel_name}
💰 **Amount**: ${bid_amount:.3f} per {bid_type.upper()}
⏰ **Duration**: {duration_hours} hours
💰 **Max Budget**: ${max_budget:.2f}

📊 **What happens next:**
• Your bid enters the auction queue
• Auctions run every hour
• You'll be notified if you win
• Ads start immediately after winning

🔔 **Track your bid performance:**
Use /my_bids to see all your active bids"""
        
        keyboard = [
            [
                InlineKeyboardButton(text="📊 View My Bids", callback_data="view_my_bids"),
                InlineKeyboardButton(text="🎯 Place Another Bid", callback_data="browse_channels")
            ],
            [
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")
            ]
        ]
        
        await callback_query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await state.clear()
        await callback_query.answer("Bid placed successfully!")
        
    except Exception as e:
        logger.error(f"Error confirming bid: {e}")
        await callback_query.answer("Error placing bid. Please try again.")

def setup_adsense_handlers(dp):
    """Setup AdSense handlers"""
    dp.include_router(router)
    logger.info("✅ AdSense handlers registered")