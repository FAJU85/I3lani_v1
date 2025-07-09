"""
Comprehensive Confirmation System for I3lani Bot
Prevents accidental actions with summary and confirmation prompts
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from languages import get_text
from database import db
from modern_keyboard import create_modern_confirmation
import logging

logger = logging.getLogger(__name__)

class ConfirmationSystem:
    """Handles all confirmation prompts for critical actions"""
    
    def __init__(self):
        self.confirmation_timeout = 300  # 5 minutes timeout
        
    async def create_ad_submission_confirmation(self, user_id: int, language: str, 
                                              ad_data: Dict, pricing_data: Dict) -> Dict:
        """Create confirmation for ad submission"""
        
        # Get channel names
        channel_names = []
        if ad_data.get('selected_channels'):
            for channel_id in ad_data['selected_channels']:
                channel = await db.get_channel_by_id(channel_id)
                if channel:
                    channel_names.append(channel.get('name', f'Channel {channel_id}'))
        
        # Build confirmation text
        confirmation_text = {
            'en': f"""📝 <b>Review Your Advertisement</b>
            
<b>📋 Ad Details:</b>
• <b>Content:</b> {ad_data.get('ad_text', 'Photo/Video only')[:100]}{'...' if len(ad_data.get('ad_text', '')) > 100 else ''}
• <b>Photos:</b> {len(ad_data.get('photos', []))} photo(s)
• <b>Videos:</b> {len(ad_data.get('videos', []))} video(s)

<b>📺 Selected Channels:</b>
{chr(10).join([f'• {name}' for name in channel_names]) if channel_names else '• None selected'}

<b>⏰ Campaign Duration:</b>
• <b>Duration:</b> {ad_data.get('duration_days', 1)} day(s)
• <b>Posts per day:</b> {ad_data.get('posts_per_day', 1)}
• <b>Total posts:</b> {ad_data.get('total_posts', 1)}

<b>💰 Pricing:</b>
• <b>Base cost:</b> ${pricing_data.get('base_cost', 0):.2f}
• <b>Discount:</b> {pricing_data.get('discount_percent', 0)}% (${pricing_data.get('discount_amount', 0):.2f})
• <b>Final price:</b> ${pricing_data.get('final_price', 0):.2f}

<b>⚠️ Are you sure you want to proceed with this advertisement?</b>
This action cannot be undone after payment is processed.""",
            
            'ar': f"""📝 <b>مراجعة إعلانك</b>
            
<b>📋 تفاصيل الإعلان:</b>
• <b>المحتوى:</b> {ad_data.get('ad_text', 'صورة/فيديو فقط')[:100]}{'...' if len(ad_data.get('ad_text', '')) > 100 else ''}
• <b>الصور:</b> {len(ad_data.get('photos', []))} صورة
• <b>الفيديوهات:</b> {len(ad_data.get('videos', []))} فيديو

<b>📺 القنوات المختارة:</b>
{chr(10).join([f'• {name}' for name in channel_names]) if channel_names else '• لم يتم اختيار قنوات'}

<b>⏰ مدة الحملة:</b>
• <b>المدة:</b> {ad_data.get('duration_days', 1)} يوم
• <b>منشورات يومياً:</b> {ad_data.get('posts_per_day', 1)}
• <b>إجمالي المنشورات:</b> {ad_data.get('total_posts', 1)}

<b>💰 التسعير:</b>
• <b>التكلفة الأساسية:</b> ${pricing_data.get('base_cost', 0):.2f}
• <b>الخصم:</b> {pricing_data.get('discount_percent', 0)}% (${pricing_data.get('discount_amount', 0):.2f})
• <b>السعر النهائي:</b> ${pricing_data.get('final_price', 0):.2f}

<b>⚠️ هل أنت متأكد من المتابعة مع هذا الإعلان؟</b>
لا يمكن التراجع عن هذا الإجراء بعد معالجة الدفع.""",
            
            'ru': f"""📝 <b>Проверьте вашу рекламу</b>
            
<b>📋 Детали объявления:</b>
• <b>Контент:</b> {ad_data.get('ad_text', 'Только фото/видео')[:100]}{'...' if len(ad_data.get('ad_text', '')) > 100 else ''}
• <b>Фото:</b> {len(ad_data.get('photos', []))} фото
• <b>Видео:</b> {len(ad_data.get('videos', []))} видео

<b>📺 Выбранные каналы:</b>
{chr(10).join([f'• {name}' for name in channel_names]) if channel_names else '• Каналы не выбраны'}

<b>⏰ Длительность кампании:</b>
• <b>Продолжительность:</b> {ad_data.get('duration_days', 1)} дней
• <b>Постов в день:</b> {ad_data.get('posts_per_day', 1)}
• <b>Всего постов:</b> {ad_data.get('total_posts', 1)}

<b>💰 Цена:</b>
• <b>Базовая стоимость:</b> ${pricing_data.get('base_cost', 0):.2f}
• <b>Скидка:</b> {pricing_data.get('discount_percent', 0)}% (${pricing_data.get('discount_amount', 0):.2f})
• <b>Итоговая цена:</b> ${pricing_data.get('final_price', 0):.2f}

