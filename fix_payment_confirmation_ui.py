#!/usr/bin/env python3
"""
Fix Payment Confirmation UI - Show Campaign ID After Payment
"""

import sqlite3
from datetime import datetime

def show_campaign_after_payment_fix():
    """Add campaign ID display to payment confirmation"""
    
    print("🔧 Fixing Payment Confirmation UI...")
    
    # Check if we need to add campaign ID display to payment handlers
    with open('automatic_payment_confirmation.py', 'r') as f:
        content = f.read()
    
    if 'Campaign ID:' in content:
        print("   ✅ Payment confirmation already shows campaign ID")
    else:
        print("   ⚠️  Payment confirmation needs campaign ID display")
    
    # Check recent payments and campaigns
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Get recent payments
    cursor.execute('''
        SELECT memo, amount, status, created_at 
        FROM untracked_payments 
        WHERE created_at > datetime('now', '-24 hours')
        ORDER BY created_at DESC
    ''')
    
    recent_payments = cursor.fetchall()
    print(f"\n📊 Recent payments (last 24 hours): {len(recent_payments)}")
    
    for memo, amount, status, created_at in recent_payments:
        # Find matching campaign
        cursor.execute('''
            SELECT campaign_id FROM campaigns 
            WHERE payment_memo = ? OR campaign_id LIKE ?
        ''', (memo, f'%{memo[:4]}%'))
        
        campaign = cursor.fetchone()
        campaign_id = campaign[0] if campaign else "Not found"
        
        print(f"   💰 {memo}: {amount} TON ({status}) → {campaign_id}")
    
    conn.close()
    
    # Check campaign list functionality
    print("\n🔧 Checking Campaign List Functionality...")
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Check if campaigns are properly visible
    cursor.execute('''
        SELECT user_id, COUNT(*) as count, MAX(created_at) as latest
        FROM campaigns
        GROUP BY user_id
        ORDER BY latest DESC
    ''')
    
    user_campaigns = cursor.fetchall()
    print(f"   📋 Users with campaigns: {len(user_campaigns)}")
    
    for user_id, count, latest in user_campaigns:
        print(f"   👤 User {user_id}: {count} campaigns (latest: {latest})")
    
    conn.close()
    
    print("\n✅ Payment confirmation UI analysis completed")

if __name__ == "__main__":
    show_campaign_after_payment_fix()