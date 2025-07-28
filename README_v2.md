# Pastey - Local Clipboard Manager

A Windows application that monitors and manages clipboard history with enhanced security features.

## Features

### Core Functionality
- **Continuous clipboard monitoring** - Automatically captures clipboard changes
- **SQLite database storage** - Persistent history across sessions
- **Global hotkeys** - Quick access without switching windows
- **Pin important items** - Keep frequently used content at the top

### Security Features ✨ *NEW*
- **Sensitive data hiding** - Mark passwords, API keys, and other sensitive content
- **Custom aliases** - Replace sensitive content with meaningful labels
- **Visual indicators** - Clear distinction between regular, pinned, and sensitive items
- **Secure display** - Sensitive content only shows when pasted, not in the interface

### Hotkeys
- **Ctrl+Shift+Z** - Open clipboard manager
- **Ctrl+Shift+Q** - Exit application

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/silasmendes/pastey.git
   cd pastey
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python pastey.py
   ```

   Or use the batch file:
   ```bash
   run_pastey.bat
   ```

## Usage

### Basic Operations
1. **Start the application** - Run `python pastey.py`
2. **Copy text** - Use Ctrl+C as normal; content is automatically captured
3. **Open clipboard history** - Press `Ctrl+Shift+Z`
4. **Paste content** - Double-click an item or press Enter
5. **Pin important items** - Right-click and select "Toggle Pin"

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

### Interface Guide

#### Visual Indicators
- **📌** - Pinned items (blue background)
- **🔒** - Sensitive items (red background)
- **Regular** - Normal clipboard content

#### Keyboard Shortcuts
- **Double-click** or **Enter** - Paste selected item
- **Space** - Toggle pin status
- **Delete** - Remove selected item
- **Escape** - Close clipboard manager

#### Right-click Menu
- **Paste** - Paste the selected content
- **Toggle Pin** - Pin/unpin the item
- **Mark as Sensitive** / **Remove Sensitive** - Toggle sensitive status
- **Edit Alias** - Change the alias for sensitive items
- **Delete** - Remove the item permanently

## Security & Privacy

### Data Protection
- **Local storage only** - All data stays on your computer
- **No network access** - No data is transmitted anywhere
- **Sensitive content encryption** - Original sensitive data is hidden in the interface
- **Database exclusion** - `.gitignore` prevents accidental sharing of clipboard history

### Best Practices
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

## Requirements

- **Python 3.7+**
- **Windows OS** (uses Windows-specific clipboard APIs)
- **Administrator privileges** (recommended for global hotkeys)

## Dependencies

```
pyperclip==1.9.0    # Clipboard access
keyboard==0.13.5    # Global hotkeys
pyautogui==0.9.54   # Automated pasting
```

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

## Troubleshooting

### Common Issues

1. **Global hotkeys not working**
   - Run as Administrator
   - Check for conflicting hotkey assignments

2. **Clipboard monitoring stops**
   - Restart the application
   - Check if other clipboard managers are running

3. **Database errors**
   - Delete the `.db` files to reset (loses history)
   - Check file permissions

### Performance Tips

- **Regular cleanup** - Use "Clear Unpinned" to maintain performance
- **Limit clipboard size** - Very large clipboard content may slow down the interface
- **Close other clipboard managers** - Avoid conflicts with other tools

## Development

### Project Structure
```
pastey/
├── pastey.py              # Main application
├── clipboard_monitor.py   # Clipboard monitoring
├── database.py           # SQLite operations
├── gui.py               # Tkinter interface
├── requirements.txt     # Dependencies
├── README.md           # This file
└── .gitignore         # Git exclusions
```

### Running Tests
```bash
python test_pastey.py      # Basic functionality tests
python test_sensitive.py   # Sensitive data feature tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute.

## Version History

### v2.0.0 - Sensitive Data Support
- ✨ Added sensitive data hiding with custom aliases
- ✨ Enhanced right-click context menu
- ✨ Visual indicators for different content types
- ✨ Secure display of sensitive content
- 🔒 Improved security and privacy features

### v1.0.0 - Initial Release
- ✅ Basic clipboard monitoring
- ✅ SQLite database storage
- ✅ Pin/unpin functionality
- ✅ Global hotkeys
- ✅ Tkinter GUI interface
