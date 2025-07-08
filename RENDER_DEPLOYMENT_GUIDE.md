# Deploy I3lani Bot to Render - Simple Guide

Render is much easier than Google Cloud Run! Here's how to deploy your bot:

## Step 1: Sign up for Render
1. Go to https://render.com
2. Sign up with GitHub/GitLab or email
3. You get **FREE hosting** for your bot!

## Step 2: Create a PostgreSQL Database
1. In Render dashboard, click "New +"
2. Choose "PostgreSQL"
3. Fill in:
   - Name: `i3lani-db`
   - Database: `i3lani`
   - User: `i3lani_user`
   - Region: Choose closest to you
   - Plan: **Free** (perfect for starting)
4. Click "Create Database"
5. Wait for it to be ready (takes 2-3 minutes)
6. Copy the "External Database URL" - you'll need this!

## Step 3: Deploy Your Bot
1. Click "New +" again
2. Choose "Web Service"
3. Connect your GitHub/GitLab repo OR use "Public Git repository"
4. If using public repo, paste: `https://github.com/your-username/your-repo`
5. Fill in:
   - Name: `i3lani-bot`
   - Runtime: Python
   - Build Command: `pip install -r render_requirements.txt`
   - Start Command: `python deployment_server.py`
   - Plan: **Free**
6. Click "Create Web Service"

## Step 4: Set Environment Variables
After the service is created:
1. Go to "Environment" tab
2. Add these variables:
   - `BOT_TOKEN` = Your bot token from @BotFather
   - `DATABASE_URL` = The PostgreSQL URL you copied
   - `ADMIN_IDS` = Your Telegram user ID
   - `TON_WALLET_ADDRESS` = Your TON wallet address
   - `DISABLE_STARS_FLASK` = 1

## Step 5: Deploy!
1. Click "Manual Deploy" → "Deploy latest commit"
2. Watch the logs - it should say "Bot started successfully"
3. Your bot is now live!

## Testing Your Bot
1. Open Telegram
2. Search for your bot
3. Send `/start` - it should respond!

## Troubleshooting

### Bot not responding?
- Check the logs in Render dashboard
- Make sure BOT_TOKEN is correct
- Verify DATABASE_URL is set

### Database errors?
- Make sure you're using Render's PostgreSQL URL, not Replit's
- The URL should start with `postgresql://`

### Port errors?
- Don't worry! Render sets the PORT automatically
- Our code already handles this

## Free Tier Limits
- Your bot sleeps after 15 minutes of inactivity
- First message might take 5-10 seconds to wake up
- Perfect for testing and small bots
- Upgrade to Starter ($7/month) for always-on bot

## Quick Deploy Link
Use this button in your README:
```markdown
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
```

That's it! Your bot is now running on Render for FREE! 🎉