"""
Enhanced Telegram Stars Payment System for I3lani Bot
Phase 1 & Phase 2 Enhancements: Advanced validation, error handling, TON Connect integration
"""

import logging
import asyncio
import json
import time
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, 
    PreCheckoutQuery, Message, CallbackQuery,
    LabeledPrice, SuccessfulPayment
)
from aiogram.exceptions import TelegramAPIError

# Import existing systems
from clean_stars_payment_system import CleanStarsPayment
from global_sequence_system import (
    get_global_sequence_manager, start_user_global_sequence,
    log_sequence_step, link_to_global_sequence
)
from sequence_logger import get_sequence_logger

# Import enhanced components
from enhanced_payment_processor import (
    PaymentRequest, PaymentMethod, PaymentStatus, FraudDetector,
    TransactionValidator, PaymentErrorHandler
)
from payment_amount_validator import PaymentAmountValidator
from ton_connect_integration import get_ton_connect_integration

logger = get_sequence_logger(__name__)

class PaymentValidationLevel(Enum):
    BASIC = "basic"
    ENHANCED = "enhanced"
    STRICT = "strict"

@dataclass
class EnhancedPaymentResult:
    """Enhanced payment result with detailed information"""
    success: bool
    payment_id: str
    transaction_id: Optional[str]
    amount_paid: Optional[Decimal]
    validation_level: PaymentValidationLevel
    fraud_score: float
    error_message: Optional[str]
    recovery_options: List[str]
    processing_time: float
    metadata: Dict[str, Any]

