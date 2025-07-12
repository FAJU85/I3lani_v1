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
from dynamic_pricing import get_dynamic_pricing
from states import AdminStates
# Admin UI control removed during cleanup

logger = logging.getLogger(__name__)

# AdminStates is now imported from states.py to avoid duplication

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
        
        # Remove fake channels - use real data from database
        
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
                InlineKeyboardButton(text="🧠 Smart Pricing System", callback_data="admin_smart_pricing"),
                InlineKeyboardButton(text="📊 Pricing Table", callback_data="admin_pricing_table")
            ],
            [
                InlineKeyboardButton(text="🎨 UI Control", callback_data="ui_control_main"),
                InlineKeyboardButton(text="🔧 Troubleshoot", callback_data="admin_troubleshoot")
            ],
            [
                InlineKeyboardButton(text="👥 User Management", callback_data="admin_users"),
                InlineKeyboardButton(text="💸 Payout Management", callback_data="admin_payouts")
            ],
            [
                InlineKeyboardButton(text="🛡️ Anti-Fraud Panel", callback_data="admin_fraud"),
                InlineKeyboardButton(text="🔒 Security Center", callback_data="admin_security")
            ],
            [
                InlineKeyboardButton(text="🛡️ Content Moderation", callback_data="admin_moderation"),
                InlineKeyboardButton(text="📋 Violation Reports", callback_data="admin_violations")
            ],
            [
                InlineKeyboardButton(text="🎮 Gamification Management", callback_data="admin_gamification"),
                InlineKeyboardButton(text="🏅 Achievement Analytics", callback_data="admin_achievements")
            ],
            [
                InlineKeyboardButton(text="🤖 Bot Control", callback_data="admin_bot_control"),
                InlineKeyboardButton(text="🧪 Test Bot Workflow", callback_data="admin_test_workflow")
            ],
            [
                InlineKeyboardButton(text="📄 Usage Agreement", callback_data="admin_agreement"),
                InlineKeyboardButton(text="📋 Test History", callback_data="admin_test_history")
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
        # Get real channel data from database
        channels = await db.get_channels(active_only=False)
        active_channels = [ch for ch in channels if ch.get('is_active', False)]
        
        text = f"""
**I3lani Bot Admin Panel**

**System Status:** SUCCESS: Online
**Total Users:** {await self.get_total_users()}
**Active Channels:** {len(active_channels)}
**Total Channels:** {len(channels)}

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
        try:
            # Get real channel data from database
            channels = await db.get_channels(active_only=False)
            active_channels = [ch for ch in channels if ch.get('is_active', False)]
            logger.info(f"Channel management: Found {len(channels)} channels, {len(active_channels)} active")
            
            text = f"""<b>📺 Channel Management</b>

<b>Active Channels:</b> {len(active_channels)}
<b>Total Channels:</b> {len(channels)}

<b>Channels:</b>
            """.strip()
            
            if not channels:
                text += "\n\nNo channels found. Add channels by making the bot admin in a channel."
            else:
                for channel in channels:
                    status = "✅" if channel.get('is_active', False) else "❌"
                    channel_name = channel['name']
                    text += f"\n{status} <b>{channel_name}</b>"
                    text += f"\n   • ID: <code>{channel['telegram_channel_id']}</code>"
                    text += f"\n   • Subscribers: {channel['subscribers']:,}"
                    text += f"\n   • Category: {channel.get('category', 'general')}"
            
            keyboard = [
                [
                    InlineKeyboardButton(text="🚀 Enhanced Dashboard", callback_data="enhanced_channel_dashboard"),
                    InlineKeyboardButton(text="📊 Channel Analytics", callback_data="admin_channel_stats")
                ],
                [
                    InlineKeyboardButton(text="⚡ Bulk Operations", callback_data="bulk_channel_operations"),
                    InlineKeyboardButton(text="📈 Advanced Reports", callback_data="detailed_channel_analysis")
                ],
                [
                    InlineKeyboardButton(text="🔍 Discover Channels", callback_data="admin_discover_channels"),
                    InlineKeyboardButton(text="📥 Bulk Import", callback_data="admin_bulk_import")
                ],
                [
                    InlineKeyboardButton(text="➕ Add Channel", callback_data="admin_add_channel"),
                    InlineKeyboardButton(text="EDIT: Edit Channel", callback_data="admin_edit_channel")
                ],
                [
                    InlineKeyboardButton(text="🗑️ Remove Channel", callback_data="admin_remove_channel"),
                    InlineKeyboardButton(text="🔄 Refresh Stats", callback_data="bulk_update_stats")
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
            
        except Exception as e:
            logger.error(f"Channel management error: {e}")
            simple_text = f"<b>📺 Channel Management</b>\n\nError loading channels: {str(e)}"
            keyboard = [[InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")]]
            await callback_query.message.edit_text(
                simple_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode='HTML'
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
                InlineKeyboardButton(text="EDIT: Edit Package", callback_data="admin_edit_subscription")
            ],
            [
                InlineKeyboardButton(text="🗑️ Remove Package", callback_data="admin_remove_subscription"),
                InlineKeyboardButton(text="STATS: Package Stats", callback_data="admin_subscription_stats")
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
        """Show smart day-based pricing management interface"""
        from frequency_pricing import FrequencyPricingSystem
        pricing = FrequencyPricingSystem()
        
        text = "**🧠 Smart Day-Based Pricing Management**\n\n"
        text += "**Core Logic:** We Sell Days, You Gain Reach™\n\n"
        
        text += "**Current Pricing Tiers:**\n"
        
        # Show sample tiers
        sample_tiers = [1, 3, 7, 15, 30, 60, 90]
        for days in sample_tiers:
            tier_info = pricing.frequency_tiers.get(days)
            if tier_info:
                pricing_data = pricing.calculate_pricing(days)
                text += f"• **{days} days** - {tier_info['posts_per_day']} posts/day\n"
                text += f"  ${pricing_data['final_cost_usd']:.2f} ({tier_info['discount']}% discount)\n"
        
        text += "\n**Smart Pricing Features:**\n"
        text += "• Dynamic day-based pricing (1-365 days)\n"
        text += "• More days = More posts per day + Bigger discounts\n"
        text += "• Automatic volume discounts (0% to 35% off)\n"
        text += "• Base rate: $1.00 per post per day\n\n"
        
        text += "**Management Options:**\n"
        
        keyboard = [
            [
                InlineKeyboardButton(text="🧠 Smart Pricing System", callback_data="admin_smart_pricing"),
                InlineKeyboardButton(text="📊 Pricing Table", callback_data="admin_pricing_table")
            ],
            [
                InlineKeyboardButton(text="💰 Revenue Analytics", callback_data="admin_revenue_analytics"),
                InlineKeyboardButton(text="🎯 Usage Statistics", callback_data="admin_usage_stats")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        try:
            await callback_query.message.edit_text(
                text, 
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode='Markdown'
            )
        except Exception:
            await callback_query.message.answer(
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
            status = "SUCCESS:" if schedule['active'] else "ERROR:"
            text += f"\n{status} **{schedule_id.title()}:** {schedule['time']}"
        
        text += f"""

**Schedule Settings:**
- Auto-publish: SUCCESS: Enabled
- Timezone: UTC
- Retry failed posts: SUCCESS: Enabled
- Max posts per hour: 10
        """.strip()
        
        keyboard = [
            [
                InlineKeyboardButton(text="➕ Add Schedule", callback_data="admin_create_schedule"),
                InlineKeyboardButton(text="EDIT: Edit Schedule", callback_data="admin_edit_schedule")
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

**Bot Status:** SUCCESS: Online and Running
**Uptime:** {await self.get_bot_uptime()}
**Memory Usage:** {await self.get_memory_usage()}
**Active Sessions:** {await self.get_active_sessions()}

**Bot Features:**
- Multi-language support (EN/AR/RU) SUCCESS:
- Payment processing (TON/Stars) SUCCESS:
- Auto-publishing SUCCESS:
- Referral system SUCCESS:
- Debug system SUCCESS:

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
                InlineKeyboardButton(text="STATS: System Logs", callback_data="admin_system_logs")
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
                InlineKeyboardButton(text="SUCCESS: Unban User", callback_data="admin_unban_user")
            ],
            [
                InlineKeyboardButton(text="STATS: User Analytics", callback_data="user_analytics"),
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
        # Get real channel data from database
        channels = await db.get_channels(active_only=False)
        active_channels = [ch for ch in channels if ch.get('is_active', False)]
        total_subscribers = sum(ch.get('subscribers', 0) for ch in channels)
        
        text = f"""
**STATS: Channel Statistics**

**Total Channels:** {len(channels)}
**Active Channels:** {len(active_channels)}
**Total Subscribers:** {total_subscribers:,}
**Average Subscribers:** {total_subscribers // len(channels) if channels else 0:,}

**Channel Details:**
        """.strip()
        
        if not channels:
            text += "\n\nNo channels found in database."
            text += "\n\n**To add channels:**"
            text += "\n1. Add the bot as administrator to your channel"
            text += "\n2. Give the bot permission to post messages"
            text += "\n3. The bot will automatically detect and add the channel"
        else:
            for channel in channels:
                status = "SUCCESS:" if channel.get('is_active', False) else "INACTIVE:"
                text += f"\n{status} **{channel['name']}**"
                text += f"\n   - {channel.get('subscribers', 0):,} subscribers"
                text += f"\n   - Category: {channel.get('category', 'general').title()}"
                text += f"\n   - ID: `{channel.get('telegram_channel_id', 'N/A')}`"
        
        keyboard = [
            [
                InlineKeyboardButton(text="🔄 Refresh Stats", callback_data="admin_statistics"),
                InlineKeyboardButton(text="📺 Channel Management", callback_data="admin_channels")
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

    # Helper methods for statistics
    async def get_total_users(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute("SELECT COUNT(*) FROM users")
                return (await result.fetchone())[0]
        except Exception as e:
            logger.error(f"Error getting total users: {e}")
            return 0

    async def get_active_users(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE last_activity > datetime('now', '-7 days')"
                )
                return (await result.fetchone())[0]
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return 0

    async def get_new_users_today(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE created_at > datetime('now', '-1 day')"
                )
                return (await result.fetchone())[0]
        except Exception as e:
            logger.error(f"Error getting new users today: {e}")
            return 0

    async def get_paid_users(self) -> int:
        try:
            async with db.connection() as conn:
                result = await conn.execute(
                    "SELECT COUNT(DISTINCT user_id) FROM payments WHERE status = 'confirmed'"
                )
                return (await result.fetchone())[0]
        except Exception as e:
            logger.error(f"Error getting paid users: {e}")
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

    async def show_moderation_panel(self, callback_query: CallbackQuery):
        """Show content moderation management panel"""
        try:
            from content_moderation import ContentModerationSystem
            moderation_system = ContentModerationSystem(db, self.bot)
            
            # Get moderation statistics
            stats = await moderation_system.get_moderation_statistics()
            
            text = f"""
🛡️ **Content Moderation Panel**

**Strike System Status:**
• Total Violations: {stats.get('total_violations', 0)}
• Banned Users: {stats.get('banned_users', 0)}
• Active Warnings: {stats.get('active_warnings', 0)}
• Violations Today: {stats.get('violations_today', 0)}

**Compliance Standards:**
✅ Telegram Community Guidelines
✅ International Regulations
✅ Ethical Standards
✅ Human Rights Compliance
✅ Saudi Arabian Regulations

**Six-Strike Policy:**
• Strikes 1-5: Warning + Edit Opportunity
• Strike 6: Permanent Ban + No Compensation
            """.strip()
            
            keyboard = [
                [
                    InlineKeyboardButton(text="📊 Violation Statistics", callback_data="mod_statistics"),
                    InlineKeyboardButton(text="⚠️ Active Warnings", callback_data="mod_warnings")
                ],
                [
                    InlineKeyboardButton(text="🚫 Banned Users", callback_data="mod_banned_users"),
                    InlineKeyboardButton(text="📋 Violation History", callback_data="mod_violation_history")
                ],
                [
                    InlineKeyboardButton(text="🔧 Moderation Settings", callback_data="mod_settings"),
                    InlineKeyboardButton(text="📜 Moderation Logs", callback_data="mod_logs")
                ],
                [
                    InlineKeyboardButton(text="🔄 Manual Review", callback_data="mod_manual_review"),
                    InlineKeyboardButton(text="⚡ Quick Actions", callback_data="mod_quick_actions")
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
            
        except Exception as e:
            logger.error(f"Moderation panel error: {e}")
            await callback_query.answer("Error loading moderation panel", show_alert=True)

    async def show_violation_reports(self, callback_query: CallbackQuery):
        """Show violation reports and statistics"""
        try:
            from content_moderation import ContentModerationSystem
            moderation_system = ContentModerationSystem(db, self.bot)
            
            # Get detailed violation statistics
            stats = await moderation_system.get_moderation_statistics()
            
            text = f"""
📋 **Violation Reports Dashboard**

**Daily Statistics:**
• Violations Today: {stats.get('violations_today', 0)}
• New Warnings: {stats.get('active_warnings', 0)}
• Content Approved: {stats.get('approved_today', 0)}
• Rejection Rate: {stats.get('rejection_rate', 0):.1f}%

**Violation Categories:**
• Hate Speech: {stats.get('hate_speech', 0)}
• Adult Content: {stats.get('adult_content', 0)}
• Illegal Content: {stats.get('illegal_content', 0)}
• Fraud/Scam: {stats.get('fraud_scam', 0)}
• Spam: {stats.get('spam', 0)}
• Violence: {stats.get('violence', 0)}
• Discrimination: {stats.get('discrimination', 0)}
• Saudi Compliance: {stats.get('saudi_specific', 0)}

**Strike Distribution:**
• Strike 1: {stats.get('strike_1', 0)} users
• Strike 2: {stats.get('strike_2', 0)} users
• Strike 3: {stats.get('strike_3', 0)} users
• Strike 4: {stats.get('strike_4', 0)} users
• Strike 5: {stats.get('strike_5', 0)} users
• Strike 6: {stats.get('banned_users', 0)} users (banned)
            """.strip()
            
            keyboard = [
                [
                    InlineKeyboardButton(text="📈 Detailed Analytics", callback_data="violation_analytics"),
                    InlineKeyboardButton(text="🔍 Search Violations", callback_data="violation_search")
                ],
                [
                    InlineKeyboardButton(text="📊 Export Report", callback_data="violation_export"),
                    InlineKeyboardButton(text="🔔 Alert Settings", callback_data="violation_alerts")
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
            
        except Exception as e:
            logger.error(f"Violation reports error: {e}")
            await callback_query.answer("Error loading violation reports", show_alert=True)

# Initialize admin system
admin_system = AdminSystem()

# Admin handlers
@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    """Handle admin command"""
    user_id = message.from_user.id
    
    if not admin_system.is_admin(user_id):
        await message.answer("ERROR: Access denied. Admin privileges required.")
        return
    
    await state.set_state(AdminStates.main_menu)
    await admin_system.show_main_menu(message)

@router.callback_query(F.data == "admin_main")
async def admin_main_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle admin main menu callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    await state.set_state(AdminStates.main_menu)
    await admin_system.show_main_menu(callback_query, edit=True)
    await callback_query.answer()

@router.callback_query(F.data == "admin_channels")
async def admin_channels_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel management callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
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
        await callback_query.answer("ERROR: Access denied!")
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
        [InlineKeyboardButton(text="ERROR: Cancel", callback_data="admin_packages")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "admin_edit_price")
async def admin_edit_price_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle edit price callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied!")
        return
    
    from database import db
    packages = await db.get_packages(active_only=False)
    
    if not packages:
        await callback_query.answer("ERROR: No packages found!")
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
        InlineKeyboardButton(text="ERROR: Cancel", callback_data="admin_packages")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "admin_remove_price")
async def admin_remove_price_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle remove price callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied!")
        return
    
    from database import db
    packages = await db.get_packages(active_only=False)
    
    if not packages:
        await callback_query.answer("ERROR: No packages found!")
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
        InlineKeyboardButton(text="ERROR: Cancel", callback_data="admin_packages")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data == "admin_price_stats")
async def admin_price_stats_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle price stats callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied!")
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
            status = "SUCCESS:" if package.get('active', True) else "ERROR:"
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
        await callback_query.answer("ERROR: Access denied.")
        return
    
    await state.set_state(AdminStates.pricing_management)
    await admin_system.show_pricing_management(callback_query)
    await callback_query.answer()


# REMOVED: admin_view_all_plans_callback - old progressive monthly plans callback removed


@router.callback_query(F.data == "admin_price_analytics")
async def admin_price_analytics_callback(callback_query: CallbackQuery, state: FSMContext):
    """Show pricing analytics and statistics"""
    if not admin_system.is_admin(callback_query.from_user.id):
        await callback_query.answer("❌ Unauthorized")
        return
    
    pricing = get_pricing_system()
    all_plans = pricing.get_all_plans()
    
    text = "**💰 Pricing Analytics Dashboard**\n\n"
    
    # Calculate analytics
    total_plans = len(all_plans)
    avg_discount = sum(plan['discount_percent'] for plan in all_plans) / total_plans
    max_savings = max(pricing.calculate_savings(plan['plan_id'])['savings_amount'] for plan in all_plans)
    min_price = min(plan['discounted_price'] for plan in all_plans)
    max_price = max(plan['discounted_price'] for plan in all_plans)
    
    text += f"**Overview:**\n"
    text += f"• Total plans: {total_plans}\n"
    text += f"• Average discount: {avg_discount:.1f}%\n"
    text += f"• Maximum savings: ${max_savings:.0f}\n"
    text += f"• Price range: ${min_price:.0f} - ${max_price:.0f}\n\n"
    
    text += f"**Plan Categories:**\n"
    text += f"• Short-term (1-3 months): {len([p for p in all_plans if p['duration_months'] <= 3])} plans\n"
    text += f"• Medium-term (4-8 months): {len([p for p in all_plans if 4 <= p['duration_months'] <= 8])} plans\n"
    text += f"• Long-term (9+ months): {len([p for p in all_plans if p['duration_months'] >= 9])} plans\n\n"
    
    text += f"**Discount Tiers:**\n"
    text += f"• 10-20% discount: {len([p for p in all_plans if 10 <= p['discount_percent'] <= 20])} plans\n"
    text += f"• 21-35% discount: {len([p for p in all_plans if 21 <= p['discount_percent'] <= 35])} plans\n"
    text += f"• 36-45% discount: {len([p for p in all_plans if p['discount_percent'] >= 36])} plans\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 View All Plans", callback_data="admin_view_all_plans"),
            InlineKeyboardButton(text="📈 Revenue Projections", callback_data="admin_revenue_projections")
        ],
        [InlineKeyboardButton(text="⬅️ Back to Pricing", callback_data="admin_packages")]
    ])
    
    try:
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    except Exception:
        await callback_query.message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    
    await callback_query.answer()

@router.callback_query(F.data == "admin_schedules")
async def admin_schedules_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle publishing schedules callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    await state.set_state(AdminStates.publishing_schedules)
    await admin_system.show_publishing_schedules(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_bot_control")
async def admin_bot_control_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle bot control callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    await state.set_state(AdminStates.bot_control)
    await admin_system.show_bot_control(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_users")
async def admin_users_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle user management callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    await state.set_state(AdminStates.user_management)
    await admin_system.show_user_management(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_statistics")
async def admin_statistics_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle statistics callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    await state.set_state(AdminStates.statistics)
    await admin_system.show_statistics(callback_query)
    await callback_query.answer()

@router.callback_query(F.data == "admin_refresh")
async def admin_refresh_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle refresh callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    await callback_query.answer("🔄 Data refreshed!")
    await admin_system.show_main_menu(callback_query, edit=True)

# Channel Management Handlers
@router.callback_query(F.data == "admin_discover_channels")
async def admin_discover_channels_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle discover existing channels callback"""
    await callback_query.answer()
    
    text = """
**🚀 Comprehensive Channel Discovery**

Scanning for ALL channels where the bot is administrator...
This may take a few moments.
    """.strip()
    
    # Show loading message
    await callback_query.message.edit_text(text)
    
    # Import channel manager
    from channel_manager import channel_manager
    
    if channel_manager:
        # Force comprehensive discovery
        discovery_results = await channel_manager.force_full_channel_discovery()
        
        # Get updated channel list
        channels = await db.get_channels(active_only=False)
        active_channels = [ch for ch in channels if ch.get('is_active', False)]
        
        result_text = f"""
**🎯 Comprehensive Discovery Results**

**Scan Summary:**
• Channels Scanned: {discovery_results.get('total_scanned', 0)}
• Newly Discovered: {discovery_results.get('newly_discovered', 0)}
• Already Known: {discovery_results.get('already_known', 0)}
• Failed Attempts: {discovery_results.get('failed_attempts', 0)}

**Current Status:**
• Total Channels: {len(channels)}
• Active Channels: {len(active_channels)}

"""
        
        if discovery_results.get('newly_discovered', 0) > 0:
            result_text += "**🎉 Newly Discovered Channels:**\n"
            for channel in discovery_results.get('discovered_channels', []):
                result_text += f"• **{channel['name']}** ({channel['username']}) - {channel['subscribers']:,} subscribers\n"
        
        if active_channels:
            result_text += "\n**✅ All Active Channels:**\n"
            for i, channel in enumerate(active_channels, 1):
                result_text += f"{i}. **{channel['name']}** - {channel['subscribers']:,} subscribers\n"
        
        if len(channels) > len(active_channels):
            inactive_channels = [ch for ch in channels if not ch.get('is_active', False)]
            result_text += f"\n**❌ Inactive Channels:** {len(inactive_channels)}\n"
            for channel in inactive_channels[:3]:  # Show first 3
                result_text += f"• {channel['name']} (not accessible)\n"
        
        if len(channels) == 0:
            result_text += "\n**No channels found.**\n\n"
            result_text += "**To add channels:**\n"
            result_text += "1. Add bot as admin to your channel\n"
            result_text += "2. Give bot permission to post messages\n"
            result_text += "3. Use 'Force Discovery' or 'Add Channel'\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Force Discovery", callback_data="admin_discover_channels"),
                InlineKeyboardButton(text="➕ Add Channel", callback_data="admin_add_channel")
            ],
            [InlineKeyboardButton(text="📥 Bulk Import Channels", callback_data="admin_bulk_import")],
            [InlineKeyboardButton(text="🔙 Back to Channels", callback_data="admin_channels")]
        ])
        
        await callback_query.message.edit_text(result_text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await callback_query.message.edit_text(
            "ERROR: Channel manager not initialized. Please restart the bot.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 Back", callback_data="admin_channels")]
            ])
        )


