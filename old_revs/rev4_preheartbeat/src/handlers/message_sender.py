"""
Enhanced message sender with proper state handling and vehicle data
"""
import can
import time
import random
import logging
from ..utils.can_ids import *

logger = logging.getLogger(__name__)

class MessageSender:
    def __init__(self):
        self.bus = can.interface.Bus(channel="can0", interface="socketcan")
        self.message_counter = 0
        self.current_state = VehicleStates.PARK
        self.current_substate = VehicleStates.READY
        self.status_flags = VehicleStates.SYSTEMS_CHECK_PASS | VehicleStates.BATTERY_OK
        
        # Initialize simulated values
        self.current_values = {
            "charge_percent": 80,
            "battery_temp": 25,
            "motor_temp": 40,
            "power_output": 0,
            "tire_temps": [35, 35, 35, 35],
            "tire_pressures": [32, 32, 32, 32]
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)

    def send_state_message(self):
        """
        Send vehicle state message
        Message Format (8 bytes):
        - Byte 0: Primary State
        - Byte 1: Sub-state
        - Byte 2: Status Flags
        - Byte 3: Checksum
        - Bytes 4-5: Timestamp (ms)
        - Bytes 6-7: Message Counter
        """
        try:
            # Create message data
            timestamp = int((time.time() * 1000) % 65536)  # 16-bit timestamp
            
            data = [
                self.current_state,
                self.current_substate,
                self.status_flags,
                0,  # Checksum placeholder
                (timestamp >> 8) & 0xFF,  # Timestamp high byte
                timestamp & 0xFF,         # Timestamp low byte
                (self.message_counter >> 8) & 0xFF,  # Counter high byte
                self.message_counter & 0xFF          # Counter low byte
            ]
            
            # Calculate checksum (simple sum of first 3 bytes)
            data[3] = sum(data[0:3]) & 0xFF
            
            # Send message
            message = can.Message(
                arbitration_id=VEHICLE_STATE_ID,
                data=data,
                is_extended_id=False
            )
            self.bus.send(message)
            
            # Increment counter
            self.message_counter = (self.message_counter + 1) % 65536
            
            self.logger.debug(f"State message sent: {VehicleStates.get_state_name(self.current_state)}")
            
        except Exception as e:
            self.logger.error(f"Error sending state message: {e}")

    def update_state(self, new_state, new_substate=None, flags=None):
        """Update vehicle state and send state message"""
        try:
            old_state = self.current_state
            self.current_state = new_state
            
            if new_substate is not None:
                self.current_substate = new_substate
                
            if flags is not None:
                self.status_flags = flags
                
            self.send_state_message()
            
            self.logger.info(
                f"State changed: {VehicleStates.get_state_name(old_state)} -> "
                f"{VehicleStates.get_state_name(new_state)}"
            )
            
        except Exception as e:
            self.logger.error(f"Error updating state: {e}")

    def send_charge_percentage(self):
        """Send battery charge percentage"""
        try:
            # Update charge percentage based on state
            if self.current_state == VehicleStates.CHARGE:
                self.current_values["charge_percent"] = min(
                    self.current_values["charge_percent"] + 0.1, 100)
            elif self.current_state == VehicleStates.DRIVE:
                self.current_values["charge_percent"] = max(
                    self.current_values["charge_percent"] - 0.05, 0)
                
            data = [int(self.current_values["charge_percent"])]
            message = can.Message(
                arbitration_id=CHARGE_PERCENTAGE_ID,
                data=data,
                is_extended_id=False
            )
            self.bus.send(message)
            
        except Exception as e:
            self.logger.error(f"Error sending charge percentage: {e}")

    def send_motor_temp(self):
        """Send motor temperature"""
        try:
            # Update motor temp based on state and power output
            if self.current_state == VehicleStates.DRIVE:
                target_temp = 40 + (self.current_values["power_output"] / 255 * 40)
            else:
                target_temp = 40
            
            # Smooth temperature transition
            self.current_values["motor_temp"] += (target_temp - self.current_values["motor_temp"]) * 0.1
            
            data = [int(self.current_values["motor_temp"])]
            message = can.Message(
                arbitration_id=MOTOR_TEMP_ID,
                data=data,
                is_extended_id=False
            )
            self.bus.send(message)
            
        except Exception as e:
            self.logger.error(f"Error sending motor temp: {e}")

    def send_battery_temp(self):
        """Send battery temperature"""
        try:
            # Update battery temp based on state
            if self.current_state == VehicleStates.CHARGE:
                target_temp = 35
            else:
                target_temp = 25
            
            # Smooth temperature transition
            self.current_values["battery_temp"] += (target_temp - self.current_values["battery_temp"]) * 0.1
            
            data = [int(self.current_values["battery_temp"])]
            message = can.Message(
                arbitration_id=BATTERY_TEMP_ID,
                data=data,
                is_extended_id=False
            )
            self.bus.send(message)
            
        except Exception as e:
            self.logger.error(f"Error sending battery temp: {e}")

    def send_power_output(self):
        """Send power output"""
        try:
            # Update power output based on state
            if self.current_state == VehicleStates.DRIVE:
                target_power = random.randint(50, 200)
            else:
                target_power = 0
            
            # Smooth power transition
            self.current_values["power_output"] += (target_power - self.current_values["power_output"]) * 0.1
            
            data = [int(self.current_values["power_output"])]
            message = can.Message(
                arbitration_id=POWER_OUTPUT_ID,
                data=data,
                is_extended_id=False
            )
            self.bus.send(message)
            
        except Exception as e:
            self.logger.error(f"Error sending power output: {e}")

    def send_tire_data(self):
        """Send tire temperatures and pressures"""
        try:
            # Update tire temps based on power output
            base_temp = 35
            if self.current_state == VehicleStates.DRIVE:
                base_temp += (self.current_values["power_output"] / 255 * 20)
            
            # Update each tire with slight variations
            for i in range(4):
                target_temp = base_temp + random.uniform(-2, 2)
                self.current_values["tire_temps"][i] += (target_temp - self.current_values["tire_temps"][i]) * 0.1
                # Pressure correlates with temperature
                self.current_values["tire_pressures"][i] = 32 + (self.current_values["tire_temps"][i] - 35) * 0.2
            
            # Send tire temperatures
            temp_message = can.Message(
                arbitration_id=TIRE_TEMP_ID,
                data=[int(temp) for temp in self.current_values["tire_temps"]],
                is_extended_id=False
            )
            self.bus.send(temp_message)
            
            # Send tire pressures
            pressure_message = can.Message(
                arbitration_id=TIRE_PRESSURE_ID,
                data=[int(pressure) for pressure in self.current_values["tire_pressures"]],
                is_extended_id=False
            )
            self.bus.send(pressure_message)
            
        except Exception as e:
            self.logger.error(f"Error sending tire data: {e}")