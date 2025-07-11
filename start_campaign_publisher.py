#!/usr/bin/env python3
"""
Manually start the enhanced campaign publisher to process all pending posts
"""
import asyncio
import sys
import os
import logging
from aiogram import Bot
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

async def start_publisher():
    """Start the enhanced campaign publisher manually"""
    try:
        # Initialize bot
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("BOT_TOKEN not found")
            return
            
        bot = Bot(token=bot_token)
        logger.info("Bot initialized")
        
        # Initialize database
        from database import init_db
        await init_db()
        logger.info("Database initialized")
        
        # Initialize Post Identity System
        from post_identity_system import init_post_identity_system
        await init_post_identity_system()
        logger.info("Post Identity System initialized")
        
        # Initialize Enhanced Campaign Publisher
        from enhanced_campaign_publisher import init_enhanced_campaign_publisher
        publisher = await init_enhanced_campaign_publisher(bot)
        
        if not publisher:
            logger.error("Failed to initialize publisher")
            return
            
        logger.info(f"Publisher initialized, running status: {publisher.running}")
        
        # Check for pending posts
        due_posts = await publisher._get_due_posts()
        logger.info(f"Found {len(due_posts)} posts ready for publishing")
        
        # Get campaign stats
        from database import Database
        db = Database()
        
        # Check all active campaigns
        query = """
            SELECT c.campaign_id, c.user_id, c.status,
                   COUNT(cp.id) as total_posts,
                   COUNT(CASE WHEN cp.status = 'published' THEN 1 END) as published,
                   COUNT(CASE WHEN cp.status = 'scheduled' THEN 1 END) as scheduled
            FROM campaigns c
            LEFT JOIN campaign_posts cp ON c.campaign_id = cp.campaign_id
            WHERE c.status = 'active'
            GROUP BY c.campaign_id
            ORDER BY c.created_at DESC
        """
        
        conn = await db.get_connection()
        cursor = await conn.execute(query)
        campaigns = await cursor.fetchall()
        await cursor.close()
        
        logger.info("\n=== Campaign Status Summary ===")
        for campaign in campaigns:
            if campaign[5] > 0:  # scheduled column
                logger.info(f"Campaign {campaign[0]}: {campaign[4]}/{campaign[3]} published, {campaign[5]} pending")
                
        # Check scheduled post times
        query2 = """
            SELECT campaign_id, scheduled_time, status
            FROM campaign_posts 
            WHERE status = 'scheduled'
            AND campaign_id IN (SELECT campaign_id FROM campaigns WHERE status = 'active')
            ORDER BY scheduled_time ASC
            LIMIT 10
        """
        cursor2 = await conn.execute(query2)
        scheduled_posts = await cursor2.fetchall()
        await cursor2.close()
        
        logger.info("\n=== Next Scheduled Posts ===")
        for post in scheduled_posts:
            logger.info(f"Campaign {post[0]}: scheduled for {post[1]}")
        
        # Start the publisher if not running
        if not publisher.running:
            logger.info("Starting publisher...")
            await publisher.start()
            logger.info("Publisher started successfully")
        
        # Let it run for a while to process pending posts
        logger.info("Processing pending posts for 5 minutes...")
        
        # Process in intervals
        for i in range(10):  # 10 intervals of 30 seconds = 5 minutes
            await asyncio.sleep(30)
            
            # Check status
            campaigns_updated = await db.execute_query("""
                SELECT COUNT(DISTINCT campaign_id) as active_campaigns,
                       COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as pending,
                       COUNT(CASE WHEN status = 'published' THEN 1 END) as published
                FROM campaign_posts
                WHERE campaign_id IN (
                    SELECT campaign_id FROM campaigns WHERE status = 'active'
                )
            """)
            
            if campaigns_updated:
                stats = campaigns_updated[0]
                logger.info(f"Progress: {stats['published']} published, {stats['pending']} pending")
                
                if stats['pending'] == 0:
                    logger.info("All posts published!")
                    break
        
        logger.info("Publisher running successfully!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start_publisher())