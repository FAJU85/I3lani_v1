#!/usr/bin/env python3
"""
Handlers Integration with Global Sequence System
Integrate all bot handlers with unified sequence tracking
"""

from global_sequence_system import (
    start_user_global_sequence, log_sequence_step, link_to_global_sequence,
    get_user_sequence_id, complete_global_sequence
)
from sequence_logger import get_sequence_logger, with_sequence

# Enhanced logger with sequence support
logger = get_sequence_logger(__name__)

class SequenceHandlerMixin:
    """Mixin to add sequence tracking to handlers"""
    
    @staticmethod
    async def ensure_user_sequence(user_id: int, username: str = None, language: str = None) -> str:
        """Ensure user has an active sequence"""
        sequence_id = get_user_sequence_id(user_id)
        
        if not sequence_id:
            # Start new sequence if none exists
            sequence_id = start_user_global_sequence(user_id, username, language)
            logger.info(f"🆔 Created new sequence {sequence_id} for user {user_id}")
        
        return sequence_id
    
    @staticmethod
    async def log_handler_step(sequence_id: str, handler_name: str, user_id: int, 
                              action: str, metadata: dict = None):
        """Log handler step with sequence tracking"""
        step_name = f"{handler_name}_{action.replace(' ', '_')}"
        
        handler_metadata = metadata or {}
        handler_metadata.update({
            'user_id': user_id,
            'handler': handler_name,
            'action': action
        })
        
        log_sequence_step(sequence_id, step_name, "handlers", handler_metadata)
        logger.step_complete(sequence_id, step_name, "handlers", f"Handler: {handler_name}")

# Integration templates for existing handlers

def integrate_start_handler():
    """Integration template for start_handler"""
    return '''
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command with sequence tracking"""
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Start global sequence
    sequence_id = start_user_global_sequence(user_id, username)
    
    with with_sequence(logger, sequence_id):
        logger.info(f"🚀 User {user_id} started bot interaction")
        logger.step_start(sequence_id, "User_Flow_1_Start", "handlers", "Bot started by user")
        
        # Store sequence ID in state
        await state.update_data(sequence_id=sequence_id)
        
        # Existing start handler logic...
        
        # Log language selection step when completed
        logger.step_complete(sequence_id, "User_Flow_2_LanguageSelect", "handlers", 
                           "Language selection initiated")
'''

def integrate_language_selection():
    """Integration template for language selection"""
    return '''
async def language_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle language selection with sequence tracking"""
    user_id = callback_query.from_user.id
    language = callback_query.data.split('_')[1]  # e.g., 'lang_ar'
    
    # Get sequence ID from state
    state_data = await state.get_data()
    sequence_id = state_data.get('sequence_id') or await ensure_user_sequence(user_id)
    
    with with_sequence(logger, sequence_id):
        logger.step_complete(sequence_id, "User_Flow_2_LanguageSelect", "handlers", 
                           f"Language selected: {language}", {'language': language})
        
        # Update sequence with language
        link_to_global_sequence(sequence_id, "user_preferences", "language", language)
        
        # Existing language selection logic...
        
        logger.step_complete(sequence_id, "User_Flow_3_MainMenu", "handlers", 
                           "Main menu displayed")
'''

def integrate_create_ad_handler():
    """Integration template for create ad handler"""
    return '''
async def create_ad_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle ad creation start with sequence tracking"""
    user_id = callback_query.from_user.id
    
    # Get or create sequence
    state_data = await state.get_data()
    sequence_id = state_data.get('sequence_id') or await ensure_user_sequence(user_id)
    
    with with_sequence(logger, sequence_id):
        logger.step_start(sequence_id, "CreateAd_Step_1_Start", "handlers", "Ad creation initiated")
        
        # Store in state for next steps
        await state.update_data(sequence_id=sequence_id, creating_ad=True)
        
        # Existing ad creation logic...
        
        logger.step_complete(sequence_id, "CreateAd_Step_1_Start", "handlers", 
                           "Ad creation flow started")
'''

