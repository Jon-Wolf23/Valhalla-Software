// Jon's Embeddeed

// LIBRARIES
#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include <SerialUART.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP3XX.h>
#include <SparkFun_u-blox_GNSS_Arduino_Library.h>
#include <Servo.h>

/*######################### PIN DECLARATIONS ########################*/

// CS pin on pico
#define SD_CS_PIN 17

// Serial1 UART
#define Serial1_TX_PIN 0
#define Serial1_RX_PIN 1

// BMP390
Adafruit_BMP3XX bmp390;
#define BMP390_ADDRESS 0x77

// ZOE-M8Q
SFE_UBLOX_GNSS zoem8q;

// Buzzer and Led pin
#define BUZ_LED_PIN 22

// Voltage
#define VOLTAGE_PIN 26

// Define Servo Pins
const int CAN_SERVO_PIN = 10;
const int PARA_SERVO_PIN = 11;
const int CAN_NMOS_PIN = 21;
const int PARA_NMOS_PIN = 20;

Servo Parachute;
Servo Canister;

/*###################################################################*/


/*############## GLOBAL VARIABLES AND CONSTANTS #####################*/

// Message Type Indicator
const String STATUS_IND = "1";
const String ERROR_IND = "2";
const String DATA_IND = "0";

// Data Variables
const int team_id = 1004;
float mission_time;
int packet_count = 0;
String sw_state;
String pl_state;
float altitude = 0.0;
float reference_pressure;
float pressure  = 0.0;
float temp = 0.0;
float voltage = 0.0;
float gps_latitude = 0.0;
float gps_longitude = 0.0;

// true if SD card fails to connect
bool SDERROR = false;

// true if BMP390 fails to connect
bool BMPERROR = false;

// true if ZOE-M8Q fails to connect
bool ZOEERROR = false;

bool deployed = false;
bool released = false;
bool sd_closed = false;

float prev_alt = 0;

String state;

String data;

// SD
String file;
File data_file;

// Timer
unsigned long last_time = 0;
unsigned long interval = 1000;

/*###################################################################*/


/*################## FUNCTION DECLARATIONS ##########################*/

String file_increment(const String base, const String ext);
void init_sd();
void init_bmp390();
void init_zoem8q();
float roundToPrecision(float value, int decimalPlaces);
String format_time(unsigned long mission_time_ms);
void activate_BUZandLED();
float get_reference_pressure();

/*###################################################################*/


/*########################## SETUP ##################################*/

void setup() {
  // Opens Serial connection through USB for debugging
  Serial.begin(9600);
  delay(500);

  // Opens Serial1 connection to connect to XBee
  Serial1.begin(9600);
  delay(500);

  // Initializes I2C
  Wire.begin();

  // Initialize SD card
  Serial1.println(STATUS_IND + "Connecting to SD Card...");
  Serial.println("Connecting to SD Card...");
  init_sd();

  if(!SDERROR)
  {
    // Create a new csv name
    String base_file_name = "test";
    String ext = ".csv";
    file = file_increment(base_file_name, ext);

    data_file = SD.open(file, FILE_WRITE);
    if (data_file)
    {
      Serial1.println(STATUS_IND + "File creation successful");
      // println csv header to file
      data_file.println("TEAM_ID, MISSION_TIME, PACKET_COUNT, SW_STATE, PL_STATE, ALTITUDE, PRESSURE, TEMPERATURE, VOLTAGE, GPS_LATITUDE, GPS_LONGITUDE");
      data_file.flush();
      data_file.close();
    }else
    {
      Serial1.println(ERROR_IND + "CSV file failed to open");
      Serial.println("Error with sd");
      SDERROR = true;
    }
  }

  // Init BMP390
  Serial1.println(STATUS_IND + "Connecting to BMP390...");
  init_bmp390();

  // Init ZOE-M8Q
  Serial1.println(STATUS_IND + "Connecting to ZOE-M8Q...");
  init_zoem8q();

  pinMode(CAN_NMOS_PIN, OUTPUT);
  pinMode(PARA_NMOS_PIN, OUTPUT);

  Parachute.attach(PARA_SERVO_PIN);
  Canister.attach(CAN_SERVO_PIN);

  // Init buzzer and LED
  pinMode(BUZ_LED_PIN, OUTPUT);
  digitalWrite(BUZ_LED_PIN, LOW);

  digitalWrite(CAN_NMOS_PIN, HIGH);
  digitalWrite(PARA_NMOS_PIN, HIGH);
  // Move servos back to 0 degrees
  Canister.write(90);
  delay(500);
  Parachute.write(180);
  delay(1000);
  digitalWrite(CAN_NMOS_PIN, LOW);
  digitalWrite(PARA_NMOS_PIN, LOW);
  state = "launch";
}

