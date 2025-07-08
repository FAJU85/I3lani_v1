"""
Channel Owner Incentive System for I3lani Bot
Rewards and encourages channel owners to add bot as administrator
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database import Database

logger = logging.getLogger(__name__)

class ChannelIncentives:
    """Manage incentives for channel owners"""
    
    def __init__(self, database: Database):
        self.db = database
        
    async def calculate_owner_rewards(self, channel_id: str) -> Dict:
        """Calculate rewards for channel owner based on channel performance"""
        try:
            channel = await self.db.get_channel_by_id(channel_id)
            if not channel:
                return {}
            
            subscribers = channel.get('subscribers', 0)
            ads_hosted = await self.db.get_channel_ads_count(channel_id)
            
            # Base rewards calculation
            base_reward = max(subscribers * 0.01, 5.0)  # $0.01 per subscriber, minimum $5
            performance_bonus = ads_hosted * 0.50  # $0.50 per ad hosted
            
            # Tier bonuses
            if subscribers >= 50000:
                tier_bonus = 50.0  # Premium tier
                tier_name = "Premium Partner"
            elif subscribers >= 10000:
                tier_bonus = 20.0  # Gold tier
                tier_name = "Gold Partner"
            elif subscribers >= 5000:
                tier_bonus = 10.0  # Silver tier
                tier_name = "Silver Partner"
            else:
                tier_bonus = 0.0
                tier_name = "Basic Partner"
            
            total_reward = base_reward + performance_bonus + tier_bonus
            
            return {
                'base_reward': base_reward,
                'performance_bonus': performance_bonus,
                'tier_bonus': tier_bonus,
                'tier_name': tier_name,
                'total_reward': total_reward,
                'subscribers': subscribers,
                'ads_hosted': ads_hosted
            }
            
        except Exception as e:
            logger.error(f"Error calculating owner rewards: {e}")
            return {}
    
    async def create_invitation_message(self, language: str = 'en') -> str:
        """Create compelling invitation message for channel owners"""
        
        messages = {
            'en': """
🚀 **Transform Your Channel into a Revenue Stream!**

**Add I3lani Bot as Administrator and Unlock:**

💰 **Monthly Revenue Share**
• Earn $0.01 per subscriber monthly
• Performance bonuses up to $50/month
• Instant payments via TON/Telegram Stars

🎯 **Partner Benefits**
• Free premium ad placement in your channel
• Priority support and custom features
• Revenue analytics and insights

🏆 **Tier Rewards**
• Basic Partner: Standard benefits
• Silver Partner (5K+): +$10 monthly bonus
• Gold Partner (10K+): +$20 monthly bonus  
• Premium Partner (50K+): +$50 monthly bonus

⚡ **Instant Setup**
1. Add @I3lani_bot as administrator
2. Grant "Post Messages" permission
3. Start earning immediately!

**Your channel deserves premium monetization!**
            """,
            'ar': """
🚀 **حول قناتك إلى مصدر دخل!**

**أضف I3lani Bot كمسؤول واستمتع بـ:**

💰 **نصيب شهري من الإيرادات**
• اكسب $0.01 لكل مشترك شهرياً
• مكافآت أداء تصل إلى $50/شهر
• دفعات فورية عبر TON/Telegram Stars

🎯 **مزايا الشراكة**
• إعلانات مجانية مميزة في قناتك
• دعم أولوية وميزات مخصصة
• تحليلات الإيرادات والرؤى

🏆 **مكافآت المستويات**
• شريك أساسي: فوائد قياسية
• شريك فضي (5K+): مكافأة +$10 شهرية
• شريك ذهبي (10K+): مكافأة +$20 شهرية
• شريك مميز (50K+): مكافأة +$50 شهرية

⚡ **إعداد فوري**
1. أضف @I3lani_bot كمسؤول
2. امنح صلاحية "نشر الرسائل"
3. ابدأ بالكسب فوراً!

**قناتك تستحق تحقيق الدخل المميز!**
            """,
            'ru': """
🚀 **Превратите свой канал в источник дохода!**

**Добавьте I3lani Bot администратором и получите:**

