"""
Enhanced TON Payment System with Memo-Based Verification
Prioritizes memo/note matching for reliable payment confirmation
"""

import asyncio
import aiohttp
import json
import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

# Import timeline components
try:
    from animated_transaction_timeline import (
        get_timeline_manager, create_payment_timeline, update_payment_timeline,
        complete_payment_timeline, TimelineStepStatus, TIMELINE_STEPS
    )
    TIMELINE_AVAILABLE = True
except ImportError:
    TIMELINE_AVAILABLE = False
    logger.warning("Timeline components not available")

logger = logging.getLogger(__name__)

@dataclass
class TONTransaction:
    """Represents a TON transaction with all relevant details"""
    hash: str
    amount: float
    sender: str
    recipient: str
    memo: str
    timestamp: datetime
    confirmed: bool = False

class EnhancedTONPaymentSystem:
    """Enhanced TON payment system with memo-based verification"""
    
    def __init__(self, bot_wallet_address: str):
        self.bot_wallet_address = bot_wallet_address
        self.ton_api_base = "https://toncenter.com/api/v2"
        self.active_monitors = {}  # payment_id -> monitor_task
        
    async def generate_unique_memo(self, user_id: int, payment_context: str = "payment") -> str:
        """Generate unique memo for payment tracking"""
        import random
        import string
        
        # Format: 2 letters + 4 digits (ensures uniqueness)
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        digits = ''.join(random.choices(string.digits, k=4))
        memo = letters + digits
        
        # Log memo generation for tracking
        logger.info(f"Generated memo {memo} for user {user_id} ({payment_context})")
        
        return memo
    
    async def create_payment_request(self, user_id: int, amount_ton: float, 
                                   user_wallet: str, campaign_details: dict, bot_instance=None) -> Dict:
        """Create enhanced payment request with memo-based verification"""
        
        # Generate unique memo for this payment
        memo = await self.generate_unique_memo(user_id, "campaign_payment")
        
        # Create payment request with comprehensive details
        payment_request = {
            'payment_id': f"ton_{user_id}_{int(datetime.now().timestamp())}",
            'user_id': user_id,
            'amount_ton': amount_ton,
            'memo': memo,
            'user_wallet': user_wallet,
            'bot_wallet': self.bot_wallet_address,
            'campaign_details': campaign_details,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=20)).isoformat(),
            'status': 'pending'
        }
        
        # Create animated timeline if available
        if TIMELINE_AVAILABLE and bot_instance:
            try:
                await create_payment_timeline(user_id, payment_request['payment_id'], bot_instance)
                # Update timeline - memo generation completed
                await update_payment_timeline(
                    payment_request['payment_id'], 
                    TIMELINE_STEPS['MEMO_GENERATION'], 
                    TimelineStepStatus.COMPLETED
                )
                # Start payment instructions step
                await update_payment_timeline(
                    payment_request['payment_id'], 
                    TIMELINE_STEPS['PAYMENT_INSTRUCTIONS'], 
                    TimelineStepStatus.IN_PROGRESS
                )
            except Exception as e:
                logger.error(f"Error creating timeline: {e}")
        
        logger.info(f"Created payment request: {payment_request['payment_id']} with memo: {memo}")
        return payment_request
    
    async def start_payment_monitoring(self, payment_request: Dict, 
                                     on_success_callback, on_failure_callback) -> str:
        """Start monitoring TON payments with memo-based verification"""
        
        payment_id = payment_request['payment_id']
        memo = payment_request['memo']
        expected_amount = payment_request['amount_ton']
        user_wallet = payment_request['user_wallet']
        
        # Update timeline - payment instructions completed, start blockchain monitoring
        if TIMELINE_AVAILABLE:
            try:
                await update_payment_timeline(
                    payment_id, 
                    TIMELINE_STEPS['PAYMENT_INSTRUCTIONS'], 
                    TimelineStepStatus.COMPLETED
                )
                await update_payment_timeline(
                    payment_id, 
                    TIMELINE_STEPS['BLOCKCHAIN_MONITORING'], 
                    TimelineStepStatus.IN_PROGRESS
                )
            except Exception as e:
                logger.error(f"Error updating timeline: {e}")
        
        logger.info(f"Starting payment monitoring for {payment_id} with memo: {memo}")
        
        # Start monitoring task
        monitor_task = asyncio.create_task(
            self._monitor_payment_with_memo(
                payment_request, on_success_callback, on_failure_callback
            )
        )
        
        self.active_monitors[payment_id] = monitor_task
        
        return payment_id
    
    async def _monitor_payment_with_memo(self, payment_request: Dict, 
                                       on_success_callback, on_failure_callback):
        """Monitor payment with priority on memo matching"""
        
        payment_id = payment_request['payment_id']
        memo = payment_request['memo']
        expected_amount = payment_request['amount_ton']
        user_wallet = payment_request['user_wallet']
        
        # Monitoring parameters
        timeout_minutes = 20
        check_interval = 30  # Check every 30 seconds
        max_checks = (timeout_minutes * 60) // check_interval
        
        logger.info(f"Monitoring payment {payment_id} for {timeout_minutes} minutes")
        
        for check_num in range(max_checks):
            try:
                # Check for incoming transactions
                transactions = await self._get_incoming_transactions()
                
                # Look for matching transaction with memo priority
                matching_transaction = await self._find_matching_transaction(
                    transactions, memo, expected_amount, user_wallet
                )
                
                if matching_transaction:
                    logger.info(f"✅ Payment confirmed: {payment_id} with memo: {memo}")
                    
                    # Update timeline - blockchain monitoring completed, start verification
                    if TIMELINE_AVAILABLE:
                        try:
                            await update_payment_timeline(
                                payment_id, 
                                TIMELINE_STEPS['BLOCKCHAIN_MONITORING'], 
                                TimelineStepStatus.COMPLETED
                            )
                            await update_payment_timeline(
                                payment_id, 
                                TIMELINE_STEPS['PAYMENT_VERIFICATION'], 
                                TimelineStepStatus.IN_PROGRESS
                            )
                        except Exception as e:
                            logger.error(f"Error updating timeline: {e}")
                    
                    # Call success callback
                    await on_success_callback(payment_request, matching_transaction)
                    
                    # Update timeline - verification completed, start campaign activation
                    if TIMELINE_AVAILABLE:
                        try:
                            await update_payment_timeline(
                                payment_id, 
                                TIMELINE_STEPS['PAYMENT_VERIFICATION'], 
                                TimelineStepStatus.COMPLETED
                            )
                            await update_payment_timeline(
                                payment_id, 
                                TIMELINE_STEPS['CAMPAIGN_ACTIVATION'], 
                                TimelineStepStatus.IN_PROGRESS
                            )
                            # Complete timeline after short delay
                            await asyncio.sleep(2)
                            await complete_payment_timeline(payment_id, success=True)
                        except Exception as e:
                            logger.error(f"Error completing timeline: {e}")
                    
                    # Remove from active monitors
                    if payment_id in self.active_monitors:
                        del self.active_monitors[payment_id]
                    
                    return
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring payment {payment_id}: {e}")
                await asyncio.sleep(check_interval)
        
        # Payment timed out
        logger.warning(f"⏰ Payment timeout: {payment_id} with memo: {memo}")
        
        # Update timeline - monitoring failed
        if TIMELINE_AVAILABLE:
            try:
                await update_payment_timeline(
                    payment_id, 
                    TIMELINE_STEPS['BLOCKCHAIN_MONITORING'], 
                    TimelineStepStatus.FAILED,
                    error_message="Payment timeout - no matching transaction found"
                )
                await complete_payment_timeline(payment_id, success=False)
            except Exception as e:
                logger.error(f"Error updating timeline for timeout: {e}")
        
        await on_failure_callback(payment_request, "timeout")
        
        # Remove from active monitors
        if payment_id in self.active_monitors:
            del self.active_monitors[payment_id]
    
    async def _get_incoming_transactions(self) -> List[TONTransaction]:
        """Get recent incoming transactions to bot wallet"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get transactions from TON Center API
                url = f"{self.ton_api_base}/getTransactions"
                params = {
                    'address': self.bot_wallet_address,
                    'limit': 50,
                    'to_lt': 0,
                    'archival': True
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = []
                        
                        for tx in data.get('result', []):
                            # Parse transaction data
                            in_msg = tx.get('in_msg', {})
                            
                            if in_msg and in_msg.get('value', 0) > 0:
                                # Extract transaction details
                                amount = float(in_msg.get('value', 0)) / 1_000_000_000  # Convert from nanotons
                                sender = in_msg.get('source', '')
                                memo = self._extract_memo_from_transaction(tx)
                                timestamp = datetime.fromtimestamp(tx.get('utime', 0))
                                
                                transaction = TONTransaction(
                                    hash=tx.get('transaction_id', {}).get('hash', ''),
                                    amount=amount,
                                    sender=sender,
                                    recipient=self.bot_wallet_address,
                                    memo=memo,
                                    timestamp=timestamp
                                )
                                
                                transactions.append(transaction)
                        
                        return transactions
                    else:
                        logger.error(f"Error fetching transactions: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting incoming transactions: {e}")
            return []
    
    def _extract_memo_from_transaction(self, transaction: dict) -> str:
        """Extract memo/comment from transaction data"""
        try:
            # Check various possible locations for memo/comment
            in_msg = transaction.get('in_msg', {})
            
            # Check decoded_body for comment
            decoded_body = in_msg.get('decoded_body', {})
            if decoded_body and decoded_body.get('comment'):
                return decoded_body['comment'].strip()
            
            # Check msg_data for comment
            msg_data = in_msg.get('msg_data', {})
            if msg_data and msg_data.get('text'):
                return msg_data['text'].strip()
            
            # Check raw message for comment
            if in_msg.get('message'):
                return in_msg['message'].strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting memo: {e}")
            return ""
    
    async def _find_matching_transaction(self, transactions: List[TONTransaction], 
                                       expected_memo: str, expected_amount: float, 
                                       user_wallet: str) -> Optional[TONTransaction]:
        """Find transaction matching memo with optional wallet verification"""
        
        # Recent transactions only (last 30 minutes)
        recent_threshold = datetime.now() - timedelta(minutes=30)
        
        for transaction in transactions:
            # Skip old transactions
            if transaction.timestamp < recent_threshold:
                continue
            
            # Primary matching: Check memo/note
            memo_match = self._is_memo_match(transaction.memo, expected_memo)
            
            if memo_match:
                logger.info(f"🎯 Memo match found: {transaction.memo} == {expected_memo}")
                
                # Secondary verification: Amount check (with small tolerance)
                amount_match = self._is_amount_match(transaction.amount, expected_amount)
                
                if amount_match:
                    logger.info(f"💰 Amount match: {transaction.amount} ≈ {expected_amount}")
                    
                    # CRITICAL: Wallet address verification (mandatory for security)
                    wallet_match = self._is_wallet_match(transaction.sender, user_wallet)
                    
                    if wallet_match:
                        logger.info(f"🔒 Wallet match: {transaction.sender} == {user_wallet}")
                        return transaction
                    else:
                        # SECURITY ENHANCEMENT: Reject payment if wallet doesn't match
                        logger.error(f"🚨 SECURITY ALERT: Wallet mismatch for memo {expected_memo}")
                        logger.error(f"   Expected wallet: {user_wallet}")
                        logger.error(f"   Actual sender: {transaction.sender}")
                        logger.error(f"   Amount: {transaction.amount} TON")
                        logger.error(f"   Transaction hash: {transaction.hash}")
                        
                        # Log potential fraud attempt
                        await self._log_potential_fraud(transaction, expected_memo, user_wallet)
                        
                        # Do not proceed - reject payment for security
                        continue
                else:
                    logger.warning(f"❌ Amount mismatch: {transaction.amount} != {expected_amount}")
            else:
                logger.debug(f"❌ Memo mismatch: '{transaction.memo}' != '{expected_memo}'")
        
        return None
    
    def _is_memo_match(self, transaction_memo: str, expected_memo: str) -> bool:
        """Check if memo matches (case-insensitive, whitespace-tolerant)"""
        if not transaction_memo or not expected_memo:
            return False
        
        # Clean and normalize memo strings
        clean_tx_memo = re.sub(r'\s+', '', transaction_memo.upper())
        clean_expected_memo = re.sub(r'\s+', '', expected_memo.upper())
        
        return clean_tx_memo == clean_expected_memo
    
    def _is_amount_match(self, transaction_amount: float, expected_amount: float, 
                        tolerance: float = 0.01) -> bool:
        """Check if amount matches within tolerance"""
        return abs(transaction_amount - expected_amount) <= tolerance
    
    def _is_wallet_match(self, transaction_sender: str, user_wallet: str) -> bool:
        """Check if wallet addresses match (with address normalization)"""
        if not transaction_sender or not user_wallet:
            return False
        
        # Normalize wallet addresses (handle EQ/UQ prefixes)
        normalized_sender = self._normalize_wallet_address(transaction_sender)
        normalized_user_wallet = self._normalize_wallet_address(user_wallet)
        
        return normalized_sender == normalized_user_wallet
    
    def _normalize_wallet_address(self, address: str) -> str:
        """Normalize wallet address by converting EQ prefix to UQ"""
        if not address:
            return ""
        
        # Convert EQ prefix to UQ for consistency
        if address.startswith('EQ'):
            return 'UQ' + address[2:]
        
        return address
    
    async def cancel_payment_monitoring(self, payment_id: str):
        """Cancel active payment monitoring"""
        if payment_id in self.active_monitors:
            self.active_monitors[payment_id].cancel()
            del self.active_monitors[payment_id]
            logger.info(f"Cancelled payment monitoring for {payment_id}")
    
    async def get_payment_status(self, payment_id: str) -> Dict:
        """Get current payment status"""
        if payment_id in self.active_monitors:
            return {
                'payment_id': payment_id,
                'status': 'monitoring',
                'active': True
            }
        else:
            return {
                'payment_id': payment_id,
                'status': 'completed_or_expired',
                'active': False
            }
    
    def get_active_monitors_count(self) -> int:
        """Get number of active payment monitors"""
        return len(self.active_monitors)
    
    async def _log_potential_fraud(self, transaction: TONTransaction, expected_memo: str, expected_wallet: str):
        """Log potential fraud attempt for security monitoring"""
        try:
            fraud_log = {
                'timestamp': datetime.now().isoformat(),
                'type': 'wallet_mismatch_fraud_attempt',
                'transaction_hash': transaction.hash,
                'transaction_amount': transaction.amount,
                'transaction_sender': transaction.sender,
                'transaction_memo': transaction.memo,
                'expected_memo': expected_memo,
                'expected_wallet': expected_wallet,
                'risk_level': 'HIGH',
                'status': 'blocked'
            }
            
            # Log to system logger
            logger.error(f"🚨 FRAUD ATTEMPT BLOCKED: {fraud_log}")
            
            # Store in database for admin review (if database available)
            try:
                from database import db
                await db.log_fraud_attempt(fraud_log)
            except Exception as db_error:
                logger.warning(f"Could not store fraud log in database: {db_error}")
            
            # Send alert to admin (if available)
            await self._send_fraud_alert_to_admin(fraud_log)
            
        except Exception as e:
            logger.error(f"Error logging fraud attempt: {e}")
    
    async def _send_fraud_alert_to_admin(self, fraud_log: dict):
        """Send fraud alert to admin users"""
        try:
            from config import ADMIN_IDS
            from main_bot import bot
            
            if not ADMIN_IDS:
                return
            
            alert_message = f"""🚨 **SECURITY ALERT - Payment Fraud Attempt Blocked**

