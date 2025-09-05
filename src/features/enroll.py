import time

import adafruit_fingerprint

from src.config import CAPTURE_TIME_OUT, LED
from src.core.sensor import FingerprintSensor
from src.logger import setup_logger

local_logger = setup_logger()


class Enroll(FingerprintSensor):
    def _enroll(self):
        local_logger.info("enrolling finger")
        for _buffer in range(1, 3):
            self.config_led(LED.get("p_finger", {"color": 2, "mode": 2}))
            if _buffer == 1:
                local_logger.info("Place finger on sensor...")
                if self.capture(timeout=CAPTURE_TIME_OUT, buffer=_buffer):
                    local_logger.info("remove finger")
                    self.config_led(LED.get("r_finger", {"color": 6, "mode": 2}))
                    status = self._sensor.get_image()
                    while status != adafruit_fingerprint.NOFINGER:
                        time.sleep(0.5)
                        status = self._sensor.get_image()
                    continue
                return False
            local_logger.info("Place same finger on sensor...")
            if self.capture(timeout=CAPTURE_TIME_OUT, buffer=_buffer):
                return self._check_prints()
        return False

    def _template(self, buffer: int = 1):
        local_logger.info("Templating...")
        status = self._sensor.image_2_tz(buffer)
        if status == adafruit_fingerprint.OK:
            local_logger.info("Templated")
            return True
        if status == adafruit_fingerprint.IMAGEMESS:
            local_logger.error("Image too messy")
        elif status == adafruit_fingerprint.FEATUREFAIL:
            local_logger.error("Could not identify features")
        elif status == adafruit_fingerprint.INVALIDIMAGE:
            local_logger.error("Image invalid")
        else:
            local_logger.error("Other error")
        return False

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

    def capture(self, timeout: int = 5, buffer: int = 1) -> bool:
        """
        Wait for finger, create model with sensor and read raw image data
        Returns raw image buffer or None if timeout/no image/error.
        """
        local_logger.info("capture finger image... ")
        start_time = time.time()
        while (time.time() - start_time) <= timeout:
            status = self._sensor.get_image()
            if status == adafruit_fingerprint.OK:
                local_logger.info("Fingerprint image captured.")
                if self._template(buffer):
                    return True
            if status == adafruit_fingerprint.NOFINGER:
                time.sleep(2)
                continue  # Just wait silently
            if status == adafruit_fingerprint.IMAGEFAIL:
                local_logger.error("Imaging error.")
                break
            local_logger.error("Unknown error while capturing image.")
            break
        local_logger.error("Timeout or failed to read finger.")
        return False

    def get_raw(self):
        if self._enroll():
            local_logger.info("enroll finger Success")
            _data = self._sensor.get_fpdata("image", slot=1)
            self.config_led(LED.get("succes", {"color": 4, "mode": 3, "cycle": 20}))
            return _data
        self.config_led(LED.get("error", {"color": 1, "mode": 2, "cycle": 20}))
        local_logger.error("enroll finger Failed")
        return False
