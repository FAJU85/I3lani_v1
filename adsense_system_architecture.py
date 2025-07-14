"""
AdSense-Like System Architecture for I3lani Bot
Implements auction-based pricing, revenue sharing, and ad performance tracking
"""

import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import json
import aiosqlite
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AdPlacement:
    """Represents an ad placement opportunity"""
    channel_id: str
    channel_name: str
    category: str
    subscribers: int
    avg_engagement: float
    suggested_cpc: Decimal
    suggested_cpm: Decimal
    owner_id: int
    available_slots: int

@dataclass
class AdBid:
    """Represents a bid for an ad placement"""
    advertiser_id: int
    channel_id: str
    bid_amount: Decimal
    bid_type: str  # 'cpc' or 'cpm'
    duration_hours: int
    content: str
    media_url: Optional[str]
    target_clicks: Optional[int]
    target_impressions: Optional[int]
    max_budget: Decimal
    created_at: datetime

@dataclass
class AdPerformance:
    """Tracks ad performance metrics"""
    ad_id: str
    channel_id: str
    impressions: int
    clicks: int
    ctr: float
    cost_per_click: Decimal
    cost_per_impression: Decimal
    revenue_generated: Decimal
    channel_owner_share: Decimal
    platform_share: Decimal

class AdSenseSystem:
    """
    Main AdSense-like system for auction-based ad placements
    """
    
    def __init__(self, database_path: str = "ads.db"):
        self.db_path = database_path
        self.revenue_split = {
            'channel_owner': Decimal('0.68'),  # 68% to channel owners
            'platform': Decimal('0.32')        # 32% to platform
        }
        self.currency_rates = {
            'stars_to_usd': Decimal('0.038'),  # $0.038 per Star
            'ton_to_usd': Decimal('7.50'),     # $7.50 per TON (adjustable)
            'usd_to_ton': Decimal('0.133')     # 1 USD = 0.133 TON
        }
    
    async def initialize_database(self):
        """Initialize the AdSense database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Enhanced channels table with performance metrics
            await db.execute('''
                CREATE TABLE IF NOT EXISTS adsense_channels (
                    channel_id TEXT PRIMARY KEY,
                    owner_id INTEGER NOT NULL,
                    channel_name TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    subscribers INTEGER DEFAULT 0,
                    avg_engagement REAL DEFAULT 0.0,
                    total_impressions INTEGER DEFAULT 0,
                    total_clicks INTEGER DEFAULT 0,
                    total_revenue REAL DEFAULT 0.0,
                    suggested_cpc REAL DEFAULT 0.05,
                    suggested_cpm REAL DEFAULT 2.00,
                    available_slots INTEGER DEFAULT 10,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Ad bids table for auction system
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ad_bids (
                    bid_id TEXT PRIMARY KEY,
                    advertiser_id INTEGER NOT NULL,
                    channel_id TEXT NOT NULL,
                    bid_amount REAL NOT NULL,
                    bid_type TEXT NOT NULL CHECK (bid_type IN ('cpc', 'cpm')),
                    duration_hours INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    media_url TEXT,
                    target_clicks INTEGER,
                    target_impressions INTEGER,
                    max_budget REAL NOT NULL,
                    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'cancelled')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (channel_id) REFERENCES adsense_channels (channel_id)
                )
            ''')
            
            # Ad performance tracking
            await db.execute('''
                CREATE TABLE IF NOT EXISTS ad_performance (
                    ad_id TEXT PRIMARY KEY,
                    bid_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    ctr REAL DEFAULT 0.0,
                    cost_per_click REAL DEFAULT 0.0,
                    cost_per_impression REAL DEFAULT 0.0,
                    revenue_generated REAL DEFAULT 0.0,
                    channel_owner_share REAL DEFAULT 0.0,
                    platform_share REAL DEFAULT 0.0,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bid_id) REFERENCES ad_bids (bid_id),
                    FOREIGN KEY (channel_id) REFERENCES adsense_channels (channel_id)
                )
            ''')
            
            # Revenue sharing tracking
            await db.execute('''
                CREATE TABLE IF NOT EXISTS revenue_sharing (
                    payment_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    owner_id INTEGER NOT NULL,
                    ad_id TEXT NOT NULL,
                    total_revenue REAL NOT NULL,
                    owner_share REAL NOT NULL,
                    platform_share REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed')),
                    payment_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    FOREIGN KEY (channel_id) REFERENCES adsense_channels (channel_id),
                    FOREIGN KEY (ad_id) REFERENCES ad_performance (ad_id)
                )
            ''')
            
            # Auction results tracking
            await db.execute('''
                CREATE TABLE IF NOT EXISTS auction_results (
                    auction_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    winning_bid_id TEXT NOT NULL,
                    winning_amount REAL NOT NULL,
                    total_bids INTEGER NOT NULL,
                    avg_bid_amount REAL NOT NULL,
                    auction_end_time TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (channel_id) REFERENCES adsense_channels (channel_id),
                    FOREIGN KEY (winning_bid_id) REFERENCES ad_bids (bid_id)
                )
            ''')
            
            await db.commit()
            logger.info("✅ AdSense database schema initialized")
    
    async def register_channel(self, channel_id: str, owner_id: int, channel_name: str, 
                              category: str = 'general', subscribers: int = 0) -> bool:
        """Register a new channel in the AdSense system"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Calculate suggested pricing based on subscribers and category
                suggested_cpc, suggested_cpm = self._calculate_suggested_pricing(subscribers, category)
                
                await db.execute('''
                    INSERT OR REPLACE INTO adsense_channels 
                    (channel_id, owner_id, channel_name, category, subscribers, 
                     suggested_cpc, suggested_cpm, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (channel_id, owner_id, channel_name, category, subscribers,
                      float(suggested_cpc), float(suggested_cpm), datetime.now()))
                
                await db.commit()
                logger.info(f"✅ Channel {channel_name} registered in AdSense system")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error registering channel: {e}")
            return False
    
    def _calculate_suggested_pricing(self, subscribers: int, category: str) -> Tuple[Decimal, Decimal]:
        """Calculate suggested CPC and CPM based on channel metrics"""
        # Base pricing tiers
        base_cpc = Decimal('0.05')  # $0.05 base CPC
        base_cpm = Decimal('2.00')  # $2.00 base CPM
        
        # Subscriber multipliers
        if subscribers >= 100000:
            subscriber_multiplier = Decimal('3.0')
        elif subscribers >= 50000:
            subscriber_multiplier = Decimal('2.5')
        elif subscribers >= 10000:
            subscriber_multiplier = Decimal('2.0')
        elif subscribers >= 5000:
            subscriber_multiplier = Decimal('1.5')
        elif subscribers >= 1000:
            subscriber_multiplier = Decimal('1.2')
        else:
            subscriber_multiplier = Decimal('1.0')
        
        # Category multipliers
        category_multipliers = {
            'crypto': Decimal('1.8'),
            'finance': Decimal('1.6'),
            'technology': Decimal('1.4'),
            'business': Decimal('1.3'),
            'shopping': Decimal('1.2'),
            'entertainment': Decimal('1.0'),
            'general': Decimal('1.0')
        }
        
        category_multiplier = category_multipliers.get(category.lower(), Decimal('1.0'))
        
        suggested_cpc = base_cpc * subscriber_multiplier * category_multiplier
        suggested_cpm = base_cpm * subscriber_multiplier * category_multiplier
        
        return suggested_cpc, suggested_cpm
    
    async def get_available_channels(self, category: str = None) -> List[AdPlacement]:
        """Get list of available channels for ad placement"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = '''
                    SELECT channel_id, channel_name, category, subscribers, 
                           avg_engagement, suggested_cpc, suggested_cpm, 
                           owner_id, available_slots
                    FROM adsense_channels 
                    WHERE is_active = 1 AND available_slots > 0
                '''
                params = []
                
                if category:
                    query += ' AND category = ?'
                    params.append(category)
                
                query += ' ORDER BY subscribers DESC, avg_engagement DESC'
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                    return [
                        AdPlacement(
                            channel_id=row[0],
                            channel_name=row[1],
                            category=row[2],
                            subscribers=row[3],
                            avg_engagement=row[4],
                            suggested_cpc=Decimal(str(row[5])),
                            suggested_cpm=Decimal(str(row[6])),
                            owner_id=row[7],
                            available_slots=row[8]
                        )
                        for row in rows
                    ]
                    
        except Exception as e:
            logger.error(f"❌ Error getting available channels: {e}")
            return []
    
    async def place_bid(self, bid: AdBid) -> str:
        """Place a bid for an ad placement"""
        try:
            bid_id = f"BID-{datetime.now().strftime('%Y%m%d')}-{bid.advertiser_id}-{hash(bid.channel_id) % 10000:04d}"
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO ad_bids 
                    (bid_id, advertiser_id, channel_id, bid_amount, bid_type, 
                     duration_hours, content, media_url, target_clicks, 
                     target_impressions, max_budget, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (bid_id, bid.advertiser_id, bid.channel_id, 
                      float(bid.bid_amount), bid.bid_type, bid.duration_hours,
                      bid.content, bid.media_url, bid.target_clicks,
                      bid.target_impressions, float(bid.max_budget), datetime.now()))
                
                await db.commit()
                logger.info(f"✅ Bid {bid_id} placed successfully")
                return bid_id
                
        except Exception as e:
            logger.error(f"❌ Error placing bid: {e}")
            raise
    
    async def run_auction(self, channel_id: str) -> Optional[str]:
        """Run auction for a specific channel and return winning bid ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get all pending bids for this channel
                async with db.execute('''
                    SELECT bid_id, advertiser_id, bid_amount, bid_type, max_budget
                    FROM ad_bids 
                    WHERE channel_id = ? AND status = 'pending'
                    ORDER BY bid_amount DESC
                ''', (channel_id,)) as cursor:
                    bids = await cursor.fetchall()
                
                if not bids:
                    return None
                
                # Select winning bid (highest bid)
                winning_bid = bids[0]
                winning_bid_id = winning_bid[0]
                winning_amount = winning_bid[2]
                
                # Update winning bid status
                await db.execute('''
                    UPDATE ad_bids 
                    SET status = 'active' 
                    WHERE bid_id = ?
                ''', (winning_bid_id,))
                
                # Cancel other bids
                for bid in bids[1:]:
                    await db.execute('''
                        UPDATE ad_bids 
                        SET status = 'cancelled' 
                        WHERE bid_id = ?
                    ''', (bid[0],))
                
                # Record auction result
                auction_id = f"AUC-{datetime.now().strftime('%Y%m%d')}-{hash(channel_id) % 10000:04d}"
                avg_bid = sum(bid[2] for bid in bids) / len(bids)
                
                await db.execute('''
                    INSERT INTO auction_results 
                    (auction_id, channel_id, winning_bid_id, winning_amount, 
                     total_bids, avg_bid_amount, auction_end_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (auction_id, channel_id, winning_bid_id, winning_amount,
                      len(bids), avg_bid, datetime.now()))
                
                await db.commit()
                logger.info(f"✅ Auction completed for {channel_id}, winner: {winning_bid_id}")
                return winning_bid_id
                
        except Exception as e:
            logger.error(f"❌ Error running auction: {e}")
            return None
    
    async def track_ad_performance(self, ad_id: str, impressions: int = 0, clicks: int = 0) -> bool:
        """Track ad performance and update metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get current performance
                async with db.execute('''
                    SELECT impressions, clicks, revenue_generated 
                    FROM ad_performance 
                    WHERE ad_id = ?
                ''', (ad_id,)) as cursor:
                    current = await cursor.fetchone()
                
                if current:
                    new_impressions = current[0] + impressions
                    new_clicks = current[1] + clicks
                    ctr = (new_clicks / new_impressions * 100) if new_impressions > 0 else 0
                    
                    await db.execute('''
                        UPDATE ad_performance 
                        SET impressions = ?, clicks = ?, ctr = ?
                        WHERE ad_id = ?
                    ''', (new_impressions, new_clicks, ctr, ad_id))
                    
                    await db.commit()
                    logger.info(f"✅ Performance updated for ad {ad_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Error tracking performance: {e}")
            return False
    
    async def calculate_revenue_share(self, ad_id: str) -> Dict:
        """Calculate revenue share for channel owner and platform"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT ap.revenue_generated, ap.channel_id, ac.owner_id
                    FROM ad_performance ap
                    JOIN adsense_channels ac ON ap.channel_id = ac.channel_id
                    WHERE ap.ad_id = ?
                ''', (ad_id,)) as cursor:
                    result = await cursor.fetchone()
                
                if result:
                    total_revenue = Decimal(str(result[0]))
                    channel_id = result[1]
                    owner_id = result[2]
                    
                    owner_share = total_revenue * self.revenue_split['channel_owner']
                    platform_share = total_revenue * self.revenue_split['platform']
                    
                    return {
                        'total_revenue': total_revenue,
                        'owner_share': owner_share,
                        'platform_share': platform_share,
                        'channel_id': channel_id,
                        'owner_id': owner_id
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error calculating revenue share: {e}")
            return {}

# Global instance
adsense_system = AdSenseSystem()