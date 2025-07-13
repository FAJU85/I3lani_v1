"""
System Health Monitor for I3lani Bot
Real-time system health monitoring and alerting
"""

import asyncio
import aiosqlite
import psutil
import time
from datetime import datetime
from typing import Dict, List

class SystemHealthMonitor:
    def __init__(self):
        self.db_path = 'bot.db'
        self.start_time = time.time()
        
    async def get_system_health(self) -> Dict:
        """Get comprehensive system health report"""
        try:
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'uptime': self._get_uptime(),
                'memory': self._get_memory_usage(),
                'cpu': self._get_cpu_usage(),
                'database': await self._get_database_health(),
                'payment_system': await self._get_payment_system_health(),
                'bot_status': await self._get_bot_status()
            }
            
            # Calculate overall health score
            health_data['overall_score'] = self._calculate_health_score(health_data)
            
            return health_data
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        uptime_seconds = time.time() - self.start_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    def _get_memory_usage(self) -> Dict:
        """Get memory usage statistics"""
        try:
            memory = psutil.virtual_memory()
            return {
                'used_percent': memory.percent,
                'used_mb': memory.used / (1024 * 1024),
                'total_mb': memory.total / (1024 * 1024),
                'available_mb': memory.available / (1024 * 1024)
            }
        except Exception:
            return {'error': 'Unable to get memory stats'}
    
    def _get_cpu_usage(self) -> Dict:
        """Get CPU usage statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            return {
                'usage_percent': cpu_percent,
                'cores': psutil.cpu_count()
            }
        except Exception:
            return {'error': 'Unable to get CPU stats'}
    
    async def _get_database_health(self) -> Dict:
        """Get database health status"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check database size
                await cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = (await cursor.fetchone())[0]
                
                # Check table counts
                await cursor.execute("SELECT COUNT(*) FROM users")
                users = (await cursor.fetchone())[0]
                
                await cursor.execute("SELECT COUNT(*) FROM campaigns")
                campaigns = (await cursor.fetchone())[0]
                
                return {
                    'status': 'healthy',
                    'size_mb': db_size / (1024 * 1024),
                    'users': users,
                    'campaigns': campaigns
                }
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _get_payment_system_health(self) -> Dict:
        """Get payment system health"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check recent payments
                await cursor.execute("""
                    SELECT COUNT(*) FROM payments 
                    WHERE created_at > datetime('now', '-1 hour')
                """)
                recent_payments = (await cursor.fetchone())[0]
                
                # Check payment success rate
                await cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN status = 'confirmed' THEN 1 END) * 100.0 / COUNT(*) 
                    FROM payments 
                    WHERE created_at > datetime('now', '-24 hours')
                """)
                success_rate = (await cursor.fetchone())[0] or 0
                
                return {
                    'status': 'healthy',
                    'recent_payments': recent_payments,
                    'success_rate': success_rate
                }
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def _get_bot_status(self) -> Dict:
        """Get bot operational status"""
        try:
            return {
                'status': 'running',
                'features': [
                    'Multi-language support',
                    'Payment processing',
                    'Campaign management',
                    'Channel detection'
                ]
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_health_score(self, health_data: Dict) -> float:
        """Calculate overall health score"""
        score = 100.0
        
        # Memory usage impact
        if health_data['memory'].get('used_percent', 0) > 80:
            score -= 10
        elif health_data['memory'].get('used_percent', 0) > 60:
            score -= 5
        
        # CPU usage impact
        if health_data['cpu'].get('usage_percent', 0) > 80:
            score -= 10
        elif health_data['cpu'].get('usage_percent', 0) > 60:
            score -= 5
        
        # Database health impact
        if health_data['database'].get('status') != 'healthy':
            score -= 20
        
        # Payment system impact
        if health_data['payment_system'].get('status') != 'healthy':
            score -= 15
        
        return max(0, score)

# Global instance
health_monitor = SystemHealthMonitor()
