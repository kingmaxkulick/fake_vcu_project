"""
Modified handler to use keyboard instead of GPIO
"""
import logging
import sys
import tty
import termios
import threading
from ..utils.can_ids import VehicleStates

class KeyboardHandler:
    def __init__(self, message_sender):
        self.message_sender = message_sender
        self.logger = logging.getLogger(__name__)
        self.running = True
        
        # Keyboard mapping
        self.KEY_MAPPING = {
            'p': ('park', VehicleStates.PARK),
            'd': ('drive', VehicleStates.DRIVE),
            'r': ('reverse', VehicleStates.REVERSE),
            't': ('track', VehicleStates.DRIVE),  # Track mode is a special drive mode
            'f': ('fault', VehicleStates.FAULT),
            'c': ('charge', VehicleStates.CHARGE)
        }
        
        # Start keyboard listening thread
        self.keyboard_thread = threading.Thread(target=self._keyboard_listener)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        
        self.logger.info("Keyboard handler initialized")
        self.logger.info("Available commands:")
        self.logger.info("p - Park")
        self.logger.info("d - Drive")
        self.logger.info("r - Reverse")
        self.logger.info("t - Track Mode")
        self.logger.info("f - Fault")
        self.logger.info("c - Charge")
        self.logger.info("q - Quit")

    def _get_char(self):
        """Get a single character from stdin"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _keyboard_listener(self):
        """Listen for keyboard input"""
        while self.running:
            try:
                char = self._get_char()
                
                # Exit on 'q'
                if char == 'q':
                    self.logger.info("Quit command received")
                    self.running = False
                    sys.exit(0)
                
                # Handle state changes
                if char in self.KEY_MAPPING:
                    state_name, state_code = self.KEY_MAPPING[char]
                    
                    # Special handling for charge state
                    if state_name == 'charge':
                        self.message_sender.update_state(
                            state_code,
                            VehicleStates.INITIALIZING,
                            self.message_sender.status_flags | VehicleStates.CHARGING_CONNECTED
                        )
                    # Special handling for track mode
                    elif state_name == 'track':
                        self.message_sender.update_state(
                            state_code,
                            VehicleStates.ACTIVE,  # Use ACTIVE for track mode
                            self.message_sender.status_flags | VehicleStates.MOTOR_READY
                        )
                    else:
                        self.message_sender.update_state(
                            state_code,
                            VehicleStates.READY
                        )
                    
                    self.logger.info(f"State changed to: {state_name}")
                
            except Exception as e:
                self.logger.error(f"Error in keyboard handler: {e}")
                continue

    def cleanup(self):
        """Cleanup when stopping"""
        self.running = False
        self.logger.info("Keyboard handler shutdown")