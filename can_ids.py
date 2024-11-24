# CAN IDs for different types of data
CHARGE_PERCENTAGE_ID = 0x101          # Real-time charge percentage
CHARGING_RATE_ID = 0x102              # Charging rate (kW/hr)
ESTIMATED_FULL_CHARGE_TIME_ID = 0x103 # Estimated time for full charge
BATTERY_TEMP_ID = 0x104               # Battery pack temperature
MOTOR_TEMP_ID = 0x201                 # Motor temperature
INVERTER_TEMP_ID = 0x202              # Inverter temperature
TIRE_TEMP_ID = 0x301                  # Tire temperature (can be expanded for each tire if needed)
TIRE_PRESSURE_ID = 0x302              # Tire pressure (can be expanded for each tire if needed)
POWER_OUTPUT_ID = 0x401               # Power output metric
TORQUE_DISTRIBUTION_ID = 0x402        # Torque distribution to each of the 4 wheels
SUSPENSION_METRICS_ID = 0x403         # Suspension compression/rebound metric
G_FORCES_ID = 0x404                   # G-forces
BRAKE_TEMP_ID = 0x405                 # Brake temperature
