"""
UI Control System for I3lani Bot
Allows admins to customize all text elements in the bot interface
"""

import logging
import json
from typing import Dict, Any, Optional
from database import db

logger = logging.getLogger(__name__)

class UIControlSystem:
    """System for managing customizable UI elements"""
    
    def __init__(self):
        self.cache = {}
        self.default_texts = self._load_default_texts()
    
    def _load_default_texts(self) -> Dict[str, Dict[str, str]]:
        """Load default text configurations for all UI elements"""
        return {
            # Main Menu Buttons
            'main_menu_buttons': {
                'create_ad': {
                    'en': '📝 Create Ad',
                    'ar': '📝 إنشاء إعلان',
                    'ru': '📝 Создать рекламу'
                },
                'channel_partners': {
                    'en': '🤝 Channel Partners',
                    'ar': '🤝 شركاء القنوات',
                    'ru': '🤝 Партнеры каналов'
                },
                'share_win': {
                    'en': '🎁 Share & Win',
                    'ar': '🎁 شارك واربح',
                    'ru': '🎁 Поделись и выиграй'
                },
                'gaming_hub': {
                    'en': '🎮 Gaming Hub',
                    'ar': '🎮 مركز الألعاب',
                    'ru': '🎮 Игровой центр'
                },
                'leaderboard': {
                    'en': '🏆 Leaderboard',
                    'ar': '🏆 لوحة المتصدرين',
                    'ru': '🏆 Рейтинг'
                },
                'language_settings': {
                    'en': '🌐 Language',
                    'ar': '🌐 اللغة',
                    'ru': '🌐 Язык'
                },
                'contact_support': {
                    'en': '📞 Contact Support',
                    'ar': '📞 تواصل مع الدعم',
                    'ru': '📞 Связаться с поддержкой'
                }
            },
            
            # Welcome Messages
            'welcome_messages': {
                'new_user_welcome': {
                    'en': 'Welcome to I3lani Bot! 🎯\n\nYour professional advertising platform is ready.',
                    'ar': 'مرحباً بك في بوت I3lani! 🎯\n\nمنصة الإعلانات المهنية جاهزة لك.',
                    'ru': 'Добро пожаловать в I3lani Bot! 🎯\n\nВаша профессиональная рекламная платформа готова.'
                },
                'returning_user': {
                    'en': 'Welcome back! 👋\n\nReady to continue your advertising journey?',
                    'ar': 'أهلاً بعودتك! 👋\n\nهل أنت مستعد لمواصلة رحلتك الإعلانية؟',
                    'ru': 'Добро пожаловать обратно! 👋\n\nГотовы продолжить свое рекламное путешествие?'
                }
            },
            
            # Navigation Buttons
            'navigation_buttons': {
                'back_to_main': {
                    'en': '◀️ Back to Main',
                    'ar': '◀️ العودة للرئيسية',
                    'ru': '◀️ Назад к главной'
                },
                'continue': {
                    'en': '▶️ Continue',
                    'ar': '▶️ متابعة',
                    'ru': '▶️ Продолжить'
                },
                'cancel': {
                    'en': '❌ Cancel',
                    'ar': '❌ إلغاء',
                    'ru': '❌ Отмена'
                },
                'try_again': {
                    'en': '🔄 Try Again',
                    'ar': '🔄 حاول مرة أخرى',
                    'ru': '🔄 Попробовать снова'
                }
            },
            
            # Ad Creation Messages
            'ad_creation': {
                'upload_content': {
                    'en': '📤 Upload your ad content (text, photo, or video)',
                    'ar': '📤 ارفع محتوى إعلانك (نص، صورة، أو فيديو)',
                    'ru': '📤 Загрузите содержимое вашей рекламы (текст, фото или видео)'
                },
                'select_channels': {
                    'en': '📺 Select channels for your advertisement',
                    'ar': '📺 اختر القنوات لإعلانك',
                    'ru': '📺 Выберите каналы для вашей рекламы'
                },
                'content_received': {
                    'en': '✅ Content received! Now select your channels.',
                    'ar': '✅ تم استلام المحتوى! الآن اختر قنواتك.',
                    'ru': '✅ Контент получен! Теперь выберите каналы.'
                }
            },
            
            # Payment Messages
            'payment_messages': {
                'select_payment_method': {
                    'en': '💳 Select your payment method',
                    'ar': '💳 اختر طريقة الدفع',
                    'ru': '💳 Выберите способ оплаты'
                },
                'payment_processing': {
                    'en': '⏳ Processing your payment...',
                    'ar': '⏳ جاري معالجة دفعتك...',
                    'ru': '⏳ Обработка вашего платежа...'
                },
                'payment_successful': {
                    'en': '✅ Payment successful! Your ad is being processed.',
                    'ar': '✅ تم الدفع بنجاح! جاري معالجة إعلانك.',
                    'ru': '✅ Платеж успешен! Ваша реклама обрабатывается.'
                }
            },
            
            # Error Messages
            'error_messages': {
                'general_error': {
                    'en': '❌ An error occurred. Please try again.',
                    'ar': '❌ حدث خطأ. يرجى المحاولة مرة أخرى.',
                    'ru': '❌ Произошла ошибка. Пожалуйста, попробуйте еще раз.'
                },
                'network_error': {
                    'en': '🌐 Network error. Please check your connection.',
                    'ar': '🌐 خطأ في الشبكة. يرجى التحقق من اتصالك.',
                    'ru': '🌐 Сетевая ошибка. Проверьте подключение.'
                },
                'payment_failed': {
                    'en': '💳 Payment failed. Please try again or contact support.',
                    'ar': '💳 فشل الدفع. يرجى المحاولة مرة أخرى أو الاتصال بالدعم.',
                    'ru': '💳 Платеж не прошел. Попробуйте еще раз или обратитесь в поддержку.'
                }
            },
            
            # Success Messages
            'success_messages': {
                'ad_created': {
                    'en': '🎉 Advertisement created successfully!',
                    'ar': '🎉 تم إنشاء الإعلان بنجاح!',
                    'ru': '🎉 Реклама создана успешно!'
                },
                'settings_saved': {
                    'en': '💾 Settings saved successfully!',
                    'ar': '💾 تم حفظ الإعدادات بنجاح!',
                    'ru': '💾 Настройки сохранены успешно!'
                },
                'language_changed': {
                    'en': '🌐 Language changed successfully!',
                    'ar': '🌐 تم تغيير اللغة بنجاح!',
                    'ru': '🌐 Язык изменен успешно!'
                }
            }
        }
    
    async def get_text(self, category: str, key: str, language: str = 'en') -> str:
        """Get customized text for UI elements"""
        try:
            # Check cache first
            cache_key = f"{category}_{key}_{language}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Get from database
            custom_text = await db.get_ui_text(category, key, language)
            if custom_text:
                self.cache[cache_key] = custom_text
                return custom_text
            
            # Fall back to default
            default_text = self.default_texts.get(category, {}).get(key, {}).get(language)
            if default_text:
                self.cache[cache_key] = default_text
                return default_text
            
            # Ultimate fallback
            fallback = self.default_texts.get(category, {}).get(key, {}).get('en', f'{category}_{key}')
            self.cache[cache_key] = fallback
            return fallback
            
        except Exception as e:
            logger.error(f"Error getting UI text: {e}")
            return f"{category}_{key}"
    
    async def set_text(self, category: str, key: str, language: str, text: str) -> bool:
        """Set custom text for UI elements"""
        try:
            success = await db.set_ui_text(category, key, language, text)
            if success:
                # Update cache
                cache_key = f"{category}_{key}_{language}"
                self.cache[cache_key] = text
                logger.info(f"UI text updated: {category}.{key}.{language}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting UI text: {e}")
            return False
    
    async def reset_text(self, category: str, key: str, language: str) -> bool:
        """Reset text to default"""
        try:
            success = await db.delete_ui_text(category, key, language)
            if success:
                # Clear cache
                cache_key = f"{category}_{key}_{language}"
                if cache_key in self.cache:
                    del self.cache[cache_key]
                logger.info(f"UI text reset to default: {category}.{key}.{language}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resetting UI text: {e}")
            return False
    
    async def get_all_customizations(self) -> Dict[str, Any]:
        """Get all UI customizations"""
        try:
            return await db.get_all_ui_customizations()
        except Exception as e:
            logger.error(f"Error getting all customizations: {e}")
            return {}
    
    async def export_customizations(self) -> str:
        """Export all customizations as JSON"""
        try:
            customizations = await self.get_all_customizations()
            return json.dumps(customizations, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error exporting customizations: {e}")
            return "{}"
    
    async def import_customizations(self, json_data: str) -> bool:
        """Import customizations from JSON"""
        try:
            data = json.loads(json_data)
            success_count = 0
            
            for category, keys in data.items():
                for key, languages in keys.items():
                    for language, text in languages.items():
                        if await self.set_text(category, key, language, text):
                            success_count += 1
            
            logger.info(f"Imported {success_count} UI customizations")
            return success_count > 0
        except Exception as e:
            logger.error(f"Error importing customizations: {e}")
            return False
    
    def get_available_categories(self) -> list:
        """Get list of all available text categories"""
        return list(self.default_texts.keys())
    
    def get_category_keys(self, category: str) -> list:
        """Get all keys for a specific category"""
        return list(self.default_texts.get(category, {}).keys())
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return ['en', 'ar', 'ru']
    
    async def clear_cache(self):
        """Clear the text cache"""
        self.cache.clear()
        logger.info("UI text cache cleared")

# Global UI control system instance
ui_control = UIControlSystem()