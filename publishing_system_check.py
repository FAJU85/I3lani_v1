#!/usr/bin/env python3
"""
Publishing System Check
Comprehensive check of the publishing system to identify and fix issues
"""

import asyncio
import aiosqlite
import logging
from datetime import datetime, timedelta
from database import db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PublishingSystemChecker:
    def __init__(self):
        self.db_path = 'bot.db'
        self.issues = []
        self.fixes_applied = []
        
    async def comprehensive_check(self):
        """Perform comprehensive publishing system check"""
        
        print("🔍 PUBLISHING SYSTEM COMPREHENSIVE CHECK")
        print("=" * 50)
        
        results = {
            'database_check': await self._check_database_structure(),
            'post_status_check': await self._check_post_status(),
            'campaign_status_check': await self._check_campaign_status(),
            'publisher_process_check': await self._check_publisher_process(),
            'scheduling_check': await self._check_scheduling_system(),
            'error_analysis': await self._analyze_errors()
        }
        
        # Display results
        await self._display_results(results)
        
        # Apply fixes if needed
        if self.issues:
            await self._apply_fixes()
        
        return results
    
    async def _check_database_structure(self):
        """Check database structure for publishing system"""
        print("\n1. 🗄️  DATABASE STRUCTURE CHECK")
        print("-" * 30)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check if required tables exist
                required_tables = [
                    'campaign_posts',
                    'campaigns',
                    'channel_publishing_logs',
                    'publishing_status'
                ]
                
                existing_tables = []
                for table in required_tables:
                    try:
                        await cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                        result = await cursor.fetchone()
                        if result:
                            existing_tables.append(table)
                            print(f"   ✅ Table {table}: EXISTS")
                        else:
                            print(f"   ❌ Table {table}: MISSING")
                            self.issues.append(f"Missing table: {table}")
                    except Exception as e:
                        print(f"   ❌ Error checking table {table}: {e}")
                        self.issues.append(f"Error checking table {table}: {e}")
                
                # Check table structures
                for table in existing_tables:
                    await cursor.execute(f"PRAGMA table_info({table})")
                    columns = await cursor.fetchall()
                    print(f"   📊 {table}: {len(columns)} columns")
                
                return {
                    'status': 'healthy' if len(existing_tables) == len(required_tables) else 'issues',
                    'existing_tables': existing_tables,
                    'missing_tables': [t for t in required_tables if t not in existing_tables]
                }
                
        except Exception as e:
            print(f"   ❌ Database structure check error: {e}")
            self.issues.append(f"Database structure error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_post_status(self):
        """Check status of posts in the system"""
        print("\n2. 📋 POST STATUS CHECK")
        print("-" * 30)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Get post status counts
                await cursor.execute('''
                    SELECT status, COUNT(*) as count
                    FROM campaign_posts
                    GROUP BY status
                    ORDER BY count DESC
                ''')
                
                status_counts = await cursor.fetchall()
                
                total_posts = sum(count for _, count in status_counts)
                
                print(f"   📊 Total posts: {total_posts}")
                
                for status, count in status_counts:
                    percentage = (count / total_posts * 100) if total_posts > 0 else 0
                    print(f"   {self._get_status_icon(status)} {status}: {count} ({percentage:.1f}%)")
                
                # Check for stuck posts
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'scheduled' 
                    AND scheduled_time < datetime('now', '-1 hour')
                ''')
                
                stuck_posts = (await cursor.fetchone())[0]
                if stuck_posts > 0:
                    print(f"   ⚠️  Stuck posts (scheduled >1h ago): {stuck_posts}")
                    self.issues.append(f"{stuck_posts} posts stuck in scheduled status")
                
                # Check for posts due soon
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'scheduled'
                    AND scheduled_time BETWEEN datetime('now') AND datetime('now', '+10 minutes')
                ''')
                
                due_soon = (await cursor.fetchone())[0]
                print(f"   ⏰ Posts due in next 10 minutes: {due_soon}")
                
                return {
                    'status': 'healthy' if stuck_posts == 0 else 'issues',
                    'total_posts': total_posts,
                    'status_counts': dict(status_counts),
                    'stuck_posts': stuck_posts,
                    'due_soon': due_soon
                }
                
        except Exception as e:
            print(f"   ❌ Post status check error: {e}")
            self.issues.append(f"Post status error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_campaign_status(self):
        """Check status of campaigns"""
        print("\n3. 🎯 CAMPAIGN STATUS CHECK")
        print("-" * 30)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Get campaign status counts
                await cursor.execute('''
                    SELECT status, COUNT(*) as count
                    FROM campaigns
                    GROUP BY status
                    ORDER BY count DESC
                ''')
                
                campaign_counts = await cursor.fetchall()
                
                total_campaigns = sum(count for _, count in campaign_counts)
                
                print(f"   📊 Total campaigns: {total_campaigns}")
                
                for status, count in campaign_counts:
                    percentage = (count / total_campaigns * 100) if total_campaigns > 0 else 0
                    print(f"   {self._get_status_icon(status)} {status}: {count} ({percentage:.1f}%)")
                
                # Check for campaigns without posts
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaigns c
                    LEFT JOIN campaign_posts cp ON c.campaign_id = cp.campaign_id
                    WHERE cp.campaign_id IS NULL
                ''')
                
                campaigns_without_posts = (await cursor.fetchone())[0]
                if campaigns_without_posts > 0:
                    print(f"   ⚠️  Campaigns without posts: {campaigns_without_posts}")
                    self.issues.append(f"{campaigns_without_posts} campaigns have no posts")
                
                return {
                    'status': 'healthy' if campaigns_without_posts == 0 else 'issues',
                    'total_campaigns': total_campaigns,
                    'status_counts': dict(campaign_counts),
                    'campaigns_without_posts': campaigns_without_posts
                }
                
        except Exception as e:
            print(f"   ❌ Campaign status check error: {e}")
            self.issues.append(f"Campaign status error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_publisher_process(self):
        """Check if publisher process is running"""
        print("\n4. 🤖 PUBLISHER PROCESS CHECK")
        print("-" * 30)
        
        try:
            import os
            import psutil
            
            # Check if enhanced_campaign_publisher.py exists
            if os.path.exists('enhanced_campaign_publisher.py'):
                print("   ✅ Enhanced campaign publisher file exists")
            else:
                print("   ❌ Enhanced campaign publisher file missing")
                self.issues.append("Enhanced campaign publisher file missing")
                return {'status': 'error', 'error': 'Publisher file missing'}
            
            # Check if publisher is imported in main_bot.py
            try:
                with open('main_bot.py', 'r') as f:
                    main_content = f.read()
                    if 'enhanced_campaign_publisher' in main_content:
                        print("   ✅ Publisher imported in main_bot.py")
                    else:
                        print("   ❌ Publisher not imported in main_bot.py")
                        self.issues.append("Publisher not imported in main_bot.py")
            except Exception as e:
                print(f"   ❌ Error checking main_bot.py: {e}")
            
            # Check recent publishing activity
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'published'
                    AND published_time > datetime('now', '-1 hour')
                ''')
                
                recent_publishes = (await cursor.fetchone())[0]
                print(f"   📈 Recent publishes (last hour): {recent_publishes}")
                
                if recent_publishes == 0:
                    # Check if there are posts that should have been published
                    await cursor.execute('''
                        SELECT COUNT(*) FROM campaign_posts
                        WHERE status = 'scheduled'
                        AND scheduled_time < datetime('now', '-10 minutes')
                    ''')
                    
                    overdue_posts = (await cursor.fetchone())[0]
                    if overdue_posts > 0:
                        print(f"   ⚠️  Overdue posts not published: {overdue_posts}")
                        self.issues.append(f"Publisher may not be running - {overdue_posts} overdue posts")
                
                return {
                    'status': 'healthy' if recent_publishes > 0 or overdue_posts == 0 else 'issues',
                    'recent_publishes': recent_publishes,
                    'overdue_posts': overdue_posts if 'overdue_posts' in locals() else 0
                }
                
        except Exception as e:
            print(f"   ❌ Publisher process check error: {e}")
            self.issues.append(f"Publisher process error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _check_scheduling_system(self):
        """Check scheduling system"""
        print("\n5. ⏰ SCHEDULING SYSTEM CHECK")
        print("-" * 30)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check scheduling pattern
                await cursor.execute('''
                    SELECT 
                        DATE(scheduled_time) as date,
                        COUNT(*) as posts_count
                    FROM campaign_posts
                    WHERE status IN ('scheduled', 'published')
                    GROUP BY DATE(scheduled_time)
                    ORDER BY date DESC
                    LIMIT 7
                ''')
                
                daily_schedule = await cursor.fetchall()
                
                print("   📅 Daily scheduling pattern (last 7 days):")
                for date, count in daily_schedule:
                    print(f"      {date}: {count} posts")
                
                # Check for scheduling gaps
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'scheduled'
                    AND scheduled_time > datetime('now', '+7 days')
                ''')
                
                far_future_posts = (await cursor.fetchone())[0]
                if far_future_posts > 0:
                    print(f"   ⚠️  Posts scheduled >7 days ahead: {far_future_posts}")
                
                # Check for proper time intervals
                await cursor.execute('''
                    SELECT campaign_id, COUNT(*) as post_count,
                           MIN(scheduled_time) as first_post,
                           MAX(scheduled_time) as last_post
                    FROM campaign_posts
                    WHERE status IN ('scheduled', 'published')
                    GROUP BY campaign_id
                    HAVING post_count > 1
                    LIMIT 5
                ''')
                
                multi_post_campaigns = await cursor.fetchall()
                
                print(f"   📊 Multi-post campaigns: {len(multi_post_campaigns)}")
                
                return {
                    'status': 'healthy',
                    'daily_schedule': daily_schedule,
                    'far_future_posts': far_future_posts,
                    'multi_post_campaigns': len(multi_post_campaigns)
                }
                
        except Exception as e:
            print(f"   ❌ Scheduling system check error: {e}")
            self.issues.append(f"Scheduling system error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _analyze_errors(self):
        """Analyze publishing errors"""
        print("\n6. 🔍 ERROR ANALYSIS")
        print("-" * 30)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check for failed posts
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'failed'
                ''')
                
                failed_count = (await cursor.fetchone())[0]
                
                if failed_count > 0:
                    print(f"   ❌ Failed posts: {failed_count}")
                    
                    # Get recent failure reasons if available
                    await cursor.execute('''
                        SELECT campaign_id, channel_id, scheduled_time, error_message
                        FROM campaign_posts
                        WHERE status = 'failed'
                        ORDER BY scheduled_time DESC
                        LIMIT 5
                    ''')
                    
                    recent_failures = await cursor.fetchall()
                    
                    print("   📋 Recent failures:")
                    for campaign_id, channel_id, scheduled_time, error_msg in recent_failures:
                        print(f"      {campaign_id} -> {channel_id}: {error_msg or 'Unknown error'}")
                
                # Check publishing logs if available
                try:
                    await cursor.execute('''
                        SELECT COUNT(*) FROM channel_publishing_logs
                        WHERE status = 'error'
                        AND created_at > datetime('now', '-24 hours')
                    ''')
                    
                    recent_log_errors = (await cursor.fetchone())[0]
                    if recent_log_errors > 0:
                        print(f"   ⚠️  Recent publishing log errors: {recent_log_errors}")
                
                except Exception:
                    # Table might not exist
                    pass
                
                return {
                    'status': 'healthy' if failed_count == 0 else 'issues',
                    'failed_posts': failed_count,
                    'recent_failures': recent_failures if 'recent_failures' in locals() else []
                }
                
        except Exception as e:
            print(f"   ❌ Error analysis failed: {e}")
            self.issues.append(f"Error analysis error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _get_status_icon(self, status):
        """Get appropriate icon for status"""
        icons = {
            'scheduled': '⏰',
            'published': '✅',
            'failed': '❌',
            'active': '🟢',
            'completed': '✅',
            'cancelled': '❌'
        }
        return icons.get(status, '❓')
    
    async def _display_results(self, results):
        """Display comprehensive results"""
        print("\n" + "=" * 50)
        print("📊 PUBLISHING SYSTEM STATUS REPORT")
        print("=" * 50)
        
        # Calculate overall health
        healthy_components = sum(1 for r in results.values() if r.get('status') == 'healthy')
        total_components = len(results)
        
        health_score = (healthy_components / total_components * 100) if total_components > 0 else 0
        
        print(f"\n🏆 OVERALL HEALTH: {health_score:.1f}% ({healthy_components}/{total_components} components healthy)")
        
        if health_score >= 90:
            print("   🟢 EXCELLENT: Publishing system is working optimally")
        elif health_score >= 70:
            print("   🟡 GOOD: Publishing system is working with minor issues")
        elif health_score >= 50:
            print("   🟠 FAIR: Publishing system has some issues")
        else:
            print("   🔴 POOR: Publishing system has critical issues")
        
        # Component status
        print("\n📋 COMPONENT STATUS:")
        for component, data in results.items():
            status = data.get('status', 'unknown')
            icon = "✅" if status == 'healthy' else ("⚠️" if status == 'issues' else "❌")
            print(f"   {icon} {component.replace('_', ' ').title()}: {status.upper()}")
        
        # Issues summary
        if self.issues:
            print(f"\n⚠️  ISSUES FOUND ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n✅ NO ISSUES FOUND")
        
        # Recommendations
        print("\n🎯 RECOMMENDATIONS:")
        if health_score >= 90:
            print("   • System is operating optimally")
            print("   • Continue regular monitoring")
        elif health_score >= 70:
            print("   • Address minor issues to improve performance")
            print("   • Monitor publishing activity")
        else:
            print("   • Immediate attention required for critical issues")
            print("   • Check publisher process and database integrity")
            print("   • Review scheduling system")
    
    async def _apply_fixes(self):
        """Apply fixes for identified issues"""
        print("\n🔧 APPLYING FIXES")
        print("-" * 30)
        
        # Fix stuck posts
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Reset stuck posts to scheduled
                await cursor.execute('''
                    UPDATE campaign_posts
                    SET status = 'scheduled',
                        scheduled_time = datetime('now', '+1 minute')
                    WHERE status = 'scheduled'
                    AND scheduled_time < datetime('now', '-1 hour')
                ''')
                
                fixed_posts = cursor.rowcount
                if fixed_posts > 0:
                    print(f"   ✅ Reset {fixed_posts} stuck posts")
                    self.fixes_applied.append(f"Reset {fixed_posts} stuck posts")
                
                await conn.commit()
                
        except Exception as e:
            print(f"   ❌ Error applying fixes: {e}")
        
        # Display fixes applied
        if self.fixes_applied:
            print(f"\n✅ FIXES APPLIED ({len(self.fixes_applied)}):")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"   {i}. {fix}")

async def main():
    """Main function to run publishing system check"""
    checker = PublishingSystemChecker()
    results = await checker.comprehensive_check()
    
    # Save results
    import json
    with open('publishing_system_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Full report saved to: publishing_system_report.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())