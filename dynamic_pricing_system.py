"""
Dynamic Pricing System for I3lani Bot
Supports interactive day selection with discounts and publishing frequency
"""
import asyncio
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class PricingConfig:
    """Configuration for dynamic pricing"""
    base_price_per_day: float = 2.0
    min_days: int = 1
    max_days: int = 365
    discount_tiers: Dict[int, float] = None
    publishing_frequency_options: List[int] = None
    
    def __post_init__(self):
        if self.discount_tiers is None:
            self.discount_tiers = {
                1: 0,      # 1 day: 0% discount
                3: 5,      # 3 days: 5% discount
                7: 10,     # 7 days: 10% discount
                14: 15,    # 14 days: 15% discount
                30: 20,    # 30 days: 20% discount
                90: 25,    # 90 days: 25% discount
                180: 30,   # 180 days: 30% discount
                365: 35    # 365 days: 35% discount
            }
        
        if self.publishing_frequency_options is None:
            self.publishing_frequency_options = [1, 2, 3, 4, 5]

class DynamicPricingCalculator:
    """Calculator for dynamic pricing with discounts"""
    
    def __init__(self, config: PricingConfig = None):
        self.config = config or PricingConfig()
    
    def calculate_discount_percentage(self, days: int) -> float:
        """Calculate discount percentage based on days"""
        # Find the highest applicable discount tier
        applicable_discount = 0
        for tier_days, discount in sorted(self.config.discount_tiers.items()):
            if days >= tier_days:
                applicable_discount = discount
            else:
                break
        
        return applicable_discount
    
    def calculate_price(self, days: int, channels: int, posts_per_day: int = 1) -> Dict:
        """Calculate total price with discount"""
        base_total = self.config.base_price_per_day * days * channels * posts_per_day
        discount_percentage = self.calculate_discount_percentage(days)
        discount_amount = base_total * (discount_percentage / 100)
        final_price = base_total - discount_amount
        
        return {
            'days': days,
            'channels': channels,
            'posts_per_day': posts_per_day,
            'base_price_per_day': self.config.base_price_per_day,
            'base_total': base_total,
            'discount_percentage': discount_percentage,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'savings': discount_amount
        }
    
    def get_next_discount_tier(self, current_days: int) -> Tuple[int, float]:
        """Get next discount tier information"""
        for tier_days, discount in sorted(self.config.discount_tiers.items()):
            if tier_days > current_days:
                return tier_days, discount
        return None, None

class DynamicDaysSelector:
    """Interactive days selector with dynamic pricing"""
    
    def __init__(self, calculator: DynamicPricingCalculator = None):
        self.calculator = calculator or DynamicPricingCalculator()
        self.current_days = 7  # Default starting point
        self.current_posts_per_day = 1  # Default publishing frequency
    
    def increment_days(self, step: int = 1) -> int:
        """Increment days with bounds checking"""
        new_days = min(self.current_days + step, self.calculator.config.max_days)
        self.current_days = new_days
        return new_days
    
    def decrement_days(self, step: int = 1) -> int:
        """Decrement days with bounds checking"""
        new_days = max(self.current_days - step, self.calculator.config.min_days)
        self.current_days = new_days
        return new_days
    
    def set_days(self, days: int) -> int:
        """Set days directly with bounds checking"""
        self.current_days = max(
            self.calculator.config.min_days, 
            min(days, self.calculator.config.max_days)
        )
        return self.current_days
    
    def set_posts_per_day(self, posts: int) -> int:
        """Set publishing frequency per day"""
        self.current_posts_per_day = max(1, min(posts, 10))  # Limit to 1-10 posts per day
        return self.current_posts_per_day
    
    def get_pricing_display(self, channels: int) -> Dict:
        """Get formatted pricing display information"""
        pricing = self.calculator.calculate_price(
            self.current_days, 
            channels, 
            self.current_posts_per_day
        )
        
        # Get next discount tier info
        next_tier_days, next_discount = self.calculator.get_next_discount_tier(self.current_days)
        
        return {
            **pricing,
            'next_discount_tier': {
                'days': next_tier_days,
                'discount': next_discount
            } if next_tier_days else None,
            'discount_message': self._get_discount_message(pricing['discount_percentage']),
            'savings_message': self._get_savings_message(pricing['savings']),
            'posts_per_day': self.current_posts_per_day
        }
    
    def _get_discount_message(self, discount: float) -> str:
        """Generate discount message"""
        if discount == 0:
            return "No discount"
        return f"{discount}% discount applied"
    
    def _get_savings_message(self, savings: float) -> str:
        """Generate savings message"""
        if savings == 0:
            return ""
        return f"You save ${savings:.2f}"

# Global instance
pricing_calculator = DynamicPricingCalculator()
days_selector = DynamicDaysSelector(pricing_calculator)

def get_pricing_calculator() -> DynamicPricingCalculator:
    """Get the global pricing calculator instance"""
    return pricing_calculator

def get_days_selector() -> DynamicDaysSelector:
    """Get the global days selector instance"""
    return days_selector

def format_dynamic_pricing_display(days: int, channels: int, posts_per_day: int, language: str = 'en') -> str:
    """Format the dynamic pricing display for UI"""
    selector = get_days_selector()
    selector.set_days(days)
    selector.set_posts_per_day(posts_per_day)
    
    pricing_info = selector.get_pricing_display(channels)
    
    if language == 'ar':
        return f"""⏰ **اختر مدة الإعلان**

🔽 **{days} يوم** 🔼
💰 **الخصم:** {pricing_info['discount_percentage']}%
📅 **النشر يومياً:** {posts_per_day} مرة

💵 **السعر الأساسي:** ${pricing_info['base_total']:.2f}
🎁 **التوفير:** ${pricing_info['savings']:.2f}
✨ **السعر النهائي:** ${pricing_info['final_price']:.2f}

📊 **التفاصيل:**
• {channels} قناة × {days} يوم × {posts_per_day} نشر/يوم
• السعر الأساسي: ${pricing_info['base_price_per_day']:.2f}/يوم/قناة"""
    
    elif language == 'ru':
        return f"""⏰ **Выберите длительность рекламы**

🔽 **{days} дней** 🔼
💰 **Скидка:** {pricing_info['discount_percentage']}%
📅 **Публикаций в день:** {posts_per_day}

💵 **Базовая цена:** ${pricing_info['base_total']:.2f}
🎁 **Экономия:** ${pricing_info['savings']:.2f}
✨ **Итоговая цена:** ${pricing_info['final_price']:.2f}

📊 **Детали:**
• {channels} каналов × {days} дней × {posts_per_day} публ./день
• Базовая цена: ${pricing_info['base_price_per_day']:.2f}/день/канал"""
    
    else:  # English
        return f"""⏰ **Select Ad Duration**

🔽 **{days} days** 🔼
💰 **Discount:** {pricing_info['discount_percentage']}%
📅 **Publish per day:** {posts_per_day}

💵 **Base Price:** ${pricing_info['base_total']:.2f}
🎁 **You Save:** ${pricing_info['savings']:.2f}
✨ **Final Price:** ${pricing_info['final_price']:.2f}

📊 **Breakdown:**
• {channels} channels × {days} days × {posts_per_day} posts/day
• Base rate: ${pricing_info['base_price_per_day']:.2f}/day/channel"""