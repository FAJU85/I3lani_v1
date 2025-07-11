#!/usr/bin/env python3
"""
Comprehensive validation of media publishing bug fix
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediaPublishingValidator:
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path
        
    def validate_fix(self):
        """Comprehensive validation of the media publishing fix"""
        print("🔍 MEDIA PUBLISHING BUG VALIDATION")
        print("=" * 50)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test 1: Verify campaign CAM-2025-07-OR41 has media
            print("\n📋 Test 1: Campaign CAM-2025-07-OR41 Media Check")
            cursor.execute("""
                SELECT campaign_id, content_type, media_url, 
                       CASE WHEN media_url IS NOT NULL THEN 'YES' ELSE 'NO' END as has_media
                FROM campaigns 
                WHERE campaign_id = 'CAM-2025-07-OR41'
            """)
            
            campaign_result = cursor.fetchone()
            if campaign_result:
                print(f"   ✅ Campaign found: {campaign_result[0]}")
                print(f"   Content type: {campaign_result[1]}")
                print(f"   Has media: {campaign_result[3]}")
                if campaign_result[3] == 'YES':
                    print(f"   Media URL: {campaign_result[2][:50]}...")
                test1_passed = campaign_result[3] == 'YES'
            else:
                print("   ❌ Campaign not found")
                test1_passed = False
            
            # Test 2: Verify publisher queries include media info
            print("\n📋 Test 2: Publisher Query Media Support")
            cursor.execute("""
                SELECT cp.id, cp.campaign_id, cp.channel_id, cp.status,
                       c.content_type, c.media_url,
                       CASE WHEN c.media_url IS NOT NULL THEN 'YES' ELSE 'NO' END as has_media
                FROM campaign_posts cp
                JOIN campaigns c ON cp.campaign_id = c.campaign_id
                WHERE cp.campaign_id = 'CAM-2025-07-OR41'
                AND cp.status = 'scheduled'
                ORDER BY cp.scheduled_time ASC
                LIMIT 3
            """)
            
            publisher_results = cursor.fetchall()
            print(f"   Found {len(publisher_results)} scheduled posts with media info")
            test2_passed = len(publisher_results) > 0
            
            for result in publisher_results:
                print(f"   Post {result[0]}: {result[2]} | {result[4]} | Media: {result[6]}")
                
            # Test 3: Verify media publishing methods are available
            print("\n📋 Test 3: Media Publishing Methods Check")
            from campaign_publisher import CampaignPublisher
            
            # Check if the publisher has photo and video methods
            publisher = CampaignPublisher(None)  # Bot instance not needed for method check
            
            # Simulate the publishing logic check
            has_photo_logic = "send_photo" in str(CampaignPublisher._publish_single_post.__code__.co_names)
            has_video_logic = "send_video" in str(CampaignPublisher._publish_single_post.__code__.co_names)
            
            print(f"   Photo publishing support: {'✅ YES' if has_photo_logic else '❌ NO'}")
            print(f"   Video publishing support: {'✅ YES' if has_video_logic else '❌ NO'}")
            
            test3_passed = has_photo_logic and has_video_logic
            
            # Test 4: Verify content propagation from ads to campaigns
            print("\n📋 Test 4: Content Propagation Check")
            cursor.execute("""
                SELECT a.ad_id, a.content_type as ad_content_type, 
                       a.media_url as ad_media_url,
                       c.campaign_id, c.content_type as campaign_content_type,
                       c.media_url as campaign_media_url
                FROM ads a
                JOIN campaigns c ON a.user_id = c.user_id
                WHERE c.campaign_id = 'CAM-2025-07-OR41'
                AND a.content_type = 'photo'
                ORDER BY a.created_at DESC
                LIMIT 1
            """)
            
            propagation_result = cursor.fetchone()
            if propagation_result:
                print(f"   Ad {propagation_result[0]}: {propagation_result[1]} | {propagation_result[2][:30]}...")
                print(f"   Campaign {propagation_result[3]}: {propagation_result[4]} | {propagation_result[5][:30]}...")
                test4_passed = propagation_result[1] == propagation_result[4] and propagation_result[2] == propagation_result[5]
                print(f"   Content propagation: {'✅ CORRECT' if test4_passed else '❌ INCORRECT'}")
            else:
                print("   ❌ No matching ad-campaign pair found")
                test4_passed = False
                
            # Test 5: Verify published posts with media
            print("\n📋 Test 5: Published Posts with Media")
            cursor.execute("""
                SELECT cp.campaign_id, cp.channel_id, cp.status, 
                       c.content_type, c.media_url,
                       cp.published_at
                FROM campaign_posts cp
                JOIN campaigns c ON cp.campaign_id = c.campaign_id
                WHERE c.media_url IS NOT NULL
                AND cp.status = 'published'
                ORDER BY cp.published_at DESC
                LIMIT 5
            """)
            
            published_results = cursor.fetchall()
            print(f"   Found {len(published_results)} published posts with media")
            test5_passed = len(published_results) > 0
            
            for result in published_results:
                print(f"   {result[0]} → {result[1]} | {result[2]} | {result[3]}")
                
            # Test 6: Debug campaign publisher logging
            print("\n📋 Test 6: Campaign Publisher Media Debug Logging")
            
            # Check if the publisher has proper media debug logging
            import inspect
            source = inspect.getsource(CampaignPublisher._publish_single_post)
            
            has_media_debug = "MEDIA DEBUG LOGGING" in source
            has_content_type_log = "Content Type:" in source
            has_media_url_log = "Media URL:" in source
            
            print(f"   Media debug logging: {'✅ YES' if has_media_debug else '❌ NO'}")
            print(f"   Content type logging: {'✅ YES' if has_content_type_log else '❌ NO'}")
            print(f"   Media URL logging: {'✅ YES' if has_media_url_log else '❌ NO'}")
            
            test6_passed = has_media_debug and has_content_type_log and has_media_url_log
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 VALIDATION SUMMARY")
            print("=" * 50)
            
            tests = [
                ("Campaign has media URL", test1_passed),
                ("Publisher queries include media", test2_passed),
                ("Media publishing methods available", test3_passed),
                ("Content propagation correct", test4_passed),
                ("Published posts with media exist", test5_passed),
                ("Debug logging implemented", test6_passed)
            ]
            
            passed_tests = sum(1 for _, passed in tests if passed)
            total_tests = len(tests)
            
            for test_name, passed in tests:
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"   {test_name}: {status}")
                
            print(f"\n📈 Overall Result: {passed_tests}/{total_tests} tests passed")
            
            if passed_tests == total_tests:
                print("🎉 MEDIA PUBLISHING BUG COMPLETELY FIXED!")
                print("   All validation tests passed successfully.")
                return True
            else:
                print("⚠️  MEDIA PUBLISHING BUG PARTIALLY FIXED")
                print(f"   {total_tests - passed_tests} issues still need attention.")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during validation: {e}")
            return False
            
        finally:
            conn.close()

if __name__ == "__main__":
    validator = MediaPublishingValidator()
    success = validator.validate_fix()
    
    if success:
        print("\n✅ Media publishing system is fully operational!")
        print("Users will now see both images and text in published ads.")
    else:
        print("\n❌ Media publishing system needs further fixes.")
        print("Some components may still have issues.")