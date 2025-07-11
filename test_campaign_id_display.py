#!/usr/bin/env python3
"""
Test Campaign ID Display in Payment Confirmations
"""
import asyncio
import sqlite3
from datetime import datetime
import json

async def test_campaign_id_display():
    """Test that campaign IDs are displayed in payment confirmations"""
    print("🧪 TESTING CAMPAIGN ID DISPLAY IN PAYMENT CONFIRMATIONS")
    print("=" * 60)
    
    # 1. Check TON payment confirmation format
    print("\n1️⃣ CHECKING TON PAYMENT CONFIRMATION")
    print("-" * 40)
    
    with open('automatic_payment_confirmation.py', 'r') as f:
        content = f.read()
    
    if 'رقم الحملة الإعلانية:' in content:
        print("✅ Arabic campaign ID display found")
    else:
        print("❌ Arabic campaign ID display missing")
    
    if 'ID кампании:' in content:
        print("✅ Russian campaign ID display found")
    else:
        print("❌ Russian campaign ID display missing")
    
    if 'Campaign ID:' in content:
        print("✅ English campaign ID display found")
    else:
        print("❌ English campaign ID display missing")
    
    # 2. Check Stars payment confirmation format
    print("\n2️⃣ CHECKING STARS PAYMENT CONFIRMATION")
    print("-" * 40)
    
    with open('clean_stars_payment_system.py', 'r') as f:
        content = f.read()
    
    if 'رقم الحملة الإعلانية:' in content:
        print("✅ Arabic campaign ID display found")
    else:
        print("❌ Arabic campaign ID display missing")
    
    if 'ID кампании:' in content:
        print("✅ Russian campaign ID display found")
    else:
        print("❌ Russian campaign ID display missing")
    
    if 'Campaign ID:' in content:
        print("✅ English campaign ID display found")
    else:
        print("❌ English campaign ID display missing")
    
    # 3. Check database for recent campaigns
    print("\n3️⃣ CHECKING RECENT CAMPAIGNS")
    print("-" * 40)
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT campaign_id, user_id, payment_method, created_at
        FROM campaigns
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    recent_campaigns = cursor.fetchall()
    
    if recent_campaigns:
        print(f"Found {len(recent_campaigns)} recent campaigns:")
        for campaign in recent_campaigns:
            print(f"  - {campaign[0]} (User: {campaign[1]}, Method: {campaign[2]})")
    else:
        print("No recent campaigns found")
    
    # 4. Check campaign ID format
    print("\n4️⃣ CHECKING CAMPAIGN ID FORMAT")
    print("-" * 40)
    
    with open('campaign_management.py', 'r') as f:
        content = f.read()
    
    if 'CAM-' in content and 'generate_campaign_id' in content:
        print("✅ Campaign ID generation found (CAM-YYYY-MM-XXXX format)")
    else:
        print("❌ Campaign ID generation not found")
    
    # 5. Test a sample confirmation message
    print("\n5️⃣ SAMPLE CONFIRMATION MESSAGE")
    print("-" * 40)
    
    sample_campaign_id = "CAM-2025-07-TEST"
    sample_amount = 0.360
    sample_duration = 7
    sample_channels = 3
    sample_posts_per_day = 2
    sample_total_posts = sample_duration * sample_posts_per_day * sample_channels
    
    print("Arabic Sample:")
    print(f"""✅ تم تأكيد دفع TON!

تم التحقق من دفع TON الخاص بك على البلوك تشين!

💰 المبلغ المستلم: {sample_amount:.3f} TON

📅 مدة الحملة: {sample_duration} أيام
📊 تكرار النشر: {sample_posts_per_day} مرة يومياً
📺 القنوات: {sample_channels} قناة
📈 إجمالي المنشورات: {sample_total_posts} منشور

رقم الحملة الإعلانية: {sample_campaign_id}
🚀 حملتك الإعلانية تبدأ الآن!
🟢 الحالة: نشط""")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ CAMPAIGN ID DISPLAY TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_campaign_id_display())