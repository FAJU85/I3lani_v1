"""
Payment Memo Tracker for I3lani Bot
Handles payment memo tracking and user identification
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from database import db

logger = logging.getLogger(__name__)

class PaymentMemoTracker:
    """Tracks payment memos and links them to users"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize payment memo tracker"""
        if self.initialized:
            return
        
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            # Create payment_memo_tracking table if it doesn't exist
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment_memo_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memo TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    campaign_id TEXT,
                    processed_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            await connection.commit()
            await connection.close()
            
            self.initialized = True
            logger.info("✅ Payment memo tracker initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize payment memo tracker: {e}")
            raise
    
    async def track_payment_memo(self, memo: str, user_id: int, amount: float) -> bool:
        """Track a payment memo with user ID"""
        try:
            await self.initialize()
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            # Insert or update payment memo tracking
            await cursor.execute('''
                INSERT OR REPLACE INTO payment_memo_tracking 
                (memo, user_id, amount, status, timestamp)
                VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)
            ''', (memo, user_id, amount))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Tracked payment memo {memo} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error tracking payment memo {memo}: {e}")
            return False
    
    async def get_user_by_memo(self, memo: str) -> Optional[int]:
        """Get user ID associated with payment memo"""
        try:
            await self.initialize()
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute(
                "SELECT user_id FROM payment_memo_tracking WHERE memo = ?",
                (memo,)
            )
            
            result = await cursor.fetchone()
            await connection.close()
            
            if result:
                return result[0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user by memo {memo}: {e}")
            return None
    
    async def mark_payment_processed(self, memo: str, campaign_id: str = None) -> bool:
        """Mark payment as processed"""
        try:
            await self.initialize()
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                UPDATE payment_memo_tracking 
                SET status = 'processed', 
                    processed_at = CURRENT_TIMESTAMP,
                    campaign_id = ?
                WHERE memo = ?
            ''', (campaign_id, memo))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Marked payment {memo} as processed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking payment {memo} as processed: {e}")
            return False
    
    async def get_pending_payments(self) -> list:
        """Get all pending payment memos"""
        try:
            await self.initialize()
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                SELECT memo, user_id, amount, timestamp 
                FROM payment_memo_tracking 
                WHERE status = 'pending'
                ORDER BY timestamp ASC
            ''')
            
            results = await cursor.fetchall()
            await connection.close()
            
            return [
                {
                    'memo': row[0],
                    'user_id': row[1], 
                    'amount': row[2],
                    'timestamp': row[3]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"❌ Error getting pending payments: {e}")
            return []

# Global instance
memo_tracker = PaymentMemoTracker()

async def init_payment_memo_tracker():
    """Initialize payment memo tracker"""
    await memo_tracker.initialize()

def get_payment_memo_tracker():
    """Get payment memo tracker instance"""
    return memo_tracker