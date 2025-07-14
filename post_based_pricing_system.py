"""
Post-Based Pricing System for I3lani Bot
New tier-based pricing with post packages and optional add-ons
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class PostPackage(Enum):
    """Post package tiers"""
    STARTER = "starter"
    BASIC = "basic"
    GROWTH = "growth"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class PostPackageConfig:
    """Configuration for post packages"""
    name: str
    posts: int
    price_usd: float
    cost_per_post: float
    target_users: str

@dataclass
class AddOnConfig:
    """Configuration for add-ons"""
    name: str
    price_usd: float
    description: str

class PostBasedPricingSystem:
    """New post-based pricing system with packages and add-ons"""
    
    def __init__(self):
        # Conversion rates
        self.usd_to_ton = 0.36
        self.usd_to_stars = 34
        
        # Post packages
        self.packages = {
            PostPackage.STARTER: PostPackageConfig(
                name="Starter",
                posts=5,
                price_usd=1.45,
                cost_per_post=0.29,
                target_users="Trial users"
            ),
            PostPackage.BASIC: PostPackageConfig(
                name="Basic",
                posts=20,
                price_usd=4.99,
                cost_per_post=0.25,
                target_users="Quick campaigns"
            ),
            PostPackage.GROWTH: PostPackageConfig(
                name="Growth",
                posts=50,
                price_usd=9.99,
                cost_per_post=0.20,
                target_users="Consistent promoters"
            ),
            PostPackage.PRO: PostPackageConfig(
                name="Pro",
                posts=120,
                price_usd=19.99,
                cost_per_post=0.17,
                target_users="Marketers"
            ),
            PostPackage.ENTERPRISE: PostPackageConfig(
                name="Enterprise",
                posts=300,
                price_usd=39.99,
                cost_per_post=0.13,
                target_users="Agencies / Resellers"
            )
        }
        
        # Add-ons
        self.addons = {
            "auto_schedule_per_day": AddOnConfig(
                name="Daily Auto-Scheduling",
                price_usd=0.25,
                description="Automatically distributes posts across selected days"
            ),
            "advanced_analytics": AddOnConfig(
                name="Advanced Analytics",
                price_usd=0.99,
                description="Track clicks, referrers, devices, CTR with PDF export"
            ),
            "extra_channels": AddOnConfig(
                name="Extra 10 Channels",
                price_usd=0.50,
                description="Access to additional 10 channels"
            ),
            "pinned_post": AddOnConfig(
                name="Pinned in Channel",
                price_usd=0.75,
                description="Pin your post in selected channels"
            ),
            "top_hour_timing": AddOnConfig(
                name="Top-of-Hour Timing",
                price_usd=0.30,
                description="Schedule posts at optimal times"
            )
        }
        
        # Limits and rules
        self.max_posts_per_day = 12
        self.post_expiry_days = 90
        
    def get_package_info(self, package: PostPackage) -> Dict:
        """Get package information with pricing"""
        config = self.packages[package]
        
        return {
            'package': package.value,
            'name': config.name,
            'posts': config.posts,
            'price_usd': config.price_usd,
            'price_ton': config.price_usd * self.usd_to_ton,
            'price_stars': round(config.price_usd * self.usd_to_stars),
            'cost_per_post': config.cost_per_post,
            'target_users': config.target_users,
            'savings_vs_starter': self._calculate_savings(package, PostPackage.STARTER)
        }
    
    def get_all_packages(self) -> List[Dict]:
        """Get all package information"""
        return [self.get_package_info(pkg) for pkg in PostPackage]
    
    def get_addon_info(self, addon_key: str) -> Dict:
        """Get add-on information with pricing"""
        config = self.addons[addon_key]
        
        return {
            'key': addon_key,
            'name': config.name,
            'price_usd': config.price_usd,
            'price_ton': config.price_usd * self.usd_to_ton,
            'price_stars': round(config.price_usd * self.usd_to_stars),
            'description': config.description
        }
    
    def get_all_addons(self) -> List[Dict]:
        """Get all add-on information"""
        return [self.get_addon_info(key) for key in self.addons.keys()]
    
    def calculate_total_price(self, package: PostPackage, addons: List[str] = None, 
                            auto_schedule_days: int = 0) -> Dict:
        """Calculate total price with package and add-ons"""
        if addons is None:
            addons = []
            
        package_info = self.get_package_info(package)
        total_usd = package_info['price_usd']
        
        # Add auto-scheduling cost
        if auto_schedule_days > 0:
            auto_schedule_cost = auto_schedule_days * self.addons["auto_schedule_per_day"].price_usd
            total_usd += auto_schedule_cost
        
        # Add other add-ons
        addon_costs = []
        for addon_key in addons:
            if addon_key in self.addons and addon_key != "auto_schedule_per_day":
                addon_info = self.get_addon_info(addon_key)
                addon_costs.append(addon_info)
                total_usd += addon_info['price_usd']
        
        return {
            'package': package_info,
            'auto_schedule_days': auto_schedule_days,
            'auto_schedule_cost': auto_schedule_days * self.addons["auto_schedule_per_day"].price_usd if auto_schedule_days > 0 else 0,
            'addons': addon_costs,
            'total_usd': total_usd,
            'total_ton': total_usd * self.usd_to_ton,
            'total_stars': round(total_usd * self.usd_to_stars)
        }
    
    def _calculate_savings(self, package: PostPackage, base_package: PostPackage) -> float:
        """Calculate savings percentage compared to base package"""
        if package == base_package:
            return 0.0
            
        package_config = self.packages[package]
        base_config = self.packages[base_package]
        
        # Calculate cost per post savings
        savings_per_post = base_config.cost_per_post - package_config.cost_per_post
        savings_percentage = (savings_per_post / base_config.cost_per_post) * 100
        
        return round(savings_percentage, 1)
    
    def get_recommended_package(self, posts_needed: int) -> PostPackage:
        """Recommend best package based on posts needed"""
        best_package = PostPackage.STARTER
        best_value = float('inf')
        
        for package in PostPackage:
            config = self.packages[package]
            if config.posts >= posts_needed:
                value_score = config.price_usd / config.posts
                if value_score < best_value:
                    best_value = value_score
                    best_package = package
        
        return best_package
    
    def validate_auto_schedule(self, posts: int, days: int) -> Tuple[bool, str]:
        """Validate auto-scheduling parameters"""
        if days <= 0:
            return False, "Days must be greater than 0"
        
        posts_per_day = posts / days
        if posts_per_day > self.max_posts_per_day:
            return False, f"Maximum {self.max_posts_per_day} posts per day allowed"
        
        return True, "Valid scheduling parameters"
    
    def calculate_optimal_schedule(self, posts: int, max_days: int = 30) -> List[Dict]:
        """Calculate optimal scheduling options"""
        options = []
        
        for days in range(1, min(max_days + 1, posts + 1)):
            posts_per_day = posts / days
            
            if posts_per_day <= self.max_posts_per_day:
                auto_cost = days * self.addons["auto_schedule_per_day"].price_usd
                
                options.append({
                    'days': days,
                    'posts_per_day': round(posts_per_day, 1),
                    'auto_schedule_cost': auto_cost,
                    'cost_per_post': auto_cost / posts if posts > 0 else 0
                })
        
        return options
    
    def format_package_display(self, package: PostPackage, language: str = 'en') -> str:
        """Format package for display"""
        info = self.get_package_info(package)
        
        if language == 'ar':
            return f"""📦 **{info['name']}**
📊 {info['posts']} منشور
💰 ${info['price_usd']:.2f} (${info['cost_per_post']:.2f}/منشور)
🎯 {info['target_users']}"""
        elif language == 'ru':
            return f"""📦 **{info['name']}**
📊 {info['posts']} постов
💰 ${info['price_usd']:.2f} (${info['cost_per_post']:.2f}/пост)
🎯 {info['target_users']}"""
        else:  # English
            return f"""📦 **{info['name']}**
📊 {info['posts']} posts
💰 ${info['price_usd']:.2f} (${info['cost_per_post']:.2f}/post)
🎯 {info['target_users']}"""

# Global instance
post_pricing_system = PostBasedPricingSystem()

def get_post_pricing_system() -> PostBasedPricingSystem:
    """Get the global post pricing system instance"""
    return post_pricing_system