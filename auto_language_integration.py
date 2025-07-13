#!/usr/bin/env python3
"""
Auto Language Integration
Integrates automatic language detection into existing systems
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from automatic_language_system import automatic_language_system, get_user_language_auto, localize_text_auto

logger = logging.getLogger(__name__)

class AutoLanguageIntegration:
    """Integration layer for automatic language system"""
    
    def __init__(self):
        self.integrated_systems = set()
        
    async def integrate_handlers(self):
        """Integrate automatic language into handlers"""
        try:
            # Import handlers dynamically
            import handlers
            
            # Create wrapper for message handlers
            original_handlers = {}
            
            # Store original methods
            for attr_name in dir(handlers):
                attr = getattr(handlers, attr_name)
                if callable(attr) and not attr_name.startswith('_'):
                    original_handlers[attr_name] = attr
            
            # Create auto-language wrapper
            def create_auto_language_wrapper(original_func):
                async def wrapper(*args, **kwargs):
                    # Extract user_id from message or callback
                    user_id = None
                    
                    if args:
                        if hasattr(args[0], 'from_user'):
                            user_id = args[0].from_user.id
                        elif hasattr(args[0], 'message') and hasattr(args[0].message, 'from_user'):
                            user_id = args[0].message.from_user.id
                    
                    # Get user language if available
                    if user_id:
                        language = await get_user_language_auto(user_id)
                        kwargs['auto_language'] = language
                    
                    return await original_func(*args, **kwargs)
                
                return wrapper
            
            # Apply wrappers (in memory, not modifying files)
            for name, func in original_handlers.items():
                if asyncio.iscoroutinefunction(func):
                    setattr(handlers, name, create_auto_language_wrapper(func))
            
            self.integrated_systems.add('handlers')
            logger.info("✅ Auto-language integrated into handlers")
            
        except Exception as e:
            logger.error(f"Error integrating handlers: {e}")
    
    async def integrate_admin_system(self):
        """Integrate automatic language into admin system"""
        try:
            import admin_system
            
            # Create admin language wrapper
            original_admin_class = admin_system.AdminSystem
            
            class AutoLanguageAdminSystem(original_admin_class):
                async def get_user_language(self, user_id: int) -> str:
                    """Override to use automatic language system"""
                    return await get_user_language_auto(user_id)
                
                async def send_localized_message(self, user_id: int, message_key: str, **kwargs):
                    """Send localized message"""
                    text = await localize_text_auto(user_id, message_key, **kwargs)
                    # Implementation depends on specific admin system
                    return text
            
            # Replace admin system class
            admin_system.AdminSystem = AutoLanguageAdminSystem
            
            self.integrated_systems.add('admin_system')
            logger.info("✅ Auto-language integrated into admin system")
            
        except Exception as e:
            logger.error(f"Error integrating admin system: {e}")
    
    async def integrate_payment_systems(self):
        """Integrate automatic language into payment systems"""
        try:
            # Enhanced Stars Payment System
            try:
                import enhanced_stars_payment_system
                
                original_process = enhanced_stars_payment_system.EnhancedStarsPaymentSystem.process_payment
                
                async def auto_language_process_payment(self, payment_data: Dict) -> Dict:
                    """Process payment with automatic language"""
                    user_id = payment_data.get('user_id')
                    if user_id:
                        language = await get_user_language_auto(user_id)
                        payment_data['language'] = language
                    
                    return await original_process(self, payment_data)
                
                enhanced_stars_payment_system.EnhancedStarsPaymentSystem.process_payment = auto_language_process_payment
                
            except ImportError:
                logger.warning("Enhanced Stars payment system not available")
            
            # Clean Stars Payment System
            try:
                import clean_stars_payment_system
                
                original_create_invoice = clean_stars_payment_system.CleanStarsPayment.create_invoice
                
                async def auto_language_create_invoice(self, user_id: int, *args, **kwargs):
                    """Create invoice with automatic language"""
                    language = await get_user_language_auto(user_id)
                    kwargs['language'] = language
                    
                    return await original_create_invoice(self, user_id, *args, **kwargs)
                
                clean_stars_payment_system.CleanStarsPayment.create_invoice = auto_language_create_invoice
                
            except ImportError:
                logger.warning("Clean Stars payment system not available")
            
            self.integrated_systems.add('payment_systems')
            logger.info("✅ Auto-language integrated into payment systems")
            
        except Exception as e:
            logger.error(f"Error integrating payment systems: {e}")
    
    async def integrate_campaign_systems(self):
        """Integrate automatic language into campaign systems"""
        try:
            # Enhanced Campaign Publisher
            try:
                import enhanced_campaign_publisher
                
                original_publish = enhanced_campaign_publisher.EnhancedCampaignPublisher.publish_post
                
                async def auto_language_publish_post(self, post_data: Dict) -> bool:
                    """Publish post with automatic language"""
                    user_id = post_data.get('user_id')
                    if user_id:
                        language = await get_user_language_auto(user_id)
                        post_data['language'] = language
                    
                    return await original_publish(self, post_data)
                
                enhanced_campaign_publisher.EnhancedCampaignPublisher.publish_post = auto_language_publish_post
                
            except ImportError:
                logger.warning("Enhanced campaign publisher not available")
            
            # Campaign Management
            try:
                import campaign_management
                
                # Add language detection to campaign creation
                original_create_campaign = getattr(campaign_management, 'create_campaign', None)
                
                if original_create_campaign:
                    async def auto_language_create_campaign(user_id: int, *args, **kwargs):
                        """Create campaign with automatic language"""
                        language = await get_user_language_auto(user_id)
                        kwargs['language'] = language
                        
                        return await original_create_campaign(user_id, *args, **kwargs)
                    
                    setattr(campaign_management, 'create_campaign', auto_language_create_campaign)
                
            except ImportError:
                logger.warning("Campaign management not available")
            
            self.integrated_systems.add('campaign_systems')
            logger.info("✅ Auto-language integrated into campaign systems")
            
        except Exception as e:
            logger.error(f"Error integrating campaign systems: {e}")
    
    async def integrate_channel_systems(self):
        """Integrate automatic language into channel systems"""
        try:
            # Channel Manager
            try:
                import channel_manager
                
                original_send_notification = getattr(channel_manager, 'send_notification', None)
                
                if original_send_notification:
                    async def auto_language_send_notification(user_id: int, *args, **kwargs):
                        """Send notification with automatic language"""
                        language = await get_user_language_auto(user_id)
                        kwargs['language'] = language
                        
                        return await original_send_notification(user_id, *args, **kwargs)
                    
                    setattr(channel_manager, 'send_notification', auto_language_send_notification)
                
            except ImportError:
                logger.warning("Channel manager not available")
            
            self.integrated_systems.add('channel_systems')
            logger.info("✅ Auto-language integrated into channel systems")
            
        except Exception as e:
            logger.error(f"Error integrating channel systems: {e}")
    
    async def integrate_all_systems(self):
        """Integrate automatic language into all systems"""
        try:
            logger.info("🌍 Starting automatic language integration...")
            
            await self.integrate_handlers()
            await self.integrate_admin_system()
            await self.integrate_payment_systems()
            await self.integrate_campaign_systems()
            await self.integrate_channel_systems()
            
            logger.info(f"✅ Automatic language integration complete")
            logger.info(f"   Integrated systems: {', '.join(self.integrated_systems)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in automatic language integration: {e}")
            return False
    
    def get_integration_status(self) -> Dict:
        """Get integration status"""
        return {
            'integrated_systems': list(self.integrated_systems),
            'total_systems': len(self.integrated_systems),
            'status': 'active' if self.integrated_systems else 'inactive'
        }

# Global integration instance
auto_language_integration = AutoLanguageIntegration()

async def apply_automatic_language_to_all_systems():
    """Apply automatic language detection to all systems"""
    return await auto_language_integration.integrate_all_systems()

def get_integration_status() -> Dict:
    """Get automatic language integration status"""
    return auto_language_integration.get_integration_status()