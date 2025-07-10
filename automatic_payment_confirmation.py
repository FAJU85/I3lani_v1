#!/usr/bin/env python3
"""
Automatic Payment Confirmation System
Sends automatic confirmations to users when payments are detected
"""

import asyncio
import logging
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomaticPaymentConfirmation:
    """Automatic payment confirmation system"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        
    async def init_tables(self):
        """Initialize payment tracking tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create payment_memo_tracking table for user -> memo mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_memo_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    memo TEXT NOT NULL UNIQUE,
                    amount REAL NOT NULL,
                    payment_method TEXT DEFAULT 'TON',
                    ad_data TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confirmed_at TIMESTAMP NULL
                );
            """)
            
            # Create index for faster memo lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memo_tracking_memo 
                ON payment_memo_tracking(memo);
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Payment confirmation tables initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing confirmation tables: {e}")
            return False
    
    async def track_user_payment(self, user_id: int, memo: str, amount: float, ad_data: dict = None):
        """Track user payment for automatic confirmation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ALWAYS get actual user ad content to ensure real content is used
            actual_ad_content = await self._get_user_ad_content(user_id)
            if actual_ad_content:
                if not ad_data:
                    ad_data = {}
                # Override any existing content with actual user content
                ad_data.update(actual_ad_content)
                logger.info(f"✅ Retrieved real user content for user {user_id}: {actual_ad_content.get('ad_content', '')[:50]}...")
            
            # Store ad_data as JSON - prioritize real user content
            if ad_data and ad_data.get('ad_content'):
                ad_data_json = json.dumps(ad_data)
                logger.info(f"✅ Stored real user content: {ad_data.get('ad_content', '')[:50]}...")
            else:
                # Fallback only if no real content available
                ad_data_json = json.dumps({
                    'duration_days': 7,
                    'posts_per_day': 2,
                    'selected_channels': ['@i3lani', '@smshco', '@Five_SAR'],
                    'total_reach': 357,
                    'ad_content': f'Fallback content for user {user_id} - no ad found'
                })
                logger.warning(f"⚠️ Using fallback content for user {user_id} - no real ad content found")
            
            cursor.execute("""
                INSERT OR REPLACE INTO payment_memo_tracking 
                (user_id, memo, amount, ad_data, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (user_id, memo, amount, ad_data_json))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Tracking payment {memo} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error tracking user payment: {e}")
            return False
    
    async def find_user_by_memo(self, memo: str) -> Optional[Dict[str, Any]]:
        """Find user by payment memo"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, memo, amount, ad_data, status, created_at
                FROM payment_memo_tracking 
                WHERE memo = ? AND status = 'pending'
            """, (memo,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_id': row['user_id'],
                    'memo': row['memo'],
                    'amount': row['amount'],
                    'ad_data': json.loads(row['ad_data']) if row['ad_data'] else {},
                    'status': row['status'],
                    'created_at': row['created_at']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding user by memo: {e}")
            return None
    
    async def send_automatic_confirmation(self, user_id: int, memo: str, amount: float, ad_data: dict):
        """Send automatic confirmation to user"""
        try:
            from main_bot import bot_instance
            
            if not bot_instance:
                logger.error("❌ Bot instance not available")
                return False
            
            # Create confirmation message
            confirmation_message = f"""✅ **Payment Automatically Confirmed!**

💰 **Amount:** {amount} TON
🎫 **Transaction ID:** {memo}
📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎉 **Your advertisement campaign is now ACTIVE!**

**Campaign Details:**
• Duration: {ad_data.get('duration_days', 7)} days
• Channels: {len(ad_data.get('selected_channels', []))} channels
• Total reach: {ad_data.get('total_reach', 357)} subscribers
• Posts per day: {ad_data.get('posts_per_day', 2)} posts

Your advertisement will be published across selected channels according to your schedule.

Thank you for choosing I3lani! 🚀"""
            
            # Create navigation keyboard
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")],
                [InlineKeyboardButton(text="📊 My Ads", callback_data="my_ads")]
            ])
            
            # Send confirmation
            await bot_instance.send_message(
                user_id, 
                confirmation_message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            # Mark as confirmed
            await self.mark_payment_confirmed(memo)
            
            # Activate campaign and get campaign ID
            campaign_id = await self.activate_campaign(user_id, memo, amount, ad_data)
            
            # Update confirmation message to include campaign ID
            if campaign_id:
                confirmation_message += f"\n\n**🎯 Campaign ID:** {campaign_id}"
            
            logger.info(f"✅ Automatic confirmation sent to user {user_id} for memo {memo}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending automatic confirmation: {e}")
            return False
    
    async def mark_payment_confirmed(self, memo: str):
        """Mark payment as confirmed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE payment_memo_tracking 
                SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
                WHERE memo = ?
            """, (memo,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Payment {memo} marked as confirmed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking payment confirmed: {e}")
            return False
    
    async def mark_payment_confirmed(self, memo: str, campaign_id: str = None):
        """Mark payment as confirmed with optional campaign ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE payment_memo_tracking 
                SET status = 'confirmed', 
                    confirmed_at = CURRENT_TIMESTAMP,
                    ad_data = CASE 
                        WHEN ? IS NOT NULL THEN 
                            json_set(COALESCE(ad_data, '{}'), '$.campaign_id', ?)
                        ELSE ad_data 
                    END
                WHERE memo = ?
            """, (campaign_id, campaign_id, memo))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Payment {memo} marked as confirmed with campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking payment confirmed: {e}")
            return False
    
    async def activate_campaign(self, user_id: int, memo: str, amount: float, ad_data: dict):
        """Activate user campaign with unique ID"""
        try:
            # Create campaign using the new campaign management system
            from campaign_management import create_campaign_for_payment
            
            campaign_id = await create_campaign_for_payment(
                user_id, memo, amount, ad_data, 'TON'
            )
            
            if campaign_id:
                logger.info(f"✅ Campaign {campaign_id} activated for user {user_id}, memo {memo}")
                return campaign_id
            else:
                logger.error(f"❌ Failed to create campaign for user {user_id}, memo {memo}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error activating campaign: {e}")
            return False
    
    async def _get_user_ad_content(self, user_id: int) -> dict:
        """Get actual user ad content from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get most recent ad by user
            cursor.execute('''
                SELECT ad_id, content, content_type, media_url
                FROM ads 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'ad_content': row['content'],
                    'content_type': row['content_type'],
                    'media_url': row['media_url'],
                    'ad_id': row['ad_id']
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting user ad content: {e}")
            return {}

# Global instance
automatic_confirmation = AutomaticPaymentConfirmation()

async def init_automatic_confirmation():
    """Initialize automatic confirmation system"""
    return await automatic_confirmation.init_tables()

async def track_payment_for_user(user_id: int, memo: str, amount: float, ad_data: dict = None):
    """Track payment for automatic confirmation"""
    return await automatic_confirmation.track_user_payment(user_id, memo, amount, ad_data)

async def handle_confirmed_payment(payment_data: dict):
    """Handle confirmed payment and create campaign automatically"""
    try:
        user_id = payment_data['user_id']
        memo = payment_data['memo']
        amount = payment_data['amount']
        currency = payment_data.get('currency', 'TON')
        payment_method = payment_data.get('payment_method', 'blockchain')
        
        logger.info(f"🎯 Processing confirmed {currency} payment: user {user_id}, memo {memo}, amount {amount}")
        
        # Get tracked payment data
        user_data = await automatic_confirmation.find_user_by_memo(memo)
        
        if not user_data:
            logger.error(f"❌ No tracked payment found for memo {memo}")
            return False
        
        # Create campaign automatically using campaign management system
        try:
            from campaign_management import create_campaign_for_payment
            
            campaign_data = {
                'user_id': user_id,
                'payment_memo': memo,
                'payment_amount': amount,
                'payment_currency': currency,
                'payment_method': payment_method,
                'ad_data': user_data.get('ad_data', {})
            }
            
            campaign_id = await create_campaign_for_payment(campaign_data)
            
            if campaign_id:
                logger.info(f"✅ Campaign {campaign_id} created for {currency} payment {memo}")
                
                # Mark payment as confirmed
                await automatic_confirmation.mark_payment_confirmed(memo, campaign_id)
                
                return True
            else:
                logger.error(f"❌ Failed to create campaign for {currency} payment {memo}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating campaign for {currency} payment: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error handling confirmed {payment_data.get('currency', 'unknown')} payment: {e}")
        return False

async def process_detected_payment(memo: str, amount: float):
    """Process payment detected by scanner"""
    user_data = await automatic_confirmation.find_user_by_memo(memo)
    
    if user_data:
        logger.info(f"🎯 Found user {user_data['user_id']} for memo {memo}")
        
        # Send automatic confirmation
        success = await automatic_confirmation.send_automatic_confirmation(
            user_data['user_id'],
            memo,
            amount,
            user_data['ad_data']
        )
        
        if success:
            logger.info(f"✅ Automatic confirmation sent for memo {memo}")
        else:
            logger.error(f"❌ Failed to send confirmation for memo {memo}")
        
        return success
    else:
        logger.warning(f"⚠️ No user found for memo {memo}")
        return False

if __name__ == "__main__":
    async def test_system():
        await init_automatic_confirmation()
        
        # Test tracking a payment
        await track_payment_for_user(123456, "TE1234", 0.36, {
            'duration_days': 7,
            'posts_per_day': 2,
            'selected_channels': ['@i3lani', '@smshco', '@Five_SAR'],
            'total_reach': 357
        })
        
        # Test processing detected payment
        await process_detected_payment("TE1234", 0.36)
    
    asyncio.run(test_system())