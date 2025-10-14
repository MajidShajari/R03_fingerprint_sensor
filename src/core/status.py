from enum import Enum, auto


class SensorStatus(Enum):
    START = auto()
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
