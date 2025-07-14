"""
Auction-Based Advertising System for I3lani Bot
Implements CPC/CPM bidding, daily auctions, and revenue sharing
"""

import asyncio
import aiosqlite
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import schedule
import time
from decimal import Decimal

logger = logging.getLogger(__name__)

class BidType(Enum):
    """Bid types for advertising"""
    CPC = "CPC"  # Cost Per Click
    CPM = "CPM"  # Cost Per Mille (1000 impressions)

class AdStatus(Enum):
    """Ad status tracking"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class AuctionStatus(Enum):
    """Auction status tracking"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AuctionAd:
    """Auction advertisement data structure"""
    ad_id: int
    advertiser_id: int
    content: str
    image_url: Optional[str]
    category: str
    bid_type: BidType
    bid_amount: float
    daily_budget: float
    target_audience: str
    keywords: List[str]
    status: AdStatus
    created_at: datetime
    updated_at: datetime

@dataclass
class AuctionBid:
    """Auction bid data structure"""
    bid_id: int
    ad_id: int
    channel_id: str
    bid_amount: float
    estimated_reach: int
    quality_score: float
    final_score: float
    won: bool
    created_at: datetime

@dataclass
class AuctionResult:
    """Daily auction results"""
    auction_id: int
    auction_date: datetime
    channel_id: str
    winning_ad_id: int
    winning_bid_amount: float
    estimated_impressions: int
    status: AuctionStatus
    created_at: datetime

@dataclass
class PerformanceMetrics:
    """Ad performance tracking"""
    ad_id: int
    channel_id: str
    date: datetime
    impressions: int
    clicks: int
    ctr: float  # Click-through rate
    revenue: float
    cost: float
    roi: float  # Return on investment

