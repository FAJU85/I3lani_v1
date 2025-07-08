#!/usr/bin/env python3
"""
Background Worker for I3lani Bot
Handles async tasks like payment verification, analytics, and cleanup
"""
import asyncio
import os
import logging
import json
from datetime import datetime, timedelta
from database import Database
import aiohttp
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackgroundWorker:
    def __init__(self):
        self.db = Database()
        self.running = True
        self.ton_wallet = os.getenv('TON_WALLET_ADDRESS', 'UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB')
        
    async def start(self):
        """Start all background tasks"""
        logger.info("🚀 Starting I3lani Bot background worker...")
        
        # Start all background tasks
        tasks = [
            self.payment_monitor(),
            self.channel_analytics_updater(),
            self.reward_processor(),
            self.database_cleanup(),
            self.health_checker()
        ]
        
        await asyncio.gather(*tasks)
    
    async def payment_monitor(self):
        """Monitor pending TON payments"""
        logger.info("💰 Starting payment monitor...")
        
        while self.running:
            try:
                # Check pending TON payments
                pending_payments = await self.db.get_pending_payments()
                
                for payment in pending_payments:
                    await self.verify_ton_payment(payment)
                
                # Check every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Payment monitor error: {e}")
                await asyncio.sleep(60)
    
    async def verify_ton_payment(self, payment):
        """Verify TON payment using TonAPI"""
        try:
            wallet_address = payment['wallet_address']
            memo = payment['memo']
            amount = payment['amount']
            
            # Check TonAPI for transactions
            async with aiohttp.ClientSession() as session:
                url = f"https://tonapi.io/v2/accounts/{wallet_address}/transactions"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for tx in data.get('transactions', []):
                            if self.is_payment_transaction(tx, memo, amount):
                                await self.confirm_payment(payment['id'])
                                logger.info(f"✅ Payment confirmed: {payment['id']}")
                                return
                                
        except Exception as e:
            logger.error(f"TON payment verification error: {e}")
    
    def is_payment_transaction(self, transaction, expected_memo, expected_amount):
        """Check if transaction matches expected payment"""
        try:
            # Extract memo and amount from transaction
            if 'out_msgs' in transaction:
                for msg in transaction['out_msgs']:
                    if 'decoded_body' in msg:
                        comment = msg['decoded_body'].get('comment', '')
                        if comment == expected_memo:
                            # Check amount (convert from nanotons)
                            value = int(msg.get('value', 0)) / 1_000_000_000
                            if abs(value - expected_amount) < 0.01:
                                return True
            return False
        except:
            return False
    
    async def confirm_payment(self, payment_id):
        """Confirm payment and activate subscription"""
        await self.db.confirm_payment(payment_id)
        await self.db.activate_subscription(payment_id)
    
    async def channel_analytics_updater(self):
        """Update channel analytics periodically"""
        logger.info("📊 Starting channel analytics updater...")
        
        while self.running:
            try:
                channels = await self.db.get_active_channels()
                
                for channel in channels:
                    await self.update_channel_stats(channel)
                
                # Update every 6 hours
                await asyncio.sleep(6 * 3600)
                
            except Exception as e:
                logger.error(f"Analytics updater error: {e}")
                await asyncio.sleep(3600)
    
    async def update_channel_stats(self, channel):
        """Update individual channel statistics"""
        try:
            # This would use Telegram API to get real stats
            # For now, we'll update the last_updated field
            await self.db.update_channel_stats(
                channel['id'],
                channel['subscribers'],
                channel['active_subscribers'],
                datetime.now()
            )
            logger.info(f"Updated stats for channel: {channel['name']}")
            
        except Exception as e:
            logger.error(f"Channel stats update error: {e}")
    
    async def reward_processor(self):
        """Process pending rewards"""
        logger.info("🎁 Starting reward processor...")
        
        while self.running:
            try:
                pending_rewards = await self.db.get_pending_rewards()
                
                for reward in pending_rewards:
                    await self.process_reward(reward)
                
                # Process every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Reward processor error: {e}")
                await asyncio.sleep(600)
    
    async def process_reward(self, reward):
        """Process individual reward"""
        try:
            # Calculate reward amount based on type
            amount = await self.calculate_reward_amount(reward)
            
            # Add to user's balance
            await self.db.add_reward_balance(reward['user_id'], amount)
            
            # Mark as processed
            await self.db.mark_reward_processed(reward['id'])
            
            logger.info(f"Processed reward: {reward['type']} for user {reward['user_id']}")
            
        except Exception as e:
            logger.error(f"Reward processing error: {e}")
    
    async def calculate_reward_amount(self, reward):
        """Calculate reward amount based on type"""
        reward_amounts = {
            'referral': 2.0,
            'registration': 5.0,
            'channel_addition': 10.0,
            'monthly_bonus': 25.0
        }
        return reward_amounts.get(reward['type'], 0.0)
    
    async def database_cleanup(self):
        """Clean up old data"""
        logger.info("🧹 Starting database cleanup...")
        
        while self.running:
            try:
                # Clean up old logs (keep last 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                await self.db.cleanup_old_logs(cutoff_date)
                
                # Clean up expired sessions
                await self.db.cleanup_expired_sessions()
                
                # Clean up temporary files
                await self.cleanup_temp_files()
                
                logger.info("Database cleanup completed")
                
                # Run daily
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                logger.error(f"Database cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            temp_dir = "/tmp"
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    if file.startswith("i3lani_"):
                        file_path = os.path.join(temp_dir, file)
                        if os.path.getctime(file_path) < time.time() - 86400:  # 24 hours
                            os.remove(file_path)
        except Exception as e:
            logger.error(f"Temp file cleanup error: {e}")
    
    async def health_checker(self):
        """Health check and monitoring"""
        logger.info("❤️ Starting health checker...")
        
        while self.running:
            try:
                # Check database connection
                await self.db.check_connection()
                
                # Check disk space
                await self.check_disk_space()
                
                # Check memory usage
                await self.check_memory_usage()
                
                # Log health status
                logger.info("Health check completed - all systems operational")
                
                # Check every 15 minutes
                await asyncio.sleep(900)
                
            except Exception as e:
                logger.error(f"Health checker error: {e}")
                await asyncio.sleep(300)
    
    async def check_disk_space(self):
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_gb = free / (1024**3)
            
            if free_gb < 1:  # Less than 1GB free
                logger.warning(f"Low disk space: {free_gb:.2f}GB free")
                
        except Exception as e:
            logger.error(f"Disk space check error: {e}")
    
    async def check_memory_usage(self):
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                logger.warning(f"High memory usage: {memory.percent}%")
                
        except Exception as e:
            logger.error(f"Memory check error: {e}")
    
    def stop(self):
        """Stop the worker"""
        logger.info("Stopping background worker...")
        self.running = False

async def main():
    """Main worker entry point"""
    worker = BackgroundWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        worker.stop()
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())