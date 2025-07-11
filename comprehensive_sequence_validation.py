#!/usr/bin/env python3
"""
Comprehensive Global Sequence System Validation
Complete testing and validation of the unified tracking system
"""

import sqlite3
import json
from datetime import datetime
from global_sequence_system import get_global_sequence_manager
from sequence_logger import setup_sequence_logging, get_sequence_logger
import time

def validate_sequence_format(sequence_id: str) -> bool:
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

def validate_step_format(step_id: str) -> bool:
    """Validate step ID format SEQ-YYYY-MM-XXXXX:StepName"""
    try:
        parts = step_id.split(':')
        if len(parts) != 2:
            return False
        
        sequence_part = parts[0]
        step_part = parts[1]
        
        return validate_sequence_format(sequence_part) and len(step_part) > 0
    except:
        return False

def test_database_schema():
    """Test database schema completeness"""
    print("🔶 VALIDATING DATABASE SCHEMA")
    
    required_tables = [
        'global_sequences',
        'global_sequence_steps', 
        'global_component_links',
        'sequence_counter'
    ]
    
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        schema_valid = True
        for table in required_tables:
            if table in existing_tables:
                print(f"   ✅ Table {table} exists")
            else:
                print(f"   ❌ Table {table} missing")
                schema_valid = False
        
        # Test required columns
        cursor.execute("PRAGMA table_info(global_sequences)")
        seq_columns = [col[1] for col in cursor.fetchall()]
        
        required_seq_columns = [
            'sequence_id', 'user_id', 'username', 'language', 
            'status', 'current_step', 'step_count'
        ]
        
        for col in required_seq_columns:
            if col in seq_columns:
                print(f"   ✅ Column global_sequences.{col} exists")
            else:
                print(f"   ❌ Column global_sequences.{col} missing")
                schema_valid = False
        
        return schema_valid
        
    except Exception as e:
        print(f"   ❌ Database schema validation failed: {e}")
        return False
    finally:
        conn.close()

def test_sequence_generation():
    """Test sequence ID generation and uniqueness"""
    print("\n🔶 VALIDATING SEQUENCE GENERATION")
    
    manager = get_global_sequence_manager()
    
    # Generate multiple sequences
    sequences = []
    for i in range(5):
        seq_id = manager.start_user_sequence(
            user_id=1000000 + i,
            username=f"testuser{i}",
            language="en"
        )
        sequences.append(seq_id)
        print(f"   Generated: {seq_id}")
    
    # Validate format
    format_valid = True
    for seq_id in sequences:
        if validate_sequence_format(seq_id):
            print(f"   ✅ Format valid: {seq_id}")
        else:
            print(f"   ❌ Format invalid: {seq_id}")
            format_valid = False
    
    # Check uniqueness
    unique_valid = len(sequences) == len(set(sequences))
    if unique_valid:
        print(f"   ✅ All sequences unique")
    else:
        print(f"   ❌ Duplicate sequences detected")
    
    return format_valid and unique_valid

def test_step_logging():
    """Test step logging functionality"""
    print("\n🔶 VALIDATING STEP LOGGING")
    
    manager = get_global_sequence_manager()
    logger = get_sequence_logger(__name__)
    
    # Create test sequence
    sequence_id = manager.start_user_sequence(2000000, "steptest", "ar")
    
    # Test various step types
    test_steps = [
        ("User_Flow_1_Start", "handlers"),
        ("User_Flow_2_LanguageSelect", "handlers"),
        ("CreateAd_Step_1_Start", "handlers"),
        ("CreateAd_Step_2_UploadContent", "handlers"),
        ("CreateAd_Step_6_CalculatePrice", "frequency_pricing"),
        ("Payment_Step_1_ProcessTON", "payment_system"),
        ("Campaign_Step_1_CreateCampaign", "campaign_management"),
        ("Publish_Step_1_SendToChannel", "campaign_publisher")
    ]
    
    step_logging_valid = True
    for step_name, component in test_steps:
        try:
            step_id = manager.log_step(sequence_id, step_name, component, {
                "test_data": "validation",
                "timestamp": datetime.now().isoformat()
            })
            
            if validate_step_format(step_id):
                print(f"   ✅ Step logged: {step_id}")
            else:
                print(f"   ❌ Invalid step format: {step_id}")
                step_logging_valid = False
                
        except Exception as e:
            print(f"   ❌ Step logging failed: {step_name} - {e}")
            step_logging_valid = False
    
    return step_logging_valid

