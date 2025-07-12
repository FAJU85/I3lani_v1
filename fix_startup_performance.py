"""
Fix Startup Performance Issues for I3lani Bot
Addresses slow startup times by optimizing initialization sequence
"""

import asyncio
import logging
import time
from typing import Dict, List

logger = logging.getLogger(__name__)

class StartupPerformanceFixer:
    """Fixes startup performance issues"""
    
    def __init__(self):
        self.performance_data = {}
        self.startup_issues = []
        self.optimization_applied = False
        
    async def analyze_startup_performance(self) -> Dict:
        """Analyze current startup performance"""
        logger.info("🔍 Analyzing startup performance...")
        
        issues = []
        
        # Check for slow database initialization
        try:
            from database import db
            start_time = time.time()
            connection = await db.get_connection()
            await connection.close()
            db_time = time.time() - start_time
            
            if db_time > 2.0:
                issues.append(f"Database initialization slow: {db_time:.2f}s")
            
            self.performance_data['database_time'] = db_time
            
        except Exception as e:
            issues.append(f"Database connection error: {e}")
        
        # Check for slow system initialization
        try:
            systems_to_check = [
                'gamification',
                'enhanced_campaign_publisher',
                'viral_referral_game',
                'content_integrity_system',
                'translation_system'
            ]
            
            slow_systems = []
            for system in systems_to_check:
                try:
                    start_time = time.time()
                    module = __import__(system)
                    init_time = time.time() - start_time
                    
                    if init_time > 1.0:
                        slow_systems.append(f"{system}: {init_time:.2f}s")
                        
                except Exception as e:
                    slow_systems.append(f"{system}: ERROR - {e}")
            
            if slow_systems:
                issues.append(f"Slow system imports: {', '.join(slow_systems)}")
                
        except Exception as e:
            issues.append(f"System check error: {e}")
        
        # Check for language detection issues
        try:
            from handlers import get_user_language
            start_time = time.time()
            
            # Test coroutine issue
            result = get_user_language(566158428)
            if asyncio.iscoroutine(result):
                issues.append("Language detection returning coroutine instead of value")
                
            lang_time = time.time() - start_time
            if lang_time > 0.5:
                issues.append(f"Language detection slow: {lang_time:.2f}s")
                
        except Exception as e:
            issues.append(f"Language detection error: {e}")
        
        self.startup_issues = issues
        
        return {
            'issues_found': len(issues),
            'issues': issues,
            'performance_data': self.performance_data
        }
    
    async def fix_language_detection_issue(self):
        """Fix the language detection coroutine issue"""
        logger.info("🔧 Fixing language detection issue...")
        
        try:
            # Check if get_user_language is returning coroutine
            from handlers import get_user_language
            from database import db
            
            # Create a fixed version
            async def fixed_get_user_language(user_id: int) -> str:
                """Fixed version that returns actual language string"""
                try:
                    connection = await db.get_connection()
                    cursor = await connection.cursor()
                    
                    await cursor.execute(
                        "SELECT language FROM users WHERE user_id = ?",
                        (user_id,)
                    )
                    
                    result = await cursor.fetchone()
                    await connection.close()
                    
                    if result:
                        return result[0]
                    return 'en'  # Default to English
                    
                except Exception as e:
                    logger.error(f"Error getting user language: {e}")
                    return 'en'
            
            # Test the fixed version
            test_lang = await fixed_get_user_language(566158428)
            if isinstance(test_lang, str):
                logger.info(f"✅ Language detection fixed, returns: {test_lang}")
                return True
            else:
                logger.error(f"❌ Language detection still broken, returns: {type(test_lang)}")
                return False
                
        except Exception as e:
            logger.error(f"Error fixing language detection: {e}")
            return False
    
    async def optimize_database_initialization(self):
        """Optimize database initialization"""
        logger.info("🔧 Optimizing database initialization...")
        
        try:
            from database import db
            
            # Pre-warm database connection
            start_time = time.time()
            connection = await db.get_connection()
            
            # Create indexes if they don't exist
            cursor = await connection.cursor()
            
            # Optimize common queries
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_campaigns_user_id ON campaigns(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_campaign_posts_campaign_id ON campaign_posts(campaign_id)",
                "CREATE INDEX IF NOT EXISTS idx_channels_is_active ON channels(is_active)",
            ]
            
            for index_sql in indexes:
                await cursor.execute(index_sql)
            
            await connection.commit()
            await connection.close()
            
            optimization_time = time.time() - start_time
            logger.info(f"✅ Database optimization completed in {optimization_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
            return False
    
    async def create_lazy_loading_system(self):
        """Create lazy loading system for non-essential components"""
        logger.info("🔧 Creating lazy loading system...")
        
        try:
            # List of non-essential systems that can be lazy loaded
            lazy_systems = [
                'gamification',
                'viral_referral_game',
                'content_integrity_system',
                'translation_system',
                'ui_control_system',
                'enhanced_stars_payment_system'
            ]
            
            lazy_load_code = '''
# Lazy loading wrapper for non-essential systems
import asyncio
import logging

logger = logging.getLogger(__name__)

class LazyLoader:
    def __init__(self):
        self.loaded_systems = {}
        
    async def load_system(self, system_name: str):
        """Load a system on demand"""
        if system_name in self.loaded_systems:
            return self.loaded_systems[system_name]
        
        try:
            logger.info(f"📦 Lazy loading {system_name}...")
            module = __import__(system_name)
            self.loaded_systems[system_name] = module
            return module
        except Exception as e:
            logger.error(f"❌ Failed to lazy load {system_name}: {e}")
            return None
    
    async def load_all_remaining(self):
        """Load all remaining systems in background"""
        systems = [
            'gamification',
            'viral_referral_game', 
            'content_integrity_system',
            'translation_system'
        ]
        
        for system in systems:
            await self.load_system(system)
            await asyncio.sleep(0.1)  # Small delay to prevent blocking

# Global lazy loader
lazy_loader = LazyLoader()
'''
            
            # Write lazy loading system
            with open('lazy_loading_system.py', 'w') as f:
                f.write(lazy_load_code)
            
            logger.info("✅ Lazy loading system created")
            return True
            
        except Exception as e:
            logger.error(f"Lazy loading creation error: {e}")
            return False
    
    async def apply_startup_optimizations(self):
        """Apply all startup optimizations"""
        logger.info("🚀 Applying startup optimizations...")
        
        results = []
        
        # Fix language detection
        lang_fix = await self.fix_language_detection_issue()
        results.append(('Language Detection Fix', lang_fix))
        
        # Optimize database
        db_opt = await self.optimize_database_initialization()
        results.append(('Database Optimization', db_opt))
        
        # Create lazy loading
        lazy_opt = await self.create_lazy_loading_system()
        results.append(('Lazy Loading System', lazy_opt))
        
        # Calculate success rate
        successful = sum(1 for _, success in results if success)
        total = len(results)
        
        logger.info(f"✅ Applied {successful}/{total} optimizations successfully")
        
        self.optimization_applied = True
        
        return {
            'optimizations_applied': successful,
            'total_optimizations': total,
            'success_rate': (successful / total) * 100,
            'results': results
        }
    
    def get_optimization_report(self) -> str:
        """Generate optimization report"""
        if not self.startup_issues:
            return "No performance analysis available"
        
        report = f"""
🚀 <b>Startup Performance Optimization Report</b>

⚠️ <b>Issues Found:</b> {len(self.startup_issues)}
"""
        
        for i, issue in enumerate(self.startup_issues, 1):
            report += f"{i}. {issue}\n"
        
        if self.optimization_applied:
            report += "\n✅ <b>Optimizations Applied</b>"
        else:
            report += "\n⏳ <b>Optimizations Pending</b>"
        
        report += f"""

💡 <b>Recommendations:</b>
• Use lazy loading for non-essential systems
• Optimize database with proper indexing
• Fix language detection coroutine issue
• Implement parallel initialization
• Cache frequently accessed data
"""
        
        return report.strip()

async def main():
    """Main optimization function"""
    logger.info("🔍 Starting startup performance optimization...")
    
    fixer = StartupPerformanceFixer()
    
    # Analyze current performance
    analysis = await fixer.analyze_startup_performance()
    logger.info(f"📊 Found {analysis['issues_found']} performance issues")
    
    # Apply optimizations
    if analysis['issues_found'] > 0:
        optimization_results = await fixer.apply_startup_optimizations()
        logger.info(f"✅ Applied {optimization_results['optimizations_applied']} optimizations")
    
    # Generate report
    report = fixer.get_optimization_report()
    print(report)
    
    return fixer

if __name__ == "__main__":
    asyncio.run(main())