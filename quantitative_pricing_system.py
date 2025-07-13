"""
Quantitative Pricing System for I3lani Bot
Implements mathematical formulas for any-day selection with progressive discounts
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class QuantitativePricingConfig:
    """Configuration for quantitative pricing"""
    base_price_per_post: float = 0.29  # P₀ = $0.29 per post per day
    max_discount: float = 25.0  # Maximum discount percentage
    discount_rate: float = 0.8  # Discount rate per day (0.8%)
    max_posts_per_day: int = 12  # Maximum posts per day
    min_days: int = 1
    max_days: int = 365
    
    # Conversion rates
    usd_to_ton: float = 0.36
    usd_to_stars: int = 34

class QuantitativePricingCalculator:
    """Calculator for quantitative pricing with mathematical formulas"""
    
    def __init__(self, config: QuantitativePricingConfig = None):
        self.config = config or QuantitativePricingConfig()
    
    def calculate_posts_per_day(self, days: int) -> int:
        """
        Calculate posts per day based on duration
        Formula: R = min(12, max(1, ⌊D/2.5⌋ + 1))
        """
        posts_per_day = max(1, math.floor(days / 2.5) + 1)
        return min(self.config.max_posts_per_day, posts_per_day)
    
    def calculate_discount_percentage(self, days: int) -> float:
        """
        Calculate progressive discount percentage
        Formula: δ = min(25%, D × 0.8%)
        """
        discount = days * self.config.discount_rate
        return min(self.config.max_discount, discount)
    
    def calculate_posting_schedule(self, posts_per_day: int) -> List[str]:
        """
        Calculate posting schedule with even distribution across 24 hours
        """
        if posts_per_day <= 1:
            return ["00:00"]
        
        interval_hours = 24 / posts_per_day
        posting_times = []
        
        for i in range(posts_per_day):
            hour = int(i * interval_hours)
            minute = int((i * interval_hours % 1) * 60)
            posting_times.append(f"{hour:02d}:{minute:02d}")
        
        return posting_times
    
    def calculate_price(self, days: int, channels: int, custom_posts_per_day: int = None) -> Dict:
        """
        Calculate total price with quantitative formulas
        Formula: Price = D × R × P₀ × (1 - δ)
        """
        # Use custom posts per day if provided, otherwise calculate
        posts_per_day = custom_posts_per_day or self.calculate_posts_per_day(days)
        
        # Calculate discount percentage
        discount_percentage = self.calculate_discount_percentage(days)
        
        # Calculate base price
        base_price = days * posts_per_day * channels * self.config.base_price_per_post
        
        # Apply discount
        discount_amount = base_price * (discount_percentage / 100)
        final_price = base_price - discount_amount
        
        # Calculate posting schedule
        posting_times = self.calculate_posting_schedule(posts_per_day)
        posting_interval = f"Every {24/posts_per_day:.1f} hours" if posts_per_day > 1 else "Once daily"
        
        # Convert to different currencies
        ton_price = final_price * self.config.usd_to_ton
        stars_price = int(final_price * self.config.usd_to_stars)
        
        return {
            'days': days,
            'channels': channels,
            'posts_per_day': posts_per_day,
            'base_price_per_post': self.config.base_price_per_post,
            'base_price': base_price,
            'discount_percentage': discount_percentage,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'savings': discount_amount,
            'ton_price': ton_price,
            'stars_price': stars_price,
            'posting_times': posting_times,
            'posting_interval': posting_interval,
            'total_posts': days * posts_per_day * channels
        }
    
    def get_pricing_matrix(self, channels: int = 1, max_days: int = 30) -> List[Dict]:
        """Generate pricing matrix for different day selections"""
        matrix = []
        
        # Key day selections
        key_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30]
        
        for days in key_days:
            if days <= max_days:
                pricing = self.calculate_price(days, channels)
                matrix.append(pricing)
        
        return matrix
    
    def get_next_discount_milestone(self, current_days: int) -> Tuple[int, float]:
        """Get next discount milestone"""
        milestones = [3, 7, 14, 30, 60, 90, 180, 365]
        
        for milestone in milestones:
            if milestone > current_days:
                discount = self.calculate_discount_percentage(milestone)
                return milestone, discount
        
        return None, None
    
    def validate_selection(self, days: int, posts_per_day: int) -> Dict:
        """Validate user selection"""
        errors = []
        warnings = []
        
        if days < self.config.min_days:
            errors.append(f"Minimum days: {self.config.min_days}")
        
        if days > self.config.max_days:
            errors.append(f"Maximum days: {self.config.max_days}")
        
        if posts_per_day > self.config.max_posts_per_day:
            errors.append(f"Maximum posts per day: {self.config.max_posts_per_day}")
        
        if posts_per_day < 1:
            errors.append("Minimum posts per day: 1")
        
        # Rate limiting warnings
        if posts_per_day > 12:
            warnings.append("High posting frequency may affect delivery")
        
        if days > 180:
            warnings.append("Long campaigns require careful content planning")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

# Global calculator instance
calculator = QuantitativePricingCalculator()

def calculate_quantitative_price(days: int, channels: int, custom_posts_per_day: int = None) -> Dict:
    """Global function for quantitative price calculation"""
    return calculator.calculate_price(days, channels, custom_posts_per_day)

def get_posting_schedule(posts_per_day: int) -> List[str]:
    """Global function for posting schedule calculation"""
    return calculator.calculate_posting_schedule(posts_per_day)

def get_pricing_matrix(channels: int = 1, max_days: int = 30) -> List[Dict]:
    """Global function for pricing matrix"""
    return calculator.get_pricing_matrix(channels, max_days)

# Example usage and testing
if __name__ == "__main__":
    calc = QuantitativePricingCalculator()
    
    # Test cases from the specification
    test_cases = [
        (1, 1),   # 1 day, 1 channel
        (3, 1),   # 3 days, 1 channel
        (7, 1),   # 7 days, 1 channel
        (30, 1),  # 30 days, 1 channel
        (365, 1), # 365 days, 1 channel
    ]
    
    print("Quantitative Pricing Test Results:")
    print("=" * 60)
    
    for days, channels in test_cases:
        result = calc.calculate_price(days, channels)
        print(f"Days: {days:3d} | Posts/Day: {result['posts_per_day']:2d} | "
              f"Discount: {result['discount_percentage']:5.1f}% | "
              f"Price: ${result['final_price']:6.2f} | "
              f"Interval: {result['posting_interval']}")
    
    print("\nPosting Schedule Examples:")
    print("=" * 40)
    
    for posts in [1, 2, 3, 4, 6, 12]:
        schedule = calc.calculate_posting_schedule(posts)
        print(f"{posts:2d} posts/day: {', '.join(schedule)}")