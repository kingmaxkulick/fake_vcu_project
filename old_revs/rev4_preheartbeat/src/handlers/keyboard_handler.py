"""
Keyboard handler for vehicle state changes
"""
import logging
from ..utils.can_ids import VehicleStates

# Get logger but don't set up here - it uses main.py's configuration
logger = logging.getLogger(__name__)

class KeyboardHandler:
    def __init__(self, message_sender):
        self.message_sender = message_sender
        self.logger = logging.getLogger(__name__)
        self.running = True

    def handle_input(self, key):
        """Handle a single keypress"""
        try:
            # Map keys to states
            states = {
                'p': (VehicleStates.PARK, "PARK"),
                'd': (VehicleStates.DRIVE, "DRIVE"),
                'r': (VehicleStates.REVERSE, "REVERSE"),
                'c': (VehicleStates.CHARGE, "CHARGE"),
                'f': (VehicleStates.FAULT, "FAULT"),
                't': (VehicleStates.DRIVE, "TRACK")  # Track is a special drive mode
            }

            if key == 'q':
                self.running = False
                self.logger.info("Quit command received")
                return False

            if key in states:
                state_code, state_name = states[key]
                
                # Special handling for track mode
                if key == 't':
                    self.message_sender.update_state(
                        state_code,
                        VehicleStates.ACTIVE,
                        self.message_sender.status_flags | VehicleStates.MOTOR_READY
                    )
                # Special handling for charge mode
                elif key == 'c':
                    self.message_sender.update_state(
                        state_code,
                        VehicleStates.INITIALIZING,
                        self.message_sender.status_flags | VehicleStates.CHARGING_CONNECTED
                    )
                # Normal state changes
                else:
                    self.message_sender.update_state(
                        state_code,
                        VehicleStates.READY
                    )
                
                print(f"\nState changed to: {state_name}")
                self.logger.info(f"State changed to: {state_name}")
                
            return True

        except Exception as e:
            self.logger.error(f"Error handling keyboard input: {e}")
            return True

    def cleanup(self):
        """Cleanup when stopping"""
        self.running = False
        self.logger.info("Keyboard handler shutdown")