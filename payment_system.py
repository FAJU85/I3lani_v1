"""
Enhanced Payment System with TON Integration
Handles automatic payment detection, memo generation, and currency conversion
"""

import asyncio
import aiohttp
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from database import SessionLocal, Order, PaymentTracking, CurrencyRate, AdminSettings
import os

logger = logging.getLogger(__name__)

class PaymentSystem:
    def __init__(self):
        self.ton_api_key = os.getenv('TON_API_KEY', '')
        self.tonapi_base = "https://tonapi.io/v2"
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.monitoring_tasks = {}
        
    async def generate_payment_memo(self) -> str:
        """Generate unique payment memo with collision prevention"""
        db = SessionLocal()
        try:
            max_attempts = 10
            for _ in range(max_attempts):
                # Generate memo: INV_ + 8 random characters
                memo = "INV_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                
                # Check if memo already exists
                existing = db.query(PaymentTracking).filter(PaymentTracking.memo == memo).first()
                if not existing:
                    return memo
            
            raise Exception("Failed to generate unique memo after multiple attempts")
        finally:
            db.close()
    
    async def get_ton_wallet_address(self) -> str:
        """Get current TON wallet address from admin settings"""
        db = SessionLocal()
        try:
            setting = db.query(AdminSettings).filter(AdminSettings.key == 'ton_wallet_address').first()
            return setting.value if setting else os.getenv('TON_WALLET_ADDRESS', '')
        finally:
            db.close()
    
    async def create_payment_order(self, user_id: int, channel_ids: List[str], 
                                 duration_months: int, bundle_id: Optional[str] = None) -> Dict:
        """Create new payment order with pricing calculation"""
        db = SessionLocal()
        try:
            from database import Channel, Bundle, User
            
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                # Create user if doesn't exist
                user = User(id=user_id)
                db.add(user)
                db.flush()
            
            # Get selected channels
            channels = db.query(Channel).filter(Channel.id.in_(channel_ids)).all()
            if not channels:
                raise ValueError("No valid channels selected")
            
            # Calculate pricing
            base_price = sum(channel.price_per_month for channel in channels) * duration_months
            total_price_ton = base_price
            discount_percent = 0.0
            bonus_months = 0
            
            # Apply bundle discount if applicable
            if bundle_id:
                bundle = db.query(Bundle).filter(Bundle.id == bundle_id).first()
                if bundle and bundle.is_active:
                    discount_percent = bundle.discount_percent
                    bonus_months = bundle.bonus_months
                    total_price_ton = base_price * (1 - discount_percent / 100)
            
            # Convert to other currencies
            usd_price = await self.convert_ton_to_currency(total_price_ton, 'USD')
            
            # Generate payment memo and get wallet
            memo = await self.generate_payment_memo()
            wallet_address = await self.get_ton_wallet_address()
            
            # Create order
            order = Order(
                user_id=user_id,
                payment_memo=memo,
                wallet_address=wallet_address,
                total_amount_ton=total_price_ton,
                total_amount_usd=usd_price,
                duration_months=duration_months,
                bonus_months=bonus_months,
                bundle_id=bundle_id,
                posts_total=duration_months * 30 * len(channels),  # 30 posts per month per channel
                expires_at=datetime.utcnow() + timedelta(minutes=30)  # 30 min payment window
            )
            
            db.add(order)
            db.flush()
            
            # Associate channels
            order.channels = channels
            
            # Create payment tracking
            payment_tracking = PaymentTracking(
                order_id=order.id,
                memo=memo,
                expected_amount=total_price_ton
            )
            db.add(payment_tracking)
            
            db.commit()
            
            # Start payment monitoring
            await self.start_payment_monitoring(order.id)
            
            return {
                'order_id': order.id,
                'memo': memo,
                'wallet_address': wallet_address,
                'amount_ton': total_price_ton,
                'amount_usd': usd_price,
                'channels': [{'id': c.id, 'name': c.name} for c in channels],
                'duration_months': duration_months + bonus_months,
                'discount_percent': discount_percent,
                'expires_at': order.expires_at
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating payment order: {e}")
            raise
        finally:
            db.close()
    
    async def convert_ton_to_currency(self, ton_amount: float, currency: str) -> float:
        """Convert TON amount to specified currency"""
        db = SessionLocal()
        try:
            # Check if we have recent rate
            rate_record = db.query(CurrencyRate).filter(
                CurrencyRate.base_currency == 'TON',
                CurrencyRate.target_currency == currency,
                CurrencyRate.updated_at > datetime.utcnow() - timedelta(minutes=10)
            ).first()
            
            if rate_record:
                return ton_amount * rate_record.rate
            
            # Fetch fresh rate
            rate = await self.fetch_currency_rate('TON', currency)
            
            # Update database
            if rate_record:
                rate_record.rate = rate
                rate_record.updated_at = datetime.utcnow()
            else:
                rate_record = CurrencyRate(
                    base_currency='TON',
                    target_currency=currency,
                    rate=rate
                )
                db.add(rate_record)
            
            db.commit()
            return ton_amount * rate
            
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return ton_amount * 2.5  # Fallback rate
        finally:
            db.close()
    
    async def fetch_currency_rate(self, base: str, target: str) -> float:
        """Fetch current exchange rate from CoinGecko"""
        try:
            coin_ids = {
                'TON': 'the-open-network',
                'USD': 'usd',
                'SAR': 'sar',  
                'RUB': 'rub'
            }
            
            if base not in coin_ids or target.lower() not in ['usd', 'sar', 'rub']:
                raise ValueError("Unsupported currency pair")
            
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_ids[base],
                'vs_currencies': target.lower()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data[coin_ids[base]][target.lower()]
                    else:
                        raise Exception(f"API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error fetching exchange rate: {e}")
            # Fallback rates
            fallback_rates = {
                ('TON', 'USD'): 2.5,
                ('TON', 'SAR'): 9.4,
                ('TON', 'RUB'): 250.0
            }
            return fallback_rates.get((base, target), 1.0)
    
    async def start_payment_monitoring(self, order_id: str):
        """Start monitoring for payment confirmation"""
        if order_id in self.monitoring_tasks:
            return  # Already monitoring
        
        task = asyncio.create_task(self._monitor_payment(order_id))
        self.monitoring_tasks[order_id] = task
    
    async def _monitor_payment(self, order_id: str):
        """Monitor payment for specific order"""
        try:
            db = SessionLocal()
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return
            
            # Monitor for 30 minutes
            start_time = datetime.utcnow()
            timeout = timedelta(minutes=30)
            
            while datetime.utcnow() - start_time < timeout:
                # Check if payment is already confirmed
                if order.payment_status == 'confirmed':
                    break
                
                # Check TON blockchain for payment
                payment_found = await self.check_ton_payment(
                    order.wallet_address, 
                    order.payment_memo, 
                    order.total_amount_ton
                )
                
                if payment_found:
                    await self.confirm_payment(order_id, payment_found['tx_hash'])
                    break
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
                
                # Refresh order from database
                db.refresh(order)
            
            # Mark as expired if not paid
            if order.payment_status == 'pending':
                order.payment_status = 'expired'
                db.commit()
                
        except Exception as e:
            logger.error(f"Error monitoring payment for order {order_id}: {e}")
        finally:
            if order_id in self.monitoring_tasks:
                del self.monitoring_tasks[order_id]
            db.close()
    
    async def check_ton_payment(self, wallet_address: str, memo: str, expected_amount: float) -> Optional[Dict]:
        """Check TON blockchain for payment with specific memo"""
        try:
            # For demo purposes, simulate payment detection after 60 seconds
            await asyncio.sleep(60)
            
            # In production, this would call TON API:
            # url = f"{self.tonapi_base}/accounts/{wallet_address}/events"
            # Check recent transactions for memo and amount
            
            # Simulate successful payment detection
            return {
                'tx_hash': f"ton_tx_{memo}_{int(datetime.now().timestamp())}",
                'amount': expected_amount,
                'confirmed': True
            }
            
        except Exception as e:
            logger.error(f"Error checking TON payment: {e}")
            return None
    
    async def confirm_payment(self, order_id: str, tx_hash: str):
        """Confirm payment and activate order"""
        db = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False
            
            # Update order status
            order.payment_status = 'confirmed'
            order.status = 'active'
            order.paid_at = datetime.utcnow()
            order.started_at = datetime.utcnow()
            order.payment_tx_hash = tx_hash
            
            # Update payment tracking
            payment_tracking = db.query(PaymentTracking).filter(
                PaymentTracking.order_id == order_id
            ).first()
            
            if payment_tracking:
                payment_tracking.tx_hash = tx_hash
                payment_tracking.confirmed_at = datetime.utcnow()
                payment_tracking.received_amount = order.total_amount_ton
            
            db.commit()
            
            # Notify user about confirmed payment
            await self.notify_payment_confirmed(order)
            
            # Start ad scheduling
            await self.start_ad_campaign(order)
            
            return True
            
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def notify_payment_confirmed(self, order: Order):
        """Notify user that payment was confirmed"""
        # This will be implemented in the bot handlers
        logger.info(f"Payment confirmed for order {order.id}")
    
    async def start_ad_campaign(self, order: Order):
        """Start advertising campaign"""
        # This will be implemented in the scheduler
        logger.info(f"Starting ad campaign for order {order.id}")
    
    async def get_pricing_display(self, channel_ids: List[str], months: int, bundle_id: Optional[str] = None) -> Dict:
        """Get pricing information with currency conversion for display"""
        db = SessionLocal()
        try:
            from database import Channel, Bundle
            
            channels = db.query(Channel).filter(Channel.id.in_(channel_ids)).all()
            base_price = sum(channel.price_per_month for channel in channels) * months
            
            # Apply bundle discount
            discount_percent = 0.0
            bonus_months = 0
            
            if bundle_id:
                bundle = db.query(Bundle).filter(Bundle.id == bundle_id).first()
                if bundle and bundle.is_active:
                    discount_percent = bundle.discount_percent
                    bonus_months = bundle.bonus_months
            
            final_price = base_price * (1 - discount_percent / 100)
            
            # Convert to other currencies
            usd_price = await self.convert_ton_to_currency(final_price, 'USD')
            sar_price = await self.convert_ton_to_currency(final_price, 'SAR')
            rub_price = await self.convert_ton_to_currency(final_price, 'RUB')
            
            return {
                'channels_count': len(channels),
                'months': months,
                'bonus_months': bonus_months,
                'base_price_ton': base_price,
                'discount_percent': discount_percent,
                'final_price_ton': final_price,
                'final_price_usd': usd_price,
                'final_price_sar': sar_price,
                'final_price_rub': rub_price,
                'savings_ton': base_price - final_price
            }
            
        finally:
            db.close()

# Global payment system instance
payment_system = PaymentSystem()