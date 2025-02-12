import time
import logging
import cflib.crtp
from cflib.crazyflie import Crazyflie
from src.config import CRAZYFLIE_URI

logging.basicConfig(level=logging.ERROR)

# Initialize Crazyflie
cflib.crtp.init_drivers()

def takeoff():
    cf = Crazyflie()

    try:
        print("Connecting to Crazyflie...")
        cf.open_link(CRAZYFLIE_URI)
        time.sleep(2)  # Allow connection time
        print("Connected! Taking off...")

        # Increase thrust gradually for a smooth takeoff
        thrust = 40000  # Adjust this value based on your drone’s needs
        roll = 0.0      # No tilt in roll
        pitch = 0.0     # No tilt in pitch
        yawrate = 0.0   # No rotation

        # Take off and hover
        for _ in range(20):  # Maintain for 2 seconds
            cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
            time.sleep(0.1)

        print("Hovering...")

        # Maintain hover for 3 more seconds
        time.sleep(3)

        # Land safely by gradually reducing thrust
        for _ in range(20):
            thrust -= 500  # Gradually decrease thrust
            cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
            time.sleep(0.1)

        cf.commander.send_setpoint(0, 0, 0, 0)  # Cut thrust
        print("Landing...")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cf.close_link()
