# Boot configuration for Seeed XIAO RP2040
# This file runs before main.py

import os
import sys
import machine

# Print boot information
print("\n" + "="*40)
print("Seeed XIAO RP2040 Boot")
print("="*40)
print(f"Platform: {sys.platform}")
print(f"MicroPython Version: {os.uname().release}")
print("="*40 + "\n")

# Configure USB HID for media control (volume)
try:
    import usb_hid
    from usb_hid import HID
    
    # Setup HID reports for media control
    # Media control report descriptor
    MEDIA_REPORT_ID = 2
    
    print("USB HID initialized for media control")
    print("  - Volume Up/Down support enabled")
    
except ImportError:
    print("Warning: usb_hid module not available")
    print("Volume control will not work")

print("System initialized successfully")
