# Contributing to I3lani Bot

## Overview

I3lani Bot is a sophisticated Telegram marketing bot with blockchain integration. This guide helps external contributors understand the codebase and contribution process.

## Getting Started

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd i3lani-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_minimal.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Required variables:
   BOT_TOKEN=your_bot_token_here
   ADMIN_IDS=your_telegram_user_id
   TON_WALLET_ADDRESS=your_ton_wallet
   ```

4. **Initialize database**
   ```bash
   python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

### Project Structure

```
i3lani-bot/
├── main.py                 # Main entry point
├── deployment_server.py    # Production deployment server
├── main_bot.py            # Core bot functionality
├── database.py            # Database operations
├── handlers.py            # Message handlers
├── admin_system.py        # Admin panel functionality
├── config.py              # Configuration management
├── languages.py           # Multi-language support
├── payments.py            # Payment processing
├── stars_handler.py       # Telegram Stars integration
├── channel_manager.py     # Channel management
├── atomic_rewards.py      # Reward system
├── gamification.py        # Gamification features
├── content_moderation.py  # Content moderation
├── anti_fraud.py          # Anti-fraud protection
├── requirements_minimal.txt # Production dependencies
├── manual-test-checklist.md # Testing guide
├── issues.md              # Bug tracking
└── docs/                  # Documentation
```

## Code Architecture

### Core Components

1. **Bot Layer** (`main_bot.py`, `handlers.py`)
   - Aiogram-based Telegram bot framework
   - Message routing and handler organization
   - FSM (Finite State Machine) for conversation flows

2. **Database Layer** (`database.py`)
   - SQLite with async operations (aiosqlite)
   - PostgreSQL support for production
   - Database schema management

3. **Payment System** (`payments.py`, `stars_handler.py`)
   - TON cryptocurrency integration
   - Telegram Stars native payments
   - Dynamic pricing calculations

4. **Admin System** (`admin_system.py`)
   - Comprehensive admin panel
   - User management and analytics
   - Channel management interface

5. **Feature Modules**
   - `channel_manager.py`: Channel discovery and management
   - `atomic_rewards.py`: Referral and reward system
   - `gamification.py`: Achievement and leveling system
   - `content_moderation.py`: Content approval system
   - `anti_fraud.py`: Fraud detection and prevention

### Key Design Patterns

1. **Async/Await**: All database and API operations use async patterns
2. **FSM States**: Conversation flows managed through finite state machines
3. **Modular Architecture**: Features separated into independent modules
4. **Error Handling**: Comprehensive try-catch blocks with logging
5. **Configuration Management**: Environment-based configuration

## Development Guidelines

### Code Style

- **Python Style**: Follow PEP 8 guidelines
- **Async Functions**: Use `async def` for I/O operations
- **Error Handling**: Always include proper exception handling
- **Logging**: Use structured logging with appropriate levels
- **Comments**: Add inline comments for complex logic

### Database Operations

```python
# Good: Async database operations
async def create_user(user_id: int, username: str):
    """Create new user with proper error handling"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "INSERT INTO users (id, username) VALUES (?, ?)",
                (user_id, username)
            )
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise
```

### Handler Implementation

```python
# Good: Handler with proper structure
async def command_handler(message: Message, state: FSMContext):
    """
    Handle specific command
    
    Args:
        message: Telegram message object
        state: FSM state for conversation flow
    """
    try:
        user_id = message.from_user.id
        
        # Get user data
        user = await db.get_user(user_id)
        if not user:
            await message.reply("User not found")
            return
        
        # Process command
        result = await process_command(user_id)
        
        # Send response
        await message.reply(result)
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        await message.reply("An error occurred")
```

### Adding New Features

1. **Create module file** (e.g., `new_feature.py`)
2. **Add database tables** in `database.py`
3. **Create handlers** following existing patterns
4. **Add to router** in appropriate handler setup
5. **Add translations** in `languages.py`
6. **Write tests** in `manual-test-checklist.md`
7. **Update documentation**

