# app/gesture.py
import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import logging
import time
from app.config import (
    HAND_DETECTION_CONFIDENCE, 
    MAX_NUM_HANDS, 
    GESTURE_ACTIONS,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    VOLUME_STEP,
    GESTURE_COOLDOWN
)
from app.media_controller import VolumeController

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=MAX_NUM_HANDS, 
            min_detection_confidence=HAND_DETECTION_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        
        # Set frame size from config
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
        
        if gesture_action == "play" or gesture_action == "pause":
            # Toggle play/pause with space
            pyautogui.press("space")
        elif gesture_action == "next":
            pyautogui.hotkey("ctrl", "right")
        elif gesture_action == "previous":
            pyautogui.hotkey("ctrl", "left")
        elif gesture_action == "volume_up" and self.has_volume_control:
            self.volume_controller.volume_up(VOLUME_STEP)
        elif gesture_action == "volume_down" and self.has_volume_control:
            self.volume_controller.volume_down(VOLUME_STEP)
        elif gesture_action == "mute_toggle" and self.has_volume_control:
            # Toggle mute state
            self.volume_controller.mute() if not self.volume_controller.volume.GetMute() else self.volume_controller.unmute()

        if gesture_action:
            logging.info(f"Gesture recognized: {gesture_action}")
            self.last_action_time = now
            self.prev_gesture = gesture_action

    def stop(self):
        """Stop the gesture recognition loop"""
        self._running = False
        logging.info("Stopping gesture recognition...")

    def run(self):
        logging.info("Starting camera feed for gesture recognition.")
        self._running = True
        
        while self._running:
            success, frame = self.cap.read()
            if not success:
                logging.error("Failed to read from camera")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.hands.process(rgb_frame)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    finger_count = self.count_raised_fingers(hand_landmarks)
                    self.map_gesture_to_action(finger_count)

            cv2.imshow("Gesture Controller - Press Q to Quit", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        # Clean up resources
        self.release_resources()
        
    def release_resources(self):
        """Release camera and close windows"""
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        logging.info("Camera feed closed.")
