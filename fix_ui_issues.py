#!/usr/bin/env python3
"""
Fix UI Issues for Channel Selection and Wallet Display
Addresses layout problems and missing information
"""

import sqlite3
from typing import List, Dict

def create_channel_button_text(channel_name: str, subscriber_count: int, is_selected: bool = False) -> str:
    """Create properly formatted channel button text with subscriber count"""
    
    # Truncate long channel names
    if len(channel_name) > 20:
        display_name = channel_name[:17] + "..."
    else:
        display_name = channel_name
    
    # Format subscriber count
    if subscriber_count >= 1000000:
        sub_text = f"{subscriber_count/1000000:.1f}M"
    elif subscriber_count >= 1000:
        sub_text = f"{subscriber_count/1000:.1f}K"
    else:
        sub_text = str(subscriber_count)
    
    # Selection indicator
    indicator = "🟢" if is_selected else "⚪️"
    
    # Two-line format for better readability
    return f"{indicator} {display_name}\n📊 {sub_text} subscribers"

def create_wallet_button_text(wallet_address: str, is_current: bool = False) -> str:
    """Create properly formatted wallet button text"""
    
    # Truncate wallet address for display
    if len(wallet_address) > 20:
        display_address = wallet_address[:10] + "..." + wallet_address[-6:]
    else:
        display_address = wallet_address
    
    prefix = "✅ Current: " if is_current else "💳 "
    
    return f"{prefix}{display_address}"

def get_enhanced_channel_data() -> List[Dict]:
    """Get channel data with proper formatting"""
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Get channels with subscriber counts
    cursor.execute('''
        SELECT channel_id, channel_name, name, subscribers, active_subscribers, is_active
        FROM channels
        WHERE is_active = 1
        ORDER BY subscribers DESC
    ''')
    
    channels = cursor.fetchall()
    enhanced_channels = []
    
    for channel_id, channel_name, name, subscribers, active_subscribers, is_active in channels:
        # Use the better name
        display_name = channel_name or name or channel_id
        
        # Use active subscribers if available, otherwise regular subscribers
        sub_count = active_subscribers or subscribers or 0
        
        enhanced_channels.append({
            'channel_id': channel_id,
            'display_name': display_name,
            'subscriber_count': sub_count,
            'is_active': is_active,
            'button_text': create_channel_button_text(display_name, sub_count)
        })
    
    conn.close()
    return enhanced_channels

def test_ui_fixes():
    """Test the UI fixes"""
    print("🧪 Testing UI Fixes...")
    
    # Test channel button formatting
    test_cases = [
        ("Short Channel", 1500, False),
        ("Very Long Channel Name That Overflows", 1250000, True),
        ("Medium Channel Name", 850, False)
    ]
    
    for name, count, selected in test_cases:
        button_text = create_channel_button_text(name, count, selected)
        print(f"   Channel: {button_text.replace(chr(10), ' | ')}")
    
    # Test wallet button formatting
    test_wallets = [
        ("UQDZpONCwPqBcWezyEGK9ikCHMknoyTrBL-L2hATQbClmulB", True),
        ("EQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tsUh", False)
    ]
    
    for wallet, is_current in test_wallets:
        button_text = create_wallet_button_text(wallet, is_current)
        print(f"   Wallet: {button_text}")
    
    # Test enhanced channel data
    channels = get_enhanced_channel_data()
    print(f"\n   Enhanced channels: {len(channels)} found")
    for channel in channels[:3]:  # Show first 3
        print(f"   - {channel['display_name']}: {channel['subscriber_count']} subscribers")
    
    print("✅ UI fixes tested successfully")

if __name__ == "__main__":
    test_ui_fixes()