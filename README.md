# Pastey - Local Clipboard Manager

A local Windows clipboard manager that monitors and stores your clipboard history with a simple, intuitive interface.

## Features

- 📋 **Continuous Clipboard Monitoring**: Automatically captures all text copied to clipboard
- 💾 **Local SQLite Storage**: All data stored locally in a secure database
- ⚡ **Global Hotkey Access**: Press `Ctrl+Shift+V` to instantly open clipboard history
- 📌 **Pin Important Items**: Keep frequently used text permanently in your history
- 🔄 **Smart Duplicate Prevention**: Avoids storing consecutive identical copies
- 🧹 **Automatic Cleanup**: Maintains up to 100 recent items (pinned items never deleted)
- 🎯 **Quick Paste**: Double-click or press Enter to paste any item

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

**Important**: For global hotkeys to work properly, you may need to run the command prompt or PowerShell as Administrator.

### Using the Clipboard Manager

1. **Copy text** anywhere in Windows - it will automatically be captured
2. **Press `Ctrl+Shift+V`** to open the clipboard history window
3. **Select and paste**:
   - Double-click any item to paste it
   - Use arrow keys + Enter to select and paste
   - Right-click for context menu options

### Interface Features

- **📌 Pin Items**: Right-click → "Toggle Pin" or press Space to pin/unpin items
- **🗑️ Delete Items**: Select item → press Delete key or use context menu
- **🧹 Clear Unpinned**: Button to remove all unpinned items at once
- **🔄 Refresh**: Button to refresh the list (happens automatically)

### Keyboard Shortcuts

#### Global Shortcuts
- `Ctrl+Shift+V` - Open/close clipboard manager
- `Ctrl+C` - Exit application

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

- 🔒 **100% Local**: No data is sent to the cloud or external servers
- 💾 **Local Storage**: All clipboard history stored in local SQLite database
- 🚫 **No Network Access**: Application works completely offline
- 🧹 **Automatic Cleanup**: Old items are automatically removed (except pinned items)

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

- `pyperclip` - Clipboard access
- `keyboard` - Global hotkeys
- `pyautogui` - Automated pasting
- `tkinter` - GUI framework (included with Python)
- `sqlite3` - Database (included with Python)

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve Pastey!
