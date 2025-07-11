#!/usr/bin/env python3
"""
I3lani Bot System Audit Scanner
Comprehensive analysis of all bot systems and modules
"""
import os
import sqlite3
import json
from datetime import datetime
from collections import defaultdict

class SystemAuditScanner:
    def __init__(self):
        self.db_path = "bot.db"
        self.issues = []
        self.fixes_needed = []
        self.files_to_delete = []
        self.working_systems = []
        
    def scan_all_systems(self):
        """Perform comprehensive system scan"""
        print("🔍 I3LANI BOT COMPREHENSIVE SYSTEM AUDIT")
        print("=" * 60)
        
        # 1. Scan test and debug files
        self.scan_test_files()
        
        # 2. Scan database tables
        self.scan_database_tables()
        
        # 3. Scan core systems
        self.scan_core_systems()
        
        # 4. Scan payment systems
        self.scan_payment_systems()
        
        # 5. Scan campaign and publishing systems
        self.scan_campaign_systems()
        
        # 6. Scan UI and language systems
        self.scan_ui_systems()
        
        # 7. Scan unused/legacy systems
        self.scan_legacy_systems()
        
        # 8. Generate report
        self.generate_audit_report()
    
    def scan_test_files(self):
        """Identify test and debug files"""
        print("\n1️⃣ SCANNING TEST AND DEBUG FILES")
        print("-" * 40)
        
        test_patterns = ["test_", "fix_", "debug_", "old_", "legacy_", "temp_", "backup_"]
        test_files = []
        
        for root, dirs, files in os.walk("."):
            # Skip cache directories
            if ".cache" in root or "__pycache__" in root:
                continue
                
            for file in files:
                if file.endswith(".py"):
                    for pattern in test_patterns:
                        if pattern in file:
                            filepath = os.path.join(root, file)
                            if ".cache" not in filepath:
                                test_files.append(filepath)
                                break
        
        print(f"Found {len(test_files)} test/debug files")
        self.files_to_delete.extend(test_files[:50])  # Mark first 50 for deletion
        
    def scan_database_tables(self):
        """Analyze database structure and usage"""
        print("\n2️⃣ SCANNING DATABASE TABLES")
        print("-" * 40)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        table_usage = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            table_usage[table_name] = count
        
        # Identify unused tables
        unused_tables = []
        active_tables = []
        
        for table, count in table_usage.items():
            if count == 0 and table not in ['sqlite_sequence', 'bot_settings']:
                unused_tables.append(table)
            else:
                active_tables.append((table, count))
        
        print(f"Active tables: {len(active_tables)}")
        print(f"Empty tables: {len(unused_tables)}")
        
        if unused_tables:
            self.issues.append(f"Empty database tables: {', '.join(unused_tables[:10])}")
        
        conn.close()
        
    def scan_core_systems(self):
        """Check core bot functionality"""
        print("\n3️⃣ SCANNING CORE SYSTEMS")
        print("-" * 40)
        
        core_files = {
            "main_bot.py": "Main bot entry point",
            "handlers.py": "Message handlers",
            "database.py": "Database operations",
            "languages.py": "Multilingual support"
        }
        
        for file, desc in core_files.items():
            if os.path.exists(file):
                size = os.path.getsize(file)
                if size > 100000:  # > 100KB
                    self.issues.append(f"{file} is very large ({size/1024:.1f}KB) - needs refactoring")
                else:
                    self.working_systems.append(f"{desc} ({file})")
            else:
                self.issues.append(f"Missing core file: {file}")
                
    def scan_payment_systems(self):
        """Analyze payment system implementations"""
        print("\n4️⃣ SCANNING PAYMENT SYSTEMS")
        print("-" * 40)
        
        payment_files = []
        for file in os.listdir("."):
            if "payment" in file.lower() and file.endswith(".py"):
                payment_files.append(file)
        
        print(f"Found {len(payment_files)} payment-related files")
        
        # Check for duplicates
        ton_systems = [f for f in payment_files if "ton" in f.lower()]
        stars_systems = [f for f in payment_files if "stars" in f.lower()]
        
        if len(ton_systems) > 3:
            self.issues.append(f"Multiple TON payment systems ({len(ton_systems)} files)")
        
        if len(stars_systems) > 3:
            self.issues.append(f"Multiple Stars payment systems ({len(stars_systems)} files)")
            
        # Check active payment systems
        active_payment = ["enhanced_ton_payment_monitoring.py", "clean_stars_payment_system.py"]
        for system in active_payment:
            if os.path.exists(system):
                self.working_systems.append(f"Payment system: {system}")
                
    def scan_campaign_systems(self):
        """Check campaign and publishing systems"""
        print("\n5️⃣ SCANNING CAMPAIGN & PUBLISHING SYSTEMS")
        print("-" * 40)
        
        campaign_files = []
        publishing_files = []
        
        for file in os.listdir("."):
            if file.endswith(".py"):
                if "campaign" in file.lower():
                    campaign_files.append(file)
                elif "publish" in file.lower():
                    publishing_files.append(file)
        
        print(f"Campaign files: {len(campaign_files)}")
        print(f"Publishing files: {len(publishing_files)}")
        
        # Check for active systems
        if os.path.exists("campaign_management.py"):
            self.working_systems.append("Campaign management system")
        
        if os.path.exists("enhanced_campaign_publisher.py"):
            self.working_systems.append("Enhanced campaign publisher")
        else:
            self.fixes_needed.append("Campaign publisher may not be running")
            
    def scan_ui_systems(self):
        """Check UI and user interface systems"""
        print("\n6️⃣ SCANNING UI SYSTEMS")
        print("-" * 40)
        
        ui_files = []
        for file in os.listdir("."):
            if file.endswith(".py") and any(word in file.lower() for word in ["ui", "interface", "button", "keyboard"]):
                ui_files.append(file)
        
        print(f"UI-related files: {len(ui_files)}")
        
        # Check for issues
        if len(ui_files) > 10:
            self.issues.append(f"Too many UI files ({len(ui_files)}) - consolidation needed")
            
    def scan_legacy_systems(self):
        """Identify legacy and unused systems"""
        print("\n7️⃣ SCANNING LEGACY SYSTEMS")
        print("-" * 40)
        
        legacy_patterns = [
            "neural", "quantum", "protocol", "matrix", "cyber",
            "enhancement", "optimization", "advanced", "super"
        ]
        
        legacy_files = []
        for file in os.listdir("."):
            if file.endswith(".py"):
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    for pattern in legacy_patterns:
                        if pattern in content and file not in ["languages.py", "handlers.py"]:
                            legacy_files.append(file)
                            break
        
        if legacy_files:
            self.issues.append(f"Files with legacy terminology: {len(legacy_files)}")
            
    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "=" * 60)
        print("📊 AUDIT REPORT SUMMARY")
        print("=" * 60)
        
        print(f"\n✅ WORKING SYSTEMS ({len(self.working_systems)}):")
        for system in self.working_systems[:10]:
            print(f"   • {system}")
        
        print(f"\n⚠️  ISSUES FOUND ({len(self.issues)}):")
        for issue in self.issues[:10]:
            print(f"   • {issue}")
        
        print(f"\n🔧 FIXES NEEDED ({len(self.fixes_needed)}):")
        for fix in self.fixes_needed[:10]:
            print(f"   • {fix}")
        
        print(f"\n🗑️  FILES TO DELETE ({len(self.files_to_delete)}):")
        for file in self.files_to_delete[:10]:
            print(f"   • {file}")
        
        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "working_systems": self.working_systems,
            "issues": self.issues,
            "fixes_needed": self.fixes_needed,
            "files_to_delete": self.files_to_delete
        }
        
        with open("audit_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("\n📄 Detailed report saved to audit_report.json")

if __name__ == "__main__":
    scanner = SystemAuditScanner()
    scanner.scan_all_systems()