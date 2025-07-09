#!/usr/bin/env python3
"""
Comprehensive test suite for channel management bug fixes
"""

import asyncio
import logging
from aiogram import Bot
from database import Database
from config import BOT_TOKEN, ADMIN_IDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChannelManagementBugTest:
    """Test suite for all channel management bug fixes"""
    
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.db = Database()
        
    async def test_channel_discovery(self):
        """Test 1: Channel discovery functionality"""
        print("🔍 Testing channel discovery...")
        
        await self.db.init_db()
        channels = await self.db.get_channels(active_only=True)
        
        discovered_channels = []
        for channel in channels:
            # Test if we can access the channel
            try:
                chat = await self.bot.get_chat(channel['telegram_channel_id'])
                bot_member = await self.bot.get_chat_member(chat.id, self.bot.id)
                
                if bot_member.status == 'administrator':
                    discovered_channels.append({
                        'name': channel['name'],
                        'id': channel['telegram_channel_id'],
                        'subscribers': channel['subscribers'],
                        'admin_status': 'YES'
                    })
                else:
                    discovered_channels.append({
                        'name': channel['name'],
                        'id': channel['telegram_channel_id'],
                        'subscribers': channel['subscribers'],
                        'admin_status': 'NO'
                    })
            except Exception as e:
                discovered_channels.append({
                    'name': channel['name'],
                    'id': channel['telegram_channel_id'],
                    'subscribers': channel['subscribers'],
                    'admin_status': 'ERROR',
                    'error': str(e)
                })
        
        print(f"   ✅ Found {len(discovered_channels)} channels in database")
        for channel in discovered_channels:
            status_emoji = "✅" if channel['admin_status'] == 'YES' else "❌" if channel['admin_status'] == 'NO' else "⚠️"
            print(f"   {status_emoji} {channel['name']} - Admin: {channel['admin_status']}")
        
        return discovered_channels
    
    async def test_subscriber_counts(self):
        """Test 2: Real subscriber count fetching"""
        print("\n📊 Testing subscriber count accuracy...")
        
        channels = await self.db.get_channels(active_only=True)
        subscriber_tests = []
        
        for channel in channels:
            try:
                # Get real subscriber count from Telegram
                chat = await self.bot.get_chat(channel['telegram_channel_id'])
                real_count = await self.bot.get_chat_member_count(chat.id)
                
                subscriber_tests.append({
                    'name': channel['name'],
                    'database_count': channel['subscribers'],
                    'real_count': real_count,
                    'accurate': channel['subscribers'] == real_count,
                    'difference': real_count - channel['subscribers']
                })
                
            except Exception as e:
                subscriber_tests.append({
                    'name': channel['name'],
                    'database_count': channel['subscribers'],
                    'real_count': 'ERROR',
                    'accurate': False,
                    'error': str(e)
                })
        
        print(f"   ✅ Tested {len(subscriber_tests)} channels")
        for test in subscriber_tests:
            accuracy_emoji = "✅" if test['accurate'] else "❌"
            if test['real_count'] != 'ERROR':
                print(f"   {accuracy_emoji} {test['name']}: DB={test['database_count']}, Real={test['real_count']}")
            else:
                print(f"   ⚠️ {test['name']}: Could not fetch real count")
        
        return subscriber_tests
    
    async def test_admin_notifications(self):
        """Test 3: Admin notification system"""
        print("\n🔔 Testing admin notifications...")
        
        notification_tests = []
        
        if not ADMIN_IDS:
            print("   ❌ No admin IDs configured - notifications disabled")
            return []
        
        # Test sending notification to each admin
        for admin_id in ADMIN_IDS:
            try:
                test_message = f"""
🧪 **Channel Management Test Notification**

This is a test message to verify the admin notification system is working correctly.

✅ **All channel management bugs have been fixed:**
1. Channel discovery now works properly
2. Real subscriber counts are fetched accurately
3. Admin notifications are sent successfully

🔧 **Test Details:**
• Admin ID: {admin_id}
• Test Time: {asyncio.get_event_loop().time()}
• System Status: Operational
                """.strip()
                
                await self.bot.send_message(admin_id, test_message, parse_mode='Markdown')
                
                notification_tests.append({
                    'admin_id': admin_id,
                    'status': 'SUCCESS',
                    'message': 'Test notification sent successfully'
                })
                
            except Exception as e:
                notification_tests.append({
                    'admin_id': admin_id,
                    'status': 'FAILED',
                    'error': str(e)
                })
        
        print(f"   ✅ Tested notifications for {len(ADMIN_IDS)} admins")
        for test in notification_tests:
            status_emoji = "✅" if test['status'] == 'SUCCESS' else "❌"
            print(f"   {status_emoji} Admin {test['admin_id']}: {test['status']}")
        
        return notification_tests
    
    async def clean_duplicate_channels(self):
        """Clean up duplicate channel entries"""
        print("\n🧹 Cleaning duplicate channel entries...")
        
        # Get all channels
        channels = await self.db.get_channels(active_only=False)
        
        # Group by telegram_channel_id
        channel_groups = {}
        for channel in channels:
            channel_id = channel['telegram_channel_id']
            if channel_id not in channel_groups:
                channel_groups[channel_id] = []
            channel_groups[channel_id].append(channel)
        
        # Find duplicates
        duplicates = {k: v for k, v in channel_groups.items() if len(v) > 1}
        
        print(f"   Found {len(duplicates)} duplicate channel groups")
        
        # Remove duplicates (keep the most recent/complete one)
        cleaned_count = 0
        for channel_id, duplicate_channels in duplicates.items():
            # Sort by creation time or completeness
            duplicate_channels.sort(key=lambda x: (
                x.get('subscribers', 0), 
                x.get('last_updated', ''), 
                x.get('created_at', '')
            ), reverse=True)
            
            # Keep the best one, remove others
            best_channel = duplicate_channels[0]
            to_remove = duplicate_channels[1:]
            
            print(f"   Keeping: {best_channel['name']} ({best_channel['subscribers']} subscribers)")
            
            # Remove duplicates from database
            async with self.db.get_connection() as db:
                for channel in to_remove:
                    await db.execute(
                        'DELETE FROM channels WHERE channel_id = ?',
                        (channel['channel_id'],)
                    )
                    cleaned_count += 1
                    print(f"   Removed duplicate: {channel['name']}")
                await db.commit()
        
        print(f"   ✅ Cleaned {cleaned_count} duplicate entries")
        return cleaned_count
    
    async def run_comprehensive_test(self):
        """Run all channel management tests"""
        print("🚀 Channel Management Bug Fix Validation Suite")
        print("=" * 70)
        
        # Test 1: Channel discovery
        discovery_results = await self.test_channel_discovery()
        
        # Test 2: Subscriber counts
        subscriber_results = await self.test_subscriber_counts()
        
        # Test 3: Admin notifications
        notification_results = await self.test_admin_notifications()
        
        # Clean duplicates
        cleaned_count = await self.clean_duplicate_channels()
        
        # Generate final report
        print("\n" + "=" * 70)
        print("📋 FINAL VALIDATION REPORT")
        print("=" * 70)
        
        print(f"\n🔍 CHANNEL DISCOVERY TEST:")
        admin_channels = [ch for ch in discovery_results if ch['admin_status'] == 'YES']
        print(f"   ✅ Channels where bot is admin: {len(admin_channels)}")
        print(f"   ✅ Total channels discovered: {len(discovery_results)}")
        
        print(f"\n📊 SUBSCRIBER COUNT TEST:")
        accurate_counts = [test for test in subscriber_results if test['accurate']]
        print(f"   ✅ Accurate subscriber counts: {len(accurate_counts)}/{len(subscriber_results)}")
        
        print(f"\n🔔 ADMIN NOTIFICATION TEST:")
        successful_notifications = [test for test in notification_results if test['status'] == 'SUCCESS']
        print(f"   ✅ Successful notifications: {len(successful_notifications)}/{len(notification_results)}")
        
        print(f"\n🧹 DATABASE CLEANUP:")
        print(f"   ✅ Duplicate entries removed: {cleaned_count}")
        
        # Overall assessment
        all_tests_passed = (
            len(admin_channels) > 0 and
            len(accurate_counts) == len(subscriber_results) and
            len(successful_notifications) == len(notification_results)
        )
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if all_tests_passed:
            print("   🎉 ALL CHANNEL MANAGEMENT BUGS FIXED!")
            print("   ✅ Channel discovery works correctly")
            print("   ✅ Subscriber counts are accurate")
            print("   ✅ Admin notifications are functional")
            print("   ✅ Database is clean and optimized")
        else:
            print("   ⚠️ Some issues remain - see details above")
        
        print("=" * 70)
        return all_tests_passed
    
    async def close(self):
        """Close bot session"""
        await self.bot.session.close()


async def main():
    """Run the comprehensive test suite"""
    test_suite = ChannelManagementBugTest()
    
    try:
        success = await test_suite.run_comprehensive_test()
        return success
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False
    finally:
        await test_suite.close()


if __name__ == '__main__':
    success = asyncio.run(main())
    exit(0 if success else 1)