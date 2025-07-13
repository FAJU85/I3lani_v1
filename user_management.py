"""
User Management System for I3lani Bot
Comprehensive user account management
"""

import asyncio
import aiosqlite
from datetime import datetime
from typing import Dict, List, Optional

class UserManagementSystem:
    def __init__(self):
        self.db_path = 'bot.db'
        
    async def get_user_stats(self) -> Dict:
        """Get comprehensive user statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Total users
                await cursor.execute("SELECT COUNT(*) FROM users")
                total_users = (await cursor.fetchone())[0]
                
                # Active users (with campaigns)
                await cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM campaigns 
                    WHERE status = 'active'
                """)
                active_users = (await cursor.fetchone())[0]
                
                # Paid users
                await cursor.execute("SELECT COUNT(DISTINCT user_id) FROM payments")
                paid_users = (await cursor.fetchone())[0]
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'paid_users': paid_users,
                    'conversion_rate': (paid_users / total_users * 100) if total_users > 0 else 0
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    async def get_user_details(self, user_id: int) -> Dict:
        """Get detailed user information"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # User info
                await cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                user = await cursor.fetchone()
                
                if not user:
                    return {'error': 'User not found'}
                
                # User campaigns
                await cursor.execute("SELECT COUNT(*) FROM campaigns WHERE user_id = ?", (user_id,))
                campaigns = (await cursor.fetchone())[0]
                
                # User payments
                await cursor.execute("SELECT COUNT(*) FROM payments WHERE user_id = ?", (user_id,))
                payments = (await cursor.fetchone())[0]
                
                return {
                    'user_id': user_id,
                    'campaigns': campaigns,
                    'payments': payments,
                    'status': 'active' if campaigns > 0 else 'inactive'
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    async def search_users(self, query: str) -> List[Dict]:
        """Search users by various criteria"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                await cursor.execute("""
                    SELECT user_id, first_name, last_name, username
                    FROM users 
                    WHERE first_name LIKE ? OR last_name LIKE ? OR username LIKE ?
                    LIMIT 20
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
                
                users = await cursor.fetchall()
                
                return [
                    {
                        'user_id': user[0],
                        'first_name': user[1],
                        'last_name': user[2],
                        'username': user[3]
                    }
                    for user in users
                ]
                
        except Exception as e:
            return []
    
    async def ban_user(self, user_id: int, reason: str) -> bool:
        """Ban a user"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                await cursor.execute("""
                    UPDATE users 
                    SET banned = 1, ban_reason = ?, ban_date = ?
                    WHERE user_id = ?
                """, (reason, datetime.now(), user_id))
                
                await conn.commit()
                return True
                
        except Exception as e:
            return False
    
    async def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                await cursor.execute("""
                    UPDATE users 
                    SET banned = 0, ban_reason = NULL, ban_date = NULL
                    WHERE user_id = ?
                """, (user_id,))
                
                await conn.commit()
                return True
                
        except Exception as e:
            return False

# Global instance
user_management = UserManagementSystem()
