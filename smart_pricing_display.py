"""
Smart & Scalable Ad Pricing Display System
Beautiful pricing table interface for I3lani Bot
"""

from typing import Dict, List
from frequency_pricing import FrequencyPricingSystem
from languages import get_text

class SmartPricingDisplay:
    """Displays beautiful pricing tables with smart scaling logic"""
    
    def __init__(self):
        self.pricing_system = FrequencyPricingSystem()
        
    def generate_pricing_table_message(self, language: str = 'en') -> str:
        """Generate beautiful pricing table message"""
        
        # Core pricing data
        core_tiers = [1, 3, 5, 7, 10, 15, 20, 30]
        
        if language == 'ar':
            header = """
🧠 **نظام التسعير الذكي والقابل للتوسع**

## 💡 كيف يعمل النظام
- ✅ **المزيد من الأيام = المزيد من المنشورات يومياً**
- ✅ **المزيد من الأيام = خصم أكبر**
- ✅ **تسعير تلقائي بالدولار والتون وستارز تليجرام**

## 📊 جدول التسعير الديناميكي
```
الأيام | منشورات/يوم | خصم   | سعر يومي | المجموع  | السعر النهائي
----|----------|------|--------|--------|----------"""
            
            rows = []
            for days in core_tiers:
                pricing = self.pricing_system.calculate_pricing(days)
                rows.append(f"{days:>3} | {pricing['posts_per_day']:>8} | {pricing['discount_percent']:>3}% | ${pricing['daily_price']:>5.2f} | ${pricing['base_cost_usd']:>6.2f} | ${pricing['final_cost_usd']:>7.2f}")
            
            footer = """```

🔄 **تدفق الحساب الآلي:**
1. المستخدم يختار عدد أيام الإعلان
2. البوت يحسب تلقائياً: المنشورات/اليوم + الخصم + التحويل للعملات
3. عرض الأسعار بـ: 💵 دولار | 💎 تون | 🌟 ستارز

**جاهز للنشر كمنطق التسعير الافتراضي!**
            """
            
        elif language == 'ru':
            header = """
🧠 **Умная и масштабируемая система ценообразования**

## 💡 Как это работает
- ✅ **Больше дней = больше постов в день**
- ✅ **Больше дней = больше скидка**
- ✅ **Автоматическое ценообразование в USD, TON и Telegram Stars**

## 📊 Динамическая таблица цен
```
Дни | Посты/день | Скидка | Дневная ставка | Сумма  | Итоговая цена
----|-----------|--------|---------------|--------|-------------"""
            
            rows = []
            for days in core_tiers:
                pricing = self.pricing_system.calculate_pricing(days)
                rows.append(f"{days:>3} | {pricing['posts_per_day']:>9} | {pricing['discount_percent']:>5}% | ${pricing['daily_price']:>12.2f} | ${pricing['base_cost_usd']:>5.2f} | ${pricing['final_cost_usd']:>11.2f}")
            
            footer = """```

🔄 **Поток автоматических расчетов:**
1. Пользователь выбирает количество дней рекламы
2. Бот автоматически рассчитывает: посты/день + скидку + конвертацию валют
3. Отображение цен в: 💵 USD | 💎 TON | 🌟 Stars

**Готово к развертыванию как логика ценообразования по умолчанию!**
            """
            
        else:  # English
            header = """
🧠 **Smart & Scalable Ad Pricing System**

## 💡 How It Works
- ✅ **More Days = More Posts Per Day**
- ✅ **More Days = Bigger Discount**
- ✅ **Auto Pricing in USD, TON, and Telegram Stars**

## 📊 Dynamic Pricing Table
```
Days | Posts/Day | Discount | Daily Rate | Subtotal | Final Price
-----|-----------|----------|------------|----------|------------"""
            
            rows = []
            for days in core_tiers:
                pricing = self.pricing_system.calculate_pricing(days)
                rows.append(f"{days:>4} | {pricing['posts_per_day']:>9} | {pricing['discount_percent']:>7}% | ${pricing['daily_price']:>9.2f} | ${pricing['base_cost_usd']:>7.2f} | ${pricing['final_cost_usd']:>10.2f}")
            
            footer = """```

🔄 **Automated Calculation Flow:**
1. User selects number of ad days
2. Bot automatically calculates: posts/day + discount + currency conversion
3. Display prices in: 💵 USD | 💎 TON | 🌟 Stars

**Ready for deployment as default pricing logic!**
            """
        
        return header + "\n" + "\n".join(rows) + "\n" + footer
    
    def generate_quick_pricing_preview(self, days: int, language: str = 'en') -> str:
        """Generate quick pricing preview for specific days"""
        
        pricing = self.pricing_system.calculate_pricing(days)
        
        if language == 'ar':
            return f"""
💰 **معاينة سريعة للتسعير - {days} يوم**

📅 المدة: {days} يوم
📈 منشورات يومياً: {pricing['posts_per_day']}
🔽 خصم: {pricing['discount_percent']}%
💵 السعر النهائي: ${pricing['final_cost_usd']:.2f}

💎 بالتون: {pricing['cost_ton']:.2f} TON
🌟 بالستارز: {pricing['cost_stars']:,} Stars
            """
        elif language == 'ru':
            return f"""
💰 **Быстрый просмотр цен - {days} дней**

📅 Продолжительность: {days} дней
📈 Постов в день: {pricing['posts_per_day']}
🔽 Скидка: {pricing['discount_percent']}%
💵 Итоговая цена: ${pricing['final_cost_usd']:.2f}

💎 В TON: {pricing['cost_ton']:.2f} TON
🌟 В Stars: {pricing['cost_stars']:,} Stars
            """
        else:  # English
            return f"""
💰 **Quick Pricing Preview - {days} Days**

📅 Duration: {days} days
📈 Posts per day: {pricing['posts_per_day']}
🔽 Discount: {pricing['discount_percent']}%
💵 Final Price: ${pricing['final_cost_usd']:.2f}

💎 In TON: {pricing['cost_ton']:.2f} TON
🌟 In Stars: {pricing['cost_stars']:,} Stars
            """
    
    def generate_bulk_buyer_info(self, language: str = 'en') -> str:
        """Generate info about extended tiers for bulk buyers"""
        
        extended_tiers = [45, 60, 90]
        
        if language == 'ar':
            header = """
🚀 **طبقات موسعة للمشترين بالجملة**

للحملات الكبيرة وحملات العلامات التجارية:
            """
            
            rows = []
            for days in extended_tiers:
                pricing = self.pricing_system.calculate_pricing(days)
                rows.append(f"📅 {days} يوم: {pricing['posts_per_day']} منشور/يوم، خصم {pricing['discount_percent']}%، ${pricing['final_cost_usd']:.2f}")
            
        elif language == 'ru':
            header = """
🚀 **Расширенные уровни для крупных покупателей**

Для крупных кампаний и брендинга:
            """
            
            rows = []
            for days in extended_tiers:
                pricing = self.pricing_system.calculate_pricing(days)
                rows.append(f"📅 {days} дней: {pricing['posts_per_day']} постов/день, скидка {pricing['discount_percent']}%, ${pricing['final_cost_usd']:.2f}")
            
        else:  # English
            header = """
🚀 **Extended Tiers for Bulk Buyers**

For large campaigns and brand advertising:
            """
            
            rows = []
            for days in extended_tiers:
                pricing = self.pricing_system.calculate_pricing(days)
                rows.append(f"📅 {days} days: {pricing['posts_per_day']} posts/day, {pricing['discount_percent']}% discount, ${pricing['final_cost_usd']:.2f}")
        
        return header + "\n" + "\n".join(rows)
    
    def generate_comparison_message(self, days_list: List[int], language: str = 'en') -> str:
        """Generate comparison message between different day options"""
        
        if language == 'ar':
            header = "📊 **مقارنة خيارات التسعير**\n\n"
            
        elif language == 'ru':
            header = "📊 **Сравнение вариантов ценообразования**\n\n"
            
        else:  # English
            header = "📊 **Pricing Options Comparison**\n\n"
        
        comparisons = []
        for days in days_list:
            pricing = self.pricing_system.calculate_pricing(days)
            tier = self.pricing_system.get_tier_for_days(days)
            
            if language == 'ar':
                comparison = f"""
🔹 **{days} يوم - {tier['name']}**
   📈 {pricing['posts_per_day']} منشور/يوم
   💰 خصم {pricing['discount_percent']}%
   💵 ${pricing['final_cost_usd']:.2f}
   💎 {pricing['cost_ton']:.2f} TON
   🌟 {pricing['cost_stars']:,} Stars
                """
            elif language == 'ru':
                comparison = f"""
🔹 **{days} дней - {tier['name']}**
   📈 {pricing['posts_per_day']} постов/день
   💰 Скидка {pricing['discount_percent']}%
   💵 ${pricing['final_cost_usd']:.2f}
   💎 {pricing['cost_ton']:.2f} TON
   🌟 {pricing['cost_stars']:,} Stars
                """
            else:  # English
                comparison = f"""
🔹 **{days} Days - {tier['name']}**
   📈 {pricing['posts_per_day']} posts/day
   💰 {pricing['discount_percent']}% discount
   💵 ${pricing['final_cost_usd']:.2f}
   💎 {pricing['cost_ton']:.2f} TON
   🌟 {pricing['cost_stars']:,} Stars
                """
            
            comparisons.append(comparison)
        
        return header + "\n".join(comparisons)

# Global instance
smart_pricing_display = SmartPricingDisplay()