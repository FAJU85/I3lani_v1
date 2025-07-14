#!/usr/bin/env python3
"""
Advanced Pricing Management System for I3lani Bot
Complete admin control over pricing structures with CRUD operations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

class PricingManagementStates(StatesGroup):
    """States for pricing management"""
    waiting_for_tier_details = State()
    waiting_for_tier_edit = State()
    waiting_for_bulk_pricing = State()
    waiting_for_offer_details = State()
    waiting_for_bundle_details = State()

class AdvancedPricingManager:
    """Advanced pricing management with full admin control"""
    
    def __init__(self):
        self.pricing_categories = {
            'current': 'Current Pricing Tiers',
            'experimental': 'Experimental Pricing',
            'offers': 'Promotional Offers', 
            'bundles': 'Bundle Packages',
            'custom': 'Custom Pricing Rules'
        }
        
    async def initialize_pricing_database(self):
        """Initialize comprehensive pricing database"""
        connection = await db.get_connection()
        cursor = await connection.cursor()
        
        # Enhanced pricing tiers table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_tiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tier_name TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                posts_per_day INTEGER DEFAULT 2,
                base_price_usd REAL NOT NULL,
                discount_percent REAL DEFAULT 0.0,
                final_price_usd REAL NOT NULL,
                tier_category TEXT DEFAULT 'current',
                is_active BOOLEAN DEFAULT 1,
                priority INTEGER DEFAULT 1,
                description TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Promotional offers table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS promotional_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                offer_name TEXT NOT NULL,
                offer_code TEXT UNIQUE,
                discount_type TEXT DEFAULT 'percentage',
                discount_value REAL NOT NULL,
                min_duration INTEGER DEFAULT 1,
                max_duration INTEGER DEFAULT 90,
                usage_limit INTEGER DEFAULT 0,
                current_usage INTEGER DEFAULT 0,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bundle packages table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS bundle_packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bundle_name TEXT NOT NULL,
                bundle_description TEXT,
                total_days INTEGER NOT NULL,
                total_posts INTEGER NOT NULL,
                original_price REAL NOT NULL,
                bundle_price REAL NOT NULL,
                savings_amount REAL NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pricing history table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                old_price REAL,
                new_price REAL,
                change_reason TEXT,
                changed_by INTEGER,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pricing analytics table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tier_id INTEGER,
                selection_count INTEGER DEFAULT 0,
                revenue_generated REAL DEFAULT 0.0,
                conversion_rate REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await connection.commit()
        logger.info("✅ Advanced pricing database initialized")
    
    async def create_pricing_tier(self, tier_data: Dict) -> bool:
        """Create a new pricing tier"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            # Calculate final price with discount
            base_price = tier_data['base_price_usd']
            discount = tier_data.get('discount_percent', 0.0)
            final_price = base_price * (1 - discount / 100)
            
            await cursor.execute('''
                INSERT INTO pricing_tiers (
                    tier_name, duration_days, posts_per_day, base_price_usd,
                    discount_percent, final_price_usd, tier_category, description,
                    created_by, priority
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tier_data['name'],
                tier_data['duration_days'],
                tier_data.get('posts_per_day', 2),
                base_price,
                discount,
                final_price,
                tier_data.get('category', 'current'),
                tier_data.get('description', ''),
                tier_data.get('created_by', 0),
                tier_data.get('priority', 1)
            ))
            
            # Log pricing history
            tier_id = cursor.lastrowid
            await cursor.execute('''
                INSERT INTO pricing_history (item_type, item_id, new_price, change_reason, changed_by)
                VALUES (?, ?, ?, ?, ?)
            ''', ('tier', tier_id, final_price, 'Created new tier', tier_data.get('created_by', 0)))
            
            await connection.commit()
            logger.info(f"✅ Created pricing tier: {tier_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating pricing tier: {e}")
            return False
    
    async def update_pricing_tier(self, tier_id: int, updates: Dict) -> bool:
        """Update existing pricing tier"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            # Get old price for history
            await cursor.execute('SELECT final_price_usd FROM pricing_tiers WHERE id = ?', (tier_id,))
            old_price = (await cursor.fetchone())[0]
            
            # Build update query dynamically
            update_fields = []
            values = []
            
            for field, value in updates.items():
                if field in ['tier_name', 'duration_days', 'posts_per_day', 'base_price_usd', 
                           'discount_percent', 'description', 'priority', 'is_active']:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
            
            # Recalculate final price if base price or discount changed
            if 'base_price_usd' in updates or 'discount_percent' in updates:
                base_price = updates.get('base_price_usd', old_price)
                discount = updates.get('discount_percent', 0.0)
                final_price = base_price * (1 - discount / 100)
                update_fields.append("final_price_usd = ?")
                values.append(final_price)
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(tier_id)
            
            query = f"UPDATE pricing_tiers SET {', '.join(update_fields)} WHERE id = ?"
            await cursor.execute(query, values)
            
            # Log pricing history
            new_price = updates.get('final_price_usd', old_price)
            await cursor.execute('''
                INSERT INTO pricing_history (item_type, item_id, old_price, new_price, change_reason, changed_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('tier', tier_id, old_price, new_price, 'Updated tier', updates.get('updated_by', 0)))
            
            await connection.commit()
            logger.info(f"✅ Updated pricing tier ID: {tier_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating pricing tier: {e}")
            return False
    
    async def delete_pricing_tier(self, tier_id: int, admin_id: int) -> bool:
        """Delete pricing tier"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            # Soft delete - mark as inactive
            await cursor.execute('''
                UPDATE pricing_tiers SET is_active = 0, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (tier_id,))
            
            # Log deletion
            await cursor.execute('''
                INSERT INTO pricing_history (item_type, item_id, change_reason, changed_by)
                VALUES (?, ?, ?, ?)
            ''', ('tier', tier_id, 'Deleted tier', admin_id))
            
            await connection.commit()
            logger.info(f"✅ Deleted pricing tier ID: {tier_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting pricing tier: {e}")
            return False
    
    async def get_all_pricing_tiers(self, category: str = None, active_only: bool = True) -> List[Dict]:
        """Get all pricing tiers with optional filtering"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            query = "SELECT * FROM pricing_tiers"
            params = []
            
            conditions = []
            if active_only:
                conditions.append("is_active = 1")
            if category:
                conditions.append("tier_category = ?")
                params.append(category)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY priority ASC, duration_days ASC"
            
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Error getting pricing tiers: {e}")
            return []
    
    async def create_promotional_offer(self, offer_data: Dict) -> bool:
        """Create promotional offer"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            await cursor.execute('''
                INSERT INTO promotional_offers (
                    offer_name, offer_code, discount_type, discount_value,
                    min_duration, max_duration, usage_limit, start_date, end_date,
                    created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                offer_data['name'],
                offer_data.get('code', ''),
                offer_data.get('discount_type', 'percentage'),
                offer_data['discount_value'],
                offer_data.get('min_duration', 1),
                offer_data.get('max_duration', 90),
                offer_data.get('usage_limit', 0),
                offer_data.get('start_date'),
                offer_data.get('end_date'),
                offer_data.get('created_by', 0)
            ))
            
            await connection.commit()
            logger.info(f"✅ Created promotional offer: {offer_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating promotional offer: {e}")
            return False
    
    async def create_bundle_package(self, bundle_data: Dict) -> bool:
        """Create bundle package"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            original_price = bundle_data['original_price']
            bundle_price = bundle_data['bundle_price']
            savings = original_price - bundle_price
            
            await cursor.execute('''
                INSERT INTO bundle_packages (
                    bundle_name, bundle_description, total_days, total_posts,
                    original_price, bundle_price, savings_amount, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bundle_data['name'],
                bundle_data.get('description', ''),
                bundle_data['total_days'],
                bundle_data['total_posts'],
                original_price,
                bundle_price,
                savings,
                bundle_data.get('created_by', 0)
            ))
            
            await connection.commit()
            logger.info(f"✅ Created bundle package: {bundle_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating bundle package: {e}")
            return False
    
    async def get_pricing_analytics(self) -> Dict:
        """Get pricing analytics and statistics"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            analytics = {}
            
            # Most popular tiers
            await cursor.execute('''
                SELECT pt.tier_name, pa.selection_count, pa.revenue_generated
                FROM pricing_tiers pt
                LEFT JOIN pricing_analytics pa ON pt.id = pa.tier_id
                WHERE pt.is_active = 1
                ORDER BY pa.selection_count DESC
                LIMIT 5
            ''')
            analytics['popular_tiers'] = await cursor.fetchall()
            
            # Revenue by tier
            await cursor.execute('''
                SELECT tier_category, SUM(COALESCE(pa.revenue_generated, 0)) as total_revenue
                FROM pricing_tiers pt
                LEFT JOIN pricing_analytics pa ON pt.id = pa.tier_id
                WHERE pt.is_active = 1
                GROUP BY tier_category
            ''')
            analytics['revenue_by_category'] = await cursor.fetchall()
            
            # Pricing changes this month
            await cursor.execute('''
                SELECT COUNT(*) as changes_count
                FROM pricing_history
                WHERE changed_at >= datetime('now', '-30 days')
            ''')
            analytics['monthly_changes'] = (await cursor.fetchone())[0]
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting pricing analytics: {e}")
            return {}
    
    async def bulk_update_pricing(self, updates: List[Dict]) -> bool:
        """Bulk update multiple pricing tiers"""
        try:
            connection = await db.get_connection()
            cursor = await connection.cursor()
            
            for update in updates:
                tier_id = update['tier_id']
                new_data = update['updates']
                
                # Update tier
                await self.update_pricing_tier(tier_id, new_data)
            
            await connection.commit()
            logger.info(f"✅ Bulk updated {len(updates)} pricing tiers")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error in bulk pricing update: {e}")
            return False
    
    def format_pricing_display(self, tiers: List[Dict]) -> str:
        """Format pricing tiers for display"""
        if not tiers:
            return "No pricing tiers found."
        
        text = "<b>📊 Current Pricing Structure</b>\n\n"
        
        for tier in tiers:
            discount_text = f" (-{tier['discount_percent']}%)" if tier['discount_percent'] > 0 else ""
            status = "✅" if tier['is_active'] else "❌"
            
            text += f"{status} <b>{tier['tier_name']}</b>\n"
            text += f"   • Duration: {tier['duration_days']} days\n"
            text += f"   • Posts/Day: {tier['posts_per_day']}\n"
            text += f"   • Price: ${tier['final_price_usd']:.2f}{discount_text}\n"
            text += f"   • Category: {tier['tier_category']}\n\n"
        
        return text

# Global instance
pricing_manager = AdvancedPricingManager()