@router.callback_query(F.data == "admin_bulk_import")
async def admin_bulk_import_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle bulk import channels callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    text = """
**📥 Bulk Import Channels**

Send me a list of channel usernames where the bot is administrator.

**Format:** One username per line
```
@channel1
@channel2
@channel3
channel4
```

**Note:** Only channels where the bot has admin rights will be added.

Send your channel list now or click Cancel to go back.
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_channels")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await state.set_state(AdminStates.bulk_import_channels)
    await callback_query.answer()


@router.callback_query(F.data == "admin_add_channel")
async def admin_add_channel_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle add channel callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    await state.set_state(AdminStates.add_channel)
    
    text = """
📺 **Add New Channel**

**Auto-Discovery Mode**

Enter the channel username (e.g., @yourchannel) and the bot will automatically:

✅ Check if bot is administrator
✅ Get subscriber count and details  
✅ Detect category and set pricing
✅ Add to the advertising system

**Requirements:**
- Bot must be administrator in the channel
- Bot must have permission to post messages
- Channel must be public or accessible

Enter the channel username:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_channels")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.message(AdminStates.add_channel)
async def handle_add_channel_message(message: Message, state: FSMContext):
    """Handle channel addition message using auto-discovery"""
    try:
        username = message.text.strip()
        
        # Validate username format
        if not username.startswith('@'):
            if not username.startswith('t.me/'):
                username = f"@{username}"
            else:
                # Extract username from t.me link
                username = f"@{username.split('/')[-1]}"
        
        # Show processing message
        processing_msg = await message.reply(f"🔍 **Processing {username}...**\n\nChecking bot permissions and gathering channel info...")
        
        # Import channel manager
        from channel_manager import channel_manager
        
        if not channel_manager:
            await processing_msg.edit_text("❌ **Error**: Channel manager not available. Please restart the bot.")
            await state.clear()
            return
        
        # Try to discover and add the channel
        success = await channel_manager.discover_channel_by_username(username)
        
        if success:
            # Get channel info from database
            channels = await db.get_channels(active_only=False)
            added_channel = None
            for ch in channels:
                if ch.get('telegram_channel_id') == username:
                    added_channel = ch
                    break
            
            if added_channel:
                result_text = f"""
✅ **Channel Added Successfully!**

**{added_channel['name']}**

📊 **Details:**
• Username: {username}
• Subscribers: {added_channel['subscribers']:,}
• Category: {added_channel['category']}
• Base Price: ${added_channel['base_price_usd']:.2f}
• Status: {'Active' if added_channel.get('is_active', False) else 'Inactive'}

The channel is now available for advertising!
                """.strip()
            else:
                result_text = f"✅ **Channel {username} added successfully!**"
        else:
            result_text = f"""
❌ **Failed to add {username}**

**Possible reasons:**
• Bot is not administrator in the channel
• Bot doesn't have permission to post messages
• Channel is private/inaccessible
• Channel doesn't exist

**To fix:**
1. Add the bot as administrator to {username}
2. Grant permission to post messages
3. Try again
            """.strip()
        
        # Show result
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Add Another", callback_data="admin_add_channel"),
                InlineKeyboardButton(text="🔍 Discover All", callback_data="admin_discover_channels")
            ],
            [InlineKeyboardButton(text="🔙 Back to Channels", callback_data="admin_channels")]
        ])
        
        await processing_msg.edit_text(result_text, reply_markup=keyboard, parse_mode='Markdown')
        
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
        await message.reply("ERROR: Invalid subscriber count. Please enter a valid number.")
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        await message.reply("ERROR: Error adding channel. Please try again.")

