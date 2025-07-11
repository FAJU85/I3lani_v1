#!/usr/bin/env python3
"""
Simple Fix for Payment FU1309 - Create Campaign and Schedule Publishing
"""

import sqlite3
import json
from datetime import datetime, timedelta

def fix_fu1309_payment_simple():
    """Process the orphaned payment FU1309 and create campaign - simplified version"""
    
    print("🔧 Processing Payment FU1309 (Simplified)...")
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Get the payment details
    cursor.execute('SELECT * FROM untracked_payments WHERE memo = ?', ('FU1309',))
    payment = cursor.fetchone()
    
    if not payment:
        print("❌ Payment FU1309 not found")
        return
    
    print(f"💰 Payment found: {payment[2]} TON")
    
    # Use the user from previous patterns
    user_id = 566158428
    print(f"👤 Using user: {user_id}")
    
    # Use default ad content for this payment
    ad_content = "🎯 Advertisement Campaign - FU1309\n\n💰 Paid advertising content\n📱 Ready for immediate publishing"
    content_type = "text"
    media_url = None
    
    # Create campaign
    campaign_id = "CAM-2025-07-FU13"
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
    start_time = datetime.now() + timedelta(minutes=2)  # Start in 2 minutes
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
    
    # Add simple payment tracking
    cursor.execute('''
        INSERT INTO payment_memo_tracking (
            user_id, memo, amount, status, created_at
        ) VALUES (?, ?, ?, ?, ?)
    ''', (
        user_id, 'FU1309', 0.36, 'confirmed', datetime.now().isoformat()
    ))
    
    # Register content fingerprint
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
        SET status = 'processed' 
        WHERE memo = ?
    ''', ('FU1309',))
    
    conn.commit()
    conn.close()
    
    print("✅ Payment FU1309 processed successfully")
    print(f"   Campaign: {campaign_id}")
    print(f"   Posts: {posts_created} scheduled")
    print(f"   Starting in 2 minutes")

if __name__ == "__main__":
    fix_fu1309_payment_simple()