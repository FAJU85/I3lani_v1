#!/usr/bin/env python3
"""
Pricing Admin Handlers for I3lani Bot
Complete admin interface for pricing management
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from advanced_pricing_management import pricing_manager, PricingManagementStates
from config import ADMIN_IDS
from database import db

logger = logging.getLogger(__name__)

async def show_pricing_management_menu(callback_query: CallbackQuery, state: FSMContext):
    """Show main pricing management menu"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied", show_alert=True)
        return
    
    # Get current pricing statistics
    tiers = await pricing_manager.get_all_pricing_tiers()
    analytics = await pricing_manager.get_pricing_analytics()
    
    text = f"""<b>💰 Advanced Pricing Management</b>

<b>📊 Current Status:</b>
• Active Pricing Tiers: {len(tiers)}
• Monthly Changes: {analytics.get('monthly_changes', 0)}
• Categories: Current, Experimental, Offers, Bundles

<b>🎯 Quick Actions:</b>
Manage all aspects of your pricing structure with full control over tiers, discounts, and promotional offers.
"""
    
    keyboard = [
        [
            InlineKeyboardButton(text="📋 View All Tiers", callback_data="pricing_view_all"),
            InlineKeyboardButton(text="➕ Add New Tier", callback_data="pricing_add_tier")
        ],
        [
            InlineKeyboardButton(text="✏️ Edit Existing Tier", callback_data="pricing_edit_tier"),
            InlineKeyboardButton(text="🗑️ Delete Tier", callback_data="pricing_delete_tier")
        ],
        [
            InlineKeyboardButton(text="🎁 Manage Offers", callback_data="pricing_manage_offers"),
            InlineKeyboardButton(text="📦 Manage Bundles", callback_data="pricing_manage_bundles")
        ],
        [
            InlineKeyboardButton(text="📊 Analytics", callback_data="pricing_analytics"),
            InlineKeyboardButton(text="🔄 Bulk Update", callback_data="pricing_bulk_update")
        ],
        [
            InlineKeyboardButton(text="🔧 Advanced Settings", callback_data="pricing_advanced"),
            InlineKeyboardButton(text="📜 Price History", callback_data="pricing_history")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
        ]
    ]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )

async def show_all_pricing_tiers(callback_query: CallbackQuery, state: FSMContext):
    """Show all pricing tiers"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied", show_alert=True)
        return
    
    tiers = await pricing_manager.get_all_pricing_tiers(active_only=False)
    text = pricing_manager.format_pricing_display(tiers)
    
    # Add summary statistics
    active_tiers = [t for t in tiers if t['is_active']]
    total_revenue = sum(t.get('revenue_generated', 0) for t in tiers)
    
    text += f"\n<b>📈 Summary:</b>\n"
    text += f"• Total Tiers: {len(tiers)}\n"
    text += f"• Active Tiers: {len(active_tiers)}\n"
    text += f"• Categories: {len(set(t['tier_category'] for t in tiers))}\n"
    
    keyboard = [
        [
            InlineKeyboardButton(text="🔄 Refresh", callback_data="pricing_view_all"),
            InlineKeyboardButton(text="📊 Filter by Category", callback_data="pricing_filter_category")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back to Pricing", callback_data="pricing_management")
        ]
    ]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )

async def add_new_pricing_tier(callback_query: CallbackQuery, state: FSMContext):
    """Start adding new pricing tier"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied", show_alert=True)
        return
    
    text = """<b>➕ Add New Pricing Tier</b>

Please provide the tier details in the following format:

<code>Tier Name
Duration (days)
Posts per day
Base price (USD)
Discount percentage (optional)
Category (current/experimental/custom)
Description (optional)</code>

<b>Example:</b>
<code>Premium Week
7
3
2.50
10
current
Weekly premium advertising package</code>
"""
    
    await state.set_state(PricingManagementStates.waiting_for_tier_details)
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="pricing_management")]
        ]),
        parse_mode='HTML'
    )

async def process_new_tier_details(message: Message, state: FSMContext):
    """Process new tier details"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Access denied")
        return
    
    try:
        lines = message.text.strip().split('\n')
        if len(lines) < 4:
            await message.answer("❌ Invalid format. Please provide at least: Name, Duration, Posts per day, Base price")
            return
        
        tier_data = {
            'name': lines[0].strip(),
            'duration_days': int(lines[1].strip()),
            'posts_per_day': int(lines[2].strip()),
            'base_price_usd': float(lines[3].strip()),
            'discount_percent': float(lines[4].strip()) if len(lines) > 4 and lines[4].strip() else 0.0,
            'category': lines[5].strip() if len(lines) > 5 and lines[5].strip() else 'current',
            'description': lines[6].strip() if len(lines) > 6 else '',
            'created_by': message.from_user.id
        }
        
        # Validate data
        if tier_data['duration_days'] < 1 or tier_data['duration_days'] > 365:
            await message.answer("❌ Duration must be between 1 and 365 days")
            return
        
        if tier_data['posts_per_day'] < 1 or tier_data['posts_per_day'] > 10:
            await message.answer("❌ Posts per day must be between 1 and 10")
            return
        
        if tier_data['base_price_usd'] < 0.1:
            await message.answer("❌ Base price must be at least $0.10")
            return
        
        # Create tier
        success = await pricing_manager.create_pricing_tier(tier_data)
        
        if success:
            final_price = tier_data['base_price_usd'] * (1 - tier_data['discount_percent'] / 100)
            text = f"""✅ <b>Pricing Tier Created Successfully</b>

