# app/ui.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
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


class MediaControllerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture-Based Media Controller")
        self.setGeometry(500, 300, 500, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f8;
                font-family: 'Segoe UI';
                font-size: 15px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLabel#statusLabel {
                color: #333;
                font-weight: bold;
                font-size: 16px;
            }
        """)

        self.gesture_active = False
        self.worker_thread = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("🎮 Gesture-Based Media Controller")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.toggle_button = QPushButton("▶ Start Gesture Recognition")
        self.toggle_button.clicked.connect(self.toggle_gesture_mode)

        self.quit_button = QPushButton("❌ Exit")
        self.quit_button.clicked.connect(self.close_application)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.status_label)
        layout.addSpacing(10)
        layout.addWidget(self.toggle_button)
        layout.addSpacing(10)
        layout.addWidget(self.quit_button)

        self.setLayout(layout)

    def toggle_gesture_mode(self):
        if not self.gesture_active:
            self.status_label.setText("Status: Recognizing gestures...")
            self.toggle_button.setText("⏸ Stop Gesture Recognition")
            self.gesture_active = True

            logging.info("Gesture Recognition Started")

            self.worker_thread = GestureWorker()
            self.worker_thread.finished.connect(self.on_thread_finished)
            self.worker_thread.start()
        else:
            self.status_label.setText("Status: Stopping...")
            self.toggle_button.setEnabled(False)
            
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
            self.gesture_active = False
            logging.info("Gesture Recognition Stopped")

    def on_thread_finished(self):
        self.status_label.setText("Status: Idle")
        self.toggle_button.setText("▶ Start Gesture Recognition")
        self.gesture_active = False
        logging.info("Gesture thread finished.")

    def close_application(self):
        if self.gesture_active:
            reply = QMessageBox.question(
                self, 
                "Confirm Exit", 
                "Gesture recognition is active. Stop it and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
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
