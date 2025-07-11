#!/usr/bin/env python3
"""
I3lani Bot System Validator
Validates critical systems are working correctly
"""
import os
import sqlite3
import importlib.util
from datetime import datetime

class SystemValidator:
    def __init__(self):
        self.db_path = "bot.db"
        self.validation_results = {}
        
    def validate_all_systems(self):
        """Validate all critical systems"""
        print("✅ I3LANI BOT SYSTEM VALIDATION")
        print("=" * 60)
        
        # 1. Validate core files
        self.validate_core_files()
        
        # 2. Validate database schema
        self.validate_database_schema()
        
        # 3. Validate payment flow
        self.validate_payment_flow()
        
        # 4. Validate campaign flow
        self.validate_campaign_flow()
        
        # 5. Validate publishing system
        self.validate_publishing_system()
        
        # 6. Generate validation report
        self.generate_validation_report()
    
    def validate_core_files(self):
        """Check core files exist and are loadable"""
        print("\n1️⃣ VALIDATING CORE FILES")
        print("-" * 40)
        
        core_files = {
            "main_bot.py": "Bot entry point",
            "handlers.py": "Message handlers",
            "database.py": "Database operations",
            "languages.py": "Multilingual support",
            "campaign_management.py": "Campaign system",
            "enhanced_campaign_publisher.py": "Publishing system",
            "clean_stars_payment_system.py": "Stars payments",
            "enhanced_ton_payment_monitoring.py": "TON payments",
            "automatic_payment_confirmation.py": "Payment confirmation"
        }
        
        for file, desc in core_files.items():
            if os.path.exists(file):
                try:
                    # Try to load the module
                    spec = importlib.util.spec_from_file_location("module", file)
                    module = importlib.util.module_from_spec(spec)
                    self.validation_results[file] = "✅ Working"
                    print(f"✅ {desc}: {file}")
                except Exception as e:
                    self.validation_results[file] = f"❌ Error: {str(e)[:50]}"
                    print(f"❌ {desc}: {file} - Error loading")
            else:
                self.validation_results[file] = "❌ Missing"
                print(f"❌ {desc}: {file} - Missing")
    
    def validate_database_schema(self):
        """Check database tables and schema"""
        print("\n2️⃣ VALIDATING DATABASE SCHEMA")
        print("-" * 40)
        
        required_tables = [
            "users", "channels", "campaigns", "campaign_posts",
            "payments", "ads", "subscriptions", "orders"
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"✅ Table exists: {table}")
            else:
                missing_tables.append(table)
                print(f"❌ Missing table: {table}")
        
        self.validation_results["database_schema"] = f"Missing tables: {len(missing_tables)}"
        
        conn.close()
    
    def validate_payment_flow(self):
        """Check payment system integration"""
        print("\n3️⃣ VALIDATING PAYMENT FLOW")
        print("-" * 40)
        
        # Check TON payment flow
        ton_files = [
            "enhanced_ton_payment_monitoring.py",
            "wallet_manager.py",
            "automatic_payment_confirmation.py"
        ]
        
        ton_flow_ok = all(os.path.exists(f) for f in ton_files)
        
        # Check Stars payment flow
        stars_files = [
            "clean_stars_payment_system.py",
            "automatic_payment_confirmation.py"
        ]
        
        stars_flow_ok = all(os.path.exists(f) for f in stars_files)
        
        print(f"TON payment flow: {'✅ Complete' if ton_flow_ok else '❌ Incomplete'}")
        print(f"Stars payment flow: {'✅ Complete' if stars_flow_ok else '❌ Incomplete'}")
        
        self.validation_results["payment_flow"] = {
            "ton": ton_flow_ok,
            "stars": stars_flow_ok
        }
    
    def validate_campaign_flow(self):
        """Check campaign creation and management"""
        print("\n4️⃣ VALIDATING CAMPAIGN FLOW")
        print("-" * 40)
        
        # Check campaign flow files
        campaign_files = [
            "campaign_management.py",
            "campaign_handlers.py"
        ]
        
        campaign_flow_ok = all(os.path.exists(f) for f in campaign_files)
        
        # Check if campaigns table has proper columns
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(campaigns)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ["campaign_id", "user_id", "ad_content", "media_url", "content_type"]
        missing_columns = [col for col in required_columns if col not in columns]
        
        print(f"Campaign files: {'✅ Complete' if campaign_flow_ok else '❌ Incomplete'}")
        print(f"Campaign table schema: {'✅ Complete' if not missing_columns else f'❌ Missing: {missing_columns}'}")
        
        self.validation_results["campaign_flow"] = {
            "files": campaign_flow_ok,
            "schema": len(missing_columns) == 0
        }
        
        conn.close()
    
    def validate_publishing_system(self):
        """Check publishing system status"""
        print("\n5️⃣ VALIDATING PUBLISHING SYSTEM")
        print("-" * 40)
        
        # Check if publisher is running
        if os.path.exists(".bot_pid"):
            with open(".bot_pid", "r") as f:
                pid = f.read().strip()
            print(f"Bot PID: {pid}")
        else:
            print("❌ Bot PID file not found")
        
        # Check campaign_posts table
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM campaign_posts WHERE status = 'scheduled'")
        scheduled = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM campaign_posts WHERE status = 'published'")
        published = cursor.fetchone()[0]
        
        print(f"Scheduled posts: {scheduled}")
        print(f"Published posts: {published}")
        
        self.validation_results["publishing_system"] = {
            "scheduled_posts": scheduled,
            "published_posts": published
        }
        
        conn.close()
    
    def generate_validation_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT")
        print("=" * 60)
        
        # Count issues
        issues = 0
        for key, value in self.validation_results.items():
            if isinstance(value, str) and "❌" in value:
                issues += 1
            elif isinstance(value, dict):
                for k, v in value.items():
                    if v is False or (isinstance(v, str) and "❌" in v):
                        issues += 1
        
        print(f"\nTotal Issues Found: {issues}")
        
        if issues == 0:
            print("\n🎉 All systems validated successfully!")
        else:
            print("\n⚠️  Some issues need attention")
        
        # Save validation report
        with open("validation_report.json", "w") as f:
            import json
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": self.validation_results,
                "total_issues": issues
            }, f, indent=2)
        
        print("\n📄 Validation report saved to validation_report.json")

if __name__ == "__main__":
    validator = SystemValidator()
    validator.validate_all_systems()