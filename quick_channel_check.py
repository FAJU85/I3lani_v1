#!/usr/bin/env python3
"""
Quick channel check for specific patterns
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def quick_check():
    """Quick check for channels"""
    bot = Bot(token=BOT_TOKEN)
    
    # Specific channels to check based on common patterns
    channels_to_check = [
        # Already known
        "@i3lani", "@smshco",
        # Variations of i3lani
        "@i3lani_official", "@i3lani_main", "@i3lani_channel",
        "@i3lani_ads", "@i3lani_news", "@i3lani_ksa",
        "@i3lani_saudi", "@i3lani_sa", "@i3lani_arab",
        "@i3lani_market", "@i3lani_shop", "@i3lani_store",
        # Alternative spellings
        "@3lani", "@e3lani", "@i3lan", "@e3lan",
        # Shop variations
        "@shop_smart", "@smart_shop", "@smshco_official",
        # Arabic transliterations
        "@i3lany", "@e3lany", "@a3lani"
    ]
    
    logger.info(f"Checking {len(channels_to_check)} potential channels...")
    found_channels = []
    
    for channel in channels_to_check:
        try:
            chat = await bot.get_chat(channel)
            bot_member = await bot.get_chat_member(chat.id, bot.id)
            
            if bot_member.status == "administrator":
                subscribers = await bot.get_chat_member_count(chat.id)
                found_channels.append({
                    'username': channel,
                    'title': chat.title,
                    'subscribers': subscribers,
                    'can_post': bot_member.can_post_messages
                })
                logger.info(f"✅ FOUND: {chat.title} ({channel}) - {subscribers} subscribers, Can post: {bot_member.can_post_messages}")
        except Exception as e:
            # Channel doesn't exist or bot not admin
            pass
        
        await asyncio.sleep(0.1)  # Small delay to avoid rate limits
    
    logger.info(f"\n📊 RESULTS: Found {len(found_channels)} channels where bot is admin:")
    for ch in found_channels:
        logger.info(f"  - {ch['title']} ({ch['username']}) - {ch['subscribers']} subscribers")
    
    await bot.close()

if __name__ == "__main__":
    asyncio.run(quick_check())