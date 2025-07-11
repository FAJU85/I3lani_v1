#!/usr/bin/env python3
"""
Step Title System for I3lani Bot
Clear, visible step titles for each bot interaction with multilingual support
"""

import logging
from typing import Dict, Optional
from global_sequence_system import get_global_sequence_manager, log_sequence_step
from sequence_logger import get_sequence_logger

logger = get_sequence_logger(__name__)

class StepTitleManager:
    """Centralized management of step titles with multilingual support"""
    
    def __init__(self):
        self.step_titles = {
            # Main Menu and Navigation
            "main_menu": {
                "ar": "(القائمة الرئيسية)",
                "en": "(Main Menu)",
                "ru": "(Главное меню)"
            },
            "settings": {
                "ar": "(الإعدادات)",
                "en": "(Settings)",
                "ru": "(Настройки)"
            },
            "help": {
                "ar": "(المساعدة)",
                "en": "(Help)",
                "ru": "(Помощь)"
            },
            "language_selection": {
                "ar": "(اختيار اللغة)",
                "en": "(Language Selection)",
                "ru": "(Выбор языка)"
            },
            
            # Ad Creation Flow
            "create_ad_start": {
                "ar": "(إنشاء إعلان)",
                "en": "(Create Ad)",
                "ru": "(Создать объявление)"
            },
            "upload_image": {
                "ar": "(اختيار الصورة)",
                "en": "(Upload Image)",
                "ru": "(Загрузить изображение)"
            },
            "upload_video": {
                "ar": "(اختيار الفيديو)",
                "en": "(Upload Video)",
                "ru": "(Загрузить видео)"
            },
            "enter_text": {
                "ar": "(كتابة النص)",
                "en": "(Enter Ad Text)",
                "ru": "(Введите текст объявления)"
            },
            "select_channels": {
                "ar": "(اختيار القنوات)",
                "en": "(Select Channels)",
                "ru": "(Выбрать каналы)"
            },
            "select_days": {
                "ar": "(اختيار عدد الأيام)",
                "en": "(Select Days)",
                "ru": "(Выбрать дни)"
            },
            "posts_per_day": {
                "ar": "(عدد مرات النشر في اليوم)",
                "en": "(Posts Per Day)",
                "ru": "(Постов в день)"
            },
            "confirm_campaign": {
                "ar": "(تأكيد الحملة)",
                "en": "(Confirm Campaign)",
                "ru": "(Подтвердить кампанию)"
            },
            
            # Payment Flow
            "choose_payment": {
                "ar": "(اختيار طريقة الدفع)",
                "en": "(Choose Payment Method)",
                "ru": "(Выберите способ оплаты)"
            },
            "payment_ton": {
                "ar": "(دفع بـ TON)",
                "en": "(Pay with TON)",
                "ru": "(Оплата TON)"
            },
            "payment_stars": {
                "ar": "(دفع بالنجوم)",
                "en": "(Pay with Stars)",
                "ru": "(Оплата звездами)"
            },
            "confirm_payment": {
                "ar": "(تأكيد الدفع)",
                "en": "(Confirm Payment)",
                "ru": "(Подтвердить платеж)"
            },
            "payment_waiting": {
                "ar": "(انتظار الدفع)",
                "en": "(Waiting for Payment)",
                "ru": "(Ожидание платежа)"
            },
            "payment_success": {
                "ar": "(تم الدفع بنجاح)",
                "en": "(Payment Successful)",
                "ru": "(Платеж успешен)"
            },
            
            # Campaign Management
            "my_campaigns": {
                "ar": "(حملاتي)",
                "en": "(My Campaigns)",
                "ru": "(Мои кампании)"
            },
            "campaign_details": {
                "ar": "(تفاصيل الحملة)",
                "en": "(Campaign Details)",
                "ru": "(Детали кампании)"
            },
            "campaign_stats": {
                "ar": "(إحصائيات الحملة)",
                "en": "(Campaign Statistics)",
                "ru": "(Статистика кампании)"
            },
            
            # Publishing Flow
            "publish_ad": {
                "ar": "(نشر الإعلان)",
                "en": "(Publish Ad)",
                "ru": "(Опубликовать объявление)"
            },
            "publishing_progress": {
                "ar": "(تقدم النشر)",
                "en": "(Publishing Progress)",
                "ru": "(Прогресс публикации)"
            },
            "publishing_complete": {
                "ar": "(تم النشر بنجاح)",
                "en": "(Publishing Complete)",
                "ru": "(Публикация завершена)"
            },
            
            # Admin Panel
            "admin_panel": {
                "ar": "(لوحة الإدارة)",
                "en": "(Admin Panel)",
                "ru": "(Панель администратора)"
            },
            "channel_management": {
                "ar": "(إدارة القنوات)",
                "en": "(Channel Management)",
                "ru": "(Управление каналами)"
            },
            "user_management": {
                "ar": "(إدارة المستخدمين)",
                "en": "(User Management)",
                "ru": "(Управление пользователями)"
            },
            "pricing_management": {
                "ar": "(إدارة الأسعار)",
                "en": "(Pricing Management)",
                "ru": "(Управление ценами)"
            },
            "statistics": {
                "ar": "(الإحصائيات)",
                "en": "(Statistics)",
                "ru": "(Статистика)"
            },
            
            # Referral System
            "referral_program": {
                "ar": "(برنامج الإحالة)",
                "en": "(Referral Program)",
                "ru": "(Реферальная программа)"
            },
            "referral_stats": {
                "ar": "(إحصائيات الإحالة)",
                "en": "(Referral Statistics)",
                "ru": "(Статистика рефералов)"
            },
            "generate_referral": {
                "ar": "(إنشاء رابط إحالة)",
                "en": "(Generate Referral Link)",
                "ru": "(Создать реферальную ссылку)"
            },
            
            # Support and Contact
            "contact_support": {
                "ar": "(تواصل معنا)",
                "en": "(Contact Support)",
                "ru": "(Связаться с поддержкой)"
            },
            "submit_feedback": {
                "ar": "(إرسال تعليق)",
                "en": "(Submit Feedback)",
                "ru": "(Отправить отзыв)"
            },
            "report_issue": {
                "ar": "(الإبلاغ عن مشكلة)",
                "en": "(Report Issue)",
                "ru": "(Сообщить о проблеме)"
            },
            
            # Error States
            "error_state": {
                "ar": "(خطأ في النظام)",
                "en": "(System Error)",
                "ru": "(Системная ошибка)"
            },
            "maintenance_mode": {
                "ar": "(وضع الصيانة)",
                "en": "(Maintenance Mode)",
                "ru": "(Режим обслуживания)"
            }
        }
        
        # Step title formatting options
        self.title_formats = {
            "default": "{title}",
            "with_icon": "🧭 {title}",
            "with_arrow": "➡️ {title}",
            "with_step": "📍 {title}",
            "bordered": "═══ {title} ═══"
        }
    
    def get_step_title(self, step_key: str, language: str = "en", 
                      format_style: str = "default") -> str:
        """Get formatted step title for given language"""
        try:
            if step_key not in self.step_titles:
                logger.warning(f"⚠️ Step title not found: {step_key}")
                return f"({step_key.replace('_', ' ').title()})"
            
            if language not in self.step_titles[step_key]:
                logger.warning(f"⚠️ Language {language} not found for step {step_key}")
                language = "en"  # Fallback to English
            
            title = self.step_titles[step_key][language]
            
            if format_style in self.title_formats:
                title = self.title_formats[format_style].format(title=title)
            
            return title
            
        except Exception as e:
            logger.error(f"❌ Error getting step title: {e}")
            return f"({step_key.replace('_', ' ').title()})"
    
    def create_titled_message(self, step_key: str, content: str, 
                             language: str = "en", user_id: int = None,
                             format_style: str = "default") -> str:
        """Create message with step title at the beginning"""
        try:
            title = self.get_step_title(step_key, language, format_style)
            
            # Log step with sequence system if user_id provided
            if user_id:
                manager = get_global_sequence_manager()
                sequence_id = manager.get_user_active_sequence(user_id)
                if sequence_id:
                    log_sequence_step(sequence_id, f"StepTitle_{step_key}", "step_title_system", {
                        "step_key": step_key,
                        "language": language,
                        "format_style": format_style,
                        "title": title
                    })
            
            # Combine title with content
            titled_message = f"{title}\n\n{content}"
            
            logger.info(f"✅ Created titled message for step: {step_key} ({language})")
            return titled_message
            
        except Exception as e:
            logger.error(f"❌ Error creating titled message: {e}")
            return content  # Return original content if error
    
    def get_all_steps_for_language(self, language: str = "en") -> Dict[str, str]:
        """Get all step titles for a specific language"""
        try:
            result = {}
            for step_key, translations in self.step_titles.items():
                if language in translations:
                    result[step_key] = translations[language]
                else:
                    result[step_key] = translations.get("en", step_key)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting all steps for language: {e}")
            return {}
    
    def add_custom_step_title(self, step_key: str, titles: Dict[str, str]):
        """Add custom step title for dynamic steps"""
        try:
            self.step_titles[step_key] = titles
            logger.info(f"✅ Added custom step title: {step_key}")
            
        except Exception as e:
            logger.error(f"❌ Error adding custom step title: {e}")
    
    def validate_step_coverage(self) -> Dict[str, any]:
        """Validate that all languages have complete step coverage"""
        try:
            languages = ["ar", "en", "ru"]
            validation_report = {
                "total_steps": len(self.step_titles),
                "languages_checked": languages,
                "missing_translations": {},
                "coverage_complete": True
            }
            
            for step_key, translations in self.step_titles.items():
                for lang in languages:
                    if lang not in translations:
                        if lang not in validation_report["missing_translations"]:
                            validation_report["missing_translations"][lang] = []
                        validation_report["missing_translations"][lang].append(step_key)
                        validation_report["coverage_complete"] = False
            
            logger.info(f"📊 Step title validation complete")
            logger.info(f"   Total steps: {validation_report['total_steps']}")
            logger.info(f"   Coverage complete: {validation_report['coverage_complete']}")
            
            if not validation_report["coverage_complete"]:
                for lang, missing in validation_report["missing_translations"].items():
                    logger.warning(f"   Missing {lang}: {len(missing)} steps")
            
            return validation_report
            
        except Exception as e:
            logger.error(f"❌ Error validating step coverage: {e}")
            return {"coverage_complete": False, "error": str(e)}

