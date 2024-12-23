import csv
import os

class CSV_Handler():
    def __init__(self):
        # Initialize with a target directory where files will be saved
        self.directory = "CSV Files"
        self.file = ""

    def set_csv(self, filename):
        "Set the current file name manually"
        file = self.directory + '/' + filename
        return file

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
        try:
            with open(self.file, mode='w', newline='', buffering=1) as file:  # Using buffered I/O
                writer = csv.writer(file)
                writer.writerow([
                    "TEAM_ID", "MISSION_TIME", "PACKET_COUNT", "SW_STATE", "PL_STATE", 
                    "ALTITUDE", "PRESSURE", "TEMP", "VOLTAGE", "GPS_LATITUDE", "GPS_LONGITUDE"
                ])
        except IOError as e:
            print(f"Error creating CSV file: {e}")

    def open_csv(self, telementary):
        """Reads CSV data incrementally and appends it to the telementary dictionary."""
        #print(f"Trying to open CSV file: {self.file}")  # Debugging line
        try:
            with open(self.file, newline='', encoding='utf-8', buffering=1) as csvfile:
                csv_reader = csv.reader(csvfile)
                
                # Skip the header row
                next(csv_reader)

                for row in csv_reader:
                    if len(row) >= 10:
                        telementary["team_id"].append(int(row[0]))
                        telementary["mission_time"].append(self.convert_to_milliseconds(row[1]))
                        telementary["packet_count"].append(float(row[2]))
                        telementary["sw_state"].append(row[3])
                        telementary["pl_state"].append(row[4])
                        telementary["altitude"].append(float(row[5]))
                        telementary["pressure"].append(float(row[6]))
                        telementary["temp"].append(float(row[7]))
                        telementary["voltage"].append(float(row[8]))
                        telementary["gps_latitude"].append(float(row[9]))
                        telementary["gps_longitude"].append(float(row[10]))
                        #print(f"Read row: {row}")
                    
                #print(f"Read CSV file: {self.file}") # Debugging Line

                return telementary
        except FileNotFoundError:
            print(f"File not found: {self.file}")
        except IOError as e:
            print(f"Error reading CSV file: {e}")
    
            
    def close_csv(self, telementary, current_error, current_status, csv):
        # Resetting the values
        csv = ""
        telementary = {
            "team_id": [],
            "mission_time": [],
            "packet_count": [],
            "sw_state": [],
            "pl_state": [],
            "altitude": [],
            "pressure": [],
            "temp": [],
            "voltage": [],
            "gps_latitude": [],
            "gps_longitude": []
        }

        current_error = ""
        current_status = ""

        # Returning the modified values
        return telementary, current_error, current_status, csv
    
    def files_in_directory(self, directory):
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
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