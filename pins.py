# Pin configuration for Seeed XIAO RP2040
# Pins are based on XIAO RP2040 pinout

# MX-Style Switch pins
SWITCH_PINS = {
    'switch_1': 0,   # GPIO0 - D0
    'switch_2': 1,   # GPIO1 - D1
    'switch_3': 2,   # GPIO2 - D2
    'switch_4': 3,   # GPIO3 - D3
    'switch_5': 4,   # GPIO4 - D4
    'switch_6': 5,   # GPIO5 - D5
}

# EC11 Rotary Encoder pins
ENCODER_CLK = 28    # GPIO28 - D8 (Clock signal)
ENCODER_DT = 27     # GPIO27 - D7 (Data signal)
ENCODER_SW = 26     # GPIO26 - D6 (Switch/Button)

# OLED Display pins (SSD1306 - I2C)
OLED_SDA = 6        # GPIO6 - D4 (I2C SDA)
OLED_SCL = 7        # GPIO7 - D5 (I2C SCL)
OLED_I2C_ID = 0     # I2C bus 0
OLED_I2C_FREQ = 400000  # 400kHz

# Display settings
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_ADDR = 0x3C    # I2C address for SSD1306

# Debounce time in milliseconds
DEBOUNCE_TIME = 20

# Encoder settings
ENCODER_DEBOUNCE_TIME = 2  # ms for encoder contacts
