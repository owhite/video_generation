#include <Arduino.h>
#include <Wire.h>

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

//FUNCTIONS

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

  //Store gyroscope values and divide by 131.0 as per the datasheet to convert to degrees/sec
  gyro_x = (int16_t)(Wire.read() << 8 | Wire.read()) / 131.0 - gyro_x_error;
  gyro_y = (int16_t)(Wire.read() << 8 | Wire.read()) / 131.0 - gyro_y_error;
  gyro_z = (int16_t)(Wire.read() << 8 | Wire.read()) / 131.0 - gyro_z_error;
}

//Calculate the average initial gyroscope values to find the error
//Supposed to be 0 deg/sec because it is initially at rest
//This allows us to eliminate drift along the roll and pitch axes
void calculate_gyro_error(){
    for (int cal_int = 0; cal_int < average_cycle_count; cal_int++){ //average_cycle_count cycles
    read_mpu_6050_data(); //Retrieve gyro data
    gyro_x_sum += gyro_x; //sum the values
    gyro_y_sum += gyro_y;
    gyro_z_sum += gyro_z;

    delay(2);
  }

  gyro_x_error = gyro_x_sum / average_cycle_count; //divide by average_cycle_count to get average deg/sec
  gyro_y_error = gyro_y_sum / average_cycle_count;
  gyro_z_error = gyro_z_sum / average_cycle_count;
}

//Calculate the average initial accelerometer pitch and roll values
//This will be the error since we take the startup position to be 0 on the pitch and roll axes
void calculuate_accelerometer_error(){
  
  for (int cal_acc_int = 0; cal_acc_int < average_cycle_count; cal_acc_int++){
    
    read_mpu_6050_data(); //get the accelerometer data

    acc_pitch_error += (atan(acc_y / sqrt(pow(acc_z, 2) + pow(acc_x, 2))) * 180 / PI); //sum the accelerometer pitch and roll angles in degrees
    acc_roll_error += (atan(-1 * acc_z / sqrt(pow(acc_y, 2) + pow(acc_x, 2))) * 180 / PI);
    acc_magnitude_sum += acc_magnitude;

    delay(2);
  }

  acc_pitch_error /= average_cycle_count; //divide by average_cycle_count to get the average pitch and roll values
  acc_roll_error /= average_cycle_count;
  acc_magnitude_initial = acc_magnitude_sum / average_cycle_count;
  
}

//Calculuate pitch and roll values
void calculate_pitch_roll(){
  dPitch = gyro_z * dT; //small change in angle for each cycle
  dRoll = gyro_y * dT;

  //Accelerometer-based calculations
  acc_pitch = (atan(acc_y / sqrt(pow(acc_z, 2) + pow(acc_x, 2))) * 180 / PI) - acc_pitch_error; //calculate pitch and roll values according to accelerometer and subtract the error
  acc_roll = (atan(-1 * acc_z / sqrt(pow(acc_y, 2) + pow(acc_x, 2))) * 180 / PI) - acc_roll_error;

  //Calculating the final pitch and roll values
  if(abs(acc_magnitude - acc_magnitude_initial) <= .01){
    pitch = (pitch + dPitch) *.97 + acc_pitch * .03; //adding the small change in pitch and roll
    roll = (roll + dRoll) * .97 + acc_roll * .03; //gyro values are more precise but accel helps to eliminate drift
  }
  else{
    pitch = (pitch + dPitch);
    roll = (roll + dRoll);
  }
  

}

//MAIN
void setup() {
  
  Wire.begin();
  Serial.begin(9600);

  delay(100);

  setup_mpu_6050_registers(); //setup the registers

  Serial.println("Calibrating Gyro");

  calculate_gyro_error(); //get the gyroscope error values

  Serial.println("Gyro Calibration Complete");
  Serial.println("Calibrating Accelerometer");

  calculuate_accelerometer_error(); //get the accelerometer error values

  Serial.println("Accelerometer Calibration Complete");

}

void loop() {

  cycle_start = micros(); //start of cycle
  read_mpu_6050_data(); //get data from MPU6050
  calculate_pitch_roll(); //calculate pitch and roll from MPU6050

  Serial.print(pitch);
  Serial.print(" / ");
  Serial.println(roll);

  

  while(((micros() - cycle_start) / 1000000.0) < dT);
}
