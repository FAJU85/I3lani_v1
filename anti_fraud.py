"""
Anti-Fraud Protection System for I3lani Bot
Prevents affiliate marketers and bots from abusing the referral system
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
import hashlib
import random

logger = logging.getLogger(__name__)

class AntiFraudSystem:
    """Comprehensive anti-fraud protection for partner/referral system"""
    
    def __init__(self, db):
        self.db = db
        self.fraud_cache = {}  # In-memory cache for fast checks
        self.behavior_patterns = {}  # Track user behavior patterns
        
        # Fraud detection thresholds
        self.SUSPICIOUS_THRESHOLDS = {
            'referrals_per_hour': 5,  # Max referrals per hour
            'referrals_per_day': 20,  # Max referrals per day
            'min_referral_gap': 30,   # Min seconds between referrals
            'max_same_ip_refs': 3,    # Max refs from same IP
            'min_user_activity': 5,   # Min actions before referral validity
            'username_similarity': 0.8,  # Max username similarity threshold
            'rapid_sequence_limit': 3,    # Max rapid sequential actions
        }
        
        # Bot detection patterns
        self.BOT_PATTERNS = {
            'rapid_actions': 10,      # Actions per minute
            'identical_timing': 3,    # Same timing patterns
            'predictable_usernames': True,  # Sequential/pattern usernames
            'no_profile_photos': True,      # Missing profile photos
            'instant_referrals': True,      # Immediate referral after joining
        }

    async def validate_referral(self, referrer_id: int, referred_id: int, referred_user_data: dict) -> dict:
        """Comprehensive referral validation with fraud detection"""
        validation_result = {
            'valid': True,
            'risk_score': 0,
            'flags': [],
            'block_reason': None
        }
        
        try:
            # 1. Check referral rate limits
            rate_check = await self._check_referral_rates(referrer_id)
            if not rate_check['valid']:
                validation_result['valid'] = False
                validation_result['risk_score'] += 50
                validation_result['flags'].extend(rate_check['flags'])
                validation_result['block_reason'] = 'Rate limit exceeded'
            
            # 2. Detect bot-like behavior
            bot_check = await self._detect_bot_behavior(referred_id, referred_user_data)
            if bot_check['is_bot']:
                validation_result['valid'] = False
                validation_result['risk_score'] += 80
                validation_result['flags'].extend(bot_check['flags'])
                validation_result['block_reason'] = 'Bot account detected'
            
            # 3. Check user activity patterns
            activity_check = await self._validate_user_activity(referred_id)
            if not activity_check['valid']:
                validation_result['risk_score'] += 30
                validation_result['flags'].extend(activity_check['flags'])
            
            # 4. Cross-reference with known fraud patterns
            pattern_check = await self._check_fraud_patterns(referrer_id, referred_id, referred_user_data)
            if pattern_check['suspicious']:
                validation_result['risk_score'] += pattern_check['risk_score']
                validation_result['flags'].extend(pattern_check['flags'])
                
                if pattern_check['risk_score'] > 70:
                    validation_result['valid'] = False
                    validation_result['block_reason'] = 'Fraud pattern detected'
            
            # 5. Implement machine learning-based detection
            ml_check = await self._ml_fraud_detection(referrer_id, referred_id, referred_user_data)
            validation_result['risk_score'] += ml_check['risk_score']
            validation_result['flags'].extend(ml_check['flags'])
            
            # Log suspicious activity
            if validation_result['risk_score'] > 50:
                await self._log_suspicious_activity(referrer_id, referred_id, validation_result)
            
            # Auto-block high risk
            if validation_result['risk_score'] > 80:
                validation_result['valid'] = False
                await self._flag_user_for_review(referrer_id, validation_result)
                
        except Exception as e:
            logger.error(f"Fraud validation error: {e}")
            validation_result['valid'] = False
            validation_result['block_reason'] = 'System error during validation'
        
        return validation_result

    async def _check_referral_rates(self, referrer_id: int) -> dict:
        """Check if user is exceeding referral rate limits"""
        result = {'valid': True, 'flags': []}
        
        try:
            # Get recent referrals
            recent_refs = await self.db.get_user_referrals_timeframe(referrer_id, hours=24)
            hourly_refs = await self.db.get_user_referrals_timeframe(referrer_id, hours=1)
            
            # Check daily limit
            if len(recent_refs) >= self.SUSPICIOUS_THRESHOLDS['referrals_per_day']:
                result['valid'] = False
                result['flags'].append('Daily referral limit exceeded')
            
            # Check hourly limit
            if len(hourly_refs) >= self.SUSPICIOUS_THRESHOLDS['referrals_per_hour']:
                result['valid'] = False
                result['flags'].append('Hourly referral limit exceeded')
            
            # Check referral gaps
            if len(recent_refs) > 1:
                time_gaps = []
                for i in range(1, len(recent_refs)):
                    gap = recent_refs[i-1]['created_at'] - recent_refs[i]['created_at']
                    time_gaps.append(gap.total_seconds())
                
                if any(gap < self.SUSPICIOUS_THRESHOLDS['min_referral_gap'] for gap in time_gaps):
                    result['flags'].append('Referrals too rapid')
                    
        except Exception as e:
            logger.error(f"Rate check error: {e}")
            result['flags'].append('Rate check failed')
        
        return result

    async def _detect_bot_behavior(self, user_id: int, user_data: dict) -> dict:
        """Detect if user exhibits bot-like behavior"""
        result = {'is_bot': False, 'flags': [], 'confidence': 0}
        
        try:
            # Check username patterns
            username = user_data.get('username', '')
            if username:
                if self._is_generated_username(username):
                    result['confidence'] += 30
                    result['flags'].append('Generated username pattern')
            
            # Check profile completeness
            if not user_data.get('first_name'):
                result['confidence'] += 20
                result['flags'].append('Missing first name')
            
            if not user_data.get('profile_photo'):
                result['confidence'] += 15
                result['flags'].append('No profile photo')
            
            # Check account age (if available)
            if user_data.get('account_age_days', 999) < 7:
                result['confidence'] += 25
                result['flags'].append('Very new account')
            
            # Check activity patterns
            activity_patterns = await self._analyze_activity_patterns(user_id)
            if activity_patterns['suspicious']:
                result['confidence'] += activity_patterns['score']
                result['flags'].extend(activity_patterns['flags'])
            
            # Check for immediate referral registration
            if await self._is_instant_referral(user_id):
                result['confidence'] += 40
                result['flags'].append('Instant referral registration')
            
            # Determine if likely bot
            if result['confidence'] > 60:
                result['is_bot'] = True
                
        except Exception as e:
            logger.error(f"Bot detection error: {e}")
            result['flags'].append('Bot detection failed')
        
        return result

    async def _validate_user_activity(self, user_id: int) -> dict:
        """Validate user has genuine activity before referral rewards"""
        result = {'valid': True, 'flags': []}
        
        try:
            # Check user interactions
            interactions = await self.db.get_user_interactions(user_id)
            
            if len(interactions) < self.SUSPICIOUS_THRESHOLDS['min_user_activity']:
                result['valid'] = False
                result['flags'].append('Insufficient user activity')
            
            # Check for genuine engagement
            if not await self._has_genuine_engagement(user_id):
                result['flags'].append('No genuine engagement detected')
            
        except Exception as e:
            logger.error(f"Activity validation error: {e}")
            result['flags'].append('Activity validation failed')
        
        return result

    async def _check_fraud_patterns(self, referrer_id: int, referred_id: int, user_data: dict) -> dict:
        """Check against known fraud patterns"""
        result = {'suspicious': False, 'risk_score': 0, 'flags': []}
        
        try:
            # Check for username farming patterns
            similar_users = await self._find_similar_usernames(user_data.get('username', ''))
            if len(similar_users) > 5:
                result['risk_score'] += 30
                result['flags'].append('Username farming pattern')
            
            # Check referrer's history
            referrer_history = await self.db.get_referrer_fraud_history(referrer_id)
            if referrer_history['previous_blocks'] > 2:
                result['risk_score'] += 40
                result['flags'].append('Referrer has fraud history')
            
            # Check for coordinated account creation
            if await self._detect_coordinated_creation(referred_id, user_data):
                result['risk_score'] += 50
                result['flags'].append('Coordinated account creation')
            
            if result['risk_score'] > 30:
                result['suspicious'] = True
                
        except Exception as e:
            logger.error(f"Pattern check error: {e}")
            result['flags'].append('Pattern check failed')
        
        return result

    async def _ml_fraud_detection(self, referrer_id: int, referred_id: int, user_data: dict) -> dict:
        """Machine learning-based fraud detection"""
        result = {'risk_score': 0, 'flags': []}
        
        try:
            # Feature extraction
            features = await self._extract_features(referrer_id, referred_id, user_data)
            
            # Simple rule-based ML simulation (replace with actual ML model)
            risk_factors = 0
            
            # Username entropy check
            username = user_data.get('username', '')
            if username and self._calculate_entropy(username) < 2.5:
                risk_factors += 1
                result['flags'].append('Low username entropy')
            
            # Timing analysis
            if await self._suspicious_timing_pattern(referrer_id):
                risk_factors += 2
                result['flags'].append('Suspicious timing pattern')
            
            # Network analysis
            if await self._network_fraud_detection(referrer_id, referred_id):
                risk_factors += 3
                result['flags'].append('Network fraud indicators')
            
            # Convert risk factors to score
            result['risk_score'] = min(risk_factors * 15, 60)
            
        except Exception as e:
            logger.error(f"ML detection error: {e}")
            result['flags'].append('ML detection failed')
        
        return result

    def _is_generated_username(self, username: str) -> bool:
        """Detect generated usernames"""
        patterns = [
            r'^user\d+$',           # user123
            r'^[a-z]+\d{3,}$',      # name123456
            r'^[a-z]{1,3}_[a-z]{1,3}_\d+$',  # ab_cd_123
            r'^\w+_bot$',           # something_bot
        ]
        
        import re
        for pattern in patterns:
            if re.match(pattern, username.lower()):
                return True
        return False

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0
        
        import math
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        entropy = 0
        text_len = len(text)
        for count in char_counts.values():
            probability = count / text_len
            entropy -= probability * math.log2(probability)
        
        return entropy

    async def _analyze_activity_patterns(self, user_id: int) -> dict:
        """Analyze user activity for bot patterns"""
        result = {'suspicious': False, 'score': 0, 'flags': []}
        
        try:
            # Get user actions
            actions = await self.db.get_user_actions(user_id, limit=50)
            
            if not actions:
                return result
            
            # Check for identical timing intervals
            if len(actions) > 3:
                intervals = []
                for i in range(1, len(actions)):
                    interval = actions[i-1]['timestamp'] - actions[i]['timestamp']
                    intervals.append(interval.total_seconds())
                
                # Check for suspiciously regular intervals
                if len(set(intervals)) == 1 and len(intervals) > 2:
                    result['score'] += 40
                    result['flags'].append('Identical timing intervals')
            
            # Check for rapid sequential actions
            rapid_count = 0
            for i in range(1, len(actions)):
                if actions[i-1]['timestamp'] - actions[i]['timestamp'] < timedelta(seconds=1):
                    rapid_count += 1
            
            if rapid_count > self.BOT_PATTERNS['rapid_actions']:
                result['score'] += 30
                result['flags'].append('Too many rapid actions')
            
            if result['score'] > 20:
                result['suspicious'] = True
                
        except Exception as e:
            logger.error(f"Activity pattern analysis error: {e}")
            
        return result

    async def _is_instant_referral(self, user_id: int) -> bool:
        """Check if user registered via referral immediately after joining"""
        try:
            user_created = await self.db.get_user_creation_time(user_id)
            referral_time = await self.db.get_referral_registration_time(user_id)
            
            if user_created and referral_time:
                time_diff = referral_time - user_created
                return time_diff.total_seconds() < 10  # Less than 10 seconds
                
        except Exception as e:
            logger.error(f"Instant referral check error: {e}")
            
        return False

    async def _has_genuine_engagement(self, user_id: int) -> bool:
        """Check if user has genuine engagement patterns"""
        try:
            # Check various engagement metrics
            actions = await self.db.get_user_actions(user_id)
            
            # Look for diverse action types
            action_types = set(action['type'] for action in actions)
            if len(action_types) < 3:
                return False
            
            # Check for message interactions (not just button clicks)
            has_messages = any(action['type'] == 'message' for action in actions)
            if not has_messages:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Engagement check error: {e}")
            return False

    async def _find_similar_usernames(self, username: str) -> List[dict]:
        """Find similar usernames in database"""
        try:
            if not username:
                return []
            
            similar_users = []
            all_users = await self.db.get_all_usernames()
            
            for user in all_users:
                similarity = self._calculate_similarity(username, user['username'])
                if similarity > self.SUSPICIOUS_THRESHOLDS['username_similarity']:
                    similar_users.append(user)
            
            return similar_users
            
        except Exception as e:
            logger.error(f"Similar username search error: {e}")
            return []

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using Levenshtein distance"""
        if not str1 or not str2:
            return 0
        
        # Simple similarity calculation
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1
        
        # Calculate edit distance
        edit_distance = self._levenshtein_distance(str1.lower(), str2.lower())
        similarity = 1 - (edit_distance / max_len)
        
        return similarity

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    async def _detect_coordinated_creation(self, user_id: int, user_data: dict) -> bool:
        """Detect coordinated account creation patterns"""
        try:
            # Check for multiple accounts created in short timeframe
            recent_accounts = await self.db.get_recent_account_creations(hours=1)
            
            if len(recent_accounts) > 10:  # More than 10 accounts in 1 hour
                return True
            
            # Check for similar naming patterns
            similar_patterns = 0
            username = user_data.get('username', '')
            if username:
                for account in recent_accounts:
                    if self._has_similar_pattern(username, account['username']):
                        similar_patterns += 1
                
                if similar_patterns > 3:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Coordinated creation detection error: {e}")
            return False

    def _has_similar_pattern(self, username1: str, username2: str) -> bool:
        """Check if usernames follow similar patterns"""
        if not username1 or not username2:
            return False
        
        # Check for similar structures
        import re
        
        # Extract patterns (letters vs numbers)
        pattern1 = re.sub(r'[a-zA-Z]', 'L', re.sub(r'\d', 'N', username1))
        pattern2 = re.sub(r'[a-zA-Z]', 'L', re.sub(r'\d', 'N', username2))
        
        return pattern1 == pattern2

    async def _suspicious_timing_pattern(self, referrer_id: int) -> bool:
        """Detect suspicious timing patterns in referrals"""
        try:
            referrals = await self.db.get_user_referrals(referrer_id)
            
            if len(referrals) < 3:
                return False
            
            # Check for too regular intervals
            intervals = []
            for i in range(1, len(referrals)):
                interval = referrals[i-1]['created_at'] - referrals[i]['created_at']
                intervals.append(interval.total_seconds())
            
            # Check if intervals are suspiciously regular
            if len(set(intervals)) <= 2 and len(intervals) > 5:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Timing pattern analysis error: {e}")
            return False

    async def _network_fraud_detection(self, referrer_id: int, referred_id: int) -> bool:
        """Detect network-based fraud patterns"""
        try:
            # Check for circular referrals
            if await self._detect_circular_referrals(referrer_id, referred_id):
                return True
            
            # Check for referral farms
            if await self._detect_referral_farm(referrer_id):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Network fraud detection error: {e}")
            return False

    async def _detect_circular_referrals(self, referrer_id: int, referred_id: int) -> bool:
        """Detect circular referral patterns"""
        try:
            # Check if referred user has referred the referrer
            referred_refs = await self.db.get_user_referrals(referred_id)
            
            for ref in referred_refs:
                if ref['referred_user_id'] == referrer_id:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Circular referral detection error: {e}")
            return False

    async def _detect_referral_farm(self, referrer_id: int) -> bool:
        """Detect referral farming operations"""
        try:
            referrals = await self.db.get_user_referrals(referrer_id)
            
            # Check for signs of farming
            recent_refs = [r for r in referrals if 
                         datetime.now() - r['created_at'] < timedelta(days=1)]
            
            if len(recent_refs) > 20:  # More than 20 referrals in a day
                return True
            
            # Check for inactive referred users
            inactive_count = 0
            for ref in referrals[-10:]:  # Check last 10 referrals
                activity = await self.db.get_user_activity_count(ref['referred_user_id'])
                if activity < 3:  # Less than 3 actions
                    inactive_count += 1
            
            if inactive_count > 7:  # More than 70% inactive
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Referral farm detection error: {e}")
            return False

    async def _extract_features(self, referrer_id: int, referred_id: int, user_data: dict) -> dict:
        """Extract features for ML analysis"""
        features = {}
        
        try:
            # User features
            features['username_length'] = len(user_data.get('username', ''))
            features['has_first_name'] = bool(user_data.get('first_name'))
            features['has_last_name'] = bool(user_data.get('last_name'))
            features['has_username'] = bool(user_data.get('username'))
            features['has_profile_photo'] = bool(user_data.get('profile_photo'))
            
            # Timing features
            features['hour_of_day'] = datetime.now().hour
            features['day_of_week'] = datetime.now().weekday()
            
            # Referrer features
            referrer_refs = await self.db.get_user_referrals(referrer_id)
            features['referrer_total_refs'] = len(referrer_refs)
            features['referrer_recent_refs'] = len([r for r in referrer_refs if 
                                                   datetime.now() - r['created_at'] < timedelta(hours=24)])
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return {}

    async def _log_suspicious_activity(self, referrer_id: int, referred_id: int, validation_result: dict):
        """Log suspicious activity for review"""
        try:
            log_entry = {
                'timestamp': datetime.now(),
                'referrer_id': referrer_id,
                'referred_id': referred_id,
                'risk_score': validation_result['risk_score'],
                'flags': validation_result['flags'],
                'block_reason': validation_result.get('block_reason'),
                'status': 'blocked' if not validation_result['valid'] else 'flagged'
            }
            
            await self.db.log_fraud_activity(log_entry)
            
            # Alert admins for high-risk cases
            if validation_result['risk_score'] > 70:
                await self._alert_admins(log_entry)
                
        except Exception as e:
            logger.error(f"Suspicious activity logging error: {e}")

    async def _flag_user_for_review(self, user_id: int, validation_result: dict):
        """Flag user for manual review"""
        try:
            await self.db.flag_user_for_review(
                user_id, 
                validation_result['risk_score'],
                validation_result['flags'],
                validation_result.get('block_reason')
            )
            
        except Exception as e:
            logger.error(f"User flagging error: {e}")

    async def _alert_admins(self, log_entry: dict):
        """Alert administrators about high-risk fraud attempts"""
        try:
            # Format alert message
            alert_message = f"""
🚨 **HIGH RISK FRAUD ALERT** 🚨

**Risk Score:** {log_entry['risk_score']}/100
**Referrer ID:** {log_entry['referrer_id']}
**Referred ID:** {log_entry['referred_id']}
**Flags:** {', '.join(log_entry['flags'])}
**Status:** {log_entry['status'].upper()}

**Action Required:** Manual review recommended
**Time:** {log_entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            # Send to admin channel (implement based on your admin system)
            await self.db.send_admin_alert(alert_message)
            
        except Exception as e:
            logger.error(f"Admin alert error: {e}")

    async def get_fraud_statistics(self) -> dict:
        """Get fraud detection statistics"""
        try:
            stats = await self.db.get_fraud_statistics()
            return {
                'total_blocked': stats.get('total_blocked', 0),
                'flagged_today': stats.get('flagged_today', 0),
                'risk_distribution': stats.get('risk_distribution', {}),
                'common_flags': stats.get('common_flags', []),
                'detection_rate': stats.get('detection_rate', 0)
            }
        except Exception as e:
            logger.error(f"Fraud statistics error: {e}")
            return {}

    async def review_flagged_user(self, user_id: int, admin_decision: str, notes: str = ""):
        """Admin review of flagged users"""
        try:
            await self.db.update_user_review_status(user_id, admin_decision, notes)
            
            if admin_decision == 'approved':
                # Unblock and process pending rewards
                await self.db.unblock_user(user_id)
                await self.db.process_pending_rewards(user_id)
            elif admin_decision == 'rejected':
                # Permanently block and remove rewards
                await self.db.permanently_block_user(user_id)
                await self.db.remove_fraudulent_rewards(user_id)
                
        except Exception as e:
            logger.error(f"User review error: {e}")