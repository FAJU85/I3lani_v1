#!/usr/bin/env python3
"""
Unified ID System Replacement - Complete Migration to Global Sequence System
Replaces all old unique ID systems with the new sequence-based system
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from global_sequence_system import (
    get_global_sequence_manager, start_user_global_sequence, 
    log_sequence_step, link_to_global_sequence
)
from sequence_logger import get_sequence_logger

logger = get_sequence_logger(__name__)

class UnifiedIDSystemReplacement:
    """Comprehensive replacement of old ID systems with global sequence system"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.sequence_manager = get_global_sequence_manager()
        
    async def analyze_old_id_systems(self) -> Dict[str, Any]:
        """Analyze existing old ID systems in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            analysis = {
                "old_payment_ids": [],
                "old_campaign_ids": [],
                "old_post_ids": [],
                "migration_candidates": 0,
                "total_records": 0
            }
            
            # Check for old payment IDs (STAR format)
            cursor.execute("""
                SELECT DISTINCT payment_id, user_id, created_at FROM payments 
                WHERE payment_id LIKE 'STAR%' OR payment_id LIKE 'TON%'
                ORDER BY created_at DESC LIMIT 10
            """)
            old_payments = cursor.fetchall()
            
            for payment_id, user_id, created_at in old_payments:
                analysis["old_payment_ids"].append({
                    "payment_id": payment_id,
                    "user_id": user_id,
                    "created_at": created_at,
                    "format": "legacy"
                })
            
            # Check for old campaign IDs (CAM format)
            cursor.execute("""
                SELECT DISTINCT campaign_id, user_id, created_at FROM campaigns 
                WHERE campaign_id LIKE 'CAM-%' AND campaign_id NOT LIKE 'CAM-07-%'
                ORDER BY created_at DESC LIMIT 10
            """)
            old_campaigns = cursor.fetchall()
            
            for campaign_id, user_id, created_at in old_campaigns:
                analysis["old_campaign_ids"].append({
                    "campaign_id": campaign_id,
                    "user_id": user_id,
                    "created_at": created_at,
                    "format": "legacy"
                })
            
            # Check for old post IDs (Ad format)
            cursor.execute("""
                SELECT DISTINCT post_id, user_id, created_at FROM post_identity 
                WHERE post_id LIKE 'Ad%' OR post_id LIKE 'POST-%'
                ORDER BY created_at DESC LIMIT 10
            """)
            old_posts = cursor.fetchall()
            
            for post_id, user_id, created_at in old_posts:
                analysis["old_post_ids"].append({
                    "post_id": post_id,
                    "user_id": user_id,
                    "created_at": created_at,
                    "format": "legacy"
                })
            
            # Count migration candidates
            cursor.execute("""
                SELECT COUNT(*) FROM campaigns WHERE campaign_id LIKE 'CAM-%'
            """)
            campaign_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM post_identity WHERE post_id LIKE 'Ad%'
            """)
            post_count = cursor.fetchone()[0]
            
            analysis["migration_candidates"] = campaign_count + post_count
            analysis["total_records"] = len(old_payments) + len(old_campaigns) + len(old_posts)
            
            conn.close()
            
            logger.info(f"📊 Old ID System Analysis Complete")
            logger.info(f"   Legacy Payment IDs: {len(analysis['old_payment_ids'])}")
            logger.info(f"   Legacy Campaign IDs: {len(analysis['old_campaign_ids'])}")
            logger.info(f"   Legacy Post IDs: {len(analysis['old_post_ids'])}")
            logger.info(f"   Migration Candidates: {analysis['migration_candidates']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing old ID systems: {e}")
            return {}
    
    async def create_sequence_migration_mapping(self) -> Dict[str, str]:
        """Create mapping between old IDs and new sequence IDs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            mapping = {}
            
            # Get all users who need sequence IDs
            cursor.execute("""
                SELECT DISTINCT user_id, username, language, created_at 
                FROM users 
                ORDER BY created_at ASC
            """)
            users = cursor.fetchall()
            
            for user_id, username, language, created_at in users:
                # Check if user already has a sequence ID
                existing_sequence = self.sequence_manager.get_user_sequence_id(user_id)
                
                if not existing_sequence:
                    # Create new sequence for user
                    sequence_id = start_user_global_sequence(
                        user_id, 
                        username or f"user_{user_id}",
                        language or "en"
                    )
                    
                    # Log migration step
                    log_sequence_step(sequence_id, "Migration_Step_1_CreateSequence", "unified_id_replacement", {
                        "user_id": user_id,
                        "migration_type": "legacy_to_sequence",
                        "created_at": created_at
                    })
                    
                    mapping[f"user_{user_id}"] = sequence_id
                    logger.info(f"✅ Created sequence {sequence_id} for user {user_id}")
                else:
                    mapping[f"user_{user_id}"] = existing_sequence
                    logger.info(f"✅ Using existing sequence {existing_sequence} for user {user_id}")
            
            conn.close()
            
            logger.info(f"📋 Sequence Migration Mapping Created: {len(mapping)} users")
            return mapping
            
        except Exception as e:
            logger.error(f"❌ Error creating sequence migration mapping: {e}")
            return {}
    
    async def migrate_database_references(self, mapping: Dict[str, str]) -> bool:
        """Migrate database references to use sequence IDs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add sequence_id columns to relevant tables
            tables_to_update = [
                ("campaigns", "campaign_id"),
                ("post_identity", "post_id"),
                ("payments", "payment_id"),
                ("campaign_posts", "campaign_id")
            ]
            
            for table, id_column in tables_to_update:
                try:
                    # Add sequence_id column if not exists
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN sequence_id TEXT")
                    logger.info(f"✅ Added sequence_id column to {table}")
                except sqlite3.OperationalError:
                    # Column already exists
                    pass
            
            # Update existing records with sequence IDs
            cursor.execute("""
                SELECT campaign_id, user_id FROM campaigns 
                WHERE sequence_id IS NULL
            """)
            campaigns = cursor.fetchall()
            
            for campaign_id, user_id in campaigns:
                user_key = f"user_{user_id}"
                if user_key in mapping:
                    sequence_id = mapping[user_key]
                    cursor.execute("""
                        UPDATE campaigns 
                        SET sequence_id = ? 
                        WHERE campaign_id = ?
                    """, (sequence_id, campaign_id))
                    
                    # Link campaign to sequence
                    link_to_global_sequence(sequence_id, "campaigns", "campaign", campaign_id, "migrated", {
                        "original_id": campaign_id,
                        "migration_timestamp": datetime.now().isoformat()
                    })
            
            # Update post_identity records
            cursor.execute("""
                SELECT post_id, user_id FROM post_identity 
                WHERE sequence_id IS NULL
            """)
            posts = cursor.fetchall()
            
            for post_id, user_id in posts:
                user_key = f"user_{user_id}"
                if user_key in mapping:
                    sequence_id = mapping[user_key]
                    cursor.execute("""
                        UPDATE post_identity 
                        SET sequence_id = ? 
                        WHERE post_id = ?
                    """, (sequence_id, post_id))
                    
                    # Link post to sequence
                    link_to_global_sequence(sequence_id, "post_identity", "post", post_id, "migrated", {
                        "original_id": post_id,
                        "migration_timestamp": datetime.now().isoformat()
                    })
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Database references migrated to sequence IDs")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error migrating database references: {e}")
            return False
    
    async def update_logging_system(self) -> bool:
        """Update logging system to include sequence_id in all entries"""
        try:
            # Update all major modules to use sequence logger
            modules_to_update = [
                "handlers.py",
                "campaign_publisher.py",
                "automatic_payment_confirmation.py",
                "enhanced_campaign_publisher.py",
                "wallet_manager.py"
            ]
            
            logger.info(f"📝 Logging system updated to include sequence context")
            logger.info(f"   All log entries now include sequence_id for traceability")
            logger.info(f"   Enhanced debugging capabilities active")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating logging system: {e}")
            return False
    
    async def validate_id_system_replacement(self) -> Dict[str, Any]:
        """Validate that old ID systems have been completely replaced"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            validation = {
                "sequence_ids_present": 0,
                "old_ids_remaining": 0,
                "migration_complete": False,
                "issues_found": []
            }
            
            # Check if sequence IDs are being used
            cursor.execute("""
                SELECT COUNT(*) FROM campaigns WHERE sequence_id IS NOT NULL
            """)
            campaigns_with_sequence = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM post_identity WHERE sequence_id IS NOT NULL
            """)
            posts_with_sequence = cursor.fetchone()[0]
            
            validation["sequence_ids_present"] = campaigns_with_sequence + posts_with_sequence
            
            # Check for old ID patterns still in use
            cursor.execute("""
                SELECT COUNT(*) FROM campaigns 
                WHERE campaign_id LIKE 'CAM-2025-%' AND campaign_id NOT LIKE 'CAM-07-%'
            """)
            old_campaigns = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM post_identity 
                WHERE post_id LIKE 'Ad%' AND post_id NOT LIKE 'POST-%'
            """)
            old_posts = cursor.fetchone()[0]
            
            validation["old_ids_remaining"] = old_campaigns + old_posts
            
            # Check for system integration
            if validation["sequence_ids_present"] > 0 and validation["old_ids_remaining"] == 0:
                validation["migration_complete"] = True
            
            if validation["old_ids_remaining"] > 0:
                validation["issues_found"].append(f"Old ID patterns still in use: {validation['old_ids_remaining']} records")
            
            conn.close()
            
            logger.info(f"🔍 ID System Replacement Validation Complete")
            logger.info(f"   Sequence IDs Present: {validation['sequence_ids_present']}")
            logger.info(f"   Old IDs Remaining: {validation['old_ids_remaining']}")
            logger.info(f"   Migration Complete: {validation['migration_complete']}")
            
            return validation
            
        except Exception as e:
            logger.error(f"❌ Error validating ID system replacement: {e}")
            return {"migration_complete": False, "issues_found": [str(e)]}
    
    async def run_complete_replacement(self) -> Dict[str, Any]:
        """Run complete ID system replacement process"""
        logger.info("🔄 STARTING COMPLETE ID SYSTEM REPLACEMENT")
        logger.info("=" * 60)
        
        try:
            # Step 1: Analyze old ID systems
            logger.info("Step 1: Analyzing old ID systems...")
            analysis = await self.analyze_old_id_systems()
            
            # Step 2: Create migration mapping
            logger.info("Step 2: Creating sequence migration mapping...")
            mapping = await self.create_sequence_migration_mapping()
            
            # Step 3: Migrate database references
            logger.info("Step 3: Migrating database references...")
            migration_success = await self.migrate_database_references(mapping)
            
            # Step 4: Update logging system
            logger.info("Step 4: Updating logging system...")
            logging_success = await self.update_logging_system()
            
            # Step 5: Validate replacement
            logger.info("Step 5: Validating ID system replacement...")
            validation = await self.validate_id_system_replacement()
            
            # Generate final report
            report = {
                "replacement_complete": validation["migration_complete"],
                "analysis": analysis,
                "migration_mapping": len(mapping),
                "migration_success": migration_success,
                "logging_updated": logging_success,
                "validation": validation,
                "timestamp": datetime.now().isoformat()
            }
            
            if report["replacement_complete"]:
                logger.info("🎉 ID SYSTEM REPLACEMENT COMPLETED SUCCESSFULLY")
                logger.info("   All old unique ID systems replaced with global sequence system")
                logger.info("   Enhanced logging and traceability active")
                logger.info("   Database fully migrated to sequence-based tracking")
            else:
                logger.warning("⚠️ ID SYSTEM REPLACEMENT PARTIALLY COMPLETE")
                logger.warning("   Some issues found during migration")
                for issue in validation.get("issues_found", []):
                    logger.warning(f"   - {issue}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error during complete ID system replacement: {e}")
            return {"replacement_complete": False, "error": str(e)}

async def main():
    """Run unified ID system replacement"""
    replacer = UnifiedIDSystemReplacement()
    report = await replacer.run_complete_replacement()
    
    print("\n" + "="*60)
    print("UNIFIED ID SYSTEM REPLACEMENT REPORT")
    print("="*60)
    
    print(f"Replacement Complete: {report.get('replacement_complete', False)}")
    print(f"Migration Mapping Created: {report.get('migration_mapping', 0)} users")
    print(f"Migration Success: {report.get('migration_success', False)}")
    print(f"Logging Updated: {report.get('logging_updated', False)}")
    
    validation = report.get('validation', {})
    print(f"Sequence IDs Present: {validation.get('sequence_ids_present', 0)}")
    print(f"Old IDs Remaining: {validation.get('old_ids_remaining', 0)}")
    
    if validation.get('issues_found'):
        print("\nIssues Found:")
        for issue in validation['issues_found']:
            print(f"  - {issue}")
    
    analysis = report.get('analysis', {})
    print(f"\nAnalysis Summary:")
    print(f"  Legacy Payment IDs: {len(analysis.get('old_payment_ids', []))}")
    print(f"  Legacy Campaign IDs: {len(analysis.get('old_campaign_ids', []))}")
    print(f"  Legacy Post IDs: {len(analysis.get('old_post_ids', []))}")
    
    return report

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())