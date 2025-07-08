# Background Workers for I3lani Bot

## Overview
Background workers handle async tasks separately from the main bot, improving performance and reliability.

## What We've Built

### 1. Main Background Worker (`worker.py`)
Handles these tasks:
- **Payment Monitor**: Verifies TON payments every 30 seconds
- **Channel Analytics**: Updates channel stats every 6 hours  
- **Reward Processor**: Processes pending rewards every 5 minutes
- **Database Cleanup**: Cleans old data daily
- **Health Checker**: Monitors system health every 15 minutes

### 2. Task Queue System (`task_queue.py`)
- SQLite-based job queue (no Redis needed)
- Automatic retry with exponential backoff
- Task scheduling and prioritization
- Error handling and logging

### 3. Render Configuration
Updated `render.yaml` with:
- **Web Service**: Main bot (deployment_server.py)
- **Worker Service**: Background tasks (worker.py)
- **Shared Database**: Both services use same PostgreSQL

## How It Works

### Payment Verification Flow
1. User makes TON payment
2. Payment details stored in database
3. Background worker checks TonAPI every 30 seconds
4. When payment confirmed, user subscription activated

### Reward Processing Flow
1. User earns reward (referral, channel addition, etc.)
2. Reward added to queue
3. Background worker processes reward every 5 minutes
4. TON balance updated in user account

### Channel Analytics Flow
1. Worker updates channel stats every 6 hours
2. Gets subscriber count from Telegram API
3. Calculates active subscribers (45% of total)
4. Updates pricing based on new stats

## Benefits

### Performance
- Main bot stays responsive
- Heavy tasks don't block user interactions
- Parallel processing of multiple tasks

### Reliability
- Automatic retries for failed tasks
- Error logging and monitoring
- Graceful failure handling

### Scalability
- Easy to add new background tasks
- Can scale workers independently
- Queue-based processing prevents overload

## Deployment on Render

### Automatic Setup
Render will deploy both services from `render.yaml`:
1. **i3lani-bot**: Main web service
2. **i3lani-worker**: Background worker
3. **i3lani-db**: PostgreSQL database

### Free Tier Limits
- Web service: Sleeps after 15 min (worker keeps running)
- Worker service: Always running (doesn't sleep)
- Database: 1GB storage, 100 connections

### Monitoring
- Check logs in Render dashboard
- Worker logs show task processing
- Health checks every 15 minutes

## Common Background Tasks

### Payment Tasks
```python
# Add payment verification task
await queue.add_task('payment_verification', {
    'payment_id': 12345,
    'wallet_address': 'UQDZpO...',
    'amount': 10.0,
    'memo': 'i3lani_12345'
})
```

### Reward Tasks
```python
# Add reward distribution task
await queue.add_task('reward_distribution', {
    'user_id': 12345,
    'reward_type': 'referral',
    'amount': 2.0
}, delay_seconds=300)  # Process in 5 minutes
```

### Analytics Tasks
```python
# Add channel analytics task
await queue.add_task('channel_analytics', {
    'channel_id': '@i3lani',
    'force_update': True
}, delay_seconds=3600)  # Process in 1 hour
```

## Adding New Background Tasks

1. **Define Handler**:
```python
async def handle_my_task(payload):
    # Your task logic here
    pass
```

2. **Register Handler**:
```python
processor.register_handler('my_task', handle_my_task)
```

3. **Add to Queue**:
```python
await queue.add_task('my_task', {'data': 'value'})
```

## Best Practices

### Task Design
- Keep tasks small and focused
- Make tasks idempotent (safe to retry)
- Use proper error handling
- Log important events

### Error Handling
- Tasks automatically retry 3 times
- Failed tasks are logged with error message
- Critical errors alert admins

### Performance
- Use async/await for I/O operations
- Batch database operations when possible
- Monitor memory usage
- Clean up old tasks regularly

## Troubleshooting

### Worker Not Processing Tasks
1. Check worker logs in Render dashboard
2. Verify database connection
3. Ensure task handlers are registered

### High Memory Usage
1. Increase cleanup frequency
2. Process tasks in smaller batches
3. Monitor for memory leaks

### Payment Verification Issues
1. Check TonAPI availability
2. Verify wallet address format
3. Ensure memo matches expected format

## Future Enhancements

- Redis integration for better performance
- Task priorities and scheduling
- Distributed worker nodes
- Real-time task monitoring dashboard
- Webhook-based payment confirmations

Background workers make your bot more robust, scalable, and responsive!