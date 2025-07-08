# I3lani Bot Deployment Checklist

## Pre-Deployment Verification ✅

### Core Files Ready
- [x] `deployment_server.py` - Main web server entry point
- [x] `worker.py` - Background worker for async tasks  
- [x] `main_bot.py` - Core bot functionality
- [x] `database.py` - Database layer with all methods
- [x] `handlers.py` - All bot handlers
- [x] `admin_system.py` - Admin panel
- [x] `config.py` - Configuration management
- [x] `languages.py` - Multi-language support
- [x] `requirements.txt` - Python dependencies

### Deployment Configuration
- [x] `render.yaml` - Render deployment config (web + worker)
- [x] `Dockerfile` - Google Cloud Run config
- [x] `cloudbuild.yaml` - Cloud Build configuration
- [x] `.gitignore` - Git ignore file

### Documentation  
- [x] `README.md` - Project overview and quick deploy
- [x] `RENDER_DEPLOYMENT_GUIDE.md` - Detailed Render instructions
- [x] `CLOUD_RUN_DEPLOYMENT_GUIDE.md` - Cloud Run instructions
- [x] `BACKGROUND_WORKERS_GUIDE.md` - Worker documentation
- [x] `MOBILE_GITHUB_UPLOAD_TIPS.md` - Mobile upload guide

### Bot Features Tested
- [x] Multi-language support (EN, AR, RU)
- [x] TON cryptocurrency payments
- [x] Telegram Stars payments
- [x] Channel management (3 active channels)
- [x] Admin panel functionality
- [x] Referral system with rewards
- [x] Content moderation
- [x] Gamification system
- [x] Background worker tasks

## GitHub Upload Steps

### 1. Create Repository
1. Go to github.com on mobile/desktop
2. Click "+" → "New repository"
3. Name: `i3lani-bot`
4. Description: "Telegram advertising bot with blockchain payments"
5. Set to Public (for free Render deployment)
6. Click "Create repository"

### 2. Upload Files
**Important files to upload:**
- All `.py` files (main.py, handlers.py, etc.)
- `requirements.txt`
- `render.yaml` 
- `README.md`
- All `.md` documentation files
- `Dockerfile` and `cloudbuild.yaml`

**Files to SKIP:**
- `.env` (contains secrets)
- `bot.db` (local database)
- `__pycache__/` folders
- `.replit` files
- `uv.lock`

### 3. Update README
After upload, edit README.md line 19:
Replace: `YOUR_USERNAME/YOUR_REPO_NAME`
With: `yourusername/i3lani-bot`

## Render Deployment Steps

### 1. Create Account
1. Go to render.com
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### 2. Deploy Database
1. Click "New +" → "PostgreSQL"
2. Name: `i3lani-db`
3. Database: `i3lani`
4. User: `i3lani_user`
5. Plan: **Free**
6. Click "Create Database"
7. Wait 2-3 minutes for setup
8. Copy the "External Database URL"

### 3. Deploy Bot Services
1. Click "New +" → "Web Service"
2. Connect GitHub repo: `yourusername/i3lani-bot`
3. Render auto-detects `render.yaml`
4. This creates TWO services:
   - `i3lani-bot` (main web service)
   - `i3lani-worker` (background worker)

### 4. Configure Environment Variables
For **i3lani-bot** service:
- `BOT_TOKEN` = Your bot token from @BotFather
- `ADMIN_IDS` = Your Telegram user ID
- `TON_WALLET_ADDRESS` = Your TON wallet address
- `DATABASE_URL` = (auto-set from database)
- `DISABLE_STARS_FLASK` = 1

For **i3lani-worker** service:
- `BOT_TOKEN` = Your bot token from @BotFather  
- `DATABASE_URL` = (auto-set from database)

### 5. Deploy
1. Click "Deploy Latest Commit" on both services
2. Monitor logs for successful deployment
3. Bot should be live in 3-5 minutes

## Post-Deployment Testing

### 1. Check Services
- Web service: Shows "Live" status
- Worker service: Shows "Live" status  
- Database: Shows "Available" status

### 2. Test Bot
1. Open Telegram
2. Search for your bot
3. Send `/start` command
4. Bot should respond with language selection
5. Test creating an ad
6. Test payment flow

### 3. Monitor Logs
- Web service logs: User interactions
- Worker service logs: Background tasks
- Database logs: Connection status

## Troubleshooting

### Bot Not Responding
1. Check web service logs for errors
2. Verify `BOT_TOKEN` is correct
3. Ensure database connection is working

### Background Tasks Not Running
1. Check worker service logs
2. Verify database connection
3. Restart worker service if needed

### Database Connection Issues
1. Verify `DATABASE_URL` is set correctly
2. Check database service status
3. Ensure PostgreSQL is running

## Success Indicators
- ✅ Both services showing "Live"
- ✅ Bot responds to `/start` command
- ✅ Users can create ads and make payments
- ✅ Background worker processing tasks
- ✅ No errors in service logs

## Support
If you encounter issues:
1. Check Render service logs first
2. Verify environment variables
3. Test database connectivity
4. Contact through bot admin panel

Your bot is now ready for production deployment! 🚀