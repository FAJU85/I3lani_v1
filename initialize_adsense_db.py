#!/usr/bin/env python3
"""
Initialize AdSense Database Tables
Creates the necessary tables for the AdSense system
"""

import asyncio
import aiosqlite
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_adsense_tables():
    """Create AdSense system tables"""
    logger.info("🗄️ Creating AdSense database tables...")
    
    async with aiosqlite.connect("bot.db") as db:
        # AdSense Channels table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS adsense_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE NOT NULL,
                channel_name TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                subscribers INTEGER DEFAULT 0,
                avg_engagement REAL DEFAULT 0.0,
                suggested_cpc REAL DEFAULT 0.01,
                suggested_cpm REAL DEFAULT 0.50,
                owner_id INTEGER,
                available_slots INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # AdSense Bids table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS adsense_bids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                advertiser_id INTEGER NOT NULL,
                channel_id TEXT NOT NULL,
                bid_amount REAL NOT NULL,
                bid_type TEXT NOT NULL CHECK (bid_type IN ('cpc', 'cpm')),
                duration_hours INTEGER NOT NULL,
                content TEXT NOT NULL,
                media_url TEXT,
                target_clicks INTEGER,
                target_impressions INTEGER,
                max_budget REAL NOT NULL,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'cancelled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (channel_id) REFERENCES adsense_channels (channel_id),
                FOREIGN KEY (advertiser_id) REFERENCES users (user_id)
            )
        ''')
        
        # AdSense Auctions table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS adsense_auctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                winning_bid_id INTEGER,
                auction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_bids INTEGER DEFAULT 0,
                winning_amount REAL,
                FOREIGN KEY (channel_id) REFERENCES adsense_channels (channel_id),
                FOREIGN KEY (winning_bid_id) REFERENCES adsense_bids (id)
            )
        ''')
        
        # AdSense Performance table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS adsense_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                ctr REAL DEFAULT 0.0,
                cost_per_click REAL DEFAULT 0.0,
                cost_per_impression REAL DEFAULT 0.0,
                revenue_generated REAL DEFAULT 0.0,
                channel_owner_share REAL DEFAULT 0.0,
                platform_share REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (channel_id) REFERENCES adsense_channels (channel_id)
            )
        ''')
        
        await db.commit()
        logger.info("✅ AdSense database tables created successfully")

async def register_existing_channels():
    """Register existing channels in AdSense system"""
    logger.info("📺 Registering existing channels in AdSense system...")
    
    async with aiosqlite.connect("bot.db") as db:
        # Get existing channels
        cursor = await db.execute("SELECT * FROM channels")
        channels = await cursor.fetchall()
        
        for channel in channels:
            channel_id = channel[0]  # id
            name = channel[1]        # name
            subscribers = channel[3] if len(channel) > 3 else 0
            category = channel[4] if len(channel) > 4 else 'general'
            
            # Calculate suggested pricing based on subscribers
            suggested_cpc = max(0.01, min(0.10, subscribers * 0.0001))
            suggested_cpm = max(0.50, min(5.00, subscribers * 0.001))
            
            # Register in AdSense system
            await db.execute('''
                INSERT OR REPLACE INTO adsense_channels 
                (channel_id, channel_name, category, subscribers, owner_id, suggested_cpc, suggested_cpm)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (channel_id, name, category, subscribers, 123456, suggested_cpc, suggested_cpm))
            
            logger.info(f"✅ Registered: {name} ({channel_id}) - {subscribers} subscribers")
        
        await db.commit()
        logger.info(f"✅ Registered {len(channels)} channels in AdSense system")

async def test_adsense_functionality():
    """Test AdSense system functionality"""
    logger.info("🧪 Testing AdSense functionality...")
    
    async with aiosqlite.connect("bot.db") as db:
        # Test 1: Check AdSense channels
        cursor = await db.execute("SELECT * FROM adsense_channels")
        channels = await cursor.fetchall()
        logger.info(f"📺 Found {len(channels)} AdSense channels")
        
        for channel in channels:
            logger.info(f"   - {channel[2]} ({channel[1]}): {channel[4]} subscribers, CPC: ${channel[6]:.3f}, CPM: ${channel[7]:.2f}")
        
        # Test 2: Place a test bid
        if channels:
            test_channel = channels[0]
            await db.execute('''
                INSERT INTO adsense_bids 
                (advertiser_id, channel_id, bid_amount, bid_type, duration_hours, content, max_budget)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (123456, test_channel[1], 0.05, 'cpc', 24, 'Test AdSense bid content', 10.00))
            
            await db.commit()
            logger.info("✅ Test bid placed successfully")
        
        # Test 3: Check bids
        cursor = await db.execute("SELECT * FROM adsense_bids")
        bids = await cursor.fetchall()
        logger.info(f"💰 Found {len(bids)} bids in system")
        
        for bid in bids:
            logger.info(f"   - Bid ID: {bid[0]}, Channel: {bid[2]}, Amount: ${bid[3]:.3f}, Type: {bid[4]}")

async def main():
    """Main function to initialize and test AdSense system"""
    logger.info("🚀 Starting AdSense Database Initialization")
    
    try:
        # Create tables
        await create_adsense_tables()
        
        # Register existing channels
        await register_existing_channels()
        
        # Test functionality
        await test_adsense_functionality()
        
        logger.info("✅ AdSense database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during AdSense initialization: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())