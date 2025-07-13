#!/usr/bin/env python3
"""
Integration Fixes for I3lani Bot
Fixes system integration issues by providing proper bot instance handling
"""

import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class IntegrationFixManager:
    def __init__(self):
        self.fixes_applied = []
        
    async def apply_all_integration_fixes(self):
        """Apply all integration fixes"""
        
        print("🔧 APPLYING INTEGRATION FIXES")
        print("=" * 50)
        
        # Fix 1: Enhanced TON Payment Monitoring export
        await self._fix_ton_payment_monitoring_export()
        
        # Fix 2: Campaign Publisher bot instance requirement
        await self._fix_campaign_publisher_integration()
        
        # Fix 3: Channel Manager bot instance requirement
        await self._fix_channel_manager_integration()
        
        # Fix 4: Multilingual Menu System bot instance requirement
        await self._fix_multilingual_menu_integration()
        
        # Generate fix report
        await self._generate_fix_report()
        
        return self.fixes_applied
    
    async def _fix_ton_payment_monitoring_export(self):
        """Fix TON payment monitoring export issue"""
        print("\n1. 🔨 Fixing TON Payment Monitoring Export...")
        
        try:
            # Check the current export in enhanced_ton_payment_monitoring.py
            with open('enhanced_ton_payment_monitoring.py', 'r') as f:
                content = f.read()
            
            # Add proper export if missing
            if 'enhanced_ton_payment_monitoring =' not in content:
                # Find the class definition
                if 'class EnhancedTonPaymentMonitoring:' in content:
                    # Add global instance at the end
                    content += '\n\n# Global instance for easy import\nenhanced_ton_payment_monitoring = EnhancedTonPaymentMonitoring()\n'
                    
                    with open('enhanced_ton_payment_monitoring.py', 'w') as f:
                        f.write(content)
                    
                    print("   ✅ Added global instance export")
                    self.fixes_applied.append("Fixed TON payment monitoring export")
                else:
                    print("   ⚠️  No class definition found")
            else:
                print("   ✅ Export already exists")
                
        except Exception as e:
            print(f"   ❌ Error fixing TON monitoring: {e}")
    
    async def _fix_campaign_publisher_integration(self):
        """Fix campaign publisher bot instance requirement"""
        print("\n2. 🔨 Fixing Campaign Publisher Integration...")
        
        try:
            # Create a wrapper that handles bot instance requirement
            wrapper_content = '''
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
'''
            
            with open('campaign_publisher_integration.py', 'w') as f:
                f.write(wrapper_content)
            
            print("   ✅ Created campaign publisher integration wrapper")
            self.fixes_applied.append("Created campaign publisher integration wrapper")
            
        except Exception as e:
            print(f"   ❌ Error fixing campaign publisher: {e}")
    
    async def _fix_channel_manager_integration(self):
        """Fix channel manager bot instance requirement"""
        print("\n3. 🔨 Fixing Channel Manager Integration...")
        
        try:
            # Create a wrapper for channel manager
            wrapper_content = '''
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
'''
            
            with open('channel_manager_integration.py', 'w') as f:
                f.write(wrapper_content)
            
            print("   ✅ Created channel manager integration wrapper")
            self.fixes_applied.append("Created channel manager integration wrapper")
            
        except Exception as e:
            print(f"   ❌ Error fixing channel manager: {e}")
    
    async def _fix_multilingual_menu_integration(self):
        """Fix multilingual menu system bot instance requirement"""
        print("\n4. 🔨 Fixing Multilingual Menu Integration...")
        
        try:
            # Create a wrapper for multilingual menu system
            wrapper_content = '''
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
'''
            
            with open('multilingual_menu_integration.py', 'w') as f:
                f.write(wrapper_content)
            
            print("   ✅ Created multilingual menu integration wrapper")
            self.fixes_applied.append("Created multilingual menu integration wrapper")
            
        except Exception as e:
            print(f"   ❌ Error fixing multilingual menu: {e}")
    
    async def _generate_fix_report(self):
        """Generate integration fix report"""
        print("\n" + "=" * 50)
        print("📊 INTEGRATION FIXES REPORT")
        print("=" * 50)
        
        print(f"\n🔧 FIXES APPLIED: {len(self.fixes_applied)}")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"   {i}. {fix}")
        
        print("\n✅ INTEGRATION FIXES COMPLETE")
        print("\nNOTE: These fixes provide wrappers that handle bot instance requirements.")
        print("The actual systems will work properly when bot instances are available.")

async def main():
    """Main function to apply integration fixes"""
    fixer = IntegrationFixManager()
    fixes = await fixer.apply_all_integration_fixes()
    return fixes

if __name__ == "__main__":
    asyncio.run(main())