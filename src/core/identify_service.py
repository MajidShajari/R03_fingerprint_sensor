from typing import Callable, List, Optional, Tuple

import adafruit_fingerprint

from src.config import settings
from src.core.sensor_service import FingerprintSensorService
from src.core.status import SensorStatus
from src.utils.logger import setup_logger


class IdentifyService(FingerprintSensorService):
    """
    Service for identifying a fingerprint against stored templates
    or uploading a fingerprint image directly to the sensor.
    """

    def __init__(
        self,
        on_status: Optional[Callable[[SensorStatus], None]] = None,
        port: Optional[str] = None,
        baudrate: Optional[int] = None,
    ):
        super().__init__(port, baudrate, on_status)
        self.logger = setup_logger("IdentifyService")

    # -----------------------
    # Upload external data to sensor memory
    # -----------------------
    def upload_to_sensor(self, finger_data: List[int]) -> Tuple[SensorStatus, Optional[int]]:
        """
        Upload fingerprint image data to an empty location in the sensor’s memory.

        :param finger_data: Raw fingerprint image data as list of ints.
        :return: (SensorStatus, stored_location)
        """
        try:
            self.logger.info("upload finger print file to sensor")
            # ensure templates info is up-to-date
            if hasattr(self._sensor, "read_templates"):
                self._sensor.read_templates()

            templates = getattr(self._sensor, "templates", [])
            free_locs = [i for i in range(self._sensor.library_size) if i not in templates]
            if not free_locs:
                self.logger.error("No free locations available in sensor.")
                return self.response(SensorStatus.STORAGE_FULL)

            loc_id = free_locs[0]
            self.logger.info("Uploading fingerprint to location %d", loc_id)

            ok = self._sensor.send_fpdata(finger_data, "image")
            if not ok:
                self.logger.error("Failed to send fingerprint data to sensor.")
                return self.response(SensorStatus.FAIL)

            if self._sensor.image_2_tz(2) != adafruit_fingerprint.OK:
                self.logger.error("Failed to convert uploaded image to template.")
                return self.response(SensorStatus.FAIL)

            store_status = self._sensor.store_model(loc_id, 2)
            if store_status != adafruit_fingerprint.OK:
                self.logger.error("Failed to store uploaded fingerprint at location %d (code: %s)", loc_id, store_status)
                return self.response(SensorStatus.FAIL)

            # refresh template list if possible
            if hasattr(self._sensor, "read_templates"):
                self._sensor.read_templates()

            self.logger.info("Fingerprint successfully stored at location %d", loc_id)
            return self.response(SensorStatus.SUCCESS, loc_id=loc_id)

        except Exception as e:
            self.logger.exception("Error during fingerprint upload: %s", e)
            return self.response(SensorStatus.FAIL, None)

    # -----------------------
    # Authenticate (live capture + search)
    # -----------------------
    def authenticate(self) -> Tuple[SensorStatus, Optional[int]]:
        """
        Capture a fingerprint and check if it matches any stored templates.

        :return: (SensorStatus, finger_id if found)
        """
        try:
            # Step 1 - Ask to place finger
            self.config_led(settings.LED["p_finger"])
            self.send(SensorStatus.PLACE_FINGER, "Place your finger on the sensor")

            if not self.capture(timeout=settings.CAPTURE_TIME_OUT):
                self.config_led(settings.LED["error"])
                self.send(SensorStatus.FAIL, "Failed to read image")
                return self.response(SensorStatus.FAIL, "Failed to read image")
            self.send(SensorStatus.REMOVE_FINGER, "Remove your finger")
            self.send(SensorStatus.PROCESSING, "Searching for fingerprint...")
            search_result = self._sensor.finger_search()
            if search_result == adafruit_fingerprint.OK:
                loc_id = getattr(self._sensor, "finger_id", None)
                auth_confidence = getattr(self._sensor, "confidence", None)
                self.send(SensorStatus.SUCCESS, "Fingerprint recognized")
                return self.response(SensorStatus.SUCCESS, loc_id=loc_id, confidence=auth_confidence)

            if search_result == adafruit_fingerprint.NOTFOUND:
                self.logger.info("Fingerprint not found in library.")
                self.send(SensorStatus.NOT_FOUND, "Fingerprint not found in library.")
                return self.response(SensorStatus.NOT_FOUND)
            self.send(SensorStatus.FAIL, f"Unexpected result from finger_search(): {search_result}")
            return self.response(SensorStatus.FAIL)

        except Exception as e:
            self.send(SensorStatus.FAIL, f"Error during authentication: {e}")
            return self.response(SensorStatus.FAIL)
