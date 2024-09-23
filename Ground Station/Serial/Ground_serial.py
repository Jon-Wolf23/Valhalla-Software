import serial
import time
import csv
from threading import Thread, Event

import serial.tools
import serial.tools.list_ports

def return_com_ports():

    # Get a list of all COM ports
    ports = serial.tools.list_ports.comports()
    
    # Extract the port names
    com_ports = [port.device for port in ports]
    
    return com_ports

class DataReader:
    def __init__(self, port, baudrate, csv_file):
        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        self.data = {
            "altitude": None,
            "pressure": None,
            "temperature": None,
            "voltage": None,
            "timestamp": None,
            "packet_count": 0
        }
        self.running = True
        self.stop_event = Event()
         # Open CSV file for writing
        self.csv_file = csv_file
        

    def init_csv(csv_file):
        csv_file = open(csv_file, 'w', newline='')
        csv_writer = csv.DictWriter(csv_file, fieldnames=csv_file.data.keys())
        csv_writer.writeheader("TeamID", "Altitude", "Pressure", "Temperature", "Voltage", "Timestamp", "Packet Count")  # Write header to CSV
        return

    def read_data(self):
        while self.running:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    self.parse_data(line)
                    self.data['packet_count'] += 1
                    # Writes data to csv
                    self.csv_writer.writerow(f"TeamID,", self.data)
                    
                time.sleep(0.1)
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                break

    def parse_data(self, line):
        # Assume the line format is: "altitude,pressure,temperature,voltage"
        try:
            altitude, pressure, temperature, voltage = map(float, line.split(','))
            self.data.update({
                "altitude": altitude,
                "pressure": pressure,
                "temperature": temperature,
                "voltage": voltage,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        except ValueError:
            print(f"Invalid data format: {line}")

    def start(self):
        self.thread = Thread(target=self.read_data)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.serial_port.close()

if __name__ == "__main__":
    reader = DataReader(port='COM3', baudrate=9600)  # Change COM port and baudrate as needed
    try:
        reader.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        reader.stop()
        print("Data reading stopped.")