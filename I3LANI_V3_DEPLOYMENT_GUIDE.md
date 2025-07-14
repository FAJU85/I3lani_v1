# I3lani v3 Deployment Guide

## System Overview

I3lani v3 is a complete architectural transformation from subscription-based to auction-based advertising system. The new system provides:

- **Auction-Based Ad Placement**: Daily auctions match ads to channels based on category and bid amount
- **Multi-Role User Management**: Advertisers, Channel Owners, and Affiliates with distinct workflows
- **Dual Payment System**: TON cryptocurrency and Telegram Stars integration
- **Revenue Sharing**: 68% to channel owners, 32% to platform
- **Affiliate Commission**: 5% on referral activity
- **Withdrawal System**: $50 minimum threshold for TON withdrawals

## Architecture Components

### 1. Core Architecture (`i3lani_v3_architecture.py`)
- **I3laniV3Database**: Complete database schema with 7 tables
- **AuctionSystem**: Daily auction matching system
- **RevenueCalculator**: Automated revenue distribution
- **WithdrawalSystem**: TON withdrawal processing
- **I3laniV3Core**: Main system coordination

### 2. Bot Commands (`v3_bot_commands.py`)
- **Role Selection**: Advertiser, Channel Owner, Affiliate workflows
- **Ad Creation**: Content → Category → Bid Type → Bid Amount → Payment
- **Channel Registration**: Admin verification and category assignment
- **Statistics**: Role-specific performance metrics
- **User Management**: Profile and balance management

### 3. Auction System (`v3_auction_scheduler.py`)
- **Daily Auctions**: 9:00 AM automated auction execution
- **Ad Posting**: Automatic posting with trackable links
- **Performance Tracking**: Impression and click recording
- **Revenue Processing**: Real-time revenue calculation

### 4. Payment Integration (`v3_payment_integration.py`)
- **TON Payments**: Blockchain-based payment verification
- **Telegram Stars**: Native Telegram payment processing
- **Affiliate Commissions**: Automatic commission distribution
- **Payment Confirmation**: Automated payment verification workflows

### 5. Admin Interface (`v3_admin_commands.py`)
- **System Statistics**: Comprehensive dashboard
- **Ad Moderation**: Approval/rejection workflows
- **User Management**: Multi-role user administration
- **Financial Overview**: Revenue and commission tracking

### 6. Integration Layer (`v3_integration_main.py`)
- **Seamless Integration**: Works alongside existing bot systems
- **Click Tracking**: CPC ad performance monitoring
- **Statistics Dashboard**: Real-time system metrics
- **Admin Functions**: System administration tools

## Database Schema

### Users Table (`users_v3`)
```sql
- user_id (PRIMARY KEY)
- username, first_name
- user_type (advertiser, channel_owner, affiliate)
- balance_ton, balance_stars
- referrer_id (affiliate tracking)
- created_at
```

### Channels Table (`channels_v3`)
```sql
- channel_id (PRIMARY KEY)
- channel_name, category
- owner_id (foreign key)
- subscribers, is_active
- created_at
```

### Ads Table (`ads_v3`)
```sql
- ad_id (PRIMARY KEY)
- advertiser_id (foreign key)
- content, category
- bid_type (CPC/CPM), bid_amount
- status (pending, approved, rejected, active, completed)
- impressions, clicks, total_cost
- created_at
```

### Ad Placements Table (`ad_placements_v3`)
```sql
- placement_id (PRIMARY KEY)
- ad_id, channel_id (foreign keys)
- placement_date
- impressions, clicks, revenue
```

### Payments Table (`payments_v3`)
```sql
- payment_id (PRIMARY KEY)
- user_id (foreign key)
- amount, currency (TON/STARS)
- purpose, status
- transaction_hash
- created_at
```

### Withdrawals Table (`withdrawals_v3`)
```sql
- withdrawal_id (PRIMARY KEY)
- user_id (foreign key)
- amount, wallet_address
- status, transaction_hash
- created_at
```

### Commissions Table (`commissions_v3`)
```sql
- commission_id (PRIMARY KEY)
- affiliate_id, referred_user_id (foreign keys)
- amount, source
- created_at
```

## User Workflows

### Advertiser Workflow
1. **Registration**: Select "Advertiser" role
2. **Ad Creation**: Use "Create Ad" button
3. **Content Input**: Submit text, image, or video content
4. **Category Selection**: Choose from 10 categories
5. **Bid Configuration**: Select CPC or CPM, set bid amount
6. **Payment**: Pay with TON or Telegram Stars
7. **Admin Approval**: Wait for admin review
8. **Auction Entry**: Approved ads enter daily auction
9. **Performance Tracking**: Monitor impressions, clicks, costs

