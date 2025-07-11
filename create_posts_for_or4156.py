#!/usr/bin/env python3
"""
Create scheduled posts for the OR4156 campaign
"""

import sqlite3
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_scheduled_posts():
    """Create scheduled posts for campaign CAM-2025-07-OR41"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Get campaign details
        cursor.execute("SELECT * FROM campaigns WHERE campaign_id = 'CAM-2025-07-OR41'")
        campaign = cursor.fetchone()
        
        if not campaign:
            logger.error("Campaign CAM-2025-07-OR41 not found")
            return False
            
        campaign_id = campaign[1]
        user_id = campaign[2]
        duration_days = campaign[11]
        posts_per_day = campaign[12]
        total_posts = campaign[13]
        selected_channels = campaign[14]
        ad_content = campaign[7]
        content_type = campaign[24]
        media_url = campaign[25]
        
        print(f"Creating posts for campaign {campaign_id}")
        print(f"User ID: {user_id}")
        print(f"Duration: {duration_days} days")
        print(f"Posts per day: {posts_per_day}")
        print(f"Total posts: {total_posts}")
        print(f"Channels: {selected_channels}")
        
        # Parse channels
        channels = selected_channels.split(',')
        
        # Create posts for each day and channel
        start_date = datetime.now()
        post_count = 0
        
        for day in range(duration_days):
            for post_per_day in range(posts_per_day):
                for channel in channels:
                    channel = channel.strip()
                    
                    # Calculate scheduled time
                    scheduled_time = start_date + timedelta(
                        days=day,
                        hours=post_per_day * 12  # Space posts 12 hours apart
                    )
                    
                    # Insert post
                    cursor.execute("""
                        INSERT INTO campaign_posts (
                            campaign_id, channel_id, post_content, scheduled_time, status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        campaign_id, channel, ad_content, scheduled_time, "scheduled", datetime.now()
                    ))
                    
                    post_count += 1
                    
                    print(f"  Post {post_count}: {channel} at {scheduled_time}")
        
        conn.commit()
        print(f"✅ Created {post_count} scheduled posts for campaign {campaign_id}")
        
        # Update campaign with post count
        cursor.execute("""
            UPDATE campaigns 
            SET total_posts = ? 
            WHERE campaign_id = ?
        """, (post_count, campaign_id))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating posts: {e}")
        return False

if __name__ == "__main__":
    success = create_scheduled_posts()
    if success:
        print("\n🎉 All scheduled posts created successfully!")
        print("The automatic publishing system will now process these posts.")
    else:
        print("\n❌ Failed to create scheduled posts")