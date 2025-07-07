"""
Complete Admin System for I3lani Bot
Full bot control, pricing, channels, subscriptions, and publishing schedules
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from datetime import datetime, timedelta
import json
import os

from config import ADMIN_IDS, CHANNELS
from database import db

logger = logging.getLogger(__name__)

class AdminStates(StatesGroup):
    # Main menu states
    main_menu = State()
    
    # Channel management
    channel_management = State()
    add_channel = State()
    edit_channel = State()
    remove_channel = State()
    
    # Subscription management
    subscription_management = State()
    create_subscription = State()
    edit_subscription = State()
    remove_subscription = State()
    
    # Pricing management
    pricing_management = State()
    set_pricing = State()
    
    # Publishing schedules
    publishing_schedules = State()
    create_schedule = State()
    edit_schedule = State()
    
    # Bot control
    bot_control = State()
    broadcast_message = State()
    
    # User management
    user_management = State()
    
    # Statistics
    statistics = State()

router = Router()

class AdminSystem:
    def __init__(self):
        self.subscription_packages = {
            'starter': {
                'name': 'Starter Package',
                'price_usd': 10.0,
                'duration_days': 30,
                'posts_per_day': 1,
                'channels_included': 1
            },
            'professional': {
                'name': 'Professional Package',
                'price_usd': 25.0,
                'duration_days': 30,
                'posts_per_day': 3,
                'channels_included': 2
            },
            'enterprise': {
                'name': 'Enterprise Package',
                'price_usd': 50.0,
                'duration_days': 30,
                'posts_per_day': 5,
                'channels_included': 3
            }
        }
        
        self.channels = {
            'i3lani_main': {
                'name': 'I3lani Main Channel',
                'telegram_id': '@i3lani',
                'url': 'https://t.me/i3lani',
                'category': 'General',
                'subscribers': 10000,
                'active': True
            },
            'i3lani_tech': {
                'name': 'I3lani Tech',
                'telegram_id': '@i3lani_tech',
                'url': 'https://t.me/i3lani_tech',
                'category': 'Technology',
                'subscribers': 5000,
                'active': True
            },
            'i3lani_business': {
                'name': 'I3lani Business',
                'telegram_id': '@i3lani_business',
                'url': 'https://t.me/i3lani_business',
                'category': 'Business',
                'subscribers': 7500,
                'active': True
            }
        }
        
        self.publishing_schedules = {
            'morning': {'time': '09:00', 'active': True},
            'afternoon': {'time': '14:00', 'active': True},
            'evening': {'time': '19:00', 'active': True}
        }

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in ADMIN_IDS

    def create_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Create main admin menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(text="📺 Channel Management", callback_data="admin_channels"),
                InlineKeyboardButton(text="📦 Subscription Management", callback_data="admin_subscriptions")
            ],
            [
                InlineKeyboardButton(text="💰 Pricing Management", callback_data="admin_pricing"),
                InlineKeyboardButton(text="⏰ Publishing Schedules", callback_data="admin_schedules")
            ],
            [
                InlineKeyboardButton(text="🤖 Bot Control", callback_data="admin_bot_control"),
                InlineKeyboardButton(text="👥 User Management", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton(text="📊 Statistics", callback_data="admin_statistics"),
                InlineKeyboardButton(text="🔄 Refresh Data", callback_data="admin_refresh")
            ],
            [
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def show_main_menu(self, message_or_query, edit: bool = False):
        """Show main admin menu"""
        text = f"""
🔧 **I3lani Bot Admin Panel**

**System Status:** ✅ Online
**Total Users:** {await self.get_total_users()}
**Active Channels:** {len([c for c in self.channels.values() if c['active']])}
**Revenue Today:** ${await self.get_daily_revenue():.2f}

**Quick Actions:**
• Manage channels and subscriptions
• Control pricing and schedules
• Monitor user activity
• View detailed statistics
• Send broadcast messages

Select an option to continue:
        """.strip()
        
        keyboard = self.create_main_menu_keyboard()
        
        if edit and hasattr(message_or_query, 'message'):
            await message_or_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
        else:
            await message_or_query.answer(text, reply_markup=keyboard, parse_mode='Markdown')

    async def show_channel_management(self, callback_query: CallbackQuery):
        """Show channel management interface"""
        text = f"""
📺 Channel Management