### Channel Owner Workflow
1. **Registration**: Select "Channel Owner" role
2. **Channel Addition**: Use "Add Channel" button
3. **Channel Verification**: Bot verifies admin permissions
4. **Category Assignment**: Select channel category
5. **Automatic Matching**: Receive ads through auction system
6. **Revenue Earning**: Earn 68% of ad revenue automatically
7. **Withdrawal**: Request TON withdrawals ($50 minimum)
8. **Performance Monitoring**: Track channel performance

### Affiliate Workflow
1. **Registration**: Select "Affiliate" role
2. **Referral Link**: Get unique referral link
3. **User Referral**: Share link with potential users
4. **Commission Earning**: Earn 5% on referral activity
5. **Balance Tracking**: Monitor commission earnings
6. **Withdrawal**: Request TON withdrawals ($50 minimum)

## Admin Functions

### System Administration (`/adminv3`)
- **System Stats**: User counts, revenue, auction results
- **Ad Moderation**: Approve/reject pending ads
- **User Management**: View user statistics and activity
- **Channel Management**: Monitor channel performance
- **Financial Overview**: Track payments, revenue, commissions
- **Force Auction**: Manually trigger auction system

### Key Admin Commands
- `/adminv3` - Main admin panel
- Ad approval/rejection workflows
- Force auction execution
- User role management
- Financial oversight

## Integration with Existing System

### Backward Compatibility
- V3 system runs alongside existing subscription system
- Shared payment infrastructure (TON/Stars)
- Common admin panel integration
- Unified user management

### New Features Added
- Daily auction system (9:00 AM)
- Multi-role user management
- CPC/CPM bidding system
- Trackable ad links
- Automated revenue sharing
- Affiliate commission system
- Enhanced admin interface

## Deployment Steps

### 1. Database Initialization
```python
# Automatic on first run
await i3lani_v3.initialize()
```

### 2. System Integration
```python
# In main_bot.py
from v3_integration_main import initialize_i3lani_v3
v3_integration = await initialize_i3lani_v3(bot, dp)
```

### 3. Admin Setup
```python
# Register admin handlers
from v3_admin_commands import setup_v3_admin_handlers
setup_v3_admin_handlers(dp, bot)
```

### 4. Payment Configuration
- TON wallet address: `UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB`
- Telegram Stars: Native integration
- Payment verification: Automated blockchain monitoring

### 5. Auction Scheduler
- Daily auctions: 9:00 AM automatic execution
- Ad posting: Immediate after auction
- Performance tracking: Real-time monitoring

## Production Considerations

### Performance Optimization
- Database indexing for auction queries
- Asynchronous payment processing
- Efficient ad posting with delays
- Cached statistics for admin panel

### Security Features
- Admin-only access controls
- Payment verification systems
- Affiliate commission validation
- Withdrawal approval workflows

### Monitoring and Logging
- Comprehensive system logging
- Auction execution tracking
- Payment processing monitoring
- Error handling and recovery

### Scalability
- Database optimization for large datasets
- Efficient auction algorithms
- Parallel ad posting capabilities
- Load balancing for high traffic

## Key Benefits

### For Advertisers
- Competitive bidding system
- Targeted audience reach
- Performance tracking
- Flexible payment options

### For Channel Owners
- Automated revenue generation
- 68% revenue share
- Category-based matching
- Performance analytics

### For Affiliates
- 5% commission on all referral activity
- Passive income opportunities
- Simple referral system
- TON-based withdrawals

### For Platform
- 32% revenue share
- Automated system management
- Comprehensive admin controls
- Scalable architecture

## Support and Maintenance

### Regular Tasks
- Daily auction monitoring
- Payment verification
- Ad moderation
- User support

### System Updates
- Database schema migrations
- Feature enhancements
- Performance optimizations
- Security updates

### Troubleshooting
- Auction system issues
- Payment processing problems
- Channel verification errors
- Withdrawal processing delays

## Conclusion

I3lani v3 represents a complete transformation to an auction-based advertising platform with comprehensive multi-role user management, automated revenue sharing, and enterprise-grade administrative controls. The system provides a scalable, secure, and efficient solution for Telegram-based advertising with integrated cryptocurrency payments and affiliate marketing capabilities.