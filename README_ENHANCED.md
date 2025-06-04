# 🎮 Enhanced Gesture-Based Media Controller

A Python application that uses computer vision and hand gesture recognition to control media playback. The application detects hand gestures through **camera feed or video files** and translates them into media control actions like play/pause, volume control, and track navigation.

## ✨ New Features

### 📹 Video File Support
- **Load and process any video file** for gesture recognition
- Supported formats: `.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`, `.flv`
- Frame-by-frame processing with progress tracking
- Video looping and restart functionality (press 'R' to restart)

### 🖥️ Enhanced UI
- **Real-time Video Display**: See the processed video feed directly in the application
- **Live Gesture Feedback**: Real-time display of detected gestures and finger counts
- **Gesture Log**: Timestamped log of all detected gestures
- **Source Selection**: Easy switching between camera and video file input
- **Status Updates**: Real-time status messages from the gesture recognition engine

### 🔧 Improved Recognition
- Better visual feedback with gesture overlays on video
- Frame counter and progress tracking for video files
- Enhanced error handling and status reporting
- Signal-based communication between recognition engine and UI

## 🖐️ Gesture Mappings

| Fingers Raised | Action |
|----------------|--------|
| 0 (Fist) | Play |
| 1 | Next Track |
| 2 | Previous Track |
| 3 | Volume Up |
| 4 | Volume Down |
| 5 (Open Hand) | Pause |

## 📋 Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- PyQt5
- PyAutoGUI
- PyCaw (for Windows volume control)
- NumPy

## 🚀 Installation

1. **Clone this repository:**
```bash
git clone <repository-url>
cd gesture-media-controller
```

2. **Install the required dependencies:**
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Basic Usage

Run the application:
```bash
python main.py
```

### 📷 Using Camera Input:
1. Select **"Camera"** as video source
2. Click **"Start Gesture Recognition"** to begin
3. Position your hand in front of the camera
4. Make gestures with different numbers of raised fingers
5. Watch real-time feedback in the application window
6. Press **'Q'** in the OpenCV window or click **"Stop"** to end recognition

### 🎬 Using Video File Input:
1. Select **"Video File"** as video source
2. Click **"Browse"** to select a video file (.mp4, .avi, .mov, etc.)
3. Click **"Start Gesture Recognition"** to begin processing
4. The video will play and detect gestures automatically
5. Press **'R'** in the OpenCV window to restart the video
6. Press **'Q'** or click **"Stop"** to end processing

### 🎥 Creating Test Videos

Generate a test video with simulated gestures:
```bash
python create_test_video.py
```

This creates `test_gesture_video.mp4` with different finger counts for testing the system.

## ⚙️ Configuration

### Camera Configuration

Edit `app/config.py` to customize camera settings:

#### USB Camera (Default)
```python
USE_RTSP_CAMERA = False
CAMERA_INDEX = 0  # 0 = built-in, 1 = first external, etc.
```

#### RTSP Network Camera
```python
USE_RTSP_CAMERA = True
RTSP_URL = "rtsp://your-camera-url"
RTSP_TRANSPORT = "udp"  # or "tcp"
```

### Gesture Settings
```python
# Gesture action mapping
GESTURE_ACTIONS = {
    0: "play",
    1: "next",
    2: "previous",
    3: "volume_up",
    4: "volume_down",
    5: "pause"
}

# Detection sensitivity (0.0 to 1.0)
HAND_DETECTION_CONFIDENCE = 0.7

# Cooldown between actions (seconds)
GESTURE_COOLDOWN = 2.0
```

## 📁 Project Structure

```
gesture-media-controller/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── gesture.py         # Enhanced gesture recognition logic
│   ├── media_controller.py # Volume control functionality
│   └── ui.py             # Enhanced PyQt5 user interface
├── main.py               # Application entry point
├── create_test_video.py  # Test video generator
├── requirements.txt      # Python dependencies
├── test_cameras.py       # Camera detection utility
├── test_rtsp_camera.py   # RTSP camera testing
└── README.md            # Documentation
```

## 🎮 Application Interface

The enhanced UI includes:

### Left Panel (Controls)
- **Video Source Selection**: Choose between camera or video file
- **File Browser**: Select video files for processing
- **Status Indicator**: Visual status with color coding
- **Current Gesture Display**: Real-time gesture feedback
- **Control Buttons**: Start/stop recognition

### Right Panel (Display)
- **Video Feed**: Live display of processed video with gesture overlays
- **Gesture Log**: Scrollable log of detected gestures with timestamps

## 🔧 Troubleshooting

### Camera Issues
- Run `python test_cameras.py` to detect available cameras
- For RTSP cameras, use `python test_rtsp_camera.py` to test connectivity
- Check camera permissions and ensure no other applications are using the camera

### Video File Issues
- Ensure video file format is supported (mp4, avi, mov, mkv, wmv, flv)
- Check that the video file path is accessible
- Try different video files if one doesn't work
- Check the gesture log for processing status

### Gesture Detection Issues
- Ensure good lighting conditions (for camera input)
- Keep hand clearly visible and within frame
- Adjust `HAND_DETECTION_CONFIDENCE` if detection is too sensitive/insensitive
- Check that fingers are clearly separated when making gestures
- Use the test video to verify the system is working correctly

### Volume Control Issues (Windows)
- Ensure PyCaw is properly installed
- Run the application as administrator if volume control doesn't work
- Check Windows audio settings and ensure the correct audio device is selected

## 🎯 Key Improvements in This Version

1. **Video File Processing**: Complete support for video file input with multiple formats
2. **Enhanced UI**: Modern interface with real-time video display and gesture feedback
3. **Better User Experience**: Intuitive source selection and comprehensive status updates
4. **Improved Recognition**: Better visual feedback and error handling
5. **Test Video Generator**: Built-in tool to create test videos for validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MediaPipe team for the excellent hand tracking solution
- OpenCV community for computer vision tools
- PyQt5 for the GUI framework
- Original developer: **Srinidhi N S**