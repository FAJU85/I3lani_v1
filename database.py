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
            
            # Subscriptions table
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
                    status TEXT DEFAULT 'pending',
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
            
            await db.commit()
            
        # Initialize default channels
        await self.init_default_channels()
        
        # Initialize default packages
        await init_default_packages(self)
    
    async def init_default_channels(self):
        """Initialize default channels"""
        # Check if channels already exist
        existing_channels = await self.get_channels()
        if existing_channels:
            return
            
        # Add default channels
        default_channels = [
            {
                'channel_id': 'i3lani_main',
                'name': 'I3lani Main Channel',
                'telegram_channel_id': '@i3lani',
                'subscribers': 10000,
                'base_price_usd': 5.0,
                'is_popular': True,
                'is_active': True
            },
            {
                'channel_id': 'i3lani_tech',
                'name': 'I3lani Tech',
                'telegram_channel_id': '@i3lani_tech',
                'subscribers': 5000,
                'base_price_usd': 3.0,
                'is_popular': False,
                'is_active': True
            },
            {
                'channel_id': 'i3lani_business',
                'name': 'I3lani Business',
                'telegram_channel_id': '@i3lani_business',
                'subscribers': 7500,
                'base_price_usd': 4.0,
                'is_popular': False,
                'is_active': True
            }
        ]
        
        async with aiosqlite.connect(self.db_path) as db:
            for channel in default_channels:
                await db.execute('''
                    INSERT OR IGNORE INTO channels 
                    (channel_id, name, telegram_channel_id, subscribers, base_price_usd, is_popular, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    channel['channel_id'], channel['name'], channel['telegram_channel_id'],
                    channel['subscribers'], channel['base_price_usd'], 
                    channel['is_popular'], channel['is_active']
                ))
            await db.commit()
    
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
    
    async def create_subscription(self, user_id: int, ad_id: int, 
                                 channel_id: str, duration_months: int,
                                 total_price: float, currency: str = 'USD') -> int:
        """Create new subscription"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO subscriptions 
                (user_id, ad_id, channel_id, duration_months, total_price, currency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, ad_id, channel_id, duration_months, total_price, currency))
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
            
            return {
                'total_ads': total_ads,
                'active_ads': active_ads,
                'total_spent': total_spent
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