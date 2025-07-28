"""
Clipboard monitor module.
Continuously monitors the Windows clipboard for changes.
"""

import pyperclip
import threading
import time
from typing import Callable, Optional


class ClipboardMonitor:
    def __init__(self, callback: Callable[[str], None]):
        """
        Initialize clipboard monitor.
        
        Args:
            callback: Function to call when new clipboard content is detected
        """
        self.callback = callback
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_content = ""
        
    def start_monitoring(self):
        """Start monitoring clipboard in a separate thread."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Clipboard monitoring started...")
    
    def stop_monitoring(self):
        """Stop monitoring clipboard."""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        print("Clipboard monitoring stopped.")
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread."""
        # Initialize with current clipboard content
        try:
            self.last_content = pyperclip.paste()
        except Exception:
            self.last_content = ""
        
        while self.monitoring:
            try:
                current_content = pyperclip.paste()
                
                # Check if content has changed and is not empty
                if (current_content != self.last_content and 
                    current_content.strip() and 
                    isinstance(current_content, str)):
                    
                    self.last_content = current_content
                    # Call the callback with new content
                    self.callback(current_content)
                
                # Sleep to avoid excessive CPU usage
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
                time.sleep(1)  # Wait longer on error
    
    def get_current_content(self) -> str:
        """Get current clipboard content."""
        try:
            return pyperclip.paste()
        except Exception:
            return ""
    
    def set_content(self, content: str):
        """Set clipboard content."""
        try:
            pyperclip.copy(content)
            self.last_content = content
        except Exception as e:
            print(f"Error setting clipboard content: {e}")
