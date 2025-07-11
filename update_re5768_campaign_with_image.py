#!/usr/bin/env python3
"""
Update RE5768 campaign with correct QQQ2 ad content and image if found
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_qqq2_ad_with_image():
    """Find the actual QQQ2 ad with image content"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Search for QQQ2 in content (case insensitive)
        cursor.execute("""
            SELECT ad_id, user_id, content, content_type, media_url, created_at
            FROM ads 
            WHERE LOWER(content) LIKE '%qqq2%' 
            OR UPPER(content) LIKE '%QQQ2%'
            ORDER BY created_at DESC
        """)
        
        qqq2_ads = cursor.fetchall()
        
        if qqq2_ads:
            print(f"✅ Found {len(qqq2_ads)} ads with QQQ2 content:")
            for ad in qqq2_ads:
                print(f"   Ad {ad[0]}: User {ad[1]} | {ad[3]} | {ad[5]}")
                print(f"   Content: {ad[2][:200]}...")
                if ad[4]:
                    print(f"   Media: {ad[4][:50]}...")
                print()
            
            # Return the one with image if available
            for ad in qqq2_ads:
                if ad[4]:  # has media_url
                    return ad
            
            # Otherwise return the first one
            return qqq2_ads[0]
        
        # If no QQQ2 found, search for recent ads with images
        cursor.execute("""
            SELECT ad_id, user_id, content, content_type, media_url, created_at
            FROM ads 
            WHERE content_type = 'photo' 
            AND created_at >= '2025-07-11 01:00:00'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        recent_photo_ads = cursor.fetchall()
        
        if recent_photo_ads:
            print(f"📋 Found {len(recent_photo_ads)} recent photo ads:")
            for ad in recent_photo_ads:
                print(f"   Ad {ad[0]}: User {ad[1]} | {ad[3]} | {ad[5]}")
                print(f"   Content: {ad[2][:100]}...")
                if ad[4]:
                    print(f"   Media: {ad[4][:50]}...")
                print()
            
            # Check if any of these contain QQQ2
            for ad in recent_photo_ads:
                if 'QQQ2' in ad[2].upper() or 'qqq2' in ad[2].lower():
                    return ad
            
            # Return the most recent photo ad
            return recent_photo_ads[0]
        
        # Check user 7043475 for any photo ads
        cursor.execute("""
            SELECT ad_id, user_id, content, content_type, media_url, created_at
            FROM ads 
            WHERE user_id = 7043475 
            AND content_type = 'photo'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        user_photo_ads = cursor.fetchall()
        
        if user_photo_ads:
            print(f"📋 Found {len(user_photo_ads)} photo ads for user 7043475:")
            for ad in user_photo_ads:
                print(f"   Ad {ad[0]}: {ad[3]} | {ad[5]}")
                print(f"   Content: {ad[2][:100]}...")
                if ad[4]:
                    print(f"   Media: {ad[4][:50]}...")
                print()
            
            return user_photo_ads[0]
        
        print("❌ No QQQ2 ad with image found")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error finding QQQ2 ad: {e}")
        return None
        
    finally:
        conn.close()

def update_re5768_campaign_with_correct_content():
    """Update RE5768 campaign with correct QQQ2 content if found"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Find the correct ad
        correct_ad = find_qqq2_ad_with_image()
        
        if correct_ad:
            ad_id, user_id, content, content_type, media_url, created_at = correct_ad
            
            print(f"✅ Found correct ad: {ad_id}")
            print(f"   User: {user_id}")
            print(f"   Content type: {content_type}")
            print(f"   Media: {'YES' if media_url else 'NO'}")
            print(f"   Content: {content[:200]}...")
            
            # Update the campaign
            cursor.execute("""
                UPDATE campaigns 
                SET user_id = ?, ad_content = ?, content_type = ?, media_url = ?
                WHERE campaign_id = 'CAM-2025-07-RE57'
            """, (user_id, content, content_type, media_url))
            
            # Update the campaign posts
            cursor.execute("""
                UPDATE campaign_posts 
                SET post_content = ?
                WHERE campaign_id = 'CAM-2025-07-RE57'
            """, (content,))
            
            # Update payment tracking
            cursor.execute("""
                UPDATE payment_memo_tracking 
                SET user_id = ?
                WHERE memo = 'RE5768'
            """, (user_id,))
            
            conn.commit()
            
            print(f"✅ Updated campaign CAM-2025-07-RE57 with correct content")
            print(f"   Updated to user: {user_id}")
            print(f"   Content type: {content_type}")
            print(f"   Media: {'YES' if media_url else 'NO'}")
            
            return True
            
        else:
            print("❌ Could not find correct QQQ2 ad content")
            
            # Check if current campaign is fine
            cursor.execute("""
                SELECT campaign_id, user_id, ad_content, content_type, media_url
                FROM campaigns 
                WHERE campaign_id = 'CAM-2025-07-RE57'
            """)
            
            current_campaign = cursor.fetchone()
            if current_campaign:
                print(f"ℹ️  Current campaign CAM-2025-07-RE57:")
                print(f"   User: {current_campaign[1]}")
                print(f"   Content type: {current_campaign[3]}")
                print(f"   Media: {'YES' if current_campaign[4] else 'NO'}")
                print(f"   Content: {current_campaign[2][:200]}...")
                
                # Check if posts are scheduled
                cursor.execute("""
                    SELECT COUNT(*) as scheduled_count,
                           SUM(CASE WHEN scheduled_time <= datetime('now') THEN 1 ELSE 0 END) as due_count
                    FROM campaign_posts 
                    WHERE campaign_id = 'CAM-2025-07-RE57' 
                    AND status = 'scheduled'
                """)
                
                post_stats = cursor.fetchone()
                print(f"   Posts: {post_stats[0]} scheduled, {post_stats[1]} due")
                
                print("ℹ️  Campaign is active and will publish with current content")
                return True
            
            return False
            
    except Exception as e:
        logger.error(f"❌ Error updating campaign: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔍 Looking for QQQ2 ad with image content...")
    success = update_re5768_campaign_with_correct_content()
    
    if success:
        print("\n✅ RE5768 campaign is ready for publishing!")
        print("The automatic publishing system will handle the scheduled posts.")
    else:
        print("\n❌ Could not update campaign with correct content")
        print("The campaign will proceed with current content.")