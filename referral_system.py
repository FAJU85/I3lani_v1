"""
Referral System for I3lani Bot
Implements affiliate tracking, rewards, and friend discounts
"""

import hashlib
import base64
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from database import *
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class ReferralSystem:
    """Complete referral system with affiliate tracking and rewards"""
    
    def __init__(self):
        self.base_url = "https://t.me/I3lani_bot"
        self.friend_discount_percent = 5.0
        self.reward_free_days = 3
    
    def generate_referral_link(self, user_id: int) -> str:
        """Generate unique referral link for user"""
        # Create unique referral code based on user ID
        referral_code = self._generate_referral_code(user_id)
        return f"{self.base_url}?start=ref_{referral_code}"
    
    def _generate_referral_code(self, user_id: int) -> str:
        """Generate unique 8-character referral code"""
        # Create deterministic code based on user ID
        hash_input = f"i3lani_ref_{user_id}_{datetime.now().strftime('%Y%m')}"
        hash_object = hashlib.sha256(hash_input.encode())
        hash_hex = hash_object.hexdigest()
        
        # Convert to base36 for shorter code
        code = base64.b32encode(bytes.fromhex(hash_hex[:10])).decode()[:8]
        return code.upper()
    
    def decode_referral_code(self, code: str) -> Optional[int]:
        """Decode referral code to get referrer user ID"""
        try:
            # For now, we'll store the mapping in database
            # In production, implement proper encoding/decoding
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.referral_code == code).first()
                return user.id if user else None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error decoding referral code {code}: {e}")
            return None
    
    def track_referral(self, referrer_id: int, referee_id: int) -> bool:
        """Track new referral conversion"""
        try:
            db = SessionLocal()
            try:
                # Check if referral already exists
                existing = db.query(Referral).filter(
                    Referral.referrer_id == referrer_id,
                    Referral.referee_id == referee_id
                ).first()
                
                if existing:
                    return False
                
                # Create new referral record
                referral = Referral(
                    referrer_id=referrer_id,
                    referee_id=referee_id,
                    created_at=datetime.utcnow()
                )
                db.add(referral)
                
                # Update referee's referrer
                db.query(User).filter(User.id == referee_id).update({
                    'referrer_id': referrer_id
                })
                
                db.commit()
                logger.info(f"Referral tracked: {referrer_id} -> {referee_id}")
                return True
                
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error tracking referral: {e}")
            return False
    
    def apply_friend_discount(self, user_id: int) -> float:
        """Apply 5% friend discount if user was referred"""
        try:
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user and user.referrer_id:
                    return self.friend_discount_percent
                return 0.0
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error applying friend discount: {e}")
            return 0.0
    
    def calculate_rewards(self, referrer_id: int) -> Dict[str, int]:
        """Calculate rewards for referrer"""
        try:
            db = SessionLocal()
            try:
                # Count successful referrals (users who made at least one purchase)
                successful_referrals = db.query(func.count(Referral.id)).filter(
                    Referral.referrer_id == referrer_id,
                    Referral.reward_granted == True
                ).scalar()
                
                # Count pending referrals (users who signed up but haven't purchased)
                pending_referrals = db.query(func.count(Referral.id)).filter(
                    Referral.referrer_id == referrer_id,
                    Referral.reward_granted == False
                ).scalar()
                
                # Calculate free days earned
                free_days_earned = successful_referrals * self.reward_free_days
                
                return {
                    'successful_referrals': successful_referrals,
                    'pending_referrals': pending_referrals,
                    'free_days_earned': free_days_earned,
                    'total_referrals': successful_referrals + pending_referrals
                }
                
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error calculating rewards: {e}")
            return {'successful_referrals': 0, 'pending_referrals': 0, 'free_days_earned': 0, 'total_referrals': 0}
    
    def grant_referral_reward(self, referrer_id: int, referee_id: int) -> bool:
        """Grant reward when referred user makes first purchase"""
        try:
            db = SessionLocal()
            try:
                # Find the referral record
                referral = db.query(Referral).filter(
                    Referral.referrer_id == referrer_id,
                    Referral.referee_id == referee_id,
                    Referral.reward_granted == False
                ).first()
                
                if not referral:
                    return False
                
                # Mark reward as granted
                referral.reward_granted = True
                
                # Add free posting days to referrer
                referrer = db.query(User).filter(User.id == referrer_id).first()
                if referrer:
                    referrer.free_posts_remaining = (referrer.free_posts_remaining or 0) + self.reward_free_days
                
                db.commit()
                logger.info(f"Referral reward granted: {referrer_id} earned {self.reward_free_days} free days")
                return True
                
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error granting referral reward: {e}")
            return False
    
    def get_referral_statistics(self, user_id: int) -> Dict[str, any]:
        """Get comprehensive referral statistics for user"""
        try:
            db = SessionLocal()
            try:
                # Get user's referral code
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return {}
                
                # Ensure user has referral code
                if not user.referral_code:
                    user.referral_code = self._generate_referral_code(user_id)
                    db.commit()
                
                # Get referral statistics
                referrals = db.query(Referral).filter(Referral.referrer_id == user_id).all()
                
                stats = {
                    'referral_link': self.generate_referral_link(user_id),
                    'referral_code': user.referral_code,
                    'total_referrals': len(referrals),
                    'successful_referrals': len([r for r in referrals if r.reward_granted]),
                    'pending_referrals': len([r for r in referrals if not r.reward_granted]),
                    'free_days_earned': len([r for r in referrals if r.reward_granted]) * self.reward_free_days,
                    'free_days_remaining': user.free_posts_remaining or 0,
                    'total_earned': len([r for r in referrals if r.reward_granted]) * self.reward_free_days * 0.99,  # Estimate value
                    'recent_referrals': []
                }
                
                # Get recent referrals
                recent = db.query(Referral).filter(
                    Referral.referrer_id == user_id
                ).order_by(Referral.created_at.desc()).limit(5).all()
                
                for referral in recent:
                    referee = db.query(User).filter(User.id == referral.referee_id).first()
                    stats['recent_referrals'].append({
                        'username': referee.username if referee else 'Unknown',
                        'date': referral.created_at,
                        'rewarded': referral.reward_granted
                    })
                
                return stats
                
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting referral statistics: {e}")
            return {}
    
    def check_referral_eligibility(self, user_id: int) -> bool:
        """Check if user can use referral system"""
        try:
            db = SessionLocal()
            try:
                # Check if user already has a referrer
                user = db.query(User).filter(User.id == user_id).first()
                return user and not user.referrer_id
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error checking referral eligibility: {e}")
            return False
    
    def get_referral_leaderboard(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get top referrers leaderboard"""
        try:
            db = SessionLocal()
            try:
                # Get top referrers by successful referrals
                top_referrers = db.query(
                    User.id,
                    User.username,
                    func.count(Referral.id).label('referral_count')
                ).join(
                    Referral, User.id == Referral.referrer_id
                ).filter(
                    Referral.reward_granted == True
                ).group_by(
                    User.id, User.username
                ).order_by(
                    func.count(Referral.id).desc()
                ).limit(limit).all()
                
                leaderboard = []
                for idx, (user_id, username, count) in enumerate(top_referrers, 1):
                    leaderboard.append({
                        'rank': idx,
                        'username': username or f"User_{user_id}",
                        'referrals': count,
                        'rewards_earned': count * self.reward_free_days
                    })
                
                return leaderboard
                
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting referral leaderboard: {e}")
            return []

# Add referral table to database if not exists
class Referral(Base):
    __tablename__ = 'referrals'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    referrer_id = Column(Integer, ForeignKey('users.id'))
    referee_id = Column(Integer, ForeignKey('users.id'))
    reward_granted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    referrer = relationship("User", foreign_keys=[referrer_id])
    referee = relationship("User", foreign_keys=[referee_id])

# Update User model to include referral fields
def update_user_model():
    """Update User model to include referral fields"""
    try:
        db = SessionLocal()
        try:
            # Add referral_code column if it doesn't exist
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code VARCHAR(10)"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS referrer_id INTEGER"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS free_posts_remaining INTEGER DEFAULT 0"))
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error updating user model: {e}")