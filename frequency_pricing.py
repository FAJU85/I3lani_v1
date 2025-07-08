"""
Frequency-Based Pricing System for I3lani Bot
The more days purchased, the higher the posting frequency and better discounts
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FrequencyPricingSystem:
    """Advanced pricing system where more days = higher frequency + bigger discounts"""
    
    def __init__(self):
        # Base cost per post per channel per day
        self.BASE_COST_PER_POST = 0.50  # $0.50 per post per channel per day
        
        # Frequency tiers based on days purchased
        self.frequency_tiers = {
            1: {'posts_per_day': 1, 'discount': 0, 'name': 'Basic'},
            2: {'posts_per_day': 1, 'discount': 5, 'name': 'Starter'},
            3: {'posts_per_day': 2, 'discount': 10, 'name': 'Standard'},
            5: {'posts_per_day': 2, 'discount': 15, 'name': 'Enhanced'},
            7: {'posts_per_day': 3, 'discount': 20, 'name': 'Weekly'},
            10: {'posts_per_day': 3, 'discount': 25, 'name': 'Extended'},
            14: {'posts_per_day': 4, 'discount': 30, 'name': 'Bi-Weekly'},
            21: {'posts_per_day': 5, 'discount': 35, 'name': 'Premium'},
            30: {'posts_per_day': 6, 'discount': 40, 'name': 'Monthly'},
            45: {'posts_per_day': 7, 'discount': 45, 'name': 'Extended Monthly'},
            60: {'posts_per_day': 8, 'discount': 50, 'name': 'Bi-Monthly'},
            90: {'posts_per_day': 10, 'discount': 55, 'name': 'Quarterly'},
            180: {'posts_per_day': 12, 'discount': 60, 'name': 'Semi-Annual'},
            365: {'posts_per_day': 15, 'discount': 65, 'name': 'Annual'}
        }
        
        # Convert to USD equivalent (Telegram Stars)
        self.USD_TO_STARS = 34  # 1 USD = 34 Telegram Stars
        self.USD_TO_TON = 0.36  # 1 USD = 0.36 TON

    def get_tier_for_days(self, days: int) -> Dict:
        """Get the pricing tier for given number of days"""
        # Find the appropriate tier (highest tier that doesn't exceed days)
        applicable_tiers = [tier_days for tier_days in self.frequency_tiers.keys() if tier_days <= days]
        
        if not applicable_tiers:
            # Less than 1 day, use basic tier
            return {**self.frequency_tiers[1], 'tier_days': 1}
        
        tier_days = max(applicable_tiers)
        tier_data = self.frequency_tiers[tier_days].copy()
        tier_data['tier_days'] = tier_days
        
        return tier_data

    def calculate_pricing(self, days: int, channels_count: int) -> Dict:
        """Calculate comprehensive pricing for given days and channels"""
        
        tier = self.get_tier_for_days(days)
        posts_per_day = tier['posts_per_day']
        discount_percent = tier['discount']
        tier_name = tier['name']
        
        # Calculate base costs
        total_posts = days * posts_per_day * channels_count
        base_cost = total_posts * self.BASE_COST_PER_POST
        
        # Apply discount
        discount_amount = base_cost * (discount_percent / 100)
        final_cost_usd = base_cost - discount_amount
        
        # Convert to other currencies
        cost_stars = int(final_cost_usd * self.USD_TO_STARS)
        cost_ton = round(final_cost_usd * self.USD_TO_TON, 3)
        
        # Calculate per-day and per-channel costs
        cost_per_day = final_cost_usd / days if days > 0 else final_cost_usd
        cost_per_channel = final_cost_usd / channels_count if channels_count > 0 else final_cost_usd
        
        return {
            'days': days,
            'channels_count': channels_count,
            'tier_name': tier_name,
            'posts_per_day': posts_per_day,
            'total_posts': total_posts,
            'discount_percent': discount_percent,
            'base_cost_usd': round(base_cost, 2),
            'discount_amount_usd': round(discount_amount, 2),
            'final_cost_usd': round(final_cost_usd, 2),
            'cost_stars': cost_stars,
            'cost_ton': cost_ton,
            'cost_per_day_usd': round(cost_per_day, 2),
            'cost_per_channel_usd': round(cost_per_channel, 2),
            'posts_per_channel_per_day': posts_per_day,
            'savings_usd': round(discount_amount, 2),
            'savings_percent': discount_percent
        }

    def get_pricing_breakdown_text(self, pricing: Dict, language: str = 'en') -> str:
        """Generate detailed pricing breakdown text"""
        
        if language == 'ar':
            return f"""
💰 **تفاصيل التسعير - {pricing['tier_name']}**

