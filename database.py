"""
SQLite database operations for I3lani Telegram Bot
"""
import aiosqlite
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
from config import DATABASE_URL


class Database:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # First, check if we need to add free_trial columns
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'free_trial_used' not in column_names:
                await db.execute('ALTER TABLE users ADD COLUMN free_trial_used BOOLEAN DEFAULT FALSE')
                await db.execute('ALTER TABLE users ADD COLUMN free_trial_date TIMESTAMP')
                await db.commit()
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    language TEXT DEFAULT 'en',
                    currency TEXT DEFAULT 'USD',
                    referrer_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_spent REAL DEFAULT 0.0,
                    free_days INTEGER DEFAULT 0,
                    free_ads_used INTEGER DEFAULT 0,
                    last_free_ad_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id)
                )
            ''')
            
            # Channels table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    telegram_channel_id TEXT NOT NULL,
                    subscribers INTEGER DEFAULT 0,
                    base_price_usd REAL DEFAULT 0.0,
                    is_popular BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Packages table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS packages (
                    package_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    price_usd REAL NOT NULL,
                    duration_days INTEGER NOT NULL,
                    posts_per_day INTEGER NOT NULL,
                    channels_included INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Ads table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ads (
                    ad_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    media_url TEXT,
                    link_url TEXT,
                    content_type TEXT DEFAULT 'text',
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Subscriptions table with progressive plan support
            await db.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    ad_id INTEGER NOT NULL,
                    channel_id TEXT NOT NULL,
                    duration_months INTEGER NOT NULL,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    total_price REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    posts_per_day INTEGER DEFAULT 1,
                    total_posts INTEGER DEFAULT 30,
                    discount_percent INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    last_published TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (ad_id) REFERENCES ads (ad_id),
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
                )
            ''')
            
            # Payments table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subscription_id INTEGER,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    payment_method TEXT NOT NULL,
                    memo TEXT UNIQUE,
                    tx_hash TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confirmed_at TIMESTAMP,
                    failed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions (subscription_id)
                )
            ''')
            
            # Referrals table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    referee_id INTEGER NOT NULL,
                    channel_id TEXT,
                    reward_granted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                    FOREIGN KEY (referee_id) REFERENCES users (user_id),
                    FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
                )
            ''')
            
            # Bot settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Partner rewards tracking table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS partner_rewards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    channel_id TEXT,
                    reward_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP NULL
                )
            ''')
            
            # Partner referrals tracking table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS partner_referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    referred_id INTEGER NOT NULL,
                    channel_id TEXT,
                    commission_rate REAL DEFAULT 0.05,
                    total_earned REAL DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Partner status tracking table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS partner_status (
                    user_id INTEGER PRIMARY KEY,
                    tier TEXT DEFAULT 'Basic',
                    total_earnings REAL DEFAULT 0,
                    pending_rewards REAL DEFAULT 0,
                    total_referrals INTEGER DEFAULT 0,
                    active_channels INTEGER DEFAULT 0,
                    registration_bonus_paid BOOLEAN DEFAULT FALSE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Payout requests table for reward transfers
            await db.execute('''
                CREATE TABLE IF NOT EXISTS payout_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payout_id TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'pending',
                    wallet_address TEXT,
                    transaction_hash TEXT,
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            await db.commit()
            
        # Initialize default channels
        await self.init_default_channels()
        
        # Initialize default packages
        await init_default_packages(self)
        
        # Initialize default settings
        await self.init_default_settings()
    
    async def init_default_channels(self):
        """Initialize default channels - Only called if no channels exist"""
        # This method now does nothing - channels are added automatically when bot becomes admin
        pass
        
    async def init_default_settings(self):
        """Initialize default bot settings"""
        # Check if usage agreement exists, if not create default
        agreement = await self.get_bot_setting('usage_agreement')
        if not agreement:
            default_agreement = """📋 Usage Agreement

By using I3lani Bot's advertising services, you agree to:

1. 📝 Content Guidelines
   - No illegal, harmful, or offensive content
   - No spam or misleading advertisements
   - Respect intellectual property rights

2. 💳 Payment Terms
   - All payments are processed securely
   - No refunds after ad approval and publishing
   - Prices are subject to change

3. 🔒 Privacy & Data
   - Your data is protected and not shared
   - We store only necessary information
   - You can request data deletion

4. 📢 Publishing Rights
   - We reserve the right to reject inappropriate content
   - Ads are published according to selected plan
   - No guarantee of specific results

5. 🚫 Prohibited Uses
   - No cryptocurrency scams or fraud
   - No adult content or illegal services
   - No hate speech or discrimination

For support, contact: @i3lani_support
Last updated: July 2025"""
            
            await self.set_bot_setting(
                'usage_agreement', 
                default_agreement,
                'Terms of service and usage agreement for bot users'
            )
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM users WHERE user_id = ?', (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def create_user(self, user_id: int, username: Optional[str] = None, 
                         language: str = 'en', referrer_id: Optional[int] = None) -> bool:
        """Create new user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO users (user_id, username, language, referrer_id)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, language, referrer_id))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    async def set_user_language(self, user_id: int, language: str) -> bool:
        """Set user language preference"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users SET language = ? WHERE user_id = ?
                ''', (language, user_id))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error setting user language: {e}")
            return False
    
    async def get_active_channels(self) -> List[Dict]:
        """Get all active advertising channels"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM channels 
                    WHERE is_active = 1 
                    ORDER BY name
                ''') as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting active channels: {e}")
            return []
    
    async def update_user_language(self, user_id: int, language: str) -> bool:
        """Update user language"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'UPDATE users SET language = ? WHERE user_id = ?',
                    (language, user_id)
                )
                await db.commit()
                return True
        except Exception as e:
            print(f"Error updating user language: {e}")
            return False
    
    async def create_ad(self, user_id: int, content: str, 
                       media_url: Optional[str] = None, content_type: str = 'text') -> int:
        """Create new ad"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO ads (user_id, content, media_url, content_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, content, media_url, content_type))
            await db.commit()
            return cursor.lastrowid or 0
    
    async def get_channels(self, active_only: bool = True) -> List[Dict]:
        """Get all channels"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT * FROM channels'
            if active_only:
                query += ' WHERE is_active = 1'
            query += ' ORDER BY is_popular DESC, subscribers DESC'
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def add_channel_automatically(self, channel_id: str, channel_name: str, 
                                      telegram_channel_id: str, subscribers: int = 0,
                                      active_subscribers: int = 0, total_posts: int = 0,
                                      category: str = 'general', description: str = '',
                                      base_price_usd: float = 5.0) -> bool:
        """Add channel automatically when bot becomes admin with detailed info"""
        async with aiosqlite.connect(self.db_path) as db:
            # First check if we need to add new columns
            cursor = await db.execute("PRAGMA table_info(channels)")
            columns = [row[1] for row in await cursor.fetchall()]
            
            # Add missing columns if they don't exist
            if 'active_subscribers' not in columns:
                await db.execute('ALTER TABLE channels ADD COLUMN active_subscribers INTEGER DEFAULT 0')
            if 'total_posts' not in columns:
                await db.execute('ALTER TABLE channels ADD COLUMN total_posts INTEGER DEFAULT 0')
            if 'category' not in columns:
                await db.execute('ALTER TABLE channels ADD COLUMN category TEXT DEFAULT "general"')
            if 'description' not in columns:
                await db.execute('ALTER TABLE channels ADD COLUMN description TEXT')
            if 'last_updated' not in columns:
                await db.execute('ALTER TABLE channels ADD COLUMN last_updated TIMESTAMP')
            
            # Insert or update channel with all details
            await db.execute('''
                INSERT OR REPLACE INTO channels 
                (channel_id, name, telegram_channel_id, subscribers, active_subscribers, 
                 total_posts, category, description, base_price_usd, is_popular, is_active, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                channel_id, channel_name, telegram_channel_id,
                subscribers, active_subscribers, total_posts, category, description,
                base_price_usd, False, True
            ))
            await db.commit()
            return True
    
    async def remove_channel_automatically(self, telegram_channel_id: str) -> bool:
        """Remove channel when bot is no longer admin"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE channels SET is_active = FALSE 
                WHERE telegram_channel_id = ?
            ''', (telegram_channel_id,))
            await db.commit()
            return True
    
    async def activate_channel(self, channel_id: str) -> bool:
        """Activate a channel"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE channels 
                    SET is_active = 1, last_updated = CURRENT_TIMESTAMP
                    WHERE telegram_channel_id = ? OR channel_id = ?
                ''', (channel_id, channel_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error activating channel: {e}")
            return False
    
    async def deactivate_channel(self, channel_id: str) -> bool:
        """Deactivate a channel"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE channels 
                    SET is_active = 0, last_updated = CURRENT_TIMESTAMP
                    WHERE telegram_channel_id = ? OR channel_id = ?
                ''', (channel_id, channel_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error deactivating channel: {e}")
            return False
    
    async def delete_channel(self, channel_id: str) -> bool:
        """Permanently delete a channel from database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    DELETE FROM channels 
                    WHERE telegram_channel_id = ? OR channel_id = ?
                ''', (channel_id, channel_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting channel: {e}")
            return False
    
    async def clean_invalid_channels(self) -> int:
        """Remove all channels that bot can't access"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Delete invalid channels (these are old fake channels)
                result = await db.execute('''
                    DELETE FROM channels 
                    WHERE name IN ('I3lani Business', 'I3lani Tech', 'Tech News Channel', 'Business Updates')
                    OR telegram_channel_id NOT LIKE '@%'
                ''')
                await db.commit()
                return result.rowcount
        except Exception as e:
            logger.error(f"Error cleaning invalid channels: {e}")
            return 0

    async def get_bot_admin_channels(self) -> List[Dict]:
        """Get channels where bot is admin (active channels only)"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT channel_id, name, telegram_channel_id, subscribers, base_price_usd, is_popular
                FROM channels 
                WHERE is_active = TRUE
                ORDER BY is_popular DESC, subscribers DESC
            ''') as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'channel_id': row[0],
                        'name': row[1],
                        'telegram_channel_id': row[2],
                        'subscribers': row[3],
                        'base_price_usd': row[4],
                        'is_popular': row[5]
                    } for row in rows
                ]
    
    async def create_subscription(self, user_id: int, ad_id: int, 
                                 channel_id: str, duration_months: int,
                                 total_price: float, currency: str = 'USD',
                                 posts_per_day: int = 1, total_posts: int = 30,
                                 discount_percent: int = 0) -> int:
        """Create new subscription with progressive plan details"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO subscriptions 
                (user_id, ad_id, channel_id, duration_months, total_price, currency, 
                 posts_per_day, total_posts, discount_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, ad_id, channel_id, duration_months, total_price, currency,
                  posts_per_day, total_posts, discount_percent))
            await db.commit()
            return cursor.lastrowid
    
    async def get_subscription(self, subscription_id: int) -> Optional[Dict]:
        """Get subscription by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM subscriptions WHERE subscription_id = ?
            ''', (subscription_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def create_payment(self, user_id: int, subscription_id: int,
                           amount: float, currency: str, payment_method: str,
                           memo: str) -> int:
        """Create new payment"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO payments 
                (user_id, subscription_id, amount, currency, payment_method, memo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, subscription_id, amount, currency, payment_method, memo))
            await db.commit()
            return cursor.lastrowid
    
    async def activate_subscriptions(self, subscription_ids: List[int], duration_days: int) -> bool:
        """Activate subscriptions after payment confirmation"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Update all subscriptions to active status
                for subscription_id in subscription_ids:
                    await db.execute('''
                        UPDATE subscriptions 
                        SET status = 'active',
                            start_date = CURRENT_TIMESTAMP,
                            end_date = datetime('now', '+' || ? || ' days')
                        WHERE subscription_id = ?
                    ''', (duration_days, subscription_id))
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error activating subscriptions: {e}")
            return False
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get total ads
            async with db.execute(
                'SELECT COUNT(*) as total_ads FROM ads WHERE user_id = ?',
                (user_id,)
            ) as cursor:
                total_ads = (await cursor.fetchone())[0]
            
            # Get active subscriptions
            async with db.execute('''
                SELECT COUNT(*) as active_ads FROM subscriptions 
                WHERE user_id = ? AND status = 'active'
            ''', (user_id,)) as cursor:
                active_ads = (await cursor.fetchone())[0]
            
            # Get total spent
            async with db.execute(
                'SELECT total_spent FROM users WHERE user_id = ?',
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                total_spent = row[0] if row else 0.0
            
            # Get free ads used this month
            async with db.execute('''
                SELECT COUNT(*) as free_ads_used FROM ads 
                WHERE user_id = ? AND package_type = 'free' 
                AND created_at > datetime('now', 'start of month')
            ''', (user_id,)) as cursor:
                free_ads_used = (await cursor.fetchone())[0]
            
            return {
                'total_ads': total_ads,
                'active_ads': active_ads,
                'total_spent': total_spent,
                'free_ads_used': free_ads_used
            }
    
    async def get_referral_stats(self, user_id: int) -> Dict:
        """Get referral statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get referral count
            async with db.execute(
                'SELECT COUNT(*) as total_referrals FROM referrals WHERE referrer_id = ?',
                (user_id,)
            ) as cursor:
                total_referrals = (await cursor.fetchone())[0]
            
            # Get free days
            async with db.execute(
                'SELECT free_days FROM users WHERE user_id = ?',
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                free_days = row[0] if row else 0
            
            return {
                'total_referrals': total_referrals,
                'free_days': free_days,
                'total_value': total_referrals * 3  # 3 free days per referral
            }
    
    async def create_referral(self, referrer_id: int, referee_id: int) -> bool:
        """Create referral relationship"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO referrals (referrer_id, referee_id)
                    VALUES (?, ?)
                ''', (referrer_id, referee_id))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error creating referral: {e}")
            return False
    
    # Partner reward methods
    async def add_partner_reward(self, user_id: int, channel_id: str, reward_type: str, 
                                amount: float, description: str = None) -> bool:
        """Add a new partner reward"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO partner_rewards (user_id, channel_id, reward_type, amount, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, channel_id, reward_type, amount, description))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding partner reward: {e}")
            return False
    
    async def get_partner_status(self, user_id: int) -> Dict:
        """Get partner status and statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute('''
                    SELECT * FROM partner_status WHERE user_id = ?
                ''', (user_id,))
                result = await cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error getting partner status: {e}")
            return None
    
    async def create_partner_status(self, user_id: int) -> bool:
        """Create initial partner status and give registration bonus"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create partner status
                await db.execute('''
                    INSERT OR REPLACE INTO partner_status 
                    (user_id, tier, total_earnings, pending_rewards, registration_bonus_paid)
                    VALUES (?, 'Basic', 5.0, 5.0, TRUE)
                ''', (user_id,))
                
                # Add registration bonus reward
                await db.execute('''
                    INSERT INTO partner_rewards 
                    (user_id, reward_type, amount, description, status)
                    VALUES (?, 'registration_bonus', 5.0, 'Welcome bonus for new partners', 'confirmed')
                ''', (user_id,))
                
                await db.commit()
                return True
        except Exception as e:
            print(f"Error creating partner status: {e}")
            return False
    
    async def update_partner_earnings(self, user_id: int, amount: float) -> bool:
        """Update partner earnings"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE partner_status 
                    SET total_earnings = total_earnings + ?, 
                        pending_rewards = pending_rewards + ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (amount, amount, user_id))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error updating partner earnings: {e}")
            return False
    
    async def get_partner_rewards(self, user_id: int) -> List[Dict]:
        """Get partner rewards history"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute('''
                    SELECT * FROM partner_rewards 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC
                ''', (user_id,))
                results = await cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting partner rewards: {e}")
            return []
    
    async def get_partner_referrals(self, user_id: int) -> List[Dict]:
        """Get partner referrals"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('''
                    SELECT pr.*, u.username as referred_username
                    FROM partner_referrals pr
                    LEFT JOIN users u ON pr.referred_id = u.user_id
                    WHERE pr.referrer_id = ?
                    ORDER BY pr.created_at DESC
                ''', (user_id,))
                results = await cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting partner referrals: {e}")
            return []
    
    async def get_referral_count(self, user_id: int) -> int:
        """Get total referral count for user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('''
                    SELECT COUNT(*) FROM referrals WHERE referrer_id = ?
                ''', (user_id,))
                result = await cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting referral count: {e}")
            return 0
    
    async def get_referral_by_ids(self, referrer_id: int, referred_id: int) -> Optional[Dict]:
        """Check if referral already exists"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('''
                    SELECT * FROM referrals WHERE referrer_id = ? AND referee_id = ?
                ''', (referrer_id, referred_id))
                result = await cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error getting referral by IDs: {e}")
            return None
    
    async def execute_query(self, query: str, params: tuple = ()) -> bool:
        """Execute raw SQL query"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(query, params)
                await db.commit()
                return True
        except Exception as e:
            print(f"Error executing query: {e}")
            return False
    
    async def increment_free_ads_used(self, user_id: int) -> bool:
        """Increment free ads used count for user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if user exists in stats
                cursor = await db.execute('''
                    SELECT free_ads_used FROM users WHERE user_id = ?
                ''', (user_id,))
                result = await cursor.fetchone()
                
                if result:
                    # Update existing count
                    current_count = result[0] or 0
                    await db.execute('''
                        UPDATE users SET free_ads_used = ? WHERE user_id = ?
                    ''', (current_count + 1, user_id))
                else:
                    # Initialize count for new user
                    await db.execute('''
                        UPDATE users SET free_ads_used = 1 WHERE user_id = ?
                    ''', (user_id,))
                
                await db.commit()
                return True
        except Exception as e:
            print(f"Error incrementing free ads used: {e}")
            return False

    async def reset_free_ads_counter(self, user_id: int) -> bool:
        """Reset the free ads counter for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET free_ads_used = 0, last_free_ad_reset = ? WHERE user_id = ?",
                (datetime.now().isoformat(), user_id)
            )
            await db.commit()
            return True
    
    async def increment_free_ads_used(self, user_id: int) -> bool:
        """Increment the free ads used counter for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET free_ads_used = free_ads_used + 1 WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
            return True
    
    async def check_free_trial_available(self, user_id: int) -> bool:
        """Check if user can use free trial"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT free_trial_used FROM users WHERE user_id = ?
            ''', (user_id,))
            result = await cursor.fetchone()
            
            if result:
                return not result[0]  # Return True if free_trial_used is False
            return True  # New users can use free trial
    
    async def use_free_trial(self, user_id: int):
        """Mark free trial as used"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE users 
                SET free_trial_used = TRUE, free_trial_date = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (user_id,))
            await db.commit()
            
    async def create_package(self, package_id: str, name: str, price_usd: float,
                            duration_days: int, posts_per_day: int, channels_included: int) -> bool:
        """Create new package"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO packages 
                (package_id, name, price_usd, duration_days, posts_per_day, channels_included)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (package_id, name, price_usd, duration_days, posts_per_day, channels_included))
            await db.commit()
            return True
            
    async def get_packages(self, active_only: bool = True) -> List[Dict]:
        """Get all packages"""
        async with aiosqlite.connect(self.db_path) as db:
            if active_only:
                cursor = await db.execute('''
                    SELECT package_id, name, price_usd, duration_days, posts_per_day, channels_included
                    FROM packages WHERE is_active = 1
                    ORDER BY price_usd ASC
                ''')
            else:
                cursor = await db.execute('''
                    SELECT package_id, name, price_usd, duration_days, posts_per_day, channels_included
                    FROM packages
                    ORDER BY price_usd ASC
                ''')
            
            rows = await cursor.fetchall()
            return [
                {
                    'package_id': row[0],
                    'name': row[1],
                    'price_usd': row[2],
                    'duration_days': row[3],
                    'posts_per_day': row[4],
                    'channels_included': row[5]
                }
                for row in rows
            ]
            
    async def get_package(self, package_id: str) -> Optional[Dict]:
        """Get package by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT package_id, name, price_usd, duration_days, posts_per_day, channels_included
                FROM packages WHERE package_id = ?
            ''', (package_id,))
            row = await cursor.fetchone()
            
            if row:
                return {
                    'package_id': row[0],
                    'name': row[1],
                    'price_usd': row[2],
                    'duration_days': row[3],
                    'posts_per_day': row[4],
                    'channels_included': row[5]
                }
            return None
            
    async def get_bot_setting(self, setting_key: str) -> Optional[str]:
        """Get bot setting value"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT setting_value FROM bot_settings WHERE setting_key = ?',
                (setting_key,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None
            
    async def set_bot_setting(self, setting_key: str, setting_value: str, description: str = None) -> bool:
        """Set bot setting value"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO bot_settings (setting_key, setting_value, description, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (setting_key, setting_value, description, datetime.now().isoformat()))
            await db.commit()
            return True
            
    async def get_all_bot_settings(self) -> List[Dict]:
        """Get all bot settings"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT * FROM bot_settings ORDER BY setting_key')
            rows = await cursor.fetchall()
            return [
                {
                    'setting_key': row[0],
                    'setting_value': row[1],
                    'description': row[2],
                    'updated_at': row[3]
                }
                for row in rows
            ]
    
    # Payout system methods for reward transfers from bot wallet
    async def create_payout_request(self, user_id: int, amount: float, payout_id: str, status: str = 'pending'):
        """Create a new payout request for reward transfer"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO payout_requests (user_id, amount, payout_id, status)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, amount, payout_id, status))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error creating payout request: {e}")
            return False
    
    async def get_payout_requests(self, status: str = None) -> List[Dict]:
        """Get payout requests for admin processing"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if status:
                    cursor = await db.execute('''
                        SELECT pr.*, u.username 
                        FROM payout_requests pr
                        LEFT JOIN users u ON pr.user_id = u.user_id
                        WHERE pr.status = ?
                        ORDER BY pr.requested_at DESC
                    ''', (status,))
                else:
                    cursor = await db.execute('''
                        SELECT pr.*, u.username 
                        FROM payout_requests pr
                        LEFT JOIN users u ON pr.user_id = u.user_id
                        ORDER BY pr.requested_at DESC
                    ''')
                
                requests = await cursor.fetchall()
                return [dict(row) for row in requests]
        except Exception as e:
            print(f"Error getting payout requests: {e}")
            return []
    
    async def update_payout_status(self, payout_id: str, status: str, wallet_address: str = None, 
                                  transaction_hash: str = None, notes: str = None):
        """Update payout request status after bot wallet transfer"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if status == 'completed':
                    await db.execute('''
                        UPDATE payout_requests 
                        SET status = ?, wallet_address = ?, transaction_hash = ?, 
                            notes = ?, processed_at = CURRENT_TIMESTAMP
                        WHERE payout_id = ?
                    ''', (status, wallet_address, transaction_hash, notes, payout_id))
                    
                    # Reset user's pending rewards to 0 after successful transfer
                    cursor = await db.execute('SELECT user_id, amount FROM payout_requests WHERE payout_id = ?', (payout_id,))
                    row = await cursor.fetchone()
                    if row:
                        user_id, amount = row
                        await db.execute('''
                            UPDATE partner_status 
                            SET pending_rewards = 0, last_updated = CURRENT_TIMESTAMP
                            WHERE user_id = ?
                        ''', (user_id,))
                else:
                    await db.execute('''
                        UPDATE payout_requests 
                        SET status = ?, notes = ?
                        WHERE payout_id = ?
                    ''', (status, notes, payout_id))
                
                await db.commit()
                return True
        except Exception as e:
            print(f"Error updating payout status: {e}")
            return False


# Global database instance
db = Database()


async def init_db():
    """Initialize database"""
    await db.init_db()


async def get_user_language(user_id: int) -> str:
    """Get user language, default to English"""
    user = await db.get_user(user_id)
    return user['language'] if user else 'en'


async def ensure_user_exists(user_id: int, username: Optional[str] = None) -> bool:
    """Ensure user exists in database"""
    user = await db.get_user(user_id)
    if not user:
        return await db.create_user(user_id, username)
    return True


# Add to Database class
async def init_default_packages(db_instance):
    """Initialize default packages"""
    # Check if packages already exist
    existing_packages = await db_instance.get_packages()
    if existing_packages:
        return
        
    # Add default packages
    default_packages = [
        {
            'package_id': 'free',
            'name': 'Free Plan',
            'price_usd': 0.0,
            'duration_days': 3,
            'posts_per_day': 1,
            'channels_included': 1
        },
        {
            'package_id': 'bronze',
            'name': '1 Month Plan',
            'price_usd': 9.0,
            'duration_days': 30,
            'posts_per_day': 1,
            'channels_included': 3
        },
        {
            'package_id': 'silver',
            'name': '3 Months Plan',
            'price_usd': 27.0,
            'duration_days': 90,
            'posts_per_day': 1,
            'channels_included': 3
        },
        {
            'package_id': 'gold',
            'name': '6 Months Plan',
            'price_usd': 49.0,
            'duration_days': 180,
            'posts_per_day': 1,
            'channels_included': 3
        }
    ]
    
    async with aiosqlite.connect(db_instance.db_path) as db:
        for package in default_packages:
            await db.execute('''
                INSERT OR IGNORE INTO packages
                (package_id, name, price_usd, duration_days, posts_per_day, channels_included, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                package['package_id'], package['name'], package['price_usd'],
                package['duration_days'], package['posts_per_day'], 
                package['channels_included'], True
            ))
        await db.commit()

# Additional Database methods for Channel Incentives
Database.get_user_channels = lambda self, user_id: self._get_user_channels(user_id)
Database.get_channel_ads_count = lambda self, channel_id: self._get_channel_ads_count(channel_id)
Database.get_channel_by_id = lambda self, channel_id: self._get_channel_by_id(channel_id)

async def _get_user_channels(self, user_id: int) -> List[Dict]:
    """Get channels owned by user (where they are admin)"""
    try:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM channels 
                WHERE owner_id = ? AND is_active = 1
                ORDER BY subscribers DESC
            ''', (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting user channels: {e}")
        return []

async def _get_channel_ads_count(self, channel_id: str) -> int:
    """Get number of ads hosted in channel"""
    try:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT COUNT(*) FROM subscriptions 
                WHERE channel_id = ? AND status = 'active'
            ''', (channel_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
    except Exception as e:
        print(f"Error getting channel ads count: {e}")
        return 0

async def _get_channel_by_id(self, channel_id: str) -> Optional[Dict]:
    """Get channel by ID"""
    try:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT * FROM channels WHERE id = ?
            ''', (channel_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    except Exception as e:
        print(f"Error getting channel by ID: {e}")
        return None

# Anti-fraud database methods
async def log_user_interaction(self, user_id: int, interaction_type: str, details: str = ""):
    """Log user interaction for fraud detection"""
    async with aiosqlite.connect(self.db_path) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                interaction_type TEXT NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            INSERT INTO user_interactions (user_id, interaction_type, details)
            VALUES (?, ?, ?)
        """, (user_id, interaction_type, details))
        
        await conn.commit()

