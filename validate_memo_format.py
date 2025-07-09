#!/usr/bin/env python3
"""
Simple validation script for payment memo format bug fix
"""

import sys
import os
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from payments import PaymentProcessor


def main():
    print("🚀 Payment Memo Format Validation")
    print("="*50)
    
    # Create payment processor
    processor = PaymentProcessor()
    
    # Test memo generation
    print("\n📝 Testing memo generation...")
    
    # Generate 20 memos for testing
    memos = []
    for i in range(20):
        memo = processor.generate_memo()
        memos.append(memo)
        
    print(f"Generated memos: {memos}")
    
    # Validate format
    pattern = re.compile(r'^[A-Z]{2}\d{4}$')
    
    print("\n🧪 Format validation results:")
    
    all_valid = True
    for memo in memos:
        is_valid = pattern.match(memo) is not None
        length_ok = len(memo) == 6
        letters_ok = memo[:2].isalpha() and memo[:2].isupper()
        digits_ok = memo[2:].isdigit()
        
        status = "✅" if is_valid and length_ok and letters_ok and digits_ok else "❌"
        print(f"{status} {memo} - Length: {len(memo)}, Letters: {memo[:2]}, Digits: {memo[2:]}")
        
        if not (is_valid and length_ok and letters_ok and digits_ok):
            all_valid = False
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Format: 2 letters + 4 digits")
    print(f"   Pattern: [A-Z]{2}[0-9]{4}")
    print(f"   All valid: {'✅ YES' if all_valid else '❌ NO'}")
    print(f"   Total combinations: {26**2 * 10**4:,}")
    
    if all_valid:
        print("\n🎉 BUG FIX SUCCESSFUL!")
        print("   Payment memo format is now exactly 2 letters + 4 digits")
        print("   Old long format (AD{user_id}_{timestamp}) has been replaced")
        print("   User experience significantly improved")
    else:
        print("\n❌ BUG FIX FAILED - Some memos are invalid")
    
    print("="*50)
    
    return all_valid


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)