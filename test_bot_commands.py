"""
Test script to verify bot commands are working correctly
"""
import asyncio
from enhanced_simple import start_command, dashboard_command, referral_command
from aiogram.types import Message, User, Chat
from unittest.mock import AsyncMock, MagicMock

class MockMessage:
    def __init__(self, user_id, text="/start"):
        self.from_user = User(id=user_id, is_bot=False, first_name="Test")
        self.chat = Chat(id=user_id, type="private")
        self.text = text
        self.message_id = 1
        
    async def answer(self, text, reply_markup=None, parse_mode=None):
        print(f"Bot Response: {text[:100]}...")
        return True

async def test_commands():
    """Test the new bot commands"""
    print("Testing bot commands...")
    
    # Test start command
    mock_message = MockMessage(123456, "/start")
    try:
        await start_command(mock_message, None)
        print("✅ /start command: Working")
    except Exception as e:
        print(f"❌ /start command error: {e}")
    
    # Test dashboard command
    try:
        await dashboard_command(mock_message)
        print("✅ /dashboard command: Working")
    except Exception as e:
        print(f"❌ /dashboard command error: {e}")
    
    # Test referral command
    try:
        await referral_command(mock_message)
        print("✅ /referral command: Working")
    except Exception as e:
        print(f"❌ /referral command error: {e}")

if __name__ == "__main__":
    asyncio.run(test_commands())