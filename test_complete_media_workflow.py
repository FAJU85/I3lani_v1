#!/usr/bin/env python3
"""Test Complete Media Workflow from Ad Creation to Campaign Publishing"""

import sqlite3
import json
from datetime import datetime

def test_complete_media_workflow():
    """Test the complete media workflow from ad creation to campaign publishing"""
    try:
        conn = sqlite3.connect('bot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("🔍 Testing Complete Media Workflow")
        print("=" * 50)
        
        # 1. Check FU13 campaign specifically (the one from our fix)
        print("\n1️⃣ CAMPAIGN FU13 MEDIA STATUS:")
        cursor.execute("""
            SELECT campaign_id, user_id, ad_content, content_type, media_url, 
                   payment_memo, created_at, status
            FROM campaigns 
            WHERE campaign_id = 'CAM-2025-07-FU13'
        """)
        
        campaign = cursor.fetchone()
        if campaign:
            print(f"   Campaign ID: {campaign['campaign_id']}")
            print(f"   User ID: {campaign['user_id']}")
            print(f"   Content Type: {campaign['content_type']}")
            print(f"   Has Media: {bool(campaign['media_url'])}")
            print(f"   Media URL: {campaign['media_url'][:50]}..." if campaign['media_url'] else "None")
            print(f"   Status: {campaign['status']}")
        else:
            print("   ❌ Campaign CAM-2025-07-FU13 not found!")
        
        # 2. Check campaign posts for FU13
        print("\n\n2️⃣ CAMPAIGN POSTS FOR FU13:")
        cursor.execute("""
            SELECT id, channel_id, scheduled_time, status, published_at
            FROM campaign_posts 
            WHERE campaign_id = 'CAM-2025-07-FU13'
            ORDER BY scheduled_time
            LIMIT 10
        """)
        
        posts = cursor.fetchall()
        print(f"   Found {len(posts)} posts scheduled")
        
        published_count = 0
        for i, post in enumerate(posts, 1):
            status_icon = "✅" if post['status'] == 'published' else "⏳"
            print(f"   {status_icon} Post {i}: {post['channel_id']} - {post['status']}")
            if post['status'] == 'published':
                published_count += 1
        
        print(f"\n   Summary: {published_count}/{len(posts)} posts published")
        
        # 3. Check content integrity registration
        print("\n\n3️⃣ CONTENT INTEGRITY REGISTRATION:")
        cursor.execute("""
            SELECT campaign_id, content_hash, media_url, created_at
            FROM content_fingerprints 
            WHERE campaign_id = 'CAM-2025-07-FU13'
        """)
        
        fingerprint = cursor.fetchone()
        if fingerprint:
            print(f"   ✅ Content registered with hash: {fingerprint['content_hash'][:20]}...")
            print(f"   Has media URL: {bool(fingerprint['media_url'])}")
            print(f"   Registration date: {fingerprint['created_at']}")
        else:
            print(f"   ⚠️ No content fingerprint found for FU13")
        
        # 4. Check if media is properly linked in publishing workflow
        print("\n\n4️⃣ PUBLISHING WORKFLOW MEDIA CHECK:")
        cursor.execute("""
            SELECT 
                cp.id,
                cp.channel_id,
                c.content_type,
                c.media_url,
                c.ad_content
            FROM campaign_posts cp
            JOIN campaigns c ON c.campaign_id = cp.campaign_id
            WHERE cp.campaign_id = 'CAM-2025-07-FU13'
            LIMIT 1
        """)
        
        publishing_test = cursor.fetchone()
        if publishing_test:
            print(f"   ✅ Publishing query returns media info:")
            print(f"      Content type: {publishing_test['content_type']}")
            print(f"      Has media: {bool(publishing_test['media_url'])}")
        else:
            print(f"   ❌ Publishing query failed")
        
        # 5. Check recent payment tracking with media
        print("\n\n5️⃣ RECENT PAYMENT TRACKING WITH MEDIA:")
        cursor.execute("""
            SELECT memo, user_id, ad_data, created_at
            FROM payment_memo_tracking 
            WHERE created_at >= datetime('now', '-1 hour')
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        
        recent_payments = cursor.fetchall()
        print(f"   Found {len(recent_payments)} recent payment trackings")
        
        for payment in recent_payments:
            print(f"\n   Payment {payment['memo']}:")
            if payment['ad_data']:
                try:
                    ad_data = json.loads(payment['ad_data'])
                    print(f"   Content type: {ad_data.get('content_type', 'Not set')}")
                    print(f"   Has media URL: {bool(ad_data.get('media_url'))}")
                except:
                    print(f"   Invalid JSON data")
        
        conn.close()
        print("\n✅ Complete media workflow test finished")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_complete_media_workflow()