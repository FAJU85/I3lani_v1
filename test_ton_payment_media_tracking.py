#!/usr/bin/env python3
"""Test TON Payment Media Tracking - Simulates complete payment flow with media"""

import asyncio
import sqlite3
import json
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# Initialize storage
storage = MemoryStorage()

async def test_ton_payment_media_tracking():
    """Test complete TON payment flow with media tracking"""
    print("🧪 Testing TON Payment Media Tracking")
    print("=" * 50)
    
    # Test user and media details
    test_user_id = 777777777
    test_media_url = "AgACAgQAAxkBAAITestMediaURL123456789"
    test_ad_content = "Test ad with media content"
    test_content_type = "photo"
    
    # Create FSM context for the test user
    state = FSMContext(storage=storage, key=(test_user_id, test_user_id))
    
    # Set state data simulating a complete ad creation flow
    await state.set_data({
        'ad_text': test_ad_content,
        'content_type': test_content_type,
        'photos': [test_media_url],
        'selected_channels': ['@i3lani', '@smshco'],
        'days': 7,
        'posts_per_day': 2,
        'pricing_calculation': {
            'days': 7,
            'posts_per_day': 2,
            'total_posts': 14,
            'total_reach': 341,
            'total_usd': 2.52,
            'total_ton': 0.36
        }
    })
    
    print(f"✅ Set up test state with media URL: {test_media_url[:30]}...")
    
    # Test automatic payment confirmation tracking
    try:
        from automatic_payment_confirmation import track_payment_for_user
        
        # Create test payment memo
        test_memo = f"TEST{datetime.now().strftime('%H%M%S')}"
        test_amount = 0.36
        
        # Create ad_data with media information (as done in handlers.py)
        ad_data = {
            'duration_days': 7,
            'posts_per_day': 2,
            'selected_channels': ['@i3lani', '@smshco'],
            'total_reach': 341,
            'ad_content': test_ad_content,
            'content_type': test_content_type,
            'media_url': test_media_url
        }
        
        print(f"\n📝 Tracking payment with memo: {test_memo}")
        print(f"   Content type: {ad_data['content_type']}")
        print(f"   Has media: {bool(ad_data['media_url'])}")
        
        # Track the payment
        success = await track_payment_for_user(test_user_id, test_memo, test_amount, ad_data)
        
        if success:
            print(f"✅ Payment tracking successful")
            
            # Verify in database
            conn = sqlite3.connect('bot.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT memo, user_id, amount, ad_data, status
                FROM payment_memo_tracking
                WHERE memo = ?
            """, (test_memo,))
            
            tracking = cursor.fetchone()
            if tracking:
                print(f"\n🔍 Database verification:")
                print(f"   Memo: {tracking['memo']}")
                print(f"   User ID: {tracking['user_id']}")
                print(f"   Amount: {tracking['amount']}")
                print(f"   Status: {tracking['status']}")
                
                if tracking['ad_data']:
                    try:
                        saved_ad_data = json.loads(tracking['ad_data'])
                        print(f"\n📦 Saved ad_data:")
                        print(f"   Content type: {saved_ad_data.get('content_type', 'Not saved')}")
                        print(f"   Has media URL: {bool(saved_ad_data.get('media_url'))}")
                        print(f"   Media URL: {saved_ad_data.get('media_url', 'None')[:30]}..." if saved_ad_data.get('media_url') else "   Media URL: None")
                        print(f"   Ad content: {saved_ad_data.get('ad_content', 'None')[:50]}...")
                    except:
                        print(f"   ❌ Failed to parse ad_data JSON")
            else:
                print(f"   ❌ Payment tracking not found in database")
            
            conn.close()
        else:
            print(f"❌ Payment tracking failed")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ TON payment media tracking test completed")

if __name__ == "__main__":
    asyncio.run(test_ton_payment_media_tracking())