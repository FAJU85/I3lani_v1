#!/usr/bin/env python3
"""
Clean Telegram Stars Payment System
Simple, effective, traceable payment system with campaign integration
"""

import logging
import json
import time
import random
import string
from datetime import datetime
from typing import Dict, Optional, List, Any
from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    PreCheckoutQuery, Message, CallbackQuery,
    LabeledPrice, SuccessfulPayment
)
from aiogram.exceptions import TelegramAPIError

logger = logging.getLogger(__name__)

class CleanStarsPayment:
    """Clean, simple Stars payment system with full traceability"""
    
    def __init__(self, bot: Bot, db_instance=None):
        self.bot = bot
        self.db = db_instance
        
        # Stars payment configuration
        self.currency = "XTR"  # Telegram Stars currency code
        self.provider_token = ""  # Empty for Stars payments
        
        # Payment tracking
        self.pending_payments = {}  # In-memory storage for pending payments
    
    def generate_payment_id(self) -> str:
        """Generate unique payment ID: STAR{timestamp}{random}"""
        timestamp = int(time.time())
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"STAR{timestamp}{random_part}"
    
    async def create_payment_invoice(self, user_id: int, campaign_data: Dict, 
                                   pricing_data: Dict, language: str = 'en') -> Dict:
        """Create Telegram Stars invoice with campaign integration"""
        
        try:
            # Generate unique payment ID
            payment_id = self.generate_payment_id()
            
            # Extract campaign details
            days = campaign_data.get('duration', 1)
            channels = campaign_data.get('selected_channels', [])
            posts_per_day = campaign_data.get('posts_per_day', 1)
            total_posts = days * posts_per_day
            
            # Extract pricing details
            stars_amount = pricing_data.get('total_stars', 0)
            usd_amount = pricing_data.get('total_usd', 0)
            
            # Create invoice title and description
            if language == 'ar':
                title = "حملة إعلانية I3lani"
                description = f"📢 حملة {days} أيام، {posts_per_day} منشور/يوم عبر {len(channels)} قنوات. معرف الدفع: {payment_id}"
            elif language == 'ru':
                title = "Рекламная кампания I3lani"
                description = f"📢 Кампания {days} дней, {posts_per_day} постов/день через {len(channels)} каналов. ID платежа: {payment_id}"
            else:
                title = "I3lani Advertising Campaign"
                description = f"📢 {days} days campaign, {posts_per_day} posts/day across {len(channels)} channels. Payment ID: {payment_id}"
            
            # Create payload with all campaign data
            payload = json.dumps({
                'payment_id': payment_id,
                'user_id': user_id,
                'campaign_data': campaign_data,
                'pricing_data': pricing_data,
                'created_at': datetime.now().isoformat()
            })
            
            # Create price breakdown
            prices = [LabeledPrice(label="Campaign Cost", amount=stars_amount)]
            
            logger.info(f"💫 Creating Stars invoice for user {user_id}")
            logger.info(f"   Payment ID: {payment_id}")
            logger.info(f"   Amount: {stars_amount} ⭐ (${usd_amount:.2f})")
            logger.info(f"   Campaign: {days} days, {len(channels)} channels")
            
            # Store pending payment for tracking
            self.pending_payments[payment_id] = {
                'user_id': user_id,
                'payment_id': payment_id,
                'stars_amount': stars_amount,
                'usd_amount': usd_amount,
                'campaign_data': campaign_data,
                'pricing_data': pricing_data,
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            # Send Stars invoice
            invoice_message = await self.bot.send_invoice(
                chat_id=user_id,
                title=title,
                description=description,
                payload=payload,
                provider_token=self.provider_token,
                currency=self.currency,
                prices=prices,
                max_tip_amount=0,
                suggested_tip_amounts=[],
                start_parameter=f"stars_{payment_id}",
                provider_data=json.dumps({
                    'service': 'I3lani_Advertising',
                    'payment_id': payment_id,
                    'version': '3.0'
                }),
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False
            )
            
            return {
                'success': True,
                'payment_id': payment_id,
                'invoice_message_id': invoice_message.message_id,
                'stars_amount': stars_amount,
                'usd_amount': usd_amount
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create Stars invoice: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def handle_pre_checkout(self, pre_checkout_query: PreCheckoutQuery) -> bool:
        """Handle pre-checkout validation"""
        try:
            payload_data = json.loads(pre_checkout_query.invoice_payload)
            payment_id = payload_data.get('payment_id')
            
            if payment_id and payment_id in self.pending_payments:
                logger.info(f"✅ Pre-checkout approved for payment {payment_id}")
                await pre_checkout_query.answer(ok=True)
                return True
            else:
                logger.warning(f"❌ Pre-checkout rejected: payment {payment_id} not found")
                await pre_checkout_query.answer(ok=False, error_message="Payment not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Pre-checkout error: {e}")
            await pre_checkout_query.answer(ok=False, error_message="Validation failed")
            return False
    
    async def handle_successful_payment(self, message: Message) -> Dict:
        """Handle successful Stars payment and create campaign"""
        try:
            successful_payment = message.successful_payment
            payload_data = json.loads(successful_payment.invoice_payload)
            payment_id = payload_data.get('payment_id')
            user_id = message.from_user.id
            
            logger.info(f"🎉 Stars payment successful: {payment_id}")
            logger.info(f"   Amount: {successful_payment.total_amount} ⭐")
            logger.info(f"   Charge ID: {successful_payment.telegram_payment_charge_id}")
            
            # Get pending payment data
            payment_data = self.pending_payments.get(payment_id)
            if not payment_data:
                raise Exception(f"Payment data not found for {payment_id}")
            
            # Extract campaign and pricing data
            campaign_data = payment_data['campaign_data']
            pricing_data = payment_data['pricing_data']
            
            # Create campaign in database
            campaign_id = await self.create_campaign_from_payment(
                user_id, payment_id, campaign_data, pricing_data, successful_payment
            )
            
            # Send receipt to user
            await self.send_payment_receipt(
                message, payment_id, campaign_id, payment_data
            )
            
            # Mark payment as completed
            if payment_id in self.pending_payments:
                self.pending_payments[payment_id]['status'] = 'completed'
                self.pending_payments[payment_id]['campaign_id'] = campaign_id
                self.pending_payments[payment_id]['completed_at'] = datetime.now().isoformat()
            
            return {
                'success': True,
                'payment_id': payment_id,
                'campaign_id': campaign_id,
                'receipt_sent': True
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing Stars payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_campaign_from_payment(self, user_id: int, payment_id: str, 
                                         campaign_data: Dict, pricing_data: Dict, 
                                         successful_payment: SuccessfulPayment) -> str:
        """Create campaign record from successful payment"""
        try:
            if not self.db:
                raise Exception("Database not available")
            
            # Extract campaign details
            days = campaign_data.get('duration', 1)
            channels = campaign_data.get('selected_channels', [])
            posts_per_day = campaign_data.get('posts_per_day', 1)
            ad_content = campaign_data.get('ad_content', '')
            photos = campaign_data.get('photos', [])
            
            # Create ad record
            ad_id = await self.db.create_ad(
                user_id=user_id,
                content=ad_content,
                media_url=photos[0] if photos else None,
                content_type='photo' if photos else 'text'
            )
            
            # Create payment record
            db_payment_id = await self.db.create_payment(
                user_id=user_id,
                subscription_id=None,  # Will link after subscription creation
                amount=pricing_data.get('total_stars', 0),
                currency='STARS',
                payment_method='telegram_stars',
                memo=payment_id
            )
            
            # Create subscriptions for each channel
            subscription_ids = []
            for channel_id in channels:
                subscription_id = await self.db.create_subscription(
                    user_id=user_id,
                    ad_id=ad_id,
                    channel_id=channel_id,
                    duration_months=days,  # Using days as duration
                    total_price=pricing_data.get('total_stars', 0),
                    currency='STARS',
                    posts_per_day=posts_per_day,
                    total_posts=days * posts_per_day
                )
                subscription_ids.append(subscription_id)
            
            # Activate subscriptions
            if subscription_ids:
                await self.db.activate_subscriptions(subscription_ids, days)
                
                # Link payment to first subscription
                await self.db.update_payment_subscription(db_payment_id, subscription_ids[0])
            
            logger.info(f"✅ Campaign created: Ad ID {ad_id}, Payment ID {payment_id}")
            logger.info(f"   Subscriptions: {len(subscription_ids)} created and activated")
            
            return f"CAM-{payment_id}"
            
        except Exception as e:
            logger.error(f"❌ Error creating campaign from payment: {e}")
            raise
    
    async def send_payment_receipt(self, message: Message, payment_id: str, 
                                 campaign_id: str, payment_data: Dict):
        """Send payment receipt to user"""
        try:
            user_id = message.from_user.id
            
            # Get user language
            from handlers import get_user_language
            language = await get_user_language(user_id)
            
            # Extract data
            stars_amount = payment_data['stars_amount']
            usd_amount = payment_data['usd_amount']
            campaign_data = payment_data['campaign_data']
            
            days = campaign_data.get('duration', 1)
            channels = campaign_data.get('selected_channels', [])
            posts_per_day = campaign_data.get('posts_per_day', 1)
            
            # Create receipt message
            if language == 'ar':
                receipt_text = f"""🧾 إيصال الدفع
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ تم استلام الدفع!

طريقة الدفع: ⭐ نجوم تيليجرام
المبلغ المدفوع: {stars_amount} STARS
تاريخ الدفع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
رقم الدفع: {payment_id}

تفاصيل الإعلان:
• القنوات المختارة: {len(channels)} قنوات
• مدة الحملة: {days} أيام
• منشورات يومية: {posts_per_day}
• إجمالي المنشورات: {days * posts_per_day}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

شكراً لاستخدام بوت I3lani!
للدعم: /support"""
            elif language == 'ru':
                receipt_text = f"""🧾 Квитанция об оплате
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Платеж получен!

Способ оплаты: ⭐ Telegram Stars
Сумма платежа: {stars_amount} STARS
Дата платежа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
ID платежа: {payment_id}

Детали объявления:
• Выбранные каналы: {len(channels)} каналов
• Длительность кампании: {days} дней
• Посты в день: {posts_per_day}
• Всего постов: {days * posts_per_day}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Спасибо за использование I3lani Bot!
Поддержка: /support"""
            else:
                receipt_text = f"""🧾 Payment Receipt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Payment Received!

Payment Method: ⭐ Telegram Stars
Amount Paid: {stars_amount} STARS
Payment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Payment ID: {payment_id}

Campaign Details:
• Selected Channels: {len(channels)} channels
• Campaign Duration: {days} days
• Daily Posts: {posts_per_day}
• Total Posts: {days * posts_per_day}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for using I3lani Bot!
Support: /support"""
            
            # Create navigation keyboard
            if language == 'ar':
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 حملاتي", callback_data="my_campaigns")],
                    [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")]
                ])
            elif language == 'ru':
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 Мои кампании", callback_data="my_campaigns")],
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📊 My Campaigns", callback_data="my_campaigns")],
                    [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
                ])
            
            await message.answer(receipt_text, reply_markup=keyboard, parse_mode='Markdown')
            logger.info(f"✅ Payment receipt sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending payment receipt: {e}")

# Global instance
_clean_stars_payment = None

def get_clean_stars_payment(bot: Bot, db_instance=None) -> CleanStarsPayment:
    """Get global clean Stars payment instance"""
    global _clean_stars_payment
    if _clean_stars_payment is None:
        _clean_stars_payment = CleanStarsPayment(bot, db_instance)
    return _clean_stars_payment

async def handle_clean_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> Dict:
    """Handle pre-checkout using clean system"""
    stars_payment = get_clean_stars_payment(pre_checkout_query.bot)
    success = await stars_payment.handle_pre_checkout(pre_checkout_query)
    return {'success': success}

async def handle_clean_successful_payment(message: Message) -> Dict:
    """Handle successful payment using clean system"""
    from database import db
    stars_payment = get_clean_stars_payment(message.bot, db)
    return await stars_payment.handle_successful_payment(message)