"""
Web3 Neo-Futuristic UI Components for I3lani Bot
Advanced blockchain aesthetic with fintech design language
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Optional, Tuple
import asyncio
from datetime import datetime

class Web3UI:
    """Web3-themed UI components with neo-futuristic design"""
    
    # Cyberpunk symbols and elements
    CYBER_SYMBOLS = {
        # Core nodes
        'node_active': '◈',
        'node_inactive': '◇',
        'node_premium': '◆',
        'node_quantum': '⬢',
        'node_void': '⬡',
        
        # Neural connections
        'connect': '━',
        'branch': '┣',
        'end': '┗',
        'vertical': '┃',
        
        # Quantum elements
        'quantum_fill': '█',
        'quantum_partial': '▓',
        'quantum_empty': '░',
        'quantum_spark': '▦',
        
        # Digital currency
        'crypto_ton': '◈',
        'crypto_stars': '⬢',
        'crypto_usd': '◇',
        'crypto_btc': '◉',
        'crypto_eth': '◆',
        
        # Status indicators
        'online': '●',
        'offline': '○',
        'processing': '◐',
        'warning': '◑',
        'critical': '●',
        
        # Directional
        'up': '▲',
        'down': '▼',
        'left': '◀',
        'right': '▶',
        'forward': '⏵',
        'back': '⏴',
    }
    
    @staticmethod
    def create_neural_header(title: str, subtitle: str = None, level: str = "primary") -> str:
        """Create neural network-style header"""
        borders = {
            "primary": ("⬢", "◈", "⬢"),
            "secondary": ("◇", "◆", "◇"),
            "quantum": ("⬡", "⬢", "⬡")
        }
        
        left, center, right = borders.get(level, borders["primary"])
        
        header_lines = []
        header_lines.append(f"{left}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{right}")
        header_lines.append(f"▲ **{title.upper()}** ▲")
        
        if subtitle:
            header_lines.append(f"◦ {subtitle} ◦")
            
        header_lines.append(f"{left}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{right}")
        
        return "\n".join(header_lines)
    
    @staticmethod
    def create_quantum_section(title: str, content: str, node_type: str = "data") -> str:
        """Create quantum-styled content section"""
        nodes = {
            "data": "◇",
            "process": "◈", 
            "output": "◆",
            "warning": "⬡",
            "success": "⬢",
            "critical": "◉"
        }
        
        node = nodes.get(node_type, "◇")
        
        return f"""
{node}━━ **{title}** ━━{node}
{content}
"""
    
    @staticmethod
    def create_holographic_display(content: str, display_type: str = "info") -> str:
        """Create holographic-style information display"""
        displays = {
            "info": ("▣", "◤ DATA MATRIX ◥"),
            "success": ("▦", "◤ SUCCESS PROTOCOL ◥"), 
            "warning": ("▨", "◤ ALERT SYSTEM ◥"),
            "error": ("▩", "◤ ERROR DETECTED ◥"),
            "crypto": ("◈", "◤ CRYPTO VAULT ◥"),
            "neural": ("⬢", "◤ NEURAL NETWORK ◥"),
            "quantum": ("⬡", "◤ QUANTUM STATE ◥")
        }
        
        symbol, header = displays.get(display_type, ("▣", "◤ SYSTEM DATA ◥"))
        
        return f"""
{symbol}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{symbol}
{header}
{content}
{symbol}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{symbol}
"""
    
    @staticmethod
    def create_quantum_progress(current: float, maximum: float, width: int = 12) -> str:
        """Create quantum-themed progress visualization"""
        if maximum == 0:
            percentage = 0
        else:
            percentage = min(current / maximum, 1.0)
        
        filled = int(percentage * width)
        empty = width - filled
        
        # Quantum progress elements
        quantum_fill = "█" * filled
        quantum_empty = "░" * empty
        
        progress_visual = f"▤{quantum_fill}{quantum_empty}▤"
        
        return f"""
