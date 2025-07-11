#!/usr/bin/env python3
"""Test media saving during ad creation process"""

import sqlite3
import json
from datetime import datetime

def test_media_saving():
    """Test if media URLs are being saved correctly"""
    try:
        conn = sqlite3.connect('bot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("🔍 Testing Media Saving in Ad Creation Process")
        print("=" * 50)
        
        # 1. Check recent ads with media
        print("\n1️⃣ RECENT ADS WITH MEDIA:")
        cursor.execute("""
            SELECT ad_id, user_id, content, content_type, media_url, created_at
            FROM ads 
            WHERE media_url IS NOT NULL 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        ads_with_media = cursor.fetchall()
        print(f"   Found {len(ads_with_media)} ads with media")
        
        for ad in ads_with_media:
            print(f"\n   Ad {ad['ad_id']} (User {ad['user_id']}):")
            print(f"   Type: {ad['content_type']}")
            print(f"   Media: {ad['media_url'][:50]}..." if ad['media_url'] else "None")
            print(f"   Content: {ad['content'][:50]}...")
            print(f"   Created: {ad['created_at']}")
        
        # 2. Check campaigns with media
        print("\n\n2️⃣ CAMPAIGNS WITH MEDIA:")
        cursor.execute("""
            SELECT campaign_id, user_id, ad_content, content_type, media_url, 
                   payment_memo, created_at
            FROM campaigns 
            WHERE media_url IS NOT NULL 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        campaigns_with_media = cursor.fetchall()
        print(f"   Found {len(campaigns_with_media)} campaigns with media")
        
        for campaign in campaigns_with_media:
            print(f"\n   Campaign {campaign['campaign_id']} (User {campaign['user_id']}):")
            print(f"   Type: {campaign['content_type']}")
            print(f"   Media: {campaign['media_url'][:50]}..." if campaign['media_url'] else "None")
            print(f"   Payment: {campaign['payment_memo']}")
            print(f"   Created: {campaign['created_at']}")
        
        # 3. Check payment tracking with ad_data
        print("\n\n3️⃣ PAYMENT TRACKING WITH AD DATA:")
        cursor.execute("""
            SELECT memo, user_id, ad_data, created_at
            FROM payment_memo_tracking 
            WHERE ad_data IS NOT NULL 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        payments_with_data = cursor.fetchall()
        print(f"   Found {len(payments_with_data)} payments with ad data")
        
        for payment in payments_with_data:
            print(f"\n   Payment {payment['memo']} (User {payment['user_id']}):")
            if payment['ad_data']:
                try:
                    ad_data = json.loads(payment['ad_data'])
                    print(f"   Content type: {ad_data.get('content_type', 'Not set')}")
                    print(f"   Has media: {bool(ad_data.get('media_url'))}")
                    if ad_data.get('media_url'):
                        print(f"   Media URL: {ad_data.get('media_url')[:50]}...")
                except:
                    print(f"   Invalid JSON data")
            print(f"   Created: {payment['created_at']}")
        
        # 4. Test media propagation from ads to campaigns
        print("\n\n4️⃣ MEDIA PROPAGATION TEST:")
        cursor.execute("""
            SELECT 
                c.campaign_id,
                c.user_id,
                c.content_type as campaign_type,
                c.media_url as campaign_media,
                a.content_type as ad_type,
                a.media_url as ad_media
            FROM campaigns c
            LEFT JOIN ads a ON a.user_id = c.user_id
            WHERE c.created_at >= datetime('now', '-1 day')
            GROUP BY c.campaign_id
            ORDER BY c.created_at DESC
            LIMIT 5
        """)
        
        propagation_test = cursor.fetchall()
        for test in propagation_test:
            print(f"\n   Campaign {test['campaign_id']}:")
            print(f"   Campaign has media: {bool(test['campaign_media'])}")
            print(f"   User has ads with media: {bool(test['ad_media'])}")
            if test['ad_media'] and not test['campaign_media']:
                print(f"   ⚠️  WARNING: User has media in ads but not in campaign!")
        
        conn.close()
        print("\n✅ Media saving test completed")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_media_saving()