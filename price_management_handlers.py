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
💰 <b>Price Management System</b>

📊 <b>Overview:</b>
• Total Price Tiers: {summary.get('total_tiers', 0)}
• Active Tiers: {summary.get('active_tiers', 0)}
• Inactive Tiers: {summary.get('inactive_tiers', 0)}
• Base Price: ${summary.get('base_price_usd', 1.00):.2f}/post/day

💸 <b>Price Range:</b>
• Minimum: ${summary.get('price_range', {}).get('min_price', 0):.2f}
• Maximum: ${summary.get('price_range', {}).get('max_price', 0):.2f}

📈 <b>Analytics:</b>
• Total Revenue: ${summary.get('total_revenue', 0):.2f}
• Total Usage: {summary.get('total_usage', 0)} campaigns

🎯 <b>Current Price Tiers:</b>
"""
        
        # Show first 5 tiers
        for tier in tiers[:5]:
            status_icon = "🟢" if tier['is_active'] else "🔴"
            text += f"• {status_icon} <b>{tier['duration_days']} days</b> - {tier['posts_per_day']} posts/day\n"
            text += f"  ${tier['final_price_usd']:.2f} ({tier['discount_percent']:.0f}% discount)\n"
        
        if len(tiers) > 5:
            text += f"... and {len(tiers) - 5} more tiers\n"
        
        # Create management keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Add New Price", callback_data="price_add_new"),
                InlineKeyboardButton(text="✏️ Edit Prices", callback_data="price_edit_list")
            ],
            [
                InlineKeyboardButton(text="📋 All Price Tiers", callback_data="price_view_all"),
                InlineKeyboardButton(text="📊 Price Analytics", callback_data="price_analytics")
            ],
            [
                InlineKeyboardButton(text="📈 Price History", callback_data="price_history"),
                InlineKeyboardButton(text="⚡ Bulk Operations", callback_data="price_bulk_ops")
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