def integrate_upload_content_handler():
    """Integration template for content upload"""
    return '''
async def upload_content_handler(message: Message, state: FSMContext):
    """Handle content upload with sequence tracking"""
    user_id = message.from_user.id
    
    # Get sequence from state
    state_data = await state.get_data()
    sequence_id = state_data.get('sequence_id')
    
    if not sequence_id:
        logger.error(f"No sequence ID found for user {user_id} during content upload")
        return
    
    with with_sequence(logger, sequence_id):
        logger.step_start(sequence_id, "CreateAd_Step_2_UploadContent", "handlers", 
                         "Content upload in progress")
        
        # Determine content type
        content_type = "text"
        content_data = {"text": message.text}
        
        if message.photo:
            content_type = "photo"
            content_data = {
                "text": message.caption or "",
                "media_url": message.photo[-1].file_id,
                "media_type": "photo"
            }
        elif message.video:
            content_type = "video"
            content_data = {
                "text": message.caption or "",
                "media_url": message.video.file_id,
                "media_type": "video"
            }
        
        # Save ad to database
        ad_id = await save_ad_content(user_id, content_data, content_type)
        
        # Link ad to sequence
        link_to_global_sequence(sequence_id, "ads", "ad", str(ad_id), "primary", {
            "content_type": content_type,
            "has_media": content_type != "text"
        })
        
        # Store ad_id in state
        await state.update_data(ad_id=ad_id)
        
        logger.step_complete(sequence_id, "CreateAd_Step_2_UploadContent", "handlers", 
                           f"Content uploaded: {content_type}", {
                               "ad_id": ad_id,
                               "content_type": content_type,
                               "has_media": content_type != "text"
                           })
        
        # Continue to channel selection
        logger.step_start(sequence_id, "CreateAd_Step_3_SelectChannels", "handlers", 
                         "Channel selection initiated")
'''

def integrate_channel_selection():
    """Integration template for channel selection"""
    return '''
async def continue_with_channels_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle channel selection with sequence tracking"""
    user_id = callback_query.from_user.id
    
    # Get sequence from state
    state_data = await state.get_data()
    sequence_id = state_data.get('sequence_id')
    
    with with_sequence(logger, sequence_id):
        logger.step_complete(sequence_id, "CreateAd_Step_3_SelectChannels", "handlers", 
                           "Channel selection completed")
        
        # Get selected channels from state
        selected_channels = state_data.get('selected_channels', [])
        
        # Link channels to sequence
        for channel in selected_channels:
            link_to_global_sequence(sequence_id, "channels", "channel", channel, "selected")
        
        logger.step_start(sequence_id, "CreateAd_Step_4_SelectDuration", "handlers", 
                         "Duration selection initiated", {
                             "selected_channels": selected_channels,
                             "channel_count": len(selected_channels)
                         })
'''

def integrate_payment_processing():
    """Integration template for payment processing"""
    return '''
async def process_ton_payment(user_id: int, amount: float, memo: str, sequence_id: str = None):
    """Process TON payment with sequence tracking"""
    
    if not sequence_id:
        sequence_id = get_user_sequence_id(user_id)
    
    if sequence_id:
        with with_sequence(logger, sequence_id):
            logger.step_start(sequence_id, "Payment_Step_1_ProcessTON", "payment_system", 
                             "TON payment processing started")
            
            # Link payment to sequence
            link_to_global_sequence(sequence_id, "payments", "ton_payment", memo, "primary", {
                "amount": amount,
                "currency": "TON",
                "memo": memo,
                "user_id": user_id
            })
            
            # Existing payment processing logic...
            
            logger.step_complete(sequence_id, "Payment_Step_2_PaymentDetected", "payment_system", 
                               f"TON payment detected: {memo}", {
                                   "memo": memo,
                                   "amount": amount,
                                   "verification_status": "pending"
                               })

async def confirm_payment(user_id: int, memo: str, sequence_id: str = None):
    """Confirm payment with sequence tracking"""
    
    if not sequence_id:
        sequence_id = get_user_sequence_id(user_id)
    
    if sequence_id:
        with with_sequence(logger, sequence_id):
            logger.step_complete(sequence_id, "Payment_Step_3_PaymentConfirmed", "payment_system", 
                               f"Payment confirmed: {memo}")
            
            # Start campaign creation
            logger.step_start(sequence_id, "Campaign_Step_1_CreateCampaign", "campaign_management", 
                             "Campaign creation from payment")
'''

