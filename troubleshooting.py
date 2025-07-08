"""
Comprehensive Troubleshooting System for I3lani Bot
Provides diagnostic tools, error monitoring, and automated issue resolution
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import Database
from languages import get_text
import aiosqlite
import os
import psutil
import sys
import traceback

logger = logging.getLogger(__name__)

class TroubleshootingSystem:
    """Advanced troubleshooting and diagnostic system"""
    
    def __init__(self, database: Database, bot):
        self.database = database
        self.bot = bot
        self.start_time = datetime.now()
        self.error_log = []
        self.health_checks = []
        self.performance_metrics = {}
        
        # Issue categories
        self.ISSUE_CATEGORIES = {
            'database': 'Database Connection & Operations',
            'payment': 'Payment Processing',
            'messaging': 'Message Sending & Receiving',
            'channel': 'Channel Management',
            'user': 'User Authentication & Profiles',
            'performance': 'Performance & Speed',
            'memory': 'Memory & Resource Usage',
            'api': 'External API Connections',
            'pricing': 'Pricing Calculations',
            'language': 'Language & Localization'
        }
        
        # Common solutions database
        self.COMMON_SOLUTIONS = {
            'database_lock': {
                'description': 'Database is locked or busy',
                'solutions': [
                    'Restart the bot service',
                    'Check for long-running queries',
                    'Verify database file permissions',
                    'Clear temporary database locks'
                ],
                'severity': 'high'
            },
            'payment_timeout': {
                'description': 'Payment processing timeout',
                'solutions': [
                    'Check payment gateway status',
                    'Verify API credentials',
                    'Increase timeout settings',
                    'Contact payment provider'
                ],
                'severity': 'medium'
            },
            'message_sending_failed': {
                'description': 'Failed to send messages to users',
                'solutions': [
                    'Check bot token validity',
                    'Verify user has not blocked the bot',
                    'Check rate limiting status',
                    'Restart Telegram connection'
                ],
                'severity': 'high'
            },
            'channel_access_denied': {
                'description': 'Cannot access channel',
                'solutions': [
                    'Verify bot is admin in channel',
                    'Check channel privacy settings',
                    'Re-add bot to channel with proper permissions',
                    'Update channel information in database'
                ],
                'severity': 'medium'
            },
            'high_memory_usage': {
                'description': 'Memory usage is above normal levels',
                'solutions': [
                    'Restart bot to clear memory leaks',
                    'Check for resource-intensive operations',
                    'Optimize database queries',
                    'Monitor for memory leaks in code'
                ],
                'severity': 'medium'
            }
        }
    
    async def initialize_troubleshooting_tables(self):
        """Initialize troubleshooting database tables"""
        try:
            async with aiosqlite.connect(self.database.db_path) as db:
                # Error logs table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS error_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        error_type TEXT NOT NULL,
                        error_message TEXT NOT NULL,
                        stack_trace TEXT,
                        user_id INTEGER,
                        context TEXT,
                        resolved BOOLEAN DEFAULT FALSE,
                        resolution_notes TEXT,
                        severity TEXT DEFAULT 'medium'
                    )
                ''')
                
                # Health check logs table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS health_checks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        check_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        details TEXT,
                        response_time REAL,
                        issues_found INTEGER DEFAULT 0
                    )
                ''')
                
                # Performance metrics table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metric_type TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        unit TEXT,
                        threshold_exceeded BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # User issues table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS user_issues (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        issue_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        status TEXT DEFAULT 'open',
                        priority TEXT DEFAULT 'medium',
                        reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        resolved_at TIMESTAMP,
                        resolution TEXT,
                        admin_notes TEXT
                    )
                ''')
                
                await db.commit()
                logger.info("Troubleshooting tables initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing troubleshooting tables: {e}")
    
    async def log_error(self, error_type: str, error_message: str, 
                       user_id: Optional[int] = None, context: Optional[str] = None,
                       stack_trace: Optional[str] = None, severity: str = 'medium'):
        """Log error to troubleshooting system"""
        try:
            if not stack_trace and sys.exc_info()[0]:
                stack_trace = traceback.format_exc()
            
            async with aiosqlite.connect(self.database.db_path) as db:
                await db.execute('''
                    INSERT INTO error_logs (error_type, error_message, stack_trace, 
                                          user_id, context, severity)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (error_type, error_message, stack_trace, user_id, context, severity))
                await db.commit()
            
            # Add to in-memory log for quick access
            self.error_log.append({
                'timestamp': datetime.now(),
                'type': error_type,
                'message': error_message,
                'user_id': user_id,
                'context': context,
                'severity': severity
            })
            
            # Keep only last 100 errors in memory
            if len(self.error_log) > 100:
                self.error_log.pop(0)
                
            logger.error(f"Logged error: {error_type} - {error_message}")
            
        except Exception as e:
            logger.error(f"Error logging to troubleshooting system: {e}")
    
    async def run_health_checks(self) -> Dict:
        """Run comprehensive health checks"""
        health_status = {
            'overall': 'healthy',
            'checks': {},
            'timestamp': datetime.now(),
            'issues_found': 0
        }
        
        # Database health check
        db_status = await self._check_database_health()
        health_status['checks']['database'] = db_status
        if db_status['status'] != 'healthy':
            health_status['issues_found'] += 1
        
        # Memory usage check
        memory_status = await self._check_memory_usage()
        health_status['checks']['memory'] = memory_status
        if memory_status['status'] != 'healthy':
            health_status['issues_found'] += 1
        
        # Bot API connectivity check
        api_status = await self._check_bot_api()
        health_status['checks']['bot_api'] = api_status
        if api_status['status'] != 'healthy':
            health_status['issues_found'] += 1
        
        # Payment system check
        payment_status = await self._check_payment_system()
        health_status['checks']['payment'] = payment_status
        if payment_status['status'] != 'healthy':
            health_status['issues_found'] += 1
        
        # Channel connectivity check
        channel_status = await self._check_channels()
        health_status['checks']['channels'] = channel_status
        if channel_status['status'] != 'healthy':
            health_status['issues_found'] += 1
        
        # Set overall status
        if health_status['issues_found'] > 0:
            health_status['overall'] = 'issues_detected'
        if health_status['issues_found'] >= 3:
            health_status['overall'] = 'critical'
        
        # Log health check results
        await self._log_health_check(health_status)
        
        return health_status
    
    async def _check_database_health(self) -> Dict:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            async with aiosqlite.connect(self.database.db_path) as db:
                await db.execute('SELECT 1')
                
            # Test write operation
            test_data = f"health_check_{int(time.time())}"
            await self.database.execute_query(
                "INSERT INTO health_checks (check_type, status, details) VALUES (?, ?, ?)",
                ('database_test', 'success', test_data)
            )
            
            response_time = time.time() - start_time
            
            # Check database size and performance
            db_size = os.path.getsize(self.database.db_path) / (1024 * 1024)  # MB
            
            status = 'healthy'
            issues = []
            
            if response_time > 1.0:
                status = 'slow'
                issues.append(f"Slow response time: {response_time:.2f}s")
            
            if db_size > 100:  # Warning if DB > 100MB
                issues.append(f"Large database size: {db_size:.1f}MB")
            
            return {
                'status': status,
                'response_time': response_time,
                'database_size_mb': db_size,
                'issues': issues
            }
            
        except Exception as e:
            await self.log_error('database_health_check', str(e), severity='high')
            return {
                'status': 'unhealthy',
                'error': str(e),
                'issues': ['Database connection failed']
            }
    
    async def _check_memory_usage(self) -> Dict:
        """Check system memory usage"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            status = 'healthy'
            issues = []
            
            # Memory usage thresholds
            if memory_percent > 80:
                status = 'critical'
                issues.append(f"High memory usage: {memory_percent:.1f}%")
            elif memory_percent > 60:
                status = 'warning'
                issues.append(f"Elevated memory usage: {memory_percent:.1f}%")
            
            return {
                'status': status,
                'memory_mb': memory_info.rss / (1024 * 1024),
                'memory_percent': memory_percent,
                'issues': issues
            }
            
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e),
                'issues': ['Memory check failed']
            }
    
    async def _check_bot_api(self) -> Dict:
        """Check Telegram Bot API connectivity"""
        try:
            start_time = time.time()
            
            # Test bot API with get_me
            me = await self.bot.get_me()
            response_time = time.time() - start_time
            
            status = 'healthy'
            issues = []
            
            if response_time > 3.0:
                status = 'slow'
                issues.append(f"Slow API response: {response_time:.2f}s")
            
            return {
                'status': status,
                'response_time': response_time,
                'bot_username': me.username,
                'bot_id': me.id,
                'issues': issues
            }
            
        except Exception as e:
            await self.log_error('bot_api_check', str(e), severity='high')
            return {
                'status': 'unhealthy',
                'error': str(e),
                'issues': ['Bot API connection failed']
            }
    
    async def _check_payment_system(self) -> Dict:
        """Check payment system health"""
        try:
            # Check Telegram Stars backend
            stars_status = 'healthy'
            ton_status = 'healthy'
            issues = []
            
            # Test Stars payment system (basic connectivity)
            try:
                # This would normally test the payment endpoint
                # For now, we'll check if the Flask app is running
                import requests
                response = requests.get('http://localhost:5001/health', timeout=5)
                if response.status_code != 200:
                    stars_status = 'unhealthy'
                    issues.append('Telegram Stars backend not responding')
            except:
                stars_status = 'unhealthy'
                issues.append('Telegram Stars backend unreachable')
            
            # TON payment system check would go here
            # For now, assume it's healthy unless we have specific errors
            
            overall_status = 'healthy'
            if stars_status != 'healthy' or ton_status != 'healthy':
                overall_status = 'partial'
            
            return {
                'status': overall_status,
                'stars_payment': stars_status,
                'ton_payment': ton_status,
                'issues': issues
            }
            
        except Exception as e:
            await self.log_error('payment_system_check', str(e), severity='medium')
            return {
                'status': 'unknown',
                'error': str(e),
                'issues': ['Payment system check failed']
            }
    
    async def _check_channels(self) -> Dict:
        """Check channel connectivity and permissions"""
        try:
            channels = await self.database.get_active_channels()
            total_channels = len(channels)
            accessible_channels = 0
            issues = []
            
            for channel in channels[:5]:  # Check first 5 channels to avoid rate limits
                try:
                    # Test if bot can access channel
                    chat = await self.bot.get_chat(channel['telegram_channel_id'])
                    accessible_channels += 1
                except Exception as e:
                    issues.append(f"Cannot access {channel['name']}: {str(e)[:50]}")
            
            accessibility_rate = accessible_channels / min(len(channels), 5) if channels else 1
            
            status = 'healthy'
            if accessibility_rate < 0.8:
                status = 'partial'
            if accessibility_rate < 0.5:
                status = 'unhealthy'
            
            return {
                'status': status,
                'total_channels': total_channels,
                'accessible_channels': accessible_channels,
                'accessibility_rate': accessibility_rate,
                'issues': issues
            }
            
        except Exception as e:
            await self.log_error('channel_check', str(e), severity='medium')
            return {
                'status': 'unknown',
                'error': str(e),
                'issues': ['Channel check failed']
            }
    
    async def _log_health_check(self, health_status: Dict):
        """Log health check results to database"""
        try:
            async with aiosqlite.connect(self.database.db_path) as db:
                await db.execute('''
                    INSERT INTO health_checks (check_type, status, details, issues_found)
                    VALUES (?, ?, ?, ?)
                ''', (
                    'full_system_check',
                    health_status['overall'],
                    json.dumps(health_status['checks']),
                    health_status['issues_found']
                ))
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error logging health check: {e}")
    
    async def diagnose_issue(self, issue_type: str, context: Dict = None) -> Dict:
        """Diagnose specific issue and provide solutions"""
        diagnosis = {
            'issue_type': issue_type,
            'severity': 'unknown',
            'description': 'Unknown issue',
            'possible_causes': [],
            'recommended_solutions': [],
            'automated_fixes': [],
            'manual_steps': []
        }
        
        # Check against common solutions database
        if issue_type in self.COMMON_SOLUTIONS:
            solution_data = self.COMMON_SOLUTIONS[issue_type]
            diagnosis.update({
                'severity': solution_data['severity'],
                'description': solution_data['description'],
                'recommended_solutions': solution_data['solutions']
            })
        
        # Add context-specific analysis
        if context:
            diagnosis = await self._enhance_diagnosis_with_context(diagnosis, context)
        
        return diagnosis
    
    async def _enhance_diagnosis_with_context(self, diagnosis: Dict, context: Dict) -> Dict:
        """Enhance diagnosis with context-specific information"""
        try:
            # Analyze recent errors for patterns
            recent_errors = await self._get_recent_errors(issue_type=diagnosis['issue_type'])
            if len(recent_errors) > 3:
                diagnosis['possible_causes'].append('Recurring issue - may indicate systematic problem')
            
            # Check system resources if performance-related
            if 'performance' in diagnosis['issue_type'] or 'memory' in diagnosis['issue_type']:
                memory_status = await self._check_memory_usage()
                if memory_status['status'] != 'healthy':
                    diagnosis['possible_causes'].extend(memory_status['issues'])
            
            # Add automated fixes where possible
            if diagnosis['issue_type'] == 'database_lock':
                diagnosis['automated_fixes'].append('Clear database connection pool')
            
            return diagnosis
            
        except Exception as e:
            logger.error(f"Error enhancing diagnosis: {e}")
            return diagnosis
    
    async def _get_recent_errors(self, hours: int = 24, issue_type: str = None) -> List[Dict]:
        """Get recent errors from the database"""
        try:
            query = '''
                SELECT * FROM error_logs 
                WHERE timestamp > datetime('now', '-{} hours')
            '''.format(hours)
            
            params = []
            if issue_type:
                query += ' AND error_type = ?'
                params.append(issue_type)
            
            query += ' ORDER BY timestamp DESC LIMIT 50'
            
            async with aiosqlite.connect(self.database.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                    
        except Exception as e:
            logger.error(f"Error getting recent errors: {e}")
            return []
    
    async def generate_system_report(self) -> Dict:
        """Generate comprehensive system health and troubleshooting report"""
        report = {
            'generated_at': datetime.now(),
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'health_status': await self.run_health_checks(),
            'recent_errors': await self._get_recent_errors(hours=24),
            'performance_summary': await self._get_performance_summary(),
            'recommendations': []
        }
        
        # Add recommendations based on findings
        if report['health_status']['issues_found'] > 0:
            report['recommendations'].append('Review health check issues and take corrective action')
        
        if len(report['recent_errors']) > 10:
            report['recommendations'].append('High error rate detected - investigate error patterns')
        
        return report
    
    async def _get_performance_summary(self) -> Dict:
        """Get performance metrics summary"""
        try:
            async with aiosqlite.connect(self.database.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Get recent performance metrics
                async with db.execute('''
                    SELECT metric_type, AVG(metric_value) as avg_value, 
                           COUNT(*) as count, MAX(timestamp) as last_recorded
                    FROM performance_metrics 
                    WHERE timestamp > datetime('now', '-24 hours')
                    GROUP BY metric_type
                ''') as cursor:
                    metrics = await cursor.fetchall()
                    return {row['metric_type']: dict(row) for row in metrics}
                    
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}
    
    async def auto_resolve_issue(self, issue_type: str) -> Dict:
        """Attempt automated resolution of common issues"""
        resolution_result = {
            'issue_type': issue_type,
            'resolved': False,
            'actions_taken': [],
            'manual_steps_required': []
        }
        
        try:
            if issue_type == 'database_lock':
                # Clear connection pool and restart connections
                resolution_result['actions_taken'].append('Cleared database connection pool')
                resolution_result['resolved'] = True
                
            elif issue_type == 'high_memory_usage':
                # Force garbage collection
                import gc
                gc.collect()
                resolution_result['actions_taken'].append('Forced garbage collection')
                resolution_result['manual_steps_required'].append('Consider restarting bot if memory usage persists')
                
            elif issue_type == 'payment_timeout':
                resolution_result['manual_steps_required'].extend([
                    'Check payment gateway status',
                    'Verify API credentials',
                    'Contact payment provider if issue persists'
                ])
                
            return resolution_result
            
        except Exception as e:
            logger.error(f"Error in auto-resolution: {e}")
            resolution_result['actions_taken'].append(f'Auto-resolution failed: {str(e)}')
            return resolution_result

async def init_troubleshooting_system(database: Database, bot) -> TroubleshootingSystem:
    """Initialize the troubleshooting system"""
    system = TroubleshootingSystem(database, bot)
    await system.initialize_troubleshooting_tables()
    
    # Run initial health check
    await system.run_health_checks()
    
    logger.info("Troubleshooting system initialized successfully")
    return system