/*###################################################################*/


/*########################### LOOP ##################################*/

void loop() {

  unsigned long current_time = millis();

  // Check if 1 second has passed since the last execution
  if (current_time - last_time >= interval) {
    last_time = current_time;
    if(state == "launch")
    {
      pl_state = "n";
      sw_state = "reading ascent data";
    }else if(state == "release")
    {
      pl_state = "r";
      sw_state = "detached from canister";
    }else if(state == "deploy" && released)
    {
      pl_state = "r";
      sw_state = "parachute deployed";
    }else if(state == "landed" && released && deployed)
    {
      pl_state = "landed";
      sw_state = "done";
    }else
    {
      pl_state = "error";
      sw_state = "error";
    }
    
    // Send data packet
    packet_count++;
    mission_time = millis();
    String send_time = format_time(mission_time);
    voltage = analogRead(VOLTAGE_PIN) * (6.0/1023)*0.42;
    voltage = roundToPrecision(voltage, 1);
    if(!BMPERROR)
    {
      altitude = roundToPrecision(bmp390.readAltitude(reference_pressure), 4);
      pressure = roundToPrecision(bmp390.pressure / 100, 4);
      temp = roundToPrecision(bmp390.temperature, 4);
    }
    if(!ZOEERROR && zoem8q.getFixType() > 2)
    {
      gps_latitude = roundToPrecision(zoem8q.getLatitude() / 10000000.0, 4);   // Latitude in degrees
      gps_longitude = roundToPrecision(zoem8q.getLongitude() / 10000000.0, 4); // Longitude in degrees
    }else
    {
      gps_latitude = 0.0;
      gps_longitude = 0.0;
    }
    data = DATA_IND + "1004," + send_time +","+ String(packet_count) +","+ sw_state +","+ pl_state +","+ String(altitude) +","+ String(pressure) +","+ String(temp) +","+ String(voltage) +","+ String(gps_latitude) +","+ String(gps_longitude);
    if(!SDERROR)
    {
      data_file = SD.open(file, FILE_WRITE);
      if (data_file)
      {
        data_file.println(data); // Come back and strip the data_ind char
        data_file.flush();
        data_file.close();
      }
    }
    Serial1.println(data);
    
    if(state == "release" && !released)
    {
      digitalWrite(PARA_NMOS_PIN, HIGH);
      digitalWrite(CAN_NMOS_PIN, HIGH);
      Canister.write(180);
      delay(500);
      Canister.write(90);
      delay(100);
      digitalWrite(CAN_NMOS_PIN, LOW);
      digitalWrite(PARA_NMOS_PIN, LOW);
      released = true;
    }

    if(state == "deploy" && !deployed)
    {
      digitalWrite(PARA_NMOS_PIN, HIGH);
      digitalWrite(CAN_NMOS_PIN, HIGH);
      Parachute.write(0);
      delay(700);
      digitalWrite(PARA_NMOS_PIN, LOW);
      digitalWrite(CAN_NMOS_PIN, LOW);
      deployed = true;
    }
    
    if(state == "landed")
    {
      if(!sd_closed && data_file)
      {
        data_file.close();
      }
      sd_closed = true;
      digitalWrite(BUZ_LED_PIN, HIGH);  // Signal landing with LED
    }

    if(altitude > 500 && !released) {
      state = "release";
    }

    if (altitude < 300 && released) {
      state = "deploy"; 
      
    }

    //Check landing
    if (altitude < 25 && deployed) {
      state = "landed";
    }
  }
}

/*###################################################################*/


/*##################### FUNCITON DEFINITIONS #######################*/

String file_increment(const String base, const String ext)
{
  int index = 1;
  String file_name = base + String(index) + ext;

  while(SD.exists(file_name.c_str()))
  {
    index++;
    file_name = base + String(index) + ext;
  }
  return file_name;
}


