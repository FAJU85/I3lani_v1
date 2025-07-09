"""
I3lani Bot Debugging & Logging System
Comprehensive logging with step identifiers for debugging and traceability
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

class StepLogger:
    """
    Step-based logging system for debugging and traceability
    Each process step has a unique identifier for easy debugging
    """
    
    def __init__(self):
        self.logger = logging.getLogger('i3lani_steps')
        self.current_session = {}
        
    def log_step(self, step_name: str, user_id: int, action: str, data: Optional[Dict] = None, success: bool = True):
        """
        Log a step in the user flow
        
        Args:
            step_name: Unique step identifier (e.g., "CreateAd_Step_3_SelectDays")
            user_id: User ID for tracking
            action: Description of what happened
            data: Additional data to log
            success: Whether the step succeeded
        """
        level = logging.INFO if success else logging.ERROR
        
        log_entry = {
            'step': step_name,
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'success': success
        }
        
        if data:
            log_entry['data'] = data
            
        # Store in session for debugging
        if user_id not in self.current_session:
            self.current_session[user_id] = []
        self.current_session[user_id].append(log_entry)
        
        # Log to file
        status = "SUCCESS" if success else "ERROR"
        self.logger.log(level, f"[{status}] {step_name} - User {user_id}: {action}")
        
        if data:
            self.logger.log(level, f"[{status}] {step_name} - Data: {json.dumps(data)}")
    
    def log_error(self, step_name: str, user_id: int, error: Exception, context: Optional[Dict] = None):
        """
        Log an error with full context
        
        Args:
            step_name: Step where error occurred
            user_id: User ID
            error: Exception object
            context: Additional context data
        """
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self.log_step(step_name, user_id, f"ERROR: {str(error)}", error_data, success=False)
        
        # Log full traceback for debugging
        import traceback
        self.logger.error(f"[ERROR] {step_name} - User {user_id} - Full traceback:\n{traceback.format_exc()}")
    
    def get_user_session(self, user_id: int) -> list:
        """Get all logged steps for a user session"""
        return self.current_session.get(user_id, [])
    
    def clear_user_session(self, user_id: int):
        """Clear session data for a user"""
        if user_id in self.current_session:
            del self.current_session[user_id]
    
    def get_step_statistics(self) -> Dict[str, Any]:
        """Get statistics about step success rates"""
        stats = {}
        for user_id, steps in self.current_session.items():
            for step in steps:
                step_name = step['step']
                if step_name not in stats:
                    stats[step_name] = {'total': 0, 'success': 0, 'error': 0}
                
                stats[step_name]['total'] += 1
                if step['success']:
                    stats[step_name]['success'] += 1
                else:
                    stats[step_name]['error'] += 1
        
        # Calculate success rates
        for step_name in stats:
            total = stats[step_name]['total']
            success = stats[step_name]['success']
            stats[step_name]['success_rate'] = (success / total * 100) if total > 0 else 0
        
        return stats

# Global logger instance
step_logger = StepLogger()

# Step name constants for consistency
class StepNames:
    """Consistent step names for debugging"""
    
    # User Flow Steps
    START_COMMAND = "User_Flow_1_Start"
    LANGUAGE_SELECTION = "User_Flow_2_LanguageSelection"
    MAIN_MENU = "User_Flow_3_MainMenu"
    
    # Ad Creation Steps
    CREATE_AD_START = "CreateAd_Step_1_Start"
    UPLOAD_CONTENT = "CreateAd_Step_2_UploadContent"
    SELECT_CHANNELS = "CreateAd_Step_3_SelectChannels"
    SELECT_DAYS = "CreateAd_Step_4_SelectDays"
    SELECT_POSTS_PER_DAY = "CreateAd_Step_5_PostsPerDay"
    CALCULATE_PRICE = "CreateAd_Step_6_CalculatePrice"
    SHOW_SUMMARY = "CreateAd_Step_7_ShowSummary"
    
    # Payment Steps
    PAYMENT_METHOD_SELECTION = "Payment_Step_1_ChooseMethod"
    TON_PAYMENT_INIT = "Payment_Step_2_TON_Init"
    TON_PAYMENT_MONITOR = "Payment_Step_3_TON_Monitor"
    TON_PAYMENT_CONFIRM = "Payment_Step_4_TON_Confirm"
    STARS_PAYMENT_INIT = "Payment_Step_2_Stars_Init"
    STARS_PAYMENT_CONFIRM = "Payment_Step_3_Stars_Confirm"
    PAYMENT_TIMEOUT = "Payment_Step_Error_Timeout"
    
    # Admin Steps
    ADMIN_ACCESS = "Admin_Step_1_Access"
    ADMIN_MAIN_MENU = "Admin_Step_2_MainMenu"
    ADMIN_CHANNEL_MANAGEMENT = "Admin_Step_3_ChannelManagement"
    ADMIN_USER_MANAGEMENT = "Admin_Step_4_UserManagement"
    ADMIN_STATISTICS = "Admin_Step_5_Statistics"
    
    # Channel Management Steps
    CHANNEL_DISCOVERY = "Channel_Step_1_Discovery"
    CHANNEL_VERIFICATION = "Channel_Step_2_Verification"
    CHANNEL_ADDITION = "Channel_Step_3_Addition"
    CHANNEL_REMOVAL = "Channel_Step_4_Removal"
    
    # Referral Steps
    REFERRAL_LINK_GENERATION = "Referral_Step_1_GenerateLink"
    REFERRAL_REGISTRATION = "Referral_Step_2_Registration"
    REFERRAL_REWARD_DISTRIBUTION = "Referral_Step_3_RewardDistribution"
    
    # Error Steps
    ERROR_HANDLER = "Error_Handler"
    ERROR_CALLBACK_TIMEOUT = "Error_Callback_Timeout"
    ERROR_DATABASE = "Error_Database"
    ERROR_TELEGRAM_API = "Error_TelegramAPI"
    CALLBACK_TIMEOUT = "Error_Callback_Timeout"
    DATABASE_ERROR = "Error_Database"
    TELEGRAM_API_ERROR = "Error_TelegramAPI"
    CHANNEL_VERIFICATION = "Channel_Step_2_Verification"

# Convenience functions
def log_success(step_name: str, user_id: int, action: str, data: Optional[Dict] = None):
    """Log a successful step"""
    step_logger.log_step(step_name, user_id, action, data, success=True)

def log_error(step_name: str, user_id: int, error: Exception, context: Optional[Dict] = None):
    """Log an error step"""
    step_logger.log_error(step_name, user_id, error, context)

def log_info(step_name: str, user_id: int, message: str, data: Optional[Dict] = None):
    """Log informational step"""
    step_logger.log_step(step_name, user_id, message, data, success=True)

def get_user_journey(user_id: int) -> list:
    """Get complete user journey for debugging"""
    return step_logger.get_user_session(user_id)

def clear_user_journey(user_id: int):
    """Clear user journey data"""
    step_logger.clear_user_session(user_id)

def get_step_analytics() -> Dict[str, Any]:
    """Get step analytics for debugging"""
    return step_logger.get_step_statistics()

# Debug helper functions
def debug_user_flow(user_id: int):
    """Print user flow for debugging"""
    journey = get_user_journey(user_id)
    print(f"\n=== User {user_id} Journey ===")
    for step in journey:
        status = "✅" if step['success'] else "❌"
        print(f"{status} {step['step']}: {step['action']}")
        if 'data' in step and step['data']:
            print(f"   Data: {json.dumps(step['data'], indent=2)}")
    print("=" * 30)

def debug_step_statistics():
    """Print step statistics for debugging"""
    stats = get_step_analytics()
    print("\n=== Step Statistics ===")
    for step_name, data in stats.items():
        success_rate = data['success_rate']
        total = data['total']
        print(f"{step_name}: {success_rate:.1f}% success ({total} total)")
    print("=" * 30)

# Example usage functions
def example_log_usage():
    """Example of how to use the logging system"""
    user_id = 123456
    
    # Log successful step
    log_success(StepNames.CREATE_AD_START, user_id, "User started ad creation")
    
    # Log step with data
    log_info(StepNames.SELECT_DAYS, user_id, "User selected 10 days", {
        'days_selected': 10,
        'discount_applied': 12,
        'price_calculated': 88.0
    })
    
    # Log error
    try:
        # Some operation that might fail
        raise ValueError("Invalid payment amount")
    except Exception as e:
        log_error(StepNames.PAYMENT_METHOD_SELECTION, user_id, e, {
            'payment_method': 'TON',
            'amount': 'invalid'
        })
    
    # Debug user journey
    debug_user_flow(user_id)