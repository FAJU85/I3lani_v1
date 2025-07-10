#!/usr/bin/env python3
"""
Fix Database Schema for Post Identity System
Add missing columns and ensure compatibility
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Fix database schema to support Post Identity System"""
    
    print("🔧 FIXING DATABASE SCHEMA FOR POST IDENTITY SYSTEM")
    print("="*55)
    
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Check current campaigns table structure
        cursor.execute("PRAGMA table_info(campaigns)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"📋 Current campaigns table columns: {columns}")
        
        # Add missing columns to campaigns table
        missing_columns = []
        
        if 'content_type' not in columns:
            missing_columns.append(('content_type', 'TEXT DEFAULT "text"'))
            
        if 'media_url' not in columns:
            missing_columns.append(('media_url', 'TEXT'))
            
        if 'advertiser_username' not in columns:
            missing_columns.append(('advertiser_username', 'TEXT'))
        
        # Add missing columns
        for col_name, col_def in missing_columns:
            try:
                cursor.execute(f"ALTER TABLE campaigns ADD COLUMN {col_name} {col_def}")
                print(f"✅ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"⚠️ Column {col_name} already exists")
                else:
                    print(f"❌ Error adding {col_name}: {e}")
        
        # Update campaigns with content from ads table
        print(f"\n📝 Updating campaigns with actual content from ads table...")
        
        cursor.execute('''
            UPDATE campaigns 
            SET content_type = (
                SELECT a.content_type 
                FROM ads a 
                WHERE a.user_id = campaigns.user_id 
                ORDER BY a.created_at DESC 
                LIMIT 1
            ),
            media_url = (
                SELECT a.media_url 
                FROM ads a 
                WHERE a.user_id = campaigns.user_id 
                ORDER BY a.created_at DESC 
                LIMIT 1
            ),
            ad_content = (
                SELECT a.content 
                FROM ads a 
                WHERE a.user_id = campaigns.user_id 
                ORDER BY a.created_at DESC 
                LIMIT 1
            )
            WHERE EXISTS (
                SELECT 1 FROM ads a WHERE a.user_id = campaigns.user_id
            )
        ''')
        
        updated_campaigns = cursor.rowcount
        print(f"✅ Updated {updated_campaigns} campaigns with latest content")
        
        # Update advertiser usernames
        cursor.execute('''
            UPDATE campaigns 
            SET advertiser_username = COALESCE(
                (SELECT username FROM users WHERE users.user_id = campaigns.user_id),
                'user_' || campaigns.user_id
            )
        ''')
        
        updated_usernames = cursor.rowcount
        print(f"✅ Updated {updated_usernames} campaigns with advertiser usernames")
        
        # Verify CAM-2025-07-YBZ3 specifically
        cursor.execute('''
            SELECT campaign_id, ad_content, content_type, media_url, advertiser_username
            FROM campaigns 
            WHERE campaign_id = 'CAM-2025-07-YBZ3'
        ''')
        
        campaign_data = cursor.fetchone()
        if campaign_data:
            campaign_id, ad_content, content_type, media_url, username = campaign_data
            print(f"\n🎯 CAM-2025-07-YBZ3 verification:")
            print(f"  Content: \"{ad_content}\"")
            print(f"  Type: {content_type}")
            print(f"  Media: {media_url}")
            print(f"  Username: {username}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Database schema updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_database_schema()
    if success:
        print("\n🎉 Database schema fix completed!")
    else:
        print("\n❌ Database schema fix failed")