"""
Telegram Stars Payment Integration for Enhanced Ad Bot
Integrates with existing TON payment system to offer dual payment options
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from aiogram import Bot, types
from aiogram.types import (
    PreCheckoutQuery, 
    SuccessfulPayment, 
    LabeledPrice,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import SessionLocal, Order, Channel, User

logger = logging.getLogger(__name__)

class TelegramStarsPayment:
    """Telegram Stars payment handler integrated with existing bot"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        
    async def create_stars_invoice(self, user_id: int, order_data: Dict) -> None:
        """Create Telegram Stars invoice for order"""
        try:
            db = SessionLocal()
            
            # Get order details
            order = db.query(Order).filter(Order.id == order_data['order_id']).first()
            if not order:
                logger.error(f"Order not found: {order_data['order_id']}")
                return
            
            # Calculate Stars amount (1 USD = 100 Stars approximately)
            stars_amount = int(float(order.total_amount_usd) * 100)
            
            # Create invoice description
            channels = db.query(Channel).filter(Channel.id.in_(order_data['channels'])).all()
            channel_names = [c.name for c in channels]
            
            description = (
                f"🎯 Ad Campaign for {order.duration_months} months\n"
                f"📺 Channels: {', '.join(channel_names[:2])}"
                f"{'...' if len(channel_names) > 2 else ''}\n"
                f"📊 Total posts: {order.posts_total}"
            )
            
            # Create unique payload for tracking
            payload = f"stars_order_{order.id}_{user_id}"
            
            # Send invoice
            await self.bot.send_invoice(
                chat_id=user_id,
                title=f"💫 Ad Campaign - {order.duration_months} Month{'s' if order.duration_months > 1 else ''}",
                description=description,
                payload=payload,
                provider_token="",  # Empty for Stars payments
                currency="XTR",  # Telegram Stars
                prices=[LabeledPrice(label="Ad Campaign", amount=stars_amount)],
                photo_url="https://raw.githubusercontent.com/telegram-bot-sdk/telegram-bot-sdk/master/docs/logo.png",
                photo_width=512,
                photo_height=512,
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False,
                max_tip_amount=0,
                suggested_tip_amounts=[]
            )
            
            logger.info(f"Stars invoice sent for order {order.id}: {stars_amount} Stars")
            
        except Exception as e:
            logger.error(f"Error creating Stars invoice: {e}")
        finally:
            db.close()
    
    async def handle_pre_checkout(self, pre_checkout_query: PreCheckoutQuery) -> None:
        """Handle pre-checkout validation for Stars payments"""
        try:
            # Parse payload
            payload_parts = pre_checkout_query.invoice_payload.split("_")
            if len(payload_parts) != 3 or payload_parts[0] != "stars":
                await pre_checkout_query.answer(ok=False, error_message="Invalid payment request")
                return
            
            order_id = payload_parts[2]
            user_id = int(payload_parts[3])
            
            # Validate user
            if user_id != pre_checkout_query.from_user.id:
                await pre_checkout_query.answer(ok=False, error_message="Invalid user")
                return
            
            # Check order exists and is valid
            db = SessionLocal()
            order = db.query(Order).filter(Order.id == order_id).first()
            
            if not order:
                await pre_checkout_query.answer(ok=False, error_message="Order not found")
                return
            
            if order.payment_status != 'pending':
                await pre_checkout_query.answer(ok=False, error_message="Order already processed")
                return
            
            # Validate amount
            expected_stars = int(order.total_amount_usd * 100)
            if pre_checkout_query.total_amount != expected_stars:
                await pre_checkout_query.answer(ok=False, error_message="Invalid amount")
                return
            
            # Approve payment
            await pre_checkout_query.answer(ok=True)
            logger.info(f"Pre-checkout approved for order {order_id}")
            
        except Exception as e:
            logger.error(f"Pre-checkout error: {e}")
            await pre_checkout_query.answer(ok=False, error_message="Payment validation failed")
        finally:
            db.close()
    
    async def handle_successful_payment(self, message: types.Message) -> None:
        """Handle successful Stars payment"""
        try:
            payment: SuccessfulPayment = message.successful_payment
            
            # Parse payload
            payload_parts = payment.invoice_payload.split("_")
            order_id = payload_parts[2]
            user_id = int(payload_parts[3])
            
            db = SessionLocal()
            
            # Update order status
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.error(f"Order not found for successful payment: {order_id}")
                return
            
            # Update order with Stars payment info
            order.payment_status = 'confirmed'
            order.payment_method = 'telegram_stars'
            order.status = 'active'
            order.paid_at = datetime.utcnow()
            order.payment_tx_hash = payment.telegram_payment_charge_id
            order.started_at = datetime.utcnow()
            order.expires_at = datetime.utcnow() + timedelta(days=30 * order.duration_months)
            
            db.commit()
            
            # Get channel names for confirmation
            channels = db.query(Channel).filter(Channel.id.in_([c.id for c in order.channels])).all()
            channel_names = [c.name for c in channels]
            
            # Send confirmation message
            await message.answer(
                f"✅ Payment Successful!\n\n"
                f"🌟 Paid with Telegram Stars: {payment.total_amount} Stars\n"
                f"📦 Order ID: {order.id}\n"
                f"🎯 Campaign Duration: {order.duration_months} months\n"
                f"📺 Channels: {', '.join(channel_names)}\n"
                f"📊 Total Posts: {order.posts_total}\n"
                f"💳 Payment ID: {payment.telegram_payment_charge_id}\n\n"
                f"🚀 Your advertising campaign is now active!\n"
                f"Your ads will start appearing across selected channels."
            )
            
            # Start campaign (integrate with existing campaign system)
            await self.start_campaign(order_id)
            
            logger.info(f"Stars payment successful: Order {order_id}, Amount {payment.total_amount} Stars")
            
        except Exception as e:
            logger.error(f"Error processing successful Stars payment: {e}")
        finally:
            db.close()
    
    async def start_campaign(self, order_id: str) -> None:
        """Start advertising campaign after successful payment"""
        try:
            db = SessionLocal()
            order = db.query(Order).filter(Order.id == order_id).first()
            
            if not order:
                return
            
            # This will integrate with your existing campaign scheduler
            # For now, we'll just log that the campaign should start
            logger.info(f"Starting campaign for order {order_id}")
            
            # You can integrate this with your existing scheduler.py
            # to start posting ads across selected channels
            
        except Exception as e:
            logger.error(f"Error starting campaign: {e}")
        finally:
            db.close()
    
    async def refund_stars_payment(self, order_id: str, admin_user_id: int) -> bool:
        """Refund Stars payment (admin only)"""
        try:
            db = SessionLocal()
            
            # Check if admin
            admin = db.query(User).filter(User.id == admin_user_id, User.is_admin == True).first()
            if not admin:
                return False
            
            # Get order
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order or order.payment_method != 'telegram_stars':
                return False
            
            # Process refund
            success = await self.bot.refund_star_payment(
                user_id=order.user_id,
                telegram_payment_charge_id=order.payment_tx_hash
            )
            
            if success:
                # Update order status
                order.payment_status = 'refunded'
                order.status = 'cancelled'
                db.commit()
                
                # Notify user
                await self.bot.send_message(
                    order.user_id,
                    f"💫 Stars Payment Refunded\n\n"
                    f"Your payment of {int(order.total_amount_usd * 100)} Stars has been refunded.\n"
                    f"Order ID: {order.id}\n\n"
                    f"The refund will appear in your Telegram Stars balance shortly."
                )
                
                logger.info(f"Stars payment refunded for order {order_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error refunding Stars payment: {e}")
            return False
        finally:
            db.close()
    
    def get_payment_method_keyboard(self, order_id: str) -> InlineKeyboardMarkup:
        """Create payment method selection keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💎 Pay with TON",
                    callback_data=f"pay_ton_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Pay with Telegram Stars", 
                    callback_data=f"pay_stars_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 View Pricing Details",
                    callback_data=f"view_pricing_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back to Selection",
                    callback_data="reset_selection"
                )
            ]
        ])
    
    async def show_payment_comparison(self, user_id: int, order_data: Dict) -> None:
        """Show payment method comparison"""
        try:
            db = SessionLocal()
            order = db.query(Order).filter(Order.id == order_data['order_id']).first()
            
            if not order:
                return
            
            # Calculate both payment amounts
            usd_amount = order.total_amount_usd
            ton_amount = order.total_amount_ton
            stars_amount = int(usd_amount * 100)
            
            comparison_text = (
                f"💳 **Payment Methods Available**\n\n"
                f"**Option 1: TON Cryptocurrency**\n"
                f"💎 Amount: {ton_amount:.3f} TON\n"
                f"💰 USD Value: ${usd_amount:.2f}\n"
                f"⚡ Fast blockchain confirmation\n"
                f"🔐 Decentralized payment\n\n"
                f"**Option 2: Telegram Stars**\n"
                f"⭐ Amount: {stars_amount} Stars\n"
                f"💰 USD Value: ${usd_amount:.2f}\n"
                f"🚀 Instant confirmation\n"
                f"🎯 Built into Telegram\n\n"
                f"Choose your preferred payment method:"
            )
            
            keyboard = self.get_payment_method_keyboard(order.id)
            
            await self.bot.send_message(
                user_id,
                comparison_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing payment comparison: {e}")
        finally:
            db.close()

# Integration helper functions
async def register_stars_handlers(dp, bot: Bot):
    """Register Telegram Stars payment handlers"""
    stars_payment = TelegramStarsPayment(bot)
    
    # Register handlers
    dp.pre_checkout_query.register(stars_payment.handle_pre_checkout)
    dp.message.register(
        stars_payment.handle_successful_payment,
        lambda message: message.successful_payment is not None
    )
    
    return stars_payment