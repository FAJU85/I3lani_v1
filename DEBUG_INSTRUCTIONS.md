# Debug Instructions for I3lani Bot

## Step-Based Debugging System

Every process in the I3lani Bot is assigned a unique step identifier for easy debugging and traceability.

### Step Naming Convention

Format: `Component_Step_Number_Description`

Examples:
- `CreateAd_Step_3_SelectDays`
- `Payment_Step_1_ChooseMethod`
- `Admin_Step_2_MainMenu`
- `Referral_Step_3_RewardDistribution`

### Using logger.py

The bot includes a comprehensive logging system with step identifiers:

```python
from logger import log_success, log_error, log_info, StepNames

# Log successful action
log_success(StepNames.SELECT_DAYS, user_id, "User selected 10 days", {
    'days_selected': 10,
    'discount_applied': 12,
    'price_calculated': 88.0
})

# Log error with context
try:
    result = calculate_price(days, channels)
except Exception as e:
    log_error(StepNames.CALCULATE_PRICE, user_id, e, {
        'days': days,
        'channels': channels
    })
```

### Step Identifiers Reference

#### User Flow Steps
- `User_Flow_1_Start` - /start command
- `User_Flow_2_LanguageSelection` - Language selection
- `User_Flow_3_MainMenu` - Main menu display

#### Ad Creation Steps
- `CreateAd_Step_1_Start` - Create ad button clicked
- `CreateAd_Step_2_UploadContent` - Content upload (text/image/video)
- `CreateAd_Step_3_SelectChannels` - Channel selection
- `CreateAd_Step_4_SelectDays` - Duration selection
- `CreateAd_Step_5_PostsPerDay` - Posts per day selection
- `CreateAd_Step_6_CalculatePrice` - Price calculation
- `CreateAd_Step_7_ShowSummary` - Payment summary

#### Payment Steps
- `Payment_Step_1_ChooseMethod` - Payment method selection
- `Payment_Step_2_TON_Init` - TON payment initialization
- `Payment_Step_3_TON_Monitor` - TON payment monitoring
- `Payment_Step_4_TON_Confirm` - TON payment confirmation
- `Payment_Step_2_Stars_Init` - Stars payment initialization
- `Payment_Step_3_Stars_Confirm` - Stars payment confirmation
- `Payment_Step_Error_Timeout` - Payment timeout

#### Admin Steps
- `Admin_Step_1_Access` - Admin panel access
- `Admin_Step_2_MainMenu` - Admin main menu
- `Admin_Step_3_ChannelManagement` - Channel management
- `Admin_Step_4_UserManagement` - User management
- `Admin_Step_5_Statistics` - Statistics view

#### Channel Management Steps
- `Channel_Step_1_Discovery` - Channel discovery
- `Channel_Step_2_Verification` - Channel verification
- `Channel_Step_3_Addition` - Channel addition
- `Channel_Step_4_Removal` - Channel removal

#### Referral Steps
- `Referral_Step_1_GenerateLink` - Generate referral link
- `Referral_Step_2_Registration` - New user registration via referral
- `Referral_Step_3_RewardDistribution` - Reward distribution

#### Error Steps
- `Error_Handler` - General error handling
- `Error_Callback_Timeout` - Callback query timeout
- `Error_Database` - Database errors
- `Error_TelegramAPI` - Telegram API errors

## Debugging Instructions

### 1. Identify the Affected Step

When debugging or modifying:
- Identify the step via name or number
- Locate the responsible file and function
- Understand expected vs actual behavior

### 2. Locate Files and Functions

**Step-to-File Mapping:**
- `CreateAd_Step_*` → `handlers.py`
- `Payment_Step_*` → `payments.py`, `stars_handler.py`
- `Admin_Step_*` → `admin_system.py`
- `Channel_Step_*` → `channel_manager.py`
- `Referral_Step_*` → `atomic_rewards.py`
- `*_CalculatePrice` → `frequency_pricing.py`

### 3. Add Logging to Functions

