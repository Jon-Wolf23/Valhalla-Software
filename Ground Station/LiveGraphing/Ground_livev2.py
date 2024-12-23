import sys
import random                                                                             
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QSizePolicy
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class LiveGraph(QWidget):
    def __init__(self, graph_title, x_label, y_label):
        super().__init__()

        # Layout setup
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Matplotlib Figure and Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        # Set the size policy to allow expanding and shrinking with the window
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initialize the Matplotlib axes with provided titles and labels
        self.ax = self.figure.add_subplot(111)
        self.graph_title = graph_title  # Store the title
        self.x_label = x_label  # Store x-axis label
        self.y_label = y_label  # Store y-axis label
        
        self.ax.set_title(self.graph_title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.grid(True)

        # Initialize empty lists for storing x and y values
        self.x_values = []
        self.y_values = []

    def update_graph(self, x_values, y_values):
        """Update the plot with the provided data."""
        
        self.x_values = x_values[-15:]
        self.y_values = y_values[-15:]

        # Clear and re-plot the data
        self.ax.cla()
        self.ax.plot(self.x_values, self.y_values, color="blue")
        self.ax.set_title(self.graph_title)  # Restore the title
        self.ax.set_xlabel(self.x_label)  # Restore x-axis label
        self.ax.set_ylabel(self.y_label)  # Restore y-axis label
        self.ax.grid(True)

        # Redraw the canvas
        self.canvas.draw()




class LiveData(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Labels for each piece of data
        self.mission_time_label = QLabel("Mission Time: --:--:--.--")
        self.packet_count_label = QLabel("Packet Count: --")
        self.software_state_label = QLabel("Software State: N/A")
        self.payload_state_label = QLabel("Payload State: N/A")
        self.gps_latitude_label = QLabel("GPS Latitude: --.--")
        self.gps_longitude_label = QLabel("GPS Longitude: --.--")

        # Create a bold font
        bold_font = QFont()
        bold_font.setBold(True)

        # Set the bold font for each label
        self.mission_time_label.setFont(bold_font)
        self.packet_count_label.setFont(bold_font)
        self.software_state_label.setFont(bold_font)
        self.payload_state_label.setFont(bold_font)
        self.gps_latitude_label.setFont(bold_font)
        self.gps_longitude_label.setFont(bold_font)

        # Add labels to the layout
        layout.addWidget(self.mission_time_label)
        layout.addWidget(self.packet_count_label)
        layout.addWidget(self.software_state_label)
        layout.addWidget(self.payload_state_label)
        layout.addWidget(self.gps_latitude_label)
        layout.addWidget(self.gps_longitude_label)


    def update_labels(self, mission_time, packet_count, sw_state, pl_state, gps_latitude, gps_longitude):
        """Update the values of the labels with real data."""

        # Initialize real data variables
        self.mission_time = mission_time[-1] if mission_time else None
        self.packet_count = packet_count[-1] if packet_count else None
        self.sw_state = sw_state[-1] if sw_state else None
        self.payload_state = pl_state[-1] if pl_state else None
        self.gps_latitude = gps_latitude[-1] if gps_latitude else None
        self.gps_longitude = gps_longitude[-1] if gps_longitude else None

        if self.mission_time:
            self.mission_time_label.setText(f"Mission Time: {self.format_time()}")
            self.packet_count_label.setText(f"Packet Count: {self.packet_count}")
            self.software_state_label.setText(f"Software State: {self.sw_state}")
            self.payload_state_label.setText(f"Payload State: {self.payload_state}")
            self.gps_latitude_label.setText(f"GPS Latitude: {self.gps_latitude:.4f}")
            self.gps_longitude_label.setText(f"GPS Longitude: {self.gps_longitude:.4f}")
        else:
            self.mission_time_label.setText("Mission Time: 00:00:00.00")
            self.packet_count_label.setText("Packet Count: 0")
            self.software_state_label.setText("Software State: Unknown")
            self.payload_state_label.setText("Payload State: Unknown")
            self.gps_latitude_label.setText("GPS Latitude: 0.0000")
            self.gps_longitude_label.setText("GPS Longitude: 0.0000")

    def format_time(self):
        if self.mission_time:
            # Convert mission_time from milliseconds to total seconds
            total_seconds = self.mission_time / 1000.0
            hours = int(total_seconds) // 3600
            total_seconds %= 3600
            minutes = int(total_seconds) // 60
            seconds = total_seconds % 60
            return f"{hours:02}:{minutes:02}:{seconds:05.2f}"
        else:
            return "00:00:00.00"