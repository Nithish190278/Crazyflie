from src.takeoff import takeoff
from src.position_logger import log_position

def main():
    print("Connecting to Crazyflie...")
    takeoff()
    log_position()

if __name__ == "__main__":
    main()
