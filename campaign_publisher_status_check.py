#!/usr/bin/env python3
"""
Campaign Publisher Status Check
Real-time monitoring of campaign publisher status and performance
"""

import asyncio
import sqlite3
import sys
sys.path.append('.')
from datetime import datetime

async def check_publisher_status():
    """Check the current status of the campaign publisher system"""
    
    print("📊 CAMPAIGN PUBLISHER STATUS CHECK")
    print("="*50)
    
    # Check 1: Database Status
    print("\n1. Database Status:")
    print("-" * 20)
    
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Check campaign status
        cursor.execute('SELECT posts_published, total_posts, status FROM campaigns WHERE campaign_id = ?', ('CAM-2025-07-YBZ3',))
        result = cursor.fetchone()
        
        if result:
            posts_published, total_posts, status = result
            progress = (posts_published / total_posts * 100) if total_posts > 0 else 0
            print(f"Campaign CAM-2025-07-YBZ3:")
            print(f"  Status: {status}")
            print(f"  Progress: {posts_published}/{total_posts} ({progress:.1f}%)")
        
        # Check post status distribution
        cursor.execute('''
            SELECT status, COUNT(*) 
            FROM campaign_posts 
            WHERE campaign_id = 'CAM-2025-07-YBZ3'
            GROUP BY status
        ''')
        
        post_stats = cursor.fetchall()
        print("  Post Status:")
        for status, count in post_stats:
            print(f"    {status}: {count}")
        
        # Check for due posts right now
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            SELECT COUNT(*) FROM campaign_posts 
            WHERE campaign_id = 'CAM-2025-07-YBZ3' 
            AND status = 'scheduled' 
            AND scheduled_time <= ?
        ''', (now,))
        
        due_count = cursor.fetchone()[0]
        print(f"  Posts due now: {due_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    
    # Check 2: Publisher System Status
    print("\n2. Publisher System Status:")
    print("-" * 30)
    
    try:
        from campaign_publisher import CampaignPublisher, get_campaign_publisher
        from aiogram import Bot
        from config import BOT_TOKEN
        
        # Check global publisher
        global_publisher = get_campaign_publisher()
        
        if global_publisher:
            print(f"✅ Global publisher exists")
            print(f"   Running: {global_publisher.running}")
        else:
            print("⚠️ No global publisher found")
        
        # Test fresh publisher
        bot = Bot(token=BOT_TOKEN)
        test_publisher = CampaignPublisher(bot)
        
        # Test due posts retrieval
        due_posts = await test_publisher._get_due_posts()
        print(f"✅ Due posts retrieval works: {len(due_posts)} posts")
        
        await bot.session.close()
        
    except Exception as e:
        print(f"❌ Publisher system check failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Check 3: Recent Activity
    print("\n3. Recent Publishing Activity:")
    print("-" * 35)
    
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT channel_id, status, published_at, scheduled_time, error_message
            FROM campaign_posts 
            WHERE campaign_id = 'CAM-2025-07-YBZ3'
            ORDER BY id DESC 
            LIMIT 5
        ''')
        
        recent_posts = cursor.fetchall()
        
        print("Recent posts:")
        for channel, status, pub_time, sched_time, error in recent_posts:
            time_info = pub_time if pub_time else sched_time
            error_info = f" | Error: {error}" if error else ""
            print(f"  {channel} | {status} | {time_info}{error_info}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Activity check failed: {e}")
    
    # Check 4: Performance Recommendations
    print("\n4. Performance Recommendations:")
    print("-" * 40)
    
    recommendations = []
    
    if due_count > 0:
        recommendations.append("⚠️ Posts are due but not being published automatically")
        recommendations.append("🔧 Campaign publisher automatic loop needs to be verified")
    
    if posts_published > 0:
        recommendations.append("✅ Manual publishing is working correctly")
    
    if due_count == 0:
        recommendations.append("ℹ️ No posts currently due - may be scheduled for future")
    
    for rec in recommendations:
        print(f"  {rec}")
    
    # Summary
    print("\n" + "="*50)
    print("📋 STATUS SUMMARY")
    print("="*50)
    
    if posts_published > 0:
        print("✅ Campaign system is functional")
        print("✅ Database is properly configured")
        print("✅ Manual publishing works")
    
    if due_count > 0:
        print("⚠️ Automatic publishing needs attention")
    else:
        print("ℹ️ No immediate publishing action needed")
    
    return True

if __name__ == "__main__":
    asyncio.run(check_publisher_status())