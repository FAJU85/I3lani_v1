"""
TON Wallet Address Management System
Handles wallet address collection and storage for different scenarios
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import WalletStates, AdCreationStates, CreateAd
from database import db
from languages import get_text
from database import get_user_language


logger = logging.getLogger(__name__)
router = Router()

class WalletManager:
    """Centralized TON wallet address management"""
    
    @staticmethod
    def validate_ton_address(address: str) -> bool:
        """Validate TON wallet address format"""
        if not address:
            return False
        
        # Remove whitespace
        address = address.strip()
        
        # Check prefix and length
        if not (address.startswith('EQ') or address.startswith('UQ')):
            return False
        
        if len(address) != 48:
            return False
        
        # Check if it's alphanumeric + allowed characters
        allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
        if not all(c in allowed_chars for c in address):
            return False
        
        return True
    
    @staticmethod
    async def get_user_wallet_address(user_id: int) -> Optional[str]:
        """Get user's stored TON wallet address"""
        try:
            user = await db.get_user(user_id)
            if user:
                return user.get('ton_wallet_address')
            return None
        except Exception as e:
            logger.error(f"Error getting user wallet address: {e}")
            return None
    
    @staticmethod
    async def set_user_wallet_address(user_id: int, wallet_address: str) -> bool:
        """Store user's TON wallet address"""
        try:
            await db.set_user_wallet_address(user_id, wallet_address)
            return True
        except Exception as e:
            logger.error(f"Error setting user wallet address: {e}")
            return False
    
    @staticmethod
    async def request_wallet_address(message_or_callback, state: FSMContext, context: str = 'payment'):
        """Request TON wallet address from user based on context"""
        # Handle both Message and CallbackQuery types
        if hasattr(message_or_callback, 'from_user'):
            user_id = message_or_callback.from_user.id
            if hasattr(message_or_callback, 'message'):
                # CallbackQuery
                send_method = message_or_callback.message.edit_text
            else:
                # Message
                send_method = message_or_callback.reply
        else:
            return
        
        language = await get_user_language(user_id)
        
        # Check if user already has a wallet address
        existing_wallet = await WalletManager.get_user_wallet_address(user_id)
        
        if existing_wallet:
            # User has existing wallet, ask if they want to use it or enter new one
            await WalletManager.show_wallet_options(message_or_callback, state, existing_wallet, context)
            return
        
        # No existing wallet, request new one
        await WalletManager.show_wallet_input_prompt(message_or_callback, state, context)
    
    @staticmethod
    async def show_wallet_options(message_or_callback, state: FSMContext, existing_wallet: str, context: str):
        """Show options to use existing wallet or enter new one"""
        user_id = message_or_callback.from_user.id
        language = await get_user_language(user_id)
        
        # Create context-specific messages
        if context == 'payment':
            if language == 'ar':
                title = "💰 عنوان محفظة TON للدفع"
                description = "لديك محفظة TON محفوظة مسبقاً. اختر خيار:"
                # Format wallet address properly
                wallet_display = existing_wallet[:10] + '...' + existing_wallet[-8:] if len(existing_wallet) > 20 else existing_wallet
                use_existing = f"✅ استخدام المحفظة الحالية\n`{wallet_display}`"
                enter_new = "🔄 إدخال محفظة جديدة"
            elif language == 'ru':
                title = "💰 TON адрес кошелька для оплаты"
                description = "У вас есть сохраненный TON кошелек. Выберите опцию:"
                # Format wallet address properly
                wallet_display = existing_wallet[:10] + '...' + existing_wallet[-8:] if len(existing_wallet) > 20 else existing_wallet
                use_existing = f"✅ Использовать текущий кошелек\n`{wallet_display}`"
                enter_new = "🔄 Ввести новый кошелек"
            else:
                title = "💰 TON Wallet Address for Payment"
                description = "You have a saved TON wallet. Choose an option:"
                # Format wallet address properly
                wallet_display = existing_wallet[:10] + '...' + existing_wallet[-8:] if len(existing_wallet) > 20 else existing_wallet
                use_existing = f"✅ Use Current Wallet\n`{wallet_display}`"
                enter_new = "🔄 Enter New Wallet"
        
        elif context == 'affiliate':
            if language == 'ar':
                title = "🤝 عنوان محفظة TON للبرنامج التابع"
                description = "لديك محفظة TON محفوظة مسبقاً. اختر خيار:"
                # Format wallet address properly
                wallet_display = existing_wallet[:10] + '...' + existing_wallet[-8:] if len(existing_wallet) > 20 else existing_wallet
                use_existing = f"✅ استخدام المحفظة الحالية\n`{wallet_display}`"
                enter_new = "🔄 إدخال محفظة جديدة"
            elif language == 'ru':
                title = "🤝 TON адрес кошелька для партнерской программы"
                description = "У вас есть сохраненный TON кошелек. Выберите опцию:"
                # Format wallet address properly
                wallet_display = existing_wallet[:10] + '...' + existing_wallet[-8:] if len(existing_wallet) > 20 else existing_wallet
                use_existing = f"✅ Использовать текущий кошелек\n`{wallet_display}`"
                enter_new = "🔄 Ввести новый кошелек"
            else:
                title = "🤝 TON Wallet Address for Affiliate Program"
                description = "You have a saved TON wallet. Choose an option:"
                # Format wallet address properly
                wallet_display = existing_wallet[:10] + '...' + existing_wallet[-8:] if len(existing_wallet) > 20 else existing_wallet
                use_existing = f"✅ Use Current Wallet\n`{wallet_display}`"
                enter_new = "🔄 Enter New Wallet"
        
        elif context == 'channel':
            if language == 'ar':
                title = "📺 عنوان محفظة TON لإضافة القناة"
                description = "لديك محفظة TON محفوظة مسبقاً. اختر خيار:"
                # Format wallet address properly
                wallet_display = existing_wallet[:10] + '...' + existing_wallet[-8:] if len(existing_wallet) > 20 else existing_wallet
                use_existing = f"✅ استخدام المحفظة الحالية\n`{wallet_display}`"
                enter_new = "🔄 إدخال محفظة جديدة"
            elif language == 'ru':
                title = "📺 TON адрес кошелька для добавления канала"
                description = "У вас есть сохраненный TON кошелек. Выберите опцию:"
                # Format wallet address properly
                wallet_display = existing_wallet[:10] + '...' + existing_wallet[-8:] if len(existing_wallet) > 20 else existing_wallet
                use_existing = f"✅ Использовать текущий кошелек\n`{wallet_display}`"
                enter_new = "🔄 Ввести новый кошелек"
            else:
                title = "📺 TON Wallet Address for Channel Addition"
                description = "You have a saved TON wallet. Choose an option:"
                # Format wallet address properly
                wallet_display = existing_wallet[:10] + '...' + existing_wallet[-8:] if len(existing_wallet) > 20 else existing_wallet
                use_existing = f"✅ Use Current Wallet\n`{wallet_display}`"
                enter_new = "🔄 Enter New Wallet"
        
        text = f"**{title}**\n\n{description}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=use_existing, callback_data=f"use_existing_wallet_{context}")],
            [InlineKeyboardButton(text=enter_new, callback_data=f"enter_new_wallet_{context}")],
            [InlineKeyboardButton(text="❌ Cancel" if language == 'en' else "❌ إلغاء" if language == 'ar' else "❌ Отмена", callback_data="cancel_wallet_input")]
        ])
        
        # Store context and existing wallet for later use - PRESERVE existing state data
        current_data = await state.get_data()
        await state.update_data(
            wallet_context=context,
            existing_wallet=existing_wallet,
            # Preserve payment data if it exists
            **{k: v for k, v in current_data.items() if k.startswith(('pending_payment', 'payment_', 'amount_', 'final_pricing'))}
        )
        
        if hasattr(message_or_callback, 'message'):
            await message_or_callback.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
        else:
            await message_or_callback.reply(text, reply_markup=keyboard, parse_mode='Markdown')
    
    @staticmethod
    async def show_wallet_input_prompt(message_or_callback, state: FSMContext, context: str):
        """Show wallet input prompt based on context"""
        user_id = message_or_callback.from_user.id
        language = await get_user_language(user_id)
        
        # Create context-specific messages
        if context == 'payment':
            if language == 'ar':
                title = "💰 إدخال عنوان محفظة TON للدفع"
                description = "لمعالجة دفعة TON، نحتاج إلى عنوان محفظتك:"
                instructions = """**التعليمات:**
- يجب أن يكون هذا العنوان الذي ستدفع منه
- يبدأ بـ EQ أو UQ
- يجب أن يكون 48 حرفاً بالضبط
- تأكد من صحة العنوان لتجنب فقدان الأموال"""
            elif language == 'ru':
                title = "💰 Ввод адреса TON кошелька для оплаты"
                description = "Для обработки TON платежа нам нужен адрес вашего кошелька:"
                instructions = """**Инструкции:**
- Это должен быть адрес, с которого вы будете платить
- Начинается с EQ или UQ
- Должен быть точно 48 символов
- Убедитесь в правильности адреса, чтобы избежать потери средств"""
            else:
                title = "💰 Enter TON Wallet Address for Payment"
                description = "To process your TON payment, we need your wallet address:"
                instructions = """**Instructions:**
- This should be the address you will pay from
- Starts with EQ or UQ
- Must be exactly 48 characters
- Ensure the address is correct to avoid loss of funds"""
        
        elif context == 'affiliate':
            if language == 'ar':
                title = "🤝 إدخال عنوان محفظة TON للبرنامج التابع"
                description = "لتلقي عمولات البرنامج التابع، نحتاج إلى عنوان محفظتك:"
                instructions = """**التعليمات:**
- سيتم إرسال جميع العمولات إلى هذا العنوان
- يبدأ بـ EQ أو UQ
- يجب أن يكون 48 حرفاً بالضبط
- تأكد من صحة العنوان لتجنب فقدان العمولات"""
            elif language == 'ru':
                title = "🤝 Ввод адреса TON кошелька для партнерской программы"
                description = "Для получения комиссий партнерской программы нам нужен адрес вашего кошелька:"
                instructions = """**Инструкции:**
- Все комиссии будут отправлены на этот адрес
- Начинается с EQ или UQ
- Должен быть точно 48 символов
- Убедитесь в правильности адреса, чтобы не потерять комиссии"""
            else:
                title = "🤝 Enter TON Wallet Address for Affiliate Program"
                description = "To receive affiliate commissions, we need your wallet address:"
                instructions = """**Instructions:**
- All commissions will be sent to this address
- Starts with EQ or UQ
- Must be exactly 48 characters
- Ensure the address is correct to avoid losing commissions"""
        
        elif context == 'channel':
            if language == 'ar':
                title = "📺 إدخال عنوان محفظة TON لإضافة القناة"
                description = "لتلقي أرباح النشر في القناة، نحتاج إلى عنوان محفظتك:"
                instructions = """**التعليمات:**
- سيتم إرسال جميع أرباح النشر إلى هذا العنوان
- يبدأ بـ EQ أو UQ
- يجب أن يكون 48 حرفاً بالضبط
- تأكد من صحة العنوان لتجنب فقدان الأرباح"""
            elif language == 'ru':
                title = "📺 Ввод адреса TON кошелька для добавления канала"
                description = "Для получения доходов от публикации в канале нам нужен адрес вашего кошелька:"
                instructions = """**Инструкции:**
- Все доходы от публикации будут отправлены на этот адрес
- Начинается с EQ или UQ
- Должен быть точно 48 символов
- Убедитесь в правильности адреса, чтобы не потерять доходы"""
            else:
                title = "📺 Enter TON Wallet Address for Channel Addition"
                description = "To receive channel publishing earnings, we need your wallet address:"
                instructions = """**Instructions:**
- All publishing earnings will be sent to this address
- Starts with EQ or UQ
- Must be exactly 48 characters
- Ensure the address is correct to avoid losing earnings"""
        
        text = f"**{title}**\n\n{description}\n\n{instructions}\n\n**Example:** `EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE`\n\n💬 Send your wallet address now:"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel" if language == 'en' else "❌ إلغاء" if language == 'ar' else "❌ Отмена", callback_data="cancel_wallet_input")]
        ])
        
        # Set appropriate state based on context
        if context == 'payment':
            await state.set_state(WalletStates.payment_wallet_input)
        elif context == 'affiliate':
            await state.set_state(WalletStates.affiliate_wallet_input)
        elif context == 'channel':
            await state.set_state(WalletStates.channel_wallet_input)
        
        # Store context for later use - PRESERVE existing state data
        current_data = await state.get_data()
        await state.update_data(
            wallet_context=context,
            # Preserve payment data if it exists
            **{k: v for k, v in current_data.items() if k.startswith(('pending_payment', 'payment_', 'amount_', 'final_pricing'))}
        )
        
        if hasattr(message_or_callback, 'message'):
            await message_or_callback.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
        else:
            await message_or_callback.reply(text, reply_markup=keyboard, parse_mode='Markdown')

