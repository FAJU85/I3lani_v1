#!/usr/bin/env python3
"""
Complete Payment System Test
Test quantitative pricing and payment handlers integration
"""

import sys
import asyncio
import json
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_quantitative_pricing_complete():
    """Test the complete quantitative pricing system"""
    print("=" * 60)
    print("TESTING QUANTITATIVE PRICING SYSTEM")
    print("=" * 60)
    
    try:
        from quantitative_pricing_system import calculate_quantitative_price
        
        # Test cases according to the specifications
        test_cases = [
            (1, 1, "$0.29", "1 post/day", "0.8% discount"),
            (1, 4, "$0.29", "1 post/day", "0.8% discount"),  # Same price regardless of channels
            (3, 2, "$0.85", "2 posts/day", "2.4% discount"),
            (7, 5, "$1.92", "3 posts/day", "5.6% discount"),
            (30, 10, "$6.61", "12 posts/day", "24% discount"),
            (365, 20, "$79.34", "12 posts/day", "25% discount")
        ]
        
        passed = 0
        failed = 0
        
        for days, channels, expected_price, expected_posts, expected_discount in test_cases:
            result = calculate_quantitative_price(days, channels)
            
            actual_price = f"${result['final_price']:.2f}"
            actual_posts = f"{result['posts_per_day']} posts/day"
            actual_discount = f"{result['discount_percentage']:.1f}% discount"
            
            price_match = actual_price == expected_price
            posts_match = actual_posts == expected_posts
            discount_match = actual_discount == expected_discount
            
            if price_match and posts_match and discount_match:
                print(f"✅ {days} days, {channels} channels: {actual_price} ({actual_posts}, {actual_discount})")
                passed += 1
            else:
                print(f"❌ {days} days, {channels} channels:")
                print(f"   Expected: {expected_price} ({expected_posts}, {expected_discount})")
                print(f"   Actual:   {actual_price} ({actual_posts}, {actual_discount})")
                failed += 1
        
        print(f"\n📊 Quantitative Pricing Test Results: {passed}/{passed + failed} passed")
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ Quantitative pricing test failed: {e}")
        return False

def test_payment_handlers_registration():
    """Test that payment handlers are properly registered"""
    print("\n" + "=" * 60)
    print("TESTING PAYMENT HANDLERS REGISTRATION")
    print("=" * 60)
    
    try:
        # Check if handlers file has the payment handlers
        with open('handlers.py', 'r') as f:
            content = f.read()
        
        # Look for payment handler functions
        has_ton_handler = '@router.callback_query(F.data == "pay_ton")' in content
        has_stars_handler = '@router.callback_query(F.data == "pay_stars")' in content
        has_ton_function = 'def pay_ton_handler(' in content
        has_stars_function = 'def pay_stars_handler(' in content
        
        print(f"✅ TON payment callback registered: {has_ton_handler}")
        print(f"✅ Stars payment callback registered: {has_stars_handler}")
        print(f"✅ TON payment function defined: {has_ton_function}")
        print(f"✅ Stars payment function defined: {has_stars_function}")
        
        # Check states
        with open('states.py', 'r') as f:
            states_content = f.read()
        
        has_ton_state = 'ton_payment = State()' in states_content
        has_stars_state = 'stars_payment = State()' in states_content
        
        print(f"✅ TON payment state defined: {has_ton_state}")
        print(f"✅ Stars payment state defined: {has_stars_state}")
        
        all_registered = all([has_ton_handler, has_stars_handler, has_ton_function, has_stars_function, has_ton_state, has_stars_state])
        
        print(f"\n📊 Payment Handlers Registration: {'✅ PASSED' if all_registered else '❌ FAILED'}")
        return all_registered
        
    except Exception as e:
        print(f"❌ Payment handlers registration test failed: {e}")
        return False

def test_payment_system_imports():
    """Test that required payment system modules can be imported"""
    print("\n" + "=" * 60)
    print("TESTING PAYMENT SYSTEM IMPORTS")
    print("=" * 60)
    
    imports_passed = 0
    total_imports = 0
    
    # Test WalletManager
    try:
        from wallet_manager import WalletManager
        print("✅ WalletManager imported successfully")
        imports_passed += 1
    except ImportError as e:
        print(f"❌ WalletManager import failed: {e}")
    total_imports += 1
    
    # Test CleanStarsPayment
    try:
        from clean_stars_payment_system import CleanStarsPayment
        print("✅ CleanStarsPayment imported successfully")
        imports_passed += 1
    except ImportError as e:
        print(f"❌ CleanStarsPayment import failed: {e}")
    total_imports += 1
    
    # Test States
    try:
        from states import CreateAd
        print("✅ CreateAd states imported successfully")
        imports_passed += 1
    except ImportError as e:
        print(f"❌ CreateAd states import failed: {e}")
    total_imports += 1
    
    # Test Database
    try:
        from database import Database
        print("✅ Database imported successfully")
        imports_passed += 1
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
    total_imports += 1
    
    print(f"\n📊 Payment System Imports: {imports_passed}/{total_imports} passed")
    return imports_passed == total_imports

