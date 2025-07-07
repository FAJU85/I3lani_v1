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
    
    # Package management
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
                InlineKeyboardButton(text="💰 Price Management", callback_data="admin_packages")
            ],
            [
                InlineKeyboardButton(text="👥 User Management", callback_data="admin_users"),
                InlineKeyboardButton(text="📊 Statistics", callback_data="admin_statistics")
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
**I3lani Bot Admin Panel**

**System Status:** ✅ Online
**Total Users:** {await self.get_total_users()}
**Active Channels:** {len([c for c in self.channels.values() if c['active']])}
**Revenue Today:** ${await self.get_daily_revenue():.2f}

**Quick Actions:**
- Manage channels and subscriptions
- Control packages and schedules
- Monitor user activity
- View detailed statistics
- Send broadcast messages

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
            text += f"\n   - ID: {channel['telegram_id']}"
            text += f"\n   - Subscribers: {channel['subscribers']:,}"
            text += f"\n   - Category: {channel['category']}"
        
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
**Package Management**

**Available Packages:** {len(self.subscription_packages)}

**Current Packages:**
        """.strip()
        
        for package_id, package in self.subscription_packages.items():
            text += f"\n**{package['name']}**"
            text += f"\n   - Price: ${package['price_usd']}"
            text += f"\n   - Duration: {package['duration_days']} days"
            text += f"\n   - Posts/Day: {package['posts_per_day']}"
            text += f"\n   - Channels: {package['channels_included']}"
        
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
        """Show price management interface"""
        from database import db
        
        # Get current packages from database
        packages = await db.get_packages(active_only=False)
        
        text = "**Price Management**\n\n"
        
        if packages:
            text += "**Current Packages:**\n"
            for package in packages:
                status = "✅ Active" if package.get('active', True) else "❌ Inactive"
                text += f"- {package['name']}: ${package['price_usd']} ({status})\n"
        else:
            text += "**No packages found in database.**\n"
        
        text += "\n**Package Management Options:**\n"
        text += "Create, edit, remove, or view statistics for pricing packages.\n"
        
        keyboard = [
            [
                InlineKeyboardButton(text="➕ Create Price", callback_data="admin_create_price"),
                InlineKeyboardButton(text="✏️ Edit Price", callback_data="admin_edit_price")
            ],
            [
                InlineKeyboardButton(text="🗑️ Remove Price", callback_data="admin_remove_price"),
                InlineKeyboardButton(text="📊 Price Stats", callback_data="admin_price_stats")
            ],
            [
                InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_refresh")
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
- Auto-publish: ✅ Enabled
- Timezone: UTC
- Retry failed posts: ✅ Enabled
- Max posts per hour: 10
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
- Multi-language support (EN/AR/RU) ✅
- Payment processing (TON/Stars) ✅
- Auto-publishing ✅
- Referral system ✅
- Debug system ✅

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
**User Management**

**User Statistics:**
Total Users: {total_users}
Active Users: {active_users}
- New Users Today: {await self.get_new_users_today()}
- Paid Users: {await self.get_paid_users()}

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
**Detailed Statistics**

**Revenue:**
Today: ${await self.get_daily_revenue():.2f}
This Week: ${await self.get_weekly_revenue():.2f}
This Month: ${await self.get_monthly_revenue():.2f}

**Users:**
- Total: {await self.get_total_users()}
- Active: {await self.get_active_users()}
- Premium: {await self.get_paid_users()}

**Campaigns:**
- Active: {await self.get_active_campaigns()}
- Completed: {await self.get_completed_campaigns()}
- Success Rate: {await self.get_success_rate()}%

**Channels:**
- Total Posts: {await self.get_total_posts()}
- Posts Today: {await self.get_posts_today()}
- Engagement Rate: {await self.get_engagement_rate()}%
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

# Package management removed - using dynamic pricing system instead

@router.callback_query(F.data == "admin_create_price")
async def admin_create_price_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle create price callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied!")
        return
    
    await state.set_state(AdminStates.create_subscription)
    
    text = """
➕ **Create New Price Package**

Please enter the package details in this format:
`package_id|name|price_usd|duration_days|posts_per_day|channels_included`

**Example:**
`premium|Premium Plan|99|365|10|5`

**Fields:**
- package_id: Unique identifier (no spaces)
- name: Display name for the package
- price_usd: Price in USD
- duration_days: Package duration in days
- posts_per_day: Maximum posts per day
- channels_included: Number of channels included

Type your package details:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_packages")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "admin_edit_price")
async def admin_edit_price_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle edit price callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied!")
        return
    
    from database import db
    packages = await db.get_packages(active_only=False)
    
    if not packages:
        await callback_query.answer("❌ No packages found!")
        return
    
    text = "**Edit Price Package**\n\nSelect a package to edit:"
    
    keyboard_buttons = []
    for package in packages:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{package['name']} - ${package['price_usd']}",
                callback_data=f"admin_edit_pkg_{package['package_id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="❌ Cancel", callback_data="admin_packages")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "admin_remove_price")
async def admin_remove_price_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle remove price callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied!")
        return
    
    from database import db
    packages = await db.get_packages(active_only=False)
    
    if not packages:
        await callback_query.answer("❌ No packages found!")
        return
    
    text = "**Remove Price Package**\n\nWarning: This will permanently delete the package!\n\nSelect a package to remove:"
    
    keyboard_buttons = []
    for package in packages:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"🗑️ {package['name']} - ${package['price_usd']}",
                callback_data=f"admin_remove_pkg_{package['package_id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="❌ Cancel", callback_data="admin_packages")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "admin_price_stats")
async def admin_price_stats_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle price stats callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied!")
        return
    
    from database import db
    packages = await db.get_packages(active_only=False)
    
    text = "**Price Statistics**\n\n"
    
    if packages:
        total_packages = len(packages)
        active_packages = len([p for p in packages if p.get('active', True)])
        total_revenue = sum(p['price_usd'] for p in packages)
        avg_price = total_revenue / total_packages if total_packages > 0 else 0
        
        text += f"**Package Overview:**\n"
        text += f"- Total Packages: {total_packages}\n"
        text += f"- Active Packages: {active_packages}\n"
        text += f"- Average Price: ${avg_price:.2f}\n\n"
        
        text += "**Package Details:**\n"
        for package in packages:
            status = "✅" if package.get('active', True) else "❌"
            text += f"{status} {package['name']}: ${package['price_usd']} ({package['duration_days']} days)\n"
    else:
        text += "**No packages found in database.**\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_price_stats")],
        [InlineKeyboardButton(text="⬅️ Back to Packages", callback_data="admin_packages")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "admin_packages")
