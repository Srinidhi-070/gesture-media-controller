# app/config.py

# Minimum confidence score for hand detection (0.0 to 1.0)
HAND_DETECTION_CONFIDENCE = 0.7  # Adjusted to match original implementation

# Gesture action mapping
# Number of fingers → gesture action label
GESTURE_ACTIONS = {
    0: "play",
    1: "next",
    2: "previous",
    3: "volume_up",
    4: "volume_down",
    5: "pause"
}

# Logging configuration
LOGGING_LEVEL = "INFO"

# Maximum hands to track
MAX_NUM_HANDS = 1

# Frame size (for consistent video capture window)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Volume adjustment step size
VOLUME_STEP = 0.05

# Cooldown between gesture actions (seconds)
GESTURE_COOLDOWN = 2.0

# Camera configuration
CAMERA_INDEX = 0  # 0 = built-in camera, 1 = first external camera, 2 = second external camera, etc.

# RTSP Camera configuration
USE_RTSP_CAMERA = False  # Set to True to use RTSP camera instead of USB camera
RTSP_URL = "rtsp://admin:admin123@10.101.0.20:554/avstream/channel=2/stream=0.sdp"
RTSP_TRANSPORT = "udp"  # Transport protocol: "tcp" or "udp"

# Advanced camera settings
CAMERA_AUTO_DETECT = True  # Automatically detect and use first available camera if configured camera fails
CAMERA_PREFERRED_RESOLUTION = (640, 480)  # Preferred camera resolution (width, height)
CAMERA_PREFERRED_FPS = 30  # Preferred frames per second

# Video file settings
DEFAULT_VIDEO_PATH = ""  # Default path to video file (leave empty for camera mode)
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']  # Supported video formats
VIDEO_LOOP_ENABLED = True  # Loop video when it reaches the end
