"""
I3lani v3 Payment Integration
TON and Telegram Stars payment processing for auction-based system
"""

import logging
import aiosqlite
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
from aiogram import Bot
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton

from i3lani_v3_architecture import i3lani_v3

logger = logging.getLogger(__name__)

class V3PaymentProcessor:
    """Payment processor for I3lani v3 auction system"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.ton_rate = Decimal('0.36')  # 1 USD = 0.36 TON
        self.stars_rate = 34  # 1 USD = 34 Stars
    
    async def process_ad_payment(self, user_id: int, ad_id: str, payment_method: str, amount_usd: Decimal):
        """Process payment for ad creation"""
        try:
            # Get ad details
            async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
                async with db.execute("""
                    SELECT advertiser_id, bid_type, bid_amount, content, category, status
                    FROM ads_v3 WHERE ad_id = ?
                """, (ad_id,)) as cursor:
                    ad_result = await cursor.fetchone()
                
                if not ad_result:
                    return {'success': False, 'error': 'Ad not found'}
                
                advertiser_id, bid_type, bid_amount, content, category, status = ad_result
                
                if advertiser_id != user_id:
                    return {'success': False, 'error': 'Unauthorized'}
                
                if status != 'pending':
                    return {'success': False, 'error': 'Ad already processed'}
            
            # Calculate payment amount
            if payment_method == 'TON':
                payment_amount = amount_usd * self.ton_rate
                currency = 'TON'
            elif payment_method == 'STARS':
                payment_amount = int(amount_usd * self.stars_rate)
                currency = 'STARS'
            else:
                return {'success': False, 'error': 'Invalid payment method'}
            
            # Create payment record
            payment_id = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{ad_id}"
            
            async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
                await db.execute("""
                    INSERT INTO payments_v3 
                    (payment_id, user_id, amount, currency, purpose, status)
                    VALUES (?, ?, ?, ?, ?, 'pending')
                """, (payment_id, user_id, float(payment_amount), currency, f"Ad payment for {ad_id}"))
                await db.commit()
            
            # Process payment based on method
            if payment_method == 'TON':
                return await self.process_ton_payment(payment_id, user_id, payment_amount, ad_id)
            elif payment_method == 'STARS':
                return await self.process_stars_payment(payment_id, user_id, int(payment_amount), ad_id)
            
        except Exception as e:
            logger.error(f"❌ Payment processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def process_ton_payment(self, payment_id: str, user_id: int, amount: Decimal, ad_id: str):
        """Process TON payment"""
        try:
            # Generate payment memo
            memo = payment_id[-8:]  # Last 8 characters
            
            # Create payment instructions
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ I've Sent Payment", callback_data=f"ton_confirm_{payment_id}")],
                [InlineKeyboardButton(text="❌ Cancel", callback_data=f"payment_cancel_{payment_id}")]
            ])
            
            await self.bot.send_message(
                chat_id=user_id,
                text=f"💎 TON Payment Instructions\n\n"
                     f"💰 Amount: {amount:.8f} TON\n"
                     f"📝 Memo: {memo}\n"
                     f"🎯 Ad ID: {ad_id}\n\n"
                     f"📋 Send exactly {amount:.8f} TON to:\n"
                     f"<code>UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB</code>\n\n"
                     f"⚠️ Important: Include memo '{memo}' in your transaction\n\n"
                     f"💡 Your ad will be submitted for approval once payment is confirmed.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
            return {
                'success': True,
                'payment_id': payment_id,
                'method': 'TON',
                'amount': float(amount),
                'memo': memo
            }
            
        except Exception as e:
            logger.error(f"❌ TON payment error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def process_stars_payment(self, payment_id: str, user_id: int, amount: int, ad_id: str):
        """Process Telegram Stars payment"""
        try:
            # Create Stars invoice
            prices = [LabeledPrice(label="Ad Payment", amount=amount)]
            
            invoice_link = await self.bot.create_invoice_link(
                title="I3lani Ad Payment",
                description=f"Payment for ad {ad_id}",
                payload=payment_id,
                provider_token="",  # Stars payments don't need provider token
                currency="XTR",  # Telegram Stars currency
                prices=prices
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⭐ Pay with Stars", url=invoice_link)],
                [InlineKeyboardButton(text="❌ Cancel", callback_data=f"payment_cancel_{payment_id}")]
            ])
            
            await self.bot.send_message(
                chat_id=user_id,
                text=f"⭐ Telegram Stars Payment\n\n"
                     f"💰 Amount: {amount} Stars\n"
                     f"🎯 Ad ID: {ad_id}\n\n"
                     f"Click the button below to pay with Telegram Stars.\n\n"
                     f"💡 Your ad will be submitted for approval once payment is confirmed.",
                reply_markup=keyboard
            )
            
            return {
                'success': True,
                'payment_id': payment_id,
                'method': 'STARS',
                'amount': amount,
                'invoice_link': invoice_link
            }
            
        except Exception as e:
            logger.error(f"❌ Stars payment error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def confirm_payment(self, payment_id: str, transaction_hash: Optional[str] = None):
        """Confirm payment and update ad status"""
        try:
            async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
                # Update payment status
                await db.execute("""
                    UPDATE payments_v3 
                    SET status = 'completed', transaction_hash = ?
                    WHERE payment_id = ?
                """, (transaction_hash, payment_id))
                
                # Get payment details
                async with db.execute("""
                    SELECT user_id, amount, currency, purpose
                    FROM payments_v3 WHERE payment_id = ?
                """, (payment_id,)) as cursor:
                    payment_result = await cursor.fetchone()
                
                if not payment_result:
                    return {'success': False, 'error': 'Payment not found'}
                
                user_id, amount, currency, purpose = payment_result
                
                # Extract ad_id from purpose
                ad_id = purpose.split("for ")[-1]
                
                # Update ad status to pending approval
                await db.execute("""
                    UPDATE ads_v3 
                    SET status = 'pending'
                    WHERE ad_id = ?
                """, (ad_id,))
                
                # Update user balance if needed
                if currency == 'TON':
                    await db.execute("""
                        UPDATE users_v3 
                        SET balance_ton = balance_ton + ?
                        WHERE user_id = ?
                    """, (amount, user_id))
                elif currency == 'STARS':
                    await db.execute("""
                        UPDATE users_v3 
                        SET balance_stars = balance_stars + ?
                        WHERE user_id = ?
                    """, (int(amount), user_id))
                
                await db.commit()
                
                # Notify user
                await self.bot.send_message(
                    chat_id=user_id,
                    text=f"✅ Payment Confirmed!\n\n"
                         f"💰 Amount: {amount} {currency}\n"
                         f"🎯 Ad ID: {ad_id}\n\n"
                         f"📋 Your ad has been submitted for admin approval.\n"
                         f"🚀 Once approved, it will enter the daily auction system!"
                )
                
                # Calculate affiliate commission if applicable
                await self.process_affiliate_commission(user_id, Decimal(str(amount)))
                
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'ad_id': ad_id,
                    'amount': amount,
                    'currency': currency
                }
                
        except Exception as e:
            logger.error(f"❌ Payment confirmation error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def process_affiliate_commission(self, user_id: int, amount: Decimal):
        """Process affiliate commission for advertiser spending"""
        try:
            async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
                # Check if user was referred
                async with db.execute("""
                    SELECT referrer_id FROM users_v3 WHERE user_id = ?
                """, (user_id,)) as cursor:
                    referrer_result = await cursor.fetchone()
                
                if referrer_result and referrer_result[0]:
                    affiliate_id = referrer_result[0]
                    commission_rate = Decimal('0.05')  # 5% commission
                    commission = amount * commission_rate
                    
                    # Create commission record
                    commission_id = f"COM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    await db.execute("""
                        INSERT INTO commissions_v3 
                        (commission_id, affiliate_id, referred_user_id, amount, source)
                        VALUES (?, ?, ?, ?, 'advertiser_spending')
                    """, (commission_id, affiliate_id, user_id, float(commission)))
                    
                    # Update affiliate balance
                    await db.execute("""
                        UPDATE users_v3 
                        SET balance_ton = balance_ton + ?
                        WHERE user_id = ?
                    """, (float(commission), affiliate_id))
                    
                    await db.commit()
                    
                    # Notify affiliate
                    await self.bot.send_message(
                        chat_id=affiliate_id,
                        text=f"💰 Commission Earned!\n\n"
                             f"🎯 From: Advertiser spending\n"
                             f"💰 Amount: {commission:.8f} TON\n"
                             f"📊 Commission rate: 5%\n\n"
                             f"Keep referring users to earn more!"
                    )
                    
        except Exception as e:
            logger.error(f"❌ Affiliate commission error: {e}")
    
    async def cancel_payment(self, payment_id: str, user_id: int):
        """Cancel payment"""
        try:
            async with aiosqlite.connect(i3lani_v3.db.db_path) as db:
                await db.execute("""
                    UPDATE payments_v3 
                    SET status = 'cancelled'
                    WHERE payment_id = ? AND user_id = ?
                """, (payment_id, user_id))
                await db.commit()
                
                return {'success': True, 'message': 'Payment cancelled'}
                
        except Exception as e:
            logger.error(f"❌ Payment cancellation error: {e}")
            return {'success': False, 'error': str(e)}

class V3PaymentHandlers:
    """Payment callback handlers for I3lani v3"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.processor = V3PaymentProcessor(bot)
    
    async def handle_ton_payment_callback(self, callback_query, state):
        """Handle TON payment callbacks"""
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        if data.startswith("pay_ton_"):
            ad_id = data.replace("pay_ton_", "")
            
            # Calculate payment amount (this would need to be dynamic based on ad details)
            amount_usd = Decimal('10.00')  # Example amount
            
            result = await self.processor.process_ad_payment(
                user_id=user_id,
                ad_id=ad_id,
                payment_method='TON',
                amount_usd=amount_usd
            )
            
            if result['success']:
                await callback_query.answer("💎 TON payment instructions sent!")
            else:
                await callback_query.answer(f"❌ Error: {result['error']}")
        
        elif data.startswith("ton_confirm_"):
            payment_id = data.replace("ton_confirm_", "")
            
            await callback_query.message.edit_text(
                "⏳ Payment confirmation received!\n\n"
                "We're verifying your TON payment on the blockchain.\n"
                "This usually takes 1-5 minutes.\n\n"
                "You'll receive a confirmation message once verified."
            )
            
            # In a real implementation, you would verify the payment on TON blockchain
            # For now, we'll simulate confirmation
            await self.processor.confirm_payment(payment_id)
            
            await callback_query.answer("✅ Payment confirmation received!")
        
        elif data.startswith("pay_stars_"):
            ad_id = data.replace("pay_stars_", "")
            
            amount_usd = Decimal('10.00')  # Example amount
            
            result = await self.processor.process_ad_payment(
                user_id=user_id,
                ad_id=ad_id,
                payment_method='STARS',
                amount_usd=amount_usd
            )
            
            if result['success']:
                await callback_query.answer("⭐ Stars payment ready!")
            else:
                await callback_query.answer(f"❌ Error: {result['error']}")
        
        elif data.startswith("payment_cancel_"):
            payment_id = data.replace("payment_cancel_", "")
            
            result = await self.processor.cancel_payment(payment_id, user_id)
            
            await callback_query.message.edit_text(
                "❌ Payment Cancelled\n\n"
                "Your payment has been cancelled.\n"
                "You can create a new ad anytime."
            )
            
            await callback_query.answer("Payment cancelled")
    
    async def handle_stars_payment_success(self, message):
        """Handle successful Stars payment"""
        if message.successful_payment:
            payment_id = message.successful_payment.invoice_payload
            
            # Confirm payment
            result = await self.processor.confirm_payment(
                payment_id=payment_id,
                transaction_hash=message.successful_payment.telegram_payment_charge_id
            )
            
            if result['success']:
                await message.answer(
                    "✅ Stars Payment Successful!\n\n"
                    f"🎯 Ad ID: {result['ad_id']}\n"
                    f"💰 Amount: {result['amount']} {result['currency']}\n\n"
                    f"Your ad is now pending approval!"
                )

# Global payment processor instance
payment_processor = None

def get_payment_processor(bot: Bot) -> V3PaymentProcessor:
    """Get or create payment processor instance"""
    global payment_processor
    if payment_processor is None:
        payment_processor = V3PaymentProcessor(bot)
    return payment_processor