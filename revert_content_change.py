#!/usr/bin/env python3
"""
Revert HQ1923 Campaign Content
Revert back to the original content ending with "⭐️⭐️" since the user didn't ask for content change
"""

import sqlite3

def revert_hq1923_content():
    """Revert the HQ1923 campaign content back to original"""
    
    print("🔧 REVERTING HQ1923 CAMPAIGN CONTENT")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Original content (without the KKK that was added by mistake)
        original_content = """*صدقاتكم* 🌱
 فـي:
(وقف فاطمة ابراهيم المبرك رحمها الله)

أثرهـا يمتـد ✨
وأجرهـا يبقى بإذن الله. 🍃
https://give.qb.org.sa/P/1811

⭐️⭐️"""
        
        print(f"📝 Reverting to original content:")
        print(original_content)
        print()
        
        # Update campaign content
        cursor.execute("""
            UPDATE campaigns 
            SET ad_content = ?
            WHERE campaign_id = 'CAM-2025-07-HQ19'
        """, (original_content,))
        
        # Update scheduled posts content
        cursor.execute("""
            UPDATE campaign_posts 
            SET post_content = ?
            WHERE campaign_id = 'CAM-2025-07-HQ19'
        """, (original_content,))
        
        conn.commit()
        conn.close()
        
        print("✅ Campaign content reverted to original")
        print("✅ Scheduled posts content reverted to original")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reverting content: {e}")
        return False

if __name__ == "__main__":
    success = revert_hq1923_content()
    
    if success:
        print("\n✅ CONTENT REVERT SUCCESSFUL")
        print("Content restored to original ending with '⭐️⭐️'")
    else:
        print("\n❌ CONTENT REVERT FAILED")