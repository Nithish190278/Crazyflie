import time
import logging
import cflib
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.high_level_commander import HighLevelCommander

# File to save position data
LOG_FILE = "position_log.txt"
URI = "radio://0/80/2M"  # Update this if needed

# Configure logging
logging.basicConfig(level=logging.ERROR)

def position_callback(timestamp, data, logconf):
    """Callback function to receive and log position data."""
    x = data.get("kalman.stateX", 0.0)
    y = data.get("kalman.stateY", 0.0)
    z = data.get("kalman.stateZ", 0.0)

    print(f"Position -> X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")

    # Append data to file
    with open(LOG_FILE, "a") as file:
        file.write(f"{timestamp}, {x}, {y}, {z}\n")

def fly_and_log():
    """Make Crazyflie take off, hover at 30 cm, log position, and land."""
    cflib.crtp.init_drivers(enable_debug_driver=False)
    cf = Crazyflie(rw_cache="./cache")

    print("Connecting to Crazyflie...")

    is_connected = False

    def connection_callback(link_uri):
        nonlocal is_connected
        is_connected = True
        print(f"Connected to {link_uri}")

    cf.connected.add_callback(connection_callback)
    cf.open_link(URI)

    while not is_connected:
        time.sleep(0.5)

    print("Waiting for log TOC to initialize...")
    time.sleep(2)

    # Enable high-level commander
    commander = HighLevelCommander(cf)

    # Configure position logging
    log_config = LogConfig(name="Position", period_in_ms=100)
    log_config.add_variable("kalman.stateX", "float")
    log_config.add_variable("kalman.stateY", "float")
    log_config.add_variable("kalman.stateZ", "float")

    if cf.log.toc is None:
        print("Error: Log TOC is not initialized.")
        return

    cf.log.add_config(log_config)
    log_config.data_received_cb.add_callback(position_callback)
    log_config.start()

    print("Taking off and hovering at 30 cm...")
    
    commander.takeoff(0.3, 2.0)  # Take off to 30 cm height in 2 seconds
    time.sleep(3)  # Wait for takeoff

    print("Hovering and logging position...")
    time.sleep(5)  # Hover for 5 seconds while logging

    print("Landing...")
    commander.land(0.0, 2.0)  # Land smoothly
    time.sleep(3)

    print("Flight complete. Closing connection.")
    log_config.stop()
    cf.close_link()

if __name__ == "__main__":
    fly_and_log()
