// Motor driver pins
const int AIN1_PIN = 2;
const int AIN2_PIN = 4;
const int APWM_PIN = 5;
const int BIN1_PIN = 7;
const int BIN2_PIN = 8;
const int BPWM_PIN = 6;

// Parameters
const int deadzone = 50;  // Anything between -20 and 20 is stop

void setup() {
  // Configure pins
  pinMode(AIN1_PIN, OUTPUT);
  pinMode(AIN2_PIN, OUTPUT);
  pinMode(APWM_PIN, OUTPUT);
  pinMode(BIN1_PIN, OUTPUT);
  pinMode(BIN2_PIN, OUTPUT);
  pinMode(BPWM_PIN, OUTPUT);

  // Start serial communication
  Serial.begin(9600);
}

void loop() {
  // Check if data is available to read
  if (Serial.available() > 0) {
    // Read the incoming character
    char receivedChar = Serial.read();

    // Perform actions based on the received character
    if (receivedChar == 'W') {
      drive(255, 255); // Move forward
    } else if (receivedChar == 'A') {
      drive(-255, 255); // Turn left
    } else if (receivedChar == 'S') {
      drive(-255, -255); // Move backward
    } else if (receivedChar == 'D') {
      drive(255, -255); // Turn right
    } else if (receivedChar == 'P') {
      drive(0, 0); // Stop
    }
  }
}

// Positive for forward, negative for reverse
void drive(int speed_a, int speed_b) {
  // Limit speed between -255 and 255
  speed_a = constrain(speed_a, -255, 255);
  speed_b = constrain(speed_b, -255, 255);

  // Set direction for motor A
  if (speed_a == 0) {
    digitalWrite(AIN1_PIN, LOW);
    digitalWrite(AIN2_PIN, LOW);
  } else if (speed_a > 0) {
    digitalWrite(AIN1_PIN, HIGH);
    digitalWrite(AIN2_PIN, LOW);
  } else {
    digitalWrite(AIN1_PIN, LOW);
    digitalWrite(AIN2_PIN, HIGH);
  }

  // Set direction for motor B
  if (speed_b == 0) {
    digitalWrite(BIN1_PIN, LOW);
    digitalWrite(BIN2_PIN, LOW);
  } else if (speed_b > 0) {
    digitalWrite(BIN1_PIN, HIGH);
    digitalWrite(BIN2_PIN, LOW);
  } else {
    digitalWrite(BIN1_PIN, LOW);
    digitalWrite(BIN2_PIN, HIGH);
  }

  // Set speed
  analogWrite(APWM_PIN, abs(speed_a));
  analogWrite(BPWM_PIN, abs(speed_b));
}
