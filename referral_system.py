"""
Enhanced Referral System with Automatic TON Rewards
Implements Share and Win functionality with real-time tracking
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database import Database
from languages import get_text
from ui_components import UIComponents

logger = logging.getLogger(__name__)

class ReferralSystem:
    def __init__(self, database: Database, bot):
        self.database = database
        self.bot = bot
        self.ui = UIComponents()
        
        # Referral reward rates
        self.REFERRAL_REWARDS = {
            'basic': 0.5,    # 0.5 TON per referral
            'silver': 0.8,   # 0.8 TON per referral  
            'gold': 1.2,     # 1.2 TON per referral
            'premium': 2.0   # 2.0 TON per referral
        }
        
        # Bonus thresholds
        self.BONUS_THRESHOLDS = {
            5: 2.5,    # 2.5 TON bonus for 5 referrals
            10: 6.0,   # 6.0 TON bonus for 10 referrals
            25: 20.0,  # 20 TON bonus for 25 referrals
            50: 50.0   # 50 TON bonus for 50 referrals
        }
    
    async def create_referral_link(self, user_id: int) -> str:
        """Generate unique referral link for user"""
        return f"https://t.me/I3lani_bot?start=ref_{user_id}"
    
    async def process_referral(self, referrer_id: int, referred_id: int) -> Dict:
        """Process new referral and calculate rewards"""
        try:
            # Check if referral already exists
            existing = await self.database.get_referral_by_ids(referrer_id, referred_id)
            if existing:
                return {'success': False, 'message': 'Referral already exists'}
            
            # Create referral record
            await self.database.create_referral(referrer_id, referred_id)
            
            # Get referrer tier
            referrer_tier = await self.get_user_tier(referrer_id)
            reward_amount = self.REFERRAL_REWARDS.get(referrer_tier, 0.5)
            
            # Add referral reward
            await self.database.add_partner_reward(
                user_id=referrer_id,
                channel_id=None,
                reward_type='referral',
                amount=reward_amount,
                description=f'Referral reward for user {referred_id}'
            )
            
            # Update partner earnings
            await self.database.update_partner_earnings(referrer_id, reward_amount)
            
            # Check for bonus rewards
            bonus_reward = await self.check_bonus_eligibility(referrer_id)
            if bonus_reward > 0:
                await self.database.add_partner_reward(
                    user_id=referrer_id,
                    channel_id=None,
                    reward_type='bonus',
                    amount=bonus_reward,
                    description=f'Referral milestone bonus'
                )
                await self.database.update_partner_earnings(referrer_id, bonus_reward)
            
            # Send reward notification
            await self.send_reward_notification(referrer_id, reward_amount, bonus_reward)
            
            return {
                'success': True,
                'reward_amount': reward_amount,
                'bonus_reward': bonus_reward,
                'message': 'Referral processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error processing referral: {e}")
            return {'success': False, 'message': f'Error: {e}'}
    
    async def get_user_tier(self, user_id: int) -> str:
        """Get user's current tier based on referrals"""
        referral_count = await self.database.get_referral_count(user_id)
        
        if referral_count >= 50:
            return 'premium'
        elif referral_count >= 25:
            return 'gold'
        elif referral_count >= 10:
            return 'silver'
        else:
            return 'basic'
    
    async def check_bonus_eligibility(self, user_id: int) -> float:
        """Check if user qualifies for bonus rewards"""
        referral_count = await self.database.get_referral_count(user_id)
        
        for threshold, bonus in self.BONUS_THRESHOLDS.items():
            if referral_count == threshold:
                return bonus
        
        return 0.0
    
    async def send_reward_notification(self, user_id: int, reward_amount: float, bonus_reward: float = 0):
        """Send TON reward notification to user"""
        try:
            language = await self.database.get_user_language(user_id)
            
            total_reward = reward_amount + bonus_reward
            
            notification_text = f"""
🎉 **Congratulations! New Referral Reward**

💰 **Reward Details:**
- Referral Reward: {reward_amount} TON
"""
            
            if bonus_reward > 0:
                notification_text += f"- Milestone Bonus: {bonus_reward} TON\n"
            
            notification_text += f"""
- Total Earned: {total_reward} TON

🚀 **Your Progress:**
- Current Tier: {(await self.get_user_tier(user_id)).title()}
- Total Referrals: {await self.database.get_referral_count(user_id)}

💡 **Keep Sharing:**
Your referral link: https://t.me/I3lani_bot?start=ref_{user_id}
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💰 View Earnings", callback_data="view_earnings")],
                [InlineKeyboardButton(text="🔗 Share Link", callback_data="share_referral")]
            ])
            
            await self.bot.send_message(
                chat_id=user_id,
                text=notification_text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error sending reward notification: {e}")
    
    async def create_share_win_dashboard(self, user_id: int, language: str = 'en') -> str:
        """Create Share and Win dashboard with live data"""
        
        # Get user statistics
        referral_count = await self.database.get_referral_count(user_id)
        partner_status = await self.database.get_partner_status(user_id)
        recent_rewards = await self.database.get_partner_rewards(user_id)
        
        # Calculate next tier requirements
        current_tier = await self.get_user_tier(user_id)
        next_tier_requirement = self.get_next_tier_requirement(referral_count)
        
        # Calculate total earnings from referrals
        referral_earnings = sum(r['amount'] for r in recent_rewards if r['reward_type'] in ['referral', 'bonus'])
        
        dashboard_text = f"""
