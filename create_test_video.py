#!/usr/bin/env python3
"""
Create a test video with hand gestures for testing the gesture recognition system.
This script creates a simple video with text overlays showing different finger counts.
"""

import cv2
import numpy as np
import os

def create_test_video():
    """Create a test video with gesture simulation"""
    
    # Video properties
    width, height = 640, 480
    fps = 30
    duration = 30  # seconds
    total_frames = fps * duration
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = 'test_gesture_video.mp4'
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Define gesture sequence (finger counts)
    gesture_sequence = [0, 1, 2, 3, 4, 5] * 5  # Repeat sequence
    frames_per_gesture = total_frames // len(gesture_sequence)
    
    print(f"Creating test video: {output_path}")
    print(f"Duration: {duration} seconds")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")
    
    for frame_num in range(total_frames):
        # Create a frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add gradient background
        for y in range(height):
            color_value = int(50 + (y / height) * 100)
            frame[y, :] = [color_value, color_value//2, color_value//3]
        
        # Determine current gesture
        gesture_index = frame_num // frames_per_gesture
        if gesture_index >= len(gesture_sequence):
            gesture_index = len(gesture_sequence) - 1
        
        finger_count = gesture_sequence[gesture_index]
        
        # Add text overlay
        text = f"Fingers: {finger_count}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        color = (255, 255, 255)
        thickness = 3
        
        # Get text size for centering
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2
        
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness)
        
        # Add frame counter
        frame_text = f"Frame: {frame_num + 1}/{total_frames}"
        cv2.putText(frame, frame_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        # Add time indicator
        time_text = f"Time: {frame_num/fps:.1f}s"
        cv2.putText(frame, time_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        # Add gesture action
        from app.config import GESTURE_ACTIONS
        action = GESTURE_ACTIONS.get(finger_count, "Unknown")
        action_text = f"Action: {action}"
        cv2.putText(frame, action_text, (10, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2)
        
        # Draw a simple hand representation
        draw_hand_representation(frame, finger_count, width, height)
        
        # Write frame
        out.write(frame)
        
        # Show progress
        if frame_num % (fps * 2) == 0:  # Every 2 seconds
            progress = (frame_num / total_frames) * 100
            print(f"Progress: {progress:.1f}%")
    
    # Release video writer
    out.release()
    print(f"Test video created successfully: {output_path}")
    return output_path

def draw_hand_representation(frame, finger_count, width, height):
    """Draw a simple hand representation showing the finger count"""
    
    # Hand center
    hand_x = width // 4
    hand_y = height // 2
    
    # Draw palm
    cv2.circle(frame, (hand_x, hand_y), 50, (150, 150, 150), -1)
    
    # Draw fingers based on count
    finger_positions = [
        (hand_x - 30, hand_y - 60),  # Thumb
        (hand_x - 15, hand_y - 80),  # Index
        (hand_x, hand_y - 85),       # Middle
        (hand_x + 15, hand_y - 80),  # Ring
        (hand_x + 30, hand_y - 60)   # Pinky
    ]
    
    for i in range(5):
        if i < finger_count:
            # Draw extended finger
            cv2.circle(frame, finger_positions[i], 8, (255, 255, 255), -1)
            cv2.line(frame, (hand_x, hand_y), finger_positions[i], (255, 255, 255), 4)
        else:
            # Draw folded finger
            cv2.circle(frame, finger_positions[i], 4, (100, 100, 100), -1)

if __name__ == "__main__":
    try:
        video_path = create_test_video()
        print(f"\nTest video created at: {os.path.abspath(video_path)}")
        print("You can now use this video file in the gesture recognition application.")
    except Exception as e:
        print(f"Error creating test video: {e}")