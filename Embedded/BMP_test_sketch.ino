/*
Test code for BMP
*/

#include <Adafruit_Sensor.h>
#include "Adafruit_BMP3XX.h"

Adafruit_BMP3XX bmp;

#define IC2_SDA_PIN 6 //GP6
#define IC2_SCL_PIN 7 //GP7

#define SEALEVELPRESSURE_HPA (1013.25)

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);

//Checks to see if sensor is connected
if (!bmp.begin_I2C()) {
    Serial.print("Could not find a valid BMP085 sensor, check wiring!");
    while (1); //prevents loop from starting
}
}

void loop() {
  // put your main code here, to run repeatedly:
  //Records and prints data:
  if (! bmp.performReading()) {
    Serial.println("Failed to perform reading :(");
    return;
  }
  Serial.print("Temperature = ");
  Serial.print(bmp.temperature);
  Serial.println(" *C");

  Serial.print("Pressure = ");
  Serial.print(bmp.pressure / 100.0);
  Serial.println(" hPa");

  Serial.print("Approx. Alt = ");
  Serial.print(bmp.readAltitude(SEALEVELPRESSURE_HPA));
  Serial.println(" m");

  Serial.println();
  Serial.println();
  Serial.println();
  delay(2000); //will take this out after testing. Pls remind if its still in before flight day.
}
