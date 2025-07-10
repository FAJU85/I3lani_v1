#!/usr/bin/env python3
"""
Fix Campaign Publisher Database Schema
Add missing columns and update schema for campaign publishing
"""

import sqlite3
import logging

def fix_database_schema():
    """Fix database schema for campaign publisher"""
    print("🔧 FIXING CAMPAIGN PUBLISHER DATABASE SCHEMA")
    print("="*50)
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    try:
        # Add error_message column to campaign_posts if it doesn't exist
        print("1. Adding error_message column to campaign_posts...")
        try:
            cursor.execute('ALTER TABLE campaign_posts ADD COLUMN error_message TEXT')
            print("   ✅ Added error_message column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ✅ error_message column already exists")
            else:
                print(f"   ❌ Error adding error_message column: {e}")
        
        # Add published_at column to campaign_posts if it doesn't exist
        print("2. Adding published_at column to campaign_posts...")
        try:
            cursor.execute('ALTER TABLE campaign_posts ADD COLUMN published_at TEXT')
            print("   ✅ Added published_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ✅ published_at column already exists")
            else:
                print(f"   ❌ Error adding published_at column: {e}")
        
        # Check available channel fields
        print("3. Checking channel table structure...")
        cursor.execute('PRAGMA table_info(channels)')
        channel_columns = [col[1] for col in cursor.fetchall()]
        print(f"   Available columns: {', '.join(channel_columns)}")
        
        # Get sample channel data to understand the structure
        cursor.execute('SELECT * FROM channels WHERE active = 1 LIMIT 1')
        sample_channel = cursor.fetchone()
        
        if sample_channel:
            # Get column names
            cursor.execute('PRAGMA table_info(channels)')
            columns = [col[1] for col in cursor.fetchall()]
            channel_dict = dict(zip(columns, sample_channel))
            
            print("   Sample channel data:")
            for key, value in channel_dict.items():
                print(f"     {key}: {value}")
        
        conn.commit()
        print("\n✅ Database schema fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_schema()