async def admin_packages_callback(callback_query: CallbackQuery, state: FSMContext):
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
@router.callback_query(F.data == "admin_discover_channels")
async def admin_discover_channels_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle discover existing channels callback"""
    await callback_query.answer()
    
    text = """
**Discovering Existing Channels**

Scanning for channels where the bot is already an administrator...
    """.strip()
    
    # Show loading message
    await callback_query.message.edit_text(text)
    
    # Import channel manager
    from channel_manager import channel_manager
    
    if channel_manager:
        # Sync existing channels
        await channel_manager.sync_existing_channels()
        
        # Get updated channel list
        channels = await admin_system.db.get_channels(active_only=True)
        
        result_text = f"""
**Channel Discovery Complete**

Found {len(channels)} active channels:

"""
        
        for i, channel in enumerate(channels, 1):
            result_text += f"{i}. **{channel['name']}** - {channel['subscribers']:,} subscribers\n"
        
        if not channels:
            result_text += "No channels found where bot is administrator.\n\n"
            result_text += "**To add channels:**\n"
            result_text += "1. Add the bot as administrator to your channel\n"
            result_text += "2. Give the bot permission to post messages\n"
            result_text += "3. The bot will automatically detect and add the channel\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Channels", callback_data="admin_channels")]
        ])
        
        await callback_query.message.edit_text(result_text, reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(
            "❌ Channel manager not initialized. Please restart the bot.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_channels")]
            ])
        )

@router.callback_query(F.data == "admin_add_channel")
async def admin_add_channel_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle add channel callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.add_channel)
    
    text = """
