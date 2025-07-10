#!/usr/bin/env python3
"""
Enhanced Telegram Stars Payment System
Based on official Telegram Bot API: https://core.telegram.org/bots/api#payments
Implements comprehensive Stars payment with advanced features
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    PreCheckoutQuery, Message, CallbackQuery,
    LabeledPrice, SuccessfulPayment
)
from aiogram.exceptions import TelegramAPIError

logger = logging.getLogger(__name__)

class EnhancedStarsPayment:
    """Enhanced Telegram Stars payment system with full API compliance"""
    
    def __init__(self, bot: Bot, db_instance=None):
        self.bot = bot
        self.db = db_instance
        
        # Stars payment configuration
        self.currency = "XTR"  # Telegram Stars currency code
        self.provider_token = ""  # Empty for Stars payments
        self.max_tip_amount = 0  # No tips for advertising campaigns
        
        # Enhanced payment metadata
        self.payment_metadata = {
            "service": "I3lani_Advertising",
            "version": "2.0",
            "api_compliance": "telegram_bot_api_7.0"
        }
    
    async def create_enhanced_invoice(self, user_id: int, campaign_data: Dict, 
                                    pricing_data: Dict, language: str = 'en') -> Dict:
        """Create enhanced Stars invoice with full API compliance"""
        
        try:
            # Generate unique payment identifier
            payment_id = self._generate_payment_id()
            
            # Create comprehensive invoice description
            invoice_data = self._build_invoice_data(campaign_data, pricing_data, payment_id, language)
            
            # Enhanced payload with metadata
            enhanced_payload = self._create_enhanced_payload(user_id, payment_id, campaign_data)
            
            # Create price breakdown
            price_breakdown = self._create_price_breakdown(pricing_data)
            
            logger.info(f"💫 Creating enhanced Stars invoice for user {user_id}")
            logger.info(f"   Payment ID: {payment_id}")
            logger.info(f"   Amount: {pricing_data.get('total_stars', 0)} ⭐")
            logger.info(f"   Campaign: {campaign_data.get('duration', 'N/A')} days")
            
            # Send enhanced invoice with full API parameters
            invoice_message = await self.bot.send_invoice(
                chat_id=user_id,
                title=invoice_data['title'],
                description=invoice_data['description'],
                payload=enhanced_payload,
                provider_token=self.provider_token,
                currency=self.currency,
                prices=price_breakdown,
                max_tip_amount=self.max_tip_amount,
                suggested_tip_amounts=[],
                start_parameter=f"stars_payment_{payment_id}",
                provider_data=json.dumps(self.payment_metadata),
                photo_url=None,  # Optional: Add campaign preview
                photo_size=None,
                photo_width=None,
                photo_height=None,
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False,
                disable_notification=False,
                protect_content=False,
                reply_markup=self._create_payment_keyboard(payment_id, language)
            )
            
            # Store payment tracking
            await self._store_payment_tracking(user_id, payment_id, campaign_data, pricing_data)
            
            return {
                'success': True,
                'payment_id': payment_id,
                'invoice_message_id': invoice_message.message_id,
                'amount_stars': pricing_data.get('total_stars', 0),
                'amount_usd': pricing_data.get('total_usd', 0.0)
            }
            
        except TelegramAPIError as e:
            logger.error(f"❌ Telegram API error creating Stars invoice: {e}")
            return {'success': False, 'error': f"Telegram API error: {e}"}
        except Exception as e:
            logger.error(f"❌ Error creating enhanced Stars invoice: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_payment_id(self) -> str:
        """Generate unique payment ID for Stars payments"""
        import random
        import string
        timestamp = int(datetime.now().timestamp())
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"STAR{timestamp}{random_part}"
    
    def _build_invoice_data(self, campaign_data: Dict, pricing_data: Dict, 
                           payment_id: str, language: str) -> Dict:
        """Build comprehensive invoice title and description"""
        
        duration = campaign_data.get('duration', 7)
        posts_per_day = pricing_data.get('posts_per_day', 1)
        channels = campaign_data.get('selected_channels', [])
        discount = pricing_data.get('discount_percent', 0)
        
        # Multilingual titles and descriptions
        if language == 'ar':
            title = f"🌟 حملة إعلانية I3lani - {duration} أيام"
            description = (f"📢 حملة إعلانية احترافية\n"
                         f"⏱️ المدة: {duration} أيام\n"
                         f"📝 المشاركات: {posts_per_day} يومياً\n"
                         f"📺 القنوات: {len(channels)} قناة\n"
                         f"💎 الوصول: {sum(ch.get('subscribers', 0) for ch in channels):,} متابع")
            if discount > 0:
                description += f"\n🎁 خصم: {discount}%"
        elif language == 'ru':
            title = f"🌟 Рекламная кампания I3lani - {duration} дней"
            description = (f"📢 Профессиональная рекламная кампания\n"
                         f"⏱️ Продолжительность: {duration} дней\n"
                         f"📝 Посты: {posts_per_day} в день\n"
                         f"📺 Каналы: {len(channels)} каналов\n"
                         f"💎 Охват: {sum(ch.get('subscribers', 0) for ch in channels):,} подписчиков")
            if discount > 0:
                description += f"\n🎁 Скидка: {discount}%"
        else:  # English default
            title = f"🌟 I3lani Advertising Campaign - {duration} days"
            description = (f"📢 Professional advertising campaign\n"
                         f"⏱️ Duration: {duration} days\n"
                         f"📝 Posts: {posts_per_day} per day\n"
                         f"📺 Channels: {len(channels)} channels\n"
                         f"💎 Reach: {sum(ch.get('subscribers', 0) for ch in channels):,} subscribers")
            if discount > 0:
                description += f"\n🎁 Discount: {discount}%"
        
        description += f"\n\n🆔 Payment ID: {payment_id}"
        
        return {
            'title': title,
            'description': description
        }
    
    def _create_enhanced_payload(self, user_id: int, payment_id: str, campaign_data: Dict) -> str:
        """Create enhanced payload with campaign metadata"""
        
        payload_data = {
            'payment_id': payment_id,
            'user_id': user_id,
            'campaign_type': 'advertising',
            'service': 'i3lani_bot',
            'timestamp': int(datetime.now().timestamp()),
            'channels': [ch.get('id', ch.get('name', '')) for ch in campaign_data.get('selected_channels', [])],
            'duration': campaign_data.get('duration', 7),
            'version': '2.0'
        }
        
        return json.dumps(payload_data)
    
    def _create_price_breakdown(self, pricing_data: Dict) -> List[LabeledPrice]:
        """Create detailed price breakdown for Stars payment"""
        
        prices = []
        
        # Base campaign price
        base_amount = int(pricing_data.get('total_stars', 0))
        prices.append(LabeledPrice(label="Campaign Base Price", amount=base_amount))
        
        # Discount if applicable
        discount_percent = pricing_data.get('discount_percent', 0)
        if discount_percent > 0:
            discount_amount = int(base_amount * discount_percent / 100)
            prices.append(LabeledPrice(label=f"Volume Discount ({discount_percent}%)", amount=-discount_amount))
        
        return prices
    
    def _create_payment_keyboard(self, payment_id: str, language: str) -> InlineKeyboardMarkup:
        """Create enhanced payment keyboard with additional options"""
        
        # Multilingual button text
        if language == 'ar':
            pay_button = "💫 ادفع بالنجوم"
            cancel_button = "❌ إلغاء"
            help_button = "❓ مساعدة"
        elif language == 'ru':
            pay_button = "💫 Оплатить звёздами"
            cancel_button = "❌ Отмена"
            help_button = "❓ Помощь"
        else:
            pay_button = "💫 Pay with Stars"
            cancel_button = "❌ Cancel"
            help_button = "❓ Help"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=pay_button, pay=True)],
            [
                InlineKeyboardButton(text=help_button, callback_data=f"stars_help_{payment_id}"),
                InlineKeyboardButton(text=cancel_button, callback_data=f"stars_cancel_{payment_id}")
            ]
        ])
        
        return keyboard
    
    async def _store_payment_tracking(self, user_id: int, payment_id: str, 
                                    campaign_data: Dict, pricing_data: Dict):
        """Store enhanced payment tracking data"""
        
        try:
            if not self.db:
                logger.warning("No database instance available for payment tracking")
                return
            
            import aiosqlite
            async with aiosqlite.connect(self.db.db_path) as conn:
                await conn.execute('''
                    INSERT OR REPLACE INTO payment_memo_tracking 
                    (memo, user_id, currency, amount, created_at, status, metadata, payment_type)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 'pending', ?, 'stars')
                ''', (
                    payment_id,
                    user_id, 
                    'XTR',
                    pricing_data.get('total_stars', 0),
                    json.dumps({
                        'campaign_data': campaign_data,
                        'pricing_data': pricing_data,
                        'payment_method': 'telegram_stars',
                        'api_version': '2.0'
                    })
                ))
                await conn.commit()
                
            logger.info(f"✅ Stored Stars payment tracking for {payment_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing payment tracking: {e}")
    
    async def handle_pre_checkout_query(self, pre_checkout_query: PreCheckoutQuery) -> Dict:
        """Enhanced pre-checkout validation with comprehensive checks"""
        
        try:
            # Parse enhanced payload
            payload_data = json.loads(pre_checkout_query.invoice_payload)
            payment_id = payload_data.get('payment_id')
            user_id = payload_data.get('user_id')
            
            logger.info(f"🔍 Pre-checkout validation for payment {payment_id}")
            
            # Comprehensive validation checks
            validation_result = await self._validate_pre_checkout(
                pre_checkout_query, payload_data
            )
            
            if validation_result['valid']:
                # Answer pre-checkout query successfully
                await pre_checkout_query.answer(ok=True)
                
                logger.info(f"✅ Pre-checkout approved for {payment_id}")
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'amount': pre_checkout_query.total_amount
                }
            else:
                # Answer with error message
                await pre_checkout_query.answer(
                    ok=False, 
                    error_message=validation_result['error']
                )
                
                logger.warning(f"❌ Pre-checkout rejected for {payment_id}: {validation_result['error']}")
                return {
                    'success': False,
                    'error': validation_result['error']
                }
                
        except Exception as e:
            error_msg = f"Payment validation failed: {str(e)}"
            await pre_checkout_query.answer(ok=False, error_message=error_msg)
            logger.error(f"❌ Pre-checkout error: {e}")
            return {'success': False, 'error': error_msg}
    
    async def _validate_pre_checkout(self, pre_checkout_query: PreCheckoutQuery, 
                                   payload_data: Dict) -> Dict:
        """Comprehensive pre-checkout validation"""
        
        try:
            # Basic payload validation
            required_fields = ['payment_id', 'user_id', 'campaign_type']
            for field in required_fields:
                if field not in payload_data:
                    return {'valid': False, 'error': f"Missing {field} in payment data"}
            
            # User ID validation
            if payload_data['user_id'] != pre_checkout_query.from_user.id:
                return {'valid': False, 'error': "User ID mismatch"}
            
            # Currency validation
            if pre_checkout_query.currency != "XTR":
                return {'valid': False, 'error': "Invalid currency for Stars payment"}
            
            # Amount validation (minimum 1 Star)
            if pre_checkout_query.total_amount < 1:
                return {'valid': False, 'error': "Invalid payment amount"}
            
            # Check if payment is still pending
            if self.db:
                import aiosqlite
                async with aiosqlite.connect(self.db.db_path) as conn:
                    async with conn.execute(
                        'SELECT status FROM payment_memo_tracking WHERE memo = ?',
                        (payload_data['payment_id'],)
                    ) as cursor:
                        result = await cursor.fetchone()
                        if not result:
                            return {'valid': False, 'error': "Payment not found"}
                        if result[0] != 'pending':
                            return {'valid': False, 'error': "Payment already processed"}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': f"Validation error: {str(e)}"}
    
    async def handle_successful_payment(self, message: Message) -> Dict:
        """Enhanced successful payment processing with comprehensive features"""
        
        try:
            successful_payment = message.successful_payment
            
            # Parse payment data
            payload_data = json.loads(successful_payment.invoice_payload)
            payment_id = payload_data.get('payment_id')
            user_id = message.from_user.id
            
            logger.info(f"💫 Processing successful Stars payment {payment_id}")
            logger.info(f"   User: {user_id}")
            logger.info(f"   Amount: {successful_payment.total_amount} ⭐")
            logger.info(f"   Currency: {successful_payment.currency}")
            logger.info(f"   Telegram Payment ID: {successful_payment.telegram_payment_charge_id}")
            
            # Update payment status
            await self._update_payment_status(payment_id, successful_payment)
            
            # Create campaign from payment
            campaign_result = await self._create_campaign_from_payment(payment_id, payload_data)
            
            # Send enhanced receipt
            receipt_result = await self._send_enhanced_receipt(
                user_id, payment_id, successful_payment, campaign_result
            )
            
            # Activate advertising campaign
            if campaign_result.get('success'):
                await self._activate_advertising_campaign(campaign_result['campaign_id'])
            
            logger.info(f"✅ Stars payment {payment_id} processed successfully")
            
            return {
                'success': True,
                'payment_id': payment_id,
                'campaign_id': campaign_result.get('campaign_id'),
                'receipt_sent': receipt_result.get('success', False)
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing successful Stars payment: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _update_payment_status(self, payment_id: str, successful_payment: SuccessfulPayment):
        """Update payment status with Telegram payment details"""
        
        try:
            if not self.db:
                return
            
            import aiosqlite
            async with aiosqlite.connect(self.db.db_path) as conn:
                await conn.execute('''
                    UPDATE payment_memo_tracking 
                    SET status = 'confirmed',
                        confirmed_at = CURRENT_TIMESTAMP,
                        telegram_payment_id = ?,
                        provider_payment_id = ?
                    WHERE memo = ?
                ''', (
                    successful_payment.telegram_payment_charge_id,
                    successful_payment.provider_payment_charge_id,
                    payment_id
                ))
                await conn.commit()
                
            logger.info(f"✅ Updated payment status for {payment_id}")
            
        except Exception as e:
            logger.error(f"❌ Error updating payment status: {e}")
    
    async def _create_campaign_from_payment(self, payment_id: str, payload_data: Dict) -> Dict:
        """Create advertising campaign from successful payment"""
        
        try:
            # Get payment tracking data
            if not self.db:
                return {'success': False, 'error': 'No database connection'}
            
            import aiosqlite
            async with aiosqlite.connect(self.db.db_path) as conn:
                async with conn.execute(
                    'SELECT user_id, metadata FROM payment_memo_tracking WHERE memo = ?',
                    (payment_id,)
                ) as cursor:
                    result = await cursor.fetchone()
                    if not result:
                        return {'success': False, 'error': 'Payment data not found'}
                    
                    user_id, metadata_json = result
                    metadata = json.loads(metadata_json)
                    
            # Use campaign management system
            from campaign_management import CampaignManager
            campaign_manager = CampaignManager()
            
            campaign_id = await campaign_manager.create_campaign_for_payment(
                user_id=user_id,
                payment_id=payment_id,
                payment_method='telegram_stars',
                campaign_data=metadata.get('campaign_data', {}),
                pricing_data=metadata.get('pricing_data', {})
            )
            
            return {
                'success': True,
                'campaign_id': campaign_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating campaign from payment: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _send_enhanced_receipt(self, user_id: int, payment_id: str, 
                                   successful_payment: SuccessfulPayment, 
                                   campaign_result: Dict) -> Dict:
        """Send enhanced payment receipt with campaign details"""
        
        try:
            # Get user language
            language = 'en'  # Default, should get from database
            if self.db:
                import aiosqlite
                async with aiosqlite.connect(self.db.db_path) as conn:
                    async with conn.execute(
                        'SELECT language FROM users WHERE user_id = ?',
                        (user_id,)
                    ) as cursor:
                        result = await cursor.fetchone()
                        if result:
                            language = result[0]
            
            # Create multilingual receipt
            receipt_text = self._create_receipt_text(
                payment_id, successful_payment, campaign_result, language
            )
            
            # Send receipt with enhanced keyboard
            receipt_keyboard = self._create_receipt_keyboard(
                campaign_result.get('campaign_id'), language
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=receipt_text,
                parse_mode='HTML',
                reply_markup=receipt_keyboard
            )
            
            logger.info(f"✅ Enhanced receipt sent to user {user_id}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"❌ Error sending enhanced receipt: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_receipt_text(self, payment_id: str, successful_payment: SuccessfulPayment,
                           campaign_result: Dict, language: str) -> str:
        """Create multilingual receipt text"""
        
        if language == 'ar':
            receipt = f"""✅ <b>تم الدفع بنجاح!</b>

