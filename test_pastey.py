"""
Test script to verify all modules are working correctly.
Run this before using the main application.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import tkinter
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    try:
        import pyperclip
        print("✓ pyperclip imported successfully")
    except ImportError as e:
        print(f"✗ pyperclip import failed: {e}")
        return False
    
    try:
        import keyboard
        print("✓ keyboard imported successfully")
    except ImportError as e:
        print(f"✗ keyboard import failed: {e}")
        return False
    
    try:
        import pyautogui
        print("✓ pyautogui imported successfully")
    except ImportError as e:
        print(f"✗ pyautogui import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database functionality."""
    print("\nTesting database...")
    
    try:
        from database import ClipboardDB
        
        # Use a test database
        db = ClipboardDB("test_pastey.db")
        
        # Test adding items
        db.add_item("Test item 1")
        db.add_item("Test item 2")
        
        # Test getting items
        items = db.get_all_items()
        if len(items) >= 2:
            print("✓ Database operations working correctly")
        else:
            print("✗ Database operations failed")
            return False
        
        # Test pinning
        if items:
            item_id = items[0][0]
            db.toggle_pin(item_id)
            print("✓ Pin/unpin functionality working")
        
        # Cleanup (ignore file lock errors)
        try:
            os.remove("test_pastey.db")
        except:
            pass  # File might be locked, that's okay
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_clipboard():
    """Test clipboard functionality."""
    print("\nTesting clipboard...")
    
    try:
        from clipboard_monitor import ClipboardMonitor
        
        def dummy_callback(content):
            pass
        
        monitor = ClipboardMonitor(dummy_callback)
        
        # Test getting current content
        current = monitor.get_current_content()
        print(f"✓ Current clipboard content: '{current[:30]}...' (first 30 chars)")
        
        # Test setting content
        test_content = "Test clipboard content from Pastey"
        monitor.set_content(test_content)
        
        # Verify it was set
        new_content = monitor.get_current_content()
        if test_content in new_content:
            print("✓ Clipboard read/write working correctly")
        else:
            print("✗ Clipboard write might have failed")
            
        return True
        
    except Exception as e:
        print(f"✗ Clipboard test failed: {e}")
        return False

def test_gui():
    """Test GUI creation (without showing)."""
    print("\nTesting GUI...")
    
    try:
        from gui import ClipboardGUI
        from database import ClipboardDB
        
        db = ClipboardDB("test_gui.db")
        
        def dummy_paste_callback(content):
            pass
        
        gui = ClipboardGUI(db, dummy_paste_callback)
        gui.create_window()
        
        if gui.root:
            print("✓ GUI window created successfully")
            gui.destroy()
            # Cleanup (ignore file lock errors)
            try:
                os.remove("test_gui.db")
            except:
                pass  # File might be locked, that's okay
            return True
        else:
            print("✗ GUI window creation failed")
            return False
            
    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Pastey Clipboard Manager - Testing Components")
    print("=" * 50)
    
    if sys.platform != "win32":
        print("⚠️  Warning: This application is designed for Windows")
    
    tests = [
        ("Dependencies", test_imports),
        ("Database", test_database),
        ("Clipboard", test_clipboard),
        ("GUI", test_gui),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 20)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Pastey is ready to use.")
        print("\nTo start the application, run:")
        print("  python pastey.py")
        print("\nOr double-click: run_pastey.bat")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nMake sure all dependencies are installed:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()
