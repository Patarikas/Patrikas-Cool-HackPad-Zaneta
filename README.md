# XIAO RP2040 Keyboard Controller Project

## Overview
This project implements a keyboard controller using:
- **Microcontroller**: Seeed XIAO RP2040 (RP2040 chip)
- **Input Devices**: 
  - 6 × MX-style mechanical switches
  - 1 × EC11 rotary encoder with push button

## Hardware Requirements
- Seeed XIAO RP2040
- 6 × MX-style switches
- 1 × EC11 rotary encoder
- 6 × Cherry MX compatible keycaps (optional)
- USB-C cable for programming

## Wiring Diagram

### MX Switches
| Switch | GPIO Pin | XIAO Pin |
|--------|----------|----------|
| Switch 1 | GPIO0 | D0 |
| Switch 2 | GPIO1 | D1 |
| Switch 3 | GPIO2 | D2 |
| Switch 4 | GPIO3 | D3 |
| Switch 5 | GPIO4 | D4 |
| Switch 6 | GPIO5 | D5 |

All switch pins should be connected with one end to ground and the other to the GPIO pin.

### EC11 Rotary Encoder
| Signal | GPIO Pin | XIAO Pin |
|--------|----------|----------|
| CLK | GPIO28 | D8 |
| DT | GPIO27 | D7 |
| SW | GPIO26 | D6 |
| GND | GND | GND |
| VCC | 3V3 | 3V3 |

## File Structure
```
project/
├── main.py          # Main program entry point
├── boot.py          # Boot initialization script
├── pins.py          # Pin definitions and configuration
├── encoder.py       # EC11 rotary encoder handler class
└── README.md        # This file
```

## Code Files Description

### pins.py
- Defines GPIO pin mappings for all inputs
- Contains debounce timing constants
- Centralizes all hardware configuration

### encoder.py
- `EC11Encoder` class for rotary encoder handling
- Implements rotation detection (clockwise/counter-clockwise)
- Handles encoder button presses with debouncing
- Interrupt-driven architecture for low latency

### main.py
- `SwitchHandler` class for managing MX switches
- Switch press detection with debouncing
- Callback-based event system
- Example callbacks for switches and encoder
- Main initialization and event loop

### boot.py
- System initialization
- Debug information printing

## Features
- **Interrupt-driven**: All inputs handled via GPIO interrupts
- **Debouncing**: Hardware debouncing for switches (20ms) and encoder (2ms)
- **Callback System**: Easy to implement custom actions for each input
- **Modular Design**: Separate modules for encoder and switch handling

## Usage

### Basic Setup
```python
from main import init_switches, init_encoder

# Initialize with default callbacks
init_switches(my_switch_callback)
init_encoder(my_rotate_callback, my_button_callback)
```

### Custom Callbacks
```python
def handle_switch_1(switch_name):
    if switch_name == 'switch_1':
        print("Switch 1 pressed!")

def handle_rotation(direction):
    if direction == 1:
        print("Rotated clockwise")
    else:
        print("Rotated counter-clockwise")

def handle_encoder_button():
    print("Encoder button pressed!")

init_switches(handle_switch_1)
init_encoder(handle_rotation, handle_encoder_button)
```

### Individual Switch Callbacks
```python
from main import switch_handler

def switch_1_action():
    print("Switch 1 action")

switch_handler.register_callback('switch_1', switch_1_action)
```

## Programming the XIAO RP2040

### Using Thonny IDE (Recommended)
1. Download and install [Thonny IDE](https://thonny.org/)
2. Install MicroPython firmware on XIAO RP2040
3. Copy files to the microcontroller
4. Run main.py

### Using Arduino IDE with MicroPython
1. Set up Arduino IDE with RP2040 board support
2. Install MicroPython via UF2 bootloader
3. Transfer files via USB

### Using Command Line (mpremote)
```bash
pip install mpremote

# Copy files to device
mpremote cp boot.py :
mpremote cp pins.py :
mpremote cp encoder.py :
mpremote cp main.py :

# Run main program
mpremote run main.py
```

## Testing
After uploading the code:
1. Open the serial monitor/console
2. Press each switch - should see "Switch pressed: switch_X"
3. Rotate the encoder - should see rotation direction messages
4. Press the encoder button - should see button press message

## Troubleshooting

### No output on serial monitor
- Check USB connection
- Verify board is selected correctly in IDE
- Ensure boot.py and main.py are on the device

### Switches not responding
- Verify GPIO pin numbers in pins.py match your wiring
- Check that switches are properly connected to GND
- Test continuity of connections

### Encoder not detecting rotation
- Check CLK and DT pins are correctly wired
- Verify encoder is connected to 3.3V
- Check encoder contacts for corrosion
- Increase ENCODER_DEBOUNCE_TIME if needed

### Erratic behavior or multiple triggers
- Increase DEBOUNCE_TIME in pins.py
- Add RC filters (100nF capacitors) to switch inputs
- Ensure proper ground connections

## Performance Considerations
- **Interrupt latency**: ~10-50μs on RP2040
- **Debounce time**: 20ms for switches (typical MX switch debounce)
- **Encoder polling**: 2ms debounce time
- **Memory**: ~4KB for this program (RP2040 has 264KB RAM)

## Future Enhancements
- USB HID support for keyboard/media commands
- Multi-key combinations detection
- Rotary encoder acceleration
- LED feedback support
- OLED display integration
- Wireless capability with additional modules

## References
- [XIAO RP2040 Datasheet](https://wiki.seeedstudio.com/XIAO-RP2040/)
- [RP2040 Datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
- [EC11 Rotary Encoder Datasheet](https://datasheet.lcsc.com/lcsc/2109131730_TM-EC11-V01F-15P3-1F-1.pdf)
- [MicroPython Documentation](https://docs.micropython.org/)

## License
This project is open source and available for personal and commercial use.

## Author Notes
This code provides a solid foundation for a mechanical keyboard controller, macro pad, or custom input device. Customize the callback functions to implement your desired functionality.
