# Required libraries and scripts
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QDialog,
    QLineEdit,
    QSplitter,
)
from PySide6.QtCore import (
    Qt,
    Signal
)
from PySide6.QtGui import (
    QAction,
    QIcon
)
import  Serial.Ground_serial as sr
import LiveGraphing.Ground_livev2 as gl
import Data.Data_Handler as data

## OBJECT DECLARATIONS
csv_handler = data.CSV_Handler()
serial = sr.SerialReader()

class MainWindow(QMainWindow):
    window_closed = Signal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ground Station")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Main layout uses QVBoxLayout, but we add QSplitters for better resizing
        main_layout = QVBoxLayout(central_widget)

        # Icon
        self.setWindowIcon(QIcon(r'GUI\wolf_icon.ico'))

        # Top and bottom layouts using QSplitter to make them resizable
        top_splitter = QSplitter(self)
        top_splitter.setOrientation(Qt.Horizontal)
        self.graph1 = gl.LiveGraph("Altitude", "Time(ms)", "Altitude(m)")
        self.graph2 = gl.LiveGraph("Temperature", "Time(ms)", "Temperature(C)")
        top_splitter.addWidget(self.graph1)
        top_splitter.addWidget(self.graph2)

        bottom_splitter = QSplitter(self)
        bottom_splitter.setOrientation(Qt.Horizontal)
        self.graph3 = gl.LiveGraph("Voltage", "Time(ms)", "Voltage(V)")
        self.info4 = gl.LiveData()
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

        # Serial Callback
        serial.register_callback(self.update_data)

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)

        


######################### Menu Bar #########################

    # Create menu bar, called from main, displays overhead menu and dropdowns
    def create_menu_bar(self):
        self.menu_bar = self.menuBar()

        # File menu
        file_menu = self.menu_bar.addMenu("File")
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
        setup_menu = self.menu_bar.addMenu("Setup/Status")
        setup_action = QAction("Configure", self)
        setup_action.triggered.connect(self.show_setup_window)
        setup_menu.addAction(setup_action)
        status_action = QAction("Show Status", self)
        status_action.triggered.connect(self.show_status_message)
        setup_menu.addAction(status_action)

        self.run_serial = QAction("Run Serial")
        self.run_serial.triggered.connect(self.toggle_serial)
        self.menu_bar.addAction(self.run_serial)

######################### Menu Bar Functions #########################

    # Called from create_menu_bar, creates a SetupWindow instance
    def show_setup_window(self):
        if serial.running == False:
            self.setup_window = SetupWindow(self, "Setup")
            self.setup_window.show()

    # Called from create_menu_bar, creates StatusWindow instance
    def show_status_message(self):
        self.status_window = StatusWindow(self, "Status")
        self.status_window.show()

    def create_csv(self):
        if serial.running == False:
            self.create_window = CreateCSV(self)
            self.create_window.show()

    # Function to open csv file, called by the open file action in menu bar
    def open_csv(self):
        if serial.running == False:
            self.open_window = OpenCSV(self, "CSV Files")
            self.open_window.csv_opened.connect(self.update_data)
            self.open_window.show()
    
    # Function to close csv file, called by the close file action in menu bar
    def close_csv(self):
        if serial.running == False:
            serial.telementary, serial.current_error, serial.current_status, serial.csv_file = csv_handler.close_csv(serial.telementary, serial.current_error, serial.current_status, serial.csv_file)
            self.update_data()

    def update_data(self):
        self.graph1.update_graph(serial.telementary["mission_time"], serial.telementary["altitude"])
        self.graph2.update_graph(serial.telementary["mission_time"], serial.telementary["temp"])
        self.graph3.update_graph(serial.telementary["mission_time"], serial.telementary["voltage"])
        self.info4.update_labels(serial.telementary["mission_time"],
                                 serial.telementary["packet_count"],
                                 serial.telementary["sw_state"],
                                 serial.telementary["pl_state"],
                                 serial.telementary["gps_latitude"],
                                 serial.telementary["gps_longitude"])


