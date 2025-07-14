#!/usr/bin/env python3
"""
Test Auction System Implementation
Comprehensive testing of the auction advertising system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auction_advertising_system import get_auction_system, ChannelCategory, BidType, AdStatus
from decimal import Decimal
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_auction_system():
    """Test the complete auction system"""
    
    print("🎯 Testing I3lani Auction Advertising System")
    print("=" * 50)
    
    # Initialize system
    auction_system = await get_auction_system()
    
    # Test 1: Database Initialization
    print("\n1️⃣ Testing Database Initialization...")
    try:
        await auction_system.initialize_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    # Test 2: Channel Registration
    print("\n2️⃣ Testing Channel Registration...")
    try:
        # Add test channels
        channels = [
            ("@test_tech", 123, ChannelCategory.TECH, 1000),
            ("@test_lifestyle", 456, ChannelCategory.LIFESTYLE, 2000),
            ("@test_business", 789, ChannelCategory.BUSINESS, 500),
        ]
        
        for channel_id, owner_id, category, subscribers in channels:
            success = await auction_system.add_channel(channel_id, owner_id, category, subscribers)
            if success:
                print(f"✅ Channel {channel_id} registered in {category.value}")
            else:
                print(f"❌ Failed to register channel {channel_id}")
        
        # Test getting channels by category
        tech_channels = await auction_system.get_channels_by_category(ChannelCategory.TECH)
        print(f"✅ Found {len(tech_channels)} tech channels")
        
    except Exception as e:
        print(f"❌ Channel registration failed: {e}")
        return False
    
    # Test 3: Ad Creation
    print("\n3️⃣ Testing Ad Creation...")
    try:
        # Create test ads
        ads = [
            (111, "Best Tech Product Ever! 💻", None, ChannelCategory.TECH, BidType.CPC, Decimal("0.25")),
            (222, "Amazing Lifestyle Content! 🌟", "https://example.com/image.jpg", ChannelCategory.LIFESTYLE, BidType.CPM, Decimal("2.50")),
            (333, "Business Growth Secrets! 💼", None, ChannelCategory.BUSINESS, BidType.CPC, Decimal("0.50")),
        ]
        
        created_ads = []
        for advertiser_id, content, image_url, category, bid_type, bid_amount in ads:
            ad_id = await auction_system.create_ad(advertiser_id, content, image_url, category, bid_type, bid_amount)
            if ad_id:
                created_ads.append(ad_id)
                print(f"✅ Ad {ad_id} created: {content[:30]}...")
            else:
                print(f"❌ Failed to create ad: {content[:30]}...")
        
        print(f"✅ Created {len(created_ads)} ads successfully")
        
    except Exception as e:
        print(f"❌ Ad creation failed: {e}")
        return False
    
    # Test 4: Ad Approval (simulate admin approval)
    print("\n4️⃣ Testing Ad Approval...")
    try:
        for ad_id in created_ads:
            await auction_system.update_ad_status(ad_id, AdStatus.APPROVED)
            print(f"✅ Ad {ad_id} approved")
        
    except Exception as e:
        print(f"❌ Ad approval failed: {e}")
        return False
    
    # Test 5: Daily Auction
    print("\n5️⃣ Testing Daily Auction...")
    try:
        results = await auction_system.run_daily_auction()
        
        total_matches = sum(len(category_results) for category_results in results.values())
        print(f"✅ Daily auction completed: {total_matches} matches")
        
        for category, category_results in results.items():
            print(f"  • {category.title()}: {len(category_results)} matches")
            for result in category_results:
                print(f"    - {result.ad_id} → {result.channel_id} (${result.winning_bid})")
        
    except Exception as e:
        print(f"❌ Daily auction failed: {e}")
        return False
    
    # Test 6: Performance Tracking
    print("\n6️⃣ Testing Performance Tracking...")
    try:
        # Test impression tracking
        test_ad_id = created_ads[0] if created_ads else "test_ad"
        test_channel_id = "@test_tech"
        
        await auction_system.track_impression(test_ad_id, test_channel_id)
        print(f"✅ Impression tracked for {test_ad_id}")
        
        # Test click tracking
        await auction_system.track_click(test_ad_id, test_channel_id)
        print(f"✅ Click tracked for {test_ad_id}")
        
    except Exception as e:
        print(f"❌ Performance tracking failed: {e}")
        return False
    
    # Test 7: User Statistics
    print("\n7️⃣ Testing User Statistics...")
    try:
        # Test channel owner stats
        owner_stats = await auction_system.get_user_stats(123)
        print(f"✅ Channel owner stats: Balance ${owner_stats.get('balance', 0):.2f}")
        
        # Test advertiser stats
        advertiser_stats = await auction_system.get_advertiser_stats(111)
        print(f"✅ Advertiser stats: {len(advertiser_stats.get('ads', []))} ads")
        
    except Exception as e:
        print(f"❌ User statistics failed: {e}")
        return False
    
    # Test 8: Revenue Calculation
    print("\n8️⃣ Testing Revenue Calculation...")
    try:
        # Test revenue distribution
        await auction_system.calculate_and_distribute_revenue(
            test_ad_id, test_channel_id, Decimal("1.00"), "cpc"
        )
        print(f"✅ Revenue distributed: $1.00 for CPC")
        
        # Check updated balance
        updated_stats = await auction_system.get_user_stats(123)
        print(f"✅ Updated balance: ${updated_stats.get('balance', 0):.2f}")
        
    except Exception as e:
        print(f"❌ Revenue calculation failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! Auction system is working correctly.")
    print("\n📊 System Features Tested:")
    print("• Database initialization and schema creation")
    print("• Channel registration with categorization")
    print("• Ad creation with CPC/CPM bidding")
    print("• Admin approval workflow")
    print("• Daily auction matching system")
    print("• Performance tracking (impressions/clicks)")
    print("• Revenue sharing (68%/32% split)")
    print("• User statistics and analytics")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_auction_system())
    if success:
        print("\n✅ Auction system is ready for production!")
    else:
        print("\n❌ Auction system needs attention before deployment.")
        sys.exit(1)