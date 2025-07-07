#!/usr/bin/env python3
"""
Quick script to add test channels to the I3lani Bot database
This is for testing purposes when you have channels where the bot is already admin
"""

import asyncio
from database import db

async def add_test_channels():
    """Add some test channels for demonstration"""
    
    # Initialize database
    await db.init_db()
    
    # Add test channels (replace with your actual channel usernames)
    test_channels = [
        {
            'channel_id': 'test_tech_channel',
            'name': 'Tech News Channel',
            'telegram_channel_id': '@technews_demo',
            'subscribers': 5000,
            'active_subscribers': 2250,
            'total_posts': 500,
            'category': 'technology',
            'description': 'Latest technology news and updates',
            'base_price_usd': 12.0
        },
        {
            'channel_id': 'test_business_channel', 
            'name': 'Business Updates',
            'telegram_channel_id': '@business_demo',
            'subscribers': 3000,
            'active_subscribers': 1350,
            'total_posts': 200,
            'category': 'business',
            'description': 'Business news and startup updates',
            'base_price_usd': 8.4
        }
    ]
    
    print("Adding test channels...")
    
    for channel in test_channels:
        success = await db.add_channel_automatically(
            channel_id=channel['channel_id'],
            channel_name=channel['name'],
            telegram_channel_id=channel['telegram_channel_id'],
            subscribers=channel['subscribers'],
            active_subscribers=channel['active_subscribers'],
            total_posts=channel['total_posts'],
            category=channel['category'],
            description=channel['description'],
            base_price_usd=channel['base_price_usd']
        )
        
        if success:
            print(f"✅ Added channel: {channel['name']}")
        else:
            print(f"❌ Failed to add channel: {channel['name']}")
    
    # Verify channels were added
    channels = await db.get_channels(active_only=True)
    print(f"\n📊 Total active channels: {len(channels)}")
    
    for channel in channels:
        print(f"- {channel['name']}: {channel['subscribers']:,} subscribers")

if __name__ == "__main__":
    asyncio.run(add_test_channels())