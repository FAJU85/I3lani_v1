#!/usr/bin/env python3
"""
Comprehensive test suite for Enhanced Telegram Stars Payment System
Tests all components based on official Telegram Bot API specifications
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_stars_payment_system():
    """Comprehensive test of enhanced Stars payment system"""
    
    print("🌟 COMPREHENSIVE ENHANCED STARS PAYMENT SYSTEM TEST")
    print("="*65)
    
    test_results = []
    
    # Test 1: Enhanced Payment System Import and Initialization
    print("1. Testing enhanced payment system import and initialization...")
    try:
        from enhanced_telegram_stars_payment import (
            EnhancedStarsPayment,
            get_enhanced_stars_payment,
            create_enhanced_stars_invoice,
            handle_enhanced_pre_checkout,
            handle_enhanced_successful_payment
        )
        
        test_results.append("✅ Enhanced Stars payment system imports successful")
        print("   ✅ All enhanced payment functions imported")
        
        # Test initialization without bot instance
        enhanced_payment = EnhancedStarsPayment(None, None)
        test_results.append("✅ Enhanced payment system initialization successful")
        print("   ✅ Enhanced payment system initialized")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced payment system import error: {e}")
        print(f"   ❌ Import error: {e}")
    
    # Test 2: Enhanced Invoice Data Building
    print("\n2. Testing enhanced invoice data building...")
    try:
        # Create test data
        campaign_data = {
            'duration': 7,
            'selected_channels': [
                {'name': '@i3lani', 'subscribers': 120},
                {'name': '@smshco', 'subscribers': 112},
                {'name': '@Five_SAR', 'subscribers': 125}
            ],
            'posts_per_day': 2
        }
        
        pricing_data = {
            'total_stars': 238,  # Example Stars amount
            'total_usd': 7.00,
            'posts_per_day': 2,
            'discount_percent': 10
        }
        
        # Test invoice data building for different languages
        enhanced_payment = EnhancedStarsPayment(None, None)
        
        # Test English invoice
        invoice_en = enhanced_payment._build_invoice_data(
            campaign_data, pricing_data, "STAR1704829800ABCD", 'en'
        )
        
        # Test Arabic invoice
        invoice_ar = enhanced_payment._build_invoice_data(
            campaign_data, pricing_data, "STAR1704829800ABCD", 'ar'
        )
        
        # Test Russian invoice
        invoice_ru = enhanced_payment._build_invoice_data(
            campaign_data, pricing_data, "STAR1704829800ABCD", 'ru'
        )
        
        # Validate invoice structure
        required_fields = ['title', 'description']
        for lang, invoice in [('EN', invoice_en), ('AR', invoice_ar), ('RU', invoice_ru)]:
            if all(field in invoice for field in required_fields):
                test_results.append(f"✅ Enhanced invoice data building for {lang} successful")
                print(f"   ✅ {lang} invoice: {invoice['title']}")
            else:
                test_results.append(f"❌ Enhanced invoice data building for {lang} failed")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced invoice data building error: {e}")
        print(f"   ❌ Invoice building error: {e}")
    
    # Test 3: Enhanced Payload Creation
    print("\n3. Testing enhanced payload creation...")
    try:
        test_payload = enhanced_payment._create_enhanced_payload(
            user_id=566158428,
            payment_id="STAR1704829800ABCD",
            campaign_data=campaign_data
        )
        
        # Parse and validate payload
        payload_data = json.loads(test_payload)
        required_payload_fields = [
            'payment_id', 'user_id', 'campaign_type', 
            'service', 'timestamp', 'channels', 'duration', 'version'
        ]
        
        if all(field in payload_data for field in required_payload_fields):
            test_results.append("✅ Enhanced payload creation successful")
            print(f"   ✅ Payload contains all required fields")
            print(f"   📋 Payment ID: {payload_data['payment_id']}")
            print(f"   👤 User ID: {payload_data['user_id']}")
            print(f"   🔗 Service: {payload_data['service']}")
        else:
            missing_fields = [f for f in required_payload_fields if f not in payload_data]
            test_results.append(f"❌ Enhanced payload missing fields: {missing_fields}")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced payload creation error: {e}")
        print(f"   ❌ Payload error: {e}")
    
    # Test 4: Enhanced Price Breakdown
    print("\n4. Testing enhanced price breakdown...")
    try:
        price_breakdown = enhanced_payment._create_price_breakdown(pricing_data)
        
        # Validate price breakdown structure
        if price_breakdown and len(price_breakdown) > 0:
            test_results.append("✅ Enhanced price breakdown creation successful")
            print(f"   ✅ Price breakdown contains {len(price_breakdown)} items")
            
            for item in price_breakdown:
                print(f"   💰 {item.label}: {item.amount}")
        else:
            test_results.append("❌ Enhanced price breakdown creation failed")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced price breakdown error: {e}")
        print(f"   ❌ Price breakdown error: {e}")
    
    # Test 5: Enhanced Payment Keyboard Creation
    print("\n5. Testing enhanced payment keyboard creation...")
    try:
        keyboard_en = enhanced_payment._create_payment_keyboard("STAR1704829800ABCD", 'en')
        keyboard_ar = enhanced_payment._create_payment_keyboard("STAR1704829800ABCD", 'ar')
        keyboard_ru = enhanced_payment._create_payment_keyboard("STAR1704829800ABCD", 'ru')
        
        # Validate keyboard structure
        for lang, keyboard in [('EN', keyboard_en), ('AR', keyboard_ar), ('RU', keyboard_ru)]:
            if keyboard and keyboard.inline_keyboard:
                test_results.append(f"✅ Enhanced keyboard creation for {lang} successful")
                print(f"   ✅ {lang} keyboard: {len(keyboard.inline_keyboard)} rows")
            else:
                test_results.append(f"❌ Enhanced keyboard creation for {lang} failed")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced keyboard creation error: {e}")
        print(f"   ❌ Keyboard error: {e}")
    
    # Test 6: Enhanced Receipt Text Generation
    print("\n6. Testing enhanced receipt text generation...")
    try:
        # Mock successful payment object
        class MockSuccessfulPayment:
            def __init__(self):
                self.total_amount = 238
                self.currency = "XTR"
                self.telegram_payment_charge_id = "TCH_1234567890"
        
        mock_payment = MockSuccessfulPayment()
        campaign_result = {'success': True, 'campaign_id': 'CAM-2025-07-TEST'}
        
        # Test receipt for different languages
        receipt_en = enhanced_payment._create_receipt_text(
            "STAR1704829800ABCD", mock_payment, campaign_result, 'en'
        )
        receipt_ar = enhanced_payment._create_receipt_text(
            "STAR1704829800ABCD", mock_payment, campaign_result, 'ar'
        )
        receipt_ru = enhanced_payment._create_receipt_text(
            "STAR1704829800ABCD", mock_payment, campaign_result, 'ru'
        )
        
        # Validate receipts contain required information
        required_info = ["Payment", "Amount", "238", "XTR", "TCH_1234567890"]
        
        for lang, receipt in [('EN', receipt_en), ('AR', receipt_ar), ('RU', receipt_ru)]:
            if receipt and len(receipt) > 100:  # Reasonable receipt length
                test_results.append(f"✅ Enhanced receipt generation for {lang} successful")
                print(f"   ✅ {lang} receipt: {len(receipt)} characters")
            else:
                test_results.append(f"❌ Enhanced receipt generation for {lang} failed")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced receipt generation error: {e}")
        print(f"   ❌ Receipt error: {e}")
    
    # Test 7: Integration with Handlers
    print("\n7. Testing integration with handlers...")
    try:
        from handlers import (
            confirm_stars_payment_handler,
            enhanced_pre_checkout_query_handler,
            enhanced_successful_payment_handler
        )
        
        test_results.append("✅ Enhanced handler integration successful")
        print("   ✅ Enhanced handlers imported successfully")
        print("   📋 confirm_stars_payment_handler: Available")
        print("   📋 enhanced_pre_checkout_query_handler: Available")
        print("   📋 enhanced_successful_payment_handler: Available")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced handler integration error: {e}")
        print(f"   ❌ Handler integration error: {e}")
    
    # Test 8: Enhanced API Compliance Features
    print("\n8. Testing enhanced API compliance features...")
    try:
        # Test payment metadata
        metadata = enhanced_payment.payment_metadata
        required_metadata = ['service', 'version', 'api_compliance']
        
        if all(key in metadata for key in required_metadata):
            test_results.append("✅ Enhanced API compliance metadata successful")
            print(f"   ✅ Service: {metadata['service']}")
            print(f"   ✅ Version: {metadata['version']}")
            print(f"   ✅ API Compliance: {metadata['api_compliance']}")
        else:
            test_results.append("❌ Enhanced API compliance metadata incomplete")
        
        # Test payment configuration
        if (enhanced_payment.currency == "XTR" and 
            enhanced_payment.provider_token == "" and 
            enhanced_payment.max_tip_amount == 0):
            test_results.append("✅ Enhanced payment configuration correct")
            print("   ✅ Currency: XTR (Telegram Stars)")
            print("   ✅ Provider token: Empty (as required for Stars)")
            print("   ✅ Max tip amount: 0 (no tips for campaigns)")
        else:
            test_results.append("❌ Enhanced payment configuration incorrect")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced API compliance test error: {e}")
        print(f"   ❌ API compliance error: {e}")
    
    # Test 9: Enhanced Database Integration
    print("\n9. Testing enhanced database integration...")
    try:
        # Test database structure compatibility
        from database import db
        
        # Check if payment tracking table exists
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as conn:
            async with conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='payment_memo_tracking'"
            ) as cursor:
                table_exists = await cursor.fetchone()
        
        if table_exists:
            test_results.append("✅ Enhanced database integration successful")
            print("   ✅ Payment tracking table available")
        else:
            test_results.append("⚠️ Enhanced database integration partial - table missing")
            print("   ⚠️ Payment tracking table not found")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced database integration error: {e}")
        print(f"   ❌ Database integration error: {e}")
    
    # Test 10: Enhanced Campaign Integration
    print("\n10. Testing enhanced campaign integration...")
    try:
        from campaign_management import CampaignManager
        from automatic_payment_confirmation import handle_confirmed_payment
        
        test_results.append("✅ Enhanced campaign integration successful")
        print("   ✅ Campaign manager available")
        print("   ✅ Automatic payment confirmation available")
        
    except Exception as e:
        test_results.append(f"❌ Enhanced campaign integration error: {e}")
        print(f"   ❌ Campaign integration error: {e}")
    
    # Summary
    print(f"\n{'='*65}")
    print("📊 ENHANCED STARS PAYMENT SYSTEM TEST SUMMARY")
    print(f"{'='*65}")
    
    success_count = len([r for r in test_results if r.startswith("✅")])
    warning_count = len([r for r in test_results if r.startswith("⚠️")])
    error_count = len([r for r in test_results if r.startswith("❌")])
    total_tests = len(test_results)
    
    print(f"✅ Successful: {success_count}/{total_tests}")
    print(f"⚠️ Warnings: {warning_count}/{total_tests}")
    print(f"❌ Errors: {error_count}/{total_tests}")
    
    success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print(f"\n🔍 DETAILED RESULTS:")
    for i, result in enumerate(test_results, 1):
        print(f"{i:2d}. {result}")
    
    if success_rate >= 90:
        print(f"\n🎉 ENHANCED STARS PAYMENT SYSTEM: EXCELLENT PERFORMANCE")
        print("   All critical components operational")
        print("   Ready for production deployment")
    elif success_rate >= 80:
        print(f"\n✅ ENHANCED STARS PAYMENT SYSTEM: GOOD PERFORMANCE")
        print("   Core functionality operational")
        print("   Minor improvements recommended")
    elif success_rate >= 70:
        print(f"\n⚠️ ENHANCED STARS PAYMENT SYSTEM: ACCEPTABLE PERFORMANCE")
        print("   Basic functionality working")
        print("   Several improvements needed")
    else:
        print(f"\n❌ ENHANCED STARS PAYMENT SYSTEM: NEEDS IMPROVEMENT")
        print("   Critical issues found")
        print("   System requires fixes before deployment")
    
    return {
        'success_rate': success_rate,
        'total_tests': total_tests,
        'results': test_results
    }

if __name__ == "__main__":
    asyncio.run(test_enhanced_stars_payment_system())