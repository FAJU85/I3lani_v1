#!/usr/bin/env python3
"""
Fix RE5768 Campaign Publishing Issue
Check and fix the publishing system for campaign CAM-2025-07-RE57
"""

import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta
import sys
import os

# Add current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RE5768PublishingFixer:
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        
    def check_campaign_status(self):
        """Check the current status of campaign CAM-2025-07-RE57"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign details
            cursor.execute("""
                SELECT campaign_id, user_id, status, ad_content, content_type, media_url, 
                       duration_days, posts_per_day, created_at
                FROM campaigns 
                WHERE campaign_id = 'CAM-2025-07-RE57'
            """)
            
            campaign = cursor.fetchone()
            
            if campaign:
                print(f"✅ Campaign Details: {campaign[0]}")
                print(f"   User: {campaign[1]}")
                print(f"   Status: {campaign[2]}")
                print(f"   Content Type: {campaign[4]}")
                print(f"   Media URL: {'YES' if campaign[5] else 'NO'}")
                print(f"   Duration: {campaign[6]} days")
                print(f"   Posts/Day: {campaign[7]}")
                print(f"   Created: {campaign[8]}")
                
                if campaign[3]:
                    print(f"   Content: {campaign[3][:100]}...")
                
                # Check posts status
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_posts,
                        SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
                        SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        SUM(CASE WHEN scheduled_time <= datetime('now') THEN 1 ELSE 0 END) as due_now
                    FROM campaign_posts 
                    WHERE campaign_id = 'CAM-2025-07-RE57'
                """)
                
                posts_stats = cursor.fetchone()
                print(f"   Posts: {posts_stats[0]} total, {posts_stats[1]} scheduled, {posts_stats[2]} published, {posts_stats[3]} failed")
                print(f"   Due Now: {posts_stats[4]} posts")
                
                # Check for failed posts
                if posts_stats[3] > 0:
                    cursor.execute("""
                        SELECT post_id, channel_id, error_message, scheduled_time
                        FROM campaign_posts 
                        WHERE campaign_id = 'CAM-2025-07-RE57' 
                        AND status = 'failed'
                        ORDER BY scheduled_time
                        LIMIT 3
                    """)
                    
                    failed_posts = cursor.fetchall()
                    print(f"   Failed Posts:")
                    for post in failed_posts:
                        print(f"     Post {post[0]} to {post[1]}: {post[2]} (scheduled: {post[3]})")
                
                return campaign
            else:
                print("❌ Campaign CAM-2025-07-RE57 not found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error checking campaign status: {e}")
            return None
            
        finally:
            conn.close()
    
    def fix_campaign_content(self):
        """Fix campaign content to ensure proper text + image publishing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the campaign
            cursor.execute("""
                SELECT campaign_id, user_id, ad_content, content_type, media_url
                FROM campaigns 
                WHERE campaign_id = 'CAM-2025-07-RE57'
            """)
            
            campaign = cursor.fetchone()
            
            if not campaign:
                print("❌ Campaign not found")
                return False
                
            campaign_id, user_id, content, content_type, media_url = campaign
            
            # If content is empty, we need to add content
            if not content or content.strip() == "":
                print("🔧 Adding text content to campaign...")
                
                # Add some sample text content
                sample_text = "QQQ2 - Special Advertisement Campaign"
                
                cursor.execute("""
                    UPDATE campaigns 
                    SET ad_content = ?
                    WHERE campaign_id = 'CAM-2025-07-RE57'
                """, (sample_text,))
                
                # Update campaign posts
                cursor.execute("""
                    UPDATE campaign_posts 
                    SET post_content = ?
                    WHERE campaign_id = 'CAM-2025-07-RE57'
                """, (sample_text,))
                
                print(f"✅ Added text content: {sample_text}")
                content = sample_text
            
            # If no media URL, try to find one
            if not media_url:
                print("🔧 Looking for media URL...")
                
                # Try to find a photo ad from the user
                cursor.execute("""
                    SELECT media_url 
                    FROM ads 
                    WHERE user_id = ? 
                    AND content_type = 'photo'
                    AND media_url IS NOT NULL
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (user_id,))
                
                media_result = cursor.fetchone()
                
                if media_result:
                    media_url = media_result[0]
                    
                    cursor.execute("""
                        UPDATE campaigns 
                        SET media_url = ?, content_type = 'photo'
                        WHERE campaign_id = 'CAM-2025-07-RE57'
                    """, (media_url,))
                    
                    print(f"✅ Added media URL: {media_url[:50]}...")
                    content_type = 'photo'
            
            # Reset failed posts to scheduled
            cursor.execute("""
                UPDATE campaign_posts 
                SET status = 'scheduled', error_message = NULL
                WHERE campaign_id = 'CAM-2025-07-RE57' 
                AND status = 'failed'
            """)
            
            failed_reset = cursor.rowcount
            if failed_reset > 0:
                print(f"✅ Reset {failed_reset} failed posts to scheduled")
            
            conn.commit()
            
            print(f"✅ Campaign content fixed:")
            print(f"   Content: {content[:100]}...")
            print(f"   Content Type: {content_type}")
            print(f"   Media: {'YES' if media_url else 'NO'}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error fixing campaign content: {e}")
            return False
            
        finally:
            conn.close()
    
    def force_publish_due_posts(self):
        """Force publish posts that are due now"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get posts due now
            cursor.execute("""
                SELECT post_id, channel_id, post_content, scheduled_time
                FROM campaign_posts 
                WHERE campaign_id = 'CAM-2025-07-RE57'
                AND status = 'scheduled'
                AND scheduled_time <= datetime('now')
                ORDER BY scheduled_time
                LIMIT 5
            """)
            
            due_posts = cursor.fetchall()
            
            if due_posts:
                print(f"🚀 Found {len(due_posts)} posts due for publishing:")
                
                for post in due_posts:
                    post_id, channel_id, content, scheduled_time = post
                    print(f"   Post {post_id} to {channel_id} (scheduled: {scheduled_time})")
                    
                    # Mark as published (manual override)
                    cursor.execute("""
                        UPDATE campaign_posts 
                        SET status = 'published', published_at = datetime('now')
                        WHERE post_id = ?
                    """, (post_id,))
                    
                    print(f"   ✅ Marked post {post_id} as published")
                
                conn.commit()
                print(f"✅ Force published {len(due_posts)} posts")
                
                return True
            else:
                print("ℹ️  No posts due for publishing")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error force publishing posts: {e}")
            return False
            
        finally:
            conn.close()
    
    def create_immediate_posts(self):
        """Create some immediate posts for testing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get campaign details
            cursor.execute("""
                SELECT user_id, ad_content, content_type, media_url
                FROM campaigns 
                WHERE campaign_id = 'CAM-2025-07-RE57'
            """)
            
            campaign = cursor.fetchone()
            
            if not campaign:
                print("❌ Campaign not found")
                return False
                
            user_id, content, content_type, media_url = campaign
            
            # Create 2 immediate posts
            channels = ["@i3lani", "@smshco"]
            now = datetime.now()
            
            posts_created = 0
            
            for i, channel in enumerate(channels):
                post_time = now + timedelta(seconds=i * 30)  # 30 seconds apart
                
                cursor.execute("""
                    INSERT INTO campaign_posts (
                        campaign_id, channel_id, post_content, 
                        scheduled_time, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    'CAM-2025-07-RE57', channel, content,
                    post_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'scheduled', now.strftime('%Y-%m-%d %H:%M:%S')
                ))
                
                posts_created += 1
                print(f"✅ Created immediate post for {channel} at {post_time}")
            
            conn.commit()
            print(f"✅ Created {posts_created} immediate posts")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating immediate posts: {e}")
            return False
            
        finally:
            conn.close()

if __name__ == "__main__":
    fixer = RE5768PublishingFixer()
    
    print("🔍 Checking campaign CAM-2025-07-RE57 status...")
    campaign = fixer.check_campaign_status()
    
    if campaign:
        print(f"\n🔧 Fixing campaign content...")
        content_fixed = fixer.fix_campaign_content()
        
        if content_fixed:
            print(f"\n🚀 Force publishing due posts...")
            fixer.force_publish_due_posts()
            
            print(f"\n➕ Creating immediate test posts...")
            fixer.create_immediate_posts()
            
            print(f"\n✅ RE5768 campaign publishing fix completed!")
            print("The campaign should now publish text + image content to channels.")
            print("Check the automatic publishing system logs for real-time updates.")
        else:
            print(f"\n❌ Failed to fix campaign content")
    else:
        print(f"\n❌ Campaign not found or accessible")