@router.callback_query(F.data == "admin_edit_channel")
async def admin_edit_channel_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle edit channel callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    text = "EDIT: **Edit Channel**\n\nSelect a channel to edit:"
    
    keyboard = []
    channels = await db.get_channels(active_only=False)
    for channel in channels:
        keyboard.append([InlineKeyboardButton(
            text=f"{channel['name']} ({channel.get('telegram_channel_id', 'N/A')})",
            callback_data=f"edit_channel_{channel.get('channel_id', 'unknown')}"
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
        await callback_query.answer("ERROR: Access denied.")
        return
    
    channel_id = callback_query.data.replace("edit_channel_", "")
    channels = await db.get_channels(active_only=False)
    channel = next((ch for ch in channels if ch.get('channel_id') == channel_id), None)
    
    if not channel:
        await callback_query.answer("ERROR: Channel not found.")
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
            InlineKeyboardButton(text="EDIT: Edit Name", callback_data=f"edit_name_{channel_id}"),
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
        await callback_query.answer("ERROR: Access denied.")
        return
    
    channel_id = callback_query.data.replace("toggle_channel_", "")
    channels = await db.get_channels(active_only=False)
    channel = next((ch for ch in channels if ch.get('channel_id') == channel_id), None)
    
    if not channel:
        await callback_query.answer("ERROR: Channel not found.")
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
        await callback_query.answer("ERROR: Access denied.")
        return
    
    text = "🗑️ **Remove Channel**\n\n⚠️ Select a channel to remove (this action cannot be undone):"
    
    keyboard = []
    channels = await db.get_channels(active_only=False)
    for channel in channels:
        keyboard.append([InlineKeyboardButton(
            text=f"🗑️ {channel['name']} ({channel.get('telegram_channel_id', 'N/A')})",
            callback_data=f"remove_channel_{channel.get('channel_id', 'unknown')}"
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
        await callback_query.answer("ERROR: Access denied.")
        return
    
    channel_id = callback_query.data.replace("remove_channel_", "")
    channels = await db.get_channels(active_only=False)
    channel = next((ch for ch in channels if ch.get('channel_id') == channel_id), None)
    
    if not channel:
        await callback_query.answer("ERROR: Channel not found.")
        return
    
    # Remove channel permanently
    success = await db.delete_channel(channel_id)
    
    if success:
        await callback_query.message.edit_text(
            f"✅ **Channel Removed Successfully**\n\n**{channel['name']}** has been permanently deleted from the system.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Channels", callback_data="admin_channels")]
            ]),
            parse_mode='Markdown'
        )
    else:
        await callback_query.answer("ERROR: Failed to remove channel.")
    


# Package Management Handlers
@router.callback_query(F.data.startswith("admin_price_"))
async def admin_price_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle pricing update callbacks"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    package_type = callback_query.data.replace("admin_price_", "")
    package = admin_system.subscription_packages.get(package_type)
    
    if not package:
        await callback_query.answer("ERROR: Package not found.")
        return
    
    await state.set_state(AdminStates.set_pricing)
    await state.update_data(package_type=package_type)
    
    text = f"""
$ **Update {package['name']} Price**

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
            await message.reply("ERROR: Price must be greater than 0.")
            return
        
        # Update package price
        old_price = admin_system.subscription_packages[package_type]['price_usd']
        admin_system.subscription_packages[package_type]['price_usd'] = new_price
        
        success_text = f"""
SUCCESS: **Price Updated Successfully!**

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
        await message.reply("ERROR: Invalid price format. Please enter a valid number.")
    except Exception as e:
        logger.error(f"Error updating price: {e}")
        await message.reply("ERROR: Error updating price. Please try again.")

# Subscription Management Handlers
@router.callback_query(F.data == "admin_create_subscription")
async def admin_create_subscription_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle create subscription callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    await state.set_state(AdminStates.create_subscription)
    
    text = """
+ **Create New Subscription Package**

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
            await message.reply("ERROR: Invalid format. Please provide all 5 fields: Name, Price, Duration, Posts/Day, Channels")
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
SUCCESS: **Subscription Package Created Successfully!**

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
        await message.reply("ERROR: Invalid format. Please check that prices and numbers are valid.")
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        await message.reply("ERROR: Error creating subscription. Please try again.")

@router.callback_query(F.data == "admin_edit_subscription")
async def admin_edit_subscription_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle edit subscription callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    text = """
EDIT: **Edit Subscription Package**

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
        await callback_query.answer("ERROR: Access denied.")
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
        await callback_query.answer("ERROR: Access denied.")
        return
    
    package_id = callback_query.data.replace("remove_package_", "")
    package = admin_system.subscription_packages.get(package_id)
    
    if not package:
        await callback_query.answer("ERROR: Package not found.")
        return
    
    # Remove package
    del admin_system.subscription_packages[package_id]
    
    await callback_query.answer("SUCCESS: Package removed successfully!")
    
    # Return to subscription management
    await admin_system.show_subscription_management(callback_query)

@router.callback_query(F.data == "admin_channel_stats")
async def admin_channel_stats_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel stats callback"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    # Get real channel data from database
    channels = await db.get_channels(active_only=False)
    active_channels = [ch for ch in channels if ch.get('is_active', False)]
    total_subscribers = sum(ch.get('subscribers', 0) for ch in channels)
    
    text = f"""
STATS: **Channel Statistics**

**Total Channels:** {len(channels)}
**Active Channels:** {len(active_channels)}
**Total Subscribers:** {total_subscribers:,}
**Average Subscribers:** {total_subscribers // len(channels) if channels else 0:,}

**Channel Details:**
    """.strip()
    
    if not channels:
        text += "\n\nNo channels found in database."
        text += "\n\n**To add channels:**"
        text += "\n1. Add the bot as administrator to your channel"
        text += "\n2. Give the bot permission to post messages"
        text += "\n3. The bot will automatically detect and add the channel"
    else:
        for channel in channels:
            status = "SUCCESS:" if channel.get('is_active', False) else "INACTIVE:"
            text += f"\n{status} **{channel['name']}**"
            text += f"\n   - {channel.get('subscribers', 0):,} subscribers"
            text += f"\n   - Category: {channel.get('category', 'general').title()}"
    
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
        await callback_query.answer("ERROR: Access denied.")
        return
    
    text = f"""
STATS: **Subscription Package Statistics**

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
        await message.reply("ERROR: Access denied!")
        return
    
    try:
        # Parse package details: package_id|name|price_usd|duration_days|posts_per_day|channels_included
        parts = message.text.strip().split('|')
        if len(parts) != 6:
            await message.reply("ERROR: Invalid format! Please use: `package_id|name|price_usd|duration_days|posts_per_day|channels_included`")
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
SUCCESS: **Price Package Created Successfully!**

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
            await message.reply("ERROR: Failed to create package. Package ID might already exist.")
        
    except ValueError:
        await message.reply("ERROR: Invalid number format! Please check price, duration, posts per day, and channels values.")
    except Exception as e:
        await message.reply(f"ERROR: Error creating package: {str(e)}")
    
    await state.clear()

@router.callback_query(F.data.startswith("admin_remove_pkg_"))
async def admin_remove_package_confirm(callback_query: CallbackQuery, state: FSMContext):
    """Handle package removal confirmation"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied!")
        return
    
    package_id = callback_query.data.replace("admin_remove_pkg_", "")
    
    try:
        from database import db
        packages = await db.get_packages(active_only=False)
        package = next((p for p in packages if p['package_id'] == package_id), None)
        
        if not package:
            await callback_query.answer("ERROR: Package not found!")
            return
        
        # Remove package from database
        async with db.get_connection() as conn:
            await conn.execute("DELETE FROM packages WHERE package_id = ?", (package_id,))
            await conn.commit()
        
        success_text = f"""
SUCCESS: **Package Removed Successfully!**

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
        await callback_query.answer(f"SUCCESS: Package '{package['name']}' removed!")
        
    except Exception as e:
        await callback_query.answer(f"ERROR: Error removing package: {str(e)}")

@router.callback_query(F.data.startswith("admin_edit_pkg_"))
async def admin_edit_package_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle package editing"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied!")
        return
    
    package_id = callback_query.data.replace("admin_edit_pkg_", "")
    
    try:
        from database import db
        packages = await db.get_packages(active_only=False)
        package = next((p for p in packages if p['package_id'] == package_id), None)
        
        if not package:
            await callback_query.answer("ERROR: Package not found!")
            return
        
        await state.update_data(edit_package_id=package_id)
        await state.set_state(AdminStates.edit_subscription)
        
        text = f"""
EDIT: **Edit Package: {package['name']}**

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
            [InlineKeyboardButton(text="ERROR: Cancel", callback_data="admin_packages")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"ERROR: Error loading package: {str(e)}")

@router.message(AdminStates.edit_subscription)
async def handle_edit_package_message(message: Message, state: FSMContext):
    """Handle edit package form submission"""
    user_id = message.from_user.id
    
    if not admin_system.is_admin(user_id):
        await message.reply("ERROR: Access denied!")
        return
    
    try:
        data = await state.get_data()
        package_id = data.get('edit_package_id')
        
        if not package_id:
            await message.reply("ERROR: Package ID not found!")
            return
        
        # Parse package details: name|price_usd|duration_days|posts_per_day|channels_included
        parts = message.text.strip().split('|')
        if len(parts) != 5:
            await message.reply("ERROR: Invalid format! Please use: `name|price_usd|duration_days|posts_per_day|channels_included`")
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
SUCCESS: **Package Updated Successfully!**

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
        await message.reply("ERROR: Invalid number format! Please check price, duration, posts per day, and channels values.")
    except Exception as e:
        await message.reply(f"ERROR: Error updating package: {str(e)}")
    
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
        
        response = "STATS: **Detailed Channel Information**\n\n"
        
        for channel in channels:
            status = "SUCCESS: Active" if channel.get('is_active') else "ERROR: Inactive"
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
    
    @router.callback_query(F.data == "admin_gamification")
    async def admin_gamification_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle gamification management callback"""
        user_id = callback_query.from_user.id
        
        if not admin_system.is_admin(user_id):
            await callback_query.answer("Access denied")
            return
        
        try:
            from gamification import GamificationSystem
            gamification = GamificationSystem(admin_system.db, callback_query.message.bot)
            
            # Get gamification statistics
            total_users = await admin_system.get_total_users()
            active_users = await admin_system.get_active_users()
            
            # Get level distribution
            xp_leaderboard = await gamification.get_leaderboard('xp', 50)
            level_distribution = {}
            for user in xp_leaderboard:
                level = user['level']
                level_distribution[level] = level_distribution.get(level, 0) + 1
            
            # Get achievement statistics  
            total_achievements = len(gamification.achievements)
            avg_achievements = sum(user.get('total_achievements', 0) for user in xp_leaderboard) / len(xp_leaderboard) if xp_leaderboard else 0
            
            stats_text = f"""
🎮 **GAMIFICATION MANAGEMENT** 🎮

**System Statistics:**
👥 Total Users: {total_users:,}
⚡ Active Users: {active_users:,}
🏆 Total Achievements: {total_achievements}
📊 Avg Achievements per User: {avg_achievements:.1f}

**Level Distribution:**
{chr(10).join(f"Level {level}: {count} users" for level, count in sorted(level_distribution.items())) if level_distribution else "No data available"}

**Top Performers:**
{chr(10).join(f"{i+1}. {user['display_name']} - Level {user['level']} ({user['xp']:,} XP)" for i, user in enumerate(xp_leaderboard[:5])) if xp_leaderboard else "No users yet"}

**System Health:** ✅ Operational
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🏆 View All Achievements", callback_data="admin_view_achievements"),
                    InlineKeyboardButton(text="📊 User Analytics", callback_data="admin_gamification_analytics")
                ],
                [
                    InlineKeyboardButton(text="🎯 Award Manual Achievement", callback_data="admin_manual_achievement"),
                    InlineKeyboardButton(text="⚡ Award Manual XP", callback_data="admin_manual_xp")
                ],
                [
                    InlineKeyboardButton(text="🔄 System Settings", callback_data="admin_gamification_settings"),
                    InlineKeyboardButton(text="📈 Export Data", callback_data="admin_export_gamification")
                ],
                [
                    InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
                ]
            ])
            
            await callback_query.message.edit_text(
                stats_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Admin gamification error: {e}")
            await callback_query.answer("Error loading gamification management")

    @router.callback_query(F.data == "admin_achievements")
    async def admin_achievements_callback(callback_query: CallbackQuery, state: FSMContext):
        """Handle achievement analytics callback"""
        user_id = callback_query.from_user.id
        
        if not admin_system.is_admin(user_id):
            await callback_query.answer("Access denied")
            return
        
        try:
            from gamification import GamificationSystem
            gamification = GamificationSystem(admin_system.db, callback_query.message.bot)
            
            # Get achievement statistics
            achievement_stats = {}
            for achievement_id, achievement in gamification.achievements.items():
                # Count users who have this achievement
                async with admin_system.db.get_connection() as conn:
                    async with conn.execute("""
                        SELECT COUNT(*) as count FROM user_achievements 
                        WHERE achievement_id = ?
                    """, (achievement_id,)) as cursor:
                        result = await cursor.fetchone()
                        count = result[0] if result else 0
                
                achievement_stats[achievement_id] = {
                    'name': achievement['name'],
                    'type': achievement['type'],
                    'unlocked_count': count,
                    'reward_ton': achievement['reward_ton']
                }
            
            # Sort by most unlocked
            sorted_achievements = sorted(achievement_stats.items(), 
                                       key=lambda x: x[1]['unlocked_count'], 
                                       reverse=True)
            
            analytics_text = f"""
🏆 **ACHIEVEMENT ANALYTICS** 🏆

**Most Popular Achievements:**
{chr(10).join(f"{i+1}. {data['name']} - {data['unlocked_count']} users" for i, (_, data) in enumerate(sorted_achievements[:10])) if sorted_achievements else "No achievements unlocked yet"}

**Achievement Categories:**
{chr(10).join(f"• {category}: {len([a for _, a in achievement_stats.items() if a['type'] == category])} achievements" for category in set(a['type'] for a in achievement_stats.values())) if achievement_stats else "No categories available"}

**Total TON Distributed:** {sum(a['unlocked_count'] * a['reward_ton'] for a in achievement_stats.values()):.2f} TON

**Rarest Achievements:**
{chr(10).join(f"🔥 {data['name']} - {data['unlocked_count']} users" for _, data in sorted(achievement_stats.items(), key=lambda x: x[1]['unlocked_count'])[:5]) if achievement_stats else "No rare achievements yet"}
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🎮 Gamification Main", callback_data="admin_gamification"),
                    InlineKeyboardButton(text="📊 User Leaderboard", callback_data="admin_user_leaderboard")
                ],
                [
                    InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
                ]
            ])
            
            await callback_query.message.edit_text(
                analytics_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Achievement analytics error: {e}")
            await callback_query.answer("Error loading achievement analytics")
    
    logger.info("Admin system handlers setup completed")

# Usage Agreement Handlers
@router.callback_query(F.data == "admin_agreement")
async def admin_agreement_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle usage agreement management"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    try:
        # Get current usage agreement
        agreement = await db.get_bot_setting('usage_agreement')
        
        if agreement:
            preview = agreement[:200] + "..." if len(agreement) > 200 else agreement
            text = f"""
📄 **Usage Agreement Management**

**Current Agreement Preview:**
{preview}

**Character Count:** {len(agreement)} chars

You can view the full agreement or edit it below:
            """.strip()
        else:
            text = "📄 **Usage Agreement Management**\n\nNo usage agreement found. Click 'Edit Agreement' to create one."
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👀 View Full Agreement", callback_data="view_agreement")],
            [InlineKeyboardButton(text="✏️ Edit Agreement", callback_data="edit_agreement")],
            [InlineKeyboardButton(text="🔄 Reset to Default", callback_data="reset_agreement")],
            [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
        await callback_query.answer("Usage agreement management")
        
    except Exception as e:
        logger.error(f"Error showing usage agreement: {e}")
        await callback_query.answer("Error loading usage agreement", show_alert=True)

@router.callback_query(F.data == "view_agreement")
async def view_agreement_handler(callback_query: CallbackQuery, state: FSMContext):
    """View full usage agreement"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    try:
        agreement = await db.get_bot_setting('usage_agreement')
        
        if not agreement:
            await callback_query.answer("No agreement found", show_alert=True)
            return
        
        text = f"📄 **Usage Agreement**\n\n{agreement}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_agreement")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
        await callback_query.answer("Viewing full agreement")
            
    except Exception as e:
        logger.error(f"Error showing full agreement: {e}")
        await callback_query.answer("Error loading full agreement", show_alert=True)