◢━━━ QUANTUM PROGRESS ━━━◣
{progress_visual} {percentage * 100:.1f}%
◥━━━━━━━━━━━━━━━━━━━━━━━◤
"""
    
    @staticmethod
    def create_blockchain_metrics(metrics: dict, title: str = "BLOCKCHAIN ANALYTICS") -> str:
        """Create blockchain-themed metrics display"""
        result = f"◦◦◦ {title} ◦◦◦\n"
        result += "┌─────────────────────────────────┐\n"
        
        for key, value in metrics.items():
            # Format key
            formatted_key = key.replace('_', ' ').title()
            formatted_value = str(value)
            
            # Add cryptocurrency symbols where appropriate
            if 'ton' in key.lower():
                formatted_value = f"◈ {formatted_value}"
            elif 'star' in key.lower():
                formatted_value = f"⬢ {formatted_value}"
            elif 'usd' in key.lower() or '$' in str(value):
                formatted_value = f"◇ {formatted_value}"
            
            result += f"│ {formatted_key:<20} {formatted_value:>8} │\n"
        
        result += "└─────────────────────────────────┘"
        return result
    
    @staticmethod
    def create_neural_navigation(options: list) -> str:
        """Create neural network-style navigation"""
        nav_text = "\n◇━━━ NEURAL PATHWAYS ━━━◇\n"
        
        for i, option in enumerate(options):
            connector = "├─" if i < len(options) - 1 else "└─"
            nav_text += f"{connector} ◈ {option}\n"
            
        return nav_text
    
    @staticmethod
    def format_crypto_amount(amount: float, currency: str = "TON") -> str:
        """Format cryptocurrency with Web3 aesthetics"""
        symbols = {
            "TON": "◈",
            "USD": "◇",
            "STARS": "⬢",
            "ETH": "◆",
            "BTC": "◉"
        }
        
        symbol = symbols.get(currency.upper(), "◇")
        
        if currency.upper() == "USD":
            return f"{symbol} ${amount:.2f}"
        else:
            return f"{symbol} {amount:.2f} {currency}"
    
    @staticmethod
    def create_cyber_tier_display(tier: str, stats: dict = None) -> str:
        """Create cyberpunk tier status display"""
        tier_designs = {
            "Basic": ("◇", "INITIATE LEVEL"),
            "Silver": ("◈", "NAVIGATOR CLASS"), 
            "Gold": ("◆", "ARCHITECT TIER"),
            "Premium": ("⬢", "QUANTUM STATUS"),
            "VIP": ("◉", "NEXUS PRIME")
        }
        
        symbol, display_name = tier_designs.get(tier, ("◇", f"{tier.upper()} TIER"))
        
        tier_display = f"""
{symbol}━━━ {display_name} ━━━{symbol}
"""
        
        if stats:
            tier_display += "┌─────────────────────────────┐\n"
            for key, value in stats.items():
                tier_display += f"│ {key:<18} {str(value):>8} │\n"
            tier_display += "└─────────────────────────────┘"
        
        return tier_display
    
    @staticmethod
    def create_fintech_dashboard(title: str, data: dict) -> str:
        """Create professional fintech-style dashboard"""
        dashboard = f"""
⬢━━━━━━━ {title.upper()} DASHBOARD ━━━━━━━⬢

▣ PERFORMANCE METRICS
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
"""
        
        for metric, value in data.items():
            formatted_metric = metric.replace('_', ' ').title()
            formatted_value = str(value)
            
            # Add visual indicators for different data types
            if isinstance(value, (int, float)):
                if value > 0:
                    indicator = "▲"
                elif value < 0:
                    indicator = "▼"
                else:
                    indicator = "◈"
            else:
                indicator = "◈"
            
            dashboard += f"┃ {indicator} {formatted_metric:<22} {formatted_value:>5} ┃\n"
        
        dashboard += "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        return dashboard
    
    @staticmethod
    def create_web3_alert(message: str, alert_type: str = "info") -> str:
        """Create Web3-themed alert messages"""
        alert_designs = {
            "info": ("◇", "SYSTEM NOTIFICATION", "░"),
            "success": ("◈", "SUCCESS PROTOCOL", "▓"),
            "warning": ("⬡", "WARNING DETECTED", "▨"), 
            "error": ("▩", "CRITICAL ERROR", "█"),
            "crypto": ("◆", "CRYPTO TRANSACTION", "▦"),
            "quantum": ("⬢", "QUANTUM UPDATE", "▤")
        }
        
        symbol, header, fill = alert_designs.get(alert_type, ("◇", "SYSTEM MESSAGE", "░"))
        
        return f"""
{symbol}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{symbol}
▲ {header} ▲
{message}
{symbol}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{symbol}
"""
    
    @staticmethod
    def create_quantum_wallet(balance: float, currency: str = "TON", status: str = "secured") -> str:
        """Create quantum wallet visualization"""
        status_indicators = {
            "secured": "🔒 QUANTUM SECURED",
            "active": "⚡ ACTIVE MINING",
            "syncing": "🔄 BLOCKCHAIN SYNC",
            "offline": "📴 OFFLINE MODE"
        }
        
        status_text = status_indicators.get(status, "🔒 QUANTUM SECURED")
        formatted_balance = Web3UI.format_crypto_amount(balance, currency)
        
        return f"""
⬢━━━━━━━ QUANTUM WALLET ━━━━━━━⬢
┌─────────────────────────────────┐
│           ◈ BALANCE ◈           │
│     {formatted_balance:^23}     │
│                                 │
│      {status_text:^21}      │
└─────────────────────────────────┘
"""
    
    @staticmethod
    def create_matrix_table(headers: list, rows: list, title: str = "DATA MATRIX") -> str:
        """Create Matrix-style data table"""
        table = f"""
