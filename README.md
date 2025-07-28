# Pastey - Local Clipboard Manager

A Windows application that monitors and manages clipboard history with enhanced security features.

## Features

### Core Functionality
- 📋 **Continuous clipboard monitoring** - Automatically captures all text copied to clipboard
- 💾 **SQLite database storage** - Persistent history across sessions
- ⚡ **Global hotkeys** - Quick access without switching windows
- 📌 **Pin important items** - Keep frequently used content at the top
- 🔄 **Smart duplicate prevention** - Avoids storing consecutive identical copies
- 🧹 **Automatic cleanup** - Maintains up to 100 recent items (pinned items never deleted)

### Security Features 🔒
- **Sensitive data hiding** - Mark passwords, API keys, and other sensitive content
- **Custom aliases** - Replace sensitive content with meaningful labels
- **Visual indicators** - Clear distinction between regular, pinned, and sensitive items
- **Secure display** - Sensitive content only shows when pasted, not in the interface

## Requirements

- Windows 10/11
- Python 3.7+
- Administrator privileges (recommended for global hotkeys)

## Installation

1. **Clone or download** this repository to your local machine

2. **Create a virtual environment** (optional but recommended):
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

Run the main application:
```powershell
python pastey.py
```

Or use the batch file:
```powershell
run_pastey.bat
```

**Important**: For global hotkeys to work properly, you may need to run the command prompt or PowerShell as Administrator.

### Basic Operations

1. **Copy text** anywhere in Windows - it will automatically be captured
2. **Press `Ctrl+Shift+Z`** to open the clipboard history window
3. **Select and paste**:
   - Double-click any item to paste it
   - Use arrow keys + Enter to select and paste
   - Right-click for context menu options

### Sensitive Data Management 🔒

#### Marking Content as Sensitive
1. Right-click on any clipboard item
2. Select "Mark as Sensitive"
3. Enter a meaningful alias (e.g., "Gmail Password", "API Key", "SSH Key")
4. The original content is hidden and replaced with your alias

#### Using Sensitive Content
- **In the interface**: Only the alias is displayed (e.g., "🔒 Gmail Password")
- **When pasting**: The actual sensitive content is pasted, not the alias
- **Visual indicators**: Sensitive items have a red background and lock icon

#### Managing Sensitive Content
- **Edit alias**: Right-click → "Edit Alias"
- **Remove sensitivity**: Right-click → "Remove Sensitive"
- **Persistence**: Sensitive items and aliases are saved across app restarts

### Interface Features

#### Visual Indicators
- **📌** - Pinned items (blue background)
- **🔒** - Sensitive items (red background)
- **Regular** - Normal clipboard content

#### Available Actions
- **📌 Pin Items**: Right-click → "Toggle Pin" or press Space to pin/unpin items
- **🔒 Mark as Sensitive**: Right-click → "Mark as Sensitive" to hide sensitive content
- **✏️ Edit Alias**: Right-click → "Edit Alias" to change sensitive content labels
- **🗑️ Delete Items**: Select item → press Delete key or use context menu
- **🧹 Clear Unpinned**: Button to remove all unpinned items at once
- **🔄 Refresh**: Button to refresh the list (happens automatically)

### Keyboard Shortcuts

#### Global Shortcuts
- `Ctrl+Shift+Z` - Open/close clipboard manager
- `Ctrl+Shift+Q` - Exit application

#### Within the Interface
- `Enter` - Paste selected item
- `Space` - Toggle pin/unpin selected item
- `Delete` - Delete selected item
- `Escape` - Close window
- `↑/↓` - Navigate through items

## File Structure

```
pastey/
├── pastey.py              # Main application file
├── database.py            # SQLite database operations
├── clipboard_monitor.py   # Clipboard monitoring functionality
├── gui.py                 # Tkinter GUI interface
├── requirements.txt       # Python dependencies
├── clipboard_history.db   # SQLite database (created automatically)
└── README.md             # This file
```

