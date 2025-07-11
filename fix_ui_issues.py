#!/usr/bin/env python3
"""
Fix UI Issues for Channel Selection and Wallet Display
Addresses layout problems and missing information
"""

def create_channel_button_text(channel_name: str, subscriber_count: int, is_selected: bool = False) -> str:
    """Create properly formatted channel button text with subscriber count"""
    # Handle long channel names
    max_length = 25
    if len(channel_name) > max_length:
        display_name = channel_name[:max_length-3] + "..."
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
    indicator = "🟢" if is_selected else "⚪"
    
    # Create two-line button text
    button_text = f"{indicator} {display_name}\n👥 {sub_text} subscribers"
    
    return button_text

def create_wallet_button_text(wallet_address: str, is_current: bool = False) -> str:
    """Create properly formatted wallet button text"""
    # Truncate wallet address for display
    if len(wallet_address) > 20:
        display_address = f"{wallet_address[:8]}...{wallet_address[-8:]}"
    else:
        display_address = wallet_address
    
    # Add indicator for current wallet
    if is_current:
        return f"✅ Current: {display_address}"
    else:
        return f"💳 {display_address}"

def get_enhanced_channel_data() -> list:
    """Get channel data with proper formatting"""
    channels = [
        {"name": "@i3lani", "subscribers": 102, "id": "@i3lani"},
        {"name": "@smshco", "subscribers": 50, "id": "@smshco"},
        {"name": "@Five_SAR", "subscribers": 1500, "id": "@Five_SAR"},
        {"name": "@VeryLongChannelNameThatNeedsToBeShortened", "subscribers": 5000, "id": "@longchannel"}
    ]
    
    enhanced_channels = []
    for channel in channels:
        enhanced_channels.append({
            'channel_id': channel['id'],
            'name': channel['name'],
            'subscribers': channel['subscribers']
        })
    
    return enhanced_channels

def test_ui_fixes():
    """Test the UI fixes"""
    print("🧪 Testing UI Fixes...")
    print("=" * 50)
    
    # Test channel buttons
    print("\n📺 Channel Selection Buttons:")
    channels = get_enhanced_channel_data()
    
    for i, channel in enumerate(channels):
        is_selected = i % 2 == 0  # Alternate selection for demo
        button_text = create_channel_button_text(
            channel['name'], 
            channel['subscribers'], 
            is_selected
        )
        print(f"\nChannel {i+1}:")
        print(button_text)
        print("-" * 30)
    
    # Test wallet buttons
    print("\n💳 Wallet Selection Buttons:")
    wallets = [
        "UQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tpjk",
        "EQCDGpuy0XhoGxaM4BdIWFKBOGyLgPv5kblXur-2uvy0tsUh",
        "Short_Wallet_123"
    ]
    
    for i, wallet in enumerate(wallets):
        is_current = i == 0
        button_text = create_wallet_button_text(wallet, is_current)
        print(f"\nWallet {i+1}:")
        print(button_text)
        print("-" * 30)

if __name__ == "__main__":
    test_ui_fixes()