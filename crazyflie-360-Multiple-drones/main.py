import time
import numpy as np
import threading
import csv
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

# Initialize Crazyflie radio
cflib.crtp.init_drivers(enable_debug_driver=False)

# List of URIs for the three drones
DRONE_URIS = [
    'radio://0/80/2M',  # Drone 1
    'radio://0/81/2M',  # Drone 2
    'radio://0/82/2M'   # Drone 3
]

# Heights for each drone
DRONE_HEIGHTS = [0.5, 0.8, 1.1]

# File to store coordinates
DATA_FILE = "drone_positions.csv"


def record_data(timestamp, drone_id, x, y, height):
    """Logs drone position data to a CSV file."""
    with open(DATA_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, drone_id, x, y, height])


def take_off(cf, height, duration=2.0):
    """Lifts the drone to the specified height."""
    print(f"🚀 Drone taking off to {height}m...")
    steps = int(duration / 0.1)
    for _ in range(steps):
        cf.commander.send_hover_setpoint(0, 0, 0, height)
        time.sleep(0.1)


def circular_motion_continuous(cf, drone_id, radius=0.6, base_duration=14, pause_time=0.2):
    """Moves in a circular trajectory and logs coordinates."""
    print(f"🔄 Drone {drone_id} moving in a circle...")

    steps = 18  # 360° divided by 20° per step
    move_time = (base_duration - steps * pause_time) / steps  # Adjusted movement time per step

    for angle in range(0, 361, 20):  # Full 360° motion
        timestamp = time.time()
        rad = np.deg2rad(angle)
        x = radius * np.cos(rad)
        y = radius * np.sin(rad)

        vx = -radius * (2 * np.pi / base_duration) * np.sin(rad)
        vy = radius * (2 * np.pi / base_duration) * np.cos(rad)

        cf.commander.send_hover_setpoint(vx, vy, 0, DRONE_HEIGHTS[drone_id])
        record_data(timestamp, drone_id, x, y, DRONE_HEIGHTS[drone_id])
        print(f"📍 Drone {drone_id} at Angle={angle}° (x={x:.2f}, y={y:.2f})")

        time.sleep(move_time)
        cf.commander.send_hover_setpoint(0, 0, 0, DRONE_HEIGHTS[drone_id])  # Pause
        time.sleep(pause_time)

    print(f"✅ Drone {drone_id} completed circular motion!")


def land(cf, duration=2.0):
    """Lands the drone smoothly."""
    print("⬇️ Landing...")
    steps = int(duration / 0.1)
    for _ in range(steps):
        cf.commander.send_hover_setpoint(0, 0, 0, 0.2)
        time.sleep(0.1)

    cf.commander.send_stop_setpoint()
    print("✅ Landed safely!")


def main():
    """Controls the three Crazyflie drones."""
    scfs = [SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) for uri in DRONE_URIS]

    # Create CSV file and add header
    with open(DATA_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Drone ID", "X", "Y", "Height"])

    # Connect all drones
    for i, scf in enumerate(scfs):
        scf.open_link()
        print(f"✅ Drone {i} connected!")

    try:
        # Take off all drones
        threads = []
        for i, scf in enumerate(scfs):
            t = threading.Thread(target=take_off, args=(scf.cf, DRONE_HEIGHTS[i]))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Start circular motion for all drones simultaneously
        threads = []
        for i, scf in enumerate(scfs):
            t = threading.Thread(target=circular_motion_continuous, args=(scf.cf, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Land all drones
        threads = []
        for scf in scfs:
            t = threading.Thread(target=land, args=(scf.cf,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    finally:
        for scf in scfs:
            scf.close_link()
        print("🔗 All drone connections closed!")


if __name__ == '__main__':
    main()
