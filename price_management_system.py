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
        
        # Price tiers table
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
        
        # Price history table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration_days INTEGER,
                old_price REAL,
                new_price REAL,
                change_reason TEXT,
                admin_id INTEGER,
                change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Price analytics table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                duration_days INTEGER,
                usage_count INTEGER DEFAULT 0,
                total_revenue REAL DEFAULT 0.0,
                last_used TIMESTAMP,
                popularity_score REAL DEFAULT 0.0
            )
        ''')
        
        await connection.commit()
        await connection.close()
        
        # Initialize default pricing tiers if none exist
        await self.initialize_default_prices()
        logger.info("✅ Price management database initialized")
    
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
    
    async def get_pricing_summary(self) -> Dict:
        """Get comprehensive pricing summary"""
        try:
            tiers = await self.get_all_price_tiers()
            active_tiers = [t for t in tiers if t['is_active']]
            
            total_revenue = 0.0
            total_usage = 0
            
            # Get analytics totals
            analytics = await self.get_price_analytics()
            if 'all_tiers' in analytics:
                for tier_analytics in analytics['all_tiers']:
                    total_revenue += tier_analytics['total_revenue']
                    total_usage += tier_analytics['usage_count']
            
            return {
                'total_tiers': len(tiers),
                'active_tiers': len(active_tiers),
                'inactive_tiers': len(tiers) - len(active_tiers),
                'base_price_usd': self.base_price_usd,
                'price_range': {
                    'min_price': min(t['final_price_usd'] for t in active_tiers) if active_tiers else 0,
                    'max_price': max(t['final_price_usd'] for t in active_tiers) if active_tiers else 0
                },
                'total_revenue': total_revenue,
                'total_usage': total_usage,
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