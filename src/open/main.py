import serial
import time
import YB_Pcb_Car
import RPi.GPIO as GPIO

# ---------------- GPIO Setup ----------------
LED_PIN = 21
BUTTON_PIN = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ---------------- Car Setup ----------------
car = YB_Pcb_Car.YB_Pcb_Car()
car.Ctrl_Servo(3, 90)  # 90° = straight

# ---------------- Serial Setup ----------------
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

def read_data():
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        distances = line.split(',')
        if len(distances) >= 4:
            try:
                distancem = float(distances[1])
                distance = float(distances[0])
                distance1 = float(distances[2])
                color = distances[3]
                return distancem, distance, distance1, color
            except ValueError:
                print("Error parsing data:", line)
    return None, None, None, None

def center_robot(distance, distance1, tolerance=5):
    if distance is None or distance1 is None:
        return
    diff = distance - distance1
    if abs(diff) <= tolerance:
        car.Ctrl_Servo(3, 90)
        car.Car_Back(70, 70)
        print("Centered: straight")
    elif diff > 0:
        car.Ctrl_Servo(3, 100)
        car.Car_Back(70, 70)
        print("Steering right to center")
    else:
        car.Ctrl_Servo(3, 80)
        car.Car_Back(70, 70)
        print("Steering left to center")

def handle_color(color):
    if color == "r":
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
    while True:
        distancem, distance, distance1, color = read_data()
        if color:
            car.Car_Back(30, 30)
            print(f"Detected color: {color}")
            if color in ["r", "b"]:
                handle_color(color)
            if distancem and distancem <= 15:
                car.Car_Stop()
                break
        time.sleep(0.1)

# ---------------- Startup ----------------
if __name__ == "__main__":
    try:
        GPIO.output(LED_PIN, GPIO.HIGH)
        print("Waiting for button press to start...")

        # Wait for button press event (not holding)
        GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING)  # Detect press
        time.sleep(0.2)  # small debounce

        GPIO.output(LED_PIN, GPIO.LOW)
        print("Button pressed once, starting main program...")
        main()

    except KeyboardInterrupt:
        pass
    finally:
        car.Car_Stop()
        GPIO.cleanup()
