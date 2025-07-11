#!/usr/bin/env python3
"""Check current publishing status"""
import sqlite3

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

# Get overall stats
cursor.execute("""
    SELECT 
        COUNT(DISTINCT campaign_id) as active_campaigns,
        COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
        COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled
    FROM campaign_posts
    WHERE campaign_id IN (
        SELECT campaign_id FROM campaigns WHERE status = 'active'
    )
""")

stats = cursor.fetchone()
print(f"\n=== PUBLISHING STATUS ===")
print(f"Active Campaigns: {stats[0]}")
print(f"Published Posts: {stats[1]}")
print(f"Scheduled Posts: {stats[2]}")

# Get per-campaign breakdown
cursor.execute("""
    SELECT c.campaign_id, c.user_id,
           COUNT(cp.id) as total_posts,
           COUNT(CASE WHEN cp.status = 'published' THEN 1 END) as published,
           COUNT(CASE WHEN cp.status = 'scheduled' THEN 1 END) as scheduled
    FROM campaigns c
    LEFT JOIN campaign_posts cp ON c.campaign_id = cp.campaign_id
    WHERE c.status = 'active' AND cp.status IS NOT NULL
    GROUP BY c.campaign_id
    HAVING scheduled > 0
    ORDER BY scheduled DESC
    LIMIT 10
""")

print(f"\n=== CAMPAIGNS WITH PENDING POSTS ===")
campaigns = cursor.fetchall()
for campaign in campaigns:
    print(f"{campaign[0]}: {campaign[3]}/{campaign[2]} published, {campaign[4]} pending")

conn.close()