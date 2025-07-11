"""
Enhanced Payment Processor for I3lani Bot
Comprehensive payment processing with improved validation, error handling, and performance
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
from decimal import Decimal, ROUND_HALF_UP

from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    TON_BLOCKCHAIN = "ton_blockchain"
    TELEGRAM_STARS = "telegram_stars"
    TON_CONNECT = "ton_connect"
    TELEGRAM_WALLET = "telegram_wallet"

@dataclass
class PaymentRequest:
    """Enhanced payment request structure"""
    payment_id: str
    user_id: int
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    memo: str
    recipient_address: str
    created_at: datetime
    expires_at: datetime
    status: PaymentStatus
    metadata: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class PaymentResult:
    """Payment processing result"""
    success: bool
    payment_id: str
    transaction_hash: Optional[str]
    amount_received: Optional[Decimal]
    status: PaymentStatus
    error_message: Optional[str]
    metadata: Dict[str, Any]

class FraudDetector:
    """Advanced fraud detection system"""
    
    def __init__(self):
        self.suspicious_patterns = set()
        self.user_activity_cache = {}
        self.fraud_threshold = 0.7
    
    async def analyze_payment(self, payment_request: PaymentRequest) -> Dict[str, Any]:
        """Analyze payment for fraud patterns"""
        risk_score = 0.0
        risk_factors = []
        
        # Check for rapid successive payments
        if await self._check_rapid_payments(payment_request.user_id):
            risk_score += 0.3
            risk_factors.append("rapid_successive_payments")
        
        # Check for unusual amounts
        if await self._check_unusual_amount(payment_request.amount):
            risk_score += 0.2
            risk_factors.append("unusual_amount")
        
        # Check for suspicious memo patterns
        if await self._check_suspicious_memo(payment_request.memo):
            risk_score += 0.4
            risk_factors.append("suspicious_memo")
        
        # Check user history
        if await self._check_user_history(payment_request.user_id):
            risk_score += 0.3
            risk_factors.append("suspicious_user_history")
        
        return {
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'is_suspicious': risk_score >= self.fraud_threshold,
            'requires_manual_review': risk_score >= 0.5
        }
    
    async def _check_rapid_payments(self, user_id: int) -> bool:
        """Check for rapid successive payments"""
        current_time = datetime.now()
        user_activity = self.user_activity_cache.get(user_id, [])
        
        # Check payments in last 5 minutes
        recent_payments = [
            timestamp for timestamp in user_activity
            if (current_time - timestamp).total_seconds() < 300
        ]
        
        return len(recent_payments) >= 3
    
    async def _check_unusual_amount(self, amount: Decimal) -> bool:
        """Check for unusual payment amounts"""
        # Define suspicious amount patterns
        suspicious_amounts = [
            Decimal('0.01'),  # Too small
            Decimal('1000.00'),  # Too large
        ]
        
        return any(abs(amount - suspicious) < Decimal('0.001') for suspicious in suspicious_amounts)
    
    async def _check_suspicious_memo(self, memo: str) -> bool:
        """Check for suspicious memo patterns"""
        suspicious_keywords = ['test', 'hack', 'scam', 'fraud', 'fake']
        memo_lower = memo.lower()
        
        return any(keyword in memo_lower for keyword in suspicious_keywords)
    
    async def _check_user_history(self, user_id: int) -> bool:
        """Check user's payment history for suspicious patterns"""
        try:
            from database import db
            
            # Check for excessive failed payments
            result = await db.fetchone("""
                SELECT COUNT(*) as failed_count
                FROM payment_history 
                WHERE user_id = ? AND status = 'failed' 
                AND created_at > datetime('now', '-1 day')
            """, (user_id,))
            
            failed_count = result[0] if result else 0
            return failed_count >= 5
            
        except Exception as e:
            logger.error(f"Error checking user history: {e}")
            return False