async def log_user_action(self, user_id: int, action_type: str, details: str = ""):
    """Log user action for fraud detection"""
    async with aiosqlite.connect(self.db_path) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            INSERT INTO user_actions (user_id, action_type, details)
            VALUES (?, ?, ?)
        """, (user_id, action_type, details))
        
        await conn.commit()

async def is_user_blocked(self, user_id: int) -> bool:
    """Check if user is blocked for fraud"""
    async with aiosqlite.connect(self.db_path) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'blocked'
            )
        """)
        
        query = """
        SELECT status FROM blocked_users 
        WHERE user_id = ? AND status IN ('blocked', 'permanently_blocked')
        """
        
        async with conn.execute(query, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return bool(row)

async def is_user_banned(self, user_id: int) -> bool:
    """Check if user is banned for content violations"""
    async with aiosqlite.connect(self.db_path) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS banned_users (
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                banned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'banned'
            )
        """)
        
        query = """
        SELECT status FROM banned_users 
        WHERE user_id = ? AND status = 'permanently_banned'
        """
        
        async with conn.execute(query, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return bool(row)

# Bind methods to Database class
Database._get_user_channels = _get_user_channels
Database._get_channel_ads_count = _get_channel_ads_count  
Database._get_channel_by_id = _get_channel_by_id
Database.log_user_interaction = log_user_interaction
Database.log_user_action = log_user_action
Database.is_user_blocked = is_user_blocked
Database.is_user_banned = is_user_banned