💫 <b>تفاصيل الدفع:</b>
🆔 رقم الدفع: <code>{payment_id}</code>
⭐ المبلغ: {successful_payment.total_amount} نجمة
💱 العملة: {successful_payment.currency}
🔗 معرف تليجرام: <code>{successful_payment.telegram_payment_charge_id}</code>

📢 <b>تفاصيل الحملة:</b>"""
        elif language == 'ru':
            receipt = f"""✅ <b>Оплата прошла успешно!</b>

💫 <b>Детали платежа:</b>
🆔 ID платежа: <code>{payment_id}</code>
⭐ Сумма: {successful_payment.total_amount} звёзд
💱 Валюта: {successful_payment.currency}
🔗 ID Telegram: <code>{successful_payment.telegram_payment_charge_id}</code>

📢 <b>Детали кампании:</b>"""
        else:
            receipt = f"""✅ <b>Payment Successful!</b>

💫 <b>Payment Details:</b>
🆔 Payment ID: <code>{payment_id}</code>
⭐ Amount: {successful_payment.total_amount} Stars
💱 Currency: {successful_payment.currency}
🔗 Telegram ID: <code>{successful_payment.telegram_payment_charge_id}</code>

📢 <b>Campaign Details:</b>"""
        
        if campaign_result.get('success'):
            campaign_id = campaign_result.get('campaign_id')
            if language == 'ar':
                receipt += f"\n🎯 معرف الحملة: <code>{campaign_id}</code>\n✅ الحملة جاهزة للنشر"
            elif language == 'ru':
                receipt += f"\n🎯 ID кампании: <code>{campaign_id}</code>\n✅ Кампания готова к публикации"
            else:
                receipt += f"\n🎯 Campaign ID: <code>{campaign_id}</code>\n✅ Campaign ready for publishing"
        
        return receipt
    
    def _create_receipt_keyboard(self, campaign_id: str, language: str) -> InlineKeyboardMarkup:
        """Create receipt keyboard with campaign actions"""
        
        if language == 'ar':
            view_campaign = "👁️ عرض الحملة"
            support = "🆘 الدعم"
        elif language == 'ru':
            view_campaign = "👁️ Просмотр кампании"
            support = "🆘 Поддержка"
        else:
            view_campaign = "👁️ View Campaign"
            support = "🆘 Support"
        
        buttons = []
        if campaign_id:
            buttons.append([InlineKeyboardButton(text=view_campaign, 
                                               callback_data=f"view_campaign_{campaign_id}")])
        
        buttons.append([InlineKeyboardButton(text=support, 
                                           callback_data="contact_support")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    async def _activate_advertising_campaign(self, campaign_id: str):
        """Activate the advertising campaign for publishing"""
        
        try:
            # Use automatic publishing system
            from automatic_publishing_solution import automatic_publishing_manager
            
            if automatic_publishing_manager:
                await automatic_publishing_manager.schedule_campaign_immediately(campaign_id)
                logger.info(f"✅ Campaign {campaign_id} activated for publishing")
            else:
                logger.warning(f"⚠️ Automatic publishing manager not available")
                
        except Exception as e:
            logger.error(f"❌ Error activating campaign {campaign_id}: {e}")

# Global instance for use in handlers
enhanced_stars_payment = None

def get_enhanced_stars_payment(bot_instance, db_instance=None):
    """Get or create enhanced Stars payment instance"""
    global enhanced_stars_payment
    if enhanced_stars_payment is None:
        enhanced_stars_payment = EnhancedStarsPayment(bot_instance, db_instance)
    return enhanced_stars_payment

# Handler integration functions
async def create_enhanced_stars_invoice(user_id: int, campaign_data: Dict, 
                                      pricing_data: Dict, language: str = 'en') -> Dict:
    """Create enhanced Stars invoice (for use in handlers)"""
    if enhanced_stars_payment:
        return await enhanced_stars_payment.create_enhanced_invoice(
            user_id, campaign_data, pricing_data, language
        )
    return {'success': False, 'error': 'Payment system not initialized'}

async def handle_enhanced_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> Dict:
    """Handle enhanced pre-checkout validation (for use in handlers)"""
    if enhanced_stars_payment:
        return await enhanced_stars_payment.handle_pre_checkout_query(pre_checkout_query)
    return {'success': False, 'error': 'Payment system not initialized'}

async def handle_enhanced_successful_payment(message: Message) -> Dict:
    """Handle enhanced successful payment (for use in handlers)"""
    if enhanced_stars_payment:
        return await enhanced_stars_payment.handle_successful_payment(message)
    return {'success': False, 'error': 'Payment system not initialized'}