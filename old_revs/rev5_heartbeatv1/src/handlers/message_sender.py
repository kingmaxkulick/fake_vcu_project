"""
Enhanced message sender with proper state handling and vehicle data
"""
import can
import time
import logging
from threading import Lock
from ..utils.can_ids import *

logger = logging.getLogger(__name__)

class MessageSender:
    def __init__(self):
        self.bus = can.interface.Bus(channel="can0", interface="socketcan")
        self.message_counter = 0
        self.current_state = VehicleStates.PARK
        self.current_substate = VehicleStates.READY
        self.status_flags = VehicleStates.SYSTEMS_CHECK_PASS | VehicleStates.BATTERY_OK
        self.bus_lock = Lock()
        
        # Initialize simulated values
        self.current_values = {
            "charge_percent": 80,
            "battery_temp": 25,
            "motor_temp": 40,
            "power_output": 0,
            "tire_temps": [35, 35, 35, 35],
            "tire_pressures": [32, 32, 32, 32]
        }

    def send_state_message(self):
        """Send vehicle state message"""
        try:
            timestamp = int((time.time() * 1000) % 65536)  # 16-bit timestamp
            
            data = [
                self.current_state & 0xFF,
                self.current_substate & 0xFF,
                self.status_flags & 0xFF,
                0,  # Checksum placeholder
                (timestamp >> 8) & 0xFF,
                timestamp & 0xFF,
                (self.message_counter >> 8) & 0xFF,
                self.message_counter & 0xFF
            ]
            
            data[3] = sum(data[0:3]) & 0xFF  # Checksum
            
            message = can.Message(
                arbitration_id=VEHICLE_STATE_ID,
                data=data,
                is_extended_id=False,
                dlc=8
            )
            
            with self.bus_lock:
                self.bus.send(message)
            
            self.message_counter = (self.message_counter + 1) % 65536
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending state message: {e}")
            return False

    def send_can_message(self, arbitration_id, data, is_extended_id=False):
        """Generic method to send CAN messages"""
        try:
            message = can.Message(
                arbitration_id=arbitration_id,
                data=data,
                is_extended_id=is_extended_id,
                dlc=len(data)
            )
            with self.bus_lock:
                self.bus.send(message)
            return True
        except Exception as e:
            logger.error(f"Error sending message {hex(arbitration_id)}: {e}")
            return False

    def send_charge_percentage(self):
        """Send battery charge percentage"""
        try:
            data = [int(self.current_values["charge_percent"])]
            return self.send_can_message(CHARGE_PERCENTAGE_ID, data)
        except Exception as e:
            logger.error(f"Error sending charge percentage: {e}")
            return False

    def send_motor_temp(self):
        """Send motor temperature"""
        try:
            data = [int(self.current_values["motor_temp"])]
            return self.send_can_message(MOTOR_TEMP_ID, data)
        except Exception as e:
            logger.error(f"Error sending motor temp: {e}")
            return False

    def send_battery_temp(self):
        """Send battery temperature"""
        try:
            data = [int(self.current_values["battery_temp"])]
            return self.send_can_message(BATTERY_TEMP_ID, data)
        except Exception as e:
            logger.error(f"Error sending battery temp: {e}")
            return False

    def send_tire_data(self):
        """Send tire temperatures and pressures"""
        try:
            temp_data = [int(t) for t in self.current_values["tire_temps"]]
            pressure_data = [int(p) for p in self.current_values["tire_pressures"]]
            
            temp_success = self.send_can_message(TIRE_TEMP_ID, temp_data)
            pressure_success = self.send_can_message(TIRE_PRESSURE_ID, pressure_data)
            
            return temp_success and pressure_success
        except Exception as e:
            logger.error(f"Error sending tire data: {e}")
            return False

    def send_power_output(self):
        """Send power output"""
        try:
            data = [int(self.current_values["power_output"])]
            return self.send_can_message(POWER_OUTPUT_ID, data)
        except Exception as e:
            logger.error(f"Error sending power output: {e}")
            return False