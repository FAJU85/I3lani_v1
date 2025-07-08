"""
Enhanced UI Components for I3lani Bot
Provides modern, visually appealing UI elements
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Optional, Tuple
import asyncio
from datetime import datetime

class UIComponents:
    """Enhanced UI components with modern design"""
    
    # Visual elements and symbols
    ICONS = {
        # Navigation
        'back': '◀️',
        'forward': '▶️',
        'home': '🏠',
        'menu': '☰',
        
        # Actions
        'create': '➕',
        'edit': '✏️',
        'delete': '🗑',
        'refresh': '🔄',
        'search': '🔍',
        'settings': '⚙️',
        
        # Status
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'loading': '⏳',
        'done': '✓',
        'pending': '○',
        'active': '●',
        
        # Features
        'ad': '📢',
        'channel': '📡',
        'payment': '💳',
        'stats': '📊',
        'help': '❓',
        'language': '🌐',
        'referral': '👥',
        'premium': '⭐',
        
        # Currencies
        'ton': '💎',
        'stars': '⭐',
        'usd': '💵',
        
        # Visual separators
        'dot': '•',
        'arrow': '→',
        'check': '✓',
        'cross': '✗',
        'bullet': '▸',
    }
    
    # Modern color-coded prefixes (using markdown)
    PREFIXES = {
        'success': '[✓]',
        'error': '[✗]',
        'info': '[i]',
        'warning': '[!]',
        'question': '[?]',
        'star': '[★]',
        'diamond': '[◆]',
    }
    
    @staticmethod
    def create_header(title: str, subtitle: Optional[str] = None, icon: Optional[str] = None) -> str:
        """Create a visually appealing header"""
        lines = []
        
        # Add decorative line
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Add title with icon
        if icon:
            lines.append(f"{icon} **{title}** {icon}")
        else:
            lines.append(f"**{title}**")
        
        # Add subtitle if provided
        if subtitle:
            lines.append(f"_{subtitle}_")
        
        # Add decorative line
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        return "\n".join(lines)
    
    @staticmethod
    def create_section(title: str, content: str, icon: Optional[str] = None) -> str:
        """Create a formatted section"""
        section_icon = icon or UIComponents.ICONS['bullet']
        return f"\n{section_icon} **{title}**\n{content}"
    
    @staticmethod
    def create_list_item(text: str, icon: Optional[str] = None, indent: int = 0) -> str:
        """Create a formatted list item"""
        item_icon = icon or UIComponents.ICONS['dot']
        indent_str = "  " * indent
        return f"{indent_str}{item_icon} {text}"
    
    @staticmethod
    def create_info_box(title: str, content: str, style: str = 'info') -> str:
        """Create an information box with style"""
        prefix = UIComponents.PREFIXES.get(style, '[i]')
        border = "┌" + "─" * 24 + "┐"
        
        lines = [
            border,
            f"│ {prefix} {title}",
            "├" + "─" * 24 + "┤"
        ]
        
        # Split content into lines and format
        for line in content.split('\n'):
            if line.strip():
                lines.append(f"│ {line.strip()}")
        
        lines.append("└" + "─" * 24 + "┘")
        
        return "\n".join(lines)
    
    @staticmethod
    def create_stats_display(stats: Dict[str, any]) -> str:
        """Create a formatted stats display"""
        lines = []
        
        for key, value in stats.items():
            # Format the key
            formatted_key = key.replace('_', ' ').title()
            
            # Format the value based on type
            if isinstance(value, (int, float)):
                if value >= 1000000:
                    formatted_value = f"{value/1000000:.1f}M"
                elif value >= 1000:
                    formatted_value = f"{value/1000:.1f}K"
                else:
                    formatted_value = str(value)
            else:
                formatted_value = str(value)
            
            lines.append(f"{UIComponents.ICONS['bullet']} {formatted_key}: **{formatted_value}**")
        
        return "\n".join(lines)
    
    @staticmethod
    def create_progress_bar(current: int, total: int, width: int = 10) -> str:
        """Create a visual progress bar"""
        if total == 0:
            percentage = 0
        else:
            percentage = min(100, int((current / total) * 100))
        
        filled = int((percentage / 100) * width)
        empty = width - filled
        
        bar = "█" * filled + "░" * empty
        
        return f"[{bar}] {percentage}%"
    
    @staticmethod
    def create_button(text: str, icon: Optional[str] = None, style: str = 'default') -> str:
        """Create formatted button text"""
        if icon:
            return f"{icon} {text}"
        
        # Add default icons based on style
        style_icons = {
            'primary': UIComponents.ICONS['forward'],
            'success': UIComponents.ICONS['success'],
            'danger': UIComponents.ICONS['error'],
            'back': UIComponents.ICONS['back'],
            'info': UIComponents.ICONS['info'],
        }
        
        if style in style_icons:
            return f"{style_icons[style]} {text}"
        
        return text
    
    @staticmethod
    def create_navigation_keyboard(
        current_page: str,
        back_callback: Optional[str] = None,
        home_callback: Optional[str] = "back_to_main",
        extra_buttons: Optional[List[Dict]] = None
    ) -> InlineKeyboardMarkup:
        """Create a standardized navigation keyboard"""
        keyboard = []
        
        # Add extra buttons if provided
        if extra_buttons:
            for button_row in extra_buttons:
                if isinstance(button_row, list):
                    row = []
                    for btn in button_row:
                        row.append(InlineKeyboardButton(
                            text=UIComponents.create_button(btn['text'], btn.get('icon')),
                            callback_data=btn['callback_data']
                        ))
                    keyboard.append(row)
                else:
                    keyboard.append([InlineKeyboardButton(
                        text=UIComponents.create_button(button_row['text'], button_row.get('icon')),
                        callback_data=button_row['callback_data']
                    )])
        
        # Add navigation row
        nav_row = []
        if back_callback:
            nav_row.append(InlineKeyboardButton(
                text=UIComponents.create_button("Back", style='back'),
                callback_data=back_callback
            ))
        
        nav_row.append(InlineKeyboardButton(
            text=UIComponents.create_button("Home", icon=UIComponents.ICONS['home']),
            callback_data=home_callback
        ))
        
        if nav_row:
            keyboard.append(nav_row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_selection_keyboard(
        items: List[Dict[str, any]],
        selected_ids: List[str],
        select_callback_prefix: str,
        columns: int = 2,
        show_all_button: bool = True,
        back_callback: Optional[str] = None
    ) -> InlineKeyboardMarkup:
        """Create a selection keyboard with visual indicators"""
        keyboard = []
        
        # Create item buttons
        row = []
        for i, item in enumerate(items):
            item_id = str(item.get('id', i))
            is_selected = item_id in selected_ids
            
            # Create visual indicator
            indicator = UIComponents.ICONS['active'] if is_selected else UIComponents.ICONS['pending']
            
            # Create button text
            text = f"{indicator} {item.get('name', f'Item {i+1}')}"
            
            # Add to row
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=f"{select_callback_prefix}{item_id}"
            ))
            
            # Check if we need to start a new row
            if len(row) >= columns:
                keyboard.append(row)
                row = []
        
        # Add remaining buttons
        if row:
            keyboard.append(row)
        
        # Add control buttons
        control_row = []
        
        if show_all_button:
            if len(selected_ids) < len(items):
                control_row.append(InlineKeyboardButton(
                    text=UIComponents.create_button("Select All", UIComponents.ICONS['success']),
                    callback_data=f"{select_callback_prefix}all"
                ))
            else:
                control_row.append(InlineKeyboardButton(
                    text=UIComponents.create_button("Deselect All", UIComponents.ICONS['cross']),
                    callback_data=f"{select_callback_prefix}none"
                ))
        
        if control_row:
            keyboard.append(control_row)
        
        # Add navigation
        if back_callback:
            keyboard.append([InlineKeyboardButton(
                text=UIComponents.create_button("Back", style='back'),
                callback_data=back_callback
            )])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_confirmation_keyboard(
        confirm_callback: str,
        cancel_callback: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel"
    ) -> InlineKeyboardMarkup:
        """Create a confirmation keyboard"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=UIComponents.create_button(confirm_text, style='success'),
                    callback_data=confirm_callback
                ),
                InlineKeyboardButton(
                    text=UIComponents.create_button(cancel_text, style='danger'),
                    callback_data=cancel_callback
                )
            ]
        ])
    
    @staticmethod
    def format_price(amount: float, currency: str = 'USD') -> str:
        """Format price with currency symbol"""
        currency_symbols = {
            'USD': '$',
            'TON': UIComponents.ICONS['ton'],
            'STARS': UIComponents.ICONS['stars'],
        }
        
        symbol = currency_symbols.get(currency.upper(), currency)
        
        if currency.upper() == 'USD':
            return f"{symbol}{amount:,.2f}"
        elif currency.upper() == 'TON':
            return f"{amount:.2f} {symbol}"
        elif currency.upper() == 'STARS':
            return f"{int(amount)} {symbol}"
        else:
            return f"{amount} {currency}"
    
    @staticmethod
    def format_date(date: datetime, include_time: bool = False) -> str:
        """Format date in user-friendly way"""
        if include_time:
            return date.strftime("%d %B %Y at %H:%M")
        return date.strftime("%d %B %Y")
    
    @staticmethod
    def create_loading_message(text: str = "Processing") -> str:
        """Create a loading message"""
        return f"{UIComponents.ICONS['loading']} {text}..."
    
    @staticmethod
    def create_success_message(title: str, content: Optional[str] = None) -> str:
        """Create a success message"""
        icon = UIComponents.ICONS['success']
        
        if content:
            return f"{icon} **{title}**\n\n{content}"
        return f"{icon} **{title}**"
    
    @staticmethod
    def create_error_message(title: str, content: Optional[str] = None, suggestion: Optional[str] = None) -> str:
        """Create an error message with optional suggestion"""
        icon = UIComponents.ICONS['error']
        
        lines = [f"{icon} **{title}**"]
        
        if content:
            lines.append(f"\n{content}")
        
        if suggestion:
            lines.append(f"\n{UIComponents.ICONS['info']} **Suggestion:** {suggestion}")
        
        return "\n".join(lines)


