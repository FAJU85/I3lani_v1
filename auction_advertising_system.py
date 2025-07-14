"""
Auction-Based Advertising System for I3lani Bot
Complete implementation with channel categorization, CPC/CPM bidding, and revenue sharing
"""

import asyncio
import logging
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import requests
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BidType(Enum):
    CPC = "cpc"  # Cost Per Click
    CPM = "cpm"  # Cost Per Mille (1000 impressions)

class AdStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"

class ChannelCategory(Enum):
    TECH = "tech"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    SHOPPING = "shopping"
    CRYPTO = "crypto"
    HEALTH = "health"
    TRAVEL = "travel"
    FOOD = "food"
    GENERAL = "general"

@dataclass
class AdBid:
    ad_id: str
    advertiser_id: int
    content: str
    image_url: Optional[str]
    category: ChannelCategory
    bid_type: BidType
    bid_amount: Decimal
    created_at: datetime
    status: AdStatus = AdStatus.PENDING

@dataclass
class ChannelData:
    channel_id: str
    owner_id: int
    category: ChannelCategory
    subscribers: int
    active_subscribers: int
    is_verified: bool = False
    created_at: datetime = None

@dataclass
class AuctionResult:
    auction_id: str
    channel_id: str
    ad_id: str
    winning_bid: Decimal
    scheduled_date: datetime
    created_at: datetime

