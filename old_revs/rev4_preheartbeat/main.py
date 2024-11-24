"""
Main program for VCU simulator
"""
import asyncio
import logging
import sys
from datetime import datetime
from src.handlers.keyboard_handler import KeyboardHandler
from src.handlers.message_sender import MessageSender
from src.utils.can_ids import VehicleStates

# Setup logging to console instead of file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # This redirects logging to console
)
logger = logging.getLogger(__name__)

class VCUSimulator:
    def __init__(self):
        self.message_sender = MessageSender()
        self.keyboard_handler = KeyboardHandler(self.message_sender)
        
        # Initialize with default state
        self.message_sender.update_state(
            VehicleStates.PARK,
            VehicleStates.READY,
            VehicleStates.SYSTEMS_CHECK_PASS | VehicleStates.BATTERY_OK
        )
        
        # Print initial instructions
        print("""
VCU Simulator Running
====================
Available commands:
-----------------
p - Park
d - Drive
r - Reverse
t - Track Mode
f - Fault
c - Charge
q - Quit

Current State: PARK
==================
""")
        
        logger.info("VCU Simulator initialized")

    async def run_metrics_broadcast(self):
        """Send vehicle metrics"""
        while self.keyboard_handler.running:
            try:
                self.message_sender.send_charge_percentage()
                await asyncio.sleep(2)
                
                self.message_sender.send_motor_temp()
                await asyncio.sleep(2)
                
                self.message_sender.send_battery_temp()
                await asyncio.sleep(2)
                
                self.message_sender.send_power_output()
                await asyncio.sleep(2)
                
                self.message_sender.send_tire_data()
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in metrics broadcast: {e}")
                await asyncio.sleep(1)

    async def run_keyboard(self):
        """Handle keyboard input"""
        while self.keyboard_handler.running:
            try:
                if sys.stdin.isatty():  # Only try to read keyboard if we're in a terminal
                    key = sys.stdin.read(1).lower()
                    if not self.keyboard_handler.handle_input(key):
                        break
            except Exception as e:
                logger.error(f"Error reading keyboard input: {e}")
            await asyncio.sleep(0.1)

    async def main(self):
        """Main coroutine running all VCU tasks"""
        try:
            # Create tasks for concurrent execution
            metrics_task = asyncio.create_task(self.run_metrics_broadcast())
            keyboard_task = asyncio.create_task(self.run_keyboard())
            
            # Run everything concurrently
            await asyncio.gather(metrics_task, keyboard_task)
            
        except asyncio.CancelledError:
            logger.info("VCU tasks cancelled")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.keyboard_handler.cleanup()

def main():
    """Entry point"""
    try:
        logger.info("Starting VCU Simulator")
        simulator = VCUSimulator()
        asyncio.run(simulator.main())
        
    except KeyboardInterrupt:
        logger.info("VCU Simulator stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logging.info("VCU Simulator shutdown complete")

if __name__ == "__main__":
    main()