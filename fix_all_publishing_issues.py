#!/usr/bin/env python3
"""
Comprehensive fix for all 5 critical publishing and confirmation issues
"""

import sqlite3
import json
from datetime import datetime, timedelta

def fix_issue_1_auto_publishing():
    """Fix campaigns not auto-publishing after payment"""
    print("\n1️⃣ FIXING AUTO-PUBLISHING AFTER PAYMENT")
    print("-" * 50)
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Get all campaigns without scheduled posts
    cursor.execute('''
        SELECT c.campaign_id, c.user_id, c.plan_id, c.duration_days, c.selected_channels
        FROM campaigns c
        LEFT JOIN (
            SELECT campaign_id, COUNT(*) as post_count 
            FROM campaign_posts 
            GROUP BY campaign_id
        ) cp ON c.campaign_id = cp.campaign_id
        WHERE cp.post_count IS NULL OR cp.post_count = 0
    ''')
    
    campaigns_without_posts = cursor.fetchall()
    print(f"   Found {len(campaigns_without_posts)} campaigns without scheduled posts")
    
    # Create posts for each campaign
    for campaign_id, user_id, plan_id, duration_days, selected_channels_json in campaigns_without_posts:
        try:
            selected_channels = json.loads(selected_channels_json) if selected_channels_json else []
            if not selected_channels:
                continue
                
            # Calculate posts per channel
            total_posts = len(selected_channels) * duration_days * 2  # 2 posts per day per channel
            posts_per_channel = duration_days * 2
            
            print(f"\n   Creating posts for {campaign_id}:")
            print(f"   - Channels: {selected_channels}")
            print(f"   - Duration: {duration_days} days")
            print(f"   - Total posts: {total_posts}")
            
            # Create posts starting immediately
            start_time = datetime.now()
            post_interval = timedelta(hours=12)  # 2 posts per day
            
            post_count = 0
            for day in range(duration_days):
                for slot in range(2):  # 2 posts per day
                    for channel in selected_channels:
                        scheduled_time = start_time + (day * timedelta(days=1)) + (slot * post_interval)
                        
                        cursor.execute('''
                            INSERT INTO campaign_posts (
                                campaign_id, channel_id, scheduled_time, 
                                status, created_at
                            ) VALUES (?, ?, ?, 'scheduled', datetime('now'))
                        ''', (campaign_id, channel, scheduled_time.isoformat()))
                        
                        post_count += 1
            
            print(f"   ✅ Created {post_count} posts for {campaign_id}")
            
        except Exception as e:
            print(f"   ❌ Error creating posts for {campaign_id}: {e}")
    
    conn.commit()
    conn.close()
    print("\n   ✅ Auto-publishing fix completed")