# Animated elements for enhanced UX
class AnimatedUI:
    """Provides animated UI elements"""
    
    @staticmethod
    async def create_typing_effect(text: str, delay: float = 0.05) -> List[str]:
        """Create a typing effect animation frames"""
        frames = []
        for i in range(1, len(text) + 1):
            frames.append(text[:i] + "▋")
        frames.append(text)
        return frames
    
    @staticmethod
    def create_spinner_frames(text: str) -> List[str]:
        """Create spinner animation frames"""
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        return [f"{spinner} {text}" for spinner in spinners]
    
    @staticmethod
    def create_progress_frames(total: int, text: str = "Loading") -> List[str]:
        """Create progress animation frames"""
        frames = []
        for i in range(total + 1):
            bar = UIComponents.create_progress_bar(i, total)
            frames.append(f"{text}\n{bar}")
        return frames


# Quick access UI templates
class UITemplates:
    """Pre-built UI templates for common scenarios"""
    
    @staticmethod
    def welcome_message(username: str, language: str = 'en') -> str:
        """Create a welcome message"""
        icon = UIComponents.ICONS['star']
        
        welcome_texts = {
            'en': f"""
{UIComponents.create_header("Welcome to I3lani Bot", f"Hello, {username}!", icon)}

{UIComponents.create_section("What can I do?", 
f'''{UIComponents.create_list_item("Create and publish ads across multiple channels")}
{UIComponents.create_list_item("Pay with TON cryptocurrency or Telegram Stars")}
{UIComponents.create_list_item("Track your campaign performance")}
{UIComponents.create_list_item("Earn rewards through referrals")}''',
UIComponents.ICONS['info'])}

{UIComponents.create_section("Quick Start",
"Tap 'Create Ad' below to begin your first campaign!",
UIComponents.ICONS['forward'])}
""",
            'ar': f"""
{UIComponents.create_header("مرحباً بك في I3lani Bot", f"أهلاً، {username}!", icon)}

{UIComponents.create_section("ماذا يمكنني أن أفعل؟",
f'''{UIComponents.create_list_item("إنشاء ونشر الإعلانات عبر قنوات متعددة")}
{UIComponents.create_list_item("الدفع بعملة TON أو نجوم تيليجرام")}
{UIComponents.create_list_item("تتبع أداء حملتك")}
{UIComponents.create_list_item("اكسب مكافآت من خلال الإحالات")}''',
UIComponents.ICONS['info'])}

{UIComponents.create_section("البداية السريعة",
"اضغط على 'إنشاء إعلان' أدناه لبدء حملتك الأولى!",
UIComponents.ICONS['forward'])}
""",
            'ru': f"""
{UIComponents.create_header("Добро пожаловать в I3lani Bot", f"Привет, {username}!", icon)}

{UIComponents.create_section("Что я могу сделать?",
f'''{UIComponents.create_list_item("Создавать и публиковать объявления в нескольких каналах")}
{UIComponents.create_list_item("Оплачивать криптовалютой TON или звездами Telegram")}
{UIComponents.create_list_item("Отслеживать эффективность кампании")}
{UIComponents.create_list_item("Зарабатывать награды за рефералов")}''',
UIComponents.ICONS['info'])}

{UIComponents.create_section("Быстрый старт",
"Нажмите 'Создать объявление' ниже, чтобы начать свою первую кампанию!",
UIComponents.ICONS['forward'])}
"""
        }
        
        return welcome_texts.get(language, welcome_texts['en']).strip()
    
    @staticmethod
    def payment_summary(payment_data: Dict, language: str = 'en') -> str:
        """Create a payment summary"""
        # Extract data
        total_usd = payment_data.get('total_usd', 0)
        total_ton = payment_data.get('total_ton', 0)
        total_stars = payment_data.get('total_stars', 0)
        channels = payment_data.get('channels', [])
        duration_days = payment_data.get('duration_days', 0)
        posts_per_day = payment_data.get('posts_per_day', 1)
        discount = payment_data.get('discount_percent', 0)
        
        # Create header
        header = UIComponents.create_header("Payment Summary", "Review your order", UIComponents.ICONS['payment'])
        
        # Create order details
        order_details = UIComponents.create_section("Order Details",
f'''{UIComponents.create_list_item(f"Duration: {duration_days} days")}
{UIComponents.create_list_item(f"Posts per day: {posts_per_day}")}
{UIComponents.create_list_item(f"Total posts: {duration_days * posts_per_day}")}
{UIComponents.create_list_item(f"Channels: {len(channels)}")}''')
        
        # Create pricing details
        pricing = UIComponents.create_section("Pricing",
f'''{UIComponents.create_list_item(f"Base price: {UIComponents.format_price(payment_data.get('base_price', 0))}")}
{UIComponents.create_list_item(f"Discount: {discount}%")}
{UIComponents.create_list_item(f"Final price: {UIComponents.format_price(total_usd)}")}''',
UIComponents.ICONS['ton'])
        
        # Create payment options
        payment_options = UIComponents.create_section("Payment Options",
f'''{UIComponents.create_list_item(f"TON: {UIComponents.format_price(total_ton, 'TON')}")}
{UIComponents.create_list_item(f"Stars: {UIComponents.format_price(total_stars, 'STARS')}")}''')
        
        return f"{header}\n{order_details}\n{pricing}\n{payment_options}"