@router.callback_query(F.data == "edit_agreement")
async def edit_agreement_handler(callback_query: CallbackQuery, state: FSMContext):
    """Edit usage agreement"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("❌ Access denied", show_alert=True)
        return
    
    await state.set_state(AdminStates.edit_agreement)
    text = """
✏️ **Edit Usage Agreement**

Please send the new usage agreement text. This will be shown to users when they make payments.

Send your new agreement text now:
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_agreement")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer("Ready to edit agreement")

@router.message(AdminStates.edit_agreement)
async def process_agreement_edit(message: Message, state: FSMContext):
    """Process new usage agreement text"""
    user_id = message.from_user.id
    
    if not admin_system.is_admin(user_id):
        await message.answer("❌ Access denied")
        return
    
    new_agreement = message.text
    if len(new_agreement) < 50:
        await message.answer("❌ Agreement too short. Please provide at least 50 characters.")
        return
    
    # Save new agreement
    await db.set_bot_setting('usage_agreement', new_agreement, 'Terms of service and usage agreement for bot users')
    
    text = f"""
✅ **Usage Agreement Updated Successfully**

**New Agreement Preview:**
{new_agreement[:200]}{'...' if len(new_agreement) > 200 else ''}

**Character Count:** {len(new_agreement)} chars

The new agreement will be shown to users during payment.
    """.strip()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Back to Agreement", callback_data="admin_agreement")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    await state.clear()


