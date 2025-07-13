#!/usr/bin/env python3
"""
Referral System Handlers for I3lani Bot
Handles /refer, /balance, /withdraw commands and referral workflows
"""

import logging
from decimal import Decimal
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from automatic_language_system import get_user_language_auto
from languages import get_text
from referral_system import get_referral_system

logger = logging.getLogger(__name__)
router = Router()

class ReferralStates(StatesGroup):
    """States for referral system"""
    waiting_for_wallet_address = State()
    waiting_for_withdrawal_amount = State()
    confirming_withdrawal = State()

@router.message(Command("refer"))
async def refer_command(message: Message, state: FSMContext):
    """Handle /refer command - show referral information"""
    user_id = message.from_user.id
    
    try:
        # Get user language
        language = await get_user_language_auto(user_id)
        
        # Get referral system
        referral_sys = await get_referral_system()
        
        # Get user referral data
        referral_data = await referral_sys.get_user_referral_data(user_id)
        
        if not referral_data:
            await message.reply("❌ Error accessing referral system. Please try again.")
            return
        
        # Get bot username from message
        bot_username = message.bot.username
        referral_link = await referral_sys.get_referral_link(user_id, bot_username)
        
        # Create referral message
        text = f"""💸 <b>Earn Passive Income with Referrals!</b>

👥 <b>Your referral link:</b>
<code>{referral_link}</code>

🎁 <b>What your friends get:</b>
• 0.00010000 TON signup bonus
• Access to premium advertising platform

🏆 <b>What you earn:</b>
• 20% of everything they earn — forever!
• Passive income with no limits

📊 <b>Your Statistics:</b>
• Total referrals: {referral_data.get('referral_count', 0)}
• Total earnings: {referral_data.get('total_earnings', 0)} TON
• Available balance: {referral_data.get('available_balance', 0)} TON

💡 <b>How it works:</b>
1. Share your link with friends
2. They join and get bonus TON
3. You earn 20% of their spending
4. Withdraw anytime to your TON wallet

📌 <b>Commands:</b>
• /balance - Check earnings & stats
• /withdraw - Get paid in TON
• /refer - Show this message"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 Check Balance", callback_data="referral_balance"),
                InlineKeyboardButton(text="💳 Withdraw", callback_data="referral_withdraw")
            ],
            [
                InlineKeyboardButton(text="📊 Statistics", callback_data="referral_stats"),
                InlineKeyboardButton(text="🔗 Share Link", callback_data="referral_share")
            ]
        ])
        
        await message.reply(text, reply_markup=keyboard, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error in refer command: {e}")
        await message.reply("❌ Error processing referral command. Please try again.")

@router.message(Command("balance"))
async def balance_command(message: Message, state: FSMContext):
    """Handle /balance command - show balance and referral stats"""
    user_id = message.from_user.id
    
    try:
        # Get user language
        language = await get_user_language_auto(user_id)
        
        # Get referral system
        referral_sys = await get_referral_system()
        
        # Get user referral data
        referral_data = await referral_sys.get_user_referral_data(user_id)
        
        if not referral_data:
            await message.reply("❌ Error accessing referral system. Please try again.")
            return
        
        # Format recent earnings
        recent_earnings_text = ""
        if referral_data.get('recent_earnings'):
            recent_earnings_text = "\n\n📈 <b>Recent Earnings:</b>\n"
            for earning in referral_data['recent_earnings'][:5]:
                earning_type = earning[0].replace('_', ' ').title()
                amount = earning[1]
                date = earning[2][:10]  # Just date part
                recent_earnings_text += f"• {earning_type}: {amount} TON ({date})\n"
        
        # Format referred users
        referred_users_text = ""
        if referral_data.get('referred_users'):
            referred_users_text = f"\n\n👥 <b>Your Referrals ({len(referral_data['referred_users'])}):</b>\n"
            for user in referral_data['referred_users'][:5]:
                user_earnings = user[1]
                join_date = user[2][:10]
                referred_users_text += f"• User {user[0]}: {user_earnings} TON (joined {join_date})\n"
        
        text = f"""💰 <b>Your Referral Balance</b>

💎 <b>Available Balance:</b> {referral_data.get('available_balance', 0)} TON
📊 <b>Total Earnings:</b> {referral_data.get('total_earnings', 0)} TON
💸 <b>Total Withdrawn:</b> {referral_data.get('total_withdrawn', 0)} TON

👥 <b>Referral Stats:</b>
• Total referrals: {referral_data.get('referral_count', 0)}
• Signup bonus claimed: {'✅' if referral_data.get('signup_bonus_claimed') else '❌'}
• Referral code: <code>{referral_data.get('referral_code', 'N/A')}</code>

{recent_earnings_text}{referred_users_text}

