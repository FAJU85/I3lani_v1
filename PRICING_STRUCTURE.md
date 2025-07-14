# I3lani Bot Pricing Structure

## Core Pricing Model

**Base Price:** $0.29 per day (regardless of channel count or posts per day)

## Mathematical Formulas

### 1. Posts per Day Calculation
```
R = min(12, max(1, ⌊D/2.5⌋ + 1))
```
Where D = number of days

### 2. Discount Percentage
```
δ = min(25%, D × 0.8%)
```
Progressive discount based on campaign duration

### 3. Final Price
```
Price = D × $0.29 × (1 - δ)
```
Minimum price guarantee: $0.29

## Pricing Examples

| Duration | Base Price | Discount | Final Price | Posts/Day | TON Price | Stars Price |
|----------|------------|----------|-------------|-----------|-----------|-------------|
| 1 Day    | $0.29      | 0.8%     | $0.29       | 1         | 0.10 TON  | 10 Stars    |
| 3 Days   | $0.87      | 2.4%     | $0.85       | 2         | 0.31 TON  | 29 Stars    |
| 7 Days   | $2.03      | 5.6%     | $1.92       | 3         | 0.69 TON  | 65 Stars    |
| 14 Days  | $4.06      | 11.2%    | $3.61       | 6         | 1.30 TON  | 123 Stars   |
| 30 Days  | $8.70      | 24.0%    | $6.61       | 12        | 2.38 TON  | 225 Stars   |
| 365 Days | $105.85    | 25.0%    | $79.34      | 12        | 28.56 TON | 2,698 Stars |

## Currency Conversion Rates

- **TON:** USD × 0.36
- **Telegram Stars:** USD × 34

## Key Features

### Unlimited Channel Selection
- No additional cost for multiple channels
- Same price whether you select 1 or 100 channels

### Automatic Posting Schedule
- Posts distributed evenly across 24 hours
- Examples:
  - 1 post/day: 00:00
  - 2 posts/day: 00:00, 12:00
  - 3 posts/day: 00:00, 08:00, 16:00
  - 6 posts/day: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00

### Progressive Discounts
- Up to 25% off for longer campaigns
- Discount increases by 0.8% per day
- Maximum discount capped at 25%

### Minimum Price Protection
- Always at least $0.29 minimum
- Protects against extremely low prices

### Maximum Posts Limitation
- Up to 12 posts per day for campaigns ≥30 days
- Prevents spam while maximizing exposure

## Pricing Tiers Summary

### Short-term (1-7 days)
- **Target:** Quick promotions, event announcements
- **Posts:** 1-3 per day
- **Discount:** 0.8% - 5.6%
- **Best for:** Time-sensitive offers

### Medium-term (8-30 days)
- **Target:** Brand awareness, product launches
- **Posts:** 4-12 per day
- **Discount:** 6.4% - 24%
- **Best for:** Sustained marketing campaigns

### Long-term (31+ days)
- **Target:** Brand building, continuous presence
- **Posts:** 12 per day (maximum)
- **Discount:** 24% - 25%
- **Best for:** Long-term brand visibility

## Payment Methods

1. **TON Cryptocurrency**
   - Blockchain-based payments
   - Instant confirmation
   - Decentralized

2. **Telegram Stars**
   - Native Telegram payment
   - Integrated checkout
   - Instant processing

## Additional Benefits

- **Referral System:** 5% commission on referred users
- **Admin Free Access:** Administrators get free posting privileges
- **Multi-language Support:** English, Arabic, Russian
- **Content Types:** Text, images, videos, combinations
- **Real-time Analytics:** Campaign performance tracking