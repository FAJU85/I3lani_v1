#!/usr/bin/env python3
"""
Manually add channels where bot is administrator
This will help discover channels that auto-discovery might miss
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of channels to check - add your channel usernames here
CHANNELS_TO_CHECK = [
    "@i3lani",        # Already known
    "@smshco",        # Already known  
    "@Five_SAR",      # Recently added
    
    # Add more channel usernames below where your bot is admin:
    # "@your_channel_1",
    # "@your_channel_2",
    # etc.
]

async def manually_add_channels():
    """Check and add channels from the list"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    
    try:
        logger.info("=" * 60)
        logger.info("MANUAL CHANNEL ADDITION")
        logger.info("=" * 60)
        
        added = 0
        already_exists = 0
        not_admin = 0
        errors = 0
        
        for channel_username in CHANNELS_TO_CHECK:
            try:
                logger.info(f"\nChecking {channel_username}...")
                
                # Get channel info
                chat = await bot.get_chat(channel_username)
                
                # Check if bot is admin
                bot_member = await bot.get_chat_member(chat.id, bot.id)
                
                if bot_member.status != 'administrator':
                    logger.warning(f"❌ Bot is NOT admin in {channel_username}")
                    not_admin += 1
                    continue
                
                if not bot_member.can_post_messages:
                    logger.warning(f"❌ Bot cannot post in {channel_username}")
                    not_admin += 1
                    continue
                
                # Get member count
                member_count = await bot.get_chat_member_count(chat.id)
                
                # Check if already in database
                channels = await db.get_channels(active_only=False)
                exists = any(ch['telegram_channel_id'] == channel_username for ch in channels)
                
                if exists:
                    logger.info(f"✓ {chat.title} already in database")
                    already_exists += 1
                else:
                    # Add to database
                    success = await db.add_channel(
                        channel_id=channel_username.replace("@", ""),
                        channel_name=chat.title,
                        telegram_channel_id=channel_username,
                        subscribers=member_count,
                        price_per_post=1.0  # Base price
                    )
                    
                    if success:
                        logger.info(f"✅ Added {chat.title} - {member_count} subscribers")
                        added += 1
                    else:
                        logger.error(f"Failed to add {channel_username}")
                        errors += 1
                        
            except Exception as e:
                logger.error(f"Error with {channel_username}: {e}")
                errors += 1
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Newly added: {added}")
        logger.info(f"📋 Already exists: {already_exists}")
        logger.info(f"❌ Not admin: {not_admin}")
        logger.info(f"⚠️ Errors: {errors}")
        
        # Show all channels
        logger.info("\n" + "=" * 60)
        logger.info("ALL CHANNELS IN DATABASE")
        logger.info("=" * 60)
        
        all_channels = await db.get_channels(active_only=False)
        for i, ch in enumerate(all_channels, 1):
            status = "✅ Active" if ch.get('is_active', False) else "❌ Inactive"
            logger.info(f"{i}. {ch['name']} (@{ch['telegram_channel_id']}) - {ch['subscribers']} subscribers - {status}")
        
        logger.info(f"\nTotal channels: {len(all_channels)}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logger.info("\nTo add more channels:")
    logger.info("1. Edit this file and add channel usernames to CHANNELS_TO_CHECK list")
    logger.info("2. Make sure the bot is admin in those channels")
    logger.info("3. Run this script again\n")
    
    asyncio.run(manually_add_channels())