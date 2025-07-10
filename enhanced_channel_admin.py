"""
Enhanced Channel Administration Interface
Using official Telegram API for comprehensive channel management
"""

import asyncio
import logging
from typing import Dict, List, Optional
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database import db
from languages import get_text, get_user_language
from telegram_channel_api import get_telegram_channel_api
from datetime import datetime
import json

logger = logging.getLogger(__name__)
router = Router()


class EnhancedChannelAdmin:
    """Enhanced channel administration with Telegram API integration"""
    
    def __init__(self):
        self.telegram_api = None
    
    async def initialize(self, bot):
        """Initialize with bot instance"""
        self.telegram_api = get_telegram_channel_api(bot)
    
    async def show_enhanced_channel_dashboard(self, callback_query: CallbackQuery):
        """Show enhanced channel management dashboard"""
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Get comprehensive channel statistics
        channels = await self.telegram_api.scan_bot_admin_channels()
        
        if language == 'ar':
            text = f"""🔧 **لوحة إدارة القنوات المتقدمة**

📊 **إحصائيات شاملة:**
• المجموع: {len(channels)} قناة
• المشتركون الإجماليون: {sum(ch.get('member_count', 0) for ch in channels):,}
• المشتركون النشطون: {sum(ch.get('active_subscribers', 0) for ch in channels):,}
• معدل المشاركة: {self._calculate_avg_engagement(channels):.1f}%

📈 **تحليل الفئات:**
{self._format_category_analysis(channels, language)}

🔄 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        elif language == 'ru':
            text = f"""🔧 **Расширенная панель управления каналами**

📊 **Подробная статистика:**
• Всего: {len(channels)} каналов
• Общие подписчики: {sum(ch.get('member_count', 0) for ch in channels):,}
• Активные подписчики: {sum(ch.get('active_subscribers', 0) for ch in channels):,}
• Средняя вовлеченность: {self._calculate_avg_engagement(channels):.1f}%

📈 **Анализ категорий:**
{self._format_category_analysis(channels, language)}

🔄 Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        else:
            text = f"""🔧 **Enhanced Channel Management Dashboard**

📊 **Comprehensive Statistics:**
• Total: {len(channels)} channels
• Total Subscribers: {sum(ch.get('member_count', 0) for ch in channels):,}
• Active Subscribers: {sum(ch.get('active_subscribers', 0) for ch in channels):,}
• Average Engagement: {self._calculate_avg_engagement(channels):.1f}%

📈 **Category Analysis:**
{self._format_category_analysis(channels, language)}

🔄 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        keyboard = self._create_enhanced_dashboard_keyboard(language)
        
        await callback_query.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def show_detailed_channel_analysis(self, callback_query: CallbackQuery):
        """Show detailed analysis for each channel"""
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        channels = await self.telegram_api.scan_bot_admin_channels()
        
        if not channels:
            await callback_query.answer("No channels found", show_alert=True)
            return
        
        # Create detailed analysis text
        analysis_text = self._format_detailed_analysis(channels, language)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔄 Refresh Analysis" if language == 'en' else 
                     "🔄 تحديث التحليل" if language == 'ar' else 
                     "🔄 Обновить анализ",
                callback_data="refresh_channel_analysis"
            )],
            [InlineKeyboardButton(
                text="📊 Export Report" if language == 'en' else 
                     "📊 تصدير التقرير" if language == 'ar' else 
                     "📊 Экспорт отчета",
                callback_data="export_channel_report"
            )],
            [InlineKeyboardButton(
                text="◀️ Back" if language == 'en' else 
                     "◀️ العودة" if language == 'ar' else 
                     "◀️ Назад",
                callback_data="enhanced_channel_dashboard"
            )]
        ])
        
        await callback_query.message.edit_text(
            analysis_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def perform_bulk_channel_operations(self, callback_query: CallbackQuery):
        """Perform bulk operations on channels"""
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        if language == 'ar':
            text = """⚡ **العمليات المجمعة للقنوات**

اختر العملية التي تريد تطبيقها على جميع القنوات:

