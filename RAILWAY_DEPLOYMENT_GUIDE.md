# Deploy I3lani Bot to Railway

Railway.app is another excellent hosting platform that's perfect for deploying your Telegram bot. It offers free tier hosting with PostgreSQL database support.

## Why Railway?

- **Free Tier:** $5 worth of credits monthly (enough for small bots)
- **PostgreSQL:** Free managed database included
- **GitHub Integration:** One-click deployment from GitHub
- **Automatic Deployments:** Updates when you push to GitHub
- **Simple Setup:** Even easier than Render
- **Better Performance:** Often faster than other free platforms

## Step-by-Step Deployment

### 1. Upload to GitHub First
1. Create repository: `i3lani-bot`
2. Upload all project files (extract from ZIP)
3. Make repository public
4. Include `railway.json` configuration file

### 2. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your repositories
4. You'll get $5 free credits monthly

### 3. Deploy Database
1. Click "New Project"
2. Choose "Provision PostgreSQL"
3. Database will be created automatically
4. Copy the connection details (auto-generated)

### 4. Deploy Bot Service
1. Click "New Project" → "Deploy from GitHub repo"
2. Select your repository: `yourusername/i3lani-bot`
3. Railway auto-detects Python and uses `railway.json`
4. Deployment starts automatically

### 5. Configure Environment Variables
In your Railway dashboard:

**Required Variables:**
- `BOT_TOKEN` = Your bot token from @BotFather
- `ADMIN_IDS` = Your Telegram user ID
- `DATABASE_URL` = Auto-set by Railway PostgreSQL
- `DISABLE_STARS_FLASK` = 1

**Optional Variables:**
- `TON_WALLET_ADDRESS` = Your TON wallet address
- `PORT` = Auto-set by Railway (usually 8080)

### 6. Deploy Worker Service (Optional)
1. Click "New Project" → "Deploy from GitHub repo"
2. Select same repository: `yourusername/i3lani-bot`
3. Change start command to: `python worker.py`
4. Set same environment variables as bot service

## Configuration Files

### railway.json
```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python deployment_server.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "on_failure"
  }
}
```

### Environment Variables Setup
```bash
# Required
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=your_telegram_user_id
DATABASE_URL=postgresql://... (auto-set)
DISABLE_STARS_FLASK=1

# Optional
TON_WALLET_ADDRESS=UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB
```

## Architecture Options

### Option 1: Single Service (Recommended)
- **Service:** Bot + Background tasks in one container
- **Database:** Railway PostgreSQL
- **Cost:** ~$1-2/month within free credits
- **Setup:** Easiest, one deployment

### Option 2: Multi-Service 
- **Service 1:** Bot web server (`deployment_server.py`)
- **Service 2:** Background worker (`worker.py`)
- **Database:** Railway PostgreSQL
- **Cost:** ~$2-3/month
- **Setup:** More complex but better separation

## Deployment Commands

Railway auto-detects your Python app and runs:
```bash
# Install dependencies
pip install -r requirements.txt

# Start application
python deployment_server.py
```

## Post-Deployment

### 1. Check Deployment Status
- Service should show "Active" status
- Database should show "Running"
- Check logs for any errors

### 2. Test Your Bot
1. Open Telegram
2. Search for your bot
3. Send `/start` command
4. Bot should respond with language selection

### 3. Monitor Usage
- Railway dashboard shows resource usage
- Monitor credit consumption
- Check logs for performance issues

## Advantages Over Render

### Performance
- **Railway:** Usually faster cold starts
- **Render:** Can be slower on free tier

### Database
- **Railway:** Integrated PostgreSQL setup
- **Render:** Separate database service

### Pricing
- **Railway:** $5 credits monthly
- **Render:** Usage-based, can run out faster

### Interface
- **Railway:** Cleaner, more modern UI
- **Render:** More traditional hosting interface

## Free Tier Limits

### Railway Free Tier
- $5 worth of credits monthly
- 500 hours of execution time
- 1GB RAM per service
- 1GB storage per database

### Estimated Usage
- **Small bot:** ~$1-2/month
- **Medium bot:** ~$3-4/month
- **Large bot:** May exceed free tier

## Troubleshooting

### Bot Not Starting
1. Check environment variables are set
2. Verify `BOT_TOKEN` is correct
3. Check service logs for errors
4. Ensure `railway.json` is in repository

### Database Connection Issues
1. Verify `DATABASE_URL` is auto-set
2. Check PostgreSQL service is running
3. Restart both services if needed

### Out of Credits
1. Monitor usage in Railway dashboard
2. Optimize code to reduce resource usage
3. Consider upgrading to paid plan ($5/month)

## Monitoring and Maintenance

### Health Checks
- Railway automatically monitors `/health` endpoint
- Restarts service if health check fails
- Logs available in dashboard

### Auto-Deployments
- Push to GitHub → Automatic deployment
- No manual intervention needed
- Can disable auto-deploy if preferred

### Scaling
- Can easily scale up with more resources
- Add more services as needed
- Database scales automatically

## Migration from Other Platforms

### From Render
1. Export environment variables
2. Deploy to Railway with same settings
3. Update DNS/webhooks if needed

### From Heroku
1. Use same repository
2. Convert `Procfile` to `railway.json`
3. Migrate database if needed

## Best Practices

### Code Organization
- Use `deployment_server.py` as entry point
- Keep `worker.py` for background tasks
- Environment variables in Railway dashboard

### Performance
- Use connection pooling for database
- Implement proper error handling
- Monitor memory usage

### Security
- Never commit secrets to GitHub
- Use environment variables for all sensitive data
- Regularly rotate API keys

## Support and Documentation

### Railway Resources
- [Railway Docs](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [Railway Twitter](https://twitter.com/Railway)

### Bot Support
- Check service logs first
- Verify environment variables
- Test database connectivity
- Contact through bot admin panel

## Comparison: Railway vs Render vs Heroku

| Feature | Railway | Render | Heroku |
|---------|---------|---------|---------|
| Free Tier | $5 credits | 750 hours | Limited |
| Database | Included | Separate | Add-on |
| Setup | Easiest | Easy | Complex |
| Performance | Fast | Good | Variable |
| UI | Modern | Clean | Traditional |

## Conclusion

Railway is an excellent choice for deploying your I3lani bot, especially if you want:
- Simple setup process
- Integrated database
- Modern dashboard
- Good performance
- Automatic deployments

The free tier should be sufficient for most small to medium bots, and the upgrade path is straightforward when you need more resources.

Ready to deploy your bot to Railway? 🚀