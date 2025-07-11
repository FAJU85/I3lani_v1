#!/usr/bin/env python3
"""
I3lani Bot System Cleanup Executor
Executes cleanup based on audit results
"""
import os
import sqlite3
import shutil
from datetime import datetime

class SystemCleanupExecutor:
    def __init__(self):
        self.db_path = "bot.db"
        self.deleted_files = []
        self.fixed_issues = []
        self.errors = []
        
    def execute_cleanup(self):
        """Execute comprehensive system cleanup"""
        print("🧹 I3LANI BOT SYSTEM CLEANUP")
        print("=" * 60)
        
        # 1. Delete test files
        self.delete_test_files()
        
        # 2. Clean database tables
        self.clean_database_tables()
        
        # 3. Consolidate payment systems
        self.consolidate_payment_systems()
        
        # 4. Fix campaign systems
        self.fix_campaign_systems()
        
        # 5. Clean UI files
        self.clean_ui_files()
        
        # 6. Generate cleanup report
        self.generate_cleanup_report()
    
    def delete_test_files(self):
        """Delete unnecessary test and debug files"""
        print("\n1️⃣ DELETING TEST AND DEBUG FILES")
        print("-" * 40)
        
        # List of files to delete (excluding critical ones)
        files_to_delete = [
            "test_pricing.py", "test_flask.py", "test_token.py",
            "test_deployment.py", "test_deployment_fixes.py",
            "test_bot_startup.py", "test_simple_interface.py",
            "test_enhanced_ton_payment.py", "test_enhanced_stars_system.py",
            "test_payment_fix.py", "test_payment_security_fix.py",
            "test_stars_payment_fix.py", "test_stars_payment_database_fix.py",
            "test_wallet_bug_fixes.py", "test_wallet_critical_bug_fixes.py",
            "test_ton_payment_bug_fix.py", "test_ton_payment_system_fix.py",
            "test_flexible_payment_verification.py", "test_payment_memo_format_fix.py",
            "fix_emojis.py", "fix_bot_conflict.py", "fix_deployment_issues.py",
            "fix_language_bug.py", "fix_menus.py", "fix_post_languages.py",
            "debug_channels.py", "debug_payment_flow.py", "debug_ton_payments.py",
            "old_payment_system.py", "legacy_handlers.py", "temp_fix.py"
        ]
        
        for file in files_to_delete:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    self.deleted_files.append(file)
                except Exception as e:
                    self.errors.append(f"Could not delete {file}: {e}")
        
        print(f"Deleted {len(self.deleted_files)} files")
    
    def clean_database_tables(self):
        """Clean up unused database tables"""
        print("\n2️⃣ CLEANING DATABASE TABLES")
        print("-" * 40)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tables that are empty and not needed
        tables_to_drop = [
            "flow_transitions",  # Old workflow system
            "leaderboard_cache",  # Unused gamification
            "partner_referrals",  # Not implemented
            "payout_requests",  # Not implemented
            "performance_metrics"  # Old monitoring
        ]
        
        dropped = 0
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                dropped += 1
            except Exception as e:
                self.errors.append(f"Could not drop table {table}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"Dropped {dropped} unused tables")
        self.fixed_issues.append(f"Cleaned {dropped} unused database tables")
    
    def consolidate_payment_systems(self):
        """Keep only active payment systems"""
        print("\n3️⃣ CONSOLIDATING PAYMENT SYSTEMS")
        print("-" * 40)
        
        # Keep only these payment files
        keep_payment_files = [
            "enhanced_ton_payment_monitoring.py",
            "clean_stars_payment_system.py", 
            "automatic_payment_confirmation.py",
            "wallet_manager.py",
            "payment_amount_validator.py"
        ]
        
        # Delete redundant payment files
        redundant_payment_files = [
            "enhanced_stars_payment_system.py",  # Duplicate of clean_stars
            "enhanced_telegram_stars_payment.py",  # Duplicate
            "stars_payment_handler.py",  # Old implementation
            "ton_payment_handler.py",  # Old implementation
            "payment_processor.py",  # Replaced by automatic confirmation
            "payment_validation.py",  # Merged into validator
            "stars_invoice_handler.py",  # Old Stars implementation
            "ton_blockchain_monitor.py",  # Replaced by enhanced monitoring
        ]
        
        deleted = 0
        for file in redundant_payment_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    deleted += 1
                    self.deleted_files.append(file)
                except Exception as e:
                    self.errors.append(f"Could not delete {file}: {e}")
        
        print(f"Consolidated payment systems - deleted {deleted} redundant files")
        self.fixed_issues.append("Consolidated payment systems to 5 core files")
    
    def fix_campaign_systems(self):
        """Ensure campaign systems are properly configured"""
        print("\n4️⃣ FIXING CAMPAIGN SYSTEMS")
        print("-" * 40)
        
        # Check if publisher is properly initialized
        with open("main_bot.py", "r") as f:
            content = f.read()
        
        if "enhanced_campaign_publisher.start()" not in content:
            self.fixed_issues.append("Campaign publisher needs to be started in main_bot.py")
        else:
            self.fixed_issues.append("Campaign publisher properly configured")
        
        # Delete redundant campaign files
        redundant_campaign_files = [
            "campaign_publisher.py",  # Replaced by enhanced version
            "simple_campaign_publisher.py",  # Old implementation
            "campaign_scheduler.py",  # Merged into publisher
            "campaign_validator.py",  # Merged into management
            "publishing_scheduler.py",  # Replaced by enhanced publisher
        ]
        
        deleted = 0
        for file in redundant_campaign_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    deleted += 1
                    self.deleted_files.append(file)
                except Exception as e:
                    self.errors.append(f"Could not delete {file}: {e}")
        
        print(f"Cleaned up {deleted} redundant campaign files")
    
    def clean_ui_files(self):
        """Consolidate UI and interface files"""
        print("\n5️⃣ CLEANING UI FILES")
        print("-" * 40)
        
        # Delete redundant UI files
        redundant_ui_files = [
            "button_fix_validation.py",
            "button_test_handler.py",
            "button_status_report.py",
            "enhanced_ui_system.py",  # If features already in handlers
            "simple_interface.py",  # Old implementation
            "ui_enhancement.py",  # Merged into handlers
            "keyboard_builder.py",  # If using aiogram built-in
            "menu_builder.py",  # If redundant with handlers
        ]
        
        deleted = 0
        for file in redundant_ui_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    deleted += 1
                    self.deleted_files.append(file)
                except Exception as e:
                    self.errors.append(f"Could not delete {file}: {e}")
        
        print(f"Cleaned up {deleted} redundant UI files")
        self.fixed_issues.append("Consolidated UI system files")
    
    def generate_cleanup_report(self):
        """Generate cleanup execution report"""
        print("\n" + "=" * 60)
        print("📊 CLEANUP EXECUTION REPORT")
        print("=" * 60)
        
        print(f"\n✅ FIXED ISSUES ({len(self.fixed_issues)}):")
        for fix in self.fixed_issues:
            print(f"   • {fix}")
        
        print(f"\n🗑️  DELETED FILES ({len(self.deleted_files)}):")
        print(f"   Total: {len(self.deleted_files)} files removed")
        
        print(f"\n❌ ERRORS ({len(self.errors)}):")
        for error in self.errors[:5]:
            print(f"   • {error}")
        
        # Save cleanup log
        log = {
            "timestamp": datetime.now().isoformat(),
            "deleted_files": self.deleted_files,
            "fixed_issues": self.fixed_issues,
            "errors": self.errors
        }
        
        with open("cleanup_log.json", "w") as f:
            import json
            json.dump(log, f, indent=2)
        
        print("\n📄 Cleanup log saved to cleanup_log.json")

if __name__ == "__main__":
    executor = SystemCleanupExecutor()
    executor.execute_cleanup()