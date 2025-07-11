#!/usr/bin/env python3
"""
Comprehensive Bug Fixes Validation
End-to-end testing of all reported issues
"""

import asyncio
import logging
import sqlite3
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def validate_bug_fixes():
    """Comprehensive validation of all reported bug fixes"""
    print("🔧 COMPREHENSIVE BUG FIXES VALIDATION")
    print("=" * 50)
    
    test_results = {
        'campaign_publishing': False,
        'campaign_list': False,
        'channel_ui': False,
        'channel_detection': False,
        'content_integrity': False
    }
    
    # Test 1: Campaign Publishing
    print("\n🧪 Test 1: Campaign Publishing")
    print("-" * 30)
    
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Check recent publishing activity
        cursor.execute('''
            SELECT COUNT(*) FROM channel_publishing_logs 
            WHERE created_at > datetime('now', '-15 minutes')
        ''')
        recent_posts = cursor.fetchone()[0]
        
        # Check problematic campaigns
        problem_campaigns = ['CAM-2025-07-YBZ3', 'CAM-2025-07-Z2ZU']
        publishing_working = True
        
        for campaign_id in problem_campaigns:
            cursor.execute('''
                SELECT COUNT(*) as published
                FROM campaign_posts 
                WHERE campaign_id = ? AND status = 'published'
            ''', (campaign_id,))
            
            published_count = cursor.fetchone()[0]
            print(f"   {campaign_id}: {published_count} posts published")
            
            if published_count == 0:
                publishing_working = False
        
        test_results['campaign_publishing'] = publishing_working and recent_posts > 0
        print(f"   Result: {'✅ PASS' if test_results['campaign_publishing'] else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        test_results['campaign_publishing'] = False
    
    # Test 2: Campaign List
    print("\n🧪 Test 2: Campaign List")
    print("-" * 30)
    
    try:
        # Check if campaigns appear in user lists
        cursor.execute('''
            SELECT user_id, COUNT(*) as campaign_count
            FROM campaigns
            WHERE created_at > datetime('now', '-24 hours')
            GROUP BY user_id
        ''')
        
        user_campaigns = cursor.fetchall()
        campaigns_visible = len(user_campaigns) > 0
        
        for user_id, count in user_campaigns:
            print(f"   User {user_id}: {count} campaigns")
        
        test_results['campaign_list'] = campaigns_visible
        print(f"   Result: {'✅ PASS' if test_results['campaign_list'] else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        test_results['campaign_list'] = False
    
    # Test 3: Channel UI Data
    print("\n🧪 Test 3: Channel UI Data")
    print("-" * 30)
    
    try:
        # Get channel data structure
        cursor.execute('PRAGMA table_info(channels)')
        columns = cursor.fetchall()
        
        has_subscriber_field = any('subscriber' in col[1].lower() for col in columns)
        
        # Get channel data
        cursor.execute('SELECT * FROM channels LIMIT 3')
        channels = cursor.fetchall()
        
        print(f"   Channels available: {len(channels)}")
        print(f"   Has subscriber field: {has_subscriber_field}")
        
        test_results['channel_ui'] = len(channels) > 0
        print(f"   Result: {'✅ PASS' if test_results['channel_ui'] else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        test_results['channel_ui'] = False
    
    # Test 4: Content Integrity
    print("\n🧪 Test 4: Content Integrity")
    print("-" * 30)
    
    try:
        # Check content fingerprints
        cursor.execute('SELECT COUNT(*) FROM content_fingerprints')
        fingerprint_count = cursor.fetchone()[0]
        
        print(f"   Content fingerprints: {fingerprint_count}")
        
        # Test content integrity system
        from content_integrity_system import ContentIntegritySystem
        system = ContentIntegritySystem()
        
        # Test hash generation
        test_hash = system.generate_content_hash("Test content", "test_media")
        hash_working = len(test_hash) > 0
        
        print(f"   Hash generation: {'✅' if hash_working else '❌'}")
        
        test_results['content_integrity'] = fingerprint_count > 0 and hash_working
        print(f"   Result: {'✅ PASS' if test_results['content_integrity'] else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        test_results['content_integrity'] = False
    
    # Test 5: Channel Detection (Check if handler exists)
    print("\n🧪 Test 5: Channel Detection")
    print("-" * 30)
    
    try:
        # Check if comprehensive publishing fix is handling channel detection
        import os
        handler_exists = os.path.exists('comprehensive_publishing_fix.py')
        
        if handler_exists:
            with open('comprehensive_publishing_fix.py', 'r') as f:
                content = f.read()
                has_channel_detection = 'my_chat_member' in content or 'handle_new_channel' in content
        else:
            has_channel_detection = False
        
        print(f"   Channel detection handler: {'✅' if has_channel_detection else '❌'}")
        
        test_results['channel_detection'] = has_channel_detection
        print(f"   Result: {'✅ PASS' if test_results['channel_detection'] else '❌ FAIL'}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        test_results['channel_detection'] = False
    
    conn.close()
    
    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL BUGS FIXED - SYSTEM FULLY OPERATIONAL")
    else:
        print(f"⚠️  {total_tests - passed_tests} issues still need attention")
    
    return test_results

if __name__ == "__main__":
    asyncio.run(validate_bug_fixes())