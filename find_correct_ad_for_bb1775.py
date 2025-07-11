#!/usr/bin/env python3
"""
Find and fix the correct ad content for BB1775 campaign
The user says they sent an ad with "( t2 )" at the end and an image
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_correct_ad_for_bb1775():
    """Find the correct ad content for BB1775 payment"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        print("🔍 Searching for user 566158428 ads with 't2' or similar patterns...")
        
        # Search for ads with t2 pattern
        search_patterns = [
            "t2", "T2", "(t2)", "(T2)", "( t2 )", "( T2 )", 
            "t2)", "T2)", "(t2", "(T2"
        ]
        
        for pattern in search_patterns:
            cursor.execute("""
                SELECT ad_id, content, content_type, media_url, created_at
                FROM ads 
                WHERE user_id = 566158428 
                AND content LIKE ?
                ORDER BY created_at DESC
                LIMIT 5
            """, (f"%{pattern}%",))
            
            results = cursor.fetchall()
            if results:
                print(f"✅ Found {len(results)} ads with pattern '{pattern}':")
                for ad in results:
                    print(f"   Ad {ad[0]}: {ad[1][:100]}...")
                    print(f"   Type: {ad[2]}, Media: {'YES' if ad[3] else 'NO'}")
                    print(f"   Created: {ad[4]}")
                    print()
                return results[0]  # Return the most recent match
        
        print("🔍 No ads found with 't2' pattern. Checking all recent ads...")
        
        # Get all recent ads for this user
        cursor.execute("""
            SELECT ad_id, content, content_type, media_url, created_at
            FROM ads 
            WHERE user_id = 566158428 
            AND content IS NOT NULL 
            AND content != ''
            ORDER BY created_at DESC
            LIMIT 15
        """)
        
        all_ads = cursor.fetchall()
        print(f"📋 Found {len(all_ads)} recent ads for user 566158428:")
        
        for i, ad in enumerate(all_ads):
            print(f"{i+1}. Ad {ad[0]} ({ad[4]}):")
            print(f"   Content: {ad[1][:150]}...")
            print(f"   Type: {ad[2]}, Media: {'YES' if ad[3] else 'NO'}")
            print()
            
        # Look for ads with images
        photo_ads = [ad for ad in all_ads if ad[2] == 'photo' and ad[3]]
        if photo_ads:
            print(f"📸 Found {len(photo_ads)} photo ads:")
            for ad in photo_ads:
                print(f"   Ad {ad[0]}: {ad[1][:100]}...")
                print(f"   Media: {ad[3]}")
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error searching for ads: {e}")
        return None
        
    finally:
        conn.close()

def update_bb1775_campaign_content(ad_id, content, content_type, media_url):
    """Update BB1775 campaign with correct content"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        print(f"🔄 Updating campaign CAM-2025-07-BB17 with ad {ad_id} content...")
        
        # Update campaign content
        cursor.execute("""
            UPDATE campaigns 
            SET ad_content = ?, content_type = ?, media_url = ?
            WHERE campaign_id = 'CAM-2025-07-BB17'
        """, (content, content_type, media_url))
        
        # Update all scheduled posts with new content
        cursor.execute("""
            UPDATE campaign_posts 
            SET post_content = ?
            WHERE campaign_id = 'CAM-2025-07-BB17'
        """, (content,))
        
        conn.commit()
        
        print("✅ Campaign updated successfully!")
        print(f"   Content: {content[:100]}...")
        print(f"   Type: {content_type}")
        print(f"   Media: {'YES' if media_url else 'NO'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating campaign: {e}")
        return False
        
    finally:
        conn.close()

def check_campaign_status():
    """Check the current status of BB1775 campaign"""
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
            print("📊 Current campaign status:")
            print(f"   Campaign: {campaign[0]}")
            print(f"   Content: {campaign[1][:150]}...")
            print(f"   Type: {campaign[2]}")
            print(f"   Media: {'YES' if campaign[3] else 'NO'}")
            print(f"   Status: {campaign[4]}")
        
        # Check scheduled posts
        cursor.execute("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
                   SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published
            FROM campaign_posts 
            WHERE campaign_id = 'CAM-2025-07-BB17'
        """)
        
        stats = cursor.fetchone()
        print(f"   Posts: {stats[0]} total, {stats[1]} scheduled, {stats[2]} published")
        
        return campaign
        
    except Exception as e:
        logger.error(f"❌ Error checking campaign: {e}")
        return None
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔍 Finding correct ad for BB1775 campaign...")
    
    # Check current campaign status
    current_campaign = check_campaign_status()
    
    # Find correct ad
    correct_ad = find_correct_ad_for_bb1775()
    
    if correct_ad:
        print("\n✅ Found correct ad! Updating campaign...")
        success = update_bb1775_campaign_content(
            correct_ad[0], correct_ad[1], correct_ad[2], correct_ad[3]
        )
        
        if success:
            print("\n🎉 Campaign updated successfully!")
            check_campaign_status()
        else:
            print("\n❌ Failed to update campaign")
    else:
        print("\n❌ Could not find the correct ad with '( t2 )' pattern")
        print("Please check if the ad was properly saved or provide more details.")