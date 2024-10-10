/*
Test code for BMP
*/

#define SDA_PIN 6 //GP6
#define SCL_PIN 7 //GP7
void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);

//Checks to see if sensor is connected
if (!bmp.begin()) {
    Serial.print("Could not find a valid BMP085 sensor, check wiring!");
    while (1); //prevents loop from starting
}

void loop() {
  // put your main code here, to run repeatedly:
  //Records and prints data:
  Serial.print("Temperature = ");
  Serial.print(bmp.readTemperature());
  Serial.println(" *C");

  Serial.print("Pressure = ");
  Serial.print(bmp.readPressure());
  Serial.println(" Pa");

  delay(1000); //will take this out after testing. Pls remind if its still in after.
}
