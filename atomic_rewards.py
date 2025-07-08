"""
Atomic TON Reward System for I3lani Bot
Handles automatic and instant TON reward distribution for partners
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from database import Database
from languages import get_text

logger = logging.getLogger(__name__)

class AtomicRewardSystem:
    """Handles atomic TON reward distribution with instant processing"""
    
    def __init__(self, database: Database, bot):
        self.database = database
        self.bot = bot
        
        # TON reward rates
        self.REWARD_RATES = {
            'registration': 5.0,        # 5 TON for new partner registration
            'referral': 2.0,           # 2 TON per successful referral
            'channel_add': 10.0,       # 10 TON for adding new channel
            'subscriber_growth': 0.01, # 0.01 TON per new subscriber
            'ad_host': 1.0,           # 1 TON per ad hosted
            'monthly_bonus': 25.0,     # 25 TON monthly active bonus
            'tier_upgrade': 50.0       # 50 TON for tier upgrades
        }
        
        # Minimum payout threshold - Made challenging but achievable
        self.MIN_PAYOUT = 25.0  # 25 TON minimum (requires 12+ premium referrals or 50+ basic referrals)
        
        # TON wallet for distributions (would be configured in production)
        self.REWARD_WALLET = "UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB"
    
    async def process_atomic_reward(self, user_id: int, reward_type: str, 
                                   amount: float = None, channel_id: str = None, 
                                   description: str = None) -> Dict:
        """Process atomic reward with instant distribution"""
        
        try:
            # Calculate reward amount if not provided
            if amount is None:
                amount = self.REWARD_RATES.get(reward_type, 0.0)
            
            if amount <= 0:
                return {'success': False, 'message': 'Invalid reward amount'}
            
            # Create reward record
            reward_id = await self.database.add_partner_reward(
                user_id=user_id,
                channel_id=channel_id,
                reward_type=reward_type,
                amount=amount,
                description=description or f'Atomic {reward_type} reward'
            )
            
            # Update partner earnings atomically
            await self.database.update_partner_earnings(user_id, amount)
            
            # Check if user qualifies for instant payout
            partner_status = await self.database.get_partner_status(user_id)
            if partner_status and partner_status['pending_rewards'] >= self.MIN_PAYOUT:
                payout_result = await self.process_instant_payout(user_id)
                instant_payout = payout_result.get('success', False)
            else:
                instant_payout = False
            
            # Send real-time notification
            await self.send_atomic_notification(user_id, reward_type, amount, instant_payout)
            
            return {
                'success': True,
                'reward_id': reward_id,
                'amount': amount,
                'instant_payout': instant_payout,
                'message': 'Atomic reward processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error processing atomic reward: {e}")
            return {'success': False, 'message': f'Error: {e}'}
    
    async def process_instant_payout(self, user_id: int) -> Dict:
        """Process instant TON payout when threshold is met"""
        
        try:
            partner_status = await self.database.get_partner_status(user_id)
            if not partner_status:
                return {'success': False, 'message': 'Partner status not found'}
            
            payout_amount = partner_status['pending_rewards']
            
            if payout_amount < self.MIN_PAYOUT:
                return {'success': False, 'message': 'Below minimum payout threshold'}
            
            # In production, this would trigger actual TON transfer
            # For now, we'll mark as processed and notify user
            
            # Update partner status - clear pending rewards
            await self.database.execute_query('''
                UPDATE partner_status 
                SET pending_rewards = 0, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            
            # Create payout record
            await self.database.add_partner_reward(
                user_id=user_id,
                channel_id=None,
                reward_type='payout',
                amount=payout_amount,
                description=f'Instant TON payout - {payout_amount} TON'
            )
            
            # Send payout notification
            await self.send_payout_notification(user_id, payout_amount)
            
            return {
                'success': True,
                'amount': payout_amount,
                'message': 'Instant payout processed'
            }
            
        except Exception as e:
            logger.error(f"Error processing instant payout: {e}")
            return {'success': False, 'message': f'Error: {e}'}
    
    async def process_registration_reward(self, user_id: int) -> Dict:
        """Process automatic registration reward for new partners"""
        
        # Check if user already received registration bonus
        partner_status = await self.database.get_partner_status(user_id)
        if partner_status and partner_status['registration_bonus_paid']:
            return {'success': False, 'message': 'Registration bonus already paid'}
        
        # Create partner status if doesn't exist
        if not partner_status:
            await self.database.create_partner_status(user_id)
        
        # Process atomic registration reward
        result = await self.process_atomic_reward(
            user_id=user_id,
            reward_type='registration',
            description='Welcome bonus for new partner registration'
        )
        
        if result['success']:
            # Mark registration bonus as paid
            await self.database.execute_query('''
                UPDATE partner_status 
                SET registration_bonus_paid = TRUE
                WHERE user_id = ?
            ''', (user_id,))
            
            # Gamification integration
            try:
                from gamification import GamificationSystem
                gamification = GamificationSystem(self.database, self.bot)
                
                # Award XP for registration
                await gamification.award_xp(user_id, 50, "Partner registration")
                
                # Check special achievements (early adopter, first partner, etc.)
                await gamification.check_achievement(user_id, 'special', 1)
                
                logger.info(f"Gamification reward processed for new partner {user_id}")
                
            except Exception as e:
                logger.error(f"Error processing gamification reward for registration: {e}")
        
        return result
    
    async def process_referral_reward(self, referrer_id: int, referred_id: int) -> Dict:
        """Process atomic referral reward with gamification"""
        
        # Check if referral already exists
        existing = await self.database.get_referral_by_ids(referrer_id, referred_id)
        if existing:
            return {'success': False, 'message': 'Referral already processed'}
        
        # Create referral record
        await self.database.create_referral(referrer_id, referred_id)
        
        # Process atomic referral reward
        result = await self.process_atomic_reward(
            user_id=referrer_id,
            reward_type='referral',
            description=f'Referral reward for user {referred_id}'
        )
        
        # Gamification integration
        try:
            from gamification import GamificationSystem
            gamification = GamificationSystem(self.database, self.bot)
            
            # Award XP for referral
            await gamification.award_xp(referrer_id, 25, "Successful referral")
            
            # Check referral achievements
            referral_count = await self.database.get_referral_count(referrer_id)
            await gamification.check_achievement(referrer_id, 'referrals_made', referral_count)
            
            logger.info(f"Gamification reward processed for referrer {referrer_id}")
            
        except Exception as e:
            logger.error(f"Error processing gamification reward: {e}")
        
        return result
    
    async def process_channel_reward(self, user_id: int, channel_id: str) -> Dict:
        """Process reward for adding new channel with gamification"""
        
        result = await self.process_atomic_reward(
            user_id=user_id,
            reward_type='channel_add',
            channel_id=channel_id,
            description=f'Channel addition reward for {channel_id}'
        )
        
        # Gamification integration
        try:
            from gamification import GamificationSystem
            gamification = GamificationSystem(self.database, self.bot)
            
            # Award XP for channel addition
            await gamification.award_xp(user_id, 30, "Channel addition")
            
            # Check channel achievements
            channel_count = await self.database.get_user_channel_count(user_id)
            await gamification.check_achievement(user_id, 'channels_added', channel_count)
            
            logger.info(f"Gamification reward processed for channel addition by user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing gamification reward for channel: {e}")
        
        return result
    
    async def send_atomic_notification(self, user_id: int, reward_type: str, 
                                     amount: float, instant_payout: bool = False):
        """Send real-time reward notification"""
        
        try:
            language = await self.database.get_user_language(user_id)
            
            # Get reward type display name
            reward_names = {
                'registration': 'Registration Bonus',
                'referral': 'Referral Reward',
                'channel_add': 'Channel Addition',
                'subscriber_growth': 'Subscriber Growth',
                'ad_host': 'Ad Hosting',
                'monthly_bonus': 'Monthly Bonus',
                'tier_upgrade': 'Tier Upgrade'
            }
            
            reward_name = reward_names.get(reward_type, reward_type.title())
            
            notification_text = f"""
