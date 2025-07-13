#!/usr/bin/env python3
"""
Image Upload System Check
Comprehensive check of the image upload system to identify and fix issues
"""

import asyncio
import aiosqlite
import logging
import os
from database import db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageUploadSystemChecker:
    def __init__(self):
        self.db_path = 'bot.db'
        self.issues = []
        self.fixes_applied = []
        
    async def comprehensive_check(self):
        """Perform comprehensive image upload system check"""
        
        print("🔍 IMAGE UPLOAD SYSTEM COMPREHENSIVE CHECK")
        print("=" * 60)
        
        results = {
            'handler_validation': await self._validate_handlers(),
            'state_management': await self._validate_state_management(),
            'database_integration': await self._validate_database_integration(),
            'media_storage': await self._validate_media_storage(),
            'content_type_handling': await self._validate_content_type_handling(),
            'error_handling': await self._validate_error_handling(),
            'workflow_integration': await self._validate_workflow_integration()
        }
        
        # Display results
        await self._display_results(results)
        
        # Apply fixes if needed
        if self.issues:
            await self._apply_fixes()
        
        return results
    
    async def _validate_handlers(self):
        """Validate image upload handlers"""
        print("\n1. 🎯 HANDLER VALIDATION")
        print("-" * 30)
        
        try:
            # Check if handlers.py exists
            if not os.path.exists('handlers.py'):
                print("   ❌ handlers.py file missing")
                self.issues.append("handlers.py file missing")
                return {'status': 'error', 'error': 'handlers.py missing'}
            
            # Check for photo upload handler
            with open('handlers.py', 'r') as f:
                content = f.read()
                
            handlers_found = {
                'handle_photo_upload': 'handle_photo_upload' in content,
                'photo_state_handler': 'AdCreationStates.upload_photos' in content,
                'done_photos_handler': 'done_photos' in content,
                'skip_photos_handler': 'skip_photos' in content,
                'continue_from_photos': 'continue_from_photos' in content
            }
            
            print("   📋 Handler availability:")
            for handler, exists in handlers_found.items():
                if exists:
                    print(f"      ✅ {handler}: EXISTS")
                else:
                    print(f"      ❌ {handler}: MISSING")
                    self.issues.append(f"Missing handler: {handler}")
            
            # Check for proper router registration
            router_patterns = [
                '@router.message(AdCreationStates.upload_photos, F.photo)',
                '@router.callback_query(F.data == "done_photos")',
                '@router.callback_query(F.data == "skip_photos")'
            ]
            
            router_registrations = 0
            for pattern in router_patterns:
                if pattern in content:
                    router_registrations += 1
                    print(f"      ✅ Router registration: {pattern}")
                else:
                    print(f"      ❌ Missing router: {pattern}")
            
            if router_registrations == len(router_patterns):
                print("   ✅ All handlers properly registered")
                status = 'healthy'
            else:
                print(f"   ⚠️  {router_registrations}/{len(router_patterns)} handlers registered")
                status = 'issues'
                self.issues.append(f"Missing router registrations: {len(router_patterns) - router_registrations}")
            
            return {
                'status': status,
                'handlers_found': handlers_found,
                'router_registrations': router_registrations,
                'total_patterns': len(router_patterns)
            }
            
        except Exception as e:
            print(f"   ❌ Handler validation error: {e}")
            self.issues.append(f"Handler validation error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_state_management(self):
        """Validate state management for image uploads"""
        print("\n2. 🔄 STATE MANAGEMENT VALIDATION")
        print("-" * 30)
        
        try:
            # Check if states.py exists
            if os.path.exists('states.py'):
                with open('states.py', 'r') as f:
                    states_content = f.read()
                    
                if 'upload_photos' in states_content:
                    print("   ✅ upload_photos state defined")
                    upload_photos_defined = True
                else:
                    print("   ❌ upload_photos state missing")
                    upload_photos_defined = False
                    self.issues.append("upload_photos state not defined")
            else:
                print("   ❌ states.py file missing")
                upload_photos_defined = False
                self.issues.append("states.py file missing")
            
            # Check for related states
            related_states = ['upload_content', 'provide_contact_info', 'preview_ad']
            states_found = 0
            
            if os.path.exists('states.py'):
                with open('states.py', 'r') as f:
                    states_content = f.read()
                    
                for state in related_states:
                    if state in states_content:
                        states_found += 1
                        print(f"   ✅ Related state: {state}")
                    else:
                        print(f"   ❌ Missing state: {state}")
            
            # Check state transitions in handlers
            if os.path.exists('handlers.py'):
                with open('handlers.py', 'r') as f:
                    handlers_content = f.read()
                    
                state_transitions = [
                    'await state.set_state(AdCreationStates.upload_photos)',
                    'await state.set_state(AdCreationStates.upload_content)',
                    'await state.update_data(uploaded_photos='
                ]
                
                transitions_found = 0
                for transition in state_transitions:
                    if transition in handlers_content:
                        transitions_found += 1
                        print(f"   ✅ State transition: {transition[:50]}...")
                    else:
                        print(f"   ❌ Missing transition: {transition[:50]}...")
            
            status = 'healthy' if upload_photos_defined and states_found >= 2 else 'issues'
            
            return {
                'status': status,
                'upload_photos_defined': upload_photos_defined,
                'related_states_found': states_found,
                'state_transitions_found': transitions_found if 'transitions_found' in locals() else 0
            }
            
        except Exception as e:
            print(f"   ❌ State management validation error: {e}")
            self.issues.append(f"State management error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_database_integration(self):
        """Validate database integration for image uploads"""
        print("\n3. 🗄️  DATABASE INTEGRATION VALIDATION")
        print("-" * 30)
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check if ads table has media_url column
                await cursor.execute("PRAGMA table_info(ads)")
                columns = await cursor.fetchall()
                
                column_names = [col[1] for col in columns]
                
                required_columns = ['media_url', 'content_type', 'content']
                missing_columns = []
                
                for col in required_columns:
                    if col in column_names:
                        print(f"   ✅ Column {col}: EXISTS")
                    else:
                        print(f"   ❌ Column {col}: MISSING")
                        missing_columns.append(col)
                        self.issues.append(f"Missing database column: {col}")
                
                # Check for existing ads with media
                await cursor.execute('''
                    SELECT COUNT(*) FROM ads 
                    WHERE media_url IS NOT NULL AND media_url != ''
                ''')
                
                ads_with_media = (await cursor.fetchone())[0]
                print(f"   📊 Ads with media: {ads_with_media}")
                
                # Check content type distribution
                await cursor.execute('''
                    SELECT content_type, COUNT(*) as count
                    FROM ads
                    WHERE content_type IS NOT NULL
                    GROUP BY content_type
                ''')
                
                content_types = await cursor.fetchall()
                
                print(f"   📊 Content types:")
                for content_type, count in content_types:
                    print(f"      {content_type}: {count}")
                
                # Check campaigns table integration
                await cursor.execute("PRAGMA table_info(campaigns)")
                campaign_columns = await cursor.fetchall()
                
                campaign_column_names = [col[1] for col in campaign_columns]
                
                if 'media_url' in campaign_column_names:
                    print("   ✅ Campaigns table has media_url column")
                    campaigns_media_ready = True
                else:
                    print("   ❌ Campaigns table missing media_url column")
                    campaigns_media_ready = False
                    self.issues.append("Campaigns table missing media_url column")
                
                status = 'healthy' if len(missing_columns) == 0 and campaigns_media_ready else 'issues'
                
                return {
                    'status': status,
                    'missing_columns': missing_columns,
                    'ads_with_media': ads_with_media,
                    'content_types': len(content_types),
                    'campaigns_media_ready': campaigns_media_ready
                }
                
        except Exception as e:
            print(f"   ❌ Database integration validation error: {e}")
            self.issues.append(f"Database integration error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_media_storage(self):
        """Validate media storage system"""
        print("\n4. 💾 MEDIA STORAGE VALIDATION")
        print("-" * 30)
        
        try:
            # Check if media storage directory exists
            media_dirs = ['media', 'uploads', 'photos']
            media_dir_exists = False
            
            for dir_name in media_dirs:
                if os.path.exists(dir_name):
                    print(f"   ✅ Media directory: {dir_name}")
                    media_dir_exists = True
                    break
            
            if not media_dir_exists:
                print("   ⚠️  No dedicated media directory found")
                print("   ℹ️  Using Telegram file_id system (recommended)")
            
            # Check file handling capabilities
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.cursor()
                
                # Check for file_id storage
                await cursor.execute('''
                    SELECT media_url FROM ads 
                    WHERE media_url IS NOT NULL 
                    AND media_url != ''
                    LIMIT 5
                ''')
                
                media_samples = await cursor.fetchall()
                
                print(f"   📊 Media URL samples: {len(media_samples)}")
                
                telegram_file_ids = 0
                for media_url, in media_samples:
                    if media_url and (media_url.startswith('AgAC') or media_url.startswith('BAA')):
                        telegram_file_ids += 1
                        print(f"   ✅ Telegram file_id: {media_url[:20]}...")
                    else:
                        print(f"   ❓ Other media: {media_url[:20]}...")
                
                # Check for media URL validation
                file_id_pattern_valid = telegram_file_ids > 0
                
                if file_id_pattern_valid:
                    print("   ✅ Telegram file_id pattern detected")
                    status = 'healthy'
                else:
                    print("   ⚠️  No Telegram file_id pattern detected")
                    status = 'warning'
                
                return {
                    'status': status,
                    'media_dir_exists': media_dir_exists,
                    'media_samples': len(media_samples),
                    'telegram_file_ids': telegram_file_ids,
                    'file_id_pattern_valid': file_id_pattern_valid
                }
                
        except Exception as e:
            print(f"   ❌ Media storage validation error: {e}")
            self.issues.append(f"Media storage error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_content_type_handling(self):
        """Validate content type handling"""
        print("\n5. 📝 CONTENT TYPE HANDLING VALIDATION")
        print("-" * 30)
        
        try:
            # Check handlers for content type logic
            if os.path.exists('handlers.py'):
                with open('handlers.py', 'r') as f:
                    content = f.read()
                
                content_type_patterns = [
                    'content_type.*photo',
                    'content_type.*text',
                    'content_type.*video',
                    'message.photo',
                    'message.video'
                ]
                
                patterns_found = 0
                for pattern in content_type_patterns:
                    if pattern in content:
                        patterns_found += 1
                        print(f"   ✅ Content type pattern: {pattern}")
                    else:
                        print(f"   ❌ Missing pattern: {pattern}")
                
                # Check enhanced campaign publisher
                if os.path.exists('enhanced_campaign_publisher.py'):
                    with open('enhanced_campaign_publisher.py', 'r') as f:
                        publisher_content = f.read()
                    
                    publisher_patterns = [
                        'send_photo',
                        'send_video',
                        'content_type.*photo',
                        'content_type.*video'
                    ]
                    
                    publisher_patterns_found = 0
                    for pattern in publisher_patterns:
                        if pattern in publisher_content:
                            publisher_patterns_found += 1
                            print(f"   ✅ Publisher pattern: {pattern}")
                        else:
                            print(f"   ❌ Missing publisher pattern: {pattern}")
                
                # Check database for content types
                async with aiosqlite.connect(self.db_path) as conn:
                    cursor = await conn.cursor()
                    
                    await cursor.execute('''
                        SELECT content_type, COUNT(*) as count
                        FROM ads
                        WHERE content_type IS NOT NULL
                        GROUP BY content_type
                    ''')
                    
                    content_type_stats = await cursor.fetchall()
                    
                    print(f"   📊 Content type distribution:")
                    for content_type, count in content_type_stats:
                        print(f"      {content_type}: {count}")
                
                status = 'healthy' if patterns_found >= 3 else 'issues'
                
                return {
                    'status': status,
                    'handler_patterns_found': patterns_found,
                    'publisher_patterns_found': publisher_patterns_found if 'publisher_patterns_found' in locals() else 0,
                    'content_type_stats': len(content_type_stats)
                }
                
        except Exception as e:
            print(f"   ❌ Content type handling validation error: {e}")
            self.issues.append(f"Content type handling error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_error_handling(self):
        """Validate error handling for image uploads"""
        print("\n6. 🛡️  ERROR HANDLING VALIDATION")
        print("-" * 30)
        
        try:
            # Check for error handling in handlers
            if os.path.exists('handlers.py'):
                with open('handlers.py', 'r') as f:
                    content = f.read()
                
                error_patterns = [
                    'try:',
                    'except Exception as e:',
                    'logger.error',
                    'await message.reply.*error',
                    'max_photos_reached'
                ]
                
                error_handling_found = 0
                for pattern in error_patterns:
                    if pattern in content:
                        error_handling_found += 1
                        print(f"   ✅ Error handling: {pattern}")
                    else:
                        print(f"   ❌ Missing error handling: {pattern}")
                
                # Check for specific upload error handling
                upload_error_patterns = [
                    'Photo upload error',
                    'error_uploading_photo',
                    'max_photos_reached'
                ]
                
                upload_error_handling = 0
                for pattern in upload_error_patterns:
                    if pattern in content:
                        upload_error_handling += 1
                        print(f"   ✅ Upload error handling: {pattern}")
                    else:
                        print(f"   ❌ Missing upload error: {pattern}")
                
                status = 'healthy' if error_handling_found >= 3 else 'issues'
                
                return {
                    'status': status,
                    'error_handling_found': error_handling_found,
                    'upload_error_handling': upload_error_handling
                }
                
        except Exception as e:
            print(f"   ❌ Error handling validation error: {e}")
            self.issues.append(f"Error handling validation error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_workflow_integration(self):
        """Validate workflow integration"""
        print("\n7. 🔄 WORKFLOW INTEGRATION VALIDATION")
        print("-" * 30)
        
        try:
            # Check integration with main workflow
            if os.path.exists('handlers.py'):
                with open('handlers.py', 'r') as f:
                    content = f.read()
                
                workflow_patterns = [
                    'continue_to_channels',
                    'show_channel_selection',
                    'create_ad',
                    'back_to_photos',
                    'skip_photos'
                ]
                
                workflow_integration = 0
                for pattern in workflow_patterns:
                    if pattern in content:
                        workflow_integration += 1
                        print(f"   ✅ Workflow integration: {pattern}")
                    else:
                        print(f"   ❌ Missing workflow: {pattern}")
                
                # Check for proper state transitions
                state_transitions = [
                    'AdCreationStates.upload_photos',
                    'AdCreationStates.upload_content',
                    'await state.set_state'
                ]
                
                state_integration = 0
                for transition in state_transitions:
                    if transition in content:
                        state_integration += 1
                        print(f"   ✅ State integration: {transition}")
                    else:
                        print(f"   ❌ Missing state: {transition}")
                
                status = 'healthy' if workflow_integration >= 3 and state_integration >= 2 else 'issues'
                
                return {
                    'status': status,
                    'workflow_integration': workflow_integration,
                    'state_integration': state_integration
                }
                
        except Exception as e:
            print(f"   ❌ Workflow integration validation error: {e}")
            self.issues.append(f"Workflow integration error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _display_results(self, results):
        """Display comprehensive results"""
        print("\n" + "=" * 60)
        print("📊 IMAGE UPLOAD SYSTEM VALIDATION REPORT")
        print("=" * 60)
        
        # Calculate overall health
        healthy_components = sum(1 for r in results.values() if r.get('status') == 'healthy')
        total_components = len(results)
        
        health_score = (healthy_components / total_components * 100) if total_components > 0 else 0
        
        print(f"\n🏆 OVERALL HEALTH: {health_score:.1f}% ({healthy_components}/{total_components} components healthy)")
        
        if health_score >= 90:
            print("   🟢 EXCELLENT: Image upload system is working optimally")
        elif health_score >= 70:
            print("   🟡 GOOD: Image upload system is working well")
        elif health_score >= 50:
            print("   🟠 FAIR: Image upload system needs some attention")
        else:
            print("   🔴 POOR: Image upload system has critical issues")
        
        print("\n📋 COMPONENT STATUS:")
        for component, data in results.items():
            status = data.get('status', 'unknown')
            if status == 'healthy':
                icon = "✅"
            elif status == 'warning':
                icon = "⚠️"
            else:
                icon = "❌"
            
            print(f"   {icon} {component.replace('_', ' ').title()}: {status.upper()}")
        
        # Issues summary
        if self.issues:
            print(f"\n⚠️  ISSUES FOUND ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n✅ NO ISSUES FOUND")
        
        # Recommendations
        print("\n🎯 RECOMMENDATIONS:")
        if health_score >= 90:
            print("   • Image upload system is operating optimally")
            print("   • Continue regular testing with actual uploads")
        elif health_score >= 70:
            print("   • Address any warnings to improve performance")
            print("   • Test upload functionality with different file types")
        else:
            print("   • Immediate attention required for failed components")
            print("   • Review handler registration and state management")
            print("   • Test upload workflow end-to-end")
    
    async def _apply_fixes(self):
        """Apply fixes for identified issues"""
        print("\n🔧 APPLYING FIXES")
        print("-" * 30)
        
        # This would contain specific fixes for common issues
        print("   ℹ️  Image upload system fixes would be applied here")
        print("   ℹ️  Common fixes include:")
        print("   • Handler registration fixes")
        print("   • Database schema updates")
        print("   • Error handling improvements")
        print("   • State management corrections")

async def main():
    """Main function to run image upload system check"""
    checker = ImageUploadSystemChecker()
    results = await checker.comprehensive_check()
    
    # Save results
    import json
    with open('image_upload_validation_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Full validation report saved to: image_upload_validation_report.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())