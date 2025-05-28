# app/media_controller.py
import platform
import logging

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