▲▲▲ {title.upper()} ▲▲▲
╔{'═' * (len(headers) * 12 + len(headers) - 1)}╗
║ {'│'.join(f'{h:^11}' for h in headers)} ║
╠{'═' * (len(headers) * 12 + len(headers) - 1)}╣
"""
        
        for row in rows:
            formatted_row = []
            for cell in row:
                formatted_row.append(f'{str(cell):^11}')
            table += f"║ {'│'.join(formatted_row)} ║\n"
        
        table += f"╚{'═' * (len(headers) * 12 + len(headers) - 1)}╝"
        return table
    
    @staticmethod
    def create_neon_separator(length: int = 35, pattern: str = "standard") -> str:
        """Create neon-style separators"""
        patterns = {
            "standard": ["◈", "◇", "◆", "⬢", "⬡"],
            "quantum": ["⬢", "⬡", "▦", "▤", "▨"],
            "neural": ["◇", "◈", "◇", "◈", "◇"],
            "matrix": ["█", "▓", "░", "▓", "█"]
        }
        
        pattern_chars = patterns.get(pattern, patterns["standard"])
        separator = ""
        
        for i in range(length):
            separator += pattern_chars[i % len(pattern_chars)]
            
        return separator
    
    @staticmethod
    def create_cyber_keyboard_button(text: str, icon_type: str = "standard") -> str:
        """Create cyberpunk-styled button text"""
        icons = {
            "standard": "◈",
            "action": "▶",
            "back": "◀",
            "confirm": "✓",
            "cancel": "✗",
            "crypto": "◆",
            "quantum": "⬢",
            "neural": "◇"
        }
        
        icon = icons.get(icon_type, "◈")
        return f"{icon} {text}"
    
    @staticmethod  
    def create_earnings_display(balance: float, tier: str, progress: float = 0) -> str:
        """Create Web3 earnings dashboard"""
        tier_symbol = Web3UI.create_cyber_tier_display(tier)
        formatted_balance = Web3UI.format_crypto_amount(balance, "TON")
        progress_bar = Web3UI.create_quantum_progress(progress, 25.0)
        
        return f"""
{Web3UI.create_neural_header("QUANTUM EARNINGS MATRIX", "Partner Reward System")}

{Web3UI.create_quantum_section("Current Balance", formatted_balance, "crypto")}

{tier_symbol}

{progress_bar}

{Web3UI.create_holographic_display("Rewards secured in quantum vault", "crypto")}
"""

class Web3Templates:
    """Pre-built Web3 UI templates for common scenarios"""
    
    @staticmethod
    def main_menu(username: str, language: str = 'en') -> str:
        """Create Web3-themed main menu"""
        welcome_data = {
            'en': {
                'title': 'I3LANI NEURAL NETWORK',
                'subtitle': f'Welcome, Agent {username}',
                'features': [
                    'Multi-Channel Ad Broadcasting',
                    'Quantum Payment Processing', 
                    'Neural Analytics Dashboard',
                    'Crypto Reward Mining'
                ]
            },
            'ar': {
                'title': 'شبكة I3LANI العصبية',
                'subtitle': f'مرحباً، العميل {username}',
                'features': [
                    'بث الإعلانات متعدد القنوات',
                    'معالجة المدفوعات الكمية',
                    'لوحة التحليلات العصبية', 
                    'تعدين المكافآت المشفرة'
                ]
            }
        }
        
        data = welcome_data.get(language, welcome_data['en'])
        
        menu = Web3UI.create_neural_header(data['title'], data['subtitle'])
        menu += "\n\n"
        
        features_text = "\n".join([f"◈ {feature}" for feature in data['features']])
        menu += Web3UI.create_quantum_section("NEURAL CAPABILITIES", features_text, "process")
        
        menu += "\n" + Web3UI.create_web3_alert("Select neural pathway to continue", "info")
        
        return menu
    
    @staticmethod
    def payment_interface(amount: float, currency: str, channels: int) -> str:
        """Create Web3 payment interface"""
        payment_data = {
            'Amount': Web3UI.format_crypto_amount(amount, currency),
            'Channels': f'{channels} Neural Nodes',
            'Protocol': 'Quantum Secure',
            'Status': 'Ready for Mining'
        }
        
        interface = Web3UI.create_neural_header("QUANTUM PAYMENT PROTOCOL", "Secure Transaction Interface")
        interface += "\n\n"
        interface += Web3UI.create_blockchain_metrics(payment_data, "TRANSACTION MATRIX")
        interface += "\n\n"
        interface += Web3UI.create_web3_alert("Quantum encryption active. Proceed with payment mining.", "crypto")
        
        return interface
    
    @staticmethod
    def earnings_dashboard(balance: float, tier: str, referrals: int, progress: float) -> str:
        """Create comprehensive earnings dashboard"""
        earnings_data = {
            'Quantum Balance': Web3UI.format_crypto_amount(balance, "TON"),
            'Neural Tier': tier,
            'Network Nodes': referrals,
            'Mining Progress': f'{progress:.1f}%'
        }
        
        dashboard = Web3UI.create_neural_header("PARTNER EARNINGS MATRIX", "Quantum Reward System")
        dashboard += "\n\n"
        dashboard += Web3UI.create_fintech_dashboard("NEURAL EARNINGS", earnings_data)
        dashboard += "\n\n"
        dashboard += Web3UI.create_quantum_progress(progress, 100)
        dashboard += "\n\n"
        dashboard += Web3UI.create_web3_alert("Continue mining to unlock quantum rewards", "quantum")
        
        return dashboard