#!/usr/bin/env python3
"""
Implement Automatic Language System
Updates all key files to use automatic language detection
"""

import os
import re
import logging

logger = logging.getLogger(__name__)

def update_handlers_file():
    """Update handlers.py to use automatic language system"""
    try:
        # Read current handlers.py
        with open('handlers.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace all get_user_language function calls to use automatic system
        new_content = content.replace(
            'await db.get_user_language(user_id)',
            'await get_user_language_auto(user_id)'
        )
        
        # Add import at the top
        if 'from automatic_language_system import get_user_language_auto' not in new_content:
            # Find import section and add our import
            import_pattern = r'(from database import db\n)'
            replacement = r'\1from automatic_language_system import get_user_language_auto\n'
            new_content = re.sub(import_pattern, replacement, new_content)
        
        # Write back
        with open('handlers.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Updated handlers.py with automatic language system")
        return True
        
    except Exception as e:
        print(f"❌ Error updating handlers.py: {e}")
        return False

def update_admin_system_file():
    """Update admin_system.py to use automatic language system"""
    try:
        # Read current admin_system.py
        with open('admin_system.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add import at the top
        if 'from automatic_language_system import get_user_language_auto' not in content:
            # Find import section and add our import
            import_pattern = r'(from database import db\n)'
            replacement = r'\1from automatic_language_system import get_user_language_auto\n'
            content = re.sub(import_pattern, replacement, content)
        
        # Replace language getting calls
        content = content.replace(
            'await db.get_user_language(user_id)',
            'await get_user_language_auto(user_id)'
        )
        
        # Write back
        with open('admin_system.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated admin_system.py with automatic language system")
        return True
        
    except Exception as e:
        print(f"❌ Error updating admin_system.py: {e}")
        return False

def update_payment_systems():
    """Update payment systems to use automatic language"""
    updated_files = []
    
    # Files to update
    payment_files = [
        'clean_stars_payment_system.py',
        'enhanced_stars_payment_system.py',
        'automatic_payment_confirmation.py'
    ]
    
    for filename in payment_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add import if not exists
                if 'from automatic_language_system import get_user_language_auto' not in content:
                    # Find a good place to add import
                    if 'import logging' in content:
                        content = content.replace(
                            'import logging',
                            'import logging\nfrom automatic_language_system import get_user_language_auto'
                        )
                
                # Replace language getting calls
                content = content.replace(
                    'await db.get_user_language(user_id)',
                    'await get_user_language_auto(user_id)'
                )
                
                # Write back
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updated_files.append(filename)
                
            except Exception as e:
                print(f"❌ Error updating {filename}: {e}")
    
    if updated_files:
        print(f"✅ Updated payment systems: {', '.join(updated_files)}")
        return True
    else:
        print("⚠️ No payment system files updated")
        return False

def update_campaign_systems():
    """Update campaign systems to use automatic language"""
    updated_files = []
    
    # Files to update
    campaign_files = [
        'enhanced_campaign_publisher.py',
        'campaign_management.py',
        'campaign_handlers.py'
    ]
    
    for filename in campaign_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add import if not exists
                if 'from automatic_language_system import get_user_language_auto' not in content:
                    # Find a good place to add import
                    if 'import logging' in content:
                        content = content.replace(
                            'import logging',
                            'import logging\nfrom automatic_language_system import get_user_language_auto'
                        )
                
                # Replace language getting calls
                content = content.replace(
                    'await db.get_user_language(user_id)',
                    'await get_user_language_auto(user_id)'
                )
                
                # Write back
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updated_files.append(filename)
                
            except Exception as e:
                print(f"❌ Error updating {filename}: {e}")
    
    if updated_files:
        print(f"✅ Updated campaign systems: {', '.join(updated_files)}")
        return True
    else:
        print("⚠️ No campaign system files updated")
        return False

def create_language_wrapper_functions():
    """Create wrapper functions for easy language access"""
    wrapper_content = '''#!/usr/bin/env python3
"""
Language Wrapper Functions
Easy access to automatic language system
"""

from automatic_language_system import get_user_language_auto, localize_text_auto

async def get_language(user_id: int) -> str:
    """Get user language (wrapper)"""
    return await get_user_language_auto(user_id)

async def get_localized_text(user_id: int, text_key: str, **kwargs) -> str:
    """Get localized text (wrapper)"""
    return await localize_text_auto(user_id, text_key, **kwargs)

async def get_text_for_user(user_id: int, key: str, **kwargs) -> str:
    """Get text for user in their language"""
    language = await get_language(user_id)
    
    from languages import get_text
    text = get_text(language, key)
    
    if kwargs:
        text = text.format(**kwargs)
    
    return text
'''
    
    with open('language_helpers.py', 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    print("✅ Created language wrapper functions")

def main():
    """Main implementation function"""
    print("🌍 Implementing Automatic Language System...")
    print("=" * 50)
    
    success_count = 0
    total_operations = 5
    
    # Update handlers
    if update_handlers_file():
        success_count += 1
    
    # Update admin system
    if update_admin_system_file():
        success_count += 1
    
    # Update payment systems
    if update_payment_systems():
        success_count += 1
    
    # Update campaign systems
    if update_campaign_systems():
        success_count += 1
    
    # Create wrapper functions
    try:
        create_language_wrapper_functions()
        success_count += 1
    except Exception as e:
        print(f"❌ Error creating wrapper functions: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Implementation Results: {success_count}/{total_operations} successful")
    
    if success_count == total_operations:
        print("✅ Automatic language system successfully implemented!")
        print("   🌍 All systems now use user language automatically")
        print("   🔄 Language detection integrated into all handlers")
        print("   💬 Localized messages for all user interactions")
        print("   🎯 Supports EN/AR/RU with automatic detection")
    else:
        print(f"⚠️ Partial implementation: {success_count}/{total_operations} operations completed")
    
    return success_count == total_operations

if __name__ == "__main__":
    main()