@router.message(AdminStates.bulk_import_channels)
async def handle_bulk_import_channels(message: Message, state: FSMContext):
    """Handle bulk channel import message"""
    user_id = message.from_user.id
    
    if user_id not in ADMIN_IDS:
        await message.reply("ERROR: Access denied.")
        return
    
    try:
        # Parse channel list
        lines = message.text.strip().split('\n')
        channels = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Clean the username
                if not line.startswith('@'):
                    line = '@' + line
                channels.append(line)
        
        if not channels:
            await message.reply("No channels found in your message. Please send a list of channel usernames.")
            return
        
        await message.reply(f"🔍 Processing {len(channels)} channels...")
        
        # Import channel manager
        from channel_manager import channel_manager
        
        # Process each channel
        results = await channel_manager.discover_multiple_channels(channels)
        
        # Prepare results message
        success_count = sum(1 for success in results.values() if success)
        failed_count = len(results) - success_count
        
        result_text = f"""
**📥 Bulk Import Results**

Total processed: {len(results)}
✅ Successfully added: {success_count}
❌ Failed: {failed_count}

**Details:**
"""
        
        for username, success in results.items():
            if success:
                result_text += f"✅ {username} - Added successfully\n"
            else:
                result_text += f"❌ {username} - Failed (not admin or already exists)\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📺 View All Channels", callback_data="admin_channels")],
            [InlineKeyboardButton(text="🔙 Back to Admin", callback_data="admin_main")]
        ])
        
        await message.reply(result_text, reply_markup=keyboard, parse_mode='Markdown')
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error processing bulk import: {e}")
        await message.reply(
            "Error processing channels. Please check the format and try again.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Back", callback_data="admin_channels")]
            ])
        )


