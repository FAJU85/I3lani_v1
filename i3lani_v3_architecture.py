"""
I3lani v3 Architecture Implementation
Complete redesign from subscription-based to auction-based advertising system
"""

import asyncio
import aiosqlite
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging
import json

logger = logging.getLogger(__name__)

class I3laniV3Database:
    """Database schema for I3lani v3 architecture"""
    
    def __init__(self, db_path: str = "i3lani_v3.db"):
        self.db_path = db_path
    
    async def initialize_v3_database(self):
        """Initialize I3lani v3 database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table (advertisers, channel owners, affiliates)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users_v3 (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    user_type TEXT CHECK(user_type IN ('advertiser', 'channel_owner', 'affiliate')),
                    balance_ton DECIMAL(10,8) DEFAULT 0,
                    balance_stars INTEGER DEFAULT 0,
                    referrer_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users_v3(user_id)
                )
            """)
            
            # Channels table (registered by channel owners)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS channels_v3 (
                    channel_id TEXT PRIMARY KEY,
                    channel_name TEXT,
                    owner_id INTEGER,
                    category TEXT,
                    subscribers INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users_v3(user_id)
                )
            """)
            
            # Ads table (created by advertisers)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ads_v3 (
                    ad_id TEXT PRIMARY KEY,
                    advertiser_id INTEGER,
                    content TEXT,
                    category TEXT,
                    bid_type TEXT CHECK(bid_type IN ('CPC', 'CPM')),
                    bid_amount DECIMAL(10,2),
                    status TEXT CHECK(status IN ('pending', 'approved', 'rejected', 'active', 'completed')),
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    total_cost DECIMAL(10,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (advertiser_id) REFERENCES users_v3(user_id)
                )
            """)
            
            # Ad placements (auction results)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ad_placements_v3 (
                    placement_id TEXT PRIMARY KEY,
                    ad_id TEXT,
                    channel_id TEXT,
                    placement_date DATE,
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    revenue DECIMAL(10,2) DEFAULT 0,
                    FOREIGN KEY (ad_id) REFERENCES ads_v3(ad_id),
                    FOREIGN KEY (channel_id) REFERENCES channels_v3(channel_id)
                )
            """)
            
            # Payments table (TON and Telegram Stars)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments_v3 (
                    payment_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    amount DECIMAL(10,8),
                    currency TEXT CHECK(currency IN ('TON', 'STARS')),
                    purpose TEXT,
                    status TEXT CHECK(status IN ('pending', 'completed', 'failed')),
                    transaction_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users_v3(user_id)
                )
            """)
            
            # Withdrawals table (TON only)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS withdrawals_v3 (
                    withdrawal_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    amount DECIMAL(10,8),
                    wallet_address TEXT,
                    status TEXT CHECK(status IN ('pending', 'processing', 'completed', 'failed')),
                    transaction_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users_v3(user_id)
                )
            """)
            
            # Commissions table (affiliate earnings)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS commissions_v3 (
                    commission_id TEXT PRIMARY KEY,
                    affiliate_id INTEGER,
                    referred_user_id INTEGER,
                    amount DECIMAL(10,8),
                    source TEXT, -- 'advertiser_spending' or 'channel_owner_earnings'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (affiliate_id) REFERENCES users_v3(user_id),
                    FOREIGN KEY (referred_user_id) REFERENCES users_v3(user_id)
                )
            """)
            
            await db.commit()
            logger.info("✅ I3lani v3 database schema initialized")

class AuctionSystem:
    """Daily auction system for matching ads to channels"""
    
    def __init__(self, db: I3laniV3Database):
        self.db = db
    
    async def run_daily_auction(self):
        """Run daily auction to match ads to channels"""
        logger.info("🔄 Running daily auction...")
        
        async with aiosqlite.connect(self.db.db_path) as db:
            # Get all approved ads
            async with db.execute("""
                SELECT ad_id, advertiser_id, category, bid_type, bid_amount, content
                FROM ads_v3 
                WHERE status = 'approved'
                ORDER BY bid_amount DESC
            """) as cursor:
                ads = await cursor.fetchall()
            
            # Get all active channels
            async with db.execute("""
                SELECT channel_id, category, subscribers, owner_id
                FROM channels_v3 
                WHERE is_active = TRUE
                ORDER BY subscribers DESC
            """) as cursor:
                channels = await cursor.fetchall()
            
            placements = []
            today = datetime.now().date()
            
            for ad in ads:
                ad_id, advertiser_id, ad_category, bid_type, bid_amount, content = ad
                
                # Find matching channels by category
                matching_channels = [
                    ch for ch in channels 
                    if ch[1] == ad_category  # category match
                ]
                
                # Place ad in top channels based on bid
                for channel in matching_channels[:3]:  # Top 3 channels
                    channel_id, category, subscribers, owner_id = channel
                    
                    placement_id = f"PLC-{datetime.now().strftime('%Y%m%d')}-{ad_id[:6]}-{channel_id[:6]}"
                    
                    placements.append({
                        'placement_id': placement_id,
                        'ad_id': ad_id,
                        'channel_id': channel_id,
                        'placement_date': today,
                        'bid_amount': bid_amount,
                        'bid_type': bid_type,
                        'content': content
                    })
            
            # Insert placements into database
            for placement in placements:
                await db.execute("""
                    INSERT INTO ad_placements_v3 
                    (placement_id, ad_id, channel_id, placement_date)
                    VALUES (?, ?, ?, ?)
                """, (
                    placement['placement_id'],
                    placement['ad_id'],
                    placement['channel_id'],
                    placement['placement_date']
                ))
            
            await db.commit()
            logger.info(f"✅ Daily auction completed: {len(placements)} placements created")
            
            return placements