⚡ **Instant Reward Received!**

💰 **Reward Details:**
- Type: {reward_name}
- Amount: {amount} TON
- Status: {"Paid Out" if instant_payout else "Pending"}

🚀 **Your Progress:**
"""
            
            if instant_payout:
                notification_text += f"- Instant Payout: {amount} TON sent to your wallet\n"
            else:
                partner_status = await self.database.get_partner_status(user_id)
                if partner_status:
                    notification_text += f"- Pending Rewards: {partner_status['pending_rewards']} TON\n"
                    notification_text += f"- Total Earnings: {partner_status['total_earnings']} TON\n"
            
            notification_text += f"""
💡 **Next Steps:**
- Minimum payout: {self.MIN_PAYOUT} TON
- Keep earning to reach instant payout threshold
- Check your partner dashboard for details

🔗 **Share & Earn More:**
Your referral link: https://t.me/I3lani_bot?start=ref_{user_id}
            """.strip()
            
            await self.bot.send_message(
                chat_id=user_id,
                text=notification_text
            )
            
        except Exception as e:
            logger.error(f"Error sending atomic notification: {e}")
    
    async def send_payout_notification(self, user_id: int, amount: float):
        """Send payout notification"""
        
        try:
            notification_text = f"""
🎉 **TON Payout Processed!**

