#include "BluetoothSerial.h"
BluetoothSerial SerialBT;

#define BAUDRATE 115200

// #define LED_PIN BUILTIN_LED
#define LED_PIN 02
#define GPIO_PIN 27

boolean blinkFlag = false;

void setup() {
  Serial.begin(BAUDRATE);
  Serial1.begin(BAUDRATE);
  SerialBT.begin("MP2 LOGGER");

  pinMode(LED_PIN,  OUTPUT);
  pinMode(GPIO_PIN, INPUT);
}

void loop() {
  char c1;
  char c2;
  char c3;

  /* if (digitalRead(GPIO_PIN)) {
    digitalWrite(LED_PIN, HIGH);
  }
  else {
    digitalWrite(LED_PIN, LOW);
  }
  */
  delay(200);
  digitalWrite(LED_PIN, LOW);

  delay(200);
  digitalWrite(LED_PIN, HIGH);

  // Serial (not Serial1) goes to teensy

  while (Serial.available()) {
    c1 = Serial.read();
    Serial1.write(c1);
    SerialBT.write(c1);
  }

  while (Serial1.available()){
    c2 = Serial1.read();
    Serial.write(c2);
    SerialBT.write(c2);
  }

  while (SerialBT.available()){
    c3 = SerialBT.read();
    Serial.write(c3);
    Serial1.write(c3);
  }
}