# Callback handlers for wallet options
@router.callback_query(F.data.startswith("use_existing_wallet_"))
async def use_existing_wallet_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle using existing wallet address"""
    try:
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Extract context from callback data
        context = callback_query.data.replace("use_existing_wallet_", "")
        
        # Get existing wallet from state data
        data = await state.get_data()
        existing_wallet = data.get('existing_wallet')
        
        # If no wallet in state, try to get from database
        if not existing_wallet:
            existing_wallet = await WalletManager.get_user_wallet_address(user_id)
        
        if not existing_wallet:
            # Show error message in user's language
            error_msg = {
                'ar': "❌ خطأ: لا يوجد محفظة محفوظة",
                'ru': "❌ Ошибка: Не найден сохраненный кошелек",
                'en': "❌ Error: No saved wallet found"
            }.get(language, "❌ Error: No saved wallet found")
            
            await callback_query.answer(error_msg, show_alert=True)
            return
        
        # Show loading message
        loading_msg = {
            'ar': "🔄 جاري المتابعة بالمحفظة الحالية...",
            'ru': "🔄 Продолжение с текущим кошельком...",
            'en': "🔄 Continuing with current wallet..."
        }.get(language, "🔄 Continuing with current wallet...")
        
        await callback_query.answer(loading_msg)
        
        # Continue with the appropriate flow based on context
        if context == 'payment':
            await continue_payment_with_wallet(callback_query, state, existing_wallet)
        elif context == 'affiliate':
            await continue_affiliate_with_wallet(callback_query, state, existing_wallet)
        elif context == 'channel':
            await continue_channel_with_wallet(callback_query, state, existing_wallet)
        else:
            # Unknown context error
            error_msg = {
                'ar': "❌ خطأ: سياق غير معروف",
                'ru': "❌ Ошибка: Неизвестный контекст",
                'en': "❌ Error: Unknown context"
            }.get(language, "❌ Error: Unknown context")
            
            await callback_query.answer(error_msg, show_alert=True)
            
    except Exception as e:
        logger.error(f"Error in use_existing_wallet_handler: {e}")
        
        # Show generic error message
        error_msg = {
            'ar': "❌ حدث خطأ، يرجى المحاولة مرة أخرى",
            'ru': "❌ Произошла ошибка, попробуйте еще раз",
            'en': "❌ An error occurred, please try again"
        }.get(language, "❌ An error occurred, please try again")
        
        await callback_query.answer(error_msg, show_alert=True)

@router.callback_query(F.data.startswith("enter_new_wallet_"))
async def enter_new_wallet_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle entering new wallet address"""
    context = callback_query.data.replace("enter_new_wallet_", "")
    
    # Show wallet input prompt
    await WalletManager.show_wallet_input_prompt(callback_query, state, context)
    await callback_query.answer()

