from typing import List

import adafruit_fingerprint

from src.config import CAPTURE_TIME_OUT
from src.core.sensor import FingerprintSensor
from src.core.status import IdentifyStatus
from src.utils.logger import setup_logger

local_logger = setup_logger("Identify")


class Identify(FingerprintSensor):
    def __init__(self, on_status=None):
        super().__init__()
        self.on_status = on_status or (lambda status: None)

    def notify(self, status: IdentifyStatus):
        local_logger.info("Status: %s", status.name)
        self.on_status(status)

    def upload_to_sensor(self, finger_data: List[int], sensor_location: int) -> bool:
        """send data to slot in sensor"""
        if not (0 <= sensor_location < self._sensor.library_size):
            local_logger.error("Invalid sensor location: %s", sensor_location)
            self.notify(IdentifyStatus.FAIL)
        try:
            self.notify(IdentifyStatus.START)
            self._sensor.read_templates()
            local_logger.info("Templates before upload: %s", self._sensor.templates)
            if sensor_location in self._sensor.templates:
                local_logger.error("Location %s is already occupied", sensor_location)
                self.notify(IdentifyStatus.LOCATION_OCCUPIED)
                self._sensor.delete_model(sensor_location)
                local_logger.info("Deleted existing template at location %s", sensor_location)
            status = self._sensor.send_fpdata(finger_data, "image")
            if status:
                self._sensor.image_2_tz(2)
                self._sensor.store_model(sensor_location, 2)
                self._sensor.read_templates()
                local_logger.info("Templates after upload: %s", self._sensor.templates)
                self.notify(IdentifyStatus.SUCCESS)
            local_logger.error("Failed to send fingerprint data to sensor")
            return IdentifyStatus.FAIL
        except TypeError:
            local_logger.exception("Fingerprint data is corrupt")
            return IdentifyStatus.FAIL
        except Exception as e:
            local_logger.exception("Error during upload: %s", e)
            return IdentifyStatus.FAIL

    def authenticate(self) -> IdentifyStatus:
        """Authenticate a fingerprint against stored templates."""
        try:
            self.notify(IdentifyStatus.PLACE_FINGER)
            if self._capture(CAPTURE_TIME_OUT):
                status = self._sensor.finger_search()
                if status == adafruit_fingerprint.OK:

                    local_logger.info("Fingerprint detected with ID: %s", self.loc_id)
                    self.notify(IdentifyStatus.SUCCESS)
                    return self._sensor.finger_id
                if status == adafruit_fingerprint.NOTFOUND:
                    local_logger.info("Fingerprint not found in library")
                    self.notify(IdentifyStatus.NOT_FOUND)
            return IdentifyStatus.FAIL
        except Exception as e:
            local_logger.exception("Error during authentication: %s", e)
            return IdentifyStatus.FAIL