class AuctionAdvertisingSystem:
    """Main auction advertising system"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.min_cpc_bid = 0.10  # $0.10 minimum CPC
        self.min_cpm_bid = 1.00  # $1.00 minimum CPM
        self.revenue_split = {
            "channel_owner": 0.68,  # 68% to channel owner
            "platform": 0.32        # 32% to platform
        }
        self.withdrawal_minimum = 50.00  # $50 minimum withdrawal
        
    async def initialize_database(self):
        """Initialize auction advertising database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Enhanced channels table for auction system
            await db.execute('''
                CREATE TABLE IF NOT EXISTS auction_channels (
                    channel_id TEXT PRIMARY KEY,
                    owner_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    telegram_channel_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subscribers INTEGER DEFAULT 0,
                    avg_engagement_rate REAL DEFAULT 0.0,
                    quality_score REAL DEFAULT 1.0,
                    min_cpc_bid REAL DEFAULT 0.10,
                    min_cpm_bid REAL DEFAULT 1.00,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users (user_id)
                )
            ''')
            
            # Auction advertisements table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS auction_ads (
                    ad_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    advertiser_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    image_url TEXT,
                    category TEXT NOT NULL,
                    bid_type TEXT NOT NULL,
                    bid_amount REAL NOT NULL,
                    daily_budget REAL NOT NULL,
                    target_audience TEXT,
                    keywords TEXT,
                    status TEXT DEFAULT 'draft',
                    clicks INTEGER DEFAULT 0,
                    impressions INTEGER DEFAULT 0,
                    spent_amount REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (advertiser_id) REFERENCES users (user_id)
                )
            ''')
            
            # Daily auctions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS daily_auctions (
                    auction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auction_date DATE NOT NULL,
                    channel_id TEXT NOT NULL,
                    winning_ad_id INTEGER,
                    winning_bid_amount REAL,
                    estimated_impressions INTEGER,
                    actual_impressions INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'scheduled',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (channel_id) REFERENCES auction_channels (channel_id),
                    FOREIGN KEY (winning_ad_id) REFERENCES auction_ads (ad_id)
                )
            ''')
            
            # Auction bids table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS auction_bids (
                    bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auction_id INTEGER NOT NULL,
                    ad_id INTEGER NOT NULL,
                    channel_id TEXT NOT NULL,
                    bid_amount REAL NOT NULL,
                    quality_score REAL DEFAULT 1.0,
                    final_score REAL NOT NULL,
                    won BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (auction_id) REFERENCES daily_auctions (auction_id),
                    FOREIGN KEY (ad_id) REFERENCES auction_ads (ad_id),
                    FOREIGN KEY (channel_id) REFERENCES auction_channels (channel_id)
                )
            ''')
            
            # Performance tracking table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ad_performance (
                    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad_id INTEGER NOT NULL,
                    channel_id TEXT NOT NULL,
                    date DATE NOT NULL,
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    ctr REAL DEFAULT 0.0,
                    revenue REAL DEFAULT 0.0,
                    cost REAL DEFAULT 0.0,
                    roi REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ad_id) REFERENCES auction_ads (ad_id),
                    FOREIGN KEY (channel_id) REFERENCES auction_channels (channel_id)
                )
            ''')
            
            # Revenue tracking and balances
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_balances (
                    user_id INTEGER PRIMARY KEY,
                    balance REAL DEFAULT 0.0,
                    total_earned REAL DEFAULT 0.0,
                    total_withdrawn REAL DEFAULT 0.0,
                    last_withdrawal TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Withdrawal requests
            await db.execute('''
                CREATE TABLE IF NOT EXISTS withdrawal_requests (
                    withdrawal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    payment_details TEXT,
                    status TEXT DEFAULT 'pending',
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Trackable links for CPC ads
            await db.execute('''
                CREATE TABLE IF NOT EXISTS trackable_links (
                    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad_id INTEGER NOT NULL,
                    channel_id TEXT NOT NULL,
                    original_url TEXT NOT NULL,
                    short_url TEXT NOT NULL,
                    clicks INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ad_id) REFERENCES auction_ads (ad_id),
                    FOREIGN KEY (channel_id) REFERENCES auction_channels (channel_id)
                )
            ''')
            
            await db.commit()
            logger.info("✅ Auction advertising system database initialized")
    
    async def create_auction_ad(self, advertiser_id: int, content: str, 
                               image_url: Optional[str], category: str,
                               bid_type: BidType, bid_amount: float,
                               daily_budget: float, target_audience: str = "",
                               keywords: List[str] = None) -> int:
        """Create a new auction advertisement"""
        keywords = keywords or []
        
        # Validate minimum bid amounts
        if bid_type == BidType.CPC and bid_amount < self.min_cpc_bid:
            raise ValueError(f"CPC bid must be at least ${self.min_cpc_bid}")
        elif bid_type == BidType.CPM and bid_amount < self.min_cpm_bid:
            raise ValueError(f"CPM bid must be at least ${self.min_cpm_bid}")
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO auction_ads (
                    advertiser_id, content, image_url, category, bid_type,
                    bid_amount, daily_budget, target_audience, keywords, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (advertiser_id, content, image_url, category, bid_type.value,
                  bid_amount, daily_budget, target_audience, 
                  json.dumps(keywords), AdStatus.PENDING.value))
            
            ad_id = cursor.lastrowid
            await db.commit()
            
            logger.info(f"Created auction ad {ad_id} for advertiser {advertiser_id}")
            return ad_id
    
    async def register_channel(self, owner_id: int, channel_id: str, 
                              name: str, telegram_channel_id: str,
                              category: str, subscribers: int = 0) -> bool:
        """Register a channel for auction advertising"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute('''
                    INSERT INTO auction_channels (
                        channel_id, owner_id, name, telegram_channel_id,
                        category, subscribers, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (channel_id, owner_id, name, telegram_channel_id,
                      category, subscribers, True))
                
                await db.commit()
                logger.info(f"Registered channel {channel_id} for owner {owner_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to register channel {channel_id}: {e}")
                return False
    
    async def run_daily_auction(self, auction_date: datetime = None) -> Dict[str, Any]:
        """Run daily auction for all channels"""
        if auction_date is None:
            auction_date = datetime.now().date()
        
        auction_results = []
        
        async with aiosqlite.connect(self.db_path) as db:
            # Get all active channels
            async with db.execute('''
                SELECT channel_id, category, subscribers, quality_score
                FROM auction_channels WHERE is_active = TRUE
            ''') as cursor:
                channels = await cursor.fetchall()
            
            for channel_id, category, subscribers, quality_score in channels:
                # Get matching ads for this channel's category
                async with db.execute('''
                    SELECT ad_id, advertiser_id, content, image_url, bid_type,
                           bid_amount, daily_budget, spent_amount
                    FROM auction_ads 
                    WHERE category = ? AND status = 'approved' 
                    AND spent_amount < daily_budget
                    ORDER BY bid_amount DESC
                ''', (category,)) as cursor:
                    ads = await cursor.fetchall()
                
                if not ads:
                    continue
                
                # Create auction for this channel
                auction_cursor = await db.execute('''
                    INSERT INTO daily_auctions (
                        auction_date, channel_id, status
                    ) VALUES (?, ?, ?)
                ''', (auction_date, channel_id, AuctionStatus.RUNNING.value))
                
                auction_id = auction_cursor.lastrowid
                
                # Process bids for each ad
                winning_ad = None
                winning_bid = 0.0
                
                for ad in ads:
                    ad_id, advertiser_id, content, image_url, bid_type, bid_amount, daily_budget, spent_amount = ad
                    
                    # Calculate quality score and final bid score
                    quality_score = await self._calculate_ad_quality_score(ad_id, channel_id)
                    final_score = bid_amount * quality_score
                    
                    # Record bid
                    await db.execute('''
                        INSERT INTO auction_bids (
                            auction_id, ad_id, channel_id, bid_amount,
                            quality_score, final_score
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (auction_id, ad_id, channel_id, bid_amount,
                          quality_score, final_score))
                    
                    # Check if this is the winning bid
                    if final_score > winning_bid:
                        winning_ad = ad
                        winning_bid = final_score
                
                # Update auction with winner
                if winning_ad:
                    estimated_impressions = int(subscribers * 0.1)  # 10% reach estimate
                    
                    await db.execute('''
                        UPDATE daily_auctions 
                        SET winning_ad_id = ?, winning_bid_amount = ?,
                            estimated_impressions = ?, status = ?
                        WHERE auction_id = ?
                    ''', (winning_ad[0], winning_ad[5], estimated_impressions,
                          AuctionStatus.COMPLETED.value, auction_id))
                    
                    # Mark winning bid
                    await db.execute('''
                        UPDATE auction_bids SET won = TRUE 
                        WHERE auction_id = ? AND ad_id = ?
                    ''', (auction_id, winning_ad[0]))
                    
                    auction_results.append({
                        'auction_id': auction_id,
                        'channel_id': channel_id,
                        'winning_ad_id': winning_ad[0],
                        'winning_bid_amount': winning_ad[5],
                        'estimated_impressions': estimated_impressions
                    })
                
                await db.commit()
        
        logger.info(f"Daily auction completed for {len(auction_results)} channels")
        return {
            'auction_date': auction_date,
            'results': auction_results,
            'total_auctions': len(auction_results)
        }
    
    async def _calculate_ad_quality_score(self, ad_id: int, channel_id: str) -> float:
        """Calculate quality score for ad-channel combination"""
        # Basic quality score implementation
        # In production, this would consider:
        # - Ad engagement history
        # - Channel-ad relevance
        # - Advertiser reputation
        # - Content quality metrics
        
        base_score = 1.0
        
        async with aiosqlite.connect(self.db_path) as db:
            # Check historical performance
            async with db.execute('''
                SELECT AVG(ctr) FROM ad_performance 
                WHERE ad_id = ? AND channel_id = ?
            ''', (ad_id, channel_id)) as cursor:
                result = await cursor.fetchone()
                if result and result[0]:
                    ctr_bonus = min(result[0] * 10, 0.5)  # CTR bonus up to 0.5
                    base_score += ctr_bonus
        
        return min(base_score, 2.0)  # Cap at 2.0
    
    async def create_trackable_link(self, ad_id: int, channel_id: str, 
                                   original_url: str) -> str:
        """Create trackable link for CPC ads"""
        # In production, integrate with Bitly or similar service
        short_url = f"https://i3l.ai/c/{ad_id}_{channel_id}"
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO trackable_links (
                    ad_id, channel_id, original_url, short_url
                ) VALUES (?, ?, ?, ?)
            ''', (ad_id, channel_id, original_url, short_url))
            
            await db.commit()
        
        return short_url
    
    async def track_click(self, link_id: int) -> bool:
        """Track click on CPC ad"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE trackable_links 
                SET clicks = clicks + 1
                WHERE link_id = ?
            ''', (link_id,))
            
            await db.commit()
            return True
    
    async def update_performance_metrics(self, ad_id: int, channel_id: str,
                                        impressions: int, clicks: int) -> bool:
        """Update ad performance metrics"""
        today = datetime.now().date()
        ctr = (clicks / impressions) if impressions > 0 else 0.0
        
        async with aiosqlite.connect(self.db_path) as db:
            # Get ad details for revenue calculation
            async with db.execute('''
                SELECT bid_type, bid_amount FROM auction_ads WHERE ad_id = ?
            ''', (ad_id,)) as cursor:
                ad_data = await cursor.fetchone()
            
            if not ad_data:
                return False
            
            bid_type, bid_amount = ad_data
            
            # Calculate revenue
            if bid_type == 'CPC':
                revenue = clicks * bid_amount
            else:  # CPM
                revenue = (impressions / 1000) * bid_amount
            
            # Update or insert performance record
            await db.execute('''
                INSERT OR REPLACE INTO ad_performance (
                    ad_id, channel_id, date, impressions, clicks, ctr, revenue, cost
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ad_id, channel_id, today, impressions, clicks, ctr, revenue, revenue))
            
            await db.commit()
            
            # Update channel owner balance
            await self._update_channel_owner_balance(channel_id, revenue)
            
            return True
    
    async def _update_channel_owner_balance(self, channel_id: str, revenue: float):
        """Update channel owner balance with revenue share"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get channel owner
            async with db.execute('''
                SELECT owner_id FROM auction_channels WHERE channel_id = ?
            ''', (channel_id,)) as cursor:
                result = await cursor.fetchone()
            
            if not result:
                return
            
            owner_id = result[0]
            owner_share = revenue * self.revenue_split["channel_owner"]
            
            # Update balance
            await db.execute('''
                INSERT OR REPLACE INTO user_balances (
                    user_id, balance, total_earned, updated_at
                ) VALUES (
                    ?, 
                    COALESCE((SELECT balance FROM user_balances WHERE user_id = ?), 0) + ?,
                    COALESCE((SELECT total_earned FROM user_balances WHERE user_id = ?), 0) + ?,
                    ?
                )
            ''', (owner_id, owner_id, owner_share, owner_id, owner_share, datetime.now()))
            
            await db.commit()
    
    async def get_advertiser_stats(self, advertiser_id: int) -> Dict[str, Any]:
        """Get advertiser performance statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get ad performance summary
            async with db.execute('''
                SELECT 
                    COUNT(*) as total_ads,
                    SUM(impressions) as total_impressions,
                    SUM(clicks) as total_clicks,
                    AVG(ctr) as avg_ctr,
                    SUM(cost) as total_spent
                FROM ad_performance p
                JOIN auction_ads a ON p.ad_id = a.ad_id
                WHERE a.advertiser_id = ?
            ''', (advertiser_id,)) as cursor:
                stats = await cursor.fetchone()
            
            return {
                'total_ads': stats[0] or 0,
                'total_impressions': stats[1] or 0,
                'total_clicks': stats[2] or 0,
                'avg_ctr': stats[3] or 0.0,
                'total_spent': stats[4] or 0.0
            }
    
    async def get_channel_owner_stats(self, owner_id: int) -> Dict[str, Any]:
        """Get channel owner earnings statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get balance
            async with db.execute('''
                SELECT balance, total_earned, total_withdrawn
                FROM user_balances WHERE user_id = ?
            ''', (owner_id,)) as cursor:
                balance_data = await cursor.fetchone()
            
            if not balance_data:
                return {
                    'balance': 0.0,
                    'total_earned': 0.0,
                    'total_withdrawn': 0.0,
                    'can_withdraw': False
                }
            
            balance, total_earned, total_withdrawn = balance_data
            
            return {
                'balance': balance,
                'total_earned': total_earned,
                'total_withdrawn': total_withdrawn or 0.0,
                'can_withdraw': balance >= self.withdrawal_minimum
            }
    
    async def request_withdrawal(self, user_id: int, amount: float,
                                payment_method: str, payment_details: str) -> bool:
        """Request withdrawal for channel owner"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check balance
            async with db.execute('''
                SELECT balance FROM user_balances WHERE user_id = ?
            ''', (user_id,)) as cursor:
                result = await cursor.fetchone()
            
            if not result or result[0] < amount or amount < self.withdrawal_minimum:
                return False
            
            # Create withdrawal request
            await db.execute('''
                INSERT INTO withdrawal_requests (
                    user_id, amount, payment_method, payment_details
                ) VALUES (?, ?, ?, ?)
            ''', (user_id, amount, payment_method, payment_details))
            
            await db.commit()
            return True

# Global instance
auction_system = AuctionAdvertisingSystem()

async def initialize_auction_system():
    """Initialize the auction advertising system"""
    await auction_system.initialize_database()
    logger.info("✅ Auction advertising system initialized")

def get_auction_system() -> AuctionAdvertisingSystem:
    """Get the global auction system instance"""
    return auction_system