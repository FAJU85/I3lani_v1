#!/usr/bin/env python3
"""
Integration of Animated Transitions into Existing Bot Handlers
Updates handlers to use smooth animated transitions between stages
"""

import logging
from typing import Dict, List
from animated_transitions import get_animated_transitions, animate_to_stage, smooth_callback_transition
from sequence_logger import get_sequence_logger

logger = get_sequence_logger(__name__)

class TransitionIntegration:
    """Integrates animated transitions into existing bot handlers"""
    
    def __init__(self):
        self.transitions = get_animated_transitions()
        
        # Map handler functions to their stage transitions
        self.handler_transitions = {
            # Main navigation transitions
            "show_main_menu": {
                "to_stage": "main_menu",
                "from_stages": ["language_selection", "settings", "help"]
            },
            "create_ad_handler": {
                "to_stage": "create_ad_start", 
                "from_stages": ["main_menu"]
            },
            "show_settings_handler": {
                "to_stage": "settings",
                "from_stages": ["main_menu"]
            },
            "show_help_handler": {
                "to_stage": "help",
                "from_stages": ["main_menu", "settings"]
            },
            
            # Ad creation flow transitions
            "upload_content_handler": {
                "to_stage": "enter_text",
                "from_stages": ["create_ad_start", "upload_image"]
            },
            "handle_photo_upload": {
                "to_stage": "upload_image",
                "from_stages": ["create_ad_start"]
            },
            "show_channel_selection": {
                "to_stage": "select_channels",
                "from_stages": ["enter_text", "upload_image"]
            },
            "show_dynamic_days_selector": {
                "to_stage": "select_days",
                "from_stages": ["select_channels"]
            },
            "show_posts_per_day_selection": {
                "to_stage": "posts_per_day",
                "from_stages": ["select_days"]
            },
            "show_frequency_payment_summary": {
                "to_stage": "confirm_campaign",
                "from_stages": ["posts_per_day"]
            },
            
            # Payment flow transitions
            "show_payment_methods": {
                "to_stage": "choose_payment",
                "from_stages": ["confirm_campaign"]
            },
            "process_ton_payment": {
                "to_stage": "payment_ton",
                "from_stages": ["choose_payment"]
            },
            "process_stars_payment": {
                "to_stage": "payment_stars", 
                "from_stages": ["choose_payment"]
            },
            "payment_confirmation": {
                "to_stage": "payment_success",
                "from_stages": ["payment_ton", "payment_stars"]
            },
            
            # Campaign management transitions
            "show_user_campaigns": {
                "to_stage": "my_campaigns",
                "from_stages": ["main_menu", "payment_success"]
            },
            "show_campaign_details": {
                "to_stage": "campaign_details",
                "from_stages": ["my_campaigns"]
            },
            
            # Admin transitions
            "admin_main_menu": {
                "to_stage": "admin_panel",
                "from_stages": ["main_menu"]
            },
            "admin_channels": {
                "to_stage": "channel_management",
                "from_stages": ["admin_panel"]
            },
            "admin_users": {
                "to_stage": "user_management",
                "from_stages": ["admin_panel"]
            }
        }
        
        # Special transition effects for specific flows
        self.special_effects = {
            "payment_processing": {
                "animation": "payment_processing",
                "duration": 3.0,
                "show_progress": True
            },
            "ad_publishing": {
                "animation": "publishing",
                "duration": 2.5, 
                "show_progress": True
            },
            "channel_loading": {
                "animation": "loading_wave",
                "duration": 2.0,
                "show_progress": False
            }
        }
    
    def get_transition_config(self, handler_name: str, from_context: str = None) -> Dict:
        """Get transition configuration for a handler"""
        config = self.handler_transitions.get(handler_name, {})
        
        # Add contextual from_stage if provided
        if from_context and from_context in config.get("from_stages", []):
            config["from_stage"] = from_context
        
        return config
    
    async def apply_transition_to_handler(self, 
                                        handler_name: str,
                                        message_or_query,
                                        content: str,
                                        language: str = "en",
                                        user_id: int = None,
                                        keyboard = None,
                                        from_context: str = None) -> bool:
        """Apply animated transition to a handler"""
        try:
            config = self.get_transition_config(handler_name, from_context)
            
            if not config:
                logger.warning(f"⚠️ No transition config for handler: {handler_name}")
                return False
            
            to_stage = config["to_stage"]
            from_stage = config.get("from_stage")
            
            # Apply the animated transition
            success = await animate_to_stage(
                message_or_query=message_or_query,
                to_stage=to_stage,
                content=content,
                language=language,
                user_id=user_id,
                keyboard=keyboard,
                from_stage=from_stage
            )
            
            if success:
                logger.info(f"✅ Applied transition for {handler_name}: {from_stage} → {to_stage}")
            else:
                logger.error(f"❌ Failed to apply transition for {handler_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error applying transition to {handler_name}: {e}")
            return False
    
    async def apply_callback_transition(self,
                                      callback_query,
                                      content: str,
                                      keyboard = None,
                                      language: str = "en",
                                      handler_name: str = None,
                                      from_context: str = None) -> bool:
        """Apply smooth transition for callback queries"""
        try:
            stage_key = None
            
            if handler_name:
                config = self.get_transition_config(handler_name, from_context)
                stage_key = config.get("to_stage")
            
            success = await smooth_callback_transition(
                callback_query=callback_query,
                new_content=content,
                keyboard=keyboard,
                language=language,
                stage_key=stage_key
            )
            
            if success:
                logger.info(f"✅ Applied callback transition for {handler_name or 'unknown'}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error applying callback transition: {e}")
            return False
    
    async def apply_special_effect(self,
                                 effect_name: str,
                                 message_or_query,
                                 operation_text: str,
                                 language: str = "en") -> bool:
        """Apply special transition effects"""
        try:
            effect_config = self.special_effects.get(effect_name)
            
            if not effect_config:
                logger.warning(f"⚠️ Unknown special effect: {effect_name}")
                return False
            
            if effect_config.get("show_progress"):
                # Use progress bar animation
                from animated_transitions import get_animated_transitions
                transitions = get_animated_transitions()
                
                if hasattr(message_or_query, 'message'):
                    message = message_or_query.message
                else:
                    message = message_or_query
                
                success = await transitions.progress_bar_animation(
                    message=message,
                    operation=operation_text,
                    steps=5,
                    language=language
                )
            else:
                # Use loading animation
                from animated_transitions import animate_loading
                success = await animate_loading(
                    message_or_query=message_or_query,
                    operation=operation_text,
                    language=language,
                    animation_type=effect_config["animation"]
                )
            
            if success:
                logger.info(f"✅ Applied special effect: {effect_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error applying special effect {effect_name}: {e}")
            return False
    
    def create_integration_wrappers(self) -> Dict[str, str]:
        """Create wrapper functions for handler integration"""
        wrappers = {}
        
        for handler_name, config in self.handler_transitions.items():
            wrapper_code = f'''
async def {handler_name}_with_transition(message_or_query, content, language="en", user_id=None, keyboard=None, from_context=None):
    """Enhanced {handler_name} with animated transitions"""
    from transition_integration import TransitionIntegration
    
    integration = TransitionIntegration()
    
    # Apply transition animation
    success = await integration.apply_transition_to_handler(
        handler_name="{handler_name}",
        message_or_query=message_or_query,
        content=content,
        language=language,
        user_id=user_id,
        keyboard=keyboard,
        from_context=from_context
    )
    
    return success
'''
            wrappers[handler_name] = wrapper_code
        
        return wrappers
    
    def generate_integration_guide(self) -> Dict[str, any]:
        """Generate integration guide for developers"""
        guide = {
            "overview": "Animated Transitions Integration Guide",
            "total_handlers": len(self.handler_transitions),
            "special_effects": len(self.special_effects),
            "integration_steps": [
                "1. Import transition_integration module",
                "2. Create TransitionIntegration instance", 
                "3. Replace direct message sends with transition calls",
                "4. Add from_context parameter to track stage flow",
                "5. Use special effects for loading operations"
            ],
            "example_usage": {
                "basic_transition": '''
from transition_integration import TransitionIntegration

integration = TransitionIntegration()

# In your handler
await integration.apply_transition_to_handler(
    handler_name="show_main_menu",
    message_or_query=callback_query,
    content=menu_text,
    language=user_language,
    user_id=user_id,
    keyboard=menu_keyboard,
    from_context="settings"
)
''',
                "callback_transition": '''
# For callback queries
await integration.apply_callback_transition(
    callback_query=callback_query,
    content=new_content,
    keyboard=new_keyboard,
    language=language,
    handler_name="create_ad_handler"
)
''',
                "special_effect": '''
# For special operations
await integration.apply_special_effect(
    effect_name="payment_processing",
    message_or_query=message,
    operation_text="Processing payment...",
    language=language
)
'''
            },
            "transition_map": self.handler_transitions,
            "benefits": [
                "Enhanced user experience with smooth transitions",
                "Visual feedback for all stage changes",
                "Consistent animation styling across the bot",
                "Improved perceived performance",
                "Better user engagement and retention"
            ]
        }
        
        return guide

