#!/usr/bin/env python3
"""
I3lani Bot Content Storage System
Shows how Text + Image + Video content is stored and linked to ads and campaigns
"""

import sqlite3
from datetime import datetime

def show_content_storage_system():
    """Show how different content types are stored and linked"""
    
    print("📁 I3LANI CONTENT STORAGE SYSTEM")
    print("="*50)
    
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    
    # 1. Ads Table - Original Content Storage
    print("\n1️⃣ ADS TABLE - Original Content Storage:")
    print("   Stores user-submitted content before campaign creation")
    
    cursor.execute("""
        SELECT ad_id, user_id, content_type, 
               CASE 
                   WHEN content_type = 'text' THEN SUBSTR(content, 1, 50) || '...'
                   WHEN content_type = 'photo' THEN 'Photo with caption: ' || SUBSTR(content, 1, 30) || '...'
                   WHEN content_type = 'video' THEN 'Video with caption: ' || SUBSTR(content, 1, 30) || '...'
                   ELSE 'Unknown type'
               END as content_preview,
               CASE WHEN media_url IS NOT NULL THEN 'YES' ELSE 'NO' END as has_media,
               created_at
        FROM ads 
        WHERE ad_id IN (73, 74, 87)
        ORDER BY created_at DESC
    """)
    
    ads = cursor.fetchall()
    print(f"\n   📋 Recent Ads with Different Content Types:")
    for ad in ads:
        print(f"   📄 Ad {ad[0]} → User {ad[1]} → {ad[2]} → Media: {ad[4]}")
        print(f"      Content: {ad[3]}")
        print(f"      Created: {ad[5]}")
        print()
    
    # 2. Content Type Examples
    print("\n2️⃣ CONTENT TYPE EXAMPLES:")
    
    # Text only
    cursor.execute("""
        SELECT ad_id, content, media_url
        FROM ads 
        WHERE content_type = 'text' AND content IS NOT NULL AND content != ''
        ORDER BY created_at DESC
        LIMIT 2
    """)
    
    text_ads = cursor.fetchall()
    print(f"\n   📝 TEXT ONLY ADS:")
    for ad in text_ads:
        print(f"   Ad {ad[0]}: {ad[1][:80]}...")
        print(f"   Media URL: {ad[2] if ad[2] else 'None'}")
        print()
    
    # Photo with text
    cursor.execute("""
        SELECT ad_id, content, media_url
        FROM ads 
        WHERE content_type = 'photo' AND media_url IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 2
    """)
    
    photo_ads = cursor.fetchall()
    print(f"\n   📷 PHOTO + TEXT ADS:")
    for ad in photo_ads:
        print(f"   Ad {ad[0]}: Text: {ad[1][:50] if ad[1] else 'No caption'}...")
        print(f"   Media URL: {ad[2][:50]}...")
        print()
    
    # 3. Campaign Content Linking
    print("\n3️⃣ CAMPAIGN CONTENT LINKING:")
    print("   How ad content is copied to campaigns for publishing")
    
    cursor.execute("""
        SELECT c.campaign_id, c.content_type, c.ad_content, c.media_url,
               a.ad_id, a.content_type as original_type, a.media_url as original_media
        FROM campaigns c
        LEFT JOIN ads a ON c.user_id = a.user_id
        WHERE c.campaign_id IN ('CAM-2025-07-RE57', 'CAM-2025-07-BB17', 'CAM-2025-07-OR41')
        AND a.created_at = (
            SELECT MAX(created_at) 
            FROM ads a2 
            WHERE a2.user_id = c.user_id
        )
    """)
    
    campaign_links = cursor.fetchall()
    print(f"\n   🔗 Campaign → Ad Content Links:")
    for link in campaign_links:
        print(f"   Campaign: {link[0]}")
        print(f"   Content Type: {link[1]} → Media: {'YES' if link[3] else 'NO'}")
        print(f"   Linked to Ad: {link[4]} → Original Type: {link[5]}")
        print(f"   Content: {link[2][:60] if link[2] else 'Empty'}...")
        print()
    
    # 4. Publishing Content Structure
    print("\n4️⃣ PUBLISHING CONTENT STRUCTURE:")
    print("   How campaigns publish different content types")
    
    cursor.execute("""
        SELECT campaign_id, content_type, 
               CASE 
                   WHEN content_type = 'text' THEN 'Text message only'
                   WHEN content_type = 'photo' THEN 'Photo with caption'
                   WHEN content_type = 'video' THEN 'Video with caption'
                   ELSE 'Unknown publishing type'
               END as publishing_method,
               CASE WHEN media_url IS NOT NULL THEN 'send_photo/send_video' ELSE 'send_message' END as telegram_method
        FROM campaigns
        WHERE campaign_id IN ('CAM-2025-07-RE57', 'CAM-2025-07-BB17', 'CAM-2025-07-OR41')
    """)
    
    publishing = cursor.fetchall()
    print(f"\n   📺 Publishing Methods:")
    for pub in publishing:
        print(f"   {pub[0]} → {pub[1]} → {pub[2]}")
        print(f"   Telegram API: {pub[3]}")
        print()
    
    # 5. Content Storage Schema
    print("\n5️⃣ CONTENT STORAGE SCHEMA:")
    print("   Database fields for different content types")
    
    print(f"\n   📊 ADS TABLE FIELDS:")
    print(f"   - ad_id: Unique identifier")
    print(f"   - user_id: Owner of the ad")
    print(f"   - content: Text content (caption for media)")
    print(f"   - content_type: 'text', 'photo', 'video'")
    print(f"   - media_url: Telegram file_id for photos/videos")
    print(f"   - created_at: Timestamp")
    
    print(f"\n   📊 CAMPAIGNS TABLE FIELDS:")
    print(f"   - campaign_id: Unique identifier")
    print(f"   - ad_content: Copy of original text")
    print(f"   - content_type: Copy of original type")
    print(f"   - media_url: Copy of original media")
    print(f"   - payment_memo: Link to payment")
    
    # 6. Content Publishing Flow
    print("\n6️⃣ CONTENT PUBLISHING FLOW:")
    print("   Text Only: campaign.ad_content → send_message()")
    print("   Photo + Text: campaign.media_url + campaign.ad_content → send_photo(caption)")
    print("   Video + Text: campaign.media_url + campaign.ad_content → send_video(caption)")
    
    # 7. Current Content Status
    print("\n7️⃣ CURRENT CONTENT STATUS:")
    
    cursor.execute("""
        SELECT 
            content_type,
            COUNT(*) as total_ads,
            SUM(CASE WHEN media_url IS NOT NULL THEN 1 ELSE 0 END) as with_media,
            SUM(CASE WHEN content IS NOT NULL AND content != '' THEN 1 ELSE 0 END) as with_text
        FROM ads
        GROUP BY content_type
    """)
    
    stats = cursor.fetchall()
    print(f"\n   📈 Content Statistics:")
    for stat in stats:
        print(f"   {stat[0]}: {stat[1]} total, {stat[2]} with media, {stat[3]} with text")
    
    conn.close()
    
    print("\n✅ CONTENT STORAGE SYSTEM COMPLETE")
    print("   Every ad can contain text, image, video, or combinations")
    print("   Content is preserved from ads to campaigns to publishing")
    print("   Telegram API methods automatically selected based on content type")

if __name__ == "__main__":
    show_content_storage_system()