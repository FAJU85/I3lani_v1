#!/usr/bin/env python3
"""
Check all channels where bot is administrator
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_all_channels():
    """Find all channels where bot is admin"""
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"Bot: @{bot_info.username} (ID: {bot_info.id})")
        
        # Check common channel patterns
        test_channels = [
            "@i3lani", "@smshco", "@i3lani_main", "@i3lani_news",
            "@i3lani_ads", "@i3lani_channel", "@i3lani_market",
            "@i3lani_offers", "@i3lani_deals", "@i3lani_shop",
            "@i3lani_store", "@i3lani_business", "@i3lani_tech",
            "@i3lani_promo", "@i3lani_sale", "@i3lani_buy",
            "@i3lani_sell", "@i3lani_trade", "@i3lani_commerce"
        ]
        
        found_channels = []
        
        for channel in test_channels:
            try:
                chat = await bot.get_chat(channel)
                # Check if bot is admin
                bot_member = await bot.get_chat_member(chat.id, bot_info.id)
                
                if bot_member.status == "administrator":
                    subscribers = await bot.get_chat_member_count(chat.id)
                    logger.info(f"✅ FOUND: {chat.title} ({channel}) - {subscribers} subscribers")
                    logger.info(f"   Can post: {bot_member.can_post_messages}")
                    found_channels.append({
                        'username': channel,
                        'title': chat.title,
                        'id': chat.id,
                        'subscribers': subscribers,
                        'can_post': bot_member.can_post_messages
                    })
            except Exception as e:
                # Channel doesn't exist or bot not member
                pass
        
        logger.info(f"\n📊 Summary: Found {len(found_channels)} channels where bot is admin")
        
        # Also check if there are any channels in bot's updates
        logger.info("\n🔍 Checking recent updates for channel memberships...")
        updates = await bot.get_updates(limit=100)
        
        channel_updates = set()
        for update in updates:
            if update.my_chat_member and update.my_chat_member.chat.type in ['channel', 'supergroup']:
                chat = update.my_chat_member.chat
                channel_updates.add((chat.id, chat.title, chat.username))
        
        if channel_updates:
            logger.info(f"Found {len(channel_updates)} channels in recent updates:")
            for chat_id, title, username in channel_updates:
                logger.info(f"  - {title} (@{username or 'private'})")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(check_all_channels())