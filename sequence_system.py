#!/usr/bin/env python3
"""
I3lani Bot Sequence System
Comprehensive flow tracking and component integration system
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SequenceType(Enum):
    """Types of sequences in the system"""
    USER_ONBOARDING = "user_onboarding"
    AD_CREATION = "ad_creation"
    PAYMENT_PROCESSING = "payment_processing"
    CAMPAIGN_MANAGEMENT = "campaign_management"
    CONTENT_PUBLISHING = "content_publishing"
    ADMIN_ACTION = "admin_action"
    SYSTEM_MAINTENANCE = "system_maintenance"
    ERROR_RECOVERY = "error_recovery"

class SequenceStatus(Enum):
    """Status of sequence steps"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING = "waiting"

class SequenceStep:
    """Individual step in a sequence"""
    def __init__(self, step_id: str, name: str, description: str, 
                 component: str, dependencies: List[str] = None):
        self.step_id = step_id
        self.name = name
        self.description = description
        self.component = component
        self.dependencies = dependencies or []
        self.status = SequenceStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.metadata = {}

class SequenceSystem:
    """Main sequence system for tracking all bot flows"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.active_sequences = {}
        self.sequence_definitions = {}
        self.initialize_database()
        self.define_sequences()
    
    def initialize_database(self):
        """Initialize sequence tracking tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main sequences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sequences (
                    sequence_id TEXT PRIMARY KEY,
                    sequence_type TEXT NOT NULL,
                    user_id INTEGER,
                    entity_id TEXT,
                    status TEXT DEFAULT 'active',
                    current_step TEXT,
                    progress_percentage INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            # Sequence steps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sequence_steps (
                    step_id TEXT PRIMARY KEY,
                    sequence_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    step_description TEXT,
                    component TEXT,
                    step_order INTEGER,
                    status TEXT DEFAULT 'pending',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    metadata TEXT,
                    FOREIGN KEY (sequence_id) REFERENCES sequences (sequence_id)
                )
            """)
            
            # Component integration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS component_links (
                    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sequence_id TEXT NOT NULL,
                    component_name TEXT NOT NULL,
                    entity_type TEXT,
                    entity_id TEXT,
                    link_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sequence_id) REFERENCES sequences (sequence_id)
                )
            """)
            
            # Flow transitions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flow_transitions (
                    transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sequence_id TEXT NOT NULL,
                    from_step TEXT,
                    to_step TEXT NOT NULL,
                    transition_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    trigger_event TEXT,
                    metadata TEXT,
                    FOREIGN KEY (sequence_id) REFERENCES sequences (sequence_id)
                )
            """)
            
            conn.commit()
            logger.info("✅ Sequence system database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing sequence database: {e}")
            raise
        finally:
            conn.close()
    
    def define_sequences(self):
        """Define all sequence flows in the system"""
        
        # User Onboarding Sequence
        self.sequence_definitions[SequenceType.USER_ONBOARDING] = [
            SequenceStep("user_start", "User Start", "User starts bot interaction", "handlers"),
            SequenceStep("language_selection", "Language Selection", "User selects language", "handlers"),
            SequenceStep("main_menu", "Main Menu", "User reaches main menu", "handlers"),
            SequenceStep("profile_setup", "Profile Setup", "User profile created", "database"),
            SequenceStep("onboarding_complete", "Onboarding Complete", "User ready to use bot", "system")
        ]
        
        # Ad Creation Sequence
        self.sequence_definitions[SequenceType.AD_CREATION] = [
            SequenceStep("ad_start", "Ad Creation Start", "User starts creating ad", "handlers"),
            SequenceStep("content_upload", "Content Upload", "User uploads text/media", "handlers"),
            SequenceStep("channel_selection", "Channel Selection", "User selects channels", "handlers"),
            SequenceStep("duration_selection", "Duration Selection", "User selects duration", "handlers"),
            SequenceStep("pricing_calculation", "Pricing Calculation", "System calculates pricing", "frequency_pricing"),
            SequenceStep("payment_method", "Payment Method", "User selects payment method", "handlers"),
            SequenceStep("ad_draft_saved", "Ad Draft Saved", "Ad saved to database", "database"),
            SequenceStep("ad_creation_complete", "Ad Creation Complete", "Ad ready for payment", "system")
        ]
        
        # Payment Processing Sequence
        self.sequence_definitions[SequenceType.PAYMENT_PROCESSING] = [
            SequenceStep("payment_start", "Payment Start", "User initiates payment", "handlers"),
            SequenceStep("payment_method_selected", "Payment Method Selected", "TON or Stars selected", "handlers"),
            SequenceStep("payment_instructions", "Payment Instructions", "User receives payment info", "wallet_manager"),
            SequenceStep("payment_monitoring", "Payment Monitoring", "System monitors blockchain/Telegram", "payment_monitoring"),
            SequenceStep("payment_detected", "Payment Detected", "Payment found on blockchain", "payment_scanner"),
            SequenceStep("payment_verified", "Payment Verified", "Payment amount/memo verified", "payment_verification"),
            SequenceStep("payment_confirmed", "Payment Confirmed", "User notified of confirmation", "automatic_confirmation"),
            SequenceStep("payment_complete", "Payment Complete", "Payment fully processed", "system")
        ]
        
        # Campaign Management Sequence
        self.sequence_definitions[SequenceType.CAMPAIGN_MANAGEMENT] = [
            SequenceStep("campaign_create", "Campaign Creation", "Campaign created from payment", "campaign_management"),
            SequenceStep("content_copy", "Content Copy", "Ad content copied to campaign", "campaign_management"),
            SequenceStep("post_identity", "Post Identity", "Unique post ID generated", "post_identity_system"),
            SequenceStep("schedule_posts", "Schedule Posts", "Posts scheduled for publishing", "campaign_management"),
            SequenceStep("campaign_active", "Campaign Active", "Campaign ready for publishing", "system"),
            SequenceStep("campaign_complete", "Campaign Complete", "All posts published", "system")
        ]
        
        # Content Publishing Sequence
        self.sequence_definitions[SequenceType.CONTENT_PUBLISHING] = [
            SequenceStep("publish_start", "Publishing Start", "Post due for publishing", "campaign_publisher"),
            SequenceStep("content_prepare", "Content Prepare", "Content prepared for channel", "campaign_publisher"),
            SequenceStep("channel_send", "Channel Send", "Content sent to channel", "campaign_publisher"),
            SequenceStep("publish_verify", "Publish Verify", "Publication verified", "post_identity_system"),
            SequenceStep("publish_log", "Publish Log", "Publication logged", "database"),
            SequenceStep("publish_complete", "Publish Complete", "Post successfully published", "system")
        ]
        
        # Admin Action Sequence
        self.sequence_definitions[SequenceType.ADMIN_ACTION] = [
            SequenceStep("admin_auth", "Admin Authentication", "Admin identity verified", "admin_system"),
            SequenceStep("admin_action", "Admin Action", "Admin performs action", "admin_system"),
            SequenceStep("system_update", "System Update", "System state updated", "database"),
            SequenceStep("admin_log", "Admin Log", "Action logged", "database"),
            SequenceStep("admin_complete", "Admin Complete", "Admin action completed", "system")
        ]
        
        logger.info(f"✅ Defined {len(self.sequence_definitions)} sequence types")
    
    def start_sequence(self, sequence_type: SequenceType, user_id: int = None, 
                      entity_id: str = None, metadata: Dict = None) -> str:
        """Start a new sequence"""
        try:
            sequence_id = f"{sequence_type.value}_{int(time.time())}_{user_id or 'system'}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create main sequence record
            cursor.execute("""
                INSERT INTO sequences (
                    sequence_id, sequence_type, user_id, entity_id, 
                    status, current_step, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                sequence_id, sequence_type.value, user_id, entity_id,
                'active', None, json.dumps(metadata or {})
            ))
            
            # Create sequence steps
            if sequence_type in self.sequence_definitions:
                steps = self.sequence_definitions[sequence_type]
                for i, step in enumerate(steps):
                    step_id = f"{sequence_id}_{step.step_id}"
                    cursor.execute("""
                        INSERT INTO sequence_steps (
                            step_id, sequence_id, step_name, step_description,
                            component, step_order, status, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        step_id, sequence_id, step.name, step.description,
                        step.component, i, 'pending', json.dumps(step.metadata)
                    ))
            
            conn.commit()
            self.active_sequences[sequence_id] = {
                'type': sequence_type,
                'user_id': user_id,
                'entity_id': entity_id,
                'current_step': 0,
                'started_at': datetime.now()
            }
            
            logger.info(f"🚀 Started sequence: {sequence_id} ({sequence_type.value})")
            return sequence_id
            
        except Exception as e:
            logger.error(f"❌ Error starting sequence: {e}")
            raise
        finally:
            conn.close()
    
    def advance_sequence(self, sequence_id: str, step_name: str = None, 
                        metadata: Dict = None, error_message: str = None) -> bool:
        """Advance sequence to next step or specific step"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current sequence info
            cursor.execute("""
                SELECT sequence_type, current_step, status 
                FROM sequences 
                WHERE sequence_id = ?
            """, (sequence_id,))
            
            seq_info = cursor.fetchone()
            if not seq_info:
                logger.warning(f"⚠️ Sequence not found: {sequence_id}")
                return False
            
            sequence_type_str, current_step, status = seq_info
            
            if status != 'active':
                logger.warning(f"⚠️ Sequence not active: {sequence_id} ({status})")
                return False
            
            # Find next step
            if step_name:
                # Advance to specific step
                cursor.execute("""
                    SELECT step_id, step_order 
                    FROM sequence_steps 
                    WHERE sequence_id = ? AND step_name = ?
                """, (sequence_id, step_name))
            else:
                # Advance to next step
                cursor.execute("""
                    SELECT step_id, step_order 
                    FROM sequence_steps 
                    WHERE sequence_id = ? AND status = 'pending'
                    ORDER BY step_order 
                    LIMIT 1
                """, (sequence_id,))
            
            next_step = cursor.fetchone()
            if not next_step:
                logger.info(f"✅ Sequence completed: {sequence_id}")
                self.complete_sequence(sequence_id)
                return True
            
            step_id, step_order = next_step
            
            # Update step status
            status_update = 'failed' if error_message else 'completed'
            cursor.execute("""
                UPDATE sequence_steps 
                SET status = ?, completed_at = CURRENT_TIMESTAMP, 
                    error_message = ?, metadata = ?
                WHERE step_id = ?
            """, (status_update, error_message, json.dumps(metadata or {}), step_id))
            
            # Update sequence current step
            progress = ((step_order + 1) / self.get_total_steps(sequence_id)) * 100
            cursor.execute("""
                UPDATE sequences 
                SET current_step = ?, progress_percentage = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE sequence_id = ?
            """, (step_name or f"step_{step_order}", int(progress), sequence_id))
            
            # Log transition
            cursor.execute("""
                INSERT INTO flow_transitions (
                    sequence_id, from_step, to_step, trigger_event, metadata
                ) VALUES (?, ?, ?, ?, ?)
            """, (sequence_id, current_step, step_name or f"step_{step_order}", 
                  'advance', json.dumps(metadata or {})))
            
            conn.commit()
            
            logger.info(f"⏩ Advanced sequence: {sequence_id} → {step_name or f'step_{step_order}'}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error advancing sequence: {e}")
            return False
        finally:
            conn.close()
    
    def link_component(self, sequence_id: str, component_name: str, 
                      entity_type: str, entity_id: str, link_type: str = "primary"):
        """Link a component entity to a sequence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO component_links (
                    sequence_id, component_name, entity_type, entity_id, link_type
                ) VALUES (?, ?, ?, ?, ?)
            """, (sequence_id, component_name, entity_type, entity_id, link_type))
            
            conn.commit()
            logger.info(f"🔗 Linked {component_name}:{entity_type}:{entity_id} to {sequence_id}")
            
        except Exception as e:
            logger.error(f"❌ Error linking component: {e}")
        finally:
            conn.close()
    
    def get_sequence_status(self, sequence_id: str) -> Optional[Dict]:
        """Get current status of a sequence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get sequence info
            cursor.execute("""
                SELECT sequence_type, user_id, entity_id, status, 
                       current_step, progress_percentage, created_at, updated_at
                FROM sequences 
                WHERE sequence_id = ?
            """, (sequence_id,))
            
            seq_info = cursor.fetchone()
            if not seq_info:
                return None
            
            # Get steps
            cursor.execute("""
                SELECT step_name, status, started_at, completed_at, error_message
                FROM sequence_steps 
                WHERE sequence_id = ?
                ORDER BY step_order
            """, (sequence_id,))
            
            steps = cursor.fetchall()
            
            return {
                'sequence_id': sequence_id,
                'type': seq_info[0],
                'user_id': seq_info[1],
                'entity_id': seq_info[2],
                'status': seq_info[3],
                'current_step': seq_info[4],
                'progress_percentage': seq_info[5],
                'created_at': seq_info[6],
                'updated_at': seq_info[7],
                'steps': [
                    {
                        'name': step[0],
                        'status': step[1],
                        'started_at': step[2],
                        'completed_at': step[3],
                        'error_message': step[4]
                    } for step in steps
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting sequence status: {e}")
            return None
        finally:
            conn.close()
    
    def get_total_steps(self, sequence_id: str) -> int:
        """Get total number of steps in a sequence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM sequence_steps WHERE sequence_id = ?
            """, (sequence_id,))
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"❌ Error getting step count: {e}")
            return 0
        finally:
            conn.close()
    
    def complete_sequence(self, sequence_id: str):
        """Mark sequence as completed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sequences 
                SET status = 'completed', progress_percentage = 100,
                    completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE sequence_id = ?
            """, (sequence_id,))
            
            conn.commit()
            
            if sequence_id in self.active_sequences:
                del self.active_sequences[sequence_id]
                
            logger.info(f"✅ Completed sequence: {sequence_id}")
            
        except Exception as e:
            logger.error(f"❌ Error completing sequence: {e}")
        finally:
            conn.close()
    
    def get_active_sequences(self, user_id: int = None) -> List[Dict]:
        """Get all active sequences, optionally for a specific user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT sequence_id, sequence_type, current_step, 
                           progress_percentage, created_at, updated_at
                    FROM sequences 
                    WHERE user_id = ? AND status = 'active'
                    ORDER BY updated_at DESC
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT sequence_id, sequence_type, user_id, current_step,
                           progress_percentage, created_at, updated_at
                    FROM sequences 
                    WHERE status = 'active'
                    ORDER BY updated_at DESC
                """)
            
            sequences = cursor.fetchall()
            
            return [
                {
                    'sequence_id': seq[0],
                    'type': seq[1],
                    'user_id': seq[2] if not user_id else user_id,
                    'current_step': seq[3 if user_id else 3],
                    'progress_percentage': seq[4 if user_id else 4],
                    'created_at': seq[5 if user_id else 5],
                    'updated_at': seq[6 if user_id else 6]
                } for seq in sequences
            ]
            
        except Exception as e:
            logger.error(f"❌ Error getting active sequences: {e}")
            return []
        finally:
            conn.close()
    
    def find_sequences_by_component(self, component_name: str, entity_id: str) -> List[str]:
        """Find sequences linked to a specific component entity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT sequence_id 
                FROM component_links 
                WHERE component_name = ? AND entity_id = ?
            """, (component_name, entity_id))
            
            sequences = cursor.fetchall()
            return [seq[0] for seq in sequences]
            
        except Exception as e:
            logger.error(f"❌ Error finding sequences by component: {e}")
            return []
        finally:
            conn.close()
    
    def get_system_health(self) -> Dict:
        """Get overall system health from sequence perspective"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get sequence statistics
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(progress_percentage) as avg_progress
                FROM sequences
                GROUP BY status
            """)
            
            status_stats = cursor.fetchall()
            
            # Get component health
            cursor.execute("""
                SELECT 
                    component,
                    COUNT(*) as total_steps,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM sequence_steps
                GROUP BY component
            """)
            
            component_stats = cursor.fetchall()
            
            return {
                'status_distribution': {
                    stat[0]: {'count': stat[1], 'avg_progress': stat[2]}
                    for stat in status_stats
                },
                'component_health': {
                    stat[0]: {
                        'total_steps': stat[1],
                        'completed': stat[2],
                        'failed': stat[3],
                        'success_rate': (stat[2] / stat[1]) * 100 if stat[1] > 0 else 0
                    } for stat in component_stats
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system health: {e}")
            return {}
        finally:
            conn.close()

# Global sequence system instance
sequence_system = None

def get_sequence_system() -> SequenceSystem:
    """Get global sequence system instance"""
    global sequence_system
    if sequence_system is None:
        sequence_system = SequenceSystem()
    return sequence_system

def start_user_sequence(user_id: int, sequence_type: SequenceType, 
                       entity_id: str = None, metadata: Dict = None) -> str:
    """Helper function to start a user sequence"""
    return get_sequence_system().start_sequence(sequence_type, user_id, entity_id, metadata)

def advance_user_sequence(sequence_id: str, step_name: str = None, 
                         metadata: Dict = None, error_message: str = None) -> bool:
    """Helper function to advance a user sequence"""
    return get_sequence_system().advance_sequence(sequence_id, step_name, metadata, error_message)

def link_to_sequence(sequence_id: str, component_name: str, 
                    entity_type: str, entity_id: str, link_type: str = "primary"):
    """Helper function to link component to sequence"""
    return get_sequence_system().link_component(sequence_id, component_name, entity_type, entity_id, link_type)