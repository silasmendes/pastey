"""
Pastey - Local Clipboard Manager
A Windows application that monitors and manages clipboard history.

Features:
- Continuous clipboard monitoring
- SQLite database for persistence
- Global hotkey (Ctrl+Shift+Z) to open interface
- Pin/unpin important items
- Automatic paste functionality
"""

import tkinter as tk
import keyboard
import pyautogui
import threading
import time
import sys
import queue
from clipboard_monitor import ClipboardMonitor
from database import ClipboardDB
from gui import ClipboardGUI


class PasteyApp:
    def __init__(self):
        """Initialize the Pastey clipboard manager application."""
        self.db = ClipboardDB()
        self.clipboard_monitor = ClipboardMonitor(self.on_clipboard_change)
        self.gui = ClipboardGUI(self.db, self.on_paste_content)
        self.running = True
        self.gui_queue = queue.Queue()
        
        # Setup global hotkey
        self.setup_hotkeys()
        
        print("Pastey Clipboard Manager started!")
        print("Press Ctrl+Shift+Z to open clipboard history")
        print("Press Ctrl+Shift+Q to exit")
    
    def setup_hotkeys(self):
        """Setup global hotkeys for the application."""
        try:
            # Clear any existing hotkeys first
            keyboard.unhook_all()
            
            # Hotkey to show clipboard manager
            keyboard.add_hotkey('ctrl+shift+z', self.toggle_gui, suppress=True)
            
            # Alternative hotkey to exit application (use a different combination)
            keyboard.add_hotkey('ctrl+shift+q', self.exit_app, suppress=True)
            
            print("Global hotkeys registered:")
            print("  Ctrl+Shift+Z - Open clipboard manager")
            print("  Ctrl+Shift+Q - Exit application")
            
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
            print("You may need to run as administrator for global hotkeys to work.")
    
    def on_clipboard_change(self, content: str):
        """
        Callback function called when clipboard content changes.
        
        Args:
            content: New clipboard content
        """
        # Filter out very short content and whitespace-only content
        if len(content.strip()) < 2:
            return
        
        # Add to database
        if self.db.add_item(content):
            print(f"New clipboard item added: {content[:50]}...")
    
    def on_paste_content(self, content: str):
        """
        Callback function to paste content to the active application.
        
        Args:
            content: Content to paste
        """
        try:
            # Set clipboard content
            self.clipboard_monitor.set_content(content)
            
            # Wait a moment for clipboard to update
            time.sleep(0.1)
            
            # Send Ctrl+V to paste
            pyautogui.hotkey('ctrl', 'v')
            
            print(f"Pasted content: {content[:50]}...")
            
        except Exception as e:
            print(f"Error pasting content: {e}")
    
    def toggle_gui(self):
        """Toggle the GUI visibility - called from hotkey thread."""
        try:
            # Put the toggle request in the queue for the main thread to process
            self.gui_queue.put(('toggle', None))
                
        except Exception as e:
            print(f"Error toggling GUI: {e}")
    
    def _process_gui_queue(self):
        """Process GUI events from the queue - called from main thread."""
        try:
            while not self.gui_queue.empty():
                action, data = self.gui_queue.get_nowait()
                
                if action == 'toggle':
                    if not self.gui.root:
                        self.gui.create_window()
                    
                    if self.gui.is_visible:
                        self.gui.hide_window()
                    else:
                        self.gui.show_window()
                        
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error processing GUI queue: {e}")
    
    def start(self):
        """Start the application."""
        # Start clipboard monitoring in a separate thread
        monitor_thread = threading.Thread(target=self._start_monitoring, daemon=True)
        monitor_thread.start()
        
        # Create the GUI window (hidden initially)
        self.gui.create_window()
        
        # Start the main event loop in the main thread
        self.run_main_loop()
    
    def _start_monitoring(self):
        """Start clipboard monitoring in background thread."""
        self.clipboard_monitor.start_monitoring()
    
    def run_main_loop(self):
        """Run the main application loop in the main thread."""
        try:
            while self.running:
                # Process GUI events from queue
                self._process_gui_queue()
                
                # Process GUI events
                if self.gui.root:
                    try:
                        self.gui.root.update()
                    except tk.TclError:
                        # Window was destroyed
                        break
                
                # Small sleep to prevent high CPU usage
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt")
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.cleanup()
    
    def exit_app(self):
        """Exit the application."""
        print("\nShutting down Pastey...")
        self.running = False
    
    def cleanup(self):
        """Clean up resources before exit."""
        try:
            # Stop clipboard monitoring
            self.clipboard_monitor.stop_monitoring()
            
            # Remove hotkeys
            keyboard.unhook_all()
            
            # Destroy GUI
            if self.gui.root:
                self.gui.destroy()
            
            print("Cleanup completed.")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")


def main():
    """Main entry point for the application."""
    try:
        # Check if running on Windows
        if sys.platform != "win32":
            print("This application is designed for Windows only.")
            return
        
        # Create and start the application
        app = PasteyApp()
        app.start()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        print("Make sure you have all required dependencies installed.")
        print("Run: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