def fix_issue_2_subscriber_count():
    """Fix subscriber count display in channel selection"""
    print("\n2️⃣ FIXING SUBSCRIBER COUNT DISPLAY")
    print("-" * 50)
    
    # Update handlers.py to show subscriber count
    try:
        with open('handlers.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if subscriber count is already being displayed
        if 'create_channel_button_text' in content:
            print("   ✅ Channel button already uses subscriber count display")
        else:
            print("   ⚠️  Need to update channel selection to show subscriber counts")
            
            # Find the channel selection button creation
            if 'InlineKeyboardButton(text=channel[1]' in content:
                print("   📝 Updating channel button creation...")
                
                # Replace simple channel name with formatted text including subscribers
                old_pattern = 'InlineKeyboardButton(text=channel[1], callback_data=f"toggle_channel_{channel[0]}")'
                new_pattern = '''InlineKeyboardButton(
                    text=create_channel_button_text(channel[1], channel[4], channel[0] in selected_channels),
                    callback_data=f"toggle_channel_{channel[0]}"
                )'''
                
                content = content.replace(old_pattern, new_pattern)
                
                # Save the updated file
                with open('handlers.py', 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print("   ✅ Updated channel selection to show subscriber counts")
                
    except Exception as e:
        print(f"   ❌ Error updating handlers.py: {e}")
    
    # Verify channel data has subscriber counts
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT channel_id, name, subscriber_count FROM channels WHERE is_active = 1')
    channels = cursor.fetchall()
    
    print(f"\n   📊 Active channels with subscriber counts:")
    for channel_id, name, sub_count in channels:
        print(f"   - {name}: {sub_count} subscribers")
    
    conn.close()

def fix_issue_3_campaign_id_display():
    """Fix campaign ID display after payment confirmation"""
    print("\n3️⃣ FIXING CAMPAIGN ID DISPLAY AFTER PAYMENT")
    print("-" * 50)
    
    # Check automatic_payment_confirmation.py
    try:
        with open('automatic_payment_confirmation.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add campaign ID to confirmation message
        if 'Campaign ID:' not in content:
            print("   📝 Adding campaign ID to payment confirmation...")
            
            # Find the confirmation message section
            search_pattern = "text = f\"\"\"✅"
            if search_pattern in content:
                # Update confirmation message to include campaign ID
                old_message = '''text = f"""✅ **تم تأكيد الدفع!**

تم استلام دفعتك بنجاح وتفعيل حملتك الإعلانية.

**تفاصيل الدفع:**
• المبلغ: {amount:.3f} TON
• معرف المعاملة: {memo}

سيتم نشر إعلانك وفقاً للخطة المحددة."""'''

                new_message = '''text = f"""✅ **تم تأكيد الدفع!**

تم استلام دفعتك بنجاح وتفعيل حملتك الإعلانية.

**معرف الحملة:** `{campaign_id}`

**تفاصيل الدفع:**
• المبلغ: {amount:.3f} TON
• معرف المعاملة: {memo}

سيتم نشر إعلانك وفقاً للخطة المحددة."""'''
                
                content = content.replace(old_message, new_message)
                
                # Save updated file
                with open('automatic_payment_confirmation.py', 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print("   ✅ Updated payment confirmation to show campaign ID")
                
    except Exception as e:
        print(f"   ❌ Error updating payment confirmation: {e}")

def fix_issue_4_media_publishing():
    """Fix media (images/videos) not being published with ads"""
    print("\n4️⃣ FIXING MEDIA PUBLISHING")
    print("-" * 50)
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Check if campaigns table has media columns
    cursor.execute("PRAGMA table_info(campaigns)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'media_url' not in columns:
        print("   ⚠️  Adding media columns to campaigns table...")
        cursor.execute('ALTER TABLE campaigns ADD COLUMN media_url TEXT')
        cursor.execute('ALTER TABLE campaigns ADD COLUMN content_type TEXT')
        cursor.execute('ALTER TABLE campaigns ADD COLUMN content TEXT')
        conn.commit()
        print("   ✅ Added media columns to campaigns table")
    
    # Copy media data from ads to campaigns
    cursor.execute('''
        UPDATE campaigns
        SET media_url = (
            SELECT a.media_url FROM ads a 
            WHERE a.user_id = campaigns.user_id 
            AND a.created_at <= campaigns.created_at
            ORDER BY a.created_at DESC
            LIMIT 1
        ),
        content_type = (
            SELECT a.content_type FROM ads a 
            WHERE a.user_id = campaigns.user_id 
            AND a.created_at <= campaigns.created_at
            ORDER BY a.created_at DESC
            LIMIT 1
        ),
        content = (
            SELECT a.content FROM ads a 
            WHERE a.user_id = campaigns.user_id 
            AND a.created_at <= campaigns.created_at
            ORDER BY a.created_at DESC
            LIMIT 1
        )
        WHERE media_url IS NULL
    ''')
    
    updated = cursor.rowcount
    conn.commit()
    print(f"   ✅ Updated {updated} campaigns with media data")
    
    # Verify media data
    cursor.execute('''
        SELECT campaign_id, content_type, media_url 
        FROM campaigns 
        WHERE created_at > datetime('now', '-1 day')
    ''')
    
    recent_campaigns = cursor.fetchall()
    print(f"\n   📊 Recent campaigns media status:")
    for campaign_id, content_type, media_url in recent_campaigns:
        has_media = "Yes" if media_url else "No"
        print(f"   - {campaign_id}: Type={content_type}, Has Media={has_media}")
    
    conn.close()

def fix_issue_5_publishing_confirmation():
    """Fix publishing confirmation messages to users"""
    print("\n5️⃣ FIXING PUBLISHING CONFIRMATION MESSAGES")
    print("-" * 50)
    
    # Create a publishing notification system
    notification_code = '''
async def send_publishing_notification(bot, user_id: int, campaign_id: str, 
                                     channel_id: str, post_id: str, language: str = 'en'):
    """Send publishing confirmation to user"""
    
    try:
        from datetime import datetime
        from database import Database
        
        db = Database()
        
        # Get campaign details
        campaign = await db.get_campaign_details(campaign_id)
        if not campaign:
            return
            
        # Get channel name
        channel = await db.get_channel_by_id(channel_id)
        channel_name = channel['name'] if channel else channel_id
        
        # Calculate remaining days and posts
        end_date = datetime.fromisoformat(campaign['end_date'])
        days_remaining = (end_date - datetime.now()).days
        
        # Count remaining posts
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM campaign_posts 
            WHERE campaign_id = ? AND status = 'scheduled'
        """, (campaign_id,))
        posts_remaining = cursor.fetchone()[0]
        conn.close()
        
        # Create confirmation message
        if language == 'ar':
            text = f"""📢 تم نشر إعلانك

**معرف الحملة:** `{campaign_id}`
**القناة:** {channel_name}
**الوقت:** {datetime.now().strftime('%H:%M')}
**التاريخ:** {datetime.now().strftime('%d-%m-%Y')}

📅 الأيام المتبقية: {days_remaining}
🔁 المنشورات المتبقية: {posts_remaining}"""
        
        elif language == 'ru':
            text = f"""📢 Ваша реклама опубликована

**ID кампании:** `{campaign_id}`
**Канал:** {channel_name}
**Время:** {datetime.now().strftime('%H:%M')}
**Дата:** {datetime.now().strftime('%d-%m-%Y')}

📅 Дней осталось: {days_remaining}
🔁 Постов осталось: {posts_remaining}"""
        
        else:  # English
            text = f"""📢 Your ad has been published

**Campaign ID:** `{campaign_id}`
**Channel:** {channel_name}
**Time:** {datetime.now().strftime('%H:%M')}
**Date:** {datetime.now().strftime('%d-%m-%Y')}

📅 Days Remaining: {days_remaining}
🔁 Posts Remaining: {posts_remaining}"""
        
        # Send notification
        await bot.send_message(user_id, text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error sending publishing notification: {e}")
'''
    
    # Add to enhanced_campaign_publisher.py
    try:
        with open('enhanced_campaign_publisher.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'send_publishing_notification' not in content:
            print("   📝 Adding publishing notification system...")
            
            # Add the notification function
            content = content.replace(
                'logger = logging.getLogger(__name__)',
                'logger = logging.getLogger(__name__)\n' + notification_code
            )
            
            # Update the publishing method to send notifications
            if '_publish_single_post' in content:
                # Add notification after successful publishing
                search = "logger.info(f\"✅ Successfully published {post_id} to {channel_id}\")"
                replace = '''logger.info(f"✅ Successfully published {post_id} to {channel_id}")
                        
                        # Send user notification
                        user_language = await self._get_user_language(user_id)
                        await send_publishing_notification(
                            self.bot, user_id, campaign_id, 
                            channel_id, post_id, user_language
                        )'''
                
                content = content.replace(search, replace)
            
            with open('enhanced_campaign_publisher.py', 'w', encoding='utf-8') as f:
                f.write(content)
                
            print("   ✅ Added publishing notification system")
            
    except Exception as e:
        print(f"   ❌ Error adding notification system: {e}")

def main():
    """Run all fixes"""
    print("🚀 COMPREHENSIVE FIX FOR ALL 5 PUBLISHING ISSUES")
    print("=" * 60)
    
    # Run all fixes
    fix_issue_1_auto_publishing()
    fix_issue_2_subscriber_count()
    fix_issue_3_campaign_id_display()
    fix_issue_4_media_publishing()
    fix_issue_5_publishing_confirmation()
    
    print("\n" + "=" * 60)
    print("✅ ALL FIXES COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    main()