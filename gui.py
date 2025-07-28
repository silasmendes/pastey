"""
GUI module for clipboard manager.
Provides the main interface for viewing and managing clipboard history.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
from typing import Callable, List, Tuple, Optional
from database import ClipboardDB


class ClipboardGUI:
    def __init__(self, db: ClipboardDB, on_paste_callback: Callable[[str], None]):
        """
        Initialize the clipboard manager GUI.
        
        Args:
            db: Database instance for clipboard operations
            on_paste_callback: Function to call when pasting content
        """
        self.db = db
        self.on_paste_callback = on_paste_callback
        self.root: Optional[tk.Tk] = None
        self.tree: Optional[ttk.Treeview] = None
        self.is_visible = False
        
    def create_window(self):
        """Create the main window."""
        if self.root:
            return
            
        self.root = tk.Tk()
        self.root.title("Pastey - Clipboard Manager")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Configure window to be hidden by default
        self.root.withdraw()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Bind Escape key to close window
        self.root.bind("<Escape>", lambda e: self.hide_window())
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title label
        title_label = ttk.Label(main_frame, text="Clipboard History", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        ttk.Button(button_frame, text="Refresh", 
                  command=self.refresh_list).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Clear Unpinned", 
                  command=self.clear_unpinned).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Delete Selected", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        # Instructions label
        instructions = ttk.Label(main_frame, 
                                text="Double-click or press Enter to paste • Right-click to pin/unpin",
                                foreground="gray")
        instructions.pack(pady=(0, 5))
        
        # Treeview frame with scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("content", "pinned", "timestamp")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("content", text="Content")
        self.tree.heading("pinned", text="Pinned")
        self.tree.heading("timestamp", text="Timestamp")
        
        self.tree.column("content", width=350, minwidth=200)
        self.tree.column("pinned", width=60, minwidth=50)
        self.tree.column("timestamp", width=150, minwidth=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Paste", command=self.paste_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Toggle Pin", command=self.toggle_pin_selected)
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
    
    def _setup_bindings(self):
        """Setup event bindings."""
        # Double-click to paste
        self.tree.bind("<Double-1>", lambda e: self.paste_selected())
        
        # Enter key to paste
        self.tree.bind("<Return>", lambda e: self.paste_selected())
        
        # Right-click for context menu
        self.tree.bind("<Button-3>", self._show_context_menu)
        
        # Space to toggle pin
        self.tree.bind("<space>", lambda e: self.toggle_pin_selected())
        
        # Delete key to delete item
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
    
    def _show_context_menu(self, event):
        """Show context menu at cursor position."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def show_window(self):
        """Show the clipboard manager window."""
        if not self.root:
            self.create_window()
        
        self.refresh_list()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_visible = True
        
        # Focus on the treeview
        self.tree.focus_set()
        
        # Select the first item if available
        items = self.tree.get_children()
        if items:
            self.tree.selection_set(items[0])
    
    def hide_window(self):
        """Hide the clipboard manager window."""
        if self.root:
            self.root.withdraw()
            self.is_visible = False
    
    def refresh_list(self):
        """Refresh the clipboard items list."""
        if not self.tree:
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get items from database
        items = self.db.get_all_items()
        
        # Add items to treeview
        for item_id, content, is_pinned, timestamp in items:
            # Truncate content for display
            display_content = content.replace('\n', ' ').replace('\r', '')
            if len(display_content) > 80:
                display_content = display_content[:77] + "..."
            
            pinned_text = "📌" if is_pinned else ""
            
            # Format timestamp
            formatted_time = timestamp.split('.')[0] if '.' in timestamp else timestamp
            
            # Insert item with ID as tag
            item_ref = self.tree.insert("", tk.END, 
                                      values=(display_content, pinned_text, formatted_time),
                                      tags=(str(item_id),))
            
            # Highlight pinned items
            if is_pinned:
                self.tree.set(item_ref, "content", f"📌 {display_content}")
    
    def get_selected_item_id(self) -> Optional[int]:
        """Get the ID of the currently selected item."""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        tags = self.tree.item(item, "tags")
        return int(tags[0]) if tags else None
    
    def paste_selected(self):
        """Paste the selected clipboard item."""
        item_id = self.get_selected_item_id()
        if not item_id:
            return
        
        content = self.db.get_item_content(item_id)
        if content:
            self.hide_window()
            self.on_paste_callback(content)
    
    def toggle_pin_selected(self):
        """Toggle pin status of the selected item."""
        item_id = self.get_selected_item_id()
        if item_id and self.db.toggle_pin(item_id):
            self.refresh_list()
    
    def delete_selected(self):
        """Delete the selected item."""
        item_id = self.get_selected_item_id()
        if not item_id:
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            if self.db.delete_item(item_id):
                self.refresh_list()
    
    def clear_unpinned(self):
        """Clear all unpinned items."""
        if messagebox.askyesno("Confirm Clear", "Clear all unpinned items?"):
            count = self.db.clear_unpinned_items()
            self.refresh_list()
            messagebox.showinfo("Cleared", f"Removed {count} unpinned items.")
    
    def destroy(self):
        """Destroy the window."""
        if self.root:
            self.root.destroy()
            self.root = None
