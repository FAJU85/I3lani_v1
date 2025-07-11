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
        'welcome': '👋 Welcome to I3lani!\n\nYour gateway to powerful Telegram advertising. You\'re in control of your campaigns.',
        'choose_language': '🌐 Choose your language to get started:',
        'language_selected': '✅ Language: English 🇺🇸',
        'language_changed': '✅ Perfect! Language updated to English.',
        
        # Main menu
        'main_menu': '🚀 I3lani - Your Advertising Command Center\n\nCrypto advertising made easy. Start building your reach today.\n\nWhat would you like to do?',
        'main_menu_welcome': '💎 I3lani Platform\n\nSmart advertising. Simple results.',
        'main_menu_status': 'Status: 🟢 LIVE & SECURED',
        'main_menu_features': '⚡ What you get:\n• 🎯 Smart campaign builder\n• 📊 Multi-channel reach\n• 💪 Real-time tracking\n• 🔐 Bank-level security',
        'main_menu_ready': '💼 Ready to amplify your reach?',
        'your_account': '📊 Your Account:',
        'total_campaigns': '📢 Total Campaigns:',
        'account_status': '🎯 Account Status:',
        'account_active': 'ACTIVE',
        'performance': '🌟 Performance:',
        'performance_optimized': 'OPTIMIZED',
        'create_ad': '🚀 Create Campaign',
        'my_ads': '📊 My Campaigns',
        'pricing': '💰 Simple Pricing', 
        'share_earn': '💎 Earn & Share',
        'settings': '⚙️ Your Settings',
        'help': '💬 Get Help',
        'channel_partners': '🤝 Partner Hub',
        'gaming_hub': '🎮 Rewards Center',
        'leaderboard': '🏆 Top Performers',
        
        # Navigation
        'back': '⬅️ Back',
        'back_to_main': '⬅️ Main Menu',
        'back_to_channels': '⬅️ Back to Channels', 
        'back_to_photos': '⬅️ Back to Photos',
        'continue': '➡️ Continue',
        'continue_to_channels': '➡️ Select Channels',
        'cancel': '❌ Cancel',
        'confirm': '✅ Confirm',
        'try_again': '🔄 Try Again',
        'contact_support': '💬 Get Support',
        'refresh': '🔄 Refresh',
        'skip': '⏭ Skip',
        
        # Error reporting
        'report_error': '🚨 Report Error',
        'error_reported': '✅ Error Reported',
        'error_report_success': '✅ Error Report #{report_id} submitted successfully!\n\nOur team will review your report and fix the issue quickly. You can continue using the bot normally.',
        'error_report_prompt': '🚨 **Report Error**\n\nPlease describe the problem you encountered:\n\n• What happened?\n• What did you expect?\n• Any other details?\n\nThis helps us improve the bot for everyone.',
        'error_report_step': 'Step: {step_name}',
        
        # Confirmation system
        'confirm_action': '✅ Confirm',
        'cancel_action': '❌ Cancel',
        'edit_action': '✏️ Edit',
        'review_details': '📝 Review Details',
        'confirmation_required': '⚠️ Confirm Your Choice',
        'action_cannot_be_undone': 'This action is permanent.',
        'proceed_with_action': 'Ready to proceed?',
        'confirmation_timeout': 'Time expired. Let\'s try again.',
        'action_confirmed': '✅ Perfect! Action completed.',
        'action_cancelled': '❌ Action cancelled.',
        
        # Ad creation
        'send_ad_content': '🎯 **Let\'s Build Your Campaign**\n\nUpload your content and we\'ll handle the rest:\n• 📝 Text message\n• 📸 Photo with caption\n• 🎥 Video with caption\n\nYour content is secured with advanced encryption. Start now:',
        'ad_received': '✅ Perfect! Your content is ready to go.',
        'choose_channels': '📢 Choose Your Reach - Select Channels:',
        'select_duration': '⏱️ **Set Your Timeline**\n\nHow long should your campaign run? You\'re in control:',
        'choose_payment': '💳 **Simple & Secure Payment**\n\nPick your preferred method - all transactions are protected:',
        'upload_photo': '📸 Add Photo',
        'upload_video': '🎥 Add Video',
        'add_text': '📝 Write Copy',
        'provide_contact': '📞 Add Contact',
        'contact_info_prompt': '📞 **Make It Easy to Reach You**\n\nHow should customers connect with you?\n\nExamples:\n• Phone: +966501234567\n• WhatsApp: +966501234567\n• Email: user@email.com\n• Telegram: @username\n\nYour contact info is kept secure:',
        
        # Modern ad creation - Step 1 Photo Upload
        'create_ad_header': '🚀 Launch Your Campaign',
        'create_ad_step1_title': '🎯 **Step 1: Visual Content**',
        'create_ad_photo_prompt': 'Want to add photos to boost engagement?\nUpload up to 5 stunning images',
        'create_ad_photo_instructions': '📸 Upload now or skip to continue - you\'re in control',
        'create_ad_modern_design': '*Crypto advertising made simple*',
        'skip_photos': '⏭ Skip Photos',
        
        # Error messages
        'error_creating_ad': 'Oops! Something went wrong. Let\'s try that again.',
        'free_trial_used': 'You\'ve already claimed your free trial! Ready to upgrade?',
        'help_unavailable': 'Help is temporarily down. We\'ll be back shortly!',
        'settings_unavailable': 'Settings are being updated. Check back in a moment!',
        'error_showing_duration': 'Can\'t load duration options right now. Let\'s fix this.',
        'error_processing_duration': 'Duration selection failed. Let\'s try again.',
        'error_updating_language': 'Language update failed. Give it another shot!',
        'invalid_package_selected': 'That package isn\'t available. Choose another one.',
        'send_ad_text_prompt': 'Your ad needs some text. Write something amazing!',
        'ad_text_prompt': 'Tell your story! Add your ad text now.',
        'no_channels_available': 'No channels are live right now. Contact our support team for help.',
        'send_more_photos': 'Send more photos',
        'ready_for_channels': 'Ready for channel selection',
        'write_ad_text': 'Now write your ad text',
        'error_confirming_ad': 'Error confirming ad. Please try again.',
        
        # Photo upload messages
        'max_photos_reached': 'Perfect! You\'ve hit the 5-photo limit. Ready to continue?',
        'photo_uploaded': '📸 Photo {count}/5 secured.',
        'done_photos': '✅ Photos Ready',
        'add_more_photos': '📸 Add More',
        'add_more_photos_text': '📸 **Add More Visual Power**\n\nUpload more photos (max 5 total):',
        'provide_contact_info': '📞 **Make It Easy to Connect**\n\nHow should customers reach you?\n\nExamples:\n- Phone: +966501234567\n- WhatsApp: +966501234567\n- Email: user@email.com\n- Telegram: @username\n\nContent secured! Let\'s pick your channels.',
        
        # Unified flow messages (Bug #005 fix)
        'ad_content_ready': '✅ **Your content is locked and loaded!**\n\nNow let\'s pick your channels for maximum reach.',
        'photos_done_add_text': '📸 **Photos secured!**\n\nNow write compelling copy to complete your campaign.',
        'photos_skipped_add_text': '📝 **Tell your story**\n\nWrite copy that converts customers.',
        'continue_to_text': '➡️ Write Copy',
        'ready_for_text': 'Ready for your message',
        'create_ad_text_instructions': '📝 **Write Copy That Converts**\n\nMake your message compelling:\n- What you\'re offering\n- Why it\'s valuable\n- Key benefits\n- How to contact you\n\nStart writing:',
        
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
        'payment_instructions': '💳 **Secure Payment Process**',
        'memo_format': '📝 Transaction ID: {memo}',
        'payment_sent': '✅ Payment Confirmed & Secure',
        
        # Payment receipt
        'payment_receipt_title': '🧾 **Payment Receipt**',
        'payment_received': '✅ Payment Received!',
        'payment_method': 'Payment Method:',
        'amount_paid': 'Amount Paid:',
        'payment_date': 'Payment Date:',
        'payment_id': 'Payment ID:',
        'ad_details': 'Ad Details:',
        'selected_channels': 'Selected Channels:',
        'campaign_duration': 'Campaign Duration:',
        'posts_per_day': 'Posts Per Day:',
        'total_posts': 'Total Posts:',
        'receipt_thank_you': 'Thank you for using I3lani Bot!',
        'receipt_support': 'Support: /support',
        
        # TON Payment Confirmation Messages
        'ton_payment_confirmed': '🎉 **TON Payment Secured!**',
        'payment_verified': 'Your TON payment is verified and protected on the blockchain!',
        'campaign_starting': '🚀 **Your Campaign is Live!**',
        'campaign_details_confirmed': '📊 **Your Campaign Setup:**',
        'payment_amount_received': '💰 **Amount Confirmed:**',
        'campaign_will_run': '📅 **Campaign Duration:**',
        'posting_frequency_confirmed': '📊 **Posting Schedule:**',
        'channels_confirmed': '📺 **Your Channels:**',
        'total_posts_confirmed': '📈 **Total Reach:**',
        'publishing_notifications': '📱 You\'ll get real-time updates as your ads go live across channels',
        'thank_you_choosing': 'Welcome to I3lani! You\'re set up for success.',
        'campaign_status_active': '🟢 Status: LIVE & GROWING',
        
        # Ad publishing notifications
        'ad_published_title': '✅ **Ad Published Successfully!**',
        'ad_published_message': 'Your advertisement has been published successfully!',
        'published_channel': 'Published to:',
        'published_date': 'Publication Date:',
        'ad_id': 'Ad ID:',
        'ad_summary': 'Ad Summary:',
        'publishing_status': 'Status: Published',
        'publishing_success': 'Your ad is now live and visible to channel subscribers!',
        'publishing_thank_you': 'Thank you for choosing I3lani Bot!',
        
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
        
        # Payment interface translations
        'ad_plan_summary': '✅ **Your Ad Plan Summary:**',
        'duration_label': '📅 **Duration:**',
        'posts_per_day_label': '📝 **Posts per day:**',
        'discount_label': '💰 **Discount:**',
        'final_price_label': '💵 **Final Price:**',
        'in_ton_label': '💎 **In TON:**',
        'in_stars_label': '⭐ **In Telegram Stars:**',
        'selected_channels_label': '📺 **Selected Channels:**',
        'campaign_details_label': '📊 **Campaign Details:**',
        'daily_rate_label': '• Daily Rate:',
        'total_posts_label': '• Total Posts:',
        'base_cost_label': '• Base Cost:',
        'you_save_label': '• You Save:',
        'usage_agreement_notice': '📌 **By making this payment, you agree to the Usage Agreement.**',
        'pricing_tip': '💡 **More days = More posts per day + Bigger discounts!**',
        'pay_with_ton': '💎 Pay with TON',
        'pay_with_stars': '⭐ Pay with Stars',
        'change_duration': '📝 Change Duration',
        'change_channels': '📺 Change Channels',
        'days_word': 'days',
        'posts_word': 'posts',
        'off_word': 'off',
        'per_day': 'per day',
        'smart_pricing_system': '🧠 **Smart Pricing System - Choose Days**',
        'selected_days': '📅 **Selected Days:**',
        'smart_logic': '💡 **Smart Logic:**',
        'more_days_more_posts': '✅ More Days = More Posts Per Day',
        'more_days_bigger_discount': '✅ More Days = Bigger Discount',
        'auto_currency_calc': '✅ Auto Currency Calculation (USD, TON, Stars)',
        'click_adjust_days': '🔄 Click +/- to adjust days or choose from quick options',
        'continue_with_days': 'Continue with {days} days',
    },
    
    'ar': {
        'code': 'ar',
        'name': 'العربية',
        'flag': '🇸🇦',
        'currency': 'SAR',
        'currency_symbol': 'ر.س',
        
        # Welcome and start
        'welcome': '👋 أهلاً بك في إعلاني!\n\nبوابتك لإعلانات تليجرام القوية. أنت تتحكم في حملاتك.',
        'choose_language': '🌐 اختر لغتك للبدء:',
        'language_selected': '✅ اللغة: العربية 🇸🇦',
        'language_changed': '✅ ممتاز! تم تحديث اللغة للعربية.',
        
        # Main menu
        'main_menu': '🚀 إعلاني - مركز القيادة الإعلاني\n\nإعلانات العملات المشفرة سهلة. ابدأ ببناء وصولك اليوم.\n\nماذا تريد أن تفعل؟',
        'main_menu_welcome': '💎 منصة إعلاني\n\nإعلانات ذكية. نتائج بسيطة.',
        'main_menu_status': 'الحالة: 🟢 مباشر ومؤمن',
        'main_menu_features': '⚡ ما تحصل عليه:\n• 🎯 أداة بناء حملات ذكية\n• 📊 وصول متعدد القنوات\n• 💪 تتبع مباشر\n• 🔐 أمان على مستوى البنوك',
        'main_menu_ready': '💼 جاهز لتضخيم وصولك؟',
        'your_account': '📊 حسابك:',
        'total_campaigns': '📢 عدد الحملات:',
        'account_status': '🎯 حالة الحساب:',
        'account_active': 'نشط',
        'performance': '🌟 الأداء:',
        'performance_optimized': 'محسن',
        'create_ad': '🚀 إنشاء حملة',
        'my_ads': '📊 حملاتي',
        'pricing': '💰 أسعار بسيطة', 
        'share_earn': '💎 اربح وشارك',
        'settings': '⚙️ إعداداتك',
        'help': '💬 احصل على مساعدة',
        'channel_partners': '🤝 مركز الشركاء',
        'gaming_hub': '🎮 مركز المكافآت',
        'leaderboard': '🏆 أفضل المؤدين',
        
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
        'skip': '⏭ تخطي',
        
        # Error reporting
        'report_error': '🚨 الإبلاغ عن خطأ',
        'error_reported': '✅ تم الإبلاغ عن الخطأ',
        'error_report_success': '✅ تم إرسال تقرير الخطأ #{report_id} بنجاح!\n\nسيراجع فريقنا تقريرك وسيصحح المشكلة بسرعة. يمكنك مواصلة استخدام البوت بشكل طبيعي.',
        'error_report_prompt': '🚨 **الإبلاغ عن خطأ**\n\nيرجى وصف المشكلة التي واجهتها:\n\n• ماذا حدث؟\n• ماذا توقعت؟\n• أي تفاصيل أخرى؟\n\nهذا يساعدنا في تحسين البوت للجميع.',
        'error_report_step': 'الخطوة: {step_name}',
        
        # Confirmation system
        'confirm_action': '✅ تأكيد',
        'cancel_action': '❌ إلغاء',
        'edit_action': '✏️ تعديل',
        'review_details': '📝 مراجعة التفاصيل',
        'confirmation_required': '⚠️ يلزم التأكيد',
        'action_cannot_be_undone': 'لا يمكن التراجع عن هذا الإجراء.',
        'proceed_with_action': 'هل أنت متأكد من المتابعة؟',
        'confirmation_timeout': 'انتهت مهلة التأكيد. يرجى المحاولة مرة أخرى.',
        'action_confirmed': '✅ تم تأكيد الإجراء بنجاح!',
        'action_cancelled': '❌ تم إلغاء الإجراء.',
        
        # Ad creation
        'send_ad_content': '🎯 **لنبني حملتك**\n\nارفع محتواك وسنتولى الباقي:\n• 📝 رسالة نصية\n• 📸 صورة مع وصف\n• 🎥 فيديو مع وصف\n\nمحتواك مؤمن بتشفير متقدم. ابدأ الآن:',
        'ad_received': '✅ مثالي! محتواك جاهز للانطلاق.',
        'choose_channels': '📢 اختر وصولك - حدد القنوات:',
        'select_duration': '⏱️ **حدد جدولك الزمني**\n\nكم يجب أن تستمر حملتك؟ أنت تتحكم:',
        'choose_payment': '💳 **دفع بسيط ومؤمن**\n\nاختر طريقتك المفضلة - جميع المعاملات محمية:',
        'upload_photo': '📸 رفع صورة',
        'upload_video': '🎥 رفع فيديو',
        'add_text': '📝 إضافة نص',
        'provide_contact': '📞 إضافة معلومات الاتصال',
        'contact_info_prompt': '📞 **معلومات الاتصال**\n\nكيف يمكن للعملاء التواصل معك؟\n\nأمثلة:\n• هاتف: +966501234567\n• واتساب: +966501234567\n• بريد: user@email.com\n• تليجرام: @username\n\nيرجى تقديم تفاصيل الاتصال:',
        
        # Modern ad creation - Step 1 Photo Upload
        'create_ad_header': '📝 إنشاء إعلان جديد',
        'create_ad_step1_title': '🎯 **خطوة 1: إضافة الصور**',
        'create_ad_photo_prompt': 'هل تريد إضافة صور لإعلانك؟\nيمكنك إضافة حتى 5 صور عالية الجودة',
        'create_ad_photo_instructions': '📸 أرسل الصور الآن أو اضغط "تخطي" للمتابعة بدون صور',
        'create_ad_modern_design': '*التصميم الحديث يوفر تجربة مريحة ومهدئة*',
        'skip_photos': '⏭ تخطي الصور',
        
        # Error messages
        'error_creating_ad': 'عذراً! حدث خطأ. لنجرب مرة أخرى.',
        'free_trial_used': 'لقد استخدمت تجربتك المجانية! مستعد للترقية؟',
        'help_unavailable': 'المساعدة متوقفة مؤقتاً. سنعود قريباً!',
        'settings_unavailable': 'الإعدادات قيد التحديث. تحقق بعد لحظة!',
        'error_showing_duration': 'لا يمكن تحميل خيارات المدة الآن. لنصلح هذا.',
        'error_processing_duration': 'فشل اختيار المدة. لنجرب مرة أخرى.',
        'error_updating_language': 'فشل تحديث اللغة. جرب مرة أخرى!',
        'invalid_package_selected': 'هذه الحزمة غير متاحة. اختر أخرى.',
        'send_ad_text_prompt': 'إعلانك يحتاج نص. اكتب شيئاً رائعاً!',
        'ad_text_prompt': 'احك قصتك! أضف نص إعلانك الآن.',
        'no_channels_available': 'لا توجد قنوات مباشرة الآن. اتصل بفريق الدعم للمساعدة.',
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
        
        # Payment receipt
        'payment_receipt_title': '🧾 **إيصال الدفع**',
        'payment_received': '✅ تم استلام الدفع!',
        'payment_method': 'طريقة الدفع:',
        'amount_paid': 'المبلغ المدفوع:',
        'payment_date': 'تاريخ الدفع:',
        'payment_id': 'رقم الدفع:',
        'ad_details': 'تفاصيل الإعلان:',
        'selected_channels': 'القنوات المختارة:',
        'campaign_duration': 'مدة الحملة:',
        'posts_per_day': 'منشورات يومية:',
        'total_posts': 'إجمالي المنشورات:',
        'receipt_thank_you': 'شكراً لاستخدام بوت I3lani!',
        'receipt_support': 'للدعم: /support',
        
        # TON Payment Confirmation Messages
        'ton_payment_confirmed': '✅ **تم تأكيد دفع TON!**',
        'payment_verified': 'تم التحقق من دفع TON الخاص بك على البلوك تشين!',
        'campaign_starting': '🚀 **حملتك الإعلانية تبدأ الآن!**',
        'campaign_details_confirmed': '📊 **تفاصيل الحملة:**',
        'payment_amount_received': '💰 **المبلغ المستلم:**',
        'campaign_will_run': '📅 **مدة الحملة:**',
        'posting_frequency_confirmed': '📊 **تكرار النشر:**',
        'channels_confirmed': '📺 **القنوات:**',
        'total_posts_confirmed': '📈 **إجمالي المنشورات:**',
        'publishing_notifications': '📱 ستتلقى إشعارات عند نشر إعلانك في كل قناة',
        'thank_you_choosing': 'شكراً لاختيار منصة I3lani!',
        'campaign_status_active': '🟢 الحالة: نشط',
        
        # Ad publishing notifications
        'ad_published_title': '✅ **تم نشر إعلانك بنجاح!**',
        'ad_published_message': 'تم نشر إعلانك بنجاح!',
        'published_channel': 'نُشر في:',
        'published_date': 'تاريخ النشر:',
        'ad_id': 'رقم الإعلان:',
        'ad_summary': 'ملخص الإعلان:',
        'publishing_status': 'الحالة: منشور',
        'publishing_success': 'إعلانك الآن مباشر ومرئي لمشتركي القناة!',
        'publishing_thank_you': 'شكراً لاختيارك بوت I3lani!',
        
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
        
        # Payment interface translations
        'ad_plan_summary': '✅ **ملخص خطة إعلانك:**',
        'duration_label': '📅 **المدة:**',
        'posts_per_day_label': '📝 **منشورات يومياً:**',
        'discount_label': '💰 **الخصم:**',
        'final_price_label': '💵 **السعر النهائي:**',
        'in_ton_label': '💎 **بعملة TON:**',
        'in_stars_label': '⭐ **بنجوم تليجرام:**',
        'selected_channels_label': '📺 **القنوات المختارة:**',
        'campaign_details_label': '📊 **تفاصيل الحملة:**',
        'daily_rate_label': '• معدل يومي:',
        'total_posts_label': '• إجمالي المنشورات:',
        'base_cost_label': '• التكلفة الأساسية:',
        'you_save_label': '• توفر:',
        'usage_agreement_notice': '📌 **بإجراء هذا الدفع، أنت توافق على شروط الاستخدام.**',
        'pricing_tip': '💡 **المزيد من الأيام = المزيد من المنشورات يومياً + خصومات أكبر!**',
        'pay_with_ton': '💎 دفع بـ TON',
        'pay_with_stars': '⭐ دفع بالنجوم',
        'change_duration': '📝 تغيير المدة',
        'change_channels': '📺 تغيير القنوات',
        'days_word': 'أيام',
        'posts_word': 'منشورات',
        'off_word': 'خصم',
        'per_day': 'يومياً',
        'smart_pricing_system': '🧠 **نظام التسعير الذكي - اختر الأيام**',
        'selected_days': '📅 **الأيام المختارة:**',
        'smart_logic': '💡 **المنطق الذكي:**',
        'more_days_more_posts': '✅ المزيد من الأيام = المزيد من المنشورات يومياً',
        'more_days_bigger_discount': '✅ المزيد من الأيام = خصم أكبر',
        'auto_currency_calc': '✅ حساب العملة التلقائي (USD, TON, Stars)',
        'click_adjust_days': '🔄 انقر +/- لضبط الأيام أو اختر من الخيارات السريعة',
        'continue_with_days': 'متابعة مع {days} أيام',
    },
    
    'ru': {
        'code': 'ru',
        'name': 'Русский',
        'flag': '🇷🇺',
        'currency': 'RUB',
        'currency_symbol': '₽',
        
        # Welcome and start
        'welcome': '👋 Добро пожаловать в I3lani!\n\nВаш шлюз к мощной рекламе в Telegram. Вы контролируете свои кампании.',
        'choose_language': '🌐 Выберите язык для начала:',
        'language_selected': '✅ Язык: Русский 🇷🇺',
        'language_changed': '✅ Отлично! Язык обновлен на русский.',
        
        # Main menu
        'main_menu': '🚀 I3lani - Ваш центр управления рекламой\n\nКриптореклама стала простой. Начните увеличивать охват сегодня.\n\nЧто вы хотите сделать?',
        'main_menu_welcome': '💎 Платформа I3lani\n\nУмная реклама. Простые результаты.',
        'main_menu_status': 'Статус: 🟢 В СЕТИ И ЗАЩИЩЕН',
        'main_menu_features': '⚡ Что вы получаете:\n• 🎯 Умный конструктор кампаний\n• 📊 Многоканальный охват\n• 💪 Отслеживание в реальном времени\n• 🔐 Безопасность банковского уровня',
        'main_menu_ready': '💼 Готовы усилить свой охват?',
        'your_account': '📊 Ваш аккаунт:',
        'total_campaigns': '📢 Всего кампаний:',
        'account_status': '🎯 Статус аккаунта:',
        'account_active': 'АКТИВНЫЙ',
        'performance': '🌟 Производительность:',
        'performance_optimized': 'ОПТИМИЗИРОВАН',
        'create_ad': '🚀 Создать кампанию',
        'my_ads': '📊 Мои кампании',
        'pricing': '💰 Простые цены', 
        'share_earn': '💎 Зарабатывай и делись',
        'settings': '⚙️ Ваши настройки',
        'help': '💬 Получить помощь',
        'channel_partners': '🤝 Центр партнеров',
        'gaming_hub': '🎮 Центр наград',
        'leaderboard': '🏆 Лучшие исполнители',
        
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
        'skip': '⏭ Пропустить',
        
        # Error reporting
        'report_error': '🚨 Сообщить об ошибке',
        'error_reported': '✅ Ошибка зарегистрирована',
        'error_report_success': '✅ Отчёт об ошибке #{report_id} успешно отправлен!\n\nНаша команда рассмотрит ваш отчёт и быстро исправит проблему. Вы можете продолжать пользоваться ботом нормально.',
        'error_report_prompt': '🚨 **Сообщить об ошибке**\n\nПожалуйста, опишите проблему, с которой вы столкнулись:\n\n• Что произошло?\n• Что вы ожидали?\n• Любые другие детали?\n\nЭто поможет нам улучшить бота для всех.',
        'error_report_step': 'Шаг: {step_name}',
        
        # Confirmation system
        'confirm_action': '✅ Подтвердить',
        'cancel_action': '❌ Отменить',
        'edit_action': '✏️ Редактировать',
        'review_details': '📝 Просмотр деталей',
        'confirmation_required': '⚠️ Требуется подтверждение',
        'action_cannot_be_undone': 'Это действие нельзя отменить.',
        'proceed_with_action': 'Вы уверены, что хотите продолжить?',
        'confirmation_timeout': 'Время подтверждения истекло. Пожалуйста, попробуйте снова.',
        'action_confirmed': '✅ Действие успешно подтверждено!',
        'action_cancelled': '❌ Действие отменено.',
        
        # Ad creation
        'send_ad_content': '📝 **Создайте вашу рекламу**\n\nЗагрузите ваш контент:\n• 📝 Текстовое сообщение\n• 📸 Фото с описанием\n• 🎥 Видео с описанием\n\nОтправьте ваш контент сейчас:',
        'ad_received': '✅ Контент успешно получен!',
        'choose_channels': '📢 Выберите рекламные каналы:',
        'select_duration': '⏱️ **Выберите продолжительность кампании**\n\nУкажите, как долго должна работать ваша реклама:',
        'choose_payment': '💳 **Выберите способ оплаты**\n\nВыберите, как вы хотите заплатить:',
        'upload_photo': '📸 Загрузить фото',
        'upload_video': '🎥 Загрузить видео',
        'add_text': '📝 Добавить текст',
        'provide_contact': '📞 Добавить контактную информацию',
        'contact_info_prompt': '📞 **Контактная информация**\n\nКак клиенты могут связаться с вами?\n\nПримеры:\n• Телефон: +966501234567\n• WhatsApp: +966501234567\n• Email: user@email.com\n• Telegram: @username\n\nПожалуйста, предоставьте ваши контактные данные:',
        
        # Modern ad creation - Step 1 Photo Upload
        'create_ad_header': '📝 Создать новое объявление',
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
        
        # Payment receipt
        'payment_receipt_title': '🧾 **Чек об оплате**',
        'payment_received': '✅ Оплата получена!',
        'payment_method': 'Способ оплаты:',
        'amount_paid': 'Сумма оплаты:',
        'payment_date': 'Дата оплаты:',
        'payment_id': 'ID платежа:',
        'ad_details': 'Детали объявления:',
        'selected_channels': 'Выбранные каналы:',
        'campaign_duration': 'Длительность кампании:',
        'posts_per_day': 'Постов в день:',
        'total_posts': 'Всего постов:',
        'receipt_thank_you': 'Спасибо за использование I3lani Bot!',
        'receipt_support': 'Поддержка: /support',
        
        # TON Payment Confirmation Messages
        'ton_payment_confirmed': '✅ **TON платеж подтвержден!**',
        'payment_verified': 'Ваш TON платеж был подтвержден на блокчейне!',
        'campaign_starting': '🚀 **Ваша рекламная кампания начинается сейчас!**',
        'campaign_details_confirmed': '📊 **Детали кампании:**',
        'payment_amount_received': '💰 **Получено:**',
        'campaign_will_run': '📅 **Длительность кампании:**',
        'posting_frequency_confirmed': '📊 **Частота публикации:**',
        'channels_confirmed': '📺 **Каналы:**',
        'total_posts_confirmed': '📈 **Всего постов:**',
        'publishing_notifications': '📱 Вы получите уведомления при публикации в каждом канале',
        'thank_you_choosing': 'Спасибо за выбор платформы I3lani!',
        'campaign_status_active': '🟢 Статус: АКТИВЕН',
        
        # Ad publishing notifications
        'ad_published_title': '✅ **Объявление успешно опубликовано!**',
        'ad_published_message': 'Ваше объявление успешно опубликовано!',
        'published_channel': 'Опубликовано в:',
        'published_date': 'Дата публикации:',
        'ad_id': 'ID объявления:',
        'ad_summary': 'Краткое описание:',
        'publishing_status': 'Статус: Опубликовано',
        'publishing_success': 'Ваше объявление теперь активно и видно подписчикам канала!',
        'publishing_thank_you': 'Спасибо за выбор I3lani Bot!',
        
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
        'issue_reported': '✅ Ваша проблема зарегистрирована. Команда поддержки рассмотрит её в ближайшее время.',
        
        # Payment interface translations
        'ad_plan_summary': '✅ **Итоги плана рекламы:**',
        'duration_label': '📅 **Длительность:**',
        'posts_per_day_label': '📝 **Постов в день:**',
        'discount_label': '💰 **Скидка:**',
        'final_price_label': '💵 **Итоговая цена:**',
        'in_ton_label': '💎 **В TON:**',
        'in_stars_label': '⭐ **В Telegram Stars:**',
        'selected_channels_label': '📺 **Выбранные каналы:**',
        'campaign_details_label': '📊 **Детали кампании:**',
        'daily_rate_label': '• Дневной тариф:',
        'total_posts_label': '• Всего постов:',
        'base_cost_label': '• Базовая стоимость:',
        'you_save_label': '• Вы экономите:',
        'usage_agreement_notice': '📌 **Совершая этот платеж, вы соглашаетесь с Условиями использования.**',
        'pricing_tip': '💡 **Больше дней = Больше постов в день + Больше скидки!**',
        'pay_with_ton': '💎 Оплатить TON',
        'pay_with_stars': '⭐ Оплатить Stars',
        'change_duration': '📝 Изменить длительность',
        'change_channels': '📺 Изменить каналы',
        'days_word': 'дней',
        'posts_word': 'постов',
        'off_word': 'скидка',
        'per_day': 'в день',
        'smart_pricing_system': '🧠 **Умная система ценообразования - Выберите дни**',
        'selected_days': '📅 **Выбранные дни:**',
        'smart_logic': '💡 **Умная логика:**',
        'more_days_more_posts': '✅ Больше дней = Больше постов в день',
        'more_days_bigger_discount': '✅ Больше дней = Больше скидка',
        'auto_currency_calc': '✅ Автоматический расчет валюты (USD, TON, Stars)',
        'click_adjust_days': '🔄 Нажмите +/- для изменения дней или выберите из быстрых опций',
        'continue_with_days': 'Продолжить с {days} дней',
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

async def get_user_language(user_id: int) -> str:
    """Get user's selected language from database"""
    try:
        from database import db
        language = await db.get_user_language(user_id)
        return language if language in LANGUAGES else DEFAULT_LANGUAGE
    except Exception:
        return DEFAULT_LANGUAGE