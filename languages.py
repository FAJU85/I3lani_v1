"""
Multi-language support for Telegram Ad Bot
"""

# Language configurations
LANGUAGES = {
    'en': {
        'name': 'English',
        'flag': '🇺🇸',
        'welcome_message': """
🎯 **Welcome to the Ad Bot!**

Send me your advertisement content and I'll help you promote it on our channel.

📝 **What you can send:**
• Text messages
• Photos with captions
• Videos with captions

💰 **We offer 4 advertising packages with TON payments**

Ready to start? Just send me your ad content!
""",
        'choose_language': "🌐 Choose your language:",
        'language_selected': "✅ Language set to English",
        'ad_content_received': "✅ **Ad content received!**\n\n📦 **Choose your advertising package:**",
        'package_details': """
📦 **{name} Package**

💰 **Price:** {price} TON
⏱ **Duration:** {duration} days
📅 **Repost every:** {frequency} day(s)
📊 **Total posts:** {total_posts}

Choose this package to proceed with payment.
""",
        'payment_instructions': """
💳 **Payment Instructions:**

1. Send **{price} TON** to this wallet address:
`{wallet_address}`

2. **Important:** Include this memo in your transfer:
`{memo}`

3. After sending payment, click "I've Paid" button below
4. Wait for admin approval (usually within 30 minutes)
5. Your ad will be posted automatically!

⚠️ **Important:** 
- Send exact amount: {price} TON
- Include the memo: {memo}
- The memo helps us identify your payment
""",
        'payment_received': """
✅ **Payment notification received!**

⏳ Your payment is being verified by our admin team.
You will be notified once it's approved.

📊 **Ad Details:**
📦 Package: {package_name}
💰 Price: {price} TON
📅 Posts: {total_posts}
""",
        'payment_approved': """
✅ **Payment Approved!**

Your ad has been approved and will be posted shortly.
📊 **Total posts scheduled:** {total_posts}
""",
        'payment_rejected': """
❌ **Payment Rejected**

Your payment could not be verified. Please contact support if you believe this is an error.
""",
        'campaign_started': """
🚀 **Campaign Started!**

Your {package_name} campaign is now active!

📊 **Campaign Details:**
- Duration: {duration_days} days
- Total posts: {total_posts}
- Repost every: {frequency_days} day(s)
- End date: {end_date}

Your first ad has been posted to the channel! 🎯
""",
        'ad_posted_notification': """
📢 **Ad Posted Successfully!**

Your advertisement has been posted to the channel.

📊 **Progress:**
- Post #{post_number} of {total_posts}
- Next post: {next_post_date}

{remaining_posts_text}
""",
        'campaign_completed': """
✅ **Campaign Completed!**

Your {package_name} campaign has finished successfully!

📊 **Final Statistics:**
- Total posts: {posts_count}
- Campaign duration: {duration_days} days
- Channel: @{channel_name}

🎯 **Thank you for using our service!**

Want to advertise again? Send /start to create a new campaign.
""",
        'payment_cancelled': """
❌ **Payment cancelled**

Your ad has been cancelled. Send /start to create a new ad.
""",
        'invalid_content': "❌ Please send text, photo, or video content only.",
        'no_ad_found': "❌ No ad found. Please start over.",
        'not_authorized': "❌ Not authorized",
        'ad_not_found': "❌ Ad not found",
        'buttons': {
            'ive_paid': "✅ I've Paid",
            'cancel': "❌ Cancel",
            'approve': "✅ Approve",
            'reject': "❌ Reject",
            'choose_package': "💳 Choose This Package",
            'back_to_packages': "⬅️ Back to Packages"
        },
        'admin_notification': """
🔔 **New Payment Pending Approval**

👤 **User:** @{username} (ID: {user_id})
📦 **Package:** {package_name}
💰 **Price:** {price} TON
🕒 **Submitted:** {created_at}
🔖 **Payment Memo:** `{memo}`

**Ad Content:**
{content}

💳 **Wallet:** `{wallet_address}`
🔍 **Search memo:** `{memo}` on tonviewer.com

Please verify payment and approve/reject below.
""",
        'admin_approved': """
✅ **Ad Approved** by @{admin_username}

Ad ID: {ad_id}
User: @{username}
Package: {package_name}
Approved at: {approved_at}
""",
        'admin_rejected': """
❌ **Ad Rejected** by @{admin_username}

Ad ID: {ad_id}
User: @{username}
Package: {package_name}
Rejected at: {rejected_at}
""",
        'bot_online': "🤖 Ad Bot is now online!",
        'stats_title': """
📊 **Bot Statistics**

📈 **Total Ads:** {total_ads}
⏳ **Pending Payment:** {pending_payment}
✅ **Active:** {active}
✅ **Completed:** {completed}
❌ **Rejected:** {rejected}

💰 **Revenue:** {revenue} TON
""",
        'no_active_campaigns': "📊 **No active campaigns**",
        'active_campaigns': "📊 **Active Campaigns: {count}**\n\n"
    },
    'ar': {
        'name': 'العربية',
        'flag': '🇸🇦',
        'welcome_message': """
🎯 **مرحباً بك في بوت الإعلانات!**

أرسل لي محتوى إعلانك وسأساعدك في الترويج له على قناتنا.

📝 **ما يمكنك إرساله:**
• رسائل نصية
• صور مع تعليقات
• فيديوهات مع تعليقات

💰 **نوفر 4 باقات إعلانية بدفع TON**

مستعد للبدء؟ فقط أرسل لي محتوى إعلانك!
""",
        'choose_language': "🌐 اختر لغتك:",
        'language_selected': "✅ تم تعيين اللغة إلى العربية",
        'ad_content_received': "✅ **تم استلام محتوى الإعلان!**\n\n📦 **اختر باقة الإعلان:**",
        'package_details': """
📦 **باقة {name}**

💰 **السعر:** {price} TON
⏱ **المدة:** {duration} يوم
📅 **إعادة النشر كل:** {frequency} يوم
📊 **إجمالي المنشورات:** {total_posts}

اختر هذه الباقة للمتابعة مع الدفع.
""",
        'payment_instructions': """
💳 **تعليمات الدفع:**

1. أرسل **{price} TON** إلى هذا العنوان:
`{wallet_address}`

2. بعد إرسال الدفع، انقر على الزر أدناه
3. انتظر موافقة المشرف
4. سيتم نشر إعلانك تلقائياً!

⚠️ **مهم:** تأكد من إرسال المبلغ الصحيح
""",
        'payment_received': """
✅ **تم استلام إشعار الدفع!**

⏳ يتم التحقق من دفعتك من قبل فريق المشرفين.
ستتلقى إشعاراً عند الموافقة.

📊 **تفاصيل الإعلان:**
📦 الباقة: {package_name}
💰 السعر: {price} TON
📅 المنشورات: {total_posts}
""",
        'payment_approved': """
✅ **تمت الموافقة على الدفع!**

تمت الموافقة على إعلانك وسيتم نشره قريباً.
📊 **إجمالي المنشورات المجدولة:** {total_posts}
""",
        'payment_rejected': """
❌ **تم رفض الدفع**

لم يتم التحقق من دفعتك. يرجى الاتصال بالدعم إذا كنت تعتقد أن هذا خطأ.
""",
        'campaign_completed': """
✅ **اكتملت الحملة!**

انتهت حملة {package_name} الخاصة بك.
📊 **إجمالي المنشورات:** {posts_count}
🎯 **شكراً لاستخدام خدمتنا!**
""",
        'payment_cancelled': """
❌ **تم إلغاء الدفع**

تم إلغاء إعلانك. أرسل /start لإنشاء إعلان جديد.
""",
        'invalid_content': "❌ يرجى إرسال نص أو صورة أو فيديو فقط.",
        'no_ad_found': "❌ لم يتم العثور على إعلان. يرجى البدء مرة أخرى.",
        'not_authorized': "❌ غير مخول",
        'ad_not_found': "❌ لم يتم العثور على الإعلان",
        'buttons': {
            'ive_paid': "✅ لقد دفعت",
            'cancel': "❌ إلغاء",
            'approve': "✅ موافقة",
            'reject': "❌ رفض",
            'choose_package': "💳 اختر هذه الباقة",
            'back_to_packages': "⬅️ العودة للباقات"
        },
        'admin_notification': """
🔔 **دفع جديد في انتظار الموافقة**

👤 **المستخدم:** @{username} (ID: {user_id})
📦 **الباقة:** {package_name}
💰 **السعر:** {price} TON
🕒 **تم الإرسال:** {created_at}

**محتوى الإعلان:**
{content}

💳 **المحفظة:** `{wallet_address}`

يرجى التحقق من الدفع على tonviewer.com والموافقة/الرفض أدناه.
""",
        'admin_approved': """
✅ **تمت الموافقة على الإعلان** من قبل @{admin_username}

معرف الإعلان: {ad_id}
المستخدم: @{username}
الباقة: {package_name}
تمت الموافقة في: {approved_at}
""",
        'admin_rejected': """
❌ **تم رفض الإعلان** من قبل @{admin_username}

معرف الإعلان: {ad_id}
المستخدم: @{username}
الباقة: {package_name}
تم الرفض في: {rejected_at}
""",
        'bot_online': "🤖 بوت الإعلانات متصل الآن!",
        'stats_title': """
📊 **إحصائيات البوت**

📈 **إجمالي الإعلانات:** {total_ads}
⏳ **في انتظار الدفع:** {pending_payment}
✅ **نشط:** {active}
✅ **مكتمل:** {completed}
❌ **مرفوض:** {rejected}

💰 **الإيرادات:** {revenue} TON
""",
        'no_active_campaigns': "📊 **لا توجد حملات نشطة**",
        'active_campaigns': "📊 **الحملات النشطة: {count}**\n\n"
    },
    'ru': {
        'name': 'Русский',
        'flag': '🇷🇺',
        'welcome_message': """
🎯 **Добро пожаловать в рекламный бот!**

Отправьте мне содержимое вашей рекламы, и я помогу вам продвинуть её на нашем канале.

📝 **Что вы можете отправить:**
• Текстовые сообщения
• Фотографии с подписями
• Видео с подписями

💰 **Мы предлагаем 4 рекламных пакета с оплатой TON**

Готовы начать? Просто отправьте мне содержимое вашей рекламы!
""",
        'choose_language': "🌐 Выберите язык:",
        'language_selected': "✅ Язык установлен на русский",
        'ad_content_received': "✅ **Содержимое рекламы получено!**\n\n📦 **Выберите рекламный пакет:**",
        'package_details': """
📦 **Пакет {name}**

💰 **Цена:** {price} TON
⏱ **Длительность:** {duration} дней
📅 **Репост каждые:** {frequency} день(дня)
📊 **Всего постов:** {total_posts}

Выберите этот пакет для продолжения оплаты.
""",
        'payment_instructions': """
💳 **Инструкции по оплате:**

1. Отправьте **{price} TON** на этот адрес кошелька:
`{wallet_address}`

2. После отправки платежа нажмите кнопку ниже
3. Дождитесь одобрения администратора
4. Ваша реклама будет опубликована автоматически!

⚠️ **Важно:** Убедитесь, что отправили точную сумму
""",
        'payment_received': """
✅ **Уведомление об оплате получено!**

⏳ Ваш платеж проверяется командой администраторов.
Вы получите уведомление после одобрения.

📊 **Детали рекламы:**
📦 Пакет: {package_name}
💰 Цена: {price} TON
📅 Посты: {total_posts}
""",
        'payment_approved': """
✅ **Платеж одобрен!**

Ваша реклама одобрена и вскоре будет опубликована.
📊 **Всего запланированных постов:** {total_posts}
""",
        'payment_rejected': """
❌ **Платеж отклонен**

Ваш платеж не может быть подтвержден. Обратитесь в поддержку, если считаете, что это ошибка.
""",
        'campaign_completed': """
✅ **Кампания завершена!**

Ваша кампания {package_name} завершена.
📊 **Всего постов:** {posts_count}
🎯 **Спасибо за использование нашего сервиса!**
""",
        'payment_cancelled': """
❌ **Платеж отменен**

Ваша реклама отменена. Отправьте /start для создания новой рекламы.
""",
        'invalid_content': "❌ Пожалуйста, отправьте только текст, фото или видео.",
        'no_ad_found': "❌ Реклама не найдена. Пожалуйста, начните заново.",
        'not_authorized': "❌ Не авторизован",
        'ad_not_found': "❌ Реклама не найдена",
        'buttons': {
            'ive_paid': "✅ Я оплатил",
            'cancel': "❌ Отмена",
            'approve': "✅ Одобрить",
            'reject': "❌ Отклонить",
            'choose_package': "💳 Выбрать пакет",
            'back_to_packages': "⬅️ Назад к пакетам"
        },
        'admin_notification': """
🔔 **Новый платеж ожидает одобрения**

👤 **Пользователь:** @{username} (ID: {user_id})
📦 **Пакет:** {package_name}
💰 **Цена:** {price} TON
🕒 **Отправлено:** {created_at}

**Содержимое рекламы:**
{content}

💳 **Кошелек:** `{wallet_address}`

Пожалуйста, проверьте платеж на tonviewer.com и одобрите/отклоните ниже.
""",
        'admin_approved': """
✅ **Реклама одобрена** пользователем @{admin_username}

ID рекламы: {ad_id}
Пользователь: @{username}
Пакет: {package_name}
Одобрено в: {approved_at}
""",
        'admin_rejected': """
❌ **Реклама отклонена** пользователем @{admin_username}

ID рекламы: {ad_id}
Пользователь: @{username}
Пакет: {package_name}
Отклонено в: {rejected_at}
""",
        'bot_online': "🤖 Рекламный бот сейчас онлайн!",
        'stats_title': """
📊 **Статистика бота**

📈 **Всего реклам:** {total_ads}
⏳ **Ожидает оплаты:** {pending_payment}
✅ **Активные:** {active}
✅ **Завершенные:** {completed}
❌ **Отклоненные:** {rejected}

💰 **Доход:** {revenue} TON
""",
        'no_active_campaigns': "📊 **Нет активных кампаний**",
        'active_campaigns': "📊 **Активные кампании: {count}**\n\n"
    }
}