class EnhancedStarsPaymentSystem:
    """
    Enhanced Telegram Stars Payment System
    Phase 1 & Phase 2 Enhancements Implementation
    """
    
    def __init__(self, bot: Bot, db_instance=None):
        self.bot = bot
        self.db = db_instance
        
        # Initialize existing system
        self.base_system = CleanStarsPayment(bot, db_instance)
        
        # Initialize enhanced components
        self.fraud_detector = FraudDetector()
        self.transaction_validator = TransactionValidator()
        self.error_handler = PaymentErrorHandler(bot)
        self.amount_validator = PaymentAmountValidator(bot)
        
        # Payment tracking with enhanced features
        self.pending_payments = {}
        self.payment_history = {}
        self.fraud_attempts = set()
        
        # Performance optimization
        self.payment_cache = {}
        self.api_call_cache = {}
        
        # TON Connect integration
        self.ton_connect = None
        
    async def initialize_ton_connect(self):
        """Initialize TON Connect integration"""
        try:
            manifest_url = "https://i3lani-bot.com/tonconnect-manifest.json"
            self.ton_connect = get_ton_connect_integration(self.bot, manifest_url)
            logger.info("✅ TON Connect integration initialized for Stars payments")
        except Exception as e:
            logger.error(f"❌ Failed to initialize TON Connect: {e}")
    
    async def create_enhanced_payment_request(self, user_id: int, campaign_data: Dict, 
                                            pricing_data: Dict, language: str = 'en',
                                            validation_level: PaymentValidationLevel = PaymentValidationLevel.ENHANCED) -> Dict:
        """
        Create enhanced payment request with comprehensive validation
        Phase 1 & Phase 2 Implementation
        """
        start_time = time.time()
        
        try:
            # Phase 1: Enhanced Validation
            validation_result = await self._perform_phase1_validation(user_id, campaign_data, pricing_data)
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'validation_level': validation_level.value,
                    'recovery_options': validation_result.get('recovery_options', [])
                }
            
            # Phase 1: Fraud Detection
            fraud_analysis = await self.fraud_detector.analyze_payment(
                PaymentRequest(
                    payment_id="temp",
                    user_id=user_id,
                    amount=Decimal(str(pricing_data.get('total_stars', 0))),
                    currency="XTR",
                    payment_method=PaymentMethod.TELEGRAM_STARS,
                    memo="",
                    recipient_address="",
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=20),
                    status=PaymentStatus.PENDING,
                    metadata=campaign_data
                )
            )
            
            if fraud_analysis['is_suspicious']:
                logger.warning(f"🚨 Suspicious Stars payment detected for user {user_id}")
                await self._handle_suspicious_payment(user_id, fraud_analysis)
                
                return {
                    'success': False,
                    'error': 'Payment blocked due to security concerns',
                    'fraud_score': fraud_analysis['risk_score'],
                    'recovery_options': ['contact_support', 'retry_later']
                }
            
            # Phase 2: TON Connect Enhancement (Optional)
            ton_connect_available = await self._check_ton_connect_availability(user_id)
            
            # Create enhanced invoice using base system
            invoice_result = await self.base_system.create_payment_invoice(
                user_id, campaign_data, pricing_data, language
            )
            
            if not invoice_result.get('success', False):
                # Phase 1: Enhanced Error Handling
                return await self._handle_invoice_creation_error(user_id, invoice_result, validation_level)
            
            # Phase 1: Performance Optimization - Cache result
            payment_id = invoice_result['payment_id']
            self.payment_cache[payment_id] = {
                'user_id': user_id,
                'campaign_data': campaign_data,
                'pricing_data': pricing_data,
                'created_at': datetime.now(),
                'fraud_score': fraud_analysis['risk_score'],
                'validation_level': validation_level.value
            }
            
            # Log enhanced payment creation
            processing_time = time.time() - start_time
            logger.info(f"✅ Enhanced Stars payment created: {payment_id}")
            logger.info(f"   User: {user_id}")
            logger.info(f"   Amount: {pricing_data.get('total_stars', 0)} ⭐")
            logger.info(f"   Fraud Score: {fraud_analysis['risk_score']:.3f}")
            logger.info(f"   Processing Time: {processing_time:.3f}s")
            logger.info(f"   Validation Level: {validation_level.value}")
            logger.info(f"   TON Connect Available: {ton_connect_available}")
            
            # Enhanced result with additional metadata
            enhanced_result = {
                **invoice_result,
                'fraud_score': fraud_analysis['risk_score'],
                'validation_level': validation_level.value,
                'processing_time': processing_time,
                'ton_connect_available': ton_connect_available,
                'security_features': {
                    'fraud_detection': True,
                    'amount_validation': True,
                    'enhanced_error_handling': True
                }
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced payment creation failed: {e}")
            return await self.error_handler.handle_payment_error(
                PaymentRequest(
                    payment_id="error",
                    user_id=user_id,
                    amount=Decimal(str(pricing_data.get('total_stars', 0))),
                    currency="XTR",
                    payment_method=PaymentMethod.TELEGRAM_STARS,
                    memo="",
                    recipient_address="",
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(minutes=20),
                    status=PaymentStatus.FAILED,
                    metadata=campaign_data
                ),
                e
            )
    
    async def _perform_phase1_validation(self, user_id: int, campaign_data: Dict, pricing_data: Dict) -> Dict:
        """Phase 1: Enhanced validation checks"""
        
        # Validate user eligibility
        user_check = await self._validate_user_eligibility(user_id)
        if not user_check['valid']:
            return {
                'valid': False,
                'error': user_check['error'],
                'recovery_options': ['verify_account', 'contact_support']
            }
        
        # Validate campaign data
        campaign_check = await self._validate_campaign_data(campaign_data)
        if not campaign_check['valid']:
            return {
                'valid': False,
                'error': campaign_check['error'],
                'recovery_options': ['review_campaign', 'modify_settings']
            }
        
        # Validate pricing data
        pricing_check = await self._validate_pricing_data(pricing_data)
        if not pricing_check['valid']:
            return {
                'valid': False,
                'error': pricing_check['error'],
                'recovery_options': ['recalculate_pricing', 'contact_support']
            }
        
        # Validate Stars amount
        stars_amount = pricing_data.get('total_stars', 0)
        if stars_amount <= 0 or stars_amount > 10000:  # Max 10,000 Stars per transaction
            return {
                'valid': False,
                'error': f'Invalid Stars amount: {stars_amount}. Must be between 1 and 10,000.',
                'recovery_options': ['adjust_amount', 'split_payment']
            }
        
        return {'valid': True}
    
    async def _validate_user_eligibility(self, user_id: int) -> Dict:
        """Validate user eligibility for payment"""
        try:
            # Check if user exists and is active
            from database import db
            
            user_result = await db.fetchone("""
                SELECT user_id, is_banned, failed_payment_count
                FROM users 
                WHERE user_id = ?
            """, (user_id,))
            
            if not user_result:
                return {'valid': False, 'error': 'User not found'}
            
            is_banned = user_result[1] if len(user_result) > 1 else False
            failed_payments = user_result[2] if len(user_result) > 2 else 0
            
            if is_banned:
                return {'valid': False, 'error': 'Account suspended'}
            
            if failed_payments >= 5:
                return {'valid': False, 'error': 'Too many failed payments - account restricted'}
            
            return {'valid': True}
            
        except Exception as e:
            logger.error(f"User eligibility check failed: {e}")
            return {'valid': False, 'error': 'Unable to verify account status'}
    
    async def _validate_campaign_data(self, campaign_data: Dict) -> Dict:
        """Validate campaign data structure and content"""
        required_fields = ['duration', 'selected_channels', 'posts_per_day']
        
        for field in required_fields:
            if field not in campaign_data:
                return {'valid': False, 'error': f'Missing required field: {field}'}
        
        duration = campaign_data.get('duration', 0)
        if duration < 1 or duration > 365:
            return {'valid': False, 'error': f'Invalid duration: {duration} days. Must be 1-365.'}
        
        channels = campaign_data.get('selected_channels', [])
        if not channels or len(channels) == 0:
            return {'valid': False, 'error': 'No channels selected'}
        
        posts_per_day = campaign_data.get('posts_per_day', 0)
        if posts_per_day < 1 or posts_per_day > 10:
            return {'valid': False, 'error': f'Invalid posts per day: {posts_per_day}. Must be 1-10.'}
        
        return {'valid': True}
    
    async def _validate_pricing_data(self, pricing_data: Dict) -> Dict:
        """Validate pricing data accuracy"""
        required_fields = ['total_stars', 'total_usd']
        
        for field in required_fields:
            if field not in pricing_data:
                return {'valid': False, 'error': f'Missing pricing field: {field}'}
        
        stars_amount = pricing_data.get('total_stars', 0)
        usd_amount = pricing_data.get('total_usd', 0)
        
        # Validate Stars to USD conversion (approximately 0.013 USD per Star)
        expected_usd = stars_amount * 0.013
        tolerance = 0.02  # 2 cent tolerance
        
        if abs(usd_amount - expected_usd) > tolerance:
            return {
                'valid': False,
                'error': f'Pricing mismatch: {stars_amount} Stars should equal ${expected_usd:.2f}, got ${usd_amount:.2f}'
            }
        
        return {'valid': True}
    
    async def _check_ton_connect_availability(self, user_id: int) -> bool:
        """Phase 2: Check if user has TON Connect available"""
        try:
            if not self.ton_connect:
                await self.initialize_ton_connect()
            
            if self.ton_connect:
                connection_status = await self.ton_connect.get_connection_status(user_id)
                return connection_status.get('connected', False)
            
            return False
            
        except Exception as e:
            logger.error(f"TON Connect availability check failed: {e}")
            return False
    
    async def _handle_suspicious_payment(self, user_id: int, fraud_analysis: Dict):
        """Handle suspicious payment detection"""
        self.fraud_attempts.add(user_id)
        
        # Log fraud attempt
        try:
            from database import db
            
            await db.execute("""
                INSERT INTO fraud_attempts (
                    user_id, payment_type, risk_score, risk_factors, detected_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                'telegram_stars',
                fraud_analysis['risk_score'],
                json.dumps(fraud_analysis['risk_factors']),
                datetime.now()
            ))
            
        except Exception as e:
            logger.error(f"Failed to log fraud attempt: {e}")
        
        # Notify admins for high-risk cases
        if fraud_analysis['risk_score'] >= 0.8:
            await self._notify_admins_fraud_detection(user_id, fraud_analysis)
    
    async def _notify_admins_fraud_detection(self, user_id: int, fraud_analysis: Dict):
        """Notify administrators about high-risk fraud detection"""
        try:
            from config import ADMIN_IDS
            
            admin_message = f"""
🚨 **HIGH-RISK FRAUD ALERT**

**Payment Type:** Telegram Stars
**User ID:** {user_id}
**Risk Score:** {fraud_analysis['risk_score']:.3f}
**Risk Factors:** {', '.join(fraud_analysis['risk_factors'])}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Action Required:** Manual review recommended
            """
            
            for admin_id in ADMIN_IDS:
                await self.bot.send_message(admin_id, admin_message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Failed to notify admins about fraud: {e}")
    
    async def _handle_invoice_creation_error(self, user_id: int, invoice_result: Dict, 
                                           validation_level: PaymentValidationLevel) -> Dict:
        """Phase 1: Enhanced error handling for invoice creation failures"""
        
        error_message = invoice_result.get('error', 'Unknown error')
        
        # Classify error type
        if 'payload' in error_message.lower():
            return {
                'success': False,
                'error': 'Payment data too large - please try a smaller campaign',
                'error_type': 'payload_size',
                'recovery_options': ['reduce_campaign_size', 'split_payment']
            }
        elif 'stars' in error_message.lower():
            return {
                'success': False,
                'error': 'Stars payment service temporarily unavailable',
                'error_type': 'service_unavailable',
                'recovery_options': ['retry_later', 'use_ton_payment']
            }
        elif 'amount' in error_message.lower():
            return {
                'success': False,
                'error': 'Invalid payment amount - please check your campaign settings',
                'error_type': 'invalid_amount',
                'recovery_options': ['recalculate_pricing', 'contact_support']
            }
        else:
            return {
                'success': False,
                'error': 'Payment creation failed - please try again',
                'error_type': 'generic',
                'recovery_options': ['retry_payment', 'contact_support']
            }
    
    async def process_enhanced_pre_checkout(self, pre_checkout_query: PreCheckoutQuery) -> Dict:
        """
        Enhanced pre-checkout processing with Phase 1 & Phase 2 features
        """
        start_time = time.time()
        
        try:
            # Extract payment data
            payload_data = json.loads(pre_checkout_query.invoice_payload)
            payment_id = payload_data.get('payment_id')
            user_id = pre_checkout_query.from_user.id
            
            logger.info(f"💫 Processing enhanced pre-checkout: {payment_id}")
            
            # Phase 1: Enhanced validation during pre-checkout
            validation_result = await self._validate_pre_checkout_data(pre_checkout_query, payload_data)
            
            if not validation_result['valid']:
                await pre_checkout_query.answer(
                    ok=False,
                    error_message=validation_result['error']
                )
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'payment_id': payment_id
                }
            
            # Phase 1: Additional fraud check during pre-checkout
            if payment_id in self.payment_cache:
                cached_payment = self.payment_cache[payment_id]
                
                if cached_payment['fraud_score'] >= 0.5:
                    logger.warning(f"🚨 High fraud score payment blocked: {payment_id}")
                    await pre_checkout_query.answer(
                        ok=False,
                        error_message="Payment blocked for security review"
                    )
                    return {
                        'success': False,
                        'error': 'Security review required',
                        'payment_id': payment_id
                    }
            
            # Approve pre-checkout
            await pre_checkout_query.answer(ok=True)
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Enhanced pre-checkout approved: {payment_id} ({processing_time:.3f}s)")
            
            return {
                'success': True,
                'payment_id': payment_id,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced pre-checkout failed: {e}")
            await pre_checkout_query.answer(
                ok=False,
                error_message="Payment validation failed - please try again"
            )
            return {
                'success': False,
                'error': str(e),
                'payment_id': payload_data.get('payment_id', 'unknown')
            }
    
    async def _validate_pre_checkout_data(self, pre_checkout_query: PreCheckoutQuery, payload_data: Dict) -> Dict:
        """Validate pre-checkout data"""
        
        # Check required fields
        required_fields = ['payment_id', 'user_id', 'service', 'amount']
        for field in required_fields:
            if field not in payload_data:
                return {'valid': False, 'error': f'Missing payment field: {field}'}
        
        # Validate user ID matches
        if payload_data['user_id'] != pre_checkout_query.from_user.id:
            return {'valid': False, 'error': 'User ID mismatch'}
        
        # Validate amount
        expected_amount = payload_data['amount']
        actual_amount = pre_checkout_query.total_amount
        
        if expected_amount != actual_amount:
            return {
                'valid': False,
                'error': f'Amount mismatch: expected {expected_amount}, got {actual_amount}'
            }
        
        # Check payment cache
        payment_id = payload_data['payment_id']
        if payment_id not in self.payment_cache:
            return {'valid': False, 'error': 'Payment session expired'}
        
        return {'valid': True}
    
    async def process_enhanced_successful_payment(self, message: Message) -> EnhancedPaymentResult:
        """
        Enhanced successful payment processing with Phase 1 & Phase 2 features
        """
        start_time = time.time()
        
        try:
            payment = message.successful_payment
            payload_data = json.loads(payment.invoice_payload)
            payment_id = payload_data.get('payment_id')
            user_id = message.from_user.id
            
            logger.info(f"💰 Processing enhanced successful payment: {payment_id}")
            
            # Phase 1: Enhanced payment validation
            validation_result = await self._validate_successful_payment(payment, payload_data)
            
            if not validation_result['valid']:
                return EnhancedPaymentResult(
                    success=False,
                    payment_id=payment_id,
                    transaction_id=payment.telegram_payment_charge_id,
                    amount_paid=None,
                    validation_level=PaymentValidationLevel.ENHANCED,
                    fraud_score=0.0,
                    error_message=validation_result['error'],
                    recovery_options=validation_result.get('recovery_options', []),
                    processing_time=time.time() - start_time,
                    metadata={}
                )
            
            # Phase 1: Amount validation using PaymentAmountValidator
            expected_amount = Decimal(str(payload_data['amount']))
            received_amount = Decimal(str(payment.total_amount))
            
            amount_validation = await self.amount_validator.validate_payment_amount(
                payment_id, user_id, float(expected_amount), float(received_amount)
            )
            
            if not amount_validation['valid']:
                logger.warning(f"⚠️ Amount validation failed for payment {payment_id}")
                # Handle amount mismatch according to validation protocol
                await self._handle_amount_validation_failure(user_id, amount_validation)
            
            # Get cached payment data
            cached_payment = self.payment_cache.get(payment_id, {})
            fraud_score = cached_payment.get('fraud_score', 0.0)
            
            # Process using base system
            base_result = await self.base_system.handle_successful_payment(message)
            
            if base_result.get('success', False):
                # Phase 1: Enhanced success processing
                await self._process_enhanced_success(payment_id, user_id, cached_payment)
                
                # Phase 2: TON Connect notification (if available)
                await self._notify_ton_connect_payment_success(user_id, payment_id)
                
                processing_time = time.time() - start_time
                
                logger.info(f"✅ Enhanced payment completed: {payment_id}")
                logger.info(f"   Amount: {payment.total_amount} ⭐")
                logger.info(f"   Fraud Score: {fraud_score:.3f}")
                logger.info(f"   Processing Time: {processing_time:.3f}s")
                
                return EnhancedPaymentResult(
                    success=True,
                    payment_id=payment_id,
                    transaction_id=payment.telegram_payment_charge_id,
                    amount_paid=received_amount,
                    validation_level=PaymentValidationLevel.ENHANCED,
                    fraud_score=fraud_score,
                    error_message=None,
                    recovery_options=[],
                    processing_time=processing_time,
                    metadata={
                        'base_result': base_result,
                        'amount_validation': amount_validation,
                        'ton_connect_available': await self._check_ton_connect_availability(user_id)
                    }
                )
            else:
                # Enhanced error handling for base system failure
                return await self._handle_base_system_failure(payment_id, user_id, base_result, start_time)
                
        except Exception as e:
            logger.error(f"❌ Enhanced payment processing failed: {e}")
            
            return EnhancedPaymentResult(
                success=False,
                payment_id=payment_id if 'payment_id' in locals() else 'unknown',
                transaction_id=None,
                amount_paid=None,
                validation_level=PaymentValidationLevel.ENHANCED,
                fraud_score=0.0,
                error_message=str(e),
                recovery_options=['contact_support', 'retry_later'],
                processing_time=time.time() - start_time,
                metadata={'error_type': 'exception'}
            )
    
    async def _validate_successful_payment(self, payment: SuccessfulPayment, payload_data: Dict) -> Dict:
        """Validate successful payment data"""
        
        # Basic validation
        if not payment.telegram_payment_charge_id:
            return {'valid': False, 'error': 'Missing transaction ID'}
        
        if payment.total_amount <= 0:
            return {'valid': False, 'error': 'Invalid payment amount'}
        
        # Payload validation
        required_fields = ['payment_id', 'user_id', 'service']
        for field in required_fields:
            if field not in payload_data:
                return {'valid': False, 'error': f'Missing payload field: {field}'}
        
        return {'valid': True}
    
    async def _handle_amount_validation_failure(self, user_id: int, validation_result: Dict):
        """Handle amount validation failure according to protocol"""
        
        if validation_result['status'] == 'underpayment':
            # Send underpayment message with retry option
            shortage = validation_result.get('shortage', 0)
            message = f"""
❌ **Payment Amount Insufficient**

You paid **{validation_result.get('received', 0)} Stars** but the required amount is **{validation_result.get('expected', 0)} Stars**.

**Shortage:** {shortage} Stars

Please send the correct amount to complete your campaign.
            """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Retry Payment", callback_data="retry_stars_payment")],
                [InlineKeyboardButton(text="💬 Contact Support", callback_data="contact_support")]
            ])
            
            try:
                await self.bot.send_message(user_id, message, parse_mode='Markdown', reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Failed to send underpayment message: {e}")
        
        elif validation_result['status'] == 'overpayment':
            # Send overpayment message with manual confirmation
            excess = validation_result.get('excess', 0)
            message = f"""
⚠️ **Overpayment Detected**

You paid **{validation_result.get('received', 0)} Stars** but only **{validation_result.get('expected', 0)} Stars** was required.

**Excess:** {excess} Stars

Please contact support for refund processing.
            """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Confirm Processing", callback_data="confirm_overpayment")],
                [InlineKeyboardButton(text="💬 Contact Support", callback_data="contact_support")]
            ])
            
            try:
                await self.bot.send_message(user_id, message, parse_mode='Markdown', reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Failed to send overpayment message: {e}")
    
    async def _process_enhanced_success(self, payment_id: str, user_id: int, cached_payment: Dict):
        """Process enhanced success actions"""
        
        # Update payment history
        self.payment_history[payment_id] = {
            'user_id': user_id,
            'completed_at': datetime.now(),
            'fraud_score': cached_payment.get('fraud_score', 0.0),
            'validation_level': cached_payment.get('validation_level', 'enhanced'),
            'success': True
        }
        
        # Clean up caches
        if payment_id in self.payment_cache:
            del self.payment_cache[payment_id]
        
        # Remove from fraud attempts if user was flagged
        if user_id in self.fraud_attempts:
            self.fraud_attempts.remove(user_id)
        
        # Log success metrics
        logger.info(f"📊 Enhanced payment metrics for {payment_id}:")
        logger.info(f"   Fraud Score: {cached_payment.get('fraud_score', 0.0):.3f}")
        logger.info(f"   Validation Level: {cached_payment.get('validation_level', 'enhanced')}")
        logger.info(f"   Cache Cleaned: True")
    
    async def _notify_ton_connect_payment_success(self, user_id: int, payment_id: str):
        """Phase 2: Notify TON Connect users about payment success"""
        try:
            if self.ton_connect and await self._check_ton_connect_availability(user_id):
                # Send TON Connect specific notification
                wallet_info = await self.ton_connect.get_user_wallet_info(user_id)
                
                if wallet_info:
                    logger.info(f"🔗 TON Connect user {user_id} payment completed: {payment_id}")
                    # Additional TON Connect specific processing could be added here
                    
        except Exception as e:
            logger.error(f"TON Connect notification failed: {e}")
    
    async def _handle_base_system_failure(self, payment_id: str, user_id: int, 
                                        base_result: Dict, start_time: float) -> EnhancedPaymentResult:
        """Handle base system failure with enhanced error recovery"""
        
        error_message = base_result.get('error', 'Base system processing failed')
        
        # Determine recovery options based on error type
        recovery_options = ['contact_support']
        
        if 'database' in error_message.lower():
            recovery_options.extend(['retry_later', 'manual_verification'])
        elif 'campaign' in error_message.lower():
            recovery_options.extend(['retry_campaign_creation', 'modify_campaign'])
        
        return EnhancedPaymentResult(
            success=False,
            payment_id=payment_id,
            transaction_id=None,
            amount_paid=None,
            validation_level=PaymentValidationLevel.ENHANCED,
            fraud_score=0.0,
            error_message=error_message,
            recovery_options=recovery_options,
            processing_time=time.time() - start_time,
            metadata={'base_error': base_result}
        )
    
    async def get_payment_analytics(self, user_id: Optional[int] = None) -> Dict:
        """Get enhanced payment analytics"""
        
        analytics = {
            'total_payments': len(self.payment_history),
            'successful_payments': len([p for p in self.payment_history.values() if p['success']]),
            'fraud_attempts': len(self.fraud_attempts),
            'average_fraud_score': 0.0,
            'active_cache_entries': len(self.payment_cache)
        }
        
        if self.payment_history:
            fraud_scores = [p.get('fraud_score', 0.0) for p in self.payment_history.values()]
            analytics['average_fraud_score'] = sum(fraud_scores) / len(fraud_scores)
        
        if user_id:
            user_payments = [p for p in self.payment_history.values() if p['user_id'] == user_id]
            analytics['user_payments'] = len(user_payments)
            analytics['user_success_rate'] = len([p for p in user_payments if p['success']]) / len(user_payments) if user_payments else 0
        
        return analytics
    
    async def cleanup_expired_data(self):
        """Clean up expired payment data and caches"""
        now = datetime.now()
        expired_threshold = now - timedelta(hours=24)
        
        # Clean payment cache
        expired_payments = [
            payment_id for payment_id, data in self.payment_cache.items()
            if data.get('created_at', now) < expired_threshold
        ]
        
        for payment_id in expired_payments:
            del self.payment_cache[payment_id]
        
        # Clean API cache
        self.api_call_cache.clear()
        
        logger.info(f"🧹 Cleaned up {len(expired_payments)} expired payment cache entries")

# Global instance
enhanced_stars_payment_system = None

def get_enhanced_stars_payment_system(bot: Bot, db_instance=None) -> EnhancedStarsPaymentSystem:
    """Get or create enhanced Stars payment system instance"""
    global enhanced_stars_payment_system
    if enhanced_stars_payment_system is None:
        enhanced_stars_payment_system = EnhancedStarsPaymentSystem(bot, db_instance)
    return enhanced_stars_payment_system

async def init_enhanced_stars_payment_system(bot: Bot, db_instance=None) -> EnhancedStarsPaymentSystem:
    """Initialize enhanced Stars payment system"""
    system = get_enhanced_stars_payment_system(bot, db_instance)
    
    # Initialize TON Connect
    await system.initialize_ton_connect()
    
    # Start cleanup task
    asyncio.create_task(periodic_enhanced_cleanup(system))
    
    logger.info("✅ Enhanced Telegram Stars Payment System initialized")
    logger.info("   🔍 Phase 1: Enhanced validation, fraud detection, error handling")
    logger.info("   🔗 Phase 2: TON Connect integration, advanced security")
    logger.info("   📊 Performance optimization and caching enabled")
    logger.info("   💫 Ready for enterprise-grade Stars payments")
    
    return system

async def periodic_enhanced_cleanup(system: EnhancedStarsPaymentSystem):
    """Periodic cleanup of enhanced system data"""
    while True:
        try:
            await system.cleanup_expired_data()
            await asyncio.sleep(3600)  # Clean up every hour
        except Exception as e:
            logger.error(f"❌ Enhanced cleanup error: {e}")
            await asyncio.sleep(3600)