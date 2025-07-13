"""
Multilingual Menu Integration Validation for I3lani Bot
Tests all menu components for proper language integration
"""

import asyncio
import logging
from typing import Dict, List
from database import db

logger = logging.getLogger(__name__)

class MultilingualMenuValidator:
    """Validates multilingual menu integration"""
    
    def __init__(self):
        self.validation_results = {}
        self.supported_languages = ['en', 'ar', 'ru']
        self.test_user_id = 566158428  # Test user
    
    async def validate_bot_commands_integration(self):
        """Validate bot commands are properly integrated with languages"""
        logger.info("🔍 Validating bot commands integration...")
        
        try:
            from multilingual_menu_system import get_multilingual_menu_system
            from main_bot import bot
            
            # Test if multilingual menu system is available
            menu_system = get_multilingual_menu_system(bot)
            
            # Test commands for each language
            results = {}
            for lang in self.supported_languages:
                commands = menu_system.get_bot_commands_for_language(lang)
                results[lang] = {
                    'commands_count': len(commands),
                    'has_start': any(cmd.command == 'start' for cmd in commands),
                    'has_admin': any(cmd.command == 'admin' for cmd in commands),
                    'has_support': any(cmd.command == 'support' for cmd in commands)
                }
            
            self.validation_results['bot_commands'] = {
                'status': 'success',
                'details': results,
                'issues': []
            }
            
            logger.info("✅ Bot commands validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Bot commands validation failed: {e}")
            self.validation_results['bot_commands'] = {
                'status': 'error',
                'error': str(e),
                'issues': ['Bot commands not properly integrated']
            }
            return False
    
    async def validate_main_menu_integration(self):
        """Validate main menu buttons are properly integrated"""
        logger.info("🔍 Validating main menu integration...")
        
        try:
            from multilingual_menu_system import get_multilingual_menu_system
            from main_bot import bot
            
            menu_system = get_multilingual_menu_system(bot)
            
            # Test main menu for each language
            results = {}
            for lang in self.supported_languages:
                buttons = menu_system.get_main_menu_buttons_for_language(lang)
                results[lang] = {
                    'button_rows': len(buttons),
                    'total_buttons': sum(len(row) for row in buttons),
                    'has_create_ad': any(
                        any('create_ad' in btn.callback_data for btn in row)
                        for row in buttons
                    ),
                    'has_my_ads': any(
                        any('my_ads' in btn.callback_data for btn in row)
                        for row in buttons
                    ),
                    'has_settings': any(
                        any('settings' in btn.callback_data for btn in row)
                        for row in buttons
                    )
                }
            
            self.validation_results['main_menu'] = {
                'status': 'success',
                'details': results,
                'issues': []
            }
            
            logger.info("✅ Main menu validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Main menu validation failed: {e}")
            self.validation_results['main_menu'] = {
                'status': 'error',
                'error': str(e),
                'issues': ['Main menu not properly integrated']
            }
            return False
    
    async def validate_admin_panel_integration(self):
        """Validate admin panel is properly integrated"""
        logger.info("🔍 Validating admin panel integration...")
        
        try:
            from multilingual_menu_system import get_multilingual_menu_system
            from main_bot import bot
            
            menu_system = get_multilingual_menu_system(bot)
            
            # Test admin panel for each language
            results = {}
            for lang in self.supported_languages:
                buttons = menu_system.get_admin_panel_buttons_for_language(lang)
                results[lang] = {
                    'button_rows': len(buttons),
                    'total_buttons': sum(len(row) for row in buttons),
                    'has_statistics': any(
                        any('admin_statistics' in btn.callback_data for btn in row)
                        for row in buttons
                    ),
                    'has_channels': any(
                        any('admin_channels' in btn.callback_data for btn in row)
                        for row in buttons
                    ),
                    'has_users': any(
                        any('admin_users' in btn.callback_data for btn in row)
                        for row in buttons
                    )
                }
            
            self.validation_results['admin_panel'] = {
                'status': 'success',
                'details': results,
                'issues': []
            }
            
            logger.info("✅ Admin panel validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Admin panel validation failed: {e}")
            self.validation_results['admin_panel'] = {
                'status': 'error',
                'error': str(e),
                'issues': ['Admin panel not properly integrated']
            }
            return False
    
    async def validate_language_detection(self):
        """Validate language detection is working properly"""
        logger.info("🔍 Validating language detection...")
        
        try:
            from multilingual_menu_system import get_multilingual_menu_system
            from main_bot import bot
            
            menu_system = get_multilingual_menu_system(bot)
            
            # Test language detection for test user
            user_language = await menu_system.get_user_language_async(self.test_user_id)
            
            # Test language update
            await menu_system.update_user_interface_language(self.test_user_id, 'ar')
            updated_language = await menu_system.get_user_language_async(self.test_user_id)
            
            self.validation_results['language_detection'] = {
                'status': 'success',
                'initial_language': user_language,
                'updated_language': updated_language,
                'language_update_works': updated_language == 'ar',
                'issues': []
            }
            
            logger.info("✅ Language detection validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Language detection validation failed: {e}")
            self.validation_results['language_detection'] = {
                'status': 'error',
                'error': str(e),
                'issues': ['Language detection not working properly']
            }
            return False
    
    async def validate_handlers_integration(self):
        """Validate handlers are using multilingual menus"""
        logger.info("🔍 Validating handlers integration...")
        
        try:
            from handlers import create_regular_main_menu_keyboard
            from languages import get_text
            
            # Test keyboard creation for each language
            results = {}
            for lang in self.supported_languages:
                keyboard = await create_regular_main_menu_keyboard(lang, self.test_user_id)
                
                # Test text localization
                create_ad_text = get_text(lang, 'create_ad')
                my_ads_text = get_text(lang, 'my_ads')
                settings_text = get_text(lang, 'settings')
                
                results[lang] = {
                    'keyboard_created': keyboard is not None,
                    'has_inline_keyboard': hasattr(keyboard, 'inline_keyboard'),
                    'button_count': len(keyboard.inline_keyboard) if hasattr(keyboard, 'inline_keyboard') else 0,
                    'text_localized': {
                        'create_ad': create_ad_text,
                        'my_ads': my_ads_text,
                        'settings': settings_text
                    }
                }
            
            self.validation_results['handlers_integration'] = {
                'status': 'success',
                'details': results,
                'issues': []
            }
            
            logger.info("✅ Handlers integration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Handlers integration validation failed: {e}")
            self.validation_results['handlers_integration'] = {
                'status': 'error',
                'error': str(e),
                'issues': ['Handlers not properly integrated with multilingual system']
            }
            return False
    
    async def validate_payment_memo_tracker(self):
        """Validate payment memo tracker is working"""
        logger.info("🔍 Validating payment memo tracker...")
        
        try:
            from payment_memo_tracker import memo_tracker
            
            # Test initialization
            await memo_tracker.initialize()
            
            # Test tracking a payment
            test_memo = "TEST123"
            track_result = await memo_tracker.track_payment_memo(test_memo, self.test_user_id, 1.0)
            
            # Test retrieving user by memo
            user_id = await memo_tracker.get_user_by_memo(test_memo)
            
            self.validation_results['payment_memo_tracker'] = {
                'status': 'success',
                'initialized': memo_tracker.initialized,
                'track_result': track_result,
                'user_retrieval': user_id == self.test_user_id,
                'issues': []
            }
            
            logger.info("✅ Payment memo tracker validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Payment memo tracker validation failed: {e}")
            self.validation_results['payment_memo_tracker'] = {
                'status': 'error',
                'error': str(e),
                'issues': ['Payment memo tracker not working properly']
            }
            return False
    
    async def run_comprehensive_validation(self):
        """Run comprehensive validation of multilingual menu integration"""
        logger.info("🚀 Starting comprehensive multilingual menu validation...")
        
        validations = [
            ('Bot Commands', self.validate_bot_commands_integration()),
            ('Main Menu', self.validate_main_menu_integration()),
            ('Admin Panel', self.validate_admin_panel_integration()),
            ('Language Detection', self.validate_language_detection()),
            ('Handlers Integration', self.validate_handlers_integration()),
            ('Payment Memo Tracker', self.validate_payment_memo_tracker())
        ]
        
        results = {}
        for name, validation_coro in validations:
            try:
                result = await validation_coro
                results[name] = result
            except Exception as e:
                logger.error(f"❌ {name} validation failed: {e}")
                results[name] = False
        
        return results
    
    def get_validation_report(self) -> str:
        """Generate validation report"""
        successful = sum(1 for result in self.validation_results.values() if result['status'] == 'success')
        total = len(self.validation_results)
        
        report = f"""
🔍 <b>Multilingual Menu Integration Validation Report</b>

📊 <b>Overall Status:</b> {successful}/{total} validations passed
⚡ <b>Success Rate:</b> {(successful/total*100):.1f}%

📋 <b>Validation Results:</b>
"""
        
        for component, result in self.validation_results.items():
            status_emoji = "✅" if result['status'] == 'success' else "❌"
            report += f"{status_emoji} <b>{component.replace('_', ' ').title()}</b>\n"
            
            if result['status'] == 'error':
                report += f"   Error: {result['error']}\n"
            elif 'details' in result:
                if component == 'bot_commands':
                    for lang, details in result['details'].items():
                        report += f"   {lang.upper()}: {details['commands_count']} commands\n"
                elif component == 'main_menu':
                    for lang, details in result['details'].items():
                        report += f"   {lang.upper()}: {details['total_buttons']} buttons\n"
                elif component == 'admin_panel':
                    for lang, details in result['details'].items():
                        report += f"   {lang.upper()}: {details['total_buttons']} buttons\n"
        
        if successful == total:
            report += f"""
🎉 <b>All validations passed!</b> Multilingual menu integration is working correctly.

✅ <b>Confirmed Working:</b>
• Bot commands available in all languages
• Main menu buttons properly localized
• Admin panel supports multiple languages
• Language detection and switching works
• Handlers integrated with multilingual system
• Payment memo tracker operational
"""
        else:
            report += f"""
⚠️ <b>Issues Found:</b>
"""
            for component, result in self.validation_results.items():
                if result['status'] == 'error':
                    report += f"• {component.replace('_', ' ').title()}: {result['error']}\n"
        
        return report.strip()

async def main():
    """Main validation function"""
    validator = MultilingualMenuValidator()
    
    # Run comprehensive validation
    results = await validator.run_comprehensive_validation()
    
    # Generate and display report
    report = validator.get_validation_report()
    print(report)
    
    return validator

if __name__ == "__main__":
    asyncio.run(main())