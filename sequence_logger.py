#!/usr/bin/env python3
"""
Enhanced Logging System with Global Sequence ID Integration
Automatically includes sequence IDs in all log messages for complete traceability
"""

import logging
import json
from typing import Dict, Optional, Any
from global_sequence_system import get_global_sequence_manager

class SequenceFormatter(logging.Formatter):
    """Custom formatter that includes sequence ID in log messages"""
    
    def format(self, record):
        # Add sequence ID to log record if available
        if hasattr(record, 'sequence_id') and record.sequence_id:
            # Format: [SEQ-2025-07-00123] Original message
            formatted_message = f"[{record.sequence_id}] {record.getMessage()}"
            record.msg = formatted_message
            record.args = ()
        
        return super().format(record)

class SequenceLogger:
    """Enhanced logger with automatic sequence ID integration"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.sequence_manager = get_global_sequence_manager()
        self.current_sequence_id = None
    
    def set_sequence_id(self, sequence_id: str):
        """Set current sequence ID for this logger"""
        self.current_sequence_id = sequence_id
    
    def clear_sequence_id(self):
        """Clear current sequence ID"""
        self.current_sequence_id = None
    
    def _log_with_sequence(self, level: int, msg: str, sequence_id: str = None, 
                          step_name: str = None, component: str = None, 
                          metadata: Dict = None, error_message: str = None, 
                          *args, **kwargs):
        """Log message with sequence ID integration"""
        
        # Use provided sequence_id or current one
        seq_id = sequence_id or self.current_sequence_id
        
        # Create log record with sequence ID
        extra = kwargs.get('extra', {})
        if seq_id:
            extra['sequence_id'] = seq_id
        kwargs['extra'] = extra
        
        # Log the message
        self.logger.log(level, msg, *args, **kwargs)
        
        # Log step in sequence system if step_name provided
        if seq_id and step_name and component:
            try:
                self.sequence_manager.log_step(
                    seq_id, step_name, component, metadata, error_message
                )
            except Exception as e:
                self.logger.error(f"Failed to log sequence step: {e}")
    
    def info(self, msg: str, sequence_id: str = None, step_name: str = None, 
             component: str = None, metadata: Dict = None, *args, **kwargs):
        """Info level logging with sequence tracking"""
        self._log_with_sequence(
            logging.INFO, msg, sequence_id, step_name, component, metadata, 
            None, *args, **kwargs
        )
    
    def error(self, msg: str, sequence_id: str = None, step_name: str = None, 
              component: str = None, metadata: Dict = None, error_message: str = None,
              *args, **kwargs):
        """Error level logging with sequence tracking"""
        self._log_with_sequence(
            logging.ERROR, msg, sequence_id, step_name, component, metadata, 
            error_message or msg, *args, **kwargs
        )
    
    def warning(self, msg: str, sequence_id: str = None, step_name: str = None, 
                component: str = None, metadata: Dict = None, *args, **kwargs):
        """Warning level logging with sequence tracking"""
        self._log_with_sequence(
            logging.WARNING, msg, sequence_id, step_name, component, metadata, 
            None, *args, **kwargs
        )
    
    def debug(self, msg: str, sequence_id: str = None, step_name: str = None, 
              component: str = None, metadata: Dict = None, *args, **kwargs):
        """Debug level logging with sequence tracking"""
        self._log_with_sequence(
            logging.DEBUG, msg, sequence_id, step_name, component, metadata, 
            None, *args, **kwargs
        )
    
    def step_start(self, sequence_id: str, step_name: str, component: str, 
                   description: str = "", metadata: Dict = None):
        """Log the start of a sequence step"""
        msg = f"🚀 Starting step: {step_name}"
        if description:
            msg += f" - {description}"
        
        self.info(
            msg, sequence_id=sequence_id, step_name=f"{step_name}_Start", 
            component=component, metadata=metadata or {}
        )
    
    def step_complete(self, sequence_id: str, step_name: str, component: str, 
                     description: str = "", metadata: Dict = None):
        """Log the completion of a sequence step"""
        msg = f"✅ Completed step: {step_name}"
        if description:
            msg += f" - {description}"
        
        self.info(
            msg, sequence_id=sequence_id, step_name=step_name, 
            component=component, metadata=metadata or {}
        )
    
    def step_error(self, sequence_id: str, step_name: str, component: str, 
                   error_message: str, metadata: Dict = None):
        """Log a step error"""
        msg = f"❌ Step failed: {step_name} - {error_message}"
        
        self.error(
            msg, sequence_id=sequence_id, step_name=f"{step_name}_Error", 
            component=component, metadata=metadata or {}, error_message=error_message
        )
    
    def user_action(self, sequence_id: str, user_id: int, action: str, 
                   component: str = "handlers", metadata: Dict = None):
        """Log user action with sequence tracking"""
        step_name = f"User_Action_{action.replace(' ', '_')}"
        msg = f"👤 User {user_id} action: {action}"
        
        action_metadata = metadata or {}
        action_metadata.update({
            'user_id': user_id,
            'action': action,
            'timestamp': str(datetime.now())
        })
        
        self.info(
            msg, sequence_id=sequence_id, step_name=step_name, 
            component=component, metadata=action_metadata
        )
    
    def payment_event(self, sequence_id: str, event_type: str, payment_data: Dict, 
                     component: str = "payment_system"):
        """Log payment event with sequence tracking"""
        step_name = f"Payment_{event_type.replace(' ', '_')}"
        msg = f"💳 Payment event: {event_type}"
        
        if 'amount' in payment_data:
            msg += f" - Amount: {payment_data['amount']}"
        if 'memo' in payment_data:
            msg += f" - Memo: {payment_data['memo']}"
        
        self.info(
            msg, sequence_id=sequence_id, step_name=step_name, 
            component=component, metadata=payment_data
        )
    
    def campaign_event(self, sequence_id: str, event_type: str, campaign_data: Dict, 
                      component: str = "campaign_management"):
        """Log campaign event with sequence tracking"""
        step_name = f"Campaign_{event_type.replace(' ', '_')}"
        msg = f"📊 Campaign event: {event_type}"
        
        if 'campaign_id' in campaign_data:
            msg += f" - Campaign: {campaign_data['campaign_id']}"
        
        self.info(
            msg, sequence_id=sequence_id, step_name=step_name, 
            component=component, metadata=campaign_data
        )
    
    def content_event(self, sequence_id: str, event_type: str, content_data: Dict, 
                     component: str = "content_system"):
        """Log content event with sequence tracking"""
        step_name = f"Content_{event_type.replace(' ', '_')}"
        msg = f"📝 Content event: {event_type}"
        
        if 'content_type' in content_data:
            msg += f" - Type: {content_data['content_type']}"
        if 'ad_id' in content_data:
            msg += f" - Ad: {content_data['ad_id']}"
        
        self.info(
            msg, sequence_id=sequence_id, step_name=step_name, 
            component=component, metadata=content_data
        )
    
    def admin_action(self, sequence_id: str, admin_id: int, action: str, 
                    target: str = None, component: str = "admin_system", 
                    metadata: Dict = None):
        """Log admin action with sequence tracking"""
        step_name = f"Admin_{action.replace(' ', '_')}"
        msg = f"🔧 Admin {admin_id} action: {action}"
        
        if target:
            msg += f" on {target}"
        
        admin_metadata = metadata or {}
        admin_metadata.update({
            'admin_id': admin_id,
            'action': action,
            'target': target,
            'timestamp': str(datetime.now())
        })
        
        self.info(
            msg, sequence_id=sequence_id, step_name=step_name, 
            component=component, metadata=admin_metadata
        )

def setup_sequence_logging():
    """Setup enhanced logging with sequence ID support"""
    
    # Create sequence formatter
    formatter = SequenceFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Update all handlers with sequence formatter
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
    
    logging.info("✅ Sequence logging system initialized")

def get_sequence_logger(name: str) -> SequenceLogger:
    """Get enhanced logger with sequence tracking"""
    return SequenceLogger(name)

# Context manager for sequence logging
class SequenceContext:
    """Context manager for automatic sequence ID logging"""
    
    def __init__(self, logger: SequenceLogger, sequence_id: str):
        self.logger = logger
        self.sequence_id = sequence_id
        self.previous_sequence_id = None
    
    def __enter__(self):
        self.previous_sequence_id = self.logger.current_sequence_id
        self.logger.set_sequence_id(self.sequence_id)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_sequence_id:
            self.logger.set_sequence_id(self.previous_sequence_id)
        else:
            self.logger.clear_sequence_id()

# Helper function for easy context usage
def with_sequence(logger: SequenceLogger, sequence_id: str) -> SequenceContext:
    """Create sequence logging context"""
    return SequenceContext(logger, sequence_id)