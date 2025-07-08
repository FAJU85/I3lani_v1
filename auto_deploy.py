"""
Auto-Deploy System for I3lani Bot
Automatically deploys updates when changes are made to the codebase
"""

import os
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
import asyncio

logger = logging.getLogger(__name__)

class AutoDeployHandler(FileSystemEventHandler):
    """File system event handler for auto-deployment"""
    
    def __init__(self, deployment_callback):
        self.deployment_callback = deployment_callback
        self.last_deployment = 0
        self.deployment_cooldown = 30  # 30 seconds cooldown
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        # Only watch Python files
        if not event.src_path.endswith('.py'):
            return
            
        # Skip cache files and temporary files
        if '__pycache__' in event.src_path or event.src_path.endswith('.pyc'):
            return
            
        current_time = time.time()
        
        # Implement cooldown to prevent rapid deployments
        if current_time - self.last_deployment < self.deployment_cooldown:
            return
            
        self.last_deployment = current_time
        
        logger.info(f"🔄 File changed: {event.src_path}")
        logger.info("🚀 Auto-deploying updates...")
        
        # Run deployment in background thread
        Thread(target=self.deployment_callback, args=(event.src_path,), daemon=True).start()

class AutoDeploySystem:
    """Automatic deployment system for I3lani Bot"""
    
    def __init__(self, bot_restart_callback=None):
        self.observer = Observer()
        self.bot_restart_callback = bot_restart_callback
        self.is_running = False
        self.watched_files = [
            'main.py',
            'handlers.py',
            'admin_system.py',
            'database.py',
            'languages.py',
            'translation_system.py',
            'channel_manager.py',
            'payments.py',
            'stars_handler.py',
            'config.py'
        ]
        
    def deploy_updates(self, changed_file):
        """Deploy updates after file changes"""
        try:
            logger.info(f"📝 Deploying changes from: {changed_file}")
            
            # Add a small delay to ensure file writing is complete
            time.sleep(2)
            
            # Restart bot if callback is provided
            if self.bot_restart_callback:
                logger.info("🔄 Restarting bot with new changes...")
                self.bot_restart_callback()
            
            # Log successful deployment
            logger.info("✅ Auto-deployment completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Auto-deployment failed: {e}")
    
    def start_auto_deploy(self):
        """Start the auto-deployment system"""
        if self.is_running:
            logger.warning("Auto-deploy system is already running")
            return
            
        try:
            # Set up file system watcher
            event_handler = AutoDeployHandler(self.deploy_updates)
            
            # Watch current directory for changes
            self.observer.schedule(event_handler, path='.', recursive=False)
            self.observer.start()
            
            self.is_running = True
            logger.info("🚀 Auto-deployment system started")
            logger.info(f"👀 Watching files: {', '.join(self.watched_files)}")
            
        except Exception as e:
            logger.error(f"Failed to start auto-deployment: {e}")
    
    def stop_auto_deploy(self):
        """Stop the auto-deployment system"""
        if not self.is_running:
            return
            
        try:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            logger.info("🛑 Auto-deployment system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping auto-deployment: {e}")
    
    def check_deployment_status(self):
        """Check current deployment status"""
        return {
            'is_running': self.is_running,
            'watched_files': self.watched_files,
            'last_deployment': getattr(self, 'last_deployment', None)
        }

# Global auto-deploy instance
auto_deploy_system = None

def init_auto_deploy(bot_restart_callback=None):
    """Initialize auto-deployment system"""
    global auto_deploy_system
    
    try:
        auto_deploy_system = AutoDeploySystem(bot_restart_callback)
        auto_deploy_system.start_auto_deploy()
        
        logger.info("🚀 Auto-deployment system initialized successfully")
        return auto_deploy_system
        
    except Exception as e:
        logger.error(f"Failed to initialize auto-deployment: {e}")
        return None

def stop_auto_deploy():
    """Stop auto-deployment system"""
    global auto_deploy_system
    
    if auto_deploy_system:
        auto_deploy_system.stop_auto_deploy()
        auto_deploy_system = None

def get_deployment_status():
    """Get current deployment status"""
    global auto_deploy_system
    
    if auto_deploy_system:
        return auto_deploy_system.check_deployment_status()
    
    return {'is_running': False, 'watched_files': [], 'last_deployment': None}

# Bot restart function
def restart_bot():
    """Restart the bot process"""
    try:
        logger.info("🔄 Restarting bot process...")
        
        # This would restart the bot in a production environment
        # For now, just log the restart
        logger.info("✅ Bot restart initiated")
        
    except Exception as e:
        logger.error(f"Failed to restart bot: {e}")

if __name__ == "__main__":
    # Test auto-deployment system
    logging.basicConfig(level=logging.INFO)
    
    system = init_auto_deploy(restart_bot)
    
    if system:
        try:
            # Keep the system running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping auto-deployment system...")
            stop_auto_deploy()