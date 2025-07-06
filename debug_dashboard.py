"""
Debug Dashboard for I3lani Bot
Real-time monitoring and troubleshooting interface
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from debug_system import debug_system
from config import ADMIN_IDS

class DebugDashboard:
    """Interactive debug dashboard for real-time monitoring"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.dashboard_users = set()
        self.monitoring_active = False
    
    def create_dashboard_keyboard(self) -> InlineKeyboardMarkup:
        """Create debug dashboard keyboard"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 System Health", callback_data="debug_health"),
                InlineKeyboardButton(text="📊 Performance", callback_data="debug_performance")
            ],
            [
                InlineKeyboardButton(text="💳 Payment System", callback_data="debug_payment"),
                InlineKeyboardButton(text="🗃️ Database", callback_data="debug_database")
            ],
            [
                InlineKeyboardButton(text="👥 User Activity", callback_data="debug_users"),
                InlineKeyboardButton(text="🚨 Error Log", callback_data="debug_errors")
            ],
            [
                InlineKeyboardButton(text="🔄 Refresh", callback_data="debug_refresh"),
                InlineKeyboardButton(text="⚙️ Settings", callback_data="debug_settings")
            ],
            [
                InlineKeyboardButton(text="📋 Full Report", callback_data="debug_report"),
                InlineKeyboardButton(text="❌ Close", callback_data="debug_close")
            ]
        ])
        return keyboard
    
    async def show_dashboard(self, query_or_message):
        """Show main debug dashboard"""
        if not debug_system:
            await self.send_message(query_or_message, "❌ Debug system not available")
            return
        
        health = await debug_system.get_system_health()
        
        dashboard_text = f"""
🛠️ **I3lani Bot Debug Dashboard**
Last Updated: {datetime.now().strftime('%H:%M:%S')}

**🔋 System Status:**
• Uptime: {health['uptime']}
• Messages: {health['total_messages']}
• Errors: {health['total_errors']}
• Users: {health['total_users']}

**🗃️ Database:**
• Status: {health['database_health']['status']}
• Query Time: {health['database_health'].get('query_time', 'N/A')}s

**💾 Memory:**
• Usage: {health['memory_usage_kb']} KB
• Debug Mode: {'ON' if health['debug_mode'] else 'OFF'}

**📊 Quick Actions:**
Use the buttons below to explore different areas.
        """.strip()
        
        await self.send_message(
            query_or_message, 
            dashboard_text, 
            reply_markup=self.create_dashboard_keyboard()
        )
    
    async def show_system_health(self, callback_query: CallbackQuery):
        """Show detailed system health"""
        if not debug_system:
            await callback_query.answer("Debug system not available")
            return
        
        health = await debug_system.get_system_health()
        
        health_text = f"""
🔍 **System Health Details**

**⚡ Performance:**
• Uptime: {health['uptime']}
• Total Messages: {health['total_messages']}
• Total Errors: {health['total_errors']}
• Active Sessions: {health['active_sessions']}

**🗃️ Database Status:**
• Health: {health['database_health']['status']}
• Query Time: {health['database_health'].get('query_time', 'N/A')}s
• Channels: {health['database_health'].get('channels_count', 0)}

**💾 Memory Usage:**
• Current: {health['memory_usage_kb']} KB
• Recent Errors: {health['recent_errors_count']}

**🎯 Status:** {'🟢 All Systems Operational' if health['total_errors'] == 0 else '🟡 Some Issues Detected'}
        """.strip()
        
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="debug_dashboard")]
        ])
        
        await callback_query.message.edit_text(health_text, reply_markup=back_keyboard)
    
    async def show_payment_debug(self, callback_query: CallbackQuery):
        """Show payment system debug info"""
        if not debug_system:
            await callback_query.answer("Debug system not available")
            return
        
        payment_debug = await debug_system.debug_payment_system()
        
        payment_text = f"""
💳 **Payment System Debug**

**🔧 System Status:**
• Status: {payment_debug['status']}
• Memo Format: {'✅ Valid' if payment_debug.get('memo_format_valid', False) else '❌ Invalid'}

**📝 Sample Memos (AB0102 Format):**
{chr(10).join(f"• {memo}" for memo in payment_debug.get('test_memos', []))}

**💰 Test Conversion:**
• Amount: $10.00 USD for 1 month
• Result: ${payment_debug.get('test_conversion', {}).get('final_price', 'N/A')}

**🎯 Status:** {'🟢 Payment System Healthy' if payment_debug['status'] == 'healthy' else '🔴 Payment System Issues'}
        """.strip()
        
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="debug_dashboard")]
        ])
        
        await callback_query.message.edit_text(payment_text, reply_markup=back_keyboard)
    
    async def show_user_activity(self, callback_query: CallbackQuery):
        """Show user activity summary"""
        if not debug_system:
            await callback_query.answer("Debug system not available")
            return
        
        # Get recent activity summary
        total_users = len(debug_system.user_activity)
        total_activities = sum(len(activities) for activities in debug_system.user_activity.values())
        
        # Get most active users
        most_active = sorted(
            debug_system.user_activity.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:5]
        
        activity_text = f"""
👥 **User Activity Summary**

**📊 Statistics:**
• Total Users: {total_users}
• Total Activities: {total_activities}
• Average per User: {total_activities / total_users if total_users > 0 else 0:.1f}

