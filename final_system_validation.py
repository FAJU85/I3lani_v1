#!/usr/bin/env python3
"""
Final System Validation for I3lani Bot
Validates all core systems after cleanup and fixes
"""

import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class FinalSystemValidator:
    """Final system validation after cleanup"""
    
    def __init__(self):
        self.core_systems = [
            'main_bot.py',
            'deployment_server.py',
            'database.py',
            'config.py',
            'languages.py',
            'handlers.py',
            'confirmation_handlers.py',
            'admin_system.py',
            'advanced_pricing_management.py',
            'pricing_admin_handlers.py',
            'price_management_system.py',
            'channel_manager.py',
            'advanced_channel_management.py',
            'advanced_channel_handlers.py',
            'enhanced_channel_admin.py',
            'continuous_payment_scanner.py',
            'automatic_payment_confirmation.py',
            'clean_stars_payment_system.py',
            'enhanced_telegram_stars_payment.py',
            'enhanced_stars_payment_system.py',
            'enhanced_stars_handlers.py',
            'enhanced_ton_payment_monitoring.py',
            'payment_memo_tracker.py',
            'campaign_handlers.py',
            'campaign_management.py',
            'enhanced_campaign_publisher.py',
            'content_integrity_system.py',
            'gamification.py',
            'viral_referral_game.py',
            'viral_referral_handlers.py',
            'troubleshooting_handlers.py',
            'multilingual_menu_system.py',
            'translation_system.py',
            'end_to_end_tracking_system.py',
            'global_sequence_id_system.py',
            'step_title_system.py',
            'animated_transitions.py',
            'contextual_help_system.py',
            'ui_control_system.py',
            'comprehensive_publishing_fix.py',
            'wallet_manager.py',
            'enhanced_channel_detection.py',
            'content_moderation.py',
            'atomic_rewards.py',
            'channel_incentives.py',
            'post_identity_system.py'
        ]
        
        self.validation_results = {}
    
    async def validate_system_integrity(self):
        """Validate overall system integrity"""
        print("🔍 FINAL SYSTEM VALIDATION")
        print("=" * 50)
        
        # Check file existence
        missing_files = []
        existing_files = []
        
        for system_file in self.core_systems:
            if os.path.exists(system_file):
                existing_files.append(system_file)
            else:
                missing_files.append(system_file)
        
        print(f"\n📁 File System Status:")
        print(f"   • Existing core files: {len(existing_files)}")
        print(f"   • Missing core files: {len(missing_files)}")
        
        if missing_files:
            print(f"\n❌ Missing Files:")
            for file in missing_files:
                print(f"   • {file}")
        
        return {
            'existing': len(existing_files),
            'missing': len(missing_files),
            'missing_files': missing_files
        }
    
    async def validate_imports(self):
        """Validate main_bot.py imports"""
        print(f"\n🔍 Import Validation:")
        
        try:
            with open('main_bot.py', 'r') as f:
                content = f.read()
            
            import re
            imports = re.findall(r'from\s+(\w+)\s+import|import\s+(\w+)', content)
            
            broken_imports = []
            valid_imports = []
            
            for imp in imports:
                module_name = imp[0] if imp[0] else imp[1]
                if module_name and not module_name.startswith(('aiogram', 'asyncio', 'logging', 'os', 'sys', 'json', 'datetime', 'pathlib', 'typing', 'fcntl', 'signal', 'threading', 'time', 'aiosqlite', 'flask', 'requests', 'traceback', 'subprocess')):
                    file_path = f"{module_name}.py"
                    if os.path.exists(file_path):
                        valid_imports.append(module_name)
                    else:
                        broken_imports.append(module_name)
            
            print(f"   • Valid imports: {len(valid_imports)}")
            print(f"   • Broken imports: {len(broken_imports)}")
            
            if broken_imports:
                print(f"\n❌ Broken Imports:")
                for imp in broken_imports:
                    print(f"   • {imp}")
            
            return {
                'valid': len(valid_imports),
                'broken': len(broken_imports),
                'broken_imports': broken_imports
            }
            
        except Exception as e:
            print(f"   ❌ Error checking imports: {e}")
            return {'error': str(e)}
    
    async def validate_database_systems(self):
        """Validate database systems"""
        print(f"\n🗄️ Database System Validation:")
        
        try:
            from database import db
            
            # Test database connection
            connection = await db.get_connection()
            if connection:
                print("   ✅ Database connection successful")
                
                # Check key tables
                cursor = await connection.cursor()
                tables_to_check = [
                    'users', 'channels', 'campaigns', 'campaign_posts',
                    'pricing_tiers', 'promotional_offers', 'bundle_packages'
                ]
                
                existing_tables = []
                for table in tables_to_check:
                    await cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if await cursor.fetchone():
                        existing_tables.append(table)
                
                print(f"   • Existing tables: {len(existing_tables)}/{len(tables_to_check)}")
                
                return {
                    'connection': True,
                    'tables': len(existing_tables),
                    'expected_tables': len(tables_to_check)
                }
            else:
                print("   ❌ Database connection failed")
                return {'connection': False}
                
        except Exception as e:
            print(f"   ❌ Database validation error: {e}")
            return {'error': str(e)}
    
    async def validate_payment_systems(self):
        """Validate payment systems"""
        print(f"\n💳 Payment System Validation:")
        
        try:
            # Test TON payment monitoring
            from enhanced_ton_payment_monitoring import EnhancedTonPaymentMonitoring
            ton_monitoring = EnhancedTonPaymentMonitoring()
            print("   ✅ TON payment monitoring available")
            
            # Test Stars payment system
            from enhanced_stars_payment_system import get_enhanced_stars_system
            stars_system = get_enhanced_stars_system()
            print("   ✅ Enhanced Stars payment system available")
            
            # Test clean Stars payment
            from clean_stars_payment_system import CleanStarsPayment
            print("   ✅ Clean Stars payment system available")
            
            return {
                'ton_monitoring': True,
                'stars_system': True,
                'clean_stars': True
            }
            
        except Exception as e:
            print(f"   ❌ Payment system validation error: {e}")
            return {'error': str(e)}
    
    async def validate_admin_systems(self):
        """Validate admin systems"""
        print(f"\n⚙️ Admin System Validation:")
        
        try:
            # Test admin system
            from admin_system import AdminSystem
            admin = AdminSystem()
            print("   ✅ Admin system available")
            
            # Test advanced pricing management
            from advanced_pricing_management import pricing_manager
            await pricing_manager.initialize_pricing_database()
            print("   ✅ Advanced pricing management available")
            
            # Test pricing admin handlers
            from pricing_admin_handlers import setup_pricing_admin_handlers
            print("   ✅ Pricing admin handlers available")
            
            return {
                'admin_system': True,
                'pricing_management': True,
                'pricing_handlers': True
            }
            
        except Exception as e:
            print(f"   ❌ Admin system validation error: {e}")
            return {'error': str(e)}
    
    async def validate_channel_systems(self):
        """Validate channel systems"""
        print(f"\n📺 Channel System Validation:")
        
        try:
            # Test channel manager
            from channel_manager import ChannelManager
            print("   ✅ Channel manager available")
            
            # Test advanced channel management
            from advanced_channel_management import AdvancedChannelManager
            print("   ✅ Advanced channel management available")
            
            # Test channel detection
            from enhanced_channel_detection import EnhancedChannelDetection
            print("   ✅ Enhanced channel detection available")
            
            return {
                'channel_manager': True,
                'advanced_management': True,
                'channel_detection': True
            }
            
        except Exception as e:
            print(f"   ❌ Channel system validation error: {e}")
            return {'error': str(e)}
    
    async def validate_campaign_systems(self):
        """Validate campaign systems"""
        print(f"\n📊 Campaign System Validation:")
        
        try:
            # Test campaign management
            from campaign_management import Database as CampaignDB
            print("   ✅ Campaign management available")
            
            # Test enhanced campaign publisher
            from enhanced_campaign_publisher import EnhancedCampaignPublisher
            print("   ✅ Enhanced campaign publisher available")
            
            # Test content integrity
            from content_integrity_system import ContentIntegritySystem
            integrity = ContentIntegritySystem()
            print("   ✅ Content integrity system available")
            
            return {
                'campaign_management': True,
                'campaign_publisher': True,
                'content_integrity': True
            }
            
        except Exception as e:
            print(f"   ❌ Campaign system validation error: {e}")
            return {'error': str(e)}
    
    async def run_final_validation(self):
        """Run complete final validation"""
        print("🚀 RUNNING FINAL SYSTEM VALIDATION")
        print("=" * 50)
        
        results = {}
        
        # Validate system integrity
        results['integrity'] = await self.validate_system_integrity()
        
        # Validate imports
        results['imports'] = await self.validate_imports()
        
        # Validate database systems
        results['database'] = await self.validate_database_systems()
        
        # Validate payment systems
        results['payments'] = await self.validate_payment_systems()
        
        # Validate admin systems
        results['admin'] = await self.validate_admin_systems()
        
        # Validate channel systems
        results['channels'] = await self.validate_channel_systems()
        
        # Validate campaign systems
        results['campaigns'] = await self.validate_campaign_systems()
        
        # Generate final report
        print(f"\n" + "=" * 50)
        print("🏆 FINAL VALIDATION REPORT")
        print("=" * 50)
        
        # Calculate success metrics
        total_systems = len(self.core_systems)
        existing_systems = results['integrity']['existing']
        missing_systems = results['integrity']['missing']
        
        valid_imports = results['imports'].get('valid', 0)
        broken_imports = results['imports'].get('broken', 0)
        
        print(f"\n📊 System Status:")
        print(f"   • Core systems present: {existing_systems}/{total_systems}")
        print(f"   • Valid imports: {valid_imports}")
        print(f"   • Broken imports: {broken_imports}")
        
        # Calculate overall health
        integrity_score = (existing_systems / total_systems) * 100 if total_systems > 0 else 0
        import_score = (valid_imports / (valid_imports + broken_imports)) * 100 if (valid_imports + broken_imports) > 0 else 100
        
        overall_health = (integrity_score + import_score) / 2
        
        print(f"\n📈 Health Metrics:")
        print(f"   • File integrity: {integrity_score:.1f}%")
        print(f"   • Import health: {import_score:.1f}%")
        print(f"   • Overall health: {overall_health:.1f}%")
        
        # System status
        system_status = {}
        for category, result in results.items():
            if isinstance(result, dict) and 'error' not in result:
                system_status[category] = "✅ Operational"
            else:
                system_status[category] = "❌ Issues detected"
        
        print(f"\n🔍 System Categories:")
        for category, status in system_status.items():
            print(f"   • {category.title()}: {status}")
        
        if overall_health >= 90:
            print(f"\n🟢 EXCELLENT: Bot is production-ready")
        elif overall_health >= 75:
            print(f"\n🟡 GOOD: Bot is mostly operational")
        elif overall_health >= 50:
            print(f"\n🟠 FAIR: Bot needs attention")
        else:
            print(f"\n🔴 POOR: Bot has critical issues")
        
        return {
            'overall_health': overall_health,
            'integrity_score': integrity_score,
            'import_score': import_score,
            'system_status': system_status,
            'results': results
        }

async def main():
    """Run final validation"""
    validator = FinalSystemValidator()
    return await validator.run_final_validation()

if __name__ == "__main__":
    asyncio.run(main())