class RevenueCalculator:
    """Calculate revenue sharing between platform and channel owners"""
    
    def __init__(self, db: I3laniV3Database):
        self.db = db
        self.channel_owner_share = Decimal('0.68')  # 68% to channel owners
        self.platform_share = Decimal('0.32')      # 32% to platform
        self.affiliate_commission = Decimal('0.05') # 5% affiliate commission
    
    async def calculate_placement_revenue(self, placement_id: str, impressions: int, clicks: int):
        """Calculate revenue for a specific ad placement"""
        async with aiosqlite.connect(self.db.db_path) as db:
            # Get placement and ad details
            async with db.execute("""
                SELECT p.ad_id, p.channel_id, a.bid_type, a.bid_amount, c.owner_id
                FROM ad_placements_v3 p
                JOIN ads_v3 a ON p.ad_id = a.ad_id
                JOIN channels_v3 c ON p.channel_id = c.channel_id
                WHERE p.placement_id = ?
            """, (placement_id,)) as cursor:
                result = await cursor.fetchone()
            
            if not result:
                return None
            
            ad_id, channel_id, bid_type, bid_amount, owner_id = result
            
            # Calculate revenue based on bid type
            if bid_type == 'CPM':
                revenue = Decimal(str(bid_amount)) * Decimal(str(impressions)) / 1000
            else:  # CPC
                revenue = Decimal(str(bid_amount)) * Decimal(str(clicks))
            
            # Calculate shares
            channel_owner_earnings = revenue * self.channel_owner_share
            platform_earnings = revenue * self.platform_share
            
            # Update placement revenue
            await db.execute("""
                UPDATE ad_placements_v3 
                SET impressions = ?, clicks = ?, revenue = ?
                WHERE placement_id = ?
            """, (impressions, clicks, float(revenue), placement_id))
            
            # Update channel owner balance
            await db.execute("""
                UPDATE users_v3 
                SET balance_ton = balance_ton + ?
                WHERE user_id = ?
            """, (float(channel_owner_earnings), owner_id))
            
            # Calculate affiliate commission if applicable
            async with db.execute("""
                SELECT referrer_id FROM users_v3 WHERE user_id = ?
            """, (owner_id,)) as cursor:
                referrer_result = await cursor.fetchone()
            
            if referrer_result and referrer_result[0]:
                affiliate_id = referrer_result[0]
                commission = channel_owner_earnings * self.affiliate_commission
                
                # Record commission
                commission_id = f"COM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                await db.execute("""
                    INSERT INTO commissions_v3 
                    (commission_id, affiliate_id, referred_user_id, amount, source)
                    VALUES (?, ?, ?, ?, 'channel_owner_earnings')
                """, (commission_id, affiliate_id, owner_id, float(commission)))
                
                # Update affiliate balance
                await db.execute("""
                    UPDATE users_v3 
                    SET balance_ton = balance_ton + ?
                    WHERE user_id = ?
                """, (float(commission), affiliate_id))
            
            await db.commit()
            
            return {
                'total_revenue': float(revenue),
                'channel_owner_earnings': float(channel_owner_earnings),
                'platform_earnings': float(platform_earnings),
                'impressions': impressions,
                'clicks': clicks
            }

class WithdrawalSystem:
    """Handle TON withdrawals for channel owners and affiliates"""
    
    def __init__(self, db: I3laniV3Database):
        self.db = db
        self.minimum_withdrawal = Decimal('50.0')  # $50 minimum
    
    async def process_withdrawal_request(self, user_id: int, amount: Decimal, wallet_address: str):
        """Process withdrawal request"""
        async with aiosqlite.connect(self.db.db_path) as db:
            # Check user balance
            async with db.execute("""
                SELECT balance_ton FROM users_v3 WHERE user_id = ?
            """, (user_id,)) as cursor:
                result = await cursor.fetchone()
            
            if not result:
                return {'success': False, 'error': 'User not found'}
            
            balance = Decimal(str(result[0]))
            
            if balance < amount:
                return {'success': False, 'error': 'Insufficient balance'}
            
            if amount < self.minimum_withdrawal:
                return {'success': False, 'error': f'Minimum withdrawal is ${self.minimum_withdrawal}'}
            
            # Create withdrawal record
            withdrawal_id = f"WD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            await db.execute("""
                INSERT INTO withdrawals_v3 
                (withdrawal_id, user_id, amount, wallet_address, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (withdrawal_id, user_id, float(amount), wallet_address))
            
            # Update user balance
            await db.execute("""
                UPDATE users_v3 
                SET balance_ton = balance_ton - ?
                WHERE user_id = ?
            """, (float(amount), user_id))
            
            await db.commit()
            
            return {
                'success': True,
                'withdrawal_id': withdrawal_id,
                'amount': float(amount),
                'wallet_address': wallet_address
            }

