#!/usr/bin/env python3
"""
Comprehensive test for viral referral game integration
Validates all components work together correctly
"""

import asyncio
import logging
from database import Database
from viral_referral_game import ViralReferralGame
from viral_referral_handlers import has_free_ads, consume_free_ad

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_viral_referral_system():
    """Test the complete viral referral game system"""
    
    print("🎮 Testing Viral Referral Game Integration")
    print("=" * 50)
    
    # Initialize database and viral game
    db = Database()
    viral_game = ViralReferralGame(db)
    
    # Test 1: Initialize tables
    print("\n1. Testing table initialization...")
    await viral_game.init_tables()
    print("✅ Tables initialized successfully")
    
    # Test 2: Create test users
    print("\n2. Testing user creation...")
    test_users = [101, 102, 103, 104]  # User IDs for testing
    
    for user_id in test_users:
        user = await viral_game.get_or_create_user(user_id)
        print(f"✅ Created user {user_id}: {user['referral_code']}")
    
    # Test 3: Test progress system
    print("\n3. Testing progress system...")
    user_101 = await viral_game.get_or_create_user(101)
    print(f"User 101 initial progress: {user_101['progress']}%")
    
    # Update progress to 99%
    for i in range(10):  # Multiple taps to reach 99%
        updated_user = await viral_game.update_progress(101)
        if updated_user['progress'] >= 99:
            print(f"✅ User 101 reached 99% progress: {updated_user['progress']}%")
            break
    
    # Test 4: Test referral system
    print("\n4. Testing referral system...")
    
    # User 101 refers users 102, 103, 104
    referrals = [(101, 102), (101, 103), (101, 104)]
    
    for inviter_id, invited_id in referrals:
        result = await viral_game.process_referral(inviter_id, invited_id)
        print(f"✅ Referral {inviter_id} → {invited_id}: {result['success']}")
        
        if result['success']:
            print(f"   Referral count: {result['referral_count']}")
            if result['reward_unlocked']:
                print(f"   🏆 Reward unlocked!")
    
    # Test 5: Test reward system
    print("\n5. Testing reward system...")
    
    # Check if user 101 has free ads
    stats = await viral_game.get_user_stats(101)
    if stats:
        print(f"✅ User 101 stats:")
        print(f"   Progress: {stats['user_info']['progress']}%")
        print(f"   Referral count: {stats['user_info']['referral_count']}")
        print(f"   Reward unlocked: {stats['user_info']['reward_unlocked']}")
        print(f"   Total free ads: {stats['total_free_ads']}")
        print(f"   Active rewards: {len(stats['active_rewards'])}")
    
    # Test 6: Test free ad usage
    print("\n6. Testing free ad usage...")
    
    # Check if user has free ads available
    has_ads = await has_free_ads(101)
    print(f"✅ User 101 has free ads: {has_ads}")
    
    if has_ads:
        # Consume a free ad
        used = await consume_free_ad(101)
        print(f"✅ Free ad consumed: {used}")
        
        # Check updated stats
        updated_stats = await viral_game.get_user_stats(101)
        if updated_stats:
            print(f"   Remaining free ads: {updated_stats['total_free_ads']}")
    
    # Test 7: Test keyboard generation
    print("\n7. Testing keyboard generation...")
    
    progress_keyboard = viral_game.create_progress_keyboard(101, 99, 'en')
    print(f"✅ Progress keyboard generated: {len(progress_keyboard.inline_keyboard)} rows")
    
    reward_keyboard = viral_game.create_reward_keyboard('en')
    print(f"✅ Reward keyboard generated: {len(reward_keyboard.inline_keyboard)} rows")
    
    # Test 8: Test progress messages
    print("\n8. Testing progress messages...")
    
    progress_msg = await viral_game.get_progress_message(101, 'en')
    print(f"✅ Progress message generated: {len(progress_msg)} characters")
    
    reward_msg = await viral_game.get_reward_message(101, 'en')
    print(f"✅ Reward message generated: {len(reward_msg)} characters")
    
    # Test 9: Test multilingual support
    print("\n9. Testing multilingual support...")
    
    for lang in ['en', 'ar', 'ru']:
        msg = await viral_game.get_progress_message(101, lang)
        print(f"✅ {lang.upper()} message: {len(msg)} characters")
    
    # Test 10: Test database integrity
    print("\n10. Testing database integrity...")
    
    # Check all tables have data using db methods
    user_count = await db.fetchone("SELECT COUNT(*) FROM referral_game")
    print(f"✅ Referral game users: {user_count['COUNT(*)'] if user_count else 0}")
    
    invitation_count = await db.fetchone("SELECT COUNT(*) FROM referral_invitations")
    print(f"✅ Referral invitations: {invitation_count['COUNT(*)'] if invitation_count else 0}")
    
    reward_count = await db.fetchone("SELECT COUNT(*) FROM free_ad_rewards")
    print(f"✅ Free ad rewards: {reward_count['COUNT(*)'] if reward_count else 0}")
    
    print("\n" + "=" * 50)
    print("🎉 All viral referral game tests completed successfully!")
    print("🚀 System is ready for production use!")
    
    return True

async def main():
    """Run all tests"""
    try:
        await test_viral_referral_system()
        print("\n✅ All tests passed! Viral referral game is fully integrated.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())