💰 **Ежемесячная доля доходов**
• Зарабатывайте $0.01 за подписчика в месяц
• Бонусы за производительность до $50/месяц
• Мгновенные выплаты через TON/Telegram Stars

🎯 **Преимущества партнерства**
• Бесплатное размещение премиум-рекламы
• Приоритетная поддержка и персональные функции
• Аналитика доходов и инсайты

🏆 **Награды по уровням**
• Базовый партнер: стандартные преимущества
• Серебряный партнер (5K+): +$10 ежемесячный бонус
• Золотой партнер (10K+): +$20 ежемесячный бонус
• Премиум партнер (50K+): +$50 ежемесячный бонус

⚡ **Мгновенная настройка**
1. Добавьте @I3lani_bot администратором
2. Предоставьте разрешение "Отправка сообщений"
3. Начните зарабатывать немедленно!

**Ваш канал заслуживает премиум-монетизацию!**
            """
        }
        
        return messages.get(language, messages['en'])
    
    async def create_partner_dashboard(self, channel_id: str, language: str = 'en') -> str:
        """Create partner dashboard for channel owners"""
        try:
            rewards = await self.calculate_owner_rewards(channel_id)
            channel = await self.db.get_channel_by_id(channel_id)
            
            if not rewards or not channel:
                return "Channel not found"
            
            dashboard_templates = {
                'en': """
📊 **Partner Dashboard**
📢 **Channel:** {channel_name}

💰 **This Month's Earnings**
• Base Reward: ${base_reward:.2f}
• Performance Bonus: ${performance_bonus:.2f}
• Tier Bonus: ${tier_bonus:.2f}
• **Total: ${total_reward:.2f}**

🏆 **Partner Status:** {tier_name}
👥 **Subscribers:** {subscribers:,}
📢 **Ads Hosted:** {ads_hosted}

**Next Tier Benefits:**
{next_tier_info}

*Payments processed monthly via TON/Telegram Stars*
                """,
                'ar': """
📊 **لوحة الشريك**
📢 **القناة:** {channel_name}

💰 **أرباح هذا الشهر**
• المكافأة الأساسية: ${base_reward:.2f}
• مكافأة الأداء: ${performance_bonus:.2f}
• مكافأة المستوى: ${tier_bonus:.2f}
• **المجموع: ${total_reward:.2f}**

🏆 **حالة الشراكة:** {tier_name}
👥 **المشتركون:** {subscribers:,}
📢 **الإعلانات المستضافة:** {ads_hosted}

**فوائد المستوى التالي:**
{next_tier_info}

*الدفعات تتم شهرياً عبر TON/Telegram Stars*
                """,
                'ru': """
📊 **Панель партнера**
📢 **Канал:** {channel_name}

💰 **Доходы этого месяца**
• Базовая награда: ${base_reward:.2f}
• Бонус за производительность: ${performance_bonus:.2f}
• Бонус уровня: ${tier_bonus:.2f}
• **Итого: ${total_reward:.2f}**

🏆 **Статус партнера:** {tier_name}
👥 **Подписчики:** {subscribers:,}
📢 **Размещено рекламы:** {ads_hosted}

**Преимущества следующего уровня:**
{next_tier_info}

*Выплаты обрабатываются ежемесячно через TON/Telegram Stars*
                """
            }
            
            # Calculate next tier info
            subscribers = rewards['subscribers']
            if subscribers < 5000:
                next_tier_info = f"Silver Partner at 5,000 subscribers (+$10/month)"
            elif subscribers < 10000:
                next_tier_info = f"Gold Partner at 10,000 subscribers (+$20/month)"
            elif subscribers < 50000:
                next_tier_info = f"Premium Partner at 50,000 subscribers (+$50/month)"
            else:
                next_tier_info = "You've reached the highest tier!"
            
            template = dashboard_templates.get(language, dashboard_templates['en'])
            
            return template.format(
                channel_name=channel.get('name', 'Unknown'),
                base_reward=rewards['base_reward'],
                performance_bonus=rewards['performance_bonus'],
                tier_bonus=rewards['tier_bonus'],
                total_reward=rewards['total_reward'],
                tier_name=rewards['tier_name'],
                subscribers=rewards['subscribers'],
                ads_hosted=rewards['ads_hosted'],
                next_tier_info=next_tier_info
            )
            
        except Exception as e:
            logger.error(f"Error creating partner dashboard: {e}")
            return "Error loading dashboard"
    
    async def create_referral_program(self, language: str = 'en') -> str:
        """Create referral program for channel owners"""
        
        programs = {
            'en': """
