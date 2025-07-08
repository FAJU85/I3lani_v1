"""
Bot Lock Manager for I3lani Bot
Ensures only one bot instance runs at a time
"""
import os
import sys
import time
import signal
import psutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BotLockManager:
    """Manages bot instance locking to prevent conflicts"""
    
    def __init__(self):
        self.lock_file = Path(".bot_lock")
        self.pid_file = Path(".bot_pid")
    
    def acquire_lock(self) -> bool:
        """Acquire bot lock, ensuring only one instance runs"""
        try:
            # Check if another instance is running
            if self.pid_file.exists():
                old_pid = int(self.pid_file.read_text().strip())
                
                # Check if process is actually running
                if self._is_process_running(old_pid):
                    logger.warning(f"Bot already running with PID {old_pid}")
                    # Try to terminate the old process
                    self._terminate_process(old_pid)
                    time.sleep(2)  # Give it time to shutdown
                    
                    # Check again
                    if self._is_process_running(old_pid):
                        logger.error("Failed to terminate existing bot instance")
                        return False
                
                # Clean up stale files
                self.pid_file.unlink(missing_ok=True)
                self.lock_file.unlink(missing_ok=True)
            
            # Create new lock
            current_pid = os.getpid()
            self.pid_file.write_text(str(current_pid))
            self.lock_file.touch()
            
            logger.info(f"Bot lock acquired for PID {current_pid}")
            return True
            
        except Exception as e:
            logger.error(f"Error acquiring lock: {e}")
            return False
    
    def release_lock(self):
        """Release bot lock"""
        try:
            self.pid_file.unlink(missing_ok=True)
            self.lock_file.unlink(missing_ok=True)
            logger.info("Bot lock released")
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running"""
        try:
            process = psutil.Process(pid)
            # Check if it's a Python process (our bot)
            return process.is_running() and 'python' in process.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def _terminate_process(self, pid: int):
        """Terminate a process by PID"""
        try:
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent SIGTERM to PID {pid}")
        except ProcessLookupError:
            logger.info(f"Process {pid} already terminated")
        except Exception as e:
            logger.error(f"Error terminating process {pid}: {e}")
    
    def cleanup_all_bot_processes(self):
        """Clean up all running bot processes"""
        try:
            # Find all Python processes that might be our bot
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info.get('cmdline', [])
                        if any('main_bot.py' in arg or 'deployment_server.py' in arg for arg in cmdline):
                            if proc.pid != os.getpid():
                                logger.info(f"Terminating bot process {proc.pid}")
                                proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Clean up lock files
            self.release_lock()
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error cleaning up processes: {e}")

# Global instance
lock_manager = BotLockManager()