Active Channels: {len([c for c in self.channels.values() if c['active']])}

Channels:
        """.strip()
        
        for channel_id, channel in self.channels.items():
            status = "✅" if channel['active'] else "❌"
            text += f"\n{status} {channel['name']}"
            text += f"\n   • ID: {channel['telegram_id']}"
            text += f"\n   • Subscribers: {channel['subscribers']:,}"
            text += f"\n   • Category: {channel['category']}"
        
        keyboard = [
            [
                InlineKeyboardButton(text="➕ Add Channel", callback_data="admin_add_channel"),
                InlineKeyboardButton(text="✏️ Edit Channel", callback_data="admin_edit_channel")
            ],
            [
                InlineKeyboardButton(text="🗑️ Remove Channel", callback_data="admin_remove_channel"),
                InlineKeyboardButton(text="📊 Channel Stats", callback_data="admin_channel_stats")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        try:
            await callback_query.message.edit_text(
                text, 
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
        except Exception as e:
            logger.error(f"Channel management display error: {e}")
            simple_text = f"Channel Management\n\nActive Channels: {len([c for c in self.channels.values() if c['active']])}\n\nNo channels available."
            await callback_query.message.edit_text(
                simple_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )

    async def show_subscription_management(self, callback_query: CallbackQuery):
        """Show subscription management interface"""
        text = f"""
📦 **Subscription Management**

**Available Packages:** {len(self.subscription_packages)}

**Current Packages:**
        """.strip()
        
        for package_id, package in self.subscription_packages.items():
            text += f"\n🎯 **{package['name']}**"
            text += f"\n   • Price: ${package['price_usd']}"
            text += f"\n   • Duration: {package['duration_days']} days"
            text += f"\n   • Posts/Day: {package['posts_per_day']}"
            text += f"\n   • Channels: {package['channels_included']}"
        
        keyboard = [
            [
                InlineKeyboardButton(text="➕ Create Package", callback_data="admin_create_subscription"),
                InlineKeyboardButton(text="✏️ Edit Package", callback_data="admin_edit_subscription")
            ],
            [
                InlineKeyboardButton(text="🗑️ Remove Package", callback_data="admin_remove_subscription"),
                InlineKeyboardButton(text="📊 Package Stats", callback_data="admin_subscription_stats")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        await callback_query.message.edit_text(
            text, 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )

    async def show_pricing_management(self, callback_query: CallbackQuery):
        """Show pricing management interface"""
        text = f"""
💰 **Pricing Management**

**Current Pricing:**

**Starter Package:** ${self.subscription_packages['starter']['price_usd']}
**Professional Package:** ${self.subscription_packages['professional']['price_usd']}
**Enterprise Package:** ${self.subscription_packages['enterprise']['price_usd']}

**Payment Methods:**
• TON Cryptocurrency ✅
• Telegram Stars ✅

**Exchange Rates:**
• 1 USD = 100 Telegram Stars
• TON rate: Live market rate
        """.strip()
        
        keyboard = [
            [
                InlineKeyboardButton(text="💵 Update Starter Price", callback_data="admin_price_starter"),
                InlineKeyboardButton(text="💸 Update Pro Price", callback_data="admin_price_professional")
            ],
            [
                InlineKeyboardButton(text="💰 Update Enterprise Price", callback_data="admin_price_enterprise"),
                InlineKeyboardButton(text="🔄 Refresh Rates", callback_data="admin_refresh_rates")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        await callback_query.message.edit_text(
            text, 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )

    async def show_publishing_schedules(self, callback_query: CallbackQuery):
        """Show publishing schedules management"""
        text = f"""
⏰ **Publishing Schedules**

**Current Schedule:**
        """.strip()
        
        for schedule_id, schedule in self.publishing_schedules.items():
            status = "✅" if schedule['active'] else "❌"
            text += f"\n{status} **{schedule_id.title()}:** {schedule['time']}"
        
        text += f"""

**Schedule Settings:**
• Auto-publish: ✅ Enabled
• Timezone: UTC
• Retry failed posts: ✅ Enabled
• Max posts per hour: 10
        """.strip()
        
        keyboard = [
            [
                InlineKeyboardButton(text="➕ Add Schedule", callback_data="admin_create_schedule"),
                InlineKeyboardButton(text="✏️ Edit Schedule", callback_data="admin_edit_schedule")
            ],
            [
                InlineKeyboardButton(text="🗑️ Remove Schedule", callback_data="admin_remove_schedule"),
                InlineKeyboardButton(text="⏸️ Pause All", callback_data="admin_pause_schedules")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        await callback_query.message.edit_text(
            text, 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )

    async def show_bot_control(self, callback_query: CallbackQuery):
        """Show bot control interface"""
        text = f"""
