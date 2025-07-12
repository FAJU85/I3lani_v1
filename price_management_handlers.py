"""
Price Management Handlers for I3lani Bot
Admin panel integration for price management
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from price_management_system import get_price_manager
from admin_system import safe_callback_answer, safe_edit_message
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

class PriceManagementStates(StatesGroup):
    """Price management FSM states"""
    waiting_for_new_price_data = State()
    waiting_for_edit_price_data = State()
    waiting_for_bulk_update_data = State()

# Router for price management
price_management_router = Router()

@price_management_router.callback_query(F.data == "admin_price_management")
async def show_price_management(callback_query: CallbackQuery, state: FSMContext):
    """Show price management interface"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        manager = get_price_manager()
        await manager.initialize_database()
        
        # Get pricing summary
        summary = await manager.get_pricing_summary()
        tiers = await manager.get_all_price_tiers()
        
        text = f"""
💰 <b>Comprehensive Price Management System</b>

📊 <b>System Overview:</b>
• Base Price: ${summary.get('base_price_usd', 1.00):.2f}/post/day

🎯 <b>Current Pricing:</b>
• Total Tiers: {summary.get('current_pricing', {}).get('total', 0)}
• Active Tiers: {summary.get('current_pricing', {}).get('active', 0)}
• Price Range: ${summary.get('current_pricing', {}).get('min_price', 0):.2f} - ${summary.get('current_pricing', {}).get('max_price', 0):.2f}

🆕 <b>New Pricing:</b>
• Total Plans: {summary.get('new_pricing', {}).get('total', 0)}
• Active Plans: {summary.get('new_pricing', {}).get('active', 0)}

🎁 <b>Promotional Offers:</b>
• Total Offers: {summary.get('offers', {}).get('total', 0)}
• Active Offers: {summary.get('offers', {}).get('active', 0)}
• Max Discount: {summary.get('offers', {}).get('max_discount', 0):.0f}%

📦 <b>Bundle Packages:</b>
• Total Bundles: {summary.get('bundles', {}).get('total', 0)}
• Active Bundles: {summary.get('bundles', {}).get('active', 0)}
• Featured: {summary.get('bundles', {}).get('featured', 0)}
• Max Savings: {summary.get('bundles', {}).get('max_savings', 0):.0f}%

🔧 <b>Management Categories:</b>
"""
        
        # Create management keyboard with all categories
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 Current Pricing", callback_data="price_manage_current"),
                InlineKeyboardButton(text="🆕 New Pricing", callback_data="price_manage_new")
            ],
            [
                InlineKeyboardButton(text="🎁 Offers", callback_data="price_manage_offers"),
                InlineKeyboardButton(text="📦 Bundles", callback_data="price_manage_bundles")
            ],
            [
                InlineKeyboardButton(text="📊 Analytics", callback_data="price_analytics_all"),
                InlineKeyboardButton(text="📈 History", callback_data="price_history_all")
            ],
            [
                InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_price_management"),
                InlineKeyboardButton(text="🏠 Back to Admin", callback_data="admin_main")
            ]
        ])
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Price management loaded")
        
    except Exception as e:
        logger.error(f"Error showing price management: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading price management", show_alert=True)

# CURRENT PRICING HANDLERS
@price_management_router.callback_query(F.data == "price_manage_current")
async def manage_current_pricing(callback_query: CallbackQuery, state: FSMContext):
    """Manage current pricing tiers"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        manager = get_price_manager()
        tiers = await manager.get_all_price_tiers()
        
        text = f"""
💰 <b>Current Pricing Management</b>

