# app/gesture.py
import cv2
import mediapipe as mp
import numpy as np
import logging
import time
import os
from PyQt5.QtCore import QObject, pyqtSignal
from app.config import (
    HAND_DETECTION_CONFIDENCE, 
    MAX_NUM_HANDS, 
    GESTURE_ACTIONS,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    VOLUME_STEP,
    GESTURE_COOLDOWN,
    CAMERA_INDEX,
    USE_RTSP_CAMERA,
    RTSP_URL,
    RTSP_TRANSPORT
)
from app.media_controller import VolumeController

def detect_cameras():
    """Detect available cameras and return a list of working camera indices"""
    available_cameras = []
    for i in range(10):  # Check first 10 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available_cameras.append(i)
                logging.info(f"Camera {i} detected and working")
            cap.release()
        else:
            break
    return available_cameras

class GestureRecognizer(QObject):
    # Signals for UI communication
    gesture_detected = pyqtSignal(str, int)  # gesture_name, finger_count
    frame_processed = pyqtSignal(object)  # processed frame for display
    status_update = pyqtSignal(str)  # status messages
    
    def __init__(self, video_source=None):
        super().__init__()
        self.video_source = video_source  # Can be None (camera), or path to video file
        self.is_video_file = bool(video_source)  # True if using a video file, False if using camera
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=MAX_NUM_HANDS, 
            min_detection_confidence=HAND_DETECTION_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils  # Corrected import
        
        # Initialize video source (camera or video file)
        self.cap = self._initialize_video_source()
        
        # Set frame size from config (only for USB cameras, not for video files)
        if self.cap and not USE_RTSP_CAMERA and not self.is_video_file:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        
        self.prev_gesture = None
        self.last_action_time = 0
        self._running = True
        
        # Initialize volume controller
        try:
            self.volume_controller = VolumeController()
            self.has_volume_control = True
        except Exception as e:
            logging.warning(f"Volume controller initialization failed: {e}")
            self.has_volume_control = False

    def _initialize_video_source(self):
        """Initialize video source (camera or video file)"""
        
        # If video source is specified, try to load video file
        if self.video_source:
            return self._initialize_video_file()
        
        # Otherwise, initialize camera
        return self._initialize_camera()
    
    def _initialize_video_file(self):
        """Initialize video file input"""
        logging.info(f"Initializing video file: {self.video_source}")
        
        try:
            if not os.path.exists(self.video_source):
                logging.error(f"Video file not found: {self.video_source}")
                return None
            
            cap = cv2.VideoCapture(self.video_source)
            
            if not cap.isOpened():
                logging.error("Failed to open video file")
                return None
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logging.info(f"Video file loaded successfully:")
            logging.info(f"  Resolution: {width}x{height}")
            logging.info(f"  FPS: {fps}")
            logging.info(f"  Total frames: {frame_count}")
            
            # Test if we can read frames
            ret, frame = cap.read()
            if not ret or frame is None:
                logging.error("Video file opened but cannot read frames")
                cap.release()
                return None
            
            # Reset to beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.status_update.emit(f"Video loaded: {os.path.basename(self.video_source)}")
            return cap
            
        except Exception as e:
            logging.error(f"Video file initialization failed: {e}")
            return None

    def _initialize_camera(self):
        """Initialize camera with RTSP and USB support"""
        
        # Check if RTSP camera is configured
        if USE_RTSP_CAMERA:
            return self._initialize_rtsp_camera()
        else:
            return self._initialize_usb_camera()
    
    def _initialize_rtsp_camera(self):
        """Initialize RTSP camera connection"""
        logging.info(f"Initializing RTSP camera: {RTSP_URL}")
        
        # Set OpenCV FFMPEG options for RTSP
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = f"rtsp_transport;{RTSP_TRANSPORT}"
        
        try:
            # Create VideoCapture with RTSP URL and FFMPEG backend
            cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
            
            # Set buffer size to reduce latency
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if cap.isOpened():
                # Test if we can read frames
                ret, frame = cap.read()
                if ret and frame is not None:
                    logging.info("RTSP camera initialized successfully")
                    
                    # Get actual resolution
                    height, width = frame.shape[:2]
                    logging.info(f"RTSP camera resolution: {width}x{height}")
                    
                    return cap
                else:
                    logging.error("RTSP camera opened but cannot read frames")
                    cap.release()
            else:
                logging.error("Failed to open RTSP camera")
                
        except Exception as e:
            logging.error(f"RTSP camera initialization failed: {e}")
        
        # Fallback to USB camera if RTSP fails
        logging.warning("RTSP camera failed, falling back to USB camera...")
        return self._initialize_usb_camera()
    
    def _initialize_usb_camera(self):
        """Initialize USB camera with fallback logic"""
        # First, try the configured camera index
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                logging.info(f"Successfully initialized USB camera {CAMERA_INDEX}")
                return cap
            cap.release()
        
        # If configured camera fails, detect available cameras
        logging.warning(f"USB camera {CAMERA_INDEX} not available, detecting other cameras...")
        available_cameras = detect_cameras()
        
        if available_cameras:
            # Try to use the first available camera
            camera_index = available_cameras[0]
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                logging.info(f"Using USB camera {camera_index} as fallback")
                return cap
        
        logging.error("No working cameras found!")
        return None

    def count_raised_fingers(self, hand_landmarks):
        tips_ids = [4, 8, 12, 16, 20]
        fingers = []

        # Thumb
        if hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers (index to pinky)
        for id in range(1, 5):
            if hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id] - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers.count(1)

    def map_gesture_to_action(self, finger_count):
        now = time.time()
        cooldown = GESTURE_COOLDOWN  # Use value from config

        if now - self.last_action_time < cooldown:
            return

        # Get action from config if available, otherwise use None
        gesture_action = GESTURE_ACTIONS.get(finger_count)
        
        # Log the gesture action without performing any media control
        if gesture_action:
            logging.info(f"Gesture recognized: {gesture_action}")
            self.last_action_time = now
            self.prev_gesture = gesture_action
            # Emit signal for UI update
            self.gesture_detected.emit(gesture_action, finger_count)

    def restart_video(self):
        """Restart the video file from the beginning"""
        if self.is_video_file and self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            logging.info("Video restarted from beginning")
            self.status_update.emit("Video restarted")
    
    def stop(self):
        """Stop the gesture recognition loop"""
        self._running = False
        logging.info("Stopping gesture recognition...")

    def run(self):
        if not self.cap:
            error_msg = "No video source available for gesture recognition!"
            logging.error(error_msg)
            self.status_update.emit(error_msg)
            return
            
        source_type = "video file" if self.is_video_file else "camera feed"
        logging.info(f"Starting {source_type} for gesture recognition.")
        self.status_update.emit(f"Processing {source_type}...")
        self._running = True
        
        # For video files, get total frame count for progress tracking
        total_frames = 0
        if self.is_video_file:
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_count = 0
        
        while self._running:
            success, frame = self.cap.read()
            if not success:
                if self.is_video_file:
                    logging.info("Reached end of video file")
                    self.status_update.emit("Video processing completed")
                    # Loop the video if desired
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    logging.error("Failed to read from camera")
                    break

            frame_count += 1
            
            # Don't flip video files, only camera feeds
            if not self.is_video_file:
                frame = cv2.flip(frame, 1)
                
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.hands.process(rgb_frame)

            # Draw hand landmarks and detect gestures
            current_gesture = "No hands detected"
            finger_count = 0
            
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    finger_count = self.count_raised_fingers(hand_landmarks)
                    self.map_gesture_to_action(finger_count)
                    
                    # Get gesture name for display
                    gesture_name = GESTURE_ACTIONS.get(finger_count, "Unknown")
                    current_gesture = f"{finger_count} fingers - {gesture_name}"

            # Add text overlay with current gesture info
            cv2.putText(frame, current_gesture, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add frame counter for video files
            if self.is_video_file and total_frames > 0:
                progress_text = f"Frame: {frame_count}/{total_frames}"
                cv2.putText(frame, progress_text, (10, frame.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Emit processed frame for UI display
            self.frame_processed.emit(frame.copy())

            # Small delay to prevent excessive CPU usage
            cv2.waitKey(1)

        # Clean up resources
        self.release_resources()
        
    def release_resources(self):
        """Release camera and close windows"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        self.status_update.emit("Resources released")
        logging.info("Camera feed closed.")
