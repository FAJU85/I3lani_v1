# Environment Variables Setup for I3lani Bot

## Required Secrets

### 1. BOT_TOKEN (Required)
**What it is:** Your Telegram bot token from @BotFather
**How to get:**
1. Open Telegram
2. Search for @BotFather
3. Send `/newbot` or use existing bot
4. Copy the token (looks like: `1234567890:ABCDEF...`)

**Set in Render:**
- Key: `BOT_TOKEN`
- Value: `1234567890:ABCDEF...` (your actual token)

### 2. ADMIN_IDS (Required)
**What it is:** Your Telegram user ID for admin access
**How to get:**
1. Open Telegram
2. Search for @userinfobot
3. Send `/start`
4. Bot will reply with your user ID (number like: `123456789`)

**Set in Render:**
- Key: `ADMIN_IDS`
- Value: `123456789` (your user ID)

### 3. TON_WALLET_ADDRESS (Optional)
**What it is:** Your TON wallet address for payments
**Default:** `UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB`
**How to get:**
1. Download TON Wallet app
2. Create wallet
3. Copy your wallet address

**Set in Render:**
- Key: `TON_WALLET_ADDRESS`
- Value: `UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB`

### 4. DATABASE_URL (Auto-set)
**What it is:** PostgreSQL database connection string
**How it works:** Render automatically sets this when you create PostgreSQL database
**Don't modify:** This is set automatically by Render

### 5. DISABLE_STARS_FLASK (Auto-set)
**What it is:** Prevents duplicate Flask servers
**Value:** `1`
**How it works:** Render sets this automatically from render.yaml

## Setting Environment Variables in Render

### During Deployment
1. Go to your service in Render dashboard
2. Click "Environment" tab
3. Add each variable:
   - Click "Add Environment Variable"
   - Enter key and value
   - Click "Save Changes"

### After Deployment
1. Go to service settings
2. Click "Environment"
3. Add or edit variables
4. Service will auto-deploy with new variables

## Testing Your Secrets

### 1. Check Bot Token
```
Send /start to your bot
If bot responds → Token is correct
If no response → Check token format
```

### 2. Check Admin Access
```
Send /admin to your bot
If admin panel opens → Admin ID is correct
If "not authorized" → Check user ID
```

### 3. Check Database
```
Look at service logs
If "Database initialized" → Database URL is correct
If connection errors → Check PostgreSQL service
```

## Common Issues

### Bot Not Responding
- **Problem:** BOT_TOKEN is incorrect
- **Solution:** Get new token from @BotFather
- **Check:** Token should be ~45 characters with colon

### Admin Panel Not Working
- **Problem:** ADMIN_IDS is incorrect
- **Solution:** Get user ID from @userinfobot
- **Check:** Should be numbers only, no spaces

### Database Errors
- **Problem:** DATABASE_URL is wrong
- **Solution:** Don't modify it, let Render set it
- **Check:** Should start with `postgresql://`

### Service Won't Start
- **Problem:** Missing required environment variables
- **Solution:** Add BOT_TOKEN and ADMIN_IDS
- **Check:** All required variables are set

## Security Best Practices

### Do NOT Share
- Never share your BOT_TOKEN
- Never commit secrets to GitHub
- Never post tokens in public channels

### GitHub Security
- Use `.env` files locally (not uploaded)
- Add `.env` to `.gitignore`
- Only set secrets in Render dashboard

### Token Management
- Regenerate tokens periodically
- Use different tokens for development/production
- Revoke tokens if compromised

## Quick Setup Checklist

- [ ] Get BOT_TOKEN from @BotFather
- [ ] Get ADMIN_IDS from @userinfobot
- [ ] Set both in Render dashboard
- [ ] Deploy service
- [ ] Test bot with `/start`
- [ ] Test admin with `/admin`
- [ ] Check service logs for errors

## Support

If you need help:
1. Check Render service logs first
2. Verify environment variables are set
3. Test each secret individually
4. Contact support through bot admin panel

Your bot will be secure and fully functional! 🔐