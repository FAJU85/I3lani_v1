#!/usr/bin/env python3
"""
Integration of End-to-End Tracking with Handlers
Seamlessly integrates tracking system with existing handler functions
"""

import logging
from typing import Dict, Any
from end_to_end_tracking_system import get_tracking_system, start_tracking, track_step, complete_tracking
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

class TrackingIntegration:
    """Integration helper for tracking system"""
    
    def __init__(self):
        self.tracking_system = get_tracking_system()
    
    async def ensure_tracking_started(self, user_id: int, username: str = None, state: FSMContext = None) -> str:
        """Ensure tracking is started for user"""
        try:
            if state:
                data = await state.get_data()
                tracking_id = data.get('tracking_id')
                
                if tracking_id:
                    return tracking_id
            
            # Start new tracking
            tracking_id = await start_tracking(user_id, username)
            
            if state and tracking_id:
                await state.update_data(tracking_id=tracking_id)
            
            return tracking_id
            
        except Exception as e:
            logger.error(f"❌ Error ensuring tracking started: {e}")
            return None
    
    async def track_bot_start(self, user_id: int, username: str = None, state: FSMContext = None):
        """Track bot start"""
        try:
            tracking_id = await self.ensure_tracking_started(user_id, username, state)
            if tracking_id:
                await track_step(tracking_id, "start_bot", "completed", {
                    "action": "bot_started",
                    "user_id": user_id,
                    "username": username
                })
                logger.info(f"✅ Tracked bot start for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking bot start: {e}")
    
    async def track_create_ad_start(self, user_id: int, state: FSMContext):
        """Track ad creation start"""
        try:
            tracking_id = await self.ensure_tracking_started(user_id, state=state)
            if tracking_id:
                await track_step(tracking_id, "create_ad_start", "completed", {
                    "action": "ad_creation_started",
                    "timestamp": "current"
                })
                logger.info(f"✅ Tracked ad creation start for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking ad creation start: {e}")
    
    async def track_content_upload(self, user_id: int, content_type: str, state: FSMContext):
        """Track content upload"""
        try:
            data = await state.get_data()
            tracking_id = data.get('tracking_id')
            
            if tracking_id:
                await track_step(tracking_id, "upload_content", "completed", {
                    "action": "content_uploaded",
                    "content_type": content_type,
                    "timestamp": "current"
                })
                logger.info(f"✅ Tracked content upload for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking content upload: {e}")
    
    async def track_channel_selection(self, user_id: int, selected_channels: list, state: FSMContext):
        """Track channel selection"""
        try:
            data = await state.get_data()
            tracking_id = data.get('tracking_id')
            
            if tracking_id:
                await track_step(tracking_id, "select_channels", "completed", {
                    "action": "channels_selected",
                    "channel_count": len(selected_channels),
                    "channels": selected_channels
                })
                logger.info(f"✅ Tracked channel selection for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking channel selection: {e}")
    
    async def track_duration_selection(self, user_id: int, duration_days: int, state: FSMContext):
        """Track duration selection"""
        try:
            data = await state.get_data()
            tracking_id = data.get('tracking_id')
            
            if tracking_id:
                await track_step(tracking_id, "select_duration", "completed", {
                    "action": "duration_selected",
                    "duration_days": duration_days
                })
                logger.info(f"✅ Tracked duration selection for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking duration selection: {e}")
    
    async def track_frequency_selection(self, user_id: int, posts_per_day: int, state: FSMContext):
        """Track frequency selection"""
        try:
            data = await state.get_data()
            tracking_id = data.get('tracking_id')
            
            if tracking_id:
                await track_step(tracking_id, "select_frequency", "completed", {
                    "action": "frequency_selected",
                    "posts_per_day": posts_per_day
                })
                logger.info(f"✅ Tracked frequency selection for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking frequency selection: {e}")
    
    async def track_campaign_confirmation(self, user_id: int, campaign_data: Dict, state: FSMContext):
        """Track campaign confirmation"""
        try:
            data = await state.get_data()
            tracking_id = data.get('tracking_id')
            
            if tracking_id:
                await track_step(tracking_id, "confirm_campaign", "completed", {
                    "action": "campaign_confirmed",
                    "campaign_data": campaign_data
                })
                logger.info(f"✅ Tracked campaign confirmation for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking campaign confirmation: {e}")
    
    async def track_payment_method_selection(self, user_id: int, payment_method: str, state: FSMContext):
        """Track payment method selection"""
        try:
            data = await state.get_data()
            tracking_id = data.get('tracking_id')
            
            if tracking_id:
                await track_step(tracking_id, "select_payment", "completed", {
                    "action": "payment_method_selected",
                    "payment_method": payment_method
                })
                logger.info(f"✅ Tracked payment method selection for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking payment method selection: {e}")
    
    async def track_payment_processing(self, user_id: int, payment_amount: float, state: FSMContext):
        """Track payment processing"""
        try:
            data = await state.get_data()
            tracking_id = data.get('tracking_id')
            
            if tracking_id:
                await track_step(tracking_id, "process_payment", "in_progress", {
                    "action": "payment_processing",
                    "amount": payment_amount
                })
                logger.info(f"✅ Tracked payment processing for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking payment processing: {e}")
    
    async def track_payment_confirmed(self, user_id: int, payment_memo: str, campaign_id: str, state: FSMContext):
        """Track payment confirmation"""
        try:
            data = await state.get_data()
            tracking_id = data.get('tracking_id')
            
            if tracking_id:
                await track_step(tracking_id, "payment_confirmed", "completed", {
                    "action": "payment_confirmed",
                    "payment_memo": payment_memo,
                    "campaign_id": campaign_id
                })
                logger.info(f"✅ Tracked payment confirmation for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking payment confirmation: {e}")
    
    async def track_publishing_scheduled(self, user_id: int, campaign_id: str, post_count: int, state: FSMContext):
        """Track publishing scheduled"""
        try:
            data = await state.get_data()
            tracking_id = data.get('tracking_id')
            
            if tracking_id:
                await track_step(tracking_id, "schedule_publishing", "completed", {
                    "action": "publishing_scheduled",
                    "campaign_id": campaign_id,
                    "post_count": post_count
                })
                logger.info(f"✅ Tracked publishing scheduled for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking publishing scheduled: {e}")
    
    async def track_publishing_started(self, user_id: int, campaign_id: str):
        """Track publishing started"""
        try:
            # Get tracking ID from campaign
            tracking_id = await self.get_tracking_id_from_campaign(campaign_id)
            
            if tracking_id:
                await track_step(tracking_id, "start_publishing", "completed", {
                    "action": "publishing_started",
                    "campaign_id": campaign_id
                })
                logger.info(f"✅ Tracked publishing started for campaign {campaign_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking publishing started: {e}")
    
    async def track_publishing_complete(self, user_id: int, campaign_id: str):
        """Track publishing complete and trigger final confirmation"""
        try:
            tracking_id = await self.get_tracking_id_from_campaign(campaign_id)
            
            if tracking_id:
                await track_step(tracking_id, "publishing_complete", "completed", {
                    "action": "publishing_complete",
                    "campaign_id": campaign_id
                })
                
                # Complete tracking and send final confirmation
                await complete_tracking(tracking_id, campaign_id)
                
                logger.info(f"✅ Tracked publishing complete for campaign {campaign_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking publishing complete: {e}")
    
    async def get_tracking_id_from_campaign(self, campaign_id: str) -> str:
        """Get tracking ID from campaign ID"""
        try:
            import sqlite3
            conn = sqlite3.connect("bot.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tracking_id FROM campaign_tracking 
                WHERE campaign_id = ?
            """, (campaign_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Error getting tracking ID from campaign: {e}")
            return None

# Global instance
_tracking_integration = None

def get_tracking_integration() -> TrackingIntegration:
    """Get or create tracking integration instance"""
    global _tracking_integration
    if _tracking_integration is None:
        _tracking_integration = TrackingIntegration()
    return _tracking_integration

# Convenience functions for handlers
async def track_bot_start(user_id: int, username: str = None, state: FSMContext = None):
    """Track bot start"""
    integration = get_tracking_integration()
    await integration.track_bot_start(user_id, username, state)

async def track_create_ad_start(user_id: int, state: FSMContext):
    """Track ad creation start"""
    integration = get_tracking_integration()
    await integration.track_create_ad_start(user_id, state)

async def track_content_upload(user_id: int, content_type: str, state: FSMContext):
    """Track content upload"""
    integration = get_tracking_integration()
    await integration.track_content_upload(user_id, content_type, state)

async def track_channel_selection(user_id: int, selected_channels: list, state: FSMContext):
    """Track channel selection"""
    integration = get_tracking_integration()
    await integration.track_channel_selection(user_id, selected_channels, state)

async def track_duration_selection(user_id: int, duration_days: int, state: FSMContext):
    """Track duration selection"""
    integration = get_tracking_integration()
    await integration.track_duration_selection(user_id, duration_days, state)

async def track_frequency_selection(user_id: int, posts_per_day: int, state: FSMContext):
    """Track frequency selection"""
    integration = get_tracking_integration()
    await integration.track_frequency_selection(user_id, posts_per_day, state)

async def track_campaign_confirmation(user_id: int, campaign_data: Dict, state: FSMContext):
    """Track campaign confirmation"""
    integration = get_tracking_integration()
    await integration.track_campaign_confirmation(user_id, campaign_data, state)

async def track_payment_method_selection(user_id: int, payment_method: str, state: FSMContext):
    """Track payment method selection"""
    integration = get_tracking_integration()
    await integration.track_payment_method_selection(user_id, payment_method, state)

async def track_payment_processing(user_id: int, payment_amount: float, state: FSMContext):
    """Track payment processing"""
    integration = get_tracking_integration()
    await integration.track_payment_processing(user_id, payment_amount, state)

async def track_payment_confirmed(user_id: int, payment_memo: str, campaign_id: str, state: FSMContext):
    """Track payment confirmation"""
    integration = get_tracking_integration()
    await integration.track_payment_confirmed(user_id, payment_memo, campaign_id, state)

async def track_publishing_scheduled(user_id: int, campaign_id: str, post_count: int, state: FSMContext):
    """Track publishing scheduled"""
    integration = get_tracking_integration()
    await integration.track_publishing_scheduled(user_id, campaign_id, post_count, state)

async def track_publishing_started(user_id: int, campaign_id: str):
    """Track publishing started"""
    integration = get_tracking_integration()
    await integration.track_publishing_started(user_id, campaign_id)

async def track_publishing_complete(user_id: int, campaign_id: str):
    """Track publishing complete"""
    integration = get_tracking_integration()
    await integration.track_publishing_complete(user_id, campaign_id)