📅 **المدة:** {pricing['days']} يوم
📺 **القنوات:** {pricing['channels_count']} قناة
📝 **المنشورات يومياً:** {pricing['posts_per_day']} منشور/قناة
📊 **إجمالي المنشورات:** {pricing['total_posts']:,} منشور

💵 **التكلفة الأساسية:** ${pricing['base_cost_usd']:.2f}
🎯 **الخصم ({pricing['discount_percent']}%):** -${pricing['discount_amount_usd']:.2f}
✅ **السعر النهائي:** ${pricing['final_cost_usd']:.2f}

⭐ **بالستارز:** {pricing['cost_stars']:,} ستارز
💎 **بالتون:** {pricing['cost_ton']:.3f} TON

📈 **التكلفة لكل يوم:** ${pricing['cost_per_day_usd']:.2f}
📺 **التكلفة لكل قناة:** ${pricing['cost_per_channel_usd']:.2f}

🎉 **وفرت:** ${pricing['savings_usd']:.2f} ({pricing['savings_percent']}%)
            """.strip()
        
        return f"""
💰 **Pricing Breakdown - {pricing['tier_name']} Tier**

📅 **Duration:** {pricing['days']} days
📺 **Channels:** {pricing['channels_count']} channels  
📝 **Posts per day:** {pricing['posts_per_day']} posts/channel
📊 **Total posts:** {pricing['total_posts']:,} posts

💵 **Base cost:** ${pricing['base_cost_usd']:.2f}
🎯 **Discount ({pricing['discount_percent']}%):** -${pricing['discount_amount_usd']:.2f}
✅ **Final price:** ${pricing['final_cost_usd']:.2f}

⭐ **In Stars:** {pricing['cost_stars']:,} Stars
💎 **In TON:** {pricing['cost_ton']:.3f} TON

📈 **Cost per day:** ${pricing['cost_per_day_usd']:.2f}
📺 **Cost per channel:** ${pricing['cost_per_channel_usd']:.2f}

🎉 **You save:** ${pricing['savings_usd']:.2f} ({pricing['savings_percent']}%)
        """.strip()

    def get_available_tiers(self) -> List[Dict]:
        """Get list of all available pricing tiers"""
        tiers = []
        for days, tier_data in self.frequency_tiers.items():
            tier_info = {
                'days': days,
                'name': tier_data['name'],
                'posts_per_day': tier_data['posts_per_day'],
                'discount': tier_data['discount'],
                'description': f"{tier_data['posts_per_day']} posts/day, {tier_data['discount']}% off"
            }
            tiers.append(tier_info)
        
        return tiers

    def get_tier_comparison(self, days_list: List[int], channels_count: int = 1) -> List[Dict]:
        """Compare multiple tiers for easy selection"""
        comparisons = []
        
        for days in days_list:
            pricing = self.calculate_pricing(days, channels_count)
            comparison = {
                'days': days,
                'tier_name': pricing['tier_name'],
                'posts_per_day': pricing['posts_per_day'],
                'total_posts': pricing['total_posts'],
                'discount_percent': pricing['discount_percent'],
                'final_cost_usd': pricing['final_cost_usd'],
                'cost_stars': pricing['cost_stars'],
                'cost_ton': pricing['cost_ton'],
                'savings_usd': pricing['savings_usd'],
                'value_score': (pricing['total_posts'] * pricing['discount_percent']) / pricing['final_cost_usd'] if pricing['final_cost_usd'] > 0 else 0
            }
            comparisons.append(comparison)
        
        # Sort by value score (best value first)
        comparisons.sort(key=lambda x: x['value_score'], reverse=True)
        
        return comparisons

    def get_recommendations(self, channels_count: int = 1) -> Dict:
        """Get tier recommendations based on value and usage patterns"""
        
        # Popular tier comparisons
        popular_tiers = [1, 3, 7, 14, 30, 90]
        comparisons = self.get_tier_comparison(popular_tiers, channels_count)
        
        recommendations = {
            'best_value': None,
            'most_popular': None,
            'premium_choice': None,
            'budget_friendly': None
        }
        
        # Best value (highest value score)
        if comparisons:
            recommendations['best_value'] = comparisons[0]
        
        # Most popular (typically 7-14 days)
        popular_options = [c for c in comparisons if 7 <= c['days'] <= 14]
        if popular_options:
            recommendations['most_popular'] = popular_options[0]
        
        # Premium choice (30+ days with good value)
        premium_options = [c for c in comparisons if c['days'] >= 30]
        if premium_options:
            recommendations['premium_choice'] = premium_options[0]
        
        # Budget friendly (lowest total cost)
        budget_options = sorted(comparisons, key=lambda x: x['final_cost_usd'])
        if budget_options:
            recommendations['budget_friendly'] = budget_options[0]
        
        return recommendations

def init_frequency_pricing():
    """Initialize frequency pricing system"""
    return FrequencyPricingSystem()