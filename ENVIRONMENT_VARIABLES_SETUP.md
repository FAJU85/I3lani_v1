# Environment Variables Setup for I3lani Bot

## What You Need to Set Manually

### Required Variables (Must Set):
1. **BOT_TOKEN** - Your Telegram bot token from @BotFather
2. **ADMIN_IDS** - Your Telegram user ID for admin access

### Optional Variables (Can Use Defaults):
3. **TON_WALLET_ADDRESS** - Your TON wallet (default provided)
4. **DATABASE_URL** - Auto-set by hosting platform
5. **DISABLE_STARS_FLASK** - Auto-set to prevent conflicts

## Step-by-Step Setup

### 1. Get Your Bot Token
1. Open Telegram
2. Search for @BotFather
3. Send `/mytoken` or `/newbot`
4. Copy the token (format: `1234567890:ABCDEF...`)

### 2. Get Your Admin ID
1. Search for @userinfobot in Telegram
2. Send `/start`
3. Copy your user ID (format: `123456789`)

### 3. Set Variables in Platform

#### For Railway:
1. Go to your service dashboard
2. Click "Variables" tab
3. Add:
   - Key: `BOT_TOKEN`, Value: `your_token_here`
   - Key: `ADMIN_IDS`, Value: `your_user_id_here`
4. Service auto-deploys with new variables

#### For Render:
1. Go to your service dashboard
2. Click "Environment" tab
3. Add same variables as above
4. Click "Save Changes"

#### For Google Cloud:
1. Go to Cloud Run console
2. Select your service
3. Click "Edit & Deploy New Revision"
4. Add environment variables
5. Deploy

## Default Values Already Set

### TON Wallet Address
```
UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB
```
You can use this default or replace with your own TON wallet.

### Database URL
Automatically set by the hosting platform when you create PostgreSQL database.

### Flask Disable Flag
Set to `1` to prevent duplicate servers - already configured in deployment files.

## Security Best Practices

### Never Include in Code:
- Bot tokens
- API keys
- Database passwords
- Wallet private keys

### Always Use Environment Variables:
- Set secrets in platform dashboard
- Never commit to GitHub
- Use different tokens for development/production

## Testing Your Setup

### 1. Check Bot Responds
Send `/start` to your bot - should show language selection

### 2. Check Admin Access
Send `/admin` to your bot - should show admin panel

### 3. Check Logs
Monitor platform logs for any missing variable errors

## Common Issues

### Bot Not Responding
- Check `BOT_TOKEN` is correct (no spaces, complete token)
- Verify bot is not blocked by you
- Check platform logs for connection errors

### Admin Panel Not Working
- Verify `ADMIN_IDS` is your exact user ID
- Check for typos in user ID
- Ensure no extra spaces in variable value

### Database Errors
- `DATABASE_URL` should be auto-set by platform
- If missing, check PostgreSQL service is running
- Verify database and web service are in same project

## Variable Format Examples

```bash
# Correct formats
BOT_TOKEN=1234567890:ABCDEF1234567890abcdef1234567890ABC
ADMIN_IDS=123456789
TON_WALLET_ADDRESS=UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB
DATABASE_URL=postgresql://user:pass@host:5432/db
DISABLE_STARS_FLASK=1
```

## Multiple Admins (Optional)

If you want multiple admins:
```bash
ADMIN_IDS=123456789,987654321,456789123
```
Separate multiple IDs with commas, no spaces.

## Next Steps After Setup

1. **Deploy** your service with environment variables
2. **Test** bot functionality
3. **Monitor** logs for any issues
4. **Share** bot with users

Your bot code is ready to go - you just need to provide these two essential keys for it to work!