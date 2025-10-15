# Standard Library
from enum import Enum, auto

from src.config import settings


class SensorStatus(Enum):
    PLACE_FINGER = auto()
    REMOVE_FINGER = auto()
    PLACE_SAME_FINGER = auto()
    PROCESSING = auto()
    SUCCESS = auto()
    ENROLLMISMATCH = auto()
    FAIL = auto()
    STORAGE_FULL = auto()
    LOCATION_OCCUPIED = auto()
    NOT_FOUND = auto()


LED_MAP = {
    SensorStatus.PLACE_FINGER: settings.LED.get("p_finger", {}),
    SensorStatus.REMOVE_FINGER: settings.LED.get("r_finger", {}),
    SensorStatus.PLACE_SAME_FINGER: settings.LED.get("p_finger", {}),
    SensorStatus.PROCESSING: settings.LED.get("process", {}),
    SensorStatus.SUCCESS: settings.LED.get("success", {}),
    SensorStatus.ENROLLMISMATCH: settings.LED.get("error", {}),
    SensorStatus.FAIL: settings.LED.get("error", {}),
    SensorStatus.STORAGE_FULL: settings.LED.get("error", {}),
    SensorStatus.LOCATION_OCCUPIED: settings.LED.get("error", {}),
    SensorStatus.NOT_FOUND: settings.LED.get("error", {}),
}


def get_led_mode(status: SensorStatus) -> dict:
    """
    Return LED mode dict for the given sensor status.
    Falls back to empty dict if undefined.
    """
    return LED_MAP.get(status, {})