def integrate_campaign_management():
    """Integration template for campaign management"""
    return '''
async def create_campaign_for_payment(user_id: int, payment_memo: str, campaign_data: dict, sequence_id: str = None):
    """Create campaign with sequence tracking"""
    
    if not sequence_id:
        sequence_id = get_user_sequence_id(user_id)
    
    if sequence_id:
        with with_sequence(logger, sequence_id):
            # Generate campaign ID
            campaign_id = f"CAM-{datetime.now().strftime('%Y-%m')}-{payment_memo[:4]}"
            
            logger.step_start(sequence_id, "Campaign_Step_1_CreateCampaign", "campaign_management", 
                             f"Creating campaign {campaign_id}")
            
            # Link campaign to sequence
            link_to_global_sequence(sequence_id, "campaigns", "campaign", campaign_id, "primary", {
                "payment_memo": payment_memo,
                "campaign_data": campaign_data
            })
            
            # Existing campaign creation logic...
            
            logger.step_complete(sequence_id, "Campaign_Step_2_PostIdentity", "post_identity_system", 
                               f"Post identity created for {campaign_id}")
            
            logger.step_complete(sequence_id, "Campaign_Step_3_SchedulePosts", "campaign_management", 
                               f"Posts scheduled for {campaign_id}")
'''

def integrate_content_publishing():
    """Integration template for content publishing"""
    return '''
async def publish_campaign_post(campaign_id: str, post_id: str, channel_id: str):
    """Publish content with sequence tracking"""
    
    # Find sequence by campaign
    sequence_ids = find_sequence_by_component("campaigns", campaign_id)
    
    if sequence_ids:
        sequence_id = sequence_ids[0]  # Use first found sequence
        
        with with_sequence(logger, sequence_id):
            logger.step_start(sequence_id, "Publish_Step_1_SendToChannel", "campaign_publisher", 
                             f"Publishing {post_id} to {channel_id}")
            
            try:
                # Existing publishing logic...
                message_id = await send_to_channel(channel_id, content)
                
                # Link published message to sequence
                link_to_global_sequence(sequence_id, "published_messages", "message", 
                                      f"{channel_id}:{message_id}", "published", {
                                          "post_id": post_id,
                                          "channel_id": channel_id,
                                          "message_id": message_id
                                      })
                
                logger.step_complete(sequence_id, "Publish_Step_2_Published", "campaign_publisher", 
                                   f"Content published successfully", {
                                       "post_id": post_id,
                                       "channel_id": channel_id,
                                       "message_id": message_id
                                   })
                
            except Exception as e:
                logger.step_error(sequence_id, "Publish_Step_1_SendToChannel", "campaign_publisher", 
                                str(e), {"post_id": post_id, "channel_id": channel_id})
'''

def get_integration_summary():
    """Get summary of all integration points"""
    return {
        "start_handler": "Start global sequence, log initial user interaction",
        "language_selection": "Complete language step, link language preference",
        "create_ad_handler": "Start ad creation sequence steps",
        "upload_content": "Log content upload, link ad to sequence",
        "channel_selection": "Complete channel selection, link selected channels",
        "payment_processing": "Track payment steps, link payment to sequence",
        "campaign_management": "Track campaign creation, link campaign to sequence",
        "content_publishing": "Track publishing steps, link published messages",
        "admin_actions": "Track admin actions with sequence context",
        "error_handling": "Log errors with sequence context for debugging"
    }