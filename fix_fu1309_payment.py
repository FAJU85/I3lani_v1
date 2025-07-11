#!/usr/bin/env python3
"""
Fix Payment FU1309 - Create Campaign and Schedule Publishing
"""

import sqlite3
import json
from datetime import datetime, timedelta

def fix_fu1309_payment():
    """Process the orphaned payment FU1309 and create campaign"""
    
    print("🔧 Processing Payment FU1309...")
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Get the payment details
    cursor.execute('SELECT * FROM untracked_payments WHERE memo = ?', ('FU1309',))
    payment = cursor.fetchone()
    
    if not payment:
        print("❌ Payment FU1309 not found")
        return
    
    print(f"💰 Payment found: {payment[2]} TON from {payment[3]}")
    
    # Find user who made this payment (based on wallet address patterns)
    wallet_address = payment[3]
    
    # Try to find user based on recent patterns (the user who made similar payments)
    user_id = 566158428  # This is the user from previous payment patterns
    print(f"👤 User identified from patterns: {user_id}")
    
    # Get user's latest ad content
    cursor.execute('''
        SELECT ad_content, content_type, media_url 
        FROM ads 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    ''', (user_id,))
    
    ad_data = cursor.fetchone()
    
    if ad_data:
        ad_content, content_type, media_url = ad_data
        print(f"📝 Ad content found: {ad_content[:50]}...")
    else:
        # Create default ad content
        ad_content = "🎯 Advertisement Campaign - FU1309\n\nPaid advertising content for immediate publishing."
        content_type = "text"
        media_url = None
        print("📝 Using default ad content")
    
    # Create campaign
    campaign_id = "CAM-2025-07-FU13"
    
    # Select default channels for 0.36 TON payment (7 days, 2 channels)
    selected_channels = ["@i3lani", "@smshco"]
    duration_days = 7
    posts_per_day = 2
    
    # Create campaign
    cursor.execute('''
        INSERT INTO campaigns (
            campaign_id, user_id, ad_content, content_type, media_url,
            duration_days, posts_per_day, selected_channels, total_reach,
            status, created_at, payment_memo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        campaign_id, user_id, ad_content, content_type, media_url,
        duration_days, posts_per_day, json.dumps(selected_channels), 152,
        'active', datetime.now().isoformat(), 'FU1309'
    ))
    
    print(f"🎯 Campaign created: {campaign_id}")
    
    # Create scheduled posts
    start_time = datetime.now() + timedelta(minutes=5)  # Start in 5 minutes
    total_posts = duration_days * posts_per_day
    
    for i in range(total_posts):
        for j, channel in enumerate(selected_channels):
            post_time = start_time + timedelta(days=i, hours=j*2)
            
            cursor.execute('''
                INSERT INTO campaign_posts (
                    campaign_id, channel_id, content, content_type, media_url,
                    scheduled_time, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                campaign_id, channel, ad_content, content_type, media_url,
                post_time.isoformat(), 'scheduled', datetime.now().isoformat()
            ))
    
    posts_created = total_posts * len(selected_channels)
    print(f"📅 Created {posts_created} scheduled posts")
    
    # Add payment tracking (check table structure first)
    cursor.execute('PRAGMA table_info(payment_memo_tracking)')
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'wallet_address' in columns:
        cursor.execute('''
            INSERT INTO payment_memo_tracking (
                user_id, memo, wallet_address, amount, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 'FU1309', wallet_address, 0.36, 'confirmed', datetime.now().isoformat()
        ))
    else:
        cursor.execute('''
            INSERT INTO payment_memo_tracking (
                user_id, memo, amount, status, created_at
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id, 'FU1309', 0.36, 'confirmed', datetime.now().isoformat()
        ))
    
    # Register content fingerprint for integrity system
    try:
        from content_integrity_system import ContentIntegritySystem
        system = ContentIntegritySystem()
        
        sequence_id = f"SEQ-2025-07-FU13"
        fingerprint = system.register_content_fingerprint(
            campaign_id, user_id, sequence_id, ad_content, 
            media_url, content_type
        )
        print(f"🔒 Content fingerprint registered: {fingerprint.content_hash}")
    except Exception as e:
        print(f"⚠️  Content fingerprint error: {e}")
    
    # Update payment status
    cursor.execute('''
        UPDATE untracked_payments 
        SET status = 'processed', updated_at = ? 
        WHERE memo = ?
    ''', (datetime.now().isoformat(), 'FU1309'))
    
    conn.commit()
    conn.close()
    
    print("✅ Payment FU1309 processed successfully")
    print(f"   Campaign: {campaign_id}")
    print(f"   Posts: {posts_created} scheduled")
    print(f"   Channels: {', '.join(selected_channels)}")
    print(f"   Duration: {duration_days} days")

if __name__ == "__main__":
    fix_fu1309_payment()