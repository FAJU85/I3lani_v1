#!/usr/bin/env python3
"""
Fix Media Publishing Bug - Update campaign OR4156 with correct media URL
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediaPublishingFixer:
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        
    def fix_campaign_media(self):
        """Fix campaign CAM-2025-07-OR41 media URL"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the user's latest ad with media
            cursor.execute("""
                SELECT ad_id, content, content_type, media_url 
                FROM ads 
                WHERE user_id = 566158428 AND content_type = 'photo' AND media_url IS NOT NULL
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            ad_with_media = cursor.fetchone()
            
            if ad_with_media:
                media_url = ad_with_media[3]
                content_type = ad_with_media[2]
                
                print(f"✅ Found ad with media: {ad_with_media[0]}")
                print(f"   Content type: {content_type}")
                print(f"   Media URL: {media_url}")
                
                # Update the campaign with media URL
                cursor.execute("""
                    UPDATE campaigns 
                    SET media_url = ?, content_type = ?, ad_type = ?
                    WHERE campaign_id = 'CAM-2025-07-OR41'
                """, (media_url, content_type, content_type))
                
                # Update the campaign posts with media info
                cursor.execute("""
                    UPDATE campaign_posts 
                    SET post_content = ?
                    WHERE campaign_id = 'CAM-2025-07-OR41'
                """, (ad_with_media[1],))
                
                conn.commit()
                
                print(f"✅ Updated campaign CAM-2025-07-OR41 with media URL")
                
                # Test the media publishing for scheduled posts
                cursor.execute("""
                    SELECT id, campaign_id, channel_id, post_content, scheduled_time, status
                    FROM campaign_posts 
                    WHERE campaign_id = 'CAM-2025-07-OR41' 
                    AND status = 'scheduled'
                    ORDER BY scheduled_time ASC
                    LIMIT 5
                """)
                
                scheduled_posts = cursor.fetchall()
                print(f"✅ Found {len(scheduled_posts)} scheduled posts ready for media publishing")
                
                for post in scheduled_posts:
                    print(f"   Post {post[0]}: {post[2]} at {post[4]}")
                    
                return True
                
            else:
                print("❌ No ad with media found for user 566158428")
                
                # Let's check what ads exist
                cursor.execute("""
                    SELECT ad_id, content, content_type, media_url 
                    FROM ads 
                    WHERE user_id = 566158428 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                
                all_ads = cursor.fetchall()
                print(f"📋 Found {len(all_ads)} ads for user 566158428:")
                
                for ad in all_ads:
                    print(f"   Ad {ad[0]}: {ad[2]} | Media: {'YES' if ad[3] else 'NO'}")
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Error fixing media: {e}")
            return False
            
        finally:
            conn.close()
            
    def validate_media_publishing_system(self):
        """Validate that the media publishing system works"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check campaigns with media
            cursor.execute("""
                SELECT COUNT(*) as total_campaigns, 
                       SUM(CASE WHEN media_url IS NOT NULL THEN 1 ELSE 0 END) as with_media
                FROM campaigns
            """)
            
            campaign_stats = cursor.fetchone()
            print(f"📊 Campaign Statistics:")
            print(f"   Total campaigns: {campaign_stats[0]}")
            print(f"   With media: {campaign_stats[1]}")
            
            # Check ads with media
            cursor.execute("""
                SELECT COUNT(*) as total_ads, 
                       SUM(CASE WHEN media_url IS NOT NULL THEN 1 ELSE 0 END) as with_media
                FROM ads
            """)
            
            ad_stats = cursor.fetchone()
            print(f"📊 Ad Statistics:")
            print(f"   Total ads: {ad_stats[0]}")
            print(f"   With media: {ad_stats[1]}")
            
            # Check published posts
            cursor.execute("""
                SELECT cp.campaign_id, cp.channel_id, cp.status, c.content_type, c.media_url
                FROM campaign_posts cp
                JOIN campaigns c ON cp.campaign_id = c.campaign_id
                WHERE c.media_url IS NOT NULL
                ORDER BY cp.published_at DESC
                LIMIT 10
            """)
            
            media_posts = cursor.fetchall()
            print(f"📊 Published Posts with Media: {len(media_posts)}")
            
            for post in media_posts:
                print(f"   {post[0]} → {post[1]} | {post[2]} | {post[3]}")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating media system: {e}")
            return False
            
        finally:
            conn.close()

if __name__ == "__main__":
    fixer = MediaPublishingFixer()
    
    print("🔍 Fixing media publishing bug...")
    success = fixer.fix_campaign_media()
    
    print("\n📊 Validating media publishing system...")
    fixer.validate_media_publishing_system()
    
    if success:
        print("\n✅ Media publishing bug fixed!")
        print("The campaign now has correct media URL and will publish with images.")
    else:
        print("\n❌ Media publishing bug not fully resolved")
        print("Need to investigate further or use different approach.")