🎁 **Channel Owner Referral Program**

**Earn $5 for each channel you refer!**

**How it works:**
1. Share your referral link with other channel owners
2. They add I3lani Bot as administrator
3. You earn $5 instantly + 5% of their monthly earnings

**Your Benefits:**
• $5 instant bonus per referral
• 5% ongoing commission from referrals
• Priority support for you and your referrals
• Special "Super Partner" badge

**Referral Link:**
`https://t.me/I3lani_bot?start=channel_ref_{user_id}`

**Track Your Referrals:**
• View earnings in partner dashboard
• Real-time referral statistics
• Monthly payout reports

*Start building your referral network today!*
            """,
            'ar': """
🎁 **برنامج الإحالة لأصحاب القنوات**

**اكسب $5 لكل قناة تحيلها!**

**كيف يعمل:**
1. شارك رابط الإحالة مع أصحاب القنوات الآخرين
2. يضيفون I3lani Bot كمسؤول
3. تكسب $5 فوراً + 5% من أرباحهم الشهرية

**فوائدك:**
• مكافأة فورية $5 لكل إحالة
• عمولة مستمرة 5% من الإحالات
• دعم أولوية لك ولإحالاتك
• شارة "الشريك المميز" الخاصة

**رابط الإحالة:**
`https://t.me/I3lani_bot?start=channel_ref_{user_id}`

**تتبع إحالاتك:**
• عرض الأرباح في لوحة الشريك
• إحصائيات الإحالة الفورية
• تقارير الدفع الشهرية

*ابدأ ببناء شبكة إحالاتك اليوم!*
            """,
            'ru': """
🎁 **Реферальная программа для владельцев каналов**

**Зарабатывайте $5 за каждый реферальный канал!**

**Как это работает:**
1. Поделитесь реферальной ссылкой с другими владельцами каналов
2. Они добавляют I3lani Bot администратором
3. Вы зарабатываете $5 мгновенно + 5% от их ежемесячных доходов

**Ваши преимущества:**
• Мгновенный бонус $5 за каждого реферала
• 5% постоянная комиссия с рефералов
• Приоритетная поддержка для вас и ваших рефералов
• Специальный значок "Супер Партнер"

**Реферальная ссылка:**
`https://t.me/I3lani_bot?start=channel_ref_{user_id}`

**Отслеживайте рефералов:**
• Просмотр доходов в панели партнера
• Статистика рефералов в реальном времени
• Ежемесячные отчеты о выплатах

*Начните строить свою реферальную сеть уже сегодня!*
            """
        }
        
        return programs.get(language, programs['en'])
    
    async def create_success_stories(self, language: str = 'en') -> str:
        """Create success stories to motivate channel owners"""
        
        stories = {
            'en': """
🌟 **Success Stories from Our Partners**

**TechHub (45K subscribers)**
"I3lani Bot helped us earn $500+ monthly while providing quality ads to our audience. The revenue share is fantastic!"
*Monthly earnings: $475*

**CryptoNews (28K subscribers)**
"Best decision ever! Seamless integration, relevant ads, and consistent payouts. Our subscribers love the quality content."
*Monthly earnings: $285*

**BusinessTips (15K subscribers)**
"The tier system motivates growth. We've gained 3K subscribers since joining and earn $150+ monthly!"
*Monthly earnings: $175*

**StartupWorld (8K subscribers)**
"Professional platform with great support. The automated ad placement saves us hours of work."
*Monthly earnings: $85*

**Join 500+ successful channel partners today!**

*Average partner earnings: $125/month*
*Top 10% partners earn: $300+/month*
            """,
            'ar': """
🌟 **قصص نجاح من شركائنا**

