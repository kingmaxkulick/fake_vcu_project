import RPi.GPIO as GPIO
from message_sender import send_state
import time

# GPIO setup
GPIO.cleanup()  # Reset all GPIO states
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Pin definitions
SWITCH_PINS = {
    "power": 2,  # Normal switch for power
    "charge": 3,  # Normal switch for charge
    "park": 4,  # Momentary switch for park
    "drive": 17,  # Momentary switch for drive
    "reverse": 27,  # Momentary switch for reverse
    "track": 22,  # Momentary switch for track
    "fault": 10,  # Momentary switch for fault
}

# GPIO setup
for pin in SWITCH_PINS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Monitor normal switches
def monitor_normal_switches():
    if GPIO.input(SWITCH_PINS["power"]) == GPIO.LOW:  # Switch pressed
        print("Power switch activated!")
    if GPIO.input(SWITCH_PINS["charge"]) == GPIO.LOW:  # Switch pressed
        send_state("charge")
        print("Charge state activated!")

# Handle momentary switch presses
def handle_momentary_switch(channel):
    for state, pin in SWITCH_PINS.items():
        if channel == pin:
            send_state(state)
            print(f"{state.capitalize()} state activated!")

# Add event detection for momentary switches
for state in ["park", "drive", "reverse", "track", "fault"]:
    try:
        GPIO.add_event_detect(SWITCH_PINS[state], GPIO.FALLING, callback=handle_momentary_switch, bouncetime=200)
    except RuntimeError as e:
        print(f"Failed to add edge detection for {state}: {e}")

# Main loop
try:
    while True:
        monitor_normal_switches()
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
finally:
    GPIO.cleanup()
