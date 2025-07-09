# Manual Test Checklist - I3lani Bot

## Pre-Testing Setup

### Environment Variables Required
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `ADMIN_IDS` - Comma-separated admin user IDs
- `TON_WALLET_ADDRESS` - TON wallet for payments
- `DATABASE_URL` - PostgreSQL connection string (auto-set on platforms)

### Test User Requirements
- Primary admin user (ID in ADMIN_IDS)
- Secondary test user (not admin)
- Test channels where bot is administrator

## Core Functionality Tests

### 1. Bot Startup and Health Check
**Test**: Bot initialization
**Steps**:
1. Start bot using `python deployment_server.py`
2. Check health endpoint: `curl http://localhost:5001/health`
3. Verify logs show "Bot Features:" message
4. Check database initialization logs

**Expected Results**:
- ✅ Flask server starts on port 5001
- ✅ Health endpoint returns JSON with bot status
- ✅ Database tables created successfully
- ✅ Channel discovery completes
- ✅ Bot shows "Start polling" message

### 2. Language Selection System
**Test**: Multi-language support
**Steps**:
1. Send `/start` to bot
2. Select "English" from language menu
3. Verify main menu appears in English
4. Send `/start` again, select "العربية" (Arabic)
5. Verify main menu appears in Arabic
6. Test Russian language selection

**Expected Results**:
- ✅ Language selection menu appears on first start
- ✅ Main menu text changes based on selected language
- ✅ Language preference persists across interactions
- ✅ Navigation buttons show correct language
- ✅ Error messages appear in selected language

### 3. Admin Panel Access
**Test**: Admin authentication and panel
**Steps**:
1. Send `/admin` from admin user account
2. Verify admin panel appears
3. Send `/admin` from non-admin user
4. Test each admin panel section

**Expected Results**:
- ✅ Admin user sees full admin panel
- ✅ Non-admin user gets "Access denied" message
- ✅ All admin buttons are clickable
- ✅ Statistics display real data
- ✅ Channel management shows active channels

### 4. Channel Management System
**Test**: Channel discovery and management
**Steps**:
1. Add bot as administrator to a test channel
2. Wait 30 seconds for auto-discovery
3. Check admin panel → Channel Management
4. Verify channel appears in list
5. Test channel toggle (activate/deactivate)
6. Remove bot from channel, verify auto-removal

**Expected Results**:
- ✅ New channels auto-discovered within 30 seconds
- ✅ Channel details (name, subscribers) displayed correctly
- ✅ Channel activation/deactivation works
- ✅ Removed channels disappear from list
- ✅ Channel analytics show real subscriber counts

## Ad Creation Flow Tests

### 5. Content Upload Process
**Test**: Ad creation with different content types
**Steps**:
1. Click "Create New Ad" button
2. Upload text message
3. Test with image upload
4. Test with video upload
5. Test with photo + text combination

**Expected Results**:
- ✅ Text uploads accepted and stored
- ✅ Image files processed correctly
- ✅ Video files handled properly
- ✅ Combined content (photo + text) works
- ✅ Content preview shows correctly

### 6. Channel Selection Interface
**Test**: Multi-channel selection
**Steps**:
1. After content upload, reach channel selection
2. Select single channel (click to add checkmark)
3. Test multiple channel selection
4. Verify total reach calculation
5. Test "Continue" button activation

**Expected Results**:
- ✅ Channels display with subscriber counts
- ✅ Selection indicators (✅/⭕) appear correctly
- ✅ Total reach calculates dynamically
- ✅ "Continue" button enables only when channels selected
- ✅ Channel refresh works properly

### 7. Dynamic Pricing System
**Test**: Price calculation with different parameters
**Steps**:
1. Select duration (test 1, 7, 30 days)
2. Adjust posts per day (test 1, 5, 10 posts)
3. Verify discount calculations
4. Check TON and Stars price conversion
5. Test price recalculation when changing parameters

**Expected Results**:
- ✅ Base price: $1 per post per day
- ✅ Volume discounts applied correctly (5%-30%)
- ✅ TON conversion: 1 USD = 0.36 TON
- ✅ Stars conversion: 1 USD = 34 Stars
- ✅ Price updates in real-time
- ✅ Discount explanations shown

## Payment System Tests

### 8. TON Cryptocurrency Payments
**Test**: TON blockchain payment processing
**Steps**:
1. Complete ad creation flow to payment
2. Select "Pay with TON" option
3. Note wallet address and memo code
4. Send test payment to provided address with memo
5. Wait for automatic confirmation (up to 30 seconds)
6. Verify payment success message

**Expected Results**:
- ✅ Wallet address displayed correctly
- ✅ Unique memo code generated
- ✅ 20-minute payment timer starts
- ✅ Payment detected automatically via blockchain
- ✅ Success message with navigation options
- ✅ Order marked as paid in database

### 9. Telegram Stars Payments
**Test**: Native Telegram payment system
**Steps**:
1. Complete ad creation flow to payment
2. Select "Pay with Telegram Stars" option
3. Complete payment through Telegram's interface
4. Verify payment confirmation
5. Check order status

