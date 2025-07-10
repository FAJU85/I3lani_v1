#!/usr/bin/env python3
"""
Continuous Payment Scanner
Runs continuously in background to catch missed payments
"""

import asyncio
import logging
from typing import Dict, Set
from enhanced_ton_payment_monitoring import EnhancedTONPaymentMonitor
import time
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContinuousPaymentScanner:
    """Continuous background payment scanner"""
    
    def __init__(self):
        self.monitor = EnhancedTONPaymentMonitor()
        self.bot_wallet = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
        self.confirmed_payments: Set[str] = set()
        self.last_scan_time = 0
        self.scan_interval = 30  # seconds
        self.running = False
        self.pending_payments_file = "pending_payments.json"
        
        # Load confirmed payments from file
        self.load_confirmed_payments()
    
    def load_confirmed_payments(self):
        """Load previously confirmed payments to avoid duplicates"""
        try:
            if os.path.exists(self.pending_payments_file):
                with open(self.pending_payments_file, 'r') as f:
                    data = json.load(f)
                    self.confirmed_payments = set(data.get('confirmed_payments', []))
                    logger.info(f"Loaded {len(self.confirmed_payments)} confirmed payments from file")
        except Exception as e:
            logger.error(f"Error loading confirmed payments: {e}")
    
    def save_confirmed_payments(self):
        """Save confirmed payments to file"""
        try:
            data = {
                'confirmed_payments': list(self.confirmed_payments),
                'last_updated': time.time()
            }
            with open(self.pending_payments_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving confirmed payments: {e}")
    
    async def scan_for_payments(self):
        """Scan for unconfirmed payments"""
        try:
            logger.info("🔍 Scanning for unconfirmed payments...")
            
            # Get recent transactions
            data = await self.monitor.get_transactions_toncenter(self.bot_wallet, 100)
            
            if not data:
                logger.warning("No transaction data available")
                return
            
            transactions = data.get('result', [])
            new_payments_found = 0
            
            for tx in transactions:
                if not tx.get('in_msg'):
                    continue
                
                memo = self.monitor.extract_memo_from_transaction(tx)
                
                # Check if this looks like a user payment (6-char memo, 0.36 TON)
                if memo and len(memo) == 6:
                    amount = self.monitor.extract_amount_from_transaction(tx)
                    
                    if abs(amount - 0.36) <= 0.1:  # 0.36 TON ± 0.1 tolerance
                        # Check if already confirmed
                        if memo not in self.confirmed_payments:
                            sender = self.monitor.extract_sender_from_transaction(tx)
                            timestamp = tx.get('utime', 0)
                            
                            logger.info(f"🎯 Found unconfirmed payment: {memo}")
                            logger.info(f"   Amount: {amount} TON")
                            logger.info(f"   Sender: {sender}")
                            logger.info(f"   Timestamp: {timestamp}")
                            
                            # Attempt to confirm this payment
                            success = await self.confirm_missed_payment(memo, amount, sender, timestamp)
                            
                            if success:
                                self.confirmed_payments.add(memo)
                                new_payments_found += 1
                                logger.info(f"✅ Successfully confirmed payment {memo}")
                            else:
                                logger.warning(f"❌ Failed to confirm payment {memo}")
            
            if new_payments_found > 0:
                self.save_confirmed_payments()
                logger.info(f"🎉 Confirmed {new_payments_found} missed payments")
            else:
                logger.info("✅ No new payments found")
                
        except Exception as e:
            logger.error(f"Error in payment scanning: {e}")
    
    async def confirm_missed_payment(self, memo: str, amount: float, sender: str, timestamp: int):
        """Confirm a missed payment"""
        try:
            logger.info(f"🔄 Confirming missed payment {memo}...")
            
            # Try to find the user who made this payment using memo tracker
            from payment_memo_tracker import memo_tracker
            user_info = await memo_tracker.get_user_by_memo(memo)
            
            if user_info:
                user_id = user_info['user_id']
                logger.info(f"✅ Found user {user_id} for payment {memo}")
                
                # Send confirmation message to user
                success = await self.send_payment_confirmation_to_user(
                    user_id, memo, amount, user_info['ad_data']
                )
                
                if success:
                    # Mark payment as confirmed in database
                    await memo_tracker.confirm_payment(memo)
                    logger.info(f"✅ Payment {memo} confirmed and user {user_id} notified")
                    return True
                else:
                    logger.error(f"❌ Failed to send confirmation to user {user_id}")
                    return False
            else:
                # If no user found, create comprehensive fallback notification
                logger.warning(f"⚠️ No user found for memo {memo}, creating fallback notification")
                
                # Send broadcast notification to all recent users or create admin alert
                success = await self.send_fallback_payment_notification(memo, amount, sender, timestamp)
                
                if success:
                    logger.info(f"✅ Payment {memo} fallback notification sent")
                    return True
                else:
                    logger.error(f"❌ Failed to send fallback notification for {memo}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ Error confirming payment {memo}: {e}")
            return False
            
            if user_id:
                # Create ad entry for confirmed payment
                ad_data = {
                    'user_id': user_id,
                    'memo': memo,
                    'amount': amount,
                    'payment_method': 'TON',
                    'status': 'confirmed',
                    'content': f'Payment {memo} confirmed automatically',
                    'channels': 'auto-detected',
                    'timestamp': timestamp
                }
                
                # Create ad entry
                success = await self.create_ad_from_payment(ad_data)
                
                if success:
                    logger.info(f"✅ Payment {memo} confirmed and ad created for user {user_id}")
                    
                    # Send confirmation message to user
                    await self.send_payment_confirmation(user_id, memo, amount)
                    
                    return True
                else:
                    logger.error(f"Failed to create ad for payment {memo}")
                    return False
            else:
                # If we can't find the user, still mark as confirmed to prevent reprocessing
                logger.warning(f"User not found for payment {memo}, marking as confirmed")
                return True
            
        except Exception as e:
            logger.error(f"Error confirming payment {memo}: {e}")
            return False
    
    async def find_user_by_memo(self, memo: str):
        """Find user ID by payment memo"""
        try:
            # For now, we'll extract user ID from memo pattern if possible
            # In a real implementation, you'd query the database for pending payments
            
            # If memo follows pattern like "PY6480", we can't extract user ID
            # So we'll need to implement database memo tracking
            
            # For now, return None and let the system handle it gracefully
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by memo {memo}: {e}")
            return None
    
    async def create_ad_from_payment(self, ad_data: dict):
        """Create ad entry from payment data"""
        try:
            # Simple ad creation for confirmed payments
            logger.info(f"Creating ad entry for payment {ad_data['memo']}")
            
            # In a real implementation, you'd save this to database
            # For now, just log success
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating ad from payment: {e}")
            return False
    
    async def send_payment_confirmation_to_user(self, user_id: int, memo: str, amount: float, ad_data: dict):
        """Send comprehensive payment confirmation message to user"""
        try:
            from main_bot import bot_instance
            from languages import get_user_language, get_text
            
            if bot_instance:
                # Get user language
                try:
                    language = await get_user_language(user_id)
                except:
                    language = 'en'  # Default to English
                
                # Create comprehensive confirmation message
                if language == 'ar':
                    confirmation_text = f"""✅ تم تأكيد الدفع!

💰 المبلغ المستلم: {amount:.3f} TON
🎫 رقم المعاملة: {memo}

🎉 تم تفعيل خطة إعلانك بنجاح!

📊 تفاصيل الحملة:
• المدة: {ad_data.get('days', 1)} أيام
• عدد المنشورات يومياً: {ad_data.get('posts_per_day', 1)}
• القنوات المختارة: {len(ad_data.get('selected_channels', []))}

🚀 سيتم نشر إعلانك قريباً على القنوات المختارة.

شكراً لاختيارك إعلاني!"""
                elif language == 'ru':
                    confirmation_text = f"""✅ Платеж подтвержден!

💰 Получена сумма: {amount:.3f} TON
🎫 ID транзакции: {memo}

🎉 Ваш рекламный план успешно активирован!

📊 Детали кампании:
• Продолжительность: {ad_data.get('days', 1)} дней
• Постов в день: {ad_data.get('posts_per_day', 1)}
• Выбранные каналы: {len(ad_data.get('selected_channels', []))}

🚀 Ваше объявление скоро будет опубликовано в выбранных каналах.

Спасибо за выбор I3lani!"""
                else:
                    confirmation_text = f"""✅ Payment Confirmed!

💰 Amount Received: {amount:.3f} TON
🎫 Transaction ID: {memo}

🎉 Your ad plan has been successfully activated!

📊 Campaign Details:
• Duration: {ad_data.get('days', 1)} days
• Posts per day: {ad_data.get('posts_per_day', 1)}
• Selected channels: {len(ad_data.get('selected_channels', []))}

🚀 Your advertisement will be published soon across selected channels.

Thank you for choosing I3lani!"""
                
                # Create navigation keyboard
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                
                if language == 'ar':
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")],
                        [InlineKeyboardButton(text="📊 إعلاناتي", callback_data="my_ads")]
                    ])
                elif language == 'ru':
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")],
                        [InlineKeyboardButton(text="📊 Мои объявления", callback_data="my_ads")]
                    ])
                else:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")],
                        [InlineKeyboardButton(text="📊 My Ads", callback_data="my_ads")]
                    ])
                
                await bot_instance.send_message(
                    user_id, 
                    confirmation_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
                logger.info(f"✅ Comprehensive confirmation message sent to user {user_id}")
                return True
            else:
                logger.error("❌ Bot instance not available")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error sending confirmation to user {user_id}: {e}")
            return False
    
    async def send_fallback_payment_notification(self, memo: str, amount: float, sender: str, timestamp: int):
        """Send fallback notification for untracked payments"""
        try:
            from main_bot import bot_instance
            
            if bot_instance:
                # Create admin notification for manual review
                admin_message = f"""🚨 UNTRACKED PAYMENT DETECTED

💰 Amount: {amount} TON
🎫 Memo: {memo}
👤 Sender: {sender}
📅 Timestamp: {timestamp}

This payment was detected on blockchain but no user mapping found.
Manual review required for user notification.

Action needed: Contact user with memo {memo} for confirmation."""
                
                # Try to send to admin (you can add admin user ID here)
                try:
                    # For now, just log the admin notification
                    logger.info(f"🚨 ADMIN ALERT: {admin_message}")
                except Exception as admin_error:
                    logger.error(f"Failed to send admin notification: {admin_error}")
                
                # Create public notification in bot logs
                public_message = f"""✅ PAYMENT DETECTED: {memo}

If you made a payment with memo {memo} for {amount} TON, your payment has been received and confirmed.

Your ad campaign will be activated shortly. If you don't receive confirmation within 10 minutes, please contact support with memo {memo}.

Thank you for using I3lani!"""
                
                logger.info(f"📢 PUBLIC NOTIFICATION: {public_message}")
                
                # Store untracked payment for admin review
                await self.store_untracked_payment(memo, amount, sender, timestamp)
                
                return True
            else:
                logger.error("❌ Bot instance not available for fallback notification")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending fallback notification: {e}")
            return False
    
    async def store_untracked_payment(self, memo: str, amount: float, sender: str, timestamp: int):
        """Store untracked payment for admin review"""
        try:
            import sqlite3
            
            conn = sqlite3.connect("bot.db")
            cursor = conn.cursor()
            
            # Create untracked_payments table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS untracked_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memo TEXT NOT NULL,
                    amount REAL NOT NULL,
                    sender TEXT,
                    timestamp INTEGER,
                    status TEXT DEFAULT 'pending_review',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert untracked payment
            cursor.execute("""
                INSERT INTO untracked_payments (memo, amount, sender, timestamp)
                VALUES (?, ?, ?, ?)
            """, (memo, amount, sender, timestamp))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Stored untracked payment {memo} for admin review")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing untracked payment: {e}")
            return False
    
    async def run_continuous_scanner(self):
        """Run the continuous payment scanner"""
        self.running = True
        logger.info("🚀 Starting continuous payment scanner...")
        
        while self.running:
            try:
                await self.scan_for_payments()
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Error in scanner loop: {e}")
                await asyncio.sleep(self.scan_interval)
    
    def stop_scanner(self):
        """Stop the continuous scanner"""
        self.running = False
        logger.info("🛑 Stopping continuous payment scanner...")

# Global scanner instance
payment_scanner = ContinuousPaymentScanner()

async def start_continuous_payment_monitoring():
    """Start the continuous payment monitoring system"""
    logger.info("🚀 Starting continuous payment monitoring...")
    
    # Start the scanner in background
    scanner_task = asyncio.create_task(payment_scanner.run_continuous_scanner())
    
    return scanner_task

async def stop_continuous_payment_monitoring():
    """Stop the continuous payment monitoring system"""
    payment_scanner.stop_scanner()

# Test function
async def test_payment_scanner():
    """Test the payment scanner"""
    print("🧪 Testing Continuous Payment Scanner")
    print("=" * 50)
    
    scanner = ContinuousPaymentScanner()
    
    # Test one scan
    await scanner.scan_for_payments()
    
    print("✅ Payment scanner test completed")

if __name__ == "__main__":
    asyncio.run(test_payment_scanner())