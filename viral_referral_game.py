"""
Viral Referral Game System for I3lani Bot
Users can win 1 month of free ad publishing by inviting 3 friends
"""

import logging
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from languages import get_text
from database import Database

logger = logging.getLogger(__name__)

class ViralReferralGame:
    """Viral referral game system with progress bar and friend invitations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def init_tables(self):
        """Initialize referral game tables"""
        try:
            # Create referral_game table
            await self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS referral_game (
                    user_id INTEGER PRIMARY KEY,
                    progress INTEGER DEFAULT 0,
                    referral_code TEXT UNIQUE,
                    referral_count INTEGER DEFAULT 0,
                    reward_unlocked BOOLEAN DEFAULT FALSE,
                    reward_claimed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reward_expires_at TIMESTAMP,
                    invited_by INTEGER REFERENCES referral_game(user_id)
                )
            ''')
            
            # Create referral_invitations table for tracking individual invitations
            await self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS referral_invitations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inviter_id INTEGER REFERENCES referral_game(user_id),
                    invited_id INTEGER REFERENCES referral_game(user_id),
                    invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(inviter_id, invited_id)
                )
            ''')
            
            # Create free_ad_rewards table for tracking free ad usage
            await self.db.execute_query('''
                CREATE TABLE IF NOT EXISTS free_ad_rewards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER REFERENCES referral_game(user_id),
                    reward_type TEXT DEFAULT 'referral_game',
                    ads_remaining INTEGER DEFAULT 10,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            logger.info("✅ Viral referral game tables initialized")
            
        except Exception as e:
            logger.error(f"Error initializing referral game tables: {e}")
            return None
    
    async def get_or_create_user(self, user_id: int) -> Dict:
        """Get or create user in referral game"""
        try:
            # Check if user exists
            user = await self.db.fetchone(
                'SELECT * FROM referral_game WHERE user_id = ?',
                (user_id,)
            )
            
            if not user:
                # Create new user with unique referral code
                referral_code = f"ref_{user_id}"
                
                await self.db.execute_query(
                    '''INSERT INTO referral_game 
                       (user_id, referral_code, progress, referral_count, reward_unlocked, reward_claimed)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (user_id, referral_code, 0, 0, False, False)
                )
                
                user = await self.db.fetchone(
                    'SELECT * FROM referral_game WHERE user_id = ?',
                    (user_id,)
                )
                
                logger.info(f"Created new referral game user: {user_id}")
            
            return dict(user) if user else None
            
        except Exception as e:
            logger.error(f"Error getting/creating user {user_id}: {e}")
            return None
    
    async def update_progress(self, user_id: int) -> Dict:
        """Update user progress (increment by random amount)"""
        try:
            import random
            
            user = await self.get_or_create_user(user_id)
            if not user:
                return None
            
            current_progress = user['progress']
            
            # If already at 99%, don't increment further
            if current_progress >= 99:
                return user
            
            # Increment progress by 10-25% each tap
            increment = random.randint(10, 25)
            new_progress = min(current_progress + increment, 99)
            
            await self.db.execute_query(
                'UPDATE referral_game SET progress = ? WHERE user_id = ?',
                (new_progress, user_id)
            )
            
            user['progress'] = new_progress
            
            logger.info(f"Updated progress for user {user_id}: {current_progress}% → {new_progress}%")
            
            return user
            
        except Exception as e:
            logger.error(f"Error updating progress for user {user_id}: {e}")
            return None
    
    async def process_referral(self, inviter_id: int, invited_id: int) -> Dict:
        """Process a referral invitation"""
        try:
            # Don't allow self-referral
            if inviter_id == invited_id:
                return {'success': False, 'message': 'Cannot refer yourself'}
            
            # Check if invitation already exists
            existing = await self.db.fetchone(
                'SELECT * FROM referral_invitations WHERE inviter_id = ? AND invited_id = ?',
                (inviter_id, invited_id)
            )
            
            if existing:
                return {'success': False, 'message': 'User already referred'}
            
            # Check if invited user was already referred by someone else
            invited_user = await self.db.fetchone(
                'SELECT * FROM referral_game WHERE user_id = ? AND invited_by IS NOT NULL',
                (invited_id,)
            )
            
            if invited_user:
                return {'success': False, 'message': 'User already referred by someone else'}
            
            # Create the invitation record
            await self.db.execute_query(
                'INSERT INTO referral_invitations (inviter_id, invited_id) VALUES (?, ?)',
                (inviter_id, invited_id)
            )
            
            # Mark the invited user as referred
            await self.db.execute_query(
                'UPDATE referral_game SET invited_by = ? WHERE user_id = ?',
                (inviter_id, invited_id)
            )
            
            # Update inviter's referral count
            await self.db.execute_query(
                'UPDATE referral_game SET referral_count = referral_count + 1 WHERE user_id = ?',
                (inviter_id,)
            )
            
            # Check if inviter reached 3 referrals
            inviter = await self.db.fetchone(
                'SELECT * FROM referral_game WHERE user_id = ?',
                (inviter_id,)
            )
            
            result = {
                'success': True,
                'message': 'Referral processed successfully',
                'referral_count': inviter['referral_count'],
                'reward_unlocked': False
            }
            
            # If reached 3 referrals, unlock reward
            if inviter['referral_count'] >= 3 and not inviter['reward_unlocked']:
                await self.unlock_reward(inviter_id)
                result['reward_unlocked'] = True
            
            logger.info(f"Processed referral: {inviter_id} → {invited_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing referral {inviter_id} → {invited_id}: {e}")
            return {'success': False, 'message': 'Error processing referral'}
    
    async def unlock_reward(self, user_id: int) -> bool:
        """Unlock 1 month free ad reward for user"""
        try:
            # Update referral_game table
            reward_expires = datetime.now() + timedelta(days=30)
            
            await self.db.execute_query(
                '''UPDATE referral_game 
                   SET reward_unlocked = TRUE, reward_expires_at = ?
                   WHERE user_id = ?''',
                (reward_expires, user_id)
            )
            
            # Add free ad reward (1 ad every 3 days for 30 days = 10 ads)
            await self.db.execute_query(
                '''INSERT INTO free_ad_rewards 
                   (user_id, reward_type, ads_remaining, expires_at)
                   VALUES (?, 'referral_game', 10, ?)''',
                (user_id, reward_expires)
            )
            
            logger.info(f"Unlocked reward for user {user_id}: 1 month free ads")
            
            return True
            
        except Exception as e:
            logger.error(f"Error unlocking reward for user {user_id}: {e}")
            return False
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get user's referral game statistics"""
        try:
            user = await self.get_or_create_user(user_id)
            if not user:
                return None
            
            # Get free ad rewards
            rewards = await self.db.fetchall(
                '''SELECT * FROM free_ad_rewards 
                   WHERE user_id = ? AND expires_at > CURRENT_TIMESTAMP
                   ORDER BY expires_at DESC''',
                (user_id,)
            )
            
            # Get referral invitations
            invitations = await self.db.fetchall(
                '''SELECT ri.*, rg.user_id as invited_user_id
                   FROM referral_invitations ri
                   JOIN referral_game rg ON ri.invited_id = rg.user_id
                   WHERE ri.inviter_id = ?
                   ORDER BY ri.invited_at DESC''',
                (user_id,)
            )
            
            return {
                'user_info': user,
                'active_rewards': [dict(r) for r in rewards],
                'invitations': [dict(i) for i in invitations],
                'total_free_ads': sum(r['ads_remaining'] for r in rewards)
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return None
    
    async def use_free_ad(self, user_id: int) -> bool:
        """Use one free ad from user's rewards"""
        try:
            # Get active reward with remaining ads
            reward = await self.db.fetchone(
                '''SELECT * FROM free_ad_rewards 
                   WHERE user_id = ? AND ads_remaining > 0 AND expires_at > CURRENT_TIMESTAMP
                   ORDER BY expires_at ASC LIMIT 1''',
                (user_id,)
            )
            
            if not reward:
                return False
            
            # Decrease ads_remaining
            await self.db.execute_query(
                'UPDATE free_ad_rewards SET ads_remaining = ads_remaining - 1 WHERE id = ?',
                (reward['id'],)
            )
            
            logger.info(f"Used free ad for user {user_id}: {reward['ads_remaining']} → {reward['ads_remaining'] - 1}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error using free ad for user {user_id}: {e}")
            return False
    
    def create_progress_keyboard(self, user_id: int, progress: int, language: str = 'en') -> InlineKeyboardMarkup:
        """Create progress bar keyboard"""
        
        # Progress bar visualization
        filled_blocks = int(progress / 10)
        empty_blocks = 10 - filled_blocks
        progress_bar = "█" * filled_blocks + "░" * empty_blocks
        
        if progress < 99:
            # Show tap button
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"🎮 TAP TO CONTINUE ({progress}%)",
                    callback_data=f"tap_progress_{user_id}"
                )],
                [InlineKeyboardButton(
                    text=get_text(language, 'back_to_main', 'Back to Main Menu'),
                    callback_data="back_to_main"
                )]
            ])
        else:
            # Show share button
            referral_link = f"https://t.me/I3laniBot?start=ref_{user_id}"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🎯 INVITE 3 FRIENDS (0/3)",
                    url=f"https://t.me/share/url?url={referral_link}&text=🎮 Join me on I3lani Bot! Get free advertising by completing the game!"
                )],
                [InlineKeyboardButton(
                    text="📊 My Progress",
                    callback_data=f"check_referral_progress_{user_id}"
                )],
                [InlineKeyboardButton(
                    text=get_text(language, 'back_to_main', 'Back to Main Menu'),
                    callback_data="back_to_main"
                )]
            ])
        
        return keyboard
    
    def create_reward_keyboard(self, language: str = 'en') -> InlineKeyboardMarkup:
        """Create reward unlock keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🆓 Use Free Ad Now",
                callback_data="use_free_ad"
            )],
            [InlineKeyboardButton(
                text="📊 My Rewards",
                callback_data="check_my_rewards"
            )],
            [InlineKeyboardButton(
                text=get_text(language, 'back_to_main', 'Back to Main Menu'),
                callback_data="back_to_main"
            )]
        ])
    
    async def get_progress_message(self, user_id: int, language: str = 'en') -> str:
        """Get progress message text"""
        user = await self.get_or_create_user(user_id)
        if not user:
            return "Error loading game progress"
        
        progress = user['progress']
        
        if progress < 99:
            # Progress bar visualization
            filled_blocks = int(progress / 10)
            empty_blocks = 10 - filled_blocks
            progress_bar = "█" * filled_blocks + "░" * empty_blocks
            
            if language == 'ar':
                return f"""🎮 **لعبة الإحالة الفيروسية**

