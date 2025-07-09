# One-Click Deployment for I3lani Bot

## Render One-Click Deploy

### Deploy Button
Click this button to automatically deploy your I3lani bot to Render:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/i3lani-bot)

### What This Does Automatically:
1. **Creates PostgreSQL Database** - Free tier database for bot data
2. **Deploys Web Service** - Main bot with Flask server on port 10000
3. **Deploys Worker Service** - Background worker for async tasks
4. **Sets Default Environment Variables** - Pre-configured settings
5. **Configures Health Checks** - Automatic monitoring and restart

### Manual Steps Required:
After clicking deploy, you need to set these environment variables:

**Required Variables:**
- `BOT_TOKEN` - Your bot token from @BotFather
- `ADMIN_IDS` - Your Telegram user ID from @userinfobot

**Auto-Set Variables:**
- `TON_WALLET_ADDRESS` - Default wallet provided
- `DISABLE_STARS_FLASK` - Prevents server conflicts
- `DATABASE_URL` - Auto-linked to PostgreSQL database

## Step-by-Step Process

### 1. Prepare Repository
1. Create GitHub repository: `i3lani-bot`
2. Upload all files from ZIP package
3. Make repository public
4. Include `render-deploy.json` file

### 2. One-Click Deploy
1. Click the deploy button above
2. Sign in to Render with GitHub
3. Select your repository
4. Render reads `render-deploy.json` automatically
5. Creates all services and database

### 3. Configure Environment Variables
1. Go to your web service dashboard
2. Navigate to Environment tab
3. Set required variables:
   - `BOT_TOKEN`: Your bot token
   - `ADMIN_IDS`: Your user ID
4. Save changes (auto-deploys)

### 4. Configure Worker Service
1. Go to worker service dashboard
2. Set same environment variables
3. Save changes

### 5. Test Deployment
1. Check all services show "Live" status
2. Send `/start` to your bot
3. Test admin panel with `/admin`
4. Verify background tasks are running

## Services Created

### Web Service (i3lani-bot)
- **Type:** Web service
- **Command:** `python deployment_server.py`
- **Port:** 10000 (auto-assigned)
- **Health Check:** `/health` endpoint
- **Auto-scaling:** Enabled

### Worker Service (i3lani-worker)
- **Type:** Background worker
- **Command:** `python worker.py`
- **No external port** (internal processing only)
- **Tasks:** Payment monitoring, reward processing

### Database (i3lani-db)
- **Type:** PostgreSQL
- **Plan:** Free tier
- **Auto-linked:** To both web and worker services
- **Backup:** Daily automated backups

## Environment Variables Reference

### Required (Set Manually)
```bash
BOT_TOKEN=1234567890:ABCDEF...
ADMIN_IDS=123456789
```

### Auto-Set (No Action Needed)
```bash
TON_WALLET_ADDRESS=UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB
DISABLE_STARS_FLASK=1
DATABASE_URL=postgresql://... (auto-linked)
```

## Troubleshooting

### Deploy Button Not Working
- Ensure repository is public
- Check `render-deploy.json` is in root directory
- Verify all required files are uploaded

### Services Not Starting
- Check environment variables are set
- Verify `BOT_TOKEN` format is correct
- Ensure database is connected

### Bot Not Responding
- Check web service logs for errors
- Verify webhook URL is accessible
- Test `/health` endpoint manually

## Manual Deployment Alternative

If one-click deploy doesn't work:

1. **Create Services Manually:**
   - Web service from GitHub repo
   - Worker service from same repo
   - PostgreSQL database

2. **Link Database:**
   - Connect database to both services
   - Environment variables auto-set

3. **Configure Environment:**
   - Set `BOT_TOKEN` and `ADMIN_IDS`
   - Other variables use defaults

## Benefits of One-Click Deploy

### Time Savings
- **Manual setup:** 15-20 minutes
- **One-click:** 5-10 minutes
- **Fewer errors:** Pre-configured settings

### Automatic Configuration
- Services properly linked
- Database auto-connected
- Health checks enabled
- Correct build commands

### Beginner Friendly
- No technical expertise needed
- Guided setup process
- Clear error messages
- Automatic retries

## Update Process

### Automatic Updates
1. Push changes to GitHub
2. Render auto-deploys both services
3. Zero downtime deployment
4. Health checks ensure stability

### Manual Updates
1. Go to service dashboard
2. Click "Manual Deploy"
3. Select latest commit
4. Deploy with same settings

## Monitoring

### Service Health
- **Web Service:** Check `/health` endpoint
- **Worker Service:** Monitor background tasks
- **Database:** Connection status

### Logs
- **Web Service:** User interactions, API calls
- **Worker Service:** Background processing
- **Database:** Connection and query logs

### Alerts
- Service failures
- High resource usage
- Database connection issues

## Cost Estimation

### Free Tier Usage
- **Web Service:** ~400-500 hours/month
- **Worker Service:** ~200-300 hours/month  
- **Database:** Free PostgreSQL included
- **Total:** Usually within 750-hour limit

### Upgrade Path
- **Starter Plan:** $7/month for more resources
- **Professional:** $25/month for production
- **Scaling:** Auto-scaling based on demand

Your bot will be live and fully functional within minutes of clicking the deploy button!