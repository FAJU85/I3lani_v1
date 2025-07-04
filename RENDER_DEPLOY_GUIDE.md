# Render Deployment Guide - Super Easy! 🚀

## Why Render is Better Than Heroku:
- **Free forever** (no sleeping like Heroku)
- **Easier to deploy** (no CLI needed)
- **Better performance** on free tier
- **Simple dashboard** to manage your bot

## Deploy in 3 Minutes:

### Step 1: Upload to GitHub
1. Go to [GitHub.com](https://github.com) and create a new repository
2. Upload all your bot files (or use GitHub Desktop)
3. Make sure these files are included:
   - `main.py` (your bot code)
   - `render.yaml` (deployment config)
   - `render_requirements.txt` (dependencies)
   - All other `.py` files

### Step 2: Deploy to Render
1. Go to [Render.com](https://render.com) and sign up (free)
2. Click "New +" then "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect your `render.yaml` file
5. Click "Apply" - that's it!

### Step 3: Set Your Environment Variables
In the Render dashboard, add these variables:
- `BOT_TOKEN` - Your bot token from @BotFather
- `ADMIN_IDS` - Your Telegram user ID (from @userinfobot)  
- `CHANNEL_ID` - Your channel username (like @yourchannel)
- `TON_WALLET_ADDRESS` - Already set in render.yaml

## Get Your Bot Token:
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Choose a name and username for your bot
4. Copy the token it gives you

## Get Your User ID:
1. Message @userinfobot on Telegram
2. It will reply with your user ID number

## Alternative: Manual Deployment
If you prefer manual setup:

1. **New Web Service**:
   - Repository: Your GitHub repo
   - Environment: Python 3
   - Build Command: `pip install -r render_requirements.txt`
   - Start Command: `python main.py`

2. **Set Environment Variables**:
   - BOT_TOKEN: (your bot token)
   - ADMIN_IDS: (your user ID)
   - CHANNEL_ID: (your channel)
   - TON_WALLET_ADDRESS: UQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG

## Your Bot Features:
- **Multi-language support** (English, Arabic, Russian)
- **TON cryptocurrency payments**
- **Automated ad posting and reposting**
- **Admin approval system**
- **Package selection (Starter, Pro, Growth, Elite)**

## Monitor Your Bot:
- Check logs in Render dashboard
- Your bot will be online 24/7 for free
- No sleeping or downtime issues

## Make Your Bot Admin:
1. Go to your Telegram channel
2. Add your bot as administrator
3. Give it permission to post messages

## Troubleshooting:
- **Build fails**: Check that render_requirements.txt is uploaded
- **Bot doesn't respond**: Verify BOT_TOKEN is correct
- **Can't post to channel**: Make sure bot is admin with post permissions

Your bot will be live in 2-3 minutes after deployment!

## Cost: 
- **Render**: Completely free forever
- **Heroku**: Free tier sleeps, $7/month for 24/7
- **Winner**: Render! 🎉