"""
Main program for VCU simulator with faster updates
"""
import asyncio
import logging
import sys
import termios
import tty
import select
from src.handlers.keyboard_handler import KeyboardHandler
from src.handlers.message_sender import MessageSender
from src.utils.can_ids import VehicleStates

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class VCUSimulator:
    def __init__(self):
        self.message_sender = MessageSender()
        self.keyboard_handler = KeyboardHandler(self.message_sender)
        
        # Initialize default state
        self.message_sender.current_state = VehicleStates.PARK
        self.message_sender.current_substate = VehicleStates.READY
        self.message_sender.status_flags = VehicleStates.SYSTEMS_CHECK_PASS | VehicleStates.BATTERY_OK
        
        # Send initial state message
        self.message_sender.send_state_message()
        
        self._print_instructions()

    def _print_instructions(self):
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

    async def run_metrics_broadcast(self):
        """Continuously broadcast state and metrics."""
        while self.keyboard_handler.running:
            try:
                # Send all metrics
                await self._send_all_metrics()
                # Reduced delay between cycles from 2s to 0.1s
                await asyncio.sleep(0.1)  
            except Exception as e:
                logger.error(f"Error in metrics broadcast: {e}")
                await asyncio.sleep(0.1)

    async def _send_all_metrics(self):
        """Send all metrics in sequence with minimal delays"""
        try:
            # Send state heartbeat first
            self.message_sender.send_state_message()
            await asyncio.sleep(0.01)  # Reduced from 0.1s to 0.01s
            
            # Send all other metrics simultaneously using gather
            await asyncio.gather(
                self._send_metric(self.message_sender.send_charge_percentage),
                self._send_metric(self.message_sender.send_motor_temp),
                self._send_metric(self.message_sender.send_battery_temp),
                self._send_metric(self.message_sender.send_power_output),
                self._send_metric(self.message_sender.send_tire_data)
            )
            
        except Exception as e:
            logger.error(f"Error sending metrics: {e}")

    async def _send_metric(self, metric_func):
        """Helper to send a single metric"""
        try:
            metric_func()
            await asyncio.sleep(0.01)  # Minimal delay between messages
        except Exception as e:
            logger.error(f"Error sending metric: {e}")

    async def run_keyboard(self):
        """Handle keyboard input using async approach."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while self.keyboard_handler.running:
                try:
                    if await self._is_data():
                        key = sys.stdin.read(1).lower()
                        if not self.keyboard_handler.handle_input(key):
                            break
                    await asyncio.sleep(0.01)  # Reduced from 0.1s to 0.01s
                except Exception as e:
                    logger.error(f"Error processing keyboard input: {e}")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    async def _is_data(self):
        """Check if there is data available to read."""
        return select.select([sys.stdin], [], [], 0)[0] != []

    async def main(self):
        """Main coroutine running all VCU tasks"""
        try:
            metrics_task = asyncio.create_task(self.run_metrics_broadcast())
            keyboard_task = asyncio.create_task(self.run_keyboard())
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
        simulator = VCUSimulator()
        asyncio.run(simulator.main())
    except KeyboardInterrupt:
        logger.info("VCU Simulator stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()