📊 **التقدم:** {progress}%
{progress_bar}

🎯 **الهدف:** الوصول إلى 99% ثم دعوة 3 أصدقاء
🏆 **الجائزة:** شهر مجاني من الإعلانات (إعلان واحد كل 3 أيام)

👆 **اضغط TAP TO CONTINUE للمتابعة!**"""
            
            elif language == 'ru':
                return f"""🎮 **Вирусная реферальная игра**

📊 **Прогресс:** {progress}%
{progress_bar}

🎯 **Цель:** Достичь 99%, затем пригласить 3 друзей
🏆 **Награда:** 1 месяц бесплатных объявлений (1 объявление каждые 3 дня)

👆 **Нажми TAP TO CONTINUE для продолжения!**"""
            
            else:  # English
                return f"""🎮 **Viral Referral Game**

📊 **Progress:** {progress}%
{progress_bar}

🎯 **Goal:** Reach 99% then invite 3 friends
🏆 **Reward:** 1 month free ads (1 ad every 3 days)

👆 **Tap TAP TO CONTINUE to keep going!**"""
        
        else:
            # 99% reached, show referral instructions
            referral_count = user['referral_count']
            referral_link = f"https://t.me/I3laniBot?start=ref_{user_id}"
            
            if language == 'ar':
                return f"""🎉 **تهانينا! وصلت إلى 99%**

