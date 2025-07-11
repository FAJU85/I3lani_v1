#!/usr/bin/env python3
"""
End-to-End Ad Campaign Tracking System
Comprehensive tracking from ad creation to final publication with automatic confirmation
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from global_sequence_system import GlobalSequenceManager, get_global_sequence_manager
from languages import get_text

logger = logging.getLogger(__name__)

@dataclass
class AdCampaignStep:
    """Individual step in ad campaign journey"""
    step_id: str
    step_name: str
    step_title: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    timestamp: datetime
    metadata: Dict[str, Any]
    error_message: Optional[str] = None

@dataclass
class PublishingReport:
    """Final publishing report for ad campaign"""
    campaign_id: str
    sequence_id: str
    user_id: int
    total_channels: int
    published_channels: List[str]
    failed_channels: List[str]
    publication_timestamps: Dict[str, str]
    success_rate: float
    final_status: str
    completion_timestamp: datetime

class EndToEndTrackingSystem:
    """End-to-end ad campaign tracking system"""
    
    # Define all steps in the ad campaign journey
    CAMPAIGN_STEPS = [
        {"step_id": "start_bot", "step_name": "Bot Started", "step_title": "🤖 Bot Initialization"},
        {"step_id": "create_ad_start", "step_name": "Create Ad Started", "step_title": "📝 Ad Creation Started"},
        {"step_id": "upload_content", "step_name": "Content Upload", "step_title": "📤 Content Upload"},
        {"step_id": "select_channels", "step_name": "Channel Selection", "step_title": "📺 Channel Selection"},
        {"step_id": "select_duration", "step_name": "Duration Selection", "step_title": "📅 Duration Selection"},
        {"step_id": "select_frequency", "step_name": "Frequency Selection", "step_title": "📊 Frequency Selection"},
        {"step_id": "confirm_campaign", "step_name": "Campaign Confirmation", "step_title": "✅ Campaign Confirmation"},
        {"step_id": "select_payment", "step_name": "Payment Method", "step_title": "💳 Payment Method"},
        {"step_id": "process_payment", "step_name": "Payment Processing", "step_title": "💰 Payment Processing"},
        {"step_id": "payment_confirmed", "step_name": "Payment Confirmed", "step_title": "✅ Payment Confirmed"},
        {"step_id": "schedule_publishing", "step_name": "Publishing Scheduled", "step_title": "📅 Publishing Scheduled"},
        {"step_id": "start_publishing", "step_name": "Publishing Started", "step_title": "🚀 Publishing Started"},
        {"step_id": "publishing_complete", "step_name": "Publishing Complete", "step_title": "🎉 Publishing Complete"},
    ]
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.sequence_manager = get_global_sequence_manager()
        # Initialize database will be called separately in async context
    
    async def initialize_database(self):
        """Initialize end-to-end tracking database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Campaign tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaign_tracking (
                    tracking_id TEXT PRIMARY KEY,
                    sequence_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    campaign_id TEXT,
                    current_step TEXT,
                    total_steps INTEGER DEFAULT 13,
                    completed_steps INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'in_progress',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (sequence_id) REFERENCES global_sequences (sequence_id)
                )
            """)
            
            # Campaign journey steps
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracking_steps (
                    step_tracking_id TEXT PRIMARY KEY,
                    tracking_id TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    step_title TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    metadata TEXT,
                    error_message TEXT,
                    FOREIGN KEY (tracking_id) REFERENCES campaign_tracking (tracking_id)
                )
            """)
            
            # Publishing reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publishing_reports (
                    report_id TEXT PRIMARY KEY,
                    campaign_id TEXT NOT NULL,
                    sequence_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    total_channels INTEGER,
                    published_channels TEXT,
                    failed_channels TEXT,
                    publication_timestamps TEXT,
                    success_rate REAL,
                    final_status TEXT,
                    completion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confirmation_sent BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns (campaign_id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ End-to-end tracking database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing tracking database: {e}")
    
    async def start_campaign_tracking(self, user_id: int, username: str = None) -> str:
        """Start new campaign tracking"""
        try:
            # Create or get sequence ID
            sequence_id = self.sequence_manager.generate_sequence_id()
            
            # Generate tracking ID
            tracking_id = f"TRACK-{datetime.now().strftime('%Y-%m-%d')}-{sequence_id.split('-')[-1]}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create campaign tracking record
            cursor.execute("""
                INSERT INTO campaign_tracking (
                    tracking_id, sequence_id, user_id, current_step, status, metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (tracking_id, sequence_id, user_id, "start_bot", "in_progress", "{}"))
            
            # Create all journey steps as pending
            for step in self.CAMPAIGN_STEPS:
                step_tracking_id = f"{tracking_id}-{step['step_id']}"
                cursor.execute("""
                    INSERT INTO tracking_steps (
                        step_tracking_id, tracking_id, step_id, step_name, step_title, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (step_tracking_id, tracking_id, step['step_id'], step['step_name'], 
                      step['step_title'], "pending"))
            
            conn.commit()
            conn.close()
            
            # Log step completion
            try:
                self.sequence_manager.log_step(
                    sequence_id=sequence_id,
                    step_name="Campaign Tracking Started",
                    component="tracking_system",
                    status="completed",
                    metadata={"tracking_id": tracking_id, "user_id": user_id}
                )
            except Exception as e:
                logger.warning(f"Step logging failed: {e}")
                # Continue without logging - not critical for tracking functionality
            
            logger.info(f"✅ Campaign tracking started: {tracking_id} for user {user_id}")
            return tracking_id
            
        except Exception as e:
            logger.error(f"❌ Error starting campaign tracking: {e}")
            return None
    
    async def update_step_status(self, tracking_id: str, step_id: str, status: str, 
                                metadata: Dict = None, error_message: str = None):
        """Update step status in campaign tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update step status
            step_tracking_id = f"{tracking_id}-{step_id}"
            current_time = datetime.now().isoformat()
            
            if status == "in_progress":
                cursor.execute("""
                    UPDATE tracking_steps 
                    SET status = ?, started_at = ?, metadata = ?, error_message = ?
                    WHERE step_tracking_id = ?
                """, (status, current_time, str(metadata or {}), error_message, step_tracking_id))
            elif status == "completed":
                cursor.execute("""
                    UPDATE tracking_steps 
                    SET status = ?, completed_at = ?, metadata = ?, error_message = ?
                    WHERE step_tracking_id = ?
                """, (status, current_time, str(metadata or {}), error_message, step_tracking_id))
            else:
                cursor.execute("""
                    UPDATE tracking_steps 
                    SET status = ?, metadata = ?, error_message = ?
                    WHERE step_tracking_id = ?
                """, (status, str(metadata or {}), error_message, step_tracking_id))
            
            # Update campaign tracking
            cursor.execute("""
                UPDATE campaign_tracking 
                SET current_step = ?, updated_at = ?
                WHERE tracking_id = ?
            """, (step_id, current_time, tracking_id))
            
            # Update completed steps count
            cursor.execute("""
                UPDATE campaign_tracking 
                SET completed_steps = (
                    SELECT COUNT(*) FROM campaign_journey_steps 
                    WHERE tracking_id = ? AND status = 'completed'
                )
                WHERE tracking_id = ?
            """, (tracking_id, tracking_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Step updated: {step_id} = {status} for tracking {tracking_id}")
            
        except Exception as e:
            logger.error(f"❌ Error updating step status: {e}")
    
    async def complete_campaign_tracking(self, tracking_id: str, campaign_id: str):
        """Complete campaign tracking and trigger final confirmation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Mark campaign tracking as completed
            cursor.execute("""
                UPDATE campaign_tracking 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP, campaign_id = ?
                WHERE tracking_id = ?
            """, (campaign_id, tracking_id))
            
            # Get tracking details
            cursor.execute("""
                SELECT user_id, sequence_id FROM campaign_tracking 
                WHERE tracking_id = ?
            """, (tracking_id,))
            
            result = cursor.fetchone()
            if result:
                user_id, sequence_id = result
                
                # Create publishing report
                report = await self.create_publishing_report(campaign_id, sequence_id, user_id)
                
                # Send final confirmation
                await self.send_final_confirmation(user_id, campaign_id, report)
                
                logger.info(f"✅ Campaign tracking completed: {tracking_id}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error completing campaign tracking: {e}")
    
    async def create_publishing_report(self, campaign_id: str, sequence_id: str, user_id: int) -> PublishingReport:
        """Create final publishing report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign details
            cursor.execute("""
                SELECT selected_channels, posts_per_day, duration_days 
                FROM campaigns WHERE campaign_id = ?
            """, (campaign_id,))
            
            campaign_data = cursor.fetchone()
            if not campaign_data:
                return None
            
            selected_channels, posts_per_day, duration_days = campaign_data
            
            # Get published posts
            cursor.execute("""
                SELECT channel_name, published_at, message_id, status
                FROM campaign_posts 
                WHERE campaign_id = ? AND published_at IS NOT NULL
            """, (campaign_id,))
            
            published_posts = cursor.fetchall()
            
            # Analyze publication success
            published_channels = list(set([post[0] for post in published_posts]))
            total_expected_channels = len(selected_channels.split(',') if selected_channels else [])
            
            success_rate = len(published_channels) / total_expected_channels if total_expected_channels > 0 else 0
            final_status = "success" if success_rate >= 0.8 else "partial" if success_rate > 0 else "failed"
            
            # Create publication timestamps
            publication_timestamps = {}
            for post in published_posts:
                channel_name, published_at, message_id, status = post
                if channel_name not in publication_timestamps:
                    publication_timestamps[channel_name] = published_at
            
            # Create report
            report = PublishingReport(
                campaign_id=campaign_id,
                sequence_id=sequence_id,
                user_id=user_id,
                total_channels=total_expected_channels,
                published_channels=published_channels,
                failed_channels=[],
                publication_timestamps=publication_timestamps,
                success_rate=success_rate,
                final_status=final_status,
                completion_timestamp=datetime.now()
            )
            
            # Store report in database
            report_id = f"RPT-{datetime.now().strftime('%Y-%m-%d')}-{campaign_id.split('-')[-1]}"
            
            cursor.execute("""
                INSERT INTO publishing_reports (
                    report_id, campaign_id, sequence_id, user_id, total_channels,
                    published_channels, failed_channels, publication_timestamps,
                    success_rate, final_status, completion_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (report_id, campaign_id, sequence_id, user_id, total_expected_channels,
                  ','.join(published_channels), '', str(publication_timestamps),
                  success_rate, final_status, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Publishing report created: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error creating publishing report: {e}")
            return None
    
    async def send_final_confirmation(self, user_id: int, campaign_id: str, report: PublishingReport):
        """Send final confirmation message to user"""
        try:
            # Import here to avoid circular imports
            from main_bot import bot
            from database import Database
            
            db = Database()
            language = await db.get_user_language(user_id)
            
            # Create confirmation message based on publishing report
            if report.final_status == "success":
                if language == 'ar':
                    confirmation_text = f"""🎉 **تم نشر إعلانك بنجاح!**

✅ **تم نشر إعلانك في جميع القنوات المحددة**

📊 **تفاصيل النشر:**
🆔 **رقم الحملة:** {campaign_id}
📺 **القنوات:** {len(report.published_channels)} من {report.total_channels}
📅 **وقت الإكمال:** {report.completion_timestamp.strftime('%Y-%m-%d %H:%M')}
📈 **معدل النجاح:** {report.success_rate:.1%}

**القنوات المنشورة:**
{chr(10).join(f"• {channel}" for channel in report.published_channels)}

🚀 **حملتك الآن نشطة ومرئية للجمهور!**
📈 يمكنك متابعة أداء الإعلان من "إعلاناتي"

شكراً لاستخدام بوت I3lani! 🌟"""
                elif language == 'ru':
                    confirmation_text = f"""🎉 **Ваше объявление успешно опубликовано!**

✅ **Объявление опубликовано во всех выбранных каналах**

📊 **Детали публикации:**
🆔 **ID кампании:** {campaign_id}
📺 **Каналы:** {len(report.published_channels)} из {report.total_channels}
📅 **Время завершения:** {report.completion_timestamp.strftime('%Y-%m-%d %H:%M')}
📈 **Успешность:** {report.success_rate:.1%}

**Опубликованные каналы:**
{chr(10).join(f"• {channel}" for channel in report.published_channels)}

🚀 **Ваша кампания теперь активна и видна аудитории!**
📈 Отслеживайте эффективность в "Мои объявления"

Спасибо за использование I3lani Bot! 🌟"""
                else:
                    confirmation_text = f"""🎉 **Your Ad Has Been Successfully Published!**

✅ **Your ad has been published in all selected channels**

📊 **Publication Details:**
🆔 **Campaign ID:** {campaign_id}
📺 **Channels:** {len(report.published_channels)} of {report.total_channels}
📅 **Completion Time:** {report.completion_timestamp.strftime('%Y-%m-%d %H:%M')}
📈 **Success Rate:** {report.success_rate:.1%}

**Published Channels:**
{chr(10).join(f"• {channel}" for channel in report.published_channels)}

🚀 **Your campaign is now live and visible to the audience!**
📈 Track performance in "My Ads"

Thank you for using I3lani Bot! 🌟"""
                
                # Create keyboard
                if language == 'ar':
                    keyboard = [
                        [{"text": "📊 إعلاناتي", "callback_data": "my_ads"}],
                        [{"text": "📈 إحصائيات الحملة", "callback_data": f"campaign_stats_{campaign_id}"}],
                        [{"text": "🏠 القائمة الرئيسية", "callback_data": "back_to_main"}]
                    ]
                elif language == 'ru':
                    keyboard = [
                        [{"text": "📊 Мои объявления", "callback_data": "my_ads"}],
                        [{"text": "📈 Статистика кампании", "callback_data": f"campaign_stats_{campaign_id}"}],
                        [{"text": "🏠 Главное меню", "callback_data": "back_to_main"}]
                    ]
                else:
                    keyboard = [
                        [{"text": "📊 My Ads", "callback_data": "my_ads"}],
                        [{"text": "📈 Campaign Stats", "callback_data": f"campaign_stats_{campaign_id}"}],
                        [{"text": "🏠 Main Menu", "callback_data": "back_to_main"}]
                    ]
                
                # Send confirmation message
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                
                keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=row[0]["text"], callback_data=row[0]["callback_data"])]
                    for row in keyboard
                ])
                
                await bot.send_message(
                    chat_id=user_id,
                    text=confirmation_text,
                    reply_markup=keyboard_markup,
                    parse_mode='Markdown'
                )
                
                # Mark confirmation as sent
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE publishing_reports 
                    SET confirmation_sent = TRUE 
                    WHERE campaign_id = ? AND user_id = ?
                """, (campaign_id, user_id))
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Final confirmation sent to user {user_id} for campaign {campaign_id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending final confirmation: {e}")
    
    async def get_campaign_progress(self, tracking_id: str) -> Dict:
        """Get campaign progress details"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get tracking details
            cursor.execute("""
                SELECT tracking_id, sequence_id, user_id, campaign_id, current_step, 
                       total_steps, completed_steps, status, created_at, updated_at
                FROM campaign_tracking 
                WHERE tracking_id = ?
            """, (tracking_id,))
            
            tracking_data = cursor.fetchone()
            if not tracking_data:
                return None
            
            # Get journey steps
            cursor.execute("""
                SELECT step_id, step_name, step_title, status, started_at, completed_at
                FROM campaign_journey_steps 
                WHERE tracking_id = ?
                ORDER BY step_id
            """, (tracking_id,))
            
            steps_data = cursor.fetchall()
            
            conn.close()
            
            # Format progress data
            progress = {
                "tracking_id": tracking_data[0],
                "sequence_id": tracking_data[1],
                "user_id": tracking_data[2],
                "campaign_id": tracking_data[3],
                "current_step": tracking_data[4],
                "total_steps": tracking_data[5],
                "completed_steps": tracking_data[6],
                "status": tracking_data[7],
                "progress_percentage": (tracking_data[6] / tracking_data[5]) * 100,
                "steps": [
                    {
                        "step_id": step[0],
                        "step_name": step[1],
                        "step_title": step[2],
                        "status": step[3],
                        "started_at": step[4],
                        "completed_at": step[5]
                    }
                    for step in steps_data
                ]
            }
            
            return progress
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign progress: {e}")
            return None

# Global instance
_tracking_system = None

def get_tracking_system() -> EndToEndTrackingSystem:
    """Get or create tracking system instance"""
    global _tracking_system
    if _tracking_system is None:
        _tracking_system = EndToEndTrackingSystem()
    return _tracking_system

async def start_tracking(user_id: int, username: str = None) -> str:
    """Start campaign tracking for user"""
    tracking_system = get_tracking_system()
    return await tracking_system.start_campaign_tracking(user_id, username)

async def track_step(tracking_id: str, step_id: str, status: str, metadata: Dict = None):
    """Track step completion"""
    tracking_system = get_tracking_system()
    await tracking_system.update_step_status(tracking_id, step_id, status, metadata)

async def complete_tracking(tracking_id: str, campaign_id: str):
    """Complete campaign tracking"""
    tracking_system = get_tracking_system()
    await tracking_system.complete_campaign_tracking(tracking_id, campaign_id)