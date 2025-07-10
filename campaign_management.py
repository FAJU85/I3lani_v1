#!/usr/bin/env python3
"""
Ad Campaign Identification System
Generates unique campaign IDs and manages campaign metadata
"""

import asyncio
import logging
import sqlite3
import json
import string
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    def generate_campaign_id(self) -> str:
        """Generate unique campaign ID"""
        # Format: CAM-YYYY-MM-XXXX (e.g., CAM-2025-07-A1B2)
        current_year = datetime.now().strftime("%Y")
        current_month = datetime.now().strftime("%m")
        
        # Generate 4-character alphanumeric suffix
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"CAM-{current_year}-{current_month}-{suffix}"
    
    async def create_campaign(self, user_id: int, payment_memo: str, payment_amount: float,
                            ad_data: Dict[str, Any], payment_method: str = 'TON') -> str:
        """Create new campaign with unique ID"""
        try:
            # Generate unique campaign ID
            campaign_id = self.generate_campaign_id()
            
            # Ensure uniqueness
            while await self.campaign_exists(campaign_id):
                campaign_id = self.generate_campaign_id()
            
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
            
            # Insert campaign
            cursor.execute("""
                INSERT INTO campaigns (
                    campaign_id, user_id, payment_memo, payment_method, payment_amount,
                    campaign_name, ad_content, duration_days, posts_per_day, total_posts,
                    selected_channels, channel_count, total_reach, start_date, end_date,
                    status, campaign_metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                campaign_id, user_id, payment_memo, payment_method, payment_amount,
                f"Campaign {campaign_id}", ad_data.get('ad_content', f'Advertisement campaign for payment {payment_memo}'),
                duration_days, posts_per_day, total_posts,
                ','.join(selected_channels), len(selected_channels), total_reach,
                start_date, end_date, 'active', json.dumps(campaign_metadata)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created campaign {campaign_id} for user {user_id}")
            
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
        
        # Generate multilingual summary
        if language == 'ar':
            summary = f"""🎯 **بطاقة تعريف الحملة**

**معرف الحملة:** {campaign['campaign_id']}
**الحالة:** {'نشط' if campaign['status'] == 'active' else 'غير نشط'}
**الدفع:** {campaign['payment_amount']:.3f} {campaign['payment_method']}
**المذكرة:** {campaign['payment_memo']}

**📅 الجدولة**
**المدة:** {campaign['duration_days']} أيام
**المتبقي:** {remaining_days} أيام
**تاريخ البدء:** {datetime.fromisoformat(campaign['start_date']).strftime('%Y-%m-%d')}
**تاريخ الانتهاء:** {end_date.strftime('%Y-%m-%d')}

**📊 تفاصيل الحملة**
**المنشورات يومياً:** {campaign['posts_per_day']}
**إجمالي المنشورات:** {total_posts}
**تم النشر:** {posts_published}
**التقدم:** {progress_percentage:.1f}%

**📢 القنوات ({campaign['channel_count']})**
{chr(10).join(f"• {channel}" for channel in campaign['selected_channels'])}
**إجمالي المتابعين:** {campaign['total_reach']} متابع

**📈 الأداء**
**نقاط التفاعل:** {campaign.get('engagement_score', 0.0):.1f}%
**معدل النقر:** {campaign.get('click_through_rate', 0.0):.1f}%

**تاريخ الإنشاء:** {datetime.fromisoformat(campaign['created_at']).strftime('%Y-%m-%d %H:%M')}"""
        elif language == 'ru':
            summary = f"""🎯 **ID карта кампании**

**ID кампании:** {campaign['campaign_id']}
**Статус:** {'АКТИВНА' if campaign['status'] == 'active' else 'НЕАКТИВНА'}
**Платеж:** {campaign['payment_amount']:.3f} {campaign['payment_method']}
**Мемо:** {campaign['payment_memo']}

**📅 Расписание**
**Длительность:** {campaign['duration_days']} дней
**Осталось:** {remaining_days} дней
**Дата начала:** {datetime.fromisoformat(campaign['start_date']).strftime('%Y-%m-%d')}
**Дата окончания:** {end_date.strftime('%Y-%m-%d')}

**📊 Детали кампании**
**Постов в день:** {campaign['posts_per_day']}
**Всего постов:** {total_posts}
**Опубликовано:** {posts_published}
**Прогресс:** {progress_percentage:.1f}%

**📢 Каналы ({campaign['channel_count']})**
{chr(10).join(f"• {channel}" for channel in campaign['selected_channels'])}
**Общий охват:** {campaign['total_reach']} подписчиков

**📈 Производительность**
**Оценка вовлеченности:** {campaign.get('engagement_score', 0.0):.1f}%
**CTR:** {campaign.get('click_through_rate', 0.0):.1f}%

**Создано:** {datetime.fromisoformat(campaign['created_at']).strftime('%Y-%m-%d %H:%M')}"""
        else:
            summary = f"""🎯 **Campaign ID Card**

**Campaign ID:** {campaign['campaign_id']}
**Status:** {campaign['status'].upper()}
**Payment:** {campaign['payment_amount']:.3f} {campaign['payment_method']}
**Memo:** {campaign['payment_memo']}

**📅 Schedule**
**Duration:** {campaign['duration_days']} days
**Remaining:** {remaining_days} days
**Start Date:** {datetime.fromisoformat(campaign['start_date']).strftime('%Y-%m-%d')}
**End Date:** {end_date.strftime('%Y-%m-%d')}

**📊 Campaign Details**
**Posts per Day:** {campaign['posts_per_day']}
**Total Posts:** {total_posts}
**Published:** {posts_published}
**Progress:** {progress_percentage:.1f}%

**📢 Channels ({campaign['channel_count']})**
{chr(10).join(f"• {channel}" for channel in campaign['selected_channels'])}
**Total Reach:** {campaign['total_reach']} subscribers

**📈 Performance**
**Engagement Score:** {campaign.get('engagement_score', 0.0):.1f}%
**Click-Through Rate:** {campaign.get('click_through_rate', 0.0):.1f}%

**Created:** {datetime.fromisoformat(campaign['created_at']).strftime('%Y-%m-%d %H:%M')}"""
        
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