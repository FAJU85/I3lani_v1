#!/usr/bin/env python3
"""
Simple debug to test package selection components
"""

from keyboards import get_package_keyboard
from languages import get_text
from config import PACKAGES
from models import storage, Advertisement, AdContent, AdStatus, PaymentStatus
import uuid
from datetime import datetime

def test_components():
    print("🔍 DEBUGGING PACKAGE SELECTION COMPONENTS")
    print("=" * 50)
    
    # Test 1: Basic keyboard generation
    print("\n1. Testing Package Keyboard:")
    user_id = 123456
    
    try:
        keyboard = get_package_keyboard(user_id)
        print(f"   ✅ Keyboard created: {len(keyboard.inline_keyboard)} rows")
        
        for row in keyboard.inline_keyboard:
            for btn in row:
                print(f"   📋 {btn.text} -> {btn.callback_data}")
    except Exception as e:
        print(f"   ❌ Keyboard failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Create test advertisement
    print("\n2. Testing Advertisement Storage:")
    
    try:
        ad_content = AdContent(text="Test advertisement", content_type="text")
        ad = Advertisement(
            id=str(uuid.uuid4()),
            user_id=user_id,
            username="testuser",
            content=ad_content,
            package_id="starter",
            price=0.099,
            status=AdStatus.DRAFT,
            created_at=datetime.now(),
            payment_status=PaymentStatus.PENDING,
            total_posts=2,
            repost_frequency_days=7
        )
        
        storage.save_ad(ad)
        retrieved = storage.get_user_current_ad(user_id)
        
        if retrieved:
            print(f"   ✅ Ad stored and retrieved: {retrieved.id}")
            print(f"   📝 Content: {retrieved.content.text}")
        else:
            print("   ❌ Ad not found after storage")
            
    except Exception as e:
        print(f"   ❌ Storage failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test package text generation
    print("\n3. Testing Package Text Generation:")
    
    for package_id, package in PACKAGES.items():
        try:
            text = get_text(user_id, "package_details",
                name=package['name'],
                price=package['price'],
                duration=package['duration_days'],
                frequency=package['repost_frequency_days'],
                total_posts=package['total_posts']
            )
            print(f"   ✅ {package_id}: Text generated successfully")
        except Exception as e:
            print(f"   ❌ {package_id}: Failed - {e}")
    
    # Test 4: Test callback data parsing
    print("\n4. Testing Callback Data Parsing:")
    
    test_callbacks = [
        "package_starter",
        "package_pro",
        "package_growth", 
        "package_elite"
    ]
    
    for callback_data in test_callbacks:
        try:
            package_id = callback_data.replace("package_", "")
            if package_id in PACKAGES:
                print(f"   ✅ {callback_data} -> {package_id}")
            else:
                print(f"   ❌ {callback_data} -> Invalid package: {package_id}")
        except Exception as e:
            print(f"   ❌ {callback_data} -> Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 COMPONENT TEST COMPLETED")

if __name__ == "__main__":
    test_components()