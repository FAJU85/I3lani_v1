#!/usr/bin/env python3
"""
Update HQ1923 Campaign Content
Remove the incorrect "⭐️⭐️" and update with correct content ending with "KKK"
"""

import sqlite3
from datetime import datetime


def update_hq1923_content():
    """Update the HQ1923 campaign content to fix the ending"""
    
    print("🔧 UPDATING HQ1923 CAMPAIGN CONTENT")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Current content
        cursor.execute("SELECT ad_content FROM campaigns WHERE campaign_id = 'CAM-2025-07-HQ19'")
        current_content = cursor.fetchone()
        
        if current_content:
            print(f"📋 Current content:")
            print(current_content[0])
            print()
            
            # Correct content as provided by user
            correct_content = """*صدقاتكم* 🌱
 فـي:
(وقف فاطمة ابراهيم المبرك رحمها الله)

أثرهـا يمتـد ✨
وأجرهـا يبقى بإذن الله. 🍃
https://give.qb.org.sa/P/1811


KKK"""
            
            print(f"📝 Updating to correct content:")
            print(correct_content)
            print()
            
            # Update campaign content
            cursor.execute("""
                UPDATE campaigns 
                SET ad_content = ?
                WHERE campaign_id = 'CAM-2025-07-HQ19'
            """, (correct_content,))
            
            # Update scheduled posts content
            cursor.execute("""
                UPDATE campaign_posts 
                SET post_content = ?
                WHERE campaign_id = 'CAM-2025-07-HQ19'
            """, (correct_content,))
            
            conn.commit()
            
            print("✅ Campaign content updated successfully")
            print("✅ Scheduled posts content updated successfully")
            
            # Verify update
            cursor.execute("SELECT ad_content FROM campaigns WHERE campaign_id = 'CAM-2025-07-HQ19'")
            updated_content = cursor.fetchone()
            
            if updated_content and "KKK" in updated_content[0]:
                print("✅ Verification: Content correctly ends with 'KKK'")
            else:
                print("❌ Verification: Content update may have failed")
                
        conn.close()
        
        print("\n🎉 CONTENT UPDATE COMPLETED")
        print("=" * 50)
        print("✅ Campaign CAM-2025-07-HQ19 content updated")
        print("✅ All scheduled posts will now use correct content")
        print("✅ Future posts will publish with 'KKK' ending")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating content: {e}")
        return False


if __name__ == "__main__":
    success = update_hq1923_content()
    
    if success:
        print("\n✅ CONTENT UPDATE SUCCESSFUL")
        print("Your campaign now has the correct content ending with 'KKK'")
    else:
        print("\n❌ CONTENT UPDATE FAILED")