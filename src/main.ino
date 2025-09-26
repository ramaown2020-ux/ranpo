#include <Wire.h>
#include "Adafruit_TCS34725.h"

// Pin Definitions
const int trigPin = 12;
const int echoPin = 11;
const int trigPin1 = 8;
const int echoPin1 = 9;
const int trigPinm = 4;
const int echoPinm = 5;
const int led = 13;

#define commonAnode true

// Variables
long duration, duration1, durationm;
int distance, distance1, distancem;
byte gammatable[256];

// Initialize TCS34725 sensor
Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_50MS, TCS34725_GAIN_4X);

void setup() {
  Serial.begin(115200); // Faster baud rate for quicker serial communication
  
  // Set pin modes
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPinm, OUTPUT);
  pinMode(echoPinm, INPUT);
  pinMode(led, OUTPUT);

  // Initialize TCS34725 sensor
  if (!tcs.begin()) {
    Serial.println("No TCS34725 found ... check your connections");
    while (1); // Halt if sensor not found
  }

  // Create gamma correction table
  for (int i = 0; i < 256; i++) {
    float x = i / 255.0;
    x = pow(x, 2.5) * 255;
    gammatable[i] = commonAnode ? 255 - x : x;
  }
}

void loop() {
  digitalWrite(led, HIGH); // Turn on LED for TCS34725
  delay(60); // Wait for sensor to stabilize

  float red, green, blue;
  tcs.setInterrupt(false); // Turn on LED for color reading
  tcs.getRGB(&red, &green, &blue);
  tcs.setInterrupt(true); // Turn off LED

  String result;
  if (int(blue) > int(red)) {
    result = "b";
  } else if (int(red) > int(green) && int(red) - int(green) <= 35) {
    result = "w";
  } else {
    result = "r";
  }

  // Measure distances
  distancem = measureDistance(trigPinm, echoPinm);
  distance = measureDistance(trigPin, echoPin);
  distance1 = measureDistance(trigPin1, echoPin1);

  // Print results to serial
  
  Serial.print(distancem);
  Serial.print(",");
  Serial.print(distance);
  Serial.print(",");
  Serial.print(distance1);
  Serial.print(",");
  Serial.println(result);

  // Short delay for loop stability
  delay(150); // Adjust as needed for your application
}

// Function to measure distance
int measureDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  return duration * 0.034 / 2;
}