def test_component_linking():
    """Test component linking functionality"""
    print("\n🔶 VALIDATING COMPONENT LINKING")
    
    manager = get_global_sequence_manager()
    
    # Create test sequence
    sequence_id = manager.start_user_sequence(3000000, "linktest", "ru")
    
    # Test component linking
    test_links = [
        ("ads", "ad", "123", "primary"),
        ("channels", "channel", "@i3lani", "selected"),
        ("channels", "channel", "@smshco", "selected"),
        ("payments", "ton_payment", "TE1234", "primary"),
        ("campaigns", "campaign", "CAM-2025-07-TEST", "primary"),
        ("post_identity", "post", "AdTEST", "primary"),
        ("published_messages", "message", "@i3lani:12345", "published")
    ]
    
    linking_valid = True
    for component, entity_type, entity_id, link_type in test_links:
        try:
            manager.link_component(sequence_id, component, entity_type, entity_id, link_type, {
                "test_link": True,
                "linked_at": datetime.now().isoformat()
            })
            print(f"   ✅ Linked: {component}:{entity_type}:{entity_id}")
        except Exception as e:
            print(f"   ❌ Linking failed: {component}:{entity_type}:{entity_id} - {e}")
            linking_valid = False
    
    # Test finding sequences by component
    try:
        found_sequences = manager.find_sequence_by_component("campaigns", "CAM-2025-07-TEST")
        if sequence_id in found_sequences:
            print(f"   ✅ Component search working: found {len(found_sequences)} sequences")
        else:
            print(f"   ❌ Component search failed: sequence not found")
            linking_valid = False
    except Exception as e:
        print(f"   ❌ Component search failed: {e}")
        linking_valid = False
    
    return linking_valid

def test_error_handling():
    """Test error handling and logging"""
    print("\n🔶 VALIDATING ERROR HANDLING")
    
    manager = get_global_sequence_manager()
    logger = get_sequence_logger(__name__)
    
    # Create test sequence
    sequence_id = manager.start_user_sequence(4000000, "errortest", "en")
    
    error_handling_valid = True
    
    # Test error step logging
    try:
        error_step_id = manager.log_step(
            sequence_id, "Payment_Step_2_PaymentDetected", "payment_system",
            {"payment_memo": "ER1234", "amount": 0.36},
            "Payment not found on blockchain after 20 minutes"
        )
        
        if validate_step_format(error_step_id):
            print(f"   ✅ Error step logged: {error_step_id}")
        else:
            print(f"   ❌ Invalid error step format: {error_step_id}")
            error_handling_valid = False
            
    except Exception as e:
        print(f"   ❌ Error step logging failed: {e}")
        error_handling_valid = False
    
    # Test sequence error logging
    try:
        logger.step_error(sequence_id, "Publish_Step_1_SendToChannel", "campaign_publisher",
                         "Channel access denied", {"channel_id": "@test_channel"})
        print(f"   ✅ Sequence logger error handling working")
    except Exception as e:
        print(f"   ❌ Sequence logger error handling failed: {e}")
        error_handling_valid = False
    
    return error_handling_valid

def test_integration_compatibility():
    """Test integration with existing bot components"""
    print("\n🔶 VALIDATING INTEGRATION COMPATIBILITY")
    
    integration_valid = True
    
    # Test database compatibility
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Check if existing tables still exist
        existing_tables = ['users', 'channels', 'campaigns', 'ads', 'packages']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        db_tables = [row[0] for row in cursor.fetchall()]
        
        for table in existing_tables:
            if table in db_tables:
                print(f"   ✅ Existing table preserved: {table}")
            else:
                print(f"   ⚠️ Existing table not found: {table}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Database compatibility check failed: {e}")
        integration_valid = False
    
    # Test import compatibility
    try:
        from global_sequence_system import (
            start_user_global_sequence, log_sequence_step, 
            link_to_global_sequence, get_user_sequence_id
        )
        print(f"   ✅ Import functions available")
    except Exception as e:
        print(f"   ❌ Import compatibility failed: {e}")
        integration_valid = False
    
    return integration_valid

