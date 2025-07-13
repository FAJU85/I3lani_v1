#!/usr/bin/env python3
"""
Fix indentation errors in admin_system.py
"""

import re

def fix_admin_indentation():
    """Fix indentation issues in admin_system.py"""
    with open('admin_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific indentation error on line 890
    # Replace "from automatic_language_system import get_user_language_auto" with proper indentation
    content = re.sub(
        r'^from automatic_language_system import get_user_language_auto$',
        '    from automatic_language_system import get_user_language_auto',
        content,
        flags=re.MULTILINE
    )
    
    # Write back
    with open('admin_system.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed indentation in admin_system.py")

if __name__ == "__main__":
    fix_admin_indentation()