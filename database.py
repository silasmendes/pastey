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
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
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
        
        # Clean up old items (keep only 100 non-pinned items)
        self.cleanup_old_items()
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
    
    def get_all_items(self) -> List[Tuple[int, str, bool, str]]:
        """Get all clipboard items, with pinned items first."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, content, is_pinned, timestamp 
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