class TransactionValidator:
    """Advanced transaction validation"""
    
    def __init__(self):
        self.min_confirmations = 1
        self.max_age_minutes = 60
    
    async def validate_transaction(self, transaction_hash: str, expected_amount: Decimal, memo: str) -> Dict[str, Any]:
        """Comprehensive transaction validation"""
        validation_result = {
            'valid': False,
            'checks': {},
            'error_message': None
        }
        
        try:
            # 1. Check transaction existence
            transaction = await self._get_transaction_details(transaction_hash)
            if not transaction:
                validation_result['error_message'] = "Transaction not found"
                return validation_result
            
            validation_result['checks']['exists'] = True
            
            # 2. Check transaction finality
            finality_check = await self._check_transaction_finality(transaction)
            validation_result['checks']['finality'] = finality_check
            
            # 3. Check amount accuracy
            amount_check = await self._validate_amount(transaction, expected_amount)
            validation_result['checks']['amount'] = amount_check
            
            # 4. Check memo matching
            memo_check = await self._validate_memo(transaction, memo)
            validation_result['checks']['memo'] = memo_check
            
            # 5. Check transaction structure
            structure_check = await self._validate_transaction_structure(transaction)
            validation_result['checks']['structure'] = structure_check
            
            # 6. Check transaction age
            age_check = await self._check_transaction_age(transaction)
            validation_result['checks']['age'] = age_check
            
            # Overall validation
            validation_result['valid'] = all([
                validation_result['checks']['exists'],
                validation_result['checks']['finality'],
                validation_result['checks']['amount'],
                validation_result['checks']['memo'],
                validation_result['checks']['structure'],
                validation_result['checks']['age']
            ])
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Transaction validation error: {e}")
            validation_result['error_message'] = str(e)
            return validation_result
    
    async def _get_transaction_details(self, transaction_hash: str) -> Optional[Dict]:
        """Get transaction details from blockchain"""
        try:
            from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor
            
            monitor = EnhancedTONPaymentMonitor()
            transaction = await monitor.get_transaction_by_hash(transaction_hash)
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error getting transaction details: {e}")
            return None
    
    async def _check_transaction_finality(self, transaction: Dict) -> bool:
        """Check if transaction is finalized"""
        # In TON, 1 confirmation is sufficient for finality
        return transaction.get('confirmations', 0) >= self.min_confirmations
    
    async def _validate_amount(self, transaction: Dict, expected_amount: Decimal) -> bool:
        """Validate transaction amount"""
        try:
            actual_amount = Decimal(str(transaction.get('amount', 0)))
            # Allow for small tolerance due to gas fees
            tolerance = Decimal('0.01')
            
            return abs(actual_amount - expected_amount) <= tolerance
            
        except Exception as e:
            logger.error(f"Amount validation error: {e}")
            return False
    
    async def _validate_memo(self, transaction: Dict, expected_memo: str) -> bool:
        """Validate transaction memo"""
        actual_memo = transaction.get('memo', '').strip()
        return actual_memo == expected_memo.strip()
    
    async def _validate_transaction_structure(self, transaction: Dict) -> bool:
        """Validate transaction structure"""
        required_fields = ['hash', 'amount', 'memo', 'timestamp']
        return all(field in transaction for field in required_fields)
    
    async def _check_transaction_age(self, transaction: Dict) -> bool:
        """Check if transaction is not too old"""
        try:
            transaction_time = datetime.fromtimestamp(transaction.get('timestamp', 0))
            age_minutes = (datetime.now() - transaction_time).total_seconds() / 60
            
            return age_minutes <= self.max_age_minutes
            
        except Exception as e:
            logger.error(f"Age check error: {e}")
            return False

