"""
Payment processing for I3lani Telegram Bot
Supports Telegram Stars and TON cryptocurrency
"""
import random
import string
import requests
import asyncio
import aiosqlite
from typing import Dict, Optional
from config import TON_API_KEY, TON_WALLET_ADDRESS, CURRENCY_RATES, DURATION_DISCOUNTS
from database import db
from languages import get_currency_info


class PaymentProcessor:
    def __init__(self):
        self.ton_api_key = TON_API_KEY
        self.ton_wallet = TON_WALLET_ADDRESS
        
    def generate_memo(self) -> str:
        """Generate AB0102 format memo (6-character alphanumeric)"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def calculate_price(self, base_price_usd: float, duration_months: int, 
                       currency: str = 'USD', apply_referral_discount: bool = False) -> Dict:
        """Calculate price with discounts"""
        # Base price calculation
        total_price = base_price_usd * duration_months
        
        # Apply duration discount
        discount_info = DURATION_DISCOUNTS.get(duration_months, {'discount': 0.0, 'bonus_months': 0})
        discount_amount = total_price * discount_info['discount']
        discounted_price = total_price - discount_amount
        
        # Apply referral discount if applicable
        referral_discount = 0.0
        if apply_referral_discount:
            referral_discount = discounted_price * 0.05  # 5% referral discount
            discounted_price -= referral_discount
        
        # Convert to target currency
        currency_rate = CURRENCY_RATES.get(currency, 1.0)
        final_price = discounted_price * currency_rate
        
        return {
            'base_price': base_price_usd,
            'duration_months': duration_months,
            'bonus_months': discount_info['bonus_months'],
            'total_months': duration_months + discount_info['bonus_months'],
            'currency': currency,
            'original_price': total_price * currency_rate,
            'discount_amount': discount_amount * currency_rate,
            'referral_discount': referral_discount * currency_rate,
            'final_price': final_price,
            'savings': (discount_amount + referral_discount) * currency_rate
        }
    
    async def create_payment_invoice(self, user_id: int, subscription_id: int,
                                   amount: float, currency: str, 
                                   payment_method: str) -> Dict:
        """Create payment invoice"""
        memo = self.generate_memo()
        
        # Store payment in database
        payment_id = await db.create_payment(
            user_id=user_id,
            subscription_id=subscription_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            memo=memo
        )
        
        invoice_data = {
            'payment_id': payment_id,
            'memo': memo,
            'amount': amount,
            'currency': currency,
            'payment_method': payment_method,
            'instructions': self._get_payment_instructions(payment_method, amount, currency, memo)
        }
        
        # Start payment monitoring
        if payment_method == 'ton':
            asyncio.create_task(self._monitor_ton_payment(payment_id, memo, amount))
        
        return invoice_data
    
    def _get_payment_instructions(self, payment_method: str, amount: float, 
                                currency: str, memo: str) -> Dict:
        """Get payment instructions for method"""
        if payment_method == 'ton':
            return {
                'wallet_address': self.ton_wallet,
                'amount': amount,
                'currency': currency,
                'memo': memo,
                'instructions': f"""
💎 **TON Payment Instructions**

📋 **Payment Details:**
• Amount: {amount} TON
• Wallet: `{self.ton_wallet}`
• Memo: `{memo}`

📱 **How to Pay:**
1. Open your TON wallet
2. Send exactly {amount} TON
3. Include memo: {memo}
4. Confirm transaction

⚠️ **Important:**
• Include the exact memo: {memo}
• Payment expires in 30 minutes
• Don't send from exchange wallet
                """.strip()
            }
        elif payment_method == 'stars':
            return {
                'amount': int(amount * 100),  # Convert to Stars (100 Stars = 1 USD)
                'currency': 'XTR',
                'memo': memo,
                'instructions': f"""
⭐ **Telegram Stars Payment**

📋 **Payment Details:**
• Amount: {int(amount * 100)} Stars
• Memo: `{memo}`

📱 **How to Pay:**
1. Click "Pay with Stars" button
2. Confirm payment in Telegram
3. Payment processed automatically

