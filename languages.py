"""
Comprehensive Multi-language support for I3lani Telegram Bot
Supports all bot interactions with complete translation coverage
"""

# Default language for new users
DEFAULT_LANGUAGE = 'en'

LANGUAGES = {
    'en': {
        'code': 'en',
        'name': 'English',
        'flag': '🇺🇸',
        'currency': 'USD',
        'currency_symbol': '$',
        
        # Welcome and start
        'welcome': '⬢━━━━━━━ I3LANI NEURAL NETWORK ━━━━━━━⬢\n▲ Welcome to the Quantum Advertising Matrix ▲',
        'choose_language': '◇━━━ NEURAL INTERFACE LANGUAGE ━━━◇',
        'language_selected': '◈ Neural Language: English 🇺🇸',
        'language_changed': '✅ Language changed to English successfully!',
        
        # Main menu
        'main_menu': '◈━━━ NEURAL PATHWAYS ━━━◈\n◇ Multi-Channel Broadcasting\n◇ Quantum Payment Processing\n◇ Partner Network Mining\n◇ Real-time Analytics\n\n▣ SELECT PROTOCOL ▣',
        'create_ad': '🚀 ▶ LAUNCH NEURAL BROADCAST',
        'my_ads': '📊 ◆ My Quantum Matrix',
        'pricing': '◇ Quantum Pricing', 
        'share_earn': '💎 ◆ Earnings Portal',
        'settings': '⚙️ ◈ Neural Settings',
        'help': '🆘 ◈ Quantum Support',
        'channel_partners': '🔗 ◇ Partner Network',
        'gaming_hub': '🎮 ◇ Neural Gaming Hub',
        'leaderboard': '🏆 ▲ QUANTUM LEADERBOARD ▲',
        
        # Navigation
        'back': '⬅️ Back',
        'back_to_main': '⬅️ Back to Main',
        'back_to_channels': '⬅️ Back to Channels', 
        'back_to_photos': '⬅️ Back to Photos',
        'continue': '➡️ Continue',
        'continue_to_channels': '➡️ Continue to Channels',
        'cancel': '❌ Cancel',
        'confirm': '✅ Confirm',
        'try_again': '🔄 Try Again',
        'contact_support': '📞 Contact Support',
        'refresh': '🔄 Refresh',
        
        # Ad creation
        'send_ad_content': '◇━━━ NEURAL CONTENT UPLOAD ━━━◇\n\nUpload your advertisement:\n• 📝 Text message\n• 📸 Photo with caption\n• 🎥 Video with caption\n\n▣ TRANSMIT DATA ▣',
        'ad_received': '◈ Neural Content Received Successfully! ✅',
        'choose_channels': '◇━━━ QUANTUM CHANNEL MATRIX ━━━◇\n\nSelect broadcasting channels:',
        'select_duration': '◇━━━ TEMPORAL FREQUENCY SELECTOR ━━━◇\n\nChoose campaign duration:',
        'choose_payment': '◇━━━ QUANTUM PAYMENT PROTOCOL ━━━◇\n\nSelect payment method:',
        'upload_photo': '📸 ◇ Upload Neural Image',
        'upload_video': '🎥 ◇ Upload Quantum Video',
        'add_text': '📝 ◇ Add Neural Text',
        'provide_contact': '📞 ◇ Neural Contact Protocol',
        'contact_info_prompt': '◇━━━ CONTACT NEXUS ━━━◇\n\nHow should customers reach you?\n\nExamples:\n• Phone: +966501234567\n• WhatsApp: +966501234567\n• Email: user@email.com\n• Telegram: @username\n\n▣ TRANSMIT CONTACT DATA ▣',
        
        # Channels
        'tech_news': 'Tech News (45K) 🔥',
        'gaming_hub': 'Gaming Hub (32K)',
        'business_tips': 'Business Tips (28K) 🪤',
        
        # Duration
        'duration_1_month': '1 Month',
        'duration_3_months': '3 Months (Save 10%)',
        'duration_6_months': '6 Months (Save 20% + 1 Free) 🔥',
        
        # Payment
        'pay_stars': '⬢ Quantum Stars',
        'pay_ton': '◈ TON Protocol',
        'payment_instructions': '◇━━━ QUANTUM PAYMENT PROTOCOL ━━━◇',
        'memo_format': '◈ Neural Memo: {memo}',
        'payment_sent': '◈ Transaction Confirmed',
        
        # Buttons
        'back': '🔙 Back',
        'continue': '➡️ Continue',
        'cancel': '❌ Cancel',
        'confirm': '✅ Confirm',
        'back_to_main': '◀️ Back to Main',
        'channel_partners': '🤝 Channel Partners',
        'contact_support': '💬 Contact Support',
        'try_again': '🔄 Try Again',
        'main_menu': '🏠 Main Menu',
        'continue_to_channels': '✅ Continue to Channels',
        'back_to_text': '◀️ Back to Text',
        'back_to_photos': '◀️ Back to Photos',
        
        # Referral
        'referral_link': 'Your referral link:',
        'referral_rewards': 'Referral Rewards:\n• 5% friend discount\n• 3 free posting days per referral',
        
        # Dashboard
        'dashboard': 'Dashboard',
        'total_ads': 'Total Ads: {count}',
        'active_ads': 'Active Ads: {count}',
        'total_spent': 'Total Spent: {currency}{amount}',
        
        # Common
        'loading': 'Loading...',
        'error': 'Error occurred',
        'success': 'Success!',
        'processing': 'Processing...',
        'no_channels': '❌ **No channels available**\n\nThe bot needs to be added as an administrator to channels before they can be used for advertising.\n\nPlease contact support to add channels.',
        'support_message': '📞 Need help? Contact /support for assistance!',
        'error_updating_language': 'Error updating language. Please try again.',
        'error_selecting_package': 'Error selecting package. Please try again.',
        'error_selecting_category': 'Error selecting category',
        'error_processing_ad': 'Error processing ad details. Please try again.',
        'error_uploading_photo': 'Error uploading photo. Please try again.',
        'error_processing_request': 'Error processing request. Please try again.',
        'language_updated': 'Language updated successfully!',
        
        # Help
        'help_text': """🤖 **I3lani Bot - Help & Commands**

**Available Commands:**
• /start - Start the bot
• /admin - Admin panel (admins only)  
• /dashboard - My ads dashboard
• /support - Get support
• /help - This message

Questions? Use /support to get help!""",
        'select_channels_text': '📺 **Select Advertising Channels**\n\nChoose which channels to advertise on:',
    },
    
    'ar': {
        'code': 'ar',
        'name': 'العربية',
        'flag': '🇸🇦',
        'currency': 'SAR',
        'currency_symbol': 'ر.س',
        
        # Welcome and start
        'welcome': '⬢━━━━━━━ شبكة I3LANI العصبية ━━━━━━━⬢\n▲ مرحباً بك في مصفوفة الإعلانات الكمية ▲',
        'choose_language': '◇━━━ لغة الواجهة العصبية ━━━◇',
        'language_selected': '◈ اللغة العصبية: العربية 🇸🇦',
        'language_changed': '✅ تم تغيير اللغة إلى العربية بنجاح!',
        
        # Main menu
        'main_menu': '◈━━━ المسارات العصبية ━━━◈\n◇ البث متعدد القنوات\n◇ معالجة الدفع الكمية\n◇ تعدين شبكة الشركاء\n◇ التحليلات الفورية\n\n▣ اختر البروتوكول ▣',
        'create_ad': '🚀 ▶ إطلاق البث العصبي',
        'my_ads': '📊 ◆ مصفوفتي الكمية',
        'pricing': '◇ التسعير الكمي', 
        'share_earn': '💎 ◆ بوابة الأرباح',
        'settings': '⚙️ ◈ الإعدادات العصبية',
        'help': '🆘 ◈ الدعم الكمي',
        'channel_partners': '🔗 ◇ شبكة الشركاء',
        'gaming_hub': '🎮 ◇ مركز الألعاب العصبية',
        'leaderboard': '🏆 ▲ لوحة المتصدرين الكمية ▲',
        
        # Navigation
        'back': '⬅️ رجوع',
        'back_to_main': '⬅️ العودة للرئيسية',
        'back_to_channels': '⬅️ العودة للقنوات',
        'back_to_photos': '⬅️ العودة للصور',
        'continue': '➡️ متابعة',
        'continue_to_channels': '➡️ متابعة للقنوات',
        'cancel': '❌ إلغاء',
        'confirm': '✅ تأكيد',
        'try_again': '🔄 حاول مرة أخرى',
        'contact_support': '📞 اتصل بالدعم',
        'refresh': '🔄 تحديث',
        
        # Ad creation
        'send_ad_content': '◇━━━ تحميل المحتوى العصبي ━━━◇\n\nارفع إعلانك:\n• 📝 رسالة نصية\n• 📸 صورة مع وصف\n• 🎥 فيديو مع وصف\n\n▣ إرسال البيانات ▣',
        'ad_received': '◈ تم استلام المحتوى العصبي بنجاح! ✅',
        'choose_channels': '◇━━━ مصفوفة القنوات الكمية ━━━◇\n\nاختر قنوات البث:',
        'select_duration': '◇━━━ محدد التردد الزمني ━━━◇\n\nاختر مدة الحملة:',
        'choose_payment': '◇━━━ بروتوكول الدفع الكمي ━━━◇\n\nاختر طريقة الدفع:',
        'upload_photo': '📸 ◇ رفع صورة عصبية',
        'upload_video': '🎥 ◇ رفع فيديو كمي',
        'add_text': '📝 ◇ إضافة نص عصبي',
        'provide_contact': '📞 ◇ بروتوكول الاتصال العصبي',
        'contact_info_prompt': '◇━━━ شبكة الاتصال ━━━◇\n\nكيف يمكن للعملاء التواصل معك؟\n\nأمثلة:\n• هاتف: +966501234567\n• واتساب: +966501234567\n• بريد: user@email.com\n• تليجرام: @username\n\n▣ إرسال بيانات الاتصال ▣',
        
        # Categories
        'vehicles': '🚗 المركبات',
        'real_estate': '🏠 العقارات',
        'electronics': '📱 الإلكترونيات',
        'jobs': '💼 الوظائف',
        'services': '🛠️ الخدمات',
        'fashion': '👗 الأزياء',
        'select_category': 'اختر الفئة:',
        'select_subcategory': 'اختر الفئة الفرعية:',
        
        # Channels
        'tech_news': 'أخبار التكنولوجيا (45 ألف) 🔥',
        'gaming_hub': 'مركز الألعاب (32 ألف)',
        'business_tips': 'نصائح الأعمال (28 ألف) 🪤',
        
        # Duration
        'duration_1_month': 'شهر واحد',
        'duration_3_months': '3 أشهر (وفر 10%)',
        'duration_6_months': '6 أشهر (وفر 20% + شهر مجاني) 🔥',
        
        # Payment
        'pay_stars': '⭐ نجوم تيليجرام',
        'pay_ton': '💎 عملة TON',
        'payment_instructions': 'تعليمات الدفع:',
        'memo_format': 'المذكرة: {memo}',
        'payment_sent': 'تم إرسال الدفع ✅',
        
        # Buttons
        'back': '🔙 رجوع',
        'continue': '➡️ متابعة',
        'cancel': '❌ إلغاء',
        'confirm': '✅ تأكيد',
        
        # Referral
        'referral_link': 'رابط الإحالة الخاص بك:',
        'referral_rewards': 'مكافآت الإحالة:\n• خصم 5% للأصدقاء\n• 3 أيام نشر مجانية لكل إحالة',
        
        # Dashboard
        'dashboard': 'لوحة التحكم',
        'total_ads': 'إجمالي الإعلانات: {count}',
        'active_ads': 'الإعلانات النشطة: {count}',
        'total_spent': 'إجمالي المنفق: {currency}{amount}',
        
        # Common
        'loading': 'جاري التحميل...',
        'error': 'حدث خطأ',
        'success': 'نجح!',
        'processing': 'جاري المعالجة...',
        'no_channels': '❌ **لا توجد قنوات متاحة**\n\nيجب إضافة البوت كمشرف في القنوات قبل أن يتمكن من استخدامها للإعلانات.\n\nيرجى الاتصال بالدعم لإضافة القنوات.',
        'support_message': '📞 تحتاج مساعدة؟ تواصل مع /support للحصول على المساعدة!',
        'error_updating_language': 'خطأ في تحديث اللغة. يرجى المحاولة مرة أخرى.',
        'error_selecting_package': 'خطأ في اختيار الحزمة. يرجى المحاولة مرة أخرى.',
        'error_selecting_category': 'خطأ في اختيار الفئة',
        'error_processing_ad': 'خطأ في معالجة تفاصيل الإعلان. يرجى المحاولة مرة أخرى.',
        'error_uploading_photo': 'خطأ في رفع الصورة. يرجى المحاولة مرة أخرى.',
        'error_processing_request': 'خطأ في معالجة الطلب. يرجى المحاولة مرة أخرى.',
        'language_updated': 'تم تحديث اللغة بنجاح!',
        
        # Buttons
        'back_to_main': '◀️ العودة للقائمة الرئيسية',
        'channel_partners': '🤝 شراكة القنوات',
        'contact_support': '💬 تواصل مع الدعم',
        'try_again': '🔄 حاول مرة أخرى',
        'main_menu': '🏠 القائمة الرئيسية',
        'continue_to_channels': '✅ متابعة إلى القنوات',
        'back_to_text': '◀️ العودة للنص',
        'back_to_photos': '◀️ العودة للصور',
        'back': '🔙 رجوع',
        'continue': '➡️ متابعة',
        'cancel': '❌ إلغاء',
        'confirm': '✅ تأكيد',
        
        # Help
        'help_text': """🤖 **بوت إعلاني - المساعدة والأوامر**

**الأوامر المتاحة:**
• /start - بدء تشغيل البوت
• /admin - لوحة الإدارة (للإداريين فقط)
• /dashboard - لوحة تحكم إعلاناتي
• /support - الحصول على الدعم
• /help - هذه الرسالة

أسئلة؟ استخدم /support للحصول على المساعدة!""",
        'select_channels_text': '📺 **اختر قنوات الإعلان**\n\nاختر القنوات التي تريد الإعلان عليها:',
    },
    
    'ru': {
        'code': 'ru',
        'name': 'Русский',
        'flag': '🇷🇺',
        'currency': 'RUB',
        'currency_symbol': '₽',
        
        # Welcome and start
        'welcome': '⬢━━━━━━━ I3LANI НЕЙРОСЕТЬ ━━━━━━━⬢\n▲ Добро пожаловать в Квантовую Рекламную Матрицу ▲',
        'choose_language': '◇━━━ ЯЗЫК НЕЙРОИНТЕРФЕЙСА ━━━◇',
        'language_selected': '◈ Нейроязык: Русский 🇷🇺',
        'language_changed': '✅ Язык успешно изменен на русский!',
        
        # Main menu
        'main_menu': '◈━━━ НЕЙРОПУТИ ━━━◈\n◇ Многоканальное вещание\n◇ Квантовая обработка платежей\n◇ Майнинг партнерской сети\n◇ Аналитика в реальном времени\n\n▣ ВЫБЕРИТЕ ПРОТОКОЛ ▣',
        'create_ad': '🚀 ▶ ЗАПУСК НЕЙРОВЕЩАНИЯ',
        'my_ads': '📊 ◆ Моя Квантовая Матрица',
        'pricing': '◇ Квантовые Цены', 
        'share_earn': '💎 ◆ Портал Заработка',
        'settings': '⚙️ ◈ Нейронастройки',
        'help': '🆘 ◈ Квантовая Поддержка',
        'channel_partners': '🔗 ◇ Партнерская Сеть',
        'gaming_hub': '🎮 ◇ Нейроигровой Центр',
        'leaderboard': '🏆 ▲ КВАНТОВАЯ ДОСКА ЛИДЕРОВ ▲',
        
        # Navigation
        'back': '⬅️ Назад',
        'back_to_main': '⬅️ В главное меню',
        'back_to_channels': '⬅️ К каналам',
        'back_to_photos': '⬅️ К фото',
        'continue': '➡️ Продолжить',
        'continue_to_channels': '➡️ К каналам',
        'cancel': '❌ Отмена',
        'confirm': '✅ Подтвердить',
        'try_again': '🔄 Попробовать снова',
        'contact_support': '📞 Связаться с поддержкой',
        'refresh': '🔄 Обновить',
        
        # Ad creation
        'send_ad_content': '◇━━━ ЗАГРУЗКА НЕЙРОКОНТЕНТА ━━━◇\n\nЗагрузите вашу рекламу:\n• 📝 Текстовое сообщение\n• 📸 Фото с описанием\n• 🎥 Видео с описанием\n\n▣ ПЕРЕДАТЬ ДАННЫЕ ▣',
        'ad_received': '◈ Нейроконтент успешно получен! ✅',
        'choose_channels': '◇━━━ КВАНТОВАЯ МАТРИЦА КАНАЛОВ ━━━◇\n\nВыберите каналы для трансляции:',
        'select_duration': '◇━━━ СЕЛЕКТОР ВРЕМЕННОЙ ЧАСТОТЫ ━━━◇\n\nВыберите продолжительность кампании:',
        'choose_payment': '◇━━━ КВАНТОВЫЙ ПРОТОКОЛ ОПЛАТЫ ━━━◇\n\nВыберите способ оплаты:',
        'upload_photo': '📸 ◇ Загрузить Нейроизображение',
        'upload_video': '🎥 ◇ Загрузить Квантовое Видео',
        'add_text': '📝 ◇ Добавить Нейротекст',
        'provide_contact': '📞 ◇ Протокол Нейроконтактов',
        'contact_info_prompt': '◇━━━ КОНТАКТНАЯ СЕТЬ ━━━◇\n\nКак клиенты могут связаться с вами?\n\nПримеры:\n• Телефон: +966501234567\n• WhatsApp: +966501234567\n• Email: user@email.com\n• Telegram: @username\n\n▣ ПЕРЕДАТЬ КОНТАКТНЫЕ ДАННЫЕ ▣',
        
        # Channels
        'tech_news': 'Технические новости (45K) 🔥',
        'gaming_hub': 'Игровой центр (32K)',
        'business_tips': 'Бизнес советы (28K) 🪤',
        
        # Duration
        'duration_1_month': '1 месяц',
        'duration_3_months': '3 месяца (скидка 10%)',
        'duration_6_months': '6 месяцев (скидка 20% + 1 бесплатный) 🔥',
        
        # Payment
        'pay_stars': '⭐ Telegram Stars',
        'pay_ton': '💎 TON Crypto',
        'payment_instructions': 'Инструкции по оплате:',
        'memo_format': 'Мемо: {memo}',
        'payment_sent': 'Платеж отправлен ✅',
        
        # Buttons
        'back': '🔙 Назад',
        'continue': '➡️ Продолжить',
        'cancel': '❌ Отмена',
        'confirm': '✅ Подтвердить',
        
        # Referral
        'referral_link': 'Ваша реферальная ссылка:',
        'referral_rewards': 'Реферальные награды:\n• 5% скидка для друзей\n• 3 бесплатных дня публикации за реферала',
        
        # Dashboard
        'dashboard': 'Панель управления',
        'total_ads': 'Всего объявлений: {count}',
        'active_ads': 'Активных объявлений: {count}',
        'total_spent': 'Всего потрачено: {currency}{amount}',
        
        # Common
        'loading': 'Загрузка...',
        'error': 'Произошла ошибка',
        'success': 'Успешно!',
        'processing': 'Обработка...',
        'no_channels': '❌ **Нет доступных каналов**\n\nБот должен быть добавлен как администратор в каналы, прежде чем их можно будет использовать для рекламы.\n\nОбратитесь в службу поддержки для добавления каналов.',
        'support_message': '📞 Нужна помощь? Обратитесь к /support за помощью!',
        'error_updating_language': 'Ошибка обновления языка. Пожалуйста, попробуйте снова.',
        'error_selecting_package': 'Ошибка выбора пакета. Пожалуйста, попробуйте снова.',
        'error_selecting_category': 'Ошибка выбора категории',
        'error_processing_ad': 'Ошибка обработки деталей объявления. Пожалуйста, попробуйте снова.',
        'error_uploading_photo': 'Ошибка загрузки фото. Пожалуйста, попробуйте снова.',
        'error_processing_request': 'Ошибка обработки запроса. Пожалуйста, попробуйте снова.',
        'language_updated': 'Язык успешно обновлен!',
        
        # Buttons
        'back_to_main': '◀️ В главное меню',
        'channel_partners': '🤝 Партнеры каналов',
        'contact_support': '💬 Связаться с поддержкой',
        'try_again': '🔄 Попробовать снова',
        'main_menu': '🏠 Главное меню',
        'continue_to_channels': '✅ Перейти к каналам',
        'back_to_text': '◀️ Назад к тексту',
        'back_to_photos': '◀️ Назад к фото',
        'back': '🔙 Назад',
        'continue': '➡️ Продолжить',
        'cancel': '❌ Отмена',
        'confirm': '✅ Подтвердить',
        
        # Help
        'help_text': """🤖 **I3lani Bot - Справка и команды**

**Доступные команды:**
• /start - Запустить бота
• /admin - Панель администратора (только для администраторов)
• /dashboard - Панель управления моими объявлениями
• /support - Получить поддержку
• /help - Это сообщение

Вопросы? Используйте /support для получения помощи!""",
        'select_channels_text': '📺 **Выберите рекламные каналы**\n\nВыберите каналы для размещения рекламы:',
        
        # Troubleshooting System
        'report_issue_help': 'Пожалуйста, опишите вашу проблему:\n/report_issue Описание вашей проблемы здесь',
        'issue_reported': '✅ Ваша проблема зарегистрирована. Команда поддержки рассмотрит её в ближайшее время.'
    }
}