```python
async def your_function(user_id: int, data: dict):
    """Function with proper logging"""
    try:
        # Log step start
        log_info(StepNames.YOUR_STEP, user_id, "Starting operation", {
            'input_data': data
        })
        
        # Your logic here
        result = process_data(data)
        
        # Log success
        log_success(StepNames.YOUR_STEP, user_id, "Operation completed", {
            'result': result
        })
        
        return result
        
    except Exception as e:
        # Log error with context
        log_error(StepNames.YOUR_STEP, user_id, e, {
            'input_data': data,
            'error_context': 'specific_context'
        })
        raise
```

### 4. Fix Only Related Code

**Rules:**
- Only fix the related code in the identified step
- Do not affect unrelated functionality
- Respect the user's selected language
- Log your changes for traceability

### 5. Test Your Changes

After making changes:
1. Check logs for the specific step
2. Verify the fix addresses the issue
3. Test edge cases
4. Ensure no regression in other steps

## Example Bug Fix

**Bug Report:**
- Step: `CreateAd_Step_6_CalculatePrice`
- File: `frequency_pricing.py`
- Expected: 10 days should apply 12% discount
- Actual: Full price shown, no discount

**Fix Applied:**
```python
# BUG FIX: Ensure discount is properly applied for 10+ days
if discount_percent > 0:
    discount_amount = total_base_cost * (discount_percent / 100)
    final_cost_usd = total_base_cost - discount_amount
    
    # Log successful discount application
    log_success(StepNames.CALCULATE_PRICE, user_id, f"Applied {discount_percent}% discount", {
        'base_cost': total_base_cost,
        'discount_amount': discount_amount,
        'final_cost': final_cost_usd
    })
```

## Debug Utilities

### View User Journey
```python
from logger import debug_user_flow
debug_user_flow(user_id=123456)
```

### View Step Statistics
```python
from logger import debug_step_statistics
debug_step_statistics()
```

### Clear User Session
```python
from logger import clear_user_journey
clear_user_journey(user_id=123456)
```

## Common Debugging Scenarios

### 1. Payment Not Processing
Check steps:
- `Payment_Step_1_ChooseMethod`
- `Payment_Step_2_TON_Init` or `Payment_Step_2_Stars_Init`
- `Payment_Step_3_TON_Monitor` or `Payment_Step_3_Stars_Confirm`

### 2. Price Calculation Wrong
Check steps:
- `CreateAd_Step_6_CalculatePrice`
- Look for discount calculation in `frequency_pricing.py`

### 3. Channel Not Found
Check steps:
- `Channel_Step_1_Discovery`
- `Channel_Step_2_Verification`
- `CreateAd_Step_3_SelectChannels`

### 4. Language Issues
Check steps:
- `User_Flow_2_LanguageSelection`
- Any step with user-facing text

### 5. Admin Panel Issues
Check steps:
- `Admin_Step_1_Access`
- `Admin_Step_2_MainMenu`
- Specific admin function steps

## Log Analysis

### Successful Flow Example
```
[SUCCESS] User_Flow_1_Start - User 123456: User started bot
[SUCCESS] User_Flow_2_LanguageSelection - User 123456: Selected English
[SUCCESS] CreateAd_Step_1_Start - User 123456: Started ad creation
[SUCCESS] CreateAd_Step_6_CalculatePrice - User 123456: Applied 12% discount
```

### Error Flow Example
```
[SUCCESS] CreateAd_Step_4_SelectDays - User 123456: Selected 10 days
[ERROR] CreateAd_Step_6_CalculatePrice - User 123456: ERROR: Invalid discount calculation
[ERROR] CreateAd_Step_6_CalculatePrice - Data: {"days": 10, "error": "discount_not_applied"}
```

## Performance Monitoring

The logging system also tracks:
- Step success rates
- Common error patterns
- User journey completion rates
- Performance bottlenecks

Use `get_step_analytics()` to view comprehensive statistics.

## Important Notes

1. **Always log both success and error cases**
2. **Include relevant context data in logs**
3. **Use appropriate log levels (INFO, ERROR)**
4. **Respect user privacy in logs**
5. **Clean up test logs regularly**

This debugging system ensures complete traceability of all user interactions and makes identifying and fixing issues much easier.