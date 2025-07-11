#!/usr/bin/env python3
"""
Fix RE5768 Payment Processing Issue
Creates campaign and scheduled posts for untracked payment RE5768
"""

import sqlite3
import random
import string
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RE5768PaymentFixer:
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        
    def find_qqq2_ad_content(self):
        """Find the ad content containing QQQ2 or similar text"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search for QQQ2 in various forms
            search_patterns = ['%QQQ2%', '%qqq2%', '%QQQ%', '%qqq%', '%2%']
            
            for pattern in search_patterns:
                cursor.execute("""
                    SELECT ad_id, user_id, content, content_type, media_url, created_at
                    FROM ads 
                    WHERE content LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 5
                """, (pattern,))
                
                results = cursor.fetchall()
                if results:
                    print(f"✅ Found {len(results)} ads matching pattern '{pattern}':")
                    for ad in results:
                        print(f"   Ad {ad[0]}: User {ad[1]} | {ad[3]} | {ad[5]}")
                        print(f"   Content: {ad[2][:100]}...")
                        if ad[4]:
                            print(f"   Media: {ad[4][:50]}...")
                    return results[0]  # Return the most recent match
            
            # If no QQQ2 found, look for recent ads around payment time
            payment_time = "2025-07-11 01:21:59"
            
            cursor.execute("""
                SELECT ad_id, user_id, content, content_type, media_url, created_at
                FROM ads 
                WHERE created_at >= datetime(?, '-1 hour')
                AND created_at <= datetime(?, '+30 minutes')
                ORDER BY created_at DESC
                LIMIT 10
            """, (payment_time, payment_time))
            
            recent_ads = cursor.fetchall()
            if recent_ads:
                print(f"📋 Found {len(recent_ads)} ads around payment time:")
                for ad in recent_ads:
                    print(f"   Ad {ad[0]}: User {ad[1]} | {ad[3]} | {ad[5]}")
                    print(f"   Content: {ad[2][:100]}...")
                
                # Look for ads with images
                for ad in recent_ads:
                    if ad[4]:  # has media_url
                        print(f"✅ Found ad with image: Ad {ad[0]}")
                        return ad
                
                # Return the most recent ad
                return recent_ads[0]
            
            # Check for ads from the most active user
            cursor.execute("""
                SELECT user_id, COUNT(*) as ad_count
                FROM ads 
                WHERE created_at >= '2025-07-11 00:00:00'
                GROUP BY user_id
                ORDER BY ad_count DESC
                LIMIT 3
            """)
            
            active_users = cursor.fetchall()
            if active_users:
                print(f"📋 Most active users today:")
                for user in active_users:
                    print(f"   User {user[0]}: {user[1]} ads")
                
                # Get latest ad from most active user
                cursor.execute("""
                    SELECT ad_id, user_id, content, content_type, media_url, created_at
                    FROM ads 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (active_users[0][0],))
                
                latest_ad = cursor.fetchone()
                if latest_ad:
                    print(f"✅ Using latest ad from most active user: Ad {latest_ad[0]}")
                    return latest_ad
            
            print("❌ Could not find any suitable ad content")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding ad content: {e}")
            return None
            
        finally:
            conn.close()
    
    def create_campaign_for_re5768(self, ad_data):
        """Create campaign for RE5768 payment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if not ad_data:
                print("❌ No ad data provided")
                return None
                
            ad_id, user_id, content, content_type, media_url, created_at = ad_data
            
            # Generate unique campaign ID
            campaign_id = "CAM-2025-07-RE57"
            
            # Campaign details
            duration_days = 7
            posts_per_day = 2
            channels = ["@i3lani", "@smshco"]
            
            # Create campaign
            cursor.execute("""
                INSERT INTO campaigns (
                    campaign_id, user_id, ad_content, content_type, media_url,
                    duration_days, posts_per_day, payment_method,
                    payment_amount, payment_memo, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                campaign_id, user_id, content, content_type, media_url,
                duration_days, posts_per_day, "TON",
                0.36, "RE5768", "active", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            print(f"✅ Created campaign {campaign_id} for user {user_id}")
            print(f"   Content: {content[:100]}...")
            print(f"   Content type: {content_type}")
            print(f"   Media: {'YES' if media_url else 'NO'}")
            
            # Create scheduled posts
            start_time = datetime.now()
            total_posts = duration_days * posts_per_day * len(channels)
            
            posts_created = 0
            for day in range(duration_days):
                for post_num in range(posts_per_day):
                    for channel in channels:
                        # Calculate post time
                        hours_offset = (day * 24) + (post_num * 12)  # 12 hours apart
                        post_time = start_time + timedelta(hours=hours_offset)
                        
                        cursor.execute("""
                            INSERT INTO campaign_posts (
                                campaign_id, channel_id, post_content, 
                                scheduled_time, status, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            campaign_id, channel, content,
                            post_time.strftime('%Y-%m-%d %H:%M:%S'),
                            "scheduled", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ))
                        
                        posts_created += 1
            
            print(f"✅ Created {posts_created} scheduled posts")
            
            # Update payment status
            cursor.execute("""
                UPDATE untracked_payments 
                SET status = 'processed'
                WHERE memo = 'RE5768'
            """)
            
            # Add to payment tracking
            cursor.execute("""
                INSERT INTO payment_memo_tracking (user_id, memo, amount, created_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, "RE5768", 0.36, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            
            print(f"✅ Payment RE5768 processed successfully")
            print(f"   Campaign: {campaign_id}")
            print(f"   User: {user_id}")
            print(f"   Posts: {posts_created}")
            print(f"   Duration: {duration_days} days")
            print(f"   Channels: {', '.join(channels)}")
            
            return campaign_id
            
        except Exception as e:
            logger.error(f"❌ Error creating campaign: {e}")
            return None
            
        finally:
            conn.close()
    
    def validate_campaign_creation(self, campaign_id):
        """Validate that campaign was created successfully"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check campaign
            cursor.execute("""
                SELECT campaign_id, user_id, status, content_type, media_url
                FROM campaigns 
                WHERE campaign_id = ?
            """, (campaign_id,))
            
            campaign = cursor.fetchone()
            if campaign:
                print(f"✅ Campaign validation: {campaign[0]}")
                print(f"   User: {campaign[1]}")
                print(f"   Status: {campaign[2]}")
                print(f"   Content type: {campaign[3]}")
                print(f"   Media: {'YES' if campaign[4] else 'NO'}")
                
                # Check scheduled posts
                cursor.execute("""
                    SELECT COUNT(*) as total_posts,
                           SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled_posts,
                           SUM(CASE WHEN scheduled_time <= datetime('now') THEN 1 ELSE 0 END) as due_posts
                    FROM campaign_posts 
                    WHERE campaign_id = ?
                """, (campaign_id,))
                
                posts_stats = cursor.fetchone()
                print(f"✅ Posts validation: {posts_stats[0]} total, {posts_stats[1]} scheduled, {posts_stats[2]} due")
                
                return True
            else:
                print("❌ Campaign not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error validating campaign: {e}")
            return False
            
        finally:
            conn.close()

if __name__ == "__main__":
    fixer = RE5768PaymentFixer()
    
    print("🔍 Investigating RE5768 payment and QQQ2 ad...")
    ad_data = fixer.find_qqq2_ad_content()
    
    if ad_data:
        print(f"\n🎯 Creating campaign for RE5768 payment...")
        campaign_id = fixer.create_campaign_for_re5768(ad_data)
        
        if campaign_id:
            print(f"\n✅ Validating campaign {campaign_id}...")
            success = fixer.validate_campaign_creation(campaign_id)
            
            if success:
                print("\n🎉 RE5768 payment processing completed successfully!")
                print("The campaign is now active and will start publishing automatically.")
            else:
                print("\n❌ Campaign validation failed")
        else:
            print("\n❌ Campaign creation failed")
    else:
        print("\n❌ Could not find QQQ2 ad content")
        print("Manual investigation required to locate the ad content.")