💫 **Benefits:**
• Instant confirmation
• No external wallet needed
• Secure Telegram payment
                """.strip()
            }
    
    async def _monitor_ton_payment(self, payment_id: int, memo: str, 
                                  expected_amount: float, timeout_minutes: int = 30):
        """Monitor TON payment via API"""
        if not self.ton_api_key or not self.ton_wallet:
            return
            
        timeout_seconds = timeout_minutes * 60
        check_interval = 30  # Check every 30 seconds
        
        for _ in range(timeout_seconds // check_interval):
            try:
                # Check for payment via TON API
                if await self._check_ton_transaction(memo, expected_amount):
                    await self._confirm_payment(payment_id)
                    return
                    
                await asyncio.sleep(check_interval)
            except Exception as e:
                print(f"Error monitoring TON payment: {e}")
                await asyncio.sleep(check_interval)
    
    async def _check_ton_transaction(self, memo: str, expected_amount: float) -> bool:
        """Check if TON transaction exists"""
        try:
            # Use tonviewer.com API to check transactions
            url = f"https://tonviewer.com/api/v1/address/{self.ton_wallet}/transactions"
            headers = {"X-API-Key": self.ton_api_key} if self.ton_api_key else {}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                transactions = response.json()
                
                for tx in transactions.get('transactions', []):
                    # Check if transaction has the correct memo and amount
                    if (tx.get('memo') == memo and 
                        float(tx.get('amount', 0)) >= expected_amount):
                        return True
            return False
        except Exception as e:
            print(f"Error checking TON transaction: {e}")
            return False
    
    async def _confirm_payment(self, payment_id: int):
        """Confirm payment and activate subscription"""
        try:
            # Update payment status
            async with aiosqlite.connect(db.db_path) as conn:
                await conn.execute('''
                    UPDATE payments 
                    SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
                    WHERE payment_id = ?
                ''', (payment_id,))
                
                # Get subscription details
                async with conn.execute('''
                    SELECT s.*, p.user_id 
                    FROM subscriptions s 
                    JOIN payments p ON s.subscription_id = p.subscription_id
                    WHERE p.payment_id = ?
                ''', (payment_id,)) as cursor:
                    subscription = await cursor.fetchone()
                
                if subscription:
                    # Activate subscription
                    await conn.execute('''
                        UPDATE subscriptions 
                        SET status = 'active', 
                            start_date = CURRENT_TIMESTAMP,
                            end_date = datetime('now', '+{} months')
                        WHERE subscription_id = ?
                    '''.format(subscription['duration_months']), (subscription['subscription_id'],))
                    
                    # Update user total spent
                    await conn.execute('''
                        UPDATE users 
                        SET total_spent = total_spent + ?
                        WHERE user_id = ?
                    ''', (subscription['total_price'], subscription['user_id']))
                
                await conn.commit()
                
        except Exception as e:
            print(f"Error confirming payment: {e}")
    
    async def verify_stars_payment(self, payment_id: int, charge_id: str) -> bool:
        """Verify Telegram Stars payment"""
        try:
            # In real implementation, verify with Telegram API
            # For now, auto-confirm Stars payments
            await self._confirm_payment(payment_id)
            return True
        except Exception as e:
            print(f"Error verifying Stars payment: {e}")
            return False
    
    def get_pricing_display(self, channels: list, duration_months: int, 
                           currency: str = 'USD', language: str = 'en') -> str:
        """Get pricing display text"""
        total_price = 0
        channel_details = []
        
        for channel in channels:
            price_info = self.calculate_price(
                channel['base_price_usd'], 
                duration_months, 
                currency
            )
            total_price += price_info['final_price']
            channel_details.append(f"• {channel['name']} - {price_info['final_price']:.2f} {currency}")
        
        # Get discount info
        discount_info = DURATION_DISCOUNTS.get(duration_months, {'discount': 0.0, 'bonus_months': 0})
        
        pricing_text = f"""
💰 **Pricing Summary**

📊 **Selected Channels:**
{chr(10).join(channel_details)}

⏱️ **Duration:** {duration_months} months
{f"🎁 **Bonus:** +{discount_info['bonus_months']} month free" if discount_info['bonus_months'] > 0 else ""}
{f"💸 **Discount:** {discount_info['discount']*100:.0f}% off" if discount_info['discount'] > 0 else ""}

💳 **Total Price:** {total_price:.2f} {currency}
        """.strip()
        
        return pricing_text


# Global payment processor instance
payment_processor = PaymentProcessor()