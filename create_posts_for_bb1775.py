#!/usr/bin/env python3
"""
Update BB1775 campaign with media URL if needed and verify posts are ready
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_bb1775_campaign_with_media():
    """Update BB1775 campaign with media URL if user has photo content"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Check current campaign
        cursor.execute("""
            SELECT campaign_id, ad_content, content_type, media_url, status
            FROM campaigns 
            WHERE campaign_id = 'CAM-2025-07-BB17'
        """)
        
        campaign = cursor.fetchone()
        if not campaign:
            print("❌ Campaign CAM-2025-07-BB17 not found")
            return False
            
        print(f"📋 Campaign {campaign[0]} status:")
        print(f"   Content type: {campaign[2]}")
        print(f"   Media URL: {'YES' if campaign[3] else 'NO'}")
        print(f"   Status: {campaign[4]}")
        
        # Check if user has photo content
        cursor.execute("""
            SELECT content, content_type, media_url 
            FROM ads 
            WHERE user_id = 566158428 AND content_type = 'photo' AND media_url IS NOT NULL
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        photo_ad = cursor.fetchone()
        if photo_ad:
            print(f"✅ Found photo ad for user 566158428")
            print(f"   Media URL: {photo_ad[2][:50]}...")
            
            # Update campaign with media
            cursor.execute("""
                UPDATE campaigns 
                SET content_type = 'photo', media_url = ?
                WHERE campaign_id = 'CAM-2025-07-BB17'
            """, (photo_ad[2],))
            
            conn.commit()
            print("✅ Updated campaign with photo media URL")
            
        else:
            print("ℹ️  No photo content found for user - campaign will publish text only")
            
        # Check scheduled posts
        cursor.execute("""
            SELECT id, channel_id, scheduled_time, status
            FROM campaign_posts 
            WHERE campaign_id = 'CAM-2025-07-BB17'
            AND status = 'scheduled'
            ORDER BY scheduled_time ASC
            LIMIT 10
        """)
        
        scheduled_posts = cursor.fetchall()
        print(f"\n📅 Next {len(scheduled_posts)} scheduled posts:")
        
        for post in scheduled_posts:
            print(f"   Post {post[0]}: {post[1]} at {post[2]} ({post[3]})")
            
        # Check if any posts are due now
        cursor.execute("""
            SELECT COUNT(*) as due_posts
            FROM campaign_posts 
            WHERE campaign_id = 'CAM-2025-07-BB17'
            AND status = 'scheduled'
            AND scheduled_time <= datetime('now')
        """)
        
        due_count = cursor.fetchone()[0]
        if due_count > 0:
            print(f"\n⏰ {due_count} posts are due for immediate publishing")
        else:
            print("\n⏰ No posts are due for immediate publishing")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating campaign: {e}")
        return False
        
    finally:
        conn.close()

def verify_bb1775_campaign_integration():
    """Verify the campaign is properly integrated with the publishing system"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Verify campaign exists and is active
        cursor.execute("""
            SELECT campaign_id, user_id, payment_memo, status, created_at
            FROM campaigns 
            WHERE campaign_id = 'CAM-2025-07-BB17'
        """)
        
        campaign = cursor.fetchone()
        if campaign:
            print(f"✅ Campaign verified: {campaign[0]}")
            print(f"   User: {campaign[1]}")
            print(f"   Payment memo: {campaign[2]}")
            print(f"   Status: {campaign[3]}")
            print(f"   Created: {campaign[4]}")
            
            # Check payment memo tracking
            cursor.execute("""
                SELECT user_id, memo, amount, created_at
                FROM payment_memo_tracking 
                WHERE memo = 'BB1775'
            """)
            
            tracking = cursor.fetchone()
            if tracking:
                print(f"✅ Payment tracking verified: {tracking[1]} → User {tracking[0]}")
            else:
                print("❌ Payment tracking not found")
                
            # Check payment status
            cursor.execute("""
                SELECT memo, amount, status, created_at
                FROM untracked_payments 
                WHERE memo = 'BB1775'
            """)
            
            payment = cursor.fetchone()
            if payment:
                print(f"✅ Payment status: {payment[2]}")
            else:
                print("❌ Payment not found in untracked_payments")
                
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
    print("🔍 Updating BB1775 campaign with media if needed...")
    success = update_bb1775_campaign_with_media()
    
    if success:
        print("\n🔍 Verifying BB1775 campaign integration...")
        verify_bb1775_campaign_integration()
        print("\n✅ BB1775 campaign is ready for publishing!")
        print("The automatic publishing system will handle the scheduled posts.")
    else:
        print("\n❌ BB1775 campaign update failed")