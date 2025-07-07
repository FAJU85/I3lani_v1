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