# Default language
DEFAULT_LANGUAGE = 'en'

# User language storage (in production, use database)
user_languages = {}

def get_user_language(user_id: int) -> str:
    """Get user's preferred language"""
    return user_languages.get(user_id, DEFAULT_LANGUAGE)

def set_user_language(user_id: int, language: str) -> None:
    """Set user's preferred language"""
    if language in LANGUAGES:
        user_languages[user_id] = language

def get_text(user_id: int, key: str, **kwargs) -> str:
    """Get localized text for user"""
    language = get_user_language(user_id)
    
    # Navigate through nested keys (e.g., 'buttons.ive_paid')
    text_data = LANGUAGES[language]
    keys = key.split('.')
    
    for k in keys:
        if isinstance(text_data, dict) and k in text_data:
            text_data = text_data[k]
        else:
            # Fallback to English if key not found
            text_data = LANGUAGES[DEFAULT_LANGUAGE]
            for k in keys:
                if isinstance(text_data, dict) and k in text_data:
                    text_data = text_data[k]
                else:
                    return f"Missing translation: {key}"
            break
    
    # Format string with provided arguments
    if isinstance(text_data, str) and kwargs:
        try:
            return text_data.format(**kwargs)
        except KeyError:
            return text_data
    
    return text_data

def get_language_keyboard():
    """Create language selection keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for lang_code, lang_info in LANGUAGES.items():
        button_text = f"{lang_info['flag']} {lang_info['name']}"
        keyboard.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"lang_{lang_code}"
            )
        )
    
    return keyboard