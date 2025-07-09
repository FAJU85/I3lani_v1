#!/usr/bin/env python3
"""
Smart & Scalable Ad Pricing System Demo
Demonstrates the complete smart pricing system functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frequency_pricing import FrequencyPricingSystem
from smart_pricing_display import smart_pricing_display

def demo_smart_pricing_system():
    """Demonstrate the smart pricing system capabilities"""
    
    print("🧠 Smart & Scalable Ad Pricing System Demo")
    print("=" * 60)
    
    pricing_system = FrequencyPricingSystem()
    
    # Demo 1: Show the complete pricing table
    print("\n1. 📊 Complete Pricing Table:")
    print("-" * 40)
    table = smart_pricing_display.generate_pricing_table_message('en')
    print(table)
    
    # Demo 2: Show pricing for different scenarios
    print("\n2. 💰 Real-World Pricing Scenarios:")
    print("-" * 40)
    
    scenarios = [
        {"name": "Quick Campaign", "days": 1, "description": "Single day flash sale"},
        {"name": "Weekly Campaign", "days": 7, "description": "Product launch campaign"},
        {"name": "Monthly Campaign", "days": 30, "description": "Brand awareness drive"},
        {"name": "Bulk Campaign", "days": 90, "description": "Long-term brand building"}
    ]
    
    for scenario in scenarios:
        pricing = pricing_system.calculate_pricing(scenario["days"])
        print(f"\n🎯 {scenario['name']} ({scenario['description']}):")
        print(f"   📅 Duration: {pricing['days']} days")
        print(f"   📝 Posts per day: {pricing['posts_per_day']}")
        print(f"   💰 Discount: {pricing['discount_percent']}%")
        print(f"   💵 Final Price: ${pricing['final_cost_usd']:.2f}")
        print(f"   💎 TON: {pricing['cost_ton']:.2f}")
        print(f"   🌟 Stars: {pricing['cost_stars']:,}")
    
    # Demo 3: Show multi-language support
    print("\n3. 🌍 Multi-Language Support:")
    print("-" * 40)
    
    languages = [
        {"code": "en", "name": "English"},
        {"code": "ar", "name": "Arabic"},
        {"code": "ru", "name": "Russian"}
    ]
    
    for lang in languages:
        preview = smart_pricing_display.generate_quick_pricing_preview(7, lang["code"])
        print(f"\n🗣️ {lang['name']} ({lang['code']}):")
        print(preview[:200] + "..." if len(preview) > 200 else preview)
    
    # Demo 4: Show bulk buyer information
    print("\n4. 🚀 Bulk Buyer Extended Tiers:")
    print("-" * 40)
    bulk_info = smart_pricing_display.generate_bulk_buyer_info('en')
    print(bulk_info)
    
    # Demo 5: Show tier recommendations
    print("\n5. 💡 Smart Recommendations:")
    print("-" * 40)
    recommendations = pricing_system.get_recommendations(1)
    
    for rec_type, rec_data in recommendations.items():
        if rec_data:
            print(f"\n🎯 {rec_type.replace('_', ' ').title()}:")
            print(f"   📅 {rec_data['days']} days")
            print(f"   💰 {rec_data['discount_percent']}% discount")
            print(f"   💵 ${rec_data['final_cost_usd']:.2f}")
    
    # Demo 6: Show comparison between options
    print("\n6. 🔄 Pricing Comparison:")
    print("-" * 40)
    comparison = smart_pricing_display.generate_comparison_message([1, 7, 30, 90], 'en')
    print(comparison)
    
    # Demo 7: Show value calculation
    print("\n7. 📈 Value Analysis:")
    print("-" * 40)
    
    value_analysis = []
    for days in [1, 7, 30, 90]:
        pricing = pricing_system.calculate_pricing(days)
        cost_per_post = pricing['final_cost_usd'] / pricing['total_posts']
        value_analysis.append({
            'days': days,
            'cost_per_post': cost_per_post,
            'total_posts': pricing['total_posts'],
            'discount': pricing['discount_percent']
        })
    
    print("Cost per post analysis:")
    for analysis in value_analysis:
        print(f"   📅 {analysis['days']} days: ${analysis['cost_per_post']:.2f}/post ({analysis['total_posts']} posts, {analysis['discount']}% discount)")
    
    # Demo 8: Show system features
    print("\n8. ⚙️ System Features:")
    print("-" * 40)
    print("✅ Dynamic pricing based on duration")
    print("✅ Automatic discount calculation")
    print("✅ Multi-currency support (USD, TON, Stars)")
    print("✅ Bulk buyer extended tiers")
    print("✅ Real-time price previews")
    print("✅ Automated calculation flow")
    print("✅ Multi-language interface")
    print("✅ Smart recommendations")
    print("✅ Tier comparisons")
    print("✅ Error handling and validation")
    
    print("\n" + "=" * 60)
    print("🎉 Smart Pricing System Demo Complete!")
    print("=" * 60)
    print("The system is ready for production deployment with:")
    print("- 11 pricing tiers (1-90 days)")
    print("- Automatic scaling (more days = more posts + bigger discounts)")
    print("- Multi-currency support")
    print("- Complete multi-language interface")
    print("- Comprehensive admin management")
    print("- Real-time pricing calculations")
    print("\nUsers can now select days and get automatic pricing!")

if __name__ == "__main__":
    demo_smart_pricing_system()