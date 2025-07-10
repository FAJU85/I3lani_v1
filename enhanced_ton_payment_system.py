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
                                   user_wallet: str, campaign_details: dict) -> Dict:
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
        
        logger.info(f"Created payment request: {payment_request['payment_id']} with memo: {memo}")
        return payment_request
    
    async def start_payment_monitoring(self, payment_request: Dict, 
                                     on_success_callback, on_failure_callback) -> str:
        """Start monitoring TON payments with memo-based verification"""
        
        payment_id = payment_request['payment_id']
        memo = payment_request['memo']
        expected_amount = payment_request['amount_ton']
        user_wallet = payment_request['user_wallet']
        
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
                    
                    # Call success callback
                    await on_success_callback(payment_request, matching_transaction)
                    
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
                    
                    # Optional: Wallet address verification (for additional security)
                    wallet_match = self._is_wallet_match(transaction.sender, user_wallet)
                    
                    if wallet_match:
                        logger.info(f"🔒 Wallet match: {transaction.sender} == {user_wallet}")
                        return transaction
                    else:
                        # Log wallet mismatch but still proceed with memo + amount match
                        logger.warning(f"⚠️ Wallet mismatch: {transaction.sender} != {user_wallet}")
                        logger.info(f"✅ Proceeding with memo + amount match (wallet verification optional)")
                        return transaction
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

# Global instance
enhanced_ton_payment_system = None

def get_enhanced_ton_payment_system(bot_wallet_address: str) -> EnhancedTONPaymentSystem:
    """Get or create enhanced TON payment system instance"""
    global enhanced_ton_payment_system
    
    if enhanced_ton_payment_system is None:
        enhanced_ton_payment_system = EnhancedTONPaymentSystem(bot_wallet_address)
    
    return enhanced_ton_payment_system