🎯 **الآن ادعو 3 أصدقاء لتحصل على الجائزة:**
📊 **التقدم:** {referral_count}/3 أصدقاء

🔗 **رابط الدعوة:**
`{referral_link}`

📢 **شارك الرابط مع أصدقائك للحصول على:**
🆓 **شهر مجاني من الإعلانات**
📅 **إعلان واحد كل 3 أيام لمدة 30 يوماً**

💡 **نصيحة:** شارك في المجموعات والقنوات للحصول على إحالات أكثر!"""
            
            elif language == 'ru':
                return f"""🎉 **Поздравляем! Вы достигли 99%**

🎯 **Теперь пригласите 3 друзей для получения награды:**
📊 **Прогресс:** {referral_count}/3 друзей

🔗 **Ссылка для приглашения:**
`{referral_link}`

📢 **Поделитесь ссылкой с друзьями, чтобы получить:**
🆓 **1 месяц бесплатных объявлений**
📅 **1 объявление каждые 3 дня в течение 30 дней**

💡 **Совет:** Поделитесь в группах и каналах, чтобы получить больше рефералов!"""
            
            else:  # English
                return f"""🎉 **Congratulations! You reached 99%**

🎯 **Now invite 3 friends to claim your reward:**
📊 **Progress:** {referral_count}/3 friends

