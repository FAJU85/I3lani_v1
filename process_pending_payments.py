#!/usr/bin/env python3
"""
Process Pending Payments Script
Automatically processes all pending payment reviews and creates campaigns
"""

import asyncio
import aiosqlite
import logging
import random
from datetime import datetime, timedelta
from quantitative_pricing_system import QuantitativePricingCalculator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PendingPaymentProcessor:
    """Process pending payments and create campaigns"""
    
    def __init__(self):
        self.calculator = QuantitativePricingCalculator()
        self.processed_count = 0
        self.error_count = 0
    
    async def get_pending_payments(self):
        """Get all pending payments"""
        async with aiosqlite.connect('bot.db') as db:
            cursor = await db.execute("""
                SELECT memo, amount, created_at, status 
                FROM untracked_payments 
                WHERE status = 'pending_review' 
                ORDER BY created_at DESC
            """)
            return await cursor.fetchall()
    
    async def find_user_for_payment(self, memo: str, amount: float, created_at: str):
        """Find user associated with payment based on patterns"""
        async with aiosqlite.connect('bot.db') as db:
            # Check if payment is already tracked
            cursor = await db.execute("""
                SELECT user_id FROM payment_memo_tracking 
                WHERE memo = ?
            """, (memo,))
            result = await cursor.fetchone()
            
            if result:
                return result[0]
            
            # Find user based on recent activity and payment timing
            # Look for users who created ads around the payment time
            payment_time = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            time_window_start = payment_time - timedelta(hours=24)  # Extended window
            time_window_end = payment_time + timedelta(hours=24)
            
            cursor = await db.execute("""
                SELECT user_id, COUNT(*) as ad_count 
                FROM ads 
                WHERE created_at BETWEEN ? AND ?
                GROUP BY user_id
                ORDER BY ad_count DESC
            """, (time_window_start.strftime('%Y-%m-%d %H:%M:%S'),
                  time_window_end.strftime('%Y-%m-%d %H:%M:%S')))
            
            users = await cursor.fetchall()
            
            # Return most active user in time window
            if users:
                return users[0][0]
            
            # If no users found in time window, get most recent user
            cursor = await db.execute("""
                SELECT user_id FROM ads 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            result = await cursor.fetchone()
            
            return result[0] if result else 566158428  # Default user ID
    
    async def get_user_recent_ad(self, user_id: int):
        """Get user's most recent ad for campaign creation"""
        async with aiosqlite.connect('bot.db') as db:
            cursor = await db.execute("""
                SELECT content, content_type, media_url, created_at
                FROM ads 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id,))
            return await cursor.fetchone()
    
    async def determine_campaign_parameters(self, amount: float):
        """Determine campaign parameters based on payment amount"""
        # Standard amounts and their configurations
        amount_configs = {
            0.36: {'days': 7, 'channels': 2},    # Most common
            0.27: {'days': 5, 'channels': 2},    # Small package
            0.18: {'days': 3, 'channels': 2},    # Mini package
            0.72: {'days': 14, 'channels': 2},   # Extended package
        }
        
        # Find closest amount configuration
        closest_amount = min(amount_configs.keys(), key=lambda x: abs(x - amount))
        
        if abs(amount - closest_amount) <= 0.05:  # Within 5 cents tolerance
            return amount_configs[closest_amount]
        else:
            # Default configuration for unknown amounts
            return {'days': 7, 'channels': 2}
    
    async def get_active_channels(self, limit: int = 2):
        """Get active channels for campaign"""
        async with aiosqlite.connect('bot.db') as db:
            cursor = await db.execute("""
                SELECT channel_id, name, subscribers 
                FROM channels 
                WHERE is_active = 1
                ORDER BY subscribers DESC
                LIMIT ?
            """, (limit,))
            return await cursor.fetchall()
    
    async def create_campaign_from_payment(self, memo: str, amount: float, user_id: int, 
                                         ad_content: tuple, campaign_params: dict):
        """Create campaign from payment details"""
        try:
            # Generate campaign ID
            today = datetime.now()
            campaign_id = f"CAM-{today.strftime('%Y-%m')}-{memo[:4]}"
            
            # Get campaign parameters
            days = campaign_params['days']
            channels = await self.get_active_channels(campaign_params['channels'])
            
            # Calculate pricing
            pricing = self.calculator.calculate_price(days, len(channels))
            posts_per_day = pricing['posts_per_day']
            
            # Get ad details
            content, content_type, media_url, _ = ad_content
            
            # Create campaign
            async with aiosqlite.connect('bot.db') as db:
                await db.execute("""
                    INSERT INTO campaigns (
                        campaign_id, user_id, content, content_type, media_url,
                        selected_channels, duration_days, posts_per_day,
                        payment_amount, payment_method, payment_memo, status,
                        created_at, start_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    campaign_id, user_id, content, content_type, media_url,
                    ','.join([ch[0] for ch in channels]), days, posts_per_day,
                    amount, 'TON', memo, 'active',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                
                # Create scheduled posts
                total_posts = days * posts_per_day * len(channels)
                base_time = datetime.now()
                
                for day in range(days):
                    for post_num in range(posts_per_day):
                        for channel in channels:
                            # Calculate posting time
                            hours_offset = (day * 24) + (post_num * (24 / posts_per_day))
                            post_time = base_time + timedelta(hours=hours_offset)
                            
                            # Create post
                            await db.execute("""
                                INSERT INTO campaign_posts (
                                    campaign_id, channel_id, content, content_type, media_url,
                                    scheduled_time, status, created_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                campaign_id, channel[0], content, content_type, media_url,
                                post_time.strftime('%Y-%m-%d %H:%M:%S'), 'scheduled',
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            ))
                
                # Update payment tracking
                await db.execute("""
                    INSERT OR REPLACE INTO payment_memo_tracking (memo, user_id, campaign_id)
                    VALUES (?, ?, ?)
                """, (memo, user_id, campaign_id))
                
                # Update payment status
                await db.execute("""
                    UPDATE untracked_payments 
                    SET status = 'processed', processed_at = ?
                    WHERE memo = ?
                """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), memo))
                
                await db.commit()
                
                logger.info(f"✅ Created campaign {campaign_id} for payment {memo}")
                logger.info(f"   User: {user_id}, Amount: {amount} TON")
                logger.info(f"   Duration: {days} days, Posts/day: {posts_per_day}")
                logger.info(f"   Channels: {len(channels)}, Total posts: {total_posts}")
                
                return campaign_id
                
        except Exception as e:
            logger.error(f"❌ Error creating campaign for payment {memo}: {str(e)}")
            raise
    
    async def process_single_payment(self, memo: str, amount: float, created_at: str, status: str):
        """Process a single pending payment"""
        try:
            logger.info(f"🔄 Processing payment {memo} ({amount} TON)")
            
            # Find user
            user_id = await self.find_user_for_payment(memo, amount, created_at)
            if not user_id:
                logger.warning(f"⚠️  Could not find user for payment {memo}")
                return False
            
            # Get user's ad
            ad_content = await self.get_user_recent_ad(user_id)
            if not ad_content:
                logger.warning(f"⚠️  No ad content found for user {user_id}")
                return False
            
            # Determine campaign parameters
            campaign_params = await self.determine_campaign_parameters(amount)
            
            # Create campaign
            campaign_id = await self.create_campaign_from_payment(
                memo, amount, user_id, ad_content, campaign_params
            )
            
            if campaign_id:
                self.processed_count += 1
                return True
            else:
                self.error_count += 1
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing payment {memo}: {str(e)}")
            self.error_count += 1
            return False
    
    async def process_all_pending_payments(self):
        """Process all pending payments"""
        logger.info("🚀 Starting pending payments processing...")
        
        # Get all pending payments
        pending_payments = await self.get_pending_payments()
        
        if not pending_payments:
            logger.info("✅ No pending payments to process")
            return
        
        logger.info(f"📊 Found {len(pending_payments)} pending payments")
        
        # Process each payment
        for memo, amount, created_at, status in pending_payments:
            await self.process_single_payment(memo, amount, created_at, status)
            
            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.1)
        
        # Report results
        logger.info("=" * 60)
        logger.info(f"📋 Processing Summary:")
        logger.info(f"   ✅ Processed: {self.processed_count}")
        logger.info(f"   ❌ Errors: {self.error_count}")
        logger.info(f"   📊 Total: {len(pending_payments)}")
        logger.info(f"   🎯 Success rate: {(self.processed_count/len(pending_payments)*100):.1f}%")
        logger.info("=" * 60)

async def main():
    """Main function"""
    processor = PendingPaymentProcessor()
    await processor.process_all_pending_payments()

if __name__ == "__main__":
    asyncio.run(main())