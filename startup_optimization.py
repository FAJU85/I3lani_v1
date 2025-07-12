"""
Startup Optimization for I3lani Bot
Optimizes bot initialization for faster startup times
"""

import asyncio
import logging
import time
from typing import List, Callable, Any

logger = logging.getLogger(__name__)

class StartupOptimizer:
    """Optimizes bot startup performance"""
    
    def __init__(self):
        self.startup_times = {}
        self.total_startup_time = 0
        
    async def time_function(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Time a function execution"""
        start_time = time.time()
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            self.startup_times[name] = execution_time
            logger.info(f"⚡ {name}: {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.startup_times[name] = execution_time
            logger.error(f"❌ {name}: {execution_time:.3f}s - ERROR: {e}")
            return None
    
    async def parallel_init(self, tasks: List[tuple]) -> List[Any]:
        """Execute multiple initialization tasks in parallel"""
        start_time = time.time()
        
        async def run_task(name, func, *args, **kwargs):
            return await self.time_function(name, func, *args, **kwargs)
        
        # Create coroutines for all tasks
        coroutines = []
        for task in tasks:
            if len(task) == 2:
                name, func = task
                coroutines.append(run_task(name, func))
            elif len(task) >= 3:
                name, func = task[0], task[1]
                args = task[2:] if len(task) > 2 else []
                coroutines.append(run_task(name, func, *args))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        total_time = time.time() - start_time
        logger.info(f"🚀 Parallel initialization completed in {total_time:.3f}s")
        
        return results
    
    def get_startup_report(self) -> str:
        """Generate startup performance report"""
        if not self.startup_times:
            return "No startup data available"
        
        total_time = sum(self.startup_times.values())
        slowest_components = sorted(self.startup_times.items(), key=lambda x: x[1], reverse=True)
        
        report = f"""
🚀 <b>Startup Performance Report</b>

⏱️ <b>Total Startup Time:</b> {total_time:.3f}s

📊 <b>Component Timing (slowest first):</b>
"""
        
        for name, time_taken in slowest_components[:10]:
            percentage = (time_taken / total_time) * 100
            report += f"• {name}: {time_taken:.3f}s ({percentage:.1f}%)\n"
        
        # Performance recommendations
        report += f"""
💡 <b>Optimization Recommendations:</b>
"""
        
        if any(time > 2.0 for time in self.startup_times.values()):
            report += "• Some components taking >2s - consider lazy loading\n"
        
        if total_time > 10.0:
            report += "• Total startup >10s - implement parallel initialization\n"
        
        if len([t for t in self.startup_times.values() if t > 1.0]) > 5:
            report += "• Multiple slow components - review initialization order\n"
        
        return report.strip()

# Global optimizer instance
startup_optimizer = StartupOptimizer()

async def optimized_database_init():
    """Optimized database initialization"""
    try:
        from database import db
        # Only initialize essential tables first
        await db.init_db()
        logger.info("✅ Core database initialized")
        return True
    except Exception as e:
        logger.error(f"Database init error: {e}")
        return False

async def optimized_channel_sync():
    """Optimized channel synchronization"""
    try:
        from channel_manager import get_channel_manager
        manager = get_channel_manager()
        # Quick sync without full verification
        channels = await manager.get_channels()
        logger.info(f"✅ Quick channel sync: {len(channels)} channels")
        return True
    except Exception as e:
        logger.error(f"Channel sync error: {e}")
        return False

async def optimized_payment_init():
    """Optimized payment system initialization"""
    try:
        from continuous_payment_scanner import ContinuousPaymentScanner
        scanner = ContinuousPaymentScanner()
        # Start scanner without immediate scan
        logger.info("✅ Payment scanner initialized")
        return scanner
    except Exception as e:
        logger.error(f"Payment init error: {e}")
        return None

async def lazy_load_optional_systems():
    """Lazy load non-essential systems after bot is running"""
    await asyncio.sleep(5)  # Wait 5 seconds after bot starts
    
    optional_tasks = [
        ("Enhanced Campaign Publisher", "enhanced_campaign_publisher.get_campaign_publisher"),
        ("Content Integrity System", "content_integrity_system.get_content_integrity_system"),
        ("Translation System", "translation_system.get_translation_system"),
        ("Gamification System", "gamification.get_gamification_system"),
    ]
    
    for name, module_func in optional_tasks:
        try:
            module_name, func_name = module_func.rsplit('.', 1)
            module = __import__(module_name)
            func = getattr(module, func_name)
            await startup_optimizer.time_function(f"Lazy {name}", func)
        except Exception as e:
            logger.warning(f"Lazy load {name} failed: {e}")
    
    logger.info("🔄 Lazy loading of optional systems completed")

def get_startup_optimizer():
    """Get the global startup optimizer instance"""
    return startup_optimizer