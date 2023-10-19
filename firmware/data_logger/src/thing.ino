#include <Arduino.h>
#include <Wire.h>
#include <SD.h>
#include <SPI.h>
#include <string.h>
#include "tones.h"

#define compSerial Serial // data from computer keyboard to teensy USB
#define BTSerial  Serial2 // data from ESP32 to teensy UART
#define MP2Serial Serial3 // data from MP2 to teensy
#define GPSSerial Serial4 // data from GPS to teensy

#define COMP 0
#define BT   1
#define MP2  2
#define GPS  3

// sound
#define SPK_PIN 3
int melody[] = { NOTE_G5, NOTE_G5, NOTE_C6, NOTE_C6, NOTE_C6, NOTE_G5 };
int noteDurations[] = { 125, 125, 64, 125, 125, 64 };

// MPU setup
double gyro_x, gyro_y, gyro_z;
double gyro_x_error, gyro_y_error, gyro_z_error;
double gyro_x_sum, gyro_y_sum, gyro_z_sum;
unsigned long cycle_start;
double dT = .002;
double dPitch, dRoll;
double acc_x, acc_y, acc_z;
double acc_pitch, acc_roll, acc_magnitude;
double acc_pitch_error, acc_roll_error;
double pitch, roll;
double pitch_feedback_error, roll_feedback_error;
double desired_pitch, desired_roll;
double acc_magnitude_sum, acc_magnitude_initial;
double servo_roll, servo_pitch;
int average_cycle_count = 2000;

// single letter commands
#define BLINK         'b'
#define MPU           'm'
#define GET           'g'
#define COMMAND       'c'
#define END           'e' // stops record
#define RECORD        'r'
#define TONE          't' // play a sound
#define FILES         'f' // show files
#define SAVE          's' 
#define HELP          'h' 

// states
#define IDLE               0
#define INIT_RECORD        1
#define RECORD_GET_RESULTS 2
#define RECORD_JSON        3
#define STOP_RECORD        4
#define SET_MPU            5
#define CHECK_MPU          6
#define BT_RECV_LINES     7
#define SHOW_FILES         8

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
char receivedChars[4][maxReceiveLength] = {'\0', '\0', '\0', '\0'};
char oldStr[maxReceiveLength] = {};
int  currentIndex[4] = {0, 0, 0, 0};
bool lineWasRecvd[4] = {false, false, false, false};
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

// GPS
struct GPS_s{
  char GPS_valid[2];
  float GPS_lat;
  float GPS_long;
  bool success;
};

struct GPS_s g_struct;

#define EXT_BLINK_PIN 2

void setup() {
  Wire.begin();
  delay(100);
  compSerial.begin(115200);
  BTSerial.begin(115200);
  MP2Serial.begin(115200);
  GPSSerial.begin(9600);

  pinMode(EXT_BLINK_PIN, OUTPUT); 

  setup_mpu_6050_registers(); //setup the registers

  compSerial.println("Calibrating Gyro");
  BTSerial.println("Calibrating Gyro");
  calculate_gyro_error(); 
  compSerial.println("Gyro Calibration Complete"); 
  BTSerial.println("Gyro Calibration Complete"); 

  compSerial.println("Calibrating Accelerometer");
  BTSerial.println("Calibrating Accelerometer");
  calculuate_accelerometer_error(); 
  compSerial.println("Accelerometer Calibration Complete");
  BTSerial.println("Accelerometer Calibration Complete");

  if (!SD.begin(chipSelect)) {
    compSerial.println("Card failed, or not present");
  }
  compSerial.println("SD card initialized");

  BTSerial.println("Data Logger Calibration Complete");

  clrSerialString(COMP);
  clrSerialString(BT);
}

