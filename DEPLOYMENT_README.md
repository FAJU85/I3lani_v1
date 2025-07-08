# I3lani Bot - Cloud Run Deployment Configuration

This document explains the deployment setup for the I3lani Telegram Bot on Google Cloud Run.

## Architecture Overview

The application has been restructured to meet Cloud Run requirements:

- **Flask Web Server**: Required for HTTP endpoint compliance
- **Telegram Bot**: Runs in background thread with proper signal handling
- **Health Monitoring**: Multiple endpoints for deployment health checks

## File Structure

### Core Deployment Files

- `deployment_server.py` - Main Flask application for Cloud Run
- `main_bot.py` - Core bot functionality (separated from web server)
- `main.py` - Legacy main file (kept for backward compatibility)

### Configuration

- Port: 5001 (configurable via PORT environment variable)
- Host: 0.0.0.0 (required for Cloud Run)
- Threading: Bot runs in daemon thread, Flask in main thread

## HTTP Endpoints

### Health Check Endpoints

- `GET /` - Primary health check
- `GET /health` - Secondary health check
- `GET /status` - Bot status monitoring

### Webhook Endpoints

- `POST /webhook` - Telegram webhook processing (future use)

## Response Format

All endpoints return JSON with consistent structure:

```json
{
  "status": "ok",
  "service": "I3lani Telegram Bot",
  "bot_status": "running|starting|error",
  "timestamp": "ISO 8601 timestamp"
}
```

## Environment Variables

Required for deployment:
- `BOT_TOKEN` - Telegram bot token
- `PORT` - Server port (defaults to 5001)
- Additional bot-specific variables (see main configuration)

## Deployment Process

1. **Local Development**: Use `python deployment_server.py`
2. **Cloud Run**: Automatically uses deployment_server.py
3. **Health Checks**: Cloud Run monitors `/` endpoint
4. **Bot Initialization**: Background thread starts bot with proper signal handling

## Threading Architecture

- **Main Thread**: Flask server handles HTTP requests
- **Background Thread**: Telegram bot polling (daemon thread)
- **Signal Handling**: Disabled for bot polling to prevent threading conflicts

## Monitoring

- **Flask Logs**: HTTP request/response logging
- **Bot Logs**: Telegram bot operations and errors
- **Health Status**: Real-time bot status via HTTP endpoints

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Another Flask server may be running (from stars_handler)
2. **Bot Not Starting**: Check logs for threading or configuration issues
3. **Health Check Failures**: Verify Flask server is responding on correct port

### Debug Commands

```bash
# Check if server is running
curl http://localhost:5001/health

# Check bot status
curl http://localhost:5001/status

# View logs
tail -f bot.log
```

## Production Considerations

- **WSGI Server**: Flask dev server shown in logs is normal for Cloud Run
- **Scaling**: Application supports horizontal scaling
- **Monitoring**: Health endpoints provide deployment status
- **Error Handling**: Graceful degradation if bot fails but server continues

## Success Indicators

✅ Flask server starts on 0.0.0.0:5001
✅ Health endpoints respond with 200 status
✅ Bot initializes in background thread
✅ All systems (database, handlers, etc.) initialize successfully
✅ Channel discovery and sync completes
✅ Application remains stable during operation

This configuration ensures the bot meets Cloud Run requirements while maintaining full functionality.