// Motor driver pins
const int AIN1_PIN = 2;
const int AIN2_PIN = 4;
const int APWM_PIN = 5;
const int BIN1_PIN = 7;
const int BIN2_PIN = 8;
const int BPWM_PIN = 6;

// Lights pin
const int LIGHTS_PIN = 10;

// Parameters
const int deadzone = 50;
int motorSpeed = 255;   // Default full speed, updated by 'V' command
bool lightsOn = false;

void setup() {
  pinMode(AIN1_PIN, OUTPUT);
  pinMode(AIN2_PIN, OUTPUT);
  pinMode(APWM_PIN, OUTPUT);
  pinMode(BIN1_PIN, OUTPUT);
  pinMode(BIN2_PIN, OUTPUT);
  pinMode(BPWM_PIN, OUTPUT);
  pinMode(LIGHTS_PIN, OUTPUT);
  digitalWrite(LIGHTS_PIN, LOW);

  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();

    if (receivedChar == 'W') {
      drive(motorSpeed, motorSpeed);
    } else if (receivedChar == 'A') {
      drive(-motorSpeed, motorSpeed);
    } else if (receivedChar == 'S') {
      drive(-motorSpeed, -motorSpeed);
    } else if (receivedChar == 'D') {
      drive(motorSpeed, -motorSpeed);
    } else if (receivedChar == 'P') {
      drive(0, 0);
    } else if (receivedChar == 'L') {
      lightsOn = !lightsOn;
      digitalWrite(LIGHTS_PIN, lightsOn ? HIGH : LOW);
    } else if (receivedChar == 'V') {
      // Read the numeric value that follows, e.g. "V180"
      String numStr = Serial.readStringUntil('\n');
      numStr.trim();
      int val = numStr.toInt();
      motorSpeed = constrain(val, 0, 255);
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
