"""
Manual Channel Addition for @zaaaazoooo
Test script to manually add channel and verify detection
"""

import asyncio
import logging
from main_bot import bot
from database import db
from channel_manager import ChannelManager

logger = logging.getLogger(__name__)

async def manual_add_channel():
    """Manually add @zaaaazoooo channel if bot has access"""
    try:
        channel_username = 'zaaaazoooo'
        print(f"🔍 Checking access to @{channel_username}...")
        
        # Try to get chat info
        try:
            chat = await bot.get_chat(f'@{channel_username}')
            print(f"✅ Found channel: {chat.title}")
            print(f"Type: {chat.type}")
            print(f"ID: {chat.id}")
            print(f"Username: @{chat.username}")
            
            # Check bot's status in the channel
            try:
                bot_member = await bot.get_chat_member(chat.id, bot.id)
                print(f"Bot status: {bot_member.status}")
                
                if bot_member.status == 'administrator':
                    print(f"✅ Bot is admin with posting rights: {bot_member.can_post_messages}")
                    
                    # Check if already in database
                    channels = await db.get_channels(active_only=False)
                    exists = any(str(chat.id) == str(ch.get('telegram_channel_id', '')) for ch in channels)
                    
                    if not exists:
                        print("🔄 Adding channel to database...")
                        
                        # Get channel stats
                        try:
                            member_count = await bot.get_chat_member_count(chat.id)
                            print(f"Member count: {member_count}")
                        except:
                            member_count = 0
                        
                        # Add to database
                        await db.add_channel_automatically(
                            channel_id=str(chat.id),
                            channel_name=chat.title,
                            telegram_channel_id=f"@{chat.username}",
                            subscribers=member_count,
                            active_subscribers=int(member_count * 0.45),
                            total_posts=0,
                            category='general',
                            description=chat.description or '',
                            base_price_usd=2.0
                        )
                        
                        print("✅ Channel added to database successfully!")
                        
                        # Send welcome message
                        welcome_message = f"""
🎉 **I3lani Bot is now active in this channel!**

This channel is now available for advertisements through @I3lani_bot.

📊 **Channel Information:**
• **Name:** {chat.title}
• **Total Subscribers:** {member_count:,}
• **Category:** General
• **Base Ad Price:** $2.00

Users can now select this channel when creating ads through the bot.
                        """.strip()
                        
                        try:
                            await bot.send_message(chat.id, welcome_message, parse_mode='Markdown')
                            print("✅ Welcome message sent to channel")
                        except Exception as e:
                            print(f"⚠️ Could not send welcome message: {e}")
                            
                    else:
                        print("ℹ️ Channel already exists in database")
                        
                else:
                    print(f"❌ Bot is not admin (status: {bot_member.status})")
                    print("💡 The bot needs to be added as admin with 'Post Messages' permission")
                    
            except Exception as e:
                print(f"❌ Error checking bot status: {e}")
                print("💡 Bot may not be a member of this channel")
                
        except Exception as e:
            print(f"❌ Error accessing channel: {e}")
            print("💡 Possible reasons:")
            print("  • Channel doesn't exist")
            print("  • Channel is private and bot is not a member")
            print("  • Bot doesn't have access to channel info")
            
    except Exception as e:
        print(f"❌ General error: {e}")

async def check_why_not_detected():
    """Check why automatic detection might not be working"""
    print("🔍 Checking automatic detection system...")
    
    # Check if my_chat_member handler is registered
    from main_bot import dp
    
    handlers = dp.observers.get('my_chat_member', {})
    print(f"my_chat_member handlers registered: {len(handlers)}")
    
    # Check channel manager
    try:
        channel_manager = ChannelManager(bot, db)
        print("✅ Channel manager initialized")
        
        # Check if bot can access the channel
        await manual_add_channel()
        
    except Exception as e:
        print(f"❌ Channel manager error: {e}")

if __name__ == "__main__":
    asyncio.run(check_why_not_detected())