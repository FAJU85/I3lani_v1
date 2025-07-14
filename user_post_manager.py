"""
User Post Manager for I3lani Bot
Manages user post credits, usage tracking, and expiration
"""

import aiosqlite
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class PostStatus(Enum):
    """Post usage status"""
    AVAILABLE = "available"
    USED = "used"
    SCHEDULED = "scheduled"
    EXPIRED = "expired"

@dataclass
class PostCredit:
    """Individual post credit"""
    credit_id: str
    user_id: int
    package_name: str
    purchased_at: datetime
    expires_at: datetime
    status: PostStatus
    used_at: Optional[datetime] = None
    campaign_id: Optional[str] = None

class UserPostManager:
    """Manages user post credits and usage"""
    
    def __init__(self, db_path: str = "ads.db"):
        self.db_path = db_path
        self.post_expiry_days = 90
    
    async def initialize_database(self):
        """Initialize post management database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # User post credits table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_post_credits (
                    credit_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    package_name TEXT NOT NULL,
                    posts_total INTEGER NOT NULL,
                    posts_used INTEGER DEFAULT 0,
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Individual post usage tracking
            await db.execute("""
                CREATE TABLE IF NOT EXISTS post_usage_log (
                    usage_id TEXT PRIMARY KEY,
                    credit_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    campaign_id TEXT,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    channels TEXT,
                    content_hash TEXT,
                    FOREIGN KEY (credit_id) REFERENCES user_post_credits(credit_id)
                )
            """)
            
            # Auto-scheduling purchases
            await db.execute("""
                CREATE TABLE IF NOT EXISTS auto_schedule_purchases (
                    purchase_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    days_purchased INTEGER NOT NULL,
                    price_paid REAL NOT NULL,
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    days_used INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Add-on purchases
            await db.execute("""
                CREATE TABLE IF NOT EXISTS addon_purchases (
                    purchase_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    addon_key TEXT NOT NULL,
                    addon_name TEXT NOT NULL,
                    price_paid REAL NOT NULL,
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    uses_remaining INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            await db.commit()
    
    async def add_post_credits(self, user_id: int, package_name: str, posts_count: int, 
                             purchase_id: str = None) -> str:
        """Add post credits to user account"""
        from global_sequence_system import get_global_sequence_manager
        
        credit_id = purchase_id or get_global_sequence_manager().generate_id("CREDIT")
        expires_at = datetime.now() + timedelta(days=self.post_expiry_days)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO user_post_credits 
                (credit_id, user_id, package_name, posts_total, posts_used, expires_at)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (credit_id, user_id, package_name, posts_count, expires_at))
            
            await db.commit()
        
        return credit_id
    
    async def get_user_post_balance(self, user_id: int) -> Dict:
        """Get user's current post balance"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get active credits
            cursor = await db.execute("""
                SELECT credit_id, package_name, posts_total, posts_used, expires_at
                FROM user_post_credits 
                WHERE user_id = ? AND status = 'active' AND expires_at > datetime('now')
                ORDER BY expires_at ASC
            """, (user_id,))
            
            credits = await cursor.fetchall()
            
            total_posts = 0
            used_posts = 0
            credits_info = []
            
            for credit in credits:
                credit_id, package_name, posts_total, posts_used, expires_at = credit
                available = posts_total - posts_used
                total_posts += available
                used_posts += posts_used
                
                credits_info.append({
                    'credit_id': credit_id,
                    'package_name': package_name,
                    'posts_total': posts_total,
                    'posts_used': posts_used,
                    'posts_available': available,
                    'expires_at': expires_at
                })
            
            return {
                'total_available': total_posts,
                'total_used': used_posts,
                'credits': credits_info,
                'has_credits': total_posts > 0
            }
    
    async def use_post_credit(self, user_id: int, campaign_id: str, 
                            channels: List[str], content_hash: str) -> Tuple[bool, str]:
        """Use a post credit for a campaign"""
        from global_sequence_system import get_global_sequence_manager
        
        async with aiosqlite.connect(self.db_path) as db:
            # Find oldest available credit
            cursor = await db.execute("""
                SELECT credit_id, posts_total, posts_used
                FROM user_post_credits 
                WHERE user_id = ? AND status = 'active' 
                AND expires_at > datetime('now') 
                AND posts_used < posts_total
                ORDER BY expires_at ASC
                LIMIT 1
            """, (user_id,))
            
            credit = await cursor.fetchone()
            
            if not credit:
                return False, "No available post credits. Please purchase a package."
            
            credit_id, posts_total, posts_used = credit
            
            # Update credit usage
            await db.execute("""
                UPDATE user_post_credits 
                SET posts_used = posts_used + 1
                WHERE credit_id = ?
            """, (credit_id,))
            
            # Log usage
            usage_id = get_global_sequence_manager().generate_id("USAGE")
            await db.execute("""
                INSERT INTO post_usage_log 
                (usage_id, credit_id, user_id, campaign_id, channels, content_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (usage_id, credit_id, user_id, campaign_id, json.dumps(channels), content_hash))
            
            await db.commit()
            
            remaining = posts_total - posts_used - 1
            return True, f"Post credit used successfully. {remaining} posts remaining."
    
    async def add_auto_schedule_days(self, user_id: int, days: int, price_paid: float) -> str:
        """Add auto-scheduling days to user account"""
        from global_sequence_system import get_global_sequence_manager
        
        purchase_id = get_global_sequence_manager().generate_id("SCHEDULE")
        expires_at = datetime.now() + timedelta(days=365)  # Auto-schedule doesn't expire quickly
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO auto_schedule_purchases 
                (purchase_id, user_id, days_purchased, price_paid, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (purchase_id, user_id, days, price_paid, expires_at))
            
            await db.commit()
        
        return purchase_id
    
    async def get_user_auto_schedule_balance(self, user_id: int) -> Dict:
        """Get user's auto-scheduling balance"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT SUM(days_purchased - days_used) as available_days
                FROM auto_schedule_purchases 
                WHERE user_id = ? AND status = 'active' AND expires_at > datetime('now')
            """, (user_id,))
            
            result = await cursor.fetchone()
            available_days = result[0] if result[0] else 0
            
            return {
                'available_days': available_days,
                'has_auto_schedule': available_days > 0
            }
    
    async def use_auto_schedule_day(self, user_id: int) -> Tuple[bool, str]:
        """Use one auto-scheduling day"""
        async with aiosqlite.connect(self.db_path) as db:
            # Find oldest available auto-schedule purchase
            cursor = await db.execute("""
                SELECT purchase_id, days_purchased, days_used
                FROM auto_schedule_purchases 
                WHERE user_id = ? AND status = 'active' 
                AND expires_at > datetime('now') 
                AND days_used < days_purchased
                ORDER BY purchased_at ASC
                LIMIT 1
            """, (user_id,))
            
            purchase = await cursor.fetchone()
            
            if not purchase:
                return False, "No auto-scheduling days available."
            
            purchase_id, days_purchased, days_used = purchase
            
            # Update usage
            await db.execute("""
                UPDATE auto_schedule_purchases 
                SET days_used = days_used + 1
                WHERE purchase_id = ?
            """, (purchase_id,))
            
            await db.commit()
            
            remaining = days_purchased - days_used - 1
            return True, f"Auto-schedule day used. {remaining} days remaining."
    
    async def add_addon_purchase(self, user_id: int, addon_key: str, addon_name: str, 
                               price_paid: float, uses: int = 1) -> str:
        """Add add-on purchase to user account"""
        from global_sequence_system import get_global_sequence_manager
        
        purchase_id = get_global_sequence_manager().generate_id("ADDON")
        expires_at = datetime.now() + timedelta(days=365)  # Add-ons expire after 1 year
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO addon_purchases 
                (purchase_id, user_id, addon_key, addon_name, price_paid, expires_at, uses_remaining)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (purchase_id, user_id, addon_key, addon_name, price_paid, expires_at, uses))
            
            await db.commit()
        
        return purchase_id
    
    async def get_user_addons(self, user_id: int) -> List[Dict]:
        """Get user's active add-ons"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT addon_key, addon_name, uses_remaining, expires_at
                FROM addon_purchases 
                WHERE user_id = ? AND status = 'active' 
                AND expires_at > datetime('now') AND uses_remaining > 0
            """, (user_id,))
            
            addons = await cursor.fetchall()
            
            return [
                {
                    'addon_key': addon[0],
                    'addon_name': addon[1],
                    'uses_remaining': addon[2],
                    'expires_at': addon[3]
                }
                for addon in addons
            ]
    
    async def use_addon(self, user_id: int, addon_key: str) -> Tuple[bool, str]:
        """Use an add-on"""
        async with aiosqlite.connect(self.db_path) as db:
            # Find available add-on
            cursor = await db.execute("""
                SELECT purchase_id, uses_remaining
                FROM addon_purchases 
                WHERE user_id = ? AND addon_key = ? AND status = 'active' 
                AND expires_at > datetime('now') AND uses_remaining > 0
                ORDER BY purchased_at ASC
                LIMIT 1
            """, (user_id, addon_key))
            
            purchase = await cursor.fetchone()
            
            if not purchase:
                return False, f"No available {addon_key} add-on."
            
            purchase_id, uses_remaining = purchase
            
            # Update usage
            await db.execute("""
                UPDATE addon_purchases 
                SET uses_remaining = uses_remaining - 1
                WHERE purchase_id = ?
            """, (purchase_id,))
            
            await db.commit()
            
            remaining = uses_remaining - 1
            return True, f"Add-on used. {remaining} uses remaining."
    
    async def get_user_dashboard_stats(self, user_id: int) -> Dict:
        """Get comprehensive user dashboard statistics"""
        post_balance = await self.get_user_post_balance(user_id)
        auto_schedule = await self.get_user_auto_schedule_balance(user_id)
        addons = await self.get_user_addons(user_id)
        
        return {
            'posts': post_balance,
            'auto_schedule': auto_schedule,
            'addons': addons,
            'total_value': self._calculate_total_value(post_balance, auto_schedule, addons)
        }
    
    def _calculate_total_value(self, post_balance: Dict, auto_schedule: Dict, addons: List[Dict]) -> float:
        """Calculate total value of user's credits and add-ons"""
        total_value = 0.0
        
        # Value of remaining posts (using average cost per post)
        total_value += post_balance['total_available'] * 0.20  # Average cost per post
        
        # Value of auto-schedule days
        total_value += auto_schedule['available_days'] * 0.25  # $0.25 per day
        
        # Value of add-ons (simplified)
        total_value += len(addons) * 0.50  # Average add-on value
        
        return round(total_value, 2)
    
    async def expire_old_credits(self):
        """Expire old credits (maintenance function)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE user_post_credits 
                SET status = 'expired' 
                WHERE expires_at < datetime('now') AND status = 'active'
            """)
            
            await db.execute("""
                UPDATE auto_schedule_purchases 
                SET status = 'expired' 
                WHERE expires_at < datetime('now') AND status = 'active'
            """)
            
            await db.execute("""
                UPDATE addon_purchases 
                SET status = 'expired' 
                WHERE expires_at < datetime('now') AND status = 'active'
            """)
            
            await db.commit()

# Global instance
user_post_manager = UserPostManager()

def get_user_post_manager() -> UserPostManager:
    """Get the global user post manager instance"""
    return user_post_manager