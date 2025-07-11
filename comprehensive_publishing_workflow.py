#!/usr/bin/env python3
"""
Comprehensive Publishing Workflow System for I3lani Bot
Fixes Bug #X - Ensures strict adherence to required publishing steps after payment confirmation

Features:
1. ✅ Publish ads in ALL selected channels
2. ✅ Verify successful delivery to each channel  
3. ✅ Validate content type (text/image/video combinations)
4. ✅ Send per-channel confirmation to user
5. ✅ Comprehensive logging and error handling
"""

import asyncio
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import json

from aiogram import Bot
from aiogram.types import InputMediaPhoto, InputMediaVideo
from aiogram.exceptions import TelegramAPIError

from languages import get_text
from global_sequence_system import get_global_sequence_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PublishingWorkflowResult:
    """Publishing workflow result with comprehensive tracking"""
    
    def __init__(self, campaign_id: str, user_id: int):
        self.campaign_id = campaign_id
        self.user_id = user_id
        self.total_channels = 0
        self.successful_channels = []
        self.failed_channels = []
        self.content_validation_passed = False
        self.user_notifications_sent = []
        self.errors = []
        self.started_at = datetime.now()
        self.completed_at = None
        
    def mark_channel_success(self, channel: str, message_id: int):
        """Mark channel as successfully published"""
        self.successful_channels.append({
            'channel': channel,
            'message_id': message_id,
            'timestamp': datetime.now().isoformat()
        })
        
    def mark_channel_failed(self, channel: str, error: str):
        """Mark channel as failed"""
        self.failed_channels.append({
            'channel': channel,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
        
    def mark_user_notification_sent(self, channel: str, notification_sent: bool):
        """Track user notification status"""
        self.user_notifications_sent.append({
            'channel': channel,
            'sent': notification_sent,
            'timestamp': datetime.now().isoformat()
        })
        
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_channels == 0:
            return 0.0
        return (len(self.successful_channels) / self.total_channels) * 100
        
    def is_complete_success(self) -> bool:
        """Check if all channels were successfully published"""
        return len(self.successful_channels) == self.total_channels and len(self.failed_channels) == 0
        
    def complete(self):
        """Mark workflow as completed"""
        self.completed_at = datetime.now()

class ComprehensivePublishingWorkflow:
    """Comprehensive publishing workflow with strict validation and confirmation"""
    
    def __init__(self, bot: Bot, db_path: str = "bot.db"):
        self.bot = bot
        self.db_path = db_path
        
    async def execute_post_payment_workflow(self, campaign_id: str) -> PublishingWorkflowResult:
        """
        Execute complete post-payment publishing workflow
        Returns comprehensive result with per-channel status
        """
        try:
            # Step 1: Get campaign details
            campaign_data = await self._get_campaign_details(campaign_id)
            if not campaign_data:
                raise Exception(f"Campaign {campaign_id} not found")
                
            user_id = campaign_data['user_id']
            result = PublishingWorkflowResult(campaign_id, user_id)
            
            logger.info(f"🚀 Starting comprehensive publishing workflow for campaign {campaign_id}")
            
            # Step 2: Validate content type and structure
            content_validation = await self._validate_campaign_content(campaign_data)
            result.content_validation_passed = content_validation['valid']
            
            if not content_validation['valid']:
                result.errors.append(f"Content validation failed: {content_validation['reason']}")
                logger.error(f"❌ Content validation failed for {campaign_id}: {content_validation['reason']}")
                result.complete()
                return result
                
            logger.info(f"✅ Content validation passed: {content_validation['content_type']}")
            
            # Step 3: Prepare channels and content
            selected_channels = campaign_data['selected_channels'].split(',') if campaign_data['selected_channels'] else []
            result.total_channels = len(selected_channels)
            
            if not selected_channels:
                result.errors.append("No channels selected for publishing")
                result.complete()
                return result
                
            # Step 4: Publish to each channel with validation
            for channel in selected_channels:
                channel = channel.strip()
                logger.info(f"📡 Publishing to channel {channel}...")
                
                try:
                    # Publish to channel
                    publish_result = await self._publish_to_channel(
                        channel, 
                        campaign_data, 
                        content_validation
                    )
                    
                    if publish_result['success']:
                        result.mark_channel_success(channel, publish_result['message_id'])
                        logger.info(f"✅ Successfully published to {channel} - Message ID: {publish_result['message_id']}")
                        
                        # Step 5: Send per-channel confirmation to user
                        notification_sent = await self._send_channel_confirmation(
                            user_id, 
                            channel, 
                            campaign_id,
                            publish_result['message_id']
                        )
                        result.mark_user_notification_sent(channel, notification_sent)
                        
                    else:
                        result.mark_channel_failed(channel, publish_result['error'])
                        logger.error(f"❌ Failed to publish to {channel}: {publish_result['error']}")
                        
                except Exception as e:
                    error_msg = str(e)
                    result.mark_channel_failed(channel, error_msg)
                    logger.error(f"❌ Exception publishing to {channel}: {error_msg}")
                    
            # Step 6: Log comprehensive results
            await self._log_publishing_results(result)
            
            # Step 7: Send final summary to user
            await self._send_final_publishing_summary(result)
            
            result.complete()
            logger.info(f"🎯 Publishing workflow completed for {campaign_id}: {result.get_success_rate():.1f}% success rate")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Critical error in publishing workflow: {e}")
            result = PublishingWorkflowResult(campaign_id, 0)
            result.errors.append(f"Critical workflow error: {str(e)}")
            result.complete()
            return result
    
    async def _get_campaign_details(self, campaign_id: str) -> Optional[Dict]:
        """Get complete campaign details from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, ad_content, media_url, content_type, selected_channels,
                       campaign_name, duration_days, posts_per_day, total_posts
                FROM campaigns 
                WHERE campaign_id = ?
            """, (campaign_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'user_id': result[0],
                    'ad_content': result[1],
                    'media_url': result[2],
                    'content_type': result[3],
                    'selected_channels': result[4],
                    'campaign_name': result[5],
                    'duration_days': result[6],
                    'posts_per_day': result[7],
                    'total_posts': result[8]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign details: {e}")
            return None
    
    async def _validate_campaign_content(self, campaign_data: Dict) -> Dict:
        """
        Validate content type and ensure proper media+text combinations
        Returns: {'valid': bool, 'content_type': str, 'reason': str}
        """
        try:
            ad_content = campaign_data.get('ad_content', '').strip()
            media_url = campaign_data.get('media_url', '').strip()
            content_type = campaign_data.get('content_type', '').strip()
            
            # Validate basic content presence
            if not ad_content and not media_url:
                return {
                    'valid': False,
                    'content_type': 'empty',
                    'reason': 'No text content or media found'
                }
            
            # Determine actual content type
            if media_url and ad_content:
                if content_type == 'photo':
                    actual_type = 'text+image'
                elif content_type == 'video':
                    actual_type = 'text+video'
                else:
                    actual_type = 'text+media'
            elif media_url and not ad_content:
                if content_type == 'photo':
                    actual_type = 'image_only'
                elif content_type == 'video':
                    actual_type = 'video_only'
                else:
                    actual_type = 'media_only'
            elif ad_content and not media_url:
                actual_type = 'text_only'
            else:
                actual_type = 'unknown'
            
            # Validate content combinations
            valid_combinations = [
                'text_only', 'image_only', 'video_only',
                'text+image', 'text+video'
            ]
            
            if actual_type not in valid_combinations:
                return {
                    'valid': False,
                    'content_type': actual_type,
                    'reason': f'Invalid content combination: {actual_type}'
                }
            
            # Additional validation for media URLs
            if media_url:
                if not (media_url.startswith('AgAC') or media_url.startswith('BAA') or media_url.startswith('CgAC')):
                    return {
                        'valid': False,
                        'content_type': actual_type,
                        'reason': 'Invalid media URL format'
                    }
            
            return {
                'valid': True,
                'content_type': actual_type,
                'reason': 'Content validation passed'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'content_type': 'error',
                'reason': f'Validation error: {str(e)}'
            }
    
    async def _publish_to_channel(self, channel: str, campaign_data: Dict, content_validation: Dict) -> Dict:
        """
        Publish content to specific channel with proper media handling
        Returns: {'success': bool, 'message_id': int, 'error': str}
        """
        try:
            ad_content = campaign_data.get('ad_content', '')
            media_url = campaign_data.get('media_url', '')
            content_type = content_validation['content_type']
            
            message_id = None
            
            # Handle different content types
            if content_type == 'text_only':
                # Send text only
                message = await self.bot.send_message(
                    chat_id=channel,
                    text=ad_content,
                    parse_mode='HTML'
                )
                message_id = message.message_id
                
            elif content_type == 'image_only':
                # Send image only
                message = await self.bot.send_photo(
                    chat_id=channel,
                    photo=media_url
                )
                message_id = message.message_id
                
            elif content_type == 'video_only':
                # Send video only
                message = await self.bot.send_video(
                    chat_id=channel,
                    video=media_url
                )
                message_id = message.message_id
                
            elif content_type == 'text+image':
                # Send image with text caption
                message = await self.bot.send_photo(
                    chat_id=channel,
                    photo=media_url,
                    caption=ad_content,
                    parse_mode='HTML'
                )
                message_id = message.message_id
                
            elif content_type == 'text+video':
                # Send video with text caption
                message = await self.bot.send_video(
                    chat_id=channel,
                    video=media_url,
                    caption=ad_content,
                    parse_mode='HTML'
                )
                message_id = message.message_id
                
            else:
                raise Exception(f"Unsupported content type: {content_type}")
            
            return {
                'success': True,
                'message_id': message_id,
                'error': None
            }
            
        except TelegramAPIError as e:
            error_msg = f"Telegram API error: {e.message}"
            return {
                'success': False,
                'message_id': None,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Publishing error: {str(e)}"
            return {
                'success': False,
                'message_id': None,
                'error': error_msg
            }
    
    async def _send_channel_confirmation(self, user_id: int, channel: str, campaign_id: str, message_id: int) -> bool:
        """Send per-channel confirmation to user"""
        try:
            # Get user language
            user_language = await self._get_user_language(user_id)
            
            # Create confirmation message
            if user_language == 'ar':
                confirmation_text = f"""✅ **تم نشر إعلانك بنجاح!**

📢 **القناة:** {channel}
📅 **التاريخ:** {datetime.now().strftime('%d-%m-%Y')}
🕐 **الوقت:** {datetime.now().strftime('%H:%M')}
🆔 **رقم الرسالة:** {message_id}
📋 **حملة:** {campaign_id}

إعلانك الآن مباشر ومرئي لجميع متابعي القناة! 🎯"""

            elif user_language == 'ru':
                confirmation_text = f"""✅ **Ваше объявление успешно опубликовано!**

📢 **Канал:** {channel}
📅 **Дата:** {datetime.now().strftime('%d-%m-%Y')}
🕐 **Время:** {datetime.now().strftime('%H:%M')}
🆔 **ID сообщения:** {message_id}
📋 **Кампания:** {campaign_id}

Ваша реклама теперь активна и видна всем подписчикам канала! 🎯"""

            else:  # English
                confirmation_text = f"""✅ **Your ad has been successfully published!**

📢 **Channel:** {channel}
📅 **Date:** {datetime.now().strftime('%d-%m-%Y')}
🕐 **Time:** {datetime.now().strftime('%H:%M')}
🆔 **Message ID:** {message_id}
📋 **Campaign:** {campaign_id}

Your ad is now live and visible to all channel subscribers! 🎯"""
            
            # Send confirmation to user
            await self.bot.send_message(
                chat_id=user_id,
                text=confirmation_text,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Sent channel confirmation to user {user_id} for {channel}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send channel confirmation: {e}")
            return False
    
    async def _send_final_publishing_summary(self, result: PublishingWorkflowResult):
        """Send final publishing summary to user"""
        try:
            user_language = await self._get_user_language(result.user_id)
            
            # Create summary message
            success_rate = result.get_success_rate()
            
            if user_language == 'ar':
                if result.is_complete_success():
                    summary_text = f"""🎉 **اكتملت حملتك الإعلانية بنجاح!**

✅ **نُشر في جميع القنوات:** {len(result.successful_channels)}/{result.total_channels}
📊 **معدل النجاح:** {success_rate:.0f}%
🆔 **حملة:** {result.campaign_id}

جميع إعلاناتك الآن مباشرة ومرئية! 🚀"""
                else:
                    summary_text = f"""⚠️ **اكتملت حملتك مع بعض المشاكل**

✅ **نُشر بنجاح:** {len(result.successful_channels)} قناة
❌ **فشل النشر:** {len(result.failed_channels)} قناة
📊 **معدل النجاح:** {success_rate:.0f}%
🆔 **حملة:** {result.campaign_id}

اتصل بالدعم للمساعدة في القنوات الفاشلة."""

            elif user_language == 'ru':
                if result.is_complete_success():
                    summary_text = f"""🎉 **Ваша рекламная кампания успешно завершена!**

✅ **Опубликовано во всех каналах:** {len(result.successful_channels)}/{result.total_channels}
📊 **Успешность:** {success_rate:.0f}%
🆔 **Кампания:** {result.campaign_id}

Все ваши объявления теперь активны и видны! 🚀"""
                else:
                    summary_text = f"""⚠️ **Кампания завершена с проблемами**

✅ **Успешно опубликовано:** {len(result.successful_channels)} каналов
❌ **Не удалось опубликовать:** {len(result.failed_channels)} каналов
📊 **Успешность:** {success_rate:.0f}%
🆔 **Кампания:** {result.campaign_id}

Свяжитесь с поддержкой для помощи с неудачными каналами."""

            else:  # English
                if result.is_complete_success():
                    summary_text = f"""🎉 **Your advertising campaign completed successfully!**

✅ **Published in all channels:** {len(result.successful_channels)}/{result.total_channels}
📊 **Success rate:** {success_rate:.0f}%
🆔 **Campaign:** {result.campaign_id}

All your ads are now live and visible! 🚀"""
                else:
                    summary_text = f"""⚠️ **Campaign completed with issues**

✅ **Successfully published:** {len(result.successful_channels)} channels
❌ **Failed to publish:** {len(result.failed_channels)} channels
📊 **Success rate:** {success_rate:.0f}%
🆔 **Campaign:** {result.campaign_id}

Contact support for help with failed channels."""
            
            # Send summary to user
            await self.bot.send_message(
                chat_id=result.user_id,
                text=summary_text,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Sent final summary to user {result.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send final summary: {e}")
    
    async def _log_publishing_results(self, result: PublishingWorkflowResult):
        """Log comprehensive publishing results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create publishing_results table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publishing_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    total_channels INTEGER,
                    successful_channels INTEGER,
                    failed_channels INTEGER,
                    success_rate REAL,
                    content_validation_passed BOOLEAN,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    results_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert publishing result
            cursor.execute("""
                INSERT INTO publishing_results (
                    campaign_id, user_id, total_channels, successful_channels, failed_channels,
                    success_rate, content_validation_passed, started_at, completed_at, results_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.campaign_id,
                result.user_id,
                result.total_channels,
                len(result.successful_channels),
                len(result.failed_channels),
                result.get_success_rate(),
                result.content_validation_passed,
                result.started_at.isoformat(),
                result.completed_at.isoformat() if result.completed_at else None,
                json.dumps({
                    'successful_channels': result.successful_channels,
                    'failed_channels': result.failed_channels,
                    'user_notifications_sent': result.user_notifications_sent,
                    'errors': result.errors
                }, ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Logged publishing results for campaign {result.campaign_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log publishing results: {e}")
    
    async def _get_user_language(self, user_id: int) -> str:
        """Get user's preferred language"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 'en'
            
        except Exception as e:
            logger.error(f"❌ Error getting user language: {e}")
            return 'en'

# Global instance for integration
publishing_workflow = None

def get_publishing_workflow(bot: Bot) -> ComprehensivePublishingWorkflow:
    """Get or create publishing workflow instance"""
    global publishing_workflow
    if publishing_workflow is None:
        publishing_workflow = ComprehensivePublishingWorkflow(bot)
    return publishing_workflow

async def execute_post_payment_publishing(bot: Bot, campaign_id: str) -> PublishingWorkflowResult:
    """Execute post-payment publishing workflow - main entry point"""
    workflow = get_publishing_workflow(bot)
    return await workflow.execute_post_payment_workflow(campaign_id)

if __name__ == "__main__":
    print("🔧 Comprehensive Publishing Workflow System")
    print("Fixes Bug #X - Post-payment publishing workflow")
    print("Ensures strict adherence to all required publishing steps")