🔄 **تحديث الإحصائيات**: تحديث أرقام المشتركين والبيانات
📊 **تحليل شامل**: تحليل مفصل لجميع القنوات
🎯 **تحسين الفئات**: إعادة تصنيف القنوات تلقائياً
📈 **تقرير الأداء**: إنشاء تقرير شامل عن الأداء
🔗 **روابط الدعوة**: إنشاء/تحديث روابط الدعوة"""
        elif language == 'ru':
            text = """⚡ **Массовые операции с каналами**

Выберите операцию для применения ко всем каналам:

🔄 **Обновить статистику**: Обновить подписчиков и данные
📊 **Полный анализ**: Детальный анализ всех каналов
🎯 **Оптимизация категорий**: Автоматическая реклассификация
📈 **Отчет о производительности**: Создать полный отчет
🔗 **Пригласительные ссылки**: Создать/обновить ссылки"""
        else:
            text = """⚡ **Bulk Channel Operations**

Select operation to apply to all channels:

🔄 **Update Statistics**: Refresh subscriber counts and data
📊 **Comprehensive Analysis**: Detailed analysis of all channels
🎯 **Optimize Categories**: Auto-reclassify channels
📈 **Performance Report**: Generate comprehensive report
🔗 **Invite Links**: Create/update invite links"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔄 Update Statistics" if language == 'en' else 
                     "🔄 تحديث الإحصائيات" if language == 'ar' else 
                     "🔄 Обновить статистику",
                callback_data="bulk_update_stats"
            )],
            [InlineKeyboardButton(
                text="📊 Comprehensive Analysis" if language == 'en' else 
                     "📊 تحليل شامل" if language == 'ar' else 
                     "📊 Полный анализ",
                callback_data="bulk_comprehensive_analysis"
            )],
            [InlineKeyboardButton(
                text="🎯 Optimize Categories" if language == 'en' else 
                     "🎯 تحسين الفئات" if language == 'ar' else 
                     "🎯 Оптимизация категорий",
                callback_data="bulk_optimize_categories"
            )],
            [InlineKeyboardButton(
                text="📈 Performance Report" if language == 'en' else 
                     "📈 تقرير الأداء" if language == 'ar' else 
                     "📈 Отчет о производительности",
                callback_data="bulk_performance_report"
            )],
            [InlineKeyboardButton(
                text="🔗 Manage Invite Links" if language == 'en' else 
                     "🔗 إدارة روابط الدعوة" if language == 'ar' else 
                     "🔗 Управление ссылками",
                callback_data="bulk_invite_links"
            )],
            [InlineKeyboardButton(
                text="◀️ Back" if language == 'en' else 
                     "◀️ العودة" if language == 'ar' else 
                     "◀️ Назад",
                callback_data="enhanced_channel_dashboard"
            )]
        ])
        
        await callback_query.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def execute_bulk_statistics_update(self, callback_query: CallbackQuery):
        """Execute bulk statistics update"""
        user_id = callback_query.from_user.id
        language = await get_user_language(user_id)
        
        # Send progress message
        progress_text = "🔄 Updating channel statistics..." if language == 'en' else \
                       "🔄 تحديث إحصائيات القنوات..." if language == 'ar' else \
                       "🔄 Обновление статистики каналов..."
        
        await callback_query.message.edit_text(progress_text)
        
        try:
            # Perform bulk update
            updated_channels = await self.telegram_api.scan_bot_admin_channels()
            
            # Format results
            if language == 'ar':
                result_text = f"""✅ **تم تحديث الإحصائيات بنجاح**

📊 **النتائج:**
• تم تحديث: {len(updated_channels)} قناة
• المشتركون الإجماليون: {sum(ch.get('member_count', 0) for ch in updated_channels):,}
• المشتركون النشطون: {sum(ch.get('active_subscribers', 0) for ch in updated_channels):,}

⏰ تم في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            elif language == 'ru':
                result_text = f"""✅ **Статистика успешно обновлена**

📊 **Результаты:**
• Обновлено: {len(updated_channels)} каналов
• Общие подписчики: {sum(ch.get('member_count', 0) for ch in updated_channels):,}
• Активные подписчики: {sum(ch.get('active_subscribers', 0) for ch in updated_channels):,}

