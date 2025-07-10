#!/usr/bin/env python3
"""
Fix Campaign Publisher Startup Issue
Add proper campaign publisher initialization to main_bot.py
"""

import re

def fix_campaign_publisher_startup():
    """Fix the campaign publisher startup issue in main_bot.py"""
    
    print("🔧 FIXING CAMPAIGN PUBLISHER STARTUP")
    print("="*45)
    
    # Read main_bot.py
    with open('main_bot.py', 'r') as f:
        content = f.read()
    
    # Check if campaign publisher initialization exists
    if 'from campaign_publisher import init_campaign_publisher' in content:
        print("✅ Campaign publisher import already exists")
        
        # Check if it's properly called
        if 'campaign_publisher = await init_campaign_publisher(bot)' in content:
            print("✅ Campaign publisher initialization already exists")
            
            # The issue might be that it's not in the right place
            # Let's check if it's in the correct order after campaign management
            lines = content.split('\n')
            
            campaign_mgmt_line = -1
            campaign_pub_line = -1
            
            for i, line in enumerate(lines):
                if 'campaign management system' in line.lower():
                    campaign_mgmt_line = i
                elif 'campaign publisher system' in line.lower():
                    campaign_pub_line = i
            
            print(f"Campaign management init at line: {campaign_mgmt_line}")
            print(f"Campaign publisher init at line: {campaign_pub_line}")
            
            if campaign_pub_line > campaign_mgmt_line:
                print("✅ Campaign publisher is after management system")
            else:
                print("❌ Campaign publisher initialization order issue")
                
        else:
            print("❌ Campaign publisher not being called")
    else:
        print("❌ Campaign publisher import missing")
    
    # Look for the exact initialization section
    init_section_found = False
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if 'Initialize campaign publisher system' in line:
            init_section_found = True
            print(f"Found initialization section at line {i+1}")
            
            # Print surrounding lines for context
            start = max(0, i-2)
            end = min(len(lines), i+8)
            
            print("Context:")
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"{marker} {j+1}: {lines[j]}")
            break
    
    if not init_section_found:
        print("❌ Campaign publisher initialization section not found")
        return False
    
    print("\n✅ Campaign publisher code exists in main_bot.py")
    print("The issue might be that exceptions are being caught silently")
    
    return True

if __name__ == "__main__":
    fix_campaign_publisher_startup()