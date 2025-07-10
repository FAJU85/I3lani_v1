#!/usr/bin/env python3
"""
Debug Content Publishing Bug - Investigate why real user content isn't being published
"""

import asyncio
import sqlite3
import json
import sys
sys.path.append('.')

async def debug_content_publishing():
    """Debug the content publishing issue"""
    
    print("🐞 DEBUGGING CONTENT PUBLISHING BUG")
    print("="*50)
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Step 1: Check what content is stored in ads table vs campaigns
    print("1. CONTENT STORAGE COMPARISON:")
    print()
    
    # Get real user content from ads table
    print("📁 REAL USER CONTENT (ads table):")
    cursor.execute("""
        SELECT ad_id, user_id, content, content_type, media_url, created_at
        FROM ads 
        WHERE user_id = 566158428 
        ORDER BY created_at DESC 
        LIMIT 3
    """)
    
    ads = cursor.fetchall()
    for ad_id, user_id, content, content_type, media_url, created_at in ads:
        print(f"  Ad {ad_id} ({created_at}):")
        print(f"    Content: {content[:50]}..." if content else "    Content: None")
        print(f"    Type: {content_type}")
        print(f"    Media: {media_url[:50]}..." if media_url else "    Media: None")
        print()
    
    # Get campaign content 
    print("📋 CAMPAIGN CONTENT (campaigns table):")
    cursor.execute("""
        SELECT campaign_id, user_id, ad_content, payment_memo, created_at
        FROM campaigns 
        WHERE user_id = 566158428 
        ORDER BY created_at DESC 
        LIMIT 3
    """)
    
    campaigns = cursor.fetchall()
    for campaign_id, user_id, ad_content, payment_memo, created_at in campaigns:
        print(f"  {campaign_id} ({created_at}):")
        print(f"    Content: {ad_content[:50]}..." if ad_content else "    Content: None")
        print(f"    Payment: {payment_memo}")
        print()
    
    # Step 2: Check what publisher is trying to publish
    print("2. PUBLISHER CONTENT RETRIEVAL:")
    print()
    
    # Get what the publisher sees for each campaign
    for campaign_id, _, _, _, _ in campaigns:
        print(f"📤 Publishing data for {campaign_id}:")
        
        # Simulate what publisher gets
        cursor.execute("""
            SELECT cp.*, c.ad_content, c.user_id, 
                   COALESCE(c.content_type, 'text') as content_type, 
                   c.media_url
            FROM campaign_posts cp
            JOIN campaigns c ON cp.campaign_id = c.campaign_id
            WHERE cp.campaign_id = ?
            AND cp.status = 'scheduled'
            LIMIT 1
        """, (campaign_id,))
        
        post_data = cursor.fetchone()
        if post_data:
            print(f"    Content to publish: {post_data[7][:50]}..." if post_data[7] else "    Content: None")
            print(f"    Content type: {post_data[9]}")
            print(f"    Media URL: {post_data[10][:50]}..." if post_data[10] else "    Media: None")
        else:
            print(f"    ❌ No scheduled posts found")
        print()
    
    # Step 3: Check automatic payment confirmation content retrieval
    print("3. PAYMENT CONFIRMATION CONTENT RETRIEVAL:")
    print()
    
    try:
        from automatic_payment_confirmation import automatic_confirmation
        
        # Test content retrieval for user 566158428
        user_content = await automatic_confirmation._get_user_ad_content(566158428)
        
        print(f"📥 Content retrieved by payment confirmation:")
        print(f"    Content: {user_content.get('ad_content', 'None')[:50]}...")
        print(f"    Type: {user_content.get('content_type', 'None')}")
        print(f"    Media: {user_content.get('media_url', 'None')[:50]}...")
        print(f"    Ad ID: {user_content.get('ad_id', 'None')}")
        print()
        
    except Exception as e:
        print(f"    ❌ Error testing payment confirmation: {e}")
    
    # Step 4: Identify the disconnect
    print("4. PROBLEM IDENTIFICATION:")
    print()
    
    # Check if campaigns have the right content
    print("🔍 Content mismatch analysis:")
    
    # Get latest real user ad
    cursor.execute("""
        SELECT content, content_type, media_url 
        FROM ads 
        WHERE user_id = 566158428 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    latest_ad = cursor.fetchone()
    
    # Get latest campaign
    cursor.execute("""
        SELECT ad_content, campaign_metadata 
        FROM campaigns 
        WHERE user_id = 566158428 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    latest_campaign = cursor.fetchone()
    
    if latest_ad and latest_campaign:
        user_content = latest_ad[0] or ""
        campaign_content = latest_campaign[0] or ""
        
        print(f"    Latest user ad content: {user_content[:50]}...")
        print(f"    Latest campaign content: {campaign_content[:50]}...")
        
        if user_content != campaign_content:
            print(f"    ❌ CONTENT MISMATCH DETECTED!")
            print(f"    User submitted: '{user_content[:30]}...'")
            print(f"    Campaign has: '{campaign_content[:30]}...'")
        else:
            print(f"    ✅ Content matches")
    
    conn.close()
    
    print()
    print("🎯 ROOT CAUSE ANALYSIS:")
    print("="*30)
    print("The issue is likely in one of these areas:")
    print("1. Payment confirmation not retrieving latest user content")
    print("2. Campaign creation using fallback/test content instead of real content")
    print("3. Publisher not getting media URLs correctly")
    print("4. Content type mismatch (text vs photo)")
    
    return True

if __name__ == "__main__":
    asyncio.run(debug_content_publishing())