#!/usr/bin/env python3
"""
Post Identity System
Implements unique post IDs, campaign linking, and full metadata tracking
to ensure published content exactly matches user submissions
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PostMetadata:
    """Complete post metadata structure"""
    post_id: str
    campaign_id: str
    user_id: int
    advertiser_username: str
    creation_date: str
    content_text: str
    content_image: Optional[str] = None
    content_video: Optional[str] = None
    content_type: str = 'text'
    channel_count: int = 0
    publishing_days: int = 0
    posts_per_day: int = 0
    target_channels: List[str] = None
    total_reach: int = 0
    status: str = 'created'
    published_channels: List[str] = None
    verification_hash: str = ''

class PostIdentitySystem:
    """Comprehensive post identity and content integrity system"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        
    async def init_tables(self):
        """Initialize post identity tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create post_identity table for full metadata tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_identity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT UNIQUE NOT NULL,
                    campaign_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    advertiser_username TEXT NOT NULL,
                    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_text TEXT NOT NULL,
                    content_image TEXT,
                    content_video TEXT,
                    content_type TEXT DEFAULT 'text',
                    channel_count INTEGER DEFAULT 0,
                    publishing_days INTEGER DEFAULT 0,
                    posts_per_day INTEGER DEFAULT 0,
                    target_channels TEXT,
                    total_reach INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'created',
                    published_channels TEXT,
                    verification_hash TEXT,
                    metadata_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create post_publishing_log for tracking actual publications
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_publishing_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    channel_name TEXT,
                    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_id INTEGER,
                    content_hash TEXT,
                    publishing_status TEXT DEFAULT 'success',
                    error_message TEXT,
                    verification_status TEXT DEFAULT 'pending',
                    FOREIGN KEY (post_id) REFERENCES post_identity (post_id)
                );
            """)
            
            # Create content_verification table for integrity checks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_verification (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT NOT NULL,
                    original_content_hash TEXT NOT NULL,
                    published_content_hash TEXT,
                    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    match_status TEXT DEFAULT 'pending',
                    discrepancy_details TEXT,
                    FOREIGN KEY (post_id) REFERENCES post_identity (post_id)
                );
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_identity_campaign ON post_identity(campaign_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_identity_user ON post_identity(user_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_publishing_log_post ON post_publishing_log(post_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_verification_post ON content_verification(post_id);")
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Post Identity System tables initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing Post Identity System: {e}")
            return False
    
    def generate_post_id(self) -> str:
        """Generate unique post ID in format Ad00, Ad01, etc."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the highest post ID number
            cursor.execute("SELECT post_id FROM post_identity WHERE post_id LIKE 'Ad%' ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            
            if result:
                last_id = result[0]
                # Extract number from AdXX format
                try:
                    last_num = int(last_id[2:])
                    next_num = last_num + 1
                except ValueError:
                    next_num = 1
            else:
                next_num = 1
            
            conn.close()
            
            # Format as Ad00, Ad01, etc.
            post_id = f"Ad{next_num:02d}"
            
            return post_id
            
        except Exception as e:
            logger.error(f"❌ Error generating post ID: {e}")
            return f"Ad{datetime.now().strftime('%H%M%S')}"
    
    async def create_post_identity(self, campaign_id: str, user_id: int, 
                                 advertiser_username: str, content_data: Dict[str, Any],
                                 campaign_details: Dict[str, Any]) -> str:
        """Create complete post identity with full metadata - ONE POST PER CAMPAIGN"""
        try:
            # Check if post identity already exists for this campaign
            existing_post = await self.get_post_for_campaign(campaign_id)
            if existing_post:
                logger.info(f"✅ Post identity already exists for campaign {campaign_id}: {existing_post.post_id}")
                return existing_post.post_id
            
            post_id = self.generate_post_id()
            
            # Extract content information
            content_text = content_data.get('content', content_data.get('ad_content', ''))
            content_image = content_data.get('media_url', content_data.get('image_url'))
            content_video = content_data.get('video_url')
            content_type = content_data.get('content_type', 'text')
            
            # Extract campaign details
            target_channels = campaign_details.get('selected_channels', [])
            channel_count = len(target_channels)
            publishing_days = campaign_details.get('duration_days', 0)
            posts_per_day = campaign_details.get('posts_per_day', 0)
            total_reach = campaign_details.get('total_reach', 0)
            
            # Create verification hash for content integrity
            import hashlib
            content_for_hash = f"{content_text}{content_image or ''}{content_video or ''}"
            verification_hash = hashlib.md5(content_for_hash.encode()).hexdigest()
            
            # Create metadata object
            metadata = PostMetadata(
                post_id=post_id,
                campaign_id=campaign_id,
                user_id=user_id,
                advertiser_username=advertiser_username,
                creation_date=datetime.now().isoformat(),
                content_text=content_text,
                content_image=content_image,
                content_video=content_video,
                content_type=content_type,
                channel_count=channel_count,
                publishing_days=publishing_days,
                posts_per_day=posts_per_day,
                target_channels=target_channels,
                total_reach=total_reach,
                verification_hash=verification_hash
            )
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO post_identity (
                    post_id, campaign_id, user_id, advertiser_username,
                    content_text, content_image, content_video, content_type,
                    channel_count, publishing_days, posts_per_day,
                    target_channels, total_reach, verification_hash,
                    metadata_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id, campaign_id, user_id, advertiser_username,
                content_text, content_image, content_video, content_type,
                channel_count, publishing_days, posts_per_day,
                json.dumps(target_channels), total_reach, verification_hash,
                json.dumps(metadata.__dict__), 'created'
            ))
            
            # Create initial content verification record
            cursor.execute("""
                INSERT INTO content_verification (post_id, original_content_hash, match_status)
                VALUES (?, ?, 'verified')
            """, (post_id, verification_hash))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created post identity {post_id} for campaign {campaign_id}")
            return post_id
            
        except Exception as e:
            logger.error(f"❌ Error creating post identity: {e}")
            return None
    
    async def get_post_metadata(self, post_id: str) -> Optional[PostMetadata]:
        """Get complete post metadata by post ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM post_identity WHERE post_id = ?
            """, (post_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return PostMetadata(
                    post_id=row['post_id'],
                    campaign_id=row['campaign_id'],
                    user_id=row['user_id'],
                    advertiser_username=row['advertiser_username'],
                    creation_date=row['creation_date'],
                    content_text=row['content_text'],
                    content_image=row['content_image'],
                    content_video=row['content_video'],
                    content_type=row['content_type'],
                    channel_count=row['channel_count'],
                    publishing_days=row['publishing_days'],
                    posts_per_day=row['posts_per_day'],
                    target_channels=json.loads(row['target_channels']) if row['target_channels'] else [],
                    total_reach=row['total_reach'],
                    status=row['status'],
                    verification_hash=row['verification_hash']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting post metadata: {e}")
            return None
    
    async def log_publication(self, post_id: str, channel_id: str, channel_name: str, 
                            message_id: int, published_content: str) -> bool:
        """Log actual publication with content verification"""
        try:
            # Create hash of published content for verification
            import hashlib
            published_hash = hashlib.md5(published_content.encode()).hexdigest()
            
            # Get original content hash for comparison
            metadata = await self.get_post_metadata(post_id)
            if not metadata:
                logger.error(f"❌ No metadata found for post {post_id}")
                return False
            
            # Determine verification status
            verification_status = 'match' if published_hash == metadata.verification_hash else 'mismatch'
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Log the publication
            cursor.execute("""
                INSERT INTO post_publishing_log (
                    post_id, campaign_id, channel_id, channel_name,
                    message_id, content_hash, publishing_status, verification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id, metadata.campaign_id, channel_id, channel_name,
                message_id, published_hash, 'success', verification_status
            ))
            
            # Update content verification if there's a mismatch
            if verification_status == 'mismatch':
                cursor.execute("""
                    UPDATE content_verification 
                    SET published_content_hash = ?, match_status = 'mismatch',
                        discrepancy_details = 'Content hash mismatch detected'
                    WHERE post_id = ?
                """, (published_hash, post_id))
                
                logger.warning(f"⚠️ Content mismatch detected for post {post_id} in {channel_id}")
            
            # Update post status
            cursor.execute("""
                UPDATE post_identity 
                SET status = 'publishing', updated_at = CURRENT_TIMESTAMP
                WHERE post_id = ?
            """, (post_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Logged publication of {post_id} to {channel_id} - {verification_status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error logging publication: {e}")
            return False
    
    async def get_post_for_campaign(self, campaign_id: str) -> Optional[PostMetadata]:
        """Get the single post for a campaign (one-to-one relationship)"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM post_identity WHERE campaign_id = ? LIMIT 1
            """, (campaign_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return PostMetadata(
                    post_id=row['post_id'],
                    campaign_id=row['campaign_id'],
                    user_id=row['user_id'],
                    advertiser_username=row['advertiser_username'],
                    creation_date=row['creation_date'],
                    content_text=row['content_text'],
                    content_image=row['content_image'],
                    content_video=row['content_video'],
                    content_type=row['content_type'],
                    channel_count=row['channel_count'],
                    publishing_days=row['publishing_days'],
                    posts_per_day=row['posts_per_day'],
                    target_channels=json.loads(row['target_channels']) if row['target_channels'] else [],
                    total_reach=row['total_reach'],
                    status=row['status'],
                    verification_hash=row['verification_hash']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting campaign post: {e}")
            return None
    
    async def verify_content_integrity(self, campaign_id: str) -> Dict[str, Any]:
        """Verify content integrity for all posts in a campaign"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT pi.post_id, pi.verification_hash, cv.match_status, cv.discrepancy_details,
                       COUNT(ppl.id) as publications_count
                FROM post_identity pi
                LEFT JOIN content_verification cv ON pi.post_id = cv.post_id
                LEFT JOIN post_publishing_log ppl ON pi.post_id = ppl.post_id
                WHERE pi.campaign_id = ?
                GROUP BY pi.post_id
            """, (campaign_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            verification_report = {
                'campaign_id': campaign_id,
                'total_posts': len(rows),
                'verified_posts': 0,
                'mismatched_posts': 0,
                'unpublished_posts': 0,
                'details': []
            }
            
            for row in rows:
                post_status = {
                    'post_id': row['post_id'],
                    'match_status': row['match_status'],
                    'publications_count': row['publications_count'],
                    'discrepancy_details': row['discrepancy_details']
                }
                
                verification_report['details'].append(post_status)
                
                if row['match_status'] == 'verified' or row['match_status'] == 'match':
                    verification_report['verified_posts'] += 1
                elif row['match_status'] == 'mismatch':
                    verification_report['mismatched_posts'] += 1
                else:
                    verification_report['unpublished_posts'] += 1
            
            return verification_report
            
        except Exception as e:
            logger.error(f"❌ Error verifying content integrity: {e}")
            return {}

# Global instance
post_identity_system = PostIdentitySystem()

async def init_post_identity_system():
    """Initialize the Post Identity System"""
    return await post_identity_system.init_tables()

async def create_post_identity(campaign_id: str, user_id: int, advertiser_username: str,
                             content_data: Dict[str, Any], campaign_details: Dict[str, Any]) -> str:
    """Create post identity with full metadata tracking"""
    return await post_identity_system.create_post_identity(
        campaign_id, user_id, advertiser_username, content_data, campaign_details
    )

async def get_post_metadata(post_id: str) -> Optional[PostMetadata]:
    """Get complete post metadata"""
    return await post_identity_system.get_post_metadata(post_id)

async def log_publication(post_id: str, channel_id: str, channel_name: str, 
                        message_id: int, published_content: str) -> bool:
    """Log publication with content verification"""
    return await post_identity_system.log_publication(
        post_id, channel_id, channel_name, message_id, published_content
    )

async def verify_campaign_integrity(campaign_id: str) -> Dict[str, Any]:
    """Verify content integrity for campaign"""
    return await post_identity_system.verify_content_integrity(campaign_id)

if __name__ == "__main__":
    async def test_system():
        await init_post_identity_system()
        
        # Test creating post identity
        content_data = {
            'content': 'Hello New Add New car 📞',
            'content_type': 'photo',
            'media_url': 'AgACAgQAAxkBAAIDuWhs0pQ...'
        }
        
        campaign_details = {
            'selected_channels': ['@i3lani', '@smshco', '@Five_SAR'],
            'duration_days': 7,
            'posts_per_day': 2,
            'total_reach': 357
        }
        
        post_id = await create_post_identity(
            'CAM-2025-07-YBZ3', 566158428, '@username',
            content_data, campaign_details
        )
        
        print(f"Created post identity: {post_id}")
        
        # Get metadata
        metadata = await get_post_metadata(post_id)
        if metadata:
            print(f"Post metadata: {metadata.post_id} - {metadata.content_text[:50]}...")
    
    asyncio.run(test_system())