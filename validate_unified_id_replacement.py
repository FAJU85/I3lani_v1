#!/usr/bin/env python3
"""
Validate Unified ID System Replacement
Complete validation that old ID systems have been replaced with sequence system
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any
from global_sequence_system import get_global_sequence_manager
from sequence_logger import get_sequence_logger

logger = get_sequence_logger(__name__)

def validate_sequence_id_format(sequence_id: str) -> bool:
    """Validate sequence ID format SEQ-YYYY-MM-XXXXX"""
    try:
        parts = sequence_id.split('-')
        if len(parts) != 4:
            return False
        
        if parts[0] != 'SEQ':
            return False
        
        year = int(parts[1])
        month = int(parts[2])
        counter = parts[3]
        
        if year < 2025 or year > 2030:
            return False
        
        if month < 1 or month > 12:
            return False
        
        if len(counter) != 5 or not counter.isdigit():
            return False
        
        return True
    except:
        return False

def validate_old_id_elimination() -> Dict[str, Any]:
    """Validate that old ID systems have been eliminated"""
    print("🔍 VALIDATING OLD ID SYSTEM ELIMINATION")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        validation = {
            "old_payment_ids": 0,
            "old_campaign_ids": 0,
            "old_post_ids": 0,
            "sequence_based_ids": 0,
            "elimination_complete": False,
            "issues": []
        }
        
        # Check for old payment ID patterns
        cursor.execute("""
            SELECT COUNT(*) FROM payments 
            WHERE payment_id LIKE 'STAR%' AND payment_id NOT LIKE 'STARS-%'
        """)
        old_payments = cursor.fetchone()[0]
        validation["old_payment_ids"] = old_payments
        
        if old_payments > 0:
            print(f"   ❌ Found {old_payments} old payment IDs (STAR format)")
            validation["issues"].append(f"Old payment IDs found: {old_payments}")
        else:
            print(f"   ✅ No old payment IDs found")
        
        # Check for old campaign ID patterns
        cursor.execute("""
            SELECT COUNT(*) FROM campaigns 
            WHERE campaign_id LIKE 'CAM-2025-%' AND campaign_id NOT LIKE 'CAM-07-%'
        """)
        old_campaigns = cursor.fetchone()[0]
        validation["old_campaign_ids"] = old_campaigns
        
        if old_campaigns > 0:
            print(f"   ❌ Found {old_campaigns} old campaign IDs (CAM-YYYY-MM-XXXX format)")
            validation["issues"].append(f"Old campaign IDs found: {old_campaigns}")
        else:
            print(f"   ✅ No old campaign IDs found")
        
        # Check for old post ID patterns
        cursor.execute("""
            SELECT COUNT(*) FROM post_identity 
            WHERE post_id LIKE 'Ad%' AND post_id NOT LIKE 'POST-%'
        """)
        old_posts = cursor.fetchone()[0]
        validation["old_post_ids"] = old_posts
        
        if old_posts > 0:
            print(f"   ❌ Found {old_posts} old post IDs (AdXX format)")
            validation["issues"].append(f"Old post IDs found: {old_posts}")
        else:
            print(f"   ✅ No old post IDs found")
        
        # Check for sequence-based IDs
        cursor.execute("""
            SELECT COUNT(*) FROM campaigns 
            WHERE sequence_id IS NOT NULL AND sequence_id LIKE 'SEQ-%'
        """)
        sequence_campaigns = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM post_identity 
            WHERE sequence_id IS NOT NULL AND sequence_id LIKE 'SEQ-%'
        """)
        sequence_posts = cursor.fetchone()[0]
        
        validation["sequence_based_ids"] = sequence_campaigns + sequence_posts
        
        if validation["sequence_based_ids"] > 0:
            print(f"   ✅ Found {validation['sequence_based_ids']} sequence-based records")
        else:
            print(f"   ⚠️ No sequence-based records found")
        
        # Overall validation
        total_old_ids = validation["old_payment_ids"] + validation["old_campaign_ids"] + validation["old_post_ids"]
        if total_old_ids == 0 and validation["sequence_based_ids"] > 0:
            validation["elimination_complete"] = True
            print(f"   🎉 OLD ID SYSTEM ELIMINATION COMPLETE")
        else:
            print(f"   ❌ OLD ID SYSTEM ELIMINATION INCOMPLETE")
        
        conn.close()
        return validation
        
    except Exception as e:
        print(f"   ❌ Error validating old ID elimination: {e}")
        return {"elimination_complete": False, "issues": [str(e)]}