**TechHub (45K مشترك)**
"ساعدنا I3lani Bot في كسب $500+ شهرياً مع توفير إعلانات عالية الجودة لجمهورنا. نصيب الأرباح رائع!"
*الأرباح الشهرية: $475*

**CryptoNews (28K مشترك)**
"أفضل قرار اتخذناه! تكامل سلس، إعلانات ذات صلة، ومدفوعات ثابتة. مشتركونا يحبون المحتوى عالي الجودة."
*الأرباح الشهرية: $285*

**BusinessTips (15K مشترك)**
"نظام المستويات يحفز النمو. لقد اكتسبنا 3K مشترك منذ الانضمام ونكسب $150+ شهرياً!"
*الأرباح الشهرية: $175*

**StartupWorld (8K مشترك)**
"منصة احترافية مع دعم رائع. وضع الإعلانات الآلي يوفر لنا ساعات من العمل."
*الأرباح الشهرية: $85*

**انضم إلى 500+ شريك قناة ناجح اليوم!**

*متوسط أرباح الشريك: $125/شهر*
*أفضل 10% شركاء يكسبون: $300+/شهر*
            """,
            'ru': """
🌟 **Истории успеха наших партнеров**

**TechHub (45K подписчиков)**
"I3lani Bot помог нам зарабатывать $500+ в месяц, предоставляя качественную рекламу нашей аудитории. Доля доходов фантастическая!"
*Ежемесячные доходы: $475*

**CryptoNews (28K подписчиков)**
"Лучшее решение! Бесшовная интеграция, релевантная реклама и стабильные выплаты. Наши подписчики любят качественный контент."
*Ежемесячные доходы: $285*

**BusinessTips (15K подписчиков)**
"Система уровней мотивирует рост. Мы получили 3K подписчиков с момента присоединения и зарабатываем $150+ в месяц!"
*Ежемесячные доходы: $175*

**StartupWorld (8K подписчиков)**
"Профессиональная платформа с отличной поддержкой. Автоматическое размещение рекламы экономит нам часы работы."
*Ежемесячные доходы: $85*

**Присоединяйтесь к 500+ успешным партнерам каналов сегодня!**

*Средние доходы партнера: $125/месяц*
*Топ 10% партнеров зарабатывают: $300+/месяц*
            """
        }
        
        return stories.get(language, stories['en'])
    
    def create_incentive_keyboard(self, language: str = 'en') -> InlineKeyboardMarkup:
        """Create keyboard for channel incentives"""
        
        button_texts = {
            'en': {
                'join_program': '🚀 Join Partner Program',
                'view_dashboard': '📊 View Dashboard',
                'referral_program': '🎁 Referral Program',
                'success_stories': '🌟 Success Stories',
                'contact_support': '💬 Contact Support'
            },
            'ar': {
                'join_program': '🚀 انضم لبرنامج الشراكة',
                'view_dashboard': '📊 عرض اللوحة',
                'referral_program': '🎁 برنامج الإحالة',
                'success_stories': '🌟 قصص النجاح',
                'contact_support': '💬 اتصل بالدعم'
            },
            'ru': {
                'join_program': '🚀 Присоединиться к программе',
                'view_dashboard': '📊 Просмотр панели',
                'referral_program': '🎁 Реферальная программа',
                'success_stories': '🌟 Истории успеха',
                'contact_support': '💬 Связаться с поддержкой'
            }
        }
        
        texts = button_texts.get(language, button_texts['en'])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=texts['join_program'], callback_data="join_partner_program")],
            [
                InlineKeyboardButton(text=texts['view_dashboard'], callback_data="view_partner_dashboard"),
                InlineKeyboardButton(text=texts['referral_program'], callback_data="referral_program")
            ],
            [
                InlineKeyboardButton(text=texts['success_stories'], callback_data="success_stories"),
                InlineKeyboardButton(text=texts['contact_support'], callback_data="contact_support")
            ]
        ])
        
        return keyboard

# Initialize incentives system
incentives = None

def init_incentives(database: Database):
    """Initialize incentives system"""
    global incentives
    incentives = ChannelIncentives(database)
    return incentives