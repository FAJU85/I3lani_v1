# 🚀 Deploy I3lani Bot to Render in 5 Minutes

## Direct Deploy Link
After uploading to GitHub, use this link (replace YOUR_USERNAME):
```
https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/i3lani-bot
```

## Step-by-Step Deployment

### 1. One-Click Deploy
1. Click the deploy link above
2. Render will automatically:
   - Create a web service
   - Create a PostgreSQL database
   - Connect them together
   - Deploy your bot

### 2. Set Your Secrets
After deployment starts, go to Environment tab and add:
- `BOT_TOKEN` = Your bot token from @BotFather
- `ADMIN_IDS` = Your Telegram user ID  
- `TON_WALLET_ADDRESS` = Your TON wallet

### 3. That's It!
Your bot will be live in 2-3 minutes!

## What Render Gives You FREE:
✅ Web hosting (sleeps after 15 min inactivity)
✅ PostgreSQL database 
✅ Automatic HTTPS
✅ Auto-deploy when you push to GitHub
✅ Easy environment variables
✅ Logs and monitoring

## Testing Your Bot
1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Bot should respond!

## Render Dashboard
- **Logs**: See real-time bot activity
- **Environment**: Manage secrets
- **Settings**: Configure auto-deploy
- **Database**: View connection info

## Common Issues

### Bot not responding?
1. Check Logs tab for errors
2. Verify BOT_TOKEN is correct
3. Make sure service is "Live"

### Database errors?
- DATABASE_URL is set automatically by Render
- Don't modify it!

### Bot slow to respond?
- Free tier sleeps after 15 min
- First message wakes it up (5-10 sec)
- Upgrade to paid for always-on

## Need Help?
- Check logs first
- Render support is excellent
- Or ask in the bot admin panel