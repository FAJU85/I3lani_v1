#!/usr/bin/env python3
"""
Contextual Help Bubble System for I3lani Bot
Provides contextual guidance and tips for each navigation step
"""

import logging
from typing import Dict, List, Optional, Union
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from step_title_system import get_step_title
from animated_transitions import get_animated_transitions
from global_sequence_system import get_global_sequence_manager
from sequence_logger import get_sequence_logger

logger = get_sequence_logger(__name__)

class ContextualHelpSystem:
    """Manages contextual help bubbles for each bot stage"""
    
    def __init__(self):
        self.help_content = {
            # Main navigation help
            "main_menu": {
                "en": {
                    "title": "🏠 Main Menu Help",
                    "content": "Welcome to I3lani! Here you can:\n• Create new advertisements\n• View your campaigns\n• Check account settings\n• Get support",
                    "tips": ["💡 Start with 'Create Ad' for your first campaign", "📊 Check 'My Campaigns' to track progress"],
                    "quick_actions": ["Create Ad", "My Campaigns", "Settings"]
                },
                "ar": {
                    "title": "🏠 مساعدة القائمة الرئيسية",
                    "content": "مرحباً بك في إعلاني! يمكنك هنا:\n• إنشاء إعلانات جديدة\n• عرض حملاتك\n• فحص إعدادات الحساب\n• الحصول على الدعم",
                    "tips": ["💡 ابدأ بـ 'إنشاء إعلان' لحملتك الأولى", "📊 تحقق من 'حملاتي' لتتبع التقدم"],
                    "quick_actions": ["إنشاء إعلان", "حملاتي", "الإعدادات"]
                },
                "ru": {
                    "title": "🏠 Помощь главного меню",
                    "content": "Добро пожаловать в I3lani! Здесь вы можете:\n• Создавать новые рекламы\n• Просматривать кампании\n• Проверять настройки\n• Получить поддержку",
                    "tips": ["💡 Начните с 'Создать рекламу' для первой кампании", "📊 Проверьте 'Мои кампании' для отслеживания"],
                    "quick_actions": ["Создать рекламу", "Мои кампании", "Настройки"]
                }
            },
            
            # Ad creation help
            "create_ad_start": {
                "en": {
                    "title": "✏️ Create Advertisement Help",
                    "content": "Start creating your ad campaign:\n• Upload images or photos (optional)\n• Write compelling ad text\n• Choose target channels\n• Set campaign duration",
                    "tips": ["📸 High-quality images get better engagement", "✍️ Keep text clear and concise", "🎯 Choose relevant channels for your audience"],
                    "quick_actions": ["Upload Photo", "Skip to Text", "View Examples"]
                },
                "ar": {
                    "title": "✏️ مساعدة إنشاء الإعلان",
                    "content": "ابدأ في إنشاء حملتك الإعلانية:\n• رفع الصور أو الصور (اختياري)\n• كتابة نص إعلاني جذاب\n• اختيار القنوات المستهدفة\n• تحديد مدة الحملة",
                    "tips": ["📸 الصور عالية الجودة تحصل على تفاعل أفضل", "✍️ اجعل النص واضح ومختصر", "🎯 اختر قنوات مناسبة لجمهورك"],
                    "quick_actions": ["رفع صورة", "الانتقال للنص", "عرض الأمثلة"]
                },
                "ru": {
                    "title": "✏️ Помощь создания рекламы",
                    "content": "Начните создание рекламной кампании:\n• Загрузите изображения (опционально)\n• Напишите привлекательный текст\n• Выберите целевые каналы\n• Установите длительность",
                    "tips": ["📸 Качественные изображения получают больше вовлеченности", "✍️ Делайте текст ясным и кратким", "🎯 Выбирайте подходящие каналы"],
                    "quick_actions": ["Загрузить фото", "Перейти к тексту", "Примеры"]
                }
            },
            
            # Channel selection help
            "select_channels": {
                "en": {
                    "title": "📺 Channel Selection Help",
                    "content": "Choose channels for your ad campaign:\n• View live subscriber counts\n• Select multiple channels\n• Check total reach\n• Consider channel categories",
                    "tips": ["📊 More channels = wider reach", "🎯 Match channels to your target audience", "💰 Pricing scales with selected channels"],
                    "quick_actions": ["Select All", "Refresh Stats", "View Details"]
                },
                "ar": {
                    "title": "📺 مساعدة اختيار القنوات",
                    "content": "اختر القنوات لحملتك الإعلانية:\n• عرض أعداد المشتركين المباشرة\n• اختيار قنوات متعددة\n• فحص الوصول الإجمالي\n• النظر في فئات القنوات",
                    "tips": ["📊 المزيد من القنوات = وصول أوسع", "🎯 اجعل القنوات تتناسب مع جمهورك المستهدف", "💰 التسعير يتناسب مع القنوات المختارة"],
                    "quick_actions": ["اختيار الكل", "تحديث الإحصائيات", "عرض التفاصيل"]
                },
                "ru": {
                    "title": "📺 Помощь выбора каналов",
                    "content": "Выберите каналы для рекламной кампании:\n• Просмотр живой статистики подписчиков\n• Выбор нескольких каналов\n• Проверка общего охвата\n• Учет категорий каналов",
                    "tips": ["📊 Больше каналов = шире охват", "🎯 Подбирайте каналы под целевую аудиторию", "💰 Цена зависит от выбранных каналов"],
                    "quick_actions": ["Выбрать все", "Обновить статистику", "Детали"]
                }
            },
            
            # Payment help
            "payment_processing": {
                "en": {
                    "title": "💳 Payment Help",
                    "content": "Complete your campaign payment:\n• Choose payment method (TON/Stars)\n• Review campaign details\n• Confirm payment amount\n• Track payment status",
                    "tips": ["🔒 All payments are secure and encrypted", "⚡ TON payments are processed instantly", "💫 Stars payments use Telegram's system"],
                    "quick_actions": ["Pay with TON", "Pay with Stars", "Review Details"]
                },
                "ar": {
                    "title": "💳 مساعدة الدفع",
                    "content": "أكمل دفع حملتك:\n• اختر طريقة الدفع (TON/النجوم)\n• راجع تفاصيل الحملة\n• أكد مبلغ الدفعة\n• تتبع حالة الدفع",
                    "tips": ["🔒 جميع المدفوعات آمنة ومشفرة", "⚡ مدفوعات TON تتم معالجتها فوراً", "💫 مدفوعات النجوم تستخدم نظام تليجرام"],
                    "quick_actions": ["الدفع بـ TON", "الدفع بالنجوم", "مراجعة التفاصيل"]
                },
                "ru": {
                    "title": "💳 Помощь по оплате",
                    "content": "Завершите оплату кампании:\n• Выберите способ оплаты (TON/Stars)\n• Проверьте детали кампании\n• Подтвердите сумму\n• Отследите статус платежа",
                    "tips": ["🔒 Все платежи безопасны и зашифрованы", "⚡ TON платежи обрабатываются мгновенно", "💫 Stars используют систему Telegram"],
                    "quick_actions": ["Оплатить TON", "Оплатить Stars", "Детали"]
                }
            },
            
            # Settings help
            "settings": {
                "en": {
                    "title": "⚙️ Settings Help",
                    "content": "Customize your experience:\n• Change interface language\n• View account information\n• Check campaign history\n• Manage preferences",
                    "tips": ["🌍 Language changes apply immediately", "📊 Account stats update in real-time", "🔄 Settings sync across devices"],
                    "quick_actions": ["Change Language", "Account Info", "Privacy"]
                },
                "ar": {
                    "title": "⚙️ مساعدة الإعدادات",
                    "content": "خصص تجربتك:\n• تغيير لغة الواجهة\n• عرض معلومات الحساب\n• فحص تاريخ الحملات\n• إدارة التفضيلات",
                    "tips": ["🌍 تغييرات اللغة تطبق فوراً", "📊 إحصائيات الحساب تحديث في الوقت الفعلي", "🔄 الإعدادات تتزامن عبر الأجهزة"],
                    "quick_actions": ["تغيير اللغة", "معلومات الحساب", "الخصوصية"]
                },
                "ru": {
                    "title": "⚙️ Помощь настроек",
                    "content": "Настройте ваш опыт:\n• Изменить язык интерфейса\n• Просмотр информации аккаунта\n• Проверка истории кампаний\n• Управление предпочтениями",
                    "tips": ["🌍 Изменения языка применяются сразу", "📊 Статистика аккаунта обновляется в реальном времени", "🔄 Настройки синхронизируются"],
                    "quick_actions": ["Сменить язык", "Инфо аккаунта", "Приватность"]
                }
            }
        }
        
        # Help bubble display configurations
        self.bubble_styles = {
            "compact": {
                "show_tips": True,
                "show_actions": True,
                "max_length": 200
            },
            "detailed": {
                "show_tips": True,
                "show_actions": True,
                "max_length": 500
            },
            "minimal": {
                "show_tips": False,
                "show_actions": False,
                "max_length": 100
            }
        }
        
        # Contextual triggers for automatic help
        self.auto_help_triggers = {
            "first_time_user": ["main_menu", "create_ad_start"],
            "stuck_on_step": ["select_channels", "payment_processing"],
            "error_recovery": ["payment_processing", "settings"]
        }
    
    def get_contextual_help(self, step_key: str, language: str = "en", style: str = "compact") -> Dict:
        """Get contextual help content for a specific step"""
        try:
            help_data = self.help_content.get(step_key, {}).get(language, {})
            
            if not help_data:
                # Fallback to English if language not available
                help_data = self.help_content.get(step_key, {}).get("en", {})
            
            if not help_data:
                # Generic fallback help
                return self._create_generic_help(step_key, language)
            
            # Apply style configuration
            style_config = self.bubble_styles.get(style, self.bubble_styles["compact"])
            
            formatted_help = {
                "title": help_data.get("title", f"Help for {step_key}"),
                "content": help_data.get("content", "No help available for this step."),
                "has_tips": style_config["show_tips"] and bool(help_data.get("tips")),
                "has_actions": style_config["show_actions"] and bool(help_data.get("quick_actions"))
            }
            
            if formatted_help["has_tips"]:
                formatted_help["tips"] = help_data.get("tips", [])
            
            if formatted_help["has_actions"]:
                formatted_help["quick_actions"] = help_data.get("quick_actions", [])
            
            # Truncate content if needed
            max_length = style_config["max_length"]
            if len(formatted_help["content"]) > max_length:
                formatted_help["content"] = formatted_help["content"][:max_length-3] + "..."
            
            return formatted_help
            
        except Exception as e:
            logger.error(f"❌ Error getting contextual help for {step_key}: {e}")
            return self._create_generic_help(step_key, language)
    
    def _create_generic_help(self, step_key: str, language: str) -> Dict:
        """Create generic help when specific help is not available"""
        generic_messages = {
            "en": {
                "title": f"❓ Help for {step_key.replace('_', ' ').title()}",
                "content": "This step helps you navigate through the bot. Follow the on-screen instructions or contact support if you need assistance."
            },
            "ar": {
                "title": f"❓ مساعدة لـ {step_key.replace('_', ' ')}",
                "content": "هذه الخطوة تساعدك في التنقل عبر البوت. اتبع التعليمات على الشاشة أو اتصل بالدعم إذا كنت بحاجة لمساعدة."
            },
            "ru": {
                "title": f"❓ Помощь для {step_key.replace('_', ' ')}",
                "content": "Этот шаг поможет вам навигировать по боту. Следуйте инструкциям на экране или обратитесь в поддержку."
            }
        }
        
        return generic_messages.get(language, generic_messages["en"])
    
    async def show_contextual_help_bubble(self, 
                                        message_or_query: Union[Message, CallbackQuery],
                                        step_key: str,
                                        language: str = "en",
                                        style: str = "compact",
                                        auto_dismiss: bool = True) -> bool:
        """Show contextual help bubble for a specific step"""
        try:
            help_data = self.get_contextual_help(step_key, language, style)
            
            # Create help bubble text
            bubble_text = f"{help_data['title']}\n\n{help_data['content']}"
            
            if help_data.get("has_tips") and help_data.get("tips"):
                bubble_text += "\n\n🔍 **Tips:**"
                for tip in help_data["tips"][:2]:  # Limit to 2 tips for space
                    bubble_text += f"\n{tip}"
            
            # Create help keyboard
            keyboard_buttons = []
            
            if help_data.get("has_actions") and help_data.get("quick_actions"):
                # Add quick action buttons (max 2 for compact display)
                for action in help_data["quick_actions"][:2]:
                    keyboard_buttons.append([InlineKeyboardButton(
                        text=f"⚡ {action}",
                        callback_data=f"help_action_{step_key}_{action.lower().replace(' ', '_')}"
                    )])
            
            # Add dismiss button
            dismiss_text = {
                "en": "✅ Got it!",
                "ar": "✅ فهمت!",
                "ru": "✅ Понятно!"
            }.get(language, "✅ Got it!")
            
            keyboard_buttons.append([InlineKeyboardButton(
                text=dismiss_text,
                callback_data=f"help_dismiss_{step_key}"
            )])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            # Show help bubble with animation
            transitions = get_animated_transitions()
            
            if isinstance(message_or_query, CallbackQuery):
                # Show as new message for callback queries to not interfere with main flow
                await message_or_query.message.answer(
                    bubble_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                await message_or_query.answer("📋 Help bubble shown")
            else:
                # Show as direct message
                await message_or_query.answer(
                    bubble_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            
            # Log help display
            user_id = message_or_query.from_user.id if hasattr(message_or_query, 'from_user') else None
            if user_id:
                manager = get_global_sequence_manager()
                sequence_id = manager.get_user_active_sequence(user_id)
                if sequence_id:
                    from sequence_logger import log_sequence_step
                    log_sequence_step(sequence_id, f"ContextualHelp_{step_key}", 
                                    "contextual_help_system", {
                                        "step_key": step_key,
                                        "language": language,
                                        "style": style,
                                        "help_shown": True
                                    })
            
            logger.info(f"✅ Contextual help bubble shown for step: {step_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error showing contextual help bubble: {e}")
            return False
    
    async def handle_help_action(self, callback_query: CallbackQuery, action_data: str) -> bool:
        """Handle quick action buttons in help bubbles"""
        try:
            parts = action_data.split("_")
            if len(parts) < 3:
                return False
            
            step_key = parts[2]
            action = "_".join(parts[3:])
            
            user_id = callback_query.from_user.id
            
            # Map action to actual bot functions
            action_mapping = {
                "create_ad": "create_ad",
                "my_campaigns": "show_campaigns", 
                "settings": "show_settings",
                "upload_photo": "upload_photos",
                "skip_to_text": "enter_text",
                "select_all": "select_all_channels",
                "refresh_stats": "refresh_channel_stats",
                "pay_with_ton": "pay_ton",
                "pay_with_stars": "pay_stars",
                "change_language": "language_settings"
            }
            
            if action in action_mapping:
                # Dismiss help bubble
                await callback_query.message.delete()
                await callback_query.answer(f"Executing: {action.replace('_', ' ').title()}")
                
                # Log action
                manager = get_global_sequence_manager()
                sequence_id = manager.get_user_active_sequence(user_id)
                if sequence_id:
                    from sequence_logger import log_sequence_step
                    log_sequence_step(sequence_id, f"HelpAction_{action}", 
                                    "contextual_help_system", {
                                        "step_key": step_key,
                                        "action": action,
                                        "executed": True
                                    })
                
                logger.info(f"✅ Help action executed: {action} for step {step_key}")
                return True
            else:
                await callback_query.answer("Action not available")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error handling help action: {e}")
            await callback_query.answer("Error executing action")
            return False
    
    async def handle_help_dismiss(self, callback_query: CallbackQuery, step_key: str) -> bool:
        """Handle help bubble dismissal"""
        try:
            await callback_query.message.delete()
            await callback_query.answer("Help dismissed")
            
            # Log dismissal
            user_id = callback_query.from_user.id
            manager = get_global_sequence_manager()
            sequence_id = manager.get_user_active_sequence(user_id)
            if sequence_id:
                from sequence_logger import log_sequence_step
                log_sequence_step(sequence_id, f"HelpDismiss_{step_key}", 
                                "contextual_help_system", {
                                    "step_key": step_key,
                                    "dismissed": True
                                })
            
            logger.info(f"✅ Help bubble dismissed for step: {step_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error dismissing help bubble: {e}")
            return False
    
    def should_show_auto_help(self, user_id: int, step_key: str, context: str = "normal") -> bool:
        """Determine if automatic help should be shown for a user/step"""
        try:
            # Check if user is eligible for auto help
            triggers = self.auto_help_triggers.get(context, [])
            
            if step_key not in triggers:
                return False
            
            # Additional logic can be added here:
            # - First time on this step
            # - User seems stuck (time on step)
            # - Error recovery scenario
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error determining auto help eligibility: {e}")
            return False
    
    def add_help_button_to_keyboard(self, 
                                  keyboard: InlineKeyboardMarkup, 
                                  step_key: str, 
                                  language: str = "en") -> InlineKeyboardMarkup:
        """Add help button to existing keyboard"""
        try:
            help_text = {
                "en": "❓ Help",
                "ar": "❓ مساعدة", 
                "ru": "❓ Помощь"
            }.get(language, "❓ Help")
            
            help_button = InlineKeyboardButton(
                text=help_text,
                callback_data=f"show_help_{step_key}"
            )
            
            # Create new keyboard with help button added
            new_keyboard_data = []
            
            # Copy existing rows
            for row in keyboard.inline_keyboard:
                new_keyboard_data.append(row)
            
            # Add help button as new row
            new_keyboard_data.append([help_button])
            
            return InlineKeyboardMarkup(inline_keyboard=new_keyboard_data)
            
        except Exception as e:
            logger.error(f"❌ Error adding help button to keyboard: {e}")
            return keyboard

# Global instance
contextual_help = None

def get_contextual_help_system() -> ContextualHelpSystem:
    """Get global contextual help system instance"""
    global contextual_help
    if contextual_help is None:
        contextual_help = ContextualHelpSystem()
    return contextual_help

# Convenience functions
async def show_help_bubble(message_or_query: Union[Message, CallbackQuery],
                          step_key: str,
                          language: str = "en",
                          style: str = "compact") -> bool:
    """Show contextual help bubble for a step"""
    help_system = get_contextual_help_system()
    return await help_system.show_contextual_help_bubble(
        message_or_query, step_key, language, style
    )

def add_help_to_keyboard(keyboard: InlineKeyboardMarkup, 
                        step_key: str, 
                        language: str = "en") -> InlineKeyboardMarkup:
    """Add help button to keyboard"""
    help_system = get_contextual_help_system()
    return help_system.add_help_button_to_keyboard(keyboard, step_key, language)

if __name__ == "__main__":
    print("📋 CONTEXTUAL HELP SYSTEM")
    print("=" * 40)
    
    help_system = get_contextual_help_system()
    
    print(f"Available help steps: {len(help_system.help_content)}")
    print(f"Supported languages: 3 (EN/AR/RU)")
    print(f"Bubble styles: {len(help_system.bubble_styles)}")
    print(f"Auto triggers: {len(help_system.auto_help_triggers)}")
    
    print("\n🔍 Help Steps:")
    for step_key in help_system.help_content.keys():
        step_help = help_system.get_contextual_help(step_key, "en", "compact")
        print(f"  📋 {step_key}: {step_help['title']}")
    
    print("\n📋 Contextual Help System Ready")