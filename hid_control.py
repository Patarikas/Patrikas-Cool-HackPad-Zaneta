"""USB HID Media Control for volume, play/pause, etc."""

import time

# Try to import usb_hid module
try:
    import usb_hid
    HID_AVAILABLE = True
except ImportError:
    HID_AVAILABLE = False
    print("Warning: usb_hid not available - volume control disabled")


class MediaControl:
    """Handle USB HID media control commands for volume and playback"""
    
    # Media control codes
    VOLUME_UP = 0xE9
    VOLUME_DOWN = 0xEA
    VOLUME_MUTE = 0xE2
    PLAY_PAUSE = 0xCD
    NEXT_TRACK = 0xB5
    PREV_TRACK = 0xB6
    
    def __init__(self):
        """Initialize media control"""
        self.enabled = HID_AVAILABLE
        
        if self.enabled:
            try:
                # Get the HID keyboard device
                self.hid_devices = usb_hid.devices
                if self.hid_devices:
                    # Find keyboard device or media control device
                    self.keyboard = None
                    for device in self.hid_devices:
                        if device.usage_page == 0x0C:  # Consumer (media) page
                            self.keyboard = device
                            break
                    
                    if not self.keyboard and len(self.hid_devices) > 0:
                        # Fall back to first device
                        self.keyboard = self.hid_devices[0]
                    
                    if self.keyboard:
                        print("Media control device initialized")
                else:
                    self.enabled = False
                    print("No HID devices found")
            except Exception as e:
                self.enabled = False
                print(f"Error initializing media control: {e}")
    
    def volume_up(self):
        """Send volume up command"""
        if not self.enabled:
            print("Volume control not available")
            return False
        
        try:
            # Send volume up command via HID
            # Media control uses consumer control codes
            self._send_media_command(self.VOLUME_UP)
            print("Volume UP")
            return True
        except Exception as e:
            print(f"Error sending volume up: {e}")
            return False
    
    def volume_down(self):
        """Send volume down command"""
        if not self.enabled:
            print("Volume control not available")
            return False
        
        try:
            # Send volume down command via HID
            self._send_media_command(self.VOLUME_DOWN)
            print("Volume DOWN")
            return True
        except Exception as e:
            print(f"Error sending volume down: {e}")
            return False
    
    def volume_mute(self):
        """Send mute toggle command"""
        if not self.enabled:
            print("Volume control not available")
            return False
        
        try:
            self._send_media_command(self.VOLUME_MUTE)
            print("Mute toggled")
            return True
        except Exception as e:
            print(f"Error sending mute: {e}")
            return False
    
    def play_pause(self):
        """Send play/pause command"""
        if not self.enabled:
            return False
        
        try:
            self._send_media_command(self.PLAY_PAUSE)
            print("Play/Pause")
            return True
        except Exception as e:
            print(f"Error sending play/pause: {e}")
            return False
    
    def next_track(self):
        """Send next track command"""
        if not self.enabled:
            return False
        
        try:
            self._send_media_command(self.NEXT_TRACK)
            print("Next Track")
            return True
        except Exception as e:
            print(f"Error sending next track: {e}")
            return False
    
    def prev_track(self):
        """Send previous track command"""
        if not self.enabled:
            return False
        
        try:
            self._send_media_command(self.PREV_TRACK)
            print("Previous Track")
            return True
        except Exception as e:
            print(f"Error sending previous track: {e}")
            return False
    
    def _send_media_command(self, code):
        """Send a media control command via HID
        
        Args:
            code: Media control code
        """
        if not self.enabled or not self.keyboard:
            return
        
        try:
            # Consumer Control HID format: [report_id, code_low, code_high, 0]
            # Report format: 3-byte report with media control code
            report = bytes([code & 0xFF, (code >> 8) & 0xFF, 0])
            
            # Send press
            self.keyboard.send(report)
            time.sleep(0.05)  # 50ms
            
            # Send release (zeros)
            self.keyboard.send(bytes([0, 0, 0]))
            
        except AttributeError:
            # Device might not support send() method
            try:
                # Try alternative method using write()
                self.keyboard.write(report)
                time.sleep(0.05)
                self.keyboard.write(bytes([0, 0, 0]))
            except Exception as e:
                print(f"Could not send HID report: {e}")
        except Exception as e:
            print(f"Error in _send_media_command: {e}")


# Global instance
media_control = None


def init_media_control():
    """Initialize the media control module"""
    global media_control
    media_control = MediaControl()
    return media_control


def get_media_control():
    """Get the global media control instance"""
    global media_control
    if media_control is None:
        init_media_control()
    return media_control
