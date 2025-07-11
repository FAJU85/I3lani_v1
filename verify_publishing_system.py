#!/usr/bin/env python3
"""
Verify the publishing system is working correctly
"""
import sqlite3
from datetime import datetime, timedelta
import os
from aiogram import Bot
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def verify_publishing():
    """Verify the publishing system comprehensively"""
    print("🔍 VERIFYING PUBLISHING SYSTEM")
    print("=" * 50)
    
    # 1. Check database status
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Get campaign stats
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT c.campaign_id) as campaigns,
            COUNT(cp.id) as total_posts,
            COUNT(CASE WHEN cp.status = 'published' THEN 1 END) as published,
            COUNT(CASE WHEN cp.status = 'scheduled' THEN 1 END) as scheduled,
            COUNT(CASE WHEN cp.status = 'failed' THEN 1 END) as failed
        FROM campaigns c
        LEFT JOIN campaign_posts cp ON c.campaign_id = cp.campaign_id
        WHERE c.status = 'active'
    """)
    
    stats = cursor.fetchone()
    print(f"📊 CAMPAIGN STATS:")
    print(f"   Active Campaigns: {stats[0]}")
    print(f"   Total Posts: {stats[1]}")
    print(f"   Published: {stats[2]}")
    print(f"   Scheduled: {stats[3]}")
    print(f"   Failed: {stats[4]}")
    
    # 2. Check recent publishing activity
    cursor.execute("""
        SELECT cp.campaign_id, cp.channel_id, cp.scheduled_time, cp.status
        FROM campaign_posts cp
        JOIN campaigns c ON cp.campaign_id = c.campaign_id
        WHERE c.status = 'active'
        AND cp.scheduled_time <= datetime('now')
        AND cp.status = 'scheduled'
        ORDER BY cp.scheduled_time ASC
        LIMIT 10
    """)
    
    overdue_posts = cursor.fetchall()
    print(f"\n⏰ OVERDUE POSTS (should be publishing now):")
    for post in overdue_posts:
        print(f"   {post[0]} -> {post[1]} (scheduled: {post[2]})")
    
    # 3. Check channels
    cursor.execute("""
        SELECT channel_id, name, username, is_active, subscriber_count
        FROM channels
        WHERE is_active = 1
    """)
    
    channels = cursor.fetchall()
    print(f"\n📺 ACTIVE CHANNELS:")
    for channel in channels:
        print(f"   {channel[2]} ({channel[1]}): {channel[4]} subscribers")
    
    # 4. Check recent campaign content
    cursor.execute("""
        SELECT c.campaign_id, c.ad_content, c.content_type, c.media_url
        FROM campaigns c
        WHERE c.status = 'active'
        AND c.ad_content IS NOT NULL
        ORDER BY c.created_at DESC
        LIMIT 5
    """)
    
    recent_campaigns = cursor.fetchall()
    print(f"\n📝 RECENT CAMPAIGN CONTENT:")
    for campaign in recent_campaigns:
        content_preview = campaign[1][:30] + "..." if campaign[1] and len(campaign[1]) > 30 else campaign[1]
        has_media = "Yes" if campaign[3] else "No"
        print(f"   {campaign[0]}: {content_preview} (Type: {campaign[2]}, Media: {has_media})")
    
    # 5. Test bot connection
    try:
        bot_token = os.getenv('BOT_TOKEN')
        if bot_token:
            bot = Bot(token=bot_token)
            me = await bot.get_me()
            print(f"\n🤖 BOT CONNECTION: ✅ Connected as @{me.username}")
            
            # Test channel access
            for channel in channels:
                try:
                    chat = await bot.get_chat(channel[2])
                    print(f"   Channel {channel[2]}: ✅ Accessible")
                except Exception as e:
                    print(f"   Channel {channel[2]}: ❌ Error - {e}")
            
            await bot.session.close()
        else:
            print(f"\n🤖 BOT CONNECTION: ❌ No BOT_TOKEN")
    except Exception as e:
        print(f"\n🤖 BOT CONNECTION: ❌ Error - {e}")
    
    # 6. Check for publisher process
    print(f"\n🔄 PUBLISHER STATUS:")
    
    # Check if enhanced publisher initialization is in main_bot
    try:
        with open('main_bot.py', 'r') as f:
            main_bot_content = f.read()
            
        if 'init_enhanced_campaign_publisher' in main_bot_content:
            print("   ✅ Enhanced publisher initialization found in main_bot.py")
        else:
            print("   ❌ Enhanced publisher initialization NOT found in main_bot.py")
            
        if 'await publisher.start()' in main_bot_content:
            print("   ✅ Publisher start call found")
        else:
            print("   ❌ Publisher start call NOT found")
            
    except Exception as e:
        print(f"   ❌ Error checking main_bot.py: {e}")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ VERIFICATION COMPLETE")
    
    # Summary
    if stats[3] > 0:  # scheduled posts
        print(f"⚠️  WARNING: {stats[3]} posts are scheduled but not publishing")
        print("   This suggests the publisher is not running or has errors")
    else:
        print("✅ All posts are published - system appears healthy")

if __name__ == "__main__":
    asyncio.run(verify_publishing())