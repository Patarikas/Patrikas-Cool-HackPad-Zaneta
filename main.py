import time
from machine import Pin
from pins import SWITCH_PINS, DEBOUNCE_TIME
from encoder import EC11Encoder
from display import Display
from hid_control import init_media_control, get_media_control


class SwitchHandler:
    """Handler for MX-style switches with debouncing"""
    
    def __init__(self):
        self.pins = {}
        self.last_press_time = {}
        self.press_callbacks = {}
        self.states = {}
        
        # Initialize all switch pins
        for name, pin_num in SWITCH_PINS.items():
            self.pins[name] = Pin(pin_num, Pin.IN, Pin.PULL_UP)
            self.last_press_time[name] = 0
            self.states[name] = False
            self.pins[name].irq(
                trigger=Pin.IRQ_FALLING,
                handler=lambda pin, name=name: self._handle_switch_press(name, pin)
            )
    
    def _handle_switch_press(self, switch_name, pin):
        """Handle switch press with debouncing"""
        current_time = time.ticks_ms()
        
        # Debounce check
        if current_time - self.last_press_time[switch_name] < DEBOUNCE_TIME:
            return
        
        self.last_press_time[switch_name] = current_time
        self.states[switch_name] = True
        
        # Call registered callback if exists
        if switch_name in self.press_callbacks:
            self.press_callbacks[switch_name](switch_name)
    
    def register_callback(self, switch_name, callback):
        """Register a callback function for a switch
        
        Args:
            switch_name: Name of the switch (switch_1 through switch_6)
            callback: Function to call when switch is pressed, receives switch_name as argument
        """
        if switch_name in self.pins:
            self.press_callbacks[switch_name] = callback
    
    def get_active_switches(self):
        """Get list of currently active switches"""
        return [name for name, state in self.states.items() if state]
    
    def reset_states(self):
        """Reset all switch states"""
        for name in self.states:
            self.states[name] = False


# Global instances
switch_handler = None
encoder = None
display = None
media_control = None
encoder_value = 0
last_display_update = 0


def init_display():
    """Initialize the display"""
    global display
    display = Display()
    display.show_welcome()
    time.sleep(2)


def init_switches(switch_callback=None):
    """Initialize all switches
    
    Args:
        switch_callback: Function to call on any switch press (receives switch_name)
    """
    global switch_handler
    switch_handler = SwitchHandler()
    
    if switch_callback:
        for switch_name in SWITCH_PINS.keys():
            switch_handler.register_callback(switch_name, switch_callback)


def init_encoder(rotate_callback=None, button_callback=None):
    """Initialize the rotary encoder
    
    Args:
        rotate_callback: Function called with rotation direction (1 or -1)
        button_callback: Function called when encoder button pressed
    """
    global encoder
    encoder = EC11Encoder(
        callback_rotate=rotate_callback,
        callback_button=button_callback
    )


def on_switch_press(switch_name):
    """Callback for switch press"""
    print(f"Switch pressed: {switch_name}")
    if display and display.initialized:
        display.show_key_press(switch_name)


def on_encoder_rotate(direction):
    """Callback for encoder rotation"""
    global encoder_value, media_control
    encoder_value += direction
    
    if media_control and media_control.enabled:
        if direction > 0:
            # Clockwise = Volume Up
            media_control.volume_up()
        else:
            # Counter-clockwise = Volume Down
            media_control.volume_down()
    
    print(f"Encoder: {encoder_value} (rotated {direction})")


def on_encoder_button():
    """Callback for encoder button press"""
    print("Encoder button pressed")
    global encoder_value
    encoder_value = 0
    print("Encoder value reset to 0")


def update_display():
    """Update display with current status"""
    global last_display_update
    current_time = time.ticks_ms()
    
    # Update display every 500ms
    if current_time - last_display_update > 500:
        last_display_update = current_time
        if display and display.initialized:
            active_keys = switch_handler.get_active_switches()
            display.show_status(encoder_value, active_keys)
            switch_handler.reset_states()


def main():
    """Main program"""
    global media_control
    
    print("\n" + "="*50)
    print("XIAO RP2040 MICROPAD Controller")
    print("="*50)
    print("Hardware:")
    print("  - 6 MX-Style Switches")
    print("  - EC11 Rotary Encoder (Volume Control)")
    print("  - SSD1306 OLED Display (128x64)")
    print("="*50 + "\n")
    
    # Initialize media control for volume
    media_control = init_media_control()
    if media_control.enabled:
        print("✓ Volume control ENABLED via EC11 encoder\n")
    else:
        print("✗ Volume control DISABLED (USB HID not available)\n")
    
    # Initialize display
    init_display()
    
    # Initialize switches with callback
    init_switches(on_switch_press)
    
    # Initialize encoder with callbacks
    init_encoder(on_encoder_rotate, on_encoder_button)
    
    print("All systems initialized!")
    print("Ready for input...\n")
    
    # Main loop
    try:
        while True:
            update_display()
            time.sleep(0.05)  # 20ms polling interval
    except KeyboardInterrupt:
        print("\n\nProgram stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if display and display.initialized:
            display.clear()
        print("Cleanup complete")


if __name__ == "__main__":
    main()