⏰ Выполнено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            else:
                result_text = f"""✅ **Statistics Updated Successfully**

📊 **Results:**
• Updated: {len(updated_channels)} channels
• Total Subscribers: {sum(ch.get('member_count', 0) for ch in updated_channels):,}
• Active Subscribers: {sum(ch.get('active_subscribers', 0) for ch in updated_channels):,}

⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="📊 View Details" if language == 'en' else 
                         "📊 عرض التفاصيل" if language == 'ar' else 
                         "📊 Подробности",
                    callback_data="detailed_channel_analysis"
                )],
                [InlineKeyboardButton(
                    text="◀️ Back to Dashboard" if language == 'en' else 
                         "◀️ العودة للوحة" if language == 'ar' else 
                         "◀️ К панели",
                    callback_data="enhanced_channel_dashboard"
                )]
            ])
            
            await callback_query.message.edit_text(
                result_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in bulk statistics update: {e}")
            error_text = "❌ Error updating statistics" if language == 'en' else \
                        "❌ خطأ في تحديث الإحصائيات" if language == 'ar' else \
                        "❌ Ошибка обновления статистики"
            await callback_query.message.edit_text(error_text)
    
    def _calculate_avg_engagement(self, channels: List[Dict]) -> float:
        """Calculate average engagement rate across channels"""
        if not channels:
            return 0.0
        
        total_engagement = sum(ch.get('engagement_score', 0) for ch in channels)
        return total_engagement / len(channels)
    
    def _format_category_analysis(self, channels: List[Dict], language: str) -> str:
        """Format category analysis text"""
        categories = {}
        for channel in channels:
            category = channel.get('category', 'general')
            if category not in categories:
                categories[category] = {'count': 0, 'subscribers': 0}
            categories[category]['count'] += 1
            categories[category]['subscribers'] += channel.get('member_count', 0)
        
        if language == 'ar':
            analysis = []
            for category, data in categories.items():
                category_name = {
                    'technology': 'تقنية',
                    'shopping': 'تسوق',
                    'news': 'أخبار',
                    'entertainment': 'ترفيه',
                    'education': 'تعليم',
                    'business': 'أعمال',
                    'sports': 'رياضة',
                    'general': 'عام'
                }.get(category, category)
                analysis.append(f"• {category_name}: {data['count']} قناة ({data['subscribers']:,} مشترك)")
        elif language == 'ru':
            analysis = []
            for category, data in categories.items():
                category_name = {
                    'technology': 'Технологии',
                    'shopping': 'Покупки',
                    'news': 'Новости',
                    'entertainment': 'Развлечения',
                    'education': 'Образование',
                    'business': 'Бизнес',
                    'sports': 'Спорт',
                    'general': 'Общее'
                }.get(category, category)
                analysis.append(f"• {category_name}: {data['count']} каналов ({data['subscribers']:,} подписчиков)")
        else:
            analysis = []
            for category, data in categories.items():
                analysis.append(f"• {category.title()}: {data['count']} channels ({data['subscribers']:,} subscribers)")
        
        return '\n'.join(analysis)
    
    def _format_detailed_analysis(self, channels: List[Dict], language: str) -> str:
        """Format detailed channel analysis"""
        if language == 'ar':
            text = "📊 **تحليل مفصل للقنوات**\n\n"
            for i, channel in enumerate(channels, 1):
                text += f"""**{i}. {channel.get('title', 'Unknown')}**
• المعرف: @{channel.get('username', 'N/A')}
• المشتركون: {channel.get('member_count', 0):,}
• النشطون: {channel.get('active_subscribers', 0):,}
• الفئة: {channel.get('category', 'عام')}
• نقاط المشاركة: {channel.get('engagement_score', 0):.1f}

"""
        elif language == 'ru':
            text = "📊 **Детальный анализ каналов**\n\n"
            for i, channel in enumerate(channels, 1):
                text += f"""**{i}. {channel.get('title', 'Unknown')}**
