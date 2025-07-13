
# Channel Manager Integration Wrapper
from channel_manager import ChannelManager as _ChannelManager
from database import Database

class ChannelManagerWrapper:
    """Wrapper for ChannelManager that handles bot and database requirements"""
    
    def __init__(self, bot=None, database=None):
        self.bot = bot
        self.database = database or Database()
        self._manager = None
    
    def get_manager(self):
        """Get manager instance with bot and database if available"""
        if self.bot and not self._manager:
            self._manager = _ChannelManager(self.bot, self.database)
        return self._manager
    
    @property
    def is_ready(self):
        """Check if manager is ready"""
        return self.bot is not None

# Global wrapper instance
channel_manager_wrapper = ChannelManagerWrapper()

def set_bot_and_database(bot, database=None):
    """Set bot and database instances for channel manager"""
    channel_manager_wrapper.bot = bot
    if database:
        channel_manager_wrapper.database = database

def get_channel_manager():
    """Get channel manager instance"""
    return channel_manager_wrapper.get_manager()
