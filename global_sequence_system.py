#!/usr/bin/env python3
"""
Global Unique Sequence ID System for I3lani Bot
Unified tracking system with format SEQ-YYYY-MM-XXXXX for complete user journey tracing
"""

import sqlite3
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SequenceStep:
    """Individual step in a global sequence"""
    step_id: str
    step_name: str
    component: str
    timestamp: str
    status: str
    metadata: Dict
    error_message: Optional[str] = None

class GlobalSequenceManager:
    """Global Sequence ID Manager for unified tracking"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.sequence_counter = 0
        self.initialize_database()
        self.load_counter()
    
    def initialize_database(self):
        """Initialize global sequence tracking tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Global sequences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS global_sequences (
                    sequence_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    language TEXT,
                    status TEXT DEFAULT 'active',
                    current_step TEXT,
                    step_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Global sequence steps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS global_sequence_steps (
                    step_id TEXT PRIMARY KEY,
                    sequence_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    component TEXT NOT NULL,
                    step_order INTEGER,
                    status TEXT DEFAULT 'completed',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    error_message TEXT,
                    FOREIGN KEY (sequence_id) REFERENCES global_sequences (sequence_id)
                )
            """)
            
            # Component links table for global sequences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS global_component_links (
                    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sequence_id TEXT NOT NULL,
                    component_name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    link_type TEXT DEFAULT 'primary',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (sequence_id) REFERENCES global_sequences (sequence_id)
                )
            """)
            
            # Sequence counter table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sequence_counter (
                    id INTEGER PRIMARY KEY,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    counter INTEGER NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(year, month)
                )
            """)
            
            conn.commit()
            logger.info("✅ Global sequence system database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing global sequence database: {e}")
            raise
        finally:
            conn.close()
    
    def load_counter(self):
        """Load current counter for this month"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now()
            year, month = now.year, now.month
            
            cursor.execute("""
                SELECT counter FROM sequence_counter 
                WHERE year = ? AND month = ?
            """, (year, month))
            
            result = cursor.fetchone()
            if result:
                self.sequence_counter = result[0]
            else:
                # Initialize counter for this month
                cursor.execute("""
                    INSERT INTO sequence_counter (year, month, counter)
                    VALUES (?, ?, 0)
                """, (year, month))
                conn.commit()
                self.sequence_counter = 0
            
            logger.info(f"📊 Loaded sequence counter: {self.sequence_counter} for {year}-{month:02d}")
            
        except Exception as e:
            logger.error(f"❌ Error loading sequence counter: {e}")
            self.sequence_counter = 0
        finally:
            conn.close()
    
    def generate_sequence_id(self) -> str:
        """Generate new global sequence ID in format SEQ-YYYY-MM-XXXXX"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now()
            year, month = now.year, now.month
            
            # Increment counter
            self.sequence_counter += 1
            
            # Update counter in database
            cursor.execute("""
                UPDATE sequence_counter 
                SET counter = ?, updated_at = CURRENT_TIMESTAMP
                WHERE year = ? AND month = ?
            """, (self.sequence_counter, year, month))
            
            if cursor.rowcount == 0:
                # Insert new record if not exists
                cursor.execute("""
                    INSERT INTO sequence_counter (year, month, counter)
                    VALUES (?, ?, ?)
                """, (year, month, self.sequence_counter))
            
            conn.commit()
            
            # Generate sequence ID
            sequence_id = f"SEQ-{year}-{month:02d}-{self.sequence_counter:05d}"
            logger.info(f"🆔 Generated new sequence ID: {sequence_id}")
            
            return sequence_id
            
        except Exception as e:
            logger.error(f"❌ Error generating sequence ID: {e}")
            # Fallback to timestamp-based ID
            return f"SEQ-{now.year}-{now.month:02d}-{int(time.time())}"
        finally:
            conn.close()
    
    def start_user_sequence(self, user_id: int, username: str = None, 
                           language: str = None) -> str:
        """Start new global sequence for user"""
        try:
            sequence_id = self.generate_sequence_id()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata = {
                'start_time': datetime.now().isoformat(),
                'platform': 'telegram',
                'initial_language': language,
                'username': username
            }
            
            cursor.execute("""
                INSERT INTO global_sequences (
                    sequence_id, user_id, username, language, 
                    current_step, metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sequence_id, user_id, username, language,
                f"{sequence_id}:User_Flow_1_Start", json.dumps(metadata)
            ))
            
            # Log first step
            self.log_step(sequence_id, "User_Flow_1_Start", "handlers", {
                'action': 'user_start',
                'user_id': user_id,
                'username': username
            })
            
            conn.commit()
            logger.info(f"🚀 Started global sequence {sequence_id} for user {user_id}")
            
            return sequence_id
            
        except Exception as e:
            logger.error(f"❌ Error starting user sequence: {e}")
            raise
        finally:
            conn.close()
    
    def log_step(self, sequence_id: str, step_name: str, component: str, 
                metadata: Dict = None, error_message: str = None) -> str:
        """Log a step in the global sequence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current step count
            cursor.execute("""
                SELECT step_count FROM global_sequences WHERE sequence_id = ?
            """, (sequence_id,))
            
            result = cursor.fetchone()
            if not result:
                logger.warning(f"⚠️ Sequence {sequence_id} not found")
                return ""
            
            step_count = result[0] + 1
            step_id = f"{sequence_id}:{step_name}"
            
            # Insert step
            cursor.execute("""
                INSERT INTO global_sequence_steps (
                    step_id, sequence_id, step_name, component, 
                    step_order, status, metadata, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                step_id, sequence_id, step_name, component,
                step_count, 'failed' if error_message else 'completed',
                json.dumps(metadata or {}), error_message
            ))
            
            # Update sequence
            status = 'failed' if error_message else 'active'
            cursor.execute("""
                UPDATE global_sequences 
                SET current_step = ?, step_count = ?, 
                    updated_at = CURRENT_TIMESTAMP, status = ?
                WHERE sequence_id = ?
            """, (step_id, step_count, status, sequence_id))
            
            conn.commit()
            
            if error_message:
                logger.error(f"❌ Step failed: {step_id} - {error_message}")
            else:
                logger.info(f"✅ Step completed: {step_id} in {component}")
            
            return step_id
            
        except Exception as e:
            logger.error(f"❌ Error logging step: {e}")
            return ""
        finally:
            conn.close()
    
    def link_component(self, sequence_id: str, component_name: str, 
                      entity_type: str, entity_id: str, 
                      link_type: str = "primary", metadata: Dict = None):
        """Link component entity to global sequence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO global_component_links (
                    sequence_id, component_name, entity_type, 
                    entity_id, link_type, metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sequence_id, component_name, entity_type, 
                entity_id, link_type, json.dumps(metadata or {})
            ))
            
            conn.commit()
            logger.info(f"🔗 Linked {component_name}:{entity_type}:{entity_id} to {sequence_id}")
            
        except Exception as e:
            logger.error(f"❌ Error linking component: {e}")
        finally:
            conn.close()
    
    def complete_sequence(self, sequence_id: str, final_status: str = "completed"):
        """Mark global sequence as completed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE global_sequences 
                SET status = ?, completed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE sequence_id = ?
            """, (final_status, sequence_id))
            
            conn.commit()
            logger.info(f"🏁 Completed global sequence: {sequence_id} ({final_status})")
            
        except Exception as e:
            logger.error(f"❌ Error completing sequence: {e}")
        finally:
            conn.close()
    
    def get_sequence_details(self, sequence_id: str) -> Optional[Dict]:
        """Get complete details of a global sequence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get sequence info
            cursor.execute("""
                SELECT user_id, username, language, status, current_step,
                       step_count, created_at, updated_at, completed_at, metadata
                FROM global_sequences
                WHERE sequence_id = ?
            """, (sequence_id,))
            
            seq_info = cursor.fetchone()
            if not seq_info:
                return None
            
            # Get steps
            cursor.execute("""
                SELECT step_name, component, step_order, status,
                       timestamp, metadata, error_message
                FROM global_sequence_steps
                WHERE sequence_id = ?
                ORDER BY step_order
            """, (sequence_id,))
            
            steps = cursor.fetchall()
            
            # Get component links
            cursor.execute("""
                SELECT component_name, entity_type, entity_id, 
                       link_type, created_at, metadata
                FROM global_component_links
                WHERE sequence_id = ?
                ORDER BY created_at
            """, (sequence_id,))
            
            links = cursor.fetchall()
            
            return {
                'sequence_id': sequence_id,
                'user_id': seq_info[0],
                'username': seq_info[1],
                'language': seq_info[2],
                'status': seq_info[3],
                'current_step': seq_info[4],
                'step_count': seq_info[5],
                'created_at': seq_info[6],
                'updated_at': seq_info[7],
                'completed_at': seq_info[8],
                'metadata': json.loads(seq_info[9]) if seq_info[9] else {},
                'steps': [
                    {
                        'step_name': step[0],
                        'component': step[1],
                        'step_order': step[2],
                        'status': step[3],
                        'timestamp': step[4],
                        'metadata': json.loads(step[5]) if step[5] else {},
                        'error_message': step[6]
                    } for step in steps
                ],
                'component_links': [
                    {
                        'component_name': link[0],
                        'entity_type': link[1],
                        'entity_id': link[2],
                        'link_type': link[3],
                        'created_at': link[4],
                        'metadata': json.loads(link[5]) if link[5] else {}
                    } for link in links
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting sequence details: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_active_sequence(self, user_id: int) -> Optional[str]:
        """Get user's current active sequence ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT sequence_id FROM global_sequences
                WHERE user_id = ? AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Error getting user active sequence: {e}")
            return None
        finally:
            conn.close()
    
    def find_sequence_by_component(self, component_name: str, entity_id: str) -> List[str]:
        """Find sequences linked to specific component entity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT sequence_id
                FROM global_component_links
                WHERE component_name = ? AND entity_id = ?
            """, (component_name, entity_id))
            
            results = cursor.fetchall()
            return [result[0] for result in results]
            
        except Exception as e:
            logger.error(f"❌ Error finding sequences by component: {e}")
            return []
        finally:
            conn.close()
    
    def get_system_statistics(self) -> Dict:
        """Get global sequence system statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sequence statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sequences,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_sequences,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_sequences,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_sequences,
                    AVG(step_count) as avg_steps,
                    MAX(updated_at) as last_activity
                FROM global_sequences
            """)
            
            seq_stats = cursor.fetchone()
            
            # Component statistics
            cursor.execute("""
                SELECT component, COUNT(*) as step_count,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_steps,
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_steps
                FROM global_sequence_steps
                GROUP BY component
                ORDER BY step_count DESC
            """)
            
            comp_stats = cursor.fetchall()
            
            # Recent sequences
            cursor.execute("""
                SELECT sequence_id, user_id, language, status, step_count, updated_at
                FROM global_sequences
                ORDER BY updated_at DESC
                LIMIT 10
            """)
            
            recent_sequences = cursor.fetchall()
            
            return {
                'sequence_statistics': {
                    'total_sequences': seq_stats[0] or 0,
                    'active_sequences': seq_stats[1] or 0,
                    'completed_sequences': seq_stats[2] or 0,
                    'failed_sequences': seq_stats[3] or 0,
                    'average_steps': round(seq_stats[4] or 0, 1),
                    'last_activity': seq_stats[5]
                },
                'component_statistics': [
                    {
                        'component': comp[0],
                        'total_steps': comp[1],
                        'completed_steps': comp[2],
                        'failed_steps': comp[3],
                        'success_rate': round((comp[2] / comp[1]) * 100, 1) if comp[1] > 0 else 0
                    } for comp in comp_stats
                ],
                'recent_sequences': [
                    {
                        'sequence_id': seq[0],
                        'user_id': seq[1],
                        'language': seq[2],
                        'status': seq[3],
                        'step_count': seq[4],
                        'updated_at': seq[5]
                    } for seq in recent_sequences
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system statistics: {e}")
            return {}
        finally:
            conn.close()

# Global manager instance
global_sequence_manager = None

def get_global_sequence_manager() -> GlobalSequenceManager:
    """Get global sequence manager instance"""
    global global_sequence_manager
    if global_sequence_manager is None:
        global_sequence_manager = GlobalSequenceManager()
    return global_sequence_manager

def start_user_global_sequence(user_id: int, username: str = None, language: str = None) -> str:
    """Start new global sequence for user"""
    return get_global_sequence_manager().start_user_sequence(user_id, username, language)

def log_sequence_step(sequence_id: str, step_name: str, component: str, 
                     metadata: Dict = None, error_message: str = None) -> str:
    """Log step in global sequence"""
    return get_global_sequence_manager().log_step(sequence_id, step_name, component, metadata, error_message)

def link_to_global_sequence(sequence_id: str, component_name: str, entity_type: str, 
                           entity_id: str, link_type: str = "primary", metadata: Dict = None):
    """Link component to global sequence"""
    return get_global_sequence_manager().link_component(sequence_id, component_name, entity_type, entity_id, link_type, metadata)

def get_user_sequence_id(user_id: int) -> Optional[str]:
    """Get user's active sequence ID"""
    return get_global_sequence_manager().get_user_active_sequence(user_id)

def complete_global_sequence(sequence_id: str, final_status: str = "completed"):
    """Complete global sequence"""
    return get_global_sequence_manager().complete_sequence(sequence_id, final_status)