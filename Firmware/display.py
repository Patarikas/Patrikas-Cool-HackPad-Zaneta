"""SSD1306 OLED Display module for XIAO RP2040"""

from machine import I2C, Pin
import time
from pins import OLED_SDA, OLED_SCL, OLED_I2C_ID, OLED_I2C_FREQ, OLED_WIDTH, OLED_HEIGHT, OLED_ADDR


class SSD1306:
    """SSD1306 OLED Display driver (128x64)"""
    
    # SSD1306 commands
    CONTRAST = 0x81
    ENTIRE_ON = 0xA4
    NORMAL = 0xA6
    INVERT = 0xA7
    DISPLAY_OFF = 0xAE
    DISPLAY_ON = 0xAF
    SETPAGE = 0xB0
    LOWER_COLUMN_START = 0x00
    HIGHER_COLUMN_START = 0x10
    SET_START_LINE = 0x40
    
    def __init__(self, width=128, height=64, i2c_id=0, sda=6, scl=7, addr=0x3C):
        """Initialize SSD1306 display
        
        Args:
            width: Display width in pixels (default 128)
            height: Display height in pixels (default 64)
            i2c_id: I2C bus ID (0 or 1)
            sda: SDA pin number
            scl: SCL pin number
            addr: I2C address of the display
        """
        self.width = width
        self.height = height
        self.addr = addr
        self.i2c = I2C(i2c_id, scl=Pin(scl), sda=Pin(sda), freq=400000)
        
        # Frame buffer: height/8 pages * width bytes
        self.pages = height // 8
        self.buf = bytearray(self.pages * width)
        
        # Initialize display
        self.init_display()
    
    def init_display(self):
        """Initialize the display with default settings"""
        init_commands = [
            self.DISPLAY_OFF,           # Turn off display
            0xD5, 0x80,                 # Set display clock
            0xA8, 0x3F,                 # Set multiplex ratio (63)
            0xD3, 0x00,                 # Set display offset (0)
            self.SET_START_LINE,        # Set start line to 0
            0x8D, 0x14,                 # Enable charge pump
            0x20, 0x00,                 # Set memory addressing to horizontal
            0xA1,                       # Set segment re-map (flip horizontally)
            0xC8,                       # Set COM output scan direction (flip vertically)
            0xDA, 0x12,                 # Set COM pins hardware configuration
            self.CONTRAST, 0xCF,        # Set contrast
            0xD9, 0xF1,                 # Set pre-charge period
            0xDB, 0x40,                 # Set VCOMH deselect level
            self.ENTIRE_ON,             # Output follows RAM content
            self.NORMAL,                # Normal display (not inverted)
            self.DISPLAY_ON,            # Turn on display
        ]
        
        self.write_cmd(bytes(init_commands))
    
    def write_cmd(self, cmd):
        """Write command(s) to display
        
        Args:
            cmd: Single byte command or bytes object with commands
        """
        if isinstance(cmd, int):
            cmd = bytes([cmd])
        self.i2c.writeto(self.addr, bytes([0x00]) + cmd)
    
    def write_data(self, data):
        """Write data to display
        
        Args:
            data: Bytes to write to display memory
        """
        self.i2c.writeto(self.addr, bytes([0x40]) + data)
    
    def show(self):
        """Display the frame buffer"""
        for page in range(self.pages):
            self.write_cmd(self.SETPAGE | page)
            self.write_cmd(0x00)  # Column start address
            self.write_cmd(0x10)
            
            # Write one page of data
            page_start = page * self.width
            page_end = page_start + self.width
            self.write_data(self.buf[page_start:page_end])
    
    def clear(self):
        """Clear the entire display"""
        self.buf[:] = bytearray(len(self.buf))
        self.show()
    
    def fill(self, color):
        """Fill the entire display with a color
        
        Args:
            color: 1 for white, 0 for black
        """
        fill_byte = 0xFF if color else 0x00
        self.buf[:] = bytearray([fill_byte] * len(self.buf))
        self.show()
    
    def pixel(self, x, y, state=1):
        """Set or clear a pixel
        
        Args:
            x: X coordinate (0-127)
            y: Y coordinate (0-63)
            state: 1 to set pixel, 0 to clear
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        page = y // 8
        bit = y % 8
        index = page * self.width + x
        
        if state:
            self.buf[index] |= (1 << bit)
        else:
            self.buf[index] &= ~(1 << bit)
    
    def hline(self, x, y, width, color):
        """Draw a horizontal line
        
        Args:
            x: Starting X coordinate
            y: Y coordinate
            width: Line width in pixels
            color: 1 for white, 0 for black
        """
        for i in range(width):
            self.pixel(x + i, y, color)
    
    def vline(self, x, y, height, color):
        """Draw a vertical line
        
        Args:
            x: X coordinate
            y: Starting Y coordinate
            height: Line height in pixels
            color: 1 for white, 0 for black
        """
        for i in range(height):
            self.pixel(x, y + i, color)
    
    def rect(self, x, y, width, height, color, fill=False):
        """Draw a rectangle
        
        Args:
            x: Top-left X coordinate
            y: Top-left Y coordinate
            width: Width in pixels
            height: Height in pixels
            color: 1 for white, 0 for black
            fill: True to fill the rectangle
        """
        if fill:
            for i in range(height):
                self.hline(x, y + i, width, color)
        else:
            self.hline(x, y, width, color)
            self.hline(x, y + height - 1, width, color)
            self.vline(x, y, height, color)
            self.vline(x + width - 1, y, height, color)
    
    def text(self, string, x, y, color=1):
        """Draw text on display using 5x8 font
        
        Args:
            string: Text to draw
            x: Starting X coordinate
            y: Starting Y coordinate
            color: 1 for white, 0 for black
        """
        # Simple 5x8 ASCII font bitmap
        font_data = {
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
            '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],
            '1': [0x00, 0x41, 0x7F, 0x40, 0x00],
            '2': [0x72, 0x49, 0x49, 0x49, 0x46],
            '3': [0x22, 0x49, 0x49, 0x49, 0x36],
            '4': [0x0F, 0x08, 0x08, 0x08, 0x7E],
            '5': [0x27, 0x45, 0x45, 0x45, 0x39],
            '6': [0x3C, 0x4A, 0x49, 0x49, 0x30],
            '7': [0x41, 0x21, 0x11, 0x09, 0x07],
            '8': [0x36, 0x49, 0x49, 0x49, 0x36],
            '9': [0x06, 0x49, 0x49, 0x29, 0x1E],
            'A': [0x7E, 0x09, 0x09, 0x09, 0x7E],
            'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
            'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
            'D': [0x7F, 0x41, 0x41, 0x41, 0x3E],
            'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
            'F': [0x7F, 0x09, 0x09, 0x09, 0x01],
            'G': [0x3E, 0x41, 0x49, 0x49, 0x32],
            'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
            'I': [0x00, 0x41, 0x7F, 0x41, 0x00],
            'J': [0x20, 0x40, 0x41, 0x3F, 0x01],
            'K': [0x7F, 0x08, 0x14, 0x22, 0x41],
            'L': [0x7F, 0x40, 0x40, 0x40, 0x40],
            'M': [0x7F, 0x02, 0x04, 0x02, 0x7F],
            'N': [0x7F, 0x04, 0x08, 0x10, 0x7F],
            'O': [0x3E, 0x41, 0x41, 0x41, 0x3E],
            'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
            'Q': [0x3E, 0x41, 0x51, 0x21, 0x5E],
            'R': [0x7F, 0x09, 0x19, 0x29, 0x46],
            'S': [0x26, 0x49, 0x49, 0x49, 0x32],
            'T': [0x01, 0x01, 0x7F, 0x01, 0x01],
            'U': [0x3F, 0x40, 0x40, 0x40, 0x3F],
            'V': [0x1F, 0x20, 0x40, 0x20, 0x1F],
            'W': [0x7F, 0x20, 0x10, 0x20, 0x7F],
            'X': [0x63, 0x14, 0x08, 0x14, 0x63],
            'Y': [0x07, 0x08, 0x70, 0x08, 0x07],
            'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
            ':': [0x00, 0x36, 0x36, 0x00, 0x00],
            '.': [0x00, 0x60, 0x60, 0x00, 0x00],
            '-': [0x08, 0x08, 0x08, 0x08, 0x08],
        }
        
        current_x = x
        for char in string:
            if char in font_data:
                for bit_col, col_data in enumerate(font_data[char]):
                    for bit_row in range(8):
                        if col_data & (1 << bit_row):
                            self.pixel(current_x + bit_col, y + bit_row, color)
            current_x += 6  # Character width + spacing


class Display:
    """High-level display management for the micropad"""
    
    def __init__(self):
        """Initialize the display"""
        try:
            self.oled = SSD1306(
                width=OLED_WIDTH,
                height=OLED_HEIGHT,
                i2c_id=OLED_I2C_ID,
                sda=OLED_SDA,
                scl=OLED_SCL,
                addr=OLED_ADDR
            )
            self.initialized = True
            print("Display initialized successfully")
        except Exception as e:
            print(f"Failed to initialize display: {e}")
            self.initialized = False
    
    def show_welcome(self):
        """Display welcome screen"""
        if not self.initialized:
            return
        
        self.oled.clear()
        self.oled.text("MICROPAD v1.0", 20, 5)
        self.oled.text("XIAO RP2040", 25, 20)
        self.oled.hline(0, 35, 128, 1)
        self.oled.text("6 Keys + Encoder", 15, 42)
        self.oled.show()
    
    def show_status(self, encoder_value=0, active_keys=None):
        """Display current status
        
        Args:
            encoder_value: Current encoder value
            active_keys: List of active switch names
        """
        if not self.initialized:
            return
        
        self.oled.clear()
        
        # Title
        self.oled.text("STATUS", 50, 0)
        self.oled.hline(0, 10, 128, 1)
        
        # Volume level (encoder value)
        volume_bar_length = encoder_value % 20  # Clamp to 0-19
        self.oled.text(f"VOL: {volume_bar_length}", 5, 15)
        # Draw volume bar
        self.oled.rect(40, 15, 80, 8, 1, fill=False)
        bar_width = int((volume_bar_length / 20.0) * 76)
        if bar_width > 0:
            self.oled.rect(42, 17, bar_width, 4, 1, fill=True)
        
        # Active keys indicator
        key_display = "Keys:"
        if active_keys:
            key_display += " " + ",".join(active_keys)
        else:
            key_display += " None"
        self.oled.text(key_display, 5, 30)
        
        # Footer
        self.oled.hline(0, 55, 128, 1)
        self.oled.text("Ready", 50, 58)
        
        self.oled.show()
    
    def show_debug_info(self, info_dict):
        """Display debug information
        
        Args:
            info_dict: Dictionary with debug information
        """
        if not self.initialized:
            return
        
        self.oled.clear()
        self.oled.text("DEBUG INFO", 35, 0)
        self.oled.hline(0, 10, 128, 1)
        
        y_pos = 15
        for key, value in info_dict.items():
            if y_pos < 55:
                text = f"{key}: {value}"
                if len(text) > 20:
                    text = text[:20]
                self.oled.text(text, 5, y_pos)
                y_pos += 10
        
        self.oled.show()
    
    def show_key_press(self, key_name):
        """Display key press indication
        
        Args:
            key_name: Name of the pressed key
        """
        if not self.initialized:
            return
        
        self.oled.clear()
        self.oled.rect(10, 10, 108, 44, 1, fill=False)
        self.oled.text("KEY PRESSED", 32, 20)
        self.oled.text(key_name.upper(), 35, 35)
        self.oled.show()
    
    def clear(self):
        """Clear the display"""
        if self.initialized:
            self.oled.clear()
