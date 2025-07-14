"""
Post-Based System Handlers for I3lani Bot
Handles package selection, add-ons, and post management
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import List, Dict

from post_based_pricing_system import get_post_pricing_system, PostPackage
from user_post_manager import get_user_post_manager
from database import get_user_language

router = Router()

class PostBasedStates(StatesGroup):
    """States for post-based system"""
    selecting_package = State()
    selecting_addons = State()
    configuring_auto_schedule = State()
    payment_confirmation = State()
    post_usage = State()

@router.callback_query(F.data == "create_ad")
async def create_ad_post_based(callback_query: CallbackQuery, state: FSMContext):
    """Handle ad creation with post-based system"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Check user's post balance
    post_manager = get_user_post_manager()
    balance = await post_manager.get_user_post_balance(user_id)
    
    if balance['has_credits']:
        # User has credits, show quick post options
        await show_quick_post_options(callback_query, state, balance)
    else:
        # User needs to buy credits
        await show_package_selection(callback_query, state)

async def show_quick_post_options(callback_query: CallbackQuery, state: FSMContext, balance: Dict):
    """Show quick post options for users with credits"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    if language == 'ar':
        text = f"""🎯 **إنشاء إعلان سريع**

💳 **رصيدك:**
📊 {balance['total_available']} منشور متاح
💰 قيمة إجمالية: ${balance.get('total_value', 0):.2f}

اختر طريقة النشر:"""
        buttons = [
            [InlineKeyboardButton(text="📝 نشر فوري", callback_data="post_now")],
            [InlineKeyboardButton(text="📅 جدولة تلقائية", callback_data="auto_schedule")],
            [InlineKeyboardButton(text="🛒 شراء المزيد", callback_data="buy_more_posts")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")]
        ]
    elif language == 'ru':
        text = f"""🎯 **Быстрое создание рекламы**

💳 **Ваш баланс:**
📊 {balance['total_available']} постов доступно
💰 Общая стоимость: ${balance.get('total_value', 0):.2f}

Выберите способ публикации:"""
        buttons = [
            [InlineKeyboardButton(text="📝 Опубликовать сейчас", callback_data="post_now")],
            [InlineKeyboardButton(text="📅 Автопланировщик", callback_data="auto_schedule")],
            [InlineKeyboardButton(text="🛒 Купить больше", callback_data="buy_more_posts")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ]
    else:  # English
        text = f"""🎯 **Quick Ad Creation**

💳 **Your Balance:**
📊 {balance['total_available']} posts available
💰 Total value: ${balance.get('total_value', 0):.2f}

