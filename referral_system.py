#!/usr/bin/env python3
"""
Comprehensive Referral System for I3lani Bot
Implements passive income through referrals with TON rewards
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from automatic_language_system import get_user_language_auto
from languages import get_text

logger = logging.getLogger(__name__)

class ReferralSystem:
    """Complete referral system with TON rewards and passive income"""
    
    def __init__(self):
        self.signup_bonus = Decimal('0.00010000')  # 0.00010000 TON
        self.commission_rate = Decimal('0.20')  # 20% commission
        self.min_withdrawal = Decimal('0.001')  # Minimum withdrawal amount
        
    async def initialize_database(self):
        """Initialize referral system database tables"""
        try:
            from database import db
            
            # Create referral_users table
            await db.execute_query('''
                CREATE TABLE IF NOT EXISTS referral_users (
                    user_id INTEGER PRIMARY KEY,
                    referral_code TEXT UNIQUE NOT NULL,
                    referred_by INTEGER,
                    signup_bonus_claimed BOOLEAN DEFAULT FALSE,
                    total_earnings DECIMAL(20,8) DEFAULT 0.0,
                    available_balance DECIMAL(20,8) DEFAULT 0.0,
                    total_withdrawn DECIMAL(20,8) DEFAULT 0.0,
                    referral_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_earning_at TIMESTAMP,
                    ton_wallet_address TEXT,
                    FOREIGN KEY (referred_by) REFERENCES referral_users(user_id)
                )
            ''')
            
            # Create referral_earnings table
            await db.execute_query('''
                CREATE TABLE IF NOT EXISTS referral_earnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    referred_user_id INTEGER NOT NULL,
                    earning_type TEXT NOT NULL,
                    amount DECIMAL(20,8) NOT NULL,
                    source_transaction TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES referral_users(user_id),
                    FOREIGN KEY (referred_user_id) REFERENCES referral_users(user_id)
                )
            ''')
            
            # Create referral_withdrawals table
            await db.execute_query('''
                CREATE TABLE IF NOT EXISTS referral_withdrawals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount DECIMAL(20,8) NOT NULL,
                    ton_wallet_address TEXT NOT NULL,
                    transaction_hash TEXT,
                    status TEXT DEFAULT 'pending',
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES referral_users(user_id)
                )
            ''')
            
            # Create referral_analytics table
            await db.execute_query('''
                CREATE TABLE IF NOT EXISTS referral_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    new_referrals INTEGER DEFAULT 0,
                    total_signups INTEGER DEFAULT 0,
                    total_earnings DECIMAL(20,8) DEFAULT 0.0,
                    total_withdrawals DECIMAL(20,8) DEFAULT 0.0,
                    top_referrer_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            logger.info("✅ Referral system database initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing referral database: {e}")
            return False
    
    async def register_user(self, user_id: int, referrer_code: str = None) -> bool:
        """Register user in referral system"""
        try:
            from database import db
            
            # Generate referral code
            referral_code = f"ref_{user_id}"
            
            # Check if user already exists
            existing = await db.fetchone(
                "SELECT user_id FROM referral_users WHERE user_id = ?",
                (user_id,)
            )
            
            if existing:
                logger.info(f"User {user_id} already registered in referral system")
                return True
            
            # Find referrer if referrer_code provided
            referrer_id = None
            if referrer_code and referrer_code.startswith('ref_'):
                try:
                    referrer_id = int(referrer_code.replace('ref_', ''))
                    # Validate referrer exists and is not the same user
                    if referrer_id != user_id:
                        referrer_exists = await db.fetchone(
                            "SELECT user_id FROM referral_users WHERE user_id = ?",
                            (referrer_id,)
                        )
                        if not referrer_exists:
                            referrer_id = None
                    else:
                        referrer_id = None  # Prevent self-referral
                except ValueError:
                    referrer_id = None
            
            # Insert new user
            await db.execute_query('''
                INSERT INTO referral_users 
                (user_id, referral_code, referred_by, signup_bonus_claimed, available_balance)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, referral_code, referrer_id, False, 0.0))
            
            # Give signup bonus if referred
            if referrer_id:
                await self._give_signup_bonus(user_id)
                await self._update_referrer_stats(referrer_id)
            
            logger.info(f"✅ User {user_id} registered in referral system (referrer: {referrer_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registering user {user_id}: {e}")
            return False
    
    async def _give_signup_bonus(self, user_id: int) -> bool:
        """Give signup bonus to new referred user"""
        try:
            from database import db
            
            # Update user balance
            await db.execute_query('''
                UPDATE referral_users 
                SET signup_bonus_claimed = TRUE,
                    available_balance = available_balance + ?,
                    total_earnings = total_earnings + ?
                WHERE user_id = ?
            ''', (float(self.signup_bonus), float(self.signup_bonus), user_id))
            
            # Log earning
            await db.execute_query('''
                INSERT INTO referral_earnings 
                (referrer_id, referred_user_id, earning_type, amount)
                VALUES (?, ?, 'signup_bonus', ?)
            ''', (user_id, user_id, float(self.signup_bonus)))
            
            logger.info(f"✅ Signup bonus {self.signup_bonus} TON given to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error giving signup bonus to {user_id}: {e}")
            return False
    
    async def _update_referrer_stats(self, referrer_id: int) -> bool:
        """Update referrer's referral count"""
        try:
            from database import db
            
            await db.execute_query('''
                UPDATE referral_users 
                SET referral_count = referral_count + 1
                WHERE user_id = ?
            ''', (referrer_id,))
            
            logger.info(f"✅ Updated referrer {referrer_id} stats")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating referrer {referrer_id} stats: {e}")
            return False
    
    async def process_referral_commission(self, user_id: int, earning_amount: Decimal, source: str = None) -> bool:
        """Process referral commission when user earns money"""
        try:
            from database import db
            
            # Get user's referrer
            referrer_data = await db.fetchone('''
                SELECT referred_by FROM referral_users 
                WHERE user_id = ? AND referred_by IS NOT NULL
            ''', (user_id,))
            
            if not referrer_data:
                return True  # No referrer, no commission
            
            referrer_id = referrer_data[0]
            commission_amount = earning_amount * self.commission_rate
            
            # Update referrer's balance
            await db.execute_query('''
                UPDATE referral_users 
                SET available_balance = available_balance + ?,
                    total_earnings = total_earnings + ?,
                    last_earning_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (float(commission_amount), float(commission_amount), referrer_id))
            
            # Log commission earning
            await db.execute_query('''
                INSERT INTO referral_earnings 
                (referrer_id, referred_user_id, earning_type, amount, source_transaction)
                VALUES (?, ?, 'commission', ?, ?)
            ''', (referrer_id, user_id, float(commission_amount), source))
            
            logger.info(f"✅ Commission {commission_amount} TON paid to referrer {referrer_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing referral commission: {e}")
            return False
    
    async def get_user_referral_data(self, user_id: int) -> Dict:
        """Get complete referral data for user"""
        try:
            from database import db
            
            # Get main referral data
            user_data = await db.fetchone('''
                SELECT referral_code, referred_by, signup_bonus_claimed,
                       total_earnings, available_balance, total_withdrawn,
                       referral_count, ton_wallet_address
                FROM referral_users WHERE user_id = ?
            ''', (user_id,))
            
            if not user_data:
                await self.register_user(user_id)
                return await self.get_user_referral_data(user_id)
            
            # Get referral earnings history
            earnings = await db.fetchall('''
                SELECT earning_type, amount, created_at, source_transaction
                FROM referral_earnings 
                WHERE referrer_id = ? 
                ORDER BY created_at DESC LIMIT 10
            ''', (user_id,))
            
            # Get referred users
            referred_users = await db.fetchall('''
                SELECT user_id, total_earnings, created_at
                FROM referral_users 
                WHERE referred_by = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            return {
                'referral_code': user_data[0],
                'referred_by': user_data[1],
                'signup_bonus_claimed': user_data[2],
                'total_earnings': Decimal(str(user_data[3])),
                'available_balance': Decimal(str(user_data[4])),
                'total_withdrawn': Decimal(str(user_data[5])),
                'referral_count': user_data[6],
                'ton_wallet_address': user_data[7],
                'recent_earnings': earnings,
                'referred_users': referred_users
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting referral data for {user_id}: {e}")
            return {
                'referral_code': f'ref_{user_id}',
                'referred_by': None,
                'signup_bonus_claimed': False,
                'total_earnings': 0,
                'available_balance': 0,
                'total_withdrawn': 0,
                'referral_count': 0,
                'ton_wallet_address': None,
                'recent_earnings': [],
                'referred_users': []
            }
    
    async def get_referral_link(self, user_id: int, bot_username: str) -> str:
        """Get user's referral link"""
        referral_code = f"ref_{user_id}"
        return f"https://t.me/{bot_username}?start={referral_code}"
    
    async def set_wallet_address(self, user_id: int, wallet_address: str) -> bool:
        """Set user's TON wallet address"""
        try:
            from database import db
            
            await db.execute_query('''
                UPDATE referral_users 
                SET ton_wallet_address = ?
                WHERE user_id = ?
            ''', (wallet_address, user_id))
            
            logger.info(f"✅ Wallet address set for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting wallet address: {e}")
            return False
    
    async def process_withdrawal(self, user_id: int, amount: Decimal) -> Tuple[bool, str]:
        """Process withdrawal request"""
        try:
            from database import db
            
            # Get user data
            user_data = await db.fetchone('''
                SELECT available_balance, ton_wallet_address
                FROM referral_users WHERE user_id = ?
            ''', (user_id,))
            
            if not user_data:
                return False, "User not found in referral system"
            
            available_balance = Decimal(str(user_data[0]))
            wallet_address = user_data[1]
            
            # Validate withdrawal
            if not wallet_address:
                return False, "Please set your TON wallet address first"
            
            if amount < self.min_withdrawal:
                return False, f"Minimum withdrawal amount is {self.min_withdrawal} TON"
            
            if amount > available_balance:
                return False, f"Insufficient balance. Available: {available_balance} TON"
            
            # Create withdrawal request
            await db.execute_query('''
                INSERT INTO referral_withdrawals 
                (user_id, amount, ton_wallet_address, status)
                VALUES (?, ?, ?, 'pending')
            ''', (user_id, float(amount), wallet_address))
            
            # Update user balance
            await db.execute_query('''
                UPDATE referral_users 
                SET available_balance = available_balance - ?,
                    total_withdrawn = total_withdrawn + ?
                WHERE user_id = ?
            ''', (float(amount), float(amount), user_id))
            
            logger.info(f"✅ Withdrawal request created: {amount} TON for user {user_id}")
            return True, "Withdrawal request submitted successfully"
            
        except Exception as e:
            logger.error(f"❌ Error processing withdrawal: {e}")
            return False, "Error processing withdrawal request"
    
    async def get_top_referrers(self, limit: int = 10) -> List[Dict]:
        """Get top referrers by earnings"""
        try:
            from database import db
            
            top_referrers = await db.fetchall('''
                SELECT user_id, total_earnings, referral_count, available_balance
                FROM referral_users 
                WHERE referral_count > 0
                ORDER BY total_earnings DESC 
                LIMIT ?
            ''', (limit,))
            
            return [
                {
                    'user_id': row[0],
                    'total_earnings': Decimal(str(row[1])),
                    'referral_count': row[2],
                    'available_balance': Decimal(str(row[3]))
                }
                for row in top_referrers
            ]
            
        except Exception as e:
            logger.error(f"❌ Error getting top referrers: {e}")
            return []
    
    async def get_system_analytics(self) -> Dict:
        """Get referral system analytics"""
        try:
            from database import db
            
            # Total users
            total_users = await db.fetchone(
                "SELECT COUNT(*) FROM referral_users"
            )
            
            # Total earnings distributed
            total_earnings = await db.fetchone(
                "SELECT SUM(total_earnings) FROM referral_users"
            )
            
            # Total withdrawals
            total_withdrawals = await db.fetchone(
                "SELECT SUM(amount) FROM referral_withdrawals WHERE status = 'completed'"
            )
            
            # Active referrers
            active_referrers = await db.fetchone(
                "SELECT COUNT(*) FROM referral_users WHERE referral_count > 0"
            )
            
            # Pending withdrawals
            pending_withdrawals = await db.fetchone(
                "SELECT COUNT(*) FROM referral_withdrawals WHERE status = 'pending'"
            )
            
            return {
                'total_users': total_users[0] if total_users else 0,
                'total_earnings_distributed': Decimal(str(total_earnings[0])) if total_earnings[0] else Decimal('0'),
                'total_withdrawals': Decimal(str(total_withdrawals[0])) if total_withdrawals[0] else Decimal('0'),
                'active_referrers': active_referrers[0] if active_referrers else 0,
                'pending_withdrawals': pending_withdrawals[0] if pending_withdrawals else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system analytics: {e}")
            return {}

# Global referral system instance
referral_system = ReferralSystem()

async def get_referral_system() -> ReferralSystem:
    """Get referral system instance"""
    return referral_system