# Message handlers for wallet address input
@router.message(WalletStates.payment_wallet_input)
async def handle_payment_wallet_input(message: Message, state: FSMContext):
    """Handle wallet address input for payment"""
    await process_wallet_input(message, state, 'payment')

@router.message(WalletStates.affiliate_wallet_input)
async def handle_affiliate_wallet_input(message: Message, state: FSMContext):
    """Handle wallet address input for affiliate program"""
    await process_wallet_input(message, state, 'affiliate')

@router.message(WalletStates.channel_wallet_input)
async def handle_channel_wallet_input(message: Message, state: FSMContext):
    """Handle wallet address input for channel addition"""
    await process_wallet_input(message, state, 'channel')

async def process_wallet_input(message: Message, state: FSMContext, context: str):
    """Process wallet address input"""
    user_id = message.from_user.id
    language = await get_user_language(user_id)
    wallet_address = message.text.strip()
    
    # Validate wallet address
    if not WalletManager.validate_ton_address(wallet_address):
        if language == 'ar':
            error_text = "❌ عنوان المحفظة غير صحيح. يجب أن يبدأ بـ EQ أو UQ ويكون 48 حرفاً. حاول مرة أخرى:"
        elif language == 'ru':
            error_text = "❌ Неверный адрес кошелька. Должен начинаться с EQ или UQ и быть длиной 48 символов. Попробуйте еще раз:"
        else:
            error_text = "❌ Invalid wallet address. Must start with EQ or UQ and be 48 characters long. Try again:"
        
        await message.reply(error_text)
        return
    
    # Store wallet address
    wallet_saved = await WalletManager.set_user_wallet_address(user_id, wallet_address)
    logger.info(f"💾 Wallet address storage result for user {user_id}: {wallet_saved}")
    
    # Verify the wallet was saved
    try:
        saved_wallet = await WalletManager.get_user_wallet_address(user_id)
        logger.info(f"✅ Verified saved wallet for user {user_id}: {saved_wallet[:10]}...{saved_wallet[-8:] if saved_wallet else 'None'}")
    except Exception as e:
        logger.error(f"❌ Error verifying wallet save: {e}")
    
    # Continue with appropriate flow based on context
    if context == 'payment':
        await continue_payment_with_wallet(message, state, wallet_address)
    elif context == 'affiliate':
        await continue_affiliate_with_wallet(message, state, wallet_address)
    elif context == 'channel':
        await continue_channel_with_wallet(message, state, wallet_address)

