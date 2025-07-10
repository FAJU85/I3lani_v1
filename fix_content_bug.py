#!/usr/bin/env python3
"""
Fix Campaign Content Bug
Retrieve actual user ad content and fix the campaign publishing system
"""

import sqlite3
import json
import asyncio
import sys
sys.path.append('.')

def get_user_ad_content(user_id: int):
    """Get the most recent ad content for user"""
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Get most recent ad by user
        cursor.execute('''
            SELECT ad_id, content, content_type, media_url 
            FROM ads 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            ad_id, content, content_type, media_url = result
            return {
                'ad_id': ad_id,
                'content': content,
                'content_type': content_type,
                'media_url': media_url
            }
        
        return None
        
    except Exception as e:
        print(f"❌ Error getting user ad content: {e}")
        return None

def update_campaign_content(campaign_id: str, actual_content: str):
    """Update campaign with actual user content"""
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Update campaign with real content
        cursor.execute('''
            UPDATE campaigns 
            SET ad_content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE campaign_id = ?
        ''', (actual_content, campaign_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Updated campaign {campaign_id} with actual content")
        return True
        
    except Exception as e:
        print(f"❌ Error updating campaign content: {e}")
        return False

def fix_campaign_content():
    """Fix the content issue for campaign CAM-2025-07-YBZ3"""
    
    print("🔧 FIXING CAMPAIGN CONTENT BUG")
    print("="*50)
    
    # Get actual user content
    print("1. Retrieving actual user ad content...")
    user_content = get_user_ad_content(566158428)
    
    if user_content:
        print(f"   ✅ Found user content: {user_content['content'][:100]}...")
        print(f"   Type: {user_content['content_type']}")
        if user_content['media_url']:
            print(f"   Media: {user_content['media_url']}")
        
        # Update campaign with actual content
        print("2. Updating campaign with actual content...")
        success = update_campaign_content('CAM-2025-07-YBZ3', user_content['content'])
        
        if success:
            print("3. Verifying update...")
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT ad_content FROM campaigns WHERE campaign_id = ?', ('CAM-2025-07-YBZ3',))
            result = cursor.fetchone()
            
            if result:
                updated_content = result[0]
                print(f"   ✅ Campaign content updated to: {updated_content[:100]}...")
            
            conn.close()
            
        return user_content
    else:
        print("   ❌ No user content found - checking fallback options...")
        
        # Check if user has any content in state or other tables
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Check all tables for potential user content
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("   Available tables:")
        for table in tables:
            print(f"     - {table[0]}")
        
        conn.close()
        return None

if __name__ == "__main__":
    fix_campaign_content()