💡 <b>Minimum withdrawal:</b> 0.001 TON
🔗 <b>Invite more friends to earn more!</b>"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Withdraw", callback_data="referral_withdraw"),
                InlineKeyboardButton(text="🔗 Get Referral Link", callback_data="referral_link")
            ],
            [
                InlineKeyboardButton(text="📊 Full Statistics", callback_data="referral_stats"),
                InlineKeyboardButton(text="🔄 Refresh", callback_data="referral_balance")
            ]
        ])
        
        await message.reply(text, reply_markup=keyboard, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Error in balance command: {e}")
        await message.reply("❌ Error processing balance command. Please try again.")

@router.message(Command("withdraw"))
async def withdraw_command(message: Message, state: FSMContext):
    """Handle /withdraw command - start withdrawal process"""
    user_id = message.from_user.id
    
    try:
        # Get referral system
        referral_sys = await get_referral_system()
        
        # Get user referral data
        referral_data = await referral_sys.get_user_referral_data(user_id)
        
        if not referral_data:
            await message.reply("❌ Error accessing referral system. Please try again.")
            return
        
        available_balance = referral_data.get('available_balance', 0)
        wallet_address = referral_data.get('ton_wallet_address')
        
        if available_balance < Decimal('0.001'):
            await message.reply(f"❌ Insufficient balance for withdrawal.\n\n💰 Available: {available_balance} TON\n💡 Minimum: 0.001 TON")
            return
        
        if not wallet_address:
            text = """🏦 <b>Set Your TON Wallet Address</b>

To withdraw your earnings, please provide your TON wallet address.

📱 <b>How to get your TON wallet address:</b>
1. Open your TON wallet app (Tonkeeper, etc.)
2. Go to "Receive" or "Wallet Address"
3. Copy your wallet address
4. Send it here

💡 <b>Your address should start with:</b> UQ, EQ, or 0:

⚠️ <b>Important:</b> Make sure the address is correct. Wrong addresses may result in lost funds."""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Cancel", callback_data="referral_balance")]
            ])
            
            await message.reply(text, reply_markup=keyboard, parse_mode='HTML')
            await state.set_state(ReferralStates.waiting_for_wallet_address)
            return
        
        # Show withdrawal form
        text = f"""💳 <b>Withdraw TON</b>

💰 <b>Available Balance:</b> {available_balance} TON
🏦 <b>Your Wallet:</b> <code>{wallet_address}</code>

💡 <b>Enter withdrawal amount:</b>
• Minimum: 0.001 TON
• Maximum: {available_balance} TON

📝 Type the amount you want to withdraw (e.g., 0.005)"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💸 Withdraw All", callback_data=f"withdraw_all_{available_balance}"),
                InlineKeyboardButton(text="🔧 Change Wallet", callback_data="change_wallet")
            ],
            [
                InlineKeyboardButton(text="❌ Cancel", callback_data="referral_balance")
            ]
        ])
        
        await message.reply(text, reply_markup=keyboard, parse_mode='HTML')
        await state.set_state(ReferralStates.waiting_for_withdrawal_amount)
        
    except Exception as e:
        logger.error(f"Error in withdraw command: {e}")
        await message.reply("❌ Error processing withdrawal command. Please try again.")

@router.callback_query(F.data == "referral_balance")
async def referral_balance_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle referral balance callback"""
    # Trigger balance command
    await balance_command(callback_query.message, state)
    await callback_query.answer()

@router.callback_query(F.data == "referral_withdraw")
async def referral_withdraw_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle referral withdraw callback"""
    # Trigger withdraw command
    await withdraw_command(callback_query.message, state)
    await callback_query.answer()

@router.callback_query(F.data == "referral_link")
async def referral_link_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle referral link callback"""
    # Trigger refer command
    await refer_command(callback_query.message, state)
    await callback_query.answer()

@router.callback_query(F.data == "referral_stats")
async def referral_stats_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle referral stats callback"""
    user_id = callback_query.from_user.id
    
    try:
        # Get referral system
        referral_sys = await get_referral_system()
        
        # Get user referral data
        referral_data = await referral_sys.get_user_referral_data(user_id)
        
        if not referral_data:
            await callback_query.answer("❌ Error accessing referral system")
            return
        
        # Get system analytics
        analytics = await referral_sys.get_system_analytics()
        
        # Get top referrers
        top_referrers = await referral_sys.get_top_referrers(5)
        
        # Format top referrers
        top_referrers_text = "\n\n🏆 <b>Top Referrers:</b>\n"
        for i, referrer in enumerate(top_referrers, 1):
            if referrer['user_id'] == user_id:
                top_referrers_text += f"<b>{i}. You: {referrer['total_earnings']} TON ({referrer['referral_count']} refs)</b>\n"
            else:
                top_referrers_text += f"{i}. User {referrer['user_id']}: {referrer['total_earnings']} TON ({referrer['referral_count']} refs)\n"
        
        text = f"""📊 <b>Referral System Statistics</b>

👤 <b>Your Performance:</b>
• Total referrals: {referral_data.get('referral_count', 0)}
• Total earnings: {referral_data.get('total_earnings', 0)} TON
• Available balance: {referral_data.get('available_balance', 0)} TON
• Commission rate: 20%

