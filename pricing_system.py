"""
Progressive Frequency Pricing System for I3lani Bot
Handles all pricing calculations and plan management
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class PricingSystem:
    """Progressive frequency pricing system"""
    
    # Base pricing configuration
    BASE_RATE_PER_POST = 1.0  # $1 per post per channel
    
    # Progressive plans with discount tiers
    PROGRESSIVE_PLANS = {
        1: {
            'name': '1 Month Plan',
            'duration_months': 1,
            'posts_per_day': 1,
            'total_posts': 30,
            'discount_percent': 10,
            'base_price': 30.0,
            'discounted_price': 27.0
        },
        2: {
            'name': '2 Month Plan',
            'duration_months': 2,
            'posts_per_day': 2,
            'total_posts': 120,
            'discount_percent': 15,
            'base_price': 120.0,
            'discounted_price': 102.0
        },
        3: {
            'name': '3 Month Plan',
            'duration_months': 3,
            'posts_per_day': 3,
            'total_posts': 270,
            'discount_percent': 20,
            'base_price': 270.0,
            'discounted_price': 216.0
        },
        4: {
            'name': '4 Month Plan',
            'duration_months': 4,
            'posts_per_day': 4,
            'total_posts': 480,
            'discount_percent': 22,
            'base_price': 480.0,
            'discounted_price': 374.4
        },
        5: {
            'name': '5 Month Plan',
            'duration_months': 5,
            'posts_per_day': 5,
            'total_posts': 750,
            'discount_percent': 25,
            'base_price': 750.0,
            'discounted_price': 562.5
        },
        6: {
            'name': '6 Month Plan',
            'duration_months': 6,
            'posts_per_day': 6,
            'total_posts': 1080,
            'discount_percent': 30,
            'base_price': 1080.0,
            'discounted_price': 756.0
        },
        7: {
            'name': '7 Month Plan',
            'duration_months': 7,
            'posts_per_day': 7,
            'total_posts': 1470,
            'discount_percent': 32,
            'base_price': 1470.0,
            'discounted_price': 999.6
        },
        8: {
            'name': '8 Month Plan',
            'duration_months': 8,
            'posts_per_day': 8,
            'total_posts': 1920,
            'discount_percent': 35,
            'base_price': 1920.0,
            'discounted_price': 1248.0
        },
        9: {
            'name': '9 Month Plan',
            'duration_months': 9,
            'posts_per_day': 9,
            'total_posts': 2430,
            'discount_percent': 37,
            'base_price': 2430.0,
            'discounted_price': 1530.9
        },
        10: {
            'name': '10 Month Plan',
            'duration_months': 10,
            'posts_per_day': 10,
            'total_posts': 3000,
            'discount_percent': 40,
            'base_price': 3000.0,
            'discounted_price': 1800.0
        },
        11: {
            'name': '11 Month Plan',
            'duration_months': 11,
            'posts_per_day': 11,
            'total_posts': 3630,
            'discount_percent': 42,
            'base_price': 3630.0,
            'discounted_price': 2105.4
        },
        12: {
            'name': '12 Month Plan',
            'duration_months': 12,
            'posts_per_day': 12,
            'total_posts': 4380,
            'discount_percent': 45,
            'base_price': 4380.0,
            'discounted_price': 2409.0
        }
    }
    
    @classmethod
    def get_plan(cls, plan_id: int) -> Dict:
        """Get plan details by ID"""
        return cls.PROGRESSIVE_PLANS.get(plan_id)
    
    @classmethod
    def get_all_plans(cls) -> List[Dict]:
        """Get all available plans"""
        return [
            {**plan, 'plan_id': plan_id}
            for plan_id, plan in cls.PROGRESSIVE_PLANS.items()
        ]
    
    @classmethod
    def calculate_savings(cls, plan_id: int) -> Dict:
        """Calculate savings for a plan"""
        plan = cls.get_plan(plan_id)
        if not plan:
            return {}
        
        savings_amount = plan['base_price'] - plan['discounted_price']
        return {
            'original_price': plan['base_price'],
            'discounted_price': plan['discounted_price'],
            'savings_amount': savings_amount,
            'discount_percent': plan['discount_percent']
        }
    
    @classmethod
    def format_plan_display(cls, plan_id: int, currency: str = 'USD') -> str:
        """Format plan for display"""
        plan = cls.get_plan(plan_id)
        if not plan:
            return "Plan not found"
        
        savings = cls.calculate_savings(plan_id)
        
        if currency == 'USD':
            price_symbol = '$'
            price = plan['discounted_price']
        else:
            # Convert to other currencies as needed
            price_symbol = '$'
            price = plan['discounted_price']
        
        return f"""
**{plan['name']}**
• Duration: {plan['duration_months']} months
• Posts per day: {plan['posts_per_day']}
• Total posts: {plan['total_posts']}
• Price: {price_symbol}{price:.0f} (Save {savings['discount_percent']}%)
• Original: {price_symbol}{savings['original_price']:.0f}
        """.strip()
    
    @classmethod
    def get_stars_price(cls, usd_price: float) -> int:
        """Convert USD to Telegram Stars (1 USD = 200 Stars)"""
        return int(usd_price * 200)
    
    @classmethod
    def create_pricing_keyboard(cls, language: str = 'en') -> List[List[Dict]]:
        """Create pricing keyboard for user selection"""
        keyboard = []
        
        # Group plans into rows of 2
        plans = cls.get_all_plans()
        for i in range(0, len(plans), 2):
            row = []
            for j in range(2):
                if i + j < len(plans):
                    plan = plans[i + j]
                    button_text = f"{plan['duration_months']}M - ${plan['discounted_price']:.0f}"
                    row.append({
                        'text': button_text,
                        'callback_data': f"plan_{plan['plan_id']}"
                    })
            keyboard.append(row)
        
        # Add back button
        keyboard.append([{'text': '⬅️ Back', 'callback_data': 'back_to_start'}])
        
        return keyboard


def get_pricing_system():
    """Get pricing system instance"""
    return PricingSystem()