# Global instance
step_title_manager = None

def get_step_title_manager() -> StepTitleManager:
    """Get global step title manager instance"""
    global step_title_manager
    if step_title_manager is None:
        step_title_manager = StepTitleManager()
    return step_title_manager

def get_step_title(step_key: str, language: str = "en", 
                  format_style: str = "default") -> str:
    """Helper function to get step title"""
    return get_step_title_manager().get_step_title(step_key, language, format_style)

def create_titled_message(step_key: str, content: str, language: str = "en", 
                         user_id: int = None, format_style: str = "default") -> str:
    """Helper function to create titled message"""
    return get_step_title_manager().create_titled_message(
        step_key, content, language, user_id, format_style
    )

def validate_step_title_system() -> bool:
    """Validate the step title system"""
    try:
        manager = get_step_title_manager()
        validation = manager.validate_step_coverage()
        
        print("🧭 STEP TITLE SYSTEM VALIDATION")
        print("=" * 40)
        
        print(f"Total Steps: {validation['total_steps']}")
        print(f"Languages Supported: {', '.join(validation['languages_checked'])}")
        print(f"Coverage Complete: {'✅ YES' if validation['coverage_complete'] else '❌ NO'}")
        
        if not validation["coverage_complete"]:
            print("\nMissing Translations:")
            for lang, missing in validation["missing_translations"].items():
                print(f"  {lang.upper()}: {len(missing)} missing")
                for step in missing[:5]:  # Show first 5 missing
                    print(f"    - {step}")
                if len(missing) > 5:
                    print(f"    ... and {len(missing) - 5} more")
        
        return validation["coverage_complete"]
        
    except Exception as e:
        print(f"❌ Error validating step title system: {e}")
        return False

if __name__ == "__main__":
    # Run validation
    success = validate_step_title_system()
    
    # Test examples
    print(f"\n🧪 TESTING STEP TITLES:")
    manager = get_step_title_manager()
    
    test_steps = ["main_menu", "create_ad_start", "select_channels", "payment_ton"]
    languages = ["ar", "en", "ru"]
    
    for step in test_steps:
        print(f"\n{step}:")
        for lang in languages:
            title = manager.get_step_title(step, lang)
            print(f"  {lang}: {title}")
    
    print(f"\n✅ Step Title System {'Ready' if success else 'Needs Attention'}")