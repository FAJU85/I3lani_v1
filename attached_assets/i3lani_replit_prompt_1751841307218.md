# I3lani Telegram Bot - Replit Build Instructions

## Quick Setup Requirements
- **Platform**: Telegram Bot using Python + aiogram
- **Database**: SQLite (for Replit simplicity)
- **Payment**: Telegram Stars + TON cryptocurrency
- **Languages**: English 🇺🇸, Arabic 🇸🇦, Russian 🇷🇺

## Core Bot Structure

### 1. Essential Files to Create:
```
main.py          # Main bot entry point
config.py        # Bot token and settings
database.py      # SQLite database operations
handlers.py      # Message and callback handlers
payments.py      # Payment processing
languages.py     # Multi-language support
states.py        # FSM states for conversations
```

### 2. Required Dependencies (requirements.txt):
```
aiogram==3.4.1
aiohttp==3.8.5
aiosqlite==0.19.0
python-dotenv==1.0.0
requests==2.31.0
```

### 3. Core Bot Flow:
```
Start → Language Selection → Create Ad → Choose Channel → 
Select Duration → Payment → Verification → Publishing → Dashboard
```

## Essential Features to Implement

### Bot Commands & Menus:
- `/start` - Welcome with language selection
- **Main Menu**: Create Ad, My Ads, Pricing, Share & Earn, Settings, Help
- **Inline Keyboards**: Language picker, channel selection, duration options

### Payment System:
- **Telegram Stars integration**
- **TON cryptocurrency support**
- **Memo format**: AB0102 (6 characters)
- **Payment verification** via tonviewer.com API

### Database Tables (SQLite):
```sql
users: user_id, username, language, currency, referrer_id, created_at
ads: ad_id, user_id, content, media_url, link_url, status
subscriptions: subscription_id, user_id, ad_id, channel_id, duration_months, start_date, end_date, total_price
payments: payment_id, user_id, amount, currency, payment_method, memo, tx_hash, status
channels: channel_id, name, telegram_channel_id, subscribers, base_price_usd, is_popular
referrals: referral_id, referrer_id, referee_id, channel_id, reward_granted
```

## Key Implementation Details

### 1. State Management (FSM):
```python
class AdCreationStates(StatesGroup):
    language_selection = State()
    ad_content = State()
    channel_selection = State()
    duration_selection = State()
    payment_method = State()
    payment_confirmation = State()
```

### 2. Pricing Psychology:
- **3 Channels**: Tech News (45K) 🔥, Gaming Hub (32K), Business Tips (28K) 🪤
- **Duration Options**: 1 Month (base), 3 Months (save 5 TON), 6 Months (save 20 TON) 🔥
- **Default selection**: 6-month "Best Value"

### 3. Payment Processing:
```python
# Generate unique memo: AB0102 format
# Create payment invoice
# Monitor TON blockchain via tonviewer.com API
# Verify transaction and update subscription
```

### 4. Multi-language Support:
```python
LANGUAGES = {
    'en': {'welcome': 'Welcome! Choose your language:', 'currency': 'USD'},
    'ar': {'welcome': 'أهلاً! اختر لغتك:', 'currency': 'SAR'},
    'ru': {'welcome': 'Добро пожаловать! Выберите язык:', 'currency': 'RUB'}
}
```

## Environment Variables (.env):
```
BOT_TOKEN=your_telegram_bot_token
TON_API_KEY=your_ton_api_key
DATABASE_URL=sqlite:///bot.db
WEBHOOK_URL=your_replit_url
```

## Critical Features:

### User Experience:
- **One-click copy** for wallet addresses and memos
- **Back navigation** in all steps
- **Progress indicators** showing current step
- **Menu button** always visible

### Payment Methods:
- **Telegram Stars**: Built-in Telegram payment
- **TON Crypto**: Blockchain verification required

### Referral System:
- Generate unique referral links
- 5% friend discount
- Free posting days as rewards

### Admin Functions:
- Channel management
- Pricing control
- User analytics
- Content management

## Quick Start Code Structure:

### main.py:
```python
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from handlers import setup_handlers
from database import init_db

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    await init_db()
    setup_handlers(dp)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

## Success Criteria:
- Multi-language bot with currency support
- Working payment system (Stars + TON)
- Ad creation and publishing workflow
- Subscription management
- Referral system
- Admin panel for channel/pricing management

**Build this as a complete, working Telegram bot that handles the entire user journey from ad creation to payment verification and publishing.**