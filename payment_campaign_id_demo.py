#!/usr/bin/env python3
"""
Payment → Campaign ID Connection Demonstration
Shows how unique payment IDs connect to campaign IDs
"""

import asyncio
import sqlite3
import json
from datetime import datetime

async def demonstrate_payment_campaign_connection():
    """Demonstrate how payment IDs connect to campaign IDs"""
    
    print("🔗 PAYMENT → CAMPAIGN ID CONNECTION DEMO")
    print("="*50)
    
    # Step 1: Show payment memo generation
    print("1. PAYMENT MEMO GENERATION:")
    print("   User initiates payment → System generates unique memo")
    
    from payments import generate_memo
    
    # Generate sample payment memos
    for i in range(3):
        memo = generate_memo()
        print(f"   Payment #{i+1}: {memo}")
    
    print()
    
    # Step 2: Show payment tracking
    print("2. PAYMENT TRACKING:")
    print("   Memo connects to user_id for automatic confirmation")
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Show recent payment tracking entries
    cursor.execute("""
        SELECT user_id, memo, amount, status, created_at 
        FROM payment_memo_tracking 
        ORDER BY created_at DESC 
        LIMIT 3
    """)
    
    payment_tracks = cursor.fetchall()
    
    for user_id, memo, amount, status, created_at in payment_tracks:
        print(f"   User: {user_id} | Memo: {memo} | Amount: {amount} TON | Status: {status}")
    
    print()
    
    # Step 3: Show campaign creation with payment connection
    print("3. CAMPAIGN CREATION WITH PAYMENT CONNECTION:")
    print("   Payment confirmed → Campaign created with same memo")
    
    cursor.execute("""
        SELECT campaign_id, user_id, payment_memo, payment_amount, created_at
        FROM campaigns 
        ORDER BY created_at DESC 
        LIMIT 3
    """)
    
    campaigns = cursor.fetchall()
    
    for campaign_id, user_id, payment_memo, payment_amount, created_at in campaigns:
        print(f"   Campaign: {campaign_id}")
        print(f"     User: {user_id}")
        print(f"     Payment Memo: {payment_memo}")
        print(f"     Amount: {payment_amount} TON")
        print(f"     Created: {created_at}")
        print()
    
    # Step 4: Show complete connection mapping
    print("4. COMPLETE ID CONNECTION MAPPING:")
    print("   Every payment has TWO connected unique IDs")
    
    cursor.execute("""
        SELECT 
            pmt.memo as payment_memo,
            pmt.user_id,
            pmt.amount,
            c.campaign_id,
            c.created_at
        FROM payment_memo_tracking pmt
        LEFT JOIN campaigns c ON pmt.memo = c.payment_memo
        WHERE c.campaign_id IS NOT NULL
        ORDER BY c.created_at DESC
        LIMIT 5
    """)
    
    connections = cursor.fetchall()
    
    print("   Payment Memo → Campaign ID Connections:")
    for payment_memo, user_id, amount, campaign_id, created_at in connections:
        print(f"     {payment_memo} → {campaign_id}")
        print(f"       User: {user_id} | Amount: {amount} TON | Date: {created_at}")
    
    conn.close()
    
    print()
    print("5. ID SYSTEM BENEFITS:")
    print("   ✅ Payment traceability: Every payment has unique memo")
    print("   ✅ Campaign tracking: Every campaign has unique ID") 
    print("   ✅ Support efficiency: Can find campaign by payment memo")
    print("   ✅ User clarity: Both IDs visible in confirmations")
    print("   ✅ Audit trail: Complete payment → campaign history")
    
    print()
    print("6. REAL-WORLD EXAMPLE:")
    print("   User pays 0.36 TON → Gets memo 'AB1234'")
    print("   Payment detected → Creates campaign 'CAM-2025-07-XYZ1'")
    print("   Connection stored → AB1234 ↔ CAM-2025-07-XYZ1")
    print("   User sees both → Payment AB1234 created Campaign CAM-2025-07-XYZ1")
    print("   Support can trace → Memo AB1234 → Campaign CAM-2025-07-XYZ1")

if __name__ == "__main__":
    asyncio.run(demonstrate_payment_campaign_connection())