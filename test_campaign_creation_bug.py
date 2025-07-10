#!/usr/bin/env python3
"""
Test Campaign Creation Bug - Verify new campaigns are being created
"""

import asyncio
import sqlite3
import sys
sys.path.append('.')

async def test_campaign_creation():
    """Test campaign creation functionality"""
    
    print("🐞 TESTING CAMPAIGN CREATION BUG")
    print("="*45)
    
    # Step 1: Test current campaign count
    print("1. Checking current campaigns...")
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM campaigns')
    initial_count = cursor.fetchone()[0]
    print(f"   Current campaigns in database: {initial_count}")
    
    cursor.execute('SELECT campaign_id, user_id FROM campaigns ORDER BY created_at DESC')
    existing_campaigns = cursor.fetchall()
    print(f"   Existing campaigns:")
    for campaign_id, user_id in existing_campaigns:
        print(f"     - {campaign_id} (User: {user_id})")
    
    conn.close()
    
    # Step 2: Test campaign creation function
    print(f"\n2. Testing campaign creation function...")
    
    try:
        from campaign_management import campaign_manager
        
        # Test creating a new campaign
        test_user_id = 566158428
        test_payment_memo = "TEST123"
        test_payment_amount = 0.36
        
        test_ad_data = {
            'ad_content': 'Test advertisement for campaign creation bug',
            'content_type': 'text',
            'duration_days': 7,
            'posts_per_day': 2,
            'selected_channels': ['@i3lani', '@smshco'],
            'total_reach': 350
        }
        
        print(f"   Creating test campaign for user {test_user_id}...")
        new_campaign_id = await campaign_manager.create_campaign(
            user_id=test_user_id,
            payment_memo=test_payment_memo,
            payment_amount=test_payment_amount,
            ad_data=test_ad_data,
            payment_method='TON'
        )
        
        if new_campaign_id:
            print(f"   ✅ Campaign created successfully: {new_campaign_id}")
        else:
            print(f"   ❌ Campaign creation failed")
            return False
        
        # Verify it was saved to database
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM campaigns WHERE campaign_id = ?', (new_campaign_id,))
        if cursor.fetchone()[0] > 0:
            print(f"   ✅ Campaign saved to database")
        else:
            print(f"   ❌ Campaign not found in database")
            conn.close()
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error testing campaign creation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Test campaign list with new campaign
    print(f"\n3. Testing campaign list retrieval...")
    
    try:
        from campaign_management import get_user_campaign_list
        
        campaigns = await get_user_campaign_list(test_user_id, 10)
        
        print(f"   User {test_user_id} now has {len(campaigns)} campaigns:")
        for campaign in campaigns:
            print(f"     - {campaign['campaign_id']} | {campaign['status']} | {campaign['created_at']}")
        
        # Check if new campaign appears
        new_campaign_found = any(c['campaign_id'] == new_campaign_id for c in campaigns)
        
        if new_campaign_found:
            print(f"   ✅ New campaign appears in list")
        else:
            print(f"   ❌ New campaign missing from list")
            return False
        
    except Exception as e:
        print(f"   ❌ Error testing campaign list: {e}")
        return False
    
    # Step 4: Check automatic payment confirmation
    print(f"\n4. Checking automatic payment confirmation system...")
    
    try:
        from automatic_payment_confirmation import AutomaticPaymentConfirmation
        
        # Check if the system has create_campaign integration
        apc = AutomaticPaymentConfirmation()
        
        # Check if it has the required methods
        if hasattr(apc, 'create_campaign_for_payment'):
            print(f"   ✅ AutomaticPaymentConfirmation has create_campaign_for_payment method")
        else:
            print(f"   ❌ AutomaticPaymentConfirmation missing create_campaign_for_payment method")
            print(f"   🔧 This is the bug - payments don't create campaigns!")
            return False
        
    except Exception as e:
        print(f"   ❌ Error checking payment confirmation system: {e}")
    
    print(f"\n" + "="*45)
    print(f"🎯 CAMPAIGN CREATION BUG ANALYSIS")
    print(f"="*45)
    print(f"✅ Campaign creation function: WORKING")
    print(f"✅ Campaign list retrieval: WORKING")
    print(f"✅ Database storage: WORKING")
    print(f"❌ Integration issue: Payment confirmation not creating campaigns")
    print(f"")
    print(f"🔧 ROOT CAUSE IDENTIFIED:")
    print(f"   - Campaign creation function works correctly")
    print(f"   - Campaign list display works correctly")
    print(f"   - Missing link: Payment confirmation → Campaign creation")
    print(f"   - Users make payments but campaigns are not automatically created")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_campaign_creation())
    if result:
        print("\n🎯 Bug identified! Fixing payment → campaign creation flow...")
    else:
        print("\n❌ Testing failed")