**Expected Results**:
- ✅ Telegram Stars invoice generated
- ✅ Payment processed through Telegram
- ✅ Success callback received
- ✅ Order activated immediately
- ✅ Payment cancellation works

### 10. Payment Timeout Handling
**Test**: Payment expiration and recovery
**Steps**:
1. Start payment process
2. Wait 20 minutes without paying
3. Verify timeout notification
4. Test "Try Again" option
5. Test "Contact Support" functionality

**Expected Results**:
- ✅ Timeout warning after 20 minutes
- ✅ Clear explanation of what happened
- ✅ Retry option recreates payment
- ✅ Support contact information provided
- ✅ Payment session properly cleaned up

## Advanced Features Tests

### 11. Referral System
**Test**: Share & Win functionality
**Steps**:
1. Access "Share & Win Portal" from main menu
2. Generate referral link
3. Test link with new user registration
4. Verify reward distribution
5. Check referral statistics

**Expected Results**:
- ✅ Unique referral link generated
- ✅ New user registration via link tracked
- ✅ Rewards distributed automatically
- ✅ Referral statistics updated
- ✅ Tier progression works correctly

### 12. Gamification System
**Test**: Achievements and levels
**Steps**:
1. Access "Gaming Hub" from main menu
2. Check current level and XP
3. Perform actions to earn achievements
4. Test daily check-in system
5. View leaderboard

**Expected Results**:
- ✅ Current level displayed correctly
- ✅ XP progression tracked
- ✅ Achievements unlock properly
- ✅ Daily check-in rewards given
- ✅ Leaderboard shows rankings

### 13. Content Moderation
**Test**: Content approval system
**Steps**:
1. Submit ad with questionable content
2. Check admin moderation panel
3. Test content approval/rejection
4. Verify user notification system
5. Test violation tracking

**Expected Results**:
- ✅ Content flagged for review
- ✅ Admin moderation interface works
- ✅ Approval/rejection processed
- ✅ Users notified of decisions
- ✅ Violation history tracked

## Error Handling Tests

### 14. Database Connection Issues
**Test**: Database failure recovery
**Steps**:
1. Simulate database disconnection
2. Test bot behavior during outage
3. Verify graceful error messages
4. Test automatic reconnection

**Expected Results**:
- ✅ Graceful error handling
- ✅ User-friendly error messages
- ✅ No bot crashes
- ✅ Automatic recovery when database returns

### 15. Telegram API Errors
**Test**: API failure handling
**Steps**:
1. Test with invalid bot token
2. Test message sending failures
3. Test callback query timeouts
4. Verify error recovery

**Expected Results**:
- ✅ Clear error messages
- ✅ Bot continues operating
- ✅ Retry mechanisms work
- ✅ User experience maintained

## Performance Tests

### 16. High Load Handling
**Test**: Multiple concurrent users
**Steps**:
1. Simulate 10+ concurrent users
2. Test simultaneous ad creation
3. Monitor response times
4. Check memory usage

**Expected Results**:
- ✅ Response times under 2 seconds
- ✅ No timeouts or crashes
- ✅ Memory usage stable
- ✅ All users handled properly

### 17. Background Worker System
**Test**: Async task processing
**Steps**:
1. Start worker process
2. Monitor payment verification tasks
3. Check channel analytics updates
4. Verify reward processing

**Expected Results**:
- ✅ Workers process tasks regularly
- ✅ No task queue buildup
- ✅ Proper error handling
- ✅ Resource usage stable

## Deployment Tests

### 18. Railway Deployment
**Test**: Production deployment
**Steps**:
1. Deploy to Railway using ZIP package
2. Set environment variables
3. Test all functionality in production
4. Monitor logs and performance

**Expected Results**:
- ✅ Deployment completes successfully
- ✅ All features work in production
- ✅ Logs show no errors
- ✅ Performance meets requirements

### 19. Health Check Endpoints
**Test**: Monitoring endpoints
**Steps**:
1. Test GET /health endpoint
2. Test GET /status endpoint
3. Test GET / endpoint
4. Verify JSON responses

**Expected Results**:
- ✅ All endpoints return 200 OK
- ✅ JSON responses properly formatted
- ✅ Health status accurate
- ✅ Response times under 100ms

## Security Tests

### 20. Admin Access Control
**Test**: Security boundaries
**Steps**:
1. Test admin commands from non-admin user
2. Verify sensitive data protection
3. Test SQL injection attempts
4. Check environment variable security

**Expected Results**:
- ✅ Admin access properly restricted
- ✅ Sensitive data not exposed
- ✅ Database queries safe
- ✅ Environment variables secure

## Test Completion Checklist

After completing all tests, verify:
- [ ] All core functionality working
- [ ] Multi-language support operational
- [ ] Payment systems functioning
- [ ] Admin panel accessible
- [ ] Error handling graceful
- [ ] Performance acceptable
- [ ] Security measures effective
- [ ] Documentation accurate

## Test Environment Notes

- Use separate test database for testing
- Don't use production channels for testing
- Test with small amounts for payment verification
- Keep test data separate from production data
- Document any issues found during testing

## Success Criteria

Test suite passes if:
- 95%+ of test cases pass
- No critical functionality broken
- Performance meets requirements
- Security boundaries maintained
- User experience smooth
- Error handling graceful