void loop() {
  handleMPU();
  handleBlink();

  if (recvSerialData(compSerial, COMP) != 0) {
    processCommand(COMP); 
  }

  if (recvSerialData(BTSerial, BT) != 0) {
    processCommand(BT); 
  }

  if (recvSerialData(GPSSerial, GPS) != 0) {
    // compSerial.println(receivedChars[GPS]);
    // strcpy(receivedChars[GPS], "$GPRMC,005944.000,A,3918.2722,N,07636.7732,W,0.25,0.55,120723,,,A*71");
    g_struct = processGPSString(receivedChars[GPS]);
    clrSerialString(GPS); // delete string but g_struct remains
  }

  switch (state) {
  case CHECK_MPU:
    {
      compSerial.print("pitch :: ");
      compSerial.print(pitch);
      compSerial.print(" :: roll :: ");
      compSerial.println(roll);

      BTSerial.print("pitch :: ");
      BTSerial.print((char) pitch);
      BTSerial.print(" :: roll :: ");
      BTSerial.println((char) roll);

      compSerial.print("lat/long :: ");
      compSerial.print(g_struct.GPS_valid);
      compSerial.print(" :: ");
      compSerial.print(g_struct.GPS_lat);
      compSerial.print(" :: ");
      compSerial.println(g_struct.GPS_long);

      BTSerial.print("lat/long :: ");
      BTSerial.print(g_struct.GPS_valid);
      BTSerial.print(" :: ");
      BTSerial.print(g_struct.GPS_lat);
      BTSerial.print(" :: ");
      BTSerial.println(g_struct.GPS_long);
      state = IDLE;
    }
    break;
  case BT_RECV_LINES: // basically gets output until timeout
    {
      uint8_t r = recvSerialData(MP2Serial, MP2);
      if (r == 1) {
	BTSerial.println(receivedChars[MP2]);
	clrSerialString(MP2);
      }
      if (r == 2) {
	BTSerial.println(receivedChars[MP2]);
	clrSerialString(MP2);
	state = IDLE;
      }
    }
    break;
  case INIT_RECORD:
    {
      MP2Serial.write("status stop\r\n"); // send this just in case 
      MP2Serial.write("get\r\n");
      compSerial.println("INIT_RECORD :: ");
      state = RECORD_GET_RESULTS;

      // remove and then write
      if (SD.exists(SD_card_name)) { SD.remove(SD_card_name); }
      dataFile = SD.open(SD_card_name, FILE_WRITE);
      lineCount = 0;
      recordTime = millis();
      blinkFlag = true;

      if (!dataFile) {
	compSerial.print("error opening: "); compSerial.print(dataFile);
	BTSerial.print("error opening: "); BTSerial.print((char) dataFile);
      }
      else {
	compSerial.println("SD :: {\nSD :: \"blob\": \"");
	dataFile.println("{\n\"blob\": \"");
      }
    }
    break;
  case RECORD_GET_RESULTS:
    {
      uint8_t r = recvSerialData(MP2Serial, MP2);
      if (r == 1) {
	compSerial.print("SD :: ");
	compSerial.println(receivedChars[MP2]);
	if (dataFile) { dataFile.println(receivedChars[MP2]); }  // SD write
	clrSerialString(MP2);
      }
      if (r == 2) {
	startTone(); // this is blocking! 
	compSerial.println("TIMEOUT");

	compSerial.println("SD :: \",");
	compSerial.println("SD :: \"data\": [");
	if (dataFile) {
	  dataFile.println("\",");
	  dataFile.println("\"data\": [");
	}

	// note this is the term prompt string, so dump it
	clrSerialString(MP2);
	MP2Serial.write("status json\r\n");
	state = RECORD_JSON;
      }
    }
    break;
  case RECORD_JSON:
    {
      if (recvSerialData(MP2Serial, MP2)) {
	if (strstr(receivedChars[MP2], "status json") != NULL) {
	  clrSerialString(MP2);
	  break;
	}
	char *str = receivedChars[MP2];
	char *ptr = strchr(str, '{');
	int idx = 0;
	if (ptr != NULL) {
	  idx = (int)(ptr - str);
	  strcpy(receivedChars[MP2], str + idx);
	}

	if (strlen(receivedChars[MP2]) > 0) {
	  // addFloatElementToJSON(receivedChars[MP2], "pitch", pitch);
	  // the roll is useful for current mount of logger to bike
	  addFloatElementToJSON(receivedChars[MP2], "angle", roll);
	  addIntElementToJSON(receivedChars[MP2], "time", millis() - recordTime);

	  addFloatElementToJSON(receivedChars[MP2], "lat", g_struct.GPS_lat);
	  addFloatElementToJSON(receivedChars[MP2], "long", g_struct.GPS_long);

	  // write the old string
	  strcpy(oldStr, receivedChars[MP2]);
	  compSerial.print("SD :: ");
	  compSerial.print(oldStr);
	  compSerial.println(",");

	  if (dataFile) { // SD write
	    dataFile.print(oldStr);
	    dataFile.println(",");
	  } 
	  clrSerialString(MP2);
	}

	lineCount++;
	if (lineCount > 10) {
	  BTSerial.println("...");
	  clrSerialString(BT);
	  lineCount = 0;
	}
      }
    }
    break;
  case STOP_RECORD:
    {
      compSerial.println("process:: status stop");
      MP2Serial.write("status stop\r\n");

      dataFile.print(oldStr);
      dataFile.println("\n]\n}");
      compSerial.print("SD :: ");
      compSerial.print(oldStr);
      compSerial.println("\n]\nSD :: }");


      compSerial.print("...STOP_RECORD");
      BTSerial.println("...STOP_RECORD");
      if (dataFile) { dataFile.close(); }
      // dataFile.close();
      stopTone(); // this is blocking! 
      blinkFlag = false;
      state = IDLE;
    }
    break;
  case SHOW_FILES:
    {
      dataFile = SD.open("/");
      printDirectory(dataFile, 0);
      state = IDLE;
    }
    break;
  case IDLE:
    break;
  default:
    break;
  }

  // blocks until MPU is ready. 
  while(((micros() - cycle_start) / 1000000.0) < dT);
}

