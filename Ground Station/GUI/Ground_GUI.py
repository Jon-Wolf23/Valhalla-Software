# Required libraries
import sys
import csv
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QLabel
)
from PySide6.QtCore import (
    Qt
)
from PySide6.QtGui import (
    QAction
)
import  Serial.Ground_serial as sr

# Error Window pop-up, only displays an error message and a button to close it
class ErrorWindow(QWidget):
    def __init__(self, err_msg):
        super().__init__()

        #Set layout and Title
        self.setWindowTitle("Error")
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Init Widgits
        msg = QLabel(err_msg)
        ok = QPushButton("Ok", parent=self)
        ok.setCheckable(True)
        ok.clicked.connect(self.close)

        # Add Widgits to window
        layout.addWidget(msg)
        layout.addWidget(ok)


# Setup Window, called from show_setup_window, allows user to select COM port and baud rate
class SetupWindow(QWidget):
    def __init__(self, title, ports):
        super().__init__()

        # Set layout and Title
        self.setWindowTitle(title)
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Init port and baud selections
        self.port_select = QComboBox()
        items_port = [""]
        for items in ports:     # Adds blank entry to the beginnin of the ports
            items_port.append(items)
        self.port_select.addItems(items_port)
        
        self.baud_select = QComboBox()
        self.baud_select.addItems(['', '1200', '1800', '2400', '4800', '9600', '19200', '115200'])

        # Init Confirm Button
        confirm_button = QPushButton("Confirm", parent=self)
        confirm_button.setCheckable(True)
        confirm_button.clicked.connect(self, self.confirm_port_and_baud)

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
            self.error_window = ErrorWindow("Please select a COM port.")
            self.error_window.show()
        elif self.baud_select.currentText() == '' and self.port_select.currentText() != '':
            self.error_window = ErrorWindow("Please select a baud rate.")
            self.error_window.show()
        elif self.port_select.currentText() == '' and self.baud_select.currentText() == '':
            self.error_window = ErrorWindow("Please select a COM port and baud rate")
            self.error_window.show()
        else:
            MainWindow.opened_port = self.port_select.currentText()
            MainWindow.baud_number = self.baud_select.currentText()
            self.close()

# Status Window, called from show_status_message, shows connected port and baud, I need to set it up to also display if a connection is successful
class StatusWindow(QWidget):
    def __init__(self, title):
        super().__init__()
        # Set layout and title
        self.setWindowTitle(title)
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Gets values for currently set port and baud
        disp_port = MainWindow.opened_port if MainWindow.opened_port else "None Selected"
        disp_baud = MainWindow.baud_number if MainWindow.baud_number else "None Selected"
            
        # Init Widgits
        port = QLabel("Opened Port: " + disp_port)
        baud = QLabel("Baud Rate: " + disp_baud)
        ok = QPushButton("ok", parent=self)
        ok.setCheckable(True)
        ok.clicked.connect(self.close)

        # Add Widgits
        layout.addWidget(port)
        layout.addWidget(baud)
        layout.addWidget(ok)

# Place holder for live graph
class GraphPlaceholder(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

# Main Window
class MainWindow(QMainWindow):
    # Shared Variables
    opened_port = ""
    baud_number = ""

    def __init__(self):
        super().__init__()
        # Set title and layout
        self.setWindowTitle("Ground Station")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and set the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top row for the first two graphs
        top_layout = QHBoxLayout()
        graph1 = GraphPlaceholder("Graph 1")
        graph2 = GraphPlaceholder("Graph 2")
        top_layout.addWidget(graph1)
        top_layout.addWidget(graph2)

        # Bottom row for the last two graphs
        bottom_layout = QHBoxLayout()
        graph3 = GraphPlaceholder("Graph 3")
        graph4 = GraphPlaceholder("Graph 4")
        bottom_layout.addWidget(graph3)
        bottom_layout.addWidget(graph4)

        # Add top and bottom layouts to the main layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        # Create menu bar
        self.create_menu_bar()

    # Create menu bar, called from main, displays overhead menu and dropdowns
    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)

        open_file = QAction("Open", self)       # Setup to open CSV for the live graphs
        open_file.triggered.connect(self.open_csv)           # Finish in a bit, not finished

        close_file = QAction("Close", self)     # Setup to close CSV for the live graphs
        close_file.triggered.connect(self.close_csv)          # Finish in a bit, not finished

        file_menu.addAction(exit_action)
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

    # Called from create_menu_bar, creates a SetupWindow instance
    def show_setup_window(self):
        self.setup_window = SetupWindow("Setup", sr.return_com_ports())
        self.setup_window.show()

    # Called from create_menu_bar, creates StatusWindow instance
    def show_status_message(self):
        self.status_window = StatusWindow("Status")
        self.status_window.show()

    # Function to open csv file, called by the open file action in menu bar
    def open_csv(self, file_name):
        return      # Finish when live graphing is finished
    
    # Function to close csv file, called by the close file action in menu bar
    def close_csv(self, file_name):
        return      # Finish when live graphing is finished


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())