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

# Referral configuration
REFERRAL_FRIEND_DISCOUNT = 0.05  # 5% discount for friends
REFERRAL_REWARD_DAYS = 3  # 3 free posting days per referral