void init_sd()
{
  for (int i = 0; i < 10; i++)
  {
    if(SD.begin(SD_CS_PIN))  // If SD card initializes, break out of the loop
    {
      Serial1.println(STATUS_IND + "SD card connection successful");
      Serial.println(STATUS_IND + "SD card connection successful");
      SDERROR = false;
      return;
    }else
    {
      Serial1.println(ERROR_IND + "SD card failed to connect. Attempt" + String(i + 1));
      Serial.println(ERROR_IND + "SD card failed to connect. Attempt" + String(i + 1));
      delay(1000); // Wait before retrying
    }
  }
  
  Serial1.println(ERROR_IND + "SD card error, continuing without writing to CSV");
  SDERROR = true;
}


void init_bmp390()
{
  for (int i = 0; i < 10; i++)
  {
    if(!bmp390.begin_I2C(BMP390_ADDRESS))
    {
      Serial.println(ERROR_IND + "BMP390 failed to connect. Attempt" + String(i));
      delay(1000);
      if(i == 10)
      {
        Serial.println(ERROR_IND + "BMP390 error, continuing without BMP390 data");
        Serial.println(STATUS_IND + "BMP390 failure");
        BMPERROR = true;
        pressure = 0;
        temp = 0;
        altitude = 0;
        return;
      }
    }else if(bmp390.begin_I2C(BMP390_ADDRESS))
    {
      // Set up BMP390 settings
      bmp390.setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
      bmp390.setPressureOversampling(BMP3_OVERSAMPLING_4X);
      bmp390.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
      bmp390.setOutputDataRate(BMP3_ODR_50_HZ);
      reference_pressure = get_reference_pressure();
      Serial1.println(STATUS_IND + "BMP390 connection successful");
      Serial.println(STATUS_IND + "BMP390 connection successful");
      return;
    }
  } 
}

void init_zoem8q()
{
  for (int i = 0; i < 10; i++)
  {
    if(!zoem8q.begin())
    {
      Serial.println(ERROR_IND + "ZOE-M8Q failed to connect. Attempt" + String(i));
      Serial1.println(ERROR_IND + "ZOE-M8Q failed to connect. Attempt" + String(i));
      delay(1000);
    }
    if(i == 10)
    {
      Serial.println(ERROR_IND + "ZOE-M8Q error, continuing without ZOE-M8Q data");
      Serial.println(STATUS_IND + "ZOE-M8Q failure");

      Serial1.println(ERROR_IND + "ZOE-M8Q error, continuing without ZOE-M8Q data");
      Serial1.println(STATUS_IND + "ZOE-M8Q failure");
      ZOEERROR = true;
    }
  } 
  if(zoem8q.begin())
  {
    zoem8q.setI2COutput(COM_TYPE_UBX);
    Serial1.println(STATUS_IND + "ZOE-M8Q connection successful");
    Serial.println(STATUS_IND + "ZOE-M8Q connection successful");
  }
}

float roundToPrecision(float value, int decimalPlaces)
{
  float scale = pow(10, decimalPlaces);
  return round(value * scale) / scale;
}

void activate_BUZandLED()
{
  // Turn NMOS on
  digitalWrite(BUZ_LED_PIN, HIGH);
}

float get_reference_pressure()
{
  bmp390.performReading();
  bmp390.performReading();
  bmp390.performReading();
  bmp390.performReading();
  bmp390.performReading();
  bmp390.performReading();
  float ref1 = bmp390.pressure / 100.0;
  bmp390.performReading();
  float ref2 = bmp390.pressure / 100.0;
  bmp390.performReading();
  float ref3 = bmp390.pressure / 100.0;
  bmp390.performReading();
  float ref4 = bmp390.pressure / 100.0;
  bmp390.performReading();
  float ref5 = bmp390.pressure / 100.0;
  return (ref1 + ref2 + ref3 + ref4 + ref5)/5;
}

String format_time(unsigned long mission_time_ms) {
    // Convert milliseconds to total seconds
    unsigned long total_seconds = mission_time_ms / 1000;
    unsigned long hours = total_seconds / 3600;
    total_seconds %= 3600;
    unsigned long minutes = total_seconds / 60;
    unsigned long seconds = total_seconds % 60;
    unsigned long milliseconds = mission_time_ms % 1000;

    // Format the time as "HH:MM:SS.sss"
    char buffer[15];
    sprintf(buffer, "%02lu:%02lu:%02lu.%03lu", hours, minutes, seconds, milliseconds);

    return String(buffer);
}

/*###################################################################*/