import sys
import time
import threading
import random
from enum import Enum
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from pynput.keyboard import Listener, Key
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QPushButton, QGroupBox, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QColor, QPalette, QIcon
import pyautogui
import ctypes
import os

def perform_click(click_type, is_double):
    """Separate process for click operations"""
    if is_double:
        pyautogui.doubleClick(button=click_type)
    else:
        pyautogui.click(button=click_type)

class ClickType(Enum):
    LEFT = 'left'
    RIGHT = 'right'
    MIDDLE = 'middle'

# Main autoclicker engine that handles clicking mechanics
class AutoClicker(QObject):
    state_changed = pyqtSignal(bool)
    settings_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.config = {
            'interval': 1.0,  # Changed to 1.0 second default
            'click_type': ClickType.LEFT,
            'double_click': False,
            'max_clicks': None,
            'hotkey': Key.f6,
            'exit_key': Key.f12,
            'randomize': False,  
            'random_range': 0.5,  # Random variation ±50% of interval
            'process_count': min(4, multiprocessing.cpu_count())  # setting for process count
        }
        self.running = False
        self.click_thread = None
        self.listener = None
        self.click_count = 0
        self.executor = None

    def set_config(self, config):
        self.config = config
        self.settings_updated.emit(config)

    def start_clicking(self):
        if not self.running:
            self.running = True
            self.state_changed.emit(True)
            self.executor = ProcessPoolExecutor(max_workers=self.config['process_count'])
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()

    # Main clicking loop - handles timing and click execution
    def click_loop(self):
        base_interval = self.config['interval']
        click_type = self.config['click_type'].value
        max_clicks = self.config['max_clicks']
        double_click = self.config['double_click']
        randomize = self.config['randomize']
        random_range = self.config['random_range']
        
        while self.running and (max_clicks is None or self.click_count < max_clicks):
            # Submit click operation to process pool
            future = self.executor.submit(
                perform_click,
                click_type,
                double_click
            )
            
            # Handle the click completion
            try:
                future.result(timeout=base_interval)  # Wait for click to complete
                self.click_count += 1
            except Exception as e:
                print(f"Click operation failed: {e}")
            
            # Calculate sleep time
            if randomize:
                min_interval = base_interval * (1 - random_range)
                max_interval = base_interval * (1 + random_range)
                sleep_time = random.uniform(min_interval, max_interval)
            else:
                sleep_time = base_interval
            
            time.sleep(sleep_time)

    def stop_clicking(self):
        if self.running:
            self.running = False
            self.click_count = 0
            if self.executor:
                self.executor.shutdown(wait=False)
                self.executor = None
            self.state_changed.emit(False)

    def on_press(self, key):
        try:
            # Convert string representation of F-keys to actual Key objects
            if hasattr(key, 'name'):  # Handle special keys
                pressed_key = key
            else:  # Handle regular keys
                pressed_key = key.char

            if pressed_key == self.config['hotkey']:
                if self.running:
                    self.stop_clicking()
                else:
                    self.start_clicking()
            elif pressed_key == self.config['exit_key']:
                self.stop_clicking()  # Only stop clicking, don't exit
        except AttributeError:
            pass

class KeyboardListenerThread(QThread):
    def __init__(self, clicker):
        super().__init__()
        self.clicker = clicker
        self.listener = Listener(on_press=self.clicker.on_press)

    def run(self):
        self.listener.start()
        self.exec()

