"""
I3lani v3 Bot Commands Implementation
Complete bot command handlers for auction-based advertising system
"""

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from decimal import Decimal
import asyncio
from datetime import datetime

from i3lani_v3_architecture import i3lani_v3

logger = logging.getLogger(__name__)

class AdCreationStates(StatesGroup):
    """States for ad creation process"""
    waiting_content = State()
    waiting_category = State()
    waiting_bid_type = State()
    waiting_bid_amount = State()
    waiting_payment = State()

class ChannelRegistrationStates(StatesGroup):
    """States for channel registration"""
    waiting_channel_id = State()
    waiting_category = State()

class WithdrawalStates(StatesGroup):
    """States for withdrawal process"""
    waiting_amount = State()
    waiting_wallet = State()

class V3BotCommands:
    """I3lani v3 Bot Command Handlers"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.categories = [
            "Technology", "Business", "Entertainment", "Sports", 
            "Health", "Fashion", "Food", "Travel", "Education", "Other"
        ]
    
    async def start_command(self, message: Message, state: FSMContext):
        """Handle /start command"""
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        
        # Check for referral
        referrer_id = None
        if message.text and len(message.text.split()) > 1:
            ref_code = message.text.split()[1]
            if ref_code.startswith('ref_'):
                referrer_id = int(ref_code.replace('ref_', ''))
        
        # Show user type selection
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 I'm an Advertiser", callback_data="usertype_advertiser")],
            [InlineKeyboardButton(text="📺 I'm a Channel Owner", callback_data="usertype_channel_owner")],
            [InlineKeyboardButton(text="💰 I'm an Affiliate", callback_data="usertype_affiliate")]
        ])
        
        await message.answer(
            "🚀 Welcome to I3lani v3 - Advanced Advertising Platform!\n\n"
            "Choose your role to get started:",
            reply_markup=keyboard
        )
        
        await state.update_data(
            user_id=user_id,
            username=username,
            first_name=first_name,
            referrer_id=referrer_id
        )
    
    async def user_type_callback(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle user type selection"""
        user_type = callback_query.data.replace('usertype_', '')
        data = await state.get_data()
        
        # Register user
        await i3lani_v3.register_user(
            user_id=data['user_id'],
            username=data['username'],
            first_name=data['first_name'],
            user_type=user_type,
            referrer_id=data.get('referrer_id')
        )
        
        # Show role-specific menu
        if user_type == 'advertiser':
            await self.show_advertiser_menu(callback_query)
        elif user_type == 'channel_owner':
            await self.show_channel_owner_menu(callback_query)
        elif user_type == 'affiliate':
            await self.show_affiliate_menu(callback_query)
        
        await callback_query.answer()
        await state.clear()
    
    async def show_advertiser_menu(self, callback_query: CallbackQuery):
        """Show advertiser main menu"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Create Ad", callback_data="create_ad")],
            [InlineKeyboardButton(text="📊 My Ads", callback_data="my_ads")],
            [InlineKeyboardButton(text="💳 Add Balance", callback_data="add_balance")],
            [InlineKeyboardButton(text="📈 Statistics", callback_data="stats")]
        ])
        
        await callback_query.message.edit_text(
            "📢 Advertiser Dashboard\n\n"
            "Create ads with CPC/CPM bidding and reach targeted audiences through our auction system.",
            reply_markup=keyboard
        )
    
    async def show_channel_owner_menu(self, callback_query: CallbackQuery):
        """Show channel owner main menu"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📺 Add Channel", callback_data="add_channel")],
            [InlineKeyboardButton(text="📋 My Channels", callback_data="my_channels")],
            [InlineKeyboardButton(text="💰 Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton(text="📈 Statistics", callback_data="stats")]
        ])
        
        await callback_query.message.edit_text(
            "📺 Channel Owner Dashboard\n\n"
            "Register your channels and earn 68% of ad revenue automatically.",
            reply_markup=keyboard
        )
    
    async def show_affiliate_menu(self, callback_query: CallbackQuery):
        """Show affiliate main menu"""
        user_id = callback_query.from_user.id
        ref_link = f"https://t.me/{(await self.bot.get_me()).username}?start=ref_{user_id}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 My Referral Link", callback_data="ref_link")],
            [InlineKeyboardButton(text="👥 My Referrals", callback_data="my_referrals")],
            [InlineKeyboardButton(text="💰 Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton(text="📈 Statistics", callback_data="stats")]
        ])
        
        await callback_query.message.edit_text(
            f"💰 Affiliate Dashboard\n\n"
            f"Earn 5% commission on all referral activity!\n\n"
            f"Your referral link:\n`{ref_link}`\n\n"
            f"Share this link to start earning commissions.",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    async def create_ad_callback(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle create ad callback"""
        await callback_query.message.edit_text(
            "📢 Create New Ad\n\n"
            "Please send your ad content (text, image, or video):"
        )
        await state.set_state(AdCreationStates.waiting_content)
        await callback_query.answer()
    
    async def process_ad_content(self, message: Message, state: FSMContext):
        """Process ad content"""
        content = message.text or message.caption or "[Media Content]"
        
        # Store content and show category selection
        await state.update_data(content=content)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=cat, callback_data=f"category_{cat}")]
            for cat in self.categories
        ])
        
        await message.answer(
            "📂 Select Ad Category:",
            reply_markup=keyboard
        )
        await state.set_state(AdCreationStates.waiting_category)
    
    async def process_category(self, callback_query: CallbackQuery, state: FSMContext):
        """Process category selection"""
        category = callback_query.data.replace('category_', '')
        await state.update_data(category=category)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 CPC (Cost Per Click) - Min $0.10", callback_data="bid_CPC")],
            [InlineKeyboardButton(text="👁️ CPM (Cost Per 1000 Views) - Min $1.00", callback_data="bid_CPM")]
        ])
        
        await callback_query.message.edit_text(
            f"📂 Category: {category}\n\n"
            "💰 Choose Bid Type:",
            reply_markup=keyboard
        )
        await state.set_state(AdCreationStates.waiting_bid_type)
        await callback_query.answer()
    
    async def process_bid_type(self, callback_query: CallbackQuery, state: FSMContext):
        """Process bid type selection"""
        bid_type = callback_query.data.replace('bid_', '')
        await state.update_data(bid_type=bid_type)
        
        bid_desc = "per click" if bid_type == "CPC" else "per 1000 impressions"
        
        await callback_query.message.edit_text(
            f"💰 Bid Type: {bid_type}\n\n"
            f"Enter your bid amount ({bid_desc}) in USD:\n\n"
            f"Example: 0.50 for $0.50 {bid_desc}"
        )
        await state.set_state(AdCreationStates.waiting_bid_amount)
        await callback_query.answer()
    
    async def process_bid_amount(self, message: Message, state: FSMContext):
        """Process bid amount"""
        try:
            bid_amount = Decimal(message.text)
            data = await state.get_data()
            bid_type = data.get('bid_type')
            
            # Enforce minimum bids per checklist requirements
            minimum_bids = {'CPC': Decimal('0.10'), 'CPM': Decimal('1.00')}
            minimum = minimum_bids.get(bid_type, Decimal('0.01'))
            
            if bid_amount < minimum:
                await message.answer(
                    f"❌ Minimum {bid_type} bid is ${minimum}\n\n"
                    f"💰 Minimum Requirements:\n"
                    f"• CPC (Cost Per Click): $0.10\n"
                    f"• CPM (Cost Per 1000 Views): $1.00\n\n"
                    f"Please enter a higher amount:"
                )
                return
            
            # Create ad
            ad_id = await i3lani_v3.create_ad(
                advertiser_id=message.from_user.id,
                content=data['content'],
                category=data['category'],
                bid_type=data['bid_type'],
                bid_amount=bid_amount
            )
            
            # Show payment options
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💎 Pay with TON", callback_data=f"pay_ton_{ad_id}")],
                [InlineKeyboardButton(text="⭐ Pay with Telegram Stars", callback_data=f"pay_stars_{ad_id}")]
            ])
            
            await message.answer(
                f"✅ Ad Created Successfully!\n\n"
                f"📢 Ad ID: {ad_id}\n"
                f"📂 Category: {data['category']}\n"
                f"💰 Bid: ${bid_amount} {data['bid_type']}\n\n"
                f"💳 Choose Payment Method:",
                reply_markup=keyboard
            )
            
            await state.clear()
            
        except (ValueError, TypeError):
            await message.answer("❌ Invalid amount. Please enter a valid number.")
    
    async def add_channel_callback(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle add channel callback"""
        await callback_query.message.edit_text(
            "📺 Add Channel\n\n"
            "Please send your channel username or ID:\n"
            "Example: @mychannel or -1001234567890\n\n"
            "⚠️ Make sure the bot is an admin in your channel!"
        )
        await state.set_state(ChannelRegistrationStates.waiting_channel_id)
        await callback_query.answer()
    
    async def process_channel_id(self, message: Message, state: FSMContext):
        """Process channel ID/username"""
        channel_id = message.text.strip()
        
        try:
            # Verify bot is admin
            chat = await self.bot.get_chat(channel_id)
            admins = await self.bot.get_chat_administrators(channel_id)
            bot_info = await self.bot.get_me()
            
            is_admin = any(admin.user.id == bot_info.id for admin in admins)
            
            if not is_admin:
                await message.answer("❌ Bot is not an admin in this channel. Please add the bot as admin first.")
                return
            
            # Store channel info
            await state.update_data(
                channel_id=str(chat.id),
                channel_name=chat.title,
                subscribers=chat.members_count or 0
            )
            
            # Show category selection
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=cat, callback_data=f"ch_category_{cat}")]
                for cat in self.categories
            ])
            
            await message.answer(
                f"✅ Channel Verified: {chat.title}\n"
                f"👥 Members: {chat.members_count or 0}\n\n"
                f"📂 Select Channel Category:",
                reply_markup=keyboard
            )
            await state.set_state(ChannelRegistrationStates.waiting_category)
            
        except Exception as e:
            await message.answer(f"❌ Error accessing channel: {str(e)}")
    
    async def process_channel_category(self, callback_query: CallbackQuery, state: FSMContext):
        """Process channel category selection"""
        category = callback_query.data.replace('ch_category_', '')
        data = await state.get_data()
        
        # Add channel to database
        await i3lani_v3.add_channel(
            channel_id=data['channel_id'],
            channel_name=data['channel_name'],
            owner_id=callback_query.from_user.id,
            category=category,
            subscribers=data['subscribers']
        )
        
        await callback_query.message.edit_text(
            f"✅ Channel Added Successfully!\n\n"
            f"📺 Channel: {data['channel_name']}\n"
            f"📂 Category: {category}\n"
            f"👥 Subscribers: {data['subscribers']}\n\n"
            f"Your channel is now ready to receive ads through our auction system!"
        )
        
        await state.clear()
        await callback_query.answer()
    
    async def stats_callback(self, callback_query: CallbackQuery):
        """Handle statistics callback"""
        user_id = callback_query.from_user.id
        stats = await i3lani_v3.get_user_stats(user_id)
        
        if not stats:
            await callback_query.message.edit_text("❌ User not found. Please use /start first.")
            return
        
        user_type = stats['user_type']
        
        if user_type == 'advertiser':
            text = (
                f"📊 Advertiser Statistics\n\n"
                f"💰 TON Balance: {stats['balance_ton']:.8f}\n"
                f"⭐ Stars Balance: {stats['balance_stars']}\n\n"
                f"📢 Total Ads: {stats['total_ads']}\n"
                f"👁️ Total Impressions: {stats['total_impressions']}\n"
                f"👆 Total Clicks: {stats['total_clicks']}\n"
                f"💸 Total Spent: ${stats['total_spent']:.2f}"
            )
        elif user_type == 'channel_owner':
            text = (
                f"📊 Channel Owner Statistics\n\n"
                f"💰 TON Balance: {stats['balance_ton']:.8f}\n\n"
                f"📺 Total Channels: {stats['total_channels']}\n"
                f"👁️ Total Impressions: {stats['total_impressions']}\n"
                f"👆 Total Clicks: {stats['total_clicks']}\n"
                f"💰 Total Earnings: ${stats['total_revenue']:.2f}"
            )
        elif user_type == 'affiliate':
            text = (
                f"📊 Affiliate Statistics\n\n"
                f"💰 TON Balance: {stats['balance_ton']:.8f}\n\n"
                f"👥 Total Referrals: {stats['total_referrals']}\n"
                f"💰 Total Commissions: ${stats['total_commissions']:.2f}"
            )
        
        await callback_query.message.edit_text(text)
        await callback_query.answer()
    
    async def withdraw_callback(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle withdraw callback"""
        user_id = callback_query.from_user.id
        stats = await i3lani_v3.get_user_stats(user_id)
        
        if not stats or stats['balance_ton'] < 50:
            await callback_query.message.edit_text(
                f"❌ Insufficient Balance\n\n"
                f"💰 Current Balance: {stats['balance_ton']:.8f} TON\n"
                f"📋 Minimum Withdrawal: $50 worth of TON\n\n"
                f"Continue earning to reach the minimum threshold!"
            )
            return
        
        await callback_query.message.edit_text(
            f"💰 Withdraw TON\n\n"
            f"💰 Available Balance: {stats['balance_ton']:.8f} TON\n"
            f"📋 Minimum: $50 worth of TON\n\n"
            f"Enter withdrawal amount in USD:"
        )
        
        await state.set_state(WithdrawalStates.waiting_amount)
        await callback_query.answer()
    
    async def process_withdrawal_amount(self, message: Message, state: FSMContext):
        """Process withdrawal amount"""
        try:
            amount = Decimal(message.text)
            if amount < 50:
                await message.answer("❌ Minimum withdrawal is $50")
                return
            
            await state.update_data(amount=amount)
            
            await message.answer(
                f"💰 Withdrawal Amount: ${amount}\n\n"
                f"📝 Enter your TON wallet address:"
            )
            await state.set_state(WithdrawalStates.waiting_wallet)
            
        except (ValueError, TypeError):
            await message.answer("❌ Invalid amount. Please enter a valid number.")
    
    async def process_wallet_address(self, message: Message, state: FSMContext):
        """Process wallet address"""
        wallet_address = message.text.strip()
        data = await state.get_data()
        
        # Process withdrawal
        result = await i3lani_v3.withdrawal.process_withdrawal_request(
            user_id=message.from_user.id,
            amount=data['amount'],
            wallet_address=wallet_address
        )
        
        if result['success']:
            await message.answer(
                f"✅ Withdrawal Request Submitted!\n\n"
                f"💰 Amount: ${data['amount']}\n"
                f"📝 Wallet: {wallet_address}\n"
                f"🆔 Request ID: {result['withdrawal_id']}\n\n"
                f"Your withdrawal will be processed within 24 hours."
            )
        else:
            await message.answer(f"❌ Withdrawal failed: {result['error']}")
        
        await state.clear()

def setup_v3_handlers(dp: Dispatcher, bot: Bot):
    """Setup I3lani v3 command handlers"""
    commands = V3BotCommands(bot)
    
    # Register handlers
    dp.message.register(commands.start_command, Command("start"))
    dp.callback_query.register(commands.user_type_callback, lambda c: c.data.startswith("usertype_"))
    dp.callback_query.register(commands.create_ad_callback, lambda c: c.data == "create_ad")
    dp.callback_query.register(commands.add_channel_callback, lambda c: c.data == "add_channel")
    dp.callback_query.register(commands.stats_callback, lambda c: c.data == "stats")
    dp.callback_query.register(commands.withdraw_callback, lambda c: c.data == "withdraw")
    
    # State handlers
    dp.message.register(commands.process_ad_content, AdCreationStates.waiting_content)
    dp.message.register(commands.process_bid_amount, AdCreationStates.waiting_bid_amount)
    dp.message.register(commands.process_channel_id, ChannelRegistrationStates.waiting_channel_id)
    dp.message.register(commands.process_withdrawal_amount, WithdrawalStates.waiting_amount)
    dp.message.register(commands.process_wallet_address, WithdrawalStates.waiting_wallet)
    
    # Category callbacks
    dp.callback_query.register(commands.process_category, lambda c: c.data.startswith("category_"))
    dp.callback_query.register(commands.process_bid_type, lambda c: c.data.startswith("bid_"))
    dp.callback_query.register(commands.process_channel_category, lambda c: c.data.startswith("ch_category_"))
    
    logger.info("✅ I3lani v3 command handlers registered")