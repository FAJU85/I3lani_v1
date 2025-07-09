"""
Viral Referral Game Handlers for I3lani Bot
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from viral_referral_game import get_viral_game
from database import db, get_user_language

logger = logging.getLogger(__name__)

# Create router for viral referral handlers
viral_router = Router()

@viral_router.message(CommandStart(deep_link=True))
async def handle_referral_start(message: Message, state: FSMContext):
    """Handle /start with referral code"""
    try:
        user_id = message.from_user.id
        language = await get_user_language(user_id)
        
        # Extract referral code from deep link
        args = message.text.split()[1] if len(message.text.split()) > 1 else None
        
        if args and args.startswith('ref_'):
            # Extract inviter ID from referral code
            try:
                inviter_id = int(args.replace('ref_', ''))
                
                # Get viral game instance
                viral_game = get_viral_game()
                
                # Create user in referral system
                await viral_game.get_or_create_user(user_id)
                
                # Process the referral
                result = await viral_game.process_referral(inviter_id, user_id)
                
                if result['success']:
                    # Send success message to new user
                    if language == 'ar':
                        welcome_msg = f"""🎮 **مرحباً بك في لعبة الإحالة الفيروسية!**

🎯 **تم تسجيلك بنجاح عبر دعوة صديقك!**
🎉 **ساعدت صديقك في الحصول على نقطة إحالة**

💫 **ابدأ رحلتك الآن:**
• أكمل شريط التقدم للوصول إلى 99%
• ادعو 3 أصدقاء لتحصل على شهر مجاني من الإعلانات
• استمتع بالإعلانات المجانية لمدة 30 يوماً

🚀 **اضغط الزر أدناه للبدء!**"""
                    elif language == 'ru':
                        welcome_msg = f"""🎮 **Добро пожаловать в вирусную реферальную игру!**

🎯 **Вы успешно зарегистрировались по приглашению друга!**
🎉 **Вы помогли своему другу получить реферальный балл**

💫 **Начните свое путешествие сейчас:**
• Завершите прогресс-бар, чтобы достичь 99%
• Пригласите 3 друзей, чтобы получить месяц бесплатных объявлений
• Наслаждайтесь бесплатными объявлениями в течение 30 дней

🚀 **Нажмите кнопку ниже, чтобы начать!**"""
                    else:  # English
                        welcome_msg = f"""🎮 **Welcome to the Viral Referral Game!**

🎯 **You've been successfully registered via your friend's invitation!**
🎉 **You helped your friend get a referral point**

💫 **Start your journey now:**
• Complete the progress bar to reach 99%
• Invite 3 friends to get 1 month of free ads
• Enjoy free advertisements for 30 days

🚀 **Click the button below to start!**"""
                    
                    # Create start game keyboard
                    keyboard = viral_game.create_progress_keyboard(user_id, 0, language)
                    
                    await message.answer(welcome_msg, reply_markup=keyboard, parse_mode='Markdown')
                    
                    # If inviter reached 3 referrals, notify them
                    if result['reward_unlocked']:
                        try:
                            reward_msg = await viral_game.get_reward_message(inviter_id, language)
                            reward_keyboard = viral_game.create_reward_keyboard(language)
                            
                            await message.bot.send_message(
                                chat_id=inviter_id,
                                text=reward_msg,
                                reply_markup=reward_keyboard,
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            logger.error(f"Error sending reward notification to {inviter_id}: {e}")
                    
                    # Send referral progress update to inviter
                    try:
                        inviter_language = await get_user_language(inviter_id)
                        referral_count = result['referral_count']
                        
                        if inviter_language == 'ar':
                            progress_msg = f"""🎯 **تحديث الإحالة**

✅ **انضم صديق جديد إلى فريقك!**
📊 **التقدم:** {referral_count}/3 أصدقاء

{f"🏆 **مبروك! حصلت على الجائزة!**" if referral_count >= 3 else f"💪 **تحتاج إلى {3 - referral_count} أصدقاء آخرين للحصول على الجائزة**"}"""
                        elif inviter_language == 'ru':
                            progress_msg = f"""🎯 **Обновление рефералов**

✅ **Новый друг присоединился к вашей команде!**
📊 **Прогресс:** {referral_count}/3 друзей

{f"🏆 **Поздравляем! Вы получили награду!**" if referral_count >= 3 else f"💪 **Вам нужно еще {3 - referral_count} друзей для получения награды**"}"""
                        else:
                            progress_msg = f"""🎯 **Referral Update**

