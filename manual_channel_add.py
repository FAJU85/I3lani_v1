#!/usr/bin/env python3
"""
Manually add channels where bot is already admin
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def manual_add_channels():
    """Manually add specific channels"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    
    # Ask for channel usernames
    logger.info("Enter channel usernames where the bot is already an administrator.")
    logger.info("Make sure the bot has 'Post Messages' permission in these channels.")
    logger.info("Enter usernames one per line (e.g., @channelname). Type 'done' when finished:")
    
    channels_to_add = []
    while True:
        username = input("> ").strip()
        if username.lower() == 'done':
            break
        if username:
            if not username.startswith('@'):
                username = f'@{username}'
            channels_to_add.append(username)
    
    if not channels_to_add:
        logger.info("No channels provided.")
        await bot.session.close()
        return
    
    logger.info(f"\nAttempting to add {len(channels_to_add)} channels...")
    
    success_count = 0
    for username in channels_to_add:
        try:
            # Check if bot is admin
            chat = await bot.get_chat(username)
            member = await bot.get_chat_member(chat.id, bot.id)
            
            if member.status == 'administrator':
                if not member.can_post_messages:
                    logger.warning(f"❌ {username}: Bot is admin but cannot post messages")
                    continue
                
                # Get subscriber count
                count = await bot.get_chat_member_count(chat.id)
                
                # Add to database
                success = await db.add_channel(
                    channel_id=username.replace('@', ''),
                    channel_name=chat.title,
                    telegram_channel_id=username,
                    subscribers=count,
                    base_price_usd=5.0  # Default price
                )
                
                if success:
                    logger.info(f"✅ Added: {chat.title} ({username}) - {count} subscribers")
                    success_count += 1
                else:
                    logger.info(f"⚠️  {username}: Already in database")
            else:
                logger.error(f"❌ {username}: Bot is not an administrator")
                
        except Exception as e:
            logger.error(f"❌ {username}: Error - {str(e)}")
    
    logger.info(f"\n✅ Successfully added {success_count} channels")
    
    # Show all channels
    logger.info("\n=== All Active Channels ===")
    channels = await db.get_channels(active_only=True)
    for ch in channels:
        logger.info(f"• {ch['name']} (@{ch['telegram_channel_id']}) - {ch['subscribers']} subscribers")
    
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(manual_add_channels())