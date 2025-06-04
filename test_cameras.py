#!/usr/bin/env python3
"""
Camera Detection Script
This script helps you identify which camera index to use for your external camera.
"""

import cv2
import sys

def test_cameras():
    """Test and display information about available cameras"""
    print("🎥 Camera Detection Script")
    print("=" * 40)
    
    available_cameras = []
    
    for i in range(10):  # Test first 10 camera indices
        print(f"Testing camera index {i}...", end=" ")
        
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                available_cameras.append({
                    'index': i,
                    'width': width,
                    'height': height,
                    'fps': fps
                })
                
                print(f"✅ WORKING - Resolution: {width}x{height}, FPS: {fps:.1f}")
                
                # Show a preview window for 2 seconds
                cv2.imshow(f'Camera {i} Preview', frame)
                cv2.waitKey(2000)  # Show for 2 seconds
                cv2.destroyAllWindows()
                
            else:
                print("❌ Can't read frames")
            
            cap.release()
        else:
            print("❌ Can't open")
    
    print("\n" + "=" * 40)
    print("📋 SUMMARY:")
    
    if available_cameras:
        print(f"Found {len(available_cameras)} working camera(s):")
        for cam in available_cameras:
            print(f"  • Camera {cam['index']}: {cam['width']}x{cam['height']} @ {cam['fps']:.1f}fps")
        
        print(f"\n💡 RECOMMENDATION:")
        if len(available_cameras) > 1:
            print(f"   - Camera 0 is usually the built-in camera")
            print(f"   - Camera {available_cameras[1]['index']} is likely your external camera")
            print(f"   - Set CAMERA_INDEX = {available_cameras[1]['index']} in app/config.py")
        else:
            print(f"   - Only one camera found at index {available_cameras[0]['index']}")
            print(f"   - Set CAMERA_INDEX = {available_cameras[0]['index']} in app/config.py")
    else:
        print("❌ No working cameras found!")
        print("   - Make sure your camera is connected")
        print("   - Try different USB ports")
        print("   - Check if camera is being used by another application")

def interactive_camera_test():
    """Interactive camera testing with live preview"""
    print("\n🔴 INTERACTIVE MODE")
    print("Press 'q' to quit, 'n' for next camera")
    
    camera_index = 0
    while camera_index < 10:
        print(f"\nTesting camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            print(f"Camera {camera_index} opened successfully!")
            print("Press 'q' to quit, 'n' for next camera, any other key to continue")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to read frame")
                    break
                
                # Add text overlay
                cv2.putText(frame, f'Camera {camera_index} - Press q to quit, n for next', 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow(f'Camera {camera_index} Test', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                elif key == ord('n'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
        else:
            print(f"Camera {camera_index} not available")
        
        camera_index += 1
    
    print("Tested all cameras (0-9)")

if __name__ == "__main__":
    print("Choose testing mode:")
    print("1. Quick test (automatic)")
    print("2. Interactive test (manual)")
    print("3. Test RTSP camera (run test_rtsp_camera.py)")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            test_cameras()
        elif choice == "2":
            interactive_camera_test()
        elif choice == "3":
            print("For RTSP camera testing, please run:")
            print("python test_rtsp_camera.py")
        else:
            print("Invalid choice. Running quick test...")
            test_cameras()
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n✅ Camera testing complete!")