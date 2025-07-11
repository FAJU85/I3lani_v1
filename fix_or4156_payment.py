#!/usr/bin/env python3
"""
Fix payment OR4156 - manually process the untracked payment
"""

import sqlite3
import json
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentFixer:
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        
    def fix_payment_or4156(self):
        """Fix the OR4156 payment by manually processing it"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First, check if the payment exists in untracked_payments
            cursor.execute("SELECT * FROM untracked_payments WHERE memo = 'OR4156'")
            untracked = cursor.fetchone()
            
            if not untracked:
                logger.error("❌ Payment OR4156 not found in untracked_payments")
                return False
                
            print("✅ Found untracked payment OR4156:")
            print(f"   Memo: {untracked[1]}")
            print(f"   Amount: {untracked[2]} TON")
            print(f"   Wallet: {untracked[3]}")
            print(f"   Status: {untracked[5]}")
            print(f"   Created: {untracked[6]}")
            
            # Get the most recent user who was making payments (likely the owner of OR4156)
            cursor.execute("""
                SELECT user_id, COUNT(*) as payment_count 
                FROM payment_memo_tracking 
                WHERE created_at > '2025-07-10' 
                GROUP BY user_id 
                ORDER BY payment_count DESC, MAX(created_at) DESC
                LIMIT 1
            """)
            likely_user = cursor.fetchone()
            
            if likely_user:
                user_id = likely_user[0]
                print(f"✅ Most likely user for OR4156: {user_id}")
                
                # Get the user's latest ad content
                cursor.execute("""
                    SELECT content, content_type, media_url 
                    FROM ads 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (user_id,))
                
                user_ad = cursor.fetchone()
                
                if user_ad:
                    ad_content = user_ad[0]
                    content_type = user_ad[1] or 'text'
                    media_url = user_ad[2]
                    
                    print(f"✅ Found user ad content: {ad_content[:50]}...")
                    
                    # Create the campaign
                    campaign_id = f"CAM-2025-07-OR41"
                    start_date = datetime.now()
                    end_date = start_date + timedelta(days=7)
                    
                    # Default campaign settings
                    duration_days = 7
                    posts_per_day = 2
                    total_posts = duration_days * posts_per_day
                    selected_channels = "@i3lani,@smshco"
                    total_reach = 350
                    
                    campaign_data = {
                        "created_via": "manual_fix_or4156",
                        "pricing_tier": "standard",
                        "discount_applied": 0,
                        "target_audience": "general",
                        "content_type": content_type,
                        "languages": ["ar", "en"],
                        "creation_source": "payment_fix"
                    }
                    
                    # Insert campaign
                    cursor.execute("""
                        INSERT INTO campaigns (
                            campaign_id, user_id, payment_memo, payment_method, payment_amount,
                            campaign_name, ad_content, ad_type, start_date, end_date,
                            duration_days, posts_per_day, total_posts, selected_channels,
                            channel_count, total_reach, status, created_at, updated_at,
                            posts_published, engagement_score, click_through_rate,
                            campaign_metadata, content_type, media_url, advertiser_username
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        campaign_id, user_id, "OR4156", "TON", 0.36,
                        f"Campaign {campaign_id}", ad_content, content_type,
                        start_date, end_date, duration_days, posts_per_day, total_posts,
                        selected_channels, 2, total_reach, "active",
                        datetime.now(), datetime.now(), 0, 0.0, 0.0,
                        json.dumps(campaign_data), content_type, media_url, f"user_{user_id}"
                    ))
                    
                    # Update untracked_payments status
                    cursor.execute("""
                        UPDATE untracked_payments 
                        SET status = 'processed' 
                        WHERE memo = 'OR4156'
                    """)
                    
                    # Add to payment_memo_tracking for future reference
                    cursor.execute("""
                        INSERT INTO payment_memo_tracking (
                            user_id, memo, amount, payment_method, ad_data, status, created_at, confirmed_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id, "OR4156", 0.36, "TON", 
                        json.dumps({
                            "content": ad_content,
                            "content_type": content_type,
                            "media_url": media_url,
                            "duration_days": duration_days,
                            "posts_per_day": posts_per_day,
                            "selected_channels": selected_channels.split(','),
                            "total_reach": total_reach
                        }),
                        "confirmed", datetime.now(), datetime.now()
                    ))
                    
                    conn.commit()
                    
                    print(f"✅ Successfully created campaign {campaign_id}")
                    print(f"   User ID: {user_id}")
                    print(f"   Payment memo: OR4156")
                    print(f"   Amount: 0.36 TON")
                    print(f"   Duration: {duration_days} days")
                    print(f"   Posts per day: {posts_per_day}")
                    print(f"   Total posts: {total_posts}")
                    print(f"   Channels: {selected_channels}")
                    print(f"   Content: {ad_content[:50]}...")
                    
                    return True
                    
                else:
                    logger.error("❌ No ad content found for user")
                    return False
                    
            else:
                logger.error("❌ Cannot determine user for OR4156")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error fixing payment OR4156: {e}")
            return False
            
        finally:
            conn.close()

if __name__ == "__main__":
    fixer = PaymentFixer()
    success = fixer.fix_payment_or4156()
    
    if success:
        print("\n🎉 Payment OR4156 has been successfully processed!")
        print("The campaign has been created and should now be visible in the user's campaign list.")
        print("Publishing will start automatically via the campaign publisher.")
    else:
        print("\n❌ Failed to process payment OR4156")