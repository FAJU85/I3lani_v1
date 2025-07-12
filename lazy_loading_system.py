
# Lazy loading wrapper for non-essential systems
import asyncio
import logging

logger = logging.getLogger(__name__)

class LazyLoader:
    def __init__(self):
        self.loaded_systems = {}
        
    async def load_system(self, system_name: str):
        """Load a system on demand"""
        if system_name in self.loaded_systems:
            return self.loaded_systems[system_name]
        
        try:
            logger.info(f"📦 Lazy loading {system_name}...")
            module = __import__(system_name)
            self.loaded_systems[system_name] = module
            return module
        except Exception as e:
            logger.error(f"❌ Failed to lazy load {system_name}: {e}")
            return None
    
    async def load_all_remaining(self):
        """Load all remaining systems in background"""
        systems = [
            'gamification',
            'viral_referral_game', 
            'content_integrity_system',
            'translation_system'
        ]
        
        for system in systems:
            await self.load_system(system)
            await asyncio.sleep(0.1)  # Small delay to prevent blocking

# Global lazy loader
lazy_loader = LazyLoader()
