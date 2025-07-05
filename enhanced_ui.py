"""
Enhanced UI Components for Multi-Channel Selection and Pricing
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import SessionLocal, Channel, Bundle
from payment_system import payment_system
from typing import List, Dict, Optional
import json

class EnhancedUI:
    
    @staticmethod
    def get_channel_selection_keyboard(selected_channels: List[str] = None) -> InlineKeyboardMarkup:
        """Create multi-select keyboard for channels"""
        if selected_channels is None:
            selected_channels = []
        
        db = SessionLocal()
        try:
            channels = db.query(Channel).filter(Channel.is_active == True).all()
            
            keyboard = InlineKeyboardMarkup(row_width=1)
            
            # Channel selection buttons
            for channel in channels:
                is_selected = channel.id in selected_channels
                checkbox = "☑️" if is_selected else "☐"
                
                button_text = f"{checkbox} {channel.name} ({channel.price_per_month:.3f} TON/month)"
                callback_data = f"toggle_channel_{channel.id}"
                
                keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))
            
            # Control buttons
            if selected_channels:
                keyboard.add(
                    InlineKeyboardButton("📊 View Pricing", callback_data="view_pricing"),
                    InlineKeyboardButton("✅ Continue", callback_data="continue_selection")
                )
            
            keyboard.add(
                InlineKeyboardButton("🔄 Reset Selection", callback_data="reset_channels"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_selection")
            )
            
            return keyboard
            
        finally:
            db.close()
    
    @staticmethod
    def get_duration_selection_keyboard(selected_channels: List[str]) -> InlineKeyboardMarkup:
        """Create duration selection keyboard with bundle options"""
        db = SessionLocal()
        try:
            bundles = db.query(Bundle).filter(Bundle.is_active == True).all()
            
            keyboard = InlineKeyboardMarkup(row_width=2)
            
            # Regular duration options
            keyboard.add(
                InlineKeyboardButton("1 Month", callback_data=f"duration_1_{json.dumps(selected_channels)}"),
                InlineKeyboardButton("3 Months", callback_data=f"duration_3_{json.dumps(selected_channels)}")
            )
            keyboard.add(
                InlineKeyboardButton("6 Months", callback_data=f"duration_6_{json.dumps(selected_channels)}"),
                InlineKeyboardButton("12 Months", callback_data=f"duration_12_{json.dumps(selected_channels)}")
            )
            
            # Bundle options
            if bundles:
                keyboard.add(InlineKeyboardButton("🎁 Special Bundles", callback_data="separator"))
                
                for bundle in bundles:
                    bundle_text = f"🎁 {bundle.name}"
                    if bundle.bonus_months > 0:
                        bundle_text += f" (+{bundle.bonus_months} free)"
                    if bundle.discount_percent > 0:
                        bundle_text += f" (-{bundle.discount_percent}%)"
                    
                    callback_data = f"bundle_{bundle.id}_{json.dumps(selected_channels)}"
                    keyboard.add(InlineKeyboardButton(bundle_text, callback_data=callback_data))
            
            keyboard.add(InlineKeyboardButton("🔙 Back to Channels", callback_data="back_to_channels"))
            
            return keyboard
            
        finally:
            db.close()
    
    @staticmethod
    async def get_pricing_text(channel_ids: List[str], months: int, bundle_id: Optional[str] = None) -> str:
        """Generate pricing display text with currency conversion"""
        pricing = await payment_system.get_pricing_display(channel_ids, months, bundle_id)
        
        db = SessionLocal()
        try:
            channels = db.query(Channel).filter(Channel.id.in_(channel_ids)).all()
            channel_names = [c.name for c in channels]
            
            text = "💰 **Pricing Summary**\n\n"
            
            # Selected channels
            text += f"📺 **Selected Channels ({len(channel_names)}):**\n"
            for name in channel_names:
                text += f"   • {name}\n"
            text += "\n"
            
            # Duration
            total_months = months + pricing['bonus_months']
            text += f"📅 **Duration:** {months} months"
            if pricing['bonus_months'] > 0:
                text += f" + {pricing['bonus_months']} bonus months = {total_months} total"
            text += "\n\n"
            
            # Pricing breakdown
            text += f"💰 **Pricing:**\n"
            text += f"Base Price: {pricing['base_price_ton']:.3f} TON\n"
            
            if pricing['discount_percent'] > 0:
                text += f"Discount ({pricing['discount_percent']}%): -{pricing['savings_ton']:.3f} TON\n"
                text += f"**Final Price: {pricing['final_price_ton']:.3f} TON**\n\n"
            else:
                text += f"**Total: {pricing['final_price_ton']:.3f} TON**\n\n"
            
            # Currency conversions
            text += "🌍 **Price in Other Currencies:**\n"
            text += f"💵 USD: ~${pricing['final_price_usd']:.2f}\n"
            text += f"🇸🇦 SAR: ~{pricing['final_price_sar']:.2f} ريال\n"
            text += f"🇷🇺 RUB: ~{pricing['final_price_rub']:.0f} ₽\n\n"
            
            # Cost per channel breakdown
            cost_per_channel_per_month = pricing['final_price_ton'] / (len(channel_names) * months)
            text += f"📊 **Cost per Channel:** {cost_per_channel_per_month:.3f} TON/month\n"
            
            if pricing['savings_ton'] > 0:
                text += f"💡 **You Save:** {pricing['savings_ton']:.3f} TON with this bundle!\n"
            
            return text
            
        finally:
            db.close()
    
    @staticmethod
    def get_payment_confirmation_keyboard(order_data: Dict) -> InlineKeyboardMarkup:
        """Create payment confirmation keyboard"""
        keyboard = InlineKeyboardMarkup(row_width=1)
        
        keyboard.add(
            InlineKeyboardButton("💳 Pay with TON", callback_data=f"pay_order_{order_data['order_id']}")
        )
        keyboard.add(
            InlineKeyboardButton("📊 View Details", callback_data=f"view_order_{order_data['order_id']}"),
            InlineKeyboardButton("✏️ Modify Order", callback_data="modify_order")
        )
        keyboard.add(
            InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_order_{order_data['order_id']}")
        )
        
        return keyboard
    
    @staticmethod
    def get_payment_instructions_keyboard(memo: str, order_id: str) -> InlineKeyboardMarkup:
        """Create payment instructions keyboard"""
        keyboard = InlineKeyboardMarkup(row_width=1)
        
        keyboard.add(
            InlineKeyboardButton("✅ I've Sent Payment", callback_data=f"payment_sent_{order_id}")
        )
        keyboard.add(
            InlineKeyboardButton("📋 Copy Memo", callback_data=f"copy_memo_{memo}"),
            InlineKeyboardButton("💳 Copy Wallet", callback_data="copy_wallet")
        )
        keyboard.add(
            InlineKeyboardButton("❓ Payment Help", callback_data="payment_help"),
            InlineKeyboardButton("❌ Cancel Payment", callback_data=f"cancel_payment_{order_id}")
        )
        
        return keyboard
    
    @staticmethod
    def get_payment_instructions_text(order_data: Dict) -> str:
        """Generate payment instructions text"""
        expires_in = int((order_data['expires_at'] - order_data.get('created_at', order_data['expires_at'])).total_seconds() / 60)
        
        text = f"""
