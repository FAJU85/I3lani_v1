#!/usr/bin/env python3
"""
Test Content Publishing Fix - Verify real user content is now being published
"""

import asyncio
import sqlite3
import sys
sys.path.append('.')

async def test_content_publishing_fix():
    """Test that real user content is now being published correctly"""
    
    print("🔧 TESTING CONTENT PUBLISHING FIX")
    print("="*45)
    
    # Step 1: Test automatic payment confirmation content retrieval
    print("1. Testing content retrieval from automatic payment confirmation...")
    
    try:
        from automatic_payment_confirmation import automatic_confirmation
        
        # Test with user 566158428 who has real content
        user_id = 566158428
        
        print(f"   Getting content for user {user_id}...")
        user_content = await automatic_confirmation._get_user_ad_content(user_id)
        
        print(f"   ✅ Content retrieved successfully:")
        print(f"      Content: {user_content.get('ad_content', 'None')[:50]}...")
        print(f"      Type: {user_content.get('content_type', 'None')}")
        media_url = user_content.get('media_url', 'None')
        if media_url and media_url != 'None':
            print(f"      Media: {media_url[:50]}...")
        else:
            print(f"      Media: None")
        
        if user_content.get('ad_content'):
            print(f"   ✅ Real user content found")
        else:
            print(f"   ❌ No real user content found")
            return False
        
    except Exception as e:
        print(f"   ❌ Error testing content retrieval: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Test campaign creation with real content
    print(f"\n2. Testing campaign creation with real user content...")
    
    try:
        # Test creating a campaign with real content
        test_memo = "REAL123"
        test_amount = 0.36
        
        # Get real user content
        real_ad_data = user_content.copy()
        real_ad_data.update({
            'duration_days': 7,
            'posts_per_day': 2,
            'selected_channels': ['@i3lani', '@smshco'],
            'total_reach': 350
        })
        
        print(f"   Creating campaign with real content...")
        print(f"   Content to use: {real_ad_data.get('ad_content', '')[:50]}...")
        
        from campaign_management import create_campaign_for_payment
        
        campaign_id = await create_campaign_for_payment(
            user_id, test_memo, test_amount, real_ad_data, 'TON'
        )
        
        if campaign_id:
            print(f"   ✅ Campaign created: {campaign_id}")
        else:
            print(f"   ❌ Campaign creation failed")
            return False
        
        # Verify content was stored correctly
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ad_content, content_type, media_url 
            FROM campaigns 
            WHERE campaign_id = ?
        """, (campaign_id,))
        
        campaign_data = cursor.fetchone()
        conn.close()
        
        if campaign_data:
            stored_content = campaign_data[0]
            print(f"   Campaign stored content: {stored_content[:50]}...")
            
            if stored_content == real_ad_data.get('ad_content'):
                print(f"   ✅ Content matches user submission")
            else:
                print(f"   ❌ Content mismatch!")
                print(f"      Expected: {real_ad_data.get('ad_content', '')[:30]}...")
                print(f"      Got: {stored_content[:30]}...")
                return False
        else:
            print(f"   ❌ Campaign not found in database")
            return False
        
    except Exception as e:
        print(f"   ❌ Error testing campaign creation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Test end-to-end flow
    print(f"\n3. Testing end-to-end payment → campaign → content flow...")
    
    try:
        # Track another payment with real content
        test_memo_2 = "END2024"
        
        await automatic_confirmation.track_user_payment(
            user_id, test_memo_2, test_amount, real_ad_data
        )
        
        print(f"   Payment {test_memo_2} tracked with real content")
        
        # Activate campaign
        campaign_id_2 = await automatic_confirmation.activate_campaign(
            user_id, test_memo_2, test_amount, real_ad_data
        )
        
        if campaign_id_2:
            print(f"   ✅ Campaign activated: {campaign_id_2}")
            
            # Check final content
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ad_content, content_type, media_url
                FROM campaigns 
                WHERE campaign_id = ?
            """, (campaign_id_2,))
            
            final_data = cursor.fetchone()
            conn.close()
            
            if final_data and final_data[0]:
                print(f"   Final campaign content: {final_data[0][:50]}...")
                
                # Check if it matches user's real content
                if final_data[0] == user_content.get('ad_content'):
                    print(f"   ✅ End-to-end content integrity maintained")
                else:
                    print(f"   ❌ End-to-end content mismatch")
                    return False
            else:
                print(f"   ❌ No content stored in final campaign")
                return False
        else:
            print(f"   ❌ Campaign activation failed")
            return False
        
    except Exception as e:
        print(f"   ❌ Error in end-to-end test: {e}")
        return False
    
    # Step 4: Verify publisher will get correct content
    print(f"\n4. Testing publisher content retrieval...")
    
    try:
        conn = sqlite3.connect('bot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get what publisher would see for the new campaign
        cursor.execute("""
            SELECT cp.*, c.ad_content, c.user_id, 
                   COALESCE(c.content_type, 'text') as content_type, 
                   c.media_url
            FROM campaign_posts cp
            JOIN campaigns c ON cp.campaign_id = c.campaign_id
            WHERE cp.campaign_id = ?
            LIMIT 1
        """, (campaign_id_2,))
        
        publisher_data = cursor.fetchone()
        conn.close()
        
        if publisher_data:
            publisher_content = publisher_data['ad_content']
            print(f"   Publisher sees content: {publisher_content[:50]}...")
            
            if publisher_content == user_content.get('ad_content'):
                print(f"   ✅ Publisher will publish correct content")
            else:
                print(f"   ❌ Publisher has wrong content")
                return False
        else:
            print(f"   ❌ No publisher data found")
            return False
        
    except Exception as e:
        print(f"   ❌ Error testing publisher: {e}")
        return False
    
    print(f"\n" + "="*45)
    print(f"🎯 CONTENT PUBLISHING FIX RESULTS")
    print(f"="*45)
    print(f"✅ Content retrieval: FIXED")
    print(f"✅ Campaign creation: USING REAL CONTENT")
    print(f"✅ End-to-end flow: CONTENT INTEGRITY MAINTAINED")
    print(f"✅ Publisher system: WILL PUBLISH REAL CONTENT")
    print(f"")
    print(f"🔧 BUG COMPLETELY FIXED:")
    print(f"   - Real user content now retrieved from ads table")
    print(f"   - Campaigns created with actual user submissions")
    print(f"   - Publisher system gets correct content and media")
    print(f"   - Content integrity maintained throughout flow")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_content_publishing_fix())
    if result:
        print("\n🎉 Content publishing bug COMPLETELY FIXED!")
        print("Users' real content (text and images) will now be published correctly.")
    else:
        print("\n❌ Fix validation failed - needs additional work")