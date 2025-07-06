"""
Debug System for I3lani Telegram Bot
Provides comprehensive logging, monitoring, and troubleshooting capabilities
"""
import logging
import asyncio
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from aiogram.types import Message, CallbackQuery, Update
from aiogram import Bot
from database import db
from config import ADMIN_IDS

# Configure debug logging
debug_logger = logging.getLogger('debug_system')
debug_handler = logging.FileHandler('debug.log')
debug_handler.setLevel(logging.DEBUG)
debug_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
debug_handler.setFormatter(debug_formatter)
debug_logger.addHandler(debug_handler)
debug_logger.setLevel(logging.DEBUG)


class DebugSystem:
    """Comprehensive debug and monitoring system"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.error_log = []
        self.user_activity = {}
        self.system_stats = {
            'start_time': datetime.now(),
            'total_messages': 0,
            'total_errors': 0,
            'total_users': 0,
            'active_sessions': 0
        }
        self.performance_metrics = {}
        self.debug_mode = False
        
    async def log_user_activity(self, user_id: int, action: str, details: dict = None):
        """Log user activity for debugging"""
        if user_id not in self.user_activity:
            self.user_activity[user_id] = []
        
        activity = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details or {}
        }
        
        self.user_activity[user_id].append(activity)
        
        # Keep only last 50 activities per user
        if len(self.user_activity[user_id]) > 50:
            self.user_activity[user_id] = self.user_activity[user_id][-50:]
        
        debug_logger.info(f"User {user_id} action: {action} - {details}")
    
    async def log_error(self, error: Exception, context: dict = None):
        """Log errors with full context"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.error_log.append(error_info)
        self.system_stats['total_errors'] += 1
        
        # Keep only last 100 errors
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-100:]
        
        debug_logger.error(f"Error logged: {error_info}")
        
        # Notify admins of critical errors
        if isinstance(error, (ConnectionError, TimeoutError)):
            await self.notify_admins_critical_error(error_info)
    
    async def notify_admins_critical_error(self, error_info: dict):
        """Notify admins about critical errors"""
        message = f"""
🚨 **Critical Error Detected**

**Error Type:** {error_info['error_type']}
**Message:** {error_info['error_message']}
**Time:** {error_info['timestamp']}

**Context:** {json.dumps(error_info['context'], indent=2)}

**Action Required:** Please check the system immediately.
        """.strip()
        
        for admin_id in ADMIN_IDS:
            try:
                await self.bot.send_message(admin_id, message, parse_mode='Markdown')
            except Exception as e:
                debug_logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    async def track_performance(self, operation: str, duration: float):
        """Track performance metrics"""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf')
            }
        
        metrics = self.performance_metrics[operation]
        metrics['count'] += 1
        metrics['total_time'] += duration
        metrics['avg_time'] = metrics['total_time'] / metrics['count']
        metrics['max_time'] = max(metrics['max_time'], duration)
        metrics['min_time'] = min(metrics['min_time'], duration)
        
        debug_logger.info(f"Performance: {operation} took {duration:.3f}s")
        
        # Alert if operation is taking too long
        if duration > 5.0:  # 5 seconds threshold
            await self.log_error(
                Exception(f"Slow operation detected: {operation}"),
                {'duration': duration, 'operation': operation}
            )
    
    async def get_system_health(self) -> dict:
        """Get comprehensive system health report"""
        uptime = datetime.now() - self.system_stats['start_time']
        
        # Database health check
        db_health = await self.check_database_health()
        
        # Memory usage (simplified)
        memory_usage = len(self.user_activity) * 1024  # Rough estimate
        
        # Recent errors
        recent_errors = [
            error for error in self.error_log
            if datetime.fromisoformat(error['timestamp']) > datetime.now() - timedelta(hours=1)
        ]
        
        return {
            'uptime': str(uptime),
            'total_messages': self.system_stats['total_messages'],
            'total_errors': self.system_stats['total_errors'],
            'total_users': self.system_stats['total_users'],
            'active_sessions': self.system_stats['active_sessions'],
            'database_health': db_health,
            'memory_usage_kb': memory_usage,
            'recent_errors_count': len(recent_errors),
            'performance_metrics': self.performance_metrics,
            'debug_mode': self.debug_mode
        }
    
    async def check_database_health(self) -> dict:
        """Check database connectivity and performance"""
        try:
            start_time = datetime.now()
            
            # Test database connection
            users = await db.get_channels()
            
            end_time = datetime.now()
            query_time = (end_time - start_time).total_seconds()
            
            return {
                'status': 'healthy',
                'query_time': query_time,
                'channels_count': len(users) if users else 0
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'query_time': None
            }
    
    async def get_user_debug_info(self, user_id: int) -> dict:
        """Get detailed debug information for a specific user"""
        try:
            # Get user from database
            user = await db.get_user(user_id)
            user_stats = await db.get_user_stats(user_id)
            
            # Get recent activity
            recent_activity = self.user_activity.get(user_id, [])
            
            return {
                'user_id': user_id,
                'user_data': user,
                'user_stats': user_stats,
                'recent_activity': recent_activity[-10:],  # Last 10 activities
                'activity_count': len(recent_activity)
            }
        except Exception as e:
            return {
                'user_id': user_id,
                'error': str(e),
                'recent_activity': self.user_activity.get(user_id, [])
            }
    
    async def debug_payment_system(self) -> dict:
        """Debug payment system status"""
        try:
            from payments import payment_processor
            
            # Test memo generation
            test_memos = [payment_processor.generate_memo() for _ in range(5)]
            
            # Test currency conversion
            test_conversion = payment_processor.calculate_price(10.0, 1, 'USD')
            
            return {
                'status': 'healthy',
                'test_memos': test_memos,
                'test_conversion': test_conversion,
                'memo_format_valid': all(len(memo) == 6 for memo in test_memos)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def generate_debug_report(self) -> str:
        """Generate comprehensive debug report"""
        health = await self.get_system_health()
        payment_debug = await self.debug_payment_system()
        
        report = f"""
📊 **I3lani Bot Debug Report**
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**System Health:**
• Uptime: {health['uptime']}
• Total Messages: {health['total_messages']}
• Total Errors: {health['total_errors']}
• Total Users: {health['total_users']}
• Active Sessions: {health['active_sessions']}

**Database Status:**
• Status: {health['database_health']['status']}
• Query Time: {health['database_health'].get('query_time', 'N/A')}s
• Channels: {health['database_health'].get('channels_count', 0)}

**Payment System:**
• Status: {payment_debug['status']}
• Memo Format Valid: {payment_debug.get('memo_format_valid', False)}
• Sample Memos: {', '.join(payment_debug.get('test_memos', []))}

**Performance Metrics:**
{self._format_performance_metrics()}

**Recent Errors:**
{self._format_recent_errors()}

**Memory Usage:** {health['memory_usage_kb']} KB
**Debug Mode:** {'ON' if self.debug_mode else 'OFF'}
        """.strip()
        
        return report
    
    def _format_performance_metrics(self) -> str:
        """Format performance metrics for display"""
        if not self.performance_metrics:
            return "No performance data available"
        
        lines = []
        for operation, metrics in self.performance_metrics.items():
            lines.append(
                f"• {operation}: {metrics['count']} calls, "
                f"avg {metrics['avg_time']:.3f}s, "
                f"max {metrics['max_time']:.3f}s"
            )
        
        return '\n'.join(lines)
    
    def _format_recent_errors(self) -> str:
        """Format recent errors for display"""
        recent_errors = [
            error for error in self.error_log[-5:]  # Last 5 errors
        ]
        
        if not recent_errors:
            return "No recent errors"
        
        lines = []
        for error in recent_errors:
            timestamp = datetime.fromisoformat(error['timestamp']).strftime('%H:%M:%S')
            lines.append(f"• {timestamp}: {error['error_type']} - {error['error_message']}")
        
        return '\n'.join(lines)
    
    async def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_mode = not self.debug_mode
        debug_logger.info(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")
        return self.debug_mode
    
    async def clear_logs(self):
        """Clear all debug logs"""
        self.error_log = []
        self.user_activity = {}
        self.performance_metrics = {}
        debug_logger.info("Debug logs cleared")
    
    async def export_debug_data(self) -> dict:
        """Export all debug data"""
        return {
            'system_stats': self.system_stats,
            'error_log': self.error_log,
            'user_activity': self.user_activity,
            'performance_metrics': self.performance_metrics,
            'export_timestamp': datetime.now().isoformat()
        }


# Global debug system instance
debug_system = None


def init_debug_system(bot: Bot):
    """Initialize debug system"""
    global debug_system
    debug_system = DebugSystem(bot)
    return debug_system


async def debug_middleware(handler, event: Update, data: dict):
    """Middleware to track all bot activities"""
    global debug_system
    
    if debug_system is None:
        return await handler(event, data)
    
    start_time = datetime.now()
    
    try:
        # Log user activity
        if event.message:
            user_id = event.message.from_user.id
            await debug_system.log_user_activity(
                user_id, 
                'message', 
                {
                    'content_type': event.message.content_type,
                    'text': event.message.text[:100] if event.message.text else None
                }
            )
            debug_system.system_stats['total_messages'] += 1
        
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            await debug_system.log_user_activity(
                user_id, 
                'callback', 
                {'data': event.callback_query.data}
            )
        
        # Execute handler
        result = await handler(event, data)
        
        # Track performance
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        handler_name = handler.__name__ if hasattr(handler, '__name__') else 'unknown'
        await debug_system.track_performance(handler_name, duration)
        
        return result
        
    except Exception as e:
        # Log error with context
        context = {
            'handler': handler.__name__ if hasattr(handler, '__name__') else 'unknown',
            'event_type': type(event).__name__,
            'user_id': getattr(event.message or event.callback_query, 'from_user', {}).get('id') if event.message or event.callback_query else None
        }
        
        await debug_system.log_error(e, context)
        raise


# Debug command handlers
async def debug_status_command(message: Message):
    """Show debug status (admin only)"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Access denied. Admin only.")
        return
    
    global debug_system
    if debug_system is None:
        await message.reply("❌ Debug system not initialized.")
        return
    
    report = await debug_system.generate_debug_report()
    await message.reply(report, parse_mode='Markdown')


async def debug_user_command(message: Message):
    """Show debug info for specific user (admin only)"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Access denied. Admin only.")
        return
    
    global debug_system
    if debug_system is None:
        await message.reply("❌ Debug system not initialized.")
        return
    
    # Extract user ID from command
    try:
        user_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /debug_user <user_id>")
        return
    
    debug_info = await debug_system.get_user_debug_info(user_id)
    
    report = f"""
🔍 **User Debug Info - {user_id}**

**User Data:**
```json
{json.dumps(debug_info.get('user_data', {}), indent=2)}
```

**User Stats:**
```json
{json.dumps(debug_info.get('user_stats', {}), indent=2)}
```

**Recent Activity:** {debug_info.get('activity_count', 0)} total actions
    """.strip()
    
    await message.reply(report, parse_mode='Markdown')


async def debug_toggle_command(message: Message):
    """Toggle debug mode (admin only)"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Access denied. Admin only.")
        return
    
    global debug_system
    if debug_system is None:
        await message.reply("❌ Debug system not initialized.")
        return
    
    debug_mode = await debug_system.toggle_debug_mode()
    status = "enabled" if debug_mode else "disabled"
    await message.reply(f"🔧 Debug mode {status}")


async def debug_clear_command(message: Message):
    """Clear debug logs (admin only)"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Access denied. Admin only.")
        return
    
    global debug_system
    if debug_system is None:
        await message.reply("❌ Debug system not initialized.")
        return
    
    await debug_system.clear_logs()
    await message.reply("🗑️ Debug logs cleared")


def setup_debug_handlers(dp):
    """Setup debug command handlers"""
    from aiogram.filters import Command
    
    dp.message.register(debug_status_command, Command("debug_status"))
    dp.message.register(debug_user_command, Command("debug_user"))
    dp.message.register(debug_toggle_command, Command("debug_toggle"))
    dp.message.register(debug_clear_command, Command("debug_clear"))
    
    # Add debug middleware (aiogram 3.x style)
    dp.message.middleware(debug_middleware)
    dp.callback_query.middleware(debug_middleware)