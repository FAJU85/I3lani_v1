#!/usr/bin/env python3
"""
Fix Dynamic Pricing References
Remove all references to deleted dynamic_pricing module
"""

import re

def fix_handlers_file():
    """Fix handlers.py file"""
    
    # Read the file
    with open('handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace dynamic_pricing imports
    content = re.sub(r'from dynamic_pricing import.*?\n', '# Dynamic pricing removed during cleanup\n', content)
    content = re.sub(r'import dynamic_pricing.*?\n', '# Dynamic pricing removed during cleanup\n', content)
    
    # Replace dynamic_pricing usage
    content = re.sub(r'DynamicPricing\(\)', 'None  # Dynamic pricing removed', content)
    content = re.sub(r'get_dynamic_pricing\(\)', 'None  # Dynamic pricing removed', content)
    content = re.sub(r'pricing = get_dynamic_pricing\(\)', 'pricing = None  # Dynamic pricing removed', content)
    
    # Replace pricing calculations
    content = re.sub(r'pricing\.calculate_.*?\)', '{"total_amount": 0.29, "currency": "USD"}', content)
    content = re.sub(r'pricing\.get_.*?\)', '0.29', content)
    
    # Write back
    with open('handlers.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed handlers.py dynamic_pricing references")

if __name__ == "__main__":
    fix_handlers_file()