# Required libraries
import serial
import time
from threading import Thread, Event
import csv
import serial.tools
import serial.tools.list_ports


##################################################################################################################################
#   DataReader Class
##################################################################################################################################

class SerialReader:
    def __init__(self):
            
        # Initializes data dictionary
        self.telementary = {
            "team_id" : [],
            "mission_time" : [],
            "packet_count" : [],
            "sw_state" : [],
            "pl_state" : [],
            "altitude" : [],
            "pressure" : [],
            "temp" : [],
            "voltage" : [],
            "gps_latitude" : [],
            "gps_longitude" : []
        }

        # Line Identifier, determines what data is being sent by pico
        self.current_error = ""
        self.current_status = ""

        # Initializes running status, thread, stope event, csv_file
        self.running = False
        self.thread = None
        self.stop_event = Event()
        self.csv_file = ''

        # Port and Baud
        self.opened_port = ''
        self.baud_rate = ''

        # Callbacks list for notifying other objects
        self.callbacks = []

        self.serial_port = None


    ######################### Callback System #########################
    
    def register_callback(self, callback):
        """Register a callback to be triggered on data update."""
        self.callbacks.append(callback)
    
    def notify_callbacks(self):
        """Notify all registered callbacks with the latest telementary data."""
        for callback in self.callbacks:
            callback()


    ######################### Main Loop and its Connected Functions #########################
    
    # Main loop, constantly reads data from COM port until a serial exception occurs or untile the stop funciton is called
    def read_data(self):
    # Open the file in append mode for the duration of the loop
        #print("read_data called")
        file = open(self.csv_file, mode='a+', newline='')
        writer = csv.writer(file)

        while self.running:
            #print(f"{self.serial_port.in_waiting}")
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    # Read line from the serial port
                    line = self.serial_port.readline().decode('utf-8').strip()
                    print(f"Line Read: {line}")

                    # Ensure the line has at least 1 character (for identifier)
                    if len(line) > 0:
                        identifier = line[0]  # First character is the identifier
                        content = line[1:].strip()  # Rest of the line is the actual message or data
                            
                        # Process the line based on the identifier
                        self.parse_data(identifier, content)

                        # If the identifier is '0' (data), write the last parsed row of telemetry data to the CSV
                        if identifier == '0':
                            if self.telementary["packet_count"] is not None:
                                latest_row = [
                                    str(self.telementary.get("team_id", ["0"])[-1]),
                                    self.format_time(self.telementary.get("mission_time", [0])[-1]),
                                    str(self.telementary.get("packet_count", ["0"])[-1]),
                                    str(self.telementary.get("sw_state", ["0"])[-1]),
                                    str(self.telementary.get("pl_state", ["0"])[-1]),
                                    str(self.telementary.get("altitude", ["0"])[-1]),
                                    str(self.telementary.get("pressure", ["0"])[-1]),
                                    str(self.telementary.get("temp", ["0"])[-1]),
                                    str(self.telementary.get("voltage", ["0"])[-1]),
                                    str(self.telementary.get("gps_latitude", ["0"])[-1]),
                                    str(self.telementary.get("gps_longitude", ["0"])[-1])
                                ]
                                writer.writerow(latest_row)  # Write the list of values as CSV row
                                print(f"telemetry: {self.telementary}")  # Debugging Line
                
                time.sleep(0.1)
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                time.sleep(1)

    # Organized data received from the read_data function
    def parse_data(self, identifier, content):
        if identifier == '0':
            try:
                # Parse the CSV line into individual float values
                data =  list(map(str, content.split(',')))

                if len(data) != 11:
                    raise ValueError("Invalid data length")

                # Assume the line format is: "team_id,mission_time,packet_count,sw_state,pl_state,altitude,pressure,temperature,voltage,gps_latitude,gps_longitude"
                team_id, mission_time, packet_count, sw_state, pl_state, altitude, pressure, temperature, voltage, gps_latitude, gps_longitude = data

                # Append parsed data to respective lists
                self.telementary["team_id"].append(int(team_id))
                self.telementary["mission_time"].append(self.convert_to_milliseconds(mission_time))
                self.telementary["packet_count"].append(int(packet_count))
                self.telementary["sw_state"].append(sw_state)
                self.telementary["pl_state"].append(pl_state)
                self.telementary["altitude"].append(float(altitude))
                self.telementary["pressure"].append(float(pressure))
                self.telementary["temp"].append(float(temperature))
                self.telementary["voltage"].append(float(voltage))
                self.telementary["gps_latitude"].append(float(gps_latitude))
                self.telementary["gps_longitude"].append(float(gps_longitude))

                if len(self.telementary["team_id"]) > 15:
                    self.telementary["team_id"] = self.telementary["team_id"][-15:]
                    self.telementary["mission_time"] = self.telementary["mission_time"][-15:]
                    self.telementary["packet_count"] = self.telementary["packet_count"][-15:]
                    self.telementary["sw_state"] = self.telementary["sw_state"][-15:]
                    self.telementary["pl_state"] = self.telementary["pl_state"][-15:]
                    self.telementary["altitude"] = self.telementary["altitude"][-15:]
                    self.telementary["pressure"] = self.telementary["pressure"][-15:]
                    self.telementary["temp"] = self.telementary["temp"][-15:]
                    self.telementary["voltage"] = self.telementary["voltage"][-15:]
                    self.telementary["gps_latitude"] = self.telementary["gps_latitude"][-15:]
                    self.telementary["gps_longitude"] = self.telementary["gps_longitude"][-15:]

                self.notify_callbacks()

            except ValueError:
                print(f"Invalid data format: {content}")

        elif identifier == '1':
            self.current_status = content
        
        elif identifier == '2':
            self.current_error = content

    # Starts main loop
    def start(self):
        self.running = True
        try:
            self.serial_port = serial.Serial(self.opened_port, self.baud_rate, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}") # Change this later to return faulty port/connection
            self.running = False
        if self.serial_port:
            self.thread = Thread(target=self.read_data)
            self.thread.start()
            print("thread started")
        else:
            print("Serial port not available")
            self.running = False

    # Stops main loop
    def stop(self):
        self.running = False 
        if self.thread != None:
            self.thread.join()
            self.serial_port.close()

    def return_com_ports(self):
        # Get a list of all COM ports
        ports = serial.tools.list_ports.comports()
        
        # Extract the port names
        com_ports = [port.device for port in ports]
        
        return com_ports
    
    def set_csv(self, csv):
        self.csv_file = csv

    def format_time(self, mission_time):
            if mission_time:
                # Convert mission_time from milliseconds to total seconds
                total_seconds = float(mission_time) / 1000.0
                hours = int(total_seconds) // 3600
                total_seconds %= 3600
                minutes = int(total_seconds) // 60
                seconds = total_seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:05.2f}"
            else:
                return "00:00:00.00"
            
    def convert_to_milliseconds(self, formatted_time):
        if formatted_time:
            try:
                hours, minutes, seconds = map(float, formatted_time.split(':'))
                total_milliseconds = (hours * 3600 + minutes * 60 + seconds) * 1000
                return int(total_milliseconds)
            except ValueError:
                raise ValueError("Invalid time format. Use 'HH:MM:SS.ss'")
        else:
            return 0