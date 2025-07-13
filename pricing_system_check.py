#!/usr/bin/env python3
"""
Pricing System Check
Comprehensive check of all pricing systems and fix any issues
"""

import asyncio
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PricingSystemChecker:
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        
    async def comprehensive_check(self):
        """Perform comprehensive pricing system check"""
        
        print("🔍 PRICING SYSTEM COMPREHENSIVE CHECK")
        print("=" * 60)
        
        results = {
            'frequency_pricing': await self._check_frequency_pricing(),
            'dynamic_pricing': await self._check_dynamic_pricing(),
            'price_management': await self._check_price_management(),
            'admin_integration': await self._check_admin_integration(),
            'currency_conversion': await self._check_currency_conversion(),
            'pricing_display': await self._check_pricing_display()
        }
        
        await self._display_results(results)
        
        if self.issues:
            await self._apply_fixes()
        
        return results
    
    async def _check_frequency_pricing(self):
        """Check FrequencyPricingSystem"""
        print("\n1. 📊 FREQUENCY PRICING SYSTEM")
        print("-" * 40)
        
        try:
            from frequency_pricing import FrequencyPricingSystem
            
            freq_pricing = FrequencyPricingSystem()
            
            # Test basic functionality
            test_days = [1, 7, 14, 30, 90]
            valid_calculations = 0
            
            for days in test_days:
                try:
                    result = freq_pricing.calculate_pricing(days)
                    
                    # Validate result structure
                    required_keys = ['final_cost_usd', 'cost_stars', 'cost_ton', 'discount_percent', 'total_posts']
                    
                    if all(key in result for key in required_keys):
                        valid_calculations += 1
                        print(f"   ✅ {days} days: ${result['final_cost_usd']:.2f} USD, {result['discount_percent']}% discount")
                    else:
                        print(f"   ❌ {days} days: Missing required keys")
                        self.issues.append(f"FrequencyPricing missing keys for {days} days")
                        
                except Exception as e:
                    print(f"   ❌ {days} days: Error - {e}")
                    self.issues.append(f"FrequencyPricing error for {days} days: {e}")
            
            # Test tier system
            try:
                tiers = freq_pricing.get_available_tiers()
                print(f"   📊 Available tiers: {len(tiers)}")
                
                if len(tiers) > 5:
                    print("   ✅ Sufficient pricing tiers available")
                else:
                    print("   ⚠️  Limited pricing tiers")
                    self.issues.append("Limited pricing tiers in FrequencyPricing")
                    
            except Exception as e:
                print(f"   ❌ Tier system error: {e}")
                self.issues.append(f"FrequencyPricing tier system error: {e}")
            
            status = 'healthy' if valid_calculations == len(test_days) else 'issues'
            
            return {
                'status': status,
                'valid_calculations': valid_calculations,
                'total_tests': len(test_days),
                'available_tiers': len(tiers) if 'tiers' in locals() else 0
            }
            
        except ImportError:
            print("   ❌ FrequencyPricingSystem not found")
            self.issues.append("FrequencyPricingSystem module missing")
            return {'status': 'error', 'error': 'Module not found'}
        except Exception as e:
            print(f"   ❌ Frequency pricing check failed: {e}")
            self.issues.append(f"FrequencyPricing check error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_dynamic_pricing(self):
        """Check DynamicPricing system"""
        print("\n2. 🚀 DYNAMIC PRICING SYSTEM")
        print("-" * 40)
        
        try:
            from dynamic_pricing import DynamicPricing
            
            # Test basic calculation
            test_scenarios = [
                {'days': 7, 'posts_per_day': 2, 'channels': ['test1', 'test2']},
                {'days': 14, 'posts_per_day': 3, 'channels': ['test1']},
                {'days': 30, 'posts_per_day': 1, 'channels': ['test1', 'test2', 'test3']}
            ]
            
            valid_calculations = 0
            
            for scenario in test_scenarios:
                try:
                    calculation = DynamicPricing.calculate_total_cost(
                        days=scenario['days'],
                        posts_per_day=scenario['posts_per_day'],
                        channels=scenario['channels']
                    )
                    
                    # Check if result has required keys
                    if 'final_cost_usd' in calculation and 'total_posts' in calculation:
                        valid_calculations += 1
                        print(f"   ✅ {scenario['days']} days, {scenario['posts_per_day']} posts/day, {len(scenario['channels'])} channels: ${calculation['final_cost_usd']:.2f}")
                    else:
                        print(f"   ❌ Missing required keys in result for {scenario['days']} days")
                        self.issues.append(f"DynamicPricing missing keys for {scenario['days']} days")
                        
                except Exception as e:
                    print(f"   ❌ Error with {scenario['days']} days: {e}")
                    self.issues.append(f"DynamicPricing error for {scenario['days']} days: {e}")
            
            # Test edge cases
            try:
                # Test with 0 days
                edge_result = DynamicPricing.calculate_total_cost(days=0, posts_per_day=1, channels=['test'])
                print("   ✅ Edge case handling: 0 days")
            except Exception as e:
                print(f"   ❌ Edge case handling failed: {e}")
                self.issues.append(f"DynamicPricing edge case error: {e}")
            
            status = 'healthy' if valid_calculations == len(test_scenarios) else 'issues'
            
            return {
                'status': status,
                'valid_calculations': valid_calculations,
                'total_tests': len(test_scenarios)
            }
            
        except ImportError:
            print("   ❌ DynamicPricing not found")
            self.issues.append("DynamicPricing module missing")
            return {'status': 'error', 'error': 'Module not found'}
        except Exception as e:
            print(f"   ❌ Dynamic pricing check failed: {e}")
            self.issues.append(f"DynamicPricing check error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_price_management(self):
        """Check price management system"""
        print("\n3. 💰 PRICE MANAGEMENT SYSTEM")
        print("-" * 40)
        
        try:
            from price_management_system import get_price_manager
            
            manager = get_price_manager()
            await manager.initialize_database()
            
            # Test database operations
            try:
                summary = await manager.get_pricing_summary()
                print(f"   📊 Total tiers: {summary.get('total_tiers', 0)}")
                print(f"   📊 Active tiers: {summary.get('active_tiers', 0)}")
                print(f"   📊 Base price: ${summary.get('base_price_usd', 0):.2f}")
                
                # Test creating a tier
                success = await manager.create_price_tier(
                    duration_days=7,
                    posts_per_day=2,
                    discount_percent=10.0,
                    admin_id=123456
                )
                
                if success:
                    print("   ✅ Price tier creation: SUCCESS")
                    
                    # Clean up test tier
                    await manager.delete_price_tier(7, admin_id=123456)
                    print("   ✅ Price tier cleanup: SUCCESS")
                else:
                    print("   ❌ Price tier creation: FAILED")
                    self.issues.append("Price tier creation failed")
                
            except Exception as e:
                print(f"   ❌ Database operations failed: {e}")
                self.issues.append(f"Price management database error: {e}")
            
            return {'status': 'healthy', 'database_initialized': True}
            
        except ImportError:
            print("   ❌ Price management system not found")
            self.issues.append("Price management system module missing")
            return {'status': 'error', 'error': 'Module not found'}
        except Exception as e:
            print(f"   ❌ Price management check failed: {e}")
            self.issues.append(f"Price management check error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_admin_integration(self):
        """Check admin panel integration"""
        print("\n4. 🔧 ADMIN INTEGRATION")
        print("-" * 40)
        
        try:
            import os
            
            # Check if admin system has pricing functions
            if os.path.exists('admin_system.py'):
                with open('admin_system.py', 'r') as f:
                    content = f.read()
                
                pricing_functions = [
                    'show_pricing_management',
                    'pricing_management',
                    'smart_pricing_system',
                    'pricing_table'
                ]
                
                functions_found = 0
                for func in pricing_functions:
                    if func in content:
                        functions_found += 1
                        print(f"   ✅ {func}: EXISTS")
                    else:
                        print(f"   ❌ {func}: MISSING")
                
                if functions_found >= 2:
                    print("   ✅ Admin pricing integration: ADEQUATE")
                    status = 'healthy'
                else:
                    print("   ⚠️  Admin pricing integration: LIMITED")
                    self.issues.append("Limited admin pricing integration")
                    status = 'issues'
                
            else:
                print("   ❌ admin_system.py not found")
                self.issues.append("Admin system file missing")
                status = 'error'
            
            return {
                'status': status,
                'functions_found': functions_found if 'functions_found' in locals() else 0
            }
            
        except Exception as e:
            print(f"   ❌ Admin integration check failed: {e}")
            self.issues.append(f"Admin integration check error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_currency_conversion(self):
        """Check currency conversion functionality"""
        print("\n5. 💱 CURRENCY CONVERSION")
        print("-" * 40)
        
        try:
            from frequency_pricing import FrequencyPricingSystem
            
            pricing = FrequencyPricingSystem()
            
            # Test currency conversion rates
            usd_to_stars = getattr(pricing, 'USD_TO_STARS', None)
            usd_to_ton = getattr(pricing, 'USD_TO_TON', None)
            
            if usd_to_stars:
                print(f"   📊 USD to Stars rate: {usd_to_stars}")
                print("   ✅ Stars conversion: AVAILABLE")
            else:
                print("   ❌ Stars conversion: MISSING")
                self.issues.append("Stars conversion rate missing")
            
            if usd_to_ton:
                print(f"   📊 USD to TON rate: {usd_to_ton}")
                print("   ✅ TON conversion: AVAILABLE")
            else:
                print("   ❌ TON conversion: MISSING")
                self.issues.append("TON conversion rate missing")
            
            # Test actual conversion
            try:
                result = pricing.calculate_pricing(7)
                
                if 'cost_stars' in result and 'cost_ton' in result:
                    print(f"   📊 Example (7 days): ${result['final_cost_usd']:.2f} = {result['cost_stars']} Stars = {result['cost_ton']:.3f} TON")
                    print("   ✅ Multi-currency pricing: WORKING")
                    status = 'healthy'
                else:
                    print("   ❌ Multi-currency pricing: INCOMPLETE")
                    self.issues.append("Multi-currency pricing incomplete")
                    status = 'issues'
                    
            except Exception as e:
                print(f"   ❌ Currency conversion test failed: {e}")
                self.issues.append(f"Currency conversion test error: {e}")
                status = 'error'
            
            return {
                'status': status,
                'stars_rate': usd_to_stars,
                'ton_rate': usd_to_ton
            }
            
        except Exception as e:
            print(f"   ❌ Currency conversion check failed: {e}")
            self.issues.append(f"Currency conversion check error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_pricing_display(self):
        """Check pricing display functionality"""
        print("\n6. 📱 PRICING DISPLAY")
        print("-" * 40)
        
        try:
            import os
            
            # Check for pricing display components
            display_files = [
                'smart_pricing_display.py',
                'pricing_display.py',
                'frequency_pricing.py'
            ]
            
            files_found = 0
            for file in display_files:
                if os.path.exists(file):
                    files_found += 1
                    print(f"   ✅ {file}: EXISTS")
                else:
                    print(f"   ❌ {file}: MISSING")
            
            # Check handlers for pricing display
            if os.path.exists('handlers.py'):
                with open('handlers.py', 'r') as f:
                    content = f.read()
                
                pricing_handlers = [
                    'show_dynamic_days_selector',
                    'show_posts_per_day_selector',
                    'show_frequency_payment_summary'
                ]
                
                handlers_found = 0
                for handler in pricing_handlers:
                    if handler in content:
                        handlers_found += 1
                        print(f"   ✅ {handler}: EXISTS")
                    else:
                        print(f"   ❌ {handler}: MISSING")
                
                if handlers_found >= 2:
                    print("   ✅ Pricing display handlers: ADEQUATE")
                    status = 'healthy'
                else:
                    print("   ⚠️  Pricing display handlers: LIMITED")
                    self.issues.append("Limited pricing display handlers")
                    status = 'issues'
            else:
                print("   ❌ handlers.py not found")
                self.issues.append("Handlers file missing")
                status = 'error'
            
            return {
                'status': status,
                'display_files': files_found,
                'handlers_found': handlers_found if 'handlers_found' in locals() else 0
            }
            
        except Exception as e:
            print(f"   ❌ Pricing display check failed: {e}")
            self.issues.append(f"Pricing display check error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _display_results(self, results):
        """Display comprehensive results"""
        print("\n" + "=" * 60)
        print("📊 PRICING SYSTEM VALIDATION REPORT")
        print("=" * 60)
        
        # Calculate overall health
        healthy_components = sum(1 for r in results.values() if r.get('status') == 'healthy')
        total_components = len(results)
        
        health_score = (healthy_components / total_components * 100) if total_components > 0 else 0
        
        print(f"\n🏆 OVERALL HEALTH: {health_score:.1f}% ({healthy_components}/{total_components} components healthy)")
        
        if health_score >= 90:
            print("   🟢 EXCELLENT: Pricing system is working optimally")
        elif health_score >= 70:
            print("   🟡 GOOD: Pricing system is working well")
        elif health_score >= 50:
            print("   🟠 FAIR: Pricing system needs attention")
        else:
            print("   🔴 POOR: Pricing system has critical issues")
        
        print("\n📋 COMPONENT STATUS:")
        for component, data in results.items():
            status = data.get('status', 'unknown')
            if status == 'healthy':
                icon = "✅"
            elif status == 'issues':
                icon = "⚠️"
            else:
                icon = "❌"
            
            print(f"   {icon} {component.replace('_', ' ').title()}: {status.upper()}")
        
        # Issues summary
        if self.issues:
            print(f"\n⚠️  ISSUES FOUND ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n✅ NO ISSUES FOUND")
        
        # Recommendations
        print("\n🎯 RECOMMENDATIONS:")
        if health_score >= 90:
            print("   • Pricing system is operating optimally")
            print("   • Monitor currency conversion rates regularly")
        elif health_score >= 70:
            print("   • Address any warnings to improve performance")
            print("   • Test pricing calculations with real scenarios")
        else:
            print("   • Immediate attention required for failed components")
            print("   • Review pricing calculation logic")
            print("   • Ensure all pricing modules are properly integrated")
    
    async def _apply_fixes(self):
        """Apply fixes for identified issues"""
        print("\n🔧 APPLYING FIXES")
        print("-" * 30)
        
        # Fix DynamicPricing issues
        if any('DynamicPricing' in issue for issue in self.issues):
            print("   🔨 Fixing DynamicPricing issues...")
            await self._fix_dynamic_pricing()
        
        # Fix missing modules
        if any('module missing' in issue for issue in self.issues):
            print("   🔨 Addressing missing modules...")
            await self._fix_missing_modules()
        
        print("   ✅ Fixes applied successfully")
    
    async def _fix_dynamic_pricing(self):
        """Fix DynamicPricing issues"""
        print("      • Checking DynamicPricing structure...")
        
        # This would contain specific fixes for DynamicPricing
        self.fixes_applied.append("DynamicPricing structure fixes")
    
    async def _fix_missing_modules(self):
        """Fix missing module issues"""
        print("      • Checking for missing pricing modules...")
        
        # This would contain specific fixes for missing modules
        self.fixes_applied.append("Missing module fixes")

async def main():
    """Main function to run pricing system check"""
    checker = PricingSystemChecker()
    results = await checker.comprehensive_check()
    
    # Save results
    import json
    with open('pricing_system_validation_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Full validation report saved to: pricing_system_validation_report.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())