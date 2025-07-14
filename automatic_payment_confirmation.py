#!/usr/bin/env python3
"""
Automatic Payment Confirmation System
Sends automatic confirmations to users when payments are detected
"""

import asyncio
import logging
from automatic_language_system import get_user_language_auto
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomaticPaymentConfirmation:
    """Automatic payment confirmation system"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        
    async def init_tables(self):
        """Initialize payment tracking tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create payment_memo_tracking table for user -> memo mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_memo_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    memo TEXT NOT NULL UNIQUE,
                    amount REAL NOT NULL,
                    payment_method TEXT DEFAULT 'TON',
                    ad_data TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confirmed_at TIMESTAMP NULL
                );
            """)
            
            # Create index for faster memo lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memo_tracking_memo 
                ON payment_memo_tracking(memo);
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Payment confirmation tables initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing confirmation tables: {e}")
            return False
    
    async def track_user_payment(self, user_id: int, memo: str, amount: float, ad_data: dict = None):
        """Track user payment for automatic confirmation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ALWAYS get actual user ad content to ensure real content is used
            actual_ad_content = await self._get_user_ad_content(user_id)
            if actual_ad_content:
                if not ad_data:
                    ad_data = {}
                # Override any existing content with actual user content
                ad_data.update(actual_ad_content)
                logger.info(f"✅ Retrieved real user content for user {user_id}: {actual_ad_content.get('ad_content', '')[:50]}...")
            
            # Store ad_data as JSON - prioritize real user content
            if ad_data and ad_data.get('ad_content'):
                ad_data_json = json.dumps(ad_data)
                logger.info(f"✅ Stored real user content: {ad_data.get('ad_content', '')[:50]}...")
            else:
                # Fallback only if no real content available
                ad_data_json = json.dumps({
                    'duration_days': 7,
                    'posts_per_day': 2,
                    'selected_channels': ['@i3lani', '@smshco', '@Five_SAR'],
                    'total_reach': 357,
                    'ad_content': f'Fallback content for user {user_id} - no ad found'
                })
                logger.warning(f"⚠️ Using fallback content for user {user_id} - no real ad content found")
            
            cursor.execute("""
                INSERT OR REPLACE INTO payment_memo_tracking 
                (user_id, memo, amount, ad_data, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (user_id, memo, amount, ad_data_json))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Tracking payment {memo} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error tracking user payment: {e}")
            return False
    
    async def find_user_by_memo(self, memo: str) -> Optional[Dict[str, Any]]:
        """Find user by payment memo"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, memo, amount, ad_data, status, created_at
                FROM payment_memo_tracking 
                WHERE memo = ? AND status = 'pending'
            """, (memo,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_id': row['user_id'],
                    'memo': row['memo'],
                    'amount': row['amount'],
                    'ad_data': json.loads(row['ad_data']) if row['ad_data'] else {},
                    'status': row['status'],
                    'created_at': row['created_at']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding user by memo: {e}")
            return None
    
    async def send_post_package_confirmation(self, user_id: int, memo: str, amount: float, package_data: dict):
        """Send automatic confirmation for post package purchase"""
        try:
            from main_bot import bot_instance
            
            if not bot_instance:
                logger.error("❌ Bot instance not available")
                return False
            
            # Get user language
            user_language = await get_user_language_auto(user_id)
            
            # Extract package information
            package_name = package_data.get('package_name', 'Post Package')
            posts_total = package_data.get('posts_total', 0)
            auto_schedule_days = package_data.get('auto_schedule_days', 0)
            selected_addons = package_data.get('selected_addons', [])
            
            # Create confirmation message
            if user_language == 'ar':
                confirmation_message = f"""✅ **تم شراء حزمة المنشورات بنجاح!**

💰 **المبلغ المدفوع:** {amount} نجمة
🆔 **معرف المعاملة:** {memo}
📅 **التاريخ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📦 **تفاصيل الحزمة:**
• اسم الحزمة: {package_name}
• عدد المنشورات: {posts_total}
• ينتهي في: 90 يوم"""
                
                if auto_schedule_days > 0:
                    confirmation_message += f"\n• أيام الجدولة التلقائية: {auto_schedule_days}"
                
                if selected_addons:
                    confirmation_message += f"\n• الإضافات: {len(selected_addons)} إضافة"
                
                confirmation_message += "\n\n🎉 أصبحت حزمة المنشورات جاهزة للاستخدام!"
                
            elif user_language == 'ru':
                confirmation_message = f"""✅ **Пакет постов успешно куплен!**

💰 **Оплачено:** {amount} звезд
🆔 **ID транзакции:** {memo}
📅 **Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📦 **Детали пакета:**
• Название пакета: {package_name}
• Количество постов: {posts_total}
• Истекает через: 90 дней"""
                
                if auto_schedule_days > 0:
                    confirmation_message += f"\n• Дни автопланирования: {auto_schedule_days}"
                
                if selected_addons:
                    confirmation_message += f"\n• Дополнения: {len(selected_addons)} дополнений"
                
                confirmation_message += "\n\n🎉 Пакет постов готов к использованию!"
                
            else:  # English
                confirmation_message = f"""✅ **Post Package Purchase Confirmed!**

💰 **Amount Paid:** {amount} Stars
🆔 **Transaction ID:** {memo}
📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📦 **Package Details:**
• Package Name: {package_name}
• Posts Count: {posts_total}
• Expires in: 90 days"""
                
                if auto_schedule_days > 0:
                    confirmation_message += f"\n• Auto-schedule days: {auto_schedule_days}"
                
                if selected_addons:
                    confirmation_message += f"\n• Add-ons: {len(selected_addons)} add-ons"
                
                confirmation_message += "\n\n🎉 Your post package is ready to use!"
            
            # Create navigation keyboard
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            if user_language == 'ar':
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")],
                    [InlineKeyboardButton(text="📊 حملاتي", callback_data="my_ads")],
                    [InlineKeyboardButton(text="📝 إنشاء إعلان", callback_data="create_ad")]
                ])
            elif user_language == 'ru':
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")],
                    [InlineKeyboardButton(text="📊 Мои кампании", callback_data="my_ads")],
                    [InlineKeyboardButton(text="📝 Создать рекламу", callback_data="create_ad")]
                ])
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")],
                    [InlineKeyboardButton(text="📊 My Campaigns", callback_data="my_ads")],
                    [InlineKeyboardButton(text="📝 Create Ad", callback_data="create_ad")]
                ])
            
            # Process the post package purchase
            await self.process_post_package_purchase(user_id, memo, amount, package_data)
            
            # Mark as confirmed
            await self.mark_payment_confirmed(memo)
            
            # Send confirmation message
            await bot_instance.send_message(
                chat_id=user_id,
                text=confirmation_message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Post package confirmation sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending post package confirmation: {e}")
            return False
    
    async def process_post_package_purchase(self, user_id: int, memo: str, amount: float, package_data: dict):
        """Process post package purchase and add credits to user account"""
        try:
            from user_post_manager import get_user_post_manager
            
            post_manager = get_user_post_manager()
            
            # Add post credits
            package_name = package_data.get('package_name', 'Post Package')
            posts_total = package_data.get('posts_total', 0)
            
            if posts_total > 0:
                credit_id = await post_manager.add_post_credits(
                    user_id=user_id,
                    package_name=package_name,
                    posts_count=posts_total,
                    purchase_id=memo
                )
                logger.info(f"✅ Added {posts_total} post credits to user {user_id} (credit_id: {credit_id})")
            
            # Add auto-schedule days if purchased
            auto_schedule_days = package_data.get('auto_schedule_days', 0)
            if auto_schedule_days > 0:
                schedule_id = await post_manager.add_auto_schedule_days(
                    user_id=user_id,
                    days=auto_schedule_days,
                    price_paid=auto_schedule_days * 0.25  # $0.25 per day
                )
                logger.info(f"✅ Added {auto_schedule_days} auto-schedule days to user {user_id} (schedule_id: {schedule_id})")
            
            # Add any selected add-ons
            selected_addons = package_data.get('selected_addons', [])
            for addon_key in selected_addons:
                addon_id = await post_manager.add_addon_purchase(
                    user_id=user_id,
                    addon_key=addon_key,
                    addon_name=addon_key.replace('_', ' ').title(),
                    price_paid=0.50,  # Approximate add-on price
                    uses=1
                )
                logger.info(f"✅ Added addon {addon_key} to user {user_id} (addon_id: {addon_id})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing post package purchase: {e}")
            return False
    
    async def send_ton_post_package_confirmation(self, user_id: int, memo: str, amount: float, package_data: dict):
        """Send automatic confirmation for TON post package purchase"""
        try:
            from main_bot import bot_instance
            
            if not bot_instance:
                logger.error("❌ Bot instance not available")
                return False
            
            # Get user language
            user_language = await get_user_language_auto(user_id)
            
            # Extract package information
            package_name = package_data.get('package_name', 'Post Package')
            posts_total = package_data.get('posts_total', 0)
            auto_schedule_days = package_data.get('auto_schedule_days', 0)
            selected_addons = package_data.get('selected_addons', [])
            
            # Create confirmation message
            if user_language == 'ar':
                confirmation_message = f"""✅ **تم شراء حزمة المنشورات بعملة TON بنجاح!**

💰 **المبلغ المدفوع:** {amount:.3f} TON
🆔 **معرف المعاملة:** {memo}
📅 **التاريخ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📦 **تفاصيل الحزمة:**
• اسم الحزمة: {package_name}
• عدد المنشورات: {posts_total}
• ينتهي في: 90 يوم"""
                
                if auto_schedule_days > 0:
                    confirmation_message += f"\n• أيام الجدولة التلقائية: {auto_schedule_days}"
                
                if selected_addons:
                    confirmation_message += f"\n• الإضافات: {len(selected_addons)} إضافة"
                
                confirmation_message += "\n\n🎉 أصبحت حزمة المنشورات جاهزة للاستخدام!"
                
            elif user_language == 'ru':
                confirmation_message = f"""✅ **Пакет постов куплен за TON!**

💰 **Оплачено:** {amount:.3f} TON
🆔 **ID транзакции:** {memo}
📅 **Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📦 **Детали пакета:**
• Название пакета: {package_name}
• Количество постов: {posts_total}
• Истекает через: 90 дней"""
                
                if auto_schedule_days > 0:
                    confirmation_message += f"\n• Дни автопланирования: {auto_schedule_days}"
                
                if selected_addons:
                    confirmation_message += f"\n• Дополнения: {len(selected_addons)} дополнений"
                
                confirmation_message += "\n\n🎉 Пакет постов готов к использованию!"
                
            else:  # English
                confirmation_message = f"""✅ **Post Package Purchase Confirmed with TON!**

💰 **Amount Paid:** {amount:.3f} TON
🆔 **Transaction ID:** {memo}
📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📦 **Package Details:**
• Package Name: {package_name}
• Posts Count: {posts_total}
• Expires in: 90 days"""
                
                if auto_schedule_days > 0:
                    confirmation_message += f"\n• Auto-schedule days: {auto_schedule_days}"
                
                if selected_addons:
                    confirmation_message += f"\n• Add-ons: {len(selected_addons)} add-ons"
                
                confirmation_message += "\n\n🎉 Your post package is ready to use!"
            
            # Create navigation keyboard
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            if user_language == 'ar':
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")],
                    [InlineKeyboardButton(text="📊 حملاتي", callback_data="my_ads")],
                    [InlineKeyboardButton(text="📝 إنشاء إعلان", callback_data="create_ad")]
                ])
            elif user_language == 'ru':
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")],
                    [InlineKeyboardButton(text="📊 Мои кампании", callback_data="my_ads")],
                    [InlineKeyboardButton(text="📝 Создать рекламу", callback_data="create_ad")]
                ])
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")],
                    [InlineKeyboardButton(text="📊 My Campaigns", callback_data="my_ads")],
                    [InlineKeyboardButton(text="📝 Create Ad", callback_data="create_ad")]
                ])
            
            # Process the post package purchase
            await self.process_post_package_purchase(user_id, memo, amount, package_data)
            
            # Mark as confirmed
            await self.mark_payment_confirmed(memo)
            
            # Send confirmation message
            await bot_instance.send_message(
                chat_id=user_id,
                text=confirmation_message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ TON post package confirmation sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending TON post package confirmation: {e}")
            return False
    
    async def send_automatic_confirmation(self, user_id: int, memo: str, amount: float, ad_data: dict):
        """Send automatic confirmation to user"""
        try:
            from main_bot import bot_instance
            
            if not bot_instance:
                logger.error("❌ Bot instance not available")
                return False
            
            # Get actual user ad content with media if exists
            user_ad_content = await self._get_user_ad_content(user_id)
            if user_ad_content:
                # Update ad_data with actual content and media
                ad_data['ad_content'] = user_ad_content.get('ad_content', ad_data.get('ad_content', ''))
                ad_data['content_type'] = user_ad_content.get('content_type', 'text')
                ad_data['media_url'] = user_ad_content.get('media_url')
                logger.info(f"✅ Retrieved user ad content: type={ad_data['content_type']}, has_media={bool(ad_data['media_url'])}")
            
            # Create confirmation message
            confirmation_message = f"""✅ **Payment Automatically Confirmed!**

💰 **Amount:** {amount} TON
🎫 **Transaction ID:** {memo}
📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎉 **Your advertisement campaign is now ACTIVE!**

**Campaign Details:**
• Duration: {ad_data.get('duration_days', 7)} days
• Channels: {len(ad_data.get('selected_channels', []))} channels
• Total reach: {ad_data.get('total_reach', 357)} subscribers
• Posts per day: {ad_data.get('posts_per_day', 2)} posts

Your advertisement will be published across selected channels according to your schedule.

Thank you for choosing I3lani! 🚀"""
            
            # Create navigation keyboard
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")],
                [InlineKeyboardButton(text="📊 My Ads", callback_data="my_ads")]
            ])
            
            # Mark as confirmed
            await self.mark_payment_confirmed(memo)
            
            # Activate campaign and get campaign ID
            campaign_id = await self.activate_campaign(user_id, memo, amount, ad_data)
            
            # Get user language
            db = await Database().get_user(user_id)
            language = db.get('language', 'en') if db else 'en'
            
            # Update confirmation message to include campaign ID
            if campaign_id:
                # Format confirmation message with campaign details
                duration = ad_data.get('duration_days', 7)
                channels = ad_data.get('selected_channels', [])
                posts_per_day = ad_data.get('posts_per_day', 2)
                total_posts = duration * posts_per_day * len(channels)
                
                if language == 'ar':
                    confirmation_message = f"""✅ تم تأكيد دفع TON!

تم التحقق من دفع TON الخاص بك على البلوك تشين!

💰 المبلغ المستلم: {amount:.3f} TON

📅 مدة الحملة: {duration} أيام
📊 تكرار النشر: {posts_per_day} مرة يومياً
📺 القنوات: {len(channels)} قناة
📈 إجمالي المنشورات: {total_posts} منشور

رقم الحملة الإعلانية: {campaign_id}
🚀 حملتك الإعلانية تبدأ الآن!
🟢 الحالة: نشط

📱 ستتلقى إشعارات عند نشر إعلانك في كل قناة

🎯 شكراً لاختيار I3lani!"""
                elif language == 'ru':
                    confirmation_message = f"""✅ TON платеж подтвержден!

Ваш TON платеж был проверен в блокчейне!

💰 Получено: {amount:.3f} TON

📅 Длительность кампании: {duration} дней
📊 Частота публикации: {posts_per_day} раз в день
📺 Каналы: {len(channels)} канала
📈 Всего постов: {total_posts} постов

ID кампании: {campaign_id}
🚀 Ваша рекламная кампания начинается!
🟢 Статус: Активен

📱 Вы получите уведомления при публикации в каждом канале

🎯 Спасибо за выбор I3lani!"""
                else:  # English
                    confirmation_message = f"""✅ TON Payment Confirmed!

Your TON payment has been verified on blockchain!

💰 Amount Received: {amount:.3f} TON

📅 Campaign Duration: {duration} days
📊 Publishing Frequency: {posts_per_day} times daily
📺 Channels: {len(channels)} channels
📈 Total Posts: {total_posts} posts

Campaign ID: {campaign_id}
🚀 Your advertising campaign starts now!
🟢 Status: Active

📱 You'll receive notifications when your ad is published in each channel

🎯 Thank you for choosing I3lani!"""
            
            # Send confirmation with campaign ID
            await bot_instance.send_message(
                user_id, 
                confirmation_message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Automatic confirmation sent to user {user_id} for memo {memo}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending automatic confirmation: {e}")
            return False
    
    async def mark_payment_confirmed(self, memo: str):
        """Mark payment as confirmed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE payment_memo_tracking 
                SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
                WHERE memo = ?
            """, (memo,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Payment {memo} marked as confirmed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking payment confirmed: {e}")
            return False
    
    async def mark_payment_confirmed(self, memo: str, campaign_id: str = None):
        """Mark payment as confirmed with optional campaign ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE payment_memo_tracking 
                SET status = 'confirmed', 
                    confirmed_at = CURRENT_TIMESTAMP,
                    ad_data = CASE 
                        WHEN ? IS NOT NULL THEN 
                            json_set(COALESCE(ad_data, '{}'), '$.campaign_id', ?)
                        ELSE ad_data 
                    END
                WHERE memo = ?
            """, (campaign_id, campaign_id, memo))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Payment {memo} marked as confirmed with campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking payment confirmed: {e}")
            return False
    
    async def activate_campaign(self, user_id: int, memo: str, amount: float, ad_data: dict):
        """Activate user campaign with unique ID and execute comprehensive publishing workflow"""
        try:
            # Create campaign using the new campaign management system
            from campaign_management import create_campaign_for_payment
            
            campaign_id = await create_campaign_for_payment(
                user_id, memo, amount, ad_data, 'TON'
            )
            
            if campaign_id:
                logger.info(f"✅ Campaign {campaign_id} activated for user {user_id}, memo {memo}")
                
                # CRITICAL: Execute comprehensive publishing workflow
                try:
                    from comprehensive_publishing_workflow import execute_post_payment_publishing
                    from config import BOT_TOKEN
                    from aiogram import Bot
                    
                    bot = Bot(token=BOT_TOKEN)
                    publishing_result = await execute_post_payment_publishing(bot, campaign_id)
                    
                    logger.info(f"✅ Publishing workflow executed: {publishing_result.get_success_rate():.1f}% success rate")
                    
                    if publishing_result.is_complete_success():
                        logger.info(f"🎉 Campaign {campaign_id} successfully published to all channels")
                    else:
                        logger.warning(f"⚠️ Campaign {campaign_id} had publishing issues: {len(publishing_result.failed_channels)} failed channels")
                        
                except Exception as e:
                    logger.error(f"❌ Error executing publishing workflow for campaign {campaign_id}: {e}")
                    # Don't fail the campaign creation if publishing fails
                    
                return campaign_id
            else:
                logger.error(f"❌ Failed to create campaign for user {user_id}, memo {memo}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error activating campaign: {e}")
            return False
    
    async def _get_user_ad_content(self, user_id: int) -> dict:
        """Get actual user ad content from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get most recent ad by user
            cursor.execute('''
                SELECT ad_id, content, content_type, media_url
                FROM ads 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'ad_content': row['content'],
                    'content_type': row['content_type'],
                    'media_url': row['media_url'],
                    'ad_id': row['ad_id']
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting user ad content: {e}")
            return {}

# Global instance
automatic_confirmation = AutomaticPaymentConfirmation()

async def init_automatic_confirmation():
    """Initialize automatic confirmation system"""
    return await automatic_confirmation.init_tables()

async def track_payment_for_user(user_id: int, memo: str, amount: float, ad_data: dict = None):
    """Track payment for automatic confirmation"""
    return await automatic_confirmation.track_user_payment(user_id, memo, amount, ad_data)

async def handle_confirmed_payment(payment_data: dict):
    """Handle confirmed payment and create campaign automatically"""
    try:
        user_id = payment_data['user_id']
        memo = payment_data['memo']
        amount = payment_data['amount']
        currency = payment_data.get('currency', 'TON')
        payment_method = payment_data.get('payment_method', 'blockchain')
        
        logger.info(f"🎯 Processing confirmed {currency} payment: user {user_id}, memo {memo}, amount {amount}")
        
        # Get tracked payment data
        user_data = await automatic_confirmation.find_user_by_memo(memo)
        
        if not user_data:
            logger.error(f"❌ No tracked payment found for memo {memo}")
            return False
        
        # Create campaign automatically using campaign management system
        try:
            from campaign_management import create_campaign_for_payment
            
            campaign_data = {
                'user_id': user_id,
                'payment_memo': memo,
                'payment_amount': amount,
                'payment_currency': currency,
                'payment_method': payment_method,
                'ad_data': user_data.get('ad_data', {})
            }
            
            campaign_id = await create_campaign_for_payment(campaign_data)
            
            if campaign_id:
                logger.info(f"✅ Campaign {campaign_id} created for {currency} payment {memo}")
                
                # Mark payment as confirmed
                await automatic_confirmation.mark_payment_confirmed(memo, campaign_id)
                
                return True
            else:
                logger.error(f"❌ Failed to create campaign for {currency} payment {memo}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating campaign for {currency} payment: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error handling confirmed {payment_data.get('currency', 'unknown')} payment: {e}")
        return False

async def process_detected_payment(memo: str, amount: float):
    """Process payment detected by scanner"""
    user_data = await automatic_confirmation.find_user_by_memo(memo)
    
    if user_data:
        logger.info(f"🎯 Found user {user_data['user_id']} for memo {memo}")
        
        # Check if this is a post package purchase
        ad_data = user_data.get('ad_data', {})
        if ad_data.get('type') == 'post_package':
            # This is a post package purchase via TON
            package_data = {
                'package_name': ad_data.get('package_name', 'Post Package'),
                'posts_total': ad_data.get('posts_total', 0),
                'auto_schedule_days': ad_data.get('auto_schedule_days', 0),
                'selected_addons': ad_data.get('selected_addons', [])
            }
            
            success = await automatic_confirmation.send_ton_post_package_confirmation(
                user_data['user_id'],
                memo,
                amount,
                package_data
            )
            
            if success:
                logger.info(f"✅ TON post package confirmation sent for memo {memo}")
            else:
                logger.error(f"❌ Failed to send TON post package confirmation for memo {memo}")
                
            return success
        else:
            # Regular campaign payment
            success = await automatic_confirmation.send_automatic_confirmation(
                user_data['user_id'],
                memo,
                amount,
                user_data['ad_data']
            )
            
            if success:
                logger.info(f"✅ Automatic confirmation sent for memo {memo}")
            else:
                logger.error(f"❌ Failed to send confirmation for memo {memo}")
            
            return success
    else:
        logger.warning(f"⚠️ No user found for memo {memo}")
        return False

if __name__ == "__main__":
    async def test_system():
        await init_automatic_confirmation()
        
        # Test tracking a payment
        await track_payment_for_user(123456, "TE1234", 0.36, {
            'duration_days': 7,
            'posts_per_day': 2,
            'selected_channels': ['@i3lani', '@smshco', '@Five_SAR'],
            'total_reach': 357
        })
        
        # Test processing detected payment
        await process_detected_payment("TE1234", 0.36)
    
    asyncio.run(test_system())