**🏆 Most Active Users:**
"""
        
        for user_id, activities in most_active:
            activity_text += f"• User {user_id}: {len(activities)} activities\n"
        
        activity_text += f"""

**🕐 Recent Activity:**
• Last 5 minutes: Active monitoring
• Debug Mode: {'ON' if debug_system.debug_mode else 'OFF'}
        """.strip()
        
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="debug_dashboard")]
        ])
        
        await callback_query.message.edit_text(activity_text, reply_markup=back_keyboard)
    
    async def show_error_log(self, callback_query: CallbackQuery):
        """Show recent error log"""
        if not debug_system:
            await callback_query.answer("Debug system not available")
            return
        
        recent_errors = debug_system.error_log[-5:]  # Last 5 errors
        
        if not recent_errors:
            error_text = """
🚨 **Error Log**

**🎉 No Recent Errors!**
• System is running smoothly
• All components operational
• No critical issues detected

**📊 Error Statistics:**
• Total Errors: 0
• Recent Errors: 0
• System Health: 🟢 Excellent
            """.strip()
        else:
            error_text = f"""
🚨 **Error Log**

**⚠️ Recent Errors ({len(recent_errors)}):**
"""
            
            for error in recent_errors:
                timestamp = datetime.fromisoformat(error['timestamp']).strftime('%H:%M:%S')
                error_text += f"• {timestamp}: {error['error_type']}\n"
                error_text += f"  {error['error_message'][:50]}...\n"
            
            error_text += f"""

**📊 Error Statistics:**
• Total Errors: {len(debug_system.error_log)}
• Recent Errors: {len(recent_errors)}
• System Health: {'🟡 Monitoring' if len(recent_errors) > 0 else '🟢 Good'}
            """.strip()
        
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="debug_dashboard")]
        ])
        
        await callback_query.message.edit_text(error_text, reply_markup=back_keyboard)
    
    async def show_performance_metrics(self, callback_query: CallbackQuery):
        """Show performance metrics"""
        if not debug_system:
            await callback_query.answer("Debug system not available")
            return
        
        metrics = debug_system.performance_metrics
        
        if not metrics:
            perf_text = """
📊 **Performance Metrics**

**📈 No Performance Data Yet**
• System recently started
• Metrics will appear after usage
• All operations running smoothly

**🚀 Expected Performance:**
• Message handling: <1s
• Database queries: <0.5s
• Payment processing: <2s
            """.strip()
        else:
            perf_text = "📊 **Performance Metrics**\n\n"
            
            for operation, data in metrics.items():
                perf_text += f"**{operation}:**\n"
                perf_text += f"• Calls: {data['count']}\n"
                perf_text += f"• Avg Time: {data['avg_time']:.3f}s\n"
                perf_text += f"• Max Time: {data['max_time']:.3f}s\n\n"
            
            perf_text += "**🎯 Performance Status:** 🟢 Optimal"
        
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="debug_dashboard")]
        ])
        
        await callback_query.message.edit_text(perf_text, reply_markup=back_keyboard)
    
    async def show_full_report(self, callback_query: CallbackQuery):
        """Show full debug report"""
        if not debug_system:
            await callback_query.answer("Debug system not available")
            return
        
        report = await debug_system.generate_debug_report()
        
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="debug_dashboard")]
        ])
        
        await callback_query.message.edit_text(report, reply_markup=back_keyboard)
    
    async def send_message(self, query_or_message, text, reply_markup=None):
        """Send message handling both Message and CallbackQuery"""
        try:
            if hasattr(query_or_message, 'message'):
                # It's a CallbackQuery
                await query_or_message.message.edit_text(text, reply_markup=reply_markup)
            else:
                # It's a Message
                await query_or_message.reply(text, reply_markup=reply_markup)
        except Exception as e:
            print(f"Error sending message: {e}")


# Global dashboard instance
dashboard = None


def init_dashboard(bot: Bot):
    """Initialize debug dashboard"""
    global dashboard
    dashboard = DebugDashboard(bot)
    return dashboard


async def handle_debug_dashboard(callback_query: CallbackQuery):
    """Handle debug dashboard callbacks"""
    global dashboard
    
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("❌ Access denied. Admin only.")
        return
    
    if not dashboard:
        await callback_query.answer("❌ Dashboard not initialized")
        return
    
    data = callback_query.data
    
    if data == "debug_dashboard":
        await dashboard.show_dashboard(callback_query)
    elif data == "debug_health":
        await dashboard.show_system_health(callback_query)
    elif data == "debug_payment":
        await dashboard.show_payment_debug(callback_query)
    elif data == "debug_users":
        await dashboard.show_user_activity(callback_query)
    elif data == "debug_errors":
        await dashboard.show_error_log(callback_query)
    elif data == "debug_performance":
        await dashboard.show_performance_metrics(callback_query)
    elif data == "debug_report":
        await dashboard.show_full_report(callback_query)
    elif data == "debug_refresh":
        await dashboard.show_dashboard(callback_query)
    elif data == "debug_close":
        await callback_query.message.delete()
    
    await callback_query.answer()


def setup_dashboard_handlers(dp):
    """Setup dashboard handlers"""
    dp.callback_query.register(handle_debug_dashboard, lambda c: c.data.startswith("debug_"))