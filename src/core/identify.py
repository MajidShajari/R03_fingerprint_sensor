from typing import List, Tuple, Optional

import adafruit_fingerprint

from src.config import CAPTURE_TIME_OUT
from src.core.sensor import FingerprintSensor
from src.core.status import SensorStatus
from src.utils.logger import setup_logger

local_logger = setup_logger("Identify")


class Identify(FingerprintSensor):
    def __init__(self, on_status=None):
        super().__init__()
        self.on_status = on_status or (lambda status: None)
        self._sensor.empty_library()

    def notify(self, status: SensorStatus):
        local_logger.info("Status: %s", status.name)
        self.on_status(status)

    def upload_to_sensor(self, finger_data: List[int]) -> Tuple[SensorStatus, Optional[int]]:
        """send data to slot in sensor"""
        loc_list = [i for i in range(self._sensor.library_size) if i not in self._sensor.templates]
        if not loc_list:
            local_logger.error("No free locations available in sensor")
            return SensorStatus.STORAGE_FULL ,None
        try:
            self.notify(SensorStatus.START)
            self._sensor.read_templates()
            loc_id=loc_list[0]
            local_logger.info("Templates before upload: %s", self._sensor.templates)
            status = self._sensor.send_fpdata(finger_data, "image")
            if status:
                self._sensor.image_2_tz(2)
                self._sensor.store_model(loc_id, 2)
                self._sensor.read_templates()
                local_logger.info("Templates after upload: %s", self._sensor.templates)
                return SensorStatus.SUCCESS, loc_id
            else:
                local_logger.error("Failed to send fingerprint data to sensor")
                return SensorStatus.FAIL, None
        except TypeError:
            local_logger.exception("Fingerprint data is corrupt")
            return SensorStatus.FAIL, None
        except Exception as e:
            local_logger.exception("Error during upload: %s", e)
            return SensorStatus.FAIL, None

    def authenticate(self) -> Tuple[SensorStatus, Optional[int]]:
        """Authenticate a fingerprint against stored templates."""
        try:
            self.notify(SensorStatus.PLACE_FINGER)
            if self._capture(CAPTURE_TIME_OUT):
                status = self._sensor.finger_search()
                if status == adafruit_fingerprint.OK:
                    local_logger.info("Fingerprint detected with ID: %s", self._sensor.finger_id)
                    return SensorStatus.SUCCESS, self._sensor.finger_id
                if status == adafruit_fingerprint.NOTFOUND:
                    local_logger.info("Fingerprint not found in library")
                    return SensorStatus.NOT_FOUND, None
            return SensorStatus.FAIL, None
        except Exception as e:
            local_logger.exception("Error during authentication: %s", e)
            return SensorStatus.FAIL, None