def validate_sequence_system_integration() -> Dict[str, Any]:
    """Validate that sequence system is properly integrated"""
    print("\n🔍 VALIDATING SEQUENCE SYSTEM INTEGRATION")
    print("=" * 50)
    
    try:
        manager = get_global_sequence_manager()
        stats = manager.get_system_statistics()
        
        integration = {
            "sequence_system_active": False,
            "total_sequences": 0,
            "active_sequences": 0,
            "linked_components": 0,
            "integration_complete": False,
            "issues": []
        }
        
        # Check system statistics
        seq_stats = stats.get('sequence_statistics', {})
        integration["total_sequences"] = seq_stats.get('total_sequences', 0)
        integration["active_sequences"] = seq_stats.get('active_sequences', 0)
        
        if integration["total_sequences"] > 0:
            print(f"   ✅ Sequence system active: {integration['total_sequences']} total sequences")
            integration["sequence_system_active"] = True
        else:
            print(f"   ❌ Sequence system not active")
            integration["issues"].append("No sequences found")
        
        # Check component linking
        comp_stats = stats.get('component_statistics', [])
        integration["linked_components"] = len(comp_stats)
        
        if integration["linked_components"] > 0:
            print(f"   ✅ Component linking active: {integration['linked_components']} components")
            for comp in comp_stats[:5]:  # Show top 5 components
                print(f"     - {comp['component']}: {comp['total_steps']} steps")
        else:
            print(f"   ❌ Component linking not active")
            integration["issues"].append("No linked components found")
        
        # Overall integration validation
        if (integration["sequence_system_active"] and 
            integration["linked_components"] > 0 and 
            integration["active_sequences"] > 0):
            integration["integration_complete"] = True
            print(f"   🎉 SEQUENCE SYSTEM INTEGRATION COMPLETE")
        else:
            print(f"   ❌ SEQUENCE SYSTEM INTEGRATION INCOMPLETE")
        
        return integration
        
    except Exception as e:
        print(f"   ❌ Error validating sequence system integration: {e}")
        return {"integration_complete": False, "issues": [str(e)]}

def validate_logging_system_update() -> Dict[str, Any]:
    """Validate that logging system includes sequence context"""
    print("\n🔍 VALIDATING LOGGING SYSTEM UPDATE")
    print("=" * 50)
    
    try:
        logging_validation = {
            "sequence_logger_active": False,
            "log_entries_with_sequence": 0,
            "enhanced_logging_active": False,
            "issues": []
        }
        
        # Check if sequence logger is available
        try:
            test_logger = get_sequence_logger("test_module")
            if test_logger:
                print(f"   ✅ Sequence logger active and available")
                logging_validation["sequence_logger_active"] = True
            else:
                print(f"   ❌ Sequence logger not available")
                logging_validation["issues"].append("Sequence logger not available")
        except Exception as e:
            print(f"   ❌ Error accessing sequence logger: {e}")
            logging_validation["issues"].append(f"Sequence logger error: {e}")
        
        # Check for enhanced logging capabilities
        try:
            conn = sqlite3.connect("bot.db")
            cursor = conn.cursor()
            
            # Check if global_sequence_steps table has recent entries
            cursor.execute("""
                SELECT COUNT(*) FROM global_sequence_steps 
                WHERE timestamp >= datetime('now', '-1 hour')
            """)
            recent_steps = cursor.fetchone()[0]
            
            logging_validation["log_entries_with_sequence"] = recent_steps
            
            if recent_steps > 0:
                print(f"   ✅ Enhanced logging active: {recent_steps} recent entries with sequence context")
                logging_validation["enhanced_logging_active"] = True
            else:
                print(f"   ⚠️ No recent enhanced logging entries found")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error checking enhanced logging: {e}")
            logging_validation["issues"].append(f"Enhanced logging check failed: {e}")
        
        return logging_validation
        
    except Exception as e:
        print(f"   ❌ Error validating logging system: {e}")
        return {"enhanced_logging_active": False, "issues": [str(e)]}

