"""
Telegram Stars Payment Handler
Official implementation using Telegram Bot API
"""

import logging
from typing import Dict, Any, Optional
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.types.pre_checkout_query import PreCheckoutQuery
from aiogram.types.successful_payment import SuccessfulPayment
from config import BOT_TOKEN
from database import db

logger = logging.getLogger(__name__)

class TelegramStarsHandler:
    """Handle Telegram Stars payments using official API"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def create_invoice(self, user_id: int, title: str, description: str, 
                           price_stars: int, payload: str) -> InlineKeyboardMarkup:
        """Create Telegram Stars invoice"""
        try:
            # Create invoice using sendInvoice API
            prices = [LabeledPrice(label="Campaign", amount=price_stars)]
            
            # Create payment keyboard
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"💳 Pay {price_stars} ⭐",
                    pay=True
                )],
                [InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data="back_to_payment"
                )]
            ])
            
            # Send invoice
            await self.bot.send_invoice(
                chat_id=user_id,
                title=title,
                description=description,
                payload=payload,
                provider_token="",  # Empty for Stars
                currency="XTR",  # Telegram Stars currency
                prices=prices,
                reply_markup=keyboard
            )
            
            return keyboard
            
        except Exception as e:
            logger.error(f"Error creating Stars invoice: {e}")
            raise
    
    async def handle_pre_checkout(self, pre_checkout_query: PreCheckoutQuery) -> bool:
        """Handle pre-checkout query"""
        try:
            # Verify the order
            payload = pre_checkout_query.invoice_payload
            
            # For production, add validation logic here
            # For now, approve all pre-checkout queries
            
            await pre_checkout_query.answer(ok=True)
            logger.info(f"Pre-checkout approved for payload: {payload}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling pre-checkout: {e}")
            await pre_checkout_query.answer(
                ok=False, 
                error_message="Payment verification failed. Please try again."
            )
            return False
    
    async def handle_successful_payment(self, successful_payment: SuccessfulPayment, 
                                      user_id: int) -> bool:
        """Handle successful payment"""
        try:
            # Extract payment details
            payload = successful_payment.invoice_payload
            stars_amount = successful_payment.total_amount
            charge_id = successful_payment.telegram_payment_charge_id
            
            logger.info(f"Stars payment successful: {stars_amount} stars, charge: {charge_id}")
            
            # Process the payment
            await self._process_payment(user_id, payload, stars_amount, charge_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing successful payment: {e}")
            return False
    
    async def _process_payment(self, user_id: int, payload: str, 
                             stars_amount: int, charge_id: str):
        """Process the payment and activate campaign"""
        try:
            # Extract order details from payload
            order_data = self._parse_payload(payload)
            
            # Update payment status in database
            await db.update_payment_status(order_data['payment_id'], 'confirmed')
            
            # Activate subscription
            await db.activate_subscription(order_data['subscription_id'])
            
            # Publish ad to channel
            await self._publish_ad(user_id, order_data)
            
            logger.info(f"Payment processed successfully for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            raise
    
    def _parse_payload(self, payload: str) -> Dict[str, Any]:
        """Parse payload to extract order details"""
        try:
            # Expected format: "payment_id:subscription_id:user_id"
            parts = payload.split(':')
            return {
                'payment_id': int(parts[0]),
                'subscription_id': int(parts[1]),
                'user_id': int(parts[2])
            }
        except Exception as e:
            logger.error(f"Error parsing payload: {e}")
            raise
    
    async def _publish_ad(self, user_id: int, order_data: Dict[str, Any]):
        """Publish ad to I3lani channel"""
        try:
            # Get ad content from database
            ad_data = await db.get_ad_by_subscription(order_data['subscription_id'])
            
            if not ad_data:
                logger.error(f"No ad found for subscription {order_data['subscription_id']}")
                return
            
            # Format ad content
            ad_content = ad_data['content']
            formatted_content = f"📢 **Advertisement**\n\n{ad_content}\n\n✨ *Advertise with @I3lani_bot*"
            
            # Publish to I3lani channel
            i3lani_channel = "@i3lani"
            
            if ad_data.get('media_url'):
                # Handle media ads
                if ad_data['content_type'] == 'photo':
                    await self.bot.send_photo(
                        chat_id=i3lani_channel,
                        photo=ad_data['media_url'],
                        caption=formatted_content,
                        parse_mode='Markdown'
                    )
                elif ad_data['content_type'] == 'video':
                    await self.bot.send_video(
                        chat_id=i3lani_channel,
                        video=ad_data['media_url'],
                        caption=formatted_content,
                        parse_mode='Markdown'
                    )
            else:
                # Handle text ads
                await self.bot.send_message(
                    chat_id=i3lani_channel,
                    text=formatted_content,
                    parse_mode='Markdown'
                )
            
            logger.info(f"Ad published to {i3lani_channel} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error publishing ad: {e}")
            raise

# Global instance
stars_handler = None

def init_stars_handler(bot: Bot):
    """Initialize Telegram Stars handler"""
    global stars_handler
    stars_handler = TelegramStarsHandler(bot)
    return stars_handler

def get_stars_handler():
    """Get Telegram Stars handler instance"""
    return stars_handler