# Required libraries and scripts
import sys
import csv
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QLabel,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QSplitter
)
from PySide6.QtCore import (
    Qt
)
from PySide6.QtGui import (
    QAction,
    QIcon
)
import  Serial.Ground_serial as sr
import LiveGraphing.Ground_live as gl


##################################################################################################################################
#   Sub Widgets and Dialog Windows
##################################################################################################################################

def center_on_parent(self):
        """Center the window on the parent window"""
        if self.parent is not None:
            parent_geometry = self.parent.geometry()
            parent_center_x = parent_geometry.x() + (parent_geometry.width() // 2)
            parent_center_y = parent_geometry.y() + (parent_geometry.height() // 2)

            window_x = parent_center_x - (self.width() // 2)
            window_y = parent_center_y - (self.height() // 2)

            self.move(window_x, window_y)



# Error Window pop-up, only displays an error message and a button to close it
class ErrorWindow(QDialog):
    def __init__(self, parent, err_msg):
        super().__init__()

        #Set layout and Title
        self.setWindowTitle("Error")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.parent = parent
        center_on_parent(self)

        # Init Widgits
        msg = QLabel(err_msg)
        ok = QPushButton("Ok")
        ok.setCheckable(True)
        ok.clicked.connect(self.close)

        # Add Widgits to window
        layout.addWidget(msg)
        layout.addWidget(ok)

class OpenCSV(QDialog):
    def __init__(self, parent):
        super().__init__()

        # Set Layout and title
        self.setWindowTitle("Open CSV File")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.parent = parent
        center_on_parent(self)

        # Ok and Quit buttons
        ok_quit_buttons = (
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        ) 
        self.buttonBox = QDialogButtonBox(ok_quit_buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Open file dialog to select an existing CSV file
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.selected_file = file_path
            self.label.setText(f"Selected File: {file_path}")

        # Init Widgits
        layout.addWidget(self.buttonBox)


# Setup Window, called from show_setup_window, allows user to select COM port and baud rate
class SetupWindow(QWidget):
    def __init__(self, parent, title, ports):
        super().__init__()

        # Set layout and Title
        self.setWindowTitle(title)
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.parent = parent
        center_on_parent(self)

        # Init port and baud selections
        self.port_select = QComboBox()
        items_port = [""]
        for items in ports:     # Adds blank entry to the beginnin of the ports
            items_port.append(items)
        self.port_select.addItems(items_port)
        
        self.baud_select = QComboBox()
        self.baud_select.addItems(['', '1200', '1800', '2400', '4800', '9600', '19200', '115200'])

        # Init Confirm Button
        confirm_button = QPushButton("Confirm")
        confirm_button.setCheckable(True)
        confirm_button.clicked.connect(self.confirm_port_and_baud)

        # Add Widgits
        layout.addWidget(self.port_select)
        layout.addWidget(self.baud_select)
        layout.addWidget(confirm_button)

        # Reference for the error window DO NOT REMOVE OR IT WILL NOT WORK
        self.error_window = None

    # Error checks and confirms changes to selected port and baud
    def confirm_port_and_baud(self):
        #print(self.port_select.currentText(), self.baud_select.currentText())     # Debugging Line
        if self.port_select.currentText() == '' and self.baud_select.currentText() != '':
            self.error_window = ErrorWindow(self, "Please select a COM port.")
            self.error_window.exec()
        elif self.baud_select.currentText() == '' and self.port_select.currentText() != '':
            self.error_window = ErrorWindow(self, "Please select a baud rate.")
            self.error_window.exec()
        elif self.port_select.currentText() == '' and self.baud_select.currentText() == '':
            self.error_window = ErrorWindow(self, "Please select a COM port and baud rate")
            self.error_window.exec()
        else:
            MainWindow.opened_port = self.port_select.currentText()
            MainWindow.baud_number = self.baud_select.currentText()
            self.close()

# Status Window, called from show_status_message, shows connected port and baud, I need to set it up to also display if a connection is successful
class StatusWindow(QWidget):
    def __init__(self, parent, title):
        super().__init__()
        # Set layout and title
        self.setWindowTitle(title)
        self.setFixedSize(300, 110)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.parent = parent
        center_on_parent(self)

        # Gets values for currently set port and baud
        disp_port = MainWindow.opened_port if MainWindow.opened_port else "None Selected"
        disp_baud = MainWindow.baud_number if MainWindow.baud_number else "None Selected"
        disp_csv = MainWindow.csv_filepath if MainWindow.csv_filepath else "None Selected"
            
        # Init Widgits
        port = QLabel("Opened Port: " + disp_port)
        baud = QLabel("Baud Rate: " + disp_baud)
        csv = QLabel("CSV File Path: " + disp_csv)
        ok = QPushButton("Ok")
        ok.setCheckable(True)
        ok.clicked.connect(self.close)

        # Add Widgits
        layout.addWidget(port)
        layout.addWidget(baud)
        layout.addWidget(csv)
        layout.addWidget(ok)



##################################################################################################################################
#   Main Window
##################################################################################################################################

class MainWindow(QMainWindow):
    # Shared Variables
    opened_port = "" 
    baud_number = 0

    # Graphed Data
    team_id = 1004
    mission_time = []
    packet_count = []
    sw_state = []
    pl_state = []
    altitude = []
    temp = []
    voltage = []
    gps_latitude = []
    gps_longitude = []

    # Current csv file
    csv_filepath = ""

    # State of Data Reader
    main_loop_running = False

    # Data Reader
    ground_station = None


    def __init__(self):
        super().__init__()
        # Set title and layout
        self.setWindowTitle("Ground Station")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Main layout uses QVBoxLayout, but we add QSplitters for better resizing
        main_layout = QVBoxLayout(central_widget)

        # Top and bottom layouts using QSplitter to make them resizable
        top_splitter = QSplitter(self)
        top_splitter.setOrientation(Qt.Horizontal)
        self.graph1 = gl.LiveGraph("Graph 1", "Time(s)", "Altitude(m)", MainWindow.altitude, MainWindow.mission_time)
        self.graph2 = gl.LiveGraph("Graph 2", "Time(s)", "Temperature(C)", MainWindow.temp, MainWindow.mission_time)
        top_splitter.addWidget(self.graph1)
        top_splitter.addWidget(self.graph2)

        bottom_splitter = QSplitter(self)
        bottom_splitter.setOrientation(Qt.Horizontal)
        self.graph3 = gl.LiveGraph("Graph 3", "Time(s)", "Voltage(V)", MainWindow.voltage, MainWindow.mission_time)
        self.info4 = gl.LiveUpdateInfo(MainWindow.mission_time, MainWindow.packet_count, MainWindow.sw_state, MainWindow.pl_state, MainWindow.gps_latitude, MainWindow.gps_longitude)
        bottom_splitter.addWidget(self.graph3)
        bottom_splitter.addWidget(self.info4)

        # Add the splitters to the main layout
        main_layout.addWidget(top_splitter)
        main_layout.addWidget(bottom_splitter)

        # Set stretch factors to make sure each widget resizes proportionally
        top_splitter.setStretchFactor(0, 1)  # First widget takes 50%
        top_splitter.setStretchFactor(1, 1)  # Second widget takes 50%
        bottom_splitter.setStretchFactor(0, 1)  # First widget takes 50%
        bottom_splitter.setStretchFactor(1, 1)  # Second widget takes 50%

        # Create menu bar
        self.create_menu_bar()


######################### Menu Bar #########################

    # Create menu bar, called from main, displays overhead menu and dropdowns
    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        create_file = QAction("Create", self)
        create_file.triggered.connect(self.create_csv)

        open_file = QAction("Open", self)       # Setup to open CSV for the live graphs
        open_file.triggered.connect(self.open_csv)

        close_file = QAction("Close", self)     # Setup to close CSV for the live graphs
        close_file.triggered.connect(self.close_csv)

        file_menu.addAction(exit_action)
        file_menu.addAction(create_file)
        file_menu.addAction(open_file)
        file_menu.addAction(close_file)

        # Setup menu
        setup_menu = menu_bar.addMenu("Setup")
        setup_action = QAction("Configure", self)
        setup_action.triggered.connect(self.show_setup_window)
        setup_menu.addAction(setup_action)

        # Status menu
        status_menu = menu_bar.addMenu("Status")
        status_action = QAction("Show Status", self)
        status_action.triggered.connect(self.show_status_message)
        status_menu.addAction(status_action)

        self.run_action = QAction(QIcon("GUI\\run_button.png"), "Run", self)
        self.run_action.triggered.connect(self.toggle_run_stop)
        menu_bar.addAction(self.run_action)


######################### Main Program Driver #########################

    def toggle_run_stop(self):
        # Toggle between run and Stop
        if not MainWindow.main_loop_running:
            self.start_running_serial()
            self.start_running_graphs_and_info()
        else:
            self.stop_running_serial()
            self.stop_running_graphs_and_info()

    def start_running_serial(self):
        # Set to Stop state
        MainWindow.main_loop_running = True
        self.run_action.setIcon(QIcon("GUI\\stop_button.png"))
        self.run_action.setText("Stop")
        
        if MainWindow.opened_port != '' and MainWindow.baud_number != '' and MainWindow.csv_filepath != '':
            try:
                MainWindow.ground_station = sr.DataReader(port=MainWindow.opened_port, baudrate=int(MainWindow.baud_number), csv_file=MainWindow.csv_filepath)
                if MainWindow.ground_station:
                    MainWindow.ground_station.start()
            except Exception as e:
                self.error_window = ErrorWindow(self, f"Failed to start data reading: {e}")
                self.error_window.exec()
        else:
            self.error_window = ErrorWindow(self, "Need valid COM port, baud rate, and csv filepath")
            self.error_window.exec()
            self.stop_running_serial()

    def stop_running_serial(self):
        # Set to Play state
        MainWindow.main_loop_running = False
        self.run_action.setIcon(QIcon("GUI\\run_button.png"))
        self.run_action.setText("Run")

        if MainWindow.ground_station:
            MainWindow.ground_station.stop()
            MainWindow.ground_station = None

    def start_running_graphs_and_info(self):
        self.graph1.start()
        self.graph2.start()
        self.graph3.start()
        self.info4.start()

    def stop_running_graphs_and_info(self):
        self.graph1.stop()
        self.graph2.stop()
        self.graph3.stop()
        self.info4.stop()



    
######################### Menu Bar Functions #########################

    # Called from create_menu_bar, creates a SetupWindow instance
    def show_setup_window(self):
        self.setup_window = SetupWindow(self, "Setup", sr.return_com_ports())
        self.setup_window.show()

    # Called from create_menu_bar, creates StatusWindow instance
    def show_status_message(self):
        self.status_window = StatusWindow(self, "Status")
        self.status_window.show()

    def create_csv(self):
         # Open file dialog to create a new CSV file
         file_path, _ = QFileDialog.getSaveFileName(self, "Create CSV File", "", "CSV Files (*.csv)")
         if file_path:
            MainWindow.csv_filepath = file_path

    # Function to open csv file, called by the open file action in menu bar
    def open_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.csv_filepath = file_path

         # Read the CSV content
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            
            # Iterate over the rows in the CSV file
            for row in csv_reader:
                if len(row) >= 10:  # Ensure the row has at least 5 columns
                    MainWindow.mission_time.append(row[1])     # Column 1
                    MainWindow.packet_count.append(row[2])     # Column 2
                    MainWindow.sw_state.append(row[3])  # Column 3
                    MainWindow.pl_state.append(row[4])      # Column 4
                    MainWindow.altitude.append(row[5])         # Column 5
                    MainWindow.temp.append(row[6])         # Column 6
                    MainWindow.voltage.append(row[7])         # Column 7
                    MainWindow.gps_latitude.append(row[8])         # Column 8
                    MainWindow.gps_longitude.append(row[9])     # Column 9

    
    # Function to close csv file, called by the close file action in menu bar
    def close_csv(self):
        MainWindow.csv_filepath = ''
        MainWindow.mission_time = []
        MainWindow.packet_count = []
        MainWindow.sw_state = []
        MainWindow.pl_state = []
        MainWindow.altitude = []
        MainWindow.temp = []
        MainWindow.voltage = []
        MainWindow.gps_latitude = []
        MainWindow.gps_longitude = []


    
##################################################################################################################################################################
# RUNS GROUNDSTATION
##################################################################################################################################################################

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())