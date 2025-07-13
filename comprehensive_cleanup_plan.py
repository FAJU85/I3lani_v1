#!/usr/bin/env python3
"""
Comprehensive Cleanup Plan for I3lani Bot
Based on system audit findings
"""

import os
import asyncio
from pathlib import Path

class ComprehensiveCleanup:
    """Execute comprehensive system cleanup"""
    
    def __init__(self):
        self.files_to_delete = []
        self.files_to_keep = []
        self.broken_integrations = []
        
    def analyze_cleanup_needs(self):
        """Analyze what needs to be cleaned up"""
        
        # DUPLICATES TO DELETE (keep only the best/most advanced version)
        pricing_duplicates = [
            'smart_pricing_display.py',
            'smart_pricing_demo.py', 
            'frequency_pricing.py',
            'test_comprehensive_price_management.py',
            'pricing_system_check.py',
            'dynamic_pricing.py',
            'pricing_system_summary.py',
            'pricing_integration_test.py',
            'advanced_pricing_validation.py'
        ]
        
        payment_duplicates = [
            'worker.py',
            'validate_memo_format.py',
            'comprehensive_enhancement_test.py',
            'animated_transaction_timeline.py',
            'demo_animated_timeline_system.py',
            'immediate_os1497_fix.py',
            'customer_service_resolution.py',
            'manual_zz7832_activation.py',
            'system_architecture_diagram.py'
        ]
        
        admin_duplicates = [
            'admin_system_fixes.py',
            'admin_system_validation.py', 
            'admin_system_status.py',
            'admin_bot_test_system.py'
        ]
        
        channel_duplicates = [
            'find_real_channels.py',
            'check_bot_updates.py',
            'list_all_channels.py',
            'check_five_sar.py',
            'add_five_sar.py',
            'enhanced_channel_discovery.py',
            'force_channel_discovery.py',
            'check_all_channels.py',
            'final_channel_management_fix.py',
            'live_channel_stats.py',
            'demo_enhanced_channel_selection.py',
            'test_advanced_channel_management.py',
            'advanced_channel_management_status.py',
            'channel_detection_test.py',
            'manual_channel_add.py',
            'check_zaaaazoooo_channel.py',
            'why_detection_failed.py',
            'test_enhanced_detection.py',
            'verify_automatic_detection.py',
            'test_channel_detection_integration.py'
        ]
        
        # TEST AND VALIDATION FILES (not needed in production)
        test_files = [
            'test_live_system_status.py',
            'live_system_status_fix.py',
            'publishing_system_check.py',
            'publishing_system_validation.py',
            'image_upload_system_check.py',
            'image_upload_system_test.py',
            'image_upload_system_final_test.py',
            'multilingual_validation.py',
            'startup_optimization.py',
            'fix_startup_performance.py',
            'quick_startup_fix.py',
            'startup_performance_monitor.py',
            'system_integration_test.py',
            'final_system_status.py',
            'bot_systems_overview.py',
            'comprehensive_system_validator.py',
            'system_audit_cleanup.py'
        ]
        
        # BROKEN/UNUSED INTEGRATIONS
        broken_files = [
            'integration_fixes.py',
            'campaign_publisher_integration.py',
            'channel_manager_integration.py',
            'multilingual_menu_integration.py',
            'system_audit_scanner.py',
            'system_cleanup_executor.py',
            'system_validator.py',
            'final_system_optimization.py'
        ]
        
        # MANUAL FIX FILES (one-time use)
        manual_fixes = [
            'fix_hq1923_payment.py',
            'fix_bb1775_payment.py',
            'fix_re5768_payment.py',
            'fix_or4156_payment.py',
            'fix_all_campaigns_publishing.py',
            'fix_ui_issues.py',
            'comprehensive_bug_fixes.py',
            'comprehensive_bug_fixes_validation.py',
            'comprehensive_publishing_workflow.py',
            'comprehensive_publishing_workflow_validation.py'
        ]
        
        # Combine all files to delete
        self.files_to_delete = (
            pricing_duplicates + 
            payment_duplicates + 
            admin_duplicates + 
            channel_duplicates + 
            test_files + 
            broken_files + 
            manual_fixes
        )
        
        # CORE SYSTEMS TO KEEP
        self.files_to_keep = [
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
            'price_management_handlers.py',
            'channel_manager.py',
            'advanced_channel_management.py',
            'advanced_channel_handlers.py',
            'enhanced_channel_admin.py',
            'channel_incentives.py',
            'continuous_payment_scanner.py',
            'automatic_payment_confirmation.py',
            'clean_stars_payment_system.py',
            'enhanced_ton_payment_monitoring.py',
            'payment_memo_tracker.py',
            'payment_amount_validator.py',
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
            'user_management.py',
            'system_health_monitor.py',
            'wallet_manager.py',
            'telegram_channel_api.py',
            'enhanced_channel_detection.py',
            'content_moderation.py',
            'atomic_rewards.py',
            'ui_control_system.py',
            'enhanced_telegram_stars_payment.py',
            'enhanced_stars_payment_system.py',
            'ton_connect_integration.py',
            'post_identity_system.py'
        ]
        
        return {
            'delete_count': len(self.files_to_delete),
            'keep_count': len(self.files_to_keep),
            'total_files': len(self.files_to_delete) + len(self.files_to_keep)
        }
    
    def execute_cleanup(self):
        """Execute the cleanup by deleting unnecessary files"""
        print("🧹 EXECUTING COMPREHENSIVE CLEANUP")
        print("=" * 50)
        
        deleted_count = 0
        errors = []
        
        for file_path in self.files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"   ✅ Deleted: {file_path}")
                    deleted_count += 1
                else:
                    print(f"   ⚠️  Not found: {file_path}")
            except Exception as e:
                error_msg = f"❌ Error deleting {file_path}: {e}"
                print(f"   {error_msg}")
                errors.append(error_msg)
        
        print(f"\n📊 CLEANUP SUMMARY:")
        print(f"   • Files deleted: {deleted_count}")
        print(f"   • Errors: {len(errors)}")
        
        if errors:
            print(f"\n❌ ERRORS:")
            for error in errors:
                print(f"   • {error}")
        
        return {
            'deleted': deleted_count,
            'errors': len(errors),
            'error_details': errors
        }
    
    def verify_core_systems(self):
        """Verify that core systems are still intact"""
        print("\n🔍 VERIFYING CORE SYSTEMS")
        print("=" * 30)
        
        missing_core = []
        existing_core = []
        
        for file_path in self.files_to_keep:
            if os.path.exists(file_path):
                existing_core.append(file_path)
                print(f"   ✅ {file_path}")
            else:
                missing_core.append(file_path)
                print(f"   ❌ MISSING: {file_path}")
        
        print(f"\n📊 CORE SYSTEMS STATUS:")
        print(f"   • Existing: {len(existing_core)}")
        print(f"   • Missing: {len(missing_core)}")
        
        if missing_core:
            print(f"\n⚠️  MISSING CORE SYSTEMS:")
            for missing in missing_core:
                print(f"   • {missing}")
        
        return {
            'existing': len(existing_core),
            'missing': len(missing_core),
            'missing_files': missing_core
        }
    
    def check_main_bot_imports(self):
        """Check if main_bot.py imports are still valid after cleanup"""
        print("\n🔍 CHECKING MAIN BOT IMPORTS")
        print("=" * 30)
        
        try:
            with open('main_bot.py', 'r') as f:
                content = f.read()
            
            import re
            imports = re.findall(r'from\s+(\w+)\s+import|import\s+(\w+)', content)
            
            broken_imports = []
            valid_imports = []
            
            for imp in imports:
                module_name = imp[0] if imp[0] else imp[1]
                if module_name and not module_name.startswith('aiogram'):
                    file_path = f"{module_name}.py"
                    if os.path.exists(file_path):
                        valid_imports.append(module_name)
                        print(f"   ✅ {module_name}")
                    else:
                        broken_imports.append(module_name)
                        print(f"   ❌ BROKEN: {module_name}")
            
            print(f"\n📊 IMPORT STATUS:")
            print(f"   • Valid imports: {len(valid_imports)}")
            print(f"   • Broken imports: {len(broken_imports)}")
            
            return {
                'valid': len(valid_imports),
                'broken': len(broken_imports),
                'broken_imports': broken_imports
            }
            
        except Exception as e:
            print(f"   ❌ Error checking imports: {e}")
            return {'error': str(e)}
    
    def run_comprehensive_cleanup(self):
        """Run the complete cleanup process"""
        print("🚀 COMPREHENSIVE SYSTEM CLEANUP")
        print("=" * 50)
        
        # Step 1: Analyze cleanup needs
        analysis = self.analyze_cleanup_needs()
        print(f"\n📊 CLEANUP ANALYSIS:")
        print(f"   • Files to delete: {analysis['delete_count']}")
        print(f"   • Files to keep: {analysis['keep_count']}")
        print(f"   • Total files: {analysis['total_files']}")
        
        # Step 2: Execute cleanup
        cleanup_result = self.execute_cleanup()
        
        # Step 3: Verify core systems
        verification = self.verify_core_systems()
        
        # Step 4: Check main bot imports
        import_check = self.check_main_bot_imports()
        
        # Final report
        print(f"\n🏆 FINAL CLEANUP REPORT")
        print("=" * 30)
        print(f"✅ Successfully deleted {cleanup_result['deleted']} duplicate/useless files")
        print(f"✅ Preserved {verification['existing']} core systems")
        
        if verification['missing']:
            print(f"⚠️  {verification['missing']} missing core systems need attention")
        
        if 'broken_imports' in import_check and import_check['broken_imports']:
            print(f"⚠️  {import_check['broken']} broken imports need fixing")
        
        return {
            'cleanup': cleanup_result,
            'verification': verification,
            'imports': import_check
        }

def main():
    """Execute comprehensive cleanup"""
    cleaner = ComprehensiveCleanup()
    return cleaner.run_comprehensive_cleanup()

if __name__ == "__main__":
    main()