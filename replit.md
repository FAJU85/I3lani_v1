# Telegram Ad Bot

## Overview

This is a Telegram bot designed to manage and schedule advertisements on a specific channel. The bot allows users to submit advertisement content, purchase posting packages using TON cryptocurrency, and automatically schedules reposts based on the selected package. The system includes admin approval workflows and payment confirmation mechanisms.

## System Architecture

The application follows a modular Python architecture using the aiogram library for Telegram bot functionality:

- **Bot Framework**: aiogram (asynchronous Telegram bot framework)
- **State Management**: FSM (Finite State Machine) for handling user interactions
- **Storage**: In-memory storage for advertisements and user data
- **Scheduling**: Custom scheduler for automated reposting
- **Payment**: TON cryptocurrency integration

## Key Components

### 1. Configuration Management (`config.py`)
- Environment variable handling for bot token, admin IDs, and channel configuration
- Package definitions with pricing and repost frequency
- TON wallet address configuration
- Error handling for missing required environment variables

### 2. Data Models (`models.py`)
- **Advertisement**: Core data structure containing user submissions, package details, and status tracking
- **AdContent**: Flexible content container supporting text, photo, and video advertisements
- **Status Enums**: Payment and advertisement status tracking (pending, confirmed, active, completed, etc.)
- **Storage Layer**: In-memory data persistence for advertisements

### 3. Bot Handlers (`handlers.py`)
- **State Management**: Multi-step user interaction flow using FSM
- **Content Processing**: Handles text, photo, and video advertisement submissions
- **Package Selection**: Interactive keyboard-based package selection
- **Payment Workflow**: TON payment confirmation and admin approval process
- **Admin Controls**: Advertisement approval and rejection mechanisms

### 4. User Interface (`keyboards.py`)
- **Package Selection**: Dynamic keyboard generation based on available packages
- **Payment Confirmation**: Interactive payment status reporting
- **Admin Approval**: Administrative control buttons for content moderation

### 5. Scheduler (`scheduler.py`)
- **Automated Posting**: Scheduled reposting based on package frequency
- **Channel Integration**: Direct posting to configured Telegram channel
- **Content Formatting**: Proper formatting for different content types (text, photo, video)
- **Status Tracking**: Automatic advertisement lifecycle management

### 6. Main Application (`main.py`)
- **Bot Initialization**: Setup and configuration of bot instance
- **Handler Registration**: Wiring of all bot handlers and commands
- **Startup/Shutdown**: Proper resource management and admin notifications
- **Scheduler Integration**: Background task management for automated posting

## Data Flow

1. **User Interaction**: User starts bot and submits advertisement content
2. **Package Selection**: User selects posting package (Starter, Pro, Growth, Elite)
3. **Payment Process**: User receives TON wallet address and confirms payment
4. **Admin Approval**: Administrators review and approve/reject advertisements
5. **Scheduling**: Approved ads are scheduled for immediate posting and future reposts
6. **Automated Posting**: Scheduler manages reposting based on package parameters
7. **Status Updates**: Real-time tracking of advertisement lifecycle

## External Dependencies

- **aiogram**: Telegram Bot API framework
- **TON Network**: Cryptocurrency payment processing
- **Telegram Channel**: Target channel for advertisement posting
- **Environment Variables**: Configuration management for deployment

## Deployment Strategy

The application is designed for multiple deployment platforms:
- **Heroku**: Complete deployment files provided (Procfile, runtime.txt, app.json)
- **Railway/DigitalOcean**: Compatible with Python deployment
- **Cloud providers**: AWS, GCP, Azure compatible
- Environment variable configuration
- In-memory storage (suitable for lightweight deployments)
- Asynchronous operations for scalability
- Error handling and logging for production reliability

**Heroku Deployment Files**:
- `Procfile` - Defines worker process
- `runtime.txt` - Python 3.11 specification
- `heroku_requirements.txt` - All dependencies listed
- `app.json` - One-click deployment configuration
- `HEROKU_DEPLOYMENT_GUIDE.md` - Complete deployment instructions

**Note**: The current implementation uses in-memory storage, which may require migration to persistent storage (such as PostgreSQL with Drizzle ORM) for production environments to ensure data persistence across restarts.

## Changelog

- July 04, 2025. Initial setup - Complete Telegram ad bot implementation
- July 04, 2025. Bot successfully deployed and running - @I3lani_bot
- July 04, 2025. Added comprehensive multi-language support (English, Arabic, Russian)
- July 04, 2025. Bug fix: Package selection freezing issue resolved - Added proper error handling and logging to callback handlers
- July 04, 2025. Enhanced payment workflow - Added unique payment memos, comprehensive user notifications, and campaign progress tracking
- July 05, 2025. Complete system upgrade - Implemented multi-channel selection, auto payment detection, PostgreSQL database, and admin panel
- July 05, 2025. Real TON API integration - Added authentic blockchain monitoring with TON API key for automatic payment confirmation
- July 05, 2025. Database foreign key fix - Added automatic user registration to prevent order creation errors
- July 06, 2025. Complete user flow implementation - Restructured bot to follow specific workflow: ad content first, then package selection, then channel selection, then payment
- July 06, 2025. Complete admin system implementation - Added comprehensive admin panel with pricing management, channel configuration, wallet management, statistics dashboard, and system settings
- July 06, 2025. Enhanced user interface implementation - Added persistent side menu with commands: /mystats, /bugreport, /support, /history, /refresh, welcome dashboard with campaign statistics, balance checking, and comprehensive user experience features
- July 06, 2025. I3lani specifications compliance implementation - Fixed memo format to AB0102, added menu button system, implemented complete referral system, created My Ads dashboard, and enhanced bot descriptions for multi-language support

## Current Status

✅ **Bot code is production-ready**
- Bot username: @I3lani_bot
- All core features implemented and tested
- Multi-language support active (English, Arabic, Russian)
- Language selection on first interaction
- Localized messages and buttons
- Scheduler running for automated reposts
- Manual payment verification workflow active
- Ready for GitHub upload and deployment
- Complete deployment files created for Render and Heroku

## New Multi-Language Features

### Supported Languages
- **English** 🇺🇸 - Default language
- **Arabic** 🇸🇦 - Full RTL support
- **Russian** 🇷🇺 - Complete localization

### Language System
- Automatic language selection on first interaction
- Persistent user language preferences
- All user messages, buttons, and notifications localized
- Admin notifications in admin's preferred language
- Payment instructions and confirmations translated
- Campaign completion notifications in user's language

## User Preferences

Preferred communication style: Simple, everyday language.