📊 <b>Active Price Tiers ({len([t for t in tiers if t['is_active']])} active):</b>
"""
        
        for tier in tiers[:8]:  # Show up to 8 tiers
            status_icon = "🟢" if tier['is_active'] else "🔴"
            text += f"• {status_icon} <b>{tier['duration_days']} days</b> - {tier['posts_per_day']} posts/day\n"
            text += f"  ${tier['final_price_usd']:.2f} ({tier['discount_percent']:.0f}% discount)\n"
        
        if len(tiers) > 8:
            text += f"... and {len(tiers) - 8} more tiers\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Add Price Tier", callback_data="price_add_new"),
                InlineKeyboardButton(text="✏️ Edit Tier", callback_data="price_edit_list")
            ],
            [
                InlineKeyboardButton(text="📋 All Tiers", callback_data="price_view_all"),
                InlineKeyboardButton(text="🗑️ Delete Tier", callback_data="price_delete_list")
            ],
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="admin_price_management")
            ]
        ])
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Current pricing loaded")
        
    except Exception as e:
        logger.error(f"Error managing current pricing: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading current pricing", show_alert=True)

# NEW PRICING HANDLERS
@price_management_router.callback_query(F.data == "price_manage_new")
async def manage_new_pricing(callback_query: CallbackQuery, state: FSMContext):
    """Manage new/experimental pricing"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        manager = get_price_manager()
        new_pricing = await manager.get_all_new_pricing()
        
        text = f"""
🆕 <b>New Pricing Management</b>

📊 <b>Experimental Price Plans ({len(new_pricing)} total):</b>
"""
        
        if new_pricing:
            for plan in new_pricing[:6]:  # Show up to 6 plans
                status_icon = "🟢" if plan['is_active'] else "🔴"
                text += f"• {status_icon} <b>{plan['name']}</b>\n"
                text += f"  {plan['duration_days']} days, {plan['posts_per_day']} posts/day\n"
                text += f"  ${plan['final_price_usd']:.2f} ({plan['discount_percent']:.0f}% discount)\n"
                if plan['description']:
                    text += f"  <i>{plan['description'][:50]}...</i>\n"
                text += "\n"
        else:
            text += "No experimental pricing plans created yet.\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Add New Plan", callback_data="new_price_add"),
                InlineKeyboardButton(text="✏️ Edit Plan", callback_data="new_price_edit_list")
            ],
            [
                InlineKeyboardButton(text="📋 All Plans", callback_data="new_price_view_all"),
                InlineKeyboardButton(text="🗑️ Delete Plan", callback_data="new_price_delete_list")
            ],
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="admin_price_management")
            ]
        ])
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "New pricing loaded")
        
    except Exception as e:
        logger.error(f"Error managing new pricing: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading new pricing", show_alert=True)

# OFFERS HANDLERS  
@price_management_router.callback_query(F.data == "price_manage_offers")
async def manage_offers(callback_query: CallbackQuery, state: FSMContext):
    """Manage promotional offers"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        manager = get_price_manager()
        offers = await manager.get_all_offers()
        
        text = f"""
🎁 <b>Promotional Offers Management</b>

📊 <b>Current Offers ({len(offers)} total):</b>
"""
        
        if offers:
            for offer in offers[:6]:  # Show up to 6 offers
                status_icon = "🟢" if offer['is_active'] else "🔴"
                text += f"• {status_icon} <b>{offer['offer_name']}</b>\n"
                text += f"  {offer['duration_days']} days, {offer['discount_percent']:.0f}% off\n"
                text += f"  ${offer['offer_price']:.2f} (was ${offer['original_price']:.2f})\n"
                if offer['max_uses'] > 0:
                    text += f"  Uses: {offer['current_uses']}/{offer['max_uses']}\n"
                text += "\n"
        else:
            text += "No promotional offers created yet.\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Add Offer", callback_data="offer_add"),
                InlineKeyboardButton(text="✏️ Edit Offer", callback_data="offer_edit_list")
            ],
            [
                InlineKeyboardButton(text="📋 All Offers", callback_data="offer_view_all"),
                InlineKeyboardButton(text="🗑️ Delete Offer", callback_data="offer_delete_list")
            ],
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="admin_price_management")
            ]
        ])
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Offers loaded")
        
    except Exception as e:
        logger.error(f"Error managing offers: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading offers", show_alert=True)

# BUNDLES HANDLERS
@price_management_router.callback_query(F.data == "price_manage_bundles")
async def manage_bundles(callback_query: CallbackQuery, state: FSMContext):
    """Manage bundle packages"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        manager = get_price_manager()
        bundles = await manager.get_all_bundles()
        
        text = f"""
📦 <b>Bundle Packages Management</b>

📊 <b>Available Bundles ({len(bundles)} total):</b>
"""
        
        if bundles:
            for bundle in bundles[:6]:  # Show up to 6 bundles
                status_icon = "🟢" if bundle['is_active'] else "🔴"
                featured_icon = "⭐" if bundle['is_featured'] else ""
                text += f"• {status_icon}{featured_icon} <b>{bundle['bundle_name']}</b>\n"
                text += f"  {bundle['total_duration_days']} days, {bundle['total_posts']} posts\n"
                text += f"  ${bundle['bundle_price']:.2f} (save {bundle['savings_percent']:.0f}%)\n"
                text += f"  <i>{bundle['bundle_description'][:50]}...</i>\n\n"
        else:
            text += "No bundle packages created yet.\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Add Bundle", callback_data="bundle_add"),
                InlineKeyboardButton(text="✏️ Edit Bundle", callback_data="bundle_edit_list")
            ],
            [
                InlineKeyboardButton(text="📋 All Bundles", callback_data="bundle_view_all"),
                InlineKeyboardButton(text="🗑️ Delete Bundle", callback_data="bundle_delete_list")
            ],
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="admin_price_management")
            ]
        ])
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Bundles loaded")
        
    except Exception as e:
        logger.error(f"Error managing bundles: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading bundles", show_alert=True)

