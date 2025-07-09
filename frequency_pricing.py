"""
Frequency-Based Pricing System for I3lani Bot
The more days purchased, the higher the posting frequency and better discounts
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from logger import log_success, log_error, log_info, StepNames

logger = logging.getLogger(__name__)

class FrequencyPricingSystem:
    """Advanced pricing system where more days = higher frequency + bigger discounts"""
    
    def __init__(self):
        # Base cost per post per day (flat rate, not per channel)
        self.BASE_COST_PER_POST = 1.00  # $1.00 per post per day
        
        # Smart day-based frequency tiers (EXACT SPECIFICATION - Core Logic: We Sell Days, You Gain Reach)
        self.frequency_tiers = {
            1: {'posts_per_day': 1, 'discount': 0, 'name': 'Single Day', 'daily_rate': 1.00},
            3: {'posts_per_day': 2, 'discount': 5, 'name': '3-Day Boost', 'daily_rate': 2.00},
            5: {'posts_per_day': 3, 'discount': 7, 'name': '5-Day Power', 'daily_rate': 3.00},
            7: {'posts_per_day': 4, 'discount': 10, 'name': 'Weekly Pro', 'daily_rate': 4.00},
            10: {'posts_per_day': 5, 'discount': 12, 'name': '10-Day Elite', 'daily_rate': 5.00},
            15: {'posts_per_day': 6, 'discount': 15, 'name': '15-Day Premium', 'daily_rate': 6.00},
            20: {'posts_per_day': 8, 'discount': 18, 'name': '20-Day Ultra', 'daily_rate': 8.00},
            30: {'posts_per_day': 10, 'discount': 20, 'name': 'Monthly Max', 'daily_rate': 10.00},
            # Extended tiers for bulk buyers and brand campaigns
            45: {'posts_per_day': 12, 'discount': 25, 'name': 'Extended Power', 'daily_rate': 12.00},
            60: {'posts_per_day': 15, 'discount': 30, 'name': 'Bi-Monthly Pro', 'daily_rate': 15.00},
            90: {'posts_per_day': 20, 'discount': 35, 'name': 'Quarterly Elite', 'daily_rate': 20.00}
        }
        
        # Convert to USD equivalent (Telegram Stars)
        self.USD_TO_STARS = 34  # 1 USD = 34 Telegram Stars
        self.USD_TO_TON = 0.36  # 1 USD = 0.36 TON

    def get_tier_for_days(self, days: int) -> Dict:
        """Get the pricing tier for given number of days"""
        # Handle invalid input - ensure minimum 1 day
        if days < 1:
            days = 1
        
        # Find the appropriate tier (highest tier that doesn't exceed days)
        applicable_tiers = [tier_days for tier_days in self.frequency_tiers.keys() if tier_days <= days]
        
        if not applicable_tiers:
            # Less than 1 day, use basic tier
            return {**self.frequency_tiers[1], 'tier_days': 1}
        
        tier_days = max(applicable_tiers)
        tier_data = self.frequency_tiers[tier_days].copy()
        tier_data['tier_days'] = tier_days
        
        return tier_data

    def calculate_pricing(self, days: int, channels_count: int = 1, user_id: int = None) -> Dict:
        """
        Calculate smart day-based pricing (flat rate, not per channel)
        
        BUG FIX: Ensures discount is properly applied for 10+ day selections
        Step: CreateAd_Step_4_CalculatePrice
        """
        
        try:
            # Handle invalid input - ensure minimum 1 day
            if days < 1:
                days = 1
            
            # Log the pricing calculation step
            if user_id:
                log_info(StepNames.CALCULATE_PRICE, user_id, f"Calculating price for {days} days", {
                    'days': days,
                    'channels_count': channels_count
                })
            
            tier = self.get_tier_for_days(days)
            posts_per_day = tier['posts_per_day']
            discount_percent = tier['discount']
            tier_name = tier['name']
            
            # Calculate base costs using daily rate (flat rate - not multiplied by channels)
            daily_cost = tier.get('daily_rate', posts_per_day * self.BASE_COST_PER_POST)
            total_base_cost = days * daily_cost
            
            # BUG FIX: Ensure discount is properly applied for 10+ days
            # Previous issue: discount_percent was not being applied correctly
            if discount_percent > 0:
                discount_amount = total_base_cost * (discount_percent / 100)
                final_cost_usd = total_base_cost - discount_amount
                
                # Log successful discount application
                if user_id:
                    log_success(StepNames.CALCULATE_PRICE, user_id, f"Applied {discount_percent}% discount", {
                        'base_cost': total_base_cost,
                        'discount_amount': discount_amount,
                        'final_cost': final_cost_usd
                    })
            else:
                discount_amount = 0
                final_cost_usd = total_base_cost
                
                # Log no discount scenario
                if user_id:
                    log_info(StepNames.CALCULATE_PRICE, user_id, "No discount applied for this tier", {
                        'days': days,
                        'tier': tier_name
                    })
        
            # Convert to other currencies
            cost_stars = int(final_cost_usd * self.USD_TO_STARS)
            cost_ton = round(final_cost_usd * self.USD_TO_TON, 3)
            
            # Calculate total posts for the campaign
            total_posts = days * posts_per_day
            
            pricing_result = {
                'days': days,
                'channels_count': channels_count,
                'tier_name': tier_name,
                'posts_per_day': posts_per_day,
                'total_posts': total_posts,
                'discount_percent': discount_percent,
                'daily_price': round(daily_cost, 2),
                'base_cost_usd': round(total_base_cost, 2),
                'discount_amount_usd': round(discount_amount, 2),
                'final_cost_usd': round(final_cost_usd, 2),
                'cost_stars': cost_stars,
                'cost_ton': cost_ton,
                'savings_usd': round(discount_amount, 2),
                'savings_percent': discount_percent
            }
            
            # Log successful pricing calculation
            if user_id:
                log_success(StepNames.CALCULATE_PRICE, user_id, f"Price calculated: ${final_cost_usd:.2f} ({discount_percent}% discount)", {
                    'tier': tier_name,
                    'final_pricing': pricing_result
                })
            
            return pricing_result
            
        except Exception as e:
            if user_id:
                log_error(StepNames.CALCULATE_PRICE, user_id, e, {
                    'days': days,
                    'channels_count': channels_count
                })
            raise

        
        # Calculate total posts for the campaign
        total_posts = days * posts_per_day
        
        return {
            'days': days,
            'channels_count': channels_count,
            'tier_name': tier_name,
            'posts_per_day': posts_per_day,
            'total_posts': total_posts,
            'discount_percent': discount_percent,
            'daily_price': round(daily_cost, 2),
            'base_cost_usd': round(total_base_cost, 2),
            'discount_amount_usd': round(discount_amount, 2),
            'final_cost_usd': round(final_cost_usd, 2),
            'cost_stars': cost_stars,
            'cost_ton': cost_ton,
            'savings_usd': round(discount_amount, 2),
            'savings_percent': discount_percent
        }

    def get_pricing_breakdown_text(self, pricing: Dict, language: str = 'en') -> str:
        """Generate smart day-based pricing breakdown text"""
        
        if language == 'ar':
            return f"""
