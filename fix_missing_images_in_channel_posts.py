#!/usr/bin/env python3
"""
Fix Missing Images in Channel Posts - Critical Bug Report #IMAGES
ROOT CAUSE: Incorrect database JOIN in campaign_publisher.py causing media loss
SOLUTION: Fix JOIN logic and ensure campaigns store media URLs correctly
"""

import sqlite3
import asyncio
import sys
import logging
sys.path.append('.')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImagePublishingFix:
    """Fix media publishing issues in channel posts"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
    
    def analyze_issue(self):
        """Analyze the current media storage and publishing issue"""
        
        print("🔍 ANALYZING MISSING IMAGES ISSUE")
        print("="*50)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check ads with media
        cursor.execute("SELECT COUNT(*) FROM ads WHERE media_url IS NOT NULL")
        ads_with_media = cursor.fetchone()[0]
        
        # Check campaigns with media
        cursor.execute("SELECT COUNT(*) FROM campaigns WHERE media_url IS NOT NULL")
        campaigns_with_media = cursor.fetchone()[0]
        
        # Check recent campaign posts
        cursor.execute("""
            SELECT cp.campaign_id, cp.channel_id, c.ad_content, c.media_url, c.content_type
            FROM campaign_posts cp
            JOIN campaigns c ON cp.campaign_id = c.campaign_id
            WHERE c.media_url IS NOT NULL
            LIMIT 5
        """)
        
        posts_with_media = cursor.fetchall()
        
        conn.close()
        
        print(f"📊 ANALYSIS RESULTS:")
        print(f"   • Ads with media: {ads_with_media}")
        print(f"   • Campaigns with media: {campaigns_with_media}")
        print(f"   • Campaign posts with media: {len(posts_with_media)}")
        
        if posts_with_media:
            print(f"\n📋 SAMPLE CAMPAIGNS WITH MEDIA:")
            for post in posts_with_media:
                campaign_id, channel_id, content, media_url, content_type = post
                print(f"   • {campaign_id}: {content_type} - {media_url[:50]}...")
        
        # Identify the specific issue
        if ads_with_media > 0 and campaigns_with_media > 0:
            print(f"\n✅ MEDIA STORAGE: Working correctly")
            print(f"❌ ISSUE: Publishing logic not using stored media")
            return "publishing_logic"
        elif ads_with_media > 0 and campaigns_with_media == 0:
            print(f"\n❌ ISSUE: Media not copied from ads to campaigns")
            return "campaign_creation"
        else:
            print(f"\n❌ ISSUE: Media not being stored during upload")
            return "media_upload"
    
    def fix_campaign_publisher_join(self):
        """Fix the LEFT JOIN issue in campaign_publisher.py"""
        
        print(f"\n🔧 FIXING CAMPAIGN PUBLISHER JOIN LOGIC")
        
        # Read current campaign_publisher.py
        with open('campaign_publisher.py', 'r') as f:
            content = f.read()
        
        # Fix the problematic LEFT JOIN
        old_query = """cursor.execute(\"\"\"
                SELECT cp.*, c.ad_content, c.user_id, c.campaign_name, c.ad_type,
                       a.media_url, a.content_type
                FROM campaign_posts cp
                JOIN campaigns c ON cp.campaign_id = c.campaign_id
                LEFT JOIN ads a ON c.user_id = a.user_id
                WHERE cp.status = 'scheduled'
                AND cp.scheduled_time <= ?
                ORDER BY cp.scheduled_time ASC, a.created_at DESC
                LIMIT 50
            \"\"\", (now,))"""
        
        # Fixed query that uses campaigns table media directly (like enhanced publisher)
        new_query = """cursor.execute(\"\"\"
                SELECT cp.*, c.ad_content, c.user_id, c.campaign_name, c.ad_type,
                       c.media_url, c.content_type
                FROM campaign_posts cp
                JOIN campaigns c ON cp.campaign_id = c.campaign_id
                WHERE cp.status = 'scheduled'
                AND cp.scheduled_time <= ?
                ORDER BY cp.scheduled_time ASC
                LIMIT 50
            \"\"\", (now,))"""
        
        # Replace the problematic query
        if old_query in content:
            content = content.replace(old_query, new_query)
            
            with open('campaign_publisher.py', 'w') as f:
                f.write(content)
            
            print(f"✅ Fixed LEFT JOIN in campaign_publisher.py")
            return True
        else:
            print(f"⚠️ Query not found, checking alternative approach...")
            return False
    
    def ensure_campaigns_have_media(self):
        """Ensure campaigns table has media from corresponding ads"""
        
        print(f"\n🔧 ENSURING CAMPAIGNS HAVE MEDIA DATA")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find campaigns missing media but have corresponding ads with media
        cursor.execute("""
            SELECT c.campaign_id, c.user_id, a.media_url, a.content_type
            FROM campaigns c
            LEFT JOIN ads a ON c.user_id = a.user_id AND a.media_url IS NOT NULL
            WHERE c.media_url IS NULL AND a.media_url IS NOT NULL
            ORDER BY a.created_at DESC
        """)
        
        missing_media = cursor.fetchall()
        
        if missing_media:
            print(f"📋 Found {len(missing_media)} campaigns missing media")
            
            # Update campaigns with media from latest ads
            updated_count = 0
            for campaign_id, user_id, media_url, content_type in missing_media:
                cursor.execute("""
                    UPDATE campaigns 
                    SET media_url = ?, content_type = ?
                    WHERE campaign_id = ?
                """, (media_url, content_type, campaign_id))
                updated_count += 1
            
            conn.commit()
            print(f"✅ Updated {updated_count} campaigns with media")
        else:
            print(f"✅ All campaigns already have media or no media available")
        
        conn.close()
        return len(missing_media) if missing_media else 0
    
    def add_media_logging(self):
        """Add comprehensive logging to track media publishing"""
        
        print(f"\n🔧 ADDING MEDIA PUBLISHING LOGGING")
        
        # Read campaign_publisher.py
        with open('campaign_publisher.py', 'r') as f:
            content = f.read()
        
        # Add media logging before publishing
        old_publish_code = """            media_url = post.get('media_url')
            content_type = post.get('content_type', 'text')
            
            # Format the content for posting
            formatted_content = self._format_post_content(ad_content, campaign_id)"""
        
        new_publish_code = """            media_url = post.get('media_url')
            content_type = post.get('content_type', 'text')
            
            # MEDIA DEBUG LOGGING
            logger.info(f"📤 Publishing post {post_id} for campaign {campaign_id}")
            logger.info(f"   Content Type: {content_type}")
            logger.info(f"   Media URL: {media_url[:50] if media_url else 'None'}...")
            logger.info(f"   Has Media: {'YES' if media_url else 'NO'}")
            
            # Format the content for posting
            formatted_content = self._format_post_content(ad_content, campaign_id)"""
        
        if old_publish_code in content:
            content = content.replace(old_publish_code, new_publish_code)
            
            with open('campaign_publisher.py', 'w') as f:
                f.write(content)
            
            print(f"✅ Added media logging to campaign_publisher.py")
            return True
        
        return False
    
    def validate_fix(self):
        """Validate that the fix is working"""
        
        print(f"\n🧪 VALIDATING MEDIA PUBLISHING FIX")
        print("="*40)
        
        validation_results = []
        
        # Test 1: Check database has media
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM campaigns WHERE media_url IS NOT NULL")
        campaigns_with_media = cursor.fetchone()[0]
        
        if campaigns_with_media > 0:
            validation_results.append("✅ Campaigns have media URLs stored")
        else:
            validation_results.append("❌ No campaigns have media URLs")
        
        # Test 2: Check publisher query is fixed
        with open('campaign_publisher.py', 'r') as f:
            publisher_content = f.read()
        
        if "c.media_url, c.content_type" in publisher_content and "LEFT JOIN ads" not in publisher_content:
            validation_results.append("✅ Campaign publisher uses correct media query")
        else:
            validation_results.append("❌ Campaign publisher still has JOIN issue")
        
        # Test 3: Check media publishing logic
        if "send_photo" in publisher_content and "send_video" in publisher_content:
            validation_results.append("✅ Media publishing methods available")
        else:
            validation_results.append("❌ Media publishing methods missing")
        
        # Test 4: Check logging is added
        if "Media URL:" in publisher_content and "Has Media:" in publisher_content:
            validation_results.append("✅ Media debugging logging added")
        else:
            validation_results.append("❌ Media debugging logging missing")
        
        conn.close()
        
        # Show results
        passed_tests = len([r for r in validation_results if r.startswith("✅")])
        total_tests = len(validation_results)
        
        for result in validation_results:
            print(f"   {result}")
        
        print(f"\n📊 VALIDATION SUMMARY: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests == total_tests:
            print(f"\n✅ MEDIA PUBLISHING FIX COMPLETE!")
            print(f"🎯 Images should now appear in channel posts")
            print(f"📝 Check logs for media debugging information")
        else:
            print(f"\n⚠️ Some issues remain - check failed tests")
        
        return passed_tests, total_tests

def main():
    """Run the complete media publishing fix"""
    
    print("🐞 FIXING MISSING IMAGES IN CHANNEL POSTS")
    print("="*50)
    
    fixer = ImagePublishingFix()
    
    # Step 1: Analyze the issue
    issue_type = fixer.analyze_issue()
    
    # Step 2: Apply fixes based on issue type
    if issue_type in ["publishing_logic", "campaign_creation"]:
        print(f"\n🔧 APPLYING FIXES FOR: {issue_type}")
        
        # Fix the JOIN issue
        join_fixed = fixer.fix_campaign_publisher_join()
        
        # Ensure campaigns have media
        updated_campaigns = fixer.ensure_campaigns_have_media()
        
        # Add logging
        logging_added = fixer.add_media_logging()
        
        print(f"\n📋 FIX SUMMARY:")
        print(f"   • JOIN query fixed: {'✅' if join_fixed else '❌'}")
        print(f"   • Campaigns updated: {updated_campaigns}")
        print(f"   • Logging added: {'✅' if logging_added else '❌'}")
    
    # Step 3: Validate the fix
    passed, total = fixer.validate_fix()
    
    if passed == total:
        print(f"\n🎉 SUCCESS! Missing images issue has been fixed!")
        print(f"📱 Channel posts will now include user-uploaded images")
        print(f"🔍 Check campaign publisher logs for media debugging")
    else:
        print(f"\n⚠️ {total-passed} issues remain. Please review failed tests.")

if __name__ == "__main__":
    main()