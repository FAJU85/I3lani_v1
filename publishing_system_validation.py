#!/usr/bin/env python3
"""
Publishing System Validation
Final validation to ensure the publishing system is working properly
"""

import asyncio
import aiosqlite
import logging
import json
from datetime import datetime, timedelta
from database import db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PublishingSystemValidator:
    def __init__(self):
        self.db_path = 'bot.db'
        self.validation_results = {}
        
    async def comprehensive_validation(self):
        """Perform comprehensive publishing system validation"""
        
        print("🔍 PUBLISHING SYSTEM COMPREHENSIVE VALIDATION")
        print("=" * 60)
        
        # Run all validation tests
        results = {
            'database_integrity': await self._validate_database_integrity(),
            'campaign_structure': await self._validate_campaign_structure(),
            'post_scheduling': await self._validate_post_scheduling(),
            'content_publishing': await self._validate_content_publishing(),
            'error_handling': await self._validate_error_handling(),
            'performance_metrics': await self._validate_performance_metrics(),
            'system_health': await self._validate_system_health()
        }
        
        # Calculate overall score
        overall_score = self._calculate_validation_score(results)
        results['overall_score'] = overall_score
        
        # Display results
        await self._display_validation_results(results)
        
        return results
    
    async def _validate_database_integrity(self):
        """Validate database integrity for publishing system"""
        print("\n1. 🗄️  DATABASE INTEGRITY VALIDATION")
        print("-" * 40)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check data consistency
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts cp
                    LEFT JOIN campaigns c ON cp.campaign_id = c.campaign_id
                    WHERE c.campaign_id IS NULL
                ''')
                
                orphaned_posts = (await cursor.fetchone())[0]
                
                if orphaned_posts > 0:
                    print(f"   ❌ Found {orphaned_posts} orphaned posts")
                    return {'status': 'failed', 'orphaned_posts': orphaned_posts}
                else:
                    print(f"   ✅ No orphaned posts found")
                
                # Check for duplicate posts
                await cursor.execute('''
                    SELECT campaign_id, channel_id, COUNT(*) as count
                    FROM campaign_posts
                    GROUP BY campaign_id, channel_id
                    HAVING count > 1
                ''')
                
                duplicate_posts = await cursor.fetchall()
                if duplicate_posts:
                    print(f"   ❌ Found {len(duplicate_posts)} duplicate post groups")
                    return {'status': 'failed', 'duplicate_posts': len(duplicate_posts)}
                else:
                    print(f"   ✅ No duplicate posts found")
                
                # Check campaign data completeness
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaigns
                    WHERE ad_content IS NULL OR ad_content = ''
                ''')
                
                empty_campaigns = (await cursor.fetchone())[0]
                
                if empty_campaigns > 0:
                    print(f"   ❌ Found {empty_campaigns} campaigns with empty content")
                    return {'status': 'failed', 'empty_campaigns': empty_campaigns}
                else:
                    print(f"   ✅ All campaigns have content")
                
                print("   ✅ Database integrity validation passed")
                return {'status': 'passed', 'issues': 0}
                
        except Exception as e:
            print(f"   ❌ Database integrity validation failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_campaign_structure(self):
        """Validate campaign structure and relationships"""
        print("\n2. 🎯 CAMPAIGN STRUCTURE VALIDATION")
        print("-" * 40)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check campaign status distribution
                await cursor.execute('''
                    SELECT status, COUNT(*) as count
                    FROM campaigns
                    GROUP BY status
                ''')
                
                status_counts = await cursor.fetchall()
                
                total_campaigns = sum(count for _, count in status_counts)
                
                print(f"   📊 Total campaigns: {total_campaigns}")
                
                active_campaigns = 0
                for status, count in status_counts:
                    if status == 'active':
                        active_campaigns = count
                    print(f"   📋 {status}: {count}")
                
                # Check campaign-post relationships
                await cursor.execute('''
                    SELECT c.campaign_id, COUNT(cp.id) as post_count
                    FROM campaigns c
                    LEFT JOIN campaign_posts cp ON c.campaign_id = cp.campaign_id
                    GROUP BY c.campaign_id
                    HAVING post_count = 0
                ''')
                
                campaigns_without_posts = await cursor.fetchall()
                
                if campaigns_without_posts:
                    print(f"   ❌ Found {len(campaigns_without_posts)} campaigns without posts")
                    return {'status': 'failed', 'campaigns_without_posts': len(campaigns_without_posts)}
                else:
                    print(f"   ✅ All campaigns have posts")
                
                # Check for reasonable post counts per campaign
                await cursor.execute('''
                    SELECT campaign_id, COUNT(*) as post_count
                    FROM campaign_posts
                    GROUP BY campaign_id
                    HAVING post_count > 100
                ''')
                
                excessive_posts = await cursor.fetchall()
                
                if excessive_posts:
                    print(f"   ⚠️  Found {len(excessive_posts)} campaigns with >100 posts")
                
                print("   ✅ Campaign structure validation passed")
                return {
                    'status': 'passed',
                    'total_campaigns': total_campaigns,
                    'active_campaigns': active_campaigns,
                    'excessive_posts': len(excessive_posts)
                }
                
        except Exception as e:
            print(f"   ❌ Campaign structure validation failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_post_scheduling(self):
        """Validate post scheduling system"""
        print("\n3. ⏰ POST SCHEDULING VALIDATION")
        print("-" * 40)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check scheduled posts
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'scheduled'
                ''')
                
                scheduled_posts = (await cursor.fetchone())[0]
                
                print(f"   📅 Scheduled posts: {scheduled_posts}")
                
                # Check for posts scheduled in the past
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'scheduled'
                    AND scheduled_time < datetime('now', '-1 hour')
                ''')
                
                overdue_posts = (await cursor.fetchone())[0]
                
                if overdue_posts > 0:
                    print(f"   ❌ Found {overdue_posts} overdue posts")
                    return {'status': 'failed', 'overdue_posts': overdue_posts}
                else:
                    print(f"   ✅ No overdue posts found")
                
                # Check scheduling pattern
                await cursor.execute('''
                    SELECT 
                        DATE(scheduled_time) as date,
                        COUNT(*) as posts_count
                    FROM campaign_posts
                    WHERE status IN ('scheduled', 'published')
                    AND scheduled_time > datetime('now', '-7 days')
                    GROUP BY DATE(scheduled_time)
                    ORDER BY date DESC
                ''')
                
                daily_schedule = await cursor.fetchall()
                
                print(f"   📊 Daily schedule pattern (last 7 days): {len(daily_schedule)} days")
                
                # Check for reasonable scheduling intervals
                await cursor.execute('''
                    SELECT campaign_id, 
                           MIN(scheduled_time) as first_post,
                           MAX(scheduled_time) as last_post,
                           COUNT(*) as post_count
                    FROM campaign_posts
                    WHERE status IN ('scheduled', 'published')
                    GROUP BY campaign_id
                    HAVING post_count > 1
                ''')
                
                multi_post_campaigns = await cursor.fetchall()
                
                print(f"   📋 Multi-post campaigns: {len(multi_post_campaigns)}")
                
                print("   ✅ Post scheduling validation passed")
                return {
                    'status': 'passed',
                    'scheduled_posts': scheduled_posts,
                    'overdue_posts': overdue_posts,
                    'multi_post_campaigns': len(multi_post_campaigns)
                }
                
        except Exception as e:
            print(f"   ❌ Post scheduling validation failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_content_publishing(self):
        """Validate content publishing capabilities"""
        print("\n4. 📤 CONTENT PUBLISHING VALIDATION")
        print("-" * 40)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check published posts
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'published'
                ''')
                
                published_posts = (await cursor.fetchone())[0]
                
                print(f"   📤 Published posts: {published_posts}")
                
                # Check content types
                await cursor.execute('''
                    SELECT c.content_type, COUNT(*) as count
                    FROM campaign_posts cp
                    JOIN campaigns c ON cp.campaign_id = c.campaign_id
                    WHERE cp.status = 'published'
                    GROUP BY c.content_type
                ''')
                
                content_types = await cursor.fetchall()
                
                print(f"   📊 Content types published:")
                for content_type, count in content_types:
                    print(f"      {content_type or 'text'}: {count}")
                
                # Check for media publishing
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaigns c
                    JOIN campaign_posts cp ON c.campaign_id = cp.campaign_id
                    WHERE cp.status = 'published'
                    AND c.media_url IS NOT NULL
                    AND c.media_url != ''
                ''')
                
                media_posts = (await cursor.fetchone())[0]
                
                print(f"   🎬 Media posts published: {media_posts}")
                
                # Check recent publishing activity
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'published'
                    AND published_time > datetime('now', '-24 hours')
                ''')
                
                recent_publishes = (await cursor.fetchone())[0]
                
                print(f"   📈 Recent publishes (24h): {recent_publishes}")
                
                print("   ✅ Content publishing validation passed")
                return {
                    'status': 'passed',
                    'published_posts': published_posts,
                    'content_types': len(content_types),
                    'media_posts': media_posts,
                    'recent_publishes': recent_publishes
                }
                
        except Exception as e:
            print(f"   ❌ Content publishing validation failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_error_handling(self):
        """Validate error handling and recovery"""
        print("\n5. 🛡️  ERROR HANDLING VALIDATION")
        print("-" * 40)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check failed posts
                await cursor.execute('''
                    SELECT COUNT(*) FROM campaign_posts
                    WHERE status = 'failed'
                ''')
                
                failed_posts = (await cursor.fetchone())[0]
                
                print(f"   ❌ Failed posts: {failed_posts}")
                
                # Check error patterns
                await cursor.execute('''
                    SELECT error_message, COUNT(*) as count
                    FROM campaign_posts
                    WHERE status = 'failed'
                    AND error_message IS NOT NULL
                    GROUP BY error_message
                    ORDER BY count DESC
                ''')
                
                error_patterns = await cursor.fetchall()
                
                print(f"   📊 Error patterns: {len(error_patterns)}")
                
                # Check for systematic errors
                systematic_errors = 0
                for error_msg, count in error_patterns:
                    if count > 10:  # More than 10 of the same error
                        systematic_errors += 1
                        print(f"   ⚠️  Systematic error: {error_msg[:50]}... ({count} times)")
                
                if systematic_errors > 0:
                    print(f"   ❌ Found {systematic_errors} systematic error patterns")
                    return {'status': 'warning', 'systematic_errors': systematic_errors}
                else:
                    print(f"   ✅ No systematic errors found")
                
                # Check recovery rate
                total_posts = failed_posts + await self._get_published_count()
                
                if total_posts > 0:
                    success_rate = (total_posts - failed_posts) / total_posts * 100
                    print(f"   📊 Success rate: {success_rate:.1f}%")
                    
                    if success_rate >= 95:
                        print("   ✅ Excellent success rate")
                        status = 'passed'
                    elif success_rate >= 80:
                        print("   ✅ Good success rate")
                        status = 'passed'
                    else:
                        print("   ⚠️  Low success rate")
                        status = 'warning'
                else:
                    status = 'passed'
                
                print("   ✅ Error handling validation completed")
                return {
                    'status': status,
                    'failed_posts': failed_posts,
                    'error_patterns': len(error_patterns),
                    'systematic_errors': systematic_errors,
                    'success_rate': success_rate if 'success_rate' in locals() else 100
                }
                
        except Exception as e:
            print(f"   ❌ Error handling validation failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _get_published_count(self):
        """Get count of published posts"""
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.cursor()
            await cursor.execute('SELECT COUNT(*) FROM campaign_posts WHERE status = "published"')
            return (await cursor.fetchone())[0]
    
    async def _validate_performance_metrics(self):
        """Validate performance metrics"""
        print("\n6. ⚡ PERFORMANCE METRICS VALIDATION")
        print("-" * 40)
        
        try:
            import time
            
            # Test database query performance
            start_time = time.time()
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                await cursor.execute('SELECT COUNT(*) FROM campaign_posts')
                await cursor.fetchone()
            db_time = time.time() - start_time
            
            print(f"   ⏱️  Database query time: {db_time:.3f}s")
            
            # Test complex query performance
            start_time = time.time()
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                await cursor.execute('''
                    SELECT cp.campaign_id, c.ad_content, COUNT(*) as post_count
                    FROM campaign_posts cp
                    JOIN campaigns c ON cp.campaign_id = c.campaign_id
                    WHERE cp.status = 'published'
                    GROUP BY cp.campaign_id, c.ad_content
                    ORDER BY post_count DESC
                ''')
                await cursor.fetchall()
            complex_query_time = time.time() - start_time
            
            print(f"   ⏱️  Complex query time: {complex_query_time:.3f}s")
            
            # Performance assessment
            if db_time < 0.1 and complex_query_time < 0.5:
                performance_status = 'excellent'
                print("   ✅ Performance: EXCELLENT")
            elif db_time < 0.5 and complex_query_time < 1.0:
                performance_status = 'good'
                print("   ✅ Performance: GOOD")
            else:
                performance_status = 'slow'
                print("   ⚠️  Performance: SLOW")
            
            print("   ✅ Performance metrics validation completed")
            return {
                'status': 'passed',
                'performance_level': performance_status,
                'db_time': db_time,
                'complex_query_time': complex_query_time
            }
            
        except Exception as e:
            print(f"   ❌ Performance metrics validation failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_system_health(self):
        """Validate overall system health"""
        print("\n7. 🏥 SYSTEM HEALTH VALIDATION")
        print("-" * 40)
        
        try:
            # Check if enhanced campaign publisher exists
            import os
            
            if os.path.exists('enhanced_campaign_publisher.py'):
                print("   ✅ Enhanced campaign publisher file exists")
                publisher_exists = True
            else:
                print("   ❌ Enhanced campaign publisher file missing")
                publisher_exists = False
            
            # Check main_bot.py integration
            try:
                with open('main_bot.py', 'r') as f:
                    content = f.read()
                    if 'enhanced_campaign_publisher' in content:
                        print("   ✅ Publisher integrated in main_bot.py")
                        publisher_integrated = True
                    else:
                        print("   ❌ Publisher not integrated in main_bot.py")
                        publisher_integrated = False
            except Exception as e:
                print(f"   ❌ Error checking main_bot.py: {e}")
                publisher_integrated = False
            
            # Check database connectivity
            try:
                async with aiosqlite.connect(self.db_path) as conn:
                    cursor = await conn.cursor()
                    await cursor.execute('SELECT 1')
                    await cursor.fetchone()
                print("   ✅ Database connectivity: OK")
                db_connected = True
            except Exception as e:
                print(f"   ❌ Database connectivity: FAILED - {e}")
                db_connected = False
            
            # Overall system health
            health_components = [publisher_exists, publisher_integrated, db_connected]
            health_score = sum(health_components) / len(health_components) * 100
            
            print(f"   📊 System health score: {health_score:.1f}%")
            
            if health_score == 100:
                print("   ✅ System health: OPTIMAL")
                status = 'passed'
            elif health_score >= 75:
                print("   ✅ System health: GOOD")
                status = 'passed'
            else:
                print("   ❌ System health: NEEDS ATTENTION")
                status = 'failed'
            
            print("   ✅ System health validation completed")
            return {
                'status': status,
                'health_score': health_score,
                'publisher_exists': publisher_exists,
                'publisher_integrated': publisher_integrated,
                'db_connected': db_connected
            }
            
        except Exception as e:
            print(f"   ❌ System health validation failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_validation_score(self, results):
        """Calculate overall validation score"""
        weights = {
            'database_integrity': 0.20,
            'campaign_structure': 0.15,
            'post_scheduling': 0.15,
            'content_publishing': 0.20,
            'error_handling': 0.15,
            'performance_metrics': 0.05,
            'system_health': 0.10
        }
        
        status_scores = {
            'passed': 100,
            'warning': 75,
            'failed': 0,
            'error': 0
        }
        
        total_score = 0
        for component, weight in weights.items():
            if component in results:
                status = results[component].get('status', 'error')
                score = status_scores.get(status, 0)
                total_score += score * weight
        
        return {
            'score': round(total_score, 1),
            'grade': self._get_grade(total_score)
        }
    
    def _get_grade(self, score):
        """Get letter grade for score"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'B+'
        elif score >= 80:
            return 'B'
        elif score >= 75:
            return 'C+'
        elif score >= 70:
            return 'C'
        else:
            return 'D'
    
    async def _display_validation_results(self, results):
        """Display comprehensive validation results"""
        print("\n" + "=" * 60)
        print("📊 PUBLISHING SYSTEM VALIDATION REPORT")
        print("=" * 60)
        
        overall_score = results.get('overall_score', {})
        score = overall_score.get('score', 0)
        grade = overall_score.get('grade', 'F')
        
        print(f"\n🏆 OVERALL VALIDATION SCORE: {score}/100 (Grade: {grade})")
        
        if score >= 90:
            print("   🟢 EXCELLENT: Publishing system is working optimally")
        elif score >= 80:
            print("   🟡 GOOD: Publishing system is working well")
        elif score >= 70:
            print("   🟠 FAIR: Publishing system needs some attention")
        else:
            print("   🔴 POOR: Publishing system has critical issues")
        
        print("\n📋 VALIDATION RESULTS:")
        for component, data in results.items():
            if component == 'overall_score':
                continue
                
            status = data.get('status', 'unknown')
            if status == 'passed':
                icon = "✅"
            elif status == 'warning':
                icon = "⚠️"
            else:
                icon = "❌"
            
            print(f"   {icon} {component.replace('_', ' ').title()}: {status.upper()}")
        
        print("\n🎯 RECOMMENDATIONS:")
        if score >= 90:
            print("   • Publishing system is performing excellently")
            print("   • Continue monitoring for optimal performance")
        elif score >= 80:
            print("   • Address any warnings to maintain performance")
            print("   • Monitor system health regularly")
        else:
            print("   • Immediate attention required for failed components")
            print("   • Review error handling and system integration")
        
        print("\n📈 KEY METRICS:")
        
        # Extract key metrics from results
        if 'content_publishing' in results:
            pub_data = results['content_publishing']
            print(f"   • Published posts: {pub_data.get('published_posts', 0)}")
            print(f"   • Content types: {pub_data.get('content_types', 0)}")
            print(f"   • Media posts: {pub_data.get('media_posts', 0)}")
        
        if 'error_handling' in results:
            err_data = results['error_handling']
            print(f"   • Success rate: {err_data.get('success_rate', 0):.1f}%")
            print(f"   • Failed posts: {err_data.get('failed_posts', 0)}")
        
        if 'system_health' in results:
            health_data = results['system_health']
            print(f"   • System health: {health_data.get('health_score', 0):.1f}%")

async def main():
    """Main function to run publishing system validation"""
    validator = PublishingSystemValidator()
    results = await validator.comprehensive_validation()
    
    # Save results
    with open('publishing_validation_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Full validation report saved to: publishing_validation_report.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())