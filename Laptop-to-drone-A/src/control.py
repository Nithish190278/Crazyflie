import time
from src.config import URI
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

def send_control(thrust, roll, pitch, yaw):
    with SyncCrazyflie(URI) as scf:
        commander = scf.cf.commander
        commander.send_setpoint(roll, pitch, yaw, thrust)
        time.sleep(2)
        commander.send_stop_setpoint()

# Example control command: Hover
send_control(thrust=25000, roll=0, pitch=0, yaw=0)