## Testing

### Manual Testing

1. Follow `manual-test-checklist.md` for comprehensive testing
2. Test all user workflows end-to-end
3. Verify multi-language support works
4. Test payment systems with small amounts
5. Check admin panel functionality

### Adding Tests

```python
# Add test cases to manual-test-checklist.md
### Test Name
**Test**: Feature description
**Steps**:
1. Step 1
2. Step 2
3. Step 3

**Expected Results**:
- ✅ Expected outcome 1
- ✅ Expected outcome 2
```

### Bug Reporting

Use `issues.md` template:
```markdown
**Issue Type**: Bug
**Priority**: High
**Component**: Payment System
**Environment**: Development

**Description**: Clear issue description

**Steps to Reproduce**:
1. Step 1
2. Step 2

**Expected**: What should happen
**Actual**: What actually happens
```

## Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
```bash
python deployment_server.py
```

### Platform Deployment
- **Railway**: Use `i3lani-bot-railway.zip`
- **Render**: Use `i3lani-bot-render.zip`
- **Cloud Run**: Use Docker configuration

## Contributing Process

### 1. Fork and Clone
```bash
git clone <your-fork-url>
cd i3lani-bot
git remote add upstream <original-repo-url>
```

### 2. Create Feature Branch
```bash
git checkout -b feature/new-feature-name
```

### 3. Make Changes
- Follow code style guidelines
- Add comprehensive comments
- Update documentation
- Add tests if needed

### 4. Test Changes
- Run manual test checklist
- Verify all functionality works
- Check for any breaking changes

### 5. Commit Changes
```bash
git add .
git commit -m "Add: Brief description of changes"
```

### 6. Push and Create PR
```bash
git push origin feature/new-feature-name
```

### 7. Code Review
- Address reviewer feedback
- Update documentation if needed
- Ensure all tests pass

## Common Issues and Solutions

### Database Connection Issues
```python
# Solution: Use proper async context manager
async with aiosqlite.connect(DATABASE_PATH) as db:
    # Database operations here
```

### Import Errors
```python
# Solution: Check module imports and file paths
from database import db  # Correct import
```

### State Management
```python
# Solution: Use FSM states properly
await state.set_state(AdCreationStates.upload_content)
```

### Error Handling
```python
# Solution: Always include try-catch blocks
try:
    # Risky operation
    result = await api_call()
except Exception as e:
    logger.error(f"API error: {e}")
    # Handle error gracefully
```

## Code Quality Standards

### Required Checks
- [ ] Code follows PEP 8 style guide
- [ ] All functions have docstrings
- [ ] Error handling implemented
- [ ] Database operations are async
- [ ] Logging added where appropriate
- [ ] Comments added for complex logic

### Performance Considerations
- Use async operations for I/O
- Implement proper database indexing
- Cache frequently accessed data
- Monitor memory usage
- Optimize database queries

## Documentation Requirements

### Code Documentation
- Function docstrings with Args and Returns
- Inline comments for complex logic
- Module-level documentation
- Database schema documentation

### User Documentation
- Update README.md if needed
- Add feature documentation
- Update deployment guides
- Update test documentation

## Security Considerations

### Environment Variables
- Never commit `.env` files
- Use environment variables for secrets
- Validate all user inputs
- Implement proper authentication

### Database Security
- Use parameterized queries
- Validate all inputs
- Implement proper access controls
- Regular security audits

## Getting Help

### Documentation
- Read existing code comments
- Check `replit.md` for project context
- Review `manual-test-checklist.md` for testing
- Check `issues.md` for known issues

### Community
- Create issue for bugs
- Ask questions in discussions
- Follow contribution guidelines
- Be respectful and helpful

## Release Process

### Version Control
- Use semantic versioning
- Tag releases properly
- Maintain changelog
- Document breaking changes

### Deployment
- Test in staging environment
- Run full test suite
- Deploy to production
- Monitor for issues

Thank you for contributing to I3lani Bot! Your contributions help make the bot better for everyone.