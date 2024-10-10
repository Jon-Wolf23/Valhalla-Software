/*
Pin: gp0

input: gp1
output: gp0

*/


int input = 1;
int output = 0;

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
Serial1.setRX(output);
Serial1.setTX(input);
Serial1.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
Serial1.println("Hello");
delay(1000);
}
