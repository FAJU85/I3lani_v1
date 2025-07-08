"""
Troubleshooting Command Handlers for I3lani Bot
Provides user and admin interfaces for troubleshooting and diagnostics
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from typing import Dict, List
import logging
import json
from datetime import datetime, timedelta

from database import db
from languages import get_text
from config import ADMIN_IDS
from troubleshooting import TroubleshootingSystem
import aiosqlite

logger = logging.getLogger(__name__)

# Create router for troubleshooting
troubleshooting_router = Router()

# Global troubleshooting system instance
troubleshooting_system: TroubleshootingSystem = None

def init_troubleshooting_handlers(ts_system: TroubleshootingSystem):
    """Initialize troubleshooting handlers with system instance"""
    global troubleshooting_system
    troubleshooting_system = ts_system

@troubleshooting_router.message(Command("health"))
async def health_check_command(message: Message):
    """Run basic health check (admin only)"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Access denied. Admin privileges required.")
        return
    
    try:
        await message.reply("🔍 Running health checks...")
        
        health_status = await troubleshooting_system.run_health_checks()
        
        # Format health report
        status_emoji = {
            'healthy': '✅',
            'issues_detected': '⚠️',
            'critical': '🚨',
            'unknown': '❓'
        }
        
        report = f"""🏥 **System Health Report**
        
**Overall Status:** {status_emoji.get(health_status['overall'], '❓')} {health_status['overall'].title()}
**Issues Found:** {health_status['issues_found']}
**Check Time:** {health_status['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

**Component Status:**"""
        
        for component, details in health_status['checks'].items():
            component_emoji = status_emoji.get(details['status'], '❓')
            report += f"\n• {component_emoji} **{component.title()}:** {details['status']}"
            
            if details.get('issues'):
                for issue in details['issues'][:2]:  # Show max 2 issues per component
                    report += f"\n  ⚬ {issue}"
        
        if health_status['issues_found'] > 0:
            report += f"\n\n📋 Use `/troubleshoot` for detailed diagnostics"
        
        await message.reply(report, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in health check command: {e}")
        await message.reply(f"❌ Health check failed: {str(e)}")

@troubleshooting_router.message(Command("troubleshoot"))
async def troubleshoot_command(message: Message):
    """Open troubleshooting menu (admin only)"""
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Access denied. Admin privileges required.")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏥 System Health", callback_data="ts_health"),
            InlineKeyboardButton(text="📊 Error Analysis", callback_data="ts_errors")
        ],
        [
            InlineKeyboardButton(text="🔧 Auto Diagnostics", callback_data="ts_diagnose"),
            InlineKeyboardButton(text="📈 Performance", callback_data="ts_performance")
        ],
        [
            InlineKeyboardButton(text="🗂️ System Report", callback_data="ts_report"),
            InlineKeyboardButton(text="⚡ Quick Fixes", callback_data="ts_quickfix")
        ],
        [
            InlineKeyboardButton(text="📝 User Issues", callback_data="ts_user_issues"),
            InlineKeyboardButton(text="🔄 Refresh Status", callback_data="ts_refresh")
        ]
    ])
    
    await message.reply(
        "🛠️ **Troubleshooting Control Panel**\n\n"
        "Select an option to diagnose and resolve issues:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@troubleshooting_router.callback_query(F.data == "ts_health")
async def show_detailed_health(callback_query: CallbackQuery):
    """Show detailed health status"""
    try:
        await callback_query.answer("Running detailed health checks...")
        
        health_status = await troubleshooting_system.run_health_checks()
        
        detailed_report = "🏥 **Detailed Health Analysis**\n\n"
        
        for component, details in health_status['checks'].items():
            status_icon = '✅' if details['status'] == 'healthy' else '⚠️' if details['status'] in ['slow', 'warning', 'partial'] else '🚨'
            
            detailed_report += f"**{component.upper()}** {status_icon}\n"
            detailed_report += f"Status: {details['status']}\n"
            
            # Add specific metrics
            if 'response_time' in details:
                detailed_report += f"Response Time: {details['response_time']:.3f}s\n"
            if 'memory_percent' in details:
                detailed_report += f"Memory Usage: {details['memory_percent']:.1f}%\n"
            if 'database_size_mb' in details:
                detailed_report += f"Database Size: {details['database_size_mb']:.1f}MB\n"
            if 'accessibility_rate' in details:
                detailed_report += f"Channel Access: {details['accessibility_rate']:.1%}\n"
            
            if details.get('issues'):
                detailed_report += "Issues:\n"
                for issue in details['issues']:
                    detailed_report += f"• {issue}\n"
            
            detailed_report += "\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="ts_health")],
            [InlineKeyboardButton(text="◀️ Back", callback_data="ts_back")]
        ])
        
        await callback_query.message.edit_text(
            detailed_report,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing detailed health: {e}")
        await callback_query.answer("❌ Error loading health details")

@troubleshooting_router.callback_query(F.data == "ts_errors")
async def show_error_analysis(callback_query: CallbackQuery):
    """Show recent error analysis"""
    try:
        await callback_query.answer("Analyzing recent errors...")
        
        recent_errors = await troubleshooting_system._get_recent_errors(hours=24)
        
        if not recent_errors:
            report = "✅ **No Recent Errors**\n\nNo errors found in the last 24 hours."
        else:
            # Group errors by type
            error_groups = {}
            for error in recent_errors:
                error_type = error['error_type']
                if error_type not in error_groups:
                    error_groups[error_type] = []
                error_groups[error_type].append(error)
            
            report = f"📊 **Error Analysis (Last 24h)**\n\n"
            report += f"Total Errors: {len(recent_errors)}\n"
            report += f"Error Types: {len(error_groups)}\n\n"
            
            # Show top error types
            sorted_groups = sorted(error_groups.items(), key=lambda x: len(x[1]), reverse=True)
            
            for error_type, errors in sorted_groups[:5]:
                severity_icon = '🚨' if errors[0]['severity'] == 'high' else '⚠️' if errors[0]['severity'] == 'medium' else 'ℹ️'
                report += f"**{error_type}** {severity_icon}\n"
                report += f"Count: {len(errors)}\n"
                report += f"Latest: {errors[0]['timestamp']}\n"
                report += f"Message: {errors[0]['error_message'][:100]}...\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔧 Auto-Fix", callback_data="ts_autofix"),
                InlineKeyboardButton(text="📋 Full Log", callback_data="ts_fulllog")
            ],
            [InlineKeyboardButton(text="◀️ Back", callback_data="ts_back")]
        ])
        
        await callback_query.message.edit_text(
            report,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing error analysis: {e}")
        await callback_query.answer("❌ Error loading error analysis")

@troubleshooting_router.callback_query(F.data == "ts_diagnose")
async def show_diagnostic_menu(callback_query: CallbackQuery):
    """Show diagnostic options"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💾 Database Issues", callback_data="ts_diag_database"),
            InlineKeyboardButton(text="💳 Payment Issues", callback_data="ts_diag_payment")
        ],
        [
            InlineKeyboardButton(text="📨 Messaging Issues", callback_data="ts_diag_messaging"),
            InlineKeyboardButton(text="📺 Channel Issues", callback_data="ts_diag_channel")
        ],
        [
            InlineKeyboardButton(text="⚡ Performance Issues", callback_data="ts_diag_performance"),
            InlineKeyboardButton(text="🌐 Language Issues", callback_data="ts_diag_language")
        ],
        [InlineKeyboardButton(text="◀️ Back", callback_data="ts_back")]
    ])
    
    await callback_query.message.edit_text(
        "🔧 **Auto Diagnostics**\n\n"
        "Select the type of issue you want to diagnose:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@troubleshooting_router.callback_query(F.data.startswith("ts_diag_"))
async def run_specific_diagnostic(callback_query: CallbackQuery):
    """Run specific diagnostic based on issue type"""
    issue_type = callback_query.data.replace("ts_diag_", "")
    
    try:
        await callback_query.answer(f"Diagnosing {issue_type} issues...")
        
        diagnosis = await troubleshooting_system.diagnose_issue(issue_type)
        
        severity_icon = '🚨' if diagnosis['severity'] == 'high' else '⚠️' if diagnosis['severity'] == 'medium' else 'ℹ️'
        
        report = f"🔍 **{issue_type.title()} Diagnostic** {severity_icon}\n\n"
        report += f"**Description:** {diagnosis['description']}\n"
        report += f"**Severity:** {diagnosis['severity']}\n\n"
        
        if diagnosis['possible_causes']:
            report += "**Possible Causes:**\n"
            for cause in diagnosis['possible_causes']:
                report += f"• {cause}\n"
            report += "\n"
        
        if diagnosis['recommended_solutions']:
            report += "**Recommended Solutions:**\n"
            for i, solution in enumerate(diagnosis['recommended_solutions'], 1):
                report += f"{i}. {solution}\n"
            report += "\n"
        
        if diagnosis['automated_fixes']:
            report += "**Available Auto-Fixes:**\n"
            for fix in diagnosis['automated_fixes']:
                report += f"🔧 {fix}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Apply Auto-Fix", callback_data=f"ts_autofix_{issue_type}")],
            [InlineKeyboardButton(text="◀️ Back", callback_data="ts_diagnose")]
        ])
        
        await callback_query.message.edit_text(
            report,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error running diagnostic: {e}")
        await callback_query.answer("❌ Diagnostic failed")

@troubleshooting_router.callback_query(F.data.startswith("ts_autofix"))
async def apply_auto_fix(callback_query: CallbackQuery):
    """Apply automated fixes for detected issues"""
    try:
        if "_" in callback_query.data and len(callback_query.data.split("_")) > 2:
            issue_type = callback_query.data.split("_", 2)[2]
        else:
            issue_type = "general"
        
        await callback_query.answer("Applying automated fixes...")
        
        resolution = await troubleshooting_system.auto_resolve_issue(issue_type)
        
        report = f"🔧 **Auto-Fix Results**\n\n"
        report += f"**Issue Type:** {resolution['issue_type']}\n"
        report += f"**Resolved:** {'✅ Yes' if resolution['resolved'] else '❌ No'}\n\n"
        
        if resolution['actions_taken']:
            report += "**Actions Taken:**\n"
            for action in resolution['actions_taken']:
                report += f"• {action}\n"
            report += "\n"
        
        if resolution['manual_steps_required']:
            report += "**Manual Steps Required:**\n"
            for step in resolution['manual_steps_required']:
                report += f"• {step}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Re-check Health", callback_data="ts_health")],
            [InlineKeyboardButton(text="◀️ Back", callback_data="ts_back")]
        ])
        
        await callback_query.message.edit_text(
            report,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error applying auto-fix: {e}")
        await callback_query.answer("❌ Auto-fix failed")

@troubleshooting_router.callback_query(F.data == "ts_report")
async def generate_system_report(callback_query: CallbackQuery):
    """Generate comprehensive system report"""
    try:
        await callback_query.answer("Generating system report...")
        
        report_data = await troubleshooting_system.generate_system_report()
        
        # Format the report
        report = f"📋 **System Report**\n\n"
        report += f"**Generated:** {report_data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**Uptime:** {report_data['uptime_hours']:.1f} hours\n\n"
        
        # Health summary
        health = report_data['health_status']
        status_icon = '✅' if health['overall'] == 'healthy' else '⚠️' if health['overall'] == 'issues_detected' else '🚨'
        report += f"**Health Status:** {status_icon} {health['overall']}\n"
        report += f"**Issues Found:** {health['issues_found']}\n\n"
        
        # Error summary
        recent_errors = report_data['recent_errors']
        report += f"**Recent Errors (24h):** {len(recent_errors)}\n"
        
        if recent_errors:
            error_types = {}
            for error in recent_errors:
                error_type = error['error_type']
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            report += "**Top Error Types:**\n"
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:3]:
                report += f"• {error_type}: {count}\n"
        
        # Recommendations
        if report_data['recommendations']:
            report += "\n**Recommendations:**\n"
            for rec in report_data['recommendations']:
                report += f"• {rec}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📧 Export Report", callback_data="ts_export")],
            [InlineKeyboardButton(text="◀️ Back", callback_data="ts_back")]
        ])
        
        await callback_query.message.edit_text(
            report,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error generating system report: {e}")
        await callback_query.answer("❌ Report generation failed")

@troubleshooting_router.message(Command("report_issue"))
async def report_user_issue(message: Message, state: FSMContext):
    """Allow users to report issues to support"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    
    if len(message.text.split()) < 2:
        await message.reply(
            get_text(language, 'report_issue_help', 
                   "Please describe your issue:\n/report_issue Your problem description here")
        )
        return
    
    issue_description = message.text.split(maxsplit=1)[1]
    
    try:
        # Log user issue
        async with aiosqlite.connect(db.db_path) as database:
            await database.execute('''
                INSERT INTO user_issues (user_id, issue_type, description, priority)
                VALUES (?, ?, ?, ?)
            ''', (user_id, 'user_reported', issue_description, 'medium'))
            await database.commit()
        
        # Auto-categorize and provide immediate help if possible
        auto_help = await get_auto_help_response(issue_description, language)
        
        response = get_text(language, 'issue_reported',
                          "✅ Your issue has been reported. Support team will review it soon.")
        
        if auto_help:
            response += f"\n\n💡 **Quick Help:**\n{auto_help}"
        
        await message.reply(response)
        
        # Notify admins if critical keywords detected
        critical_keywords = ['crash', 'error', 'payment', 'stuck', 'broken', 'bug']
        if any(keyword in issue_description.lower() for keyword in critical_keywords):
            for admin_id in ADMIN_IDS:
                try:
                    await message.bot.send_message(
                        admin_id,
                        f"🚨 **Priority User Issue**\n\n"
                        f"**User:** {user_id}\n"
                        f"**Issue:** {issue_description}\n\n"
                        f"Use `/troubleshoot` to investigate."
                    )
                except:
                    pass  # Admin might have blocked bot
        
    except Exception as e:
        logger.error(f"Error reporting user issue: {e}")
        await message.reply("❌ Error reporting issue. Please try again later.")

async def get_auto_help_response(issue_description: str, language: str) -> str:
    """Provide automated help based on issue description"""
    issue_lower = issue_description.lower()
    
    # Common issue patterns and responses
    help_responses = {
        'language': "To change language, send /start and select your preferred language.",
        'payment': "For payment issues, check your payment method and try again. Contact support if the problem persists.",
        'channel': "Make sure the bot is an administrator in your channel with proper permissions.",
        'slow': "Try restarting the bot or clear your Telegram cache. If issues persist, contact support.",
        'error': "Please provide more details about when this error occurred. Try restarting and contact support if it continues."
    }
    
    for keyword, response in help_responses.items():
        if keyword in issue_lower:
            return response
    
    return None

@troubleshooting_router.callback_query(F.data == "ts_back")
async def back_to_troubleshoot_menu(callback_query: CallbackQuery):
    """Return to main troubleshooting menu"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏥 System Health", callback_data="ts_health"),
            InlineKeyboardButton(text="📊 Error Analysis", callback_data="ts_errors")
        ],
        [
            InlineKeyboardButton(text="🔧 Auto Diagnostics", callback_data="ts_diagnose"),
            InlineKeyboardButton(text="📈 Performance", callback_data="ts_performance")
        ],
        [
            InlineKeyboardButton(text="🗂️ System Report", callback_data="ts_report"),
            InlineKeyboardButton(text="⚡ Quick Fixes", callback_data="ts_quickfix")
        ],
        [
            InlineKeyboardButton(text="📝 User Issues", callback_data="ts_user_issues"),
            InlineKeyboardButton(text="🔄 Refresh Status", callback_data="ts_refresh")
        ]
    ])
    
    await callback_query.message.edit_text(
        "🛠️ **Troubleshooting Control Panel**\n\n"
        "Select an option to diagnose and resolve issues:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )