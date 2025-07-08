"""
Gamification System for I3lani Bot
Complete gamification for partner and affiliate systems with achievements, leaderboards, challenges
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from web3_ui import Web3UIComponents
from languages import get_text

logger = logging.getLogger(__name__)

class GamificationSystem:
    """Complete gamification system with achievements, leaderboards, and challenges"""
    
    def __init__(self, database: Database, bot):
        self.db = database
        self.bot = bot
        self.web3_ui = Web3UIComponents()
        
        # Achievement definitions
        self.achievements = {
            # Partner Achievements
            'first_channel': {
                'name': '🎯 First Channel Master',
                'description': 'Add your first channel to the network',
                'requirement': 1,
                'type': 'channels_added',
                'reward_ton': 0.5,
                'badge': '🎯'
            },
            'channel_collector': {
                'name': '📺 Channel Collector',
                'description': 'Add 5 channels to the network',
                'requirement': 5,
                'type': 'channels_added',
                'reward_ton': 2.0,
                'badge': '📺'
            },
            'network_king': {
                'name': '👑 Network King',
                'description': 'Add 10 channels to the network',
                'requirement': 10,
                'type': 'channels_added',
                'reward_ton': 5.0,
                'badge': '👑'
            },
            
            # Referral Achievements
            'first_referral': {
                'name': '🤝 First Connection',
                'description': 'Refer your first partner',
                'requirement': 1,
                'type': 'referrals_made',
                'reward_ton': 1.0,
                'badge': '🤝'
            },
            'social_butterfly': {
                'name': '🦋 Social Butterfly',
                'description': 'Refer 10 partners',
                'requirement': 10,
                'type': 'referrals_made',
                'reward_ton': 5.0,
                'badge': '🦋'
            },
            'influence_master': {
                'name': '🎭 Influence Master',
                'description': 'Refer 25 partners',
                'requirement': 25,
                'type': 'referrals_made',
                'reward_ton': 15.0,
                'badge': '🎭'
            },
            'viral_legend': {
                'name': '🌟 Viral Legend',
                'description': 'Refer 50 partners',
                'requirement': 50,
                'type': 'referrals_made',
                'reward_ton': 30.0,
                'badge': '🌟'
            },
            
            # Earnings Achievements
            'first_payout': {
                'name': '💰 First Payout',
                'description': 'Receive your first TON payout',
                'requirement': 1,
                'type': 'payouts_received',
                'reward_ton': 0.5,
                'badge': '💰'
            },
            'earnings_champion': {
                'name': '🏆 Earnings Champion',
                'description': 'Earn 100 TON total',
                'requirement': 100,
                'type': 'total_earned',
                'reward_ton': 10.0,
                'badge': '🏆'
            },
            'wealth_builder': {
                'name': '💎 Wealth Builder',
                'description': 'Earn 500 TON total',
                'requirement': 500,
                'type': 'total_earned',
                'reward_ton': 25.0,
                'badge': '💎'
            },
            
            # Activity Achievements
            'daily_grinder': {
                'name': '⚡ Daily Grinder',
                'description': 'Complete 7 daily check-ins',
                'requirement': 7,
                'type': 'daily_checkins',
                'reward_ton': 2.0,
                'badge': '⚡'
            },
            'consistency_king': {
                'name': '🔥 Consistency King',
                'description': 'Complete 30 daily check-ins',
                'requirement': 30,
                'type': 'daily_checkins',
                'reward_ton': 10.0,
                'badge': '🔥'
            },
            
            # Special Achievements
            'early_adopter': {
                'name': '🚀 Early Adopter',
                'description': 'Join during beta launch week',
                'requirement': 1,
                'type': 'special',
                'reward_ton': 5.0,
                'badge': '🚀'
            },
            'bug_hunter': {
                'name': '🐛 Bug Hunter',
                'description': 'Report a valid bug',
                'requirement': 1,
                'type': 'special',
                'reward_ton': 3.0,
                'badge': '🐛'
            },
            'community_hero': {
                'name': '🦸 Community Hero',
                'description': 'Help 5 new users get started',
                'requirement': 5,
                'type': 'community_help',
                'reward_ton': 8.0,
                'badge': '🦸'
            }
        }
        
        # Level system
        self.levels = {
            1: {'name': 'Rookie', 'xp_required': 0, 'badge': '🟢', 'perks': ['Basic dashboard']},
            2: {'name': 'Explorer', 'xp_required': 100, 'badge': '🔵', 'perks': ['Advanced analytics']},
            3: {'name': 'Specialist', 'xp_required': 250, 'badge': '🟡', 'perks': ['Priority support']},
            4: {'name': 'Expert', 'xp_required': 500, 'badge': '🟠', 'perks': ['Custom dashboard']},
            5: {'name': 'Master', 'xp_required': 1000, 'badge': '🔴', 'perks': ['Beta features']},
            6: {'name': 'Champion', 'xp_required': 2000, 'badge': '🟣', 'perks': ['VIP support']},
            7: {'name': 'Legend', 'xp_required': 5000, 'badge': '⚫', 'perks': ['Exclusive rewards']},
            8: {'name': 'Mythic', 'xp_required': 10000, 'badge': '⚪', 'perks': ['All features unlocked']}
        }
        
        # Daily challenges
        self.daily_challenges = [
            {
                'id': 'daily_checkin',
                'name': 'Daily Check-in',
                'description': 'Visit your dashboard',
                'reward_xp': 10,
                'reward_ton': 0.1,
                'type': 'daily'
            },
            {
                'id': 'share_referral',
                'name': 'Share Your Link',
                'description': 'Share your referral link',
                'reward_xp': 25,
                'reward_ton': 0.2,
                'type': 'daily'
            },
            {
                'id': 'check_earnings',
                'name': 'Monitor Earnings',
                'description': 'Check your earnings dashboard',
                'reward_xp': 15,
                'reward_ton': 0.1,
                'type': 'daily'
            }
        ]
        
        # Weekly challenges
        self.weekly_challenges = [
            {
                'id': 'weekly_referral',
                'name': 'Weekly Networking',
                'description': 'Refer 3 new partners this week',
                'requirement': 3,
                'reward_xp': 100,
                'reward_ton': 2.0,
                'type': 'weekly'
            },
            {
                'id': 'weekly_engagement',
                'name': 'Weekly Engagement',
                'description': 'Complete 5 daily challenges',
                'requirement': 5,
                'reward_xp': 75,
                'reward_ton': 1.5,
                'type': 'weekly'
            }
        ]

    async def initialize_gamification_tables(self):
        """Initialize gamification database tables"""
        try:
            async with self.db.get_connection() as conn:
                # User gamification profile
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_gamification (
                        user_id INTEGER PRIMARY KEY,
                        level INTEGER DEFAULT 1,
                        xp INTEGER DEFAULT 0,
                        total_achievements INTEGER DEFAULT 0,
                        daily_streak INTEGER DEFAULT 0,
                        last_checkin DATE,
                        total_ton_earned REAL DEFAULT 0.0,
                        leaderboard_position INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # User achievements
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        achievement_id TEXT NOT NULL,
                        unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        reward_claimed BOOLEAN DEFAULT FALSE,
                        UNIQUE(user_id, achievement_id)
                    )
                """)
                
                # Daily challenges progress
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_challenges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        challenge_id TEXT NOT NULL,
                        challenge_type TEXT NOT NULL,
                        progress INTEGER DEFAULT 0,
                        completed BOOLEAN DEFAULT FALSE,
                        completed_at DATETIME,
                        week_number INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Leaderboard cache
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS leaderboard_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        leaderboard_type TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        position INTEGER NOT NULL,
                        score REAL NOT NULL,
                        display_name TEXT,
                        badge TEXT,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await conn.commit()
                logger.info("Gamification tables initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing gamification tables: {e}")

    async def get_user_profile(self, user_id: int) -> Dict:
        """Get complete gamification profile for user"""
        try:
            async with self.db.get_connection() as conn:
                conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
                
                # Get or create user profile
                async with conn.execute("""
                    SELECT * FROM user_gamification WHERE user_id = ?
                """, (user_id,)) as cursor:
                    profile = await cursor.fetchone()
                
                if not profile:
                    # Create new profile
                    await conn.execute("""
                        INSERT INTO user_gamification (user_id) VALUES (?)
                    """, (user_id,))
                    await conn.commit()
                    
                    profile = {
                        'user_id': user_id,
                        'level': 1,
                        'xp': 0,
                        'total_achievements': 0,
                        'daily_streak': 0,
                        'last_checkin': None,
                        'total_ton_earned': 0.0,
                        'leaderboard_position': 0
                    }
                
                # Get user achievements
                async with conn.execute("""
                    SELECT achievement_id, unlocked_at, reward_claimed 
                    FROM user_achievements WHERE user_id = ?
                """, (user_id,)) as cursor:
                    achievements = await cursor.fetchall()
                
                profile['achievements'] = achievements
                profile['level_info'] = self.get_level_info(profile['level'])
                profile['next_level'] = self.get_next_level_info(profile['level'], profile['xp'])
                
                return profile
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return self.get_default_profile(user_id)

    def get_default_profile(self, user_id: int) -> Dict:
        """Get default profile for new users"""
        return {
            'user_id': user_id,
            'level': 1,
            'xp': 0,
            'total_achievements': 0,
            'daily_streak': 0,
            'last_checkin': None,
            'total_ton_earned': 0.0,
            'leaderboard_position': 0,
            'achievements': [],
            'level_info': self.levels[1],
            'next_level': self.levels[2] if 2 in self.levels else None
        }

    def get_level_info(self, level: int) -> Dict:
        """Get level information"""
        return self.levels.get(level, self.levels[1])

    def get_next_level_info(self, current_level: int, current_xp: int) -> Optional[Dict]:
        """Get next level information"""
        next_level = current_level + 1
        if next_level in self.levels:
            next_level_info = self.levels[next_level].copy()
            next_level_info['xp_needed'] = next_level_info['xp_required'] - current_xp
            return next_level_info
        return None

    async def award_xp(self, user_id: int, xp_amount: int, reason: str = "") -> Dict:
        """Award XP to user and check for level up"""
        try:
            profile = await self.get_user_profile(user_id)
            new_xp = profile['xp'] + xp_amount
            old_level = profile['level']
            new_level = self.calculate_level(new_xp)
            
            # Update database
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    UPDATE user_gamification 
                    SET xp = ?, level = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (new_xp, new_level, user_id))
                await conn.commit()
            
            # Check for level up
            level_up = new_level > old_level
            if level_up:
                await self.handle_level_up(user_id, old_level, new_level)
            
            return {
                'old_xp': profile['xp'],
                'new_xp': new_xp,
                'xp_gained': xp_amount,
                'old_level': old_level,
                'new_level': new_level,
                'level_up': level_up,
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error awarding XP: {e}")
            return {}

    def calculate_level(self, xp: int) -> int:
        """Calculate level based on XP"""
        for level in reversed(range(1, 9)):
            if xp >= self.levels[level]['xp_required']:
                return level
        return 1

    async def handle_level_up(self, user_id: int, old_level: int, new_level: int):
        """Handle level up notification and rewards"""
        try:
            level_info = self.levels[new_level]
            
            # Send level up notification
            congratulations_text = f"""
🎉 **LEVEL UP!** 🎉

{level_info['badge']} **You reached Level {new_level}: {level_info['name']}!**

**Unlocked Perks:**
{chr(10).join(f"✅ {perk}" for perk in level_info['perks'])}

**Bonus Reward:** +{new_level} TON for reaching this level!

Keep building your network and climbing the ranks! 🚀
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏆 View Profile", callback_data="gamification_profile")],
                [InlineKeyboardButton(text="🏅 Check Leaderboard", callback_data="gamification_leaderboard")]
            ])
            
            await self.bot.send_message(
                chat_id=user_id,
                text=congratulations_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            # Award level up bonus
            await self.award_ton_bonus(user_id, float(new_level), f"Level {new_level} bonus")
            
        except Exception as e:
            logger.error(f"Error handling level up: {e}")

    async def check_achievement(self, user_id: int, achievement_type: str, current_value: int) -> List[str]:
        """Check if user unlocked any achievements"""
        unlocked = []
        
        try:
            for achievement_id, achievement in self.achievements.items():
                if achievement['type'] == achievement_type and current_value >= achievement['requirement']:
                    # Check if already unlocked
                    if not await self.has_achievement(user_id, achievement_id):
                        await self.unlock_achievement(user_id, achievement_id)
                        unlocked.append(achievement_id)
            
            return unlocked
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []

    async def has_achievement(self, user_id: int, achievement_id: str) -> bool:
        """Check if user has specific achievement"""
        try:
            async with self.db.get_connection() as conn:
                async with conn.execute("""
                    SELECT 1 FROM user_achievements 
                    WHERE user_id = ? AND achievement_id = ?
                """, (user_id, achievement_id)) as cursor:
                    return bool(await cursor.fetchone())
        except Exception as e:
            logger.error(f"Error checking achievement: {e}")
            return False

    async def unlock_achievement(self, user_id: int, achievement_id: str):
        """Unlock achievement for user"""
        try:
            achievement = self.achievements[achievement_id]
            
            # Add to database
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    INSERT OR IGNORE INTO user_achievements 
                    (user_id, achievement_id) VALUES (?, ?)
                """, (user_id, achievement_id))
                
                # Update achievement count
                await conn.execute("""
                    UPDATE user_gamification 
                    SET total_achievements = total_achievements + 1
                    WHERE user_id = ?
                """, (user_id,))
                
                await conn.commit()
            
            # Send achievement notification
            await self.send_achievement_notification(user_id, achievement_id, achievement)
            
            # Award XP and TON
            await self.award_xp(user_id, 50, f"Achievement: {achievement['name']}")
            await self.award_ton_bonus(user_id, achievement['reward_ton'], f"Achievement: {achievement['name']}")
            
        except Exception as e:
            logger.error(f"Error unlocking achievement: {e}")

    async def send_achievement_notification(self, user_id: int, achievement_id: str, achievement: Dict):
        """Send achievement unlock notification"""
        try:
            notification_text = f"""
🏆 **ACHIEVEMENT UNLOCKED!** 🏆

{achievement['badge']} **{achievement['name']}**

{achievement['description']}

**Rewards:**
💰 +{achievement['reward_ton']} TON
⭐ +50 XP

Keep up the amazing work! 🎯
            """.strip()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏆 View All Achievements", callback_data="gamification_achievements")],
                [InlineKeyboardButton(text="🏅 Check Leaderboard", callback_data="gamification_leaderboard")]
            ])
            
            await self.bot.send_message(
                chat_id=user_id,
                text=notification_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error sending achievement notification: {e}")

    async def award_ton_bonus(self, user_id: int, amount: float, reason: str):
        """Award TON bonus to user"""
        try:
            # Add to partner rewards
            from atomic_rewards import AtomicRewardSystem
            atomic_rewards = AtomicRewardSystem(self.db, self.bot)
            
            await atomic_rewards.process_atomic_reward(
                user_id=user_id,
                reward_type="gamification_bonus",
                amount=amount,
                description=reason
            )
            
            # Update total earned
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    UPDATE user_gamification 
                    SET total_ton_earned = total_ton_earned + ?
                    WHERE user_id = ?
                """, (amount, user_id))
                await conn.commit()
            
        except Exception as e:
            logger.error(f"Error awarding TON bonus: {e}")

    async def process_daily_checkin(self, user_id: int) -> Dict:
        """Process daily check-in"""
        try:
            profile = await self.get_user_profile(user_id)
            today = datetime.now().date()
            last_checkin = profile.get('last_checkin')
            
            if last_checkin and str(last_checkin) == str(today):
                return {'already_checked_in': True, 'streak': profile['daily_streak']}
            
            # Calculate new streak
            yesterday = today - timedelta(days=1)
            if last_checkin and str(last_checkin) == str(yesterday):
                new_streak = profile['daily_streak'] + 1
            else:
                new_streak = 1
            
            # Update database
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    UPDATE user_gamification 
                    SET daily_streak = ?, last_checkin = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (new_streak, today, user_id))
                await conn.commit()
            
            # Award XP and TON based on streak
            base_xp = 10
            base_ton = 0.1
            streak_multiplier = min(new_streak * 0.1, 2.0)  # Max 2x multiplier
            
            xp_reward = int(base_xp * (1 + streak_multiplier))
            ton_reward = base_ton * (1 + streak_multiplier)
            
            await self.award_xp(user_id, xp_reward, f"Daily check-in (Day {new_streak})")
            await self.award_ton_bonus(user_id, ton_reward, f"Daily check-in streak bonus")
            
            # Check achievements
            await self.check_achievement(user_id, 'daily_checkins', new_streak)
            
            return {
                'success': True,
                'streak': new_streak,
                'xp_reward': xp_reward,
                'ton_reward': ton_reward,
                'streak_multiplier': streak_multiplier
            }
            
        except Exception as e:
            logger.error(f"Error processing daily check-in: {e}")
            return {'error': str(e)}

    async def get_leaderboard(self, leaderboard_type: str = 'xp', limit: int = 10) -> List[Dict]:
        """Get leaderboard data"""
        try:
            async with self.db.get_connection() as conn:
                conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
                
                if leaderboard_type == 'xp':
                    query = """
                        SELECT 
                            ug.user_id,
                            ug.level,
                            ug.xp,
                            ug.total_achievements,
                            u.username,
                            ROW_NUMBER() OVER (ORDER BY ug.xp DESC) as position
                        FROM user_gamification ug
                        LEFT JOIN users u ON ug.user_id = u.id
                        ORDER BY ug.xp DESC
                        LIMIT ?
                    """
                elif leaderboard_type == 'earnings':
                    query = """
                        SELECT 
                            ug.user_id,
                            ug.level,
                            ug.total_ton_earned,
                            ug.total_achievements,
                            u.username,
                            ROW_NUMBER() OVER (ORDER BY ug.total_ton_earned DESC) as position
                        FROM user_gamification ug
                        LEFT JOIN users u ON ug.user_id = u.id
                        ORDER BY ug.total_ton_earned DESC
                        LIMIT ?
                    """
                elif leaderboard_type == 'achievements':
                    query = """
                        SELECT 
                            ug.user_id,
                            ug.level,
                            ug.total_achievements,
                            ug.xp,
                            u.username,
                            ROW_NUMBER() OVER (ORDER BY ug.total_achievements DESC) as position
                        FROM user_gamification ug
                        LEFT JOIN users u ON ug.user_id = u.id
                        ORDER BY ug.total_achievements DESC
                        LIMIT ?
                    """
                else:
                    return []
                
                async with conn.execute(query, (limit,)) as cursor:
                    leaderboard = await cursor.fetchall()
                
                # Enhance with level info
                for entry in leaderboard:
                    entry['level_info'] = self.get_level_info(entry['level'])
                    entry['display_name'] = entry['username'] or f"User{entry['user_id']}"
                
                return leaderboard
                
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    async def create_gamification_dashboard(self, user_id: int, language: str = 'en') -> str:
        """Create comprehensive gamification dashboard"""
        try:
            profile = await self.get_user_profile(user_id)
            level_info = profile['level_info']
            next_level = profile['next_level']
            
            # Create XP progress bar
            if next_level:
                xp_progress = (profile['xp'] - level_info['xp_required']) / (next_level['xp_required'] - level_info['xp_required'])
                xp_bar = self.web3_ui.create_progress_bar(xp_progress)
            else:
                xp_bar = "████████████ MAX LEVEL"
            
            # Daily check-in status
            today = datetime.now().date()
            last_checkin = profile.get('last_checkin')
            can_checkin = not (last_checkin and str(last_checkin) == str(today))
            
            dashboard = f"""
🎮 **GAMIFICATION DASHBOARD** 🎮

{self.web3_ui.create_neural_header("PLAYER PROFILE")}

**Level Progress:**
{level_info['badge']} Level {profile['level']}: {level_info['name']}
{xp_bar}
XP: {profile['xp']:,} / {next_level['xp_required']:,} {"(MAX)" if not next_level else ""}

**Statistics:**
🏆 Achievements: {profile['total_achievements']}/{len(self.achievements)}
💰 Total Earned: {profile['total_ton_earned']:.2f} TON
🔥 Daily Streak: {profile['daily_streak']} days
📊 Leaderboard: #{profile['leaderboard_position'] or 'Unranked'}

**Daily Check-in:**
{"✅ Available" if can_checkin else "☑️ Completed"} 
Current Streak: {profile['daily_streak']} days

**Unlocked Perks:**
{chr(10).join(f"✅ {perk}" for perk in level_info['perks'])}

{self.web3_ui.create_holographic_display("NEURAL GAMING MATRIX")}
            """.strip()
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating gamification dashboard: {e}")
            return "Error loading gamification dashboard"

def init_gamification(database: Database, bot):
    """Initialize gamification system"""
    return GamificationSystem(database, bot)