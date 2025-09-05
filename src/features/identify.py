from typing import List

import adafruit_fingerprint

from config import CAPTURE_TIME_OUT, LED
from features.enroll import Enroll
from logger import setup_logger

local_logger = setup_logger()


class Identify(Enroll):
    def __init__(self):
        super().__init__()
        self._sensor.empty_library()
        self.loc_id: int

    def upload_to_sensor(self, finger_data: List[int], sensor_location: int):
        try:
            self.config_led(LED.get("process", {"color": 3, "mode": 1}))
            self._sensor.read_templates()
            local_logger.info(self._sensor.templates)
            status = self._sensor.send_fpdata(finger_data, "image")
            if status:
                self._sensor.image_2_tz(2)
                self._sensor.store_model(sensor_location, 2)
                self._sensor.read_templates()
                local_logger.info(self._sensor.templates)
                self.config_led(LED.get("off", {"mode": 4}))
                return True
            return False
        except TypeError:
            local_logger.exception("data is corrupt")
            self.config_led(LED.get("error", {"color": 1, "mode": 2, "cycle": 20}))
            return False

    def authenticate(self) -> bool:
        try:
            self.config_led(LED.get("p_finger", {"color": 2, "mode": 2}))
            status = self.capture(CAPTURE_TIME_OUT)
            if status:
                status = self._sensor.finger_search()
                if status == adafruit_fingerprint.OK:
                    local_logger.info("Detected # %s", self._sensor.finger_id)
                    self.loc_id = self._sensor.finger_id
                    self.config_led(LED.get("succes", {"color": 4, "mode": 3, "cycle": 20}))
                    return True
                if status == adafruit_fingerprint.NOTFOUND:
                    local_logger.info("Finger not found")
            self.config_led(LED.get("error", {"color": 1, "mode": 2, "cycle": 20}))
            return False
        except Exception as e:
            self.config_led(LED.get("error", {"color": 1, "mode": 2, "cycle": 20}))
            local_logger.exception("Error during authentication as %s", e)
            return False
