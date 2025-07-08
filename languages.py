"""
Multi-language support for I3lani Telegram Bot
"""

LANGUAGES = {
    'en': {
        'code': 'en',
        'name': 'English',
        'flag': '🇺🇸',
        'currency': 'USD',
        'currency_symbol': '$',
        
        # Welcome and start
        'welcome': 'Welcome to I3lani Bot! 🚀\n\nYour premium Telegram advertising platform',
        'choose_language': 'Choose your language:',
        'language_selected': 'Language selected: English 🇺🇸',
        
        # Main menu
        'main_menu': '🏠 Main Menu',
        'create_ad': '📢 Create Ad',
        'my_ads': '📊 My Ads',
        'pricing': '💰 Pricing',
        'share_earn': '🎁 Share & Earn',
        'settings': '⚙️ Settings',
        'help': '❓ Help',
        
        # Ad creation
        'send_ad_content': 'Send your ad content:\n• Text message\n• Photo with caption\n• Video with caption',
        'ad_received': 'Ad content received! ✅',
        'choose_channels': 'Choose channels for your ad:',
        'select_duration': 'Select duration:',
        'choose_payment': 'Choose payment method:',
        
        # Channels
        'tech_news': 'Tech News (45K) 🔥',
        'gaming_hub': 'Gaming Hub (32K)',
        'business_tips': 'Business Tips (28K) 🪤',
        
        # Duration
        'duration_1_month': '1 Month',
        'duration_3_months': '3 Months (Save 10%)',
        'duration_6_months': '6 Months (Save 20% + 1 Free) 🔥',
        
        # Payment
        'pay_stars': '⭐ Telegram Stars',
        'pay_ton': '💎 TON Crypto',
        'payment_instructions': 'Payment Instructions:',
        'memo_format': 'Memo: {memo}',
        'payment_sent': 'Payment Sent ✅',
        
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
        'welcome': 'مرحباً بك في بوت إعلاني! 🚀\n\nمنصة إعلانات تيليجرام المميزة',
        'choose_language': 'اختر لغتك:',
        'language_selected': 'تم اختيار اللغة: العربية 🇸🇦',
        
        # Main menu
        'main_menu': '🏠 القائمة الرئيسية',
        'create_ad': '📢 إنشاء إعلان',
        'my_ads': '📊 إعلاناتي',
        'pricing': '💰 الأسعار',
        'share_earn': '🎁 شارك واكسب',
        'settings': '⚙️ الإعدادات',
        'help': '❓ المساعدة',
        
        # Ad creation
        'send_ad_content': 'أرسل محتوى الإعلان:\n• رسالة نصية\n• صورة مع وصف\n• فيديو مع وصف',
        'ad_received': 'تم استلام محتوى الإعلان! ✅',
        'choose_channels': 'اختر القنوات لإعلانك:',
        'select_duration': 'اختر المدة:',
        'choose_payment': 'اختر طريقة الدفع:',
        
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
        'welcome': 'Добро пожаловать в I3lani Bot! 🚀\n\nВаша премиальная платформа рекламы в Telegram',
        'choose_language': 'Выберите язык:',
        'language_selected': 'Язык выбран: Русский 🇷🇺',
        
        # Main menu
        'main_menu': '🏠 Главное меню',
        'create_ad': '📢 Создать рекламу',
        'my_ads': '📊 Мои объявления',
        'pricing': '💰 Цены',
        'share_earn': '🎁 Поделиться и заработать',
        'settings': '⚙️ Настройки',
        'help': '❓ Помощь',
        
        # Ad creation
        'send_ad_content': 'Отправьте содержание рекламы:\n• Текстовое сообщение\n• Фото с описанием\n• Видео с описанием',
        'ad_received': 'Содержание рекламы получено! ✅',
        'choose_channels': 'Выберите каналы для рекламы:',
        'select_duration': 'Выберите продолжительность:',
        'choose_payment': 'Выберите способ оплаты:',
        
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
    }
}


def get_text(language_code: str, key: str, **kwargs) -> str:
    """Get localized text"""
    lang = LANGUAGES.get(language_code, LANGUAGES['en'])
    text = lang.get(key, LANGUAGES['en'].get(key, key))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text


def get_currency_info(language_code: str) -> dict:
    """Get currency information for language"""
    lang = LANGUAGES.get(language_code, LANGUAGES['en'])
    return {
        'currency': lang['currency'],
        'symbol': lang['currency_symbol']
    }