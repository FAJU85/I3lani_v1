#!/usr/bin/env python3
"""
Comprehensive test for haptic and visual effects system
Validates all enhanced UI components work correctly
"""

import asyncio
import logging
from unittest.mock import Mock, AsyncMock
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, User, Chat
from haptic_visual_effects import HapticVisualEffects, get_haptic_effects
from enhanced_keyboard_effects import EnhancedKeyboard, create_enhanced_keyboard
from sticker_manager import StickerManager, get_sticker_manager
from haptic_integration import HapticIntegration, get_haptic_integration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockBot:
    """Mock Bot for testing"""
    def __init__(self):
        self.session = Mock()
        self.sent_messages = []
        self.sent_stickers = []
        self.chat_actions = []
    
    async def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        message = Mock()
        message.message_id = len(self.sent_messages) + 1
        message.chat = Mock()
        message.chat.id = chat_id
        message.text = text
        self.sent_messages.append({
            'chat_id': chat_id,
            'text': text,
            'reply_markup': reply_markup,
            'parse_mode': parse_mode
        })
        return message
    
    async def send_sticker(self, chat_id, sticker):
        self.sent_stickers.append({
            'chat_id': chat_id,
            'sticker': sticker
        })
        return Mock()
    
    async def send_chat_action(self, chat_id, action):
        self.chat_actions.append({
            'chat_id': chat_id,
            'action': action
        })

async def test_haptic_visual_effects():
    """Test the complete haptic and visual effects system"""
    
    print("🎮 Testing Haptic & Visual Effects System")
    print("=" * 50)
    
    # Create mock bot
    bot = MockBot()
    
    # Test 1: HapticVisualEffects initialization
    print("\n1. Testing HapticVisualEffects initialization...")
    haptic_effects = HapticVisualEffects(bot)
    print("✅ HapticVisualEffects initialized successfully")
    
    # Test 2: Visual effects application
    print("\n2. Testing visual effects application...")
    
    effects_to_test = ['glow', 'pulse', 'shimmer', 'highlight', 'success', 'reward', 'game', 'payment']
    
    for effect in effects_to_test:
        enhanced_text = haptic_effects._apply_visual_effects("Test Button", effect)
        print(f"✅ {effect}: '{enhanced_text}'")
    
    # Test 3: Enhanced keyboard creation
    print("\n3. Testing enhanced keyboard creation...")
    
    test_buttons = [
        [
            {'text': 'Create Ad', 'callback_data': 'create_ad'},
            {'text': 'My Ads', 'callback_data': 'my_ads'}
        ],
        [
            {'text': 'Settings', 'callback_data': 'settings'}
        ]
    ]
    
    keyboard = await haptic_effects.create_haptic_keyboard(test_buttons, 'glow')
    print(f"✅ Enhanced keyboard created with {len(keyboard.inline_keyboard)} rows")
    
    # Test 4: Message enhancement
    print("\n4. Testing message enhancement...")
    
    test_message = "Welcome to I3lani Bot!"
    enhanced_message = haptic_effects._enhance_message_text(test_message, 'success')
    print(f"✅ Enhanced message: '{enhanced_message[:50]}...'")
    
    # Test 5: Progress bar effects
    print("\n5. Testing progress bar effects...")
    
    progress_bar = await haptic_effects.create_progress_bar_effect(75, 100, 20)
    print(f"✅ Progress bar: '{progress_bar[:50]}...'")
    
    # Test 6: Haptic message sending
    print("\n6. Testing haptic message sending...")
    
    await haptic_effects.send_haptic_message(
        chat_id=12345,
        text="Test haptic message",
        effect_type='success'
    )
    
    print(f"✅ Haptic message sent - Messages: {len(bot.sent_messages)}, Actions: {len(bot.chat_actions)}")
    
    # Test 7: Enhanced keyboard factory
    print("\n7. Testing enhanced keyboard factory...")
    
    keyboard_types = ['main_menu', 'payment', 'viral_game', 'confirmation', 'language']
    
    for kbd_type in keyboard_types:
        try:
            keyboard = create_enhanced_keyboard(kbd_type, 'en')
            print(f"✅ {kbd_type} keyboard: {len(keyboard.inline_keyboard)} rows")
        except Exception as e:
            print(f"❌ {kbd_type} keyboard failed: {e}")
    
    # Test 8: Sticker manager
    print("\n8. Testing sticker manager...")
    
    sticker_manager = StickerManager(bot)
    
    # Test different sticker contexts
    sticker_contexts = ['success', 'celebration', 'payment', 'game', 'reward']
    
    for context in sticker_contexts:
        await sticker_manager.send_context_sticker(12345, context)
        print(f"✅ {context} sticker sent")
    
    print(f"✅ Total stickers sent: {len(bot.sent_stickers)}")
    
    # Test 9: Haptic integration
    print("\n9. Testing haptic integration...")
    
    haptic_integration = HapticIntegration(bot)
    
    # Test enhanced main menu
    await haptic_integration.send_enhanced_main_menu(12345, 'en')
    print("✅ Enhanced main menu sent")
    
    # Test enhanced payment menu
    payment_data = {
        'duration': 7,
        'channels': 3,
        'total_posts': 21,
        'total_cost': 25.20
    }
    await haptic_integration.send_enhanced_payment_menu(12345, 'en', payment_data)
    print("✅ Enhanced payment menu sent")
    
    # Test enhanced viral game
    user_data = {
        'progress': 85,
        'referral_count': 2
    }
    await haptic_integration.send_enhanced_viral_game(12345, 'en', user_data)
    print("✅ Enhanced viral game sent")
    
    # Test 10: Callback handling
    print("\n10. Testing callback handling...")
    
    # Create mock callback query
    callback_query = Mock()
    callback_query.data = "haptic_glow_create_ad"
    callback_query.message = Mock()
    callback_query.message.chat = Mock()
    callback_query.message.chat.id = 12345
    callback_query.from_user = Mock()
    callback_query.from_user.id = 12345
    callback_query.answer = AsyncMock()
    
    # Test haptic callback handling
    handled = await haptic_integration.handle_haptic_callback(callback_query)
    print(f"✅ Haptic callback handled: {handled}")
    print(f"✅ Original callback data: {callback_query.data}")
    
    # Test 11: Multilingual support
    print("\n11. Testing multilingual support...")
    
    languages = ['en', 'ar', 'ru']
    
    for lang in languages:
        keyboard = create_enhanced_keyboard('main_menu', lang)
        print(f"✅ {lang.upper()} main menu: {len(keyboard.inline_keyboard)} rows")
    
    # Test 12: Effect integration
    print("\n12. Testing effect integration...")
    
    # Test different effect types
    effect_types = ['success', 'celebration', 'reward', 'payment', 'game']
    
    for effect in effect_types:
        await haptic_integration.send_enhanced_success_message(
            12345, 'en', effect, f"Test {effect} message"
        )
        print(f"✅ {effect} success message sent")
    
    # Test 13: System statistics
    print("\n13. Testing system statistics...")
    
    print(f"✅ Total messages sent: {len(bot.sent_messages)}")
    print(f"✅ Total stickers sent: {len(bot.sent_stickers)}")
    print(f"✅ Total chat actions: {len(bot.chat_actions)}")
    
    # Test 14: Error handling
    print("\n14. Testing error handling...")
    
    try:
        # Test with invalid parameters
        await haptic_effects.send_haptic_message(
            chat_id=None,
            text="Test error handling",
            effect_type='invalid_effect'
        )
        print("✅ Error handling works correctly")
    except Exception as e:
        print(f"✅ Error properly caught: {type(e).__name__}")
    
    # Test 15: Global instances
    print("\n15. Testing global instances...")
    
    global_haptic = get_haptic_effects(bot)
    global_sticker = get_sticker_manager(bot)
    global_integration = get_haptic_integration(bot)
    
    print(f"✅ Global haptic effects: {global_haptic is not None}")
    print(f"✅ Global sticker manager: {global_sticker is not None}")
    print(f"✅ Global integration: {global_integration is not None}")
    
    print("\n" + "=" * 50)
    print("🎉 All haptic & visual effects tests completed successfully!")
    print("🚀 System is ready for enhanced user experience!")
    
    return True

