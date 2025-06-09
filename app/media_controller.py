# app/media_controller.py
import platform
import logging
import pyautogui
import time

if platform.system() == "Windows":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
else:
    raise NotImplementedError("Advanced media control currently supports only Windows.")

class VolumeController:
    def __init__(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

    def mute(self):
        logging.info("Muting system volume.")
        self.volume.SetMute(1, None)

    def unmute(self):
        logging.info("Unmuting system volume.")
        self.volume.SetMute(0, None)

    def set_volume(self, level: float):
        """
        Set volume level between 0.0 (mute) and 1.0 (max).
        """
        level = max(0.0, min(1.0, level))  # clamp
        logging.info(f"Setting volume to {level * 100:.0f}%")
        self.volume.SetMasterVolumeLevelScalar(level, None)

    def volume_up(self, step=0.05):
        current = self.volume.GetMasterVolumeLevelScalar()
        new_volume = min(current + step, 1.0)
        self.set_volume(new_volume)

    def volume_down(self, step=0.05):
        current = self.volume.GetMasterVolumeLevelScalar()
        new_volume = max(current - step, 0.0)
        self.set_volume(new_volume)

class MediaPlayerController:
    """Controls media playback using system media keys via pyautogui"""
    
    def __init__(self):
        self.is_playing = False
        logging.info("Media Player Controller initialized")
    
    def play(self):
        """Simulates media play key press"""
        try:
            logging.info("Play command sent")
            pyautogui.press('playpause')
            self.is_playing = True
            return True
        except Exception as e:
            logging.error(f"Failed to send play command: {e}")
            return False
    
    def pause(self):
        """Simulates media pause key press"""
        try:
            logging.info("Pause command sent")
            pyautogui.press('playpause')
            self.is_playing = False
            return True
        except Exception as e:
            logging.error(f"Failed to send pause command: {e}")
            return False
    
    def toggle_play_pause(self):
        """Toggles between play and pause"""
        try:
            logging.info("Play/Pause toggle command sent")
            pyautogui.press('playpause')
            self.is_playing = not self.is_playing
            return True
        except Exception as e:
            logging.error(f"Failed to send play/pause toggle command: {e}")
            return False
    
    def next_track(self):
        """Simulates media next track key press"""
        try:
            logging.info("Next track command sent")
            pyautogui.press('nexttrack')
            return True
        except Exception as e:
            logging.error(f"Failed to send next track command: {e}")
            return False
    
    def previous_track(self):
        """Simulates media previous track key press"""
        try:
            logging.info("Previous track command sent")
            pyautogui.press('prevtrack')
            return True
        except Exception as e:
            logging.error(f"Failed to send previous track command: {e}")
            return False
