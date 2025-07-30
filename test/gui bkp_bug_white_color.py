"""
GUI module for clipboard manager.
Provides the main interface for viewing and managing clipboard history and bookmarks.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyautogui
from typing import Callable, List, Tuple, Optional
from database import ClipboardDB, BookmarksDB
from bookmarks_gui import BookmarksGUI


class ClipboardGUI:
    def __init__(self, db: ClipboardDB, on_paste_callback: Callable[[str], None]):
        """
        Initialize the clipboard manager GUI.
        
        Args:
            db: Database instance for clipboard operations
            on_paste_callback: Function to call when pasting content
        """
        self.db = db
        self.bookmarks_db = BookmarksDB(db.db_path)  # Use same database file
        self.on_paste_callback = on_paste_callback
        self.root: Optional[tk.Tk] = None
        self.tree: Optional[ttk.Treeview] = None
        self.notebook: Optional[ttk.Notebook] = None
        self.bookmarks_gui: Optional[BookmarksGUI] = None
        self.is_visible = False
        
    def create_window(self):
        """Create the main window."""
        if self.root:
            return
            
        self.root = tk.Tk()
        self.root.title("Pastey - Clipboard Manager & Bookmarks")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Configure window properties for better visibility
        self.root.attributes('-alpha', 0.97)  # Slight transparency for modern look
        
        # Configure window to be hidden by default
        self.root.withdraw()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Bind Escape key to close window
        self.root.bind("<Escape>", lambda e: self.hide_window())
        
        # Bind Alt+Tab friendly behavior
        self.root.bind("<FocusOut>", self._on_focus_out)
        
        self._create_widgets()
        self._setup_bindings()
        self.root.bind("<FocusOut>", self._on_focus_out)
        
        self._create_widgets()
        self._setup_bindings()
    
    def _on_focus_out(self, event):
        """Handle when window loses focus."""
        # Don't hide the window when it loses focus unless explicitly hidden
        pass
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create clipboard tab
        clipboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(clipboard_frame, text="Clipboard History")
        self._create_clipboard_widgets(clipboard_frame)
        
        # Create bookmarks tab
        bookmarks_frame = ttk.Frame(self.notebook)
        self.notebook.add(bookmarks_frame, text="URL Bookmarks")
        
        # Initialize bookmarks GUI
        self.bookmarks_gui = BookmarksGUI(self.bookmarks_db)
        self.bookmarks_gui.create_widgets(bookmarks_frame)
        
        # Set clipboard tab as default
        self.notebook.select(clipboard_frame)
    
    def _create_clipboard_widgets(self, parent_frame):
        """Create the clipboard tab widgets."""
        # Title label
        title_label = ttk.Label(parent_frame, text="Clipboard History", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        ttk.Button(button_frame, text="Refresh", 
                  command=self.refresh_list).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Clear Unpinned", 
                  command=self.clear_unpinned).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Delete Selected", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        # Instructions label
        instructions = ttk.Label(parent_frame, 
                                text="Double-click or press Enter to paste • Right-click for options",
                                foreground="gray")
        instructions.pack(pady=(0, 5))
        
        # Treeview frame with scrollbar
        tree_frame = ttk.Frame(parent_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style for Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        rowheight=25,
                        font=("Arial", 10))
        style.map("Treeview",
                  background=[('selected', '#cce5ff')],
                  foreground=[('selected', 'black')])

        # Create treeview with additional column for sensitive data
        columns = ("content", "pinned", "sensitive", "timestamp")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15, style="Treeview")
        self.tree.heading("content", text="Content")
        self.tree.heading("pinned", text="Pinned")
        self.tree.heading("sensitive", text="Sensitive")
        self.tree.heading("timestamp", text="Timestamp")
        
        self.tree.column("content", width=300, minwidth=200)
        self.tree.column("pinned", width=60, minwidth=50)
        self.tree.column("sensitive", width=70, minwidth=60)
        self.tree.column("timestamp", width=150, minwidth=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu (will be populated dynamically)
        self.context_menu = tk.Menu(self.root, tearoff=0)
    
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
            
            # Update context menu based on item type
            self._update_context_menu()
            
            self.context_menu.post(event.x_root, event.y_root)
    
    def _update_context_menu(self):
        """Update context menu options based on selected item."""
        item_id = self.get_selected_item_id()
        if not item_id:
            return
        
        # Get item details
        items = self.db.get_all_items()
        current_item = next((item for item in items if item[0] == item_id), None)
        if not current_item:
            return
        
        is_sensitive = current_item[3]  # is_sensitive column
        
        # Clear the menu
        self.context_menu.delete(0, tk.END)
        
        # Add basic options
        self.context_menu.add_command(label="Paste", command=self.paste_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Toggle Pin", command=self.toggle_pin_selected)
        
        # Add sensitive options
        if is_sensitive:
            self.context_menu.add_command(label="Remove Sensitive", command=self.toggle_sensitive_selected)
            self.context_menu.add_command(label="Edit Alias", command=self.edit_alias_selected)
        else:
            self.context_menu.add_command(label="Mark as Sensitive", command=self.toggle_sensitive_selected)
        
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
    
    def show_window(self):
        """Show the clipboard manager window and bring it to front."""
        if not self.root:
            self.create_window()
        
        # Always show clipboard tab first (index 0)
        if self.notebook:
            self.notebook.select(0)
        
        self.refresh_list()
        
        # Make sure window is visible and comes to front
        self.root.deiconify()  # Show window if minimized
        self.root.wm_state('normal')  # Ensure window is in normal state
        self.root.lift()  # Bring window to top of stacking order
        self.root.attributes('-topmost', True)  # Temporarily make it topmost
        self.root.attributes('-topmost', False)  # Remove topmost so user can interact normally
        self.root.focus_force()  # Force focus to this window
        self.root.grab_set()  # Make this window modal temporarily
        self.root.grab_release()  # Release modal state immediately
        
        # Ensure window is centered and visible on screen
        self._center_window()
        
        self.is_visible = True
        
        # Focus on the treeview
        if self.tree:
            self.tree.focus_set()
            
            # Select the first item if available
            items = self.tree.get_children()
            if items:
                self.tree.selection_set(items[0])
    
    def _center_window(self):
        """Center the window on the screen."""
        if not self.root:
            return
            
        # Update window to get accurate dimensions
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        
        # Calculate position for center
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        
        # Ensure window is not positioned off-screen
        pos_x = max(0, pos_x)
        pos_y = max(0, pos_y)
        
        # Set window position
        self.root.geometry(f"+{pos_x}+{pos_y}")
    
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
        for item_id, content, is_pinned, is_sensitive, alias, timestamp in items:
            # Use alias for display if item is sensitive and has an alias
            if is_sensitive and alias:
                display_content = alias
            else:
                # Truncate content for display
                display_content = content.replace('\n', ' ').replace('\r', '')
                if len(display_content) > 80:
                    display_content = display_content[:77] + "..."
            
            pinned_text = "📌" if is_pinned else ""
            sensitive_text = "🔒" if is_sensitive else ""
            
            # Format timestamp
            formatted_time = timestamp.split('.')[0] if '.' in timestamp else timestamp
            
            # Insert item with ID as tag
            item_ref = self.tree.insert("", tk.END, 
                                      values=(display_content, pinned_text, sensitive_text, formatted_time),
                                      tags=(str(item_id),))
            
            # Apply special styling for sensitive items
            if is_sensitive:
                self.tree.set(item_ref, "content", f"🔒 {display_content}")
                # Tag sensitive items for different coloring
                self.tree.item(item_ref, tags=(str(item_id), "sensitive"))
            elif is_pinned:
                self.tree.set(item_ref, "content", f"📌 {display_content}")
                self.tree.item(item_ref, tags=(str(item_id), "pinned"))
        
        # Configure tag colors
        self.tree.tag_configure("sensitive", background="#ffe6e6")  # Light red background
        self.tree.tag_configure("pinned", background="#e6f3ff")     # Light blue background
    
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
    
    def toggle_sensitive_selected(self):
        """Toggle sensitive status of the selected item."""
        item_id = self.get_selected_item_id()
        if not item_id:
            return
        
        # Check current sensitive status
        items = self.db.get_all_items()
        current_item = next((item for item in items if item[0] == item_id), None)
        if not current_item:
            return
        
        is_currently_sensitive = current_item[3]  # is_sensitive column
        
        if not is_currently_sensitive:
            # Making item sensitive - ask for alias
            alias = simpledialog.askstring(
                "Sensitive Data Alias",
                "Enter an alias for this sensitive data:",
                initialvalue="*** Sensitive Data ***"
            )
            
            if alias is not None:  # User didn't cancel
                if self.db.toggle_sensitive(item_id, alias):
                    self.refresh_list()
        else:
            # Removing sensitive status
            if self.db.toggle_sensitive(item_id):
                self.refresh_list()
    
    def edit_alias_selected(self):
        """Edit the alias of a sensitive item."""
        item_id = self.get_selected_item_id()
        if not item_id:
            return
        
        # Check if item is sensitive
        items = self.db.get_all_items()
        current_item = next((item for item in items if item[0] == item_id), None)
        if not current_item or not current_item[3]:  # is_sensitive column
            messagebox.showwarning("Not Sensitive", "This item is not marked as sensitive.")
            return
        
        current_alias = current_item[4] or "*** Sensitive Data ***"  # alias column
        
        new_alias = simpledialog.askstring(
            "Edit Alias",
            "Enter new alias for this sensitive data:",
            initialvalue=current_alias
        )
        
        if new_alias is not None and new_alias.strip():  # User didn't cancel and provided text
            if self.db.update_alias(item_id, new_alias.strip()):
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
