# Admin Control Panel & Bot Flow Guide

## 🔧 Admin Control Panel Access

### Admin Commands
- `/admin` - Access main admin dashboard
- `/add_channel` - Add new advertising channel
- Admin access restricted to users in ADMIN_IDS environment variable

### Dashboard Features

#### 📊 Statistics Overview
- **Total Orders**: All orders created in system
- **Confirmed Orders**: Successfully paid orders
- **Total Revenue**: Sum of all confirmed payments in TON
- **Active Campaigns**: Currently running advertisements
- **User Statistics**: Total registered users

#### 🛠 Channel Management
- **Add New Channels**: Configure new advertising channels
- **Edit Channel Details**: Modify pricing, description, subscriber count
- **Enable/Disable Channels**: Control channel availability
- **Pricing Configuration**: Set individual channel rates

#### 💰 Bundle Management
- **Create Packages**: Multi-month discount bundles
- **Bundle Pricing**: Configure discounts and bonus months
- **Package Analytics**: Track bundle popularity

#### ⚙️ System Settings
- **Wallet Configuration**: Update TON wallet address
- **Currency Rates**: Manage exchange rates (TON/USD/SAR/RUB)
- **Payment Settings**: Configure payment monitoring parameters
- **API Configuration**: TON API key management

#### 📋 Payment Monitoring
- **Live Payment Tracking**: Real-time blockchain monitoring
- **Manual Confirmation**: Override automatic detection
- **Transaction History**: Complete payment logs
- **Failed Payments**: Debug payment issues

## 🚀 Complete Bot User Flow

### 1. Initial User Interaction
```
User: /start
Bot: Welcome message + Channel selection interface
```

### 2. Channel Selection Phase
```
📺 Multi-Channel Selection Interface:
┌─────────────────────────────────┐
│ ☐ Tech Channel (5K subs)        │
│ ☐ Business Channel (12K subs)   │
│ ☐ Crypto Channel (8K subs)      │
│ ☐ Lifestyle Channel (15K subs)  │
├─────────────────────────────────┤
│ 📊 View Pricing                 │
│ ✅ Continue                     │
│ 🔄 Reset                        │
└─────────────────────────────────┘
```

### 3. Pricing Display
```
💰 Pricing Calculation:
- Selected: 2 channels
- Duration: 3 months
- Base price: 0.297 TON
- USD equivalent: $0.74
- SAR equivalent: 2.78 ر.س
- RUB equivalent: 75.42 ₽
```

### 4. Duration Selection
```
⏰ Duration Options:
┌─────────────────────────────────┐
│ 1 Month - 0.099 TON/channel     │
│ 3 Months - 10% discount         │
│ 6 Months - 15% discount         │
│ 12 Months - 20% discount        │
├─────────────────────────────────┤
│ 🔙 Back to Selection            │
└─────────────────────────────────┘
```

### 5. Payment Processing
```
💳 Payment Instructions:
┌─────────────────────────────────┐
│ 🏦 Wallet: UQDZpONCwPqBcWez... │
│ 💰 Amount: 0.297 TON           │
│ 🔖 Memo: INV_A3B7C9D2          │
│ ⏰ Expires: 30 minutes          │
├─────────────────────────────────┤
│ ✅ I Sent Payment               │
│ ❌ Cancel                       │
└─────────────────────────────────┘
```

### 6. Automatic Payment Detection
```
🔍 Real-time Blockchain Monitoring:
- Checks every 30 seconds
- Monitors for 30 minutes
- Searches for memo in transactions
- 5% tolerance for network fees
- Automatic campaign activation
```

### 7. Campaign Activation
```
🎉 Payment Confirmed!
Your payment detected on TON blockchain!

📦 Order: 7a301ffa-9713-471a
🔖 Memo: INV_A3B7C9D2
🚀 Campaign starting now!

Your ads will post across 2 channels
for the next 3 months.
```

## 🎯 Bot Command Structure

### User Commands
- `/start` - Begin channel selection
- `/help` - Show help information
- `/status` - Check campaign status

### Admin Commands
- `/admin` - Main admin dashboard
- `/add_channel` - Add new channel
- `/settings` - System settings
- `/stats` - Detailed statistics
- `/payments` - Payment monitoring

## 🔄 State Management

### User States
- `selecting_channels` - Channel selection phase
- `selecting_duration` - Duration/bundle selection
- `payment_pending` - Awaiting payment confirmation

### Admin States
- `main_menu` - Admin dashboard
- `channel_management` - Channel operations
- `bundle_management` - Package configuration
- `settings_management` - System settings

## 🏗 Technical Architecture

### Database Models
- **Users**: User registration and preferences
- **Channels**: Advertising channel configuration
- **Orders**: Campaign orders and payments
- **Bundles**: Multi-month discount packages
- **AdminSettings**: System configuration
- **PaymentTracking**: Transaction monitoring

### Integration Points
- **TON API**: Real blockchain monitoring
- **PostgreSQL**: Enterprise data persistence
- **Multi-currency**: Live exchange rates
- **Admin Panel**: Complete management interface

## 🚨 Error Handling

### User Experience
- Graceful fallbacks for network issues
- Clear error messages
- Automatic retry mechanisms
- Session state preservation

### Admin Tools
- Payment override capabilities
- Manual campaign activation
- System health monitoring
- Error log access

This comprehensive system provides enterprise-grade advertising bot functionality with professional admin controls and seamless user experience.