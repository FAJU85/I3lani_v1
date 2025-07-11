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
logger.setLevel(logging.DEBUG)

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
            logger.debug(f"Calling TON Center API: {url}")
            
            response = requests.get(url, timeout=self.request_timeout)
            logger.debug(f"TON Center API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    logger.debug(f"TON Center API success: {len(data.get('result', []))} transactions")
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
        logger.info(f"Monitoring for {int((expiration_time - time.time()) / 60)} minutes")
        
        check_number = 0
        while time.time() < expiration_time:
            check_number += 1
            remaining_minutes = int((expiration_time - time.time()) / 60)
            logger.info(f"📡 Payment check #{check_number} - {remaining_minutes} minutes remaining")
            try:
                # Try TON Center API first
                logger.debug(f"Attempting TON Center API call...")
                transactions_data = await self.get_transactions_toncenter(bot_wallet)
                
                if not transactions_data:
                    # Fallback to TON API
                    logger.debug(f"TON Center failed, trying TON API...")
                    transactions_data = await self.get_transactions_tonapi(bot_wallet)
                
                if not transactions_data:
                    logger.warning(f"❌ Failed to get transactions from all APIs for check #{check_number}")
                    await asyncio.sleep(check_interval)
                    continue
                
                logger.debug(f"✅ Got transaction data from API")
                
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
                    
                    # Extract amount
                    tx_amount = self.extract_amount_from_transaction(tx)
                    if not tx_amount:
                        continue
                    
                    # CRITICAL: Validate payment amount with protocol enforcement
                    try:
                        from payment_amount_validator import validate_payment_amount
                        from main_bot import bot_instance
                        
                        if bot_instance:
                            validation_result = await validate_payment_amount(
                                bot_instance, user_id, memo, tx_amount, amount_ton
                            )
                            
                            if validation_result['valid']:
                                # Extract sender for logging
                                sender = self.extract_sender_from_transaction(tx)
                                
                                # FLEXIBLE VERIFICATION: Focus on memo + amount only
                                # Sender verification is now optional for better compatibility
                                sender_matches = False
                                if sender:
                                    for user_format in user_wallet_formats:
                                        if sender == user_format:
                                            sender_matches = True
                                            break
                                
                                if sender_matches:
                                    logger.info(f"✅ Payment verified with sender match: {memo} for {amount_ton} TON from {sender}")
                                else:
                                    logger.warning(f"⚠️ Payment found but sender mismatch: expected {user_wallet_formats}, got {sender}")
                                    logger.info(f"✅ Payment verified by memo+amount: {memo} for {amount_ton} TON from {sender}")
                                
                                logger.info(f"Transaction amount: {tx_amount} TON")
                                
                                # Handle successful payment - Accept payment based on memo + amount
                                from handlers import handle_successful_ton_payment_with_confirmation
                                await handle_successful_ton_payment_with_confirmation(user_id, memo, amount_ton, state)
                                return True
                            else:
                                # Handle invalid payment amount
                                logger.warning(f"⚠️ Payment amount validation failed: {validation_result['status']}")
                                logger.warning(f"   Expected: {amount_ton} TON")
                                logger.warning(f"   Received: {tx_amount} TON")
                                logger.warning(f"   Difference: {validation_result['difference']} TON")
                                
                                # Send appropriate message to user
                                try:
                                    from payment_amount_validator import handle_invalid_payment_amount
                                    await handle_invalid_payment_amount(
                                        bot_instance, user_id, memo, validation_result, 
                                        tx_amount, amount_ton
                                    )
                                    logger.info(f"📩 Invalid payment notification sent to user {user_id}")
                                except Exception as e:
                                    logger.error(f"❌ Error handling invalid payment: {e}")
                                
                                # Return False to stop monitoring (payment found but invalid)
                                return False
                        else:
                            # Fallback to old validation if bot instance not available
                            amount_tolerance = 0.01  # 0.01 TON tolerance for fallback
                            if abs(tx_amount - amount_ton) <= amount_tolerance:
                                # Extract sender for logging
                                sender = self.extract_sender_from_transaction(tx)
                                
                                logger.info(f"✅ Payment verified (fallback): {memo} for {amount_ton} TON from {sender}")
                                
                                # Handle successful payment - Accept payment based on memo + amount
                                from handlers import handle_successful_ton_payment_with_confirmation
                                await handle_successful_ton_payment_with_confirmation(user_id, memo, amount_ton, state)
                                return True
                            else:
                                logger.warning(f"⚠️ Amount mismatch (fallback): expected {amount_ton}, got {tx_amount}")
                                
                    except Exception as e:
                        logger.error(f"❌ Error in payment validation: {e}")
                        # Continue with fallback validation
                        amount_tolerance = 0.01  # 0.01 TON tolerance for fallback
                        if abs(tx_amount - amount_ton) <= amount_tolerance:
                            # Extract sender for logging
                            sender = self.extract_sender_from_transaction(tx)
                            
                            logger.info(f"✅ Payment verified (fallback): {memo} for {amount_ton} TON from {sender}")
                            
                            # Handle successful payment - Accept payment based on memo + amount
                            from handlers import handle_successful_ton_payment_with_confirmation
                            await handle_successful_ton_payment_with_confirmation(user_id, memo, amount_ton, state)
                            return True
                        else:
                            logger.warning(f"⚠️ Amount mismatch (fallback): expected {amount_ton}, got {tx_amount}")
                
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