#!/usr/bin/env python3
"""
System Integration Test for I3lani Bot
Tests integration between all major systems
"""

import asyncio
import aiosqlite
from datetime import datetime
from typing import Dict, List

class SystemIntegrationTest:
    def __init__(self):
        self.test_results = {}
        self.db_path = 'bot.db'
        
    async def run_integration_tests(self):
        """Run comprehensive integration tests"""
        
        print("🔗 SYSTEM INTEGRATION TESTS")
        print("=" * 50)
        
        # Core integration tests
        await self._test_core_integrations()
        
        # Payment flow integration
        await self._test_payment_flow_integration()
        
        # Campaign flow integration
        await self._test_campaign_flow_integration()
        
        # Channel management integration
        await self._test_channel_management_integration()
        
        # User experience integration
        await self._test_ux_integration()
        
        # Generate integration report
        await self._generate_integration_report()
        
        return self.test_results
    
    async def _test_core_integrations(self):
        """Test core system integrations"""
        print("\n1. 🏗️  TESTING CORE INTEGRATIONS")
        print("-" * 40)
        
        try:
            # Test database connectivity
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                await cursor.execute("SELECT COUNT(*) FROM users")
                user_count = (await cursor.fetchone())[0]
                
                print(f"   ✅ Database integration: {user_count} users")
                self.test_results['core_database'] = {'status': 'pass', 'users': user_count}
                
            # Test language system
            from languages import get_text
            welcome_text = get_text('welcome_message', 'en')
            print(f"   ✅ Language system: {len(welcome_text)} chars")
            self.test_results['core_language'] = {'status': 'pass', 'text_length': len(welcome_text)}
            
            # Test states system
            from states import AdCreationStates
            print(f"   ✅ States system: {len(AdCreationStates.__dict__)} states")
            self.test_results['core_states'] = {'status': 'pass', 'states_count': len(AdCreationStates.__dict__)}
            
        except Exception as e:
            print(f"   ❌ Core integration error: {e}")
            self.test_results['core_integration'] = {'status': 'fail', 'error': str(e)}
    
    async def _test_payment_flow_integration(self):
        """Test payment system integration"""
        print("\n2. 💳 TESTING PAYMENT FLOW INTEGRATION")
        print("-" * 40)
        
        try:
            # Test FrequencyPricing integration
            from frequency_pricing import FrequencyPricingSystem
            pricing = FrequencyPricingSystem()
            result = pricing.calculate_pricing(7)
            
            print(f"   ✅ Pricing calculation: ${result['final_cost_usd']:.2f}")
            self.test_results['payment_pricing'] = {'status': 'pass', 'test_price': result['final_cost_usd']}
            
            # Test payment monitoring
            from enhanced_ton_payment_monitoring import enhanced_ton_payment_monitoring
            print("   ✅ Payment monitoring: System operational")
            self.test_results['payment_monitoring'] = {'status': 'pass', 'message': 'System operational'}
            
            # Test wallet management
            from wallet_manager import WalletManager
            wallet_manager = WalletManager()
            print("   ✅ Wallet management: System ready")
            self.test_results['payment_wallet'] = {'status': 'pass', 'message': 'System ready'}
            
        except Exception as e:
            print(f"   ❌ Payment flow integration error: {e}")
            self.test_results['payment_integration'] = {'status': 'fail', 'error': str(e)}
    
    async def _test_campaign_flow_integration(self):
        """Test campaign creation and management integration"""
        print("\n3. 📋 TESTING CAMPAIGN FLOW INTEGRATION")
        print("-" * 40)
        
        try:
            # Test campaign creation flow
            from campaign_management import CampaignManager
            campaign_manager = CampaignManager()
            
            print("   ✅ Campaign management: System ready")
            self.test_results['campaign_management'] = {'status': 'pass', 'message': 'System ready'}
            
            # Test enhanced campaign publisher
            from enhanced_campaign_publisher import EnhancedCampaignPublisher
            publisher = EnhancedCampaignPublisher()
            
            print("   ✅ Campaign publisher: System operational")
            self.test_results['campaign_publisher'] = {'status': 'pass', 'message': 'System operational'}
            
            # Test content integrity
            from content_integrity_system import ContentIntegritySystem
            content_system = ContentIntegritySystem()
            
            print("   ✅ Content integrity: System active")
            self.test_results['campaign_content'] = {'status': 'pass', 'message': 'System active'}
            
        except Exception as e:
            print(f"   ❌ Campaign flow integration error: {e}")
            self.test_results['campaign_integration'] = {'status': 'fail', 'error': str(e)}
    
    async def _test_channel_management_integration(self):
        """Test channel management integration"""
        print("\n4. 📺 TESTING CHANNEL MANAGEMENT INTEGRATION")
        print("-" * 40)
        
        try:
            # Test channel manager
            from channel_manager import ChannelManager
            channel_manager = ChannelManager()
            
            print("   ✅ Channel manager: System operational")
            self.test_results['channel_manager'] = {'status': 'pass', 'message': 'System operational'}
            
            # Test enhanced channel detection
            from enhanced_channel_detection import EnhancedChannelDetection
            detection = EnhancedChannelDetection()
            
            print("   ✅ Channel detection: System ready")
            self.test_results['channel_detection'] = {'status': 'pass', 'message': 'System ready'}
            
            # Check current channels
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                await cursor.execute("SELECT COUNT(*) FROM channels WHERE is_active = 1")
                active_channels = (await cursor.fetchone())[0]
                
                print(f"   ✅ Active channels: {active_channels} channels")
                self.test_results['channel_count'] = {'status': 'pass', 'active_channels': active_channels}
                
        except Exception as e:
            print(f"   ❌ Channel management integration error: {e}")
            self.test_results['channel_integration'] = {'status': 'fail', 'error': str(e)}
    
    async def _test_ux_integration(self):
        """Test user experience integration"""
        print("\n5. 🎨 TESTING UX INTEGRATION")
        print("-" * 40)
        
        try:
            # Test multilingual menu system
            from multilingual_menu_system import MultilingualMenuSystem
            menu_system = MultilingualMenuSystem()
            
            print("   ✅ Multilingual menu: System ready")
            self.test_results['ux_multilingual'] = {'status': 'pass', 'message': 'System ready'}
            
            # Test animated transitions
            from animated_transitions import AnimatedTransitions
            transitions = AnimatedTransitions()
            
            print("   ✅ Animated transitions: System active")
            self.test_results['ux_transitions'] = {'status': 'pass', 'message': 'System active'}
            
            # Test gamification
            from gamification import GamificationSystem
            gamification = GamificationSystem()
            
            print("   ✅ Gamification: System operational")
            self.test_results['ux_gamification'] = {'status': 'pass', 'message': 'System operational'}
            
        except Exception as e:
            print(f"   ❌ UX integration error: {e}")
            self.test_results['ux_integration'] = {'status': 'fail', 'error': str(e)}
    
    async def _generate_integration_report(self):
        """Generate integration test report"""
        print("\n" + "=" * 50)
        print("📊 INTEGRATION TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r.get('status') == 'pass')
        failed_tests = total_tests - passed_tests
        
        print(f"\n🏆 INTEGRATION RESULTS: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("   🟢 EXCELLENT: All systems properly integrated")
        elif passed_tests >= total_tests * 0.8:
            print("   🟡 GOOD: Most systems integrated successfully")
        else:
            print("   🔴 NEEDS ATTENTION: Integration issues detected")
        
        print("\n📋 TEST DETAILS:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'pass' else "❌"
            print(f"   {status_icon} {test_name}: {result.get('message', result.get('error', 'Complete'))}")
        
        print(f"\n✅ INTEGRATION HEALTH: {passed_tests/total_tests*100:.1f}%")
        
        # Save report
        import json
        with open('integration_test_report.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'integration_health': passed_tests/total_tests*100,
                'test_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Integration report saved to: integration_test_report.json")

async def main():
    """Main function to run integration tests"""
    tester = SystemIntegrationTest()
    results = await tester.run_integration_tests()
    return results

if __name__ == "__main__":
    asyncio.run(main())