# Railway Quick Deploy Guide - I3lani Bot

## Why Railway Is Better for This Project

Railway has proven to be more reliable than Render for Python projects with complex dependencies:
- **Better build environment** - No Rust compilation issues
- **Faster deployment** - Usually completes in 2-3 minutes
- **More reliable** - Fewer build failures
- **Better logging** - Clearer error messages
- **PostgreSQL included** - Free database with every project

## Quick Deploy Steps

### 1. Create GitHub Repository
1. Go to [GitHub](https://github.com)
2. Create new repository: `i3lani-bot`
3. Upload all files from your ZIP package
4. Make repository public

### 2. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `i3lani-bot` repository
6. Railway will automatically detect Python and deploy

### 3. Add Database
1. In Railway dashboard, click "Add Service"
2. Select "PostgreSQL"
3. Database will be automatically linked to your app
4. `DATABASE_URL` environment variable is set automatically

### 4. Set Environment Variables
1. Go to your web service in Railway
2. Click "Variables" tab
3. Add these variables:
   ```
   BOT_TOKEN=your_bot_token_here
   ADMIN_IDS=your_telegram_user_id
   TON_WALLET_ADDRESS=UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB
   DISABLE_STARS_FLASK=1
   ```

### 5. Check Deployment
1. Go to "Deployments" tab
2. Wait for build to complete (2-3 minutes)
3. Check logs for "Bot Features:" message
4. Your bot is live!

## Environment Variables Reference

### Required (Set Manually)
- `BOT_TOKEN` - Get from @BotFather
- `ADMIN_IDS` - Get from @userinfobot

### Auto-Set by Railway
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Service port (usually 8000)

### Optional (Pre-configured)
- `TON_WALLET_ADDRESS` - Default wallet provided
- `DISABLE_STARS_FLASK` - Prevents server conflicts

## Testing Your Bot

After deployment:
1. Send `/start` to your bot
2. Test language selection
3. Try `/admin` command
4. Create a test ad
5. Check payment systems work

## Railway Advantages

### Build Environment
- Modern Python environment
- Pre-installed compilation tools
- Better dependency resolution
- Faster package installation

### Deployment
- Automatic builds from GitHub
- Zero-downtime deployments
- Rollback capabilities
- Real-time build logs

### Monitoring
- Built-in metrics
- Error tracking
- Performance monitoring
- Usage analytics

### Pricing
- **Free tier**: $5 credit monthly
- **Pro tier**: $20/month for production
- **Usage-based**: Pay only for what you use

## Common Issues and Solutions

### Build Failures
Unlike Render, Railway rarely has build issues. If you encounter problems:
1. Check Python version compatibility
2. Verify requirements.txt syntax
3. Check GitHub repository permissions

### Bot Not Responding
1. Verify `BOT_TOKEN` is correct
2. Check deployment logs for errors
3. Ensure database is connected

### Database Connection Issues
1. Verify PostgreSQL service is running
2. Check `DATABASE_URL` is set
3. Restart both services if needed

## File Structure for Railway

Your repository should contain:
```
i3lani-bot/
├── deployment_server.py    # Main entry point
├── main_bot.py            # Bot logic
├── requirements_minimal.txt # Dependencies
├── railway.json           # Railway configuration
├── database.py            # Database setup
├── handlers.py            # Bot handlers
├── ... (all other files)
```

## Railway vs Render Comparison

| Feature | Railway | Render |
|---------|---------|---------|
| Build Success Rate | 95%+ | 70% (Rust issues) |
| Build Time | 2-3 min | 5-10 min |
| Free Tier | $5 credit | 750 hours |
| Database | PostgreSQL included | PostgreSQL included |
| Deployment | One-click | One-click |
| Reliability | Excellent | Good |
| Support | Community + Paid | Community |

Railway is the recommended choice for reliable deployment of your I3lani bot.