class I3laniV3Core:
    """Core I3lani v3 system"""
    
    def __init__(self):
        self.db = I3laniV3Database()
        self.auction = AuctionSystem(self.db)
        self.revenue = RevenueCalculator(self.db)
        self.withdrawal = WithdrawalSystem(self.db)
    
    async def initialize(self):
        """Initialize I3lani v3 system"""
        await self.db.initialize_v3_database()
        logger.info("✅ I3lani v3 system initialized")
    
    async def register_user(self, user_id: int, username: str, first_name: str, 
                          user_type: str, referrer_id: Optional[int] = None):
        """Register new user"""
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users_v3 
                (user_id, username, first_name, user_type, referrer_id)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, first_name, user_type, referrer_id))
            await db.commit()
    
    async def add_channel(self, channel_id: str, channel_name: str, owner_id: int, 
                         category: str, subscribers: int = 0):
        """Add new channel"""
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO channels_v3 
                (channel_id, channel_name, owner_id, category, subscribers)
                VALUES (?, ?, ?, ?, ?)
            """, (channel_id, channel_name, owner_id, category, subscribers))
            await db.commit()
    
    async def create_ad(self, advertiser_id: int, content: str, category: str, 
                       bid_type: str, bid_amount: Decimal):
        """Create new ad"""
        ad_id = f"AD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute("""
                INSERT INTO ads_v3 
                (ad_id, advertiser_id, content, category, bid_type, bid_amount, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
            """, (ad_id, advertiser_id, content, category, bid_type, float(bid_amount)))
            await db.commit()
        
        return ad_id
    
    async def get_user_stats(self, user_id: int):
        """Get user statistics"""
        async with aiosqlite.connect(self.db.db_path) as db:
            # Get user info
            async with db.execute("""
                SELECT user_type, balance_ton, balance_stars FROM users_v3 WHERE user_id = ?
            """, (user_id,)) as cursor:
                user_info = await cursor.fetchone()
            
            if not user_info:
                return None
            
            user_type, balance_ton, balance_stars = user_info
            
            stats = {
                'user_type': user_type,
                'balance_ton': balance_ton,
                'balance_stars': balance_stars
            }
            
            if user_type == 'advertiser':
                # Get advertiser stats
                async with db.execute("""
                    SELECT COUNT(*) as total_ads, SUM(impressions) as total_impressions, 
                           SUM(clicks) as total_clicks, SUM(total_cost) as total_spent
                    FROM ads_v3 WHERE advertiser_id = ?
                """, (user_id,)) as cursor:
                    ad_stats = await cursor.fetchone()
                
                stats.update({
                    'total_ads': ad_stats[0] or 0,
                    'total_impressions': ad_stats[1] or 0,
                    'total_clicks': ad_stats[2] or 0,
                    'total_spent': ad_stats[3] or 0
                })
            
            elif user_type == 'channel_owner':
                # Get channel owner stats
                async with db.execute("""
                    SELECT COUNT(*) as total_channels FROM channels_v3 WHERE owner_id = ?
                """, (user_id,)) as cursor:
                    channel_stats = await cursor.fetchone()
                
                async with db.execute("""
                    SELECT SUM(p.impressions) as total_impressions, SUM(p.clicks) as total_clicks,
                           SUM(p.revenue) as total_revenue
                    FROM ad_placements_v3 p
                    JOIN channels_v3 c ON p.channel_id = c.channel_id
                    WHERE c.owner_id = ?
                """, (user_id,)) as cursor:
                    placement_stats = await cursor.fetchone()
                
                stats.update({
                    'total_channels': channel_stats[0] or 0,
                    'total_impressions': placement_stats[0] or 0,
                    'total_clicks': placement_stats[1] or 0,
                    'total_revenue': placement_stats[2] or 0
                })
            
            elif user_type == 'affiliate':
                # Get affiliate stats
                async with db.execute("""
                    SELECT COUNT(*) as total_referrals, SUM(amount) as total_commissions
                    FROM commissions_v3 WHERE affiliate_id = ?
                """, (user_id,)) as cursor:
                    affiliate_stats = await cursor.fetchone()
                
                stats.update({
                    'total_referrals': affiliate_stats[0] or 0,
                    'total_commissions': affiliate_stats[1] or 0
                })
            
            return stats

# Global instance
i3lani_v3 = I3laniV3Core()