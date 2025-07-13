#!/usr/bin/env python3
"""
Ad Campaign Management System with Global Sequence Integration
Unified campaign management using sequence-based tracking
"""

import asyncio
import logging
from automatic_language_system import get_user_language_auto
import sqlite3
import json
import string
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Import global sequence system
from global_sequence_system import (
    get_global_sequence_manager, start_user_global_sequence, 
    log_sequence_step, link_to_global_sequence
)
from sequence_logger import get_sequence_logger

logging.basicConfig(level=logging.INFO)
logger = get_sequence_logger(__name__)

class CampaignManager:
    """Manages ad campaign creation, tracking, and metadata"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        
    async def init_tables(self):
        """Initialize campaign management tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create campaigns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL UNIQUE,
                    user_id INTEGER NOT NULL,
                    payment_memo TEXT,
                    payment_method TEXT DEFAULT 'TON',
                    payment_amount REAL,
                    
                    -- Campaign Details
                    campaign_name TEXT,
                    ad_content TEXT,
                    ad_type TEXT DEFAULT 'text',
                    
                    -- Scheduling
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_date TIMESTAMP,
                    duration_days INTEGER,
                    posts_per_day INTEGER,
                    total_posts INTEGER,
                    
                    -- Channels
                    selected_channels TEXT,
                    channel_count INTEGER,
                    total_reach INTEGER,
                    
                    -- Status
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Analytics
                    posts_published INTEGER DEFAULT 0,
                    engagement_score REAL DEFAULT 0.0,
                    click_through_rate REAL DEFAULT 0.0,
                    
                    -- Metadata
                    campaign_metadata TEXT
                );
            """)
            
            # Create campaign_posts table for tracking individual posts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaign_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    post_id TEXT,
                    post_content TEXT,
                    scheduled_time TIMESTAMP,
                    published_time TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    engagement_metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
                );
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaigns_user_id 
                ON campaigns(user_id);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_id 
                ON campaigns(campaign_id);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaigns_status 
                ON campaigns(status);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaign_posts_campaign_id 
                ON campaign_posts(campaign_id);
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Campaign management tables initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing campaign tables: {e}")
            return False
    
    def generate_campaign_id(self, sequence_id: str) -> str:
        """Generate unique campaign ID using global sequence system"""
        try:
            if sequence_id:
                # Extract sequence components
                parts = sequence_id.split('-')
                if len(parts) >= 4:
                    # Create campaign ID from sequence: CAM-MM-XXXXX
                    campaign_id = f"CAM-{parts[2]}-{parts[3]}"
                    
                    # Log campaign ID generation
                    log_sequence_step(sequence_id, "Campaign_Step_1_GenerateCampaignID", "campaign_management", {
                        "campaign_id": campaign_id,
                        "sequence_id": sequence_id,
                        "generation_method": "sequence_based"
                    })
                    
                    return campaign_id
                else:
                    logger.error(f"❌ Invalid sequence ID format: {sequence_id}")
                    return f"CAM-INVALID-{datetime.now().strftime('%H%M%S')}"
            else:
                # Fallback for legacy data  
                logger.warning("⚠️ No sequence ID provided, using fallback campaign ID generation")
                return f"CAM-LEGACY-{datetime.now().strftime('%H%M%S')}"
                
        except Exception as e:
            logger.error(f"❌ Error generating campaign ID: {e}")
            return f"CAM-ERROR-{datetime.now().strftime('%H%M%S')}"
    
    async def create_campaign(self, user_id: int, payment_memo: str, payment_amount: float,
                            ad_data: Dict[str, Any], payment_method: str = 'TON') -> str:
        """Create new campaign with sequence-based unique ID"""
        try:
            # Get user's sequence ID
            manager = get_global_sequence_manager()
            sequence_id = manager.get_user_active_sequence(user_id)
            
            # Generate unique campaign ID using sequence system
            campaign_id = self.generate_campaign_id(sequence_id)
            
            # Ensure uniqueness (sequence-based IDs should be unique by design)
            while await self.campaign_exists(campaign_id):
                campaign_id = self.generate_campaign_id(sequence_id)
            
            # Calculate campaign dates
            start_date = datetime.now()
            duration_days = ad_data.get('duration_days', 7)
            end_date = start_date + timedelta(days=duration_days)
            
            # Extract campaign details
            selected_channels = ad_data.get('selected_channels', [])
            posts_per_day = ad_data.get('posts_per_day', 2)
            total_posts = duration_days * posts_per_day
            total_reach = ad_data.get('total_reach', 357)
            
            # Create campaign metadata
            campaign_metadata = {
                'created_via': 'automatic_confirmation',
                'pricing_tier': ad_data.get('pricing_tier', 'standard'),
                'discount_applied': ad_data.get('discount_applied', 0),
                'target_audience': ad_data.get('target_audience', 'general'),
                'content_type': ad_data.get('content_type', 'text'),
                'languages': ad_data.get('languages', ['ar', 'en']),
                'creation_source': 'bot_interface'
            }
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert campaign with media support
            ad_content = ad_data.get('ad_content', f'Advertisement campaign for payment {payment_memo}')
            content_type = ad_data.get('content_type', 'text')
            media_url = ad_data.get('media_url', None)
            
            cursor.execute("""
                INSERT INTO campaigns (
                    campaign_id, user_id, payment_memo, payment_method, payment_amount,
                    campaign_name, ad_content, content_type, media_url, duration_days, posts_per_day, total_posts,
                    selected_channels, channel_count, total_reach, start_date, end_date,
                    status, campaign_metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                campaign_id, user_id, payment_memo, payment_method, payment_amount,
                f"Campaign {campaign_id}", ad_content, content_type, media_url,
                duration_days, posts_per_day, total_posts,
                ','.join(selected_channels), len(selected_channels), total_reach,
                start_date, end_date, 'active', json.dumps(campaign_metadata)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created campaign {campaign_id} for user {user_id}")
            
            # ENHANCED: Register content integrity fingerprint for this campaign
            try:
                from content_integrity_system import register_campaign_content
                
                content_fingerprint = await register_campaign_content(
                    campaign_id, user_id, sequence_id, ad_content, 
                    ad_data.get('media_url'), ad_data.get('content_type', 'text')
                )
                
                logger.info(f"✅ Content integrity registered for campaign {campaign_id}")
                logger.info(f"   Content hash: {content_fingerprint.content_hash}")
                logger.info(f"   Sequence ID: {sequence_id}")
                
            except Exception as e:
                logger.error(f"❌ Error registering content integrity: {e}")
                # Don't fail campaign creation, but log the issue for monitoring
            
            # Schedule campaign posts
            await self.schedule_campaign_posts(campaign_id, selected_channels, posts_per_day, duration_days)
            
            return campaign_id
            
        except Exception as e:
            logger.error(f"❌ Error creating campaign: {e}")
            return None
    
    async def campaign_exists(self, campaign_id: str) -> bool:
        """Check if campaign ID already exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM campaigns WHERE campaign_id = ?", (campaign_id,))
            exists = cursor.fetchone() is not None
            
            conn.close()
            return exists
            
        except Exception as e:
            logger.error(f"❌ Error checking campaign existence: {e}")
            return False
    
    async def get_campaign_by_id(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign details by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM campaigns WHERE campaign_id = ?
            """, (campaign_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                campaign = dict(row)
                # Parse JSON fields
                if campaign['campaign_metadata']:
                    campaign['campaign_metadata'] = json.loads(campaign['campaign_metadata'])
                if campaign['selected_channels']:
                    campaign['selected_channels'] = campaign['selected_channels'].split(',')
                
                return campaign
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign: {e}")
            return None
    
    async def get_user_campaigns(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's campaigns"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM campaigns 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            campaigns = []
            for row in rows:
                campaign = dict(row)
                # Parse JSON fields
                if campaign['campaign_metadata']:
                    campaign['campaign_metadata'] = json.loads(campaign['campaign_metadata'])
                if campaign['selected_channels']:
                    campaign['selected_channels'] = campaign['selected_channels'].split(',')
                campaigns.append(campaign)
            
            return campaigns
            
        except Exception as e:
            logger.error(f"❌ Error getting user campaigns: {e}")
            return []
    
    async def schedule_campaign_posts(self, campaign_id: str, channels: List[str], 
                                    posts_per_day: int, duration_days: int):
        """Schedule individual posts for campaign"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = datetime.now()
            posts_scheduled = 0
            
            # Calculate posting schedule
            hours_between_posts = 24 / posts_per_day if posts_per_day > 0 else 24
            
            for day in range(duration_days):
                for post_num in range(posts_per_day):
                    for channel in channels:
                        # Calculate scheduled time
                        scheduled_time = start_date + timedelta(
                            days=day, 
                            hours=post_num * hours_between_posts
                        )
                        
                        # Insert scheduled post
                        cursor.execute("""
                            INSERT INTO campaign_posts (
                                campaign_id, channel_id, post_content, 
                                scheduled_time, status
                            ) VALUES (?, ?, ?, ?, 'scheduled')
                        """, (
                            campaign_id, channel, 
                            f"Campaign {campaign_id} - Post {posts_scheduled + 1}",
                            scheduled_time
                        ))
                        
                        posts_scheduled += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Scheduled {posts_scheduled} posts for campaign {campaign_id}")
            return posts_scheduled
            
        except Exception as e:
            logger.error(f"❌ Error scheduling campaign posts: {e}")
            return 0
    
    async def get_campaign_summary(self, campaign_id: str, language: str = 'en') -> str:
        """Generate campaign summary text with multilingual support"""
        campaign = await self.get_campaign_by_id(campaign_id)
        
        if not campaign:
            if language == 'ar':
                return "❌ لم يتم العثور على الحملة"
            elif language == 'ru':
                return "❌ Кампания не найдена"
            else:
                return "❌ Campaign not found"
        
        # Calculate progress
        total_posts = campaign.get('total_posts', 0)
        posts_published = campaign.get('posts_published', 0)
        progress_percentage = (posts_published / total_posts * 100) if total_posts > 0 else 0
        
        # Calculate remaining days
        end_date = datetime.fromisoformat(campaign['end_date'])
        remaining_days = max(0, (end_date - datetime.now()).days)
        
        # Generate multilingual summary using HTML formatting for better compatibility
        if language == 'ar':
            summary = f"""🎯 <b>بطاقة تعريف الحملة</b>

<b>معرف الحملة:</b> {campaign['campaign_id']}
<b>الحالة:</b> {'نشط' if campaign['status'] == 'active' else 'غير نشط'}
<b>الدفع:</b> {campaign['payment_amount']:.3f} {campaign['payment_method']}
<b>المذكرة:</b> {campaign['payment_memo']}

📅 <b>الجدولة</b>
<b>المدة:</b> {campaign['duration_days']} أيام
<b>المتبقي:</b> {remaining_days} أيام
<b>تاريخ البدء:</b> {datetime.fromisoformat(campaign['start_date']).strftime('%Y-%m-%d')}
<b>تاريخ الانتهاء:</b> {end_date.strftime('%Y-%m-%d')}

📊 <b>تفاصيل الحملة</b>
<b>المنشورات يومياً:</b> {campaign['posts_per_day']}
<b>إجمالي المنشورات:</b> {total_posts}
<b>تم النشر:</b> {posts_published}
<b>التقدم:</b> {progress_percentage:.1f}%

📢 <b>القنوات ({campaign['channel_count']})</b>
{chr(10).join(f"• {channel}" for channel in campaign['selected_channels'])}
<b>إجمالي المتابعين:</b> {campaign['total_reach']} متابع

📈 <b>الأداء</b>
<b>نقاط التفاعل:</b> {campaign.get('engagement_score', 0.0):.1f}%
<b>معدل النقر:</b> {campaign.get('click_through_rate', 0.0):.1f}%

<b>تاريخ الإنشاء:</b> {datetime.fromisoformat(campaign['created_at']).strftime('%Y-%m-%d %H:%M')}"""
        elif language == 'ru':
            summary = f"""🎯 <b>ID карта кампании</b>

<b>ID кампании:</b> {campaign['campaign_id']}
<b>Статус:</b> {'АКТИВНА' if campaign['status'] == 'active' else 'НЕАКТИВНА'}
<b>Платеж:</b> {campaign['payment_amount']:.3f} {campaign['payment_method']}
<b>Мемо:</b> {campaign['payment_memo']}

📅 <b>Расписание</b>
<b>Длительность:</b> {campaign['duration_days']} дней
<b>Осталось:</b> {remaining_days} дней
<b>Дата начала:</b> {datetime.fromisoformat(campaign['start_date']).strftime('%Y-%m-%d')}
<b>Дата окончания:</b> {end_date.strftime('%Y-%m-%d')}

📊 <b>Детали кампании</b>
<b>Постов в день:</b> {campaign['posts_per_day']}
<b>Всего постов:</b> {total_posts}
<b>Опубликовано:</b> {posts_published}
<b>Прогресс:</b> {progress_percentage:.1f}%

📢 <b>Каналы ({campaign['channel_count']})</b>
{chr(10).join(f"• {channel}" for channel in campaign['selected_channels'])}
<b>Общий охват:</b> {campaign['total_reach']} подписчиков

📈 <b>Производительность</b>
<b>Оценка вовлеченности:</b> {campaign.get('engagement_score', 0.0):.1f}%
<b>CTR:</b> {campaign.get('click_through_rate', 0.0):.1f}%

<b>Создано:</b> {datetime.fromisoformat(campaign['created_at']).strftime('%Y-%m-%d %H:%M')}"""
        else:
            summary = f"""🎯 <b>Campaign ID Card</b>

<b>Campaign ID:</b> {campaign['campaign_id']}
<b>Status:</b> {campaign['status'].upper()}
<b>Payment:</b> {campaign['payment_amount']:.3f} {campaign['payment_method']}
<b>Memo:</b> {campaign['payment_memo']}

📅 <b>Schedule</b>
<b>Duration:</b> {campaign['duration_days']} days
<b>Remaining:</b> {remaining_days} days
<b>Start Date:</b> {datetime.fromisoformat(campaign['start_date']).strftime('%Y-%m-%d')}
<b>End Date:</b> {end_date.strftime('%Y-%m-%d')}

📊 <b>Campaign Details</b>
<b>Posts per Day:</b> {campaign['posts_per_day']}
<b>Total Posts:</b> {total_posts}
<b>Published:</b> {posts_published}
<b>Progress:</b> {progress_percentage:.1f}%

📢 <b>Channels ({campaign['channel_count']})</b>
{chr(10).join(f"• {channel}" for channel in campaign['selected_channels'])}
<b>Total Reach:</b> {campaign['total_reach']} subscribers

📈 <b>Performance</b>
<b>Engagement Score:</b> {campaign.get('engagement_score', 0.0):.1f}%
<b>Click-Through Rate:</b> {campaign.get('click_through_rate', 0.0):.1f}%

<b>Created:</b> {datetime.fromisoformat(campaign['created_at']).strftime('%Y-%m-%d %H:%M')}"""
        
        return summary
    
    async def update_campaign_status(self, campaign_id: str, status: str):
        """Update campaign status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE campaigns 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE campaign_id = ?
            """, (status, campaign_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Updated campaign {campaign_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating campaign status: {e}")
            return False

# Global campaign manager instance
campaign_manager = CampaignManager()

async def init_campaign_system():
    """Initialize campaign management system"""
    return await campaign_manager.init_tables()

async def create_campaign_for_payment(user_id: int, payment_memo: str, payment_amount: float,
                                    ad_data: Dict[str, Any], payment_method: str = 'TON') -> str:
    """Create campaign when payment is confirmed"""
    return await campaign_manager.create_campaign(user_id, payment_memo, payment_amount, ad_data, payment_method)

async def get_campaign_details(campaign_id: str) -> Optional[Dict[str, Any]]:
    """Get campaign details by ID"""
    return await campaign_manager.get_campaign_by_id(campaign_id)

async def get_user_campaign_list(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user's campaigns"""
    return await campaign_manager.get_user_campaigns(user_id, limit)

async def create_campaign_for_payment(user_id: int, payment_memo: str, payment_amount: float, 
                                    ad_data: Dict[str, Any], payment_method: str = 'TON') -> str:
    """Create campaign for payment confirmation - FIXES BUG WHERE NEW CAMPAIGNS DON'T APPEAR"""
    return await campaign_manager.create_campaign(user_id, payment_memo, payment_amount, ad_data, payment_method)

async def get_campaign_id_card(campaign_id: str, language: str = 'en') -> str:
    """Get campaign ID card summary with language support"""
    return await campaign_manager.get_campaign_summary(campaign_id, language)

if __name__ == "__main__":
    async def test_campaign_system():
        """Test campaign management system"""
        await init_campaign_system()
        
        # Test campaign creation
        test_ad_data = {
            'duration_days': 7,
            'posts_per_day': 2,
            'selected_channels': ['@i3lani', '@smshco', '@Five_SAR'],
            'total_reach': 357,
            'ad_content': 'Test advertisement content'
        }
        
        campaign_id = await create_campaign_for_payment(
            123456, "TE1234", 0.36, test_ad_data, "TON"
        )
        
        if campaign_id:
            print(f"✅ Created campaign: {campaign_id}")
            
            # Test campaign details
            details = await get_campaign_details(campaign_id)
            print(f"📋 Campaign details: {details}")
            
            # Test ID card
            id_card = await get_campaign_id_card(campaign_id)
            print(f"🎯 Campaign ID Card:\n{id_card}")
        else:
            print("❌ Failed to create campaign")
    
    asyncio.run(test_campaign_system())