🔗 **Your invite link:**
`{referral_link}`

📢 **Share this link with friends to get:**
🆓 **1 month of free ads**
📅 **1 ad every 3 days for 30 days**

💡 **Tip:** Share in groups and channels to get more referrals!"""
    
    async def get_reward_message(self, user_id: int, language: str = 'en') -> str:
        """Get reward unlock message"""
        stats = await self.get_user_stats(user_id)
        if not stats:
            return "Error loading reward information"
        
        total_ads = stats['total_free_ads']
        
        if language == 'ar':
            return f"""🏆 **مبروك! فزت بالجائزة الكبرى!**

🎉 **تم إلغاء قفل مكافأة الإحالة:**
🆓 **{total_ads} إعلان مجاني**
📅 **صالح لمدة 30 يوماً**
⏰ **إعلان واحد كل 3 أيام**

✨ **يمكنك الآن:**
• إنشاء إعلانات مجانية
• اختيار أي قناة متاحة
• النشر بدون دفع أي رسوم

🚀 **ابدأ استخدام إعلاناتك المجانية الآن!**"""
        
        elif language == 'ru':
            return f"""🏆 **Поздравляем! Вы выиграли главный приз!**

🎉 **Награда за рефералы разблокирована:**
🆓 **{total_ads} бесплатных объявлений**
📅 **Действительно 30 дней**
⏰ **1 объявление каждые 3 дня**

✨ **Теперь вы можете:**
• Создавать бесплатные объявления
• Выбирать любой доступный канал
• Публиковать без оплаты

🚀 **Начните использовать бесплатные объявления прямо сейчас!**"""
        
        else:  # English
            return f"""🏆 **Congratulations! You won the grand prize!**

🎉 **Referral reward unlocked:**
🆓 **{total_ads} free ads**
📅 **Valid for 30 days**
⏰ **1 ad every 3 days**

✨ **You can now:**
• Create free advertisements
• Choose any available channel
• Post without paying any fees

🚀 **Start using your free ads now!**"""

# Global instance
viral_game = None

def get_viral_game() -> ViralReferralGame:
    """Get global viral game instance"""
    global viral_game
    if viral_game is None:
        from database import db
        viral_game = ViralReferralGame(db)
    return viral_game