<b>Tier Details:</b>
• Name: {tier_data['name']}
• Duration: {tier_data['duration_days']} days
• Posts/Day: {tier_data['posts_per_day']}
• Base Price: ${tier_data['base_price_usd']:.2f}
• Discount: {tier_data['discount_percent']}%
• Final Price: ${final_price:.2f}
• Category: {tier_data['category']}
"""
            
            keyboard = [
                [
                    InlineKeyboardButton(text="➕ Add Another", callback_data="pricing_add_tier"),
                    InlineKeyboardButton(text="📋 View All Tiers", callback_data="pricing_view_all")
                ],
                [
                    InlineKeyboardButton(text="⬅️ Back to Pricing", callback_data="pricing_management")
                ]
            ]
            
            await message.answer(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode='HTML'
            )
        else:
            await message.answer("❌ Failed to create pricing tier. Please try again.")
        
    except ValueError as e:
        await message.answer(f"❌ Invalid number format: {e}")
    except Exception as e:
        logger.error(f"Error processing tier details: {e}")
        await message.answer("❌ Error processing tier details. Please check the format and try again.")
    
    await state.clear()

async def edit_pricing_tier(callback_query: CallbackQuery, state: FSMContext):
    """Show tiers for editing"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied", show_alert=True)
        return
    
    tiers = await pricing_manager.get_all_pricing_tiers(active_only=False)
    
    if not tiers:
        await callback_query.answer("No pricing tiers found", show_alert=True)
        return
    
    text = "<b>✏️ Select Tier to Edit</b>\n\n"
    
    keyboard = []
    for tier in tiers[:10]:  # Show first 10 tiers
        status = "✅" if tier['is_active'] else "❌"
        button_text = f"{status} {tier['tier_name']} ({tier['duration_days']}d - ${tier['final_price_usd']:.2f})"
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"edit_tier_{tier['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Back to Pricing", callback_data="pricing_management")])
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )

async def show_tier_edit_options(callback_query: CallbackQuery, state: FSMContext):
    """Show edit options for selected tier"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied", show_alert=True)
        return
    
    tier_id = int(callback_query.data.split('_')[2])
    
    # Get tier details
    tiers = await pricing_manager.get_all_pricing_tiers(active_only=False)
    tier = next((t for t in tiers if t['id'] == tier_id), None)
    
    if not tier:
        await callback_query.answer("Tier not found", show_alert=True)
        return
    
    text = f"""<b>✏️ Edit Tier: {tier['tier_name']}</b>

<b>Current Details:</b>
• Duration: {tier['duration_days']} days
• Posts/Day: {tier['posts_per_day']}
• Base Price: ${tier['base_price_usd']:.2f}
• Discount: {tier['discount_percent']}%
• Final Price: ${tier['final_price_usd']:.2f}
• Category: {tier['tier_category']}
• Status: {'Active' if tier['is_active'] else 'Inactive'}

