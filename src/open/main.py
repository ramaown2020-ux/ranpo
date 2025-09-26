import serial
import time
import YB_Pcb_Car

# Initialize car control
car = YB_Pcb_Car.YB_Pcb_Car()
car.Ctrl_Servo(3, 90)

# Configure the serial port (replace '/dev/ttyACM0' with your port)
ser = serial.Serial('/dev/ttyACM1', 115200, timeout=1)

def read_data():
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        distances = line.split(',')
        if len(distances) >= 4:  # Assuming 4 elements: distancem, distance, distance1, color
            try:
                distancem = float(distances[1])
                distance = float(distances[0])
                distance1 = float(distances[2])
                color = distances[3]
                return distancem, distance, distance1, color
            except ValueError:
                print("Error parsing data")
    return None, None, None, None

def handle_color(color):
    if color == "r":
        car.Car_Back(70, 70)
        car.Ctrl_Servo(3, 120)
        time.sleep(2.1)

        car.Ctrl_Servo(3, 90)
        time.sleep(1.6)
        
        t = 0
        while t <= 150:
            distancem, distance, distance1, _ = read_data()
            if distance is not None:
                print(f"Distance measured: {distance} cm")
                if distance <= 60:
                    car.Car_Back(70, 70)
                    car.Ctrl_Servo(3, 120)
                    time.sleep(1.2)

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
        car.Car_Back(30, 30)
        
        # First, detect color
        distancem, distance, distance1, color = read_data()
        
        if color:
            print(f"Detected color: {color}")
            if color == "r" or color == "b":
                handle_color(color)
                
        time.sleep(0.1)  # Sleep for a short time

if _name_ == "_main_":
    main()