<b>⚠️ Вы уверены, что хотите продолжить с этим объявлением?</b>
Это действие нельзя отменить после обработки платежа."""
        }
        
        # Create confirmation keyboard
        keyboard = self._create_confirmation_keyboard(language, 'ad_submission')
        
        return {
            'message': confirmation_text.get(language, confirmation_text['en']),
            'keyboard': keyboard,
            'action_type': 'ad_submission',
            'data': ad_data,
            'pricing': pricing_data
        }
    
    async def create_payment_confirmation(self, user_id: int, language: str, 
                                        payment_data: Dict) -> Dict:
        """Create confirmation for payment processing"""
        
        confirmation_text = {
            'en': f"""💳 <b>Payment Confirmation</b>
            
<b>💰 Payment Details:</b>
• <b>Amount:</b> {payment_data.get('amount', 0):.2f} {payment_data.get('currency', 'USD')}
• <b>Method:</b> {payment_data.get('payment_method', 'Unknown').upper()}
• <b>Campaign:</b> {payment_data.get('campaign_name', 'New Advertisement')}

<b>📋 What you're paying for:</b>
• <b>Ad duration:</b> {payment_data.get('duration_days', 1)} days
• <b>Channels:</b> {payment_data.get('channel_count', 0)} channel(s)
• <b>Total posts:</b> {payment_data.get('total_posts', 1)}

<b>📄 Agreement:</b>
By confirming this payment, you agree to our Usage Agreement and Terms of Service.

<b>⚠️ Confirm payment processing?</b>
This action will charge your account immediately.""",
            
            'ar': f"""💳 <b>تأكيد الدفع</b>
            
<b>💰 تفاصيل الدفع:</b>
• <b>المبلغ:</b> {payment_data.get('amount', 0):.2f} {payment_data.get('currency', 'USD')}
• <b>الطريقة:</b> {payment_data.get('payment_method', 'غير معروف').upper()}
• <b>الحملة:</b> {payment_data.get('campaign_name', 'إعلان جديد')}

<b>📋 ما تدفع مقابله:</b>
• <b>مدة الإعلان:</b> {payment_data.get('duration_days', 1)} يوم
• <b>القنوات:</b> {payment_data.get('channel_count', 0)} قناة
• <b>إجمالي المنشورات:</b> {payment_data.get('total_posts', 1)}

<b>📄 الاتفاقية:</b>
من خلال تأكيد هذا الدفع، فإنك توافق على اتفاقية الاستخدام وشروط الخدمة.

<b>⚠️ تأكيد معالجة الدفع؟</b>
سيتم خصم المبلغ من حسابك فوراً.""",
            
            'ru': f"""💳 <b>Подтверждение платежа</b>
            
<b>💰 Детали платежа:</b>
• <b>Сумма:</b> {payment_data.get('amount', 0):.2f} {payment_data.get('currency', 'USD')}
• <b>Метод:</b> {payment_data.get('payment_method', 'Неизвестно').upper()}
• <b>Кампания:</b> {payment_data.get('campaign_name', 'Новое объявление')}

<b>📋 За что вы платите:</b>
• <b>Длительность рекламы:</b> {payment_data.get('duration_days', 1)} дней
• <b>Каналы:</b> {payment_data.get('channel_count', 0)} канал(ов)
• <b>Всего постов:</b> {payment_data.get('total_posts', 1)}

<b>📄 Соглашение:</b>
Подтверждая этот платеж, вы соглашаетесь с нашим Пользовательским соглашением и Условиями обслуживания.

<b>⚠️ Подтвердить обработку платежа?</b>
Эта операция немедленно спишет средства с вашего счета."""
        }
        
        keyboard = self._create_confirmation_keyboard(language, 'payment_processing')
        
        return {
            'message': confirmation_text.get(language, confirmation_text['en']),
            'keyboard': keyboard,
            'action_type': 'payment_processing',
            'data': payment_data
        }
    
    async def create_channel_selection_confirmation(self, user_id: int, language: str, 
                                                  selected_channels: List[int]) -> Dict:
        """Create confirmation for channel selection"""
        
        channel_names = []
        total_reach = 0
        
        for channel_id in selected_channels:
            channel = await db.get_channel_by_id(channel_id)
            if channel:
                channel_names.append(f"• {channel.get('name', 'Unknown')} ({channel.get('subscriber_count', 0):,} subscribers)")
                total_reach += channel.get('subscriber_count', 0)
        
        confirmation_text = {
            'en': f"""📺 <b>Channel Selection Confirmation</b>
            
<b>Selected Channels ({len(selected_channels)}):</b>
{chr(10).join(channel_names)}

<b>📊 Total Reach:</b> {total_reach:,} subscribers

<b>⚠️ Confirm channel selection?</b>
You can still change channels in the next step.""",
            
            'ar': f"""📺 <b>تأكيد اختيار القنوات</b>
            
<b>القنوات المختارة ({len(selected_channels)}):</b>
{chr(10).join(channel_names)}

<b>📊 إجمالي الوصول:</b> {total_reach:,} مشترك