• Имя: @{channel.get('username', 'N/A')}
• Подписчики: {channel.get('member_count', 0):,}
• Активные: {channel.get('active_subscribers', 0):,}
• Категория: {channel.get('category', 'общее')}
• Вовлеченность: {channel.get('engagement_score', 0):.1f}

"""
        else:
            text = "📊 **Detailed Channel Analysis**\n\n"
            for i, channel in enumerate(channels, 1):
                text += f"""**{i}. {channel.get('title', 'Unknown')}**
• Username: @{channel.get('username', 'N/A')}
• Subscribers: {channel.get('member_count', 0):,}
• Active: {channel.get('active_subscribers', 0):,}
• Category: {channel.get('category', 'general')}
• Engagement: {channel.get('engagement_score', 0):.1f}

"""
        
        return text
    
    def _create_enhanced_dashboard_keyboard(self, language: str) -> InlineKeyboardMarkup:
        """Create enhanced dashboard keyboard"""
        if language == 'ar':
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 تحليل مفصل", callback_data="detailed_channel_analysis")],
                [InlineKeyboardButton(text="⚡ عمليات مجمعة", callback_data="bulk_channel_operations")],
                [InlineKeyboardButton(text="📈 تقارير متقدمة", callback_data="advanced_channel_reports")],
                [InlineKeyboardButton(text="🔄 تحديث البيانات", callback_data="refresh_channel_data")],
                [InlineKeyboardButton(text="⚙️ إعدادات القنوات", callback_data="channel_settings")],
                [InlineKeyboardButton(text="◀️ العودة للإدارة", callback_data="admin_channels")]
            ])
        elif language == 'ru':
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Детальный анализ", callback_data="detailed_channel_analysis")],
                [InlineKeyboardButton(text="⚡ Массовые операции", callback_data="bulk_channel_operations")],
                [InlineKeyboardButton(text="📈 Расширенные отчеты", callback_data="advanced_channel_reports")],
                [InlineKeyboardButton(text="🔄 Обновить данные", callback_data="refresh_channel_data")],
                [InlineKeyboardButton(text="⚙️ Настройки каналов", callback_data="channel_settings")],
                [InlineKeyboardButton(text="◀️ К управлению", callback_data="admin_channels")]
            ])
        else:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Detailed Analysis", callback_data="detailed_channel_analysis")],
                [InlineKeyboardButton(text="⚡ Bulk Operations", callback_data="bulk_channel_operations")],
                [InlineKeyboardButton(text="📈 Advanced Reports", callback_data="advanced_channel_reports")],
                [InlineKeyboardButton(text="🔄 Refresh Data", callback_data="refresh_channel_data")],
                [InlineKeyboardButton(text="⚙️ Channel Settings", callback_data="channel_settings")],
                [InlineKeyboardButton(text="◀️ Back to Admin", callback_data="admin_channels")]
            ])


# Global instance
enhanced_channel_admin = EnhancedChannelAdmin()


# Handler registration
@router.callback_query(lambda c: c.data == "enhanced_channel_dashboard")
async def enhanced_channel_dashboard_handler(callback_query: CallbackQuery):
    await enhanced_channel_admin.show_enhanced_channel_dashboard(callback_query)


@router.callback_query(lambda c: c.data == "detailed_channel_analysis")
async def detailed_channel_analysis_handler(callback_query: CallbackQuery):
    await enhanced_channel_admin.show_detailed_channel_analysis(callback_query)


@router.callback_query(lambda c: c.data == "bulk_channel_operations")
async def bulk_channel_operations_handler(callback_query: CallbackQuery):
    await enhanced_channel_admin.perform_bulk_channel_operations(callback_query)


@router.callback_query(lambda c: c.data == "bulk_update_stats")
async def bulk_update_stats_handler(callback_query: CallbackQuery):
    await enhanced_channel_admin.execute_bulk_statistics_update(callback_query)


@router.callback_query(lambda c: c.data == "refresh_channel_data")
async def refresh_channel_data_handler(callback_query: CallbackQuery):
    await enhanced_channel_admin.execute_bulk_statistics_update(callback_query)