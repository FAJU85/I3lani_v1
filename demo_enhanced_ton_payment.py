"""
Demo script showing the enhanced TON payment system with memo-based verification
Demonstrates the improved payment confirmation process
"""

import asyncio
import json
from datetime import datetime
from enhanced_ton_payment_system import get_enhanced_ton_payment_system
from languages import get_text

async def demonstrate_enhanced_payment_system():
    """Demonstrate the enhanced TON payment system"""
    print("🚀 Enhanced TON Payment System Demo")
    print("=" * 50)
    
    # Initialize the enhanced payment system
    bot_wallet = "UQBotWalletAddress123456789"
    payment_system = get_enhanced_ton_payment_system(bot_wallet)
    
    print(f"✅ Enhanced payment system initialized")
    print(f"📧 Bot wallet: {bot_wallet}")
    
    # Demo 1: Payment request creation
    print("\n📋 Demo 1: Enhanced Payment Request Creation")
    print("-" * 40)
    
    payment_request = await payment_system.create_payment_request(
        user_id=123456,
        amount_ton=2.5,
        user_wallet="EQUserWallet987654321",
        campaign_details={
            'days': 14,
            'posts_per_day': 3,
            'total_posts': 42,
            'selected_channels': ['@channel1', '@channel2', '@channel3'],
            'total_usd': 75.0
        }
    )
    
    print(f"💰 Payment ID: {payment_request['payment_id']}")
    print(f"🎯 Memo: {payment_request['memo']}")
    print(f"💎 Amount: {payment_request['amount_ton']} TON")
    print(f"📅 Expires: {payment_request['expires_at']}")
    print(f"🎨 Campaign: {payment_request['campaign_details']['days']} days, {payment_request['campaign_details']['posts_per_day']} posts/day")
    
    # Demo 2: Multilingual payment instructions
    print("\n🌍 Demo 2: Multilingual Payment Instructions")
    print("-" * 40)
    
    memo = payment_request['memo']
    amount = payment_request['amount_ton']
    
    # English instructions
    print("\n🇺🇸 English Instructions:")
    print(f"""
💎 TON Payment - Enhanced Memo Verification

Required Amount: {amount} TON
Wallet Address: {bot_wallet}
Memo/Note: `{memo}`

Enhanced Payment Steps:
1. Open your TON wallet
2. Send {amount} TON to the address above
3. CRITICAL: Add memo/note `{memo}` exactly as written
4. Complete the payment

⏰ Enhanced monitoring for 20 minutes with memo priority
🔍 Automatic confirmation when memo `{memo}` matches
🎯 More reliable payment verification system
""")
    
    # Arabic instructions
    print("\n🇸🇦 Arabic Instructions:")
    print(f"""
💎 دفع TON - نظام التحقق المحسن بالمذكرة

المبلغ المطلوب: {amount} TON
عنوان المحفظة: {bot_wallet}
المذكرة/الملاحظة: `{memo}`

خطوات الدفع المحسنة:
1. افتح محفظة TON الخاصة بك
2. أرسل {amount} TON إلى العنوان أعلاه
3. مهم جداً: أضف المذكرة/الملاحظة `{memo}` بالضبط كما هو مكتوب
4. أكمل الدفع

⏰ مراقبة محسنة لمدة 20 دقيقة مع أولوية المذكرة
🔍 تأكيد تلقائي عند مطابقة المذكرة `{memo}`
🎯 نظام تحقق أكثر موثوقية للدفع
""")
    
    # Russian instructions
    print("\n🇷🇺 Russian Instructions:")
    print(f"""
💎 Оплата TON - Улучшенная проверка по заметке

Требуемая сумма: {amount} TON
Адрес кошелька: {bot_wallet}
Заметка/Memo: `{memo}`

Улучшенные шаги оплаты:
1. Откройте свой TON кошелек
2. Отправьте {amount} TON на адрес выше
3. КРИТИЧЕСКИ ВАЖНО: Добавьте заметку/memo `{memo}` точно как написано
4. Завершите платеж

⏰ Улучшенный мониторинг 20 минут с приоритетом заметки
🔍 Автоматическое подтверждение при совпадении заметки `{memo}`
🎯 Более надежная система проверки платежей
""")
    
    # Demo 3: Memo matching demonstration
    print("\n🎯 Demo 3: Memo Matching Demonstration")
    print("-" * 40)
    
    test_memos = [
        memo,                    # Exact match
        memo.lower(),           # Case insensitive
        f" {memo} ",           # Whitespace tolerance
        f"{memo[:2]} {memo[2:]}",  # Internal whitespace
        "WRONG123",             # Wrong memo
        ""                      # Empty memo
    ]
    
    print(f"Expected memo: {memo}")
    print("Testing various memo formats:")
    
    for i, test_memo in enumerate(test_memos, 1):
        match_result = payment_system._is_memo_match(test_memo, memo)
        status = "✅ MATCH" if match_result else "❌ NO MATCH"
        print(f"  {i}. '{test_memo}' -> {status}")
    
    # Demo 4: Amount matching demonstration
    print("\n💰 Demo 4: Amount Matching Demonstration")
    print("-" * 40)
    
    test_amounts = [
        amount,          # Exact match
        amount + 0.001,  # Slight overpayment
        amount - 0.001,  # Slight underpayment
        amount + 0.02,   # Significant overpayment
        amount - 0.02,   # Significant underpayment
        0.0              # Zero amount
    ]
    
    print(f"Expected amount: {amount} TON")
    print("Testing various payment amounts:")
    
    for i, test_amount in enumerate(test_amounts, 1):
        match_result = payment_system._is_amount_match(test_amount, amount)
        status = "✅ MATCH" if match_result else "❌ NO MATCH"
        difference = test_amount - amount
        print(f"  {i}. {test_amount} TON (diff: {difference:+.3f}) -> {status}")
    
    # Demo 5: Wallet normalization demonstration
    print("\n🏦 Demo 5: Wallet Address Normalization")
    print("-" * 40)
    
    test_wallets = [
        "EQTestWallet123456789",
        "UQTestWallet123456789",
        "TestWallet123456789",
        ""
    ]
    
    print("Testing wallet address normalization:")
    
    for i, test_wallet in enumerate(test_wallets, 1):
        normalized = payment_system._normalize_wallet_address(test_wallet)
        print(f"  {i}. '{test_wallet}' -> '{normalized}'")
    
    # Demo 6: System status
    print("\n📊 Demo 6: System Status")
    print("-" * 40)
    
    active_count = payment_system.get_active_monitors_count()
    print(f"Active payment monitors: {active_count}")
    
    # Demo payment status
    status = await payment_system.get_payment_status("demo_payment_123")
    print(f"Demo payment status: {json.dumps(status, indent=2)}")
    
    # Summary
    print("\n🎉 Demo Complete!")
    print("=" * 50)
    print("✅ Enhanced TON Payment System Features:")
    print("   🎯 Memo-based verification (primary)")
    print("   💰 Amount matching with tolerance")
    print("   🏦 Wallet address normalization")
    print("   🌍 Multilingual support (EN/AR/RU)")
    print("   ⏰ 20-minute payment monitoring")
    print("   🔍 Automatic payment confirmation")
    print("   📊 Real-time monitoring status")
    print("   🔒 Enhanced security and reliability")
    print("")
    print("🚀 System is ready for production deployment!")

if __name__ == "__main__":
    asyncio.run(demonstrate_enhanced_payment_system())