<b>⚠️ تأكيد اختيار القنوات؟</b>
يمكنك تغيير القنوات في الخطوة التالية.""",
            
            'ru': f"""📺 <b>Подтверждение выбора каналов</b>
            
<b>Выбранные каналы ({len(selected_channels)}):</b>
{chr(10).join(channel_names)}

<b>📊 Общий охват:</b> {total_reach:,} подписчиков

<b>⚠️ Подтвердить выбор каналов?</b>
Вы все еще можете изменить каналы на следующем шаге."""
        }
        
        keyboard = self._create_confirmation_keyboard(language, 'channel_selection')
        
        return {
            'message': confirmation_text.get(language, confirmation_text['en']),
            'keyboard': keyboard,
            'action_type': 'channel_selection',
            'data': {'selected_channels': selected_channels, 'total_reach': total_reach}
        }
    
    async def create_ad_deletion_confirmation(self, user_id: int, language: str, 
                                            ad_id: int) -> Dict:
        """Create confirmation for ad deletion"""
        
        ad = await db.get_ad_by_id(ad_id)
        if not ad:
            return None
        
        confirmation_text = {
            'en': f"""🗑️ <b>Delete Advertisement</b>
            
<b>📋 Ad to Delete:</b>
• <b>ID:</b> {ad_id}
• <b>Content:</b> {ad.get('text', 'No text')[:100]}{'...' if len(ad.get('text', '')) > 100 else ''}
• <b>Status:</b> {ad.get('status', 'Unknown')}
• <b>Created:</b> {ad.get('created_at', 'Unknown')}

<b>⚠️ Are you sure you want to delete this ad?</b>
This action cannot be undone. If the ad is active, it will be stopped immediately.""",
            
            'ar': f"""🗑️ <b>حذف الإعلان</b>
            
<b>📋 الإعلان المراد حذفه:</b>
• <b>المعرف:</b> {ad_id}
• <b>المحتوى:</b> {ad.get('text', 'لا يوجد نص')[:100]}{'...' if len(ad.get('text', '')) > 100 else ''}
• <b>الحالة:</b> {ad.get('status', 'غير معروف')}
• <b>تم الإنشاء:</b> {ad.get('created_at', 'غير معروف')}

<b>⚠️ هل أنت متأكد من حذف هذا الإعلان؟</b>
لا يمكن التراجع عن هذا الإجراء. إذا كان الإعلان نشطاً، فسيتم إيقافه فوراً.""",
            
            'ru': f"""🗑️ <b>Удалить объявление</b>
            
<b>📋 Объявление для удаления:</b>
• <b>ID:</b> {ad_id}
• <b>Контент:</b> {ad.get('text', 'Нет текста')[:100]}{'...' if len(ad.get('text', '')) > 100 else ''}
• <b>Статус:</b> {ad.get('status', 'Неизвестно')}
• <b>Создано:</b> {ad.get('created_at', 'Неизвестно')}

<b>⚠️ Вы уверены, что хотите удалить это объявление?</b>
Это действие нельзя отменить. Если объявление активно, оно будет остановлено немедленно."""
        }
        
        keyboard = self._create_confirmation_keyboard(language, 'ad_deletion')
        
        return {
            'message': confirmation_text.get(language, confirmation_text['en']),
            'keyboard': keyboard,
            'action_type': 'ad_deletion',
            'data': {'ad_id': ad_id, 'ad_data': ad}
        }
    
    def _create_confirmation_keyboard(self, language: str, action_type: str) -> InlineKeyboardMarkup:
        """Create confirmation keyboard with confirm/cancel buttons"""
        
        confirm_text = {
            'en': '✅ Confirm',
            'ar': '✅ تأكيد',
            'ru': '✅ Подтвердить'
        }
        
        cancel_text = {
            'en': '❌ Cancel',
            'ar': '❌ إلغاء',
            'ru': '❌ Отмена'
        }
        
        edit_text = {
            'en': '✏️ Edit',
            'ar': '✏️ تعديل',
            'ru': '✏️ Редактировать'
        }
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=confirm_text.get(language, confirm_text['en']),
                    callback_data=f"confirm_{action_type}"
                ),
                InlineKeyboardButton(
                    text=cancel_text.get(language, cancel_text['en']),
                    callback_data=f"cancel_{action_type}"
                )
            ]
        ])
        
        # Add edit button for certain actions
        if action_type in ['ad_submission', 'channel_selection']:
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=edit_text.get(language, edit_text['en']),
                    callback_data=f"edit_{action_type}"
                )
            ])
        
        return keyboard
    
    async def log_confirmation_action(self, user_id: int, action_type: str, 
                                    confirmed: bool, data: Dict = None):
        """Log confirmation action for analytics"""
        try:
            await db.log_user_action(
                user_id=user_id,
                action_type=f"confirmation_{action_type}",
                action_data={
                    'confirmed': confirmed,
                    'timestamp': datetime.now().isoformat(),
                    'data': data or {}
                }
            )
        except Exception as e:
            logger.error(f"Error logging confirmation action: {e}")

# Global instance
confirmation_system = ConfirmationSystem()