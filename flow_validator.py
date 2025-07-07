"""
Flow Validator for I3lani Bot
Ensures dynamic, logical, and intelligent user flow
"""
import asyncio
from database import db
from config import ADMIN_IDS
import logging

logger = logging.getLogger(__name__)

class FlowValidator:
    """Validates and ensures intelligent flow behavior"""
    
    @staticmethod
    async def validate_package_selection(user_id: int, package_id: str) -> dict:
        """Validate package availability and user eligibility"""
        result = {'valid': False, 'reason': '', 'suggested_action': ''}
        
        try:
            # Check if package exists
            packages = await db.get_packages(active_only=True)
            package = next((p for p in packages if p['package_id'] == package_id), None)
            
            if not package:
                result['reason'] = 'Package not available'
                result['suggested_action'] = 'show_available_packages'
                return result
            
            # Check free ads limit for free package
            if package_id == 'free':
                user = await db.get_user(user_id)
                free_ads_used = user.get('free_ads_used', 0) if user else 0
                
                if free_ads_used >= 3:
                    result['reason'] = 'Free ads limit exceeded'
                    result['suggested_action'] = 'show_paid_packages'
                    return result
            
            result['valid'] = True
            return result
            
        except Exception as e:
            logger.error(f"Package validation error: {e}")
            result['reason'] = 'Validation error'
            result['suggested_action'] = 'error_recovery'
            return result
    
    @staticmethod
    async def validate_channel_selection(selected_channels: list) -> dict:
        """Validate channel selection before payment"""
        result = {'valid': False, 'reason': '', 'available_channels': []}
        
        try:
            # Get available channels
            channels = await db.get_channels(active_only=True)
            
            if not channels:
                result['reason'] = 'No channels available'
                result['suggested_action'] = 'contact_admin'
                return result
            
            # Check if selected channels are valid
            valid_channel_ids = [ch['channel_id'] for ch in channels]
            invalid_channels = [ch for ch in selected_channels if ch not in valid_channel_ids]
            
            if invalid_channels:
                result['reason'] = f'Invalid channels: {invalid_channels}'
                result['suggested_action'] = 'reselect_channels'
                return result
            
            if not selected_channels:
                result['reason'] = 'No channels selected'
                result['suggested_action'] = 'select_channels'
                return result
            
            result['valid'] = True
            result['available_channels'] = channels
            return result
            
        except Exception as e:
            logger.error(f"Channel validation error: {e}")
            result['reason'] = 'Validation error'
            result['suggested_action'] = 'error_recovery'
            return result
    
    @staticmethod
    async def validate_user_state(user_id: int, required_data: list) -> dict:
        """Validate user has required data for current flow step"""
        result = {'valid': False, 'missing_data': [], 'completed_steps': []}
        
        try:
            user = await db.get_user(user_id)
            if not user:
                result['missing_data'] = ['user_registration']
                result['suggested_action'] = 'register_user'
                return result
            
            # Check required data fields
            missing = []
            for field in required_data:
                if not user.get(field):
                    missing.append(field)
            
            result['missing_data'] = missing
            result['valid'] = len(missing) == 0
            
            # Determine completed steps
            completed = []
            if user.get('language'):
                completed.append('language_selection')
            if user.get('username'):
                completed.append('profile_setup')
            
            result['completed_steps'] = completed
            return result
            
        except Exception as e:
            logger.error(f"User state validation error: {e}")
            result['suggested_action'] = 'error_recovery'
            return result
    
    @staticmethod
    async def get_intelligent_next_step(user_id: int, current_state: str, data: dict) -> dict:
        """Intelligently determine next step based on current state and data"""
        next_step = {'state': '', 'action': '', 'message': '', 'skip_steps': []}
        
        try:
            # Package-based logic
            package = data.get('package', 'free')
            
            if package == 'free':
                # Free package - can skip channel selection and payment
                if current_state == 'confirm_ad':
                    next_step['state'] = 'publish_ad'
                    next_step['action'] = 'publish_free_ad'
                    next_step['message'] = 'Free ad will be published immediately'
                    next_step['skip_steps'] = ['channel_selection', 'payment']
                    return next_step
            
            # Paid package logic
            if current_state == 'confirm_ad':
                # Check if channels exist
                channels = await db.get_channels(active_only=True)
                if not channels:
                    next_step['state'] = 'error_state'
                    next_step['action'] = 'no_channels_available'
                    next_step['message'] = 'No advertising channels available. Contact admin.'
                    return next_step
                
                next_step['state'] = 'channel_selection'
                next_step['action'] = 'show_channel_selection'
                next_step['message'] = 'Select channels for your ad'
                return next_step
            
            if current_state == 'channel_selection':
                selected_channels = data.get('selected_channels', [])
                if selected_channels:
                    next_step['state'] = 'payment_method'
                    next_step['action'] = 'show_payment_options'
                    next_step['message'] = 'Choose payment method'
                    return next_step
            
            # Default progression
            state_progression = {
                'select_category': 'select_subcategory',
                'select_subcategory': 'select_location',
                'select_location': 'enter_ad_details',
                'enter_ad_details': 'upload_photos',
                'upload_photos': 'provide_contact_info',
                'provide_contact_info': 'preview_ad',
                'preview_ad': 'confirm_ad'
            }
            
            next_state = state_progression.get(current_state, 'main_menu')
            next_step['state'] = next_state
            next_step['action'] = f'show_{next_state}'
            next_step['message'] = f'Proceeding to {next_state.replace("_", " ")}'
            
            return next_step
            
        except Exception as e:
            logger.error(f"Next step determination error: {e}")
            next_step['state'] = 'error_state'
            next_step['action'] = 'error_recovery'
            next_step['message'] = 'Error determining next step'
            return next_step
    
    @staticmethod
    async def validate_admin_access(user_id: int) -> bool:
        """Validate admin access"""
        try:
            return str(user_id) in ADMIN_IDS
        except Exception:
            return False
    
    @staticmethod
    async def get_flow_recommendations(user_id: int, current_data: dict) -> list:
        """Get intelligent flow recommendations"""
        recommendations = []
        
        try:
            # Check completion percentage
            required_fields = ['package', 'category', 'subcategory', 'location', 'ad_details', 'contact_info']
            completed_fields = [field for field in required_fields if current_data.get(field)]
            completion_percentage = (len(completed_fields) / len(required_fields)) * 100
            
            if completion_percentage < 50:
                recommendations.append({
                    'type': 'suggestion',
                    'message': 'Complete your ad details for better results',
                    'action': 'continue_ad_creation'
                })
            
            # Package-specific recommendations
            package = current_data.get('package', 'free')
            if package == 'free':
                recommendations.append({
                    'type': 'upsell',
                    'message': 'Upgrade to paid package for more channels and longer duration',
                    'action': 'show_paid_packages'
                })
            
            # Photo recommendations
            photos = current_data.get('uploaded_photos', [])
            if len(photos) == 0:
                recommendations.append({
                    'type': 'enhancement',
                    'message': 'Add photos to increase ad effectiveness',
                    'action': 'add_photos'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Flow recommendations error: {e}")
            return []

# Global flow validator instance
flow_validator = FlowValidator()

async def validate_flow_transition(user_id: int, from_state: str, to_state: str, data: dict) -> dict:
    """Validate flow transition between states"""
    validation = {'allowed': True, 'reason': '', 'required_action': ''}
    
    try:
        # Validate required data for target state
        state_requirements = {
            'channel_selection': ['package', 'ad_details'],
            'payment_method': ['package', 'selected_channels'],
            'payment_confirmation': ['package', 'selected_channels', 'payment_method']
        }
        
        required = state_requirements.get(to_state, [])
        missing = [field for field in required if not data.get(field)]
        
        if missing:
            validation['allowed'] = False
            validation['reason'] = f'Missing required data: {missing}'
            validation['required_action'] = f'complete_{missing[0]}'
        
        return validation
        
    except Exception as e:
        logger.error(f"Flow transition validation error: {e}")
        validation['allowed'] = False
        validation['reason'] = 'Validation error'
        validation['required_action'] = 'error_recovery'
        return validation