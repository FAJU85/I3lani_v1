#!/usr/bin/env python3
"""
Campaign Management Handlers
User interface for viewing and managing campaigns
"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from languages import get_text
from database import get_user_language
from campaign_management import get_user_campaign_list, get_campaign_id_card

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

class CampaignStates(StatesGroup):
    """States for campaign management"""
    viewing_campaign = State()
    managing_campaigns = State()

@router.callback_query(F.data == "my_campaigns")
async def show_my_campaigns_handler(callback_query: CallbackQuery, state: FSMContext):
    """Show user's campaigns"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Get user's campaigns
        campaigns = await get_user_campaign_list(user_id, limit=10)
        
        if not campaigns:
            if language == 'ar':
                text = """📋 **حملاتك الإعلانية**

لا توجد حملات إعلانية حالياً.

قم بإنشاء حملة جديدة للبدء في الإعلان عبر قنواتنا المتميزة!"""
            elif language == 'ru':
                text = """📋 **Ваши рекламные кампании**

У вас пока нет активных кампаний.

Создайте новую кампанию, чтобы начать рекламировать в наших каналах!"""
            else:
                text = """📋 **Your Ad Campaigns**

You don't have any campaigns yet.

Create a new campaign to start advertising across our premium channels!"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Create New Campaign", callback_data="create_ad")],
                [InlineKeyboardButton(text="🏠 Back to Main", callback_data="back_to_main")]
            ])
        
        else:
            # Create campaigns list
            if language == 'ar':
                text = f"""📋 **حملاتك الإعلانية ({len(campaigns)})**

إليك قائمة بحملاتك الإعلانية الأخيرة:

"""
            elif language == 'ru':
                text = f"""📋 **Ваши рекламные кампании ({len(campaigns)})**

Вот список ваших последних рекламных кампаний:

"""
            else:
                text = f"""📋 **Your Ad Campaigns ({len(campaigns)})**

Here are your recent advertising campaigns:

"""
            
            # Add campaign summaries
            for i, campaign in enumerate(campaigns, 1):
                status_emoji = "🟢" if campaign['status'] == 'active' else "🔴"
                
                if language == 'ar':
                    text += f"""**{i}. {campaign['campaign_id']}** {status_emoji}
• الحالة: {campaign['status']}
• المدة: {campaign['duration_days']} أيام
• القنوات: {campaign['channel_count']}
• المنشورات: {campaign.get('posts_published', 0)}/{campaign['total_posts']}

"""
                elif language == 'ru':
                    text += f"""**{i}. {campaign['campaign_id']}** {status_emoji}
• Статус: {campaign['status']}
• Длительность: {campaign['duration_days']} дней
• Каналы: {campaign['channel_count']}
• Посты: {campaign.get('posts_published', 0)}/{campaign['total_posts']}

"""
                else:
                    text += f"""**{i}. {campaign['campaign_id']}** {status_emoji}
• Status: {campaign['status']}
• Duration: {campaign['duration_days']} days
• Channels: {campaign['channel_count']}
• Posts: {campaign.get('posts_published', 0)}/{campaign['total_posts']}