class AuctionAdvertisingSystem:
    def __init__(self, database_path: str = "ads.db"):
        self.db_path = database_path
        self.bitly_api_key = None  # Will be set via secrets
        self.min_cpc_bid = Decimal("0.10")
        self.min_cpm_bid = Decimal("1.00")
        self.revenue_share_channel = Decimal("0.68")  # 68% to channel owner
        self.revenue_share_platform = Decimal("0.32")  # 32% to platform
        self.withdrawal_minimum = Decimal("50.00")  # $50 minimum withdrawal
        
    async def initialize_database(self):
        """Initialize all required database tables"""
        async with self.get_db_connection() as db:
            await db.executescript("""
                -- Channels table with categorization
                CREATE TABLE IF NOT EXISTS auction_channels (
                    channel_id TEXT PRIMARY KEY,
                    owner_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subscribers INTEGER DEFAULT 0,
                    active_subscribers INTEGER DEFAULT 0,
                    is_verified BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Ads table with bidding system
                CREATE TABLE IF NOT EXISTS auction_ads (
                    ad_id TEXT PRIMARY KEY,
                    advertiser_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    image_url TEXT,
                    category TEXT NOT NULL,
                    bid_type TEXT NOT NULL,
                    bid_amount DECIMAL(10,2) NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Auction results table
                CREATE TABLE IF NOT EXISTS auction_results (
                    auction_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    ad_id TEXT NOT NULL,
                    winning_bid DECIMAL(10,2) NOT NULL,
                    scheduled_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (channel_id) REFERENCES auction_channels(channel_id),
                    FOREIGN KEY (ad_id) REFERENCES auction_ads(ad_id)
                );
                
                -- Performance tracking table
                CREATE TABLE IF NOT EXISTS ad_performance (
                    ad_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    revenue DECIMAL(10,2) DEFAULT 0,
                    tracking_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (ad_id, channel_id),
                    FOREIGN KEY (ad_id) REFERENCES auction_ads(ad_id),
                    FOREIGN KEY (channel_id) REFERENCES auction_channels(channel_id)
                );
                
                -- Revenue and balances table
                CREATE TABLE IF NOT EXISTS user_balances (
                    user_id INTEGER PRIMARY KEY,
                    balance DECIMAL(10,2) DEFAULT 0,
                    total_earned DECIMAL(10,2) DEFAULT 0,
                    total_withdrawn DECIMAL(10,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Earnings breakdown table
                CREATE TABLE IF NOT EXISTS earnings_log (
                    log_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    ad_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    revenue_type TEXT NOT NULL, -- 'cpc' or 'cpm'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_balances(user_id),
                    FOREIGN KEY (ad_id) REFERENCES auction_ads(ad_id),
                    FOREIGN KEY (channel_id) REFERENCES auction_channels(channel_id)
                );
                
                -- Withdrawal requests table
                CREATE TABLE IF NOT EXISTS withdrawal_requests (
                    request_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_method TEXT NOT NULL, -- 'ton' or 'stars'
                    wallet_address TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_balances(user_id)
                );
                
                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_auction_channels_category ON auction_channels(category);
                CREATE INDEX IF NOT EXISTS idx_auction_ads_category ON auction_ads(category);
                CREATE INDEX IF NOT EXISTS idx_auction_ads_status ON auction_ads(status);
                CREATE INDEX IF NOT EXISTS idx_ad_performance_ad_id ON ad_performance(ad_id);
                CREATE INDEX IF NOT EXISTS idx_earnings_log_user_id ON earnings_log(user_id);
            """)
            await db.commit()
            logger.info("✅ Auction advertising system database initialized")
    
    def get_db_connection(self):
        """Get database connection with proper setup"""
        import aiosqlite
        return aiosqlite.connect(self.db_path)
    
    async def add_channel(self, channel_id: str, owner_id: int, category: ChannelCategory, subscribers: int = 0) -> bool:
        """Add a new channel to the auction system"""
        try:
            async with self.get_db_connection() as db:
                await db.execute("""
                    INSERT OR REPLACE INTO auction_channels 
                    (channel_id, owner_id, category, subscribers, active_subscribers, is_verified)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (channel_id, owner_id, category.value, subscribers, int(subscribers * 0.45), True))
                await db.commit()
                logger.info(f"✅ Channel {channel_id} added to auction system with category: {category.value}")
                return True
        except Exception as e:
            logger.error(f"❌ Error adding channel to auction system: {e}")
            return False
    
    async def create_ad(self, advertiser_id: int, content: str, image_url: Optional[str], 
                       category: ChannelCategory, bid_type: BidType, bid_amount: Decimal) -> Optional[str]:
        """Create a new ad with bidding information"""
        try:
            # Validate bid amount
            if bid_type == BidType.CPC and bid_amount < self.min_cpc_bid:
                logger.warning(f"CPC bid too low: {bid_amount} < {self.min_cpc_bid}")
                return None
            elif bid_type == BidType.CPM and bid_amount < self.min_cpm_bid:
                logger.warning(f"CPM bid too low: {bid_amount} < {self.min_cpm_bid}")
                return None
            
            # Generate ad ID
            ad_id = f"AD-{datetime.now().strftime('%Y%m%d')}-{advertiser_id}-{int(datetime.now().timestamp() * 1000) % 10000}"
            
            async with self.get_db_connection() as db:
                await db.execute("""
                    INSERT INTO auction_ads 
                    (ad_id, advertiser_id, content, image_url, category, bid_type, bid_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (ad_id, advertiser_id, content, image_url, category.value, bid_type.value, float(bid_amount), AdStatus.PENDING.value))
                await db.commit()
                logger.info(f"✅ Ad {ad_id} created with {bid_type.value} bid: ${bid_amount}")
                return ad_id
        except Exception as e:
            logger.error(f"❌ Error creating ad: {e}")
            return None
    
    async def get_channels_by_category(self, category: ChannelCategory) -> List[ChannelData]:
        """Get all verified channels in a specific category"""
        try:
            async with self.get_db_connection() as db:
                async with db.execute("""
                    SELECT channel_id, owner_id, category, subscribers, active_subscribers, is_verified, created_at
                    FROM auction_channels 
                    WHERE category = ? AND is_verified = 1
                    ORDER BY subscribers DESC
                """, (category.value,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    channels = []
                    for row in rows:
                        channels.append(ChannelData(
                            channel_id=row[0],
                            owner_id=row[1],
                            category=ChannelCategory(row[2]),
                            subscribers=row[3],
                            active_subscribers=row[4],
                            is_verified=bool(row[5]),
                            created_at=datetime.fromisoformat(row[6]) if row[6] else None
                        ))
                    
                    return channels
        except Exception as e:
            logger.error(f"❌ Error getting channels by category: {e}")
            return []
    
    async def get_pending_ads_by_category(self, category: ChannelCategory) -> List[AdBid]:
        """Get all approved ads in a specific category"""
        try:
            async with self.get_db_connection() as db:
                async with db.execute("""
                    SELECT ad_id, advertiser_id, content, image_url, category, bid_type, bid_amount, created_at, status
                    FROM auction_ads 
                    WHERE category = ? AND status = 'approved'
                    ORDER BY bid_amount DESC
                """, (category.value,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    ads = []
                    for row in rows:
                        ads.append(AdBid(
                            ad_id=row[0],
                            advertiser_id=row[1],
                            content=row[2],
                            image_url=row[3],
                            category=ChannelCategory(row[4]),
                            bid_type=BidType(row[5]),
                            bid_amount=Decimal(str(row[6])),
                            created_at=datetime.fromisoformat(row[7]),
                            status=AdStatus(row[8])
                        ))
                    
                    return ads
        except Exception as e:
            logger.error(f"❌ Error getting pending ads: {e}")
            return []
    
    async def run_daily_auction(self) -> Dict[str, List[AuctionResult]]:
        """Run daily auction to match ads with channels"""
        try:
            auction_results = {}
            
            # Process each category
            for category in ChannelCategory:
                logger.info(f"🎯 Running auction for category: {category.value}")
                
                # Get channels and ads for this category
                channels = await self.get_channels_by_category(category)
                ads = await self.get_pending_ads_by_category(category)
                
                if not channels or not ads:
                    logger.info(f"⏭️ No channels or ads for category {category.value}")
                    continue
                
                # Match highest bidding ads to channels
                category_results = []
                for i, channel in enumerate(channels):
                    if i < len(ads):  # Match available ads to channels
                        ad = ads[i]  # Highest bidder for this channel
                        
                        # Create auction result
                        auction_id = f"AUCTION-{datetime.now().strftime('%Y%m%d')}-{channel.channel_id}-{ad.ad_id}"
                        scheduled_date = datetime.now() + timedelta(hours=1)  # Schedule for 1 hour from now
                        
                        result = AuctionResult(
                            auction_id=auction_id,
                            channel_id=channel.channel_id,
                            ad_id=ad.ad_id,
                            winning_bid=ad.bid_amount,
                            scheduled_date=scheduled_date,
                            created_at=datetime.now()
                        )
                        
                        # Store result in database
                        await self.store_auction_result(result)
                        category_results.append(result)
                        
                        # Update ad status to scheduled
                        await self.update_ad_status(ad.ad_id, AdStatus.SCHEDULED)
                        
                        logger.info(f"✅ Matched ad {ad.ad_id} (${ad.bid_amount}) to channel {channel.channel_id}")
                
                auction_results[category.value] = category_results
            
            return auction_results
            
        except Exception as e:
            logger.error(f"❌ Error running daily auction: {e}")
            return {}
    
    async def store_auction_result(self, result: AuctionResult):
        """Store auction result in database"""
        try:
            async with self.get_db_connection() as db:
                await db.execute("""
                    INSERT INTO auction_results 
                    (auction_id, channel_id, ad_id, winning_bid, scheduled_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (result.auction_id, result.channel_id, result.ad_id, 
                     float(result.winning_bid), result.scheduled_date.isoformat()))
                await db.commit()
        except Exception as e:
            logger.error(f"❌ Error storing auction result: {e}")
    
    async def update_ad_status(self, ad_id: str, status: AdStatus):
        """Update ad status"""
        try:
            async with self.get_db_connection() as db:
                await db.execute("""
                    UPDATE auction_ads 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE ad_id = ?
                """, (status.value, ad_id))
                await db.commit()
        except Exception as e:
            logger.error(f"❌ Error updating ad status: {e}")
    
    async def create_tracking_url(self, ad_id: str, original_url: str) -> str:
        """Create trackable URL using Bitly API"""
        try:
            if not self.bitly_api_key:
                logger.warning("⚠️ Bitly API key not configured, using direct URL")
                return original_url
            
            headers = {
                'Authorization': f'Bearer {self.bitly_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'long_url': original_url,
                'title': f'I3lani Ad {ad_id}'
            }
            
            response = requests.post('https://api-ssl.bitly.com/v4/shorten', 
                                   headers=headers, json=data)
            
            if response.status_code == 200:
                short_url = response.json()['link']
                logger.info(f"✅ Created tracking URL for ad {ad_id}: {short_url}")
                return short_url
            else:
                logger.error(f"❌ Bitly API error: {response.status_code}")
                return original_url
                
        except Exception as e:
            logger.error(f"❌ Error creating tracking URL: {e}")
            return original_url
    
    async def track_impression(self, ad_id: str, channel_id: str):
        """Track ad impression"""
        try:
            async with self.get_db_connection() as db:
                await db.execute("""
                    INSERT OR IGNORE INTO ad_performance 
                    (ad_id, channel_id, impressions, clicks, revenue)
                    VALUES (?, ?, 1, 0, 0)
                """, (ad_id, channel_id))
                
                await db.execute("""
                    UPDATE ad_performance 
                    SET impressions = impressions + 1
                    WHERE ad_id = ? AND channel_id = ?
                """, (ad_id, channel_id))
                
                await db.commit()
                logger.debug(f"📊 Tracked impression for ad {ad_id} in channel {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking impression: {e}")
    
    async def track_click(self, ad_id: str, channel_id: str):
        """Track ad click and calculate revenue"""
        try:
            async with self.get_db_connection() as db:
                # Update click count
                await db.execute("""
                    UPDATE ad_performance 
                    SET clicks = clicks + 1
                    WHERE ad_id = ? AND channel_id = ?
                """, (ad_id, channel_id))
                
                # Get ad details for revenue calculation
                async with db.execute("""
                    SELECT bid_type, bid_amount FROM auction_ads WHERE ad_id = ?
                """, (ad_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        bid_type, bid_amount = row[0], Decimal(str(row[1]))
                        
                        # Calculate revenue for CPC
                        if bid_type == 'cpc':
                            await self.calculate_and_distribute_revenue(ad_id, channel_id, bid_amount, 'cpc')
                
                await db.commit()
                logger.info(f"💰 Tracked click for ad {ad_id} in channel {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error tracking click: {e}")
    
    async def calculate_and_distribute_revenue(self, ad_id: str, channel_id: str, amount: Decimal, revenue_type: str):
        """Calculate and distribute revenue between channel owner and platform"""
        try:
            # Get channel owner
            async with self.get_db_connection() as db:
                async with db.execute("""
                    SELECT owner_id FROM auction_channels WHERE channel_id = ?
                """, (channel_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        logger.error(f"❌ Channel {channel_id} not found")
                        return
                    
                    owner_id = row[0]
                
                # Calculate revenue shares
                channel_revenue = amount * self.revenue_share_channel
                platform_revenue = amount * self.revenue_share_platform
                
                # Update channel owner balance
                await db.execute("""
                    INSERT OR IGNORE INTO user_balances (user_id, balance, total_earned)
                    VALUES (?, 0, 0)
                """, (owner_id,))
                
                await db.execute("""
                    UPDATE user_balances 
                    SET balance = balance + ?, total_earned = total_earned + ?
                    WHERE user_id = ?
                """, (float(channel_revenue), float(channel_revenue), owner_id))
                
                # Log earning
                log_id = f"EARN-{datetime.now().strftime('%Y%m%d')}-{owner_id}-{int(datetime.now().timestamp() * 1000) % 10000}"
                await db.execute("""
                    INSERT INTO earnings_log (log_id, user_id, ad_id, channel_id, amount, revenue_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (log_id, owner_id, ad_id, channel_id, float(channel_revenue), revenue_type))
                
                await db.commit()
                logger.info(f"💰 Distributed revenue: ${channel_revenue} to owner {owner_id}, ${platform_revenue} to platform")
                
        except Exception as e:
            logger.error(f"❌ Error calculating revenue: {e}")
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics (for channel owners)"""
        try:
            async with self.get_db_connection() as db:
                # Get balance info
                async with db.execute("""
                    SELECT balance, total_earned, total_withdrawn FROM user_balances WHERE user_id = ?
                """, (user_id,)) as cursor:
                    balance_row = await cursor.fetchone()
                    
                    if not balance_row:
                        return {"balance": 0, "total_earned": 0, "total_withdrawn": 0, "channels": [], "recent_earnings": []}
                
                # Get user's channels
                async with db.execute("""
                    SELECT channel_id, category, subscribers FROM auction_channels WHERE owner_id = ?
                """, (user_id,)) as cursor:
                    channels = await cursor.fetchall()
                
                # Get recent earnings
                async with db.execute("""
                    SELECT ad_id, channel_id, amount, revenue_type, created_at 
                    FROM earnings_log WHERE user_id = ? ORDER BY created_at DESC LIMIT 10
                """, (user_id,)) as cursor:
                    earnings = await cursor.fetchall()
                
                return {
                    "balance": balance_row[0],
                    "total_earned": balance_row[1],
                    "total_withdrawn": balance_row[2],
                    "channels": [{"channel_id": ch[0], "category": ch[1], "subscribers": ch[2]} for ch in channels],
                    "recent_earnings": [{"ad_id": e[0], "channel_id": e[1], "amount": e[2], "type": e[3], "date": e[4]} for e in earnings]
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting user stats: {e}")
            return {}
    
    async def get_advertiser_stats(self, advertiser_id: int) -> Dict:
        """Get advertiser statistics"""
        try:
            async with self.get_db_connection() as db:
                # Get ad performance
                async with db.execute("""
                    SELECT a.ad_id, a.content, a.category, a.bid_type, a.bid_amount, a.status,
                           COALESCE(SUM(p.impressions), 0) as total_impressions,
                           COALESCE(SUM(p.clicks), 0) as total_clicks,
                           0 as total_spent
                    FROM auction_ads a
                    LEFT JOIN ad_performance p ON a.ad_id = p.ad_id
                    WHERE a.advertiser_id = ?
                    GROUP BY a.ad_id
                    ORDER BY a.created_at DESC
                """, (advertiser_id,)) as cursor:
                    ads = await cursor.fetchall()
                
                ad_stats = []
                for ad in ads:
                    ctr = (ad[7] / ad[6] * 100) if ad[6] > 0 else 0  # Click-through rate
                    ad_stats.append({
                        "ad_id": ad[0],
                        "content": ad[1][:50] + "..." if len(ad[1]) > 50 else ad[1],
                        "category": ad[2],
                        "bid_type": ad[3],
                        "bid_amount": ad[4],
                        "status": ad[5],
                        "impressions": ad[6],
                        "clicks": ad[7],
                        "spent": ad[8],
                        "ctr": round(ctr, 2)
                    })
                
                return {"ads": ad_stats}
                
        except Exception as e:
            logger.error(f"❌ Error getting advertiser stats: {e}")
            return {}

# Global instance
auction_system = AuctionAdvertisingSystem()

async def get_auction_system() -> AuctionAdvertisingSystem:
    """Get or create auction system instance"""
    global auction_system
    if not hasattr(auction_system, '_initialized'):
        await auction_system.initialize_database()
        auction_system._initialized = True
    return auction_system