async def continue_payment_with_wallet(message_or_callback, state: FSMContext, wallet_address: str):
    """Continue payment process with wallet address"""
    # Get payment amount from state - try multiple keys with extensive debugging
    data = await state.get_data()
    logger.info(f"🔍 Available state data keys: {list(data.keys())}")
    
    # Try all possible payment amount keys
    amount_ton = (data.get('pending_payment_amount') or 
                  data.get('payment_amount') or 
                  data.get('amount_ton'))
    
    # Try to get from pricing data if not found
    if not amount_ton:
        pricing = data.get('final_pricing', {})
        if pricing and 'ton_amount' in pricing:
            amount_ton = pricing['ton_amount']
            logger.info(f"✅ Found amount in pricing data: {amount_ton} TON")
    
    # If still not found, try to calculate from pricing
    if not amount_ton and 'final_pricing' in data:
        pricing = data['final_pricing']
        if 'final_price' in pricing:
            # Convert USD to TON (approximately 1 USD = 0.36 TON)
            amount_ton = pricing['final_price'] * 0.36
            logger.info(f"✅ Calculated amount from USD price: {amount_ton} TON")
    
    if not amount_ton:
        # Log all available data for debugging
        logger.error(f"❌ No payment amount found in state data: {data}")
        
        # Handle both Message and CallbackQuery objects
        error_msg = "❌ Payment session expired. Please start over."
        if hasattr(message_or_callback, 'message'):
            # CallbackQuery
            await message_or_callback.message.answer(error_msg)
        else:
            # Message
            await message_or_callback.reply(error_msg)
        return
    
    logger.info(f"✅ Using payment amount: {amount_ton} TON")
    
    # Store wallet address in state
    await state.update_data(user_wallet_address=wallet_address)
    
    # Create a simplified payment processing directly here to avoid complex object handling
    user_id = message_or_callback.from_user.id
    language = await get_user_language(user_id)
    
    # Generate payment details
    import random
    import string
    import time
    from config import TON_WALLET_ADDRESS
    
    bot_wallet = TON_WALLET_ADDRESS or "EQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmrSE"
    
    # Generate unique memo (2 letters + 4 digits format)
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = ''.join(random.choices(string.digits, k=4))
    memo = letters + digits
    
    # Create expiration timestamp (20 minutes from now)
    expiration_time = int(time.time()) + (20 * 60)
    
    # Store payment info
    await state.update_data(
        payment_memo=memo,
        payment_amount=amount_ton,
        payment_expiration=expiration_time,
        bot_wallet=bot_wallet
    )
    
    # Create concise payment message to avoid MESSAGE_TOO_LONG
    if language == 'ar':
        payment_text = f"""💰 **دفع TON**

**المبلغ:** {amount_ton:.3f} TON
**العنوان:** `{bot_wallet}`
**المذكرة:** `{memo}`

**خطوات الدفع:**
1. افتح محفظة TON
2. أرسل {amount_ton:.3f} TON للعنوان أعلاه
3. أضف المذكرة `{memo}` بالضبط
4. أكد المعاملة

⏰ ينتهي في: 20 دقيقة
✅ التحقق التلقائي كل 30 ثانية"""
    elif language == 'ru':
        payment_text = f"""💰 **Оплата TON**

**Сумма:** {amount_ton:.3f} TON
**Адрес:** `{bot_wallet}`
**Заметка:** `{memo}`

**Шаги оплаты:**
1. Откройте ваш TON кошелек
2. Отправьте {amount_ton:.3f} TON на адрес выше
3. Добавьте заметку `{memo}` точно
4. Подтвердите транзакцию

⏰ Истекает через: 20 минут
✅ Автопроверка каждые 30 секунд"""
    else:
        payment_text = f"""💰 **TON Payment**

**Amount:** {amount_ton:.3f} TON
**Address:** `{bot_wallet}`
**Memo:** `{memo}`

**Payment Steps:**
1. Open your TON wallet
2. Send {amount_ton:.3f} TON to address above
3. Add memo `{memo}` exactly
4. Confirm transaction

⏰ Expires in: 20 minutes
✅ Auto-verification every 30 seconds"""
    
    # Create keyboard with cancel option
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel Payment", callback_data="cancel_payment")]
    ])
    
    # Send payment message
    if hasattr(message_or_callback, 'message'):
        # CallbackQuery
        await message_or_callback.message.edit_text(payment_text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        # Message
        await message_or_callback.reply(payment_text, reply_markup=keyboard, parse_mode='Markdown')
    
    # Track payment for automatic confirmation
    from automatic_payment_confirmation import track_payment_for_user
    
    # Check if this is a post package purchase
    is_post_package = data.get('post_package_purchase', False)
    
    if is_post_package:
        # Track post package purchase
        calculation = data.get('total_calculation', {})
        package_info = calculation.get('package', {})
        
        ad_data = {
            'type': 'post_package',
            'package_name': package_info.get('name', 'Post Package'),
            'posts_total': package_info.get('posts', 0),
            'auto_schedule_days': data.get('auto_schedule_days', 0),
            'selected_addons': data.get('selected_addons', []),
            'total_usd': calculation.get('total_usd', 0)
        }
        
        logger.info(f"📦 Tracking post package purchase: {ad_data}")
    else:
        # Regular campaign payment
        ad_data = {
            'duration_days': data.get('duration_days', 7),
            'posts_per_day': data.get('posts_per_day', 1),
            'selected_channels': data.get('selected_channels', []),
            'total_reach': data.get('total_reach', 0),
            'ad_content': data.get('ad_content', '')
        }
        
        logger.info(f"📢 Tracking campaign payment: {ad_data}")
    
    # Track payment for automatic confirmation
    await track_payment_for_user(user_id, memo, amount_ton, ad_data)
    
    # Start payment monitoring using enhanced TON payment monitoring
    import asyncio
    from enhanced_ton_payment_monitoring import monitor_ton_payment_enhanced
    
    # Log the payment initiation
    logger.info(f"💰 Starting payment monitoring for user {user_id}: {amount_ton:.3f} TON, memo: {memo}")
    
    # Start monitoring in background
    asyncio.create_task(monitor_ton_payment_enhanced(user_id, memo, amount_ton, expiration_time, wallet_address, state, bot_wallet))
    
    # Set state to wait for payment
    await state.set_state(CreateAd.waiting_payment_confirmation)

async def continue_affiliate_with_wallet(message_or_callback, state: FSMContext, wallet_address: str):
    """Continue affiliate program enrollment with wallet address"""
    user_id = message_or_callback.from_user.id
    language = await get_user_language(user_id)
    
    # Store wallet address for affiliate program
    await state.update_data(affiliate_wallet_address=wallet_address)
    
    # Continue with affiliate enrollment
    if language == 'ar':
        success_text = f"✅ تم حفظ محفظة TON بنجاح!\n\n**العنوان:** `{wallet_address}`\n\n🤝 يمكنك الآن الانضمام إلى البرنامج التابع وتلقي العمولات."
    elif language == 'ru':
        success_text = f"✅ TON кошелек успешно сохранен!\n\n**Адрес:** `{wallet_address}`\n\n🤝 Теперь вы можете присоединиться к партнерской программе и получать комиссии."
    else:
        success_text = f"✅ TON wallet saved successfully!\n\n**Address:** `{wallet_address}`\n\n🤝 You can now join the affiliate program and receive commissions."
    
    # Handle both Message and CallbackQuery objects
    if hasattr(message_or_callback, 'message'):
        # CallbackQuery
        await message_or_callback.message.answer(success_text, parse_mode='Markdown')
    else:
        # Message
        await message_or_callback.reply(success_text, parse_mode='Markdown')

async def continue_channel_with_wallet(message_or_callback, state: FSMContext, wallet_address: str):
    """Continue channel addition with wallet address"""
    user_id = message_or_callback.from_user.id
    language = await get_user_language(user_id)
    
    # Store wallet address for channel earnings
    await state.update_data(channel_wallet_address=wallet_address)
    
    # Continue with channel addition
    if language == 'ar':
        success_text = f"✅ تم حفظ محفظة TON بنجاح!\n\n**العنوان:** `{wallet_address}`\n\n📺 يمكنك الآن إضافة قناتك وتلقي أرباح النشر."
    elif language == 'ru':
        success_text = f"✅ TON кошелек успешно сохранен!\n\n**Адрес:** `{wallet_address}`\n\n📺 Теперь вы можете добавить свой канал и получать доходы от публикации."
    else:
        success_text = f"✅ TON wallet saved successfully!\n\n**Address:** `{wallet_address}`\n\n📺 You can now add your channel and receive publishing earnings."
    
    # Handle both Message and CallbackQuery objects
    if hasattr(message_or_callback, 'message'):
        # CallbackQuery
        await message_or_callback.message.answer(success_text, parse_mode='Markdown')
    else:
        # Message
        await message_or_callback.reply(success_text, parse_mode='Markdown')

@router.callback_query(F.data == "cancel_wallet_input")
async def cancel_wallet_input_handler(callback_query: CallbackQuery, state: FSMContext):
    """Handle wallet input cancellation"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Clear wallet-related state
    await state.clear()
    
    # Send cancellation message
    if language == 'ar':
        cancel_text = "❌ تم إلغاء إدخال عنوان المحفظة. يمكنك المحاولة مرة أخرى لاحقاً."
    elif language == 'ru':
        cancel_text = "❌ Ввод адреса кошелька отменен. Вы можете попробовать еще раз позже."
    else:
        cancel_text = "❌ Wallet address input cancelled. You can try again later."
    
    await callback_query.message.edit_text(cancel_text)
    await callback_query.answer()