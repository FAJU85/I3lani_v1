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
        'welcome': '👋 Welcome to I3lani Bot\n\nYour trusted platform for advertising across Telegram channels.',
        'choose_language': '🌐 Please select your language:',
        'language_selected': '✅ Language: English 🇺🇸',
        'language_changed': '✅ Language changed to English successfully!',
        
        # Main menu
        'main_menu': '📱 I3lani Bot - Main Menu\n\nManage your advertising campaigns easily and effectively.\n\nPlease select an option:',
        'create_ad': '➕ Create New Ad',
        'my_ads': '📄 My Ads',
        'pricing': '💵 Pricing', 
        'share_earn': '💎 Share & Earn Portal',
        'settings': '⚙️ Settings',
        'help': '❓ Help',
        'channel_partners': '🤝 Partner Network',
        'gaming_hub': '🎮 Rewards & Games',
        'leaderboard': '🏆 Leaderboard',
        
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
        'send_ad_content': '◇━━ NEURAL UPLOAD ━━◇\n\nUpload your advertisement:\n• 📝 Text message\n• 📸 Photo with caption\n• 🎥 Video with caption\n\n▣ TRANSMIT DATA ▣',
        'ad_received': '◈ Neural Content Received! ✅',
        'choose_channels': '◇━━ QUANTUM CHANNELS ━━◇\n\nSelect broadcasting channels:',
        'select_duration': '◇━━ FREQUENCY SELECTOR ━━◇\n\nChoose campaign duration:',
        'choose_payment': '◇━━ PAYMENT PROTOCOL ━━◇\n\nSelect payment method:',
        'upload_photo': '📸 ◇ Upload Neural Image',
        'upload_video': '🎥 ◇ Upload Quantum Video',
        'add_text': '📝 ◇ Add Neural Text',
        'provide_contact': '📞 ◇ Neural Contact Protocol',
        'contact_info_prompt': '◇━━ CONTACT NEXUS ━━◇\n\nHow should customers reach you?\n\nExamples:\n• Phone: +966501234567\n• WhatsApp: +966501234567\n• Email: user@email.com\n• Telegram: @username\n\n▣ TRANSMIT DATA ▣',
        
        # Modern ad creation - Step 1 Photo Upload
        'create_ad_header': '◇━━ Create New Ad ━━◇',
        'create_ad_step1_title': '🎯 **Step 1: Add Photos**',
        'create_ad_photo_prompt': 'Would you like to add photos to your ad?\nYou can add up to 5 high-quality photos',
        'create_ad_photo_instructions': '📸 Send photos now or click "Skip" to continue without photos',
        'create_ad_modern_design': '*Modern design provides a calming, comfortable experience*',
        'skip_photos': '⏭ Skip Photos',
        
        # Error messages
        'error_creating_ad': 'Error starting ad creation. Please try again.',
        'free_trial_used': 'You have already used your free trial!',
        'help_unavailable': 'Help temporarily unavailable. Please try again.',
        'settings_unavailable': 'Settings temporarily unavailable. Please try again.',
        'error_showing_duration': 'Error showing duration options.',
        'error_processing_duration': 'Error processing duration selection.',
        'error_updating_language': 'Error updating language',
        'invalid_package_selected': 'Invalid package selected',
        'send_ad_text_prompt': 'Please send text for your ad.',
        'ad_text_prompt': 'Please send text for your ad.',
        'no_channels_available': 'No channels available for advertising. Please contact support.',
        'send_more_photos': 'Send more photos',
        'ready_for_channels': 'Ready for channel selection',
        'write_ad_text': 'Now write your ad text',
        'error_confirming_ad': 'Error confirming ad. Please try again.',
        
        # Photo upload messages
        'max_photos_reached': 'Maximum 5 photos allowed. Click Done to continue.',
        'photo_uploaded': '📸 Photo {count}/5 uploaded.',
        'done_photos': '✅ Done with Photos',
        'add_more_photos': '📸 Add More',
        'add_more_photos_text': '📸 **Add More Photos**\n\nSend additional photos (max 5 total):',
        'provide_contact_info': '📞 **Provide Contact Information**\n\nHow should customers reach you?\n\nExamples:\n- Phone: +966501234567\n- WhatsApp: +966501234567\n- Email: user@email.com\n- Telegram: @username\n\nContent ready! Let\'s proceed to channel selection.',
        
        # Unified flow messages (Bug #005 fix)
        'ad_content_ready': '✅ **Your ad content is ready!**\n\nNow let\'s select channels for your advertisement.',
        'photos_done_add_text': '📸 **Photos uploaded successfully!**\n\nNow add your ad text to complete the content.',
        'photos_skipped_add_text': '📝 **Write your ad text**\n\nDescribe your product or service clearly.',
        'continue_to_text': '➡️ Continue to Text',
        'ready_for_text': 'Ready for text input',
        'create_ad_text_instructions': '📝 **Write Your Ad Text**\n\nDescribe your product or service clearly:\n- Product/service description\n- Price\n- Key features\n- Contact information\n\nSend your text now:',
        
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
        
        # Settings page
        'settings_title': '⚙️ **Settings**',
        'settings_description': '🔧 **Configure your bot preferences**',
        'current_language': '🌐 **Current Language:** {language_name} {flag}',
        'change_language': '🔄 **Change Language:**\nChoose your preferred language below.',
        'account_info': '📊 **Account Info:**\n- User ID: {user_id}\n- Language: {language}\n- Status: Active',
        
        # Unified journey step descriptions
        'welcome_description': '👋 Welcome to I3lani Bot - Your trusted platform for Telegram channel advertising.',
        'language_prompt': '🌐 Please select your preferred language:',
        'main_menu_description': '📱 I3lani Bot - Main Menu\n\nManage your advertising campaigns easily and effectively.\n\nPlease choose an option:',
        'create_ad_step1_description': '🎯 **Step 1: Add Photos**\n\nWould you like to add photos to your ad?\nYou can upload images now or skip this step.',
        'create_ad_step2_title': '📝 **Step 2: Add Text**',
        'create_ad_step3_title': '📺 **Step 3: Select Channels**',
        'create_ad_step4_title': '⏰ **Step 4: Choose Duration**',
        'create_ad_step5_title': '📊 **Step 5: Posts Per Day**',
        'create_ad_text_instructions': '📝 Now write your ad text content.',
        'select_channels_description': '📺 Choose which channels to advertise on:',
        'select_duration_description': '⏰ Select your campaign duration:',
        'select_posts_description': '📊 Choose how many posts per day:',
        'payment_summary_title': '💰 **Payment Summary**',
        'payment_summary_description': '📋 Review your campaign details and proceed to payment.',
        'payment_method_title': '💳 **Payment Method**',
        'payment_method_description': '💳 Choose your preferred payment method:',
        'help_title': '❓ **Help & Support**',
        'lang_english': '🇺🇸 English',
        'lang_arabic': '🇸🇦 العربية',
        'lang_russian': '🇷🇺 Русский',
        'upload_photos': '📸 Upload Photos',
        'continue_to_duration': '➡️ Continue to Duration',
        'continue_to_payment': '➡️ Continue to Payment',
        'choose_payment_method': '💳 Choose Payment Method',
        'back_to_text': '◀️ Back to Text',
        'back_to_duration': '◀️ Back to Duration',
        'back_to_summary': '◀️ Back to Summary',
        
        # Dashboard and interface elements
        'my_ads_dashboard': '📊 **My Ads Dashboard**\n\nView and manage your advertising campaigns.',
        'share_earn_portal': '💎 **Share & Earn Portal**\n\nInvite friends and earn rewards!',
        'channel_partners_interface': '🤝 **Channel Partners**\n\nJoin our partner program and earn money.',
        'gaming_hub_interface': '🎮 **Gaming Hub**\n\nEarn rewards and compete with other users.',
        'leaderboard_interface': '🏆 **Leaderboard**\n\nSee the top performers in our community.',
        'select_channels_text': '📺 **Select Advertising Channels**\n\nChoose which channels to advertise on:',
    },
    
    'ar': {
        'code': 'ar',
        'name': 'العربية',
        'flag': '🇸🇦',
        'currency': 'SAR',
        'currency_symbol': 'ر.س',
        
        # Welcome and start
        'welcome': '👋 مرحباً بك في بوت I3lani\n\nمنصتك الموثوقة للإعلان عبر قنوات التليجرام.',
        'choose_language': '🌐 يرجى اختيار لغتك:',
        'language_selected': '✅ اللغة: العربية 🇸🇦',
        'language_changed': '✅ تم تغيير اللغة إلى العربية بنجاح!',
        
        # Main menu
        'main_menu': '📱 بوت I3lani - القائمة الرئيسية\n\nأدر حملاتك الإعلانية بسهولة وفعالية.\n\nيرجى اختيار خيار:',
        'create_ad': '➕ إنشاء إعلان جديد',
        'my_ads': '📄 إعلاناتي',
        'pricing': '💵 الأسعار', 
        'share_earn': '💎 بوابة الشارك واربح',
        'settings': '⚙️ الإعدادات',
        'help': '❓ المساعدة',
        'channel_partners': '🤝 شبكة الشركاء',
        'gaming_hub': '🎮 المكافآت والألعاب',
        'leaderboard': '🏆 لوحة الصدارة',
        
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
        'send_ad_content': '◇━━ تحميل عصبي ━━◇\n\nارفع إعلانك:\n• 📝 رسالة نصية\n• 📸 صورة مع وصف\n• 🎥 فيديو مع وصف\n\n▣ إرسال البيانات ▣',
        'ad_received': '◈ تم استلام المحتوى العصبي بنجاح! ✅',
        'choose_channels': '◇━━ القنوات الكمية ━━◇\n\nاختر قنوات البث:',
        'select_duration': '◇━━ محدد التردد ━━◇\n\nاختر مدة الحملة:',
        'choose_payment': '◇━━ بروتوكول الدفع ━━◇\n\nاختر طريقة الدفع:',
        'upload_photo': '📸 ◇ رفع صورة عصبية',
        'upload_video': '🎥 ◇ رفع فيديو كمي',
        'add_text': '📝 ◇ إضافة نص عصبي',
        'provide_contact': '📞 ◇ بروتوكول الاتصال العصبي',
        'contact_info_prompt': '◇━━ شبكة الاتصال ━━◇\n\nكيف يمكن للعملاء التواصل معك؟\n\nأمثلة:\n• هاتف: +966501234567\n• واتساب: +966501234567\n• بريد: user@email.com\n• تليجرام: @username\n\n▣ إرسال البيانات ▣',
        
        # Modern ad creation - Step 1 Photo Upload
        'create_ad_header': '◇━━ إنشاء إعلان جديد ━━◇',
        'create_ad_step1_title': '🎯 **خطوة 1: إضافة الصور**',
        'create_ad_photo_prompt': 'هل تريد إضافة صور لإعلانك؟\nيمكنك إضافة حتى 5 صور عالية الجودة',
        'create_ad_photo_instructions': '📸 أرسل الصور الآن أو اضغط "تخطي" للمتابعة بدون صور',
        'create_ad_modern_design': '*التصميم الحديث يوفر تجربة مريحة ومهدئة*',
        'skip_photos': '⏭ تخطي الصور',
        
        # Error messages
        'error_creating_ad': 'خطأ في بدء إنشاء الإعلان. يرجى المحاولة مرة أخرى.',
        'free_trial_used': 'لقد استخدمت تجربتك المجانية بالفعل!',
        'help_unavailable': 'المساعدة غير متاحة مؤقتاً. يرجى المحاولة مرة أخرى.',
        'settings_unavailable': 'الإعدادات غير متاحة مؤقتاً. يرجى المحاولة مرة أخرى.',
        'error_showing_duration': 'خطأ في عرض خيارات المدة.',
        'error_processing_duration': 'خطأ في معالجة اختيار المدة.',
        'error_updating_language': 'خطأ في تحديث اللغة',
        'invalid_package_selected': 'تم اختيار حزمة غير صالحة',
        'send_ad_text_prompt': 'يرجى إرسال نص إعلانك.',
        'ad_text_prompt': 'يرجى إرسال نص إعلانك.',
        'no_channels_available': 'لا توجد قنوات متاحة للإعلان. يرجى الاتصال بالدعم.',
        'send_more_photos': 'أرسل المزيد من الصور',
        'ready_for_channels': 'جاهز لاختيار القنوات',
        'write_ad_text': 'الآن اكتب نص إعلانك',
        'error_confirming_ad': 'خطأ في تأكيد الإعلان. يرجى المحاولة مرة أخرى.',
        
        # Photo upload messages
        'max_photos_reached': 'الحد الأقصى 5 صور مسموح. اضغط تم للمتابعة.',
        'photo_uploaded': '📸 تم رفع الصورة {count}/5.',
        'done_photos': '✅ تم مع الصور',
        'add_more_photos': '📸 إضافة المزيد',
        'add_more_photos_text': '📸 **إضافة المزيد من الصور**\n\nأرسل صور إضافية (الحد الأقصى 5 صور):',
        'provide_contact_info': '📞 **توفير معلومات الاتصال**\n\nكيف يمكن للعملاء التواصل معك؟\n\nأمثلة:\n- هاتف: +966501234567\n- واتساب: +966501234567\n- بريد: user@email.com\n- تليجرام: @username\n\nالمحتوى جاهز! لننتقل إلى اختيار القنوات.',
        
        # Unified flow messages (Bug #005 fix)
        'ad_content_ready': '✅ **محتوى إعلانك جاهز!**\n\nالآن لنختار القنوات لإعلانك.',
        'photos_done_add_text': '📸 **تم رفع الصور بنجاح!**\n\nالآن أضف نص إعلانك لإكمال المحتوى.',
        'photos_skipped_add_text': '📝 **اكتب نص إعلانك**\n\nصف منتجك أو خدمتك بوضوح.',
        'continue_to_text': '➡️ متابعة للنص',
        'ready_for_text': 'جاهز لإدخال النص',
        'create_ad_text_instructions': '📝 **اكتب نص إعلانك**\n\nصف منتجك أو خدمتك بوضوح:\n- وصف المنتج/الخدمة\n- السعر\n- المميزات الرئيسية\n- معلومات الاتصال\n\nأرسل النص الآن:',
        
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
        
        # Settings page
        'settings_title': '⚙️ **الإعدادات**',
        'settings_description': '🔧 **قم بتكوين تفضيلات البوت**',
        'current_language': '🌐 **اللغة الحالية:** {language_name} {flag}',
        'change_language': '🔄 **تغيير اللغة:**\nاختر لغتك المفضلة أدناه.',
        'account_info': '📊 **معلومات الحساب:**\n- معرف المستخدم: {user_id}\n- اللغة: {language}\n- الحالة: نشط',
        
        # Unified journey step descriptions
        'welcome_description': '👋 مرحباً بك في بوت I3lani - منصتك الموثوقة للإعلان عبر قنوات التليجرام.',
        'language_prompt': '🌐 يرجى اختيار لغتك المفضلة:',
        'main_menu_description': '📱 بوت I3lani - القائمة الرئيسية\n\nأدر حملاتك الإعلانية بسهولة وفعالية.\n\nيرجى اختيار خيار:',
        'create_ad_step1_description': '🎯 **الخطوة 1: إضافة الصور**\n\nهل تريد إضافة صور لإعلانك؟\nيمكنك رفع الصور الآن أو تخطي هذه الخطوة.',
        'create_ad_step2_title': '📝 **الخطوة 2: إضافة النص**',
        'create_ad_step3_title': '📺 **الخطوة 3: اختيار القنوات**',
        'create_ad_step4_title': '⏰ **الخطوة 4: اختيار المدة**',
        'create_ad_step5_title': '📊 **الخطوة 5: المنشورات يومياً**',
        'create_ad_text_instructions': '📝 الآن اكتب محتوى نص إعلانك.',
        'select_channels_description': '📺 اختر القنوات للإعلان عليها:',
        'select_duration_description': '⏰ اختر مدة حملتك:',
        'select_posts_description': '📊 اختر عدد المنشورات يومياً:',
        'payment_summary_title': '💰 **ملخص الدفع**',
        'payment_summary_description': '📋 راجع تفاصيل حملتك وانتقل للدفع.',
        'payment_method_title': '💳 **طريقة الدفع**',
        'payment_method_description': '💳 اختر طريقة الدفع المفضلة:',
        'help_title': '❓ **المساعدة والدعم**',
        'lang_english': '🇺🇸 English',
        'lang_arabic': '🇸🇦 العربية',
        'lang_russian': '🇷🇺 Русский',
        'upload_photos': '📸 رفع الصور',
        'continue_to_duration': '➡️ المتابعة للمدة',
        'continue_to_payment': '➡️ المتابعة للدفع',
        'choose_payment_method': '💳 اختر طريقة الدفع',
        'back_to_text': '◀️ العودة للنص',
        'back_to_duration': '◀️ العودة للمدة',
        'back_to_summary': '◀️ العودة للملخص',
        
        # Dashboard and interface elements
        'my_ads_dashboard': '📊 **لوحة إعلاناتي**\n\nعرض وإدارة حملاتك الإعلانية.',
        'share_earn_portal': '💎 **بوابة الشارك واربح**\n\nادعُ الأصدقاء واحصل على المكافآت!',
        'channel_partners_interface': '🤝 **شبكة الشركاء**\n\nانضم لبرنامج الشراكة واكسب المال.',
        'gaming_hub_interface': '🎮 **مركز الألعاب**\n\nاحصل على المكافآت وتنافس مع المستخدمين الآخرين.',
        'leaderboard_interface': '🏆 **لوحة الصدارة**\n\nاطلع على أفضل المؤدين في مجتمعنا.',
        'select_channels_text': '📺 **اختر قنوات الإعلان**\n\nاختر القنوات التي تريد الإعلان عليها:',
    },
    
    'ru': {
        'code': 'ru',
        'name': 'Русский',
        'flag': '🇷🇺',
        'currency': 'RUB',
        'currency_symbol': '₽',
        
        # Welcome and start
        'welcome': '👋 Добро пожаловать в I3lani Bot\n\nВаша надежная платформа для рекламы в телеграм-каналах.',
        'choose_language': '🌐 Пожалуйста, выберите язык:',
        'language_selected': '✅ Язык: Русский 🇷🇺',
        'language_changed': '✅ Язык успешно изменен на русский!',
        
        # Main menu
        'main_menu': '📱 I3lani Bot - Главное меню\n\nУправляйте рекламными кампаниями легко и эффективно.\n\nПожалуйста, выберите опцию:',
        'create_ad': '➕ Создать новое объявление',
        'my_ads': '📄 Мои объявления',
        'pricing': '💵 Цены', 
        'share_earn': '💎 Портал Поделись и Заработай',
        'settings': '⚙️ Настройки',
        'help': '❓ Помощь',
        'channel_partners': '🤝 Партнерская сеть',
        'gaming_hub': '🎮 Награды и игры',
        'leaderboard': '🏆 Таблица лидеров',
        
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
        'send_ad_content': '◇━━ НЕЙРОЗАГРУЗКА ━━◇\n\nЗагрузите вашу рекламу:\n• 📝 Текстовое сообщение\n• 📸 Фото с описанием\n• 🎥 Видео с описанием\n\n▣ ПЕРЕДАТЬ ДАННЫЕ ▣',
        'ad_received': '◈ Нейроконтент успешно получен! ✅',
        'choose_channels': '◇━━ КВАНТОВЫЕ КАНАЛЫ ━━◇\n\nВыберите каналы для трансляции:',
        'select_duration': '◇━━ СЕЛЕКТОР ЧАСТОТЫ ━━◇\n\nВыберите продолжительность кампании:',
        'choose_payment': '◇━━ ПРОТОКОЛ ОПЛАТЫ ━━◇\n\nВыберите способ оплаты:',
        'upload_photo': '📸 ◇ Загрузить Нейроизображение',
        'upload_video': '🎥 ◇ Загрузить Квантовое Видео',
        'add_text': '📝 ◇ Добавить Нейротекст',
        'provide_contact': '📞 ◇ Протокол Нейроконтактов',
        'contact_info_prompt': '◇━━ КОНТАКТНАЯ СЕТЬ ━━◇\n\nКак клиенты могут связаться с вами?\n\nПримеры:\n• Телефон: +966501234567\n• WhatsApp: +966501234567\n• Email: user@email.com\n• Telegram: @username\n\n▣ ПЕРЕДАТЬ ДАННЫЕ ▣',
        
        # Modern ad creation - Step 1 Photo Upload
        'create_ad_header': '◇━━ Создать новое объявление ━━◇',
        'create_ad_step1_title': '🎯 **Шаг 1: Добавление фотографий**',
        'create_ad_photo_prompt': 'Хотите добавить фотографии в объявление?\nМожно добавить до 5 качественных фотографий',
        'create_ad_photo_instructions': '📸 Отправьте фото или нажмите "Пропустить"',
        'create_ad_modern_design': '*Современный дизайн обеспечивает комфорт*',
        'skip_photos': '⏭ Пропустить фото',
        
        # Error messages
        'error_creating_ad': 'Ошибка при создании объявления. Попробуйте снова.',
        'free_trial_used': 'Вы уже использовали бесплатную пробную версию!',
        'help_unavailable': 'Справка временно недоступна. Попробуйте снова.',
        'settings_unavailable': 'Настройки временно недоступны. Попробуйте снова.',
        'error_showing_duration': 'Ошибка при показе вариантов продолжительности.',
        'error_processing_duration': 'Ошибка при обработке выбора продолжительности.',
        'error_updating_language': 'Ошибка обновления языка',
        'invalid_package_selected': 'Выбран недопустимый пакет',
        'send_ad_text_prompt': 'Пожалуйста, отправьте текст для вашего объявления.',
        'ad_text_prompt': 'Пожалуйста, отправьте текст для вашего объявления.',
        'no_channels_available': 'Нет доступных каналов для рекламы. Обратитесь в службу поддержки.',
        'send_more_photos': 'Отправьте больше фотографий',
        'ready_for_channels': 'Готов к выбору каналов',
        'write_ad_text': 'Теперь напишите текст объявления',
        'error_confirming_ad': 'Ошибка при подтверждении объявления. Попробуйте снова.',
        
        # Photo upload messages
        'max_photos_reached': 'Максимум 5 фотографий разрешено. Нажмите Готово для продолжения.',
        'photo_uploaded': '📸 Фотография {count}/5 загружена.',
        'done_photos': '✅ Готово с фотографиями',
        'add_more_photos': '📸 Добавить больше',
        'add_more_photos_text': '📸 **Добавить больше фотографий**\n\nОтправьте дополнительные фотографии (максимум 5):',
        'provide_contact_info': '📞 **Предоставить контактную информацию**\n\nКак клиенты могут связаться с вами?\n\nПримеры:\n- Телефон: +966501234567\n- WhatsApp: +966501234567\n- Email: user@email.com\n- Telegram: @username\n\nКонтент готов! Переходим к выбору каналов.',
        
        # Unified flow messages (Bug #005 fix)
        'ad_content_ready': '✅ **Контент объявления готов!**\n\nТеперь выберем каналы для вашего объявления.',
        'photos_done_add_text': '📸 **Фотографии успешно загружены!**\n\nТеперь добавьте текст объявления для завершения контента.',
        'photos_skipped_add_text': '📝 **Напишите текст объявления**\n\nОпишите ваш товар или услугу четко.',
        'continue_to_text': '➡️ Продолжить к тексту',
        'ready_for_text': 'Готов к вводу текста',
        'create_ad_text_instructions': '📝 **Напишите текст объявления**\n\nОпишите ваш товар или услугу четко:\n- Описание товара/услуги\n- Цена\n- Основные преимущества\n- Контактная информация\n\nОтправьте текст сейчас:',
        
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
        
        # Settings page
        'settings_title': '⚙️ **Настройки**',
        'settings_description': '🔧 **Настройте предпочтения бота**',
        'current_language': '🌐 **Текущий язык:** {language_name} {flag}',
        'change_language': '🔄 **Изменить язык:**\nВыберите предпочитаемый язык ниже.',
        'account_info': '📊 **Информация об аккаунте:**\n- ID пользователя: {user_id}\n- Язык: {language}\n- Статус: Активен',
        
        # Unified journey step descriptions
        'welcome_description': '👋 Добро пожаловать в I3lani Bot - вашу надежную платформу для рекламы в Telegram каналах.',
        'language_prompt': '🌐 Пожалуйста, выберите предпочитаемый язык:',
        'main_menu_description': '📱 I3lani Bot - Главное меню\n\nУправляйте рекламными кампаниями легко и эффективно.\n\nПожалуйста, выберите опцию:',
        'create_ad_step1_description': '🎯 **Шаг 1: Добавление фотографий**\n\nХотите добавить фотографии в объявление?\nВы можете загрузить изображения сейчас или пропустить этот шаг.',
        'create_ad_step2_title': '📝 **Шаг 2: Добавление текста**',
        'create_ad_step3_title': '📺 **Шаг 3: Выбор каналов**',
        'create_ad_step4_title': '⏰ **Шаг 4: Выбор продолжительности**',
        'create_ad_step5_title': '📊 **Шаг 5: Постов в день**',
        'create_ad_text_instructions': '📝 Теперь напишите текст объявления.',
        'select_channels_description': '📺 Выберите каналы для рекламы:',
        'select_duration_description': '⏰ Выберите продолжительность кампании:',
        'select_posts_description': '📊 Выберите количество постов в день:',
        'payment_summary_title': '💰 **Сводка оплаты**',
        'payment_summary_description': '📋 Просмотрите детали кампании и перейдите к оплате.',
        'payment_method_title': '💳 **Метод оплаты**',
        'payment_method_description': '💳 Выберите предпочитаемый метод оплаты:',
        'help_title': '❓ **Помощь и поддержка**',
        'lang_english': '🇺🇸 English',
        'lang_arabic': '🇸🇦 العربية',
        'lang_russian': '🇷🇺 Русский',
        'upload_photos': '📸 Загрузить фото',
        'continue_to_duration': '➡️ К продолжительности',
        'continue_to_payment': '➡️ К оплате',
        'choose_payment_method': '💳 Выбрать метод оплаты',
        'back_to_text': '◀️ К тексту',
        'back_to_duration': '◀️ К продолжительности',
        'back_to_summary': '◀️ К сводке',
        
        # Dashboard and interface elements
        'my_ads_dashboard': '📊 **Панель моих объявлений**\n\nПросмотр и управление рекламными кампаниями.',
        'share_earn_portal': '💎 **Портал "Поделись и заработай"**\n\nПриглашайте друзей и получайте награды!',
        'channel_partners_interface': '🤝 **Партнеры каналов**\n\nПрисоединяйтесь к партнерской программе и зарабатывайте.',
        'gaming_hub_interface': '🎮 **Игровой центр**\n\nЗарабатывайте награды и соревнуйтесь с другими пользователями.',
        'leaderboard_interface': '🏆 **Таблица лидеров**\n\nПосмотрите лучших исполнителей в нашем сообществе.',
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