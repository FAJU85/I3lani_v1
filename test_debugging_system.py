#!/usr/bin/env python3
"""
Test script to demonstrate the debugging system for I3lani Bot
Shows how to use step logging and debug utilities
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import (
    log_success, log_error, log_info, StepNames,
    debug_user_flow, debug_step_statistics, 
    get_step_analytics, clear_user_journey
)
from frequency_pricing import FrequencyPricingSystem

async def test_pricing_calculation():
    """Test the pricing calculation with step logging"""
    print("=" * 50)
    print("Testing Pricing Calculation with Step Logging")
    print("=" * 50)
    
    pricing_system = FrequencyPricingSystem()
    test_user_id = 123456
    
    # Clear any existing journey for clean test
    clear_user_journey(test_user_id)
    
    # Test various day selections
    test_cases = [
        {'days': 1, 'expected_discount': 0},
        {'days': 5, 'expected_discount': 7},
        {'days': 10, 'expected_discount': 12},  # This was the bug case
        {'days': 15, 'expected_discount': 15},
        {'days': 30, 'expected_discount': 20}
    ]
    
    print("\nTesting discount calculations:")
    for case in test_cases:
        days = case['days']
        expected_discount = case['expected_discount']
        
        try:
            # Calculate pricing with logging
            result = pricing_system.calculate_pricing(days, channels_count=2, user_id=test_user_id)
            
            actual_discount = result['discount_percent']
            final_price = result['final_cost_usd']
            
            status = "✅ PASS" if actual_discount == expected_discount else "❌ FAIL"
            print(f"{status} {days} days: Expected {expected_discount}%, Got {actual_discount}% (${final_price:.2f})")
            
            if actual_discount != expected_discount:
                log_error(StepNames.CALCULATE_PRICE, test_user_id, 
                         Exception(f"Discount mismatch: expected {expected_discount}%, got {actual_discount}%"),
                         {'days': days, 'expected': expected_discount, 'actual': actual_discount})
            
        except Exception as e:
            print(f"❌ ERROR {days} days: {e}")
            log_error(StepNames.CALCULATE_PRICE, test_user_id, e, {'days': days})
    
    # Show user journey
    print("\n" + "=" * 30)
    print("USER JOURNEY DEBUG:")
    print("=" * 30)
    debug_user_flow(test_user_id)
    
    return test_user_id

def test_step_logging():
    """Test various step logging scenarios"""
    print("\n" + "=" * 50)
    print("Testing Step Logging System")
    print("=" * 50)
    
    test_user_id = 789012
    
    # Clear previous data
    clear_user_journey(test_user_id)
    
    # Simulate user flow with logging
    log_success(StepNames.START_COMMAND, test_user_id, "User started bot")
    
    log_info(StepNames.LANGUAGE_SELECTION, test_user_id, "Selected English", {
        'language': 'en',
        'previous_language': None
    })
    
    log_success(StepNames.MAIN_MENU, test_user_id, "Displayed main menu")
    
    log_info(StepNames.CREATE_AD_START, test_user_id, "Started ad creation")
    
    log_success(StepNames.UPLOAD_CONTENT, test_user_id, "Uploaded text content", {
        'content_type': 'text',
        'content_length': 150
    })
    
    log_success(StepNames.SELECT_CHANNELS, test_user_id, "Selected 2 channels", {
        'channels': ['@i3lani', '@smshco'],
        'total_reach': 1000
    })
    
    log_success(StepNames.SELECT_DAYS, test_user_id, "Selected 10 days", {
        'days': 10
    })
    
    # Simulate payment flow
    log_info(StepNames.PAYMENT_METHOD_SELECTION, test_user_id, "Selected TON payment")
    
    log_success(StepNames.TON_PAYMENT_INIT, test_user_id, "TON payment initialized", {
        'amount_ton': 31.68,
        'amount_usd': 88.0,
        'wallet_address': 'UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB'
    })
    
    log_success(StepNames.TON_PAYMENT_CONFIRM, test_user_id, "Payment confirmed", {
        'transaction_hash': 'abc123def456',
        'confirmation_time': '2025-07-09T15:30:00Z'
    })
    
    # Show journey
    debug_user_flow(test_user_id)
    
    return test_user_id

def test_error_scenarios():
    """Test error logging scenarios"""
    print("\n" + "=" * 50)
    print("Testing Error Scenarios")
    print("=" * 50)
    
    test_user_id = 345678
    clear_user_journey(test_user_id)
    
    # Simulate various error scenarios
    
    # Database error
    log_error(StepNames.ERROR_DATABASE, test_user_id, 
              Exception("Database connection failed"), {
                  'operation': 'get_user',
                  'connection_string': 'postgresql://***'
              })
    
    # Payment timeout
    log_error(StepNames.PAYMENT_TIMEOUT, test_user_id,
              Exception("Payment timeout after 20 minutes"), {
                  'payment_method': 'TON',
                  'amount': 88.0,
                  'timeout_duration': 1200
              })
    
    # Callback timeout
    log_error(StepNames.CALLBACK_TIMEOUT, test_user_id,
              Exception("Callback query too old"), {
                  'callback_data': 'select_channel_i3lani',
                  'age_seconds': 3600
              })
    
    # Channel verification error
    log_error(StepNames.CHANNEL_VERIFICATION, test_user_id,
              Exception("Bot not admin in channel"), {
                  'channel': '@test_channel',
                  'bot_status': 'member'
              })
    
    debug_user_flow(test_user_id)
    
    return test_user_id

async def main():
    """Main test function"""
    print("🔍 I3lani Bot Debugging System Test")
    print("=" * 50)
    
    # Test pricing calculation (main bug fix)
    pricing_user = await test_pricing_calculation()
    
    # Test step logging
    logging_user = test_step_logging()
    
    # Test error scenarios
    error_user = test_error_scenarios()
    
    # Show overall statistics
    print("\n" + "=" * 50)
    print("OVERALL STEP STATISTICS")
    print("=" * 50)
    debug_step_statistics()
    
    # Show programmatic statistics
    stats = get_step_analytics()
    print("\nPROGRAMMATIC STATISTICS:")
    for step_name, data in stats.items():
        success_rate = data['success_rate']
        total = data['total']
        errors = data['error']
        print(f"  {step_name}: {success_rate:.1f}% success ({total} total, {errors} errors)")
    
    # Instructions for debugging
    print("\n" + "=" * 50)
    print("DEBUGGING INSTRUCTIONS")
    print("=" * 50)
    print("1. Use log_success() for successful steps")
    print("2. Use log_error() for errors with context")
    print("3. Use log_info() for informational steps")
    print("4. Use debug_user_flow(user_id) to see user journey")
    print("5. Use debug_step_statistics() to see overall stats")
    print("6. Check DEBUG_INSTRUCTIONS.md for complete guide")
    
    print("\n✅ Debugging system test completed!")
    print("📋 Check bot.log for detailed logs")
    print("📖 See DEBUG_INSTRUCTIONS.md for usage guide")

if __name__ == "__main__":
    asyncio.run(main())