🤖 **Bot Control Panel**

**Bot Status:** ✅ Online and Running
**Uptime:** {await self.get_bot_uptime()}
**Memory Usage:** {await self.get_memory_usage()}
**Active Sessions:** {await self.get_active_sessions()}

**Bot Features:**
• Multi-language support (EN/AR/RU) ✅
• Payment processing (TON/Stars) ✅
• Auto-publishing ✅
• Referral system ✅
• Debug system ✅

**Control Options:**
        """.strip()
        
        keyboard = [
            [
                InlineKeyboardButton(text="📢 Broadcast Message", callback_data="admin_broadcast"),
                InlineKeyboardButton(text="🔄 Restart Bot", callback_data="admin_restart_bot")
            ],
            [
                InlineKeyboardButton(text="⏸️ Pause Bot", callback_data="admin_pause_bot"),
                InlineKeyboardButton(text="▶️ Resume Bot", callback_data="admin_resume_bot")
            ],
            [
                InlineKeyboardButton(text="🔧 Maintenance Mode", callback_data="admin_maintenance"),
                InlineKeyboardButton(text="📊 System Logs", callback_data="admin_system_logs")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        await callback_query.message.edit_text(
            text, 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )

    async def show_user_management(self, callback_query: CallbackQuery):
        """Show user management interface"""
        total_users = await self.get_total_users()
        active_users = await self.get_active_users()
        
        text = f"""
👥 **User Management**

**User Statistics:**
• Total Users: {total_users}
• Active Users: {active_users}
• New Users Today: {await self.get_new_users_today()}
• Paid Users: {await self.get_paid_users()}

**User Actions:**
        """.strip()
        
        keyboard = [
            [
                InlineKeyboardButton(text="🔍 Search User", callback_data="admin_search_user"),
                InlineKeyboardButton(text="📋 User List", callback_data="admin_user_list")
            ],
            [
                InlineKeyboardButton(text="🚫 Ban User", callback_data="admin_ban_user"),
                InlineKeyboardButton(text="✅ Unban User", callback_data="admin_unban_user")
            ],
            [
                InlineKeyboardButton(text="📊 User Analytics", callback_data="admin_user_analytics"),
                InlineKeyboardButton(text="💰 Payment History", callback_data="admin_payment_history")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        await callback_query.message.edit_text(
            text, 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )

    async def show_statistics(self, callback_query: CallbackQuery):
        """Show detailed statistics"""
        text = f"""
📊 **Detailed Statistics**

**Revenue:**
• Today: ${await self.get_daily_revenue():.2f}
• This Week: ${await self.get_weekly_revenue():.2f}
• This Month: ${await self.get_monthly_revenue():.2f}

**Users:**
• Total: {await self.get_total_users()}
• Active: {await self.get_active_users()}
• Premium: {await self.get_paid_users()}

**Campaigns:**
• Active: {await self.get_active_campaigns()}
• Completed: {await self.get_completed_campaigns()}
• Success Rate: {await self.get_success_rate()}%

