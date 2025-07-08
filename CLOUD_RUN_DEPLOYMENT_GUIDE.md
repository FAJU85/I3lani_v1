# Cloud Run Deployment Guide for I3lani Bot

## Current Status
✅ Bot is working locally and responding to messages
✅ Health endpoints are functioning correctly
✅ deployment_server.py is properly configured

## Common Cloud Run Deployment Issues & Solutions

### 1. Environment Variables Not Set in Cloud Run
When deploying to Cloud Run, you must set these environment variables:

```bash
BOT_TOKEN=your_actual_bot_token_here
DATABASE_URL=postgresql://your_database_url_here
ADMIN_IDS=your_admin_user_ids_here
TON_WALLET_ADDRESS=your_ton_wallet_address
DISABLE_STARS_FLASK=1
```

### 2. Database Connection Issues
If using Replit's PostgreSQL database locally but deploying to Cloud Run:
- You need a publicly accessible PostgreSQL database
- Options: Google Cloud SQL, Neon, Supabase, or any cloud PostgreSQL service
- Update DATABASE_URL in Cloud Run settings

### 3. Port Configuration
Cloud Run automatically sets the PORT environment variable. Our deployment_server.py already handles this correctly:
```python
port = int(os.environ.get('PORT', 5001))
```

### 4. Startup Timeout
Cloud Run requires the service to start responding within 10 minutes. Our bot starts in ~20 seconds, so this shouldn't be an issue.

## Deployment Steps

### Option 1: Deploy via Replit Deployments
1. Click the "Deploy" button in Replit
2. Select "Web Service"
3. Use these settings:
   - Build command: (leave empty)
   - Run command: `python deployment_server.py`
   - Port: 5001

### Option 2: Deploy to Google Cloud Run Manually

1. **Install Google Cloud SDK** (if not on Replit)
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

2. **Create a simple Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY . .
RUN pip install aiogram aiohttp aiosqlite flask psycopg2-binary python-dotenv requests sqlalchemy
ENV PYTHONUNBUFFERED=1
ENV DISABLE_STARS_FLASK=1
EXPOSE 5001
CMD ["python", "deployment_server.py"]
```

3. **Build and deploy**:
```bash
# Set your project ID
export PROJECT_ID=your-gcp-project-id

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/i3lani-bot

# Deploy to Cloud Run
gcloud run deploy i3lani-bot \
  --image gcr.io/$PROJECT_ID/i3lani-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5001 \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars "DISABLE_STARS_FLASK=1"
```

4. **Set environment variables in Cloud Run Console**:
- Go to Cloud Run console
- Click on your service
- Click "Edit & Deploy New Revision"
- Under "Variables & Secrets", add all required environment variables

## Troubleshooting

### Bot not responding after deployment?
1. Check Cloud Run logs for errors
2. Verify all environment variables are set correctly
3. Ensure DATABASE_URL points to a publicly accessible database
4. Check if BOT_TOKEN is correct and complete

### Health check failing?
- Our endpoints are already configured correctly
- If still failing, increase memory allocation to 1GB

### Database connection errors?
- Replit's local PostgreSQL won't work in Cloud Run
- Use a cloud PostgreSQL service and update DATABASE_URL

## Testing Deployment
After deployment, test these endpoints:
- `https://your-service-url.run.app/` - Should return JSON status
- `https://your-service-url.run.app/health` - Should return health status
- `https://your-service-url.run.app/status` - Should return bot status

Then test the bot in Telegram to ensure it's responding to messages.