# Required libraries
import serial
import time
import os
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

class SerialReader:
    def __init__(self, port, baudrate, csv_file, telementary):
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}") # Change this later to return faulty port/connection

        # Initializes data dictionary
        self.telementary = telementary

        # Initializes running status, thread, stope event, csv_file
        self.running = True
        self.thread = None
        self.stop_event = Event()
        self.csv_file = csv_file


    ######################### Main Loop and its Connected Functions #########################
    
    # Main loop, constantly reads data from COM port until a serial exception occurs or untile the stop funciton is called
    def read_data(self):
        # Open the file in append mode and write new data
        with open(self.csv_file, mode='a+', newline='') as file:
            file.seek(0, os.SEEK_END)  # Go to the end of the file
            writer = csv.writer(file)
        while self.running:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    self.parse_data(line)

                    # Write the last parsed row of telemetry data to the CSV
                    # Extract the last entry from each telemetry list
                    latest_row = [self.telemetry[i][-1] for i in range(11)]
                    writer.writerow(latest_row)
                    
                time.sleep(0.1)
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                time.sleep(1)

    # Organized data received from the read_data function
    def parse_data(self, line):
        # Assume the line format is: "TeamID,mission_time,packet_count,sw_state,pl_state,altitude,pressure,temperature,voltage,gps_latitude,gps_longitude"
        try:
            # Parse the CSV line into individual float values
            TeamID, mission_time, packet_count, sw_state, pl_state, altitude, pressure, temperature, voltage, gps_latitude, gps_longitude = map(float, line.split(','))

            # Append parsed data to respective lists
            self.telementary["team_id"].append(1004)  # Assuming TeamID is fixed at 1004
            self.telementary["mission_time"].append(mission_time)
            self.telementary["packet_count"].append(packet_count)
            self.telementary["sw_state"].append(sw_state)
            self.telementary["pl_state"].append(pl_state)
            self.telementary["altitude"].append(altitude)
            self.telementary["pressure"].append(pressure)
            self.telementary["temp"].append(temperature)
            self.telementary["voltage"].append(voltage)
            self.telementary["gps_latitude"].append(gps_latitude)
            self.telementary["gps_longitude"].append(gps_longitude)

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