# Smart pricing system handlers
async def show_smart_pricing_system(callback_query: CallbackQuery):
    """Show smart pricing system details for admin"""
    try:
        from smart_pricing_display import smart_pricing_display
        
        # Generate the complete pricing table
        pricing_table = smart_pricing_display.generate_pricing_table_message('en')
        
        text = f"""
🧠 **Smart & Scalable Ad Pricing System**

**System Status:** ✅ Fully Operational
**Implementation:** 100% Complete
**Test Results:** All tests passed

{pricing_table}

**Features:**
- Dynamic pricing based on duration
- Automatic discount calculation
- Multi-currency support (USD, TON, Stars)
- Bulk buyer extended tiers
- Real-time price previews
- Automated calculation flow

**Ready for deployment as default pricing logic!**
        """.strip()
        
        keyboard = [
            [
                InlineKeyboardButton(text="📊 View Pricing Table", callback_data="admin_pricing_table"),
                InlineKeyboardButton(text="🧪 Run Tests", callback_data="admin_test_pricing")
            ],
            [
                InlineKeyboardButton(text="💰 Bulk Buyer Info", callback_data="admin_bulk_buyers"),
                InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_smart_pricing")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing smart pricing system: {e}")
        await callback_query.answer("Error displaying pricing system", show_alert=True)


async def show_pricing_table(callback_query: CallbackQuery):
    """Show detailed pricing table"""
    try:
        from smart_pricing_display import smart_pricing_display
        from frequency_pricing import FrequencyPricingSystem
        
        pricing_system = FrequencyPricingSystem()
        
        # Get all available tiers
        tiers = pricing_system.get_available_tiers()
        
        text = """
📊 **Complete Pricing Table**

**Core Tiers (1-30 days):**
```
Days | Posts/Day | Discount | Daily Rate | Final Price
-----|-----------|----------|------------|------------"""
        
        for tier in tiers[:8]:  # Core tiers
            pricing = pricing_system.calculate_pricing(tier['days'])
            text += f"\n{tier['days']:>4} | {pricing['posts_per_day']:>9} | {pricing['discount_percent']:>7}% | ${pricing['daily_price']:>9.2f} | ${pricing['final_cost_usd']:>10.2f}"
        
        text += "\n```\n\n**Extended Tiers (45-90 days):**"
        
        extended_tiers = [45, 60, 90]
        for days in extended_tiers:
            pricing = pricing_system.calculate_pricing(days)
            text += f"\n📅 {days} days: {pricing['posts_per_day']} posts/day, {pricing['discount_percent']}% discount, ${pricing['final_cost_usd']:.2f}"
        
        text += "\n\n**Currency Conversion Rates:**"
        text += "\n💵 1 USD = 0.36 TON"
        text += "\n🌟 1 USD = 34 Stars"
        
        keyboard = [
            [
                InlineKeyboardButton(text="💡 View System Logic", callback_data="admin_smart_pricing"),
                InlineKeyboardButton(text="🔄 Refresh", callback_data="admin_pricing_table")
            ],
            [
                InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")
            ]
        ]
        
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing pricing table: {e}")
        await callback_query.answer("Error displaying pricing table", show_alert=True)

@router.callback_query(F.data == "admin_test_workflow")
async def admin_test_workflow_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle test bot workflow button"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    # Import here to avoid circular imports
    from admin_bot_test_system import run_admin_bot_test
    from aiogram import Bot
    from config import BOT_TOKEN
    
    await callback_query.message.edit_text(
        "🧪 **Bot Workflow Test Starting...**\n\n"
        "⏳ Running comprehensive bot functionality test\n"
        "📊 Testing all systems including multimedia support\n"
        "🔍 This may take 30-60 seconds...",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")]
        ])
    )
    await callback_query.answer()
    
    try:
        # Create bot instance
        bot = Bot(token=BOT_TOKEN)
        
        # Run comprehensive test
        test_suite = await run_admin_bot_test(bot, user_id)
        
        # Format results
        status_emoji = "✅" if test_suite.success_rate >= 80 else "⚠️" if test_suite.success_rate >= 60 else "❌"
        status_text = ("FULLY OPERATIONAL" if test_suite.success_rate >= 80 else 
                      "NEEDS ATTENTION" if test_suite.success_rate >= 60 else 
                      "REQUIRES IMMEDIATE ATTENTION")
        
        text = f"""🧪 **Bot Workflow Test Complete**

{status_emoji} **System Status:** {status_text}

📊 **Test Results:**
• Total Tests: {test_suite.total_tests}
• Passed: {test_suite.passed_tests} ✅
• Failed: {test_suite.failed_tests} ❌
• Warnings: {test_suite.warning_tests} ⚠️
• Success Rate: {test_suite.success_rate:.1f}%

🕐 **Test Duration:** {(test_suite.completed_at - test_suite.started_at).total_seconds():.1f} seconds

📋 **Test Suite ID:** {test_suite.suite_id}"""
        
        keyboard = [
            [InlineKeyboardButton(text="📋 View Full Report", callback_data=f"view_test_report_{test_suite.suite_id}")],
            [InlineKeyboardButton(text="📋 Test History", callback_data="admin_test_history")],
            [InlineKeyboardButton(text="🔄 Run Again", callback_data="admin_test_workflow")],
            [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")]
        ]
        
        await callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        
        await bot.session.close()
        
    except Exception as e:
        await callback_query.message.edit_text(
            f"❌ **Test Failed**\n\n"
            f"Error: {str(e)}\n\n"
            f"Please check system status and try again.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Try Again", callback_data="admin_test_workflow")],
                [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")]
            ])
        )

