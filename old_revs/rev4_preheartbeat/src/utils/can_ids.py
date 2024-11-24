"""
CAN ID and state definitions for VCU
"""

# Vehicle Data IDs remain the same
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

# Vehicle State ID
VEHICLE_STATE_ID = 0x600

# State Definitions
class VehicleStates:
    # Primary States (Byte 0)
    PARK = 0x01
    DRIVE = 0x02
    REVERSE = 0x03
    NEUTRAL = 0x04
    CHARGE = 0x05
    FAULT = 0xFF

    # Sub-States (Byte 1)
    INITIALIZING = 0x01
    READY = 0x02
    ACTIVE = 0x03
    COMPLETE = 0x04
    ERROR = 0xFF

    # Status Flags (Byte 2) - Bitwise flags
    DOOR_OPEN = 0x01
    CHARGING_CONNECTED = 0x02
    MOTOR_READY = 0x04
    BATTERY_OK = 0x08
    SYSTEMS_CHECK_PASS = 0x10

    @classmethod
    def get_state_name(cls, state_code):
        states = {
            cls.PARK: "PARK",
            cls.DRIVE: "DRIVE",
            cls.REVERSE: "REVERSE",
            cls.NEUTRAL: "NEUTRAL",
            cls.CHARGE: "CHARGE",
            cls.FAULT: "FAULT"
        }
        return states.get(state_code, "UNKNOWN")