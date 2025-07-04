# Telegram Ad Bot 🤖

A powerful multi-language Telegram advertising bot with TON cryptocurrency payments and automated reposting capabilities.

## Features

### 🌐 Multi-Language Support
- **English** 🇺🇸 - Default language
- **Arabic** 🇸🇦 - Full RTL support  
- **Russian** 🇷🇺 - Complete localization

### 💰 Payment System
- **TON Cryptocurrency** payments
- **Manual verification** by administrators
- **Flexible pricing** packages
- **Secure wallet** integration

### 📢 Advertisement Management
- **Text, Photo, Video** ad support
- **Automated reposting** based on packages
- **Admin approval** workflow
- **Campaign tracking** and statistics

### 📦 Pricing Packages
- **Starter** - 0.099 TON (3 posts, 1 day interval)
- **Pro** - 0.399 TON (7 posts, 1 day interval)
- **Growth** - 0.999 TON (15 posts, 1 day interval)
- **Elite** - 1.999 TON (30 posts, 12 hour interval)

## Quick Deploy Options

### 🚀 Deploy to Render (Recommended - Free)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Upload this repository to GitHub
2. Connect to Render.com
3. Set environment variables
4. Deploy in 2 minutes!

### 🔧 Deploy to Heroku
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Setup Instructions

### 1. Get Bot Token
1. Message @BotFather on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token

### 2. Get Your User ID
1. Message @userinfobot on Telegram
2. Copy your user ID number

### 3. Set Environment Variables
```bash
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=your_user_id_here
CHANNEL_ID=@yourchannel
TON_WALLET_ADDRESS=your_ton_wallet_address
```

### 4. Make Bot Admin
1. Add your bot to your Telegram channel
2. Give it administrator permissions
3. Enable "Post Messages" permission

## Local Development

### Prerequisites
- Python 3.11+
- pip package manager

### Installation
```bash
git clone https://github.com/yourusername/telegram-ad-bot.git
cd telegram-ad-bot
pip install -r render_requirements.txt
```

### Configuration
Create a `.env` file with your environment variables:
```
BOT_TOKEN=your_bot_token
ADMIN_IDS=your_user_id
CHANNEL_ID=@yourchannel
TON_WALLET_ADDRESS=your_wallet_address
```

### Run Locally
```bash
python main.py
```

## Project Structure

```
telegram-ad-bot/
├── main.py                    # Main bot application
├── config.py                  # Configuration and settings
├── handlers.py                # Bot command handlers
├── keyboards.py               # Telegram inline keyboards
├── languages.py               # Multi-language support
├── models.py                  # Data models and storage
├── scheduler.py               # Automated posting scheduler
├── render.yaml                # Render deployment config
├── Procfile                   # Heroku deployment config
├── runtime.txt                # Python version specification
├── app.json                   # Heroku app configuration
├── render_requirements.txt    # Python dependencies
├── heroku_requirements.txt    # Heroku-specific dependencies
├── RENDER_DEPLOY_GUIDE.md     # Render deployment guide
├── HEROKU_DEPLOYMENT_GUIDE.md # Heroku deployment guide
└── README.md                  # This file
```

## Bot Commands

### User Commands
- `/start` - Start bot and select language
- Send ad content (text, photo, video)
- Select advertising package
- Confirm payment

### Admin Commands
- `/stats` - View bot statistics
- Approve/reject pending advertisements
- Monitor active campaigns

## How It Works

1. **User Interaction**: User starts bot and selects preferred language
2. **Ad Submission**: User submits advertisement content (text, photo, or video)
3. **Package Selection**: User chooses advertising package with pricing
4. **Payment**: User sends TON payment to provided wallet address
5. **Admin Approval**: Administrator reviews and approves/rejects the ad
6. **Automated Posting**: Bot schedules and posts ads based on package parameters
7. **Reposting**: Automatic reposting according to package frequency

## Technology Stack

- **Python 3.11** - Core language
- **aiogram** - Telegram Bot API framework
- **asyncio** - Asynchronous operations
- **TON Network** - Cryptocurrency payments
- **In-memory storage** - Lightweight data persistence

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in this repository
- Join our Telegram community
- Contact the development team

## Deployment Platforms

### Render (Recommended)
- **Free tier**: No sleeping, better performance
- **Easy deployment**: One-click via GitHub
- **Documentation**: See `RENDER_DEPLOY_GUIDE.md`

### Heroku
- **Free tier**: 550 hours/month (sleeps after 30 minutes)
- **Paid tier**: $7/month for 24/7 uptime
- **Documentation**: See `HEROKU_DEPLOYMENT_GUIDE.md`

### Other Options
- Railway
- DigitalOcean App Platform
- AWS/GCP/Azure

## Security

- All sensitive data stored in environment variables
- No hardcoded tokens or secrets
- Admin-only approval system
- Secure payment verification

## Changelog

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added multi-language support
- **v1.2.0** - Added deployment guides and configurations

---

Made with ❤️ for the Telegram advertising community