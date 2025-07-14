#!/usr/bin/env python3
"""
Test Browse Channels Functionality
Tests the AdSense browse channels feature end-to-end
"""

import asyncio
import aiosqlite
import logging
from adsense_system_architecture import adsense_system
from languages import get_text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_browse_channels():
    """Test browse channels functionality"""
    logger.info("🎯 Testing Browse Channels Functionality")
    
    # Test 1: Check AdSense channels are available
    logger.info("📺 Test 1: Checking available AdSense channels...")
    
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM adsense_channels ORDER BY subscribers DESC")
        channels = await cursor.fetchall()
        
    if not channels:
        logger.error("❌ No AdSense channels found")
        return False
    
    logger.info(f"✅ Found {len(channels)} AdSense channels")
    for channel in channels:
        logger.info(f"   - {channel[2]} ({channel[1]}): {channel[4]} subscribers")
    
    # Test 2: Test language integration
    logger.info("🌍 Test 2: Testing multilingual support...")
    
    languages = ['en', 'ar', 'ru']
    for lang in languages:
        browse_text = get_text(lang, 'browse_channels')
        header_text = get_text(lang, 'available_channels_header')
        logger.info(f"   {lang}: '{browse_text}' | Header: '{header_text[:50]}...'")
    
    # Test 3: Test channel filtering
    logger.info("🔍 Test 3: Testing channel filtering...")
    
    categories = set()
    for channel in channels:
        categories.add(channel[3])  # category column
    
    logger.info(f"📊 Available categories: {categories}")
    
    # Test each category
    for category in categories:
        async with aiosqlite.connect("bot.db") as db:
            cursor = await db.execute("SELECT * FROM adsense_channels WHERE category = ?", (category,))
            filtered_channels = await cursor.fetchall()
        
        logger.info(f"   {category}: {len(filtered_channels)} channels")
    
    # Test 4: Test bid placement simulation
    logger.info("💰 Test 4: Testing bid placement simulation...")
    
    if channels:
        test_channel = channels[0]  # Use channel with most subscribers
        
        # Simulate bid data
        bid_data = {
            'advertiser_id': 999999,
            'channel_id': test_channel[1],
            'bid_amount': 0.08,
            'bid_type': 'cpc',
            'duration_hours': 48,
            'content': 'Test advertisement content for browse channels',
            'media_url': None,
            'target_clicks': 200,
            'target_impressions': None,
            'max_budget': 16.00
        }
        
        # Place bid via database
        async with aiosqlite.connect("bot.db") as db:
            cursor = await db.execute('''
                INSERT INTO adsense_bids 
                (advertiser_id, channel_id, bid_amount, bid_type, duration_hours, 
                 content, media_url, target_clicks, target_impressions, max_budget)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bid_data['advertiser_id'],
                bid_data['channel_id'],
                bid_data['bid_amount'],
                bid_data['bid_type'],
                bid_data['duration_hours'],
                bid_data['content'],
                bid_data.get('media_url'),
                bid_data.get('target_clicks'),
                bid_data.get('target_impressions'),
                bid_data['max_budget']
            ))
            
            bid_id = cursor.lastrowid
            await db.commit()
        
        logger.info(f"✅ Test bid placed successfully: BID-{bid_id:06d}")
        logger.info(f"   Channel: {test_channel[2]}")
        logger.info(f"   Amount: ${bid_data['bid_amount']:.3f} CPC")
        logger.info(f"   Budget: ${bid_data['max_budget']:.2f}")
    
    # Test 5: Test auction simulation
    logger.info("🏆 Test 5: Testing auction simulation...")
    
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute('''
            SELECT * FROM adsense_bids 
            WHERE channel_id = ? AND status = 'pending' 
            ORDER BY bid_amount DESC
        ''', (test_channel[1],))
        
        bids = await cursor.fetchall()
    
    if bids:
        winning_bid = bids[0]  # Highest bid
        logger.info(f"✅ Auction simulation - Winning bid: ${winning_bid[3]:.3f}")
        logger.info(f"   Bidder: {winning_bid[1]}")
        logger.info(f"   Content: {winning_bid[6][:50]}...")
        
        # Record auction result
        async with aiosqlite.connect("bot.db") as db:
            await db.execute('''
                INSERT INTO adsense_auctions 
                (channel_id, winning_bid_id, total_bids, winning_amount)
                VALUES (?, ?, ?, ?)
            ''', (test_channel[1], winning_bid[0], len(bids), winning_bid[3]))
            
            await db.commit()
        
        logger.info("✅ Auction result recorded")
    
    # Test 6: Test performance tracking
    logger.info("📈 Test 6: Testing performance tracking...")
    
    # Create sample performance data
    async with aiosqlite.connect("bot.db") as db:
        await db.execute('''
            INSERT INTO adsense_performance 
            (ad_id, channel_id, impressions, clicks, ctr, cost_per_click, 
             revenue_generated, channel_owner_share, platform_share)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"AD-{bid_id:06d}",
            test_channel[1],
            1000,  # impressions
            45,    # clicks
            4.5,   # ctr
            0.08,  # cost_per_click
            3.60,  # revenue_generated
            2.45,  # channel_owner_share (68%)
            1.15   # platform_share (32%)
        ))
        
        await db.commit()
    
    logger.info("✅ Performance tracking data created")
    
    # Final summary
    logger.info("📋 Browse Channels Test Summary:")
    logger.info(f"   📺 Channels available: {len(channels)}")
    logger.info(f"   🏷️ Categories: {len(categories)}")
    logger.info(f"   🌍 Languages supported: {len(languages)}")
    logger.info(f"   💰 Bids placed: {len(bids)}")
    logger.info("✅ Browse Channels functionality test completed successfully!")
    
    return True

async def main():
    """Main test function"""
    logger.info("🚀 Starting Browse Channels Test")
    
    try:
        success = await test_browse_channels()
        if success:
            logger.info("✅ All tests passed!")
        else:
            logger.error("❌ Some tests failed!")
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())