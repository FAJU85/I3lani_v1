"""
Animated Transaction Timeline for TON Payment Verification
Visualizes payment verification steps with real-time progress updates
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class TimelineStepStatus(Enum):
    """Status of timeline steps"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TimelineStep:
    """Individual step in the payment timeline"""
    step_id: str
    title: str
    description: str
    status: TimelineStepStatus
    icon: str
    duration_seconds: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def get_elapsed_time(self) -> int:
        """Get elapsed time for current step"""
        if not self.started_at:
            return 0
        return int((datetime.now() - self.started_at).total_seconds())
    
    def get_progress_percentage(self) -> int:
        """Get progress percentage for current step"""
        if self.status == TimelineStepStatus.COMPLETED:
            return 100
        elif self.status == TimelineStepStatus.FAILED:
            return 0
        elif self.status == TimelineStepStatus.IN_PROGRESS:
            elapsed = self.get_elapsed_time()
            return min(int((elapsed / self.duration_seconds) * 100), 95)
        return 0

class AnimatedTransactionTimeline:
    """Animated timeline for TON payment verification"""
    
    def __init__(self, user_id: int, payment_id: str, bot_instance=None):
        self.user_id = user_id
        self.payment_id = payment_id
        self.bot = bot_instance
        self.chat_id = user_id
        self.timeline_message_id = None
        self.animation_task = None
        self.is_active = False
        
        # Initialize timeline steps
        self.steps = [
            TimelineStep(
                step_id="wallet_collection",
                title="💳 Wallet Collection",
                description="Collecting your TON wallet address",
                status=TimelineStepStatus.PENDING,
                icon="💳",
                duration_seconds=30
            ),
            TimelineStep(
                step_id="memo_generation",
                title="🔢 Memo Generation",
                description="Generating unique payment memo",
                status=TimelineStepStatus.PENDING,
                icon="🔢",
                duration_seconds=5
            ),
            TimelineStep(
                step_id="payment_instructions",
                title="📋 Payment Instructions",
                description="Preparing payment details",
                status=TimelineStepStatus.PENDING,
                icon="📋",
                duration_seconds=10
            ),
            TimelineStep(
                step_id="blockchain_monitoring",
                title="🔍 Blockchain Monitoring",
                description="Monitoring blockchain for payment",
                status=TimelineStepStatus.PENDING,
                icon="🔍",
                duration_seconds=600  # 10 minutes
            ),
            TimelineStep(
                step_id="payment_verification",
                title="✅ Payment Verification",
                description="Verifying payment details",
                status=TimelineStepStatus.PENDING,
                icon="✅",
                duration_seconds=15
            ),
            TimelineStep(
                step_id="campaign_activation",
                title="🚀 Campaign Activation",
                description="Activating your ad campaign",
                status=TimelineStepStatus.PENDING,
                icon="🚀",
                duration_seconds=20
            )
        ]
        
        self.current_step_index = 0
        self.total_steps = len(self.steps)
        
        # Animation frames for progress indicators
        self.loading_frames = ["⏳", "⌛", "⏳", "⌛"]
        self.success_frames = ["✅", "🎉", "✅", "🎉"]
        self.frame_index = 0
    
    async def start_timeline(self) -> str:
        """Start the animated timeline"""
        self.is_active = True
        
        # Send initial timeline message
        initial_message = self._generate_timeline_message()
        
        if self.bot:
            try:
                message = await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=initial_message,
                    parse_mode='HTML'
                )
                self.timeline_message_id = message.message_id
            except Exception as e:
                logger.error(f"Error sending timeline message: {e}")
        
        # Start animation task
        self.animation_task = asyncio.create_task(self._animate_timeline())
        
        return self.payment_id
    
    async def update_step_status(self, step_id: str, status: TimelineStepStatus, error_message: str = None):
        """Update status of a specific step"""
        step = self._get_step_by_id(step_id)
        if not step:
            return
        
        # Update step status
        old_status = step.status
        step.status = status
        
        if status == TimelineStepStatus.IN_PROGRESS:
            step.started_at = datetime.now()
            # Move to this step if it's ahead
            step_index = self._get_step_index(step_id)
            if step_index > self.current_step_index:
                self.current_step_index = step_index
                
        elif status == TimelineStepStatus.COMPLETED:
            step.completed_at = datetime.now()
            # Move to next step
            self._advance_to_next_step()
            
        elif status == TimelineStepStatus.FAILED:
            step.error_message = error_message
            
        # Update timeline display
        await self._update_timeline_display()
        
        logger.info(f"Timeline step {step_id} updated: {old_status.value} -> {status.value}")
    
    async def complete_timeline(self, success: bool = True):
        """Complete the timeline"""
        self.is_active = False
        
        if success:
            # Mark all remaining steps as completed
            for step in self.steps[self.current_step_index:]:
                if step.status == TimelineStepStatus.PENDING:
                    step.status = TimelineStepStatus.COMPLETED
                    step.completed_at = datetime.now()
        
        # Final update
        await self._update_timeline_display()
        
        # Stop animation
        if self.animation_task:
            self.animation_task.cancel()
        
        logger.info(f"Timeline completed for payment {self.payment_id}")
    
    def _generate_timeline_message(self) -> str:
        """Generate the timeline message"""
        header = f"🔄 <b>TON Payment Timeline</b>\n"
        header += f"Payment ID: <code>{self.payment_id}</code>\n"
        header += f"Progress: {self._get_overall_progress()}%\n\n"
        
        timeline_text = ""
        
        for i, step in enumerate(self.steps):
            # Step number and status icon
            if step.status == TimelineStepStatus.COMPLETED:
                status_icon = "✅"
            elif step.status == TimelineStepStatus.IN_PROGRESS:
                status_icon = self.loading_frames[self.frame_index % len(self.loading_frames)]
            elif step.status == TimelineStepStatus.FAILED:
                status_icon = "❌"
            else:
                status_icon = "⏸️"
            
            # Progress bar for current step
            progress_bar = ""
            if step.status == TimelineStepStatus.IN_PROGRESS:
                progress = step.get_progress_percentage()
                filled_blocks = int(progress / 10)
                empty_blocks = 10 - filled_blocks
                progress_bar = f"\n   {'█' * filled_blocks}{'░' * empty_blocks} {progress}%"
            
            # Time information
            time_info = ""
            if step.status == TimelineStepStatus.COMPLETED and step.completed_at:
                time_info = f" ({step.completed_at.strftime('%H:%M:%S')})"
            elif step.status == TimelineStepStatus.IN_PROGRESS:
                elapsed = step.get_elapsed_time()
                time_info = f" ({elapsed}s)"
            
            # Error message
            error_text = ""
            if step.status == TimelineStepStatus.FAILED and step.error_message:
                error_text = f"\n   ⚠️ {step.error_message}"
            
            timeline_text += f"{status_icon} <b>{step.title}</b>{time_info}\n"
            timeline_text += f"   {step.description}{progress_bar}{error_text}\n\n"
        
        footer = f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}\n"
        footer += f"⏱️ Total Steps: {self.total_steps}\n"
        
        return header + timeline_text + footer
    
    def _get_overall_progress(self) -> int:
        """Calculate overall progress percentage"""
        completed_steps = sum(1 for step in self.steps if step.status == TimelineStepStatus.COMPLETED)
        current_step_progress = 0
        
        if self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]
            if current_step.status == TimelineStepStatus.IN_PROGRESS:
                current_step_progress = current_step.get_progress_percentage() / 100
        
        return int(((completed_steps + current_step_progress) / self.total_steps) * 100)
    
    def _get_step_by_id(self, step_id: str) -> Optional[TimelineStep]:
        """Get step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _get_step_index(self, step_id: str) -> int:
        """Get step index by ID"""
        for i, step in enumerate(self.steps):
            if step.step_id == step_id:
                return i
        return -1
    
    def _advance_to_next_step(self):
        """Advance to next step"""
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            # Auto-start next step if it's pending
            next_step = self.steps[self.current_step_index]
            if next_step.status == TimelineStepStatus.PENDING:
                next_step.status = TimelineStepStatus.IN_PROGRESS
                next_step.started_at = datetime.now()
    
    async def _animate_timeline(self):
        """Animate the timeline with periodic updates"""
        try:
            while self.is_active:
                # Update animation frame
                self.frame_index += 1
                
                # Update display every 2 seconds
                await self._update_timeline_display()
                
                # Wait before next frame
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            logger.info("Timeline animation cancelled")
        except Exception as e:
            logger.error(f"Error in timeline animation: {e}")
    
    async def _update_timeline_display(self):
        """Update the timeline display message"""
        if not self.bot or not self.timeline_message_id:
            return
        
        try:
            updated_message = self._generate_timeline_message()
            
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.timeline_message_id,
                text=updated_message,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error updating timeline display: {e}")

class TimelineManager:
    """Manager for multiple payment timelines"""
    
    def __init__(self, bot_instance=None):
        self.bot = bot_instance
        self.active_timelines: Dict[str, AnimatedTransactionTimeline] = {}
    
    async def create_timeline(self, user_id: int, payment_id: str) -> AnimatedTransactionTimeline:
        """Create a new payment timeline"""
        timeline = AnimatedTransactionTimeline(user_id, payment_id, self.bot)
        self.active_timelines[payment_id] = timeline
        
        await timeline.start_timeline()
        
        logger.info(f"Created timeline for payment {payment_id}")
        return timeline
    
    async def update_timeline_step(self, payment_id: str, step_id: str, 
                                 status: TimelineStepStatus, error_message: str = None):
        """Update a timeline step"""
        timeline = self.active_timelines.get(payment_id)
        if timeline:
            await timeline.update_step_status(step_id, status, error_message)
    
    async def complete_timeline(self, payment_id: str, success: bool = True):
        """Complete a timeline"""
        timeline = self.active_timelines.get(payment_id)
        if timeline:
            await timeline.complete_timeline(success)
            # Remove from active timelines
            del self.active_timelines[payment_id]
    
    def get_timeline(self, payment_id: str) -> Optional[AnimatedTransactionTimeline]:
        """Get timeline by payment ID"""
        return self.active_timelines.get(payment_id)
    
    def get_active_timelines_count(self) -> int:
        """Get number of active timelines"""
        return len(self.active_timelines)
    
    async def cleanup_expired_timelines(self, max_age_minutes: int = 30):
        """Clean up expired timelines"""
        expired_timelines = []
        current_time = datetime.now()
        
        for payment_id, timeline in self.active_timelines.items():
            if timeline.steps[0].started_at:
                age_minutes = (current_time - timeline.steps[0].started_at).total_seconds() / 60
                if age_minutes > max_age_minutes:
                    expired_timelines.append(payment_id)
        
        for payment_id in expired_timelines:
            await self.complete_timeline(payment_id, success=False)
            logger.info(f"Cleaned up expired timeline: {payment_id}")

# Global timeline manager instance
timeline_manager = TimelineManager()

def get_timeline_manager(bot_instance=None) -> TimelineManager:
    """Get or create timeline manager instance"""
    global timeline_manager
    if bot_instance and not timeline_manager.bot:
        timeline_manager.bot = bot_instance
    return timeline_manager

# Timeline step constants for easy reference
TIMELINE_STEPS = {
    'WALLET_COLLECTION': 'wallet_collection',
    'MEMO_GENERATION': 'memo_generation',
    'PAYMENT_INSTRUCTIONS': 'payment_instructions',
    'BLOCKCHAIN_MONITORING': 'blockchain_monitoring',
    'PAYMENT_VERIFICATION': 'payment_verification',
    'CAMPAIGN_ACTIVATION': 'campaign_activation'
}

# Helper functions for integration
async def create_payment_timeline(user_id: int, payment_id: str, bot_instance=None) -> AnimatedTransactionTimeline:
    """Create a new payment timeline"""
    manager = get_timeline_manager(bot_instance)
    return await manager.create_timeline(user_id, payment_id)

async def update_payment_timeline(payment_id: str, step_id: str, 
                                status: TimelineStepStatus, error_message: str = None):
    """Update payment timeline step"""
    manager = get_timeline_manager()
    await manager.update_timeline_step(payment_id, step_id, status, error_message)

async def complete_payment_timeline(payment_id: str, success: bool = True):
    """Complete payment timeline"""
    manager = get_timeline_manager()
    await manager.complete_timeline(payment_id, success)