**Transaction Details:**
• Hash: `{fraud_log['transaction_hash']}`
• Amount: {fraud_log['transaction_amount']} TON
• Sender: `{fraud_log['transaction_sender']}`
• Memo: `{fraud_log['transaction_memo']}`

**Expected Details:**
• Memo: `{fraud_log['expected_memo']}`
• Wallet: `{fraud_log['expected_wallet']}`

**Risk Level:** {fraud_log['risk_level']}
**Status:** Payment blocked and rejected

**Action Required:** Review transaction for potential fraud pattern."""
            
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(chat_id=admin_id, text=alert_message, parse_mode='Markdown')
                except Exception as send_error:
                    logger.error(f"Failed to send fraud alert to admin {admin_id}: {send_error}")
                    
        except Exception as e:
            logger.error(f"Error sending fraud alert: {e}")
    
    async def validate_payment_security(self, payment_request: Dict) -> Dict:
        """Validate payment request security parameters"""
        security_checks = {
            'memo_format': False,
            'wallet_format': False,
            'amount_valid': False,
            'expiration_valid': False,
            'user_wallet_required': False,
            'overall_secure': False
        }
        
        try:
            # Check memo format (2 letters + 4 digits)
            memo = payment_request.get('memo', '')
            import re
            security_checks['memo_format'] = bool(re.match(r'^[A-Z]{2}\d{4}$', memo))
            
            # Check wallet format
            user_wallet = payment_request.get('user_wallet', '')
            security_checks['wallet_format'] = bool(user_wallet and (
                user_wallet.startswith('UQ') or user_wallet.startswith('EQ')
            ) and len(user_wallet) >= 48)
            
            # Check amount validity
            amount = payment_request.get('amount_ton', 0)
            security_checks['amount_valid'] = amount > 0
            
            # Check expiration validity
            expires_at = payment_request.get('expires_at', '')
            if expires_at:
                from datetime import datetime
                expiry_time = datetime.fromisoformat(expires_at)
                security_checks['expiration_valid'] = expiry_time > datetime.now()
            
            # Check user wallet requirement
            security_checks['user_wallet_required'] = bool(user_wallet)
            
            # Overall security assessment
            security_checks['overall_secure'] = all([
                security_checks['memo_format'],
                security_checks['wallet_format'],
                security_checks['amount_valid'],
                security_checks['expiration_valid'],
                security_checks['user_wallet_required']
            ])
            
        except Exception as e:
            logger.error(f"Error validating payment security: {e}")
        
        return security_checks

# Global instance
enhanced_ton_payment_system = None

def get_enhanced_ton_payment_system(bot_wallet_address: str) -> EnhancedTONPaymentSystem:
    """Get or create enhanced TON payment system instance"""
    global enhanced_ton_payment_system
    
    if enhanced_ton_payment_system is None:
        enhanced_ton_payment_system = EnhancedTONPaymentSystem(bot_wallet_address)
    
    return enhanced_ton_payment_system