## Security & Privacy

### Data Protection
- 🔒 **100% Local**: No data is sent to the cloud or external servers
- 💾 **Local Storage**: All clipboard history stored in local SQLite database
- 🚫 **No Network Access**: Application works completely offline
- 🧹 **Automatic Cleanup**: Old items are automatically removed (except pinned items)
- 🔐 **Sensitive Content Protection**: Original sensitive data is hidden in the interface
- 📝 **Database Exclusion**: `.gitignore` prevents accidental sharing of clipboard history

### Best Practices for Sensitive Data
1. **Mark sensitive content immediately** after copying passwords, API keys, etc.
2. **Use descriptive aliases** like "Work Email Password" instead of generic names
3. **Regular cleanup** - Use "Clear Unpinned" to remove old content
4. **Pin frequently used sensitive items** to keep them accessible

## Use Cases

### For Developers
```
🔒 GitHub Token        (alias for: ghp_xxxxxxxxxxxxxxxxxxxx)
🔒 Database Password   (alias for: MySecretDbPass123!)
📌 Debug Commands      (pinned: console.log, breakpoints)
```

### For System Administrators
```
🔒 Root Password       (alias for: complex-root-password)
🔒 Service Account     (alias for: service-account-key)
📌 Common Commands     (pinned: systemctl, docker commands)
```

### For General Users
```
🔒 Email Password      (alias for: personal email password)
🔒 WiFi Password       (alias for: home/office WiFi password)
📌 Addresses          (pinned: frequently used addresses)
```

## Troubleshooting

### Global Hotkeys Not Working
- Run PowerShell/Command Prompt as Administrator
- Some antivirus software may block global hotkey registration

### Application Won't Start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using Python 3.7 or later
- Verify you're running on Windows

### Clipboard Not Being Monitored
- Make sure no other clipboard managers are running
- Check that the application has permission to access clipboard
- Try restarting the application

### Performance Issues
- The application is designed to be lightweight
- Database automatically cleans up old items
- If issues persist, delete `clipboard_history.db` to reset

## Customization

You can modify these settings in the code:

- **Maximum items**: Change `max_unpinned` parameter in `database.py` (default: 100)
- **Monitoring interval**: Adjust `time.sleep()` in `clipboard_monitor.py` (default: 0.5s)
- **Window size**: Modify `geometry()` in `gui.py` (default: 600x400)
- **Hotkeys**: Change hotkey combinations in `pastey.py`

## Dependencies

- `pyperclip==1.9.0` - Clipboard access
- `keyboard==0.13.5` - Global hotkeys
- `pyautogui==0.9.54` - Automated pasting
- `tkinter` - GUI framework (included with Python)
- `sqlite3` - Database (included with Python)

## Database Schema

The application uses SQLite with the following structure:

```sql
CREATE TABLE clipboard_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,           -- Original clipboard content
    is_pinned BOOLEAN DEFAULT 0,     -- Pinned status
    is_sensitive BOOLEAN DEFAULT 0,  -- Sensitive data flag
    alias TEXT DEFAULT NULL,         -- Display alias for sensitive content
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## License

This project is open source and available under the MIT License.

## Version History

### v2.0.0 - Sensitive Data Support
- ✨ Added sensitive data hiding with custom aliases
- ✨ Enhanced right-click context menu with dynamic options
- ✨ Visual indicators for different content types (pinned, sensitive, regular)
- ✨ Secure display of sensitive content (only visible when pasted)
- 🔒 Improved security and privacy features
- 🎯 Changed global hotkey to Ctrl+Shift+Z (less conflicts)

### v1.0.0 - Initial Release
- ✅ Basic clipboard monitoring
- ✅ SQLite database storage
- ✅ Pin/unpin functionality
- ✅ Global hotkeys
- ✅ Tkinter GUI interface
- ✅ Clear unpinned items functionality

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve Pastey!
