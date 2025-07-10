#!/usr/bin/env python3
"""
Enhanced TON Payment Monitoring System
Comprehensive fix for automatic payment verification issues
"""

import asyncio
import time
import requests
import json
import logging
from typing import Optional, Dict, Any, List
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

class EnhancedTONPaymentMonitor:
    """Enhanced TON payment monitoring with multiple API endpoints and robust error handling"""
    
    def __init__(self):
        self.api_endpoints = [
            "https://toncenter.com/api/v2/getTransactions",
            "https://tonapi.io/v2/blockchain/accounts/{}/transactions",
            "https://tonapi.io/v1/blockchain/getTransactions"
        ]
        self.current_endpoint = 0
        self.max_retries = 3
        self.request_timeout = 20
        
    def normalize_wallet_address(self, address: str) -> str:
        """Normalize TON wallet address properly"""
        if not address:
            return address
            
        address = address.strip()
        
        # TON addresses can be in different formats:
        # - Raw format: 0:hex...
        # - User-friendly format: EQ/UQ + base64
        # For comparison, we need to handle both formats
        
        # Convert EQ to UQ for user-friendly format (this is NOT correct - keeping both)
        # Actually, EQ and UQ are different formats and should be handled separately
        return address
    
    def convert_address_formats(self, address: str) -> List[str]:
        """Convert address to all possible formats for comparison"""
        if not address:
            return []
            
        formats = [address.strip()]
        
        # If it's EQ format, also check UQ format and vice versa
        if address.startswith('EQ'):
            uq_format = 'UQ' + address[2:]
            formats.append(uq_format)
        elif address.startswith('UQ'):
            eq_format = 'EQ' + address[2:]
            formats.append(eq_format)
            
        return formats
    
    async def get_transactions_toncenter(self, bot_wallet: str, limit: int = 100) -> Optional[Dict]:
        """Get transactions using TON Center API"""
        try:
            url = f"https://toncenter.com/api/v2/getTransactions?address={bot_wallet}&limit={limit}&archival=true"
            
            response = requests.get(url, timeout=self.request_timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data
                else:
                    logger.warning(f"TON Center API returned error: {data}")
            else:
                logger.warning(f"TON Center API request failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error calling TON Center API: {e}")
            
        return None
    
    async def get_transactions_tonapi(self, bot_wallet: str, limit: int = 100) -> Optional[Dict]:
        """Get transactions using TON API"""
        try:
            url = f"https://tonapi.io/v2/blockchain/accounts/{bot_wallet}/transactions?limit={limit}"
            
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'I3lani-Bot/1.0'
            }
            
            response = requests.get(url, headers=headers, timeout=self.request_timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.warning(f"TON API request failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error calling TON API: {e}")
            
        return None
    
    def extract_memo_from_transaction(self, tx: Dict) -> Optional[str]:
        """Extract memo from transaction with multiple fallback methods"""
        memo = None
        
        try:
            # Method 1: TON Center API format
            if tx.get('in_msg'):
                in_msg = tx['in_msg']
                
                # Check direct message field
                if 'message' in in_msg:
                    memo = in_msg['message']
                
                # Check decoded body
                elif 'decoded' in in_msg and 'body' in in_msg['decoded']:
                    memo = in_msg['decoded']['body']
                
                # Check msg_data
                elif 'msg_data' in in_msg:
                    msg_data = in_msg['msg_data']
                    if isinstance(msg_data, dict) and 'text' in msg_data:
                        memo = msg_data['text']
            
            # Method 2: TON API format
            elif tx.get('in_msg') and tx['in_msg'].get('decoded_body'):
                decoded = tx['in_msg']['decoded_body']
                if isinstance(decoded, dict) and 'comment' in decoded:
                    memo = decoded['comment']
            
            # Method 3: Alternative formats
            elif tx.get('description'):
                description = tx['description']
                if isinstance(description, dict) and 'comment' in description:
                    memo = description['comment']
                    
        except Exception as e:
            logger.error(f"Error extracting memo from transaction: {e}")
            
        return memo.strip() if memo else None
    
    def extract_amount_from_transaction(self, tx: Dict) -> Optional[float]:
        """Extract amount from transaction"""
        try:
            # Method 1: TON Center API format
            if tx.get('in_msg') and 'value' in tx['in_msg']:
                nanotons = int(tx['in_msg']['value'])
                return nanotons / 1000000000
            
            # Method 2: TON API format
            elif tx.get('in_msg') and 'amount' in tx['in_msg']:
                nanotons = int(tx['in_msg']['amount'])
                return nanotons / 1000000000
                
            # Method 3: Alternative format
            elif tx.get('value'):
                nanotons = int(tx['value'])
                return nanotons / 1000000000
                
        except Exception as e:
            logger.error(f"Error extracting amount from transaction: {e}")
            
        return None
    
    def extract_sender_from_transaction(self, tx: Dict) -> Optional[str]:
        """Extract sender address from transaction"""
        try:
            # Method 1: TON Center API format
            if tx.get('in_msg') and 'source' in tx['in_msg']:
                return tx['in_msg']['source']
            
            # Method 2: TON API format
            elif tx.get('in_msg') and 'sender' in tx['in_msg']:
                return tx['in_msg']['sender']
                
            # Method 3: Alternative format
            elif tx.get('from'):
                return tx['from']
                
        except Exception as e:
            logger.error(f"Error extracting sender from transaction: {e}")
            
        return None
    
    async def monitor_payment_enhanced(self, user_id: int, memo: str, amount_ton: float, 
                                     expiration_time: int, user_wallet: str, state: FSMContext,
                                     bot_wallet: str) -> bool:
        """Enhanced payment monitoring with multiple API endpoints and robust error handling"""
        
        check_interval = 30  # Check every 30 seconds
        user_wallet_formats = self.convert_address_formats(user_wallet)
        
        logger.info(f"Starting enhanced TON payment monitoring for user {user_id}")
        logger.info(f"Memo: {memo}, Amount: {amount_ton} TON")
        logger.info(f"Bot wallet: {bot_wallet}")
        logger.info(f"User wallet formats: {user_wallet_formats}")
        
        while time.time() < expiration_time:
            try:
                # Try TON Center API first
                transactions_data = await self.get_transactions_toncenter(bot_wallet)
                
                if not transactions_data:
                    # Fallback to TON API
                    transactions_data = await self.get_transactions_tonapi(bot_wallet)
                
                if not transactions_data:
                    logger.warning("Failed to get transactions from all APIs")
                    await asyncio.sleep(check_interval)
                    continue
                
                # Process transactions
                transactions = transactions_data.get('result', []) or transactions_data.get('transactions', [])
                
                if not transactions:
                    logger.debug(f"No transactions found for {bot_wallet}")
                    await asyncio.sleep(check_interval)
                    continue
                
                # Check each transaction
                for tx in transactions:
                    # Skip if not an incoming transaction
                    if not tx.get('in_msg'):
                        continue
                    
                    # Extract memo
                    tx_memo = self.extract_memo_from_transaction(tx)
                    if not tx_memo or tx_memo != memo:
                        continue
                    
                    # Extract sender
                    sender = self.extract_sender_from_transaction(tx)
                    if not sender:
                        continue
                    
                    # Check if sender matches user wallet (any format)
                    sender_matches = False
                    for user_format in user_wallet_formats:
                        if sender == user_format:
                            sender_matches = True
                            break
                    
                    if not sender_matches:
                        logger.debug(f"Sender {sender} doesn't match user wallet {user_wallet_formats}")
                        continue
                    
                    # Extract amount
                    tx_amount = self.extract_amount_from_transaction(tx)
                    if not tx_amount:
                        continue
                    
                    # Check amount with tolerance
                    amount_tolerance = 0.1  # 0.1 TON tolerance
                    if abs(tx_amount - amount_ton) <= amount_tolerance:
                        # Payment found and verified!
                        logger.info(f"✅ Payment verified: {memo} for {amount_ton} TON from {sender}")
                        logger.info(f"Transaction amount: {tx_amount} TON")
                        
                        # Handle successful payment
                        from handlers import handle_successful_ton_payment_with_confirmation
                        await handle_successful_ton_payment_with_confirmation(user_id, memo, amount_ton, state)
                        return True
                    else:
                        logger.warning(f"Amount mismatch: expected {amount_ton}, got {tx_amount}")
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in payment monitoring loop: {e}")
                await asyncio.sleep(check_interval)
        
        # Payment expired
        logger.warning(f"Payment expired for user {user_id}, memo: {memo}")
        from handlers import handle_expired_ton_payment
        await handle_expired_ton_payment(user_id, memo, state)
        return False

# Create global instance
ton_monitor = EnhancedTONPaymentMonitor()

async def monitor_ton_payment_enhanced(user_id: int, memo: str, amount_ton: float, 
                                     expiration_time: int, user_wallet: str, state: FSMContext,
                                     bot_wallet: str) -> bool:
    """Enhanced payment monitoring function"""
    return await ton_monitor.monitor_payment_enhanced(
        user_id, memo, amount_ton, expiration_time, user_wallet, state, bot_wallet
    )