"""
Bookmarks GUI module for clipboard manager.
Provides the interface for viewing and managing URL bookmarks.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
from typing import Callable, List, Tuple, Optional
from database import BookmarksDB


class BookmarkDialog:
    """Dialog for adding/editing bookmarks."""
    
    def __init__(self, parent, title="Add Bookmark", bookmark=None):
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x300")
        self.top.transient(parent)
        self.top.grab_set()
        
        # Center the dialog
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.top.winfo_screenheight() // 2) - (300 // 2)
        self.top.geometry(f"400x300+{x}+{y}")
        
        self._create_widgets(bookmark)
        
        # Focus on title entry
        self.title_entry.focus_set()
    
    def _create_widgets(self, bookmark):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.top)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(main_frame, text="Title:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.title_entry = ttk.Entry(main_frame, width=40)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=(0, 5))
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky="nw", pady=(0, 5))
        self.description_text = tk.Text(main_frame, width=40, height=4)
        self.description_text.grid(row=1, column=1, sticky="ew", pady=(0, 5))
        
        # URL
        ttk.Label(main_frame, text="URL:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.url_entry = ttk.Entry(main_frame, width=40)
        self.url_entry.grid(row=2, column=1, sticky="ew", pady=(0, 5))
        
        # Category
        ttk.Label(main_frame, text="Category:").grid(row=3, column=0, sticky="w", pady=(0, 5))
        self.category_entry = ttk.Entry(main_frame, width=40)
        self.category_entry.grid(row=3, column=1, sticky="ew", pady=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Fill with existing data if editing
        if bookmark:
            self.title_entry.insert(0, bookmark[1])  # title
            self.description_text.insert("1.0", bookmark[2])  # description
            self.url_entry.insert(0, bookmark[3])  # url
            self.category_entry.insert(0, bookmark[4])  # category
        
        # Bind Enter key to save
        self.top.bind("<Return>", lambda e: self._save())
        self.top.bind("<Escape>", lambda e: self._cancel())
    
    def _save(self):
        """Save the bookmark data."""
        title = self.title_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        url = self.url_entry.get().strip()
        category = self.category_entry.get().strip()
        
        if not title:
            messagebox.showerror("Error", "Title is required!")
            return
        
        if not url:
            messagebox.showerror("Error", "URL is required!")
            return
        
        if not category:
            messagebox.showerror("Error", "Category is required!")
            return
        
        self.result = (title, description, url, category)
        self.top.destroy()
    
    def _cancel(self):
        """Cancel the dialog."""
        self.result = None
        self.top.destroy()


class BookmarksGUI:
    def __init__(self, db: BookmarksDB):
        """
        Initialize the bookmarks manager GUI.
        
        Args:
            db: BookmarksDB instance for bookmark operations
        """
        self.db = db
        self.parent_frame = None
        self.tree = None
        self.category_filter = None
        self.current_category = "All"
        
    def create_widgets(self, parent_frame):
        """Create the bookmarks tab widgets."""
        self.parent_frame = parent_frame
        
        # Main frame
        main_frame = ttk.Frame(parent_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title label
        title_label = ttk.Label(main_frame, text="URL Bookmarks", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Top controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Button frame (left side)
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Add Bookmark", 
                  command=self.add_bookmark).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Edit Selected", 
                  command=self.edit_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Delete Selected", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Refresh", 
                  command=self.refresh_list).pack(side=tk.LEFT, padx=(0, 5))
        
        # Category filter frame (right side)
        filter_frame = ttk.Frame(controls_frame)
        filter_frame.pack(side=tk.RIGHT)
        
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.category_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.category_filter.pack(side=tk.LEFT)
        self.category_filter.bind("<<ComboboxSelected>>", self._on_category_change)
        
        # Instructions label
        instructions = ttk.Label(main_frame, 
                                text="Double-click to open URL • Right-click for options",
                                foreground="gray")
        instructions.pack(pady=(0, 5))
        
        # Treeview frame with scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("title", "description", "url", "category")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("title", text="Title")
        self.tree.heading("description", text="Description")
        self.tree.heading("url", text="URL")
        self.tree.heading("category", text="Category")
        
        self.tree.column("title", width=150, minwidth=100)
        self.tree.column("description", width=200, minwidth=150)
        self.tree.column("url", width=250, minwidth=200)
        self.tree.column("category", width=100, minwidth=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu
        self.context_menu = tk.Menu(parent_frame, tearoff=0)
        self.context_menu.add_command(label="Open URL", command=self.open_selected_url)
        self.context_menu.add_command(label="Copy URL", command=self.copy_selected_url)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Edit", command=self.edit_selected)
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        
        self._setup_bindings()
        self.refresh_list()
    
    def _setup_bindings(self):
        """Setup event bindings."""
        if not self.tree:
            return
            
        # Double-click to open URL
        self.tree.bind("<Double-1>", lambda e: self.open_selected_url())
        
        # Enter key to open URL
        self.tree.bind("<Return>", lambda e: self.open_selected_url())
        
        # Right-click for context menu
        self.tree.bind("<Button-3>", self._show_context_menu)
        
        # Delete key to delete item
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
    
    def _show_context_menu(self, event):
        """Show context menu at cursor position."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _on_category_change(self, event=None):
        """Handle category filter change."""
        self.current_category = self.category_filter.get()
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh the bookmarks list."""
        if not self.tree:
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Update category filter
        categories = ["All"] + self.db.get_categories()
        self.category_filter['values'] = categories
        
        if self.current_category not in categories:
            self.current_category = "All"
        
        self.category_filter.set(self.current_category)
        
        # Get bookmarks from database
        if self.current_category == "All":
            bookmarks = self.db.get_all_bookmarks()
        else:
            bookmarks = self.db.get_bookmarks_by_category(self.current_category)
        
        # Add bookmarks to treeview
        for bookmark_id, title, description, url, category, timestamp in bookmarks:
            # Truncate long text for display
            display_title = title[:30] + "..." if len(title) > 30 else title
            display_desc = description.replace('\n', ' ')[:50] + "..." if len(description) > 50 else description.replace('\n', ' ')
            display_url = url[:60] + "..." if len(url) > 60 else url
            
            self.tree.insert("", tk.END, 
                           values=(display_title, display_desc, display_url, category),
                           tags=(str(bookmark_id),))
    
    def get_selected_bookmark_id(self) -> Optional[int]:
        """Get the ID of the currently selected bookmark."""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        tags = self.tree.item(item, "tags")
        return int(tags[0]) if tags else None
    
    def add_bookmark(self):
        """Add a new bookmark."""
        if not self.parent_frame:
            return
            
        dialog = BookmarkDialog(self.parent_frame.winfo_toplevel(), "Add Bookmark")
        self.parent_frame.wait_window(dialog.top)
        
        if dialog.result:
            title, description, url, category = dialog.result
            if self.db.add_bookmark(title, description, url, category):
                self.refresh_list()
                messagebox.showinfo("Success", "Bookmark added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add bookmark!")
    
    def edit_selected(self):
        """Edit the selected bookmark."""
        bookmark_id = self.get_selected_bookmark_id()
        if not bookmark_id:
            messagebox.showwarning("No Selection", "Please select a bookmark to edit.")
            return
        
        bookmark = self.db.get_bookmark(bookmark_id)
        if not bookmark:
            messagebox.showerror("Error", "Bookmark not found!")
            return
        
        dialog = BookmarkDialog(self.parent_frame.winfo_toplevel(), "Edit Bookmark", bookmark)
        self.parent_frame.wait_window(dialog.top)
        
        if dialog.result:
            title, description, url, category = dialog.result
            if self.db.update_bookmark(bookmark_id, title, description, url, category):
                self.refresh_list()
                messagebox.showinfo("Success", "Bookmark updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update bookmark!")
    
    def delete_selected(self):
        """Delete the selected bookmark."""
        bookmark_id = self.get_selected_bookmark_id()
        if not bookmark_id:
            messagebox.showwarning("No Selection", "Please select a bookmark to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this bookmark?"):
            if self.db.delete_bookmark(bookmark_id):
                self.refresh_list()
                messagebox.showinfo("Success", "Bookmark deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete bookmark!")
    
    def open_selected_url(self):
        """Open the selected bookmark's URL in the default browser."""
        bookmark_id = self.get_selected_bookmark_id()
        if not bookmark_id:
            return
        
        bookmark = self.db.get_bookmark(bookmark_id)
        if bookmark:
            url = bookmark[3]  # URL column
            try:
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open URL: {e}")
    
    def copy_selected_url(self):
        """Copy the selected bookmark's URL to clipboard."""
        bookmark_id = self.get_selected_bookmark_id()
        if not bookmark_id:
            return
        
        bookmark = self.db.get_bookmark(bookmark_id)
        if bookmark:
            url = bookmark[3]  # URL column
            try:
                # Use pyperclip which is already a dependency
                import pyperclip
                pyperclip.copy(url)
                messagebox.showinfo("Success", "URL copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy URL: {e}")
