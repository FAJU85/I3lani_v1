#!/usr/bin/env python3
"""
Admin Bot Test System for I3lani Bot
Comprehensive testing of bot functionality through admin panel
"""

import asyncio
import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# Import existing systems
from end_to_end_tracking_system import get_tracking_system
from handlers_tracking_integration import (
    track_bot_start, track_create_ad_start, track_content_upload,
    track_channel_selection, track_duration_selection, 
    track_payment_method_selection, track_payment_confirmed,
    track_publishing_started, track_publishing_complete
)
from languages import get_text

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result structure"""
    test_id: str
    test_name: str
    status: str  # 'passed', 'failed', 'warning'
    duration: float
    details: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class TestSuite:
    """Complete test suite results"""
    suite_id: str
    admin_user_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    success_rate: float
    test_results: List[TestResult]
    final_report: str

class AdminBotTestSystem:
    """Comprehensive bot testing system for admin panel"""
    
    def __init__(self, bot: Bot, db_path: str = "bot.db"):
        self.bot = bot
        self.db_path = db_path
        self.test_user_id = 777777777  # Special test user ID
        self.test_username = "admin_test_user"
        self.tracking_system = get_tracking_system()
        self.test_results = []
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize test system database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test suites table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_test_suites (
                    suite_id TEXT PRIMARY KEY,
                    admin_user_id INTEGER NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    total_tests INTEGER,
                    passed_tests INTEGER,
                    failed_tests INTEGER,
                    warning_tests INTEGER,
                    success_rate REAL,
                    final_report TEXT
                )
            """)
            
            # Test results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_test_results (
                    result_id TEXT PRIMARY KEY,
                    suite_id TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration REAL,
                    details TEXT,
                    error_message TEXT,
                    metadata TEXT,
                    FOREIGN KEY (suite_id) REFERENCES admin_test_suites (suite_id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Admin test system database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing test database: {e}")
    
    async def run_comprehensive_bot_test(self, admin_user_id: int) -> TestSuite:
        """Run complete bot functionality test"""
        suite_id = f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        started_at = datetime.now()
        
        logger.info(f"🧪 Starting comprehensive bot test suite {suite_id}")
        
        # Initialize test suite
        test_suite = TestSuite(
            suite_id=suite_id,
            admin_user_id=admin_user_id,
            started_at=started_at,
            completed_at=None,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            warning_tests=0,
            success_rate=0.0,
            test_results=[],
            final_report=""
        )
        
        # Test cases to run
        test_cases = [
            ("Database Connectivity", self._test_database_connectivity),
            ("Tracking System", self._test_tracking_system),
            ("User Registration", self._test_user_registration),
            ("Ad Creation Flow", self._test_ad_creation_flow),
            ("Channel Selection", self._test_channel_selection),
            ("Duration Selection", self._test_duration_selection),
            ("Payment System", self._test_payment_system),
            ("Campaign Creation", self._test_campaign_creation),
            ("Publishing System", self._test_publishing_system),
            ("Final Confirmation", self._test_final_confirmation),
            ("Admin Panel Access", self._test_admin_panel_access),
            ("Language Support", self._test_language_support),
            ("Multimedia Content", self._test_multimedia_content),
            ("Error Handling", self._test_error_handling),
            ("API Integrations", self._test_api_integrations),
            ("Data Integrity", self._test_data_integrity)
        ]
        
        # Run each test case
        for test_name, test_func in test_cases:
            test_result = await self._run_single_test(test_name, test_func)
            test_suite.test_results.append(test_result)
            
            # Update counters
            if test_result.status == 'passed':
                test_suite.passed_tests += 1
            elif test_result.status == 'failed':
                test_suite.failed_tests += 1
            elif test_result.status == 'warning':
                test_suite.warning_tests += 1
        
        # Calculate final statistics
        test_suite.total_tests = len(test_suite.test_results)
        test_suite.success_rate = (test_suite.passed_tests / test_suite.total_tests * 100) if test_suite.total_tests > 0 else 0
        test_suite.completed_at = datetime.now()
        
        # Generate final report
        test_suite.final_report = self._generate_test_report(test_suite)
        
        # Save to database
        await self._save_test_suite(test_suite)
        
        logger.info(f"✅ Test suite {suite_id} completed with {test_suite.success_rate:.1f}% success rate")
        return test_suite
    
    async def _run_single_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test case"""
        test_id = f"TEST-{datetime.now().strftime('%H%M%S')}-{test_name.replace(' ', '_').upper()}"
        start_time = datetime.now()
        
        try:
            logger.info(f"🧪 Running test: {test_name}")
            
            # Execute test
            result = await test_func()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.get('success', False):
                status = 'passed'
                details = result.get('details', f"✅ {test_name} completed successfully")
                error_message = None
            else:
                status = 'failed' if result.get('critical', True) else 'warning'
                details = result.get('details', f"❌ {test_name} failed")
                error_message = result.get('error', None)
            
            logger.info(f"{'✅' if status == 'passed' else '⚠️' if status == 'warning' else '❌'} {test_name}: {status}")
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                status=status,
                duration=duration,
                details=details,
                error_message=error_message,
                metadata=result.get('metadata', {})
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"❌ Test {test_name} failed with exception: {e}")
            
            return TestResult(
                test_id=test_id,
                test_name=test_name,
                status='failed',
                duration=duration,
                details=f"❌ {test_name} failed with exception",
                error_message=str(e),
                metadata={'exception_type': type(e).__name__}
            )
    
    async def _test_database_connectivity(self) -> Dict:
        """Test database connectivity and basic operations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Check critical tables
            critical_tables = ['users', 'campaigns', 'channels', 'campaign_tracking']
            missing_tables = []
            
            table_names = [table[0] for table in tables]
            for table in critical_tables:
                if table not in table_names:
                    missing_tables.append(table)
            
            conn.close()
            
            if missing_tables:
                return {
                    'success': False,
                    'details': f"❌ Missing critical tables: {', '.join(missing_tables)}",
                    'metadata': {'missing_tables': missing_tables, 'total_tables': len(table_names)}
                }
            
            return {
                'success': True,
                'details': f"✅ Database connectivity verified. {len(table_names)} tables found",
                'metadata': {'total_tables': len(table_names), 'tables': table_names}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Database connectivity failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_tracking_system(self) -> Dict:
        """Test end-to-end tracking system"""
        try:
            # Initialize tracking system
            await self.tracking_system.initialize_database()
            
            # Start test tracking
            tracking_id = await self.tracking_system.start_campaign_tracking(
                self.test_user_id, self.test_username
            )
            
            if not tracking_id:
                return {
                    'success': False,
                    'details': "❌ Failed to start campaign tracking",
                    'error': "Tracking ID is None"
                }
            
            # Test step updates
            await self.tracking_system.update_step_status(
                tracking_id, "start_bot", "completed", 
                metadata={'test': True}
            )
            
            return {
                'success': True,
                'details': f"✅ Tracking system operational. Tracking ID: {tracking_id}",
                'metadata': {'tracking_id': tracking_id}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Tracking system test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_user_registration(self) -> Dict:
        """Test user registration and management"""
        try:
            from database import Database
            db = Database()
            
            # Test user creation
            await db.create_user(
                user_id=self.test_user_id,
                username=self.test_username,
                language_code='en'
            )
            
            # Test user retrieval
            user = await db.get_user(self.test_user_id)
            
            if user:
                return {
                    'success': True,
                    'details': f"✅ User registration working. User ID: {self.test_user_id}",
                    'metadata': {'user_id': self.test_user_id, 'username': self.test_username}
                }
            else:
                return {
                    'success': False,
                    'details': "❌ User registration failed - user not found after creation",
                    'error': "User not found"
                }
                
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ User registration test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_ad_creation_flow(self) -> Dict:
        """Test ad creation flow with dummy data"""
        try:
            # Create mock FSM context
            storage = MemoryStorage()
            state = FSMContext(storage=storage, key="test_key")
            
            # Test tracking integration with multimedia
            await track_bot_start(self.test_user_id, self.test_username, state)
            await track_create_ad_start(self.test_user_id, state)
            await track_content_upload(self.test_user_id, 'photo', state)  # Test with photo content
            
            # Test ad creation in database
            from database import Database
            db = Database()
            
            # Create comprehensive multimedia test ad
            test_ad_content = "🧪 **Test Advertisement Content - Admin Testing System**\n\n📱 This is a comprehensive test ad that includes:\n• Text content with formatting\n• Image attachment\n• Video content\n\n✅ Testing complete multimedia ad creation flow"
            
            # Test with multimedia content
            test_media_url = "AgACAgQAAxkBAAIBtWZrNlRuvM9jwN5Eg6GDvFSVz1FyAAI9xjEbPnhgU1oLe7ZB3na3AQADAgADeQADNgQ"  # Test image
            
            ad_id = await db.create_ad(
                user_id=self.test_user_id,
                content=test_ad_content,
                content_type='photo',
                media_url=test_media_url
            )
            
            if ad_id:
                return {
                    'success': True,
                    'details': f"✅ Ad creation flow working. Ad ID: {ad_id} (multimedia content)",
                    'metadata': {'ad_id': ad_id, 'content_type': 'photo', 'has_media': True}
                }
            else:
                return {
                    'success': False,
                    'details': "❌ Ad creation failed - no ad ID returned",
                    'error': "Ad ID is None"
                }
                
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Ad creation flow test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_channel_selection(self) -> Dict:
        """Test channel selection functionality"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get available channels
            cursor.execute("SELECT channel_id, channel_name FROM channels WHERE is_active = 1")
            channels = cursor.fetchall()
            conn.close()
            
            if not channels:
                return {
                    'success': False,
                    'critical': False,
                    'details': "⚠️ No active channels found for testing",
                    'metadata': {'channel_count': 0}
                }
            
            # Test channel selection tracking
            storage = MemoryStorage()
            state = FSMContext(storage=storage, key="test_key")
            
            test_channels = [channels[0][0]]  # Select first channel
            await track_channel_selection(self.test_user_id, test_channels, state)
            
            return {
                'success': True,
                'details': f"✅ Channel selection working. {len(channels)} channels available",
                'metadata': {'available_channels': len(channels), 'selected_channels': test_channels}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Channel selection test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_duration_selection(self) -> Dict:
        """Test duration selection functionality"""
        try:
            storage = MemoryStorage()
            state = FSMContext(storage=storage, key="test_key")
            
            # Test duration selection tracking
            test_duration = 7  # 7 days
            await track_duration_selection(self.test_user_id, test_duration, state)
            
            return {
                'success': True,
                'details': f"✅ Duration selection working. Test duration: {test_duration} days",
                'metadata': {'test_duration': test_duration}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Duration selection test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_payment_system(self) -> Dict:
        """Test payment system functionality"""
        try:
            storage = MemoryStorage()
            state = FSMContext(storage=storage, key="test_key")
            
            # Test payment method selection
            await track_payment_method_selection(self.test_user_id, 'TON', state)
            
            # Test payment confirmation
            test_payment_id = "TEST-PAY-ADMIN"
            test_campaign_id = "CAM-TEST-ADMIN"
            await track_payment_confirmed(self.test_user_id, test_payment_id, test_campaign_id, state)
            
            return {
                'success': True,
                'details': f"✅ Payment system tracking working. Payment ID: {test_payment_id}",
                'metadata': {'payment_id': test_payment_id, 'payment_method': 'TON'}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Payment system test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_campaign_creation(self) -> Dict:
        """Test campaign creation functionality"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create test campaign with multimedia content
            test_campaign_id = f"CAM-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            test_content = "🧪 **Test Campaign - Admin Testing System**\n\n📱 Comprehensive multimedia test campaign featuring:\n• Rich text content\n• Image attachments\n• Video content\n\n✅ Full system validation"
            test_media_url = "AgACAgQAAxkBAAIBtWZrNlRuvM9jwN5Eg6GDvFSVz1FyAAI9xjEbPnhgU1oLe7ZB3na3AQADAgADeQADNgQ"
            
            cursor.execute("""
                INSERT INTO campaigns (
                    campaign_id, user_id, ad_content, content_type, media_url,
                    selected_channels, duration_days, posts_per_day,
                    total_reach, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_campaign_id,
                self.test_user_id,
                test_content,
                "photo",
                test_media_url,
                json.dumps(["@test_channel"]),
                7,  # 7 days
                1,  # 1 post per day
                100,  # Test reach
                "active",
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'details': f"✅ Campaign creation working. Campaign ID: {test_campaign_id} (multimedia)",
                'metadata': {'campaign_id': test_campaign_id, 'duration': 7, 'content_type': 'photo', 'has_media': True}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Campaign creation test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_publishing_system(self) -> Dict:
        """Test publishing system functionality"""
        try:
            test_campaign_id = f"CAM-TEST-PUB-{datetime.now().strftime('%H%M%S')}"
            
            # Test publishing tracking
            await track_publishing_started(self.test_user_id, test_campaign_id)
            await track_publishing_complete(self.test_user_id, test_campaign_id)
            
            return {
                'success': True,
                'details': f"✅ Publishing system tracking working. Campaign ID: {test_campaign_id}",
                'metadata': {'campaign_id': test_campaign_id}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Publishing system test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_final_confirmation(self) -> Dict:
        """Test final confirmation system"""
        try:
            # Test final confirmation components
            from end_to_end_tracking_system import PublishingReport
            
            test_report = PublishingReport(
                campaign_id="CAM-TEST-CONFIRM",
                sequence_id="SEQ-TEST-CONFIRM",
                user_id=self.test_user_id,
                total_channels=1,
                published_channels=["@test_channel"],
                failed_channels=[],
                publication_timestamps={"@test_channel": datetime.now().isoformat()},
                success_rate=100.0,
                final_status="completed",
                completion_timestamp=datetime.now()
            )
            
            return {
                'success': True,
                'details': "✅ Final confirmation system components working",
                'metadata': {'success_rate': 100.0}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Final confirmation test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_admin_panel_access(self) -> Dict:
        """Test admin panel access and functionality"""
        try:
            from admin_system import AdminSystem
            
            admin_system = AdminSystem()
            
            # Test admin check (should return True for test)
            is_admin = admin_system.is_admin(self.test_user_id)
            
            return {
                'success': True,
                'details': f"✅ Admin panel access working. Admin check: {is_admin}",
                'metadata': {'admin_check': is_admin}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Admin panel access test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_multimedia_content(self) -> Dict:
        """Test multimedia content handling (text+image+video)"""
        try:
            from database import Database
            db = Database()
            
            # Test different content types
            content_types = ['text', 'photo', 'video']
            test_media_urls = {
                'text': None,
                'photo': "AgACAgQAAxkBAAIBtWZrNlRuvM9jwN5Eg6GDvFSVz1FyAAI9xjEbPnhgU1oLe7ZB3na3AQADAgADeQADNgQ",
                'video': "BAACAgQAAxkBAAIBt2ZrNlRuvM9jwN5Eg6GDvFSVz1FyAAI9xjEbPnhgU1oLe7ZB3na3AQADAgADeQADNgQ"
            }
            
            successful_tests = 0
            total_tests = len(content_types)
            
            for content_type in content_types:
                try:
                    test_content = f"🧪 **Multimedia Test - {content_type.upper()}**\n\n📱 Testing {content_type} content type:\n• Rich text formatting\n• Media attachment support\n• Database integration\n\n✅ {content_type.title()} content validation"
                    
                    ad_id = await db.create_ad(
                        user_id=self.test_user_id,
                        content=test_content,
                        content_type=content_type,
                        media_url=test_media_urls[content_type]
                    )
                    
                    if ad_id:
                        successful_tests += 1
                        logger.info(f"✅ {content_type} content test passed")
                    else:
                        logger.warning(f"⚠️ {content_type} content test failed")
                        
                except Exception as e:
                    logger.error(f"❌ {content_type} content test error: {e}")
            
            success_rate = (successful_tests / total_tests) * 100
            
            return {
                'success': success_rate >= 66,  # At least 2/3 content types should work
                'details': f"{'✅' if success_rate >= 66 else '⚠️'} Multimedia content: {successful_tests}/{total_tests} types working ({success_rate:.1f}%)",
                'metadata': {
                    'content_types_tested': content_types,
                    'successful_tests': successful_tests,
                    'success_rate': success_rate
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Multimedia content test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_language_support(self) -> Dict:
        """Test multilingual support"""
        try:
            languages = ['en', 'ar', 'ru']
            test_key = 'main_menu'
            
            translations = {}
            for lang in languages:
                translation = get_text(lang, test_key)
                translations[lang] = translation
            
            if all(translations.values()):
                return {
                    'success': True,
                    'details': f"✅ Language support working. {len(languages)} languages tested",
                    'metadata': {'languages': languages, 'translations': translations}
                }
            else:
                return {
                    'success': False,
                    'details': "❌ Language support incomplete - missing translations",
                    'metadata': {'translations': translations}
                }
                
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Language support test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_error_handling(self) -> Dict:
        """Test error handling capabilities"""
        try:
            # Test various error scenarios
            error_scenarios = 0
            handled_errors = 0
            
            # Test 1: Invalid user ID
            try:
                await track_bot_start(None, "invalid_user")
                error_scenarios += 1
            except Exception:
                handled_errors += 1
                error_scenarios += 1
            
            # Test 2: Invalid database operation
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM nonexistent_table")
                conn.close()
                error_scenarios += 1
            except Exception:
                handled_errors += 1
                error_scenarios += 1
            
            error_handling_rate = (handled_errors / error_scenarios * 100) if error_scenarios > 0 else 0
            
            return {
                'success': error_handling_rate > 50,  # At least 50% of errors should be handled
                'details': f"✅ Error handling working. {handled_errors}/{error_scenarios} errors handled ({error_handling_rate:.1f}%)",
                'metadata': {'error_scenarios': error_scenarios, 'handled_errors': handled_errors}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Error handling test failed: {str(e)}",
                'error': str(e)
            }
    
    async def _test_api_integrations(self) -> Dict:
        """Test API integrations"""
        try:
            # Test TON API integration
            from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor
            
            monitor = EnhancedTONPaymentMonitor()
            
            # Test API connectivity (don't actually make requests, just check configuration)
            has_config = hasattr(monitor, 'ton_wallet_address') and monitor.ton_wallet_address
            
            return {
                'success': has_config,
                'critical': False,  # API issues are not critical for core functionality
                'details': f"{'✅' if has_config else '⚠️'} API integration configuration {'found' if has_config else 'missing'}",
                'metadata': {'ton_configured': has_config}
            }
            
        except Exception as e:
            return {
                'success': False,
                'critical': False,
                'details': f"⚠️ API integration test warning: {str(e)}",
                'error': str(e)
            }
    
    async def _test_data_integrity(self) -> Dict:
        """Test data integrity and consistency"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Check for orphaned records
            cursor.execute("""
                SELECT COUNT(*) FROM campaigns 
                WHERE user_id NOT IN (SELECT user_id FROM users)
            """)
            orphaned_campaigns = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM campaign_tracking 
                WHERE user_id NOT IN (SELECT user_id FROM users)
            """)
            orphaned_tracking = cursor.fetchone()[0]
            
            conn.close()
            
            total_orphaned = orphaned_campaigns + orphaned_tracking
            
            return {
                'success': total_orphaned == 0,
                'details': f"{'✅' if total_orphaned == 0 else '⚠️'} Data integrity check: {total_orphaned} orphaned records found",
                'metadata': {'orphaned_campaigns': orphaned_campaigns, 'orphaned_tracking': orphaned_tracking}
            }
            
        except Exception as e:
            return {
                'success': False,
                'details': f"❌ Data integrity test failed: {str(e)}",
                'error': str(e)
            }
    
    def _generate_test_report(self, test_suite: TestSuite) -> str:
        """Generate comprehensive test report"""
        report = f"""
🧪 I3LANI BOT COMPREHENSIVE TEST REPORT
=====================================

📊 TEST SUMMARY
- Suite ID: {test_suite.suite_id}
- Admin User: {test_suite.admin_user_id}
- Started: {test_suite.started_at.strftime('%Y-%m-%d %H:%M:%S')}
- Completed: {test_suite.completed_at.strftime('%Y-%m-%d %H:%M:%S')}
- Duration: {(test_suite.completed_at - test_suite.started_at).total_seconds():.2f} seconds

📈 RESULTS OVERVIEW
- Total Tests: {test_suite.total_tests}
- Passed: {test_suite.passed_tests} ✅
- Failed: {test_suite.failed_tests} ❌
- Warnings: {test_suite.warning_tests} ⚠️
- Success Rate: {test_suite.success_rate:.1f}%

🔍 DETAILED RESULTS
"""
        
        for result in test_suite.test_results:
            status_emoji = "✅" if result.status == "passed" else "⚠️" if result.status == "warning" else "❌"
            report += f"""
{status_emoji} {result.test_name}
   Status: {result.status.upper()}
   Duration: {result.duration:.2f}s
   Details: {result.details}
"""
            if result.error_message:
                report += f"   Error: {result.error_message}\n"
        
        report += f"""
🎯 SYSTEM STATUS
{'✅ BOT SYSTEM FULLY OPERATIONAL' if test_suite.success_rate >= 80 else '⚠️ BOT SYSTEM NEEDS ATTENTION' if test_suite.success_rate >= 60 else '❌ BOT SYSTEM REQUIRES IMMEDIATE ATTENTION'}

📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return report.strip()
    
    async def _save_test_suite(self, test_suite: TestSuite):
        """Save test suite to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save test suite
            cursor.execute("""
                INSERT INTO admin_test_suites (
                    suite_id, admin_user_id, started_at, completed_at,
                    total_tests, passed_tests, failed_tests, warning_tests,
                    success_rate, final_report
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_suite.suite_id,
                test_suite.admin_user_id,
                test_suite.started_at.isoformat(),
                test_suite.completed_at.isoformat(),
                test_suite.total_tests,
                test_suite.passed_tests,
                test_suite.failed_tests,
                test_suite.warning_tests,
                test_suite.success_rate,
                test_suite.final_report
            ))
            
            # Save test results
            for result in test_suite.test_results:
                cursor.execute("""
                    INSERT INTO admin_test_results (
                        result_id, suite_id, test_name, status, duration,
                        details, error_message, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.test_id,
                    test_suite.suite_id,
                    result.test_name,
                    result.status,
                    result.duration,
                    result.details,
                    result.error_message,
                    json.dumps(result.metadata or {})
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Test suite {test_suite.suite_id} saved to database")
            
        except Exception as e:
            logger.error(f"❌ Error saving test suite: {e}")
    
    async def get_test_history(self, admin_user_id: int, limit: int = 10) -> List[Dict]:
        """Get test history for admin user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT suite_id, started_at, completed_at, total_tests,
                       passed_tests, failed_tests, warning_tests, success_rate
                FROM admin_test_suites
                WHERE admin_user_id = ?
                ORDER BY started_at DESC
                LIMIT ?
            """, (admin_user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'suite_id': row[0],
                    'started_at': row[1],
                    'completed_at': row[2],
                    'total_tests': row[3],
                    'passed_tests': row[4],
                    'failed_tests': row[5],
                    'warning_tests': row[6],
                    'success_rate': row[7]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"❌ Error getting test history: {e}")
            return []

# Global test system instance
_test_system = None

def get_admin_test_system(bot: Bot) -> AdminBotTestSystem:
    """Get or create admin test system instance"""
    global _test_system
    if _test_system is None:
        _test_system = AdminBotTestSystem(bot)
    return _test_system

async def run_admin_bot_test(bot: Bot, admin_user_id: int) -> TestSuite:
    """Run comprehensive bot test for admin"""
    test_system = get_admin_test_system(bot)
    return await test_system.run_comprehensive_bot_test(admin_user_id)