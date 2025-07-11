#!/usr/bin/env python3
"""
Update BB1775 campaign with the correct ad based on user clarification
Since the user mentions an ad with "( t2 )" that we can't find in the database,
let's use the photo ad they have until they can clarify which specific ad they want.
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_bb1775_with_photo_ad():
    """Update BB1775 campaign with the photo ad (Ad 74) as a temporary solution"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Get the photo ad (Ad 74)
        cursor.execute("""
            SELECT ad_id, content, content_type, media_url
            FROM ads 
            WHERE ad_id = 74 AND user_id = 566158428
        """)
        
        photo_ad = cursor.fetchone()
        if not photo_ad:
            print("❌ Photo ad not found")
            return False
            
        print(f"📸 Found photo ad {photo_ad[0]}:")
        print(f"   Content: {photo_ad[1]}")
        print(f"   Type: {photo_ad[2]}")
        print(f"   Media: {photo_ad[3][:50]}...")
        
        # Update BB1775 campaign with this photo ad
        cursor.execute("""
            UPDATE campaigns 
            SET ad_content = ?, content_type = ?, media_url = ?
            WHERE campaign_id = 'CAM-2025-07-BB17'
        """, (photo_ad[1], photo_ad[2], photo_ad[3]))
        
        # Update all scheduled posts with new content
        cursor.execute("""
            UPDATE campaign_posts 
            SET post_content = ?
            WHERE campaign_id = 'CAM-2025-07-BB17' AND status = 'scheduled'
        """, (photo_ad[1],))
        
        conn.commit()
        
        print("✅ Campaign updated with photo ad!")
        print(f"   New content: {photo_ad[1]}")
        print(f"   Type: {photo_ad[2]}")
        print(f"   Media: YES")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating campaign: {e}")
        return False
        
    finally:
        conn.close()

def show_available_ads_for_user():
    """Show all available ads for the user so they can identify the correct one"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Get all ads with content for this user
        cursor.execute("""
            SELECT ad_id, content, content_type, media_url, created_at
            FROM ads 
            WHERE user_id = 566158428 
            AND content IS NOT NULL 
            AND content != ''
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        ads = cursor.fetchall()
        
        print(f"📋 Available ads for user 566158428:")
        print("="*80)
        
        for i, ad in enumerate(ads, 1):
            print(f"{i}. Ad ID: {ad[0]} | Created: {ad[4]}")
            print(f"   Type: {ad[2]} | Media: {'YES' if ad[3] else 'NO'}")
            print(f"   Content: {ad[1][:200]}...")
            print("-" * 80)
            
        # Look for patterns that might match "t2"
        print("\n🔍 Searching for any patterns that might match 't2':")
        
        patterns_to_check = []
        for ad in ads:
            content = ad[1].lower()
            if 't2' in content or '(t2)' in content or '( t2 )' in content:
                patterns_to_check.append(ad)
                
        if patterns_to_check:
            print(f"✅ Found {len(patterns_to_check)} ads with 't2' pattern:")
            for ad in patterns_to_check:
                print(f"   Ad {ad[0]}: {ad[1][:100]}...")
        else:
            print("❌ No ads found with 't2' pattern")
            
        return ads
        
    except Exception as e:
        logger.error(f"❌ Error getting ads: {e}")
        return []
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔍 Showing available ads for user to identify correct one...")
    
    # Show all available ads
    available_ads = show_available_ads_for_user()
    
    print(f"\n🎯 Current campaign BB1775 is using charity donation content.")
    print(f"User says they want the ad with '( t2 )' at the end and an image.")
    print(f"Since we can't find that specific ad, let's use the photo ad temporarily.")
    
    # Update with photo ad for now
    success = update_bb1775_with_photo_ad()
    
    if success:
        print("\n✅ Campaign updated with photo ad temporarily!")
        print("User can now check if this is the correct ad or provide more details.")
    else:
        print("\n❌ Failed to update campaign")
        
    print("\n💡 Next steps:")
    print("1. User should check if the photo ad 'Hello New Add New car 📞' is correct")
    print("2. If not, user should provide the exact text or send the ad again")
    print("3. We can then update the campaign with the correct content")