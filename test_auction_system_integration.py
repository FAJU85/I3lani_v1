"""
Comprehensive test suite for auction system integration
Tests all components of the auction-based advertising system
"""

import asyncio
import aiosqlite
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuctionSystemIntegrationTest:
    """Test suite for auction system integration"""
    
    def __init__(self):
        self.db_path = "bot.db"
        self.test_results = []
    
    async def run_all_tests(self):
        """Run all auction system integration tests"""
        logger.info("🧪 Starting comprehensive auction system integration tests...")
        
        tests = [
            ("Database Schema Validation", self.test_database_schema),
            ("Auction System Initialization", self.test_auction_system_initialization),
            ("Advertiser Ad Creation", self.test_advertiser_ad_creation),
            ("Channel Registration", self.test_channel_registration),
            ("Daily Auction Process", self.test_daily_auction_process),
            ("Performance Tracking", self.test_performance_tracking),
            ("Revenue Sharing", self.test_revenue_sharing),
            ("Withdrawal System", self.test_withdrawal_system),
            ("Admin Panel Integration", self.test_admin_panel_integration),
            ("Handler Registration", self.test_handler_registration)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🔍 Running test: {test_name}")
                result = await test_func()
                
                if result:
                    logger.info(f"✅ PASSED: {test_name}")
                    passed += 1
                else:
                    logger.error(f"❌ FAILED: {test_name}")
                    failed += 1
                    
                self.test_results.append({
                    'test': test_name,
                    'passed': result,
                    'timestamp': datetime.now()
                })
                
            except Exception as e:
                logger.error(f"❌ ERROR in {test_name}: {e}")
                failed += 1
                self.test_results.append({
                    'test': test_name,
                    'passed': False,
                    'error': str(e),
                    'timestamp': datetime.now()
                })
        
        # Generate report
        success_rate = (passed / (passed + failed)) * 100
        logger.info(f"\n🎯 AUCTION SYSTEM INTEGRATION TEST REPORT")
        logger.info(f"Total Tests: {passed + failed}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80
    
    async def test_database_schema(self) -> bool:
        """Test that all auction-related database tables exist"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                tables_to_check = [
                    "auction_channels",
                    "auction_ads",
                    "daily_auctions",
                    "auction_bids",
                    "ad_performance",
                    "user_balances",
                    "withdrawal_requests",
                    "trackable_links"
                ]
                
                existing_tables = 0
                
                for table in tables_to_check:
                    cursor = await db.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    result = await cursor.fetchone()
                    
                    if result:
                        existing_tables += 1
                        logger.info(f"  ✅ Table {table} exists")
                    else:
                        logger.error(f"  ❌ Table {table} missing")
                
                return existing_tables == len(tables_to_check)
                
        except Exception as e:
            logger.error(f"Database schema test error: {e}")
            return False
    
    async def test_auction_system_initialization(self) -> bool:
        """Test that auction system can be initialized"""
        try:
            from auction_advertising_system import get_auction_system
            
            auction_system = get_auction_system()
            
            # Check system configuration
            if auction_system.min_cpc_bid != 0.10:
                logger.error(f"  ❌ Min CPC bid should be 0.10, got {auction_system.min_cpc_bid}")
                return False
            
            if auction_system.min_cpm_bid != 1.00:
                logger.error(f"  ❌ Min CPM bid should be 1.00, got {auction_system.min_cpm_bid}")
                return False
            
            if auction_system.revenue_split["channel_owner"] != 0.68:
                logger.error(f"  ❌ Channel owner share should be 0.68, got {auction_system.revenue_split['channel_owner']}")
                return False
            
            if auction_system.withdrawal_minimum != 50.00:
                logger.error(f"  ❌ Withdrawal minimum should be 50.00, got {auction_system.withdrawal_minimum}")
                return False
            
            logger.info("  ✅ Auction system configuration correct")
            return True
            
        except Exception as e:
            logger.error(f"Auction system initialization error: {e}")
            return False
    
    async def test_advertiser_ad_creation(self) -> bool:
        """Test advertiser ad creation functionality"""
        try:
            from auction_advertising_system import get_auction_system, BidType
            
            auction_system = get_auction_system()
            
            # Test CPC ad creation
            cpc_ad_id = await auction_system.create_auction_ad(
                advertiser_id=999999,
                content="Test CPC advertisement",
                image_url=None,
                category="tech",
                bid_type=BidType.CPC,
                bid_amount=0.15,
                daily_budget=10.00,
                target_audience="Tech enthusiasts",
                keywords=["technology", "innovation"]
            )
            
            if cpc_ad_id:
                logger.info(f"  ✅ CPC ad created with ID: {cpc_ad_id}")
            else:
                logger.error("  ❌ CPC ad creation failed")
                return False
            
            # Test CPM ad creation
            cpm_ad_id = await auction_system.create_auction_ad(
                advertiser_id=999999,
                content="Test CPM advertisement",
                image_url="test_image.jpg",
                category="lifestyle",
                bid_type=BidType.CPM,
                bid_amount=2.50,
                daily_budget=25.00,
                target_audience="Lifestyle enthusiasts",
                keywords=["lifestyle", "trends"]
            )
            
            if cpm_ad_id:
                logger.info(f"  ✅ CPM ad created with ID: {cpm_ad_id}")
            else:
                logger.error("  ❌ CPM ad creation failed")
                return False
            
            # Test minimum bid validation
            try:
                await auction_system.create_auction_ad(
                    advertiser_id=999999,
                    content="Test low bid",
                    image_url=None,
                    category="tech",
                    bid_type=BidType.CPC,
                    bid_amount=0.05,  # Below minimum
                    daily_budget=10.00
                )
                logger.error("  ❌ Should have rejected low CPC bid")
                return False
            except ValueError:
                logger.info("  ✅ Minimum bid validation working")
            
            return True
            
        except Exception as e:
            logger.error(f"Advertiser ad creation test error: {e}")
            return False
    
    async def test_channel_registration(self) -> bool:
        """Test channel registration functionality"""
        try:
            from auction_advertising_system import get_auction_system
            
            auction_system = get_auction_system()
            
            # Test channel registration
            success = await auction_system.register_channel(
                owner_id=888888,
                channel_id="test_channel_123",
                name="Test Channel",
                telegram_channel_id="@testchannel",
                category="tech",
                subscribers=1000
            )
            
            if success:
                logger.info("  ✅ Channel registration successful")
            else:
                logger.error("  ❌ Channel registration failed")
                return False
            
            # Verify channel in database
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT * FROM auction_channels WHERE channel_id = ?",
                    ("test_channel_123",)
                )
                result = await cursor.fetchone()
                
                if result:
                    logger.info("  ✅ Channel found in database")
                else:
                    logger.error("  ❌ Channel not found in database")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Channel registration test error: {e}")
            return False
    
    async def test_daily_auction_process(self) -> bool:
        """Test daily auction process"""
        try:
            from auction_advertising_system import get_auction_system
            
            auction_system = get_auction_system()
            
            # Run test auction
            results = await auction_system.run_daily_auction()
            
            if results and 'auction_date' in results:
                logger.info(f"  ✅ Auction ran successfully for {results['auction_date']}")
                logger.info(f"  📊 Total auctions: {results.get('total_auctions', 0)}")
                
                # Check if results were generated
                if results.get('total_auctions', 0) > 0:
                    logger.info("  ✅ Auction results generated")
                else:
                    logger.info("  ℹ️ No auction results (no matching ads/channels)")
                
                return True
            else:
                logger.error("  ❌ Auction process failed")
                return False
            
        except Exception as e:
            logger.error(f"Daily auction process test error: {e}")
            return False
    
    async def test_performance_tracking(self) -> bool:
        """Test performance tracking functionality"""
        try:
            from auction_advertising_system import get_auction_system
            
            auction_system = get_auction_system()
            
            # Test performance metrics update
            success = await auction_system.update_performance_metrics(
                ad_id=999999,
                channel_id="test_channel_123",
                impressions=1000,
                clicks=50
            )
            
            if success:
                logger.info("  ✅ Performance metrics updated")
            else:
                logger.error("  ❌ Performance metrics update failed")
                return False
            
            # Test trackable link creation
            trackable_link = await auction_system.create_trackable_link(
                ad_id=999999,
                channel_id="test_channel_123",
                original_url="https://example.com"
            )
            
            if trackable_link:
                logger.info(f"  ✅ Trackable link created: {trackable_link}")
            else:
                logger.error("  ❌ Trackable link creation failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Performance tracking test error: {e}")
            return False
    
    async def test_revenue_sharing(self) -> bool:
        """Test revenue sharing functionality"""
        try:
            from auction_advertising_system import get_auction_system
            
            auction_system = get_auction_system()
            
            # Test advertiser stats
            advertiser_stats = await auction_system.get_advertiser_stats(999999)
            
            if isinstance(advertiser_stats, dict):
                logger.info("  ✅ Advertiser stats retrieved")
                logger.info(f"    Total ads: {advertiser_stats.get('total_ads', 0)}")
                logger.info(f"    Total spent: ${advertiser_stats.get('total_spent', 0):.2f}")
            else:
                logger.error("  ❌ Advertiser stats retrieval failed")
                return False
            
            # Test channel owner stats
            channel_owner_stats = await auction_system.get_channel_owner_stats(888888)
            
            if isinstance(channel_owner_stats, dict):
                logger.info("  ✅ Channel owner stats retrieved")
                logger.info(f"    Balance: ${channel_owner_stats.get('balance', 0):.2f}")
                logger.info(f"    Total earned: ${channel_owner_stats.get('total_earned', 0):.2f}")
            else:
                logger.error("  ❌ Channel owner stats retrieval failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Revenue sharing test error: {e}")
            return False
    
    async def test_withdrawal_system(self) -> bool:
        """Test withdrawal system functionality"""
        try:
            from auction_advertising_system import get_auction_system
            
            auction_system = get_auction_system()
            
            # Test withdrawal request (should fail due to insufficient balance)
            success = await auction_system.request_withdrawal(
                user_id=888888,
                amount=100.00,
                payment_method="TON",
                payment_details="UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
            )
            
            # Should fail due to insufficient balance
            if not success:
                logger.info("  ✅ Withdrawal request correctly rejected (insufficient balance)")
            else:
                logger.error("  ❌ Withdrawal request should have been rejected")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Withdrawal system test error: {e}")
            return False
    
    async def test_admin_panel_integration(self) -> bool:
        """Test admin panel integration"""
        try:
            from auction_admin_handlers import AuctionAdminHandlers
            from database import Database
            
            db = Database()
            admin_handlers = AuctionAdminHandlers(db)
            
            # Test admin check
            is_admin = admin_handlers.is_admin(566158428)
            
            if is_admin:
                logger.info("  ✅ Admin check working")
            else:
                logger.error("  ❌ Admin check failed")
                return False
            
            # Test pending ads retrieval
            pending_ads = await admin_handlers.get_pending_ads()
            
            if isinstance(pending_ads, list):
                logger.info(f"  ✅ Pending ads retrieved: {len(pending_ads)} ads")
            else:
                logger.error("  ❌ Pending ads retrieval failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Admin panel integration test error: {e}")
            return False
    
    async def test_handler_registration(self) -> bool:
        """Test handler registration"""
        try:
            # Test that handlers can be imported
            from auction_handlers import AuctionHandlers
            from auction_admin_handlers import AuctionAdminHandlers
            from database import Database
            
            db = Database()
            
            # Test auction handlers initialization
            auction_handlers = AuctionHandlers(db)
            
            if hasattr(auction_handlers, 'create_auction_ad_command'):
                logger.info("  ✅ Auction handlers initialized")
            else:
                logger.error("  ❌ Auction handlers missing methods")
                return False
            
            # Test admin handlers initialization
            admin_handlers = AuctionAdminHandlers(db)
            
            if hasattr(admin_handlers, 'auction_admin_command'):
                logger.info("  ✅ Admin handlers initialized")
            else:
                logger.error("  ❌ Admin handlers missing methods")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Handler registration test error: {e}")
            return False
    
    def generate_detailed_report(self):
        """Generate detailed test report"""
        report = "\n" + "="*60 + "\n"
        report += "AUCTION SYSTEM INTEGRATION TEST REPORT\n"
        report += "="*60 + "\n\n"
        
        passed_tests = [r for r in self.test_results if r['passed']]
        failed_tests = [r for r in self.test_results if not r['passed']]
        
        report += f"Total Tests: {len(self.test_results)}\n"
        report += f"Passed: {len(passed_tests)}\n"
        report += f"Failed: {len(failed_tests)}\n"
        report += f"Success Rate: {(len(passed_tests) / len(self.test_results)) * 100:.1f}%\n\n"
        
        if passed_tests:
            report += "PASSED TESTS:\n"
            for test in passed_tests:
                report += f"  ✅ {test['test']}\n"
            report += "\n"
        
        if failed_tests:
            report += "FAILED TESTS:\n"
            for test in failed_tests:
                report += f"  ❌ {test['test']}\n"
                if 'error' in test:
                    report += f"     Error: {test['error']}\n"
            report += "\n"
        
        report += "SYSTEM STATUS:\n"
        if len(passed_tests) >= 8:
            report += "  🟢 AUCTION SYSTEM OPERATIONAL\n"
        elif len(passed_tests) >= 6:
            report += "  🟡 AUCTION SYSTEM PARTIALLY OPERATIONAL\n"
        else:
            report += "  🔴 AUCTION SYSTEM NEEDS ATTENTION\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report

async def main():
    """Run the comprehensive auction system test"""
    test_suite = AuctionSystemIntegrationTest()
    
    try:
        success = await test_suite.run_all_tests()
        
        # Generate detailed report
        report = test_suite.generate_detailed_report()
        print(report)
        
        # Save report to file
        with open("auction_system_test_report.txt", "w") as f:
            f.write(report)
        
        if success:
            print("🎉 AUCTION SYSTEM INTEGRATION TESTS PASSED!")
        else:
            print("⚠️ AUCTION SYSTEM INTEGRATION TESTS NEED ATTENTION")
        
        return success
        
    except Exception as e:
        print(f"❌ Test suite execution error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())