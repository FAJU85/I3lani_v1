#!/usr/bin/env python3
"""
Test Campaign Creation Fix - Verify payment → campaign creation works
"""

import asyncio
import sqlite3
import sys
sys.path.append('.')

async def test_payment_campaign_creation():
    """Test that payments now create campaigns correctly"""
    
    print("🔧 TESTING CAMPAIGN CREATION FIX")
    print("="*45)
    
    # Step 1: Count current campaigns
    print("1. Checking initial campaign count...")
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM campaigns WHERE user_id = 566158428')
    initial_count = cursor.fetchone()[0]
    print(f"   User 566158428 has {initial_count} campaigns initially")
    
    conn.close()
    
    # Step 2: Test automatic payment confirmation with campaign creation
    print(f"\n2. Testing automatic payment confirmation...")
    
    try:
        from automatic_payment_confirmation import automatic_confirmation
        
        # Initialize system
        await automatic_confirmation.init_tables()
        print(f"   ✅ Payment confirmation system initialized")
        
        # Test user data
        test_user_id = 566158428
        test_memo = "FIX456"
        test_amount = 0.36
        
        test_ad_data = {
            'ad_content': 'Fixed campaign creation test ad',
            'content_type': 'text',
            'duration_days': 7,
            'posts_per_day': 2,
            'selected_channels': ['@i3lani', '@smshco'],
            'total_reach': 350
        }
        
        # Track payment
        print(f"   Tracking payment {test_memo} for user {test_user_id}...")
        track_success = await automatic_confirmation.track_user_payment(
            test_user_id, test_memo, test_amount, test_ad_data
        )
        
        if track_success:
            print(f"   ✅ Payment tracked successfully")
        else:
            print(f"   ❌ Payment tracking failed")
            return False
        
        # Find user by memo
        print(f"   Finding user by memo {test_memo}...")
        user_data = await automatic_confirmation.find_user_by_memo(test_memo)
        
        if user_data:
            print(f"   ✅ User found: {user_data['user_id']}")
        else:
            print(f"   ❌ User not found for memo")
            return False
        
        # Test campaign creation through payment confirmation
        print(f"   Testing campaign creation...")
        campaign_id = await automatic_confirmation.activate_campaign(
            test_user_id, test_memo, test_amount, test_ad_data
        )
        
        if campaign_id:
            print(f"   ✅ Campaign created: {campaign_id}")
        else:
            print(f"   ❌ Campaign creation failed")
            return False
        
    except Exception as e:
        print(f"   ❌ Error testing payment confirmation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Verify new campaign appears in list
    print(f"\n3. Verifying campaign appears in user list...")
    
    try:
        from campaign_management import get_user_campaign_list
        
        campaigns = await get_user_campaign_list(test_user_id, 10)
        
        print(f"   User {test_user_id} now has {len(campaigns)} campaigns:")
        for campaign in campaigns[-3:]:  # Show last 3
            print(f"     - {campaign['campaign_id']} | {campaign['status']} | {campaign['created_at']}")
        
        # Check if our test campaign appears
        test_campaign_found = any(c['campaign_id'] == campaign_id for c in campaigns)
        
        if test_campaign_found:
            print(f"   ✅ New campaign {campaign_id} appears in list")
        else:
            print(f"   ❌ New campaign missing from list")
            return False
        
        # Check campaign count increased
        final_count = len(campaigns)
        if final_count > initial_count:
            print(f"   ✅ Campaign count increased: {initial_count} → {final_count}")
        else:
            print(f"   ❌ Campaign count did not increase")
            return False
        
    except Exception as e:
        print(f"   ❌ Error checking campaign list: {e}")
        return False
    
    # Step 4: Test end-to-end payment processing
    print(f"\n4. Testing end-to-end payment processing...")
    
    try:
        from automatic_payment_confirmation import process_detected_payment
        
        # Simulate payment detection and processing
        test_memo_2 = "END789"
        test_amount_2 = 0.36
        
        # First track another payment
        await automatic_confirmation.track_user_payment(
            test_user_id, test_memo_2, test_amount_2, test_ad_data
        )
        
        # Then process it (simulate payment scanner finding it)
        print(f"   Processing detected payment {test_memo_2}...")
        process_success = await process_detected_payment(test_memo_2, test_amount_2)
        
        if process_success:
            print(f"   ✅ End-to-end processing successful")
        else:
            print(f"   ❌ End-to-end processing failed")
            return False
        
        # Check final campaign list
        final_campaigns = await get_user_campaign_list(test_user_id, 10)
        final_count = len(final_campaigns)
        
        print(f"   Final campaign count: {final_count}")
        print(f"   Latest campaigns:")
        for campaign in final_campaigns[-2:]:  # Show last 2
            print(f"     - {campaign['campaign_id']} | {campaign['payment_memo']}")
        
    except Exception as e:
        print(f"   ❌ Error testing end-to-end processing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n" + "="*45)
    print(f"🎯 CAMPAIGN CREATION FIX RESULTS")
    print(f"="*45)
    print(f"✅ Payment tracking: WORKING")
    print(f"✅ Campaign creation: WORKING")  
    print(f"✅ Campaign list display: WORKING")
    print(f"✅ End-to-end payment processing: WORKING")
    print(f"")
    print(f"🔧 BUG FIXED:")
    print(f"   - Payments now automatically create campaigns")
    print(f"   - New campaigns appear in user's campaign list")
    print(f"   - Campaign count properly increases with payments")
    print(f"   - Full payment → campaign → display flow operational")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_payment_campaign_creation())
    if result:
        print("\n🎉 Campaign creation bug FIXED!")
        print("Users will now see new campaigns when they make payments.")
    else:
        print("\n❌ Fix failed - needs additional work")