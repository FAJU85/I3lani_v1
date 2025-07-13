"""
Check @zaaaazoooo channel access and detection status
"""

import asyncio
import logging
from database import db

logger = logging.getLogger(__name__)

async def check_channel_access():
    """Check if bot can access @zaaaazoooo channel"""
    try:
        # Import bot from deployment server context
        import sys
        sys.path.append('/home/runner/workspace')
        
        # Get bot instance from main_bot module
        from main_bot import bot
        
        if not bot:
            print("❌ Bot instance not available")
            return
            
        channel_username = 'zaaaazoooo'
        print(f"🔍 Checking access to @{channel_username}...")
        
        # Try to get chat info
        try:
            chat = await bot.get_chat(f'@{channel_username}')
            print(f"✅ Found channel: {chat.title}")
            print(f"Type: {chat.type}")
            print(f"ID: {chat.id}")
            if chat.username:
                print(f"Username: @{chat.username}")
            
            # Check bot's status in the channel
            try:
                bot_member = await bot.get_chat_member(chat.id, bot.id)
                print(f"Bot status: {bot_member.status}")
                
                if bot_member.status == 'administrator':
                    print(f"✅ Bot is admin")
                    print(f"Can post messages: {getattr(bot_member, 'can_post_messages', 'Unknown')}")
                    
                    # Check if channel is in database
                    channels = await db.get_channels(active_only=False)
                    channel_exists = False
                    
                    for ch in channels:
                        if (str(chat.id) == str(ch.get('telegram_channel_id', '')) or 
                            f"@{channel_username}" == str(ch.get('telegram_channel_id', ''))):
                            channel_exists = True
                            print(f"✅ Channel found in database: {ch.get('name', 'Unknown')}")
                            break
                    
                    if not channel_exists:
                        print("❌ Channel NOT found in database")
                        print("🔄 This means automatic detection didn't work")
                        print("💡 Possible reasons:")
                        print("  • Bot was added before the detection system was implemented")
                        print("  • my_chat_member handler wasn't triggered")
                        print("  • Error occurred during automatic addition")
                        
                        # Get member count
                        try:
                            member_count = await bot.get_chat_member_count(chat.id)
                            print(f"📊 Member count: {member_count}")
                        except:
                            member_count = 0
                            print("📊 Member count: Unknown")
                            
                        print(f"\n🔧 Manual addition required for @{channel_username}")
                        
                elif bot_member.status == 'left':
                    print("❌ Bot is not a member of this channel")
                    print("💡 Bot needs to be added to the channel first")
                    
                elif bot_member.status == 'member':
                    print("⚠️ Bot is a member but not admin")
                    print("💡 Bot needs admin privileges with 'Post Messages' permission")
                    
                else:
                    print(f"❌ Bot status: {bot_member.status}")
                    print("💡 Bot needs to be admin with posting rights")
                    
            except Exception as e:
                print(f"❌ Error checking bot status: {e}")
                if "chat not found" in str(e).lower():
                    print("💡 Bot is not a member of this channel")
                elif "user not found" in str(e).lower():
                    print("💡 Bot user not found in this channel")
                else:
                    print("💡 Bot may not have access to this channel")
                
        except Exception as e:
            print(f"❌ Error accessing channel: {e}")
            if "chat not found" in str(e).lower():
                print("💡 Possible reasons:")
                print("  • Channel doesn't exist")
                print("  • Channel username is incorrect")
                print("  • Channel is private and bot is not a member")
            else:
                print("💡 Bot doesn't have access to channel info")
                
    except Exception as e:
        print(f"❌ General error: {e}")

async def manual_add_channel():
    """Manually add the channel to database if bot has access"""
    try:
        from main_bot import bot
        
        if not bot:
            print("❌ Bot instance not available")
            return
            
        channel_username = 'zaaaazoooo'
        
        # Get chat info
        chat = await bot.get_chat(f'@{channel_username}')
        bot_member = await bot.get_chat_member(chat.id, bot.id)
        
        if bot_member.status == 'administrator' and getattr(bot_member, 'can_post_messages', False):
            print("🔄 Attempting to add channel to database...")
            
            # Get member count
            try:
                member_count = await bot.get_chat_member_count(chat.id)
            except:
                member_count = 0
            
            # Add to database
            await db.add_channel_automatically(
                channel_id=str(chat.id),
                channel_name=chat.title,
                telegram_channel_id=f"@{chat.username}" if chat.username else str(chat.id),
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
            print("❌ Cannot add channel - bot is not admin with posting rights")
            
    except Exception as e:
        print(f"❌ Error adding channel manually: {e}")

if __name__ == "__main__":
    print("🔍 Checking @zaaaazoooo channel status...")
    asyncio.run(check_channel_access())
    
    print("\n" + "="*50)
    print("🔧 Attempting manual addition...")
    try:
        asyncio.run(manual_add_channel())
    except Exception as e:
        print(f"❌ Manual addition failed: {e}")