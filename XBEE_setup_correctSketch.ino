/*
Example code from Jon & ChatGPT
*/


// Constants for the UART interface
#define UART_TX_PIN 0  // GP0 (TX)
#define UART_RX_PIN 1  // GP1 (RX)

void setup() {
  // Initialize Serial1 with baud rate of 9600
  Serial1.begin(9600);

  // Print a message to the main serial (USB) for debugging
  Serial.begin(9600);
  while (!Serial);  // Wait for the USB Serial to be ready
  Serial.println("UART Test Initialized on GP0 (TX) and GP1 (RX)");
}

void loop() {
  // Test: Send a message via Serial1 (UART)
  Serial1.println("Hello from Raspberry Pi Pico!");

  // Read from Serial1 (if any data is available)
  if (Serial1.available()) {
    String receivedData = Serial1.readString();
    Serial.print("Received via UART: ");
    Serial.println(receivedData);
  }

  delay(1000);  // Wait for 1 second before repeating
}
