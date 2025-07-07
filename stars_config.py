"""
Configuration for Telegram Stars Backend System
Complete configuration for Stars payment processing with Flask webhook
"""

import os
from typing import Dict, Any

# Telegram Stars Configuration
STARS_WEBHOOK_URL = os.getenv('STARS_WEBHOOK_URL', 'https://yourdomain.com/webhook')
STARS_BACKEND_PORT = int(os.getenv('STARS_BACKEND_PORT', '5001'))
STARS_BACKEND_HOST = os.getenv('STARS_BACKEND_HOST', '0.0.0.0')

# Package pricing in Telegram Stars
STARS_PACKAGE_PRICES = {
    'starter': {
        'stars': 15,  # 15 stars = ~$1.50
        'usd_value': 1.50,
        'duration_days': 7,
        'posts_per_day': 1,
        'channels': 1,
        'name': 'Starter Package',
        'description': 'Basic advertising package for new users'
    },
    'professional': {
        'stars': 75,  # 75 stars = ~$7.50
        'usd_value': 7.50,
        'duration_days': 15,
        'posts_per_day': 2,
        'channels': 2,
        'name': 'Professional Package',
        'description': 'Advanced advertising with multi-channel reach'
    },
    'enterprise': {
        'stars': 225,  # 225 stars = ~$22.50
        'usd_value': 22.50,
        'duration_days': 30,
        'posts_per_day': 3,
        'channels': 3,
        'name': 'Enterprise Package',
        'description': 'Premium advertising with maximum exposure'
    }
}

# Stars conversion rates
STARS_TO_USD_RATE = 0.1  # 1 star = $0.10 USD
USD_TO_STARS_RATE = 10   # $1 USD = 10 stars

# Webhook configuration
WEBHOOK_CONFIG = {
    'url': STARS_WEBHOOK_URL,
    'port': STARS_BACKEND_PORT,
    'host': STARS_BACKEND_HOST,
    'debug': False,
    'threaded': True
}

# Invoice template configuration
INVOICE_TEMPLATE = {
    'photo_url': 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/2b50.png',
    'photo_size': 512,
    'photo_width': 512,
    'photo_height': 512,
    'need_name': False,
    'need_phone_number': False,
    'need_email': False,
    'need_shipping_address': False,
    'send_phone_number_to_provider': False,
    'send_email_to_provider': False,
    'is_flexible': False,
    'max_tip_amount': 0,
    'suggested_tip_amounts': []
}

# Payment processing configuration
PAYMENT_CONFIG = {
    'auto_approve_checkout': True,
    'auto_publish_ads': True,
    'send_confirmations': True,
    'notify_admins': True,
    'create_subscriptions': True,
    'track_analytics': True
}

# Error handling configuration
ERROR_CONFIG = {
    'retry_attempts': 3,
    'retry_delay': 5,  # seconds
    'log_errors': True,
    'notify_admins_on_error': True
}

def get_package_by_stars(stars_amount: int) -> Dict[str, Any]:
    """Get package configuration by stars amount"""
    for package_id, package in STARS_PACKAGE_PRICES.items():
        if package['stars'] == stars_amount:
            return {'id': package_id, **package}
    
    # Return default package if not found
    return {'id': 'starter', **STARS_PACKAGE_PRICES['starter']}

def get_stars_amount_by_package(package_id: str) -> int:
    """Get stars amount for a package"""
    package = STARS_PACKAGE_PRICES.get(package_id, STARS_PACKAGE_PRICES['starter'])
    return package['stars']

def convert_stars_to_usd(stars: int) -> float:
    """Convert stars to USD value"""
    return stars * STARS_TO_USD_RATE

def convert_usd_to_stars(usd: float) -> int:
    """Convert USD to stars amount"""
    return int(usd * USD_TO_STARS_RATE)

def get_invoice_config(package_id: str) -> Dict[str, Any]:
    """Get invoice configuration for a package"""
    package = STARS_PACKAGE_PRICES.get(package_id, STARS_PACKAGE_PRICES['starter'])
    
    config = {
        'title': f'I3lani - {package["name"]}',
        'description': f'{package["description"]} - {package["duration_days"]} days, {package["posts_per_day"]} posts/day',
        'currency': 'XTR',  # Telegram Stars currency code
        'prices': [{'label': package["name"], 'amount': package["stars"]}],
        'provider_token': '',  # Empty for Stars
        **INVOICE_TEMPLATE
    }
    
    return config

# Export all configurations
__all__ = [
    'STARS_PACKAGE_PRICES',
    'STARS_WEBHOOK_URL',
    'STARS_BACKEND_PORT',
    'STARS_BACKEND_HOST',
    'WEBHOOK_CONFIG',
    'INVOICE_TEMPLATE',
    'PAYMENT_CONFIG',
    'ERROR_CONFIG',
    'get_package_by_stars',
    'get_stars_amount_by_package',
    'convert_stars_to_usd',
    'convert_usd_to_stars',
    'get_invoice_config'
]