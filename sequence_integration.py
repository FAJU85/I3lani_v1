#!/usr/bin/env python3
"""
Sequence System Integration
Integrates sequence tracking with all major bot components
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from sequence_system import (
    get_sequence_system, start_user_sequence, advance_user_sequence, 
    link_to_sequence, SequenceType
)

logger = logging.getLogger(__name__)

class SequenceIntegration:
    """Main integration class for sequence system"""
    
    def __init__(self):
        self.sequence_system = get_sequence_system()
        self.active_user_sequences = {}
    
    # User Onboarding Integration
    def start_user_onboarding(self, user_id: int, username: str = None) -> str:
        """Start user onboarding sequence"""
        metadata = {
            'username': username,
            'start_time': str(datetime.now()),
            'platform': 'telegram'
        }
        
        sequence_id = start_user_sequence(
            user_id, SequenceType.USER_ONBOARDING, 
            entity_id=f"user_{user_id}", metadata=metadata
        )
        
        self.active_user_sequences[user_id] = {
            'onboarding': sequence_id
        }
        
        logger.info(f"🚀 Started user onboarding sequence: {sequence_id}")
        return sequence_id
    
    def complete_language_selection(self, user_id: int, language: str):
        """Complete language selection step"""
        sequence_id = self.get_user_sequence(user_id, 'onboarding')
        if sequence_id:
            advance_user_sequence(sequence_id, 'language_selection', {
                'language': language,
                'selection_time': str(datetime.now())
            })
            logger.info(f"✅ User {user_id} completed language selection: {language}")
    
    def complete_profile_setup(self, user_id: int, profile_data: Dict):
        """Complete profile setup step"""
        sequence_id = self.get_user_sequence(user_id, 'onboarding')
        if sequence_id:
            advance_user_sequence(sequence_id, 'profile_setup', {
                'profile_data': profile_data,
                'setup_time': str(datetime.now())
            })
            logger.info(f"✅ User {user_id} completed profile setup")
    
    # Ad Creation Integration
    def start_ad_creation(self, user_id: int, ad_type: str = "standard") -> str:
        """Start ad creation sequence"""
        metadata = {
            'ad_type': ad_type,
            'start_time': str(datetime.now()),
            'user_id': user_id
        }
        
        sequence_id = start_user_sequence(
            user_id, SequenceType.AD_CREATION,
            entity_id=f"ad_creation_{user_id}_{int(time.time())}", 
            metadata=metadata
        )
        
        if user_id not in self.active_user_sequences:
            self.active_user_sequences[user_id] = {}
        
        self.active_user_sequences[user_id]['ad_creation'] = sequence_id
        logger.info(f"🚀 Started ad creation sequence: {sequence_id}")
        return sequence_id
    
    def complete_content_upload(self, user_id: int, ad_id: int, content_type: str, 
                              content_data: Dict):
        """Complete content upload step"""
        sequence_id = self.get_user_sequence(user_id, 'ad_creation')
        if sequence_id:
            advance_user_sequence(sequence_id, 'content_upload', {
                'ad_id': ad_id,
                'content_type': content_type,
                'content_data': content_data,
                'upload_time': str(datetime.now())
            })
            
            # Link ad to sequence
            link_to_sequence(sequence_id, 'ads', 'ad', str(ad_id))
            logger.info(f"✅ User {user_id} completed content upload: ad {ad_id}")
    
    def complete_channel_selection(self, user_id: int, selected_channels: list):
        """Complete channel selection step"""
        sequence_id = self.get_user_sequence(user_id, 'ad_creation')
        if sequence_id:
            advance_user_sequence(sequence_id, 'channel_selection', {
                'selected_channels': selected_channels,
                'channel_count': len(selected_channels),
                'selection_time': str(datetime.now())
            })
            logger.info(f"✅ User {user_id} selected {len(selected_channels)} channels")
    
    def complete_pricing_calculation(self, user_id: int, pricing_data: Dict):
        """Complete pricing calculation step"""
        sequence_id = self.get_user_sequence(user_id, 'ad_creation')
        if sequence_id:
            advance_user_sequence(sequence_id, 'pricing_calculation', {
                'pricing_data': pricing_data,
                'calculation_time': str(datetime.now())
            })
            logger.info(f"✅ User {user_id} pricing calculated: ${pricing_data.get('total_price', 0)}")
    
    # Payment Processing Integration
    def start_payment_processing(self, user_id: int, payment_method: str, 
                               amount: float, memo: str = None) -> str:
        """Start payment processing sequence"""
        metadata = {
            'payment_method': payment_method,
            'amount': amount,
            'memo': memo,
            'start_time': str(datetime.now()),
            'user_id': user_id
        }
        
        sequence_id = start_user_sequence(
            user_id, SequenceType.PAYMENT_PROCESSING,
            entity_id=f"payment_{memo or f'stars_{int(time.time())}'}", 
            metadata=metadata
        )
        
        if user_id not in self.active_user_sequences:
            self.active_user_sequences[user_id] = {}
        
        self.active_user_sequences[user_id]['payment'] = sequence_id
        logger.info(f"🚀 Started payment processing sequence: {sequence_id}")
        return sequence_id
    
    def complete_payment_detection(self, user_id: int, payment_id: str, 
                                 payment_data: Dict):
        """Complete payment detection step"""
        sequence_id = self.get_user_sequence(user_id, 'payment')
        if sequence_id:
            advance_user_sequence(sequence_id, 'payment_detected', {
                'payment_id': payment_id,
                'payment_data': payment_data,
                'detection_time': str(datetime.now())
            })
            
            # Link payment to sequence
            link_to_sequence(sequence_id, 'payments', 'payment', payment_id)
            logger.info(f"✅ Payment detected for user {user_id}: {payment_id}")
    
    def complete_payment_verification(self, user_id: int, verification_result: Dict):
        """Complete payment verification step"""
        sequence_id = self.get_user_sequence(user_id, 'payment')
        if sequence_id:
            advance_user_sequence(sequence_id, 'payment_verified', {
                'verification_result': verification_result,
                'verification_time': str(datetime.now())
            })
            logger.info(f"✅ Payment verified for user {user_id}")
    
    # Campaign Management Integration
    def start_campaign_management(self, user_id: int, campaign_id: str, 
                                payment_memo: str = None) -> str:
        """Start campaign management sequence"""
        metadata = {
            'campaign_id': campaign_id,
            'payment_memo': payment_memo,
            'start_time': str(datetime.now()),
            'user_id': user_id
        }
        
        sequence_id = start_user_sequence(
            user_id, SequenceType.CAMPAIGN_MANAGEMENT,
            entity_id=campaign_id, metadata=metadata
        )
        
        if user_id not in self.active_user_sequences:
            self.active_user_sequences[user_id] = {}
        
        self.active_user_sequences[user_id]['campaign'] = sequence_id
        
        # Link campaign to sequence
        link_to_sequence(sequence_id, 'campaigns', 'campaign', campaign_id)
        logger.info(f"🚀 Started campaign management sequence: {sequence_id}")
        return sequence_id
    
    def complete_post_identity_creation(self, user_id: int, post_id: str, 
                                      campaign_id: str):
        """Complete post identity creation step"""
        sequence_id = self.get_user_sequence(user_id, 'campaign')
        if sequence_id:
            advance_user_sequence(sequence_id, 'post_identity', {
                'post_id': post_id,
                'campaign_id': campaign_id,
                'creation_time': str(datetime.now())
            })
            
            # Link post identity to sequence
            link_to_sequence(sequence_id, 'post_identity', 'post', post_id)
            logger.info(f"✅ Post identity created: {post_id} for campaign {campaign_id}")
    
    def complete_post_scheduling(self, user_id: int, scheduled_posts: int):
        """Complete post scheduling step"""
        sequence_id = self.get_user_sequence(user_id, 'campaign')
        if sequence_id:
            advance_user_sequence(sequence_id, 'schedule_posts', {
                'scheduled_posts': scheduled_posts,
                'scheduling_time': str(datetime.now())
            })
            logger.info(f"✅ Scheduled {scheduled_posts} posts for user {user_id}")
    
    # Content Publishing Integration
    def start_content_publishing(self, campaign_id: str, post_id: str, 
                               channel_id: str) -> str:
        """Start content publishing sequence"""
        metadata = {
            'campaign_id': campaign_id,
            'post_id': post_id,
            'channel_id': channel_id,
            'start_time': str(datetime.now())
        }
        
        sequence_id = start_user_sequence(
            None, SequenceType.CONTENT_PUBLISHING,
            entity_id=f"publish_{post_id}_{channel_id}", 
            metadata=metadata
        )
        
        # Link all related entities
        link_to_sequence(sequence_id, 'campaigns', 'campaign', campaign_id)
        link_to_sequence(sequence_id, 'post_identity', 'post', post_id)
        link_to_sequence(sequence_id, 'channels', 'channel', channel_id)
        
        logger.info(f"🚀 Started content publishing sequence: {sequence_id}")
        return sequence_id
    
    def complete_content_publishing(self, sequence_id: str, message_id: str, 
                                  channel_id: str):
        """Complete content publishing step"""
        advance_user_sequence(sequence_id, 'publish_complete', {
            'message_id': message_id,
            'channel_id': channel_id,
            'publish_time': str(datetime.now())
        })
        
        # Link published message to sequence
        link_to_sequence(sequence_id, 'published_messages', 'message', message_id)
        logger.info(f"✅ Content published: message {message_id} in {channel_id}")
    
    # Admin Action Integration
    def start_admin_action(self, admin_id: int, action_type: str, 
                          target_entity: str = None) -> str:
        """Start admin action sequence"""
        metadata = {
            'admin_id': admin_id,
            'action_type': action_type,
            'target_entity': target_entity,
            'start_time': str(datetime.now())
        }
        
        sequence_id = start_user_sequence(
            admin_id, SequenceType.ADMIN_ACTION,
            entity_id=f"admin_{action_type}_{int(time.time())}", 
            metadata=metadata
        )
        
        logger.info(f"🚀 Started admin action sequence: {sequence_id}")
        return sequence_id
    
    def complete_admin_action(self, sequence_id: str, action_result: Dict):
        """Complete admin action step"""
        advance_user_sequence(sequence_id, 'admin_complete', {
            'action_result': action_result,
            'completion_time': str(datetime.now())
        })
        logger.info(f"✅ Admin action completed: {sequence_id}")
    
    # Utility Methods
    def get_user_sequence(self, user_id: int, sequence_type: str) -> Optional[str]:
        """Get active sequence ID for user by type"""
        if user_id in self.active_user_sequences:
            return self.active_user_sequences[user_id].get(sequence_type)
        return None
    
    def get_user_progress(self, user_id: int) -> Dict:
        """Get all active sequence progress for user"""
        sequences = self.sequence_system.get_active_sequences(user_id)
        
        progress = {}
        for seq in sequences:
            progress[seq['type']] = {
                'sequence_id': seq['sequence_id'],
                'progress': seq['progress_percentage'],
                'current_step': seq['current_step'],
                'last_updated': seq['updated_at']
            }
        
        return progress
    
    def get_system_overview(self) -> Dict:
        """Get comprehensive system overview"""
        health = self.sequence_system.get_system_health()
        active_sequences = self.sequence_system.get_active_sequences()
        
        return {
            'system_health': health,
            'active_sequences': len(active_sequences),
            'sequences_by_type': {},
            'component_status': health.get('component_health', {}),
            'recent_activity': active_sequences[:10]  # Last 10 active sequences
        }
    
    def find_related_sequences(self, component_name: str, entity_id: str) -> List[Dict]:
        """Find all sequences related to a component entity"""
        sequence_ids = self.sequence_system.find_sequences_by_component(component_name, entity_id)
        
        related_sequences = []
        for seq_id in sequence_ids:
            status = self.sequence_system.get_sequence_status(seq_id)
            if status:
                related_sequences.append(status)
        
        return related_sequences
    
    def diagnose_stuck_sequences(self) -> List[Dict]:
        """Diagnose sequences that might be stuck"""
        active_sequences = self.sequence_system.get_active_sequences()
        stuck_sequences = []
        
        for seq in active_sequences:
            # Check if sequence hasn't been updated in over 1 hour
            last_updated = datetime.fromisoformat(seq['updated_at'])
            if (datetime.now() - last_updated).total_seconds() > 3600:
                stuck_sequences.append({
                    'sequence_id': seq['sequence_id'],
                    'type': seq['type'],
                    'user_id': seq['user_id'],
                    'stuck_duration': (datetime.now() - last_updated).total_seconds(),
                    'last_step': seq['current_step'],
                    'progress': seq['progress_percentage']
                })
        
        return stuck_sequences

# Global integration instance
sequence_integration = None

def get_sequence_integration() -> SequenceIntegration:
    """Get global sequence integration instance"""
    global sequence_integration
    if sequence_integration is None:
        sequence_integration = SequenceIntegration()
    return sequence_integration

# Helper functions for easy integration
def track_user_start(user_id: int, username: str = None) -> str:
    """Track user start event"""
    return get_sequence_integration().start_user_onboarding(user_id, username)

def track_ad_creation(user_id: int, ad_type: str = "standard") -> str:
    """Track ad creation start"""
    return get_sequence_integration().start_ad_creation(user_id, ad_type)

def track_payment_start(user_id: int, payment_method: str, amount: float, memo: str = None) -> str:
    """Track payment processing start"""
    return get_sequence_integration().start_payment_processing(user_id, payment_method, amount, memo)

def track_campaign_creation(user_id: int, campaign_id: str, payment_memo: str = None) -> str:
    """Track campaign creation"""
    return get_sequence_integration().start_campaign_management(user_id, campaign_id, payment_memo)

def track_content_publish(campaign_id: str, post_id: str, channel_id: str) -> str:
    """Track content publishing"""
    return get_sequence_integration().start_content_publishing(campaign_id, post_id, channel_id)