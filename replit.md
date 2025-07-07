# I3lani Telegram Bot Replit Configuration

## Overview

I3lani is a Telegram advertising bot that provides premium advertising services across multiple channels. The bot handles advertisement creation, payment processing (Telegram Stars and TON cryptocurrency), multi-language support, and comprehensive admin management. It features a sophisticated referral system, dynamic pricing, and intelligent flow validation.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Bot Layer**: Aiogram-based handlers for user interactions
- **Database Layer**: SQLite database with async operations
- **Payment Processing**: Dual payment system supporting Telegram Stars and TON cryptocurrency
- **Admin System**: Comprehensive admin panel for bot management
- **Debug System**: Real-time monitoring and troubleshooting
- **Referral System**: Affiliate tracking and rewards

## Key Components

### Core Bot Framework
- **Framework**: Aiogram (Python Telegram Bot API)
- **State Management**: FSM (Finite State Machine) for conversation flows
- **Message Routing**: Router-based handler organization
- **Multi-language Support**: Complete i18n implementation

### Database Schema
- **Users**: User profiles, preferences, referral tracking
- **Channels**: Channel management with pricing and subscriber counts
- **Packages**: Subscription packages with duration and pricing
- **Orders**: Advertisement orders with payment tracking
- **Bundles**: Channel bundles for bulk advertising
- **Admin Settings**: Bot configuration and admin preferences

### Payment System
- **Telegram Stars**: Native Telegram payment with webhook processing
- **TON Cryptocurrency**: Blockchain-based payments with memo system
- **Dynamic Pricing**: Multi-currency support with automatic conversion
- **Referral Discounts**: Friend discounts and reward system

### Admin Panel
- **Channel Management**: Add/edit/remove advertising channels
- **Package Management**: Create and configure subscription packages
- **User Analytics**: Track user behavior and payment history
- **Settings Management**: Global bot configuration
- **Broadcasting**: Admin message broadcasting system

## Data Flow

1. **User Onboarding**: Language selection → Main menu → Feature access
2. **Ad Creation**: Content upload → Channel selection → Duration selection → Payment
3. **Payment Processing**: Payment method selection → Transaction verification → Order activation
4. **Admin Approval**: Content review → Approval/rejection → Publishing schedule
5. **Referral Processing**: Link generation → Friend registration → Reward distribution

## External Dependencies

### Required APIs
- **Telegram Bot API**: Core bot functionality
- **TON API**: Cryptocurrency payment processing
- **Webhook Services**: Payment confirmation handling

### Environment Variables
- `BOT_TOKEN`: Telegram bot token
- `DATABASE_URL`: SQLite database connection
- `TON_API_KEY`: TON blockchain API key
- `TON_WALLET_ADDRESS`: Payment receiving wallet
- `ADMIN_IDS`: Comma-separated admin user IDs
- `WEBHOOK_URL`: Payment webhook endpoint

### Python Dependencies
- `aiogram`: Telegram bot framework
- `aiosqlite`: Async SQLite operations
- `flask`: Webhook server for Stars payments
- `requests`: HTTP client for API calls
- `sqlalchemy`: Database ORM (partially implemented)

## Deployment Strategy

### Development Environment
- SQLite database for local development
- Memory-based FSM storage
- File-based logging system
- Environment variable configuration

### Production Considerations
- Database migration to PostgreSQL recommended
- Redis for FSM state persistence
- Structured logging with external monitoring
- Webhook SSL/TLS configuration
- Auto-scaling for high user volumes

## Changelog

- July 07, 2025. Initial setup
- July 07, 2025. Critical syntax error fix - Fixed SyntaxError in handlers.py where error_recovery_handler function had malformed try-except block. Completed the try-except structure with proper error handling and fixed keyboard configuration. Bot now starts successfully without syntax errors.
- July 07, 2025. Complete codebase cleanup and bug fixes - Removed all duplicate files, unused imports, and redundant code. Fixed duplicate function definitions, removed unused modules (debug_system, flow_validator, keyboards, models, scheduler, referral_system), cleaned up import statements, and consolidated configuration into core files. Removed 20+ duplicate/unused files, fixed all import errors, and streamlined codebase to essential components only. Bot now runs with clean, optimized code structure.
- July 07, 2025. Dynamic channel management system - Implemented automatic channel detection and management. Bot now automatically adds channels to the database when it becomes an administrator and removes them when admin privileges are revoked. No more static channel configuration - only channels where bot is admin are available for advertising. Added channel_manager.py with ChatMemberUpdated handlers, database methods for automatic channel management, and multilingual error messages for no channels available.

## User Preferences

Preferred communication style: Simple, everyday language.