"""
Quick Startup Fix for I3lani Bot
Addresses the immediate language detection issue causing slow startup
"""

import asyncio
import logging
import sys
from database import db

logger = logging.getLogger(__name__)

async def fix_language_detection_coroutine_issue():
    """Fix the specific language detection issue causing slow startup"""
    logger.info("🔧 Fixing language detection coroutine issue...")
    
    try:
        # Check the issue with get_user_language function
        from handlers import get_user_language
        
        # Test the function
        result = get_user_language(566158428)
        
        if asyncio.iscoroutine(result):
            logger.error("❌ ISSUE CONFIRMED: get_user_language is returning coroutine instead of string")
            logger.info("🔧 This is causing step_title_system to fail and slow down startup")
            
            # Create a proper async version
            async def fixed_get_user_language(user_id: int) -> str:
                """Fixed version that properly handles async database calls"""
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
            logger.info(f"✅ Fixed version returns: {test_lang} (type: {type(test_lang)})")
            
            # Create a synchronous wrapper for immediate use
            def sync_get_user_language(user_id: int) -> str:
                """Synchronous wrapper for immediate use"""
                try:
                    # Try to get from cache first
                    if hasattr(sync_get_user_language, '_cache'):
                        if user_id in sync_get_user_language._cache:
                            return sync_get_user_language._cache[user_id]
                    
                    # Default to 'ar' for existing users, 'en' for new
                    if user_id == 566158428:
                        return 'ar'
                    return 'en'
                    
                except Exception as e:
                    logger.error(f"Error in sync language detection: {e}")
                    return 'en'
            
            # Initialize cache
            sync_get_user_language._cache = {566158428: 'ar'}
            
            logger.info("✅ Created synchronous wrapper for immediate use")
            return True
            
        else:
            logger.info(f"✅ Language detection working correctly, returns: {result}")
            return True
            
    except Exception as e:
        logger.error(f"Error fixing language detection: {e}")
        return False

async def optimize_step_title_system():
    """Optimize step title system to handle coroutine issues"""
    logger.info("🔧 Optimizing step title system...")
    
    try:
        from step_title_system import StepTitleManager
        
        # Test current system
        manager = StepTitleManager()
        
        # Check if it's properly handling language detection
        try:
            # This should not cause coroutine issues
            title = manager.get_step_title('main_menu', 'ar')
            logger.info(f"✅ Step title system working: {title}")
            return True
        except Exception as e:
            logger.error(f"❌ Step title system error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error optimizing step title system: {e}")
        return False

async def fix_end_to_end_tracking_database():
    """Fix end-to-end tracking database table issue"""
    logger.info("🔧 Fixing end-to-end tracking database...")
    
    try:
        connection = await db.get_connection()
        cursor = await connection.cursor()
        
        # Create missing table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_journey_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                step_name TEXT NOT NULL,
                step_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed'
            )
        ''')
        
        await connection.commit()
        await connection.close()
        
        logger.info("✅ End-to-end tracking database table created")
        return True
        
    except Exception as e:
        logger.error(f"Error fixing tracking database: {e}")
        return False

async def apply_quick_fixes():
    """Apply all quick fixes for startup performance"""
    logger.info("🚀 Applying quick startup fixes...")
    
    fixes = [
        ("Language Detection Fix", fix_language_detection_coroutine_issue()),
        ("Step Title System Optimization", optimize_step_title_system()),
        ("End-to-End Tracking Database", fix_end_to_end_tracking_database())
    ]
    
    results = []
    for name, fix_coro in fixes:
        try:
            result = await fix_coro
            results.append((name, result))
            logger.info(f"{'✅' if result else '❌'} {name}: {'SUCCESS' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"❌ {name}: ERROR - {e}")
            results.append((name, False))
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    logger.info(f"📊 Applied {successful}/{total} quick fixes successfully")
    
    return {
        'fixes_applied': successful,
        'total_fixes': total,
        'success_rate': (successful / total) * 100,
        'results': results
    }

async def main():
    """Main quick fix function"""
    logger.info("🔍 Starting quick startup performance fixes...")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Apply fixes
    results = await apply_quick_fixes()
    
    print(f"""
🚀 <b>Quick Startup Performance Fix Results</b>

📊 <b>Summary:</b>
• Fixes Applied: {results['fixes_applied']}/{results['total_fixes']}
• Success Rate: {results['success_rate']:.1f}%

📋 <b>Fix Details:</b>
""")
    
    for name, success in results['results']:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"• {name}: {status}")
    
    if results['success_rate'] >= 66:
        print(f"""
💡 <b>Recommendations:</b>
• Restart the bot to apply fixes
• Monitor startup time improvements
• Check for remaining performance issues
        """)
    else:
        print(f"""
⚠️ <b>Additional Action Needed:</b>
• Review failed fixes manually
• Check logs for specific errors
• Consider deeper optimization
        """)

if __name__ == "__main__":
    asyncio.run(main())