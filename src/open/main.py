import serial
import time
import YB_Pcb_Car

# ---------------- Initialize car control ----------------
car = YB_Pcb_Car.YB_Pcb_Car()
car.Ctrl_Servo(3, 90)  # 90° = straight

# ---------------- Serial Setup ----------------
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)


def read_data():
    """Reads data from Arduino via serial."""
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        distances = line.split(',')
        if len(distances) >= 4:
            try:
                distancem = float(distances[1])   # center
                distance = float(distances[0])    # left
                distance1 = float(distances[2])   # right
                color = distances[3]
                return distancem, distance, distance1, color
            except ValueError:
                print("Error parsing data:", line)
    return None, None, None, None


def center_robot(distance, distance1, tolerance=5):
    """Adjust steering servo to keep robot centered.
    distance = left sensor, distance1 = right sensor
    """
    if distance is None or distance1 is None:
        return

    diff = distance - distance1  # positive = more space on left

    if abs(diff) <= tolerance:
        car.Ctrl_Servo(3, 90)
        car.Car_Back(70, 70)
        print("Centered: straight")
    elif diff > 0:
        car.Ctrl_Servo(3, 100)  # steer slightly right
        car.Car_Back(70, 70)
        print("Steering right to center")
    else:
        car.Ctrl_Servo(3, 80)   # steer slightly left
        car.Car_Back(70, 70)
        print("Steering left to center")


def handle_color(color):
    """Handles behavior based on detected color."""
    if color == "r":
        # Example: stop, reverse, then continue centered
        car.Car_Back(70, 70)
        car.Ctrl_Servo(3, 120)
        time.sleep(2)

        car.Ctrl_Servo(3, 90)
        time.sleep(1.7)

        t = 0
        while t <= 20:
            distancem, distance, distance1, _ = read_data()
            print("Center:", distancem, " Left:", distance, " Right:", distance1)

            if distance is not None and distance1 is not None:
                if (distancem <= 70 or distance <= 30) and distance1 > 30:
                    car.Car_Back(70, 70)
                    car.Ctrl_Servo(3, 120)
                    time.sleep(0.9)
                    car.Ctrl_Servo(3, 90)
                    time.sleep(1)
                elif distance1 <= 25:
                    car.Car_Back(70, 70)
                    car.Ctrl_Servo(3, 80)
                    time.sleep(0.2)
                    car.Ctrl_Servo(3, 90)
                    time.sleep(0.2)
                else:
                    car.Ctrl_Servo(3, 90)
                    time.sleep(0.5)

                t += 1
            time.sleep(0.1)

        car.Ctrl_Servo(3, 90)

    elif color == "b":
        car.Ctrl_Servo(3, 60)
        time.sleep(1)
        car.Ctrl_Servo(3, 90)
        time.sleep(0.1)


def main():
    """Main control loop."""
    while True:
        distancem, distance, distance1, color = read_data()

        if color:
            car.Car_Back(30, 30)
            print(f"Detected color: {color}")
            if color in ["r", "b"]:
                handle_color(color)

        if distancem is not None and distancem <= 15:
            car.Car_Stop()
            print("Obstacle detected! Stopping.")
            time.sleep(2)  # wait, then continue

        # Keep robot centered
        if distance is not None and distance1 is not None:
            center_robot(distance, distance1)

        time.sleep(0.1)


# ---------------- Run Program ----------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program stopped manually.")
    finally:
        car.Car_Stop()