**Channels:**
• Total Posts: {await self.get_total_posts()}
• Posts Today: {await self.get_posts_today()}
• Engagement Rate: {await self.get_engagement_rate()}%
        """.strip()
        
        keyboard = [
            [
                InlineKeyboardButton(text="📈 Detailed Report", callback_data="admin_detailed_report"),
                InlineKeyboardButton(text="📊 Export Data", callback_data="admin_export_data")
            ],
            [
                InlineKeyboardButton(text="🔄 Refresh Stats", callback_data="admin_refresh_stats"),
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        await callback_query.message.edit_text(
            text, 
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )

    # Helper methods for statistics
    async def get_total_users(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute("SELECT COUNT(*) FROM users")
                return (await result.fetchone())[0]
        except:
            return 0

    async def get_active_users(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE last_activity > datetime('now', '-7 days')"
                )
                return (await result.fetchone())[0]
        except:
            return 0

    async def get_new_users_today(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE created_at > datetime('now', '-1 day')"
                )
                return (await result.fetchone())[0]
        except:
            return 0

    async def get_paid_users(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT COUNT(DISTINCT user_id) FROM payments WHERE status = 'confirmed'"
                )
                return (await result.fetchone())[0]
        except:
            return 0

    async def get_daily_revenue(self) -> float:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT SUM(amount) FROM payments WHERE status = 'confirmed' AND created_at > datetime('now', '-1 day')"
                )
                amount = (await result.fetchone())[0]
                return amount if amount else 0.0
        except:
            return 0.0

    async def get_weekly_revenue(self) -> float:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT SUM(amount) FROM payments WHERE status = 'confirmed' AND created_at > datetime('now', '-7 days')"
                )
                amount = (await result.fetchone())[0]
                return amount if amount else 0.0
        except:
            return 0.0

    async def get_monthly_revenue(self) -> float:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT SUM(amount) FROM payments WHERE status = 'confirmed' AND created_at > datetime('now', '-30 days')"
                )
                amount = (await result.fetchone())[0]
                return amount if amount else 0.0
        except:
            return 0.0

    async def get_active_campaigns(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM subscriptions WHERE status = 'active'"
                )
                return (await result.fetchone())[0]
        except:
            return 0

    async def get_completed_campaigns(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM subscriptions WHERE status = 'completed'"
                )
                return (await result.fetchone())[0]
        except:
            return 0

    async def get_success_rate(self) -> float:
        try:
            total = await self.get_active_campaigns() + await self.get_completed_campaigns()
            completed = await self.get_completed_campaigns()
            return (completed / total * 100) if total > 0 else 0.0
        except:
            return 0.0

    async def get_total_posts(self) -> int:
        return 1500  # Mock data

    async def get_posts_today(self) -> int:
        return 25  # Mock data

    async def get_engagement_rate(self) -> float:
        return 12.5  # Mock data

    async def get_bot_uptime(self) -> str:
        return "2 days, 14 hours"  # Mock data

    async def get_memory_usage(self) -> str:
        return "128 MB"  # Mock data

    async def get_active_sessions(self) -> int:
        return 45  # Mock data

# Initialize admin system
admin_system = AdminSystem()

# Admin handlers
@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    """Handle admin command"""
    user_id = message.from_user.id
    
    if not admin_system.is_admin(user_id):
        await message.answer("❌ Access denied. Admin privileges required.")
        return
    
    await state.set_state(AdminStates.main_menu)
    await admin_system.show_main_menu(message)

@router.callback_query(F.data == "admin_main")
async def admin_main_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle admin main menu callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.main_menu)
    await admin_system.show_main_menu(callback_query, edit=True)
    await callback_query.answer()

@router.callback_query(F.data == "admin_channels")
async def admin_channels_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel management callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.channel_management)
    await admin_system.show_channel_management(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_subscriptions")
async def admin_subscriptions_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle subscription management callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.subscription_management)
    await admin_system.show_subscription_management(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_pricing")
async def admin_pricing_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle pricing management callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.pricing_management)
    await admin_system.show_pricing_management(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_schedules")
async def admin_schedules_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle publishing schedules callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.publishing_schedules)
    await admin_system.show_publishing_schedules(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_bot_control")
async def admin_bot_control_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle bot control callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.bot_control)
    await admin_system.show_bot_control(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_users")
async def admin_users_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle user management callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.user_management)
    await admin_system.show_user_management(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_statistics")
async def admin_statistics_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle statistics callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.statistics)
    await admin_system.show_statistics(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_refresh")
async def admin_refresh_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle refresh callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await callback_query.answer("🔄 Data refreshed!")
    await admin_system.show_main_menu(callback_query, edit=True)

# Channel Management Handlers
@router.callback_query(F.data == "admin_add_channel")
async def admin_add_channel_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle add channel callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.add_channel)
    
    text = """
➕ Add New Channel

Please provide the channel information in this format:

Channel Name
**Telegram ID** (e.g., @channel_name)
**Category** (e.g., Technology, Business, General)
**Estimated Subscribers** (number)

Example:
```
Tech News Channel
@technews
Technology
15000
```

