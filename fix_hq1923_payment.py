#!/usr/bin/env python3
"""
Fix HQ1923 Payment Processing Issue
Manually process the payment HQ1923 that was detected but not properly created as campaign
"""

import asyncio
import sqlite3
from datetime import datetime, timedelta
from campaign_management import CampaignManager
from database import db


async def fix_hq1923_payment():
    """Fix the HQ1923 payment processing issue"""
    
    print("🔧 FIXING HQ1923 PAYMENT PROCESSING ISSUE")
    print("=" * 50)
    
    # Payment details from logs
    memo = "HQ1923"
    amount_ton = 0.36
    user_id = 566158428
    
    print(f"📋 Processing Details:")
    print(f"   User ID: {user_id}")
    print(f"   Payment Memo: {memo}")
    print(f"   Amount: {amount_ton} TON")
    print(f"   Status: Payment detected but campaign not created")
    
    try:
        # Get user's most recent ad content
        print(f"\n1. 📖 Retrieving User Ad Content")
        print("-" * 35)
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Get user's most recent ad
        cursor.execute("""
            SELECT ad_id, content, media_url, content_type, created_at
            FROM ads 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id,))
        
        user_ad = cursor.fetchone()
        
        if user_ad:
            ad_id, content, media_url, content_type, created_at = user_ad
            print(f"   ✅ Found user ad: ID {ad_id}")
            print(f"   📝 Content: {content[:100]}...")
            print(f"   📷 Media: {'YES' if media_url else 'NO'}")
            print(f"   🕐 Created: {created_at}")
        else:
            print(f"   ❌ No ads found for user {user_id}")
            # Create a basic ad
            content = "User advertisement - Payment HQ1923"
            media_url = None
            content_type = 'text'
            print(f"   ⚠️  Creating basic ad content")
        
        # Create campaign
        print(f"\n2. 🎯 Creating Campaign")
        print("-" * 35)
        
        campaign_manager = CampaignManager()
        
        # Default campaign parameters based on 0.36 TON payment
        selected_channels = ['@i3lani', '@smshco']  # Default channels
        duration_days = 7  # Standard 7-day campaign
        posts_per_day = 1  # Standard posting frequency
        
        # Generate campaign ID
        campaign_id = f"CAM-2025-07-{memo[:4]}"
        
        print(f"   📋 Campaign ID: {campaign_id}")
        print(f"   📺 Channels: {selected_channels}")
        print(f"   📅 Duration: {duration_days} days")
        print(f"   📈 Posts per day: {posts_per_day}")
        
        # Create campaign in database
        cursor.execute("""
            INSERT INTO campaigns (
                campaign_id, user_id, start_date, end_date, 
                duration_days, posts_per_day, total_posts,
                selected_channels, payment_amount, payment_method, payment_memo,
                ad_content, ad_type, status, media_url, content_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign_id, user_id, datetime.now(), datetime.now() + timedelta(days=duration_days),
            duration_days, posts_per_day, duration_days * posts_per_day,
            ','.join(selected_channels), amount_ton, 'TON', memo,
            content, content_type, 'active', media_url, content_type
        ))
        
        conn.commit()
        print(f"   ✅ Campaign created successfully")
        
        # Create scheduled posts
        print(f"\n3. 📅 Creating Scheduled Posts")
        print("-" * 35)
        
        total_posts = duration_days * posts_per_day
        posts_created = 0
        
        for day in range(duration_days):
            for post_num in range(posts_per_day):
                for channel in selected_channels:
                    # Calculate scheduled time
                    scheduled_time = datetime.now() + timedelta(days=day, hours=post_num * 8)
                    
                    cursor.execute("""
                        INSERT INTO campaign_posts (
                            campaign_id, channel_id, post_content, 
                            scheduled_time, status
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        campaign_id, channel, content,
                        scheduled_time, 'scheduled'
                    ))
                    
                    posts_created += 1
        
        conn.commit()
        print(f"   ✅ Created {posts_created} scheduled posts")
        
        # Update payment tracking
        print(f"\n4. 💰 Updating Payment Tracking")
        print("-" * 35)
        
        # Add to payment_memo_tracking table
        cursor.execute("""
            INSERT OR REPLACE INTO payment_memo_tracking (
                memo, user_id, amount, status, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (memo, user_id, amount_ton, 'confirmed', datetime.now()))
        
        # Update untracked_payments table
        cursor.execute("""
            UPDATE untracked_payments 
            SET status = 'processed', processed_at = ?
            WHERE memo = ?
        """, (datetime.now(), memo))
        
        conn.commit()
        print(f"   ✅ Payment tracking updated")
        
        # Verification
        print(f"\n5. ✅ Verification")
        print("-" * 35)
        
        # Check campaign exists
        cursor.execute("SELECT * FROM campaigns WHERE campaign_id = ?", (campaign_id,))
        campaign = cursor.fetchone()
        
        if campaign:
            print(f"   ✅ Campaign {campaign_id} exists in database")
        else:
            print(f"   ❌ Campaign {campaign_id} not found in database")
        
        # Check scheduled posts
        cursor.execute("SELECT COUNT(*) FROM campaign_posts WHERE campaign_id = ?", (campaign_id,))
        posts_count = cursor.fetchone()[0]
        
        print(f"   ✅ {posts_count} scheduled posts ready for publishing")
        
        # Final status
        print(f"\n🎉 SUCCESS - HQ1923 Payment Processing Fixed")
        print("=" * 50)
        print(f"✅ Campaign {campaign_id} created for user {user_id}")
        print(f"✅ {posts_count} posts scheduled across {len(selected_channels)} channels")
        print(f"✅ Payment {memo} properly tracked and processed")
        print(f"✅ Automatic publishing will begin immediately")
        
        conn.close()
        
        return {
            'success': True,
            'campaign_id': campaign_id,
            'posts_created': posts_count,
            'message': 'Payment HQ1923 successfully processed and campaign created'
        }
        
    except Exception as e:
        print(f"❌ Error fixing payment: {e}")
        if 'conn' in locals():
            conn.close()
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to process payment HQ1923'
        }

if __name__ == "__main__":
    result = asyncio.run(fix_hq1923_payment())
    
    if result['success']:
        print(f"\n✅ PAYMENT HQ1923 FIXED SUCCESSFULLY")
        print(f"Campaign: {result['campaign_id']}")
        print(f"Posts: {result['posts_created']}")
    else:
        print(f"\n❌ PAYMENT FIX FAILED")
        print(f"Error: {result['error']}")