📺 **Add New Channel**

Please send the channel username (e.g., @channel_name) or channel ID:

**Note:** The bot must be added as an administrator to the channel first.

**Auto-Discovery:** If the bot is already admin in existing channels, use the "Discover Existing Channels" button instead.
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Discover Existing Channels", callback_data="admin_discover_channels")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_channels")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer()
15000

Send the channel information now:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Channels", callback_data="admin_channels")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)
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
**Channel Added Successfully!**

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
**Edit Channel: {channel['name']}**

**Current Information:**
Name: {channel['name']}
Telegram ID: {channel['telegram_id']}
Category: {channel['category']}
Subscribers: {channel['subscribers']:,}
Status: {'Active' if channel['active'] else 'Inactive'}

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
                text="Deactivate" if channel['active'] else "Activate",
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
    
    await callback_query.answer(f"Channel {status} successfully!")
    
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

# Package Management Handlers
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
        [InlineKeyboardButton(text="⬅️ Back to Packages", callback_data="admin_packages")]
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
            [InlineKeyboardButton(text="💰 Back to Packages Management", callback_data="admin_packages")],
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
        
        # Add to admin system packages (in-memory)
        admin_system.subscription_packages[package_id] = {
            'name': package_name,
            'price_usd': price_usd,
            'duration_days': duration_days,
            'posts_per_day': posts_per_day,
            'channels_included': channels_included
        }
        
        # Also save to database for persistence
        from database import db
        await db.create_package(package_id, package_name, price_usd, duration_days, posts_per_day, channels_included)
        
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
    
    text = """
📝 **Edit Subscription Package**

Select a package to edit:

**Available Packages:**
- Free Package: $0 (3 days, 3 ads per month)
- Bronze Package: $10 (1 month)
- Silver Package: $29 (3 months)  
- Gold Package: $47 (6 months)

Choose a package to modify:
    """.strip()
    
    keyboard = [
        [
            InlineKeyboardButton(text="🟫 Edit Bronze ($10)", callback_data="edit_package_bronze"),
            InlineKeyboardButton(text="🥈 Edit Silver ($29)", callback_data="edit_package_silver")
        ],
        [
            InlineKeyboardButton(text="🥇 Edit Gold ($47)", callback_data="edit_package_gold"),
            InlineKeyboardButton(text="🎁 Edit Free Package", callback_data="edit_package_free")
        ],
        [InlineKeyboardButton(text="⬅️ Back to Subscriptions", callback_data="admin_subscriptions")]
    ]
    
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
        text += f"\n   - {channel['subscribers']:,} subscribers"
        text += f"\n   - Category: {channel['category']}"
    
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
        text += f"\n   - Price: ${package['price_usd']} USD"
        text += f"\n   - Duration: {package['duration_days']} days"
        text += f"\n   - Posts/Day: {package['posts_per_day']}"
        text += f"\n   - Revenue Potential: ${package['price_usd'] * 10:.2f}/month (est.)"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Back to Subscription Management", callback_data="admin_subscriptions")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.message(AdminStates.create_subscription)
