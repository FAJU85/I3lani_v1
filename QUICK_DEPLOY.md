# Quick Deploy Commands

Copy and paste these commands one by one in your terminal:

## 1. Install Heroku CLI (if not installed)
**Windows:**
```bash
winget install Heroku.HerokuCLI
```

**macOS:**
```bash
brew tap heroku/brew && brew install heroku
```

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

## 2. Login and Create App
```bash
heroku login
heroku create telegram-ad-bot-$(date +%s)
```

## 3. Set Your Environment Variables
Replace these with your actual values:

```bash
heroku config:set BOT_TOKEN="YOUR_BOT_TOKEN_FROM_BOTFATHER"
heroku config:set ADMIN_IDS="YOUR_TELEGRAM_USER_ID"
heroku config:set CHANNEL_ID="@YOUR_CHANNEL_NAME"
heroku config:set TON_WALLET_ADDRESS="UQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG"
```

## 4. Deploy Your Code
```bash
git init
git add .
git commit -m "Deploy Telegram Ad Bot"
heroku git:remote -a $(heroku apps:info --json | jq -r '.name')
git push heroku main
```

## 5. Start Your Bot
```bash
heroku ps:scale worker=1
```

## 6. Check if Running
```bash
heroku logs --tail
```

## Get Your Values:
- **BOT_TOKEN**: Message @BotFather on Telegram, create a new bot
- **ADMIN_IDS**: Message @userinfobot on Telegram to get your user ID
- **CHANNEL_ID**: Your channel username (like @yourchannel)
- **TON_WALLET**: Your TON cryptocurrency wallet address

## Alternative: One-Click Deploy
Upload your code to GitHub and use this button:
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Your bot will be live in 2-3 minutes after deployment!