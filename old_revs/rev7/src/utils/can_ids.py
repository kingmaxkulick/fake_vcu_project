"""
CAN ID and state definitions for VCU
"""

# Vehicle Data IDs 
CHARGE_PERCENTAGE_ID = 0x101
CHARGING_RATE_ID = 0x102
ESTIMATED_FULL_CHARGE_TIME_ID = 0x103
BATTERY_TEMP_ID = 0x104
MOTOR_TEMP_ID = 0x201
INVERTER_TEMP_ID = 0x202
TIRE_TEMP_ID = 0x301
TIRE_PRESSURE_ID = 0x302
POWER_OUTPUT_ID = 0x401
TORQUE_DISTRIBUTION_ID = 0x402
SUSPENSION_METRICS_ID = 0x403
G_FORCES_ID = 0x404
BRAKE_TEMP_ID = 0x405

# Vehicle State and Fault IDs
VEHICLE_STATE_ID = 0x600
VEHICLE_FAULT_ID = 0x601

class VehicleStates:
    # Primary States (Byte 0)
    PARK = 0x01
    DRIVE = 0x02
    REVERSE = 0x03
    NEUTRAL = 0x04
    CHARGE = 0x05

    # Sub-States (Byte 1)
    INITIALIZING = 0x01
    READY = 0x02
    ACTIVE = 0x03
    COMPLETE = 0x04

    # Status Flags (Byte 2) - Bitwise flags
    DOOR_OPEN = 0x01
    CHARGING_CONNECTED = 0x02
    MOTOR_READY = 0x04
    BATTERY_OK = 0x08
    SYSTEMS_CHECK_PASS = 0x10

    # Fault Present Flag (Byte 3)
    FAULT_PRESENT = 0x01

    # Fault Sources (for ID 0x601)
    FAULT_SOURCE_BATTERY = 0x01
    FAULT_SOURCE_MOTOR = 0x02
    FAULT_SOURCE_CHARGING = 0x03
    FAULT_SOURCE_TIRE = 0x04
    FAULT_SOURCE_POWER = 0x05

    # Fault Types (for ID 0x601)
    FAULT_TYPE_TEMP_HIGH = 0x01
    FAULT_TYPE_TEMP_LOW = 0x02
    FAULT_TYPE_PRESSURE_HIGH = 0x03
    FAULT_TYPE_PRESSURE_LOW = 0x04
    FAULT_TYPE_CURRENT_HIGH = 0x05
    FAULT_TYPE_VOLTAGE_HIGH = 0x06
    FAULT_TYPE_VOLTAGE_LOW = 0x07
    FAULT_TYPE_COMM_ERROR = 0x08

    # Nominal ranges for fault detection
    NOMINAL_RANGES = {
        "battery_temp": (15, 45),    # °C
        "motor_temp": (20, 85),      # °C
        "charge_percent": (0, 100),  # %
        "power_output": (-100, 100), # kW
        "tire_temps": (20, 80),      # °C
        "tire_pressures": (28, 36)   # PSI
    }

    @classmethod
    def get_state_name(cls, state_code):
        states = {
            cls.PARK: "PARK",
            cls.DRIVE: "DRIVE",
            cls.REVERSE: "REVERSE",
            cls.NEUTRAL: "NEUTRAL",
            cls.CHARGE: "CHARGE"
        }
        return states.get(state_code, "UNKNOWN")