# Modern GUI implementation with drag support and custom styling
class AutoclickerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.clicker = AutoClicker()
        self.clicker.state_changed.connect(self.update_status)
        self.clicker.settings_updated.connect(self.load_config)
        self.dragging = False
        self.offset = None
        
        # Set the window icon
        icon_path = 'icon.ico'
        if getattr(sys, 'frozen', False):  # Check if running as a bundle
            icon_path = os.path.join(sys._MEIPASS, icon_path)  # Use temp directory
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)
        
        self.init_ui()
        self.start_listener()

    # Window drag functionality
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging and self.offset:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def init_ui(self):
        self.setWindowTitle("AutoClicker")
        self.setFixedSize(400, 550)  # Reduced height since we removed a button
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main frame
        main_frame = QWidget(self)
        main_frame.setObjectName("mainFrame")
        main_frame.setGeometry(0, 0, 400, 550)
        
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)  # Add consistent spacing
        
        # Title with centered alignment
        title = QLabel("Chun's AutoClicker v2")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; color: white; background: rgba(0,0,0,0); padding: 15px;")
        main_layout.addWidget(title)

        # Config group
        self.config_group = QGroupBox()
        config_layout = QVBoxLayout()
        config_layout.setSpacing(10)  # Consistent spacing between config items
        self.create_config_widget(config_layout, "Interval (seconds)", key="interval", element=QDoubleSpinBox, min=0.01, max=10.0, default=1.0, step=0.01)
        self.create_config_widget(config_layout, "Click Type", key="click_type", element=QComboBox, options=[t.name for t in ClickType], default="LEFT")
        self.create_config_widget(config_layout, "Double Click", key="double_click", element=QCheckBox)
        self.create_config_widget(config_layout, "Randomize Timing", key="randomize", element=QCheckBox)
        self.create_config_widget(config_layout, "Random Range (%)", key="random_range", element=QSpinBox, min=1, max=100, default=50)
        self.create_config_widget(config_layout, "Max Clicks", key="max_clicks", element=QSpinBox, min=0, max=1_000_000, default=0)
        self.hotkey_widget = self.create_config_widget(config_layout, "Hotkey", key="hotkey", element=QComboBox, options=["F6", "F7", "F8", "F9"], default="F6")
        self.exitkey_widget = self.create_config_widget(config_layout, "Exit Key", key="exit_key", element=QComboBox, options=["F12", "ESC", "F10", "F11"], default="F12")
        self.create_config_widget(config_layout, "Process Count", key="process_count", element=QSpinBox, min=1, max=multiprocessing.cpu_count(), default=min(4, multiprocessing.cpu_count()))

        self.config_group.setLayout(config_layout)
        main_layout.addWidget(self.config_group)

        # Status label with center alignment
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: white; background: rgba(0,0,0,0); padding: 10px; margin-bottom: 10px;")
        main_layout.addWidget(self.status_label)

        # Exit button in center
        exit_button = QPushButton("Exit")
        exit_button.setObjectName("exit")
        exit_button.setFixedWidth(200)  # Fixed width for better appearance
        exit_button.clicked.connect(QApplication.quit)
        
        # Center the exit button using a horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(exit_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.setStyleSheet("""
            #mainFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(40,44,52,255),
                    stop:1 rgba(44,47,51,255));
                border: 2px solid #4a9eff;
                border-radius: 14px;
            }
            QWidget {
                background: transparent;
                color: white;
            }
            QGroupBox {
                background: rgba(44,47,51,200);
                border: 2px solid #4a9eff;
                border-radius: 10px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #4a9eff;
                font-weight: bold;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                background: rgba(44,47,51,235);
                border: 1px solid #4a9eff;
                padding: 5px;
                border-radius: 5px;
                color: white;
                min-height: 25px;
            }
            QCheckBox {
                spacing: 5px;
                background: transparent;
            }
            QPushButton#exit {
                background: #e63946;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton#exit:hover {
                background: #ff4d5e;
            }
            QLabel {
                padding: 5px 0;
                color: #ffd60a;
                font-weight: bold;
                background: transparent;
            }
        """)

    # Helper function to create and configure UI elements with consistent styling
    def create_config_widget(self, layout, label_text, key, element, **kwargs):
        widget = None
        row_layout = QHBoxLayout()
        label = QLabel(label_text + ":")
        row_layout.addWidget(label)
        if element == QSpinBox:
            defaults = {'min': 0, 'max': 9999, 'default': 0}
            defaults.update(kwargs)
            widget = element()
            widget.setRange(defaults['min'], defaults['max'])
            widget.setValue(defaults['default'])
            widget.valueChanged.connect(lambda val, k=key: self.update_config(k, val))
        elif element == QDoubleSpinBox:  # Add support for QDoubleSpinBox
            defaults = {'min': 0.0, 'max': 10.0, 'default': 1.0, 'step': 0.1}
            defaults.update(kwargs)
            widget = element()
            widget.setRange(defaults['min'], defaults['max'])
            widget.setValue(defaults['default'])
            widget.setSingleStep(defaults['step'])
            widget.setDecimals(2)
            widget.valueChanged.connect(lambda val, k=key: self.update_config(k, val))
        elif element == QComboBox:
            widget = element()
            widget.addItems(kwargs['options'])
            widget.setCurrentText(kwargs['default'])
            widget.currentIndexChanged.connect(lambda: self.update_config(key, widget.currentText()))
        elif element == QCheckBox:
            widget = element(label_text)
            widget.setChecked(kwargs.get('default', False))
            widget.toggled.connect(lambda val: self.update_config(key, val))
        else:
            widget = element()
            widget.setText(kwargs.get('default', ""))
            widget.textChanged.connect(lambda text: self.update_config(key, text))
        row_layout.addWidget(widget)
        row_layout.setStretch(1, 2)
        layout.addLayout(row_layout)
        return widget

    # Update configuration when user changes settings
    def update_config(self, key, value):
        if key == 'click_type':
            try:
                value = ClickType[value.upper()]
            except KeyError:
                value = ClickType.LEFT
        elif key == 'hotkey':
            try:
                # Map F-key strings to actual Key objects
                key_map = {
                    'F6': Key.f6,
                    'F7': Key.f7,
                    'F8': Key.f8,
                    'F9': Key.f9
                }
                value = key_map.get(value, Key.f6)
            except KeyError:
                value = Key.f6
        elif key == 'exit_key':
            try:
                # Map F-key strings to actual Key objects
                key_map = {
                    'F12': Key.f12,
                    'ESC': Key.esc,
                    'F10': Key.f10,
                    'F11': Key.f11
                }
                value = key_map.get(value, Key.f12)
            except KeyError:
                value = Key.f12
        elif key == 'random_range':
            value = value / 100.0  # Convert percentage to decimal
        elif key == 'interval':
            value = float(value)  # Ensure interval is float
        elif key in ['interval', 'max_clicks']:
            value = value / 100 if key == 'interval' else value if value != 0 else None
        
        self.clicker.config[key] = value

    def load_config(self, config):
        self.clicker.set_config(config)

    def update_status(self, running):
        self.status_label.setText(f"Status: {'Running' if running else 'Stopped'}")
        state = not running
        self.config_group.setEnabled(state)

    def start_listener(self):
        self.listener_thread = KeyboardListenerThread(self.clicker)
        self.listener_thread.start()

    def closeEvent(self, event):
        """Ensure proper cleanup when closing the application"""
        if self.clicker:
            self.clicker.stop_clicking()
        if hasattr(self, 'listener_thread'):
            self.listener_thread.quit()
        event.accept()

if __name__ == '__main__':
    # Enable multiprocessing support for Windows
    multiprocessing.freeze_support()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set app icon
    app_icon = QIcon('icon.ico')
    app.setWindowIcon(app_icon)
    
    # Set the app ID for Windows taskbar icon
    if sys.platform == 'win32':
        myappid = 'mycompany.autoclicker.v2.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0, 0))
    app.setPalette(palette)
    gui = AutoclickerGUI()
    gui.show()
    sys.exit(app.exec_())