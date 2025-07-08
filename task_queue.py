#!/usr/bin/env python3
"""
Task Queue System for I3lani Bot
Handles async job processing with Redis-like functionality using SQLite
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from database import Database
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TaskQueue:
    """Simple task queue using database"""
    
    def __init__(self, db: Database):
        self.db = db
        await self.init_queue_table()
    
    async def init_queue_table(self):
        """Initialize task queue table"""
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_at TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                error_message TEXT
            )
        ''')
    
    async def add_task(self, task_type: str, payload: Dict[Any, Any], 
                      delay_seconds: int = 0, max_attempts: int = 3):
        """Add task to queue"""
        scheduled_at = datetime.now()
        if delay_seconds > 0:
            scheduled_at += timedelta(seconds=delay_seconds)
        
        await self.db.execute('''
            INSERT INTO task_queue (task_type, payload, scheduled_at, max_attempts)
            VALUES (?, ?, ?, ?)
        ''', (task_type, json.dumps(payload), scheduled_at, max_attempts))
        
        logger.info(f"Added task: {task_type}")
    
    async def get_pending_tasks(self, limit: int = 10):
        """Get pending tasks ready to process"""
        return await self.db.fetch_all('''
            SELECT * FROM task_queue 
            WHERE status = 'pending' 
            AND scheduled_at <= ?
            ORDER BY scheduled_at ASC
            LIMIT ?
        ''', (datetime.now(), limit))
    
    async def mark_task_processing(self, task_id: int):
        """Mark task as being processed"""
        await self.db.execute('''
            UPDATE task_queue 
            SET status = 'processing', attempts = attempts + 1
            WHERE id = ?
        ''', (task_id,))
    
    async def mark_task_completed(self, task_id: int):
        """Mark task as completed"""
        await self.db.execute('''
            UPDATE task_queue 
            SET status = 'completed'
            WHERE id = ?
        ''', (task_id,))
    
    async def mark_task_failed(self, task_id: int, error_message: str):
        """Mark task as failed"""
        task = await self.db.fetch_one('''
            SELECT attempts, max_attempts FROM task_queue WHERE id = ?
        ''', (task_id,))
        
        if task and task['attempts'] >= task['max_attempts']:
            status = 'failed'
        else:
            status = 'pending'  # Retry
        
        await self.db.execute('''
            UPDATE task_queue 
            SET status = ?, error_message = ?
            WHERE id = ?
        ''', (status, error_message, task_id))
    
    async def cleanup_old_tasks(self, days: int = 7):
        """Clean up old completed/failed tasks"""
        cutoff_date = datetime.now() - timedelta(days=days)
        await self.db.execute('''
            DELETE FROM task_queue 
            WHERE status IN ('completed', 'failed') 
            AND created_at < ?
        ''', (cutoff_date,))

class TaskProcessor:
    """Process tasks from the queue"""
    
    def __init__(self, queue: TaskQueue):
        self.queue = queue
        self.handlers = {}
    
    def register_handler(self, task_type: str, handler):
        """Register task handler"""
        self.handlers[task_type] = handler
        logger.info(f"Registered handler for: {task_type}")
    
    async def process_tasks(self):
        """Process pending tasks"""
        while True:
            try:
                tasks = await self.queue.get_pending_tasks()
                
                for task in tasks:
                    await self.process_task(task)
                
                if not tasks:
                    await asyncio.sleep(5)  # No tasks, wait 5 seconds
                    
            except Exception as e:
                logger.error(f"Task processor error: {e}")
                await asyncio.sleep(10)
    
    async def process_task(self, task):
        """Process individual task"""
        task_id = task['id']
        task_type = task['task_type']
        
        try:
            await self.queue.mark_task_processing(task_id)
            
            if task_type in self.handlers:
                payload = json.loads(task['payload'])
                await self.handlers[task_type](payload)
                await self.queue.mark_task_completed(task_id)
                logger.info(f"Completed task: {task_type}")
            else:
                await self.queue.mark_task_failed(task_id, f"No handler for {task_type}")
                logger.error(f"No handler for task type: {task_type}")
                
        except Exception as e:
            await self.queue.mark_task_failed(task_id, str(e))
            logger.error(f"Task {task_type} failed: {e}")

# Task handlers
async def handle_payment_verification(payload):
    """Handle payment verification task"""
    payment_id = payload['payment_id']
    # Payment verification logic here
    logger.info(f"Verifying payment: {payment_id}")

async def handle_reward_distribution(payload):
    """Handle reward distribution task"""
    user_id = payload['user_id']
    amount = payload['amount']
    # Reward distribution logic here
    logger.info(f"Distributing {amount} TON to user {user_id}")

async def handle_channel_analytics(payload):
    """Handle channel analytics update"""
    channel_id = payload['channel_id']
    # Analytics update logic here
    logger.info(f"Updating analytics for channel: {channel_id}")

async def handle_notification_send(payload):
    """Handle notification sending"""
    user_id = payload['user_id']
    message = payload['message']
    # Notification sending logic here
    logger.info(f"Sending notification to user {user_id}")

# Example usage in main worker
async def setup_task_processor(db: Database):
    """Setup task processor with handlers"""
    queue = TaskQueue(db)
    processor = TaskProcessor(queue)
    
    # Register handlers
    processor.register_handler('payment_verification', handle_payment_verification)
    processor.register_handler('reward_distribution', handle_reward_distribution)
    processor.register_handler('channel_analytics', handle_channel_analytics)
    processor.register_handler('notification_send', handle_notification_send)
    
    return queue, processor