def test_performance():
    """Test system performance with multiple operations"""
    print("\n🔶 VALIDATING PERFORMANCE")
    
    manager = get_global_sequence_manager()
    
    # Performance test: Create 10 sequences with 5 steps each
    start_time = time.time()
    
    sequences = []
    for i in range(10):
        seq_id = manager.start_user_sequence(5000000 + i, f"perftest{i}", "en")
        sequences.append(seq_id)
        
        # Add 5 steps to each sequence
        for j in range(5):
            manager.log_step(seq_id, f"Test_Step_{j}", "performance_test", {
                "step_number": j,
                "sequence_index": i
            })
    
    end_time = time.time()
    duration = end_time - start_time
    
    operations = 10 + (10 * 5)  # 10 sequences + 50 steps
    ops_per_second = operations / duration
    
    print(f"   📊 Created {len(sequences)} sequences with 50 steps")
    print(f"   📊 Duration: {duration:.2f} seconds")
    print(f"   📊 Operations per second: {ops_per_second:.1f}")
    
    performance_acceptable = ops_per_second > 10  # At least 10 operations per second
    
    if performance_acceptable:
        print(f"   ✅ Performance acceptable")
    else:
        print(f"   ⚠️ Performance below threshold")
    
    return performance_acceptable

def generate_system_report():
    """Generate comprehensive system report"""
    print("\n🔶 GENERATING SYSTEM REPORT")
    
    manager = get_global_sequence_manager()
    stats = manager.get_system_statistics()
    
    seq_stats = stats.get('sequence_statistics', {})
    comp_stats = stats.get('component_statistics', [])
    recent_sequences = stats.get('recent_sequences', [])
    
    print(f"\n📊 SYSTEM STATISTICS:")
    print(f"   Total Sequences: {seq_stats.get('total_sequences', 0)}")
    print(f"   Active Sequences: {seq_stats.get('active_sequences', 0)}")
    print(f"   Completed Sequences: {seq_stats.get('completed_sequences', 0)}")
    print(f"   Failed Sequences: {seq_stats.get('failed_sequences', 0)}")
    print(f"   Average Steps per Sequence: {seq_stats.get('average_steps', 0)}")
    
    print(f"\n📊 COMPONENT PERFORMANCE:")
    for comp in comp_stats[:10]:  # Top 10 components
        print(f"   {comp['component']}: {comp['success_rate']}% success ({comp['total_steps']} steps)")
    
    print(f"\n📊 RECENT ACTIVITY:")
    for seq in recent_sequences[:5]:  # Last 5 sequences
        print(f"   {seq['sequence_id']} - User {seq['user_id']} - {seq['status']} ({seq['step_count']} steps)")
    
    return stats

def run_comprehensive_validation():
    """Run complete validation suite"""
    print("🧪 COMPREHENSIVE GLOBAL SEQUENCE SYSTEM VALIDATION")
    print("=" * 70)
    
    # Setup logging
    setup_sequence_logging()
    
    # Run all validation tests
    results = {}
    
    results['database_schema'] = test_database_schema()
    results['sequence_generation'] = test_sequence_generation()
    results['step_logging'] = test_step_logging()
    results['component_linking'] = test_component_linking()
    results['error_handling'] = test_error_handling()
    results['integration_compatibility'] = test_integration_compatibility()
    results['performance'] = test_performance()
    
    # Generate system report
    system_stats = generate_system_report()
    
    # Calculate overall success rate
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 VALIDATION RESULTS:")
    print(f"=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 85:
        print(f"🎉 SYSTEM VALIDATION SUCCESSFUL - READY FOR PRODUCTION")
    elif success_rate >= 70:
        print(f"⚠️ SYSTEM VALIDATION PARTIAL - MINOR ISSUES DETECTED")
    else:
        print(f"❌ SYSTEM VALIDATION FAILED - MAJOR ISSUES REQUIRE ATTENTION")
    
    return {
        'validation_results': results,
        'success_rate': success_rate,
        'system_statistics': system_stats,
        'ready_for_production': success_rate >= 85
    }

if __name__ == "__main__":
    run_comprehensive_validation()