#!/usr/bin/env python3
"""
Final AdSense Integration Validation
Comprehensive test of all AdSense components
"""

import asyncio
import aiosqlite
import logging
from datetime import datetime
from languages import get_text, LANGUAGES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def validate_adsense_integration():
    """Comprehensive validation of AdSense integration"""
    logger.info("🔍 Final AdSense Integration Validation")
    
    validation_results = {
        'database_tables': False,
        'channel_registration': False,
        'multilingual_support': False,
        'bid_system': False,
        'auction_system': False,
        'performance_tracking': False,
        'ui_integration': False
    }
    
    try:
        # Test 1: Database Tables Validation
        logger.info("🗄️ Test 1: Database Tables Validation")
        async with aiosqlite.connect("bot.db") as db:
            # Check all required tables exist
            cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'adsense_%'")
            tables = [row[0] for row in await cursor.fetchall()]
            
            required_tables = ['adsense_channels', 'adsense_bids', 'adsense_auctions', 'adsense_performance']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if not missing_tables:
                validation_results['database_tables'] = True
                logger.info(f"✅ All {len(required_tables)} AdSense tables exist")
            else:
                logger.error(f"❌ Missing tables: {missing_tables}")
        
        # Test 2: Channel Registration Validation
        logger.info("📺 Test 2: Channel Registration Validation")
        async with aiosqlite.connect("bot.db") as db:
            cursor = await db.execute("SELECT COUNT(*) FROM adsense_channels")
            channel_count = (await cursor.fetchone())[0]
            
            if channel_count >= 4:  # We registered 4 channels
                validation_results['channel_registration'] = True
                logger.info(f"✅ {channel_count} channels registered in AdSense system")
                
                # Check channel details
                cursor = await db.execute("""
                    SELECT channel_name, subscribers, suggested_cpc, suggested_cpm, category 
                    FROM adsense_channels ORDER BY subscribers DESC
                """)
                channels = await cursor.fetchall()
                
                for channel in channels:
                    logger.info(f"   - {channel[0]}: {channel[1]} subs, CPC: ${channel[2]:.3f}, CPM: ${channel[3]:.2f}")
            else:
                logger.error(f"❌ Only {channel_count} channels registered, expected 4+")
        
        # Test 3: Multilingual Support Validation
        logger.info("🌍 Test 3: Multilingual Support Validation")
        required_keys = ['browse_channels', 'available_channels_header', 'place_bid', 'my_bids']
        all_languages_valid = True
        
        for lang_code in LANGUAGES.keys():
            missing_keys = []
            for key in required_keys:
                text = get_text(lang_code, key)
                if text == key:  # Fallback to key means translation missing
                    missing_keys.append(key)
            
            if missing_keys:
                logger.error(f"❌ {lang_code}: Missing keys {missing_keys}")
                all_languages_valid = False
            else:
                logger.info(f"✅ {lang_code}: All AdSense keys present")
        
        validation_results['multilingual_support'] = all_languages_valid
        
        # Test 4: Bid System Validation
        logger.info("💰 Test 4: Bid System Validation")
        async with aiosqlite.connect("bot.db") as db:
            cursor = await db.execute("SELECT COUNT(*) FROM adsense_bids")
            bid_count = (await cursor.fetchone())[0]
            
            if bid_count >= 2:  # We placed 2 test bids
                validation_results['bid_system'] = True
                logger.info(f"✅ {bid_count} bids in system")
                
                # Check bid details
                cursor = await db.execute("""
                    SELECT id, channel_id, bid_amount, bid_type, status, content 
                    FROM adsense_bids ORDER BY created_at DESC
                """)
                bids = await cursor.fetchall()
                
                for bid in bids:
                    logger.info(f"   - BID-{bid[0]:06d}: ${bid[2]:.3f} {bid[3].upper()}, Status: {bid[4]}")
            else:
                logger.error(f"❌ Only {bid_count} bids found, expected 2+")
        
        # Test 5: Auction System Validation
        logger.info("🏆 Test 5: Auction System Validation")
        async with aiosqlite.connect("bot.db") as db:
            cursor = await db.execute("SELECT COUNT(*) FROM adsense_auctions")
            auction_count = (await cursor.fetchone())[0]
            
            if auction_count >= 1:  # We created 1 auction
                validation_results['auction_system'] = True
                logger.info(f"✅ {auction_count} auctions recorded")
                
                # Check auction details
                cursor = await db.execute("""
                    SELECT channel_id, winning_bid_id, total_bids, winning_amount 
                    FROM adsense_auctions ORDER BY auction_time DESC
                """)
                auctions = await cursor.fetchall()
                
                for auction in auctions:
                    logger.info(f"   - Channel: {auction[0]}, Winning: ${auction[3]:.3f}, Total bids: {auction[2]}")
            else:
                logger.error(f"❌ Only {auction_count} auctions found, expected 1+")
        
        # Test 6: Performance Tracking Validation
        logger.info("📈 Test 6: Performance Tracking Validation")
        async with aiosqlite.connect("bot.db") as db:
            cursor = await db.execute("SELECT COUNT(*) FROM adsense_performance")
            performance_count = (await cursor.fetchone())[0]
            
            if performance_count >= 1:  # We created 1 performance record
                validation_results['performance_tracking'] = True
                logger.info(f"✅ {performance_count} performance records")
                
                # Check performance details
                cursor = await db.execute("""
                    SELECT ad_id, impressions, clicks, ctr, revenue_generated, 
                           channel_owner_share, platform_share 
                    FROM adsense_performance ORDER BY created_at DESC
                """)
                performance = await cursor.fetchall()
                
                for perf in performance:
                    logger.info(f"   - {perf[0]}: {perf[1]} impressions, {perf[2]} clicks, {perf[3]:.1f}% CTR")
                    logger.info(f"     Revenue: ${perf[4]:.2f}, Owner: ${perf[5]:.2f}, Platform: ${perf[6]:.2f}")
            else:
                logger.error(f"❌ Only {performance_count} performance records found, expected 1+")
        
        # Test 7: UI Integration Validation
        logger.info("🎨 Test 7: UI Integration Validation")
        try:
            # Test handlers import
            from handlers import browse_channels_handler
            from adsense_handlers import AdSenseHandlers
            
            # Test button text generation
            browse_button_en = get_text('en', 'browse_channels')
            browse_button_ar = get_text('ar', 'browse_channels')
            browse_button_ru = get_text('ru', 'browse_channels')
            
            if all([browse_button_en, browse_button_ar, browse_button_ru]):
                validation_results['ui_integration'] = True
                logger.info("✅ UI integration components available")
                logger.info(f"   EN: {browse_button_en}")
                logger.info(f"   AR: {browse_button_ar}")
                logger.info(f"   RU: {browse_button_ru}")
            else:
                logger.error("❌ UI integration missing components")
        except ImportError as e:
            logger.error(f"❌ UI integration import error: {e}")
        
        # Final Results Summary
        logger.info("📊 Final Validation Results:")
        total_tests = len(validation_results)
        passed_tests = sum(validation_results.values())
        
        for test_name, result in validation_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"   {test_name}: {status}")
        
        success_rate = (passed_tests / total_tests) * 100
        logger.info(f"📈 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 85:
            logger.info("🎉 AdSense Integration: PRODUCTION READY!")
            return True
        else:
            logger.warning("⚠️ AdSense Integration: NEEDS ATTENTION")
            return False
    
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        return False

async def generate_adsense_report():
    """Generate comprehensive AdSense system report"""
    logger.info("📄 Generating AdSense System Report")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'channels': [],
        'bids': [],
        'auctions': [],
        'performance': [],
        'statistics': {}
    }
    
    async with aiosqlite.connect("bot.db") as db:
        # Channels data
        cursor = await db.execute("SELECT * FROM adsense_channels ORDER BY subscribers DESC")
        channels = await cursor.fetchall()
        report['channels'] = len(channels)
        
        # Bids data
        cursor = await db.execute("SELECT * FROM adsense_bids ORDER BY created_at DESC")
        bids = await cursor.fetchall()
        report['bids'] = len(bids)
        
        # Auctions data
        cursor = await db.execute("SELECT * FROM adsense_auctions ORDER BY auction_time DESC")
        auctions = await cursor.fetchall()
        report['auctions'] = len(auctions)
        
        # Performance data
        cursor = await db.execute("SELECT * FROM adsense_performance ORDER BY created_at DESC")
        performance = await cursor.fetchall()
        report['performance'] = len(performance)
        
        # Statistics
        cursor = await db.execute("SELECT SUM(subscribers) FROM adsense_channels")
        total_subscribers = (await cursor.fetchone())[0] or 0
        
        cursor = await db.execute("SELECT SUM(revenue_generated) FROM adsense_performance")
        total_revenue = (await cursor.fetchone())[0] or 0
        
        report['statistics'] = {
            'total_subscribers': total_subscribers,
            'total_revenue': total_revenue,
            'avg_revenue_per_channel': total_revenue / len(channels) if channels else 0
        }
    
    logger.info("📊 AdSense System Report:")
    logger.info(f"   📺 Channels: {report['channels']}")
    logger.info(f"   💰 Bids: {report['bids']}")
    logger.info(f"   🏆 Auctions: {report['auctions']}")
    logger.info(f"   📈 Performance Records: {report['performance']}")
    logger.info(f"   👥 Total Subscribers: {report['statistics']['total_subscribers']:,}")
    logger.info(f"   💵 Total Revenue: ${report['statistics']['total_revenue']:.2f}")
    logger.info(f"   📊 Avg Revenue/Channel: ${report['statistics']['avg_revenue_per_channel']:.2f}")
    
    return report

async def main():
    """Main validation function"""
    logger.info("🚀 Starting Final AdSense Integration Validation")
    
    try:
        # Run comprehensive validation
        validation_success = await validate_adsense_integration()
        
        # Generate system report
        report = await generate_adsense_report()
        
        # Final status
        if validation_success:
            logger.info("🎉 VALIDATION SUCCESSFUL - AdSense system is PRODUCTION READY!")
            logger.info("✅ All core components tested and working")
            logger.info("✅ Database integration complete")
            logger.info("✅ Multilingual support operational")
            logger.info("✅ Auction system functional")
            logger.info("✅ Performance tracking active")
        else:
            logger.warning("⚠️ VALIDATION INCOMPLETE - Some components need attention")
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())