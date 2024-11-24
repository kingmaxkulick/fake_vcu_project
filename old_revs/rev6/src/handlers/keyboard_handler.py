"""
Keyboard handler for vehicle state changes and fault triggers
"""
import logging
from ..utils.can_ids import VehicleStates

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
                't': (VehicleStates.DRIVE, "TRACK")  # Track is a special drive mode
            }

            if key == 'q':
                self.running = False
                self.logger.info("Quit command received")
                return False
                
            # Handle fault trigger
            if key == 'f':
                if self.message_sender.send_fault_trigger():
                    print("\nFault triggered: Motor temperature critical")
                return True

            if key in states:
                state_code, state_name = states[key]
                
                # Reset flags first
                self.message_sender.status_flags = 0
                # Clear any existing faults
                self.message_sender.fault_present = False
                self.message_sender.fault_source = 0
                self.message_sender.fault_type = 0

                # Special handling for track mode
                if key == 't':
                    self.message_sender.current_state = state_code
                    self.message_sender.current_substate = VehicleStates.ACTIVE
                    self.message_sender.status_flags = VehicleStates.MOTOR_READY | VehicleStates.SYSTEMS_CHECK_PASS | VehicleStates.BATTERY_OK
                # Special handling for charge mode
                elif key == 'c':
                    self.message_sender.current_state = state_code
                    self.message_sender.current_substate = VehicleStates.INITIALIZING
                    self.message_sender.status_flags = VehicleStates.CHARGING_CONNECTED | VehicleStates.SYSTEMS_CHECK_PASS | VehicleStates.BATTERY_OK
                # Normal state changes
                else:
                    self.message_sender.current_state = state_code
                    self.message_sender.current_substate = VehicleStates.READY
                    self.message_sender.status_flags = VehicleStates.SYSTEMS_CHECK_PASS | VehicleStates.BATTERY_OK

                # Send updated state message immediately
                self.message_sender.send_state_message()
                print(f"\nState changed to: {state_name}")
            
            return True

        except Exception as e:
            self.logger.error(f"Error handling keyboard input: {e}")
            return True

    def cleanup(self):
        """Cleanup when stopping"""
        self.running = False