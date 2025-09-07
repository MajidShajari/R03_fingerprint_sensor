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
        self._sensor.empty_library()
        self.loc_id: int | None = None

    def notify(self, status: IdentifyStatus):
        local_logger.info("Status: %s", status.name)
        self.on_status(status)

    def upload_to_sensor(self, finger_data: List[int], sensor_location: int) -> bool:
        """ارسال دیتای خام اثر انگشت به سنسور و ذخیره در اسلات مشخص"""
        try:
            self.notify(IdentifyStatus.START)
            self._sensor.read_templates()
            local_logger.info("Templates before upload: %s", self._sensor.templates)

            status = self._sensor.send_fpdata(finger_data, "image")
            if status:
                self._sensor.image_2_tz(2)
                self._sensor.store_model(sensor_location, 2)
                self._sensor.read_templates()
                local_logger.info("Templates after upload: %s", self._sensor.templates)
                return True
            return False
        except TypeError:
            local_logger.exception("Fingerprint data is corrupt")
            return False

    def authenticate(self) -> IdentifyStatus:
        """شناسایی اثر انگشت کاربر"""
        try:
            self.notify(IdentifyStatus.PLACE_FINGER)
            if self._capture(CAPTURE_TIME_OUT):
                status = self._sensor.finger_search()
                if status == adafruit_fingerprint.OK:
                    self.loc_id = self._sensor.finger_id
                    local_logger.info("Fingerprint detected with ID: %s", self.loc_id)
                    return IdentifyStatus.SUCCESS
                if status == adafruit_fingerprint.NOTFOUND:
                    local_logger.info("Fingerprint not found in library")
                    return IdentifyStatus.NOT_FOUND
            return IdentifyStatus.FAIL
        except Exception as e:
            local_logger.exception("Error during authentication: %s", e)
            return IdentifyStatus.FAIL
