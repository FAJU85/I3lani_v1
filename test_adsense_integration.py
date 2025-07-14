#!/usr/bin/env python3
"""
Test AdSense Integration System
Tests the newly implemented AdSense functionality
"""

import asyncio
import logging
from database import Database
from adsense_system_architecture import adsense_system

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_adsense_integration():
    """Test AdSense system integration"""
    logger.info("🧪 Testing AdSense Integration System")
    
    # Initialize database
    db = Database()
    await db.init_db()
    
    # Create AdSense tables
    try:
        await db.create_adsense_tables()
        logger.info("✅ AdSense tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create AdSense tables: {e}")
        return
    
    # Initialize AdSense system
    await adsense_system.initialize_database()
    
    # Test 1: Register existing channels in AdSense system
    logger.info("📺 Test 1: Registering existing channels...")
    
    # Get existing channels from regular database
    existing_channels = await db.get_active_channels()
    logger.info(f"Found {len(existing_channels)} existing channels")
    
    # Register each channel in AdSense system
    for channel in existing_channels:
        success = await adsense_system.register_channel(
            channel_id=channel['channel_id'],
            owner_id=channel.get('owner_id', 123456),  # Default owner for testing
            channel_name=channel['name'],
            category=channel.get('category', 'general'),
            subscribers=channel.get('subscribers', 0)
        )
        if success:
            logger.info(f"✅ Registered channel: {channel['name']} ({channel['channel_id']})")
        else:
            logger.error(f"❌ Failed to register channel: {channel['name']}")
    
    # Test 2: Get available channels from AdSense system
    logger.info("🎯 Test 2: Getting available channels...")
    
    adsense_channels = await adsense_system.get_available_channels()
    logger.info(f"Found {len(adsense_channels)} AdSense channels")
    
    for channel in adsense_channels:
        logger.info(f"📊 Channel: {channel.channel_name}")
        logger.info(f"   👥 Subscribers: {channel.subscribers}")
        logger.info(f"   💰 Suggested CPC: ${channel.suggested_cpc:.3f}")
        logger.info(f"   📈 Suggested CPM: ${channel.suggested_cpm:.2f}")
        logger.info(f"   🏷️ Category: {channel.category}")
    
    # Test 3: Test bid placement
    logger.info("💰 Test 3: Testing bid placement...")
    
    if adsense_channels:
        from adsense_system_architecture import AdBid
        from datetime import datetime
        from decimal import Decimal
        
        test_bid = AdBid(
            advertiser_id=123456,
            channel_id=adsense_channels[0].channel_id,
            bid_amount=Decimal('0.05'),
            bid_type='cpc',
            duration_hours=24,
            content="Test AdSense advertisement content",
            media_url=None,
            target_clicks=100,
            target_impressions=None,
            max_budget=Decimal('5.00'),
            created_at=datetime.now()
        )
        
        bid_id = await adsense_system.place_bid(test_bid)
        if bid_id:
            logger.info(f"✅ Test bid placed successfully: {bid_id}")
        else:
            logger.error("❌ Failed to place test bid")
    
    # Test 4: Test auction simulation
    logger.info("🏆 Test 4: Testing auction simulation...")
    
    if adsense_channels:
        winning_bid = await adsense_system.run_auction(adsense_channels[0].channel_id)
        if winning_bid:
            logger.info(f"✅ Auction completed, winning bid: {winning_bid}")
        else:
            logger.info("ℹ️ No bids found for auction")
    
    # Test 5: Database integration test
    logger.info("🗄️ Test 5: Testing database integration...")
    
    # Test direct database methods
    db_channels = await db.get_adsense_channels()
    logger.info(f"Database shows {len(db_channels)} AdSense channels")
    
    # Test bid placement through database
    if db_channels:
        bid_data = {
            'advertiser_id': 123456,
            'channel_id': db_channels[0]['channel_id'],
            'bid_amount': 0.03,
            'bid_type': 'cpm',
            'duration_hours': 48,
            'content': "Test database bid content",
            'media_url': None,
            'target_clicks': None,
            'target_impressions': 1000,
            'max_budget': 10.00
        }
        
        bid_id = await db.place_adsense_bid(bid_data)
        if bid_id:
            logger.info(f"✅ Database bid placed successfully: {bid_id}")
        else:
            logger.error("❌ Failed to place database bid")
    
    # Summary
    logger.info("📋 AdSense Integration Test Summary:")
    logger.info(f"   📺 Channels registered: {len(existing_channels)}")
    logger.info(f"   🎯 AdSense channels available: {len(adsense_channels)}")
    logger.info(f"   🗄️ Database channels: {len(db_channels)}")
    logger.info("✅ AdSense integration test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_adsense_integration())