@price_management_router.callback_query(F.data == "price_add_new")
async def add_new_price_prompt(callback_query: CallbackQuery, state: FSMContext):
    """Prompt for new price tier creation"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    await state.set_state(PriceManagementStates.waiting_for_new_price_data)
    
    text = """
➕ <b>Add New Price Tier</b>

📝 <b>Enter price tier data in this format:</b>
<code>duration_days,posts_per_day,discount_percent</code>

📋 <b>Examples:</b>
• <code>5,1,7.5</code> (5 days, 1 post/day, 7.5% discount)
• <code>14,2,12.0</code> (14 days, 2 posts/day, 12% discount)
• <code>45,3,22.5</code> (45 days, 3 posts/day, 22.5% discount)

💡 <b>Notes:</b>
• Duration: 1-365 days
• Posts per day: 1-10 posts
• Discount: 0-50% discount
• Final price calculated automatically

🔄 <b>Formula:</b>
Base Cost = $1.00 × posts_per_day × duration_days
Final Price = Base Cost - (Base Cost × discount%)
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_price_management")]
    ])
    
    await safe_edit_message(
        callback_query.message,
        text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    await safe_callback_answer(callback_query, "Send new price tier data")

@price_management_router.message(PriceManagementStates.waiting_for_new_price_data)
async def process_new_price_data(message: Message, state: FSMContext):
    """Process new price tier creation"""
    user_id = message.from_user.id
    
    if user_id not in ADMIN_IDS:
        await message.answer("❌ Access denied")
        return
    
    try:
        data = message.text.strip()
        parts = data.split(',')
        
        if len(parts) != 3:
            await message.answer(
                "❌ <b>Invalid format!</b>\n\n"
                "Please use: <code>duration_days,posts_per_day,discount_percent</code>\n"
                "Example: <code>30,2,15.0</code>",
                parse_mode='HTML'
            )
            return
        
        duration_days = int(parts[0].strip())
        posts_per_day = int(parts[1].strip())
        discount_percent = float(parts[2].strip())
        
        # Validate ranges
        if not (1 <= duration_days <= 365):
            await message.answer("❌ Duration must be between 1-365 days")
            return
        
        if not (1 <= posts_per_day <= 10):
            await message.answer("❌ Posts per day must be between 1-10")
            return
        
        if not (0 <= discount_percent <= 50):
            await message.answer("❌ Discount must be between 0-50%")
            return
        
        # Create price tier
        manager = get_price_manager()
        success = await manager.create_price_tier(duration_days, posts_per_day, discount_percent, user_id)
        
        if success:
            # Get created tier for display
            tier = await manager.get_price_tier(duration_days)
            
            result_text = f"""
✅ <b>Price Tier Created Successfully!</b>

📊 <b>New Price Tier:</b>
• Duration: {duration_days} days
• Posts per day: {posts_per_day}
• Discount: {discount_percent}%
• Final Price: ${tier['final_price_usd']:.2f}

💰 <b>Calculation:</b>
• Base Cost: ${1.00 * posts_per_day * duration_days:.2f}
• Discount: ${1.00 * posts_per_day * duration_days * (discount_percent/100):.2f}
• Final Price: ${tier['final_price_usd']:.2f}

🎯 <b>This tier is now available for users!</b>
            """
        else:
            result_text = "❌ <b>Failed to create price tier</b>\n\nTier with this duration may already exist."
        
        await message.answer(result_text, parse_mode='HTML')
        
        # Return to price management
        await asyncio.sleep(2)
        
        # Create fake callback query to show price management
        class FakeCallbackQuery:
            def __init__(self, message, user_id):
                self.message = message
                self.from_user = type('User', (), {'id': user_id})()
        
        fake_callback = FakeCallbackQuery(message, user_id)
        await show_price_management(fake_callback, state)
        
    except ValueError:
        await message.answer(
            "❌ <b>Invalid data format!</b>\n\n"
            "Please ensure:\n"
            "• Duration and posts are whole numbers\n"
            "• Discount is a decimal number\n"
            "• Format: <code>duration,posts,discount</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error processing new price data: {e}")
        await message.answer("❌ Error creating price tier. Please try again.")
    
    await state.clear()

@price_management_router.callback_query(F.data == "price_edit_list")
async def show_edit_price_list(callback_query: CallbackQuery, state: FSMContext):
    """Show list of price tiers for editing"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        manager = get_price_manager()
        tiers = await manager.get_all_price_tiers()
        
        if not tiers:
            text = """
📝 <b>Edit Price Tiers</b>

❌ <b>No price tiers found.</b>

Create some price tiers first using "Add New Price" button.
            """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Back", callback_data="admin_price_management")]
            ])
        else:
            text = f"""
📝 <b>Edit Price Tiers ({len(tiers)} total)</b>

🎯 <b>Select a tier to edit:</b>
            """
            
            # Create buttons for each tier
            buttons = []
            for tier in tiers:
                status_icon = "🟢" if tier['is_active'] else "🔴"
                button_text = f"{status_icon} {tier['duration_days']} days - ${tier['final_price_usd']:.2f}"
                buttons.append([
                    InlineKeyboardButton(
                        text=button_text, 
                        callback_data=f"price_edit_{tier['duration_days']}"
                    )
                ])
            
            # Add navigation buttons
            buttons.append([
                InlineKeyboardButton(text="🔙 Back", callback_data="admin_price_management")
            ])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Select tier to edit")
        
    except Exception as e:
        logger.error(f"Error showing edit price list: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading price tiers", show_alert=True)

@price_management_router.callback_query(F.data.startswith("price_edit_"))
async def edit_price_tier_details(callback_query: CallbackQuery, state: FSMContext):
    """Show price tier edit interface"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        duration_days = int(callback_query.data.split("_")[-1])
        manager = get_price_manager()
        tier = await manager.get_price_tier(duration_days)
        
        if not tier:
            await safe_callback_answer(callback_query, "❌ Price tier not found", show_alert=True)
            return
        
        text = f"""
✏️ <b>Edit Price Tier: {duration_days} Days</b>

📊 <b>Current Settings:</b>
• Duration: {tier['duration_days']} days
• Posts per day: {tier['posts_per_day']}
• Discount: {tier['discount_percent']}%
• Final Price: ${tier['final_price_usd']:.2f}
• Status: {'🟢 Active' if tier['is_active'] else '🔴 Inactive'}
• Created: {tier['created_at'][:16]}
• Updated: {tier['updated_at'][:16]}

🔧 <b>Available Actions:</b>
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Edit Details", callback_data=f"price_edit_details_{duration_days}"),
                InlineKeyboardButton(text="🔄 Toggle Status", callback_data=f"price_toggle_{duration_days}")
            ],
            [
                InlineKeyboardButton(text="📊 View Analytics", callback_data=f"price_analytics_{duration_days}"),
                InlineKeyboardButton(text="📈 Price History", callback_data=f"price_history_{duration_days}")
            ],
            [
                InlineKeyboardButton(text="🗑️ Delete Tier", callback_data=f"price_delete_{duration_days}"),
                InlineKeyboardButton(text="📋 Duplicate", callback_data=f"price_duplicate_{duration_days}")
            ],
            [
                InlineKeyboardButton(text="🔙 Back to List", callback_data="price_edit_list")
            ]
        ])
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Price tier details loaded")
        
    except Exception as e:
        logger.error(f"Error showing price tier details: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading tier details", show_alert=True)

@price_management_router.callback_query(F.data.startswith("price_edit_details_"))
async def edit_price_tier_prompt(callback_query: CallbackQuery, state: FSMContext):
    """Prompt for editing price tier details"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        duration_days = int(callback_query.data.split("_")[-1])
        manager = get_price_manager()
        tier = await manager.get_price_tier(duration_days)
        
        if not tier:
            await safe_callback_answer(callback_query, "❌ Price tier not found", show_alert=True)
            return
        
        await state.set_state(PriceManagementStates.waiting_for_edit_price_data)
        await state.update_data(duration_days=duration_days)
        
        text = f"""
✏️ <b>Edit Price Tier: {duration_days} Days</b>

📊 <b>Current Values:</b>
• Posts per day: {tier['posts_per_day']}
• Discount: {tier['discount_percent']}%
• Final Price: ${tier['final_price_usd']:.2f}

📝 <b>Enter new values in format:</b>
<code>posts_per_day,discount_percent</code>

📋 <b>Examples:</b>
• <code>3,20.0</code> (3 posts/day, 20% discount)
• <code>1,5.5</code> (1 post/day, 5.5% discount)
• <code>4,25.0</code> (4 posts/day, 25% discount)

💡 <b>Leave field empty to keep current value:</b>
• <code>,15.0</code> (keep current posts/day, set 15% discount)
• <code>2,</code> (set 2 posts/day, keep current discount)
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data=f"price_edit_{duration_days}")]
        ])
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Send new tier values")
        
    except Exception as e:
        logger.error(f"Error showing edit prompt: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading edit prompt", show_alert=True)

@price_management_router.message(PriceManagementStates.waiting_for_edit_price_data)
async def process_edit_price_data(message: Message, state: FSMContext):
    """Process price tier editing"""
    user_id = message.from_user.id
    
    if user_id not in ADMIN_IDS:
        await message.answer("❌ Access denied")
        return
    
    try:
        data = await state.get_data()
        duration_days = data.get('duration_days')
        
        if not duration_days:
            await message.answer("❌ Error: No duration data found")
            await state.clear()
            return
        
        edit_data = message.text.strip()
        parts = edit_data.split(',')
        
        if len(parts) != 2:
            await message.answer(
                "❌ <b>Invalid format!</b>\n\n"
                "Please use: <code>posts_per_day,discount_percent</code>\n"
                "Example: <code>3,20.0</code>",
                parse_mode='HTML'
            )
            return
        
        # Parse values (empty means keep current)
        posts_per_day = None
        discount_percent = None
        
        if parts[0].strip():
            posts_per_day = int(parts[0].strip())
            if not (1 <= posts_per_day <= 10):
                await message.answer("❌ Posts per day must be between 1-10")
                return
        
        if parts[1].strip():
            discount_percent = float(parts[1].strip())
            if not (0 <= discount_percent <= 50):
                await message.answer("❌ Discount must be between 0-50%")
                return
        
        # Update price tier
        manager = get_price_manager()
        success = await manager.update_price_tier(duration_days, posts_per_day, discount_percent, user_id)
        
        if success:
            # Get updated tier for display
            tier = await manager.get_price_tier(duration_days)
            
            result_text = f"""
✅ <b>Price Tier Updated Successfully!</b>

📊 <b>Updated Price Tier:</b>
• Duration: {duration_days} days
• Posts per day: {tier['posts_per_day']}
• Discount: {tier['discount_percent']}%
• Final Price: ${tier['final_price_usd']:.2f}

🕒 <b>Last Updated:</b> {tier['updated_at'][:16]}

🎯 <b>Changes are live immediately!</b>
            """
        else:
            result_text = "❌ <b>Failed to update price tier</b>\n\nPlease try again or contact support."
        
        await message.answer(result_text, parse_mode='HTML')
        
        # Return to tier details
        await asyncio.sleep(2)
        
        # Create fake callback query to show tier details
        class FakeCallbackQuery:
            def __init__(self, message, user_id, data):
                self.message = message
                self.from_user = type('User', (), {'id': user_id})()
                self.data = data
        
        fake_callback = FakeCallbackQuery(message, user_id, f"price_edit_{duration_days}")
        await edit_price_tier_details(fake_callback, state)
        
    except ValueError:
        await message.answer(
            "❌ <b>Invalid data format!</b>\n\n"
            "Please ensure:\n"
            "• Posts per day is a whole number\n"
            "• Discount is a decimal number\n"
            "• Format: <code>posts,discount</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error processing edit price data: {e}")
        await message.answer("❌ Error updating price tier. Please try again.")
    
    await state.clear()

@price_management_router.callback_query(F.data.startswith("price_toggle_"))
async def toggle_price_tier_status(callback_query: CallbackQuery, state: FSMContext):
    """Toggle price tier active status"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        duration_days = int(callback_query.data.split("_")[-1])
        manager = get_price_manager()
        
        success = await manager.toggle_price_tier_status(duration_days, user_id)
        
        if success:
            tier = await manager.get_price_tier(duration_days)
            status = "activated" if tier['is_active'] else "deactivated"
            await safe_callback_answer(callback_query, f"✅ Price tier {status}")
            
            # Refresh tier details
            await edit_price_tier_details(callback_query, state)
        else:
            await safe_callback_answer(callback_query, "❌ Failed to toggle status", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error toggling price tier status: {e}")
        await safe_callback_answer(callback_query, "❌ Error toggling status", show_alert=True)

@price_management_router.callback_query(F.data.startswith("price_delete_"))
async def delete_price_tier_confirm(callback_query: CallbackQuery, state: FSMContext):
    """Confirm price tier deletion"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        duration_days = int(callback_query.data.split("_")[-1])
        manager = get_price_manager()
        tier = await manager.get_price_tier(duration_days)
        
        if not tier:
            await safe_callback_answer(callback_query, "❌ Price tier not found", show_alert=True)
            return
        
        text = f"""
🗑️ <b>Delete Price Tier</b>

⚠️ <b>Are you sure you want to delete this price tier?</b>

📊 <b>Tier Details:</b>
• Duration: {tier['duration_days']} days
• Posts per day: {tier['posts_per_day']}
• Final Price: ${tier['final_price_usd']:.2f}
• Status: {'🟢 Active' if tier['is_active'] else '🔴 Inactive'}

❌ <b>This action cannot be undone!</b>
💡 <b>Consider deactivating instead of deleting.</b>
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes, Delete", callback_data=f"price_delete_confirm_{duration_days}"),
                InlineKeyboardButton(text="❌ Cancel", callback_data=f"price_edit_{duration_days}")
            ]
        ])
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "Confirm deletion")
        
    except Exception as e:
        logger.error(f"Error showing delete confirmation: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading confirmation", show_alert=True)

