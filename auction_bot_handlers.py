"""
Auction Bot Handlers for I3lani Bot
Complete handler implementation for auction-based advertising system
"""

import logging
from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from decimal import Decimal
from datetime import datetime
import json

from auction_advertising_system import (
    get_auction_system, ChannelCategory, BidType, AdStatus,
    AuctionAdvertisingSystem
)
from database import Database

logger = logging.getLogger(__name__)

class ChannelRegistrationStates(StatesGroup):
    waiting_channel = State()
    selecting_category = State()

class AdCreationStates(StatesGroup):
    waiting_content = State()
    waiting_image = State()
    selecting_category = State()
    selecting_bid_type = State()
    waiting_bid_amount = State()
    confirming_ad = State()

class AuctionBotHandlers:
    def __init__(self, bot, database: Database):
        self.bot = bot
        self.db = database
        self.auction_system = None
        
    async def initialize(self):
        """Initialize auction system"""
        self.auction_system = await get_auction_system()
        
    def create_category_keyboard(self) -> InlineKeyboardMarkup:
        """Create category selection keyboard"""
        keyboard = []
        categories = [
            (ChannelCategory.TECH, "💻 Tech"),
            (ChannelCategory.LIFESTYLE, "🌟 Lifestyle"),
            (ChannelCategory.BUSINESS, "💼 Business"),
            (ChannelCategory.ENTERTAINMENT, "🎬 Entertainment"),
            (ChannelCategory.EDUCATION, "📚 Education"),
            (ChannelCategory.SHOPPING, "🛍️ Shopping"),
            (ChannelCategory.CRYPTO, "₿ Crypto"),
            (ChannelCategory.HEALTH, "🏥 Health"),
            (ChannelCategory.TRAVEL, "✈️ Travel"),
            (ChannelCategory.FOOD, "🍕 Food"),
            (ChannelCategory.GENERAL, "📋 General")
        ]
        
        # Create 2 columns
        for i in range(0, len(categories), 2):
            row = []
            for j in range(2):
                if i + j < len(categories):
                    cat_enum, cat_display = categories[i + j]
                    row.append(InlineKeyboardButton(
                        text=cat_display,
                        callback_data=f"category_select_{cat_enum.value}"
                    ))
            keyboard.append(row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def create_bid_type_keyboard(self) -> InlineKeyboardMarkup:
        """Create bid type selection keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 CPC (Cost Per Click)", callback_data="bid_type_cpc"),
                InlineKeyboardButton(text="👁️ CPM (Cost Per 1000 Views)", callback_data="bid_type_cpm")
            ],
            [
                InlineKeyboardButton(text="❓ Learn More", callback_data="bid_type_help")
            ]
        ])
    
    async def addchannel_command(self, message: Message, state: FSMContext):
        """Handle /addchannel command"""
        try:
            await state.set_state(ChannelRegistrationStates.waiting_channel)
            
            response = """
🎯 **Channel Registration**

Welcome to the I3lani auction advertising platform! 

To register your channel:
1. Forward a message from your channel
2. Or send your channel username (e.g., @yourchannel)
3. Ensure the bot is an admin in your channel

**Revenue Sharing**: 68% to you, 32% to platform
**Minimum Withdrawal**: $50 via TON or Telegram Stars

Send your channel information:
"""
            
            await message.answer(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error in addchannel command: {e}")
            await message.answer("❌ Error processing command. Please try again.")
    
    async def process_channel_registration(self, message: Message, state: FSMContext):
        """Process channel registration"""
        try:
            channel_id = None
            channel_title = None
            
            # Handle forwarded message
            if message.forward_origin:
                if hasattr(message.forward_origin, 'chat'):
                    channel_id = str(message.forward_origin.chat.id)
                    channel_title = message.forward_origin.chat.title
                elif hasattr(message.forward_origin, 'channel_chat_id'):
                    channel_id = str(message.forward_origin.channel_chat_id)
            
            # Handle channel username
            elif message.text and message.text.startswith('@'):
                username = message.text[1:]  # Remove @
                try:
                    chat = await self.bot.get_chat(username)
                    channel_id = str(chat.id)
                    channel_title = chat.title
                except Exception as e:
                    logger.error(f"❌ Error getting chat info: {e}")
                    await message.answer("❌ Channel not found. Please check the username or forward a message from the channel.")
                    return
            
            else:
                await message.answer("❌ Please forward a message from your channel or send the channel username (e.g., @yourchannel)")
                return
            
            if not channel_id:
                await message.answer("❌ Could not identify channel. Please try again.")
                return
            
            # Check if bot is admin
            try:
                member = await self.bot.get_chat_member(channel_id, self.bot.id)
                if member.status not in ['administrator', 'creator']:
                    await message.answer("❌ Bot must be an admin in the channel to register it.")
                    return
            except Exception as e:
                logger.error(f"❌ Error checking bot admin status: {e}")
                await message.answer("❌ Could not verify bot admin status. Please ensure the bot is an admin in your channel.")
                return
            
            # Get channel subscriber count
            try:
                chat_info = await self.bot.get_chat(channel_id)
                subscriber_count = await self.bot.get_chat_member_count(channel_id)
            except Exception as e:
                logger.error(f"❌ Error getting channel info: {e}")
                subscriber_count = 0
            
            # Store channel info for category selection
            await state.update_data(
                channel_id=channel_id,
                channel_title=channel_title or "Unknown Channel",
                subscriber_count=subscriber_count,
                owner_id=message.from_user.id
            )
            
            await state.set_state(ChannelRegistrationStates.selecting_category)
            
            response = f"""
✅ **Channel Verified**: {channel_title}
👥 **Subscribers**: {subscriber_count:,}
📊 **Channel ID**: {channel_id}

Now select your channel category:
"""
            
            await message.answer(response, reply_markup=self.create_category_keyboard(), parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error processing channel registration: {e}")
            await message.answer("❌ Error processing registration. Please try again.")
    
    async def handle_category_selection(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle category selection"""
        try:
            category_value = callback_query.data.replace("category_select_", "")
            category = ChannelCategory(category_value)
            
            # Get stored channel data
            data = await state.get_data()
            channel_id = data['channel_id']
            owner_id = data['owner_id']
            subscriber_count = data['subscriber_count']
            channel_title = data['channel_title']
            
            # Register channel in auction system
            success = await self.auction_system.add_channel(
                channel_id=channel_id,
                owner_id=owner_id,
                category=category,
                subscribers=subscriber_count
            )
            
            if success:
                await callback_query.message.edit_text(
                    f"""
🎉 **Channel Successfully Registered!**

📺 **Channel**: {channel_title}
📂 **Category**: {category.value.title()}
👥 **Subscribers**: {subscriber_count:,}

**Next Steps**:
• Your channel is now in the auction system
• Daily auctions match highest bidding ads to your channel
• You earn 68% of ad revenue
• Use /stats to track your earnings

**Revenue Sharing**:
• 68% to you (channel owner)
• 32% to platform
• Minimum withdrawal: $50

Welcome to I3lani! 🚀
""",
                    parse_mode='Markdown'
                )
                
                await state.clear()
                logger.info(f"✅ Channel {channel_id} registered successfully with category {category.value}")
                
            else:
                await callback_query.message.edit_text(
                    "❌ Error registering channel. Please try again or contact support."
                )
                
        except Exception as e:
            logger.error(f"❌ Error handling category selection: {e}")
            await callback_query.message.edit_text("❌ Error processing selection. Please try again.")
    
    async def createad_command(self, message: Message, state: FSMContext):
        """Handle /createad command"""
        try:
            await state.set_state(AdCreationStates.waiting_content)
            
            response = """
📝 **Create Advertisement**

Welcome to I3lani's auction advertising system!

**How it works**:
• Submit your ad content and bid amount
• Daily auctions match your ad to relevant channels
• Pay only for results (clicks or impressions)
• Your ad gets published in winning channels

**Step 1**: Send your ad content (text message)
You can add images in the next step.

**Minimum Bids**:
• CPC (Cost Per Click): $0.10
• CPM (Cost Per 1000 Views): $1.00

Send your ad text:
"""
            
            await message.answer(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error in createad command: {e}")
            await message.answer("❌ Error processing command. Please try again.")
    
    async def process_ad_content(self, message: Message, state: FSMContext):
        """Process ad content"""
        try:
            if not message.text:
                await message.answer("❌ Please send text content for your ad.")
                return
            
            await state.update_data(content=message.text)
            await state.set_state(AdCreationStates.waiting_image)
            
            response = """
✅ **Ad Content Saved**

**Step 2**: Send an image for your ad (optional)

You can:
• Send a photo to include with your ad
• Send /skip to continue without image
• Send /back to edit your content

Your ad will be more engaging with an image! 📸
"""
            
            await message.answer(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error processing ad content: {e}")
            await message.answer("❌ Error processing content. Please try again.")
    
    async def process_ad_image(self, message: Message, state: FSMContext):
        """Process ad image"""
        try:
            image_url = None
            
            if message.photo:
                # Get the largest photo
                photo = message.photo[-1]
                file_info = await self.bot.get_file(photo.file_id)
                image_url = f"https://api.telegram.org/file/bot{self.bot.token}/{file_info.file_path}"
            
            await state.update_data(image_url=image_url)
            await state.set_state(AdCreationStates.selecting_category)
            
            if image_url:
                response = "✅ **Image Added**\n\n"
            else:
                response = "📝 **Continuing without image**\n\n"
            
            response += "**Step 3**: Select your target category:"
            
            await message.answer(response, reply_markup=self.create_category_keyboard(), parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error processing ad image: {e}")
            await message.answer("❌ Error processing image. Please try again.")
    
    async def handle_ad_category_selection(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle ad category selection"""
        try:
            category_value = callback_query.data.replace("category_select_", "")
            category = ChannelCategory(category_value)
            
            await state.update_data(category=category)
            await state.set_state(AdCreationStates.selecting_bid_type)
            
            await callback_query.message.edit_text(
                f"""
✅ **Category Selected**: {category.value.title()}

**Step 4**: Choose your bidding strategy:

**CPC (Cost Per Click)**: Pay only when users click your ad
• Great for driving traffic to your website
• Minimum bid: $0.10 per click

**CPM (Cost Per 1000 Views)**: Pay per thousand impressions
• Great for brand awareness
• Minimum bid: $1.00 per 1000 views

Choose your bidding type:
""",
                reply_markup=self.create_bid_type_keyboard(),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ Error handling ad category selection: {e}")
            await callback_query.message.edit_text("❌ Error processing selection. Please try again.")
    
    async def handle_bid_type_selection(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle bid type selection"""
        try:
            if callback_query.data == "bid_type_help":
                await callback_query.answer(
                    "CPC: You pay when users click your ad. CPM: You pay per 1000 views of your ad.",
                    show_alert=True
                )
                return
            
            bid_type_value = callback_query.data.replace("bid_type_", "")
            bid_type = BidType(bid_type_value)
            
            await state.update_data(bid_type=bid_type)
            await state.set_state(AdCreationStates.waiting_bid_amount)
            
            min_bid = "$0.10" if bid_type == BidType.CPC else "$1.00"
            bid_description = "per click" if bid_type == BidType.CPC else "per 1000 views"
            
            await callback_query.message.edit_text(
                f"""
✅ **Bid Type Selected**: {bid_type.value.upper()}

**Step 5**: Enter your bid amount

**Your Choice**: {bid_type.value.upper()} ({bid_description})
**Minimum Bid**: {min_bid}

**How auctions work**:
• Daily auctions match ads to channels by category
• Highest bidders win premium channel slots
• You only pay when your ad gets results

**Enter your bid amount (e.g., 0.25 for $0.25):**
""",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"❌ Error handling bid type selection: {e}")
            await callback_query.message.edit_text("❌ Error processing selection. Please try again.")
    
    async def process_bid_amount(self, message: Message, state: FSMContext):
        """Process bid amount"""
        try:
            try:
                bid_amount = Decimal(message.text.replace('$', '').strip())
            except Exception:
                await message.answer("❌ Please enter a valid amount (e.g., 0.25 for $0.25)")
                return
            
            data = await state.get_data()
            bid_type = data['bid_type']
            
            # Validate minimum bid
            min_bid = self.auction_system.min_cpc_bid if bid_type == BidType.CPC else self.auction_system.min_cpm_bid
            if bid_amount < min_bid:
                await message.answer(f"❌ Minimum bid for {bid_type.value.upper()} is ${min_bid}")
                return
            
            await state.update_data(bid_amount=bid_amount)
            await state.set_state(AdCreationStates.confirming_ad)
            
            # Create confirmation message
            content = data['content']
            image_url = data.get('image_url')
            category = data['category']
            
            confirmation = f"""
📋 **Confirm Your Advertisement**

**Content**: {content[:100]}{"..." if len(content) > 100 else ""}
**Image**: {"✅ Included" if image_url else "❌ No image"}
**Category**: {category.value.title()}
**Bid Type**: {bid_type.value.upper()}
**Bid Amount**: ${bid_amount}

**What happens next**:
• Your ad goes into the approval queue
• Once approved, it enters daily auctions
• You'll be notified when your ad is published

**Cost**: You only pay when your ad gets results ({bid_type.value})

Confirm your ad?
"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Submit Ad", callback_data="confirm_ad"),
                    InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_ad")
                ]
            ])
            
            await message.answer(confirmation, reply_markup=keyboard, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error processing bid amount: {e}")
            await message.answer("❌ Error processing bid. Please try again.")
    
    async def handle_ad_confirmation(self, callback_query: CallbackQuery, state: FSMContext):
        """Handle ad confirmation"""
        try:
            if callback_query.data == "cancel_ad":
                await callback_query.message.edit_text("❌ Ad creation cancelled.")
                await state.clear()
                return
            
            # Get ad data
            data = await state.get_data()
            
            # Create ad in auction system
            ad_id = await self.auction_system.create_ad(
                advertiser_id=callback_query.from_user.id,
                content=data['content'],
                image_url=data.get('image_url'),
                category=data['category'],
                bid_type=data['bid_type'],
                bid_amount=data['bid_amount']
            )
            
            if ad_id:
                await callback_query.message.edit_text(
                    f"""
🎉 **Ad Successfully Submitted!**

**Ad ID**: {ad_id}
**Status**: Pending Review
**Bid**: ${data['bid_amount']} ({data['bid_type'].value.upper()})
**Category**: {data['category'].value.title()}

**Next Steps**:
• Your ad is now in the approval queue
• Admin will review within 24 hours
• Once approved, it enters daily auctions
• You'll be notified when published

**Track Progress**:
• Use /stats to check your ad performance
• Use /myads to see all your advertisements

Thank you for using I3lani! 🚀
""",
                    parse_mode='Markdown'
                )
                
                await state.clear()
                logger.info(f"✅ Ad {ad_id} created successfully by user {callback_query.from_user.id}")
                
            else:
                await callback_query.message.edit_text(
                    "❌ Error creating ad. Please try again or contact support."
                )
                
        except Exception as e:
            logger.error(f"❌ Error handling ad confirmation: {e}")
            await callback_query.message.edit_text("❌ Error processing confirmation. Please try again.")
    
    async def stats_command(self, message: Message, state: FSMContext):
        """Handle /stats command"""
        try:
            user_id = message.from_user.id
            
            # Get user stats (for channel owners)
            user_stats = await self.auction_system.get_user_stats(user_id)
            
            # Get advertiser stats
            advertiser_stats = await self.auction_system.get_advertiser_stats(user_id)
            
            response = "📊 **Your I3lani Statistics**\n\n"
            
            # Channel owner stats
            if user_stats and user_stats.get('channels'):
                response += f"""
**💰 Channel Owner Earnings**
• Balance: ${user_stats['balance']:.2f}
• Total Earned: ${user_stats['total_earned']:.2f}
• Total Withdrawn: ${user_stats['total_withdrawn']:.2f}

**📺 Your Channels** ({len(user_stats['channels'])}):
"""
                for channel in user_stats['channels']:
                    response += f"• {channel['channel_id']} - {channel['category'].title()} - {channel['subscribers']} subscribers\n"
                
                if user_stats['recent_earnings']:
                    response += f"\n**💸 Recent Earnings**:\n"
                    for earning in user_stats['recent_earnings'][:5]:
                        response += f"• ${earning['amount']:.2f} ({earning['type'].upper()}) - {earning['date'][:10]}\n"
            
            # Advertiser stats
            if advertiser_stats and advertiser_stats.get('ads'):
                response += f"""
**📈 Advertiser Performance**
• Total Ads: {len(advertiser_stats['ads'])}

**📋 Your Ads**:
"""
                for ad in advertiser_stats['ads'][:10]:
                    response += f"• {ad['ad_id']}: {ad['content'][:30]}...\n"
                    response += f"  Status: {ad['status'].title()} | Bid: ${ad['bid_amount']} ({ad['bid_type'].upper()})\n"
                    response += f"  Performance: {ad['impressions']} views, {ad['clicks']} clicks, ${ad['spent']:.2f} spent\n\n"
            
            if not user_stats.get('channels') and not advertiser_stats.get('ads'):
                response += """
**🚀 Get Started**:
• Use /addchannel to register your channel and start earning
• Use /createad to advertise your business
• Minimum withdrawal: $50 via TON or Telegram Stars

Welcome to I3lani! 🎯
"""
            
            await message.answer(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Error in stats command: {e}")
            await message.answer("❌ Error retrieving stats. Please try again.")
    
    async def handle_skip_command(self, message: Message, state: FSMContext):
        """Handle /skip command"""
        current_state = await state.get_state()
        
        if current_state == AdCreationStates.waiting_image:
            await self.process_ad_image(message, state)
        else:
            await message.answer("❌ Skip command not available in current step.")
    
    async def handle_back_command(self, message: Message, state: FSMContext):
        """Handle /back command"""
        current_state = await state.get_state()
        
        if current_state == AdCreationStates.waiting_image:
            await state.set_state(AdCreationStates.waiting_content)
            await message.answer("📝 **Back to Content**\n\nSend your ad content (text message):")
        else:
            await message.answer("❌ Back command not available in current step.")

# Global handlers instance
auction_handlers = None

def setup_auction_handlers(dp, bot, database):
    """Setup auction bot handlers"""
    global auction_handlers
    auction_handlers = AuctionBotHandlers(bot, database)
    
    # Register handlers
    dp.message.register(auction_handlers.addchannel_command, Command("addchannel"))
    dp.message.register(auction_handlers.createad_command, Command("createad"))
    dp.message.register(auction_handlers.stats_command, Command("stats"))
    dp.message.register(auction_handlers.handle_skip_command, Command("skip"))
    dp.message.register(auction_handlers.handle_back_command, Command("back"))
    
    # State handlers
    dp.message.register(
        auction_handlers.process_channel_registration,
        StateFilter(ChannelRegistrationStates.waiting_channel)
    )
    
    dp.message.register(
        auction_handlers.process_ad_content,
        StateFilter(AdCreationStates.waiting_content)
    )
    
    dp.message.register(
        auction_handlers.process_ad_image,
        StateFilter(AdCreationStates.waiting_image)
    )
    
    dp.message.register(
        auction_handlers.process_bid_amount,
        StateFilter(AdCreationStates.waiting_bid_amount)
    )
    
    # Callback handlers
    dp.callback_query.register(
        auction_handlers.handle_category_selection,
        F.data.startswith("category_select_"),
        StateFilter(ChannelRegistrationStates.selecting_category)
    )
    
    dp.callback_query.register(
        auction_handlers.handle_ad_category_selection,
        F.data.startswith("category_select_"),
        StateFilter(AdCreationStates.selecting_category)
    )
    
    dp.callback_query.register(
        auction_handlers.handle_bid_type_selection,
        F.data.startswith("bid_type_"),
        StateFilter(AdCreationStates.selecting_bid_type)
    )
    
    dp.callback_query.register(
        auction_handlers.handle_ad_confirmation,
        F.data.in_(["confirm_ad", "cancel_ad"]),
        StateFilter(AdCreationStates.confirming_ad)
    )
    
    logger.info("✅ Auction advertising handlers registered")

async def initialize_auction_handlers():
    """Initialize auction handlers"""
    global auction_handlers
    if auction_handlers:
        await auction_handlers.initialize()
        logger.info("✅ Auction handlers initialized")