Send the channel information now:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Channels", callback_data="admin_channels")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.message(AdminStates.add_channel)
async def handle_add_channel_message(message: Message, state: FSMContext):
    """Handle channel addition message"""
    try:
        lines = message.text.strip().split('\n')
        if len(lines) < 4:
            await message.reply("❌ Invalid format. Please provide all 4 fields: Name, Telegram ID, Category, Subscribers")
            return
        
        channel_name = lines[0].strip()
        telegram_id = lines[1].strip()
        category = lines[2].strip()
        subscribers = int(lines[3].strip())
        
        # Generate unique channel ID
        import time
        channel_id = f"channel_{int(time.time())}"
        
        # Add to admin system channels
        admin_system.channels[channel_id] = {
            'name': channel_name,
            'telegram_id': telegram_id,
            'url': f'https://t.me/{telegram_id.replace("@", "")}',
            'category': category,
            'subscribers': subscribers,
            'active': True
        }
        
        success_text = f"""
✅ **Channel Added Successfully!**

**Name:** {channel_name}
**ID:** {telegram_id}
**Category:** {category}
**Subscribers:** {subscribers:,}
**Status:** Active

The channel has been added to the system and is now available for advertising campaigns.
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📺 Back to Channel Management", callback_data="admin_channels")],
            [InlineKeyboardButton(text="🏠 Admin Menu", callback_data="admin_main")]
        ])
        
        await message.reply(success_text, reply_markup=keyboard, parse_mode='Markdown')
        await state.clear()
        
    except ValueError:
        await message.reply("❌ Invalid subscriber count. Please enter a valid number.")
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        await message.reply("❌ Error adding channel. Please try again.")

@router.callback_query(F.data == "admin_edit_channel")
async def admin_edit_channel_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle edit channel callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    text = "📝 **Edit Channel**\n\nSelect a channel to edit:"
    
    keyboard = []
    for channel_id, channel in admin_system.channels.items():
        keyboard.append([InlineKeyboardButton(
            text=f"{channel['name']} ({channel['telegram_id']})",
            callback_data=f"edit_channel_{channel_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Back to Channels", callback_data="admin_channels")])
    
    await callback_query.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='Markdown'
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("edit_channel_"))
async def handle_edit_channel_select(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel edit selection"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    channel_id = callback_query.data.replace("edit_channel_", "")
    channel = admin_system.channels.get(channel_id)
    
    if not channel:
        await callback_query.answer("❌ Channel not found.")
        return
    
    text = f"""
📝 **Edit Channel: {channel['name']}**

**Current Information:**
• Name: {channel['name']}
• Telegram ID: {channel['telegram_id']}
• Category: {channel['category']}
• Subscribers: {channel['subscribers']:,}
• Status: {'✅ Active' if channel['active'] else '❌ Inactive'}

What would you like to edit?
    """.strip()
    
    keyboard = [
        [
            InlineKeyboardButton(text="📝 Edit Name", callback_data=f"edit_name_{channel_id}"),
            InlineKeyboardButton(text="🔗 Edit Telegram ID", callback_data=f"edit_telegram_{channel_id}")
        ],
        [
            InlineKeyboardButton(text="📂 Edit Category", callback_data=f"edit_category_{channel_id}"),
            InlineKeyboardButton(text="👥 Edit Subscribers", callback_data=f"edit_subscribers_{channel_id}")
        ],
        [
            InlineKeyboardButton(
                text="❌ Deactivate" if channel['active'] else "✅ Activate",
                callback_data=f"toggle_channel_{channel_id}"
            )
        ],
        [InlineKeyboardButton(text="⬅️ Back to Edit", callback_data="admin_edit_channel")]
    ]
    
    await callback_query.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='Markdown'
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("toggle_channel_"))
async def handle_toggle_channel(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel activation toggle"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    channel_id = callback_query.data.replace("toggle_channel_", "")
    channel = admin_system.channels.get(channel_id)
    
    if not channel:
        await callback_query.answer("❌ Channel not found.")
        return
    
    # Toggle channel status
    channel['active'] = not channel['active']
    status = "activated" if channel['active'] else "deactivated"
    
    await callback_query.answer(f"✅ Channel {status} successfully!")
    
    # Return to edit view
    await handle_edit_channel_select(callback_query, state)

@router.callback_query(F.data == "admin_remove_channel")
async def admin_remove_channel_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle remove channel callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    text = "🗑️ **Remove Channel**\n\n⚠️ Select a channel to remove (this action cannot be undone):"
    
    keyboard = []
    for channel_id, channel in admin_system.channels.items():
        keyboard.append([InlineKeyboardButton(
            text=f"🗑️ {channel['name']} ({channel['telegram_id']})",
            callback_data=f"remove_channel_{channel_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Back to Channels", callback_data="admin_channels")])
    
    await callback_query.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='Markdown'
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("remove_channel_"))
async def handle_remove_channel_confirm(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel removal confirmation"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    channel_id = callback_query.data.replace("remove_channel_", "")
    channel = admin_system.channels.get(channel_id)
    
    if not channel:
        await callback_query.answer("❌ Channel not found.")
        return
    
    # Remove channel
    del admin_system.channels[channel_id]
    
    await callback_query.answer("✅ Channel removed successfully!")
    
    # Return to channel management
    await admin_system.show_channel_management(callback_query)

# Pricing Management Handlers
@router.callback_query(F.data.startswith("admin_price_"))
async def admin_price_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle pricing update callbacks"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    package_type = callback_query.data.replace("admin_price_", "")
    package = admin_system.subscription_packages.get(package_type)
    
    if not package:
        await callback_query.answer("❌ Package not found.")
        return
    
    await state.set_state(AdminStates.set_pricing)
    await state.update_data(package_type=package_type)
    
    text = f"""
