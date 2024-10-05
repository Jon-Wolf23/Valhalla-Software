# Required libraries
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QSizePolicy
from PySide6.QtCore import QObject, QThread, Signal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time
import numpy


class GraphDriver(QObject):
    data_updated = Signal()  # Signal to notify when new data is available

    def __init__(self, live_graph, telementary, x, y):
        super().__init__()
        self.live_graph = live_graph
        self.telementary = telementary
        self.x = x
        self.y = y
        self.running = True

    def update_data(self):
        while self.running:
            # Simulate data generation in the background
            self.live_graph.x_data = self.telementary[self.x]
            self.live_graph.y_data = self.telementary[self.y]
            
            # Emit signal to update plot in the main thread
            self.data_updated.emit()

            time.sleep(0.1)  # Simulate delay in data updates

    def stop(self):
        self.running = False


class LiveGraph(QWidget):
    def __init__(self, title, telementary, x_label, y_label, x_data, y_data):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Set up the Matplotlib Figure and FigureCanvas
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Add axes for the plot
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)

        # Initialize data lists
        self.x_data = []
        self.y_data = []

        # Initialize telementary
        self.telementary = telementary

       # Set the size policy to allow expanding and shrinking with the window
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initial plot
        self.update_plot()

        # Create worker and move it to a QThread
        self.worker = GraphDriver(self, telementary, x_data, y_data)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Connect worker's signal to the update_plot function
        self.worker.data_updated.connect(self.update_plot)

    def start(self):
        # Start the worker thread
        self.thread.started.connect(self.worker.update_data)
        self.thread.start()

    def stop(self):
        # Stop the worker thread and wait for it to finish
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()

    def update_plot(self):
        # This runs in the main thread; safe to update UI here
        self.ax.clear()
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.plot(self.x_data, self.y_data, color='blue')
        self.ax.set_xlim(left=0)

        # Redraw the canvas
        self.canvas.draw()


class InfoDriver(QObject):
    data_updated = Signal()  # Signal to notify when new data is available

    def __init__(self, live_info, telementary):
        super().__init__()
        self.live_info = live_info
        self.telementary = telementary
        self.running = True

    def update_data(self):
        while self.running:
            self.live_info.mission_time = self.telementary["mission_time"]
            self.live_info.packet_count = self.telementary["packet_count"]
            self.live_info.sw_state = self.telementary["sw_state"]
            self.live_info.pl_state = self.telementary["pl_state"]
            self.live_info.latitude = self.telementary["gps_latitude"]
            self.live_info.longitude = self.telementary["gps_longitude"]

            # Emit signal to update the info in the main thread
            self.data_updated.emit()

            time.sleep(0.1)  # Simulate delay in data updates

    def stop(self):
        self.running = False

class LiveUpdateInfo(QWidget):
    def __init__(self, telementary):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Init Values
        if not telementary["mission_time"] and not telementary["packet_count"] and not telementary["sw_state"] and not telementary["pl_state"] and not telementary["gps_latitude"] and not telementary["gps_longitude"]:
            self.mission_time = [0]
            self.packet_count = [0]
            self.sw_state = [0]
            self.pl_state = [0]
            self.latitude = [0]
            self.longitude = [0]
        else:
            self.mission_time = telementary["mission_time"]
            self.packet_count = telementary["packet_count"]
            self.sw_state = telementary["sw_state"]
            self.pl_state = telementary["pl_state"]
            self.latitude = telementary["gps_latitude"]
            self.longitude = telementary["gps_longitude"]

        # Display initial values
        self.current_mission_time = QLabel(f"Current Mission Time: {self.mission_time[-1]}")
        self.current_packet_count = QLabel(f"Current Packet Count: {self.packet_count[-1]}")
        self.current_sw_state = QLabel(f"Current Software State: {self.sw_state[-1]}")
        self.current_pl_state = QLabel(f"Current Payload State: {self.pl_state[-1]}")
        self.current_latitude = QLabel(f"Current Latitude: {self.latitude[-1]}")
        self.current_longitude = QLabel(f"Current Longitude: {self.longitude[-1]}")

        layout.addWidget(self.current_mission_time)
        layout.addWidget(self.current_packet_count)
        layout.addWidget(self.current_sw_state)
        layout.addWidget(self.current_pl_state)
        layout.addWidget(self.current_latitude)
        layout.addWidget(self.current_longitude)

        # Set size policy to be resizable
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.worker = InfoDriver(self, telementary)  # Create the data worker
        self.thread = QThread()         # Create a QThread
        self.worker.moveToThread(self.thread)

    def start(self):
        # Start the worker's update_data function when the thread starts
        self.thread.started.connect(self.worker.update_data)
        self.thread.start()

    def stop(self):
        """Stop the data update process."""
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()