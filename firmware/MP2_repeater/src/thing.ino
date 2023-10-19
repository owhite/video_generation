#include <Arduino.h>
#include <Wire.h>
#include <SD.h>
#include <SPI.h>
#include <string.h>
#include "tones.h"

#define compSerial Serial // data from computer keyboard to teensy USB
#define BTSerial  Serial2 // data from ESP32 into teensy UART
#define MP2Serial Serial3 // data from MP2 into teensy UART

#define COMP 0
#define BT   1
#define MP2  2

// sound
#define SPK_PIN 3
int melody[] = { NOTE_G5, NOTE_G5, NOTE_C6, NOTE_C6, NOTE_C6, NOTE_G5 };
int noteDurations[] = { 125, 125, 64, 125, 125, 64 };

// single letter commands
#define BLINK         'b'
#define MPU           'm'
#define GET           'g'
#define COLLECT       'c'
#define END           'e' // stops record
#define SEND_STRING   't'
#define RECORD        'r'

// states
#define IDLE               0
#define INIT_RECORD        1
#define RECORD_GET_RESULTS 2
#define RECORD_JSON        3
#define STOP_RECORD        4
#define SET_MPU            5
#define CHECK_MPU          6

uint8_t state = IDLE;

// recording stuff
int lineCount = 0;
uint32_t recordTime = 0;

// serial stuff
bool enterStrCapture = true;
bool printFlag = false;
uint32_t start[3];
bool startTimer[3] = {false, false, false};

// string handling
const uint16_t maxReceiveLength = 400;
char receivedChars[3][maxReceiveLength] = {'\0', '\0', '\0'};
int  currentIndex[3] = {0, 0, 0};
bool lineWasRecvd[3] = {false, false, false};
uint32_t serInterval = 300;  // timeout to receive character from MP2

// blinking stuff
boolean blinkOn = false;
boolean blinkFlag = false;
uint32_t blinkDelta = 0;
uint32_t blinkInterval = 200; 
uint32_t recordInterval = 100; 
uint32_t blinkNow;

// SD card stuff
char SD_card_name[25];
File dataFile;
const int chipSelect = BUILTIN_SDCARD;

#define EXT_BLINK_PIN 2

void setup() {
  Wire.begin();
  delay(100);
  compSerial.begin(115200);
  BTSerial.begin(115200);
  MP2Serial.begin(115200);

  pinMode(EXT_BLINK_PIN, OUTPUT); 

  if (!SD.begin(chipSelect)) {
    compSerial.println("Card failed, or not present");
  }
  compSerial.println("SD card initialized");
}

void loop() {
  handleBlink();

  if (recvSerialData(compSerial, COMP) != 0) {
    processCommand(COMP); 
  }

  if (recvSerialData(BTSerial, BT) != 0) {
    processCommand(BT); 
  }

  if (recvSerialData(MP2Serial, MP2)) {
    compSerial.println(receivedChars[MP2]);
    clrSerialString(MP2);
  }

}

void startTone() {
  for (int thisNote = 0; thisNote < 3; thisNote++) {
    int noteDuration = noteDurations[thisNote];
    tone(SPK_PIN, melody[thisNote], noteDuration);
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    noTone(SPK_PIN);
  }
}

void stopTone() {
  for (int thisNote = 3; thisNote < 6; thisNote++) {
    int noteDuration = noteDurations[thisNote];
    tone(SPK_PIN, melody[thisNote], noteDuration);
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    noTone(SPK_PIN);
    delay(10);
  }
}

void clrSerialString(int serNum) {
  currentIndex[serNum] = 0;
  receivedChars[serNum][0] = '\0';
}

