#!/usr/bin/env python3
"""
Clean Telegram Stars Payment System with Global Sequence Integration
Simple, effective, traceable payment system using unified sequence tracking
"""

import logging
from automatic_language_system import get_user_language_auto
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

# Import global sequence system
from global_sequence_system import (
    get_global_sequence_manager, start_user_global_sequence,
    log_sequence_step, link_to_global_sequence
)
from sequence_logger import get_sequence_logger

logger = get_sequence_logger(__name__)

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
    
    def generate_payment_id(self, user_id: int) -> str:
        """Generate unique payment ID using global sequence system"""
        manager = get_global_sequence_manager()
        sequence_id = manager.get_user_active_sequence(user_id)
        
        if sequence_id:
            # Use sequence ID as primary payment identifier
            payment_ref = f"STARS-{sequence_id.split('-')[2]}-{sequence_id.split('-')[3]}"
            
            # Log payment generation step
            log_sequence_step(sequence_id, "Payment_Step_1_GenerateStarsID", "clean_stars_payment", {
                "payment_type": "telegram_stars",
                "payment_ref": payment_ref,
                "user_id": user_id
            })
            
            return payment_ref
        else:
            # Fallback to timestamp-based ID if no sequence found
            timestamp = int(time.time())
            return f"STARS-FALLBACK-{timestamp}"
    
    async def create_post_package_invoice(self, user_id: int, campaign_data: Dict, 
                                         pricing_data: Dict, language: str = 'en') -> Dict:
        """Create Telegram Stars invoice for post package purchase"""
        
        try:
            # Get user's active sequence
            manager = get_global_sequence_manager()
            sequence_id = manager.get_user_active_sequence(user_id)
            
            if not sequence_id:
                # Start new sequence for post package purchase
                sequence_id = start_user_global_sequence(user_id, "post_package_purchase")
            
            # Generate payment ID
            payment_id = self.generate_payment_id(user_id)
            
            # Calculate Stars amount
            stars_amount = int(pricing_data.get('cost_stars', 0))
            
            if stars_amount <= 0:
                return {
                    'success': False,
                    'error': 'Invalid Stars amount'
                }
            
            # Create invoice description
            package_name = campaign_data.get('package_name', 'Post Package')
            posts_count = campaign_data.get('posts_total', 0)
            
            if language == 'ar':
                description = f"حزمة {package_name} - {posts_count} منشور"
                title = f"حزمة المنشورات - {package_name}"
            elif language == 'ru':
                description = f"Пакет {package_name} - {posts_count} постов"
                title = f"Пакет постов - {package_name}"
            else:
                description = f"{package_name} Package - {posts_count} posts"
                title = f"Post Package - {package_name}"
            
            # Create price label
            price_label = LabeledPrice(
                label=title,
                amount=stars_amount
            )
            
            # Store payment data
            payment_data = {
                'payment_id': payment_id,
                'user_id': user_id,
                'sequence_id': sequence_id,
                'amount_stars': stars_amount,
                'amount_usd': pricing_data.get('total_usd', 0),
                'package_name': package_name,
                'posts_total': posts_count,
                'auto_schedule_days': campaign_data.get('auto_schedule_days', 0),
                'selected_addons': campaign_data.get('selected_addons', []),
                'timestamp': datetime.now().isoformat(),
                'type': 'post_package'
            }
            
            self.pending_payments[payment_id] = payment_data
            
            # Log payment creation step
            log_sequence_step(sequence_id, "Payment_Step_2_CreatePostPackageInvoice", "clean_stars_payment", {
                "payment_id": payment_id,
                "stars_amount": stars_amount,
                "package_name": package_name,
                "posts_total": posts_count
            })
            
            # Create invoice
            invoice_link = await self.bot.create_invoice_link(
                title=title,
                description=description,
                payload=payment_id,
                provider_token=self.provider_token,
                currency=self.currency,
                prices=[price_label]
            )
            
            # Create invoice message
            if language == 'ar':
                invoice_message = f"""💎 **فاتورة دفع حزمة المنشورات**

📦 **الحزمة:** {package_name}
📊 **المنشورات:** {posts_count}
⭐ **السعر:** {stars_amount} نجمة

💳 **معرف الدفع:** `{payment_id}`

اضغط على الزر أدناه لإتمام الدفع بنجوم تيليغرام:"""
            elif language == 'ru':
                invoice_message = f"""💎 **Счет на пакет постов**

📦 **Пакет:** {package_name}
📊 **Постов:** {posts_count}
⭐ **Цена:** {stars_amount} звезд

💳 **ID платежа:** `{payment_id}`

Нажмите кнопку ниже для оплаты звездами Telegram:"""
            else:
                invoice_message = f"""💎 **Post Package Invoice**

📦 **Package:** {package_name}
📊 **Posts:** {posts_count}
⭐ **Price:** {stars_amount} Stars

💳 **Payment ID:** `{payment_id}`

Click the button below to pay with Telegram Stars:"""
            
            # Create keyboard
            pay_button_text = "⭐ دفع بالنجوم" if language == 'ar' else "⭐ Оплатить звездами" if language == 'ru' else "⭐ Pay with Stars"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=pay_button_text, url=invoice_link)]
            ])
            
            return {
                'success': True,
                'invoice_link': invoice_link,
                'invoice_message': invoice_message,
                'invoice_keyboard': keyboard,
                'payment_id': payment_id
            }
            
        except Exception as e:
            logger.error(f"Failed to create post package invoice: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_payment_invoice(self, user_id: int, campaign_data: Dict, 
                                   pricing_data: Dict, language: str = 'en') -> Dict:
        """Create Telegram Stars invoice with global sequence integration"""
        
        try:
            # Get user's active sequence
            manager = get_global_sequence_manager()
            sequence_id = manager.get_user_active_sequence(user_id)
            
            # Generate payment ID using sequence system
            payment_id = self.generate_payment_id(user_id)
            
            # Log invoice creation step
            if sequence_id:
                log_sequence_step(sequence_id, "Payment_Step_2_CreateStarsInvoice", "clean_stars_payment", {
                    "payment_id": payment_id,
                    "stars_amount": pricing_data.get('total_stars', 0),
                    "usd_amount": pricing_data.get('total_usd', 0),
                    "language": language
                })
            
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
            
            # Create minimal payload with sequence tracking
            payload = json.dumps({
                'payment_id': payment_id,
                'sequence_id': sequence_id,
                'user_id': user_id,
                'service': 'i3lani_ads',
                'amount': stars_amount
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
                provider_data=None,
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
        """Handle successful Stars payment and create campaign or process post package"""
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
            
            # Check if this is a post package purchase
            if payment_data.get('type') == 'post_package':
                return await self.handle_post_package_payment(message, payment_id, payment_data)
            else:
                # Handle regular campaign payment
                return await self.handle_campaign_payment(message, payment_id, payment_data)
            
        except Exception as e:
            logger.error(f"❌ Error processing Stars payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def handle_post_package_payment(self, message: Message, payment_id: str, payment_data: Dict) -> Dict:
        """Handle successful post package purchase"""
        try:
            successful_payment = message.successful_payment
            user_id = message.from_user.id
            
            # Extract package data
            package_data = {
                'package_name': payment_data.get('package_name'),
                'posts_total': payment_data.get('posts_total'),
                'auto_schedule_days': payment_data.get('auto_schedule_days', 0),
                'selected_addons': payment_data.get('selected_addons', [])
            }
            
            # Send confirmation using automatic payment confirmation system
            from automatic_payment_confirmation import AutomaticPaymentConfirmation
            confirmation_system = AutomaticPaymentConfirmation()
            
            confirmation_sent = await confirmation_system.send_post_package_confirmation(
                user_id=user_id,
                memo=payment_id,
                amount=successful_payment.total_amount,
                package_data=package_data
            )
            
            # Mark payment as completed
            if payment_id in self.pending_payments:
                self.pending_payments[payment_id]['status'] = 'completed'
                self.pending_payments[payment_id]['completed_at'] = datetime.now().isoformat()
            
            return {
                'success': True,
                'payment_id': payment_id,
                'type': 'post_package',
                'confirmation_sent': confirmation_sent
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing post package payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def handle_campaign_payment(self, message: Message, payment_id: str, payment_data: Dict) -> Dict:
        """Handle successful campaign payment"""
        try:
            successful_payment = message.successful_payment
            user_id = message.from_user.id
            
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
            logger.error(f"❌ Error processing campaign payment: {e}")
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
            
            campaign_id = f"CAM-{payment_id}"
            
            # CRITICAL: Execute comprehensive publishing workflow
            try:
                from comprehensive_publishing_workflow import execute_post_payment_publishing
                
                publishing_result = await execute_post_payment_publishing(self.bot, campaign_id)
                
                logger.info(f"✅ Stars publishing workflow executed: {publishing_result.get_success_rate():.1f}% success rate")
                
                if publishing_result.is_complete_success():
                    logger.info(f"🎉 Stars campaign {campaign_id} successfully published to all channels")
                else:
                    logger.warning(f"⚠️ Stars campaign {campaign_id} had publishing issues: {len(publishing_result.failed_channels)} failed channels")
                    
            except Exception as e:
                logger.error(f"❌ Error executing Stars publishing workflow for campaign {campaign_id}: {e}")
                # Don't fail the campaign creation if publishing fails
            
            return campaign_id
            
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
                receipt_text = f"""✅ تم تأكيد دفع نجوم تيليجرام!

تم التحقق من دفع نجوم تيليجرام الخاص بك!

💰 المبلغ المستلم: {stars_amount} STARS

📅 مدة الحملة: {days} أيام
📊 تكرار النشر: {posts_per_day} مرة يومياً
📺 القنوات: {len(channels)} قناة
📈 إجمالي المنشورات: {days * posts_per_day} منشور

رقم الحملة الإعلانية: {campaign_id}
🚀 حملتك الإعلانية تبدأ الآن!
🟢 الحالة: نشط

📱 ستتلقى إشعارات عند نشر إعلانك في كل قناة

🎯 شكراً لاختيار I3lani!"""
            elif language == 'ru':
                receipt_text = f"""✅ Оплата Telegram Stars подтверждена!

Ваш платеж Telegram Stars был проверен!

💰 Получено: {stars_amount} STARS

📅 Длительность кампании: {days} дней
📊 Частота публикации: {posts_per_day} раз в день
📺 Каналы: {len(channels)} канала
📈 Всего постов: {days * posts_per_day} постов

ID кампании: {campaign_id}
🚀 Ваша рекламная кампания начинается!
🟢 Статус: Активен

📱 Вы получите уведомления при публикации в каждом канале

🎯 Спасибо за выбор I3lani!"""
            else:
                receipt_text = f"""✅ Telegram Stars Payment Confirmed!

Your Telegram Stars payment has been verified!

💰 Amount Received: {stars_amount} STARS

📅 Campaign Duration: {days} days
📊 Publishing Frequency: {posts_per_day} times daily
📺 Channels: {len(channels)} channels
📈 Total Posts: {days * posts_per_day} posts

Campaign ID: {campaign_id}
🚀 Your advertising campaign starts now!
🟢 Status: Active

📱 You'll receive notifications when your ad is published in each channel

🎯 Thank you for choosing I3lani!"""
            
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