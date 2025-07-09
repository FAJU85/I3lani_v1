# How TON Payment Verification Works in I3lani Bot

## Overview
The bot uses a sophisticated blockchain-based verification system to confirm TON payments automatically without requiring manual user confirmation.

## Key Components

### 1. **Unique Memo Generation**
When a user initiates a TON payment, the bot generates a unique memo code with exactly 2 uppercase letters followed by 4 digits (e.g., "AB1234", "XY5678"). This memo serves as a unique identifier linking the payment to the specific user and transaction.

### 2. **Payment Instructions**
The bot provides:
- TON wallet address: `UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB`
- Exact amount in TON (e.g., 0.36 TON)
- Unique memo code (e.g., "AB1234")
- 20-minute expiration timer

### 3. **Blockchain Monitoring**
The bot monitors the TON blockchain using the TonViewer API:
```python
async def monitor_ton_payment(user_id, memo, amount_ton, expiration_time, state):
    """Monitor TON payment using TonViewer API"""
    while time.time() < expiration_time:
        # Check blockchain for payment with matching memo
        payment_verified = await payment_processor.verify_ton_payment(memo, amount_ton)
        
        if payment_verified:
            # Payment found on blockchain!
            await handle_successful_ton_payment(user_id, memo, amount_ton, state)
            return
        
        # Wait 30 seconds before next check
        await asyncio.sleep(30)
```

### 4. **Verification Process**
Every 30 seconds, the bot:
1. Queries the TonViewer API for transactions to the wallet address
2. Looks for a transaction with the exact memo code
3. Verifies the amount matches (within tolerance)
4. Confirms the transaction is recent (within the 20-minute window)

### 5. **API Integration**
The bot uses TonViewer's API endpoint:
```
https://tonviewer.com/api/v1/blockchain/accounts/{wallet_address}/transactions
```

The API returns transaction details including:
- Transaction hash
- Sender address
- Amount
- Memo/comment field
- Timestamp

### 6. **Payment Confirmation**
When a matching payment is found:
1. Bot immediately stops monitoring
2. Updates payment status in database
3. Sends success message to user
4. Proceeds with ad publishing
5. No manual "I paid" button needed!

## Security Features

1. **Unique Memos**: Each payment has a unique identifier
2. **Amount Verification**: Ensures correct payment amount
3. **Time Window**: 20-minute expiration prevents old transactions
4. **Automatic Detection**: No manual confirmation reduces fraud
5. **Blockchain Proof**: All verifications are based on actual blockchain data

## User Experience

From the user's perspective:
1. Get payment instructions with memo
2. Send TON payment with memo
3. Bot automatically detects payment
4. Receive confirmation and ad is published

The entire process is automated and typically confirms within 30-60 seconds of the blockchain transaction being confirmed.

## Error Handling

If payment expires or fails:
- User receives notification
- Can retry with new memo
- Can switch to Stars payment
- Original memo becomes invalid after expiration