"""
Configuration settings for I3lani Telegram Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')

# Payment configuration
TON_API_KEY = os.getenv('TON_API_KEY')
TON_WALLET_ADDRESS = os.getenv('TON_WALLET_ADDRESS')

# Webhook configuration
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Admin configuration
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

# Main channel configuration
CHANNEL_ID = os.getenv('CHANNEL_ID', '@i3lani')

# Channel configuration
CHANNELS = {
    # All channels will be created by admin through the admin panel
    # No default channels - admin has full control
}

# Pricing configuration
DURATION_DISCOUNTS = {
    1: {'discount': 0.0, 'bonus_months': 0},
    3: {'discount': 0.1, 'bonus_months': 0},  # 10% discount
    6: {'discount': 0.2, 'bonus_months': 1}   # 20% discount + 1 bonus month
}

# Currency rates (will be updated dynamically)
CURRENCY_RATES = {
    'USD': 1.0,
    'SAR': 3.75,
    'RUB': 92.0
}

# Package definitions - Admin will create packages manually
PACKAGES = {
    # All packages will be created by admin through the admin panel
    # No default packages - admin has full control

}

# Ad categories configuration
AD_CATEGORIES = {
    'vehicles': {
        'name': {'en': '🚗 Vehicles', 'ar': '🚗 المركبات', 'ru': '🚗 Транспорт'},
        'emoji': '🚗',
        'subcategories': {
            'cars': {'en': '🚙 Cars', 'ar': '🚙 سيارات', 'ru': '🚙 Автомобили'},
            'motorcycles': {'en': '🏍️ Motorcycles', 'ar': '🏍️ دراجات نارية', 'ru': '🏍️ Мотоциклы'},
            'trucks': {'en': '🚛 Trucks', 'ar': '🚛 شاحنات', 'ru': '🚛 Грузовики'},
            'boats': {'en': '⛵ Boats', 'ar': '⛵ قوارب', 'ru': '⛵ Лодки'},
            'parts': {'en': '🔧 Parts & Accessories', 'ar': '🔧 قطع غيار', 'ru': '🔧 Запчасти'}
        }
    },
    'real_estate': {
        'name': {'en': '🏠 Real Estate', 'ar': '🏠 العقارات', 'ru': '🏠 Недвижимость'},
        'emoji': '🏠',
        'subcategories': {
            'apartments': {'en': '🏢 Apartments', 'ar': '🏢 شقق', 'ru': '🏢 Квартиры'},
            'houses': {'en': '🏘️ Houses', 'ar': '🏘️ منازل', 'ru': '🏘️ Дома'},
            'commercial': {'en': '🏬 Commercial', 'ar': '🏬 تجاري', 'ru': '🏬 Коммерческая'},
            'land': {'en': '🌾 Land', 'ar': '🌾 أراضي', 'ru': '🌾 Земля'},
            'rentals': {'en': '🔑 Rentals', 'ar': '🔑 إيجار', 'ru': '🔑 Аренда'}
        }
    },
    'electronics': {
        'name': {'en': '📱 Electronics', 'ar': '📱 الإلكترونيات', 'ru': '📱 Электроника'},
        'emoji': '📱',
        'subcategories': {
            'phones': {'en': '📱 Mobile Phones', 'ar': '📱 هواتف محمولة', 'ru': '📱 Мобильные телефоны'},
            'computers': {'en': '💻 Computers', 'ar': '💻 حاسوب', 'ru': '💻 Компьютеры'},
            'gaming': {'en': '🎮 Gaming', 'ar': '🎮 ألعاب', 'ru': '🎮 Игры'},
            'audio': {'en': '🎧 Audio & Video', 'ar': '🎧 صوت ومرئي', 'ru': '🎧 Аудио и видео'},
            'accessories': {'en': '🔌 Accessories', 'ar': '🔌 إكسسوارات', 'ru': '🔌 Аксессуары'}
        }
    },
    'jobs': {
        'name': {'en': '💼 Jobs', 'ar': '💼 الوظائف', 'ru': '💼 Работа'},
        'emoji': '💼',
        'subcategories': {
            'fulltime': {'en': '⏰ Full-time', 'ar': '⏰ دوام كامل', 'ru': '⏰ Полный день'},
            'parttime': {'en': '🕐 Part-time', 'ar': '🕐 دوام جزئي', 'ru': '🕐 Неполный день'},
            'freelance': {'en': '💻 Freelance', 'ar': '💻 عمل حر', 'ru': '💻 Фриланс'},
            'internship': {'en': '📚 Internships', 'ar': '📚 تدريب', 'ru': '📚 Стажировка'},
            'remote': {'en': '🌐 Remote Work', 'ar': '🌐 عمل عن بعد', 'ru': '🌐 Удаленная работа'}
        }
    },
    'services': {
        'name': {'en': '🛠️ Services', 'ar': '🛠️ الخدمات', 'ru': '🛠️ Услуги'},
        'emoji': '🛠️',
        'subcategories': {
            'cleaning': {'en': '🧹 Cleaning', 'ar': '🧹 تنظيف', 'ru': '🧹 Уборка'},
            'repair': {'en': '🔧 Repair', 'ar': '🔧 إصلاح', 'ru': '🔧 Ремонт'},
            'tutoring': {'en': '👨‍🏫 Tutoring', 'ar': '👨‍🏫 دروس خصوصية', 'ru': '👨‍🏫 Репетиторство'},
            'delivery': {'en': '🚚 Delivery', 'ar': '🚚 توصيل', 'ru': '🚚 Доставка'},
            'consulting': {'en': '💡 Consulting', 'ar': '💡 استشارات', 'ru': '💡 Консультации'}
        }
    },
    'fashion': {
        'name': {'en': '👗 Fashion', 'ar': '👗 الأزياء', 'ru': '👗 Мода'},
        'emoji': '👗',
        'subcategories': {
            'clothing': {'en': '👕 Clothing', 'ar': '👕 ملابس', 'ru': '👕 Одежда'},
            'shoes': {'en': '👟 Shoes', 'ar': '👟 أحذية', 'ru': '👟 Обувь'},
            'accessories': {'en': '👜 Accessories', 'ar': '👜 إكسسوارات', 'ru': '👜 Аксессуары'},
            'jewelry': {'en': '💍 Jewelry', 'ar': '💍 مجوهرات', 'ru': '💍 Украшения'},
            'beauty': {'en': '💄 Beauty', 'ar': '💄 جمال', 'ru': '💄 Красота'}
        }
    }
}

# Location options
LOCATIONS = {
    'riyadh': '🏙️ Riyadh',
    'jeddah': '🌊 Jeddah',
    'dammam': '🏗️ Dammam',
    'mecca': '🕋 Mecca',
    'medina': '🕌 Medina',
    'khobar': '🏢 Khobar',
    'taif': '🌄 Taif',
    'tabuk': '🏜️ Tabuk',
    'online': '🌐 Online/Nationwide'
}

# Referral configuration
REFERRAL_FRIEND_DISCOUNT = 0.05  # 5% discount for friends
REFERRAL_REWARD_DAYS = 3  # 3 free posting days per referral