💰 **Update {package['name']} Price**

**Current Price:** ${package['price_usd']} USD
**Duration:** {package['duration_days']} days
**Posts per Day:** {package['posts_per_day']}
**Channels Included:** {package['channels_included']}

Please enter the new price in USD (numbers only):
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Pricing", callback_data="admin_pricing")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.message(AdminStates.set_pricing)
async def handle_price_update_message(message: Message, state: FSMContext):
    """Handle price update message"""
    try:
        data = await state.get_data()
        package_type = data['package_type']
        new_price = float(message.text.strip())
        
        if new_price <= 0:
            await message.reply("❌ Price must be greater than 0.")
            return
        
        # Update package price
        old_price = admin_system.subscription_packages[package_type]['price_usd']
        admin_system.subscription_packages[package_type]['price_usd'] = new_price
        
        success_text = f"""
✅ **Price Updated Successfully!**

**Package:** {admin_system.subscription_packages[package_type]['name']}
**Old Price:** ${old_price} USD
**New Price:** ${new_price} USD

The pricing has been updated and will apply to all new orders.
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Back to Pricing Management", callback_data="admin_pricing")],
            [InlineKeyboardButton(text="🏠 Admin Menu", callback_data="admin_main")]
        ])
        
        await message.reply(success_text, reply_markup=keyboard, parse_mode='Markdown')
        await state.clear()
        
    except ValueError:
        await message.reply("❌ Invalid price format. Please enter a valid number.")
    except Exception as e:
        logger.error(f"Error updating price: {e}")
        await message.reply("❌ Error updating price. Please try again.")

# Subscription Management Handlers
@router.callback_query(F.data == "admin_create_subscription")
async def admin_create_subscription_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle create subscription callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.create_subscription)
    
    text = """
➕ **Create New Subscription Package**

Please provide the package information in this format:

**Package Name**
**Price in USD** (number)
**Duration in Days** (number)
**Posts per Day** (number)
**Channels Included** (number)

Example:
```
Premium Package
35.00
30
4
2
```