@price_management_router.callback_query(F.data.startswith("price_delete_confirm_"))
async def delete_price_tier_execute(callback_query: CallbackQuery, state: FSMContext):
    """Execute price tier deletion"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        duration_days = int(callback_query.data.split("_")[-1])
        manager = get_price_manager()
        
        success = await manager.delete_price_tier(duration_days, user_id)
        
        if success:
            await safe_callback_answer(callback_query, "✅ Price tier deleted successfully")
            
            # Return to edit list
            await show_edit_price_list(callback_query, state)
        else:
            await safe_callback_answer(callback_query, "❌ Failed to delete price tier", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error deleting price tier: {e}")
        await safe_callback_answer(callback_query, "❌ Error deleting tier", show_alert=True)

@price_management_router.callback_query(F.data == "price_view_all")
async def view_all_price_tiers(callback_query: CallbackQuery, state: FSMContext):
    """View all price tiers in detail"""
    user_id = callback_query.from_user.id
    
    if user_id not in ADMIN_IDS:
        await safe_callback_answer(callback_query, "❌ Access denied", show_alert=True)
        return
    
    try:
        manager = get_price_manager()
        tiers = await manager.get_all_price_tiers()
        
        if not tiers:
            text = "📋 <b>All Price Tiers</b>\n\n❌ No price tiers found."
        else:
            text = f"📋 <b>All Price Tiers ({len(tiers)} total)</b>\n\n"
            
            for i, tier in enumerate(tiers, 1):
                status_icon = "🟢" if tier['is_active'] else "🔴"
                text += f"{i}. {status_icon} <b>{tier['duration_days']} Days</b>\n"
                text += f"   • Posts/Day: {tier['posts_per_day']}\n"
                text += f"   • Discount: {tier['discount_percent']:.1f}%\n"
                text += f"   • Price: ${tier['final_price_usd']:.2f}\n"
                text += f"   • Updated: {tier['updated_at'][:10]}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Edit Tiers", callback_data="price_edit_list"),
                InlineKeyboardButton(text="📊 Analytics", callback_data="price_analytics")
            ],
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="admin_price_management")
            ]
        ])
        
        await safe_edit_message(
            callback_query.message,
            text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        await safe_callback_answer(callback_query, "All price tiers loaded")
        
    except Exception as e:
        logger.error(f"Error viewing all price tiers: {e}")
        await safe_callback_answer(callback_query, "❌ Error loading price tiers", show_alert=True)

def setup_price_management_handlers(dp):
    """Setup price management handlers"""
    dp.include_router(price_management_router)
    logger.info("✅ Price management handlers registered")