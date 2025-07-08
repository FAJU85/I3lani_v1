"""
Content Moderation System for I3lani Bot
Six-strike policy with progressive violation handling
Compliance with Telegram rules, international regulations, ethical standards, human rights, and Saudi Arabian regulations
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database
from languages import get_text

logger = logging.getLogger(__name__)

class ContentModerationSystem:
    """Comprehensive content moderation with six-strike policy"""
    
    def __init__(self, database: Database, bot):
        self.db = database
        self.bot = bot
        
        # Violation categories and patterns
        self.violation_patterns = {
            'hate_speech': [
                r'\b(hate|kill|murder|terrorism|terrorist)\b',
                r'\b(racist|nazi|fascist|supremacist)\b',
                r'\b(jihad|extremist|radical|militant)\b'
            ],
            'adult_content': [
                r'\b(porn|sex|adult|xxx|nude|naked)\b',
                r'\b(escort|prostitute|hookup|dating)\b',
                r'\b(18\+|mature|explicit)\b'
            ],
            'illegal_content': [
                r'\b(drugs|marijuana|cocaine|heroin|methamphetamine)\b',
                r'\b(weapons|guns|firearms|explosives|bombs)\b',
                r'\b(piracy|cracked|hacked|stolen)\b',
                r'\b(gambling|casino|betting|lottery)\b'
            ],
            'fraud_scam': [
                r'\b(scam|fraud|fake|phishing|ponzi)\b',
                r'\b(get rich quick|easy money|guaranteed profit)\b',
                r'\b(cryptocurrency scam|bitcoin scam|investment fraud)\b'
            ],
            'spam': [
                r'\b(buy now|click here|limited time|act now)\b',
                r'\b(free money|free gift|winner|congratulations)\b',
                r'(!!!|###|\$\$\$|@@@)'
            ],
            'violence': [
                r'\b(violence|violent|assault|attack|fight)\b',
                r'\b(blood|gore|torture|abuse|harm)\b',
                r'\b(suicide|self harm|cutting|depression)\b'
            ],
            'discrimination': [
                r'\b(discrimination|racist|sexist|homophobic)\b',
                r'\b(religion hate|ethnic cleansing|genocide)\b',
                r'\b(minority attack|cultural hate)\b'
            ],
            'saudi_specific': [
                r'\b(alcohol|beer|wine|whiskey|vodka)\b',
                r'\b(pork|bacon|ham|pig meat)\b',
                r'\b(anti-islamic|anti-muslim|blasphemy)\b',
                r'\b(political opposition|regime change|revolution)\b'
            ]
        }
        
        # Violation severity levels
        self.severity_levels = {
            'low': ['spam', 'minor_policy'],
            'medium': ['adult_content', 'fraud_scam', 'copyright'],
            'high': ['hate_speech', 'violence', 'discrimination', 'illegal_content'],
            'critical': ['terrorism', 'child_exploitation', 'saudi_specific']
        }

    async def moderate_content(self, user_id: int, order_id: str, content_type: str, 
                             content_text: str = "", media_caption: str = "") -> Dict:
        """
        Moderate content with six-strike policy
        Returns: {'approved': bool, 'violations': list, 'strikes': int, 'warning': str}
        """
        try:
            # Check if user is already banned
            is_banned = await self.db.is_user_banned(user_id)
            if is_banned:
                return {
                    'approved': False,
                    'violations': ['user_banned'],
                    'strikes': 6,
                    'warning': 'User is permanently banned from advertising'
                }
            
            # Analyze content for violations
            violations = await self.analyze_content(content_text, media_caption)
            
            if not violations:
                # Content is clean - approve
                await self.log_moderation_action(user_id, order_id, 'approved', [])
                return {
                    'approved': True,
                    'violations': [],
                    'strikes': 0,
                    'warning': ''
                }
            
            # Content has violations - apply strike system
            current_strikes = await self.get_user_strikes(user_id)
            new_strikes = current_strikes + 1
            
            # Update user strikes
            await self.record_violation(user_id, order_id, violations, new_strikes)
            
            if new_strikes >= 6:
                # Sixth strike - permanent ban
                await self.ban_user(user_id, 'Six strikes violation policy')
                await self.cancel_order_no_compensation(order_id)
                
                return {
                    'approved': False,
                    'violations': violations,
                    'strikes': new_strikes,
                    'warning': 'Ad canceled - no compensation. User permanently banned after 6 violations.'
                }
            else:
                # Warning and opportunity to edit
                warning_msg = await self.generate_warning_message(violations, new_strikes)
                return {
                    'approved': False,
                    'violations': violations,
                    'strikes': new_strikes,
                    'warning': warning_msg
                }
                
        except Exception as e:
            logger.error(f"Content moderation error: {e}")
            return {
                'approved': False,
                'violations': ['system_error'],
                'strikes': 0,
                'warning': 'Technical error during content review'
            }

    async def analyze_content(self, content_text: str, media_caption: str = "") -> List[str]:
        """Analyze content for policy violations"""
        violations = []
        full_text = f"{content_text} {media_caption}".lower()
        
        # Check against violation patterns
        for category, patterns in self.violation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    if category not in violations:
                        violations.append(category)
        
        # Additional checks for Saudi Arabian compliance
        violations.extend(await self.check_saudi_compliance(full_text))
        
        # Check for human rights violations
        violations.extend(await self.check_human_rights_compliance(full_text))
        
        # Check international standards
        violations.extend(await self.check_international_standards(full_text))
        
        return list(set(violations))  # Remove duplicates

    async def check_saudi_compliance(self, content: str) -> List[str]:
        """Check compliance with Saudi Arabian regulations"""
        violations = []
        
        # Religious compliance
        if any(word in content for word in ['anti-islamic', 'blasphemy', 'haram promotion']):
            violations.append('religious_violation')
        
        # Cultural compliance
        if any(word in content for word in ['alcohol', 'pork', 'gambling']):
            violations.append('cultural_violation')
        
        # Political compliance
        if any(word in content for word in ['regime change', 'political opposition', 'revolution']):
            violations.append('political_violation')
        
        return violations

    async def check_human_rights_compliance(self, content: str) -> List[str]:
        """Check compliance with human rights standards"""
        violations = []
        
        # Check for human trafficking
        if any(word in content for word in ['human trafficking', 'forced labor', 'slavery']):
            violations.append('human_rights_violation')
        
        # Check for child exploitation
        if any(word in content for word in ['child labor', 'child exploitation', 'underage']):
            violations.append('child_rights_violation')
        
        # Check for discrimination
        if any(word in content for word in ['racial discrimination', 'gender discrimination', 'religious persecution']):
            violations.append('discrimination_violation')
        
        return violations

    async def check_international_standards(self, content: str) -> List[str]:
        """Check compliance with international regulations"""
        violations = []
        
        # GDPR compliance
        if any(word in content for word in ['collect personal data', 'sell personal info', 'data breach']):
            violations.append('privacy_violation')
        
        # Financial regulations
        if any(word in content for word in ['money laundering', 'tax evasion', 'financial fraud']):
            violations.append('financial_violation')
        
        # Copyright compliance
        if any(word in content for word in ['pirated content', 'copyright infringement', 'stolen content']):
            violations.append('copyright_violation')
        
        return violations

    async def generate_warning_message(self, violations: List[str], strikes: int) -> str:
        """Generate warning message based on violations and strikes"""
        violation_descriptions = {
            'hate_speech': 'Hate speech or discriminatory content',
            'adult_content': 'Adult or sexual content',
            'illegal_content': 'Illegal activities or substances',
            'fraud_scam': 'Fraudulent or scam content',
            'spam': 'Spam or excessive promotional content',
            'violence': 'Violent or harmful content',
            'discrimination': 'Discriminatory content',
            'saudi_specific': 'Content violating Saudi Arabian regulations',
            'religious_violation': 'Religious compliance violation',
            'cultural_violation': 'Cultural compliance violation',
            'political_violation': 'Political content violation',
            'human_rights_violation': 'Human rights violation',
            'child_rights_violation': 'Child rights violation',
            'privacy_violation': 'Privacy/data protection violation',
            'financial_violation': 'Financial regulation violation',
            'copyright_violation': 'Copyright infringement'
        }
        
        warning = f"⚠️ CONTENT VIOLATION WARNING (Strike {strikes}/6)\n\n"
        warning += "Your ad has been rejected for the following violations:\n"
        
        for violation in violations:
            desc = violation_descriptions.get(violation, violation.replace('_', ' ').title())
            warning += f"• {desc}\n"
        
        warning += f"\n📝 You have {6 - strikes} chances remaining to edit your ad.\n"
        warning += "Please review our Terms of Use and Publishing Rules:\n"
        warning += "• Telegram Community Guidelines\n"
        warning += "• International Regulations\n"
        warning += "• Ethical Standards\n"
        warning += "• Human Rights Compliance\n"
        warning += "• Saudi Arabian Regulations\n\n"
        
        if strikes == 5:
            warning += "🚨 FINAL WARNING: Next violation will result in permanent ban and ad cancellation without compensation."
        else:
            warning += "✏️ Click 'Edit Ad' to modify your content and resubmit for review."
        
        return warning

    async def get_user_strikes(self, user_id: int) -> int:
        """Get current strike count for user"""
        try:
            async with self.db.get_connection() as conn:
                query = """
                SELECT strikes FROM user_moderation_status 
                WHERE user_id = ? AND status != 'banned'
                """
                async with conn.execute(query, (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error getting user strikes: {e}")
            return 0

    async def record_violation(self, user_id: int, order_id: str, violations: List[str], strikes: int):
        """Record violation in database"""
        try:
            async with self.db.get_connection() as conn:
                # Create tables if not exist
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_moderation_status (
                        user_id INTEGER PRIMARY KEY,
                        strikes INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'active',
                        last_violation DATETIME DEFAULT CURRENT_TIMESTAMP,
                        total_violations INTEGER DEFAULT 0
                    )
                """)
                
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS content_violations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        order_id TEXT NOT NULL,
                        violations TEXT NOT NULL,
                        strike_number INTEGER NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        action_taken TEXT DEFAULT 'warning'
                    )
                """)
                
                # Update user moderation status
                await conn.execute("""
                    INSERT OR REPLACE INTO user_moderation_status 
                    (user_id, strikes, status, last_violation, total_violations)
                    VALUES (?, ?, 'active', CURRENT_TIMESTAMP, 
                           COALESCE((SELECT total_violations FROM user_moderation_status WHERE user_id = ?), 0) + 1)
                """, (user_id, strikes, user_id))
                
                # Record specific violation
                await conn.execute("""
                    INSERT INTO content_violations 
                    (user_id, order_id, violations, strike_number)
                    VALUES (?, ?, ?, ?)
                """, (user_id, order_id, ','.join(violations), strikes))
                
                await conn.commit()
                
        except Exception as e:
            logger.error(f"Error recording violation: {e}")

    async def ban_user(self, user_id: int, reason: str):
        """Ban user permanently"""
        try:
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    UPDATE user_moderation_status 
                    SET status = 'banned', last_violation = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (user_id,))
                
                await conn.execute("""
                    INSERT OR REPLACE INTO banned_users 
                    (user_id, reason, banned_at, status)
                    VALUES (?, ?, CURRENT_TIMESTAMP, 'permanently_banned')
                """, (user_id, reason))
                
                await conn.commit()
                
        except Exception as e:
            logger.error(f"Error banning user: {e}")

    async def cancel_order_no_compensation(self, order_id: str):
        """Cancel order without compensation"""
        try:
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    UPDATE orders 
                    SET status = 'cancelled_no_compensation', 
                        cancellation_reason = 'Six strikes violation policy',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (order_id,))
                
                await conn.commit()
                
        except Exception as e:
            logger.error(f"Error canceling order: {e}")

    async def log_moderation_action(self, user_id: int, order_id: str, action: str, violations: List[str]):
        """Log moderation action"""
        try:
            async with self.db.get_connection() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS moderation_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        order_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        violations TEXT,
                        moderator_id INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await conn.execute("""
                    INSERT INTO moderation_logs 
                    (user_id, order_id, action, violations)
                    VALUES (?, ?, ?, ?)
                """, (user_id, order_id, action, ','.join(violations)))
                
                await conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging moderation action: {e}")

    async def create_edit_opportunity_keyboard(self, order_id: str, language: str = 'en') -> InlineKeyboardMarkup:
        """Create keyboard for editing opportunity"""
        keyboard = [
            [
                InlineKeyboardButton(
                    text=get_text('edit_ad', language, "✏️ Edit Ad"),
                    callback_data=f"edit_ad_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text('cancel_ad', language, "❌ Cancel Ad"),
                    callback_data=f"cancel_ad_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text('view_rules', language, "📋 View Rules"),
                    callback_data="view_publishing_rules"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text('back_to_main', language, "🏠 Main Menu"),
                    callback_data="back_to_main"
                )
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def send_violation_notification(self, user_id: int, order_id: str, 
                                        violations: List[str], strikes: int, language: str = 'en'):
        """Send violation notification to user"""
        try:
            warning_message = await self.generate_warning_message(violations, strikes)
            keyboard = await self.create_edit_opportunity_keyboard(order_id, language)
            
            await self.bot.send_message(
                chat_id=user_id,
                text=warning_message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error sending violation notification: {e}")

    async def get_moderation_statistics(self) -> Dict:
        """Get moderation statistics for admin"""
        try:
            async with self.db.get_connection() as conn:
                # Total violations
                async with conn.execute("SELECT COUNT(*) FROM content_violations") as cursor:
                    total_violations = (await cursor.fetchone())[0]
                
                # Banned users
                async with conn.execute("SELECT COUNT(*) FROM banned_users WHERE status = 'permanently_banned'") as cursor:
                    banned_users = (await cursor.fetchone())[0]
                
                # Active warnings
                async with conn.execute("SELECT COUNT(*) FROM user_moderation_status WHERE strikes > 0 AND status = 'active'") as cursor:
                    active_warnings = (await cursor.fetchone())[0]
                
                # Violations today
                async with conn.execute("SELECT COUNT(*) FROM content_violations WHERE DATE(created_at) = DATE('now')") as cursor:
                    violations_today = (await cursor.fetchone())[0]
                
                return {
                    'total_violations': total_violations,
                    'banned_users': banned_users,
                    'active_warnings': active_warnings,
                    'violations_today': violations_today
                }
                
        except Exception as e:
            logger.error(f"Error getting moderation statistics: {e}")
            return {
                'total_violations': 0,
                'banned_users': 0,
                'active_warnings': 0,
                'violations_today': 0
            }

def init_content_moderation(database: Database, bot):
    """Initialize content moderation system"""
    return ContentModerationSystem(database, bot)