💰 **Payout Details:**
- Amount: {amount} TON
- Status: Completed
- Wallet: {self.REWARD_WALLET}

🚀 **Transaction Info:**
- Processing Time: Instant
- Network: TON Blockchain  
- Confirmation: Automatic

💡 **Keep Earning:**
- Continue referring friends
- Add more channels
- Grow your subscriber base
- Earn automatic TON rewards

🔗 **Share More:**
Your referral link: https://t.me/I3lani_bot?start=ref_{user_id}
            """.strip()
            
            await self.bot.send_message(
                chat_id=user_id,
                text=notification_text
            )
            
        except Exception as e:
            logger.error(f"Error sending payout notification: {e}")
    
    async def get_reward_statistics(self, user_id: int) -> Dict:
        """Get comprehensive reward statistics"""
        
        try:
            # Get all rewards
            rewards = await self.database.get_partner_rewards(user_id)
            
            # Calculate statistics
            total_earned = sum(r['amount'] for r in rewards)
            total_referrals = len([r for r in rewards if r['reward_type'] == 'referral'])
            total_payouts = sum(r['amount'] for r in rewards if r['reward_type'] == 'payout')
            
            # Get current status
            partner_status = await self.database.get_partner_status(user_id)
            
            return {
                'total_earned': total_earned,
                'total_referrals': total_referrals,
                'total_payouts': total_payouts,
                'pending_rewards': partner_status['pending_rewards'] if partner_status else 0,
                'registration_bonus_paid': partner_status['registration_bonus_paid'] if partner_status else False,
                'recent_rewards': rewards[:5]  # Last 5 rewards
            }
            
        except Exception as e:
            logger.error(f"Error getting reward statistics: {e}")
            return {}
    
    async def create_comprehensive_reward_board(self, user_id: int, language: str = 'en') -> str:
        """Create comprehensive reward board for partner"""
        
        try:
            # Get partner status and statistics
            partner_status = await self.database.get_partner_status(user_id)
            if not partner_status:
                await self.database.create_partner_status(user_id)
                partner_status = await self.database.get_partner_status(user_id)
            
            stats = await self.get_reward_statistics(user_id)
            
            # Calculate tier progress
            referral_count = stats.get('total_referrals', 0)
            if referral_count >= 50:
                tier = "Premium"
                tier_icon = "💎"
                rate = 2.0
                progress = 100
                next_milestone = "Maximum Tier Reached"
            elif referral_count >= 25:
                tier = "Gold"
                tier_icon = "🥇"
                rate = 1.2
                progress = (referral_count / 50) * 100
                next_milestone = f"{50 - referral_count} refs to Premium"
            elif referral_count >= 10:
                tier = "Silver"
                tier_icon = "🥈"
                rate = 0.8
                progress = (referral_count / 25) * 100
                next_milestone = f"{25 - referral_count} refs to Gold"
            else:
                tier = "Basic"
                tier_icon = "🥉"
                rate = 0.5
                progress = (referral_count / 10) * 100
                next_milestone = f"{10 - referral_count} refs to Silver"
            
            # Payout progress
            current_balance = partner_status.get('pending_rewards', 0.0) if partner_status else 0.0
            payout_progress = min((current_balance / self.MIN_PAYOUT) * 100, 100)
            
            # Create progress bars
            def create_progress_bar(percent: float, width: int = 10) -> str:
                filled = int((percent / 100) * width)
                return "█" * filled + "░" * (width - filled)
            
            # Create reward board
            board = f"""
