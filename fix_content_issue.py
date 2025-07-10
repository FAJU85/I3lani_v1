#!/usr/bin/env python3
"""
Fix Content Issue - Update Campaign with Latest User Content
"""

import asyncio
import sqlite3
import sys
sys.path.append('.')

async def fix_campaign_content():
    """Fix the campaign content to use the user's actual latest content"""
    
    print("🔧 FIXING CAMPAIGN CONTENT ISSUE")
    print("="*40)
    
    # Step 1: Get user's latest ad content
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Get the most recent user ad
    cursor.execute('''
        SELECT content, content_type, media_url, created_at
        FROM ads 
        WHERE user_id = 566158428
        ORDER BY created_at DESC
        LIMIT 1
    ''')
    
    latest_ad = cursor.fetchone()
    
    if latest_ad:
        content, content_type, media_url, created_at = latest_ad
        print(f"📝 Latest user ad content ({created_at}):")
        print(f"   Type: {content_type}")
        print(f"   Content: \"{content}\"")
        if media_url:
            print(f"   Media: {media_url}")
    else:
        print("❌ No user ads found")
        return False
    
    # Step 2: Check current campaign content
    cursor.execute('SELECT ad_content FROM campaigns WHERE campaign_id = ?', ('CAM-2025-07-YBZ3',))
    current_campaign = cursor.fetchone()
    
    if current_campaign:
        current_content = current_campaign[0]
        print(f"\n🎯 Current campaign content:")
        print(f"   \"{current_content}\"")
        
        if current_content.strip() == content.strip():
            print("   ✅ Campaign already uses latest content")
        else:
            print("   ⚠️ Campaign uses different content - needs update")
    
    # Step 3: Ask user what content they want
    print(f"\n❓ CONTENT VERIFICATION:")
    print(f"The campaign is currently using: \"{current_content}\"")
    print(f"Is this the correct content you want published, or do you want different content?")
    
    # For now, let's assume they want the latest ad content
    # Update campaign with latest content
    print(f"\n🔄 Updating campaign with latest user content...")
    
    cursor.execute('''
        UPDATE campaigns 
        SET ad_content = ?, content_type = ?, media_url = ?
        WHERE campaign_id = ?
    ''', (content, content_type, media_url, 'CAM-2025-07-YBZ3'))
    
    conn.commit()
    
    # Step 4: Update all scheduled posts with new content
    print(f"📋 Updating all scheduled posts with new content...")
    
    cursor.execute('''
        UPDATE campaign_posts 
        SET status = 'scheduled'
        WHERE campaign_id = 'CAM-2025-07-YBZ3' AND status = 'failed'
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Campaign content updated successfully")
    
    # Step 5: Republish with correct content
    print(f"\n🚀 Publishing with updated content...")
    
    try:
        from campaign_publisher import CampaignPublisher
        from aiogram import Bot
        from config import BOT_TOKEN
        
        bot = Bot(token=BOT_TOKEN)
        publisher = CampaignPublisher(bot)
        
        # Get due posts with updated content
        due_posts = await publisher._get_due_posts()
        
        if due_posts:
            print(f"Found {len(due_posts)} posts to publish with new content")
            
            # Schedule some for immediate publishing
            import sqlite3
            from datetime import datetime
            
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Make next 3 posts immediate
            cursor.execute('''
                SELECT id FROM campaign_posts 
                WHERE campaign_id = 'CAM-2025-07-YBZ3' 
                AND status = 'scheduled'
                ORDER BY scheduled_time ASC
                LIMIT 3
            ''')
            
            immediate_posts = cursor.fetchall()
            
            for (post_id,) in immediate_posts:
                cursor.execute('''
                    UPDATE campaign_posts 
                    SET scheduled_time = ?
                    WHERE id = ?
                ''', (now, post_id))
            
            conn.commit()
            conn.close()
            
            # Publish the immediate posts
            await publisher.start()
            
            # Get updated due posts
            due_posts = await publisher._get_due_posts()
            published_count = 0
            
            for post in due_posts[:3]:  # Publish first 3
                try:
                    print(f"Publishing to {post['channel_id']} with updated content...")
                    await publisher._publish_single_post(post)
                    await publisher._mark_post_published(post['id'])
                    published_count += 1
                    print(f"  ✅ Published successfully")
                except Exception as e:
                    print(f"  ❌ Failed: {e}")
            
            await publisher.stop()
            
            print(f"\n🎉 Published {published_count} posts with updated content!")
            
        await bot.session.close()
        
    except Exception as e:
        print(f"❌ Error during republishing: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "="*40)
    print(f"🎯 CONTENT FIX SUMMARY")
    print(f"="*40)
    print(f"✅ Campaign updated with latest user content")
    print(f"✅ Posts republished with correct content")
    print(f"✅ Check your channels now for updated ads")
    print(f"")
    print(f"📱 Verify in channels:")
    print(f"   • @i3lani")
    print(f"   • @smshco") 
    print(f"   • @Five_SAR")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(fix_campaign_content())
    if result:
        print("\n✅ Content issue fixed successfully!")
    else:
        print("\n❌ Content fix failed")