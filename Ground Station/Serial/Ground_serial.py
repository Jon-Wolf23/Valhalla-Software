# Required libraries
import serial
import time
from threading import Thread, Event
import csv
import serial.tools
import serial.tools.list_ports

######################### Returns com ports connected to computer #########################
def return_com_ports():

    # Get a list of all COM ports
    ports = serial.tools.list_ports.comports()
    
    # Extract the port names
    com_ports = [port.device for port in ports]
    
    return com_ports


##################################################################################################################################
#   DataReader Class
##################################################################################################################################

class DataReader:
    def __init__(self, port, baudrate, csv_file):
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}") # Change this later to return faulty port/connection

        # Initializes data dictionary
        self.data = {
            "TeamID": 1004,
            "mission time": None,
            "packet count": None,
            "sw state": None,
            "pl state": None,
            "altitude": None,
            "pressure": None,
            "temperature": None,
            "voltage": None,
            "gps latitude": None,
            "gps longitude": None
        }

        # Initializes running status, thread, stope event, csv_file
        self.running = True
        self.thread = None
        self.stop_event = Event()
        self.csv_file = csv_file


    ######################### Main Loop and its Connected Functions #########################
    
    # Main loop, constantly reads data from COM port until a serial exception occurs or untile the stop funciton is called
    def read_data(self):
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow("TEAM_ID,MISSION_TIME,PACKET_COUNT,SW_STATE,PL_STATE,ALTITUDE,TEMP,VOLTAGE,GPS_LATITUDE,GPS_LONGITUDE")  # Writes a header for the CSV
        while self.running:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    self.parse_data(line)
                    self.data['packet_count'] += 1
                    # Writes data to csv
                    writer.writerow(self.data)
                    
                time.sleep(0.1)
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                break

    # Organized data recieved from the read data function
    def parse_data(self, line):
        # Assume the line format is: "TeamID,mission_time,packet_count,sw_state,pl_state,altitude,pressure,temperature,voltage,gps_latitude,gps_longitude"
        try:
            TeamID, mission_time, packet_count, sw_state, pl_state, altitude, pressure, temperature, voltage, gps_latitude, gps_longitude = map(float, line.split(','))
            self.data.update({
            "TeamID": 1004,
            "mission time": mission_time,
            "packet count": packet_count,
            "sw state": sw_state,
            "pl state": pl_state,
            "altitude": altitude,
            "pressure": pressure,
            "temperature": temperature,
            "voltage": voltage,
            "gps latitude": gps_latitude,
            "gps longitude": gps_longitude
            })
        except ValueError:
            print(f"Invalid data format: {line}")

    # Starts main loop
    def start(self):
        self.thread = Thread(target=self.read_data)
        self.thread.start()

    # Stops main loop
    def stop(self):
        self.running = False 
        self.thread.join()
        self.serial_port.close()