"""
            
            # Create keyboard with campaign buttons
            keyboard_buttons = []
            
            for campaign in campaigns[:5]:  # Show first 5 campaigns
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"📋 {campaign['campaign_id']}", 
                        callback_data=f"view_campaign_{campaign['campaign_id']}"
                    )
                ])
            
            # Add navigation buttons
            keyboard_buttons.extend([
                [InlineKeyboardButton(text="🚀 Create New Campaign", callback_data="create_ad")],
                [InlineKeyboardButton(text="🔄 Refresh", callback_data="my_campaigns")],
                [InlineKeyboardButton(text="🏠 Back to Main", callback_data="back_to_main")]
            ])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback_query.message.edit_text(
            text, 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        await callback_query.answer()
        logger.info(f"✅ Campaigns list shown to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error showing campaigns: {e}")
        await callback_query.answer("Error loading campaigns")

@router.callback_query(F.data.startswith("view_campaign_"))
async def view_campaign_handler(callback_query: CallbackQuery, state: FSMContext):
    """View specific campaign details"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Extract campaign ID from callback data
        campaign_id = callback_query.data.replace("view_campaign_", "")
        
        # Get campaign ID card with language support
        id_card = await get_campaign_id_card(campaign_id, language)
        
        if not id_card or id_card == "Campaign not found":
            if language == 'ar':
                text = "❌ لم يتم العثور على الحملة الإعلانية"
            elif language == 'ru':
                text = "❌ Рекламная кампания не найдена"
            else:
                text = "❌ Campaign not found"
            
            await callback_query.answer(text)
            return
        
        # Create navigation keyboard
        if language == 'ar':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 إحصائيات الحملة", callback_data=f"campaign_stats_{campaign_id}")],
                [InlineKeyboardButton(text="📋 جميع الحملات", callback_data="my_campaigns")],
                [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")]
            ])
        elif language == 'ru':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Статистика кампании", callback_data=f"campaign_stats_{campaign_id}")],
                [InlineKeyboardButton(text="📋 Все кампании", callback_data="my_campaigns")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Campaign Stats", callback_data=f"campaign_stats_{campaign_id}")],
                [InlineKeyboardButton(text="📋 All Campaigns", callback_data="my_campaigns")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
        
        await callback_query.message.edit_text(
            id_card, 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        await callback_query.answer()
        logger.info(f"✅ Campaign {campaign_id} details shown to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error viewing campaign: {e}")
        await callback_query.answer("Error loading campaign details")

@router.callback_query(F.data.startswith("campaign_stats_"))
async def campaign_stats_handler(callback_query: CallbackQuery, state: FSMContext):
    """Show campaign statistics"""
    user_id = callback_query.from_user.id
    language = await get_user_language(user_id)
    
    try:
        # Extract campaign ID from callback data
        campaign_id = callback_query.data.replace("campaign_stats_", "")
        
        # Get campaign details for stats
        from campaign_management import get_campaign_details
        campaign = await get_campaign_details(campaign_id)
        
        if not campaign:
            if language == 'ar':
                text = "❌ لم يتم العثور على الحملة الإعلانية"
            elif language == 'ru':
                text = "❌ Рекламная кампания не найдена"
            else:
                text = "❌ Campaign not found"
            
            await callback_query.answer(text)
            return
        
        # Create detailed statistics
        if language == 'ar':
            text = f"""📊 **إحصائيات الحملة التفصيلية**

**معرف الحملة:** {campaign['campaign_id']}

**📈 الأداء**
• المنشورات المنشورة: {campaign.get('posts_published', 0)}/{campaign['total_posts']}
• معدل التفاعل: {campaign.get('engagement_score', 0.0):.1f}%
• معدل النقر: {campaign.get('click_through_rate', 0.0):.1f}%

**💰 المعلومات المالية**
• المبلغ المدفوع: {campaign['payment_amount']:.3f} {campaign['payment_method']}
• رقم المعاملة: {campaign['payment_memo']}

**📅 التوقيت**
• تاريخ البدء: {campaign['start_date'][:10]}
• تاريخ الانتهاء: {campaign['end_date'][:10]}
• المدة: {campaign['duration_days']} أيام

**📢 القنوات**
• عدد القنوات: {campaign['channel_count']}
• إجمالي المتابعين: {campaign['total_reach']}

**آخر تحديث:** {campaign['updated_at'][:16]}"""
        elif language == 'ru':
            text = f"""📊 **Подробная статистика кампании**

**ID кампании:** {campaign['campaign_id']}

**📈 Производительность**
• Опубликовано постов: {campaign.get('posts_published', 0)}/{campaign['total_posts']}
• Показатель вовлечения: {campaign.get('engagement_score', 0.0):.1f}%
• Кликабельность: {campaign.get('click_through_rate', 0.0):.1f}%

**💰 Финансовая информация**
• Сумма платежа: {campaign['payment_amount']:.3f} {campaign['payment_method']}
• ID транзакции: {campaign['payment_memo']}

**📅 Временные рамки**
• Дата начала: {campaign['start_date'][:10]}
• Дата окончания: {campaign['end_date'][:10]}
• Продолжительность: {campaign['duration_days']} дней

**📢 Каналы**
• Количество каналов: {campaign['channel_count']}
• Общий охват: {campaign['total_reach']}

**Последнее обновление:** {campaign['updated_at'][:16]}"""
        else:
            text = f"""📊 **Detailed Campaign Statistics**

**Campaign ID:** {campaign['campaign_id']}

**📈 Performance**
• Posts Published: {campaign.get('posts_published', 0)}/{campaign['total_posts']}
• Engagement Score: {campaign.get('engagement_score', 0.0):.1f}%
• Click-Through Rate: {campaign.get('click_through_rate', 0.0):.1f}%

**💰 Financial Information**
• Payment Amount: {campaign['payment_amount']:.3f} {campaign['payment_method']}
• Transaction ID: {campaign['payment_memo']}

**📅 Timeline**
• Start Date: {campaign['start_date'][:10]}
• End Date: {campaign['end_date'][:10]}
• Duration: {campaign['duration_days']} days

**📢 Channels**
• Channel Count: {campaign['channel_count']}
• Total Reach: {campaign['total_reach']}

**Last Updated:** {campaign['updated_at'][:16]}"""
        
        # Create navigation keyboard
        if language == 'ar':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 تفاصيل الحملة", callback_data=f"view_campaign_{campaign_id}")],
                [InlineKeyboardButton(text="📋 جميع الحملات", callback_data="my_campaigns")],
                [InlineKeyboardButton(text="🏠 القائمة الرئيسية", callback_data="back_to_main")]
            ])
        elif language == 'ru':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Детали кампании", callback_data=f"view_campaign_{campaign_id}")],
                [InlineKeyboardButton(text="📋 Все кампании", callback_data="my_campaigns")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Campaign Details", callback_data=f"view_campaign_{campaign_id}")],
                [InlineKeyboardButton(text="📋 All Campaigns", callback_data="my_campaigns")],
                [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back_to_main")]
            ])
        
        await callback_query.message.edit_text(
            text, 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        await callback_query.answer()
        logger.info(f"✅ Campaign {campaign_id} statistics shown to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error showing campaign stats: {e}")
        await callback_query.answer("Error loading campaign statistics")

def setup_campaign_handlers(dp):
    """Setup campaign handlers"""
    dp.include_router(router)
    logger.info("✅ Campaign handlers registered")

if __name__ == "__main__":
    print("Campaign handlers module loaded successfully")