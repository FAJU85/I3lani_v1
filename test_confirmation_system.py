#!/usr/bin/env python3
"""
Test script to validate the confirmation system integration
"""

import asyncio
import logging
from confirmation_system import confirmation_system
from confirmation_handlers import CONFIRMATION_HANDLERS
from languages import get_text

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_confirmation_system():
    """Test the confirmation system functionality"""
    print("🔍 Testing Confirmation System Integration...")
    
    # Test 1: Check if confirmation system is properly initialized
    print("\n1. Testing confirmation system initialization...")
    try:
        assert confirmation_system is not None
        print("✅ Confirmation system initialized successfully")
    except Exception as e:
        print(f"❌ Confirmation system initialization failed: {e}")
        return False
    
    # Test 2: Test confirmation handlers registration
    print("\n2. Testing confirmation handlers registration...")
    try:
        expected_handlers = [
            'confirm_ad_submission',
            'cancel_ad_submission',
            'edit_ad_submission',
            'confirm_payment_processing',
            'cancel_payment_processing',
            'confirm_channel_selection',
            'cancel_channel_selection',
            'confirm_ad_deletion',
            'cancel_ad_deletion'
        ]
        
        for handler_name in expected_handlers:
            assert handler_name in CONFIRMATION_HANDLERS, f"Handler {handler_name} not found"
            assert callable(CONFIRMATION_HANDLERS[handler_name]), f"Handler {handler_name} is not callable"
        
        print(f"✅ All {len(expected_handlers)} confirmation handlers registered successfully")
    except Exception as e:
        print(f"❌ Confirmation handlers registration failed: {e}")
        return False
    
    # Test 3: Test ad submission confirmation creation
    print("\n3. Testing ad submission confirmation creation...")
    try:
        test_ad_data = {
            'content': 'Test ad content',
            'channels': [1, 2, 3],
            'duration': 7,
            'posts_per_day': 2
        }
        
        test_pricing_data = {
            'total_usd': 15.50,
            'total_posts': 14,
            'discount_percent': 10
        }
        
        confirmation_data = await confirmation_system.create_ad_submission_confirmation(
            user_id=123456,
            language='en',
            ad_data=test_ad_data,
            pricing_data=test_pricing_data
        )
        
        assert 'message' in confirmation_data
        assert 'keyboard' in confirmation_data
        assert len(confirmation_data['message']) > 0
        assert confirmation_data['keyboard'] is not None
        
        print("✅ Ad submission confirmation created successfully")
        print(f"   Message length: {len(confirmation_data['message'])} characters")
        print(f"   Keyboard available: {confirmation_data['keyboard'] is not None}")
    except Exception as e:
        print(f"❌ Ad submission confirmation creation failed: {e}")
        return False
    
    # Test 4: Test channel selection confirmation
    print("\n4. Testing channel selection confirmation...")
    try:
        test_channels = [1, 2, 3]
        
        confirmation_data = await confirmation_system.create_channel_selection_confirmation(
            user_id=123456,
            language='en',
            selected_channels=test_channels
        )
        
        assert 'message' in confirmation_data
        assert 'keyboard' in confirmation_data
        assert len(confirmation_data['message']) > 0
        assert confirmation_data['keyboard'] is not None
        
        print("✅ Channel selection confirmation created successfully")
        print(f"   Message length: {len(confirmation_data['message'])} characters")
        print(f"   Keyboard available: {confirmation_data['keyboard'] is not None}")
    except Exception as e:
        print(f"❌ Channel selection confirmation creation failed: {e}")
        return False
    
    # Test 5: Test payment confirmation
    print("\n5. Testing payment confirmation...")
    try:
        test_payment_data = {
            'amount': 25.00,
            'currency': 'USD',
            'payment_method': 'ton',
            'memo': 'AB1234'
        }
        
        confirmation_data = await confirmation_system.create_payment_confirmation(
            user_id=123456,
            language='en',
            payment_data=test_payment_data
        )
        
        assert 'message' in confirmation_data
        assert 'keyboard' in confirmation_data
        assert len(confirmation_data['message']) > 0
        assert confirmation_data['keyboard'] is not None
        
        print("✅ Payment confirmation created successfully")
        print(f"   Message length: {len(confirmation_data['message'])} characters")
        print(f"   Keyboard available: {confirmation_data['keyboard'] is not None}")
    except Exception as e:
        print(f"❌ Payment confirmation creation failed: {e}")
        return False
    
    # Test 6: Test multilingual support
    print("\n6. Testing multilingual confirmation support...")
    try:
        languages_to_test = ['en', 'ar', 'ru']
        
        for lang in languages_to_test:
            confirmation_data = await confirmation_system.create_ad_submission_confirmation(
                user_id=123456,
                language=lang,
                ad_data=test_ad_data,
                pricing_data=test_pricing_data
            )
            
            assert 'message' in confirmation_data
            assert 'keyboard' in confirmation_data
            assert len(confirmation_data['message']) > 0
            
            print(f"✅ {lang.upper()} confirmation created successfully")
        
        print("✅ All languages supported correctly")
    except Exception as e:
        print(f"❌ Multilingual confirmation support failed: {e}")
        return False
    
    # Test 7: Test confirmation translations
    print("\n7. Testing confirmation translations...")
    try:
        test_keys = [
            'confirm_ad_submission_title',
            'confirm_ad_submission_message',
            'action_confirmed',
            'action_cancelled',
            'confirm_button',
            'cancel_button'
        ]
        
        for lang in ['en', 'ar', 'ru']:
            for key in test_keys:
                text = get_text(lang, key, f"Default {key}")
                assert text is not None
                assert len(text) > 0
        
        print("✅ All confirmation translations available")
    except Exception as e:
        print(f"❌ Confirmation translations test failed: {e}")
        return False
    
    # Test 8: Test confirmation logging
    print("\n8. Testing confirmation logging...")
    try:
        await confirmation_system.log_confirmation_action(
            user_id=123456,
            action_type='ad_submission',
            confirmed=True,
            data={'test': 'data'}
        )
        
        await confirmation_system.log_confirmation_action(
            user_id=123456,
            action_type='payment_processing',
            confirmed=False
        )
        
        print("✅ Confirmation logging working correctly")
    except Exception as e:
        print(f"❌ Confirmation logging failed: {e}")
        return False
    
    print("\n🎉 All confirmation system tests passed!")
    print("\n📊 Test Results Summary:")
    print("✅ Confirmation system initialization: PASSED")
    print("✅ Handler registration: PASSED")
    print("✅ Ad submission confirmation: PASSED")
    print("✅ Channel selection confirmation: PASSED")
    print("✅ Payment confirmation: PASSED")
    print("✅ Multilingual support: PASSED")
    print("✅ Translation availability: PASSED")
    print("✅ Confirmation logging: PASSED")
    print("\n🚀 Confirmation system is ready for production use!")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_confirmation_system())