<b>What would you like to edit?</b>
"""
    
    keyboard = [
        [
            InlineKeyboardButton(text="💰 Edit Price", callback_data=f"edit_price_{tier_id}"),
            InlineKeyboardButton(text="📅 Edit Duration", callback_data=f"edit_duration_{tier_id}")
        ],
        [
            InlineKeyboardButton(text="📊 Edit Posts/Day", callback_data=f"edit_posts_{tier_id}"),
            InlineKeyboardButton(text="🎯 Edit Discount", callback_data=f"edit_discount_{tier_id}")
        ],
        [
            InlineKeyboardButton(text="📝 Edit Name", callback_data=f"edit_name_{tier_id}"),
            InlineKeyboardButton(text="📂 Edit Category", callback_data=f"edit_category_{tier_id}")
        ],
        [
            InlineKeyboardButton(text="🔄 Toggle Status", callback_data=f"toggle_status_{tier_id}"),
            InlineKeyboardButton(text="📋 Full Edit", callback_data=f"full_edit_{tier_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back to Tiers", callback_data="pricing_edit_tier")
        ]
    ]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )

async def show_pricing_analytics(callback_query: CallbackQuery, state: FSMContext):
    """Show pricing analytics"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied", show_alert=True)
        return
    
    analytics = await pricing_manager.get_pricing_analytics()
    
    text = f"""<b>📊 Pricing Analytics</b>

<b>🏆 Most Popular Tiers:</b>
"""
    
    if analytics.get('popular_tiers'):
        for tier_name, selections, revenue in analytics['popular_tiers']:
            text += f"• {tier_name}: {selections or 0} selections, ${revenue or 0:.2f} revenue\n"
    else:
        text += "No usage data available yet.\n"
    
    text += f"""
<b>💰 Revenue by Category:</b>
"""
    
    if analytics.get('revenue_by_category'):
        for category, revenue in analytics['revenue_by_category']:
            text += f"• {category.title()}: ${revenue:.2f}\n"
    else:
        text += "No revenue data available yet.\n"
    
    text += f"""
<b>📈 Recent Activity:</b>
• Pricing Changes (30 days): {analytics.get('monthly_changes', 0)}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(text="🔄 Refresh", callback_data="pricing_analytics"),
            InlineKeyboardButton(text="📊 Detailed Report", callback_data="pricing_detailed_analytics")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back to Pricing", callback_data="pricing_management")
        ]
    ]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )

async def delete_pricing_tier(callback_query: CallbackQuery, state: FSMContext):
    """Show tiers for deletion"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied", show_alert=True)
        return
    
    tiers = await pricing_manager.get_all_pricing_tiers(active_only=False)
    
    if not tiers:
        await callback_query.answer("No pricing tiers found", show_alert=True)
        return
    
    text = "<b>🗑️ Select Tier to Delete</b>\n\n⚠️ <b>Warning:</b> This will deactivate the tier (soft delete).\n\n"
    
    keyboard = []
    for tier in tiers[:10]:  # Show first 10 tiers
        status = "✅" if tier['is_active'] else "❌"
        button_text = f"{status} {tier['tier_name']} ({tier['duration_days']}d - ${tier['final_price_usd']:.2f})"
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"delete_tier_{tier['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Back to Pricing", callback_data="pricing_management")])
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )

async def confirm_tier_deletion(callback_query: CallbackQuery, state: FSMContext):
    """Confirm tier deletion"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied", show_alert=True)
        return
    
    tier_id = int(callback_query.data.split('_')[2])
    
    # Get tier details
    tiers = await pricing_manager.get_all_pricing_tiers(active_only=False)
    tier = next((t for t in tiers if t['id'] == tier_id), None)
    
    if not tier:
        await callback_query.answer("Tier not found", show_alert=True)
        return
    
    text = f"""<b>🗑️ Confirm Deletion</b>

<b>Are you sure you want to delete this tier?</b>

<b>Tier Details:</b>
• Name: {tier['tier_name']}
• Duration: {tier['duration_days']} days
• Price: ${tier['final_price_usd']:.2f}

⚠️ <b>Note:</b> This will deactivate the tier. It can be reactivated later.
"""
    
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Confirm Delete", callback_data=f"confirm_delete_{tier_id}"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="pricing_delete_tier")
        ]
    ]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )

async def execute_tier_deletion(callback_query: CallbackQuery, state: FSMContext):
    """Execute tier deletion"""
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("Access denied", show_alert=True)
        return
    
    tier_id = int(callback_query.data.split('_')[2])
    
    success = await pricing_manager.delete_pricing_tier(tier_id, callback_query.from_user.id)
    
    if success:
        text = "✅ <b>Tier Deleted Successfully</b>\n\nThe pricing tier has been deactivated."
        keyboard = [
            [
                InlineKeyboardButton(text="📋 View All Tiers", callback_data="pricing_view_all"),
                InlineKeyboardButton(text="⬅️ Back to Pricing", callback_data="pricing_management")
            ]
        ]
    else:
        text = "❌ <b>Deletion Failed</b>\n\nThere was an error deleting the tier. Please try again."
        keyboard = [
            [InlineKeyboardButton(text="🔄 Try Again", callback_data="pricing_delete_tier")]
        ]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )

# Setup function for handlers
def setup_pricing_admin_handlers(dp):
    """Setup pricing admin handlers"""
    
    # Register all handlers
    dp.callback_query.register(show_pricing_management_menu, lambda c: c.data == "pricing_management")
    dp.callback_query.register(show_all_pricing_tiers, lambda c: c.data == "pricing_view_all")
    dp.callback_query.register(add_new_pricing_tier, lambda c: c.data == "pricing_add_tier")
    dp.callback_query.register(edit_pricing_tier, lambda c: c.data == "pricing_edit_tier")
    dp.callback_query.register(show_tier_edit_options, lambda c: c.data.startswith("edit_tier_"))
    dp.callback_query.register(show_pricing_analytics, lambda c: c.data == "pricing_analytics")
    dp.callback_query.register(delete_pricing_tier, lambda c: c.data == "pricing_delete_tier")
    dp.callback_query.register(confirm_tier_deletion, lambda c: c.data.startswith("delete_tier_"))
    dp.callback_query.register(execute_tier_deletion, lambda c: c.data.startswith("confirm_delete_"))
    
    # Message handlers
    dp.message.register(process_new_tier_details, PricingManagementStates.waiting_for_tier_details)
    
    logger.info("✅ Pricing admin handlers registered")