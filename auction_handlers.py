"""
Auction System Handlers for I3lani Bot
Handles advertiser and channel owner interactions for auction-based advertising
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from auction_advertising_system import get_auction_system, BidType, AdStatus
from database import Database
from languages import get_text

logger = logging.getLogger(__name__)

# Router for auction handlers
auction_router = Router()

class AuctionAdStates(StatesGroup):
    """States for auction ad creation"""
    waiting_content = State()
    waiting_image = State()
    waiting_category = State()
    waiting_bid_type = State()
    waiting_bid_amount = State()
    waiting_daily_budget = State()
    waiting_target_audience = State()
    waiting_keywords = State()

class ChannelRegistrationStates(StatesGroup):
    """States for channel registration"""
    waiting_channel_info = State()
    waiting_category = State()
    waiting_confirmation = State()

class AuctionHandlers:
    """Handler class for auction advertising system"""
    
    def __init__(self, database: Database):
        self.db = database
        self.auction_system = get_auction_system()
        self.categories = [
            "tech", "lifestyle", "business", "entertainment", "sports",
            "food", "travel", "health", "education", "finance"
        ]
    
    async def create_auction_ad_command(self, message: Message, state: FSMContext):
        """Start auction ad creation process"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        text = get_text(user_lang, "auction_ad_create_start")
        if not text:
            text = "🎯 Let's create your auction advertisement!\n\n" \
                  "Your ad will compete in daily auctions for the best placement in channels.\n\n" \
                  "📝 Please send your ad content (text only or text with image):"
        
        await message.answer(text)
        await state.set_state(AuctionAdStates.waiting_content)
    
    async def handle_ad_content(self, message: Message, state: FSMContext):
        """Handle ad content input"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        content = message.text or message.caption or ""
        image_url = None
        
        # Check for image
        if message.photo:
            # Get largest photo
            photo = message.photo[-1]
            image_url = photo.file_id
        
        # Store content and image
        await state.update_data(
            content=content,
            image_url=image_url
        )
        
        # Show category selection
        keyboard = InlineKeyboardBuilder()
        for category in self.categories:
            keyboard.add(InlineKeyboardButton(
                text=category.title(),
                callback_data=f"auction_category_{category}"
            ))
        keyboard.adjust(2)
        
        text = get_text(user_lang, "auction_select_category")
        if not text:
            text = "📂 Select your ad category:"
        
        await message.answer(text, reply_markup=keyboard.as_markup())
        await state.set_state(AuctionAdStates.waiting_category)
    
    async def handle_category_selection(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle category selection"""
        user_id = callback_query.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        category = callback_query.data.split("_")[-1]
        await state.update_data(category=category)
        
        # Show bid type selection
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(text="💰 CPC (Cost Per Click)", callback_data="bid_type_CPC"),
            InlineKeyboardButton(text="📊 CPM (Cost Per 1000 Views)", callback_data="bid_type_CPM")
        )
        keyboard.adjust(1)
        
        text = get_text(user_lang, "auction_select_bid_type")
        if not text:
            text = f"✅ Category: {category.title()}\n\n" \
                  "💵 Choose your bidding strategy:\n\n" \
                  "• **CPC**: Pay for each click (Min: $0.10)\n" \
                  "• **CPM**: Pay per 1000 views (Min: $1.00)"
        
        await callback_query.message.edit_text(text, reply_markup=keyboard.as_markup())
        await state.set_state(AuctionAdStates.waiting_bid_type)
    
    async def handle_bid_type_selection(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle bid type selection"""
        user_id = callback_query.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        bid_type = callback_query.data.split("_")[-1]
        await state.update_data(bid_type=bid_type)
        
        min_bid = 0.10 if bid_type == "CPC" else 1.00
        bid_name = "per click" if bid_type == "CPC" else "per 1000 views"
        
        text = get_text(user_lang, "auction_enter_bid_amount")
        if not text:
            text = f"💰 Enter your {bid_type} bid amount {bid_name}\n\n" \
                  f"Minimum bid: ${min_bid}\n\n" \
                  "Higher bids increase your chances of winning auctions!"
        
        await callback_query.message.edit_text(text)
        await state.set_state(AuctionAdStates.waiting_bid_amount)
    
    async def handle_bid_amount(self, message: Message, state: FSMContext):
        """Handle bid amount input"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        try:
            bid_amount = float(message.text)
            data = await state.get_data()
            bid_type = data.get("bid_type")
            
            min_bid = 0.10 if bid_type == "CPC" else 1.00
            
            if bid_amount < min_bid:
                error_text = get_text(user_lang, "auction_bid_too_low")
                if not error_text:
                    error_text = f"❌ Bid amount must be at least ${min_bid}"
                await message.answer(error_text)
                return
            
            await state.update_data(bid_amount=bid_amount)
            
            text = get_text(user_lang, "auction_enter_daily_budget")
            if not text:
                text = f"💳 Enter your daily budget (minimum ${bid_amount}):\n\n" \
                      "This is the maximum you'll spend per day on this ad."
            
            await message.answer(text)
            await state.set_state(AuctionAdStates.waiting_daily_budget)
            
        except ValueError:
            error_text = get_text(user_lang, "auction_invalid_amount")
            if not error_text:
                error_text = "❌ Please enter a valid number"
            await message.answer(error_text)
    
    async def handle_daily_budget(self, message: Message, state: FSMContext):
        """Handle daily budget input"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        try:
            daily_budget = float(message.text)
            data = await state.get_data()
            bid_amount = data.get("bid_amount")
            
            if daily_budget < bid_amount:
                error_text = get_text(user_lang, "auction_budget_too_low")
                if not error_text:
                    error_text = f"❌ Daily budget must be at least ${bid_amount}"
                await message.answer(error_text)
                return
            
            await state.update_data(daily_budget=daily_budget)
            
            text = get_text(user_lang, "auction_enter_target_audience")
            if not text:
                text = "🎯 Describe your target audience (optional):\n\n" \
                      "Example: 'Young professionals interested in tech'\n\n" \
                      "Or send /skip to skip this step."
            
            await message.answer(text)
            await state.set_state(AuctionAdStates.waiting_target_audience)
            
        except ValueError:
            error_text = get_text(user_lang, "auction_invalid_amount")
            if not error_text:
                error_text = "❌ Please enter a valid number"
            await message.answer(error_text)
    
    async def handle_target_audience(self, message: Message, state: FSMContext):
        """Handle target audience input"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        target_audience = message.text if message.text != "/skip" else ""
        await state.update_data(target_audience=target_audience)
        
        text = get_text(user_lang, "auction_enter_keywords")
        if not text:
            text = "🔍 Enter keywords for your ad (comma-separated, optional):\n\n" \
                  "Example: 'technology, startup, innovation'\n\n" \
                  "Or send /skip to skip this step."
        
        await message.answer(text)
        await state.set_state(AuctionAdStates.waiting_keywords)
    
    async def handle_keywords(self, message: Message, state: FSMContext):
        """Handle keywords input and create ad"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        keywords = []
        if message.text and message.text != "/skip":
            keywords = [kw.strip() for kw in message.text.split(",")]
        
        # Get all data
        data = await state.get_data()
        
        try:
            # Create auction ad
            ad_id = await self.auction_system.create_auction_ad(
                advertiser_id=user_id,
                content=data["content"],
                image_url=data.get("image_url"),
                category=data["category"],
                bid_type=BidType(data["bid_type"]),
                bid_amount=data["bid_amount"],
                daily_budget=data["daily_budget"],
                target_audience=data.get("target_audience", ""),
                keywords=keywords
            )
            
            # Create summary
            summary = f"✅ **Ad Created Successfully!**\n\n" \
                     f"🆔 Ad ID: {ad_id}\n" \
                     f"📂 Category: {data['category'].title()}\n" \
                     f"💰 Bid Type: {data['bid_type']}\n" \
                     f"💵 Bid Amount: ${data['bid_amount']:.2f}\n" \
                     f"💳 Daily Budget: ${data['daily_budget']:.2f}\n" \
                     f"🎯 Target: {data.get('target_audience', 'General')}\n\n" \
                     f"📋 Your ad is now pending review. It will participate in daily auctions once approved."
            
            await message.answer(summary)
            await state.clear()
            
            logger.info(f"Created auction ad {ad_id} for user {user_id}")
            
        except Exception as e:
            error_text = get_text(user_lang, "auction_create_error")
            if not error_text:
                error_text = f"❌ Error creating ad: {str(e)}"
            await message.answer(error_text)
            await state.clear()
    
    async def register_channel_command(self, message: Message, state: FSMContext):
        """Start channel registration process"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        text = get_text(user_lang, "channel_register_start")
        if not text:
            text = "📺 **Channel Registration**\n\n" \
                  "Register your channel to earn money from ads!\n\n" \
                  "💰 Revenue Split:\n" \
                  "• 68% to you (channel owner)\n" \
                  "• 32% to platform\n\n" \
                  "📋 Please provide your channel information:\n" \
                  "Format: @channel_username or channel_id"
        
        await message.answer(text)
        await state.set_state(ChannelRegistrationStates.waiting_channel_info)
    
    async def handle_channel_info(self, message: Message, state: FSMContext):
        """Handle channel info input"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        channel_info = message.text.strip()
        
        # Basic validation
        if not channel_info.startswith("@") and not channel_info.startswith("-"):
            error_text = get_text(user_lang, "channel_invalid_format")
            if not error_text:
                error_text = "❌ Please provide a valid channel username (@channel) or ID"
            await message.answer(error_text)
            return
        
        await state.update_data(channel_info=channel_info)
        
        # Show category selection
        keyboard = InlineKeyboardBuilder()
        for category in self.categories:
            keyboard.add(InlineKeyboardButton(
                text=category.title(),
                callback_data=f"channel_category_{category}"
            ))
        keyboard.adjust(2)
        
        text = get_text(user_lang, "channel_select_category")
        if not text:
            text = f"📂 Select your channel category for: {channel_info}"
        
        await message.answer(text, reply_markup=keyboard.as_markup())
        await state.set_state(ChannelRegistrationStates.waiting_category)
    
    async def handle_channel_category(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle channel category selection"""
        user_id = callback_query.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        category = callback_query.data.split("_")[-1]
        data = await state.get_data()
        
        # Create confirmation
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(text="✅ Confirm", callback_data="channel_confirm_yes"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="channel_confirm_no")
        )
        
        text = get_text(user_lang, "channel_confirm_registration")
        if not text:
            text = f"📋 **Confirm Channel Registration**\n\n" \
                  f"📺 Channel: {data['channel_info']}\n" \
                  f"📂 Category: {category.title()}\n\n" \
                  f"💰 You'll earn 68% of ad revenue from this channel.\n" \
                  f"🎯 Ads will be selected through daily auctions.\n\n" \
                  f"Confirm registration?"
        
        await callback_query.message.edit_text(text, reply_markup=keyboard.as_markup())
        await state.update_data(category=category)
        await state.set_state(ChannelRegistrationStates.waiting_confirmation)
    
    async def handle_channel_confirmation(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle channel registration confirmation"""
        user_id = callback_query.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        if callback_query.data == "channel_confirm_yes":
            data = await state.get_data()
            
            try:
                # Register channel
                channel_id = f"auction_{user_id}_{int(datetime.now().timestamp())}"
                success = await self.auction_system.register_channel(
                    owner_id=user_id,
                    channel_id=channel_id,
                    name=data["channel_info"],
                    telegram_channel_id=data["channel_info"],
                    category=data["category"]
                )
                
                if success:
                    text = get_text(user_lang, "channel_registered_success")
                    if not text:
                        text = f"✅ **Channel Registered Successfully!**\n\n" \
                              f"📺 Channel: {data['channel_info']}\n" \
                              f"📂 Category: {data['category'].title()}\n" \
                              f"🆔 Channel ID: {channel_id}\n\n" \
                              f"🎯 Your channel will now participate in daily auctions!\n" \
                              f"💰 Check your earnings with /earnings"
                else:
                    text = get_text(user_lang, "channel_registration_failed")
                    if not text:
                        text = "❌ Channel registration failed. Please try again."
                
                await callback_query.message.edit_text(text)
                
            except Exception as e:
                error_text = get_text(user_lang, "channel_registration_error")
                if not error_text:
                    error_text = f"❌ Registration error: {str(e)}"
                await callback_query.message.edit_text(error_text)
        
        else:
            text = get_text(user_lang, "channel_registration_cancelled")
            if not text:
                text = "❌ Channel registration cancelled."
            await callback_query.message.edit_text(text)
        
        await state.clear()
    
    async def show_advertiser_stats(self, message: Message):
        """Show advertiser statistics"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        stats = await self.auction_system.get_advertiser_stats(user_id)
        
        text = get_text(user_lang, "advertiser_stats")
        if not text:
            text = f"📊 **Your Advertising Statistics**\n\n" \
                  f"🎯 Total Ads: {stats['total_ads']}\n" \
                  f"👁️ Total Impressions: {stats['total_impressions']:,}\n" \
                  f"👆 Total Clicks: {stats['total_clicks']:,}\n" \
                  f"📈 Average CTR: {stats['avg_ctr']:.2%}\n" \
                  f"💰 Total Spent: ${stats['total_spent']:.2f}"
        
        await message.answer(text)
    
    async def show_channel_earnings(self, message: Message):
        """Show channel owner earnings"""
        user_id = message.from_user.id
        user_lang = await self.db.get_user_language(user_id)
        
        stats = await self.auction_system.get_channel_owner_stats(user_id)
        
        keyboard = InlineKeyboardBuilder()
        if stats['can_withdraw']:
            keyboard.add(InlineKeyboardButton(
                text="💸 Request Withdrawal",
                callback_data="request_withdrawal"
            ))
        
        text = get_text(user_lang, "channel_earnings")
        if not text:
            text = f"💰 **Your Channel Earnings**\n\n" \
                  f"💵 Current Balance: ${stats['balance']:.2f}\n" \
                  f"📈 Total Earned: ${stats['total_earned']:.2f}\n" \
                  f"💸 Total Withdrawn: ${stats['total_withdrawn']:.2f}\n\n"
            
            if stats['can_withdraw']:
                text += "✅ You can withdraw your earnings (min. $50)"
            else:
                text += f"⏳ Minimum withdrawal: $50.00"
        
        await message.answer(text, reply_markup=keyboard.as_markup())

# Register handlers
def setup_auction_handlers(dp, database: Database):
    """Setup auction handlers"""
    handlers = AuctionHandlers(database)
    
    # Register handlers
    dp.message.register(handlers.create_auction_ad_command, Command("createauction"))
    dp.message.register(handlers.handle_ad_content, AuctionAdStates.waiting_content)
    dp.message.register(handlers.handle_bid_amount, AuctionAdStates.waiting_bid_amount)
    dp.message.register(handlers.handle_daily_budget, AuctionAdStates.waiting_daily_budget)
    dp.message.register(handlers.handle_target_audience, AuctionAdStates.waiting_target_audience)
    dp.message.register(handlers.handle_keywords, AuctionAdStates.waiting_keywords)
    
    dp.callback_query.register(handlers.handle_category_selection, F.data.startswith("auction_category_"))
    dp.callback_query.register(handlers.handle_bid_type_selection, F.data.startswith("bid_type_"))
    
    dp.message.register(handlers.register_channel_command, Command("registerchannel"))
    dp.message.register(handlers.handle_channel_info, ChannelRegistrationStates.waiting_channel_info)
    
    dp.callback_query.register(handlers.handle_channel_category, F.data.startswith("channel_category_"))
    dp.callback_query.register(handlers.handle_channel_confirmation, F.data.startswith("channel_confirm_"))
    
    dp.message.register(handlers.show_advertiser_stats, Command("mystats"))
    dp.message.register(handlers.show_channel_earnings, Command("earnings"))
    
    logger.info("✅ Auction handlers registered")