✅ **ملخص خطة الإعلان الخاصة بك:**

📅 **المدة:** {pricing['days']} يوم
📝 **المنشورات يومياً:** {pricing['posts_per_day']} منشور
💰 **الخصم:** {pricing['discount_percent']}%
💵 **السعر النهائي:** ${pricing['final_cost_usd']:.2f}

💎 **بالتون:** {pricing['cost_ton']:.3f} TON
⭐ **بالستارز:** {pricing['cost_stars']:,} ستارز

📌 **بتأكيد هذا الدفع، أنت توافق على اتفاقية الاستخدام.**

💳 **اختر طريقة الدفع:**
💎 ادفع بالتون
⭐ ادفع بستارز تليجرام
            """.strip()
        
        return f"""
✅ **Your Ad Plan Summary:**

📅 **Duration:** {pricing['days']} days
📝 **Posts per day:** {pricing['posts_per_day']} posts
💰 **Discount:** {pricing['discount_percent']}%
💵 **Final Price:** ${pricing['final_cost_usd']:.2f}

💎 **In TON:** {pricing['cost_ton']:.3f} TON
⭐ **In Telegram Stars:** {pricing['cost_stars']:,} Stars

📌 **By making this payment, you agree to the Usage Agreement.**

💳 **Choose your payment method:**
💎 Pay with TON
⭐ Pay with Telegram Stars
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