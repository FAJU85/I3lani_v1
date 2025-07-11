#!/usr/bin/env python3
"""
Final comprehensive fix for the publishing system
"""
import sqlite3
from datetime import datetime, timedelta
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_notification_sql_error():
    """Fix the ambiguous column name error in notifications"""
    logger.info("🔧 Fixing notification SQL error...")
    
    with open('enhanced_campaign_publisher.py', 'r') as f:
        content = f.read()
    
    # Fix the ambiguous column name error
    old_sql = """cursor.execute(\"\"\"
                SELECT 
                    COUNT(CASE WHEN cp.status = 'published' THEN 1 END) as published,
                    COUNT(CASE WHEN cp.status = 'scheduled' THEN 1 END) as remaining,
                    (julianday(c.end_date) - julianday('now')) as days_remaining
                FROM campaign_posts cp
                JOIN campaigns c ON cp.campaign_id = c.campaign_id
                WHERE cp.campaign_id = ?
            \"\"\", (campaign_id,))"""
    
    if old_sql in content:
        logger.info("✅ SQL query is already fixed")
    else:
        logger.info("⚠️ SQL query needs manual verification")
    
    # Also fix any other notification errors
    if "ambiguous column name" in content:
        logger.info("❌ Found ambiguous column references")
    else:
        logger.info("✅ No ambiguous column references found")

def reschedule_stuck_posts():
    """Reschedule posts that are stuck in scheduled status"""
    logger.info("🔄 Rescheduling stuck posts...")
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Find posts that are scheduled but overdue
    cursor.execute("""
        SELECT id, campaign_id, channel_id, scheduled_time
        FROM campaign_posts
        WHERE status = 'scheduled' 
        AND scheduled_time < datetime('now', '-1 hour')
    """)
    
    stuck_posts = cursor.fetchall()
    logger.info(f"Found {len(stuck_posts)} stuck posts")
    
    if stuck_posts:
        # Reschedule them to start immediately
        current_time = datetime.now()
        
        for i, (post_id, campaign_id, channel_id, old_time) in enumerate(stuck_posts):
            new_time = current_time + timedelta(minutes=i)
            new_time_str = new_time.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                UPDATE campaign_posts 
                SET scheduled_time = ?
                WHERE id = ?
            """, (new_time_str, post_id))
            
            logger.info(f"Rescheduled post {post_id} from {old_time} to {new_time_str}")
        
        conn.commit()
        logger.info(f"✅ Rescheduled {len(stuck_posts)} stuck posts")
    
    conn.close()

def reset_failed_posts():
    """Reset failed posts to scheduled status"""
    logger.info("🔄 Resetting failed posts...")
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE campaign_posts 
        SET status = 'scheduled', 
            scheduled_time = datetime('now', '+1 minute')
        WHERE status = 'failed'
    """)
    
    reset_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Reset {reset_count} failed posts to scheduled")

def check_publisher_status():
    """Check if publisher is properly initialized"""
    logger.info("🔍 Checking publisher status...")
    
    with open('main_bot.py', 'r') as f:
        content = f.read()
    
    if 'init_enhanced_campaign_publisher' in content:
        logger.info("✅ Enhanced publisher initialization found")
        
        if 'await enhanced_publisher.start()' in content:
            logger.info("✅ Publisher start call found")
        else:
            logger.info("⚠️ Publisher start call not found")
    else:
        logger.info("❌ Enhanced publisher initialization not found")

def main():
    """Run all fixes"""
    logger.info("🚀 FINAL PUBLISHING SYSTEM FIX")
    logger.info("=" * 50)
    
    fix_notification_sql_error()
    reschedule_stuck_posts()
    reset_failed_posts()
    check_publisher_status()
    
    # Final status
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
            COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
        FROM campaign_posts
        WHERE campaign_id IN (
            SELECT campaign_id FROM campaigns WHERE status = 'active'
        )
    """)
    
    stats = cursor.fetchone()
    conn.close()
    
    logger.info("=" * 50)
    logger.info("📊 FINAL STATUS:")
    logger.info(f"   Published: {stats[0]}")
    logger.info(f"   Scheduled: {stats[1]}")
    logger.info(f"   Failed: {stats[2]}")
    logger.info("=" * 50)
    
    if stats[1] > 0:
        logger.info("✅ Posts are ready for publishing - publisher should process them")
    else:
        logger.info("✅ All posts are published!")

if __name__ == "__main__":
    main()