######################### Main Program Driver #########################

    def toggle_serial(self):
        if serial.running == False:
            if serial.opened_port != '' and serial.baud_rate != '' and csv_handler.file != '':
                print(f"Starting serial thread with port: {serial.opened_port}, baudrate: {serial.baud_rate}, csv: {csv_handler.file}")
                self.run_serial.setText("Stop Serial")
                serial.start()
            else:
                self.error_window = ErrorWindow(self, "Need valid COM port, baud rate, and csv filepath")
                self.error_window.exec()
        else:
            if serial.running:
                self.run_serial.setText("Run Serial")
                serial.stop()






##################################################################################################################################
#   Sub Widgets and Dialog Windows
##################################################################################################################################

def center_on_parent(self):
    """Center the window on the parent window"""
    if self.parent is not None:
        # Get geometry of parent window (returns QRect)
        parent_geometry = self.parent.geometry()

        # Calculate the center point of the parent window
        parent_center_x = parent_geometry.x() + (parent_geometry.width() // 2)
        parent_center_y = parent_geometry.y() + (parent_geometry.height() // 2)

        # Calculate the top-left corner of the child window (self)
        window_x = parent_center_x - (self.width() // 2)
        window_y = parent_center_y - (self.height() // 2)

        # Move the child window to the calculated position
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
        self.setWindowIcon(QIcon(r'GUI\wolf_icon.ico'))

        # Init Widgits
        msg = QLabel(err_msg)
        ok = QPushButton("Ok")
        ok.setCheckable(True)
        ok.clicked.connect(self.close)

        # Add Widgits to window
        layout.addWidget(msg)
        layout.addWidget(ok)


class OpenCSV(QWidget):
    csv_opened = Signal()
    def __init__(self, parent, directory):
        super().__init__()

        # Set Layout and title
        self.setWindowTitle("Open CSV File")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(300, 100)
        self.parent = parent
        center_on_parent(self)
        self.setWindowIcon(QIcon(r'GUI\wolf_icon.ico'))

        files = [""]
        files.extend(csv_handler.files_in_directory(directory))
        self.file_select = QComboBox()
        self.file_select.addItems(files)
        
        confirm_button = QPushButton("Confirm")
        confirm_button.setCheckable(True)
        confirm_button.clicked.connect(self.open_csv)


        layout.addWidget(self.file_select)
        layout.addWidget(confirm_button)

    def open_csv(self):
        csv_handler.file = csv_handler.set_csv(self.file_select.currentText())
        serial.set_csv(csv_handler.file)
        csv_handler.open_csv(serial.telementary)
        #print(f"Updated Telementary: {serial.telementary}") # Debugging Line
        self.csv_opened.emit()
        self.close()

        

class CreateCSV(QWidget):
    def __init__(self, parent):
        super().__init__()

        # Set Layout and title
        self.setWindowTitle("Create CSV File")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(300, 100)
        self.parent = parent
        center_on_parent(self)
        self.setWindowIcon(QIcon(r'GUI\wolf_icon.ico'))

        self.new_file = QLineEdit("Test")
        
        confirm_button = QPushButton("Confirm")
        confirm_button.setCheckable(True)
        confirm_button.clicked.connect(self.create_csv)


        layout.addWidget(self.new_file)
        layout.addWidget(confirm_button)

    def create_csv(self):
        csv_handler.create_csv(self.new_file.text())
        serial.set_csv(csv_handler.file)
        self.close()


# Setup Window, called from show_setup_window, allows user to select COM port and baud rate
class SetupWindow(QWidget):
    def __init__(self, parent, title):
        super().__init__()

        # Set layout and Title
        self.setWindowTitle(title)
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.parent = parent
        center_on_parent(self)
        self.setWindowIcon(QIcon(r'GUI\wolf_icon.ico'))

        ports = ['']
        ports.extend(serial.return_com_ports())

        # Init port and baud selections
        self.port_select = QComboBox()
        self.port_select.addItems(ports)
        
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
            serial.opened_port= self.port_select.currentText()
            serial.baud_rate = self.baud_select.currentText()
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
        self.setWindowIcon(QIcon(r'GUI\wolf_icon.ico'))

        # Gets values for currently set port and baud
        disp_port = serial.opened_port if serial.opened_port else "None Selected"
        disp_baud = serial.baud_rate if serial.baud_rate else "None Selected"
        disp_csv = csv_handler.file if csv_handler.file else "None Selected"
            
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






##################################################################################################################################################################
# RUNS GROUNDSTATION
##################################################################################################################################################################

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.window_closed.connect(serial.stop)
    window.show()
    sys.exit(app.exec())