"""
UI Issue Fixes for Channel Selection
Provides functions to create proper channel button text and handle UI formatting
"""

def create_channel_button_text(channel_name: str, subscriber_count: int, is_selected: bool) -> str:
    """Create properly formatted channel button text"""
    try:
        # Handle None or empty channel name
        if not channel_name:
            channel_name = "Unknown Channel"
        
        # Truncate long channel names for mobile display
        if len(str(channel_name)) > 20:
            display_name = str(channel_name)[:17] + "..."
        else:
            display_name = str(channel_name)
        
        # Handle subscriber count formatting
        if subscriber_count is None or subscriber_count == "":
            subscribers_text = "N/A"
        elif isinstance(subscriber_count, (int, float)):
            if subscriber_count >= 1000:
                subscribers_text = f"{subscriber_count/1000:.1f}K"
            else:
                subscribers_text = str(int(subscriber_count))
        else:
            # Try to convert to int, fallback to string
            try:
                count = int(subscriber_count)
                if count >= 1000:
                    subscribers_text = f"{count/1000:.1f}K"
                else:
                    subscribers_text = str(count)
            except (ValueError, TypeError):
                subscribers_text = str(subscriber_count)
        
        # Selection indicator
        indicator = "🟢" if is_selected else "⚪"
        
        # Create button text with proper formatting
        return f"{indicator} {display_name} ({subscribers_text})"
        
    except Exception as e:
        # Fallback formatting
        indicator = "🟢" if is_selected else "⚪"
        return f"{indicator} {channel_name} ({subscriber_count})"

def format_wallet_address(address: str) -> str:
    """Format wallet address for display"""
    if not address or len(address) < 10:
        return address
    
    # Show first 10 and last 8 characters
    return f"{address[:10]}...{address[-8:]}"

def truncate_text(text: str, max_length: int = 30) -> str:
    """Truncate text with ellipsis if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."