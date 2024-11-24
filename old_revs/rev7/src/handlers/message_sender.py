"""
Enhanced message sender with fault detection, dynamic values, and manual fault trigger
"""
import can
import time
import random
import math
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
        
        # Fault tracking
        self.fault_present = False
        self.fault_source = 0
        self.fault_type = 0
        self.fault_counter = 0
        
        # Initialize simulated values with base values
        self.current_values = {
            "charge_percent": 80,
            "battery_temp": 25,
            "motor_temp": 40,
            "power_output": 0,
            "tire_temps": [35, 35, 35, 35],
            "tire_pressures": [32, 32, 32, 32]
        }
        
        # Track time for sine wave variations
        self.start_time = time.time()

    def update_dynamic_values(self):
        """Update all simulated values based on current state with smooth variations"""
        ranges = VehicleStates.NOMINAL_RANGES
        current_time = time.time() - self.start_time
        
        def oscillate(min_val, max_val, period, phase=0, noise=0.1):
            """Create smooth oscillation between min and max with optional noise"""
            mid = (max_val + min_val) / 2
            amplitude = (max_val - min_val) / 2
            base = mid + amplitude * math.sin((current_time + phase) * (2 * math.pi / period))
            noise_val = random.uniform(-noise, noise) * amplitude
            return max(min_val, min(max_val, base + noise_val))

        # Skip updates if fault is present
        if self.fault_present:
            return

        # Battery charge decreases very slowly when in DRIVE/TRACK, increases in CHARGE
        charge_rate = 0
        if self.current_state == VehicleStates.DRIVE:
            charge_rate = -0.01  # Slow decrease
        elif self.current_state == VehicleStates.CHARGE:
            charge_rate = 0.05   # Faster increase
        
        self.current_values["charge_percent"] = max(
            ranges["charge_percent"][0],
            min(ranges["charge_percent"][1],
                self.current_values["charge_percent"] + charge_rate
            )
        )

        # Battery temp oscillates slowly, affected by charging/driving
        base_batt_temp = ranges["battery_temp"][0] + 10
        if self.current_state in [VehicleStates.DRIVE, VehicleStates.CHARGE]:
            base_batt_temp += 5
        
        self.current_values["battery_temp"] = oscillate(
            ranges["battery_temp"][0],
            ranges["battery_temp"][1],
            period=300,  # 5-minute cycle
            noise=0.05
        )

        # Motor temp varies more quickly, especially in DRIVE/TRACK
        motor_temp_range = ranges["motor_temp"]
        if self.current_state == VehicleStates.DRIVE:
            motor_temp_min = motor_temp_range[0] + 15
            motor_temp_max = motor_temp_range[1] - 5
        else:
            motor_temp_min = motor_temp_range[0]
            motor_temp_max = motor_temp_range[0] + 20
        
        self.current_values["motor_temp"] = oscillate(
            motor_temp_min,
            motor_temp_max,
            period=120,  # 2-minute cycle
            phase=45,
            noise=0.2
        )

        # Power output varies based on state
        power_range = ranges["power_output"]
        if self.current_state == VehicleStates.DRIVE:
            power_min = 0
            power_max = power_range[1] * 0.8
        elif self.current_state == VehicleStates.CHARGE:
            power_min = power_range[0] * 0.3
            power_max = power_range[0] * 0.8
        else:
            power_min = power_max = 0
        
        self.current_values["power_output"] = oscillate(
            power_min,
            power_max,
            period=30,
            noise=0.3
        )

        # Tire temperatures vary based on driving state
        base_tire_temp = ranges["tire_temps"][0] + 10
        if self.current_state == VehicleStates.DRIVE:
            base_tire_temp += 15
        
        for i in range(4):
            self.current_values["tire_temps"][i] = oscillate(
                base_tire_temp,
                base_tire_temp + 20,
                period=180,  # 3-minute cycle
                phase=i * 45,
                noise=0.1
            )

        # Tire pressures vary slightly with temperature
        base_pressure = (ranges["tire_pressures"][0] + ranges["tire_pressures"][1]) / 2
        for i in range(4):
            temp_effect = (self.current_values["tire_temps"][i] - base_tire_temp) * 0.1
            self.current_values["tire_pressures"][i] = oscillate(
                base_pressure - 1,
                base_pressure + 1,
                period=240,  # 4-minute cycle
                phase=i * 60,
                noise=0.05
            ) + temp_effect

    def check_faults(self):
        """Check all values against nominal ranges and set fault flags"""
        ranges = VehicleStates.NOMINAL_RANGES
        
        # Reset fault status if not manually set
        if not self.fault_present:
            self.fault_source = 0
            self.fault_type = 0
        
        # Skip automated fault checking if manual fault is present
        if self.fault_present:
            return
            
        # Check each value against its nominal range
        if self.current_values["battery_temp"] > ranges["battery_temp"][1]:
            self.fault_present = True
            self.fault_source = VehicleStates.FAULT_SOURCE_BATTERY
            self.fault_type = VehicleStates.FAULT_TYPE_TEMP_HIGH
        elif self.current_values["battery_temp"] < ranges["battery_temp"][0]:
            self.fault_present = True
            self.fault_source = VehicleStates.FAULT_SOURCE_BATTERY
            self.fault_type = VehicleStates.FAULT_TYPE_TEMP_LOW
            
        if self.current_values["motor_temp"] > ranges["motor_temp"][1]:
            self.fault_present = True
            self.fault_source = VehicleStates.FAULT_SOURCE_MOTOR
            self.fault_type = VehicleStates.FAULT_TYPE_TEMP_HIGH
            
        for pressure in self.current_values["tire_pressures"]:
            if pressure > ranges["tire_pressures"][1]:
                self.fault_present = True
                self.fault_source = VehicleStates.FAULT_SOURCE_TIRE
                self.fault_type = VehicleStates.FAULT_TYPE_PRESSURE_HIGH
            elif pressure < ranges["tire_pressures"][0]:
                self.fault_present = True
                self.fault_source = VehicleStates.FAULT_SOURCE_TIRE
                self.fault_type = VehicleStates.FAULT_TYPE_PRESSURE_LOW

    def send_fault_trigger(self):
        """Send a fault-triggering message (motor temp way above nominal)"""
        try:
            # Send critically high motor temperature
            fault_temp = 150  # Way above the nominal max of 85°C
            data = [
                int(fault_temp) & 0xFF,  # Single byte for temperature
            ]
            
            message = can.Message(
                arbitration_id=MOTOR_TEMP_ID,
                data=data,
                is_extended_id=False,
                dlc=1
            )
            
            with self.bus_lock:
                self.bus.send(message)
                
            # Force update the stored value to trigger fault detection
            self.current_values["motor_temp"] = fault_temp
            
            # Force fault flags
            self.fault_present = True
            self.fault_source = VehicleStates.FAULT_SOURCE_MOTOR
            self.fault_type = VehicleStates.FAULT_TYPE_TEMP_HIGH
            
            # Send fault messages
            self.send_fault_message()  # Send 0x601 first
            self.send_state_message()  # Then update state message
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending fault trigger: {e}")
            return False

    def send_fault_message(self):
        """Send dedicated fault message on 0x601"""
        try:
            if self.fault_present:
                # Simple fault counter and timestamp
                self.fault_counter = (self.fault_counter + 1) & 0xFF
                elapsed_ms = int((time.time() - self.start_time) * 1000) & 0xFFFFFFFF
                
                data = [
                    self.fault_source & 0xFF,      # Byte 0: Fault source
                    self.fault_type & 0xFF,        # Byte 1: Fault type
                    0x02,                          # Byte 2: Severity (2 = high)
                    (elapsed_ms >> 24) & 0xFF,     # Byte 3: Timestamp MSB
                    (elapsed_ms >> 16) & 0xFF,     # Byte 4: Timestamp
                    (elapsed_ms >> 8) & 0xFF,      # Byte 5: Timestamp
                    elapsed_ms & 0xFF,             # Byte 6: Timestamp LSB
                    self.fault_counter & 0xFF      # Byte 7: Fault counter
                ]
                
                message = can.Message(
                    arbitration_id=VEHICLE_FAULT_ID,
                    data=data,
                    is_extended_id=False,
                    dlc=8
                )
                
                with self.bus_lock:
                    self.bus.send(message)
                
                return True
        except Exception as e:
            logger.error(f"Error sending fault message: {e}")
            return False

    def send_state_message(self):
        """Send vehicle state message (0x600) with basic fault flag"""
        try:
            data = [
                self.current_state & 0xFF,         # Byte 0: Primary state
                self.current_substate & 0xFF,      # Byte 1: Sub-state
                self.status_flags & 0xFF,          # Byte 2: Status flags
                0x01 if self.fault_present else 0, # Byte 3: Fault present flag
                (self.message_counter >> 8) & 0xFF,# Byte 4: Counter high byte
                self.message_counter & 0xFF,       # Byte 5: Counter low byte
                0x00,                              # Byte 6: Reserved
                0x00                               # Byte 7: Reserved
            ]
            
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
            data = [int(abs(self.current_values["power_output"]))]
            return self.send_can_message(POWER_OUTPUT_ID, data)
        except Exception as e:
            logger.error(f"Error sending power output: {e}")
            return False