import os
import time
import logging
import cflib.crtp
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie import Crazyflie
from src.config import CRAZYFLIE_URI

logging.basicConfig(level=logging.ERROR)

def log_position():
    cflib.crtp.init_drivers()
    cf = Crazyflie()

    log_dir = os.path.join(os.path.dirname(__file__), "../logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "flight_data.txt")

    def log_callback(timestamp, data, logconf):
        with open(log_file_path, "a") as f:
            f.write(f"{timestamp}, {data['stateEstimate.x']}, {data['stateEstimate.y']}, {data['stateEstimate.z']}\n")
        print(f"Position: X={data['stateEstimate.x']}, Y={data['stateEstimate.y']}, Z={data['stateEstimate.z']}")

    try:
        print("Connecting to Crazyflie for logging...")
        cf.open_link(CRAZYFLIE_URI)
        time.sleep(2)

        log_config = LogConfig(name="Position", period_in_ms=100)
        log_config.add_variable("stateEstimate.x", "float")
        log_config.add_variable("stateEstimate.y", "float")
        log_config.add_variable("stateEstimate.z", "float")

        cf.log.add_config(log_config)
        log_config.data_received_cb.add_callback(log_callback)
        log_config.start()

        time.sleep(5)  # Log data for 5 seconds
        log_config.stop()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cf.close_link()
