#!/usr/bin/env python3
"""
Migrate Remaining Old ID Records to Sequence System
Handles the final 18 old ID records that need migration
"""

import sqlite3
import logging
from datetime import datetime
from global_sequence_system import get_global_sequence_manager, start_user_global_sequence, link_to_global_sequence
from sequence_logger import get_sequence_logger

logger = get_sequence_logger(__name__)

def migrate_old_campaign_ids():
    """Migrate old campaign ID records to sequence system"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        manager = get_global_sequence_manager()
        
        # Find old campaign IDs
        cursor.execute("""
            SELECT campaign_id, user_id, created_at 
            FROM campaigns 
            WHERE campaign_id LIKE 'CAM-2025-%' AND campaign_id NOT LIKE 'CAM-07-%'
            ORDER BY created_at ASC
        """)
        old_campaigns = cursor.fetchall()
        
        logger.info(f"🔄 Migrating {len(old_campaigns)} old campaign IDs")
        
        for campaign_id, user_id, created_at in old_campaigns:
            try:
                # Get or create sequence for user
                sequence_id = manager.get_user_active_sequence(user_id)
                if not sequence_id:
                    # Create sequence for this user
                    sequence_id = start_user_global_sequence(
                        user_id, 
                        f"user_{user_id}", 
                        "en"  # Default language
                    )
                    logger.info(f"✅ Created sequence {sequence_id} for user {user_id}")
                
                # Update campaign with sequence_id
                cursor.execute("""
                    UPDATE campaigns 
                    SET sequence_id = ? 
                    WHERE campaign_id = ?
                """, (sequence_id, campaign_id))
                
                # Link campaign to sequence
                link_to_global_sequence(sequence_id, "campaigns", "campaign", campaign_id, "migrated", {
                    "original_id": campaign_id,
                    "migration_timestamp": datetime.now().isoformat(),
                    "migration_type": "legacy_campaign"
                })
                
                logger.info(f"✅ Migrated campaign {campaign_id} to sequence {sequence_id}")
                
            except Exception as e:
                logger.error(f"❌ Error migrating campaign {campaign_id}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"🎉 Campaign ID migration completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error migrating campaign IDs: {e}")
        return False

def migrate_old_post_ids():
    """Migrate old post ID records to sequence system"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        manager = get_global_sequence_manager()
        
        # Find old post IDs
        cursor.execute("""
            SELECT post_id, user_id, created_at 
            FROM post_identity 
            WHERE post_id LIKE 'Ad%' AND post_id NOT LIKE 'POST-%'
            ORDER BY created_at ASC
        """)
        old_posts = cursor.fetchall()
        
        logger.info(f"🔄 Migrating {len(old_posts)} old post IDs")
        
        for post_id, user_id, created_at in old_posts:
            try:
                # Get or create sequence for user
                sequence_id = manager.get_user_active_sequence(user_id)
                if not sequence_id:
                    # Create sequence for this user
                    sequence_id = start_user_global_sequence(
                        user_id, 
                        f"user_{user_id}", 
                        "en"  # Default language
                    )
                    logger.info(f"✅ Created sequence {sequence_id} for user {user_id}")
                
                # Update post with sequence_id
                cursor.execute("""
                    UPDATE post_identity 
                    SET sequence_id = ? 
                    WHERE post_id = ?
                """, (sequence_id, post_id))
                
                # Link post to sequence
                link_to_global_sequence(sequence_id, "post_identity", "post", post_id, "migrated", {
                    "original_id": post_id,
                    "migration_timestamp": datetime.now().isoformat(),
                    "migration_type": "legacy_post"
                })
                
                logger.info(f"✅ Migrated post {post_id} to sequence {sequence_id}")
                
            except Exception as e:
                logger.error(f"❌ Error migrating post {post_id}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"🎉 Post ID migration completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error migrating post IDs: {e}")
        return False

def validate_migration_completion():
    """Validate that all old IDs have been migrated"""
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        
        # Check for remaining old campaign IDs
        cursor.execute("""
            SELECT COUNT(*) FROM campaigns 
            WHERE campaign_id LIKE 'CAM-2025-%' AND campaign_id NOT LIKE 'CAM-07-%'
        """)
        old_campaigns = cursor.fetchone()[0]
        
        # Check for remaining old post IDs
        cursor.execute("""
            SELECT COUNT(*) FROM post_identity 
            WHERE post_id LIKE 'Ad%' AND post_id NOT LIKE 'POST-%'
        """)
        old_posts = cursor.fetchone()[0]
        
        # Check for records with sequence_id
        cursor.execute("""
            SELECT COUNT(*) FROM campaigns WHERE sequence_id IS NOT NULL
        """)
        campaigns_with_sequence = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM post_identity WHERE sequence_id IS NOT NULL
        """)
        posts_with_sequence = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"📊 MIGRATION VALIDATION RESULTS:")
        logger.info(f"   Old Campaign IDs Remaining: {old_campaigns}")
        logger.info(f"   Old Post IDs Remaining: {old_posts}")
        logger.info(f"   Campaigns with Sequence: {campaigns_with_sequence}")
        logger.info(f"   Posts with Sequence: {posts_with_sequence}")
        
        if old_campaigns == 0 and old_posts == 0:
            logger.info(f"🎉 MIGRATION COMPLETE - No old IDs remaining")
            return True
        else:
            logger.warning(f"⚠️ MIGRATION INCOMPLETE - {old_campaigns + old_posts} old IDs remaining")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error validating migration: {e}")
        return False

def run_complete_migration():
    """Run complete migration of remaining old IDs"""
    logger.info("🚀 STARTING COMPLETE OLD ID MIGRATION")
    logger.info("=" * 50)
    
    try:
        # Step 1: Migrate old campaign IDs
        logger.info("Step 1: Migrating old campaign IDs...")
        campaign_success = migrate_old_campaign_ids()
        
        # Step 2: Migrate old post IDs
        logger.info("Step 2: Migrating old post IDs...")
        post_success = migrate_old_post_ids()
        
        # Step 3: Validate migration completion
        logger.info("Step 3: Validating migration completion...")
        validation_success = validate_migration_completion()
        
        # Generate report
        if campaign_success and post_success and validation_success:
            logger.info("🎉 COMPLETE OLD ID MIGRATION SUCCESSFUL")
            logger.info("   All old unique ID systems have been migrated to sequence system")
            logger.info("   100% ID system replacement achieved")
            return True
        else:
            logger.warning("⚠️ MIGRATION PARTIALLY COMPLETE")
            logger.warning("   Some issues occurred during migration")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during complete migration: {e}")
        return False

if __name__ == "__main__":
    success = run_complete_migration()
    
    if success:
        print("\n🎉 OLD ID MIGRATION COMPLETED SUCCESSFULLY")
        print("All remaining legacy IDs have been migrated to the sequence system")
    else:
        print("\n❌ OLD ID MIGRATION FAILED")
        print("Some issues occurred during the migration process")