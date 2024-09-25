import serial
import time
import random
import string

# Serial connection configuration (adjust based on your actual setup)
SERIAL_PORT = '/dev/ttyUSB0'  # Replace with your actual port (e.g., COM3 on Windows)
BAUD_RATE = 9600  # Match this with your receiving device's baud rate

TEAM_ID = "TEAM1234"  # Example team ID

def generate_telemetry_data(packet_count):
    """
    Generate a telemetry packet with random/fake data.
    Fields: TEAM_ID, MISSION_TIME, PACKET_COUNT, SW_STATE, PL_STATE, ALTITUDE, TEMP, VOLTAGE, GPS_LAT, GPS_LONG
    """
    mission_time = int(time.time())  # Mission time in seconds since epoch
    sw_state = random.choice(['IDLE', 'ACTIVE', 'ERROR'])
    pl_state = random.choice(['STANDBY', 'DEPLOYED', 'OFF'])
    altitude = random.uniform(1000, 40000)  # Altitude in meters
    temperature = random.uniform(-50, 50)  # Temperature in Celsius
    voltage = random.uniform(3.0, 12.0)  # Voltage in volts
    gps_latitude = random.uniform(-90.0, 90.0)
    gps_longitude = random.uniform(-180.0, 180.0)
    
    telemetry_packet = f"{TEAM_ID},{mission_time},{packet_count},{sw_state},{pl_state},{altitude:.2f},{temperature:.2f},{voltage:.2f},{gps_latitude:.6f},{gps_longitude:.6f}"
    return telemetry_packet

def main():
    try:
        # Open the serial connection
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            packet_count = 0
            while True:
                telemetry_packet = generate_telemetry_data(packet_count)
                ser.write(telemetry_packet.encode('utf-8'))  # Send data over serial
                print(f"Sent: {telemetry_packet}")  # Print the sent packet for debug
                packet_count += 1
                time.sleep(1)  # Simulate 1-second delay between packets
    except KeyboardInterrupt:
        print("Transmission interrupted by user.")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()