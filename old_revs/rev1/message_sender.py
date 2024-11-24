#MESSAGE_SENDER.PY

import random
import can  # Ensure python-can is installed
from can_ids import (
    CHARGE_PERCENTAGE_ID, CHARGING_RATE_ID, ESTIMATED_FULL_CHARGE_TIME_ID,
    BATTERY_TEMP_ID, MOTOR_TEMP_ID, INVERTER_TEMP_ID,
    TIRE_TEMP_ID, TIRE_PRESSURE_ID, POWER_OUTPUT_ID,
    TORQUE_DISTRIBUTION_ID, SUSPENSION_METRICS_ID,
    G_FORCES_ID, BRAKE_TEMP_ID
)

# Set up the CAN interface
bus = can.interface.Bus(channel="can0", bustype="socketcan")

def send_charge_percentage():
    data = [random.randint(0, 100)]  # Charge percentage (0-100%)
    message = can.Message(arbitration_id=CHARGE_PERCENTAGE_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_charging_rate():
    data = [random.randint(0, 200)]  # Charging rate (kW)
    message = can.Message(arbitration_id=CHARGING_RATE_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_estimated_full_charge_time():
    data = [random.randint(0, 120)]  # Estimated time for full charge (in minutes)
    message = can.Message(arbitration_id=ESTIMATED_FULL_CHARGE_TIME_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_battery_temp():
    data = [random.randint(20, 80)]  # Battery pack temperature (°C)
    message = can.Message(arbitration_id=BATTERY_TEMP_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_motor_temp():
    data = [random.randint(50, 120)]  # Motor temperature (°C)
    message = can.Message(arbitration_id=MOTOR_TEMP_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_inverter_temp():
    data = [random.randint(50, 120)]  # Inverter temperature (°C)
    message = can.Message(arbitration_id=INVERTER_TEMP_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_tire_temp():
    data = [
        random.randint(20, 100),  # Tire 1 temperature (°C)
        random.randint(20, 100),  # Tire 2 temperature (°C)
        random.randint(20, 100),  # Tire 3 temperature (°C)
        random.randint(20, 100)   # Tire 4 temperature (°C)
    ]
    message = can.Message(arbitration_id=TIRE_TEMP_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_tire_pressure():
    data = [
        random.randint(30, 50),  # Tire 1 pressure (psi)
        random.randint(30, 50),  # Tire 2 pressure (psi)
        random.randint(30, 50),  # Tire 3 pressure (psi)
        random.randint(30, 50)   # Tire 4 pressure (psi)
    ]
    message = can.Message(arbitration_id=TIRE_PRESSURE_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_power_output():
    data = [random.randint(0, 255)]  # Power output metric (scaled as needed)
    message = can.Message(arbitration_id=POWER_OUTPUT_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_torque_distribution():
    data = [
        random.randint(0, 100),  # Torque front-left
        random.randint(0, 100),  # Torque front-right
        random.randint(0, 100),  # Torque rear-left
        random.randint(0, 100)   # Torque rear-right
    ]
    message = can.Message(arbitration_id=TORQUE_DISTRIBUTION_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_suspension_metrics():
    data = [
        random.randint(0, 100),  # Front suspension compression
        random.randint(0, 100),  # Front suspension rebound
        random.randint(0, 100),  # Rear suspension compression
        random.randint(0, 100)   # Rear suspension rebound
    ]
    message = can.Message(arbitration_id=SUSPENSION_METRICS_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_g_forces():
    data = [
        random.randint(-10, 10) & 0xFF,  # X-axis G force (adjusted to fit 0-255 range)
        random.randint(-10, 10) & 0xFF,  # Y-axis G force
        random.randint(-10, 10) & 0xFF   # Z-axis G force
    ]
    message = can.Message(arbitration_id=G_FORCES_ID, data=data, is_extended_id=False)
    bus.send(message)

def send_brake_temp():
    data = [random.randint(100, 255)]  # Brake temperature (°C)
    message = can.Message(arbitration_id=BRAKE_TEMP_ID, data=data, is_extended_id=False)
    bus.send(message)
