import time
from machine import Pin, Timer
from pins import ENCODER_CLK, ENCODER_DT, ENCODER_SW, ENCODER_DEBOUNCE_TIME


class EC11Encoder:
    """EC11 Rotary Encoder handler for XIAO RP2040
    
    Handles rotation detection and button press with debouncing.
    """
    
    def __init__(self, callback_rotate=None, callback_button=None):
        """Initialize the encoder
        
        Args:
            callback_rotate: Function to call with rotation direction (1 for CW, -1 for CCW)
            callback_button: Function to call when encoder button is pressed
        """
        self.callback_rotate = callback_rotate
        self.callback_button = callback_button
        
        # Setup encoder pins
        self.clk = Pin(ENCODER_CLK, Pin.IN, Pin.PULL_UP)
        self.dt = Pin(ENCODER_DT, Pin.IN, Pin.PULL_UP)
        self.sw = Pin(ENCODER_SW, Pin.IN, Pin.PULL_UP)
        
        # State tracking
        self.last_clk = self.clk.value()
        self.last_dt = self.dt.value()
        self.last_sw = self.sw.value()
        self.last_interrupt_time = 0
        self.button_press_time = 0
        
        # Setup interrupts with debouncing
        self.clk.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._handle_rotation)
        self.sw.irq(trigger=Pin.IRQ_FALLING, handler=self._handle_button)
    
    def _handle_rotation(self, pin):
        """Handle encoder rotation with debouncing"""
        # Simple debounce using time delay
        current_time = time.ticks_ms()
        if current_time - self.last_interrupt_time < ENCODER_DEBOUNCE_TIME:
            return
        
        self.last_interrupt_time = current_time
        
        clk_val = self.clk.value()
        dt_val = self.dt.value()
        
        # Detect rotation direction using state machine
        if clk_val != self.last_clk:
            if clk_val == 0:  # Falling edge on CLK
                if dt_val == 1:  # DT is high when CLK goes low = clockwise
                    if self.callback_rotate:
                        self.callback_rotate(1)
                else:  # DT is low when CLK goes low = counter-clockwise
                    if self.callback_rotate:
                        self.callback_rotate(-1)
        
        self.last_clk = clk_val
        self.last_dt = dt_val
    
    def _handle_button(self, pin):
        """Handle encoder button press with debouncing"""
        current_time = time.ticks_ms()
        if current_time - self.button_press_time < 50:  # 50ms debounce for button
            return
        
        self.button_press_time = current_time
        
        if self.sw.value() == 0:  # Button pressed (active low)
            if self.callback_button:
                self.callback_button()