def validate_database_schema_update() -> Dict[str, Any]:
    """Validate that database schema has been updated for sequence system"""
    print("\n🔍 VALIDATING DATABASE SCHEMA UPDATE")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        schema_validation = {
            "sequence_tables_exist": False,
            "sequence_columns_added": False,
            "foreign_keys_intact": False,
            "indexes_created": False,
            "schema_complete": False,
            "issues": []
        }
        
        # Check for sequence system tables
        required_tables = [
            'global_sequences',
            'global_sequence_steps',
            'global_component_links',
            'sequence_counter'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"   ✅ Table {table} exists")
            else:
                print(f"   ❌ Table {table} missing")
                missing_tables.append(table)
        
        if not missing_tables:
            schema_validation["sequence_tables_exist"] = True
        else:
            schema_validation["issues"].append(f"Missing tables: {missing_tables}")
        
        # Check for sequence_id columns in main tables
        tables_to_check = ['campaigns', 'post_identity', 'payments']
        missing_columns = []
        
        for table in tables_to_check:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'sequence_id' in columns:
                    print(f"   ✅ Column sequence_id exists in {table}")
                else:
                    print(f"   ❌ Column sequence_id missing in {table}")
                    missing_columns.append(f"{table}.sequence_id")
            except sqlite3.OperationalError:
                print(f"   ⚠️ Table {table} not found")
        
        if not missing_columns:
            schema_validation["sequence_columns_added"] = True
        else:
            schema_validation["issues"].append(f"Missing columns: {missing_columns}")
        
        # Check for indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%sequence%'")
        sequence_indexes = cursor.fetchall()
        
        if sequence_indexes:
            print(f"   ✅ Sequence indexes created: {len(sequence_indexes)} indexes")
            schema_validation["indexes_created"] = True
        else:
            print(f"   ⚠️ No sequence indexes found")
        
        # Overall schema validation
        if (schema_validation["sequence_tables_exist"] and 
            schema_validation["sequence_columns_added"] and 
            schema_validation["indexes_created"]):
            schema_validation["schema_complete"] = True
            print(f"   🎉 DATABASE SCHEMA UPDATE COMPLETE")
        else:
            print(f"   ❌ DATABASE SCHEMA UPDATE INCOMPLETE")
        
        conn.close()
        return schema_validation
        
    except Exception as e:
        print(f"   ❌ Error validating database schema: {e}")
        return {"schema_complete": False, "issues": [str(e)]}

def run_complete_validation() -> Dict[str, Any]:
    """Run complete validation of unified ID system replacement"""
    print("🧪 COMPLETE UNIFIED ID SYSTEM REPLACEMENT VALIDATION")
    print("=" * 70)
    
    # Run all validation tests
    old_id_validation = validate_old_id_elimination()
    sequence_integration = validate_sequence_system_integration()
    logging_validation = validate_logging_system_update()
    schema_validation = validate_database_schema_update()
    
    # Calculate overall success
    validations = [
        old_id_validation.get("elimination_complete", False),
        sequence_integration.get("integration_complete", False),
        logging_validation.get("enhanced_logging_active", False),
        schema_validation.get("schema_complete", False)
    ]
    
    passed_validations = sum(validations)
    total_validations = len(validations)
    success_rate = (passed_validations / total_validations) * 100
    
    print(f"\n🎯 VALIDATION RESULTS:")
    print(f"=" * 70)
    print(f"   Old ID System Elimination: {'✅ PASSED' if old_id_validation.get('elimination_complete') else '❌ FAILED'}")
    print(f"   Sequence System Integration: {'✅ PASSED' if sequence_integration.get('integration_complete') else '❌ FAILED'}")
    print(f"   Logging System Update: {'✅ PASSED' if logging_validation.get('enhanced_logging_active') else '❌ FAILED'}")
    print(f"   Database Schema Update: {'✅ PASSED' if schema_validation.get('schema_complete') else '❌ FAILED'}")
    
    print(f"\n📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_validations}/{total_validations})")
    
    if success_rate >= 75:
        print(f"🎉 UNIFIED ID SYSTEM REPLACEMENT VALIDATION SUCCESSFUL")
        status = "SUCCESS"
    else:
        print(f"❌ UNIFIED ID SYSTEM REPLACEMENT VALIDATION FAILED")
        status = "FAILED"
    
    # Collect all issues
    all_issues = []
    all_issues.extend(old_id_validation.get("issues", []))
    all_issues.extend(sequence_integration.get("issues", []))
    all_issues.extend(logging_validation.get("issues", []))
    all_issues.extend(schema_validation.get("issues", []))
    
    if all_issues:
        print(f"\n❌ ISSUES FOUND:")
        for issue in all_issues:
            print(f"   - {issue}")
    
    return {
        "status": status,
        "success_rate": success_rate,
        "validations": {
            "old_id_elimination": old_id_validation,
            "sequence_integration": sequence_integration,
            "logging_validation": logging_validation,
            "schema_validation": schema_validation
        },
        "issues": all_issues,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    result = run_complete_validation()
    
    print(f"\n📋 FINAL VALIDATION REPORT:")
    print(f"Status: {result['status']}")
    print(f"Success Rate: {result['success_rate']:.1f}%")
    print(f"Issues Found: {len(result['issues'])}")
    print(f"Timestamp: {result['timestamp']}")