def create_transition_integration() -> TransitionIntegration:
    """Create transition integration instance"""
    return TransitionIntegration()

def validate_transition_integration() -> bool:
    """Validate the transition integration system"""
    try:
        print("🎬 TRANSITION INTEGRATION VALIDATION")
        print("=" * 50)
        
        integration = TransitionIntegration()
        
        print(f"✅ Transition Integration Initialized")
        print(f"📊 Mapped Handlers: {len(integration.handler_transitions)}")
        print(f"🎭 Special Effects: {len(integration.special_effects)}")
        
        # Test configuration retrieval
        test_handlers = ["show_main_menu", "create_ad_handler", "show_settings_handler"]
        
        print(f"\n🔍 Testing Handler Configurations:")
        for handler in test_handlers:
            config = integration.get_transition_config(handler)
            if config:
                print(f"  ✅ {handler}: {config.get('to_stage', 'N/A')}")
            else:
                print(f"  ❌ {handler}: No configuration")
        
        # Test special effects
        print(f"\n🎭 Available Special Effects:")
        for effect_name, config in integration.special_effects.items():
            print(f"  🎬 {effect_name}: {config['animation']} ({config['duration']}s)")
        
        # Generate integration guide
        guide = integration.generate_integration_guide()
        print(f"\n📘 Integration Guide Generated:")
        print(f"  📊 Total Components: {guide['total_handlers']} handlers, {guide['special_effects']} effects")
        print(f"  📋 Integration Steps: {len(guide['integration_steps'])} steps")
        
        print(f"\n✅ TRANSITION INTEGRATION SYSTEM READY")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = validate_transition_integration()
    exit(0 if success else 1)