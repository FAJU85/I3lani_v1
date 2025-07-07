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
    'i3lani_main': {
        'id': 'i3lani_main',
        'name': 'I3lani Channel',
        'telegram_channel_id': '@i3lani',
        'subscribers': 45000,
        'base_price_usd': 15.0,
        'is_popular': True
    },
    'gaming_hub': {
        'id': 'gaming_hub',
        'name': 'Gaming Hub',
        'telegram_channel_id': '@gaming_channel',
        'subscribers': 32000,
        'base_price_usd': 12.0,
        'is_popular': False
    },
    'business_tips': {
        'id': 'business_tips',
        'name': 'Business Tips',
        'telegram_channel_id': '@business_channel',
        'subscribers': 28000,
        'base_price_usd': 10.0,
        'is_popular': False
    }
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

# Package definitions - Updated pricing structure
PACKAGES = {
    'free': {
        'name': 'Free Plan',
        'duration_days': 3,
        'posts_per_day': 1,
        'price_usd': 0.0,
        'price_ton': 0.0,
        'description': '🎁 Free for @i3lani members',
        'restriction': 'Once every 2 months',
        'emoji': '🎁'
    },
    'bronze': {
        'name': 'Bronze Plan',
        'duration_days': 30,
        'posts_per_day': 0.33,  # 1 post every 3 days
        'price_usd': 10.0,
        'price_ton': 1.0,
        'description': '🟫 1 post every 3 days',
        'emoji': '🟫'
    },
    'silver': {
        'name': 'Silver Plan', 
        'duration_days': 90,  # 3 months
        'posts_per_day': 3,
        'price_usd': 29.0,
        'price_ton': 2.9,
        'description': '🥈 3 posts per day for 3 months',
        'emoji': '🥈'
    },
    'gold': {
        'name': 'Gold Plan',
        'duration_days': 180,  # 6 months
        'posts_per_day': 6,
        'price_usd': 47.0,
        'price_ton': 4.7,
        'description': '🥇 6 posts per day for 6 months',
        'emoji': '🥇'
    }
}

# Ad categories configuration
AD_CATEGORIES = {
    'vehicles': {
        'name': '🚗 Vehicles',
        'emoji': '🚗',
        'subcategories': {
            'cars': '🚙 Cars',
            'motorcycles': '🏍️ Motorcycles',
            'trucks': '🚛 Trucks',
            'boats': '⛵ Boats',
            'parts': '🔧 Parts & Accessories'
        }
    },
    'real_estate': {
        'name': '🏠 Real Estate',
        'emoji': '🏠',
        'subcategories': {
            'apartments': '🏢 Apartments',
            'houses': '🏘️ Houses',
            'commercial': '🏬 Commercial',
            'land': '🌾 Land',
            'rentals': '🔑 Rentals'
        }
    },
    'electronics': {
        'name': '📱 Electronics',
        'emoji': '📱',
        'subcategories': {
            'phones': '📱 Mobile Phones',
            'computers': '💻 Computers',
            'gaming': '🎮 Gaming',
            'audio': '🎧 Audio & Video',
            'accessories': '🔌 Accessories'
        }
    },
    'jobs': {
        'name': '💼 Jobs',
        'emoji': '💼',
        'subcategories': {
            'fulltime': '⏰ Full-time',
            'parttime': '🕐 Part-time',
            'freelance': '💻 Freelance',
            'internship': '📚 Internships',
            'remote': '🌐 Remote Work'
        }
    },
    'services': {
        'name': '🛠️ Services',
        'emoji': '🛠️',
        'subcategories': {
            'cleaning': '🧹 Cleaning',
            'repair': '🔧 Repair',
            'tutoring': '👨‍🏫 Tutoring',
            'delivery': '🚚 Delivery',
            'consulting': '💡 Consulting'
        }
    },
    'fashion': {
        'name': '👗 Fashion',
        'emoji': '👗',
        'subcategories': {
            'clothing': '👕 Clothing',
            'shoes': '👟 Shoes',
            'accessories': '👜 Accessories',
            'jewelry': '💍 Jewelry',
            'beauty': '💄 Beauty'
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