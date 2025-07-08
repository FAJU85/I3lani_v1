#!/usr/bin/env python3
"""
Check bot updates for all channel memberships
"""
import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_updates():
    """Check all bot updates for channel memberships"""
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # Get all types of updates
        logger.info("Checking bot updates for channel memberships...")
        
        # First, clear any existing updates to get fresh data
        await bot.delete_webhook()
        
        # Get updates with different offsets to find older updates
        all_updates = []
        offset = None
        
        for i in range(5):  # Try to get multiple batches
            updates = await bot.get_updates(offset=offset, limit=100, timeout=1)
            if updates:
                all_updates.extend(updates)
                offset = updates[-1].update_id + 1
                logger.info(f"Batch {i+1}: Got {len(updates)} updates")
            else:
                break
            await asyncio.sleep(0.5)
        
        logger.info(f"Total updates retrieved: {len(all_updates)}")
        
        # Analyze channel memberships
        channel_events = []
        
        for update in all_updates:
            if update.my_chat_member and update.my_chat_member.chat.type in ['channel', 'supergroup']:
                event = {
                    'chat_id': update.my_chat_member.chat.id,
                    'title': update.my_chat_member.chat.title,
                    'username': update.my_chat_member.chat.username,
                    'old_status': update.my_chat_member.old_chat_member.status,
                    'new_status': update.my_chat_member.new_chat_member.status,
                    'date': datetime.fromtimestamp(update.my_chat_member.date).strftime('%Y-%m-%d %H:%M:%S')
                }
                channel_events.append(event)
        
        # Display all channel events
        logger.info(f"\n=== Found {len(channel_events)} channel membership events ===")
        
        current_admins = []
        for event in channel_events:
            logger.info(f"\nChannel: {event['title']} (@{event['username']})")
            logger.info(f"  Status change: {event['old_status']} → {event['new_status']}")
            logger.info(f"  Date: {event['date']}")
            
            # Check current status
            if event['new_status'] == 'administrator':
                try:
                    member = await bot.get_chat_member(event['chat_id'], bot.id)
                    if member.status == 'administrator':
                        count = await bot.get_chat_member_count(event['chat_id'])
                        current_admins.append({
                            'title': event['title'],
                            'username': event['username'],
                            'subscribers': count,
                            'can_post': member.can_post_messages
                        })
                        logger.info(f"  ✅ Currently admin with {count} subscribers")
                except Exception as e:
                    logger.info(f"  ❌ Error checking current status: {e}")
        
        # Summary
        logger.info(f"\n=== SUMMARY ===")
        logger.info(f"Total channel events: {len(channel_events)}")
        logger.info(f"Currently admin in {len(current_admins)} channels:")
        
        for ch in current_admins:
            logger.info(f"  - {ch['title']} (@{ch['username']}) - {ch['subscribers']} subscribers")
        
        if len(current_admins) > 2:
            logger.info("\n✅ Found more than 2 channels! Use /admin command to sync them.")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(check_updates())