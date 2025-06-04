#!/usr/bin/env python3
"""
RTSP Camera Testing Script
This script helps you test RTSP camera connections and find the right settings.
"""

import cv2
import os
import sys
import time

def test_rtsp_connection(rtsp_url, transport="tcp"):
    """Test RTSP camera connection with specified transport protocol"""
    print(f"🎥 Testing RTSP Camera Connection")
    print(f"URL: {rtsp_url}")
    print(f"Transport: {transport}")
    print("=" * 60)
    
    # Set OpenCV FFMPEG options
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = f"rtsp_transport;{transport}"
    
    try:
        # Create VideoCapture with RTSP URL
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        
        # Set buffer size to reduce latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            print("❌ Failed to open RTSP stream")
            return False
        
        print("✅ RTSP stream opened successfully")
        
        # Try to read a frame
        print("📸 Testing frame capture...")
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print("❌ Failed to read frame from RTSP stream")
            cap.release()
            return False
        
        # Get stream properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"✅ Frame captured successfully!")
        print(f"📐 Resolution: {width}x{height}")
        print(f"🎬 FPS: {fps:.1f}")
        print(f"🖼️ Frame shape: {frame.shape}")
        
        # Show preview for 3 seconds
        print("🔍 Showing preview for 3 seconds...")
        cv2.imshow('RTSP Camera Preview', frame)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Error testing RTSP connection: {e}")
        return False

def interactive_rtsp_test(rtsp_url, transport="tcp"):
    """Interactive RTSP camera test with live preview"""
    print(f"\n🔴 INTERACTIVE RTSP TEST")
    print("Press 'q' to quit, 's' to save frame")
    print("=" * 40)
    
    # Set OpenCV FFMPEG options
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = f"rtsp_transport;{transport}"
    
    try:
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            print("❌ Failed to open RTSP stream for interactive test")
            return
        
        print("✅ RTSP stream opened. Starting live preview...")
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Add overlay text
            cv2.putText(frame, f'RTSP Camera - Frame {frame_count}', 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, 'Press q to quit, s to save frame', 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('RTSP Camera Live Preview', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"rtsp_frame_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Frame saved as {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"✅ Interactive test completed. Total frames: {frame_count}")
        
    except Exception as e:
        print(f"❌ Error in interactive test: {e}")

def test_different_transports(rtsp_url):
    """Test RTSP connection with different transport protocols"""
    print("\n🔄 Testing Different Transport Protocols")
    print("=" * 50)
    
    transports = ["tcp", "udp"]
    
    for transport in transports:
        print(f"\n🧪 Testing with {transport.upper()} transport...")
        success = test_rtsp_connection(rtsp_url, transport)
        if success:
            print(f"✅ {transport.upper()} transport works!")
        else:
            print(f"❌ {transport.upper()} transport failed")

def main():
    # Default RTSP URL (you can modify this)
    default_rtsp_url = "rtsp://admin:admin123@10.101.0.20:554/avstream/channel=2/stream=0.sdp"
    
    print("🎥 RTSP Camera Testing Tool")
    print("=" * 50)
    
    # Get RTSP URL from user or use default
    rtsp_url = input(f"Enter RTSP URL (or press Enter for default): ").strip()
    if not rtsp_url:
        rtsp_url = default_rtsp_url
        print(f"Using default URL: {rtsp_url}")
    
    print("\nChoose test mode:")
    print("1. Quick connection test")
    print("2. Test different transports")
    print("3. Interactive live preview")
    print("4. All tests")
    
    try:
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            test_rtsp_connection(rtsp_url)
        elif choice == "2":
            test_different_transports(rtsp_url)
        elif choice == "3":
            interactive_rtsp_test(rtsp_url)
        elif choice == "4":
            test_rtsp_connection(rtsp_url)
            test_different_transports(rtsp_url)
            interactive_rtsp_test(rtsp_url)
        else:
            print("Invalid choice. Running quick test...")
            test_rtsp_connection(rtsp_url)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n✅ RTSP camera testing complete!")

if __name__ == "__main__":
    main()