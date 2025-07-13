#!/usr/bin/env python3
"""
Referral System Integration
Integrates referral system with main bot and handlers
"""

import logging
from referral_system import get_referral_system
from referral_handlers import setup_referral_handlers

logger = logging.getLogger(__name__)

async def integrate_referral_system_with_bot():
    """Integrate referral system with main bot"""
    try:
        # Initialize referral system
        referral_sys = await get_referral_system()
        
        # Initialize database
        db_init = await referral_sys.initialize_database()
        
        if db_init:
            logger.info("✅ Referral system database initialized")
        else:
            logger.error("❌ Failed to initialize referral database")
            return False
        
        logger.info("✅ Referral system integrated with bot")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error integrating referral system: {e}")
        return False

def setup_referral_system_handlers(dp):
    """Setup referral system handlers"""
    try:
        setup_referral_handlers(dp)
        logger.info("✅ Referral system handlers setup complete")
        return True
    except Exception as e:
        logger.error(f"❌ Error setting up referral handlers: {e}")
        return False

async def process_referral_start_command(user_id: int, start_param: str = None):
    """Process referral from start command"""
    try:
        referral_sys = await get_referral_system()
        
        # Check if start parameter is a referral code
        if start_param and start_param.startswith('ref_'):
            success = await referral_sys.register_user(user_id, start_param)
            if success:
                logger.info(f"✅ User {user_id} registered with referral code {start_param}")
                return True
        else:
            # Register user without referral
            success = await referral_sys.register_user(user_id)
            if success:
                logger.info(f"✅ User {user_id} registered without referral")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Error processing referral start: {e}")
        return False

async def process_user_earning(user_id: int, amount: float, source: str = None):
    """Process user earning for referral commission"""
    try:
        from decimal import Decimal
        
        referral_sys = await get_referral_system()
        
        # Convert amount to Decimal
        earning_amount = Decimal(str(amount))
        
        # Process referral commission
        success = await referral_sys.process_referral_commission(user_id, earning_amount, source)
        
        if success:
            logger.info(f"✅ Referral commission processed for user {user_id}: {earning_amount}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error processing user earning: {e}")
        return False