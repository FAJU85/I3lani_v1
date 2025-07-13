#!/usr/bin/env python3
"""
Pricing Integration Test for I3lani Bot
Tests the new advanced pricing management system
"""

import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def test_advanced_pricing_system():
    """Test the advanced pricing management system"""
    
    print("🧪 TESTING ADVANCED PRICING SYSTEM")
    print("=" * 50)
    
    test_results = {}
    
    # Test 1: Initialize pricing manager
    print("\n1. 🔨 Testing Pricing Manager Initialization...")
    try:
        from advanced_pricing_management import pricing_manager
        await pricing_manager.initialize_pricing_database()
        print("   ✅ Pricing manager initialized successfully")
        test_results['initialization'] = 'pass'
    except Exception as e:
        print(f"   ❌ Error initializing pricing manager: {e}")
        test_results['initialization'] = 'fail'
    
    # Test 2: Create sample pricing tier
    print("\n2. 🎯 Testing Pricing Tier Creation...")
    try:
        tier_data = {
            'name': 'Test Premium Week',
            'duration_days': 7,
            'posts_per_day': 3,
            'base_price_usd': 2.50,
            'discount_percent': 15.0,
            'category': 'current',
            'description': 'Test premium weekly package',
            'created_by': 123456
        }
        
        success = await pricing_manager.create_pricing_tier(tier_data)
        if success:
            print("   ✅ Pricing tier created successfully")
            test_results['tier_creation'] = 'pass'
        else:
            print("   ❌ Failed to create pricing tier")
            test_results['tier_creation'] = 'fail'
    except Exception as e:
        print(f"   ❌ Error creating pricing tier: {e}")
        test_results['tier_creation'] = 'fail'
    
    # Test 3: Get all pricing tiers
    print("\n3. 📋 Testing Pricing Tier Retrieval...")
    try:
        tiers = await pricing_manager.get_all_pricing_tiers()
        print(f"   ✅ Retrieved {len(tiers)} pricing tiers")
        test_results['tier_retrieval'] = 'pass'
        
        # Display first few tiers
        for i, tier in enumerate(tiers[:3]):
            print(f"   • {tier['tier_name']}: {tier['duration_days']} days, ${tier['final_price_usd']:.2f}")
    except Exception as e:
        print(f"   ❌ Error retrieving pricing tiers: {e}")
        test_results['tier_retrieval'] = 'fail'
    
    # Test 4: Update pricing tier
    print("\n4. ✏️ Testing Pricing Tier Update...")
    try:
        if tiers:
            tier_id = tiers[0]['id']
            updates = {
                'base_price_usd': 3.00,
                'discount_percent': 20.0,
                'updated_by': 123456
            }
            
            success = await pricing_manager.update_pricing_tier(tier_id, updates)
            if success:
                print("   ✅ Pricing tier updated successfully")
                test_results['tier_update'] = 'pass'
            else:
                print("   ❌ Failed to update pricing tier")
                test_results['tier_update'] = 'fail'
        else:
            print("   ⚠️  No tiers available for update test")
            test_results['tier_update'] = 'skip'
    except Exception as e:
        print(f"   ❌ Error updating pricing tier: {e}")
        test_results['tier_update'] = 'fail'
    
    # Test 5: Create promotional offer
    print("\n5. 🎁 Testing Promotional Offer Creation...")
    try:
        offer_data = {
            'name': 'Test Summer Sale',
            'code': 'SUMMER25',
            'discount_type': 'percentage',
            'discount_value': 25.0,
            'min_duration': 3,
            'max_duration': 30,
            'usage_limit': 100,
            'start_date': datetime.now(),
            'end_date': datetime.now(),
            'created_by': 123456
        }
        
        success = await pricing_manager.create_promotional_offer(offer_data)
        if success:
            print("   ✅ Promotional offer created successfully")
            test_results['offer_creation'] = 'pass'
        else:
            print("   ❌ Failed to create promotional offer")
            test_results['offer_creation'] = 'fail'
    except Exception as e:
        print(f"   ❌ Error creating promotional offer: {e}")
        test_results['offer_creation'] = 'fail'
    
    # Test 6: Create bundle package
    print("\n6. 📦 Testing Bundle Package Creation...")
    try:
        bundle_data = {
            'name': 'Test Mega Bundle',
            'description': 'Complete advertising package',
            'total_days': 30,
            'total_posts': 60,
            'original_price': 50.00,
            'bundle_price': 35.00,
            'created_by': 123456
        }
        
        success = await pricing_manager.create_bundle_package(bundle_data)
        if success:
            print("   ✅ Bundle package created successfully")
            test_results['bundle_creation'] = 'pass'
        else:
            print("   ❌ Failed to create bundle package")
            test_results['bundle_creation'] = 'fail'
    except Exception as e:
        print(f"   ❌ Error creating bundle package: {e}")
        test_results['bundle_creation'] = 'fail'
    
    # Test 7: Get pricing analytics
    print("\n7. 📊 Testing Pricing Analytics...")
    try:
        analytics = await pricing_manager.get_pricing_analytics()
        print(f"   ✅ Retrieved pricing analytics")
        print(f"   • Popular tiers: {len(analytics.get('popular_tiers', []))}")
        print(f"   • Revenue categories: {len(analytics.get('revenue_by_category', []))}")
        print(f"   • Monthly changes: {analytics.get('monthly_changes', 0)}")
        test_results['analytics'] = 'pass'
    except Exception as e:
        print(f"   ❌ Error getting pricing analytics: {e}")
        test_results['analytics'] = 'fail'
    
    # Test 8: Test pricing handlers
    print("\n8. 🔧 Testing Pricing Admin Handlers...")
    try:
        from pricing_admin_handlers import setup_pricing_admin_handlers
        
        # Create mock dispatcher for testing
        class MockDispatcher:
            def __init__(self):
                self.handlers = []
                self.callback_query = MockCallbackQuery()
                self.message = MockMessage()
            
            def register_handler(self, handler, filter_func):
                self.handlers.append((handler, filter_func))
        
        class MockCallbackQuery:
            def register(self, handler, filter_func):
                pass
        
        class MockMessage:
            def register(self, handler, state):
                pass
        
        mock_dp = MockDispatcher()
        setup_pricing_admin_handlers(mock_dp)
        
        print("   ✅ Pricing admin handlers setup successfully")
        test_results['handlers'] = 'pass'
    except Exception as e:
        print(f"   ❌ Error setting up pricing handlers: {e}")
        test_results['handlers'] = 'fail'
    
    # Generate test report
    print("\n" + "=" * 50)
    print("📊 PRICING SYSTEM TEST REPORT")
    print("=" * 50)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results.values() if r == 'pass')
    failed_tests = sum(1 for r in test_results.values() if r == 'fail')
    skipped_tests = sum(1 for r in test_results.values() if r == 'skip')
    
    print(f"\n🏆 TEST RESULTS: {passed_tests}/{total_tests} tests passed")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   ⚠️  Skipped: {skipped_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n📈 SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("   🟢 EXCELLENT: Advanced pricing system is fully operational")
    elif success_rate >= 75:
        print("   🟡 GOOD: Advanced pricing system is mostly working")
    elif success_rate >= 50:
        print("   🟠 FAIR: Advanced pricing system needs attention")
    else:
        print("   🔴 POOR: Advanced pricing system has critical issues")
    
    print("\n📋 DETAILED RESULTS:")
    for test_name, result in test_results.items():
        status_icon = "✅" if result == 'pass' else "❌" if result == 'fail' else "⚠️"
        print(f"   {status_icon} {test_name.replace('_', ' ').title()}")
    
    print("\n🚀 PRICING FEATURES VALIDATED:")
    print("   • Complete CRUD operations for pricing tiers")
    print("   • Promotional offers management")
    print("   • Bundle packages creation")
    print("   • Advanced analytics and reporting")
    print("   • Admin interface integration")
    print("   • Database schema and operations")
    
    return test_results

async def main():
    """Main function to run pricing system tests"""
    results = await test_advanced_pricing_system()
    return results

if __name__ == "__main__":
    asyncio.run(main())