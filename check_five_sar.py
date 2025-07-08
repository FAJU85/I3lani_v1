#!/usr/bin/env python3
"""
Check if bot has access to @Five_SAR channel
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_five_sar():
    """Check @Five_SAR channel specifically"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    
    try:
        channel_username = "@Five_SAR"
        logger.info(f"Checking {channel_username} channel...")
        
        # Try to get channel info
        chat = await bot.get_chat(channel_username)
        logger.info(f"✅ Channel found: {chat.title}")
        logger.info(f"Channel ID: {chat.id}")
        logger.info(f"Type: {chat.type}")
        
        # Check if bot is admin
        bot_member = await bot.get_chat_member(chat.id, bot.id)
        logger.info(f"Bot status: {bot_member.status}")
        
        if bot_member.status == "administrator":
            logger.info("✅ Bot is administrator!")
            logger.info(f"Can post messages: {bot_member.can_post_messages}")
            logger.info(f"Can delete messages: {bot_member.can_delete_messages}")
            logger.info(f"Can manage chat: {bot_member.can_manage_chat}")
            
            # Get subscriber count
            count = await bot.get_chat_member_count(chat.id)
            logger.info(f"Subscriber count: {count}")
            
            # Check if in database
            channels = await db.get_channels(active_only=False)
            in_db = any(ch['telegram_channel_id'] == channel_username for ch in channels)
            
            if in_db:
                logger.info("✅ Channel is already in database")
            else:
                logger.info("❌ Channel is NOT in database yet")
                logger.info("\nTo add this channel:")
                logger.info("1. Use /admin command in the bot")
                logger.info("2. Click 'Manage Channels'")
                logger.info("3. Click 'Add Channel'")
                logger.info(f"4. Enter: {channel_username}")
                
        else:
            logger.info("❌ Bot is NOT an administrator in this channel")
            logger.info("\nTo use this channel:")
            logger.info("1. Go to the channel settings")
            logger.info("2. Add @I3lani_bot as administrator")
            logger.info("3. Enable 'Post Messages' permission")
            logger.info("4. Then add it through the bot's admin panel")
            
    except Exception as e:
        logger.error(f"Error accessing channel: {e}")
        logger.info("\nPossible reasons:")
        logger.info("- Channel might be private")
        logger.info("- Username might be incorrect")
        logger.info("- Bot might not have access")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(check_five_sar())