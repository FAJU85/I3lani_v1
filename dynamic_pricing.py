"""
Dynamic Pricing Calculator for I3lani Bot
Food delivery assistant style with daily discounts
"""

from typing import Dict, Tuple


class DynamicPricing:
    """Dynamic pricing calculator with daily frequency discounts"""
    
    # Base pricing configuration
    BASE_PRICE_PER_POST = 1.0  # $1 per post
    
    # Exchange rates
    USD_TO_TON = 0.36  # $1 = 0.36 TON
    USD_TO_STARS = 34  # $1 = 34 Telegram Stars
    
    # Daily discount tiers based on posts per day
    DAILY_DISCOUNTS = {
        1: 0,      # No discount for 1 post/day
        2: 5,      # 5% discount for 2 posts/day
        3: 7,      # 7% discount for 3 posts/day
        4: 10,     # 10% discount for 4 posts/day
        5: 12,     # 12% discount for 5 posts/day
        6: 15,     # 15% discount for 6 posts/day
        7: 17,     # 17% discount for 7 posts/day
        8: 20,     # 20% discount for 8 posts/day
        9: 22,     # 22% discount for 9 posts/day
        10: 25,    # 25% discount for 10 posts/day
        11: 26,    # 26% discount for 11 posts/day
        12: 27,    # 27% discount for 12 posts/day
        13: 28,    # 28% discount for 13 posts/day
        14: 28,    # 28% discount for 14 posts/day
        15: 29,    # 29% discount for 15 posts/day
        16: 29,    # 29% discount for 16 posts/day
        17: 29,    # 29% discount for 17 posts/day
        18: 30,    # 30% discount for 18 posts/day
        19: 30,    # 30% discount for 19 posts/day
        20: 30,    # 30% discount for 20 posts/day
        21: 30,    # 30% discount for 21 posts/day
        22: 30,    # 30% discount for 22 posts/day
        23: 30,    # 30% discount for 23 posts/day
        24: 30,    # 30% discount for 24 posts/day (max)
    }
    
    @classmethod
    def get_daily_discount(cls, posts_per_day: int) -> int:
        """Get discount percentage for given posts per day"""
        if posts_per_day <= 0:
            return 0
        if posts_per_day > 24:
            return 30  # Max discount
        return cls.DAILY_DISCOUNTS.get(posts_per_day, 0)
    
    @classmethod
    def calculate_daily_cost(cls, posts_per_day: int) -> Tuple[float, int]:
        """Calculate daily cost and discount percentage"""
        if posts_per_day <= 0:
            return 0.0, 0
        
        base_daily_cost = posts_per_day * cls.BASE_PRICE_PER_POST
        discount_percent = cls.get_daily_discount(posts_per_day)
        discount_amount = base_daily_cost * (discount_percent / 100)
        daily_cost = base_daily_cost - discount_amount
        
        return daily_cost, discount_percent
    
    @classmethod
    def calculate_total_cost(cls, days: int, posts_per_day: int, channels: list = None) -> Dict:
        """Calculate total cost for the posting plan"""
        if days <= 0 or posts_per_day <= 0:
            return {
                'error': 'Invalid input: days and posts per day must be positive numbers'
            }
        
        # Calculate daily cost
        daily_cost, discount_percent = cls.calculate_daily_cost(posts_per_day)
        
        # Channel cost (currently $0 but structure for future)
        channel_cost = 0.0
        if channels:
            # Future: channel_cost = sum(channel.get('extra_cost', 0) for channel in channels)
            pass
        
        # Total calculation
        total_usd = (daily_cost * days) + channel_cost
        total_ton = total_usd * cls.USD_TO_TON
        total_stars = int(total_usd * cls.USD_TO_STARS)
        
        return {
            'days': days,
            'posts_per_day': posts_per_day,
            'daily_cost': daily_cost,
            'discount_percent': discount_percent,
            'channel_cost': channel_cost,
            'total_usd': total_usd,
            'total_ton': round(total_ton, 2),
            'total_stars': total_stars,
            'channels_count': len(channels) if channels else 0
        }
    
    @classmethod
    def format_pricing_summary(cls, calculation: Dict) -> str:
        """Format pricing calculation as shopping cart summary"""
        if 'error' in calculation:
            return f"❌ {calculation['error']}"
        
        discount_text = ""
        if calculation['discount_percent'] > 0:
            discount_text = f" (after {calculation['discount_percent']}% discount)"
        
        channel_text = ""
        if calculation['channels_count'] > 0:
            channel_text = f"\n- Channels: {calculation['channels_count']} (${calculation['channel_cost']:.2f})"
        
        return f"""
🧾 **Your Posting Plan Summary**

📅 **Campaign Details:**
- Days: {calculation['days']}
- Posts/day: {calculation['posts_per_day']}
- Daily rate{discount_text}: **${calculation['daily_cost']:.2f}**{channel_text}

💰 **Total Cost:**
- **TON: {calculation['total_ton']} TON**
- **Stars: {calculation['total_stars']} ⭐**

💡 *All channels currently cost $0 — extra toppings coming soon!*
        """.strip()
    
    @classmethod
    def create_payment_keyboard_data(cls, calculation: Dict) -> list:
        """Create payment keyboard data"""
        if 'error' in calculation:
            return [
                [{'text': '❌ Fix Input', 'callback_data': 'fix_input'}],
                [{'text': '⬅️ Back', 'callback_data': 'back_to_start'}]
            ]
        
        return [
            [
                {'text': f'🔷 Pay {calculation["total_ton"]} TON', 'callback_data': 'pay_dynamic_ton'},
                {'text': f'⭐ Pay {calculation["total_stars"]} Stars', 'callback_data': 'pay_dynamic_stars'}
            ],
            [
                {'text': '🔄 Recalculate', 'callback_data': 'recalculate_dynamic'},
                {'text': '⬅️ Back', 'callback_data': 'back_to_start'}
            ]
        ]
    
    @classmethod
    def get_discount_explanation(cls, posts_per_day: int) -> str:
        """Get explanation of discount for given posts per day"""
        if posts_per_day <= 1:
            return "💡 **Tip:** Order 2+ posts per day to get volume discounts!"
        
        discount = cls.get_daily_discount(posts_per_day)
        next_tier = posts_per_day + 1
        next_discount = cls.get_daily_discount(next_tier) if next_tier <= 24 else discount
        
        explanation = f"🎉 **Volume Discount:** {discount}% off for {posts_per_day} posts/day!"
        
        if next_discount > discount and next_tier <= 24:
            explanation += f"\n💡 **Tip:** Get {next_discount}% off with {next_tier} posts/day!"
        elif discount == 30:
            explanation += f"\n🏆 **Maximum Discount:** You've reached our best rate!"
        
        return explanation


def get_dynamic_pricing():
    """Get dynamic pricing instance"""
    return DynamicPricing()