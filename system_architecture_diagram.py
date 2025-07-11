#!/usr/bin/env python3
"""
I3lani Bot System Architecture - Data Flow Relationships
Shows how Ad ID, Campaign ID, and Payment ID are connected
"""

import sqlite3
from datetime import datetime

def show_system_relationships():
    """Show the complete data flow relationships"""
    
    print("🏗️  I3LANI BOT SYSTEM ARCHITECTURE")
    print("="*50)
    
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    
    # 1. Payment Flow
    print("\n1️⃣  PAYMENT FLOW:")
    print("   TON Payment → Payment Memo → Campaign Creation")
    print("   Stars Payment → Payment ID → Campaign Creation")
    
    cursor.execute("""
        SELECT memo, user_id, amount, created_at
        FROM payment_memo_tracking 
        WHERE memo IN ('RE5768', 'BB1775', 'OR4156')
        ORDER BY created_at DESC
    """)
    
    payments = cursor.fetchall()
    print(f"\n   Recent Payment Memos:")
    for payment in payments:
        print(f"   📧 {payment[0]} → User {payment[1]} → {payment[2]} TON → {payment[3]}")
    
    # 2. Campaign Creation
    print("\n2️⃣  CAMPAIGN CREATION:")
    print("   Payment Confirmation → Campaign ID → Ad Content Link")
    
    cursor.execute("""
        SELECT campaign_id, user_id, payment_memo, payment_method, status, created_at
        FROM campaigns 
        WHERE payment_memo IN ('RE5768', 'BB1775', 'OR4156')
        ORDER BY created_at DESC
    """)
    
    campaigns = cursor.fetchall()
    print(f"\n   Active Campaigns:")
    for campaign in campaigns:
        print(f"   🎯 {campaign[0]} → User {campaign[1]} → Memo {campaign[2]} → {campaign[3]} → {campaign[4]}")
    
    # 3. Post Identity System
    print("\n3️⃣  POST IDENTITY SYSTEM:")
    print("   Campaign ID → Post ID → Content Tracking")
    
    cursor.execute("""
        SELECT post_id, campaign_id, advertiser_username, created_at
        FROM post_identity 
        WHERE campaign_id IN ('CAM-2025-07-RE57', 'CAM-2025-07-BB17', 'CAM-2025-07-OR41')
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    posts = cursor.fetchall()
    print(f"\n   Generated Post IDs:")
    for post in posts:
        print(f"   📄 {post[0]} → {post[1]} → {post[2]} → {post[3]}")
    
    # 4. Publishing System
    print("\n4️⃣  PUBLISHING SYSTEM:")
    print("   Post ID → Channel Publishing → Message Tracking")
    
    cursor.execute("""
        SELECT cp.campaign_id, cp.channel_id, cp.status, pi.post_id
        FROM campaign_posts cp
        LEFT JOIN post_identity pi ON cp.campaign_id = pi.campaign_id
        WHERE cp.campaign_id IN ('CAM-2025-07-RE57', 'CAM-2025-07-BB17', 'CAM-2025-07-OR41')
        AND cp.status = 'published'
        ORDER BY cp.published_at DESC
        LIMIT 5
    """)
    
    published = cursor.fetchall()
    print(f"\n   Published Posts:")
    for pub in published:
        print(f"   📺 {pub[0]} → {pub[1]} → {pub[2]} → {pub[3] if pub[3] else 'No Post ID'}")
    
    # 5. Complete Data Flow Example
    print("\n5️⃣  COMPLETE DATA FLOW EXAMPLE:")
    print("   RE5768 Payment → CAM-2025-07-RE57 → Ad09 → @i3lani/@smshco")
    
    # Show specific example
    cursor.execute("""
        SELECT 
            pmt.memo as payment_memo,
            pmt.user_id,
            pmt.amount,
            c.campaign_id,
            pi.post_id,
            COUNT(cp.post_id) as total_posts,
            SUM(CASE WHEN cp.status = 'published' THEN 1 ELSE 0 END) as published_posts
        FROM payment_memo_tracking pmt
        JOIN campaigns c ON pmt.memo = c.payment_memo
        LEFT JOIN post_identity pi ON c.campaign_id = pi.campaign_id
        LEFT JOIN campaign_posts cp ON c.campaign_id = cp.campaign_id
        WHERE pmt.memo = 'RE5768'
        GROUP BY pmt.memo, pmt.user_id, c.campaign_id, pi.post_id
    """)
    
    example = cursor.fetchone()
    if example:
        print(f"\n   📊 RE5768 COMPLETE FLOW:")
        print(f"      Payment: {example[0]} → User {example[1]} → {example[2]} TON")
        print(f"      Campaign: {example[3]}")
        print(f"      Post ID: {example[4]}")
        print(f"      Posts: {example[6]}/{example[5]} published")
    
    # 6. Database Tables Relationships
    print("\n6️⃣  DATABASE TABLES RELATIONSHIPS:")
    print("   📊 payment_memo_tracking (memo → user_id)")
    print("   📊 campaigns (campaign_id → payment_memo + user_id)")
    print("   📊 post_identity (post_id → campaign_id)")
    print("   📊 campaign_posts (campaign_id → channel publishing)")
    print("   📊 post_publishing_log (post_id → channel + message_id)")
    
    conn.close()
    
    print("\n✅ SYSTEM ARCHITECTURE COMPLETE")
    print("   Every payment creates a traceable path from payment to published posts")
    print("   Each component links to the next for complete audit trail")

if __name__ == "__main__":
    show_system_relationships()