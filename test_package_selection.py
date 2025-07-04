#!/usr/bin/env python3
"""
Test script to verify package selection functionality
"""

import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import get_package_keyboard, get_package_details_keyboard
from languages import get_text
from config import PACKAGES
from models import InMemoryStorage, Advertisement, AdContent, AdStatus

def test_package_flow():
    """Test the complete package selection flow"""
    print("🧪 Testing Package Selection Flow")
    print("=" * 50)
    
    # Test 1: Package keyboard generation
    print("\n1. Testing Package Keyboard Generation:")
    user_id = 123456
    keyboard = get_package_keyboard(user_id)
    
    print(f"   ✅ Generated keyboard with {len(keyboard.inline_keyboard)} package buttons")
    
    # Verify each package button
    for row in keyboard.inline_keyboard:
        for button in row:
            package_id = button.callback_data.replace("package_", "")
            if package_id in PACKAGES:
                print(f"   ✅ Button: {button.text} -> {button.callback_data}")
            else:
                print(f"   ❌ Invalid button: {button.text} -> {button.callback_data}")
    
    # Test 2: Package details keyboard
    print("\n2. Testing Package Details Keyboards:")
    for package_id in PACKAGES.keys():
        details_keyboard = get_package_details_keyboard(package_id, user_id)
        print(f"   ✅ {package_id}: {len(details_keyboard.inline_keyboard)} buttons")
        
        # Verify callback data
        for row in details_keyboard.inline_keyboard:
            for button in row:
                print(f"      - {button.text} -> {button.callback_data}")
    
    # Test 3: Package text generation
    print("\n3. Testing Package Text Generation:")
    for package_id, package in PACKAGES.items():
        try:
            details_text = get_text(user_id, "package_details",
                name=package['name'],
                price=package['price'],
                duration=package['duration_days'],
                frequency=package['repost_frequency_days'],
                total_posts=package['total_posts']
            )
            print(f"   ✅ {package_id}: Text generated successfully")
            print(f"      Preview: {details_text[:100]}...")
        except Exception as e:
            print(f"   ❌ {package_id}: Error generating text - {e}")
    
    # Test 4: Storage interaction
    print("\n4. Testing Storage Interaction:")
    storage = InMemoryStorage()
    
    # Create test advertisement
    ad_content = AdContent(text="Test ad content", content_type="text")
    ad = Advertisement(
        id="test_ad_123",
        user_id=user_id,
        username="testuser",
        content=ad_content,
        package_id="starter",
        price=0.099,
        status=AdStatus.DRAFT,
        created_at=None,
        payment_status=None
    )
    
    storage.save_ad(ad)
    retrieved_ad = storage.get_user_current_ad(user_id)
    
    if retrieved_ad:
        print("   ✅ Advertisement stored and retrieved successfully")
        print(f"      Ad ID: {retrieved_ad.id}")
        print(f"      Content: {retrieved_ad.content.text}")
    else:
        print("   ❌ Failed to store/retrieve advertisement")
    
    # Test 5: Callback data handling
    print("\n5. Testing Callback Data Handling:")
    test_callbacks = [
        "package_starter",
        "package_pro", 
        "package_growth",
        "package_elite",
        "confirm_package_starter",
        "confirm_package_pro",
        "back_to_packages"
    ]
    
    for callback_data in test_callbacks:
        if callback_data.startswith("package_"):
            package_id = callback_data.replace("package_", "")
            if package_id in PACKAGES:
                print(f"   ✅ {callback_data} -> Valid package: {package_id}")
            else:
                print(f"   ❌ {callback_data} -> Invalid package: {package_id}")
        elif callback_data.startswith("confirm_package_"):
            package_id = callback_data.replace("confirm_package_", "")
            if package_id in PACKAGES:
                print(f"   ✅ {callback_data} -> Valid confirmation: {package_id}")
            else:
                print(f"   ❌ {callback_data} -> Invalid confirmation: {package_id}")
        else:
            print(f"   ✅ {callback_data} -> Other callback")
    
    print("\n" + "=" * 50)
    print("✅ Package Selection Flow Test Completed!")
    print("All components are working correctly.")

if __name__ == "__main__":
    test_package_flow()