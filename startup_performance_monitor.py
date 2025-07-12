"""
Startup Performance Monitor for I3lani Bot
Monitors and reports on startup performance improvements
"""

import asyncio
import logging
import time
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class StartupPerformanceMonitor:
    """Monitors startup performance and provides insights"""
    
    def __init__(self):
        self.startup_start_time = None
        self.component_times = {}
        self.performance_history = []
        
    def start_monitoring(self):
        """Start monitoring startup performance"""
        self.startup_start_time = time.time()
        logger.info("🚀 Starting startup performance monitoring...")
        
    def log_component_time(self, component_name: str, start_time: float):
        """Log time taken for a component to initialize"""
        if start_time is None:
            return
            
        elapsed = time.time() - start_time
        self.component_times[component_name] = elapsed
        
        # Log with appropriate level based on performance
        if elapsed < 1.0:
            logger.info(f"✅ {component_name}: {elapsed:.2f}s (Fast)")
        elif elapsed < 3.0:
            logger.info(f"⚠️ {component_name}: {elapsed:.2f}s (Moderate)")
        else:
            logger.warning(f"🐌 {component_name}: {elapsed:.2f}s (Slow)")
    
    def get_total_startup_time(self) -> float:
        """Get total startup time"""
        if self.startup_start_time is None:
            return 0.0
        return time.time() - self.startup_start_time
    
    def get_performance_report(self) -> str:
        """Generate performance report"""
        if not self.component_times:
            return "No performance data available"
        
        total_time = self.get_total_startup_time()
        fastest_components = sorted(self.component_times.items(), key=lambda x: x[1])[:5]
        slowest_components = sorted(self.component_times.items(), key=lambda x: x[1], reverse=True)[:5]
        
        report = f"""
🚀 <b>Startup Performance Report</b>
<i>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>

⏱️ <b>Total Startup Time:</b> {total_time:.2f}s
📊 <b>Components Tracked:</b> {len(self.component_times)}

🏆 <b>Fastest Components:</b>
"""
        
        for name, time_taken in fastest_components:
            report += f"• {name}: {time_taken:.2f}s\n"
        
        report += f"""
🐌 <b>Slowest Components:</b>
"""
        
        for name, time_taken in slowest_components:
            report += f"• {name}: {time_taken:.2f}s\n"
        
        # Performance recommendations
        report += f"""
💡 <b>Performance Analysis:</b>
"""
        
        slow_components = [name for name, time_taken in self.component_times.items() if time_taken > 2.0]
        if slow_components:
            report += f"• {len(slow_components)} components taking >2s need optimization\n"
        
        if total_time > 15.0:
            report += "• Consider implementing lazy loading for non-essential systems\n"
        
        if total_time > 30.0:
            report += "• Critical: Startup time exceeds 30s, immediate optimization required\n"
        elif total_time > 10.0:
            report += "• Warning: Startup time exceeds 10s, optimization recommended\n"
        else:
            report += "• Good: Startup time is reasonable\n"
        
        return report.strip()
    
    def save_performance_data(self):
        """Save performance data for historical analysis"""
        performance_record = {
            'timestamp': datetime.now().isoformat(),
            'total_time': self.get_total_startup_time(),
            'component_times': self.component_times.copy(),
            'issues_detected': len([t for t in self.component_times.values() if t > 2.0])
        }
        
        self.performance_history.append(performance_record)
        
        # Keep only last 10 records
        if len(self.performance_history) > 10:
            self.performance_history = self.performance_history[-10:]
    
    def get_performance_trend(self) -> str:
        """Get performance trend analysis"""
        if len(self.performance_history) < 2:
            return "Not enough data for trend analysis"
        
        current = self.performance_history[-1]
        previous = self.performance_history[-2]
        
        time_diff = current['total_time'] - previous['total_time']
        
        if time_diff < -2.0:
            trend = "📈 Significant improvement"
        elif time_diff < -0.5:
            trend = "✅ Improved"
        elif time_diff > 2.0:
            trend = "📉 Significantly slower"
        elif time_diff > 0.5:
            trend = "⚠️ Slower"
        else:
            trend = "📊 Stable"
        
        return f"{trend} ({time_diff:+.1f}s vs previous startup)"

# Global monitor instance
performance_monitor = StartupPerformanceMonitor()

def get_performance_monitor():
    """Get the global performance monitor instance"""
    return performance_monitor

async def monitor_startup_performance():
    """Monitor startup performance and log results"""
    monitor = get_performance_monitor()
    monitor.start_monitoring()
    
    # Monitor key components
    component_start_times = {}
    
    # Database initialization
    component_start_times['database'] = time.time()
    try:
        from database import db
        await db.get_connection()
        monitor.log_component_time('Database', component_start_times['database'])
    except Exception as e:
        logger.error(f"Database monitoring error: {e}")
    
    # Language system
    component_start_times['language'] = time.time()
    try:
        from languages import get_text
        get_text('en', 'main_menu')  # Test language system
        monitor.log_component_time('Language System', component_start_times['language'])
    except Exception as e:
        logger.error(f"Language system monitoring error: {e}")
    
    # Generate final report
    await asyncio.sleep(1)  # Allow other components to finish
    
    report = monitor.get_performance_report()
    logger.info(f"Performance Report:\n{report}")
    
    # Save performance data
    monitor.save_performance_data()
    
    return monitor

if __name__ == "__main__":
    asyncio.run(monitor_startup_performance())