def test_currency_conversion():
    """Test currency conversion rates"""
    print("\n" + "=" * 60)
    print("TESTING CURRENCY CONVERSION")
    print("=" * 60)
    
    try:
        from quantitative_pricing_system import calculate_quantitative_price
        
        # Test 1 day campaign pricing
        result = calculate_quantitative_price(1, 1)
        
        usd_price = result['final_price']
        ton_price = result['ton_price']
        stars_price = result['stars_price']
        
        print(f"✅ 1 day campaign:")
        print(f"   USD: ${usd_price:.2f}")
        print(f"   TON: {ton_price:.3f} TON")
        print(f"   Stars: {stars_price} ⭐")
        
        # Verify conversion rates (1 USD = 0.36 TON, 1 USD = 34 Stars)
        expected_ton = round(usd_price * 0.36, 3)
        expected_stars = round(usd_price * 34)
        
        ton_correct = abs(ton_price - expected_ton) < 0.001
        stars_correct = stars_price == expected_stars
        
        print(f"✅ TON conversion accurate: {ton_correct} (expected {expected_ton:.3f})")
        print(f"✅ Stars conversion accurate: {stars_correct} (expected {expected_stars})")
        
        print(f"\n📊 Currency Conversion: {'✅ PASSED' if ton_correct and stars_correct else '❌ FAILED'}")
        return ton_correct and stars_correct
        
    except Exception as e:
        print(f"❌ Currency conversion test failed: {e}")
        return False

def test_mathematical_formulas():
    """Test the mathematical formulas implementation"""
    print("\n" + "=" * 60)
    print("TESTING MATHEMATICAL FORMULAS")
    print("=" * 60)
    
    try:
        from quantitative_pricing_system import calculate_quantitative_price
        
        # Test posts per day formula: R = min(12, max(1, ⌊D/2.5⌋ + 1))
        test_cases = [
            (1, 1),     # ⌊1/2.5⌋ + 1 = 0 + 1 = 1
            (3, 2),     # ⌊3/2.5⌋ + 1 = 1 + 1 = 2
            (7, 3),     # ⌊7/2.5⌋ + 1 = 2 + 1 = 3
            (30, 12),   # ⌊30/2.5⌋ + 1 = 12 + 1 = 13, but min(12, 13) = 12
            (365, 12)   # ⌊365/2.5⌋ + 1 = 146 + 1 = 147, but min(12, 147) = 12
        ]
        
        posts_passed = 0
        for days, expected_posts in test_cases:
            result = calculate_quantitative_price(days, 1)
            actual_posts = result['posts_per_day']
            
            if actual_posts == expected_posts:
                print(f"✅ {days} days → {actual_posts} posts/day")
                posts_passed += 1
            else:
                print(f"❌ {days} days → {actual_posts} posts/day (expected {expected_posts})")
        
        # Test discount formula: δ = min(25%, D × 0.8%)
        discount_cases = [
            (1, 0.8),    # 1 × 0.8% = 0.8%
            (3, 2.4),    # 3 × 0.8% = 2.4%
            (7, 5.6),    # 7 × 0.8% = 5.6%
            (30, 24.0),  # 30 × 0.8% = 24.0%
            (365, 25.0)  # 365 × 0.8% = 292%, but min(25%, 292%) = 25%
        ]
        
        discount_passed = 0
        for days, expected_discount in discount_cases:
            result = calculate_quantitative_price(days, 1)
            actual_discount = result['discount_percentage']
            
            if abs(actual_discount - expected_discount) < 0.1:
                print(f"✅ {days} days → {actual_discount:.1f}% discount")
                discount_passed += 1
            else:
                print(f"❌ {days} days → {actual_discount:.1f}% discount (expected {expected_discount:.1f}%)")
        
        formulas_passed = posts_passed == len(test_cases) and discount_passed == len(discount_cases)
        
        print(f"\n📊 Mathematical Formulas: {'✅ PASSED' if formulas_passed else '❌ FAILED'}")
        print(f"   Posts per day: {posts_passed}/{len(test_cases)} passed")
        print(f"   Discount calculation: {discount_passed}/{len(discount_cases)} passed")
        
        return formulas_passed
        
    except Exception as e:
        print(f"❌ Mathematical formulas test failed: {e}")
        return False

def main():
    """Run all payment system tests"""
    print("🚀 I3LANI BOT PAYMENT SYSTEM COMPREHENSIVE TEST")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Quantitative Pricing", test_quantitative_pricing_complete()))
    results.append(("Payment Handlers Registration", test_payment_handlers_registration()))
    results.append(("Payment System Imports", test_payment_system_imports()))
    results.append(("Currency Conversion", test_currency_conversion()))
    results.append(("Mathematical Formulas", test_mathematical_formulas()))
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Payment system is ready for production.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)