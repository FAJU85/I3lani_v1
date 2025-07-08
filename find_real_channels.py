#!/usr/bin/env python3
"""
Find real channels where bot is already administrator
"""
import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def find_real_channels():
    """Find real channels through bot updates and database"""
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    
    try:
        # First, check what's in the database
        logger.info("=== Checking channels in database ===")
        channels = await db.get_channels(active_only=False)
        
        for ch in channels:
            logger.info(f"DB Channel: {ch['channel_name']} (@{ch['telegram_channel_id']}) - Active: {ch['is_active']}")
            
            # Verify if bot is still admin
            try:
                chat = await bot.get_chat(ch['telegram_channel_id'])
                member = await bot.get_chat_member(chat.id, bot.id)
                
                if member.status == "administrator":
                    count = await bot.get_chat_member_count(chat.id)
                    logger.info(f"  ✅ Confirmed: Bot is admin, {count} subscribers, Can post: {member.can_post_messages}")
                else:
                    logger.info(f"  ❌ Bot is NOT admin anymore")
            except Exception as e:
                logger.info(f"  ❌ Cannot access channel: {e}")
        
        # Check bot updates for my_chat_member events
        logger.info("\n=== Checking bot updates for channel memberships ===")
        updates = await bot.get_updates(limit=100, allowed_updates=["my_chat_member"])
        
        channel_memberships = {}
        
        for update in updates:
            if update.my_chat_member and update.my_chat_member.chat.type in ['channel', 'supergroup']:
                chat = update.my_chat_member.chat
                new_status = update.my_chat_member.new_chat_member.status
                
                channel_memberships[chat.id] = {
                    'title': chat.title,
                    'username': chat.username,
                    'status': new_status,
                    'update_date': update.my_chat_member.date
                }
        
        # Display found memberships
        admin_channels = []
        for chat_id, info in channel_memberships.items():
            if info['status'] == 'administrator':
                logger.info(f"Found admin membership: {info['title']} (@{info['username']}) - Status: {info['status']}")
                
                # Verify current status
                try:
                    member = await bot.get_chat_member(chat_id, bot.id)
                    if member.status == 'administrator':
                        count = await bot.get_chat_member_count(chat_id)
                        admin_channels.append({
                            'id': chat_id,
                            'title': info['title'],
                            'username': info['username'],
                            'subscribers': count,
                            'can_post': member.can_post_messages
                        })
                        logger.info(f"  ✅ Still admin, {count} subscribers")
                except:
                    pass
        
        # Summary
        logger.info(f"\n=== SUMMARY ===")
        logger.info(f"Total channels in database: {len(channels)}")
        logger.info(f"Channels where bot is confirmed admin: {len(admin_channels)}")
        
        if admin_channels:
            logger.info("\nConfirmed admin channels:")
            for ch in admin_channels:
                logger.info(f"  - {ch['title']} (@{ch['username']}) - {ch['subscribers']} subscribers")
        
        # Ask about manual channel check
        logger.info("\n💡 To add more channels:")
        logger.info("1. Make sure the bot is added as administrator to the channel")
        logger.info("2. The bot needs 'Post Messages' permission")
        logger.info("3. Use /admin command and click 'Add Channel' to add it manually")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(find_real_channels())