#!/usr/bin/env python3
"""
Fix Stars payment system - change pricing_calculation to pricing_data
"""

import re

def fix_stars_payment():
    """Fix Stars payment handler to use pricing_data instead of pricing_calculation"""
    
    with open('handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the specific occurrences in Stars payment handlers
    # Pattern 1: pay_frequency_stars_handler
    pattern1 = r'(@router\.callback_query\(F\.data == "pay_freq_stars"\)\nasync def pay_frequency_stars_handler.*?)\n    pricing_calculation = data\.get\(\'pricing_calculation\', \{\}\)\n    \n    if not pricing_calculation:\n        await callback_query\.answer\("❌ Pricing data not found"\)\n        return\n    \n    # Get Stars amount from calculation  \n    stars_amount = pricing_calculation\.get\(\'total_stars\', 0\)'
    
    replacement1 = r'\1\n    pricing_data = data.get(\'pricing_data\', {})\n    \n    if not pricing_data:\n        await callback_query.answer("❌ Pricing data not found")\n        return\n    \n    # Get Stars amount from pricing data\n    stars_amount = pricing_data.get(\'cost_stars\', 0)'
    
    # Apply the replacement
    content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
    
    # Write the fixed content back
    with open('handlers.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed Stars payment handler to use pricing_data instead of pricing_calculation")

if __name__ == "__main__":
    fix_stars_payment()