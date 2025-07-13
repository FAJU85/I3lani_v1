#!/usr/bin/env python3
"""
Global Sequence ID System
Generates unique sequential IDs for all system operations
"""

import logging
from datetime import datetime
from typing import Dict, Optional, List
import asyncio

logger = logging.getLogger(__name__)

class GlobalSequenceIdSystem:
    """Global unique sequence ID system"""
    
    def __init__(self, db=None):
        self.db = db
        self.sequence_counter = 0
        self.current_month = datetime.now().strftime("%Y-%m")
        self.sequence_cache = {}
        
    async def initialize_sequence_database(self):
        """Initialize sequence database"""
        try:
            if not self.db:
                return False
            
            connection = await self.db.get_connection()
            cursor = await connection.cursor()
            
            # Create sequence table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS global_sequences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sequence_id TEXT UNIQUE NOT NULL,
                    sequence_type TEXT NOT NULL,
                    month_year TEXT NOT NULL,
                    counter INTEGER NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sequence counters table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS sequence_counters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month_year TEXT UNIQUE NOT NULL,
                    counter INTEGER NOT NULL DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await connection.commit()
            
            # Load current counter
            await self._load_sequence_counter()
            
            logger.info("✅ Global sequence system database initialized")
            return True
            
        except Exception as e:
            logger.error(f"Sequence database initialization error: {e}")
            return False
    
    async def _load_sequence_counter(self):
        """Load current sequence counter"""
        try:
            connection = await self.db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute("""
                SELECT counter FROM sequence_counters 
                WHERE month_year = ?
            """, (self.current_month,))
            
            result = await cursor.fetchone()
            
            if result:
                self.sequence_counter = result[0]
            else:
                # Initialize counter for new month
                await cursor.execute("""
                    INSERT INTO sequence_counters (month_year, counter)
                    VALUES (?, 0)
                """, (self.current_month,))
                await connection.commit()
                self.sequence_counter = 0
            
            logger.info(f"📊 Loaded sequence counter: {self.sequence_counter} for {self.current_month}")
            
        except Exception as e:
            logger.error(f"Error loading sequence counter: {e}")
            self.sequence_counter = 0
    
    async def generate_sequence_id(self, sequence_type: str, metadata: Optional[Dict] = None) -> str:
        """Generate unique sequence ID"""
        try:
            # Check if month changed
            current_month = datetime.now().strftime("%Y-%m")
            if current_month != self.current_month:
                self.current_month = current_month
                await self._load_sequence_counter()
            
            # Increment counter
            self.sequence_counter += 1
            
            # Generate sequence ID
            sequence_id = f"{sequence_type}-{self.current_month}-{self.sequence_counter:05d}"
            
            # Store in database
            if self.db:
                await self._store_sequence_record(sequence_id, sequence_type, metadata)
            
            # Update counter in database
            await self._update_sequence_counter()
            
            return sequence_id
            
        except Exception as e:
            logger.error(f"Error generating sequence ID: {e}")
            return f"{sequence_type}-{self.current_month}-00001"
    
    async def _store_sequence_record(self, sequence_id: str, sequence_type: str, metadata: Optional[Dict]):
        """Store sequence record in database"""
        try:
            connection = await self.db.get_connection()
            cursor = await connection.cursor()
            
            import json
            metadata_json = json.dumps(metadata) if metadata else None
            
            await cursor.execute("""
                INSERT INTO global_sequences 
                (sequence_id, sequence_type, month_year, counter, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (sequence_id, sequence_type, self.current_month, self.sequence_counter, metadata_json))
            
            await connection.commit()
            
        except Exception as e:
            logger.error(f"Error storing sequence record: {e}")
    
    async def _update_sequence_counter(self):
        """Update sequence counter in database"""
        try:
            connection = await self.db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute("""
                UPDATE sequence_counters 
                SET counter = ?, updated_at = CURRENT_TIMESTAMP
                WHERE month_year = ?
            """, (self.sequence_counter, self.current_month))
            
            await connection.commit()
            
        except Exception as e:
            logger.error(f"Error updating sequence counter: {e}")
    
    async def get_sequence_history(self, sequence_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get sequence history"""
        try:
            connection = await self.db.get_connection()
            cursor = await connection.cursor()
            
            if sequence_type:
                await cursor.execute("""
                    SELECT sequence_id, sequence_type, month_year, counter, metadata, created_at
                    FROM global_sequences 
                    WHERE sequence_type = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (sequence_type, limit))
            else:
                await cursor.execute("""
                    SELECT sequence_id, sequence_type, month_year, counter, metadata, created_at
                    FROM global_sequences 
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
            
            results = await cursor.fetchall()
            
            history = []
            for row in results:
                history.append({
                    'sequence_id': row[0],
                    'sequence_type': row[1],
                    'month_year': row[2],
                    'counter': row[3],
                    'metadata': row[4],
                    'created_at': row[5]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting sequence history: {e}")
            return []
    
    async def get_current_counter(self) -> int:
        """Get current sequence counter"""
        return self.sequence_counter
    
    async def reset_monthly_counter(self):
        """Reset counter for new month (admin only)"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            
            connection = await self.db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute("""
                INSERT OR REPLACE INTO sequence_counters (month_year, counter)
                VALUES (?, 0)
            """, (current_month,))
            
            await connection.commit()
            
            self.current_month = current_month
            self.sequence_counter = 0
            
            logger.info(f"✅ Reset sequence counter for {current_month}")
            
        except Exception as e:
            logger.error(f"Error resetting sequence counter: {e}")

# Global instance
global_sequence_manager = None

async def get_global_sequence_manager(db=None):
    """Get or create global sequence manager"""
    global global_sequence_manager
    if global_sequence_manager is None:
        global_sequence_manager = GlobalSequenceIdSystem(db)
        await global_sequence_manager.initialize_sequence_database()
    return global_sequence_manager

# Convenience functions
async def generate_campaign_id(metadata: Optional[Dict] = None, db=None) -> str:
    """Generate campaign ID"""
    manager = await get_global_sequence_manager(db)
    return await manager.generate_sequence_id("CAM", metadata)

async def generate_payment_id(metadata: Optional[Dict] = None, db=None) -> str:
    """Generate payment ID"""
    manager = await get_global_sequence_manager(db)
    return await manager.generate_sequence_id("PAY", metadata)

async def generate_post_id(metadata: Optional[Dict] = None, db=None) -> str:
    """Generate post ID"""
    manager = await get_global_sequence_manager(db)
    return await manager.generate_sequence_id("POST", metadata)