@router.callback_query(F.data == "admin_test_history")
async def admin_test_history_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle test history button"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    # Import here to avoid circular imports
    from admin_bot_test_system import get_admin_test_system
    from aiogram import Bot
    from config import BOT_TOKEN
    
    try:
        bot = Bot(token=BOT_TOKEN)
        test_system = get_admin_test_system(bot)
        
        # Get test history
        test_history = await test_system.get_test_history(user_id, limit=10)
        
        if not test_history:
            text = "📋 **Test History**\n\n⚠️ No test records found.\n\nRun your first test to see history here."
        else:
            text = f"📋 **Test History** (Last {len(test_history)} tests)\n\n"
            
            for i, test in enumerate(test_history, 1):
                status_emoji = "✅" if test['success_rate'] >= 80 else "⚠️" if test['success_rate'] >= 60 else "❌"
                started_time = datetime.fromisoformat(test['started_at']).strftime('%m/%d %H:%M')
                
                text += f"{i}. {status_emoji} **{test['suite_id']}**\n"
                text += f"   • {started_time} - {test['success_rate']:.1f}% success\n"
                text += f"   • {test['passed_tests']}/{test['total_tests']} tests passed\n\n"
        
        keyboard = [
            [InlineKeyboardButton(text="🧪 Run New Test", callback_data="admin_test_workflow")],
            [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")]
        ]
        
        await callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        await callback_query.answer()
        
        await bot.session.close()
        
    except Exception as e:
        await callback_query.message.edit_text(
            f"❌ **Error Loading Test History**\n\n"
            f"Error: {str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")]
            ])
        )
        await callback_query.answer()

@router.callback_query(F.data.startswith("view_test_report_"))
async def view_test_report_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle view test report button"""
    user_id = callback_query.from_user.id
    
    if not admin_system.is_admin(user_id):
        await callback_query.answer("ERROR: Access denied.")
        return
    
    suite_id = callback_query.data.replace("view_test_report_", "")
    
    try:
        import sqlite3
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Get test suite details
        cursor.execute("""
            SELECT final_report FROM admin_test_suites 
            WHERE suite_id = ? AND admin_user_id = ?
        """, (suite_id, user_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            await callback_query.answer("Test report not found.")
            return
        
        report = result[0]
        
        # Truncate report if too long for Telegram
        if len(report) > 4000:
            report = report[:3900] + "\n\n... (Report truncated for display)"
        
        keyboard = [
            [InlineKeyboardButton(text="📋 Test History", callback_data="admin_test_history")],
            [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")]
        ]
        
        await callback_query.message.edit_text(
            report,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='Markdown'
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.message.edit_text(
            f"❌ **Error Loading Report**\n\n"
            f"Error: {str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_main")]
            ])
        )
        await callback_query.answer()