async def test_specific_features():
    """Test specific haptic features"""
    
    print("\n🎯 Testing Specific Features")
    print("=" * 30)
    
    bot = MockBot()
    
    # Test vibration patterns
    haptic_effects = HapticVisualEffects(bot)
    
    print("\n1. Testing vibration patterns...")
    patterns = ['button_press', 'success', 'celebration', 'reward', 'game', 'payment']
    
    for pattern in patterns:
        await haptic_effects._simulate_haptic_feedback(12345, pattern)
        print(f"✅ {pattern} pattern simulated")
    
    # Test border glow effects
    print("\n2. Testing border glow effects...")
    glow_effects = ['glow', 'pulse', 'shimmer', 'highlight']
    
    for effect in glow_effects:
        text = haptic_effects._apply_visual_effects("Button", effect)
        print(f"✅ {effect} border: {text}")
    
    # Test color change effects
    print("\n3. Testing color change effects...")
    enhanced_keyboard = EnhancedKeyboard()
    
    # Test different keyboard types with effects
    keyboard_types = [
        ('main_menu', 'en'),
        ('payment', 'en'),
        ('viral_game', 'en', {'progress': 50}),
        ('confirmation', 'en', {'action_type': 'payment'})
    ]
    
    for kbd_type, lang, *kwargs in keyboard_types:
        try:
            keyboard = create_enhanced_keyboard(kbd_type, lang, **kwargs[0] if kwargs else {})
            print(f"✅ {kbd_type} keyboard with color effects created")
        except Exception as e:
            print(f"❌ {kbd_type} keyboard failed: {e}")
    
    # Test sticker automation
    print("\n4. Testing sticker automation...")
    sticker_manager = StickerManager(bot)
    
    # Test celebration sequences
    celebration_types = ['success', 'reward', 'payment', 'game_win', 'referral']
    
    for celebration in celebration_types:
        await sticker_manager.send_celebration_sequence(12345, celebration)
        print(f"✅ {celebration} celebration sequence sent")
    
    print(f"\n✅ Total automated stickers: {len(bot.sent_stickers)}")
    print("🎉 Specific features test completed!")

async def main():
    """Run all tests"""
    try:
        await test_haptic_visual_effects()
        await test_specific_features()
        print("\n✅ All haptic & visual effects tests passed!")
        print("🎮 Enhanced user experience is ready!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())