"""
Backup module for clipboard manager.
Handles automatic database backups with configurable settings.
"""

import os
import shutil
import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path
import logging


class BackupManager:
    def __init__(self, db_path: str, backup_path: str, max_backups: int = 10):
        """
        Initialize backup manager.
        
        Args:
            db_path: Path to the database file to backup
            backup_path: Directory where backups will be stored
            max_backups: Maximum number of backup files to keep
        """
        self.db_path = db_path
        self.backup_path = Path(backup_path)
        self.max_backups = max_backups
        
        # Create backup directory if it doesn't exist
        self._ensure_backup_directory()
    
    def _ensure_backup_directory(self):
        """Create backup directory if it doesn't exist."""
        try:
            self.backup_path.mkdir(parents=True, exist_ok=True)
            print(f"Backup directory ready: {self.backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup directory {self.backup_path}: {e}")
    
    def create_backup(self) -> Optional[str]:
        """
        Create a backup of the database.
        
        Returns:
            Path to the created backup file, or None if backup failed
        """
        if not os.path.exists(self.db_path):
            print(f"Database file not found: {self.db_path}")
            return None
        
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"pastey_backup_{timestamp}.db"
            backup_file_path = self.backup_path / backup_filename
            
            # Ensure database is not locked by closing any connections
            self._ensure_db_closed()
            
            # Copy the database file
            shutil.copy2(self.db_path, backup_file_path)
            
            print(f"✅ Backup created successfully: {backup_file_path}")
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return str(backup_file_path)
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return None
    
    def _ensure_db_closed(self):
        """Ensure database connections are properly closed."""
        try:
            # Create a temporary connection and close it to ensure DB is accessible
            conn = sqlite3.connect(self.db_path)
            conn.close()
        except Exception as e:
            print(f"Warning: Database access check failed: {e}")
    
    def _cleanup_old_backups(self):
        """Remove old backup files, keeping only the most recent ones."""
        try:
            # Get all backup files
            backup_files = list(self.backup_path.glob("pastey_backup_*.db"))
            
            if len(backup_files) <= self.max_backups:
                return
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove excess files
            files_to_remove = backup_files[self.max_backups:]
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    print(f"🗑️  Removed old backup: {file_path.name}")
                except Exception as e:
                    print(f"Warning: Could not remove old backup {file_path}: {e}")
                    
        except Exception as e:
            print(f"Warning: Backup cleanup failed: {e}")
    
    def list_backups(self) -> list:
        """
        List all available backup files.
        
        Returns:
            List of backup file paths sorted by date (newest first)
        """
        try:
            backup_files = list(self.backup_path.glob("pastey_backup_*.db"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return backup_files
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    def restore_backup(self, backup_file: str) -> bool:
        """
        Restore database from a backup file.
        
        Args:
            backup_file: Path to the backup file to restore
            
        Returns:
            True if restore was successful, False otherwise
        """
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                print(f"Backup file not found: {backup_file}")
                return False
            
            # Create backup of current database before restoring
            current_backup = f"{self.db_path}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.db_path, current_backup)
            print(f"Current database backed up to: {current_backup}")
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            print(f"✅ Database restored from: {backup_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore backup: {e}")
            return False


def create_backup_if_enabled(db_path: str, backup_path: str, max_backups: int = 10) -> bool:
    """
    Create a backup if backup is enabled and path is configured.
    
    Args:
        db_path: Path to the database file
        backup_path: Backup directory path
        max_backups: Maximum number of backups to keep
        
    Returns:
        True if backup was created or skipped, False if failed
    """
    if not backup_path or backup_path.strip() == "":
        print("ℹ️  Backup disabled: No backup path configured")
        return True
    
    try:
        backup_manager = BackupManager(db_path, backup_path, max_backups)
        result = backup_manager.create_backup()
        return result is not None
    except Exception as e:
        print(f"❌ Backup process failed: {e}")
        return False
