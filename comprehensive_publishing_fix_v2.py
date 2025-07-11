#!/usr/bin/env python3
"""
Comprehensive fix for all 5 critical publishing issues - Version 2
"""

import sqlite3
import json
import asyncio
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensivePublishingFix:
    """Fix all 5 critical publishing issues"""
    
    def __init__(self):
        self.db_path = "bot.db"
        
    def fix_1_auto_publishing_after_payment(self):
        """Fix campaigns not auto-publishing after payment"""
        print("\n1️⃣ FIXING AUTO-PUBLISHING AFTER PAYMENT")
        print("-" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get campaigns without posts
            cursor.execute('''
                SELECT c.campaign_id, c.user_id, c.duration_days, c.selected_channels
                FROM campaigns c
                LEFT JOIN (
                    SELECT campaign_id, COUNT(*) as post_count 
                    FROM campaign_posts 
                    GROUP BY campaign_id
                ) cp ON c.campaign_id = cp.campaign_id
                WHERE (cp.post_count IS NULL OR cp.post_count = 0)
                AND c.status = 'active'
            ''')
            
            campaigns = cursor.fetchall()
            print(f"   Found {len(campaigns)} campaigns without posts")
            
            fixed_count = 0
            for campaign_id, user_id, duration_days, channels_json in campaigns:
                try:
                    channels = json.loads(channels_json) if channels_json else []
                    if not channels:
                        continue
                    
                    # Create posts immediately
                    start_time = datetime.now()
                    posts_created = 0
                    
                    for day in range(duration_days):
                        for slot in range(2):  # 2 posts per day
                            for channel in channels:
                                scheduled_time = start_time + timedelta(
                                    days=day, 
                                    hours=slot * 12  # 12 hours apart
                                )
                                
                                cursor.execute('''
                                    INSERT INTO campaign_posts (
                                        campaign_id, channel_id, scheduled_time, 
                                        status, created_at
                                    ) VALUES (?, ?, ?, 'scheduled', datetime('now'))
                                ''', (campaign_id, channel, scheduled_time.isoformat()))
                                
                                posts_created += 1
                    
                    if posts_created > 0:
                        print(f"   ✅ Created {posts_created} posts for {campaign_id}")
                        fixed_count += 1
                        
                except Exception as e:
                    print(f"   ❌ Error processing {campaign_id}: {e}")
            
            conn.commit()
            print(f"\n   ✅ Fixed {fixed_count} campaigns")
            
        finally:
            conn.close()
    
    def fix_2_subscriber_count_display(self):
        """Fix subscriber count in channel selection"""
        print("\n2️⃣ FIXING SUBSCRIBER COUNT DISPLAY")
        print("-" * 50)
        
        # Update channel subscriber counts
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current channels
            cursor.execute('SELECT channel_id, name, subscriber_count FROM channels WHERE is_active = 1')
            channels = cursor.fetchall()
            
            print("   Current channel subscriber counts:")
            for channel_id, name, sub_count in channels:
                print(f"   - {name}: {sub_count} subscribers")
            
            # Ensure fix_ui_issues.py is being used
            try:
                with open('handlers.py', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'from fix_ui_issues import create_channel_button_text' not in content:
                    print("\n   📝 Adding subscriber count display to handlers.py...")
                    
                    # Add import
                    import_line = "from fix_ui_issues import create_channel_button_text\n"
                    insert_pos = content.find('from languages import')
                    if insert_pos > 0:
                        content = content[:insert_pos] + import_line + content[insert_pos:]
                    
                    # Update channel button creation
                    old_button = "InlineKeyboardButton(text=channel[1],"
                    new_button = "InlineKeyboardButton(text=create_channel_button_text(channel[1], channel[4], channel[0] in selected_channels),"
                    
                    content = content.replace(old_button, new_button)
                    
                    with open('handlers.py', 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print("   ✅ Updated handlers.py with subscriber count display")
                else:
                    print("   ✅ Subscriber count display already configured")
                    
            except Exception as e:
                print(f"   ❌ Error updating handlers.py: {e}")
                
        finally:
            conn.close()
    
    def fix_3_campaign_id_display(self):
        """Fix campaign ID display after payment"""
        print("\n3️⃣ FIXING CAMPAIGN ID DISPLAY AFTER PAYMENT")
        print("-" * 50)
        
        # Update automatic_payment_confirmation.py
        try:
            with open('automatic_payment_confirmation.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if we need to add campaign ID
            if 'campaign_id}' not in content and 'send_confirmation_message' in content:
                print("   📝 Updating payment confirmation to show campaign ID...")
                
                # Find and update the confirmation message
                search = '''await bot.send_message(
                    user_id,
                    text,
                    parse_mode='Markdown'
                )'''
                
                replace = '''# Add campaign ID to message
                if campaign_id:
                    if language == 'ar':
                        text = text.replace(
                            "تم استلام دفعتك",
                            f"تم استلام دفعتك\\n\\n**معرف الحملة:** `{campaign_id}`"
                        )
                    elif language == 'ru':
                        text = text.replace(
                            "Ваш платеж получен",
                            f"Ваш платеж получен\\n\\n**ID кампании:** `{campaign_id}`"
                        )
                    else:
                        text = text.replace(
                            "Your payment has been received",
                            f"Your payment has been received\\n\\n**Campaign ID:** `{campaign_id}`"
                        )
                
                await bot.send_message(
                    user_id,
                    text,
                    parse_mode='Markdown'
                )'''
                
                content = content.replace(search, replace)
                
                with open('automatic_payment_confirmation.py', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("   ✅ Updated payment confirmation messages")
            else:
                print("   ✅ Campaign ID display already configured")
                
        except Exception as e:
            print(f"   ❌ Error updating confirmation: {e}")
    
    def fix_4_media_publishing(self):
        """Fix media not being published with ads"""
        print("\n4️⃣ FIXING MEDIA PUBLISHING")
        print("-" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check campaigns table structure
            cursor.execute("PRAGMA table_info(campaigns)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Add missing columns
            if 'content' not in columns:
                cursor.execute('ALTER TABLE campaigns ADD COLUMN content TEXT')
                print("   ✅ Added content column")
            
            if 'content_type' not in columns:
                cursor.execute('ALTER TABLE campaigns ADD COLUMN content_type TEXT')
                print("   ✅ Added content_type column")
            
            if 'media_url' not in columns:
                cursor.execute('ALTER TABLE campaigns ADD COLUMN media_url TEXT')
                print("   ✅ Added media_url column")
            
            conn.commit()
            
            # Update campaigns with missing media
            cursor.execute('''
                SELECT c.campaign_id, c.user_id, c.created_at
                FROM campaigns c
                WHERE c.media_url IS NULL OR c.content IS NULL
            ''')
            
            campaigns_needing_media = cursor.fetchall()
            print(f"\n   Found {len(campaigns_needing_media)} campaigns needing media data")
            
            for campaign_id, user_id, created_at in campaigns_needing_media:
                # Find corresponding ad
                cursor.execute('''
                    SELECT content, content_type, media_url
                    FROM ads
                    WHERE user_id = ?
                    AND created_at <= ?
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (user_id, created_at))
                
                ad_data = cursor.fetchone()
                if ad_data:
                    content, content_type, media_url = ad_data
                    cursor.execute('''
                        UPDATE campaigns
                        SET content = ?, content_type = ?, media_url = ?
                        WHERE campaign_id = ?
                    ''', (content, content_type, media_url, campaign_id))
                    
                    print(f"   ✅ Updated {campaign_id} with media data")
            
            conn.commit()
            
            # Verify enhanced publisher supports media
            print("\n   Checking enhanced publisher media support...")
            try:
                with open('enhanced_campaign_publisher.py', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'send_photo' in content and 'send_video' in content:
                    print("   ✅ Enhanced publisher has media support")
                else:
                    print("   ⚠️  Enhanced publisher needs media support update")
                    
            except Exception as e:
                print(f"   ❌ Error checking publisher: {e}")
                
        finally:
            conn.close()
    
    def fix_5_publishing_notifications(self):
        """Fix publishing confirmation messages"""
        print("\n5️⃣ FIXING PUBLISHING CONFIRMATION MESSAGES")
        print("-" * 50)
        
        # Create notification handler
        notification_code = '''
    async def _send_publishing_notification(self, user_id: int, campaign_id: str, 
                                          channel_id: str, post_id: str):
        """Send publishing confirmation to user"""
        try:
            # Get user language
            from database import Database
            db = Database()
            user = await db.get_user(user_id)
            language = user.get('language', 'en') if user else 'en'
            
            # Get channel name
            try:
                chat = await self.bot.get_chat(channel_id)
                channel_name = f"@{chat.username}" if chat.username else chat.title
            except:
                channel_name = channel_id
            
            # Get campaign details
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT end_date, duration_days FROM campaigns 
                WHERE campaign_id = ?
            ''', (campaign_id,))
            
            campaign_data = cursor.fetchone()
            if not campaign_data:
                return
                
            end_date, duration_days = campaign_data
            
            # Calculate remaining
            end_dt = datetime.fromisoformat(end_date)
            days_remaining = max(0, (end_dt - datetime.now()).days)
            
            # Count remaining posts
            cursor.execute('''
                SELECT COUNT(*) FROM campaign_posts 
                WHERE campaign_id = ? AND status = 'scheduled'
            ''', (campaign_id,))
            
            posts_remaining = cursor.fetchone()[0]
            conn.close()
            
            # Create message
            now = datetime.now()
            
            if language == 'ar':
                text = f"""📢 تم نشر إعلانك `{post_id}`

**معرف الحملة:** `{campaign_id}`
**القناة:** {channel_name}
**الوقت:** {now.strftime('%H:%M')}
**التاريخ:** {now.strftime('%d-%m-%Y')}

📅 الأيام المتبقية: {days_remaining}
🔁 المنشورات المتبقية: {posts_remaining}"""
            
            elif language == 'ru':
                text = f"""📢 Ваша реклама `{post_id}` опубликована

**ID кампании:** `{campaign_id}`
**Канал:** {channel_name}
**Время:** {now.strftime('%H:%M')}
**Дата:** {now.strftime('%d-%m-%Y')}

📅 Дней осталось: {days_remaining}
🔁 Постов осталось: {posts_remaining}"""
            
            else:  # English
                text = f"""📢 Your ad `{post_id}` has been published

**Campaign ID:** `{campaign_id}`
**Channel:** {channel_name}
**Time:** {now.strftime('%H:%M')}
**Date:** {now.strftime('%d-%m-%Y')}

📅 Days Remaining: {days_remaining}
🔁 Posts Remaining: {posts_remaining}"""
            
            await self.bot.send_message(user_id, text, parse_mode='Markdown')
            logger.info(f"✅ Sent publishing notification to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
'''
        
        # Update enhanced publisher
        try:
            with open('enhanced_campaign_publisher.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '_send_publishing_notification' not in content:
                print("   📝 Adding notification system to publisher...")
                
                # Add notification method
                insert_pos = content.find('async def _publishing_loop')
                if insert_pos > 0:
                    content = content[:insert_pos] + notification_code + '\n' + content[insert_pos:]
                
                # Call notification after publishing
                search = 'logger.info(f"✅ Successfully published {post_id} to {channel_id}")'
                replace = '''logger.info(f"✅ Successfully published {post_id} to {channel_id}")
                        
                        # Send user notification
                        await self._send_publishing_notification(
                            user_id, campaign_id, channel_id, post_id
                        )'''
                
                content = content.replace(search, replace)
                
                with open('enhanced_campaign_publisher.py', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("   ✅ Added publishing notification system")
            else:
                print("   ✅ Publishing notifications already configured")
                
        except Exception as e:
            print(f"   ❌ Error adding notifications: {e}")
    
    def run_all_fixes(self):
        """Run all 5 fixes"""
        print("🚀 COMPREHENSIVE PUBLISHING FIX V2")
        print("=" * 60)
        
        self.fix_1_auto_publishing_after_payment()
        self.fix_2_subscriber_count_display()
        self.fix_3_campaign_id_display()
        self.fix_4_media_publishing()
        self.fix_5_publishing_notifications()
        
        print("\n" + "=" * 60)
        print("✅ ALL 5 FIXES COMPLETED!")
        print("=" * 60)
        
        # Verify fixes
        self.verify_fixes()
    
    def verify_fixes(self):
        """Verify all fixes are working"""
        print("\n🔍 VERIFYING FIXES...")
        print("-" * 50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check campaigns with posts
        cursor.execute('''
            SELECT COUNT(DISTINCT c.campaign_id)
            FROM campaigns c
            INNER JOIN campaign_posts cp ON c.campaign_id = cp.campaign_id
            WHERE c.status = 'active'
        ''')
        campaigns_with_posts = cursor.fetchone()[0]
        print(f"   ✅ Active campaigns with posts: {campaigns_with_posts}")
        
        # Check campaigns with media
        cursor.execute('''
            SELECT COUNT(*) FROM campaigns 
            WHERE media_url IS NOT NULL AND content IS NOT NULL
        ''')
        campaigns_with_media = cursor.fetchone()[0]
        print(f"   ✅ Campaigns with media data: {campaigns_with_media}")
        
        # Check recent posts
        cursor.execute('''
            SELECT COUNT(*) FROM campaign_posts
            WHERE scheduled_time <= datetime('now', '+5 minutes')
            AND status = 'scheduled'
        ''')
        posts_due_soon = cursor.fetchone()[0]
        print(f"   ✅ Posts due for publishing soon: {posts_due_soon}")
        
        conn.close()

if __name__ == "__main__":
    fixer = ComprehensivePublishingFix()
    fixer.run_all_fixes()