import time
import numpy as np
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

# Initialize Crazyflie radio
cflib.crtp.init_drivers(enable_debug_driver=False)

URI = 'radio://0/81/2M'


def take_off(cf, height=0.5, duration=2.0):
    """Lifts the drone to the specified height."""
    print("🚀 Taking off...")
    steps = int(duration / 0.1)
    for _ in range(steps):
        cf.commander.send_hover_setpoint(0, 0, 0, height)
        time.sleep(0.1)


def circular_motion_continuous(cf, radius=0.6, base_duration=12, pause_time=0.2):
    """Moves in a circular trajectory, ensuring a full 360° path with pauses."""
    print("🔄 Moving in a full circle...")

    positions = []  # Store collected positions
    steps = 19  # 360° divided by 20° per step (0° to 360° inclusive)
    move_time = (base_duration - steps * pause_time) / steps  # Adjusted move time per step

    for angle in range(0, 361, 20):  # 0°, 20°, ..., 360° (inclusive)
        rad = np.deg2rad(angle)  # Convert degrees to radians
        x = radius * np.cos(rad)  # X position
        y = radius * np.sin(rad)  # Y position
        vx = -radius * (2 * np.pi / base_duration) * np.sin(rad)  # X velocity
        vy = radius * (2 * np.pi / base_duration) * np.cos(rad)  # Y velocity

        cf.commander.send_hover_setpoint(vx, vy, 0, 0.5)  # Move continuously
        positions.append(f"Angle: {angle}°, x: {x:.2f}, y: {y:.2f}\n")
        print(f"📍 Reached: Angle={angle}°, x={x:.2f}, y={y:.2f}")

        time.sleep(move_time)  # Move duration
        cf.commander.send_hover_setpoint(0, 0, 0, 0.5)  # Pause
        time.sleep(pause_time)

    # Stop the drone after completing the circle
    cf.commander.send_hover_setpoint(0, 0, 0, 0.5)

    # Save collected positions to a file
    with open("positions.txt", "w") as file:
        file.writelines(positions)

    print("✅ Circular motion completed! Positions saved to positions.txt.")


def land(cf, duration=2.0):
    """Lands the drone smoothly at the starting center point."""
    print("⬇️ Landing...")
    steps = int(duration / 0.1)
    for _ in range(steps):
        cf.commander.send_hover_setpoint(0, 0, 0, 0.2)
        time.sleep(0.1)

    cf.commander.send_stop_setpoint()
    print("✅ Landed safely at the center!")


# Main function
def main():
    """Controls the Crazyflie flight."""
    print("🔄 Connecting to Crazyflie...")
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf  # Get Crazyflie object
        print("✅ Crazyflie Connected! Ready for flight.")  # Confirm connection

        take_off(cf, height=0.5)  # Lift to 0.5m
        circular_motion_continuous(cf, radius=0.6, base_duration=14, pause_time=0.2)  # Adjusted for full 360°
        land(cf)  # Land safely at the center


if __name__ == '__main__':
    main()
