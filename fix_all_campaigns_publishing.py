#!/usr/bin/env python3
"""
Fix ALL campaigns publishing issue by updating scheduled times and starting publisher
"""
import asyncio
import sqlite3
from datetime import datetime, timedelta
import logging
import os
from aiogram import Bot
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def fix_all_campaigns():
    """Fix all campaigns publishing issue"""
    try:
        # Initialize bot
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("BOT_TOKEN not found")
            return
            
        bot = Bot(token=bot_token)
        logger.info("Bot initialized")
        
        # Connect to database
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # First, check all scheduled posts
        cursor.execute("""
            SELECT cp.id, cp.campaign_id, cp.scheduled_time, cp.status,
                   c.user_id, c.status as campaign_status
            FROM campaign_posts cp
            JOIN campaigns c ON cp.campaign_id = c.campaign_id
            WHERE cp.status = 'scheduled'
            ORDER BY cp.scheduled_time ASC
        """)
        
        scheduled_posts = cursor.fetchall()
        logger.info(f"Found {len(scheduled_posts)} scheduled posts")
        
        # Update all scheduled posts to have immediate scheduling
        current_time = datetime.now()
        posts_updated = 0
        
        for i, post in enumerate(scheduled_posts):
            post_id, campaign_id, scheduled_time, status, user_id, campaign_status = post
            
            # Schedule posts to start immediately, one every minute
            new_time = current_time + timedelta(minutes=i)
            new_time_str = new_time.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                UPDATE campaign_posts 
                SET scheduled_time = ? 
                WHERE id = ?
            """, (new_time_str, post_id))
            
            posts_updated += 1
            
            if i % 10 == 0:
                logger.info(f"Updated {posts_updated} posts...")
        
        conn.commit()
        logger.info(f"✅ Updated {posts_updated} scheduled posts to start immediately")
        
        # Initialize and start the enhanced campaign publisher
        from database import init_db
        await init_db()
        
        from post_identity_system import init_post_identity_system
        await init_post_identity_system()
        
        from enhanced_campaign_publisher import init_enhanced_campaign_publisher
        publisher = await init_enhanced_campaign_publisher(bot)
        
        if not publisher:
            logger.error("Failed to initialize publisher")
            return
            
        logger.info(f"Publisher initialized, running status: {publisher.running}")
        
        if not publisher.running:
            logger.info("Starting publisher...")
            await publisher.start()
            logger.info("Publisher started")
        
        # Process posts immediately
        logger.info("Processing all pending posts...")
        
        # Keep running for 10 minutes to ensure all posts are published
        for i in range(20):  # 20 * 30 seconds = 10 minutes
            due_posts = await publisher._get_due_posts()
            logger.info(f"Iteration {i+1}: Found {len(due_posts)} posts ready for publishing")
            
            if len(due_posts) > 0:
                await publisher._process_due_posts()
                logger.info(f"Processed {len(due_posts)} posts")
            
            # Check progress
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
                    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled
                FROM campaign_posts
                WHERE campaign_id IN (
                    SELECT campaign_id FROM campaigns WHERE status = 'active'
                )
            """)
            
            stats = cursor.fetchone()
            logger.info(f"Progress: {stats[0]} published, {stats[1]} scheduled")
            
            if stats[1] == 0:
                logger.info("✅ All posts published!")
                break
            
            await asyncio.sleep(30)
        
        conn.close()
        logger.info("✅ Campaign publishing fix completed!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == "__main__":
    asyncio.run(fix_all_campaigns())