def get_text(language_code: str, key: str, default: str = None, **kwargs) -> str:
    """
    Get localized text with comprehensive fallback support
    
    Args:
        language_code: The language code (en, ar, ru)
        key: The translation key
        default: Default text if key not found
        **kwargs: Format arguments for the text
    
    Returns:
        Localized text string
    """
    # Get the language dictionary
    lang = LANGUAGES.get(language_code, LANGUAGES[DEFAULT_LANGUAGE])
    
    # Try to get the text
    text = lang.get(key)
    
    # Fallback chain: requested lang -> English -> default -> key
    if text is None:
        text = LANGUAGES[DEFAULT_LANGUAGE].get(key)
    if text is None and default:
        text = default
    if text is None:
        text = key  # Last resort: return the key itself
    
    # Apply formatting if kwargs provided
    if kwargs and text:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return unformatted text
            return text
    
    return text

def get_user_language_fallback(user_id: int = None) -> str:
    """Get user language with fallback to default"""
    # This can be called from handlers that have access to user_id
    return DEFAULT_LANGUAGE  # For now, always return default

def is_rtl_language(language_code: str) -> bool:
    """Check if language is right-to-left"""
    rtl_languages = ['ar', 'he', 'fa', 'ur']
    return language_code in rtl_languages

def get_language_info(language_code: str) -> dict:
    """Get complete language information"""
    lang = LANGUAGES.get(language_code, LANGUAGES[DEFAULT_LANGUAGE])
    return {
        'code': lang['code'],
        'name': lang['name'],
        'flag': lang['flag'],
        'currency': lang['currency'],
        'currency_symbol': lang['currency_symbol'],
        'is_rtl': is_rtl_language(language_code)
    }


def get_currency_info(language_code: str) -> dict:
    """Get currency information for language"""
    lang = LANGUAGES.get(language_code, LANGUAGES['en'])
    return {
        'currency': lang['currency'],
        'symbol': lang['currency_symbol']
    }