void processCommand(int serNum) {
  compSerial.println(receivedChars[serNum]);

  char commandString[maxReceiveLength]; 
  commandString[0] = '\0';

  char cmd = receivedChars[serNum][0];
  strncpy(commandString, receivedChars[serNum] + 2, strlen(receivedChars[serNum]));

  // this is a problem -- the BTserial is sending shit
  if (serNum != BT) {
    if (receivedChars[serNum][1] != ' ' && strlen(receivedChars[serNum]) > 2) {
      compSerial.print(serNum);
      compSerial.print(" :: ");
      compSerial.println("commands must start with single letter");
      compSerial.println(receivedChars[serNum]);
    }
  }
  if (receivedChars[serNum][1] != ' ' && strlen(receivedChars[serNum]) > 2) {
  }
  else {
    compSerial.print("CMD :: ");
    compSerial.println(cmd);
    if (strlen(commandString) > 0) {
      compSerial.print("STR :: ");
      compSerial.println(commandString);
    }
  }
  
  switch (cmd) {
  case BLINK:
    compSerial.println("process:: BLINK!");
    blinkFlag = !blinkFlag;
    state = IDLE;
    break;
  case RECORD:
    compSerial.println("process:: RECORD!");
    BTSerial.println("process:: RECORD!");
    SD_card_name[0] = '\0';
    if (strlen(commandString) > 0 && strlen(commandString) < 20) {
      strcpy(SD_card_name, commandString);
      strcat(SD_card_name, ".txt");
      compSerial.print("name :: ");
      compSerial.println(SD_card_name);
      BTSerial.print("name :: ");
      BTSerial.println(SD_card_name);
    }
    else {
      strcpy(SD_card_name, "default.txt");
      compSerial.print("name :: ");
      compSerial.println(SD_card_name);
      BTSerial.print("name :: ");
      BTSerial.println(SD_card_name);
    }
    BTSerial.println("....");
    state = INIT_RECORD;
    break;
  case GET:
    compSerial.println("process:: get");
    MP2Serial.write("get\r\n");
    state = IDLE;
    break;
  case MPU:
    compSerial.println("process:: showing MPU");
    state = CHECK_MPU;
    compSerial.println("Level the bike");
    BTSerial.println("Level the bike");
    delay(1000);
    break;
  case COLLECT:
    compSerial.println("process:: status json");
    MP2Serial.write("status json\r\n");
    state = IDLE;
    break;
  case END:
    compSerial.println(state);
    if (state == RECORD_JSON || state == RECORD_GET_RESULTS) {
      state = STOP_RECORD;
    }
    else {
      state = IDLE;
    }
    break;
  case IDLE:
    state = IDLE;
    break;
  default:
    break;
  }

  clrSerialString(serNum);
}

bool addData(char nextChar, int serNum) {  
  // Ignore these
  if ((nextChar == '\r') || (nextChar > 255) || (nextChar == 0)) {
    return false;
  }

  if (nextChar == '\n') {
    receivedChars[serNum][currentIndex[serNum]] = '\0';
    return true;
  }

  if (currentIndex[serNum] >= maxReceiveLength - 2) {
    receivedChars[serNum][maxReceiveLength] = '\0';
  }
  else {
    receivedChars[serNum][currentIndex[serNum]] = nextChar;
    receivedChars[serNum][currentIndex[serNum] + 1] = '\0';
    currentIndex[serNum]++;
  }

  return false;
}

uint8_t recvSerialData(Stream &ser, int serNum) {
  char in_char;
  bool dataReady;

  while ( ser.available() > 0 ) {
    start[serNum] = millis(); // used for timeout
    startTimer[serNum] = true;

    in_char= ser.read();
    dataReady = addData(in_char, serNum);  
    if ( dataReady ) {
      return 1;
    }
  }

  // Jens' term creates a prompt with no '/n'. 
  //  so throw in this timeout.
  if (strlen(receivedChars[serNum]) != 0 &&
      millis() - start[serNum] > serInterval &&
      startTimer[serNum]) {
    startTimer[serNum] = false;
    return 2;
  }

  return 0;
}

void handleBlink() {
  blinkNow = millis();
  uint32_t t = blinkInterval;
  if (state == RECORD_GET_RESULTS || state == RECORD_JSON) {
    t = recordInterval;
  }
  if (blinkFlag) {
    if ((blinkNow - blinkDelta) > t) {
      digitalWrite(EXT_BLINK_PIN, blinkOn);
      blinkOn = !blinkOn;
      blinkDelta = blinkNow;
    }
  }
  else {
    digitalWrite(EXT_BLINK_PIN, LOW);
  }
}