✅ **A new friend joined your team!**
📊 **Progress:** {referral_count}/3 friends

{f"🏆 **Congratulations! You got the reward!**" if referral_count >= 3 else f"💪 **You need {3 - referral_count} more friends to get the reward**"}"""
                        
                        await message.bot.send_message(
                            chat_id=inviter_id,
                            text=progress_msg,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error sending progress update to {inviter_id}: {e}")
                        
                else:
                    # Referral failed, but still show normal start
                    await show_viral_game_start(message, language)
                    
            except (ValueError, IndexError) as e:
                logger.error(f"Invalid referral code format: {args}")
                await show_viral_game_start(message, language)
        else:
            # Normal start without referral
            await show_viral_game_start(message, language)
            
    except Exception as e:
        logger.error(f"Error in referral start handler: {e}")
        await message.answer("Error starting the game. Please try again.")

async def show_viral_game_start(message: Message, language: str):
    """Show viral referral game start screen"""
    try:
        user_id = message.from_user.id
        viral_game = get_viral_game()
        
        # Get or create user
        user = await viral_game.get_or_create_user(user_id)
        if not user:
            await message.answer("Error loading game. Please try again.")
            return
        
        # Get progress message and keyboard
        progress_msg = await viral_game.get_progress_message(user_id, language)
        keyboard = viral_game.create_progress_keyboard(user_id, user['progress'], language)
        
        await message.answer(progress_msg, reply_markup=keyboard, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error showing viral game start: {e}")
        await message.answer("Error loading game. Please try again.")

@viral_router.callback_query(F.data.startswith("tap_progress_"))
async def handle_tap_progress(callback_query: CallbackQuery, state: FSMContext):
    """Handle progress bar tap"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        viral_game = get_viral_game()
        
        # Update progress
        user = await viral_game.update_progress(user_id)
        if not user:
            await callback_query.answer("Error updating progress")
            return
        
        # Get updated message and keyboard
        progress_msg = await viral_game.get_progress_message(user_id, language)
        keyboard = viral_game.create_progress_keyboard(user_id, user['progress'], language)
        
        # Update message
        await callback_query.message.edit_text(
            progress_msg,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Show progress feedback
        if user['progress'] >= 99:
            await callback_query.answer("🎉 99% reached! Now invite 3 friends!", show_alert=True)
        else:
            await callback_query.answer(f"Progress: {user['progress']}%")
            
    except Exception as e:
        logger.error(f"Error handling tap progress: {e}")
        await callback_query.answer("Error updating progress")

@viral_router.callback_query(F.data.startswith("check_referral_progress_"))
async def handle_check_referral_progress(callback_query: CallbackQuery, state: FSMContext):
    """Check referral progress"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        viral_game = get_viral_game()
        stats = await viral_game.get_user_stats(user_id)
        
        if not stats:
            await callback_query.answer("Error loading stats")
            return
        
        user_info = stats['user_info']
        referral_count = user_info['referral_count']
        invitations = stats['invitations']
        
        if language == 'ar':
            stats_msg = f"""📊 **إحصائيات الإحالة**

🎯 **التقدم:** {referral_count}/3 أصدقاء
🏆 **الحالة:** {"🎉 تم إلغاء قفل الجائزة!" if user_info['reward_unlocked'] else "🔒 الجائزة مقفلة"}

👥 **الأصدقاء المدعوون:**"""
        elif language == 'ru':
            stats_msg = f"""📊 **Статистика рефералов**

🎯 **Прогресс:** {referral_count}/3 друзей
🏆 **Статус:** {"🎉 Награда разблокирована!" if user_info['reward_unlocked'] else "🔒 Награда заблокирована"}

👥 **Приглашенные друзья:**"""
        else:
            stats_msg = f"""📊 **Referral Statistics**

🎯 **Progress:** {referral_count}/3 friends
🏆 **Status:** {"🎉 Reward unlocked!" if user_info['reward_unlocked'] else "🔒 Reward locked"}

👥 **Invited friends:**"""
        
        if invitations:
            for i, invitation in enumerate(invitations, 1):
                invited_date = invitation['invited_at'][:10]  # YYYY-MM-DD format
                stats_msg += f"\n{i}. Friend #{invitation['invited_user_id']} - {invited_date}"
        else:
            stats_msg += f"\n{get_text(language, 'no_invitations', 'No invitations yet')}"
        
        if user_info['reward_unlocked']:
            stats_msg += f"\n\n🆓 **Free ads remaining:** {stats['total_free_ads']}"
        
        await callback_query.message.edit_text(
            stats_msg,
            reply_markup=viral_game.create_progress_keyboard(user_id, user_info['progress'], language),
            parse_mode='Markdown'
        )
        
        await callback_query.answer("Stats updated")
        
    except Exception as e:
        logger.error(f"Error checking referral progress: {e}")
        await callback_query.answer("Error loading stats")

@viral_router.callback_query(F.data == "use_free_ad")
async def handle_use_free_ad(callback_query: CallbackQuery, state: FSMContext):
    """Handle free ad usage"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        viral_game = get_viral_game()
        stats = await viral_game.get_user_stats(user_id)
        
        if not stats or stats['total_free_ads'] == 0:
            await callback_query.answer("No free ads available", show_alert=True)
            return
        
        # Set flag in state that user wants to use free ad
        await state.update_data(use_free_ad=True)
        
        # Redirect to ad creation
        from handlers import create_ad_handler
        
        # Create a fake message for the ad creation handler
        fake_message = type('FakeMessage', (), {
            'from_user': callback_query.from_user,
            'answer': callback_query.message.answer,
            'bot': callback_query.bot
        })()
        
        await create_ad_handler(fake_message, state)
        await callback_query.answer("Starting free ad creation...")
        
    except Exception as e:
        logger.error(f"Error using free ad: {e}")
        await callback_query.answer("Error starting ad creation")

@viral_router.callback_query(F.data == "check_my_rewards")
async def handle_check_my_rewards(callback_query: CallbackQuery, state: FSMContext):
    """Check user rewards"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        viral_game = get_viral_game()
        stats = await viral_game.get_user_stats(user_id)
        
        if not stats:
            await callback_query.answer("Error loading rewards")
            return
        
        rewards = stats['active_rewards']
        total_ads = stats['total_free_ads']
        
        if language == 'ar':
            rewards_msg = f"""🎁 **مكافآتي**

🆓 **إجمالي الإعلانات المجانية:** {total_ads}

📋 **المكافآت النشطة:**"""
        elif language == 'ru':
            rewards_msg = f"""🎁 **Мои награды**

🆓 **Всего бесплатных объявлений:** {total_ads}

📋 **Активные награды:**"""
        else:
            rewards_msg = f"""🎁 **My Rewards**

🆓 **Total free ads:** {total_ads}

📋 **Active rewards:**"""
        
        if rewards:
            for i, reward in enumerate(rewards, 1):
                expires_date = reward['expires_at'][:10]  # YYYY-MM-DD format
                rewards_msg += f"\n{i}. {reward['ads_remaining']} ads (expires: {expires_date})"
        else:
            rewards_msg += f"\n{get_text(language, 'no_rewards', 'No active rewards')}"
        
        await callback_query.message.edit_text(
            rewards_msg,
            reply_markup=viral_game.create_reward_keyboard(language),
            parse_mode='Markdown'
        )
        
        await callback_query.answer("Rewards updated")
        
    except Exception as e:
        logger.error(f"Error checking rewards: {e}")
        await callback_query.answer("Error loading rewards")

# Command to start viral game directly
@viral_router.message(Command("game"))
async def start_viral_game_command(message: Message, state: FSMContext):
    """Start viral referral game with /game command"""
    try:
        user_id = message.from_user.id
        language = await get_user_language(user_id)
        
        await show_viral_game_start(message, language)
        
    except Exception as e:
        logger.error(f"Error starting viral game: {e}")
        await message.answer("Error starting the game. Please try again.")

# Function to check if user has free ads available
async def has_free_ads(user_id: int) -> bool:
    """Check if user has free ads available"""
    try:
        viral_game = get_viral_game()
        stats = await viral_game.get_user_stats(user_id)
        
        return stats and stats['total_free_ads'] > 0
        
    except Exception as e:
        logger.error(f"Error checking free ads for user {user_id}: {e}")
        return False

# Function to consume free ad
async def consume_free_ad(user_id: int) -> bool:
    """Consume one free ad"""
    try:
        viral_game = get_viral_game()
        return await viral_game.use_free_ad(user_id)
        
    except Exception as e:
        logger.error(f"Error consuming free ad for user {user_id}: {e}")
        return False