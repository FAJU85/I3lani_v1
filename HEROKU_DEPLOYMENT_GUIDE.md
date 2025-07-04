# Heroku Deployment Guide for Telegram Ad Bot

## Prerequisites
- Heroku account (free tier is sufficient)
- Git installed on your computer
- Your bot token and configuration values

## Step 1: Install Heroku CLI
1. Download and install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli
2. Verify installation: `heroku --version`

## Step 2: Login to Heroku
```bash
heroku login
```

## Step 3: Create a New Heroku App
```bash
heroku create your-bot-name
```
Replace `your-bot-name` with your desired app name (must be unique).

## Step 4: Set Environment Variables
Set these required environment variables in your Heroku app:

```bash
heroku config:set BOT_TOKEN="your_bot_token_here"
heroku config:set ADMIN_IDS="123456789,987654321"
heroku config:set CHANNEL_ID="@yourchannel"
heroku config:set TON_WALLET_ADDRESS="UQBvW8Z5huBkMJYdnfAEM5JqTNkuWX3diqYENkWsIL0XggGG"
```

### How to get these values:
- **BOT_TOKEN**: From @BotFather on Telegram
- **ADMIN_IDS**: Your Telegram user ID (get from @userinfobot)
- **CHANNEL_ID**: Your channel username (e.g., @yourchannel) or ID
- **TON_WALLET_ADDRESS**: Your TON cryptocurrency wallet address

## Step 5: Deploy Your Code

### Option A: Using Git
1. Initialize git repository (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Add Heroku remote:
```bash
heroku git:remote -a your-bot-name
```

3. Deploy:
```bash
git push heroku main
```

### Option B: Using Heroku Button
1. Upload your code to GitHub
2. Use the "Deploy to Heroku" button with the app.json file

## Step 6: Scale Your Bot
Start the worker process:
```bash
heroku ps:scale worker=1
```

## Step 7: Monitor Your Bot
Check if your bot is running:
```bash
heroku logs --tail
```

## Step 8: Make Your Bot Admin in Your Channel
1. Go to your Telegram channel
2. Add your bot as an administrator
3. Give it permission to post messages

## Files Created for Deployment
- `Procfile` - Tells Heroku how to run your app
- `runtime.txt` - Specifies Python version
- `heroku_requirements.txt` - Lists required Python packages
- `app.json` - Configuration for one-click deployment

## Important Notes
1. **Free Tier Limitations**: Heroku free tier sleeps after 30 minutes of inactivity
2. **Memory**: The bot uses in-memory storage, so data resets on restart
3. **Timezone**: Set timezone if needed: `heroku config:set TZ="Europe/London"`
4. **Logs**: Monitor logs regularly for errors: `heroku logs --tail`

## Troubleshooting

### Bot Not Starting
- Check environment variables: `heroku config`
- View logs: `heroku logs --tail`
- Ensure all required variables are set

### Permission Errors
- Make sure bot is admin in your channel
- Check channel ID format (@channel or -1001234567890)

### Payment Issues
- Verify TON wallet address is correct
- Ensure admins can approve/reject payments

## Cost Considerations
- **Free Tier**: 550-1000 dyno hours per month
- **Paid Tier**: $7/month for 24/7 uptime
- **Monitoring**: Free with basic metrics

## Alternative Deployment Methods
1. **Railway**: Similar to Heroku, often faster
2. **DigitalOcean App Platform**: Good alternative
3. **AWS/GCP**: More complex but more control

## Security Best Practices
- Never commit sensitive tokens to Git
- Use environment variables for all secrets
- Regularly rotate your bot token
- Monitor access logs

## Support
If you encounter issues:
1. Check Heroku status: https://status.heroku.com/
2. Review deployment logs
3. Verify all environment variables are set correctly
4. Test bot locally first

Your bot will be accessible at: https://your-bot-name.herokuapp.com
But since it's a Telegram bot, users interact with it through Telegram directly.