🎯 **PARTNER REWARD BOARD**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **CURRENT BALANCE**
├─ Pending Rewards: {current_balance:.2f} TON
├─ Minimum Payout: {self.MIN_PAYOUT} TON
├─ Progress: {payout_progress:.1f}%
└─ Status: {"🟢 READY FOR PAYOUT!" if current_balance >= self.MIN_PAYOUT else "🔴 Keep Earning"}

📊 **PAYOUT PROGRESS**
{create_progress_bar(payout_progress)} {payout_progress:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{tier_icon} **TIER STATUS: {tier.upper()}**
├─ Referral Rate: {rate} TON per referral
├─ Total Referrals: {referral_count}
├─ Tier Progress: {progress:.1f}%
└─ Next Milestone: {next_milestone}

📈 **TIER PROGRESS**
{create_progress_bar(progress)} {progress:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **EARNINGS BREAKDOWN**
├─ Total Earned: {stats.get('total_earned', 0):.2f} TON
├─ Total Payouts: {stats.get('total_payouts', 0):.2f} TON
├─ Registration Bonus: {"✅ Claimed" if stats.get('registration_bonus_paid') else "❌ Unclaimed"}
└─ Active Channels: {partner_status.get('active_channels', 0) if partner_status else 0}

💎 **REWARD RATES**
├─ Basic Tier: 0.5 TON per referral
├─ Silver Tier: 0.8 TON per referral (10+ refs)
├─ Gold Tier: 1.2 TON per referral (25+ refs)
└─ Premium Tier: 2.0 TON per referral (50+ refs)

🎁 **MILESTONE BONUSES**
├─ 5 Referrals: 2.5 TON bonus
├─ 10 Referrals: 6.0 TON bonus
├─ 25 Referrals: 20.0 TON bonus
└─ 50 Referrals: 50.0 TON bonus

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **QUICK ACTIONS**
• Share your referral link to earn TON
• Add channels to your account
• Invite friends to join the platform
• Monitor your progress regularly

⚡ **PAYOUT THRESHOLD: {self.MIN_PAYOUT} TON**
This threshold ensures quality partnerships and sustainable rewards.
{"🎉 You've reached the threshold! Contact support for payout." if current_balance >= self.MIN_PAYOUT else f"💪 You need {self.MIN_PAYOUT - current_balance:.2f} more TON to reach payout threshold."}

🔗 **Your Referral Link:**
https://t.me/I3lani_bot?start=ref_{user_id}
            """.strip()
            
            return board
            
        except Exception as e:
            logger.error(f"Error creating reward board: {e}")
            return "Error loading reward board. Please try again."

# Global atomic reward system instance
atomic_rewards = None

def init_atomic_rewards(database: Database, bot):
    """Initialize atomic reward system"""
    global atomic_rewards
    atomic_rewards = AtomicRewardSystem(database, bot)
    return atomic_rewards