Choose posting method:"""
        buttons = [
            [InlineKeyboardButton(text="📝 Post Now", callback_data="post_now")],
            [InlineKeyboardButton(text="📅 Auto-Schedule", callback_data="auto_schedule")],
            [InlineKeyboardButton(text="🛒 Buy More Posts", callback_data="buy_more_posts")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")]
        ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

async def show_package_selection(callback_query: CallbackQuery, state: FSMContext):
    """Show package selection interface"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    pricing_system = get_post_pricing_system()
    packages = pricing_system.get_all_packages()
    
    if language == 'ar':
        text = """📦 **اختر حزمة المنشورات**

اختر الحزمة المناسبة لحملتك الإعلانية:"""
    elif language == 'ru':
        text = """📦 **Выберите пакет постов**

Выберите подходящий пакет для вашей рекламной кампании:"""
    else:  # English
        text = """📦 **Choose Post Package**

Select the right package for your advertising campaign:"""
    
    buttons = []
    for package in packages:
        package_text = pricing_system.format_package_display(
            PostPackage(package['package']), language
        )
        
        # Add package as a row
        buttons.append([InlineKeyboardButton(
            text=f"{package['name']} - ${package['price_usd']:.2f}",
            callback_data=f"select_package_{package['package']}"
        )])
    
    # Add back button
    back_text = "🔙 العودة" if language == 'ar' else "🔙 Назад" if language == 'ru' else "🔙 Back"
    buttons.append([InlineKeyboardButton(text=back_text, callback_data="back_to_main")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()
    await state.set_state(PostBasedStates.selecting_package)

@router.callback_query(F.data.startswith("select_package_"))
async def handle_package_selection(callback_query: CallbackQuery, state: FSMContext):
    """Handle package selection"""
    package_key = callback_query.data.split("_")[-1]
    package = PostPackage(package_key)
    
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Store selected package
    await state.update_data(selected_package=package_key)
    
    # Show package details and add-ons
    await show_package_details_and_addons(callback_query, state, package)

async def show_package_details_and_addons(callback_query: CallbackQuery, state: FSMContext, package: PostPackage):
    """Show package details and available add-ons"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    pricing_system = get_post_pricing_system()
    package_info = pricing_system.get_package_info(package)
    addons = pricing_system.get_all_addons()
    
    if language == 'ar':
        text = f"""📦 **تفاصيل الحزمة: {package_info['name']}**

📊 **المنشورات:** {package_info['posts']}
💰 **السعر:** ${package_info['price_usd']:.2f}
📈 **التوفير:** {package_info['savings_vs_starter']:.1f}% مقارنة بالمبتدئين

🔧 **الإضافات المتاحة:**"""
    elif language == 'ru':
        text = f"""📦 **Детали пакета: {package_info['name']}**

📊 **Постов:** {package_info['posts']}
💰 **Цена:** ${package_info['price_usd']:.2f}
📈 **Экономия:** {package_info['savings_vs_starter']:.1f}% по сравнению со стартовым

🔧 **Доступные дополнения:**"""
    else:  # English
        text = f"""📦 **Package Details: {package_info['name']}**

📊 **Posts:** {package_info['posts']}
💰 **Price:** ${package_info['price_usd']:.2f}
📈 **Savings:** {package_info['savings_vs_starter']:.1f}% vs Starter

🔧 **Available Add-ons:**"""
    
    buttons = []
    
    # Add-on buttons
    for addon in addons[:3]:  # Show top 3 add-ons
        addon_text = f"{addon['name']} (+${addon['price_usd']:.2f})"
        buttons.append([InlineKeyboardButton(
            text=addon_text,
            callback_data=f"toggle_addon_{addon['key']}"
        )])
    
    # Main action buttons
    if language == 'ar':
        buttons.extend([
            [InlineKeyboardButton(text="💳 المتابعة للدفع", callback_data="proceed_to_payment")],
            [InlineKeyboardButton(text="📅 إضافة جدولة تلقائية", callback_data="add_auto_schedule")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_packages")]
        ])
    elif language == 'ru':
        buttons.extend([
            [InlineKeyboardButton(text="💳 Перейти к оплате", callback_data="proceed_to_payment")],
            [InlineKeyboardButton(text="📅 Добавить автопланирование", callback_data="add_auto_schedule")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_packages")]
        ])
    else:  # English
        buttons.extend([
            [InlineKeyboardButton(text="💳 Proceed to Payment", callback_data="proceed_to_payment")],
            [InlineKeyboardButton(text="📅 Add Auto-Schedule", callback_data="add_auto_schedule")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_packages")]
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()

@router.callback_query(F.data.startswith("toggle_addon_"))
async def handle_addon_toggle(callback_query: CallbackQuery, state: FSMContext):
    """Handle add-on toggle"""
    addon_key = callback_query.data.split("_", 2)[-1]
    
    # Get current state data
    data = await state.get_data()
    selected_addons = data.get('selected_addons', [])
    
    # Toggle add-on
    if addon_key in selected_addons:
        selected_addons.remove(addon_key)
    else:
        selected_addons.append(addon_key)
    
    await state.update_data(selected_addons=selected_addons)
    
    # Refresh display
    package_key = data.get('selected_package')
    if package_key:
        package = PostPackage(package_key)
        await show_package_details_and_addons(callback_query, state, package)

@router.callback_query(F.data == "add_auto_schedule")
async def handle_auto_schedule_config(callback_query: CallbackQuery, state: FSMContext):
    """Handle auto-schedule configuration"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    package_key = data.get('selected_package')
    
    if not package_key:
        await callback_query.answer("❌ Please select a package first", show_alert=True)
        return
    
    pricing_system = get_post_pricing_system()
    package_info = pricing_system.get_package_info(PostPackage(package_key))
    
    # Calculate optimal schedules
    optimal_schedules = pricing_system.calculate_optimal_schedule(package_info['posts'])
    
    if language == 'ar':
        text = f"""📅 **إعداد الجدولة التلقائية**

📦 حزمة: {package_info['name']} ({package_info['posts']} منشور)
💰 تكلفة الجدولة: $0.25 لكل يوم

اختر فترة الجدولة:"""
    elif language == 'ru':
        text = f"""📅 **Настройка автопланирования**

📦 Пакет: {package_info['name']} ({package_info['posts']} постов)
💰 Стоимость планирования: $0.25 в день

Выберите период планирования:"""
    else:  # English
        text = f"""📅 **Auto-Schedule Configuration**

📦 Package: {package_info['name']} ({package_info['posts']} posts)
💰 Scheduling cost: $0.25 per day

Choose scheduling period:"""
    
    buttons = []
    for schedule in optimal_schedules[:5]:  # Show top 5 options
        schedule_text = f"{schedule['days']} days ({schedule['posts_per_day']:.1f} posts/day) +${schedule['auto_schedule_cost']:.2f}"
        buttons.append([InlineKeyboardButton(
            text=schedule_text,
            callback_data=f"select_schedule_{schedule['days']}"
        )])
    
    # Back button
    back_text = "🔙 العودة" if language == 'ar' else "🔙 Назад" if language == 'ru' else "🔙 Back"
    buttons.append([InlineKeyboardButton(text=back_text, callback_data=f"select_package_{package_key}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()
    await state.set_state(PostBasedStates.configuring_auto_schedule)

@router.callback_query(F.data.startswith("select_schedule_"))
async def handle_schedule_selection(callback_query: CallbackQuery, state: FSMContext):
    """Handle schedule selection"""
    days = int(callback_query.data.split("_")[-1])
    
    await state.update_data(auto_schedule_days=days)
    await callback_query.answer(f"✅ Auto-schedule set for {days} days")
    
    # Return to package details
    data = await state.get_data()
    package_key = data.get('selected_package')
    if package_key:
        package = PostPackage(package_key)
        await show_package_details_and_addons(callback_query, state, package)

@router.callback_query(F.data == "proceed_to_payment")
async def handle_payment_proceed(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment proceed"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    data = await state.get_data()
    package_key = data.get('selected_package')
    selected_addons = data.get('selected_addons', [])
    auto_schedule_days = data.get('auto_schedule_days', 0)
    
    if not package_key:
        await callback_query.answer("❌ Please select a package first", show_alert=True)
        return
    
    pricing_system = get_post_pricing_system()
    package = PostPackage(package_key)
    
    # Calculate total price
    total_calculation = pricing_system.calculate_total_price(
        package, selected_addons, auto_schedule_days
    )
    
    # Store pricing data for payment
    await state.update_data(total_calculation=total_calculation)
    
    # Show payment summary
    await show_payment_summary(callback_query, state, total_calculation)

async def show_payment_summary(callback_query: CallbackQuery, state: FSMContext, calculation: Dict):
    """Show payment summary and payment options"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    package_info = calculation['package']
    
    if language == 'ar':
        text = f"""💳 **ملخص الدفع**

📦 **الحزمة:** {package_info['name']}
📊 **المنشورات:** {package_info['posts']}
💰 **سعر الحزمة:** ${package_info['price_usd']:.2f}

"""
    elif language == 'ru':
        text = f"""💳 **Сводка оплаты**

📦 **Пакет:** {package_info['name']}
📊 **Постов:** {package_info['posts']}
💰 **Цена пакета:** ${package_info['price_usd']:.2f}

"""
    else:  # English
        text = f"""💳 **Payment Summary**

📦 **Package:** {package_info['name']}
📊 **Posts:** {package_info['posts']}
💰 **Package Price:** ${package_info['price_usd']:.2f}

"""
    
    # Add auto-schedule if selected
    if calculation.get('auto_schedule_days', 0) > 0:
        if language == 'ar':
            text += f"📅 **الجدولة التلقائية:** {calculation['auto_schedule_days']} أيام (+${calculation['auto_schedule_cost']:.2f})\n"
        elif language == 'ru':
            text += f"📅 **Автопланирование:** {calculation['auto_schedule_days']} дней (+${calculation['auto_schedule_cost']:.2f})\n"
        else:
            text += f"📅 **Auto-Schedule:** {calculation['auto_schedule_days']} days (+${calculation['auto_schedule_cost']:.2f})\n"
    
    # Add selected add-ons
    for addon in calculation.get('addons', []):
        text += f"🔧 **{addon['name']}:** +${addon['price_usd']:.2f}\n"
    
    # Total
    if language == 'ar':
        text += f"\n💎 **المجموع:** ${calculation['total_usd']:.2f}\n"
        text += f"🪙 **TON:** {calculation['total_ton']:.2f}\n"
        text += f"⭐ **النجوم:** {calculation['total_stars']}\n\n"
        text += "اختر طريقة الدفع:"
    elif language == 'ru':
        text += f"\n💎 **Итого:** ${calculation['total_usd']:.2f}\n"
        text += f"🪙 **TON:** {calculation['total_ton']:.2f}\n"
        text += f"⭐ **Звезды:** {calculation['total_stars']}\n\n"
        text += "Выберите способ оплаты:"
    else:
        text += f"\n💎 **Total:** ${calculation['total_usd']:.2f}\n"
        text += f"🪙 **TON:** {calculation['total_ton']:.2f}\n"
        text += f"⭐ **Stars:** {calculation['total_stars']}\n\n"
        text += "Choose payment method:"
    
    # Payment buttons
    if language == 'ar':
        buttons = [
            [InlineKeyboardButton(text=f"🪙 دفع بـ TON ({calculation['total_ton']:.2f})", callback_data="pay_post_ton")],
            [InlineKeyboardButton(text=f"⭐ دفع بالنجوم ({calculation['total_stars']})", callback_data="pay_post_stars")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_packages")]
        ]
    elif language == 'ru':
        buttons = [
            [InlineKeyboardButton(text=f"🪙 Оплатить TON ({calculation['total_ton']:.2f})", callback_data="pay_post_ton")],
            [InlineKeyboardButton(text=f"⭐ Оплатить звездами ({calculation['total_stars']})", callback_data="pay_post_stars")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_packages")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text=f"🪙 Pay with TON ({calculation['total_ton']:.2f})", callback_data="pay_post_ton")],
            [InlineKeyboardButton(text=f"⭐ Pay with Stars ({calculation['total_stars']})", callback_data="pay_post_stars")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_packages")]
        ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback_query.answer()
    await state.set_state(PostBasedStates.payment_confirmation)

@router.callback_query(F.data == "pay_post_ton")
async def handle_post_ton_payment(callback_query: CallbackQuery, state: FSMContext):
    """Handle TON payment for post package"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get calculation data
    data = await state.get_data()
    calculation = data.get('total_calculation')
    
    if not calculation:
        await callback_query.answer("❌ Payment data not found", show_alert=True)
        return
    
    # Process TON payment using existing system
    from wallet_manager import WalletManager
    
    wallet_manager = WalletManager()
    
    # Store payment data in the expected format
    await state.update_data(
        pricing_data={
            'cost_ton': calculation['total_ton'],
            'cost_stars': calculation['total_stars'],
            'total_usd': calculation['total_usd']
        },
        post_package_purchase=True
    )
    
    # Show wallet address input
    await wallet_manager.show_wallet_input_prompt(callback_query, state)

@router.callback_query(F.data == "pay_post_stars")
async def handle_post_stars_payment(callback_query: CallbackQuery, state: FSMContext):
    """Handle Stars payment for post package"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    # Get calculation data
    data = await state.get_data()
    calculation = data.get('total_calculation')
    
    if not calculation:
        await callback_query.answer("❌ Payment data not found", show_alert=True)
        return
    
    # Process Stars payment using existing system
    from clean_stars_payment_system import CleanStarsPayment
    from main_bot import bot
    
    stars_system = CleanStarsPayment(bot)
    
    # Create campaign data structure for Stars payment
    campaign_data = {
        'package_name': calculation['package']['name'],
        'posts_total': calculation['package']['posts'],
        'auto_schedule_days': calculation.get('auto_schedule_days', 0),
        'selected_addons': data.get('selected_addons', [])
    }
    
    pricing_data = {
        'cost_stars': calculation['total_stars'],
        'cost_ton': calculation['total_ton'],
        'total_usd': calculation['total_usd']
    }
    
    # Create Stars invoice
    result = await stars_system.create_post_package_invoice(
        user_id=user_id,
        campaign_data=campaign_data,
        pricing_data=pricing_data,
        language=language
    )
    
    if result['success']:
        await callback_query.message.edit_text(
            result['invoice_message'],
            reply_markup=result['invoice_keyboard'],
            parse_mode='Markdown'
        )
        await callback_query.answer("Stars payment invoice created")
    else:
        await callback_query.answer(f"❌ {result['error']}", show_alert=True)

# Back navigation handlers
@router.callback_query(F.data == "back_to_packages")
async def handle_back_to_packages(callback_query: CallbackQuery, state: FSMContext):
    """Handle back to packages"""
    await show_package_selection(callback_query, state)

@router.callback_query(F.data == "buy_more_posts")
async def handle_buy_more_posts(callback_query: CallbackQuery, state: FSMContext):
    """Handle buy more posts"""
    await show_package_selection(callback_query, state)

def setup_post_based_handlers(dp):
    """Setup post-based system handlers"""
    dp.include_router(router)