async def handle_create_price_message(message: Message, state: FSMContext):
    """Handle create price form submission"""
    user_id = message.from_user.id
    
    if not admin_system.is_admin(user_id):
        await message.reply("❌ Access denied!")
        return
    
    try:
        # Parse package details: package_id|name|price_usd|duration_days|posts_per_day|channels_included
        parts = message.text.strip().split('|')
        if len(parts) != 6:
            await message.reply("❌ Invalid format! Please use: `package_id|name|price_usd|duration_days|posts_per_day|channels_included`")
            return
        
        package_id, name, price_usd, duration_days, posts_per_day, channels_included = parts
        
        # Validate data types
        price_usd = float(price_usd)
        duration_days = int(duration_days)
        posts_per_day = int(posts_per_day)
        channels_included = int(channels_included)
        
        # Create package in database
        from database import db
        success = await db.create_package(
            package_id.strip(),
            name.strip(),
            price_usd,
            duration_days,
            posts_per_day,
            channels_included
        )
        
        if success:
            success_text = f"""
✅ **Price Package Created Successfully!**

**Package Details:**
- ID: {package_id}
- Name: {name}
- Price: ${price_usd}
- Duration: {duration_days} days
- Posts per day: {posts_per_day}
- Channels included: {channels_included}

The package is now available in the pricing menu!
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Price Management", callback_data="admin_packages")]
            ])
            
            await message.reply(success_text, reply_markup=keyboard, parse_mode='Markdown')
        else:
            await message.reply("❌ Failed to create package. Package ID might already exist.")
        
    except ValueError:
        await message.reply("❌ Invalid number format! Please check price, duration, posts per day, and channels values.")
    except Exception as e:
        await message.reply(f"❌ Error creating package: {str(e)}")
    
    await state.clear()

@router.callback_query(F.data.startswith("admin_remove_pkg_"))
async def admin_remove_package_confirm(callback_query: CallbackQuery, state: FSMContext):
    """Handle package removal confirmation"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied!")
        return
    
    package_id = callback_query.data.replace("admin_remove_pkg_", "")
    
    try:
        from database import db
        packages = await db.get_packages(active_only=False)
        package = next((p for p in packages if p['package_id'] == package_id), None)
        
        if not package:
            await callback_query.answer("❌ Package not found!")
            return
        
        # Remove package from database
        async with db.get_connection() as conn:
            await conn.execute("DELETE FROM packages WHERE package_id = ?", (package_id,))
            await conn.commit()
        
        success_text = f"""
✅ **Package Removed Successfully!**

**Removed Package:**
- Name: {package['name']}
- Price: ${package['price_usd']}
- ID: {package_id}

The package has been permanently deleted and is no longer available in the pricing menu.
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back to Price Management", callback_data="admin_packages")]
        ])
        
        await callback_query.message.edit_text(success_text, reply_markup=keyboard, parse_mode='Markdown')
        await callback_query.answer(f"✅ Package '{package['name']}' removed!")
        
    except Exception as e:
        await callback_query.answer(f"❌ Error removing package: {str(e)}")

@router.callback_query(F.data.startswith("admin_edit_pkg_"))
async def admin_edit_package_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle package editing"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied!")
        return
    
    package_id = callback_query.data.replace("admin_edit_pkg_", "")
    
    try:
        from database import db
        packages = await db.get_packages(active_only=False)
        package = next((p for p in packages if p['package_id'] == package_id), None)
        
        if not package:
            await callback_query.answer("❌ Package not found!")
            return
        
        await state.update_data(edit_package_id=package_id)
        await state.set_state(AdminStates.edit_subscription)
        
        text = f"""
✏️ **Edit Package: {package['name']}**

**Current Details:**
- ID: {package['package_id']}
- Name: {package['name']}
- Price: ${package['price_usd']}
- Duration: {package['duration_days']} days
- Posts per day: {package['posts_per_day']}
- Channels: {package['channels_included']}

Please enter the new package details in this format:
`name|price_usd|duration_days|posts_per_day|channels_included`

**Example:**
`Premium Plan|99|365|10|5`

Type your updated package details:
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_packages")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"❌ Error loading package: {str(e)}")

