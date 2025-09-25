import time

import adafruit_fingerprint

from src.config import CAPTURE_TIME_OUT
from src.core.sensor import FingerprintSensor
from src.core.status import SensorStatus
from src.utils.logger import setup_logger

local_logger = setup_logger("Enroll")


class Enroll(FingerprintSensor):
    def __init__(self, on_status=None):
        super().__init__()
        self.on_status = on_status or (lambda status: None)

    def notify(self, status: SensorStatus):
        local_logger.info("Status: %s", status.name)
        self.on_status(status)

    def _enroll(self):
        self.notify(SensorStatus.START)
        for _buffer in range(1, 3):
            if _buffer == 1:
                self.notify(SensorStatus.PLACE_FINGER)
                if self._capture(timeout=CAPTURE_TIME_OUT, buffer=_buffer):
                    self.notify(SensorStatus.REMOVE_FINGER)
                    status = self._sensor.get_image()
                    while status != adafruit_fingerprint.NOFINGER:
                        self.notify(SensorStatus.REMOVE_FINGER)
                        time.sleep(0.5)
                        status = self._sensor.get_image()
                    continue
                return SensorStatus.FAIL
            self.notify(SensorStatus.PLACE_SAME_FINGER)
            if self._capture(timeout=CAPTURE_TIME_OUT, buffer=_buffer) and self._check_prints():
                return SensorStatus.SUCCESS
        return SensorStatus.FAIL

    def _check_prints(self):
        status = self._sensor.create_model()
        if status == adafruit_fingerprint.OK:
            local_logger.info("Prints match")
            return True
        if status == adafruit_fingerprint.ENROLLMISMATCH:
            local_logger.info("Prints did not match")
        else:
            local_logger.info("Other error")
        return False

    def _check_template(self, location: int = -1) -> bool:
        if self._sensor.read_sysparam() != adafruit_fingerprint.OK:
            local_logger.error("Failed to read system parameters")
            return SensorStatus.FAIL
        if self._sensor.read_templates() != adafruit_fingerprint.OK:
            local_logger.error("Failed to read templates")
            return SensorStatus.FAIL
        if self._sensor.count_templates() == adafruit_fingerprint.OK:
            local_logger.error("Failed to count templates")
            return SensorStatus.FAIL
        location = [i for i in range(self._sensor.library_size) if i not in self._sensor.templates]
        if not location:
            self.notify(SensorStatus.STORAGE_FULL)
            return SensorStatus.STORAGE_FULL
        return location[0]

    def store_finger(self, location: int = -1):
        if self._check_template():
            if location == -1:
                location = [i for i in range(self._sensor.library_size) if i not in self._sensor.templates]
                if not location:
                    return SensorStatus.STORAGE_FULL
                location = location[0]
                local_logger.info("Storing fingerprint at next available location: %s", location)
            else:
                if location in self._sensor.templates:
                    local_logger.error("Location %s is already occupied", location)
                    return SensorStatus.LOCATION_OCCUPIED

            result = self._enroll()
            if result == SensorStatus.SUCCESS:
                status = self._sensor.store_model(location)
                if status == adafruit_fingerprint.OK:
                    local_logger.info("Fingerprint stored at location %s", location)
                    self.notify(SensorStatus.SUCCESS)
                    return location
                local_logger.error("Failed to store fingerprint at location %s", location)
        self.notify(SensorStatus.FAIL)
        return False

    def get_raw(self):
        result = self._enroll()
        self.notify(result)
        if result == SensorStatus.SUCCESS:
            return self._sensor.get_fpdata("image", slot=1)
        local_logger.error("enroll finger Failed")
        return SensorStatus.FAIL