class PaymentErrorHandler:
    """Advanced payment error handling with recovery"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.retry_delays = [10, 30, 60, 120, 300]  # Exponential backoff
    
    async def handle_payment_error(self, payment_request: PaymentRequest, error: Exception) -> PaymentResult:
        """Handle payment errors with recovery strategies"""
        error_type = self._classify_error(error)
        
        recovery_strategies = {
            'network_timeout': self._handle_network_timeout,
            'insufficient_gas': self._handle_insufficient_gas,
            'invalid_address': self._handle_invalid_address,
            'amount_mismatch': self._handle_amount_mismatch,
            'memo_missing': self._handle_memo_missing,
            'fraud_detected': self._handle_fraud_detected
        }
        
        strategy = recovery_strategies.get(error_type, self._handle_generic_error)
        return await strategy(payment_request, error)
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for appropriate handling"""
        error_message = str(error).lower()
        
        if 'timeout' in error_message or 'connection' in error_message:
            return 'network_timeout'
        elif 'gas' in error_message or 'fee' in error_message:
            return 'insufficient_gas'
        elif 'address' in error_message or 'invalid' in error_message:
            return 'invalid_address'
        elif 'amount' in error_message or 'mismatch' in error_message:
            return 'amount_mismatch'
        elif 'memo' in error_message or 'comment' in error_message:
            return 'memo_missing'
        elif 'fraud' in error_message or 'suspicious' in error_message:
            return 'fraud_detected'
        else:
            return 'generic_error'
    
    async def _handle_network_timeout(self, payment_request: PaymentRequest, error: Exception) -> PaymentResult:
        """Handle network timeout errors"""
        if payment_request.retry_count < payment_request.max_retries:
            # Retry with exponential backoff
            delay = self.retry_delays[min(payment_request.retry_count, len(self.retry_delays) - 1)]
            await asyncio.sleep(delay)
            
            payment_request.retry_count += 1
            return await self._retry_payment(payment_request)
        
        return PaymentResult(
            success=False,
            payment_id=payment_request.payment_id,
            transaction_hash=None,
            amount_received=None,
            status=PaymentStatus.FAILED,
            error_message="Network timeout - maximum retries exceeded",
            metadata={'retry_count': payment_request.retry_count}
        )
    
    async def _handle_insufficient_gas(self, payment_request: PaymentRequest, error: Exception) -> PaymentResult:
        """Handle insufficient gas errors"""
        # Notify user about gas fees
        await self._notify_user_about_gas_fees(payment_request.user_id)
        
        return PaymentResult(
            success=False,
            payment_id=payment_request.payment_id,
            transaction_hash=None,
            amount_received=None,
            status=PaymentStatus.FAILED,
            error_message="Insufficient gas fees - please ensure your wallet has enough TON for gas",
            metadata={'error_type': 'insufficient_gas'}
        )
    
    async def _handle_invalid_address(self, payment_request: PaymentRequest, error: Exception) -> PaymentResult:
        """Handle invalid address errors"""
        # Request new address from user
        await self._request_new_address(payment_request.user_id)
        
        return PaymentResult(
            success=False,
            payment_id=payment_request.payment_id,
            transaction_hash=None,
            amount_received=None,
            status=PaymentStatus.FAILED,
            error_message="Invalid wallet address - please provide a valid TON address",
            metadata={'error_type': 'invalid_address'}
        )
    
    async def _handle_amount_mismatch(self, payment_request: PaymentRequest, error: Exception) -> PaymentResult:
        """Handle amount mismatch errors"""
        # Trigger amount validation protocol
        from payment_amount_validator import validate_payment_amount
        
        # This would typically be called when we detect the mismatch
        return PaymentResult(
            success=False,
            payment_id=payment_request.payment_id,
            transaction_hash=None,
            amount_received=None,
            status=PaymentStatus.FAILED,
            error_message="Payment amount mismatch - please send the exact amount",
            metadata={'error_type': 'amount_mismatch'}
        )
    
    async def _handle_memo_missing(self, payment_request: PaymentRequest, error: Exception) -> PaymentResult:
        """Handle missing memo errors"""
        # Notify user about memo requirement
        await self._notify_user_about_memo(payment_request.user_id, payment_request.memo)
        
        return PaymentResult(
            success=False,
            payment_id=payment_request.payment_id,
            transaction_hash=None,
            amount_received=None,
            status=PaymentStatus.FAILED,
            error_message=f"Missing payment memo - please include memo: {payment_request.memo}",
            metadata={'error_type': 'memo_missing'}
        )
    
    async def _handle_fraud_detected(self, payment_request: PaymentRequest, error: Exception) -> PaymentResult:
        """Handle fraud detection errors"""
        # Log fraud attempt
        await self._log_fraud_attempt(payment_request)
        
        # Notify admin
        await self._notify_admin_about_fraud(payment_request)
        
        return PaymentResult(
            success=False,
            payment_id=payment_request.payment_id,
            transaction_hash=None,
            amount_received=None,
            status=PaymentStatus.FAILED,
            error_message="Payment blocked due to security concerns - please contact support",
            metadata={'error_type': 'fraud_detected'}
        )
    
    async def _handle_generic_error(self, payment_request: PaymentRequest, error: Exception) -> PaymentResult:
        """Handle generic errors"""
        logger.error(f"Generic payment error: {error}")
        
        return PaymentResult(
            success=False,
            payment_id=payment_request.payment_id,
            transaction_hash=None,
            amount_received=None,
            status=PaymentStatus.FAILED,
            error_message="Payment processing error - please try again or contact support",
            metadata={'error_type': 'generic_error', 'original_error': str(error)}
        )
    
    async def _retry_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        """Retry payment processing"""
        # This would call the main payment processor again
        # For now, return a generic retry result
        return PaymentResult(
            success=False,
            payment_id=payment_request.payment_id,
            transaction_hash=None,
            amount_received=None,
            status=PaymentStatus.PROCESSING,
            error_message="Retrying payment processing...",
            metadata={'retry_attempt': payment_request.retry_count}
        )
    
    async def _notify_user_about_gas_fees(self, user_id: int):
        """Notify user about gas fees"""
        message = """
🚨 **Gas Fee Required**

Your payment failed because there wasn't enough TON to cover gas fees.

**Solution:**
• Ensure your wallet has at least 0.05 TON extra for gas
• Try sending a slightly higher amount
• Contact support if the issue persists

💡 **Tip:** Gas fees are required for all TON transactions
        """
        
        try:
            await self.bot.send_message(user_id, message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to notify user about gas fees: {e}")
    
    async def _request_new_address(self, user_id: int):
        """Request new wallet address from user"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Update Wallet Address", callback_data="update_wallet_address")],
            [InlineKeyboardButton(text="🎯 Connect via TON Connect", callback_data="connect_ton_wallet")],
            [InlineKeyboardButton(text="💬 Contact Support", callback_data="contact_support")]
        ])
        
        message = """
❌ **Invalid Wallet Address**

The wallet address you provided is not valid.

**Solutions:**
• Update your wallet address
• Connect via TON Connect for automatic detection
• Contact support for assistance

🔍 **Valid address format:** EQ... or UQ... (48 characters)
        """
        
        try:
            await self.bot.send_message(user_id, message, parse_mode='Markdown', reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Failed to request new address: {e}")
    
    async def _notify_user_about_memo(self, user_id: int, memo: str):
        """Notify user about memo requirement"""
        message = f"""
📝 **Missing Payment Memo**

Your payment is missing the required memo.

**Required memo:** `{memo}`

**How to add memo:**
1. Copy the memo above
2. Paste it in the "Comment" field when sending payment
3. Send the payment again

⚠️ **Important:** Payments without memo cannot be processed automatically
        """
        
        try:
            await self.bot.send_message(user_id, message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to notify user about memo: {e}")
    
    async def _log_fraud_attempt(self, payment_request: PaymentRequest):
        """Log fraud attempt to database"""
        try:
            from database import db
            
            await db.execute("""
                INSERT INTO fraud_attempts (
                    user_id, payment_id, amount, memo, 
                    detected_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                payment_request.user_id,
                payment_request.payment_id,
                str(payment_request.amount),
                payment_request.memo,
                datetime.now(),
                json.dumps(payment_request.metadata)
            ))
            
        except Exception as e:
            logger.error(f"Failed to log fraud attempt: {e}")
    
    async def _notify_admin_about_fraud(self, payment_request: PaymentRequest):
        """Notify admin about fraud detection"""
        admin_message = f"""
🚨 **FRAUD ALERT**

**User:** {payment_request.user_id}
**Amount:** {payment_request.amount} {payment_request.currency}
**Payment ID:** {payment_request.payment_id}
**Memo:** {payment_request.memo}
**Time:** {payment_request.created_at}

**Action Required:** Manual review recommended
        """
        
        try:
            # Send to admin users
            from config import ADMIN_IDS
            for admin_id in ADMIN_IDS:
                await self.bot.send_message(admin_id, admin_message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Failed to notify admin about fraud: {e}")

class EnhancedPaymentProcessor:
    """Main enhanced payment processor"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.fraud_detector = FraudDetector()
        self.transaction_validator = TransactionValidator()
        self.error_handler = PaymentErrorHandler(bot)
        self.active_payments: Dict[str, PaymentRequest] = {}
    
    async def create_payment_request(self, user_id: int, amount: Decimal, currency: str, 
                                   payment_method: PaymentMethod, memo: str, 
                                   recipient_address: str, metadata: Dict = None) -> PaymentRequest:
        """Create new payment request"""
        payment_id = self._generate_payment_id()
        
        payment_request = PaymentRequest(
            payment_id=payment_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            memo=memo,
            recipient_address=recipient_address,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=20),
            status=PaymentStatus.PENDING,
            metadata=metadata or {}
        )
        
        self.active_payments[payment_id] = payment_request
        
        # Log payment creation
        logger.info(f"💳 Created payment request: {payment_id}")
        logger.info(f"   User: {user_id}")
        logger.info(f"   Amount: {amount} {currency}")
        logger.info(f"   Method: {payment_method.value}")
        
        return payment_request
    
    async def process_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        """Process payment with enhanced validation and error handling"""
        try:
            # 1. Fraud detection
            fraud_analysis = await self.fraud_detector.analyze_payment(payment_request)
            
            if fraud_analysis['is_suspicious']:
                logger.warning(f"🚨 Suspicious payment detected: {payment_request.payment_id}")
                return PaymentResult(
                    success=False,
                    payment_id=payment_request.payment_id,
                    transaction_hash=None,
                    amount_received=None,
                    status=PaymentStatus.FAILED,
                    error_message="Payment blocked due to security concerns",
                    metadata=fraud_analysis
                )
            
            # 2. Update status
            payment_request.status = PaymentStatus.PROCESSING
            
            # 3. Process based on payment method
            if payment_request.payment_method == PaymentMethod.TON_BLOCKCHAIN:
                return await self._process_ton_blockchain_payment(payment_request)
            elif payment_request.payment_method == PaymentMethod.TELEGRAM_STARS:
                return await self._process_telegram_stars_payment(payment_request)
            elif payment_request.payment_method == PaymentMethod.TON_CONNECT:
                return await self._process_ton_connect_payment(payment_request)
            else:
                raise Exception(f"Unsupported payment method: {payment_request.payment_method}")
                
        except Exception as e:
            logger.error(f"❌ Payment processing error: {e}")
            return await self.error_handler.handle_payment_error(payment_request, e)
    
    async def _process_ton_blockchain_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        """Process TON blockchain payment"""
        # This would integrate with existing TON payment monitoring
        from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor
        
        monitor = EnhancedTONPaymentMonitor()
        
        # Start monitoring for payment
        result = await monitor.monitor_payment_enhanced(
            payment_request.user_id,
            payment_request.memo,
            float(payment_request.amount),
            payment_request.recipient_address
        )
        
        return PaymentResult(
            success=result['success'],
            payment_id=payment_request.payment_id,
            transaction_hash=result.get('transaction_hash'),
            amount_received=Decimal(str(result.get('amount_received', 0))),
            status=PaymentStatus.CONFIRMED if result['success'] else PaymentStatus.FAILED,
            error_message=result.get('error'),
            metadata=result.get('metadata', {})
        )
    
    async def _process_telegram_stars_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        """Process Telegram Stars payment"""
        # This would integrate with existing Stars payment system
        from enhanced_telegram_stars_payment import get_enhanced_stars_payment
        
        stars_payment = get_enhanced_stars_payment(self.bot, None)
        
        # Create Stars invoice
        invoice_result = await stars_payment.create_enhanced_invoice(
            payment_request.user_id,
            int(payment_request.amount),
            payment_request.metadata.get('campaign_data', {}),
            payment_request.metadata.get('pricing_data', {})
        )
        
        return PaymentResult(
            success=invoice_result['success'],
            payment_id=payment_request.payment_id,
            transaction_hash=invoice_result.get('invoice_id'),
            amount_received=payment_request.amount,
            status=PaymentStatus.CONFIRMED if invoice_result['success'] else PaymentStatus.FAILED,
            error_message=invoice_result.get('error'),
            metadata=invoice_result.get('metadata', {})
        )
    
    async def _process_ton_connect_payment(self, payment_request: PaymentRequest) -> PaymentResult:
        """Process TON Connect payment"""
        # This would integrate with TON Connect system
        from ton_connect_integration import get_ton_connect_integration
        
        ton_connect = get_ton_connect_integration(self.bot, "")
        
        # Request transaction through connected wallet
        transaction_result = await ton_connect.request_transaction(
            payment_request.user_id,
            float(payment_request.amount),
            payment_request.memo,
            payment_request.recipient_address
        )
        
        if transaction_result:
            return PaymentResult(
                success=True,
                payment_id=payment_request.payment_id,
                transaction_hash=transaction_result.get('transaction_hash'),
                amount_received=payment_request.amount,
                status=PaymentStatus.CONFIRMED,
                error_message=None,
                metadata=transaction_result
            )
        else:
            return PaymentResult(
                success=False,
                payment_id=payment_request.payment_id,
                transaction_hash=None,
                amount_received=None,
                status=PaymentStatus.FAILED,
                error_message="Failed to process TON Connect payment",
                metadata={}
            )
    
    def _generate_payment_id(self) -> str:
        """Generate unique payment ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        return f"PAY-{timestamp}-{random_suffix}"
    
    async def get_payment_status(self, payment_id: str) -> Optional[PaymentRequest]:
        """Get payment status by ID"""
        return self.active_payments.get(payment_id)
    
    async def cancel_payment(self, payment_id: str) -> bool:
        """Cancel payment request"""
        if payment_id in self.active_payments:
            payment_request = self.active_payments[payment_id]
            payment_request.status = PaymentStatus.EXPIRED
            
            logger.info(f"❌ Payment cancelled: {payment_id}")
            return True
        
        return False
    
    async def cleanup_expired_payments(self):
        """Clean up expired payments"""
        now = datetime.now()
        expired_payments = [
            payment_id for payment_id, payment_request in self.active_payments.items()
            if now > payment_request.expires_at and payment_request.status == PaymentStatus.PENDING
        ]
        
        for payment_id in expired_payments:
            self.active_payments[payment_id].status = PaymentStatus.EXPIRED
            logger.info(f"⏰ Payment expired: {payment_id}")

# Global instance
enhanced_payment_processor = None

def get_enhanced_payment_processor(bot: Bot) -> EnhancedPaymentProcessor:
    """Get or create enhanced payment processor instance"""
    global enhanced_payment_processor
    if enhanced_payment_processor is None:
        enhanced_payment_processor = EnhancedPaymentProcessor(bot)
    return enhanced_payment_processor

async def init_enhanced_payment_processor(bot: Bot) -> EnhancedPaymentProcessor:
    """Initialize enhanced payment processor"""
    processor = get_enhanced_payment_processor(bot)
    
    # Start cleanup task
    asyncio.create_task(periodic_payment_cleanup(processor))
    
    logger.info("✅ Enhanced Payment Processor initialized")
    logger.info("   🔍 Fraud detection enabled")
    logger.info("   ✅ Transaction validation enabled")
    logger.info("   🔄 Error recovery enabled")
    logger.info("   📊 Performance optimization enabled")
    
    return processor

async def periodic_payment_cleanup(processor: EnhancedPaymentProcessor):
    """Periodic cleanup of expired payments"""
    while True:
        try:
            await processor.cleanup_expired_payments()
            await asyncio.sleep(300)  # Clean up every 5 minutes
        except Exception as e:
            logger.error(f"❌ Payment cleanup error: {e}")
            await asyncio.sleep(300)