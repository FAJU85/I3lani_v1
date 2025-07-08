#!/usr/bin/env python3
"""
List all channels where bot is currently admin
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def list_channels():
    """List all channels from database and verify bot status"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    
    try:
        logger.info("=== CHECKING ALL CHANNELS ===\n")
        
        # Get all channels from database
        channels = await db.get_channels(active_only=False)
        
        if not channels:
            logger.info("No channels found in database.")
            logger.info("\nTo add channels:")
            logger.info("1. Add @I3lani_bot as administrator to your channel")
            logger.info("2. Grant 'Post Messages' permission")
            logger.info("3. Use /admin command and click 'Add Channel'")
            await bot.session.close()
            return
        
        active_channels = []
        inactive_channels = []
        
        for ch in channels:
            try:
                # Verify bot status in channel
                chat = await bot.get_chat(ch['telegram_channel_id'])
                member = await bot.get_chat_member(chat.id, bot.id)
                
                if member.status == 'administrator':
                    # Get fresh subscriber count
                    count = await bot.get_chat_member_count(chat.id)
                    active_channels.append({
                        'name': chat.title,
                        'username': ch['telegram_channel_id'],
                        'subscribers': count,
                        'can_post': member.can_post_messages,
                        'db_status': ch['is_active']
                    })
                else:
                    inactive_channels.append({
                        'name': ch['name'],
                        'username': ch['telegram_channel_id'],
                        'reason': 'Bot is not admin'
                    })
                    
            except Exception as e:
                inactive_channels.append({
                    'name': ch['name'],
                    'username': ch['telegram_channel_id'],
                    'reason': f'Error: {str(e)}'
                })
        
        # Display results
        logger.info(f"✅ ACTIVE CHANNELS ({len(active_channels)}):")
        for ch in active_channels:
            logger.info(f"\n• {ch['name']} (@{ch['username']})")
            logger.info(f"  - Subscribers: {ch['subscribers']}")
            logger.info(f"  - Can post: {ch['can_post']}")
            logger.info(f"  - DB status: {'Active' if ch['db_status'] else 'Inactive'}")
        
        if inactive_channels:
            logger.info(f"\n\n❌ INACTIVE CHANNELS ({len(inactive_channels)}):")
            for ch in inactive_channels:
                logger.info(f"\n• {ch['name']} (@{ch['username']})")
                logger.info(f"  - Reason: {ch['reason']}")
        
        logger.info(f"\n\n📊 SUMMARY:")
        logger.info(f"Total channels in database: {len(channels)}")
        logger.info(f"Active (bot is admin): {len(active_channels)}")
        logger.info(f"Inactive: {len(inactive_channels)}")
        
        if len(active_channels) < 3:
            logger.info("\n💡 TO ADD MORE CHANNELS:")
            logger.info("1. Add @I3lani_bot as administrator to your channels")
            logger.info("2. Make sure bot has 'Post Messages' permission")
            logger.info("3. Use /admin command → 'Manage Channels' → 'Add Channel'")
            logger.info("4. Or use 'Discover Existing Channels' to find channels where bot is already admin")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(list_channels())