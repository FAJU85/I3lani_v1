"""
Price Management System for I3lani Bot
Comprehensive pricing control for admin panel
"""

import logging
import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from database import db
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

class PriceManager:
    """Advanced price management system"""
    
    def __init__(self):
        self.pricing_tiers = {}
        self.base_price_usd = 1.00  # Base price per post per day
        self.last_updated = None
        
    async def initialize_database(self):
        """Initialize price management database tables"""
        connection = await db.get_connection()
        cursor = await connection.cursor()
        
        # Price tiers table (current pricing)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_tiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration_days INTEGER UNIQUE,
                posts_per_day INTEGER,
                discount_percent REAL DEFAULT 0.0,
                base_price_usd REAL DEFAULT 1.00,
                final_price_usd REAL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # New pricing table (experimental/future pricing)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS new_pricing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                duration_days INTEGER,
                posts_per_day INTEGER,
                discount_percent REAL DEFAULT 0.0,
                base_price_usd REAL DEFAULT 1.00,
                final_price_usd REAL,
                description TEXT,
                is_active BOOLEAN DEFAULT 0,
                launch_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Offers table (promotional offers)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                offer_name TEXT NOT NULL,
                offer_type TEXT DEFAULT 'discount',
                duration_days INTEGER,
                posts_per_day INTEGER,
                original_price REAL,
                offer_price REAL,
                discount_percent REAL,
                offer_description TEXT,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                max_uses INTEGER DEFAULT -1,
                current_uses INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bundles table (package deals)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS bundles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bundle_name TEXT NOT NULL,
                bundle_description TEXT,
                bundle_items TEXT,
                total_duration_days INTEGER,
                total_posts INTEGER,
                individual_price REAL,
                bundle_price REAL,
                savings_percent REAL,
                is_featured BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Price history table (for all types)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT,
                item_id INTEGER,
                old_price REAL,
                new_price REAL,
                change_reason TEXT,
                admin_id INTEGER,
                change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Price analytics table (for all types)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT,
                item_id INTEGER,
                usage_count INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0.0,
                last_used TIMESTAMP,
                popularity_score REAL DEFAULT 0.0
            )
        ''')
        
        await connection.commit()
        await connection.close()
        
        # Initialize default data if none exist
        await self.initialize_default_prices()
        await self.initialize_default_offers()
        await self.initialize_default_bundles()
        logger.info("✅ Price management database initialized with all categories")
    
    async def initialize_default_prices(self):
        """Initialize default pricing tiers"""
        default_tiers = [
            (1, 1, 0.0),    # 1 day, 1 post/day, 0% discount
            (3, 1, 5.0),    # 3 days, 1 post/day, 5% discount
            (7, 2, 10.0),   # 7 days, 2 posts/day, 10% discount
            (15, 2, 15.0),  # 15 days, 2 posts/day, 15% discount
            (30, 3, 20.0),  # 30 days, 3 posts/day, 20% discount
            (60, 3, 25.0),  # 60 days, 3 posts/day, 25% discount
            (90, 4, 30.0),  # 90 days, 4 posts/day, 30% discount
        ]
        
        existing_prices = await self.get_all_price_tiers()
        if not existing_prices:
            for days, posts_per_day, discount in default_tiers:
                await self.create_price_tier(days, posts_per_day, discount)
            logger.info("✅ Default pricing tiers initialized")
    
    async def create_price_tier(self, duration_days: int, posts_per_day: int, 
                               discount_percent: float = 0.0, admin_id: int = None) -> bool:
        """Create new price tier"""
        try:
            # Calculate final price
            base_cost = self.base_price_usd * posts_per_day * duration_days
            discount_amount = base_cost * (discount_percent / 100)
            final_price = base_cost - discount_amount
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                INSERT OR REPLACE INTO price_tiers 
                (duration_days, posts_per_day, discount_percent, base_price_usd, final_price_usd, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (duration_days, posts_per_day, discount_percent, self.base_price_usd, final_price, datetime.now()))
            
            # Log price change
            if admin_id:
                await cursor.execute('''
                    INSERT INTO price_history 
                    (duration_days, old_price, new_price, change_reason, admin_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (duration_days, 0.0, final_price, "New price tier created", admin_id))
            
            # Initialize analytics entry
            await cursor.execute('''
                INSERT OR IGNORE INTO price_analytics (duration_days)
                VALUES (?)
            ''', (duration_days,))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Created price tier: {duration_days} days, {posts_per_day} posts/day, ${final_price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating price tier: {e}")
            return False
    
    async def update_price_tier(self, duration_days: int, posts_per_day: int = None, 
                               discount_percent: float = None, admin_id: int = None) -> bool:
        """Update existing price tier"""
        try:
            # Get current tier
            current_tier = await self.get_price_tier(duration_days)
            if not current_tier:
                return False
            
            # Use existing values if not provided
            new_posts_per_day = posts_per_day if posts_per_day is not None else current_tier['posts_per_day']
            new_discount = discount_percent if discount_percent is not None else current_tier['discount_percent']
            
            # Calculate new final price
            base_cost = self.base_price_usd * new_posts_per_day * duration_days
            discount_amount = base_cost * (new_discount / 100)
            new_final_price = base_cost - discount_amount
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                UPDATE price_tiers 
                SET posts_per_day = ?, discount_percent = ?, final_price_usd = ?, updated_at = ?
                WHERE duration_days = ?
            ''', (new_posts_per_day, new_discount, new_final_price, datetime.now(), duration_days))
            
            # Log price change
            if admin_id:
                old_price = current_tier['final_price_usd']
                await cursor.execute('''
                    INSERT INTO price_history 
                    (duration_days, old_price, new_price, change_reason, admin_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (duration_days, old_price, new_final_price, "Price tier updated", admin_id))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Updated price tier: {duration_days} days, ${new_final_price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating price tier: {e}")
            return False
    
    async def delete_price_tier(self, duration_days: int, admin_id: int = None) -> bool:
        """Delete price tier"""
        try:
            # Get current tier for logging
            current_tier = await self.get_price_tier(duration_days)
            if not current_tier:
                return False
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('DELETE FROM price_tiers WHERE duration_days = ?', (duration_days,))
            
            # Log deletion
            if admin_id:
                await cursor.execute('''
                    INSERT INTO price_history 
                    (duration_days, old_price, new_price, change_reason, admin_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (duration_days, current_tier['final_price_usd'], 0.0, "Price tier deleted", admin_id))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Deleted price tier: {duration_days} days")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting price tier: {e}")
            return False
    
    async def get_price_tier(self, duration_days: int) -> Optional[Dict]:
        """Get specific price tier"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                SELECT duration_days, posts_per_day, discount_percent, base_price_usd, 
                       final_price_usd, is_active, created_at, updated_at
                FROM price_tiers WHERE duration_days = ?
            ''', (duration_days,))
            
            row = await cursor.fetchone()
            await connection.close()
            
            if row:
                return {
                    'duration_days': row[0],
                    'posts_per_day': row[1],
                    'discount_percent': row[2],
                    'base_price_usd': row[3],
                    'final_price_usd': row[4],
                    'is_active': bool(row[5]),
                    'created_at': row[6],
                    'updated_at': row[7]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting price tier: {e}")
            return None
    
    async def get_all_price_tiers(self, active_only: bool = False) -> List[Dict]:
        """Get all price tiers"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            query = '''
                SELECT duration_days, posts_per_day, discount_percent, base_price_usd, 
                       final_price_usd, is_active, created_at, updated_at
                FROM price_tiers
            '''
            
            if active_only:
                query += ' WHERE is_active = 1'
            
            query += ' ORDER BY duration_days ASC'
            
            await cursor.execute(query)
            rows = await cursor.fetchall()
            await connection.close()
            
            tiers = []
            for row in rows:
                tiers.append({
                    'duration_days': row[0],
                    'posts_per_day': row[1],
                    'discount_percent': row[2],
                    'base_price_usd': row[3],
                    'final_price_usd': row[4],
                    'is_active': bool(row[5]),
                    'created_at': row[6],
                    'updated_at': row[7]
                })
            
            return tiers
            
        except Exception as e:
            logger.error(f"Error getting all price tiers: {e}")
            return []
    
    async def toggle_price_tier_status(self, duration_days: int, admin_id: int = None) -> bool:
        """Toggle price tier active status"""
        try:
            current_tier = await self.get_price_tier(duration_days)
            if not current_tier:
                return False
            
            new_status = not current_tier['is_active']
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                UPDATE price_tiers SET is_active = ?, updated_at = ?
                WHERE duration_days = ?
            ''', (new_status, datetime.now(), duration_days))
            
            # Log status change
            if admin_id:
                reason = "Price tier activated" if new_status else "Price tier deactivated"
                await cursor.execute('''
                    INSERT INTO price_history 
                    (duration_days, old_price, new_price, change_reason, admin_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (duration_days, current_tier['final_price_usd'], current_tier['final_price_usd'], reason, admin_id))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Toggled price tier status: {duration_days} days, active: {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Error toggling price tier status: {e}")
            return False
    
    async def get_price_analytics(self, duration_days: int = None) -> Dict:
        """Get price analytics"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            if duration_days:
                await cursor.execute('''
                    SELECT duration_days, usage_count, total_revenue, last_used, popularity_score
                    FROM price_analytics WHERE duration_days = ?
                ''', (duration_days,))
                
                row = await cursor.fetchone()
                if row:
                    return {
                        'duration_days': row[0],
                        'usage_count': row[1],
                        'total_revenue': row[2],
                        'last_used': row[3],
                        'popularity_score': row[4]
                    }
                return {}
            else:
                await cursor.execute('''
                    SELECT duration_days, usage_count, total_revenue, last_used, popularity_score
                    FROM price_analytics ORDER BY popularity_score DESC
                ''')
                
                rows = await cursor.fetchall()
                analytics = []
                for row in rows:
                    analytics.append({
                        'duration_days': row[0],
                        'usage_count': row[1],
                        'total_revenue': row[2],
                        'last_used': row[3],
                        'popularity_score': row[4]
                    })
                
                await connection.close()
                return {'all_tiers': analytics}
                
        except Exception as e:
            logger.error(f"Error getting price analytics: {e}")
            return {}
    
    async def get_price_history(self, duration_days: int = None, limit: int = 50) -> List[Dict]:
        """Get price change history"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            query = '''
                SELECT duration_days, old_price, new_price, change_reason, admin_id, change_date
                FROM price_history
            '''
            
            params = []
            if duration_days:
                query += ' WHERE duration_days = ?'
                params.append(duration_days)
            
            query += ' ORDER BY change_date DESC LIMIT ?'
            params.append(limit)
            
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            await connection.close()
            
            history = []
            for row in rows:
                history.append({
                    'duration_days': row[0],
                    'old_price': row[1],
                    'new_price': row[2],
                    'change_reason': row[3],
                    'admin_id': row[4],
                    'change_date': row[5]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return []
    
    async def bulk_update_prices(self, price_changes: List[Dict], admin_id: int = None) -> Dict:
        """Bulk update multiple price tiers"""
        results = {
            'updated': 0,
            'failed': 0,
            'errors': []
        }
        
        for change in price_changes:
            try:
                duration_days = change.get('duration_days')
                posts_per_day = change.get('posts_per_day')
                discount_percent = change.get('discount_percent')
                
                success = await self.update_price_tier(duration_days, posts_per_day, discount_percent, admin_id)
                
                if success:
                    results['updated'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to update {duration_days} days tier")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error updating tier: {str(e)}")
        
        logger.info(f"✅ Bulk update completed: {results['updated']} updated, {results['failed']} failed")
        return results
    
    async def initialize_default_offers(self):
        """Initialize default promotional offers"""
        existing_offers = await self.get_all_offers()
        if not existing_offers:
            default_offers = [
                {
                    'offer_name': 'Weekend Special',
                    'offer_type': 'discount',
                    'duration_days': 3,
                    'posts_per_day': 2,
                    'discount_percent': 25.0,
                    'offer_description': 'Weekend boost with 25% discount',
                    'max_uses': 100
                },
                {
                    'offer_name': 'New User Promo',
                    'offer_type': 'discount',
                    'duration_days': 7,
                    'posts_per_day': 1,
                    'discount_percent': 30.0,
                    'offer_description': 'First-time user discount',
                    'max_uses': 50
                },
                {
                    'offer_name': 'Flash Sale',
                    'offer_type': 'discount',
                    'duration_days': 1,
                    'posts_per_day': 3,
                    'discount_percent': 40.0,
                    'offer_description': '24-hour flash promotion',
                    'max_uses': 25
                }
            ]
            
            for offer_data in default_offers:
                await self.create_offer(**offer_data)
            logger.info("✅ Default offers initialized")
    
    async def initialize_default_bundles(self):
        """Initialize default bundle packages"""
        existing_bundles = await self.get_all_bundles()
        if not existing_bundles:
            default_bundles = [
                {
                    'bundle_name': 'Starter Pack',
                    'bundle_description': 'Perfect for small businesses',
                    'bundle_items': '7 days + 15 days + 30 days',
                    'total_duration_days': 52,
                    'total_posts': 104,
                    'bundle_price': 45.0,
                    'savings_percent': 15.0
                },
                {
                    'bundle_name': 'Growth Package',
                    'bundle_description': 'Ideal for expanding reach',
                    'bundle_items': '30 days + 60 days + 90 days',
                    'total_duration_days': 180,
                    'total_posts': 540,
                    'bundle_price': 180.0,
                    'savings_percent': 25.0
                },
                {
                    'bundle_name': 'Enterprise Suite',
                    'bundle_description': 'Maximum exposure package',
                    'bundle_items': '60 days + 90 days + 180 days',
                    'total_duration_days': 330,
                    'total_posts': 1320,
                    'bundle_price': 350.0,
                    'savings_percent': 30.0
                }
            ]
            
            for bundle_data in default_bundles:
                await self.create_bundle(**bundle_data)
            logger.info("✅ Default bundles initialized")
    
    # NEW PRICING METHODS
    async def create_new_pricing(self, name: str, duration_days: int, posts_per_day: int, 
                                discount_percent: float = 0.0, description: str = "", 
                                launch_date: str = None, admin_id: int = None) -> bool:
        """Create new experimental pricing tier"""
        try:
            base_cost = self.base_price_usd * posts_per_day * duration_days
            discount_amount = base_cost * (discount_percent / 100)
            final_price = base_cost - discount_amount
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                INSERT INTO new_pricing 
                (name, duration_days, posts_per_day, discount_percent, base_price_usd, 
                 final_price_usd, description, launch_date, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, duration_days, posts_per_day, discount_percent, self.base_price_usd, 
                  final_price, description, launch_date, datetime.now()))
            
            new_pricing_id = cursor.lastrowid
            
            if admin_id:
                await cursor.execute('''
                    INSERT INTO price_history 
                    (item_type, item_id, old_price, new_price, change_reason, admin_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ("new_pricing", new_pricing_id, 0.0, final_price, "New pricing created", admin_id))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Created new pricing: {name} - ${final_price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating new pricing: {e}")
            return False
    
    async def get_all_new_pricing(self, active_only: bool = False) -> List[Dict]:
        """Get all new pricing tiers"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            query = '''
                SELECT id, name, duration_days, posts_per_day, discount_percent, 
                       base_price_usd, final_price_usd, description, is_active, 
                       launch_date, created_at, updated_at
                FROM new_pricing
            '''
            
            if active_only:
                query += ' WHERE is_active = 1'
            
            query += ' ORDER BY created_at DESC'
            
            await cursor.execute(query)
            rows = await cursor.fetchall()
            await connection.close()
            
            new_pricing = []
            for row in rows:
                new_pricing.append({
                    'id': row[0],
                    'name': row[1],
                    'duration_days': row[2],
                    'posts_per_day': row[3],
                    'discount_percent': row[4],
                    'base_price_usd': row[5],
                    'final_price_usd': row[6],
                    'description': row[7],
                    'is_active': bool(row[8]),
                    'launch_date': row[9],
                    'created_at': row[10],
                    'updated_at': row[11]
                })
            
            return new_pricing
            
        except Exception as e:
            logger.error(f"Error getting new pricing: {e}")
            return []
    
    # OFFERS METHODS
    async def create_offer(self, offer_name: str, duration_days: int, posts_per_day: int,
                          discount_percent: float, offer_description: str = "",
                          offer_type: str = "discount", max_uses: int = -1,
                          start_date: str = None, end_date: str = None, admin_id: int = None) -> bool:
        """Create promotional offer"""
        try:
            original_price = self.base_price_usd * posts_per_day * duration_days
            offer_price = original_price * (1 - discount_percent / 100)
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                INSERT INTO offers 
                (offer_name, offer_type, duration_days, posts_per_day, original_price,
                 offer_price, discount_percent, offer_description, start_date, end_date,
                 max_uses, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (offer_name, offer_type, duration_days, posts_per_day, original_price,
                  offer_price, discount_percent, offer_description, start_date, end_date,
                  max_uses, datetime.now()))
            
            offer_id = cursor.lastrowid
            
            if admin_id:
                await cursor.execute('''
                    INSERT INTO price_history 
                    (item_type, item_id, old_price, new_price, change_reason, admin_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ("offer", offer_id, original_price, offer_price, "Offer created", admin_id))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Created offer: {offer_name} - ${offer_price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating offer: {e}")
            return False
    
    async def get_all_offers(self, active_only: bool = False) -> List[Dict]:
        """Get all promotional offers"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            query = '''
                SELECT id, offer_name, offer_type, duration_days, posts_per_day,
                       original_price, offer_price, discount_percent, offer_description,
                       start_date, end_date, max_uses, current_uses, is_active,
                       created_at, updated_at
                FROM offers
            '''
            
            if active_only:
                query += ' WHERE is_active = 1'
            
            query += ' ORDER BY created_at DESC'
            
            await cursor.execute(query)
            rows = await cursor.fetchall()
            await connection.close()
            
            offers = []
            for row in rows:
                offers.append({
                    'id': row[0],
                    'offer_name': row[1],
                    'offer_type': row[2],
                    'duration_days': row[3],
                    'posts_per_day': row[4],
                    'original_price': row[5],
                    'offer_price': row[6],
                    'discount_percent': row[7],
                    'offer_description': row[8],
                    'start_date': row[9],
                    'end_date': row[10],
                    'max_uses': row[11],
                    'current_uses': row[12],
                    'is_active': bool(row[13]),
                    'created_at': row[14],
                    'updated_at': row[15]
                })
            
            return offers
            
        except Exception as e:
            logger.error(f"Error getting offers: {e}")
            return []
    
    # BUNDLES METHODS
    async def create_bundle(self, bundle_name: str, bundle_description: str, bundle_items: str,
                           total_duration_days: int, total_posts: int, bundle_price: float,
                           savings_percent: float, is_featured: bool = False, admin_id: int = None) -> bool:
        """Create bundle package"""
        try:
            individual_price = self.base_price_usd * total_posts
            
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                INSERT INTO bundles 
                (bundle_name, bundle_description, bundle_items, total_duration_days,
                 total_posts, individual_price, bundle_price, savings_percent,
                 is_featured, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bundle_name, bundle_description, bundle_items, total_duration_days,
                  total_posts, individual_price, bundle_price, savings_percent,
                  is_featured, datetime.now()))
            
            bundle_id = cursor.lastrowid
            
            if admin_id:
                await cursor.execute('''
                    INSERT INTO price_history 
                    (item_type, item_id, old_price, new_price, change_reason, admin_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ("bundle", bundle_id, individual_price, bundle_price, "Bundle created", admin_id))
            
            await connection.commit()
            await connection.close()
            
            logger.info(f"✅ Created bundle: {bundle_name} - ${bundle_price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating bundle: {e}")
            return False
    
    async def get_all_bundles(self, active_only: bool = False) -> List[Dict]:
        """Get all bundle packages"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            query = '''
                SELECT id, bundle_name, bundle_description, bundle_items,
                       total_duration_days, total_posts, individual_price,
                       bundle_price, savings_percent, is_featured, is_active,
                       created_at, updated_at
                FROM bundles
            '''
            
            if active_only:
                query += ' WHERE is_active = 1'
            
            query += ' ORDER BY is_featured DESC, created_at DESC'
            
            await cursor.execute(query)
            rows = await cursor.fetchall()
            await connection.close()
            
            bundles = []
            for row in rows:
                bundles.append({
                    'id': row[0],
                    'bundle_name': row[1],
                    'bundle_description': row[2],
                    'bundle_items': row[3],
                    'total_duration_days': row[4],
                    'total_posts': row[5],
                    'individual_price': row[6],
                    'bundle_price': row[7],
                    'savings_percent': row[8],
                    'is_featured': bool(row[9]),
                    'is_active': bool(row[10]),
                    'created_at': row[11],
                    'updated_at': row[12]
                })
            
            return bundles
            
        except Exception as e:
            logger.error(f"Error getting bundles: {e}")
            return []
    
    async def get_pricing_summary(self) -> Dict:
        """Get comprehensive pricing summary for all categories"""
        try:
            # Get all data
            tiers = await self.get_all_price_tiers()
            new_pricing = await self.get_all_new_pricing()
            offers = await self.get_all_offers()
            bundles = await self.get_all_bundles()
            
            active_tiers = [t for t in tiers if t['is_active']]
            active_offers = [o for o in offers if o['is_active']]
            active_bundles = [b for b in bundles if b['is_active']]
            
            return {
                'current_pricing': {
                    'total': len(tiers),
                    'active': len(active_tiers),
                    'min_price': min(t['final_price_usd'] for t in active_tiers) if active_tiers else 0,
                    'max_price': max(t['final_price_usd'] for t in active_tiers) if active_tiers else 0
                },
                'new_pricing': {
                    'total': len(new_pricing),
                    'active': len([p for p in new_pricing if p['is_active']])
                },
                'offers': {
                    'total': len(offers),
                    'active': len(active_offers),
                    'max_discount': max(o['discount_percent'] for o in active_offers) if active_offers else 0
                },
                'bundles': {
                    'total': len(bundles),
                    'active': len(active_bundles),
                    'featured': len([b for b in active_bundles if b['is_featured']]),
                    'max_savings': max(b['savings_percent'] for b in active_bundles) if active_bundles else 0
                },
                'base_price_usd': self.base_price_usd,
                'last_updated': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error getting pricing summary: {e}")
            return {}

# Global instance
price_manager = None

def get_price_manager() -> PriceManager:
    """Get or create price manager instance"""
    global price_manager
    if price_manager is None:
        price_manager = PriceManager()
    return price_manager