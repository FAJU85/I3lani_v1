#!/usr/bin/env python3
"""
Payment Memo Tracker
System to track memo -> user_id mappings for payment confirmations
"""

import asyncio
import logging
import sqlite3
import json
from typing import Optional, Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentMemoTracker:
    """Track payment memos and user mappings"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        
    async def init_tables(self):
        """Initialize payment memo tracking tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create payment_memos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_memos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    memo TEXT NOT NULL UNIQUE,
                    amount REAL NOT NULL,
                    payment_method TEXT DEFAULT 'TON',
                    status TEXT DEFAULT 'pending',
                    ad_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confirmed_at TIMESTAMP NULL
                );
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_payment_memos_memo 
                ON payment_memos(memo);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_payment_memos_user_id 
                ON payment_memos(user_id);
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Payment memo tracking tables initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing payment memo tables: {e}")
            return False
    
    async def store_payment_memo(self, user_id: int, memo: str, amount: float, 
                                ad_data: dict = None, payment_method: str = 'TON'):
        """Store payment memo with user information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store ad_data as JSON string
            ad_data_json = json.dumps(ad_data) if ad_data else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO payment_memos 
                (user_id, memo, amount, payment_method, ad_data, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (user_id, memo, amount, payment_method, ad_data_json))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Stored payment memo {memo} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing payment memo: {e}")
            return False
    
    async def get_user_by_memo(self, memo: str) -> Optional[Dict[str, Any]]:
        """Get user information by payment memo"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, memo, amount, payment_method, ad_data, status, created_at
                FROM payment_memos 
                WHERE memo = ? AND status = 'pending'
            """, (memo,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Parse ad_data JSON
                ad_data = json.loads(row['ad_data']) if row['ad_data'] else {}
                
                return {
                    'user_id': row['user_id'],
                    'memo': row['memo'],
                    'amount': row['amount'],
                    'payment_method': row['payment_method'],
                    'ad_data': ad_data,
                    'status': row['status'],
                    'created_at': row['created_at']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user by memo: {e}")
            return None
    
    async def confirm_payment(self, memo: str) -> bool:
        """Mark payment as confirmed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE payment_memos 
                SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
                WHERE memo = ?
            """, (memo,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Payment {memo} marked as confirmed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error confirming payment: {e}")
            return False
    
    async def get_pending_payments(self) -> list:
        """Get all pending payments"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, memo, amount, payment_method, ad_data, created_at
                FROM payment_memos 
                WHERE status = 'pending'
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            payments = []
            for row in rows:
                ad_data = json.loads(row['ad_data']) if row['ad_data'] else {}
                payments.append({
                    'user_id': row['user_id'],
                    'memo': row['memo'],
                    'amount': row['amount'],
                    'payment_method': row['payment_method'],
                    'ad_data': ad_data,
                    'created_at': row['created_at']
                })
            
            return payments
            
        except Exception as e:
            logger.error(f"❌ Error getting pending payments: {e}")
            return []

# Global instance
memo_tracker = PaymentMemoTracker()

async def init_payment_memo_tracker():
    """Initialize the payment memo tracker"""
    return await memo_tracker.init_tables()

# Test function
async def test_payment_memo_tracker():
    """Test the payment memo tracker"""
    print("🧪 Testing Payment Memo Tracker")
    print("=" * 50)
    
    # Initialize tables
    success = await memo_tracker.init_tables()
    print(f"Table initialization: {'✅' if success else '❌'}")
    
    # Test storing a memo
    test_ad_data = {
        'ad_text': 'Test advertisement',
        'selected_channels': ['channel1', 'channel2'],
        'days': 7,
        'posts_per_day': 2
    }
    
    success = await memo_tracker.store_payment_memo(
        user_id=123456,
        memo='TEST01',
        amount=0.36,
        ad_data=test_ad_data
    )
    print(f"Store memo: {'✅' if success else '❌'}")
    
    # Test retrieving user by memo
    user_info = await memo_tracker.get_user_by_memo('TEST01')
    print(f"Retrieve user: {'✅' if user_info else '❌'}")
    
    if user_info:
        print(f"   User ID: {user_info['user_id']}")
        print(f"   Memo: {user_info['memo']}")
        print(f"   Amount: {user_info['amount']}")
        print(f"   Ad data: {user_info['ad_data']}")
    
    # Test confirming payment
    success = await memo_tracker.confirm_payment('TEST01')
    print(f"Confirm payment: {'✅' if success else '❌'}")
    
    # Test getting pending payments
    pending = await memo_tracker.get_pending_payments()
    print(f"Pending payments: {len(pending)} found")
    
    print("✅ Payment memo tracker test completed")

if __name__ == "__main__":
    asyncio.run(test_payment_memo_tracker())