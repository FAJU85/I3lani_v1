"""
Enhanced UI Components for I3lani Bot Neural Network Interface
Provides advanced visual effects, colors, and hover-like button styling
"""

def create_neural_header(title: str) -> str:
    """Create neural network header with visual effects"""
    return f"""
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
<b>⚡ {title} ⚡</b>
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
"""

def create_quantum_section(title: str, content: str) -> str:
    """Create quantum-styled section with borders"""
    return f"""
<b>━━━━ {title} ━━━━</b>
{content}
"""

def create_neural_status_indicator(status: str, detail: str) -> str:
    """Create neural status indicator with color coding"""
    status_icons = {
        'online': '🟢',
        'offline': '🔴',
        'warning': '🟡',
        'syncing': '🔵',
        'optimal': '🟢'
    }
    
    icon = status_icons.get(status.lower(), '⚪')
    return f"<b>{icon} {detail}</b>"

def create_quantum_button_style(text: str, icon: str = "", style: str = "default") -> str:
    """Create quantum-styled button text with visual effects"""
    styles = {
        'primary': f"🚀 ▶ {text.upper()}",
        'secondary': f"{icon} ◆ {text}",
        'tertiary': f"{icon} ◇ {text}",
        'special': f"{icon} ◈ {text}",
        'highlight': f"🏆 ▲ {text.upper()} ▲",
        'gift': f"🎁 ⚡ {text.upper()} ⚡"
    }
    
    return styles.get(style, f"{icon} {text}")

def create_neural_stats_display(stats: dict) -> str:
    """Create neural network statistics display"""
    stats_text = ""
    for key, value in stats.items():
        stats_text += f"<b>{key}:</b> <code>{value}</code>\n"
    return stats_text

def create_quantum_progress_bar(current: int, maximum: int, width: int = 10) -> str:
    """Create quantum-styled progress bar"""
    filled = int((current / maximum) * width) if maximum > 0 else 0
    empty = width - filled
    
    bar = "▰" * filled + "▱" * empty
    percentage = int((current / maximum) * 100) if maximum > 0 else 0
    
    return f"<code>[{bar}] {percentage}%</code>"

def create_neural_feature_list(features: list) -> str:
    """Create neural network feature list with icons"""
    feature_text = ""
    icons = ["🚀", "💎", "🔗", "🎮", "🏆", "⚡", "🌟", "🔮"]
    
    for i, feature in enumerate(features):
        icon = icons[i % len(icons)]
        feature_text += f"<b>{icon}</b> <i>{feature}</i>\n"
    
    return feature_text

def create_quantum_divider(style: str = "default") -> str:
    """Create quantum-styled dividers"""
    dividers = {
        'default': "<b>═══════════════════════════════════</b>",
        'double': "<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>",
        'dotted': "<b>◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇</b>",
        'neural': "<pre>▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲</pre>"
    }
    
    return dividers.get(style, dividers['default'])

def create_animated_text_effect(text: str, effect: str = "pulse") -> str:
    """Create animated text effects using HTML formatting"""
    effects = {
        'pulse': f"<b><i>{text}</i></b>",
        'glow': f"<u><b>{text}</b></u>",
        'highlight': f"<code>{text}</code>",
        'emphasis': f"<b>{text}</b>",
        'subtle': f"<i>{text}</i>"
    }
    
    return effects.get(effect, text)

def create_neural_menu_template(title: str, stats: dict, features: list, call_to_action: str) -> str:
    """Create complete neural network menu template"""
    
    template = f"""
{create_neural_header(title)}

<pre>    ▲▲▲ NEURAL NETWORK ACTIVE ▲▲▲    </pre>
{create_neural_status_indicator('optimal', 'SYSTEM STATUS: ONLINE & OPTIMIZED')}
{create_neural_status_indicator('optimal', 'AI ENGINE: FULLY OPERATIONAL')}
{create_neural_status_indicator('optimal', 'QUANTUM CORE: SYNCHRONIZED')}

{create_quantum_section("NEURAL BROADCAST STATISTICS", create_neural_stats_display(stats))}

{create_quantum_section("QUANTUM FEATURES", create_neural_feature_list(features))}

{create_quantum_divider('default')}
<b>🎯 {call_to_action} 🎯</b>
{create_quantum_divider('default')}
"""
    
    return template.strip()

# Color codes for enhanced styling
NEURAL_COLORS = {
    'primary': '#00FFFF',      # Cyan
    'secondary': '#FF6B6B',    # Red
    'success': '#4ECDC4',      # Teal
    'warning': '#FFE66D',      # Yellow
    'info': '#A8E6CF',         # Light Green
    'dark': '#2C3E50',         # Dark Blue
    'accent': '#9B59B6'        # Purple
}

def get_colored_text(text: str, color: str) -> str:
    """Get colored text using HTML (Telegram supports basic HTML colors)"""
    return f'<span style="color: {color};">{text}</span>' if color in NEURAL_COLORS.values() else text