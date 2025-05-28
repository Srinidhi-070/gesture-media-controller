# app/config.py

# Minimum confidence score for hand detection (0.0 to 1.0)
HAND_DETECTION_CONFIDENCE = 0.7  # Adjusted to match original implementation

# Gesture action mapping
# Number of fingers → gesture action label
GESTURE_ACTIONS = {
    0: "pause",
    1: "next",
    2: "previous",
    3: "volume_up",
    4: "volume_down",
    5: "play"
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