@router.message(AdminStates.edit_subscription)
async def handle_edit_package_message(message: Message, state: FSMContext):
    """Handle edit package form submission"""
    user_id = message.from_user.id
    
    if not admin_system.is_admin(user_id):
        await message.reply("❌ Access denied!")
        return
    
    try:
        data = await state.get_data()
        package_id = data.get('edit_package_id')
        
        if not package_id:
            await message.reply("❌ Package ID not found!")
            return
        
        # Parse package details: name|price_usd|duration_days|posts_per_day|channels_included
        parts = message.text.strip().split('|')
        if len(parts) != 5:
            await message.reply("❌ Invalid format! Please use: `name|price_usd|duration_days|posts_per_day|channels_included`")
            return
        
        name, price_usd, duration_days, posts_per_day, channels_included = parts
        
        # Validate data types
        price_usd = float(price_usd)
        duration_days = int(duration_days)
        posts_per_day = int(posts_per_day)
        channels_included = int(channels_included)
        
        # Update package in database
        from database import db
        async with db.get_connection() as conn:
            await conn.execute("""
                UPDATE packages 
                SET name = ?, price_usd = ?, duration_days = ?, posts_per_day = ?, channels_included = ?
                WHERE package_id = ?
            """, (name.strip(), price_usd, duration_days, posts_per_day, channels_included, package_id))
            await conn.commit()
        
        success_text = f"""
✅ **Package Updated Successfully!**

**Updated Package Details:**
- ID: {package_id}
- Name: {name}
- Price: ${price_usd}
- Duration: {duration_days} days
- Posts per day: {posts_per_day}
- Channels included: {channels_included}

The changes are now live in the pricing menu!
        """.strip()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back to Price Management", callback_data="admin_packages")]
        ])
        
        await message.reply(success_text, reply_markup=keyboard, parse_mode='Markdown')
        
    except ValueError:
        await message.reply("❌ Invalid number format! Please check price, duration, posts per day, and channels values.")
    except Exception as e:
        await message.reply(f"❌ Error updating package: {str(e)}")
    
    await state.clear()

@router.message(Command("admin_channel_details"))
async def admin_channel_details_handler(message: Message):
    """View detailed channel information"""
    if not await is_admin(message.from_user.id):
        return
    
    try:
        channels = await db.get_channels(active_only=False)
        
        if not channels:
            await message.reply("No channels found in database.")
            return
        
        response = "📊 **Detailed Channel Information**\n\n"
        
        for channel in channels:
            status = "✅ Active" if channel.get('is_active') else "❌ Inactive"
            category = channel.get('category', 'general').title()
            active_subs = channel.get('active_subscribers', 0)
            total_posts = channel.get('total_posts', 0)
            description = channel.get('description', 'No description')
            last_updated = channel.get('last_updated', 'Never')
            
            response += f"**{channel['name']}**\n"
            response += f"- **Channel ID:** `{channel['telegram_channel_id']}`\n"
            response += f"- **Category:** {category}\n"
            response += f"- **Total Subscribers:** {channel.get('subscribers', 0):,}\n"
            response += f"- **Active Subscribers:** {active_subs:,}\n"
            response += f"- **Total Posts:** {total_posts:,}\n"
            response += f"- **Base Price:** ${channel.get('base_price_usd', 0):.2f}\n"
            response += f"- **Status:** {status}\n"
            response += f"- **Last Updated:** {last_updated}\n"
            
            if description and len(description) > 50:
                description = description[:47] + "..."
            response += f"- **Description:** {description}\n\n"
            
            # Prevent message from being too long
            if len(response) > 3500:
                response += "... (truncated for length)"
                break
        
        await message.reply(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Admin channel details error: {e}")
        await message.reply("Error retrieving channel details.")

def setup_admin_handlers(dp):
    """Setup admin handlers"""
    dp.include_router(router)
    logger.info("Admin system handlers setup completed")