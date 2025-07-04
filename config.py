import os
from typing import List

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Admin user IDs (comma-separated)
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: List[int] = []
if ADMIN_IDS_STR:
    try:
        ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",")]
    except ValueError:
        raise ValueError("ADMIN_IDS must be comma-separated integers")

# Channel configuration
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID environment variable is required")

# TON wallet address for payments
TON_WALLET_ADDRESS = os.getenv("TON_WALLET_ADDRESS", "UQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG")

# Package configurations
PACKAGES = {
    "starter": {
        "name": "Starter",
        "price": 0.099,
        "duration_days": 14,
        "repost_frequency_days": 7,
        "total_posts": 2
    },
    "pro": {
        "name": "Pro",
        "price": 0.399,
        "duration_days": 30,
        "repost_frequency_days": 3,
        "total_posts": 10
    },
    "growth": {
        "name": "Growth",
        "price": 0.999,
        "duration_days": 90,
        "repost_frequency_days": 1,
        "total_posts": 90
    },
    "elite": {
        "name": "Elite",
        "price": 1.999,
        "duration_days": 180,
        "repost_frequency_days": 1,
        "total_posts": 180
    }
}

# Bot messages
WELCOME_MESSAGE = """
🎯 **Welcome to the Ad Bot!**

Send me your advertisement content and I'll help you promote it on our channel.

📝 **What you can send:**
• Text messages
• Photos with captions
• Videos with captions

💰 **We offer 4 advertising packages with TON payments**

Ready to start? Just send me your ad content!
"""

PAYMENT_INSTRUCTIONS = """
💳 **Payment Instructions:**

1. Send **{price} TON** to this wallet address:
`{wallet_address}`

2. After sending payment, click the button below
3. Wait for admin approval
4. Your ad will be posted automatically!

⚠️ **Important:** Make sure to send the exact amount
"""
