# asyncio allows for asynchronous, non-blocking execution of tasks, ideal for timed events and I/O operations
import asyncio
from message_sender import (
    send_charge_percentage, send_charging_rate, send_estimated_full_charge_time, send_battery_temp,
    send_motor_temp, send_inverter_temp, send_tire_temp, send_tire_pressure,
    send_power_output, send_torque_distribution, send_suspension_metrics,
    send_g_forces, send_brake_temp
)

async def main():
    while True:
        send_charge_percentage()
        await asyncio.sleep(2)
        
        send_charging_rate()
        await asyncio.sleep(2)
        
        send_estimated_full_charge_time()
        await asyncio.sleep(2)
        
        send_battery_temp()
        await asyncio.sleep(2)
        
        send_motor_temp()
        await asyncio.sleep(2)
        
        send_inverter_temp()
        await asyncio.sleep(2)
        
        send_tire_temp()
        await asyncio.sleep(2)
        
        send_tire_pressure()
        await asyncio.sleep(2)
        
        send_power_output()
        await asyncio.sleep(2)
        
        send_torque_distribution()
        await asyncio.sleep(2)
        
        send_suspension_metrics()
        await asyncio.sleep(2)
        
        send_g_forces()
        await asyncio.sleep(2)
        
        send_brake_temp()
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
