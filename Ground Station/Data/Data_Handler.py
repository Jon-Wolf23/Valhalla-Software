import csv
import os
import Serial.Ground_serial as gs
import LiveGraphing.Ground_live as live

class CSV_Handler():
    def __init__(self):
        # Initialize with a target directory where files will be saved
        self.directory = "CSV Files"
        self.file = ""

    def set_csv(self, filename):
        "Set the current file name manually"
        self.file = filename

    def create_csv(self, status):
        """Creates a CSV file with the format 'status{i}.csv' in the given directory."""

        # Look for an available filename: status{i}.csv
        i = 1
        while True:
            file_path = os.path.join(self.directory, f"{status}{i}.csv")
            if not os.path.exists(file_path):
                self.file = file_path  # Save the file path
                break
            i += 1

        # Open the file in write mode and create it with headers
        with open(self.file, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Writes a header for the CSV
            writer.writerow(["TEAM_ID", "MISSION_TIME", "PACKET_COUNT", "SW_STATE", 
                             "PL_STATE", "ALTITUDE", "TEMP", "VOLTAGE", 
                             "GPS_LATITUDE", "GPS_LONGITUDE"])
            file.close()

    def open_csv(self, telementary):
        # Read the CSV content
        with open(self.directory, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            
            # Iterate over the rows in the CSV file
            for row in csv_reader:
                if len(row) >= 10:  # Ensure the row has at least 5 columns
                    telementary[0].append(row[0])   # Column 0
                    telementary[1].append(row[1])   # Column 1
                    telementary[2].append(row[2])   # Column 2
                    telementary[3].append(row[3])   # Column 3
                    telementary[4].append(row[4])   # Column 4
                    telementary[5].append(row[5])   # Column 5
                    telementary[6].append(row[6])   # Column 6
                    telementary[7].append(row[7])   # Column 7
                    telementary[8].append(row[8])   # Column 8
                    telementary[9].append(row[9])   # Column 9
                    telementary[10].append(row[10]) # Column 10
    
    def files_in_directory(self, directory):
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
class Data_Handler():
    def __init__(self):
        # Telementary Data
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

        # Serial Object
        self.ground_station = None

        # State of Main Loop
        self.running = False

        # Serial Data
        self.opened_port = None
        self.baud_rate = None
        self.ports = ['']

    def get_telementary(self):
        return self.telementary

    def clear_telementary(self):
         # Telementary Data
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

    def init_serial_object(self, port, baudrate, csv_file):
        self.ground_station = gs.SerialReader(port, baudrate, csv_file, self.telementary)

    def clear_serial_object(self):
        self.ground_station = None

    def reload_ports(self, ports):
        self.ports = ['']   # Adds blank entry to the beginning of the ports
        for items in ports:
            self.ports.append(items)
        return self.ports

