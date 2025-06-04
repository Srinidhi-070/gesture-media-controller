# app/ui.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox,
    QHBoxLayout, QFrame, QSizePolicy, QFileDialog, QGroupBox,
    QRadioButton, QButtonGroup, QTextEdit, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush, QIcon, QPixmap, QImage, QKeySequence
import logging
import cv2
import numpy as np
import os

from app.gesture import GestureRecognizer
from app.config import SUPPORTED_VIDEO_FORMATS


class GestureWorker(QThread):
    finished = pyqtSignal()
    gesture_detected = pyqtSignal(str, int)
    frame_processed = pyqtSignal(object)
    status_update = pyqtSignal(str)

    def __init__(self, video_source=None):
        super().__init__()
        self.recognizer = GestureRecognizer(video_source)
        
        # Connect signals
        self.recognizer.gesture_detected.connect(self.gesture_detected.emit)
        self.recognizer.frame_processed.connect(self.frame_processed.emit)
        self.recognizer.status_update.connect(self.status_update.emit)

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
        self.setGeometry(300, 200, 900, 700)
        
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
        self.video_source = None  # None for camera, path for video file
        self.current_gesture = "No gesture detected"
        self.gesture_log = []

        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Left panel for controls
        left_panel = self.create_control_panel()
        
        # Right panel for video display and gesture info
        right_panel = self.create_display_panel()
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        self.setLayout(main_layout)
    
    def create_control_panel(self):
        """Create the left control panel"""
        control_frame = QFrame(self)
        control_frame.setObjectName("contentFrame")
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(20)
        
        # Title with icon
        title = QLabel("🎮 Gesture Controller")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        
        # Video source selection
        source_group = QGroupBox("Video Source")
        source_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        source_layout = QVBoxLayout(source_group)
        
        # Radio buttons for source selection
        self.source_group = QButtonGroup()
        self.camera_radio = QRadioButton("Camera")
        self.video_radio = QRadioButton("Video File")
        self.camera_radio.setChecked(True)
        
        self.camera_radio.setStyleSheet("QRadioButton { color: white; }")
        self.video_radio.setStyleSheet("QRadioButton { color: white; }")
        
        self.source_group.addButton(self.camera_radio, 0)
        self.source_group.addButton(self.video_radio, 1)
        
        # Video file selection
        file_layout = QHBoxLayout()
        self.video_path_label = QLabel("No file selected")
        self.video_path_label.setStyleSheet("color: #E0E0E0; font-size: 12px;")
        self.browse_button = StyledButton("Browse", primary=True)
        self.browse_button.clicked.connect(self.browse_video_file)
        self.browse_button.setEnabled(False)
        
        file_layout.addWidget(self.video_path_label, 1)
        file_layout.addWidget(self.browse_button)
        
        source_layout.addWidget(self.camera_radio)
        source_layout.addWidget(self.video_radio)
        source_layout.addLayout(file_layout)
        
        # Connect radio button signals
        self.camera_radio.toggled.connect(self.on_source_changed)
        self.video_radio.toggled.connect(self.on_source_changed)
        
        # Status indicator and label
        status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        self.status_label = QLabel("Status: Idle")
        self.status_label.setObjectName("statusLabel")
        
        status_layout.addWidget(self.status_indicator, 0, Qt.AlignVCenter)
        status_layout.addWidget(self.status_label, 1)
        
        # Current gesture display
        gesture_group = QGroupBox("Current Gesture")
        gesture_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        gesture_layout = QVBoxLayout(gesture_group)
        
        self.current_gesture_label = QLabel(self.current_gesture)
        self.current_gesture_label.setStyleSheet("""
            color: #4CAF50;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
        """)
        self.current_gesture_label.setAlignment(Qt.AlignCenter)
        gesture_layout.addWidget(self.current_gesture_label)
        
        # Control buttons
        self.toggle_button = StyledButton("▶ Start Gesture Recognition", primary=True)
        self.toggle_button.clicked.connect(self.toggle_gesture_mode)
        
        # Restart button (only visible when using video files)
        self.restart_button = StyledButton("🔄 Restart Video", primary=True)
        self.restart_button.clicked.connect(self.restart_video)
        self.restart_button.setVisible(False)
        
        self.quit_button = StyledButton("❌ Exit", primary=False)
        self.quit_button.clicked.connect(self.close_application)
        
        # Add widgets to control layout
        control_layout.addWidget(title)
        control_layout.addWidget(source_group)
        control_layout.addLayout(status_layout)
        control_layout.addWidget(gesture_group)
        control_layout.addWidget(self.toggle_button)
        control_layout.addWidget(self.restart_button)
        control_layout.addWidget(self.quit_button)
        control_layout.addStretch()
        
        return control_frame
    
    def create_display_panel(self):
        """Create the right display panel"""
        display_frame = QFrame(self)
        display_frame.setObjectName("contentFrame")
        display_layout = QVBoxLayout(display_frame)
        display_layout.setSpacing(15)
        
        # Video display area
        video_group = QGroupBox("Video Feed")
        video_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        video_layout = QVBoxLayout(video_group)
        
        # Video display label
        self.video_label = QLabel("Video feed will appear here\n\nKeyboard Shortcuts:\n• Space: Start/Stop Recognition\n• R: Restart Video (when using video files)\n• Q: Quit Application")
        self.video_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.5);
            border: 2px dashed rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: #E0E0E0;
            font-size: 14px;
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumHeight(300)
        self.video_label.setScaledContents(True)
        self.video_label.setWordWrap(True)
        
        video_layout.addWidget(self.video_label)
        
        # Gesture log area
        log_group = QGroupBox("Gesture Log")
        log_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        log_layout = QVBoxLayout(log_group)
        
        self.gesture_log_text = QTextEdit()
        self.gesture_log_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.3);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        self.gesture_log_text.setMaximumHeight(150)
        self.gesture_log_text.setReadOnly(True)
        
        log_layout.addWidget(self.gesture_log_text)
        
        # Add to display layout
        display_layout.addWidget(video_group, 2)
        display_layout.addWidget(log_group, 1)
        
        return display_frame
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        from PyQt5.QtWidgets import QShortcut
        
        # Space bar to toggle recognition
        self.space_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.space_shortcut.activated.connect(self.toggle_gesture_mode)
        
        # R key to restart video
        self.restart_shortcut = QShortcut(QKeySequence(Qt.Key_R), self)
        self.restart_shortcut.activated.connect(self.restart_video)
        
        # Q key to quit
        self.quit_shortcut = QShortcut(QKeySequence(Qt.Key_Q), self)
        self.quit_shortcut.activated.connect(self.close_application)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Space:
            self.toggle_gesture_mode()
        elif event.key() == Qt.Key_R and self.video_radio.isChecked() and self.gesture_active:
            self.restart_video()
        elif event.key() == Qt.Key_Q:
            self.close_application()
        else:
            super().keyPressEvent(event)
    
    def on_source_changed(self):
        """Handle video source selection change"""
        is_video_file = self.video_radio.isChecked()
        self.browse_button.setEnabled(is_video_file)
        
        # Show/hide restart button based on source type
        self.restart_button.setVisible(is_video_file and self.gesture_active)
        
        if self.camera_radio.isChecked():
            self.video_source = None
            self.video_path_label.setText("Camera selected")
        
    def browse_video_file(self):
        """Open file dialog to select video file"""
        file_filter = "Video Files ("
        for ext in SUPPORTED_VIDEO_FORMATS:
            file_filter += f"*{ext} "
        file_filter = file_filter.strip() + ")"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "", file_filter
        )
        
        if file_path:
            self.video_source = file_path
            self.video_path_label.setText(os.path.basename(file_path))
            logging.info(f"Video file selected: {file_path}")
    
    def update_gesture_display(self, gesture_name, finger_count):
        """Update the current gesture display"""
        self.current_gesture = f"{finger_count} fingers - {gesture_name}"
        self.current_gesture_label.setText(self.current_gesture)
        
        # Add to gesture log
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {self.current_gesture}"
        self.gesture_log.append(log_entry)
        
        # Keep only last 50 entries
        if len(self.gesture_log) > 50:
            self.gesture_log.pop(0)
        
        # Update log display
        self.gesture_log_text.setPlainText("\n".join(self.gesture_log))
        self.gesture_log_text.moveCursor(self.gesture_log_text.textCursor().End)
    
    def update_video_frame(self, frame):
        """Update the video display with processed frame"""
        try:
            # Convert frame to Qt format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_frame.shape
            bytes_per_line = 3 * width
            
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            q_pixmap = QPixmap.fromImage(q_image)
            
            # Scale to fit label while maintaining aspect ratio
            scaled_pixmap = q_pixmap.scaled(
                self.video_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
        except Exception as e:
            logging.error(f"Error updating video frame: {e}")
    
    def update_status_message(self, message):
        """Update status message from gesture recognizer"""
        self.status_label.setText(f"Status: {message}")
    
    def restart_video(self):
        """Restart the current video file"""
        if self.worker_thread and hasattr(self.worker_thread.recognizer, 'restart_video'):
            self.worker_thread.recognizer.restart_video()
            logging.info("Video restart requested from UI")

    def toggle_gesture_mode(self):
        if not self.gesture_active:
            # Validate video source selection
            if self.video_radio.isChecked() and not self.video_source:
                QMessageBox.warning(self, "No Video File", 
                                  "Please select a video file first.")
                return
            
            # Determine video source
            source = self.video_source if self.video_radio.isChecked() else None
            source_type = "video file" if source else "camera"
            
            # Start gesture recognition
            self.status_label.setText(f"Status: Recognizing gestures from {source_type}...")
            self.status_indicator.set_status("active")
            self.toggle_button.setText("⏸ Stop Gesture Recognition")
            self.gesture_active = True
            
            # Show restart button only for video files
            self.restart_button.setVisible(self.video_radio.isChecked())

            # Create animation for status change
            self.animate_status_change(True)

            logging.info(f"Gesture Recognition Started with {source_type}")

            self.worker_thread = GestureWorker(source)
            self.worker_thread.finished.connect(self.on_thread_finished)
            self.worker_thread.gesture_detected.connect(self.update_gesture_display)
            self.worker_thread.frame_processed.connect(self.update_video_frame)
            self.worker_thread.status_update.connect(self.update_status_message)
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
            self.restart_button.setVisible(False)  # Hide restart button when stopped
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
        self.restart_button.setVisible(False)  # Hide restart button when finished
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