🚀 **Ready to Launch Your Campaign!**

📦 **Order Summary:**
• {order_data['channels_count']} channel(s) × {order_data['duration_months']} months
• Total posts: ~{order_data['duration_months'] * 30 * order_data['channels_count']}

💰 **Payment Details:**
**Amount:** `{order_data['amount_ton']:.3f} TON`
**Wallet:** `{order_data['wallet_address']}`
**Memo:** `{order_data['memo']}`

⚠️ **IMPORTANT:**
1. Send EXACTLY {order_data['amount_ton']:.3f} TON
2. Include memo: `{order_data['memo']}`
3. Payment expires in {expires_in} minutes

🔄 **Payment will be detected automatically**

💡 **How to pay:**
1. Open your TON wallet app
2. Send {order_data['amount_ton']:.3f} TON to the wallet address
3. Add `{order_data['memo']}` in the memo/comment field
4. Confirm the transaction
5. Click "I've Sent Payment" below

Your campaign will start automatically once payment is confirmed!
"""
        return text

class UserFlowStates:
    """Enhanced state management for multi-step user flow"""
    
    def __init__(self):
        self.user_data = {}
    
    def set_selected_channels(self, user_id: int, channel_ids: List[str]):
        """Set selected channels for user"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        self.user_data[user_id]['selected_channels'] = channel_ids
    
    def get_selected_channels(self, user_id: int) -> List[str]:
        """Get selected channels for user"""
        return self.user_data.get(user_id, {}).get('selected_channels', [])
    
    def toggle_channel(self, user_id: int, channel_id: str) -> List[str]:
        """Toggle channel selection for user"""
        selected = self.get_selected_channels(user_id)
        if channel_id in selected:
            selected.remove(channel_id)
        else:
            selected.append(channel_id)
        
        self.set_selected_channels(user_id, selected)
        return selected
    
    def clear_user_data(self, user_id: int):
        """Clear user data"""
        if user_id in self.user_data:
            del self.user_data[user_id]

# Global instance
user_flow = UserFlowStates()