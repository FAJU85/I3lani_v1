#!/usr/bin/env python3
"""
Fix BB1775 Payment Processing Issue
Creates campaign and scheduled posts for untracked payment BB1775
"""

import sqlite3
import random
import string
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BB1775PaymentFixer:
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        
    def identify_user_for_payment(self):
        """Identify which user the BB1775 payment belongs to"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for recent ads created around the payment time
            # Payment was created at 2025-07-11 01:03:37
            payment_time = "2025-07-11 01:03:37"
            
            # Look for ads created within 2 hours of payment
            cursor.execute("""
                SELECT user_id, ad_id, content, content_type, media_url, created_at
                FROM ads 
                WHERE created_at >= datetime(?, '-2 hours')
                AND created_at <= datetime(?, '+30 minutes')
                ORDER BY created_at DESC
            """, (payment_time, payment_time))
            
            recent_ads = cursor.fetchall()
            
            if recent_ads:
                print(f"📋 Found {len(recent_ads)} ads around payment time:")
                for ad in recent_ads:
                    print(f"   Ad {ad[1]}: User {ad[0]} | {ad[3]} | {ad[5]}")
                
                # Use the most recent ad's user
                likely_user_id = recent_ads[0][0]
                user_ad_content = recent_ads[0][2]
                content_type = recent_ads[0][3]
                media_url = recent_ads[0][4]
                
                print(f"✅ Identified likely user: {likely_user_id}")
                return likely_user_id, user_ad_content, content_type, media_url
            
            # If no recent ads, check for users with payment patterns
            cursor.execute("""
                SELECT user_id, COUNT(*) as payment_count
                FROM payment_memo_tracking 
                WHERE created_at > '2025-07-10'
                GROUP BY user_id
                ORDER BY payment_count DESC
                LIMIT 5
            """)
            
            frequent_users = cursor.fetchall()
            
            if frequent_users:
                print(f"📋 Found {len(frequent_users)} users with recent payment activity:")
                for user in frequent_users:
                    print(f"   User {user[0]}: {user[1]} payments")
                
                # Use the most active user
                likely_user_id = frequent_users[0][0]
                
                # Get their latest ad
                cursor.execute("""
                    SELECT content, content_type, media_url
                    FROM ads 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (likely_user_id,))
                
                user_ad = cursor.fetchone()
                if user_ad:
                    return likely_user_id, user_ad[0], user_ad[1], user_ad[2]
            
            print("❌ Could not identify user for payment BB1775")
            return None, None, None, None
            
        except Exception as e:
            logger.error(f"❌ Error identifying user: {e}")
            return None, None, None, None
            
        finally:
            conn.close()
    
    def create_campaign_for_payment(self, user_id, ad_content, content_type, media_url):
        """Create campaign for BB1775 payment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate unique campaign ID
            campaign_id = "CAM-2025-07-BB17"
            
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
                campaign_id, user_id, ad_content, content_type, media_url,
                duration_days, posts_per_day, "TON",
                0.36, "BB1775", "active", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            print(f"✅ Created campaign {campaign_id} for user {user_id}")
            
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
                            campaign_id, channel, ad_content,
                            post_time.strftime('%Y-%m-%d %H:%M:%S'),
                            "scheduled", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ))
                        
                        posts_created += 1
            
            print(f"✅ Created {posts_created} scheduled posts")
            
            # Update payment status
            cursor.execute("""
                UPDATE untracked_payments 
                SET status = 'processed'
                WHERE memo = 'BB1775'
            """)
            
            # Add to payment tracking
            cursor.execute("""
                INSERT INTO payment_memo_tracking (user_id, memo, amount, created_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, "BB1775", 0.36, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            
            print(f"✅ Payment BB1775 processed successfully")
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
                SELECT campaign_id, user_id, status, duration_days, posts_per_day
                FROM campaigns 
                WHERE campaign_id = ?
            """, (campaign_id,))
            
            campaign = cursor.fetchone()
            if campaign:
                print(f"✅ Campaign validation: {campaign}")
                
                # Check scheduled posts
                cursor.execute("""
                    SELECT COUNT(*) as total_posts,
                           SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled_posts
                    FROM campaign_posts 
                    WHERE campaign_id = ?
                """, (campaign_id,))
                
                posts_stats = cursor.fetchone()
                print(f"✅ Posts validation: {posts_stats[0]} total, {posts_stats[1]} scheduled")
                
                # Check payment tracking
                cursor.execute("""
                    SELECT status FROM untracked_payments WHERE memo = 'BB1775'
                """, ())
                
                payment_status = cursor.fetchone()
                if payment_status:
                    print(f"✅ Payment status: {payment_status[0]}")
                
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
    fixer = BB1775PaymentFixer()
    
    print("🔍 Investigating BB1775 payment...")
    user_id, ad_content, content_type, media_url = fixer.identify_user_for_payment()
    
    if user_id:
        print(f"\n🎯 Creating campaign for user {user_id}...")
        campaign_id = fixer.create_campaign_for_payment(user_id, ad_content, content_type, media_url)
        
        if campaign_id:
            print(f"\n✅ Validating campaign {campaign_id}...")
            success = fixer.validate_campaign_creation(campaign_id)
            
            if success:
                print("\n🎉 BB1775 payment processing completed successfully!")
                print("The campaign is now active and will start publishing automatically.")
            else:
                print("\n❌ Campaign validation failed")
        else:
            print("\n❌ Campaign creation failed")
    else:
        print("\n❌ Could not identify user for payment BB1775")
        print("Manual investigation required to link payment to user.")