🏆 **Share & Win Dashboard**

💰 **Current Status:**
- Tier: {current_tier.title()} Partner
- Total Referrals: {referral_count}
- Referral Earnings: {referral_earnings:.2f} TON
- Pending Rewards: {partner_status['pending_rewards'] if partner_status else 0:.2f} TON

🎯 **Tier Progress:**
- Current Tier: {current_tier.title()}
- Next Tier: {next_tier_requirement['next_tier']}
- Referrals Needed: {next_tier_requirement['needed']}

💎 **Reward Rates:**
- Basic: 0.5 TON per referral
- Silver: 0.8 TON per referral
- Gold: 1.2 TON per referral  
- Premium: 2.0 TON per referral

🎁 **Recent Rewards:**
"""
        
        for reward in recent_rewards[:3]:
            dashboard_text += f"- {reward['reward_type']}: {reward['amount']} TON\n"
        
        dashboard_text += f"""
🔗 **Your Referral Link:**
https://t.me/I3lani_bot?start=ref_{user_id}

📊 **How to Earn More:**
1. Share your referral link
2. Invite friends to join I3lani
3. Earn automatic TON rewards
4. Unlock higher tiers for better rates
        """.strip()
        
        return dashboard_text
    
    def get_next_tier_requirement(self, current_referrals: int) -> Dict:
        """Calculate next tier requirement"""
        if current_referrals < 10:
            return {'next_tier': 'Silver', 'needed': 10 - current_referrals}
        elif current_referrals < 25:
            return {'next_tier': 'Gold', 'needed': 25 - current_referrals}
        elif current_referrals < 50:
            return {'next_tier': 'Premium', 'needed': 50 - current_referrals}
        else:
            return {'next_tier': 'Maximum', 'needed': 0}
    
    async def create_share_buttons(self, user_id: int, language: str = 'en') -> InlineKeyboardMarkup:
        """Create share buttons with referral links"""
        
        referral_link = await self.create_referral_link(user_id)
        
        share_text = "Join I3lani - The best Telegram advertising bot! Earn TON rewards and grow your business!"
        share_url = f"https://t.me/share/url?url={referral_link}&text={share_text}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 Share with Friends", url=share_url),
            ],
            [
                InlineKeyboardButton(text="💬 Share in Groups", url=f"https://t.me/share/url?url={referral_link}&text={share_text}"),
            ],
            [
                InlineKeyboardButton(text="🔗 Copy Link", callback_data=f"copy_referral_{user_id}"),
                InlineKeyboardButton(text="📊 View Stats", callback_data="referral_stats")
            ],
            [
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")
            ]
        ])
        
        return keyboard

# Initialize referral system
referral_system = None

def init_referral_system(database: Database, bot):
    """Initialize referral system"""
    global referral_system
    referral_system = ReferralSystem(database, bot)
    return referral_system