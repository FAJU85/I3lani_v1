#!/usr/bin/env python3
"""
Enhanced Telegram Stars Payment System
Replacement for deleted enhanced Stars payment system
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from aiogram import Bot
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database

logger = logging.getLogger(__name__)

class EnhancedTelegramStarsPayment:
    """Enhanced Telegram Stars payment system"""
    
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db
        self.pending_payments = {}
        
    async def create_stars_invoice(self, user_id: int, amount: float, currency: str = "XTR", 
                                  title: str = "Ad Campaign", description: str = "Premium advertising campaign"):
        """Create Stars payment invoice"""
        try:
            # Convert amount to Stars (1 USD = 100 Stars approximately)
            stars_amount = int(amount * 100)
            
            # Create invoice
            invoice_link = await self.bot.create_invoice_link(
                title=title,
                description=description,
                payload=f"stars_payment_{user_id}_{datetime.now().timestamp()}",
                provider_token="",  # Empty for Stars
                currency=currency,
                prices=[LabeledPrice(label="Campaign", amount=stars_amount)]
            )
            
            return invoice_link
            
        except Exception as e:
            logger.error(f"Error creating Stars invoice: {e}")
            return None
    
    async def handle_pre_checkout(self, pre_checkout_query):
        """Handle pre-checkout query"""
        try:
            # Always approve Stars payments
            await pre_checkout_query.answer(ok=True)
            
        except Exception as e:
            logger.error(f"Error in pre-checkout handler: {e}")
            await pre_checkout_query.answer(ok=False, error_message="Payment processing error")
    
    async def handle_successful_payment(self, message):
        """Handle successful payment"""
        try:
            payment = message.successful_payment
            user_id = message.from_user.id
            
            # Process payment
            await self._process_stars_payment(user_id, payment)
            
        except Exception as e:
            logger.error(f"Error processing successful payment: {e}")
    
    async def _process_stars_payment(self, user_id: int, payment):
        """Process Stars payment"""
        try:
            # Create campaign from payment
            from campaign_management import create_campaign_from_payment
            
            campaign_id = await create_campaign_from_payment(
                user_id=user_id,
                payment_amount=payment.total_amount / 100,  # Convert from Stars
                payment_method="stars",
                payment_id=payment.telegram_payment_charge_id
            )
            
            # Send confirmation
            await self.bot.send_message(
                user_id,
                f"✅ Payment confirmed! Campaign {campaign_id} created successfully.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 View Campaign", callback_data=f"view_campaign_{campaign_id}")]
                ])
            )
            
        except Exception as e:
            logger.error(f"Error processing Stars payment: {e}")

# Global instance
enhanced_stars_payment = None

def get_enhanced_stars_payment(bot: Bot, db: Database) -> EnhancedTelegramStarsPayment:
    """Get or create enhanced Stars payment instance"""
    global enhanced_stars_payment
    if enhanced_stars_payment is None:
        enhanced_stars_payment = EnhancedTelegramStarsPayment(bot, db)
    return enhanced_stars_payment