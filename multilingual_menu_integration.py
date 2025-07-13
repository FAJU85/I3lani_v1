
# Multilingual Menu System Integration Wrapper
from multilingual_menu_system import MultilingualMenuSystem as _MultilingualMenuSystem

class MultilingualMenuWrapper:
    """Wrapper for MultilingualMenuSystem that handles bot requirement"""
    
    def __init__(self, bot=None):
        self.bot = bot
        self._menu_system = None
    
    def get_menu_system(self):
        """Get menu system instance with bot if available"""
        if self.bot and not self._menu_system:
            self._menu_system = _MultilingualMenuSystem(self.bot)
        return self._menu_system
    
    @property
    def is_ready(self):
        """Check if menu system is ready"""
        return self.bot is not None

# Global wrapper instance
multilingual_menu_wrapper = MultilingualMenuWrapper()

def set_bot_instance(bot):
    """Set bot instance for multilingual menu system"""
    multilingual_menu_wrapper.bot = bot

def get_multilingual_menu_system():
    """Get multilingual menu system instance"""
    return multilingual_menu_wrapper.get_menu_system()
