#!/usr/bin/env python3
"""
Fix BB1775 campaign with the correct ad containing "t1" pattern
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_and_update_t1_ad():
    """Find ad with t1 pattern and update BB1775 campaign"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        print("🔍 Searching for ads with 't1' pattern...")
        
        # Search for ads with t1 pattern
        cursor.execute("""
            SELECT ad_id, content, content_type, media_url, created_at
            FROM ads 
            WHERE user_id = 566158428 
            AND (content LIKE '%t1%' OR content LIKE '%T1%' OR 
                 content LIKE '%(t1)%' OR content LIKE '%(T1)%' OR 
                 content LIKE '%( t1 )%' OR content LIKE '%( T1 )%')
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        t1_ads = cursor.fetchall()
        
        if t1_ads:
            print(f"✅ Found {len(t1_ads)} ads with 't1' pattern:")
            for ad in t1_ads:
                print(f"   Ad {ad[0]} ({ad[4]}): {ad[1][:100]}...")
                print(f"   Type: {ad[2]}, Media: {'YES' if ad[3] else 'NO'}")
                print()
                
            # Use the most recent one
            correct_ad = t1_ads[0]
            
            print(f"🎯 Using Ad {correct_ad[0]} for BB1775 campaign...")
            
            # Update campaign with correct content
            cursor.execute("""
                UPDATE campaigns 
                SET ad_content = ?, content_type = ?, media_url = ?
                WHERE campaign_id = 'CAM-2025-07-BB17'
            """, (correct_ad[1], correct_ad[2], correct_ad[3]))
            
            # Update all scheduled posts with new content
            cursor.execute("""
                UPDATE campaign_posts 
                SET post_content = ?
                WHERE campaign_id = 'CAM-2025-07-BB17' AND status = 'scheduled'
            """, (correct_ad[1],))
            
            conn.commit()
            
            print("✅ Campaign BB1775 updated successfully!")
            print(f"   Content: {correct_ad[1][:150]}...")
            print(f"   Type: {correct_ad[2]}")
            print(f"   Media: {'YES' if correct_ad[3] else 'NO'}")
            
            return True
            
        else:
            print("❌ No ads found with 't1' pattern")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error updating campaign: {e}")
        return False
        
    finally:
        conn.close()

def verify_campaign_update():
    """Verify the campaign was updated correctly"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Check campaign
        cursor.execute("""
            SELECT campaign_id, ad_content, content_type, media_url, status
            FROM campaigns 
            WHERE campaign_id = 'CAM-2025-07-BB17'
        """)
        
        campaign = cursor.fetchone()
        if campaign:
            print("📊 Updated campaign status:")
            print(f"   Campaign: {campaign[0]}")
            print(f"   Content: {campaign[1][:200]}...")
            print(f"   Type: {campaign[2]}")
            print(f"   Media: {'YES' if campaign[3] else 'NO'}")
            print(f"   Status: {campaign[4]}")
            
            # Check if posts were updated
            cursor.execute("""
                SELECT COUNT(*) as total_posts,
                       SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled_posts,
                       SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published_posts
                FROM campaign_posts 
                WHERE campaign_id = 'CAM-2025-07-BB17'
            """)
            
            stats = cursor.fetchone()
            print(f"   Posts: {stats[0]} total, {stats[1]} scheduled, {stats[2]} published")
            
            return True
        else:
            print("❌ Campaign not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verifying campaign: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔍 Finding and updating BB1775 campaign with 't1' ad...")
    
    success = find_and_update_t1_ad()
    
    if success:
        print("\n✅ Verifying campaign update...")
        verify_campaign_update()
        print("\n🎉 BB1775 campaign updated with correct 't1' ad!")
        print("The automatic publishing system will now use the correct content.")
    else:
        print("\n❌ Could not find ad with 't1' pattern")
        print("Please check the ad content or provide more details.")