Send the package information now:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Subscriptions", callback_data="admin_subscriptions")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.message(AdminStates.create_subscription)
async def handle_create_subscription_message(message: Message, state: FSMContext):
    """Handle subscription creation message"""
    try:
        lines = message.text.strip().split('\n')
        if len(lines) < 5:
            await message.reply("❌ Invalid format. Please provide all 5 fields: Name, Price, Duration, Posts/Day, Channels")
            return
        
        package_name = lines[0].strip()
        price_usd = float(lines[1].strip())
        duration_days = int(lines[2].strip())
        posts_per_day = int(lines[3].strip())
        channels_included = int(lines[4].strip())
        
        # Generate unique package ID
        import time
        package_id = f"package_{int(time.time())}"
        
        # Add to admin system packages
        admin_system.subscription_packages[package_id] = {
            'name': package_name,
            'price_usd': price_usd,
            'duration_days': duration_days,
            'posts_per_day': posts_per_day,
            'channels_included': channels_included
        }
        
        success_text = f"""
✅ **Subscription Package Created Successfully!**

**Name:** {package_name}
**Price:** ${price_usd} USD
**Duration:** {duration_days} days
**Posts per Day:** {posts_per_day}
**Channels Included:** {channels_included}

The package has been added to the system and is now available for users.
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📦 Back to Subscription Management", callback_data="admin_subscriptions")],
            [InlineKeyboardButton(text="🏠 Admin Menu", callback_data="admin_main")]
        ])
        
        await message.reply(success_text, reply_markup=keyboard, parse_mode='Markdown')
        await state.clear()
        
    except ValueError:
        await message.reply("❌ Invalid format. Please check that prices and numbers are valid.")
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        await message.reply("❌ Error creating subscription. Please try again.")

@router.callback_query(F.data == "admin_edit_subscription")
async def admin_edit_subscription_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle edit subscription callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    text = "📝 **Edit Subscription Package**\n\nSelect a package to edit:"
    
    keyboard = []
    for package_id, package in admin_system.subscription_packages.items():
        keyboard.append([InlineKeyboardButton(
            text=f"{package['name']} (${package['price_usd']})",
            callback_data=f"edit_package_{package_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Back to Subscriptions", callback_data="admin_subscriptions")])
    
    await callback_query.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='Markdown'
    )
    await callback_query.answer()

@router.callback_query(F.data == "admin_remove_subscription")
async def admin_remove_subscription_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle remove subscription callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    text = "🗑️ **Remove Subscription Package**\n\n⚠️ Select a package to remove (this action cannot be undone):"
    
    keyboard = []
    for package_id, package in admin_system.subscription_packages.items():
        keyboard.append([InlineKeyboardButton(
            text=f"🗑️ {package['name']} (${package['price_usd']})",
            callback_data=f"remove_package_{package_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="⬅️ Back to Subscriptions", callback_data="admin_subscriptions")])
    
    await callback_query.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='Markdown'
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("remove_package_"))
async def handle_remove_package_confirm(callback_query: CallbackQuery, state: FSMContext):
    """Handle package removal confirmation"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    package_id = callback_query.data.replace("remove_package_", "")
    package = admin_system.subscription_packages.get(package_id)
    
    if not package:
        await callback_query.answer("❌ Package not found.")
        return
    
    # Remove package
    del admin_system.subscription_packages[package_id]
    
    await callback_query.answer("✅ Package removed successfully!")
    
    # Return to subscription management
    await admin_system.show_subscription_management(callback_query)

@router.callback_query(F.data == "admin_channel_stats")
async def admin_channel_stats_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel stats callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    total_subscribers = sum(ch['subscribers'] for ch in admin_system.channels.values())
    active_channels = len([ch for ch in admin_system.channels.values() if ch['active']])
    
    text = f"""
📊 **Channel Statistics**

**Total Channels:** {len(admin_system.channels)}
**Active Channels:** {active_channels}
**Total Subscribers:** {total_subscribers:,}
**Average Subscribers:** {total_subscribers // len(admin_system.channels) if admin_system.channels else 0:,}

**Channel Details:**
    """.strip()
    
    for channel_id, channel in admin_system.channels.items():
        status = "✅" if channel['active'] else "❌"
        text += f"\n{status} **{channel['name']}**"
        text += f"\n   • {channel['subscribers']:,} subscribers"
        text += f"\n   • Category: {channel['category']}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 Back to Channel Management", callback_data="admin_channels")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "admin_subscription_stats")
async def admin_subscription_stats_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle subscription stats callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    text = f"""
📊 **Subscription Package Statistics**

**Total Packages:** {len(admin_system.subscription_packages)}

**Package Performance:**
    """.strip()
    
    for package_id, package in admin_system.subscription_packages.items():
        text += f"\n📦 **{package['name']}**"
        text += f"\n   • Price: ${package['price_usd']} USD"
        text += f"\n   • Duration: {package['duration_days']} days"
        text += f"\n   • Posts/Day: {package['posts_per_day']}"
        text += f"\n   • Revenue Potential: ${package['price_usd'] * 10:.2f}/month (est.)"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Back to Subscription Management", callback_data="admin_subscriptions")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

def setup_admin_handlers(dp):
    """Setup admin handlers"""
    dp.include_router(router)
    logger.info("Admin system handlers setup completed")