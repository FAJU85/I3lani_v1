"""
Comprehensive Error Reporting System for I3lani Bot
Handles user error reports with automated logging and admin dashboard
"""

import sqlite3
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import traceback
from languages import get_text

logger = logging.getLogger(__name__)

@dataclass
class ErrorReport:
    """Data class for error reports"""
    id: Optional[int] = None
    user_id: int = 0
    step_name: str = ""
    timestamp: datetime = None
    user_description: str = ""
    system_info: str = ""
    error_type: str = "user_reported"
    severity: str = "medium"
    status: str = "open"
    admin_notes: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ErrorReportingSystem:
    """Main error reporting system class"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.step_contexts = {
            # Main bot steps
            "onboarding": "User onboarding and language selection",
            "main_menu": "Main menu display and navigation",
            "create_ad": "Advertisement creation process",
            "upload_content": "Content upload (photos, videos, text)",
            "select_channels": "Channel selection for advertising",
            "select_duration": "Duration and pricing selection",
            "payment_process": "Payment processing (TON/Stars)",
            "payment_confirmation": "Payment confirmation and verification",
            
            # Gaming and rewards
            "viral_game": "Viral referral game system",
            "rewards_system": "Rewards and gamification",
            "leaderboard": "Leaderboard display",
            "partner_program": "Channel partner program",
            
            # Admin functions
            "admin_panel": "Admin panel access and management",
            "channel_management": "Channel management functions",
            "user_analytics": "User analytics and reporting",
            "broadcast_system": "Admin broadcasting system",
            
            # Settings and help
            "settings": "User settings and preferences",
            "language_selection": "Language selection and switching",
            "help_system": "Help and support system",
            "contact_support": "Contact support functionality",
            
            # Technical issues
            "database_error": "Database connectivity issues",
            "payment_api_error": "Payment API connectivity issues",
            "telegram_api_error": "Telegram API issues",
            "general_system_error": "General system errors"
        }
        
    async def initialize_database(self):
        """Initialize error reporting database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create error_reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    step_name TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    user_description TEXT,
                    system_info TEXT,
                    error_type TEXT DEFAULT 'user_reported',
                    severity TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'open',
                    admin_notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create error_analytics table for tracking patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    step_name TEXT NOT NULL,
                    error_count INTEGER DEFAULT 1,
                    last_occurrence DATETIME NOT NULL,
                    avg_severity TEXT,
                    resolution_rate REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create admin_notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notification_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT DEFAULT 'medium',
                    is_read INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Error reporting database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing error reporting database: {e}")
            return False
    
    async def save_error_report(self, error_report: ErrorReport) -> int:
        """Save error report to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO error_reports 
                (user_id, step_name, timestamp, user_description, system_info, 
                 error_type, severity, status, admin_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                error_report.user_id,
                error_report.step_name,
                error_report.timestamp,
                error_report.user_description,
                error_report.system_info,
                error_report.error_type,
                error_report.severity,
                error_report.status,
                error_report.admin_notes
            ))
            
            report_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Update analytics
            await self.update_error_analytics(error_report.step_name, error_report.severity)
            
            # Create admin notification for high severity errors
            if error_report.severity in ['high', 'critical']:
                await self.create_admin_notification(
                    "error_report",
                    f"High Priority Error: {error_report.step_name}",
                    f"User {error_report.user_id} reported: {error_report.user_description}",
                    error_report.severity
                )
            
            logger.info(f"✅ Error report saved: ID {report_id}, Step: {error_report.step_name}")
            return report_id
            
        except Exception as e:
            logger.error(f"❌ Error saving error report: {e}")
            return 0
    
    async def update_error_analytics(self, step_name: str, severity: str):
        """Update error analytics for patterns and tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if analytics record exists
            cursor.execute('''
                SELECT id, error_count FROM error_analytics 
                WHERE step_name = ?
            ''', (step_name,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing record
                cursor.execute('''
                    UPDATE error_analytics 
                    SET error_count = error_count + 1,
                        last_occurrence = ?,
                        avg_severity = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE step_name = ?
                ''', (datetime.now(), severity, step_name))
            else:
                # Create new record
                cursor.execute('''
                    INSERT INTO error_analytics 
                    (step_name, error_count, last_occurrence, avg_severity)
                    VALUES (?, 1, ?, ?)
                ''', (step_name, datetime.now(), severity))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error updating analytics: {e}")
    
    async def create_admin_notification(self, notification_type: str, title: str, message: str, severity: str = "medium"):
        """Create admin notification for error reports"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO admin_notifications 
                (notification_type, title, message, severity)
                VALUES (?, ?, ?, ?)
            ''', (notification_type, title, message, severity))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error creating admin notification: {e}")
    
    async def get_error_reports(self, limit: int = 50, status: str = None) -> List[Dict]:
        """Get error reports with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM error_reports 
                {} ORDER BY timestamp DESC LIMIT ?
            '''.format("WHERE status = ?" if status else "")
            
            params = [status, limit] if status else [limit]
            cursor.execute(query, params)
            
            reports = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return reports
            
        except Exception as e:
            logger.error(f"❌ Error retrieving error reports: {e}")
            return []
    
    async def get_error_analytics(self) -> List[Dict]:
        """Get error analytics for admin dashboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM error_analytics 
                ORDER BY error_count DESC, last_occurrence DESC
            ''')
            
            analytics = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error retrieving error analytics: {e}")
            return []
    
    async def get_admin_notifications(self, limit: int = 20) -> List[Dict]:
        """Get admin notifications"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM admin_notifications 
                ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
            
            notifications = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return notifications
            
        except Exception as e:
            logger.error(f"❌ Error retrieving admin notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: int):
        """Mark admin notification as read"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE admin_notifications 
                SET is_read = 1 
                WHERE id = ?
            ''', (notification_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error marking notification as read: {e}")
    
    async def update_error_status(self, report_id: int, status: str, admin_notes: str = ""):
        """Update error report status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE error_reports 
                SET status = ?, admin_notes = ?
                WHERE id = ?
            ''', (status, admin_notes, report_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Error report {report_id} status updated to: {status}")
            
        except Exception as e:
            logger.error(f"❌ Error updating error status: {e}")
    
    def get_step_context(self, step_name: str) -> str:
        """Get context description for a step"""
        return self.step_contexts.get(step_name, f"Unknown step: {step_name}")
    
    async def auto_diagnose_error(self, error_report: ErrorReport) -> Dict[str, Any]:
        """Perform automatic error diagnosis"""
        diagnosis = {
            "severity": "medium",
            "category": "unknown",
            "suggested_fix": "Manual investigation required",
            "auto_resolvable": False,
            "confidence": 0.0
        }
        
        # Basic pattern matching for common issues
        description = error_report.user_description.lower()
        step = error_report.step_name.lower()
        
        # Payment-related errors
        if "payment" in step or "payment" in description:
            diagnosis.update({
                "category": "payment",
                "severity": "high",
                "suggested_fix": "Check payment API status and user balance",
                "confidence": 0.8
            })
        
        # Language/translation errors
        if "language" in description or "english" in description or "arabic" in description:
            diagnosis.update({
                "category": "localization",
                "severity": "medium",
                "suggested_fix": "Check translation system and language persistence",
                "confidence": 0.7
            })
        
        # Channel-related errors
        if "channel" in step or "channel" in description:
            diagnosis.update({
                "category": "channel_management",
                "severity": "medium",
                "suggested_fix": "Verify bot admin permissions and channel access",
                "confidence": 0.6
            })
        
        # Button/callback errors
        if "button" in description or "click" in description or "callback" in description:
            diagnosis.update({
                "category": "ui_interaction",
                "severity": "medium",
                "suggested_fix": "Check callback handlers and button configurations",
                "confidence": 0.7
            })
        
        return diagnosis
    
    def create_error_report_keyboard(self, language: str, step_name: str) -> str:
        """Create error report button text for given language and step"""
        error_button_text = {
            'en': '🐛 Report Error',
            'ar': '🐛 إبلاغ عن خطأ',
            'ru': '🐛 Сообщить об ошибке'
        }
        
        return error_button_text.get(language, error_button_text['en'])
    
    def get_error_report_prompt(self, language: str, step_name: str) -> str:
        """Get error report prompt text for given language"""
        step_context = self.get_step_context(step_name)
        
        prompts = {
            'en': f"""🐛 **Error Report**

**Current Step:** {step_name}
**Context:** {step_context}

Please describe the problem you encountered:
• What were you trying to do?
• What happened instead?
• Any error messages you saw?

Your report helps us improve the bot for everyone!

*Type your description below or tap Skip to send basic info:*""",
            
            'ar': f"""🐛 **تقرير خطأ**

**الخطوة الحالية:** {step_name}
**السياق:** {step_context}

يرجى وصف المشكلة التي واجهتها:
• ماذا كنت تحاول أن تفعل؟
• ما الذي حدث بدلاً من ذلك؟
• أي رسائل خطأ رأيتها؟

تقريرك يساعدنا في تحسين البوت للجميع!

*اكتب وصفك أدناه أو اضغط تخطي لإرسال معلومات أساسية:*""",
            
            'ru': f"""🐛 **Отчет об ошибке**

**Текущий шаг:** {step_name}
**Контекст:** {step_context}

Пожалуйста, опишите проблему, с которой вы столкнулись:
• Что вы пытались сделать?
• Что произошло вместо этого?
• Какие сообщения об ошибках вы видели?

Ваш отчет помогает нам улучшить бота для всех!

*Введите описание ниже или нажмите Пропустить для отправки базовой информации:*"""
        }
        
        return prompts.get(language, prompts['en'])
    
    def get_error_report_success_message(self, language: str, report_id: int) -> str:
        """Get success message after error report submission"""
        messages = {
            'en': f"""✅ **Error Report Submitted**

**Report ID:** #{report_id}
**Status:** Under Review

Thank you for helping us improve the bot! Our team will investigate this issue and work on a fix.

You can continue using the bot normally. We'll notify you if we need more information.

*Back to what you were doing? Use the menu below.*""",
            
            'ar': f"""✅ **تم إرسال تقرير الخطأ**

**معرف التقرير:** #{report_id}
**الحالة:** قيد المراجعة

شكراً لمساعدتنا في تحسين البوت! فريقنا سيحقق في هذه المشكلة ويعمل على حلها.

يمكنك متابعة استخدام البوت بشكل طبيعي. سنقوم بإشعارك إذا احتجنا مزيد من المعلومات.

*العودة لما كنت تفعله؟ استخدم القائمة أدناه.*""",
            
            'ru': f"""✅ **Отчет об ошибке отправлен**

**ID отчета:** #{report_id}
**Статус:** На рассмотрении

Спасибо за помощь в улучшении бота! Наша команда изучит эту проблему и поработает над исправлением.

Вы можете продолжать использовать бота в обычном режиме. Мы уведомим вас, если потребуется дополнительная информация.

*Вернуться к тому, что вы делали? Используйте меню ниже.*"""
        }
        
        return messages.get(language, messages['en'])

# Global error reporting system instance
error_reporting = ErrorReportingSystem()