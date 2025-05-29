# app/ui.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox,
    QHBoxLayout, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush, QIcon
import logging

from app.gesture import GestureRecognizer


class GestureWorker(QThread):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.recognizer = GestureRecognizer()

    def run(self):
        logging.info("Gesture thread started")
        self.recognizer.run()  # Will run until stopped or 'q' is pressed
        self.finished.emit()

    def stop(self):
        # Stop the gesture recognizer
        if hasattr(self.recognizer, 'stop'):
            self.recognizer.stop()
        logging.info("Gesture thread stop requested")


class StatusIndicator(QFrame):
    """A colored indicator to show the current status"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(15, 15)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("border-radius: 7px; background-color: #888888;")
    
    def set_status(self, status):
        if status == "active":
            self.setStyleSheet("border-radius: 7px; background-color: #4CAF50;")
        elif status == "stopping":
            self.setStyleSheet("border-radius: 7px; background-color: #FFC107;")
        else:  # idle
            self.setStyleSheet("border-radius: 7px; background-color: #888888;")


class StyledButton(QPushButton):
    """Enhanced button with animations and better styling"""
    def __init__(self, text, parent=None, primary=True):
        super().__init__(text, parent)
        self.primary = primary
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setMinimumHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        
        # Apply appropriate style based on button type
        self.update_style()
        
    def update_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2979FF;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #1565C0;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                    color: #757575;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
                QPushButton:pressed {
                    background-color: #B71C1C;
                }
            """)


class MediaControllerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture-Based Media Controller")
        self.setGeometry(500, 300, 550, 400)
        
        # Set up gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#1A237E"))
        gradient.setColorAt(1, QColor("#303F9F"))
        
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
        # Base styling
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                color: white;
            }
            QLabel {
                color: white;
            }
            QLabel#titleLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#statusLabel {
                color: #E0E0E0;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
            }
            QFrame#contentFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
            }
        """)

        self.gesture_active = False
        self.worker_thread = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create a container frame for content
        content_frame = QFrame(self)
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(20)
        
        # Title with icon
        title = QLabel("🎮 Gesture-Based Media Controller")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        
        # Status indicator and label in a horizontal layout
        status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        self.status_label = QLabel("Status: Idle")
        self.status_label.setObjectName("statusLabel")
        
        status_layout.addWidget(self.status_indicator, 0, Qt.AlignVCenter)
        status_layout.addWidget(self.status_label, 1)
        
        # Buttons
        self.toggle_button = StyledButton("▶ Start Gesture Recognition", primary=True)
        self.toggle_button.clicked.connect(self.toggle_gesture_mode)
        
        self.quit_button = StyledButton("❌ Exit", primary=False)
        self.quit_button.clicked.connect(self.close_application)
        
        # Add widgets to content layout
        content_layout.addWidget(title)
        content_layout.addLayout(status_layout)
        content_layout.addWidget(self.toggle_button)
        content_layout.addWidget(self.quit_button)
        
        # Add content frame to main layout
        main_layout.addWidget(content_frame, 1)
        
        self.setLayout(main_layout)

    def toggle_gesture_mode(self):
        if not self.gesture_active:
            # Start gesture recognition
            self.status_label.setText("Status: Recognizing gestures...")
            self.status_indicator.set_status("active")
            self.toggle_button.setText("⏸ Stop Gesture Recognition")
            self.gesture_active = True

            # Create animation for status change
            self.animate_status_change(True)

            logging.info("Gesture Recognition Started")

            self.worker_thread = GestureWorker()
            self.worker_thread.finished.connect(self.on_thread_finished)
            self.worker_thread.start()
        else:
            # Stop gesture recognition
            self.status_label.setText("Status: Stopping...")
            self.status_indicator.set_status("stopping")
            self.toggle_button.setEnabled(False)
            
            # Create animation for status change
            self.animate_status_change(False)
            
            if self.worker_thread:
                # First stop the recognizer
                self.worker_thread.stop()
                # Then wait for the thread to finish (with timeout)
                if not self.worker_thread.wait(3000):  # 3 second timeout
                    logging.warning("Thread did not exit cleanly, forcing termination")
                    self.worker_thread.terminate()
                    self.worker_thread.wait()
            
            self.status_label.setText("Status: Idle")
            self.toggle_button.setText("▶ Start Gesture Recognition")
            self.toggle_button.setEnabled(True)
            self.status_indicator.set_status("idle")
            self.gesture_active = False
            logging.info("Gesture Recognition Stopped")

    def animate_status_change(self, starting=True):
        """Create a subtle animation when status changes"""
        # Create animation for status label
        animation = QPropertyAnimation(self.status_label, b"minimumHeight")
        animation.setDuration(300)
        animation.setStartValue(self.status_label.height())
        
        if starting:
            animation.setEndValue(self.status_label.height() + 5)
            animation.setEasingCurve(QEasingCurve.OutBounce)
        else:
            animation.setEndValue(self.status_label.height() - 5)
            animation.setEasingCurve(QEasingCurve.InOutQuad)
            
        animation.start()

    def on_thread_finished(self):
        self.status_label.setText("Status: Idle")
        self.toggle_button.setText("▶ Start Gesture Recognition")
        self.status_indicator.set_status("idle")
        self.gesture_active = False
        logging.info("Gesture thread finished.")

    def close_application(self):
        if self.gesture_active:
            # Create a styled message box
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Confirm Exit")
            message_box.setText("Gesture recognition is active. Stop it and exit?")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.No)
            
            # Style the message box
            message_box.setStyleSheet("""
                QMessageBox {
                    background-color: #303F9F;
                    color: white;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #2979FF;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1565C0;
                }
            """)
            
            reply = message_box.exec_()
            
            if reply == QMessageBox.Yes:
                # Stop gesture recognition
                if self.worker_thread:
                    self.worker_thread.stop()
                    if not self.worker_thread.wait(3000):  # 3 second timeout
                        logging.warning("Thread did not exit cleanly, forcing termination")
                        self.worker_thread.terminate()
                        self.worker_thread.wait()
                
                logging.info("Application exit requested.")
                self.close()
        else:
            logging.info("Application exit requested.")
            self.close()
            
    def resizeEvent(self, event):
        """Handle window resize events to update the gradient"""
        super().resizeEvent(event)
        
        # Update gradient on resize
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#1A237E"))
        gradient.setColorAt(1, QColor("#303F9F"))
        
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