🌍 <b>System Overview:</b>
• Total users: {analytics.get('total_users', 0)}
• Active referrers: {analytics.get('active_referrers', 0)}
• Total earnings distributed: {analytics.get('total_earnings_distributed', 0)} TON
• Pending withdrawals: {analytics.get('pending_withdrawals', 0)}

{top_referrers_text}

💡 <b>Tips to earn more:</b>
• Share your link on social media
• Invite friends interested in advertising
• Help your referrals get started
• More active referrals = more earnings!"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔗 Share Link", callback_data="referral_share"),
                InlineKeyboardButton(text="💰 Balance", callback_data="referral_balance")
            ],
            [
                InlineKeyboardButton(text="🔄 Refresh", callback_data="referral_stats")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in referral stats callback: {e}")
        await callback_query.answer("❌ Error loading statistics")

@router.callback_query(F.data == "referral_share")
async def referral_share_callback(callback_query: CallbackQuery, state: FSMContext):
    """Handle referral share callback"""
    user_id = callback_query.from_user.id
    
    try:
        # Get referral system
        referral_sys = await get_referral_system()
        
        # Get bot username
        bot_username = callback_query.message.bot.username
        referral_link = await referral_sys.get_referral_link(user_id, bot_username)
        
        share_text = f"""🚀 Join I3lani Bot and earn TON!

💰 Get 0.00010000 TON signup bonus
📢 Advertise in premium Telegram channels
🏆 Earn with every campaign

Join here: {referral_link}"""
        
        text = f"""🔗 <b>Share Your Referral Link</b>

📱 <b>Your referral link:</b>
<code>{referral_link}</code>

📝 <b>Ready-to-share message:</b>
<code>{share_text}</code>

💡 <b>Share on:</b>
• Social media platforms
• Telegram groups/channels
• WhatsApp, Discord, etc.
• Friend conversations

🎯 <b>Best practices:</b>
• Explain the benefits personally
• Share in relevant communities
• Follow up with new users
• Be helpful and supportive"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Copy Link", callback_data="copy_referral_link"),
                InlineKeyboardButton(text="📊 Stats", callback_data="referral_stats")
            ],
            [
                InlineKeyboardButton(text="↩️ Back", callback_data="referral_balance")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in referral share callback: {e}")
        await callback_query.answer("❌ Error generating share content")

@router.message(ReferralStates.waiting_for_wallet_address)
async def process_wallet_address(message: Message, state: FSMContext):
    """Process wallet address input"""
    user_id = message.from_user.id
    wallet_address = message.text.strip()
    
    try:
        # Basic validation
        if not wallet_address or len(wallet_address) < 40:
            await message.reply("❌ Invalid wallet address. Please provide a valid TON wallet address.")
            return
        
        # Check if address starts with expected prefixes
        if not (wallet_address.startswith('UQ') or wallet_address.startswith('EQ') or wallet_address.startswith('0:')):
            await message.reply("❌ Invalid wallet address format. TON addresses should start with UQ, EQ, or 0:")
            return
        
        # Get referral system
        referral_sys = await get_referral_system()
        
        # Set wallet address
        success = await referral_sys.set_wallet_address(user_id, wallet_address)
        
        if success:
            await message.reply(f"✅ Wallet address saved successfully!\n\n🏦 Address: <code>{wallet_address}</code>\n\n💳 You can now withdraw your earnings using /withdraw", parse_mode='HTML')
            await state.clear()
        else:
            await message.reply("❌ Error saving wallet address. Please try again.")
        
    except Exception as e:
        logger.error(f"Error processing wallet address: {e}")
        await message.reply("❌ Error processing wallet address. Please try again.")

@router.message(ReferralStates.waiting_for_withdrawal_amount)
async def process_withdrawal_amount(message: Message, state: FSMContext):
    """Process withdrawal amount input"""
    user_id = message.from_user.id
    
    try:
        # Parse amount
        amount_str = message.text.strip()
        amount = Decimal(amount_str)
        
        if amount <= 0:
            await message.reply("❌ Amount must be greater than 0")
            return
        
        # Get referral system
        referral_sys = await get_referral_system()
        
        # Process withdrawal
        success, message_text = await referral_sys.process_withdrawal(user_id, amount)
        
        if success:
            await message.reply(f"✅ {message_text}\n\n💰 Amount: {amount} TON\n⏳ Processing time: 1-24 hours\n\n📧 You'll receive a confirmation once processed.")
            await state.clear()
        else:
            await message.reply(f"❌ {message_text}")
        
    except ValueError:
        await message.reply("❌ Invalid amount format. Please enter a valid number (e.g., 0.005)")
    except Exception as e:
        logger.error(f"Error processing withdrawal amount: {e}")
        await message.reply("❌ Error processing withdrawal. Please try again.")

def setup_referral_handlers(dp):
    """Setup referral system handlers"""
    dp.include_router(router)
    logger.info("✅ Referral system handlers registered")