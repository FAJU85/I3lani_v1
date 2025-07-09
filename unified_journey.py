#!/usr/bin/env python3
"""
Unified User Journey Engine for I3lani Bot
Provides consistent step-by-step flow across all languages
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from languages import get_text
from logger import log_info, log_error, StepNames

class JourneyStep(Enum):
    """Unified journey steps that work across all languages"""
    # Initial flow
    START = "start"
    LANGUAGE_SELECTION = "language_selection"
    MAIN_MENU = "main_menu"
    
    # Ad creation unified flow
    AD_CREATION_START = "ad_creation_start"
    AD_UPLOAD_PHOTOS = "ad_upload_photos"
    AD_UPLOAD_TEXT = "ad_upload_text"
    AD_CHANNEL_SELECTION = "ad_channel_selection"
    AD_DURATION_SELECTION = "ad_duration_selection"
    AD_POSTS_SELECTION = "ad_posts_selection"
    AD_PAYMENT_SUMMARY = "ad_payment_summary"
    AD_PAYMENT_METHOD = "ad_payment_method"
    AD_PAYMENT_PROCESS = "ad_payment_process"
    AD_CONFIRMATION = "ad_confirmation"
    
    # Settings flow
    SETTINGS_MENU = "settings_menu"
    LANGUAGE_CHANGE = "language_change"
    
    # Help flow
    HELP_DISPLAY = "help_display"
    
    # Partner flow
    PARTNER_MENU = "partner_menu"
    PARTNER_EARNINGS = "partner_earnings"
    
    # Admin flow
    ADMIN_PANEL = "admin_panel"

@dataclass
class StepData:
    """Data structure for each step"""
    step: JourneyStep
    language: str
    user_id: int
    data: Dict[str, Any] = None
    
    def get_text_key(self, key: str) -> str:
        """Get translated text for this step"""
        return get_text(self.language, key)

class UnifiedJourneyEngine:
    """
    Unified Journey Engine that ensures consistent user flow across all languages
    """
    
    def __init__(self):
        self.step_definitions = self._define_steps()
        
    def _define_steps(self) -> Dict[JourneyStep, Dict[str, Any]]:
        """Define unified step structure for all languages"""
        return {
            JourneyStep.START: {
                'title_key': 'welcome',
                'description_key': 'welcome_description',
                'buttons': [
                    {'text_key': 'choose_language', 'action': 'language_selection'}
                ],
                'next_step': JourneyStep.LANGUAGE_SELECTION
            },
            
            JourneyStep.LANGUAGE_SELECTION: {
                'title_key': 'choose_language',
                'description_key': 'language_prompt',
                'buttons': [
                    {'text_key': 'lang_english', 'action': 'lang_en'},
                    {'text_key': 'lang_arabic', 'action': 'lang_ar'},
                    {'text_key': 'lang_russian', 'action': 'lang_ru'}
                ],
                'next_step': JourneyStep.MAIN_MENU
            },
            
            JourneyStep.MAIN_MENU: {
                'title_key': 'main_menu',
                'description_key': 'main_menu_description',
                'buttons': [
                    {'text_key': 'create_ad', 'action': 'create_ad'},
                    {'text_key': 'my_ads', 'action': 'my_ads'},
                    {'text_key': 'share_earn', 'action': 'share_earn'},
                    {'text_key': 'channel_partners', 'action': 'channel_partners'},
                    {'text_key': 'settings', 'action': 'settings'},
                    {'text_key': 'help', 'action': 'help'}
                ],
                'conditional_buttons': [
                    {'text_key': 'gaming_hub', 'action': 'gaming_hub', 'condition': 'gamification_enabled'},
                    {'text_key': 'leaderboard', 'action': 'leaderboard', 'condition': 'gamification_enabled'}
                ]
            },
            
            JourneyStep.AD_CREATION_START: {
                'title_key': 'create_ad_header',
                'description_key': 'create_ad_step1_description',
                'buttons': [
                    {'text_key': 'upload_photos', 'action': 'upload_photos'},
                    {'text_key': 'skip_photos', 'action': 'skip_photos'},
                    {'text_key': 'back_to_main', 'action': 'back_to_main'}
                ],
                'next_step': JourneyStep.AD_UPLOAD_PHOTOS
            },
            
            JourneyStep.AD_UPLOAD_PHOTOS: {
                'title_key': 'create_ad_step1_title',
                'description_key': 'create_ad_photo_instructions',
                'buttons': [
                    {'text_key': 'skip_photos', 'action': 'skip_photos_to_text'},
                    {'text_key': 'back_to_main', 'action': 'back_to_main'}
                ],
                'next_step': JourneyStep.AD_UPLOAD_TEXT,
                'skip_to': JourneyStep.AD_UPLOAD_TEXT
            },
            
            JourneyStep.AD_UPLOAD_TEXT: {
                'title_key': 'create_ad_step2_title',
                'description_key': 'create_ad_text_instructions',
                'buttons': [
                    {'text_key': 'continue_to_channels', 'action': 'continue_to_channels'},
                    {'text_key': 'back_to_photos', 'action': 'back_to_photos'}
                ],
                'next_step': JourneyStep.AD_CHANNEL_SELECTION
            },
            
            JourneyStep.AD_CHANNEL_SELECTION: {
                'title_key': 'create_ad_step3_title',
                'description_key': 'select_channels_description',
                'buttons': [
                    {'text_key': 'continue_to_duration', 'action': 'continue_to_duration'},
                    {'text_key': 'back_to_text', 'action': 'back_to_text'}
                ],
                'next_step': JourneyStep.AD_DURATION_SELECTION,
                'dynamic_buttons': 'channel_list'
            },
            
            JourneyStep.AD_DURATION_SELECTION: {
                'title_key': 'create_ad_step4_title',
                'description_key': 'select_duration_description',
                'buttons': [
                    {'text_key': 'continue_to_posts', 'action': 'continue_to_posts'},
                    {'text_key': 'back_to_channels', 'action': 'back_to_channels'}
                ],
                'next_step': JourneyStep.AD_POSTS_SELECTION,
                'dynamic_buttons': 'duration_selector'
            },
            
            JourneyStep.AD_POSTS_SELECTION: {
                'title_key': 'create_ad_step5_title',
                'description_key': 'select_posts_description',
                'buttons': [
                    {'text_key': 'continue_to_payment', 'action': 'continue_to_payment'},
                    {'text_key': 'back_to_duration', 'action': 'back_to_duration'}
                ],
                'next_step': JourneyStep.AD_PAYMENT_SUMMARY,
                'dynamic_buttons': 'posts_selector'
            },
            
            JourneyStep.AD_PAYMENT_SUMMARY: {
                'title_key': 'payment_summary_title',
                'description_key': 'payment_summary_description',
                'buttons': [
                    {'text_key': 'choose_payment_method', 'action': 'choose_payment_method'},
                    {'text_key': 'back_to_posts', 'action': 'back_to_posts'}
                ],
                'next_step': JourneyStep.AD_PAYMENT_METHOD
            },
            
            JourneyStep.AD_PAYMENT_METHOD: {
                'title_key': 'payment_method_title',
                'description_key': 'payment_method_description',
                'buttons': [
                    {'text_key': 'pay_ton', 'action': 'pay_ton'},
                    {'text_key': 'pay_stars', 'action': 'pay_stars'},
                    {'text_key': 'back_to_summary', 'action': 'back_to_summary'}
                ],
                'next_step': JourneyStep.AD_PAYMENT_PROCESS
            },
            
            JourneyStep.SETTINGS_MENU: {
                'title_key': 'settings_title',
                'description_key': 'settings_description',
                'buttons': [
                    {'text_key': 'lang_english', 'action': 'lang_en'},
                    {'text_key': 'lang_arabic', 'action': 'lang_ar'},
                    {'text_key': 'lang_russian', 'action': 'lang_ru'},
                    {'text_key': 'back_to_main', 'action': 'back_to_main'}
                ],
                'next_step': JourneyStep.MAIN_MENU
            },
            
            JourneyStep.HELP_DISPLAY: {
                'title_key': 'help_title',
                'description_key': 'help_text',
                'buttons': [
                    {'text_key': 'back_to_main', 'action': 'back_to_main'}
                ],
                'next_step': JourneyStep.MAIN_MENU
            }
        }
    
    def get_step_content(self, step: JourneyStep, language: str, user_id: int, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get unified step content for any language"""
        if step not in self.step_definitions:
            log_error(StepNames.ERROR_HANDLER, user_id, 
                     Exception(f"Step {step} not defined"), 
                     {"step": step.value, "language": language})
            return self._get_error_step(language, user_id)
        
        step_def = self.step_definitions[step]
        step_data = StepData(step=step, language=language, user_id=user_id, data=data)
        
        # Build content
        content = {
            'title': step_data.get_text_key(step_def['title_key']),
            'description': step_data.get_text_key(step_def['description_key']),
            'buttons': self._build_buttons(step_def, step_data),
            'next_step': step_def.get('next_step'),
            'skip_to': step_def.get('skip_to')
        }
        
        # Add dynamic content if specified
        if 'dynamic_buttons' in step_def:
            content['dynamic_buttons'] = step_def['dynamic_buttons']
        
        # Step content generated successfully
        return content
    
    def _build_buttons(self, step_def: Dict[str, Any], step_data: StepData) -> List[Dict[str, str]]:
        """Build button list with proper translations"""
        buttons = []
        
        # Regular buttons
        for button_def in step_def.get('buttons', []):
            buttons.append({
                'text': step_data.get_text_key(button_def['text_key']),
                'action': button_def['action']
            })
        
        # Conditional buttons
        for button_def in step_def.get('conditional_buttons', []):
            if self._check_condition(button_def.get('condition'), step_data):
                buttons.append({
                    'text': step_data.get_text_key(button_def['text_key']),
                    'action': button_def['action']
                })
        
        return buttons
    
    def _check_condition(self, condition: str, step_data: StepData) -> bool:
        """Check if conditional button should be shown"""
        if condition == 'gamification_enabled':
            return True  # For now, always show gamification
        return False
    
    def _get_error_step(self, language: str, user_id: int) -> Dict[str, Any]:
        """Get error step content"""
        return {
            'title': get_text(language, 'error'),
            'description': get_text(language, 'error_processing_request'),
            'buttons': [
                {
                    'text': get_text(language, 'back_to_main'),
                    'action': 'back_to_main'
                }
            ],
            'next_step': JourneyStep.MAIN_MENU
        }
    
    def get_next_step(self, current_step: JourneyStep, action: str) -> Optional[JourneyStep]:
        """Get next step based on current step and action"""
        step_mappings = {
            # From any step
            'back_to_main': JourneyStep.MAIN_MENU,
            'language_selection': JourneyStep.LANGUAGE_SELECTION,
            
            # From main menu
            'create_ad': JourneyStep.AD_CREATION_START,
            'settings': JourneyStep.SETTINGS_MENU,
            'help': JourneyStep.HELP_DISPLAY,
            
            # Ad creation flow
            'upload_photos': JourneyStep.AD_UPLOAD_PHOTOS,
            'skip_photos': JourneyStep.AD_UPLOAD_TEXT,
            'skip_photos_to_text': JourneyStep.AD_UPLOAD_TEXT,
            'continue_to_channels': JourneyStep.AD_CHANNEL_SELECTION,
            'continue_to_duration': JourneyStep.AD_DURATION_SELECTION,
            'continue_to_posts': JourneyStep.AD_POSTS_SELECTION,
            'continue_to_payment': JourneyStep.AD_PAYMENT_SUMMARY,
            'choose_payment_method': JourneyStep.AD_PAYMENT_METHOD,
            
            # Back navigation
            'back_to_photos': JourneyStep.AD_UPLOAD_PHOTOS,
            'back_to_text': JourneyStep.AD_UPLOAD_TEXT,
            'back_to_channels': JourneyStep.AD_CHANNEL_SELECTION,
            'back_to_duration': JourneyStep.AD_DURATION_SELECTION,
            'back_to_posts': JourneyStep.AD_POSTS_SELECTION,
            'back_to_summary': JourneyStep.AD_PAYMENT_SUMMARY,
            
            # Language changes
            'lang_en': JourneyStep.MAIN_MENU,
            'lang_ar': JourneyStep.MAIN_MENU,
            'lang_ru': JourneyStep.MAIN_MENU,
        }
        
        return step_mappings.get(action)
    
    def validate_journey_consistency(self) -> Dict[str, Any]:
        """Validate that all steps are properly connected"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check that all steps have required fields
        required_fields = ['title_key', 'description_key', 'buttons']
        
        for step, step_def in self.step_definitions.items():
            for field in required_fields:
                if field not in step_def:
                    validation_result['errors'].append(f"Step {step.value} missing {field}")
                    validation_result['valid'] = False
        
        # Check that all button actions have corresponding handlers
        all_actions = set()
        for step_def in self.step_definitions.values():
            for button in step_def.get('buttons', []):
                all_actions.add(button['action'])
            for button in step_def.get('conditional_buttons', []):
                all_actions.add(button['action'])
        
        # Log validation results
        if validation_result['valid']:
            print("✅ Journey consistency validation passed!")
        else:
            print("❌ Journey consistency validation failed!")
            for error in validation_result['errors']:
                print(f"  - {error}")
        
        return validation_result

# Global instance
journey_engine = UnifiedJourneyEngine()

def get_unified_step(step: JourneyStep, language: str, user_id: int, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get unified step content - main interface function"""
    return journey_engine.get_step_content(step, language, user_id, data)

def get_next_journey_step(current_step: JourneyStep, action: str) -> Optional[JourneyStep]:
    """Get next step in journey"""
    return journey_engine.get_next_step(current_step, action)

def validate_journey() -> Dict[str, Any]:
    """Validate journey consistency"""
    return journey_engine.validate_journey_consistency()