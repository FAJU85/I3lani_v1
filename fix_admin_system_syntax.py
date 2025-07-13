#!/usr/bin/env python3
"""
Fix all syntax errors in admin_system.py
Remove misplaced import statements
"""

import re

def fix_admin_system_syntax():
    """Fix all syntax errors in admin_system.py"""
    
    # Read the file
    with open('admin_system.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove all misplaced import statements
    # Pattern to find misplaced imports that are not at the correct indentation level
    content = re.sub(r'^\s+from automatic_language_system import get_user_language_auto\s*$', '', content, flags=re.MULTILINE)
    
    # Find and fix any remaining syntax issues
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip empty lines that might cause issues
        if line.strip() == 'from automatic_language_system import get_user_language_auto':
            continue
            
        # Check for misplaced imports inside try blocks
        if 'from automatic_language_system import get_user_language_auto' in line and not line.strip().startswith('from'):
            # Remove the import part
            line = line.replace('from automatic_language_system import get_user_language_auto', '')
            line = line.strip()
            if not line:
                continue
        
        fixed_lines.append(line)
    
    # Join back together
    content = '\n'.join(fixed_lines)
    
    # Write back
    with open('admin_system.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed admin_system.py syntax errors")
    
    # Check syntax
    try:
        import ast
        ast.parse(content)
        print("✅ admin_system.py syntax is now valid")
        return True
    except SyntaxError as e:
        print(f"❌ Still has syntax error: {e}")
        return False

if __name__ == "__main__":
    fix_admin_system_syntax()