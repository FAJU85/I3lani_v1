
# Campaign Publisher Integration Wrapper
from enhanced_campaign_publisher import EnhancedCampaignPublisher as _EnhancedCampaignPublisher

class CampaignPublisherWrapper:
    """Wrapper for EnhancedCampaignPublisher that handles bot instance requirement"""
    
    def __init__(self, bot_instance=None):
        self.bot_instance = bot_instance
        self._publisher = None
    
    def get_publisher(self):
        """Get publisher instance with bot if available"""
        if self.bot_instance and not self._publisher:
            self._publisher = _EnhancedCampaignPublisher(self.bot_instance)
        return self._publisher
    
    @property
    def is_ready(self):
        """Check if publisher is ready"""
        return self.bot_instance is not None

# Global wrapper instance
campaign_publisher_wrapper = CampaignPublisherWrapper()

def set_bot_instance(bot):
    """Set bot instance for campaign publisher"""
    campaign_publisher_wrapper.bot_instance = bot

def get_campaign_publisher():
    """Get campaign publisher instance"""
    return campaign_publisher_wrapper.get_publisher()
