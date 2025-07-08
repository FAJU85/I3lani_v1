# I3lani Bot - Telegram Advertising Platform

A sophisticated Telegram advertising bot with blockchain payment integration, multilingual support, and comprehensive partner incentive system.

## Features
- 🌍 Multi-language support (English, Arabic, Russian)
- 💰 Dual payment system (TON cryptocurrency & Telegram Stars)
- 📢 Multi-channel advertising management
- 🎯 Smart pricing with volume discounts
- 🏆 Gamification and rewards system
- 🛡️ Anti-fraud protection
- 📊 Comprehensive admin panel

## Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/YOUR_REPO_NAME)

**Or use this direct link after uploading to GitHub:**
`https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/i3lani-bot`

## Manual Deployment

1. Fork/Clone this repository
2. Deploy to Render (FREE hosting + database)
3. Set environment variables:
   - `BOT_TOKEN` - Your bot token from @BotFather
   - `DATABASE_URL` - PostgreSQL URL (provided by Render)
   - `ADMIN_IDS` - Your Telegram user ID
   - `TON_WALLET_ADDRESS` - Your TON wallet address

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN=your_bot_token
export DATABASE_URL=your_database_url
export ADMIN_IDS=your_telegram_id

# Run the bot
python deployment_server.py
```

## Documentation

- [Render Deployment Guide](RENDER_DEPLOYMENT_GUIDE.md)
- [Cloud Run Deployment Guide](CLOUD_RUN_DEPLOYMENT_GUIDE.md)
- [Channel Management Guide](CHANNEL_MANAGEMENT_GUIDE.md)
- [Content Moderation Guide](CONTENT_MODERATION_GUIDE.md)

## Support

For issues or questions, contact the admin through the bot's support feature.

## License

This project is proprietary software. All rights reserved.