# 📹 RTSP Camera Integration Guide

This guide explains how to use RTSP IP cameras with the Gesture Media Controller project.

## 🎯 Overview

The project now supports both USB cameras and RTSP IP cameras. You can easily switch between them using configuration settings.

## 🔧 Configuration

### Step 1: Enable RTSP Camera

Edit `app/config.py` and modify these settings:

```python
# RTSP Camera configuration
USE_RTSP_CAMERA = True  # Set to True to use RTSP camera
RTSP_URL = "rtsp://admin:admin123@10.101.0.20:554/avstream/channel=2/stream=0.sdp"
RTSP_TRANSPORT = "tcp"  # Transport protocol: "tcp" or "udp"
```

### Step 2: Configure Your RTSP URL

Replace the `RTSP_URL` with your camera's RTSP stream URL. Common formats:

```python
# Generic format
"rtsp://username:password@ip_address:port/path"

# Examples:
"rtsp://admin:admin123@192.168.1.100:554/stream1"
"rtsp://user:pass@10.0.0.50:554/avstream/channel=1/stream=0.sdp"
"rtsp://admin:password@camera.local:554/live/main"
```

### Step 3: Choose Transport Protocol

- **TCP** (recommended): More reliable, better for unstable networks
- **UDP**: Lower latency, better for stable networks

```python
RTSP_TRANSPORT = "tcp"  # or "udp"
```

## 🧪 Testing Your RTSP Camera

### Quick Test

Run the RTSP testing script:

```bash
python test_rtsp_camera.py
```

This will:
- Test your RTSP connection
- Show camera properties (resolution, FPS)
- Display a preview window
- Test different transport protocols

### Manual Testing

You can also test manually:

```python
import cv2
import os

# Set transport protocol
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

# Test your RTSP URL
cap = cv2.VideoCapture("your_rtsp_url_here", cv2.CAP_FFMPEG)

if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print("✅ RTSP camera working!")
        cv2.imshow('Test', frame)
        cv2.waitKey(3000)
    else:
        print("❌ Can't read frames")
else:
    print("❌ Can't connect to RTSP stream")

cap.release()
cv2.destroyAllWindows()
```

## 🚀 Running the Application

Once configured, run the main application:

```bash
python main.py
```

The application will:
1. Try to connect to your RTSP camera first
2. Fall back to USB camera if RTSP fails
3. Show detailed logging about camera initialization

## 🔍 Troubleshooting

### Common Issues

**1. Connection Timeout**
```
Error: Failed to open RTSP stream
```
- Check if the camera IP is reachable: `ping 10.101.0.20`
- Verify the RTSP URL format
- Try different transport protocol (TCP vs UDP)

**2. Authentication Failed**
```
Error: RTSP authentication failed
```
- Verify username and password
- Check if camera requires different authentication

**3. Network Issues**
```
Error: Connection refused
```
- Check if RTSP port (usually 554) is open
- Verify firewall settings
- Try accessing camera web interface first

**4. Codec Issues**
```
Error: Cannot decode video stream
```
- Camera might use unsupported codec
- Try different stream quality/resolution
- Update OpenCV: `pip install --upgrade opencv-python`

### Debug Steps

1. **Test camera web interface**: Open `http://10.101.0.20` in browser
2. **Test with VLC**: Open RTSP URL in VLC media player
3. **Check network**: `telnet 10.101.0.20 554`
4. **Run RTSP test script**: `python test_rtsp_camera.py`

### Performance Optimization

**For better performance:**

```python
# In config.py, add these settings:
RTSP_BUFFER_SIZE = 1  # Reduce latency
RTSP_TIMEOUT = 5000   # Connection timeout in ms
```

**For unstable networks:**

```python
RTSP_TRANSPORT = "tcp"  # More reliable than UDP
RTSP_RECONNECT = True   # Auto-reconnect on failure
```

## 📋 Camera Compatibility

### Tested Cameras
- Hikvision IP cameras
- Dahua IP cameras
- Generic ONVIF cameras
- Axis IP cameras

### RTSP URL Formats by Brand

**Hikvision:**
```
rtsp://username:password@ip:554/Streaming/Channels/101
```

**Dahua:**
```
rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0
```

**Axis:**
```
rtsp://username:password@ip:554/axis-media/media.amp
```

**Generic ONVIF:**
```
rtsp://username:password@ip:554/onvif1
```

## 🔄 Switching Between Camera Types

You can easily switch between RTSP and USB cameras:

**Use RTSP Camera:**
```python
USE_RTSP_CAMERA = True
```

**Use USB Camera:**
```python
USE_RTSP_CAMERA = False
CAMERA_INDEX = 0  # or 1, 2, etc.
```

## 📊 Performance Considerations

### RTSP vs USB Cameras

| Feature | RTSP Camera | USB Camera |
|---------|-------------|------------|
| **Latency** | Higher (network) | Lower (direct) |
| **Flexibility** | Remote access | Local only |
| **Quality** | Depends on network | Consistent |
| **Setup** | More complex | Plug & play |
| **Reliability** | Network dependent | Hardware dependent |

### Recommendations

- **Use RTSP** for: Remote cameras, security cameras, permanent installations
- **Use USB** for: Local testing, portable setups, low-latency requirements

## 🛠️ Advanced Configuration

### Custom RTSP Options

You can add more RTSP options in the code:

```python
# In gesture.py, modify the RTSP initialization:
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    f"rtsp_transport;{RTSP_TRANSPORT};"
    "stimeout;5000000;"  # 5 second timeout
    "buffer_size;1024000"  # Buffer size
)
```

### Multiple Camera Support

To support multiple RTSP cameras, modify the config:

```python
RTSP_CAMERAS = [
    "rtsp://admin:admin123@10.101.0.20:554/stream1",
    "rtsp://admin:admin123@10.101.0.21:554/stream1"
]
```

## ✅ Verification Checklist

Before running the main application:

- [ ] RTSP URL is correct and accessible
- [ ] Camera credentials are valid
- [ ] Network connectivity is stable
- [ ] `test_rtsp_camera.py` runs successfully
- [ ] Camera preview shows clear image
- [ ] No error messages in logs

## 📞 Support

If you encounter issues:

1. Run the test script: `python test_rtsp_camera.py`
2. Check the application logs
3. Verify camera settings and network connectivity
4. Try different transport protocols (TCP/UDP)

The application includes comprehensive error handling and will fall back to USB cameras if RTSP fails.