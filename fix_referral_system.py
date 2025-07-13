#!/usr/bin/env python3
"""
Fix Referral System Database Methods
Updates all database method calls to use correct Database class methods
"""

import re
import os

def fix_referral_system_database():
    """Fix all database method calls in referral_system.py"""
    
    # Read the file
    with open('referral_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all db.execute calls with db.execute_query
    content = re.sub(r'await db\.execute\(', 'await db.execute_query(', content)
    
    # Replace all db.fetchone calls with db.fetchone
    content = re.sub(r'await db\.fetchone\(', 'await db.fetchone(', content)
    
    # Replace all db.fetchall calls with db.fetchall
    content = re.sub(r'await db\.fetchall\(', 'await db.fetchall(', content)
    
    # Write back
    with open('referral_system.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed referral_system.py database methods")

def fix_referral_handlers_database():
    """Fix database methods in referral_handlers.py if needed"""
    
    if not os.path.exists('referral_handlers.py'):
        print("⚠️ referral_handlers.py not found")
        return
    
    with open('referral_handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if any database calls need fixing
    if 'db.execute(' in content:
        content = re.sub(r'db\.execute\(', 'db.execute_query(', content)
        
        with open('referral_handlers.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed referral_handlers.py database methods")
    else:
        print("✅ referral_handlers.py database methods already correct")

def main():
    """Main fix function"""
    print("🔧 Fixing referral system database methods...")
    print("=" * 50)
    
    fix_referral_system_database()
    fix_referral_handlers_database()
    
    print("\n" + "=" * 50)
    print("✅ Referral system database methods fixed")

if __name__ == "__main__":
    main()