void printDirectory(File dir, int numTabs) {
  while (true) {

    File entry =  dir.openNextFile();
    if (! entry) {
      break;
    }
    for (uint8_t i = 0; i < numTabs; i++) {
      compSerial.print('\t');
    }
    compSerial.print(entry.name());
    if (entry.isDirectory()) {
      compSerial.println("/");
      printDirectory(entry, numTabs + 1);
    } else {
      compSerial.print("\t\t");
      compSerial.println(entry.size(), DEC);
    }
    entry.close();
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

  char str2[maxReceiveLength];  // seriously, I write bad code
  strcpy(str2, receivedChars[serNum]);
  int l = strlen(str2);
  str2[l] = '\n';
  str2[l + 1] = '\0';

  char commandString[maxReceiveLength]; 
  commandString[0] = '\0';

  if (receivedChars[serNum][1] != ' ' && strlen(receivedChars[serNum]) > 2) {
    compSerial.print("commands must start with single letter :: ");
    compSerial.print(serNum);
    compSerial.print(" :: ");
    compSerial.print(receivedChars[serNum]);
    compSerial.print(" :: ");
    compSerial.println(strlen(receivedChars[serNum]));

    clrSerialString(serNum);
    return;
  }

  char cmd = receivedChars[serNum][0];
  compSerial.print("CMD :: "); compSerial.println(cmd);

  if (strlen(receivedChars[serNum]) > 2) {
    strncpy(commandString, receivedChars[serNum] + 2, strlen(receivedChars[serNum]));
    compSerial.print("STR :: ");
    compSerial.println(commandString);
  }
  
  switch (cmd) {
  case BLINK:
    compSerial.println("process:: BLINK!");
    BTSerial.println("...blink");
    // BTSerial.println("...blink");
    blinkFlag = !blinkFlag;
    state = IDLE;
    break;
  case TONE:
    compSerial.println("process:: tone");
    BTSerial.println("...tone");
    startTone();
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
    state = BT_RECV_LINES;
    break;
  case FILES:
    compSerial.println("process:: showfiles");
    state = SHOW_FILES;
    break;
  case SAVE:
    compSerial.println("process:: save");
    MP2Serial.write("save\r\n");
    state = BT_RECV_LINES;
    break;
  case MPU:
    compSerial.println("process:: showing MPU");
    state = CHECK_MPU;
    compSerial.println("Level the bike");
    BTSerial.println("Level the bike");
    delay(400);
    break;
  case COMMAND:
    if (strlen(commandString) > 0) {
      compSerial.println("sending:");
      BTSerial.println("sending a command");
      compSerial.println(commandString);
      MP2Serial.write(commandString);
      MP2Serial.write("\r\n");
      state = BT_RECV_LINES;
    }
    else {
      compSerial.println("Please send command");
      BTSerial.println("Please send command");
      state = IDLE;
    }
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
  case HELP:
    compSerial.println("BLINK         b: blink LED on logger");
    compSerial.println("TONE          t: emit tone on logger");
    compSerial.println("RECORD        r: start recording");
    compSerial.println("END           e: stop recording ");
    compSerial.println("GET           g: send get to MP2");
    compSerial.println("COMMAND       c: send command to MP2 \"c status json\"");
    compSerial.println("SAVE          s: send save to MP2");
    compSerial.println("FILES         f: broken: see files on SD card");
    compSerial.println("HELP          h: this help message");

    BTSerial.println("BLINK         b: blink LED on logger");
    BTSerial.println("TONE          t: emit tone on logger");
    BTSerial.println("RECORD        r: start recording");
    BTSerial.println("END           e: stop recording ");
    BTSerial.println("GET           g: send get to MP2");
    BTSerial.println("COMMAND       c: send command to MP2 \"c status json\"");
    BTSerial.println("SAVE          s: send save to MP2");
    BTSerial.println("FILES         f: broken: see files on SD card");
    BTSerial.println("HELP          h: this help message");
    state = IDLE;
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

void addFloatElementToJSON(char *jsonstr, char *key, float value) {
  int len = strlen(jsonstr);

  // bail if this doesnt end with '}'
  if (jsonstr[len - 1] != '}') {
    return;
  }
  // wipe the '}' character
  jsonstr[len - 1] = '\0'; 
  char buffer[40];

  sprintf(buffer, ",\"%s\":%.6f}", key, value);  

  strcat(jsonstr, buffer);
}

void addIntElementToJSON(char *jsonstr, char *key, int value) {
  int len = strlen(jsonstr);

  // bail if this doesnt end with '}'
  if (jsonstr[len - 1] != '}') {
    return;
  }
  // wipe the '}' character
  jsonstr[len - 1] = '\0'; 
  char buffer[40];

  sprintf(buffer, ",\"%s\":%d}", key, value);  

  strcat(jsonstr, buffer);
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

struct GPS_s processGPSString(char *str) {
  struct GPS_s g;

  g.success = false;

  if (strstr(receivedChars[GPS], "$GPRMC") != NULL) {
    g.success = true;

    int pos = 0;

    char *r = strdup(str);
    char *tok = r, *end = r;

    while (tok != NULL) {
      strsep(&end, ",");

      if (pos == 2) {
	strncpy(g.GPS_valid, tok, 1);
	g.GPS_valid[1] = '\0';
      }
      if (pos == 3) {
	g.GPS_lat = atof(tok);
      }
      if (pos == 5) {
	g.GPS_long = atof(tok);
      }

      tok = end;
      pos++;
    }
    
    free(r);
  }
  return g;
}

// https://forum.pjrc.com/threads/61755-TEENSY-4-0-reading-wrong-data-on-GY-521-MPU6050-Breakout-Board
void handleMPU() {
  cycle_start = micros();
  read_mpu_6050_data(); 
  calculate_pitch_roll(); 
}

void setup_mpu_6050_registers(){
  Wire.beginTransmission(0x68);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission(true);
}

void read_mpu_6050_data(){
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(0x68, 6, true);

  //Store accelerometer values and divide by 16384 as per the datasheet
  acc_x = (int16_t)(Wire.read() << 8 | Wire.read()) / 16384.0;
  acc_y = (int16_t)(Wire.read() << 8 | Wire.read()) / 16384.0;                                 
  acc_z = (int16_t)(Wire.read() << 8 | Wire.read()) / 16384.0;
  acc_magnitude = sqrt(acc_x * acc_x + acc_y * acc_y + acc_z * acc_z);

  Wire.beginTransmission(0x68);
  Wire.write(0x43);
  Wire.endTransmission(false);
  Wire.requestFrom(0x68, 6, true);

  // per the datasheet to convert to degrees/sec
  //  store gyroscope values, divide by 131.0 as 
  gyro_x = (int16_t)(Wire.read() << 8 | Wire.read()) / 131.0 - gyro_x_error;
  gyro_y = (int16_t)(Wire.read() << 8 | Wire.read()) / 131.0 - gyro_y_error;
  gyro_z = (int16_t)(Wire.read() << 8 | Wire.read()) / 131.0 - gyro_z_error;
}

// Calculate the average initial gyroscope values to find the error
// Supposed to be 0 deg/sec because it is initially at rest
// This allows us to eliminate drift along the roll and pitch axes
void calculate_gyro_error(){
  //average_cycle_count cycles
  for (int cal_int = 0; cal_int < average_cycle_count; cal_int++){ 
    read_mpu_6050_data(); //Retrieve gyro data
    gyro_x_sum += gyro_x; //sum the values
    gyro_y_sum += gyro_y;
    gyro_z_sum += gyro_z;

    delay(2);
  }

  //divide by average_cycle_count to get average deg/sec
  gyro_x_error = gyro_x_sum / average_cycle_count; 
  gyro_y_error = gyro_y_sum / average_cycle_count;
  gyro_z_error = gyro_z_sum / average_cycle_count;
}

//Calculate average initial accelerometer pitch and roll values
// this is error since we take the startup position to be 0
// on the pitch and roll axes
void calculuate_accelerometer_error(){
  
  for (int cal_acc_int = 0; cal_acc_int < average_cycle_count; cal_acc_int++){
    
    read_mpu_6050_data(); //get the accelerometer data

    //sum the accelerometer pitch and roll angles in degrees
    acc_pitch_error += (atan(acc_y / sqrt(pow(acc_z, 2) + pow(acc_x, 2))) * 180 / PI); 
    acc_roll_error += (atan(-1 * acc_z / sqrt(pow(acc_y, 2) + pow(acc_x, 2))) * 180 / PI);
    acc_magnitude_sum += acc_magnitude;

    delay(2);
  }

  //divide by average_cycle_count to get the average pitch and roll values
  acc_pitch_error /= average_cycle_count; 
  acc_roll_error /= average_cycle_count;
  acc_magnitude_initial = acc_magnitude_sum / average_cycle_count;
}

//Calculuate pitch and roll values
void calculate_pitch_roll(){
  dPitch = gyro_z * dT; //small change in angle for each cycle
  dRoll = gyro_y * dT;

  //Accelerometer-based calculations
  acc_pitch = (atan(acc_y / sqrt(pow(acc_z, 2) + pow(acc_x, 2))) * 180 / PI) - acc_pitch_error; 
  //calculate pitch and roll values according to accelerometer and subtract the error
  acc_roll = (atan(-1 * acc_z / sqrt(pow(acc_y, 2) + pow(acc_x, 2))) * 180 / PI) - acc_roll_error;

  //Calculating the final pitch and roll values
  if (abs(acc_magnitude - acc_magnitude_initial) <= .01){
    //adding the small change in pitch and roll
    pitch = (pitch + dPitch) *.97 + acc_pitch * .03; 
    //gyro values are more precise but accel helps to eliminate drift
    roll = (roll + dRoll) * .97 + acc_roll * .03; 
  }
  else {
    pitch = (pitch + dPitch);
    roll = (roll + dRoll);
  }
}


