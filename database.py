"""
Database module for clipboard manager.
Handles SQLite operations for storing clipboard history.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional


class ClipboardDB:
    def __init__(self, db_path: str = "clipboard_history.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the clipboard_items table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    is_pinned BOOLEAN DEFAULT 0,
                    is_sensitive BOOLEAN DEFAULT 0,
                    alias TEXT DEFAULT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add new columns to existing database if they don't exist
            try:
                cursor.execute("ALTER TABLE clipboard_items ADD COLUMN is_sensitive BOOLEAN DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE clipboard_items ADD COLUMN alias TEXT DEFAULT NULL")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            conn.commit()
    
    def add_item(self, content: str) -> bool:
        """
        Add a new clipboard item to the database.
        Returns True if item was added, False if it's a duplicate of the last item.
        """
        # Check if this is the same as the last item (avoid duplicates)
        if self.is_duplicate(content):
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clipboard_items (content, is_pinned, timestamp)
                VALUES (?, 0, ?)
            """, (content, datetime.now()))
            conn.commit()
        
        return True
    
    def is_duplicate(self, content: str) -> bool:
        """Check if the content is the same as the most recent item."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT content FROM clipboard_items 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            return result and result[0] == content
    
    def get_all_items(self) -> List[Tuple[int, str, bool, bool, str, str]]:
        """Get all clipboard items, with pinned items first."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, content, is_pinned, is_sensitive, alias, timestamp 
                FROM clipboard_items 
                ORDER BY is_pinned DESC, timestamp DESC
            """)
            return cursor.fetchall()
    
    def toggle_pin(self, item_id: int) -> bool:
        """Toggle the pinned status of an item."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clipboard_items 
                SET is_pinned = NOT is_pinned 
                WHERE id = ?
            """, (item_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def toggle_sensitive(self, item_id: int, alias: str = None) -> bool:
        """Toggle the sensitive status of an item and set alias if provided."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # First get current sensitive status
            cursor.execute("SELECT is_sensitive FROM clipboard_items WHERE id = ?", (item_id,))
            result = cursor.fetchone()
            if not result:
                return False
                
            current_sensitive = result[0]
            new_sensitive = not current_sensitive
            
            if new_sensitive and alias:
                # Setting as sensitive with alias
                cursor.execute("""
                    UPDATE clipboard_items 
                    SET is_sensitive = 1, alias = ?
                    WHERE id = ?
                """, (alias, item_id))
            elif new_sensitive:
                # Setting as sensitive without alias (use default)
                cursor.execute("""
                    UPDATE clipboard_items 
                    SET is_sensitive = 1, alias = '*** Sensitive Data ***'
                    WHERE id = ?
                """, (item_id,))
            else:
                # Removing sensitive status
                cursor.execute("""
                    UPDATE clipboard_items 
                    SET is_sensitive = 0, alias = NULL
                    WHERE id = ?
                """, (item_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def update_alias(self, item_id: int, alias: str) -> bool:
        """Update the alias for a sensitive item."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clipboard_items 
                SET alias = ?
                WHERE id = ? AND is_sensitive = 1
            """, (alias, item_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a specific item from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM clipboard_items 
                WHERE id = ?
            """, (item_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def clear_unpinned_items(self) -> int:
        """Clear all unpinned items and return the number of items deleted."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM clipboard_items 
                WHERE is_pinned = 0
            """)
            conn.commit()
            return cursor.rowcount
    
    def cleanup_old_items(self, max_unpinned: int = 100):
        """Keep only the most recent max_unpinned non-pinned items."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Get IDs of items to keep (pinned + recent unpinned)
            cursor.execute("""
                SELECT id FROM clipboard_items 
                WHERE is_pinned = 1
                UNION
                SELECT id FROM (
                    SELECT id FROM clipboard_items 
                    WHERE is_pinned = 0
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
            """, (max_unpinned,))
            
            keep_ids = [str(row[0]) for row in cursor.fetchall()]
            
            if keep_ids:
                # Delete items not in the keep list
                cursor.execute(f"""
                    DELETE FROM clipboard_items 
                    WHERE id NOT IN ({','.join(['?'] * len(keep_ids))})
                """, keep_ids)
                conn.commit()
    
    def get_item_content(self, item_id: int) -> Optional[str]:
        """Get the content of a specific item."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT content FROM clipboard_items 
                WHERE id = ?
            """, (item_id,))
            result = cursor.fetchone()
            return result[0] if result else None


class BookmarksDB:
    def __init__(self, db_path: str = "clipboard_history.db"):
        """Initialize database connection and create bookmarks table if it doesn't exist."""
        self.db_path = db_path
        self.init_bookmarks_table()
    
    def init_bookmarks_table(self):
        """Create the bookmarks table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    url TEXT NOT NULL,
                    category TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def add_bookmark(self, title: str, description: str, url: str, category: str) -> bool:
        """Add a new bookmark to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO bookmarks (title, description, url, category, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (title, description, url, category, datetime.now()))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error adding bookmark: {e}")
            return False
    
    def get_all_bookmarks(self) -> List[Tuple[int, str, str, str, str, str]]:
        """Get all bookmarks ordered by category and then by title."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, url, category, timestamp 
                FROM bookmarks 
                ORDER BY category, title
            """)
            return cursor.fetchall()
    
    def get_bookmarks_by_category(self, category: str) -> List[Tuple[int, str, str, str, str, str]]:
        """Get bookmarks filtered by category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, url, category, timestamp 
                FROM bookmarks 
                WHERE category = ?
                ORDER BY title
            """, (category,))
            return cursor.fetchall()
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT category 
                FROM bookmarks 
                ORDER BY category
            """)
            return [row[0] for row in cursor.fetchall()]
    
    def update_bookmark(self, bookmark_id: int, title: str, description: str, url: str, category: str) -> bool:
        """Update a bookmark."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE bookmarks 
                    SET title = ?, description = ?, url = ?, category = ?
                    WHERE id = ?
                """, (title, description, url, category, bookmark_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating bookmark: {e}")
            return False
    
    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM bookmarks 
                    WHERE id = ?
                """, (bookmark_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting bookmark: {e}")
            return False
    
    def get_bookmark(self, bookmark_id: int) -> Optional[Tuple[int, str, str, str, str, str]]:
        """Get a specific bookmark by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, url, category, timestamp 
                FROM bookmarks 
                WHERE id = ?
            """, (bookmark_id,))
            return cursor.fetchone()
