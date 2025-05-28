# ✋ Gesture-Based Media Controller

Control your media playback with simple hand gestures using your webcam, computer vision, and AI.

---

## 📌 Overview

This project uses **MediaPipe** to detect hand gestures and map them to **system media controls** like play, pause, volume, and track navigation — no mouse or keyboard needed.

Built with:
- Python 3.10
- OpenCV
- MediaPipe
- Pycaw
- Keyboard module

---

## 🖐️ Available Gestures

The system recognizes gestures based on **how many fingers are raised**:

| 👆 Fingers Up | ✨ Gesture Meaning | 🎮 Action |
|--------------|--------------------|-----------|
| 0            | Fist               | ⏸ Pause (Space key) |
| 1            | Index only         | ⏭ Next Track (Ctrl + →) |
| 2            | Index + Middle     | ⏮ Previous Track (Ctrl + ←) |
| 3            | First 3 fingers    | 🔊 Volume Up |
| 4            | Four fingers       | 🔉 Volume Down |
| 5            | All fingers        | ▶️ Play (Space key toggle) |

---

## 🗂️ Project Structure

```
gesture-media-controller/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── gesture.py
│   ├── media_controller.py
│   └── ui.py
├── main.py
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/gesture-media-controller.git
   cd gesture-media-controller
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate     # or env\Scripts\activate on Windows
   ```

3. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python main.py
   ```

---

## ⚙️ Requirements

- Python 3.10.x (MediaPipe compatibility)
- Webcam
- Windows OS (for `pycaw` support)

---

## 🤖 Future Improvements

- Custom gesture training with ML
- UI enhancements for gesture feedback
- Spotify/VLC API integration

---

## 🧠 Credits

Developed by: **Srinidhi N S**  
Using tools: MediaPipe, OpenCV, Pycaw, Keyboard

---

## 📸 Demo

*(Add demo video or screenshots here)*

---

## 📄 License

MIT License

Copyright (c) 2025 Srinidhi N S

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell   
copies of the Software, and to permit persons to whom the Software is       
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in   
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR   
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         
DEALINGS IN THE SOFTWARE.

