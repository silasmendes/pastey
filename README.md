# Pastey

A simple Windows clipboard manager that saves your clipboard history locally.

## What it does

- Monitors your clipboard and saves everything you copy
- Shows your clipboard history in a simple window
- Lets you click on old items to paste them again
- Stores everything in a local SQLite database

## How to use

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run it:

   ```bash
   python pastey.py
   ```

3. Press `Ctrl+Shift+Z` to open the clipboard history window

That's it. Copy stuff, press the hotkey, click on what you want to paste.

## Files

- `pastey.py` - Main application
- `clipboard_monitor.py` - Watches clipboard for changes
- `database.py` - SQLite database stuff
- `gui.py` - The window interface
- `backup_manager.py` - Backs up your clipboard database
- `requirements.txt` - Python packages needed

## Requirements

- Windows
- Python 3.7+
- Run as admin for global hotkeys to work properly
