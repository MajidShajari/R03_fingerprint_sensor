import time
from typing import Callable, Dict, Optional

import adafruit_fingerprint

from src.config import settings
from src.core.sensor_service import FingerprintSensorError, FingerprintSensorService
from src.core.status import SensorStatus
from src.utils.logger import setup_logger


class FingerEnrollService(FingerprintSensorService):
    """
    Handles enrollment (registration) and image capture of fingerprints.
    Inherits base sensor communication from FingerprintSensor.
    """

    def __init__(
        self, port: Optional[str] = None, baudrate: Optional[int] = None, on_status: Optional[Callable] = None
    ):
        super().__init__(port, baudrate, on_status)
        self.logger = setup_logger("FingerEnrollService")

    # -----------------------------
    #   ENROLLING NEW FINGERPRINT
    # -----------------------------

    def enroll_finger(self) -> Dict:
        """
        Enroll fingerprint.

        Returns a dict with status and message.
        """
        try:
            self.logger.info("🟢 Starting fingerprint enrollment")

            # Step 1 - Ask to place finger
            self.config_led(settings.LED["p_finger"])
            self.send(SensorStatus.PLACE_FINGER, "Place your finger on the sensor")

            if not self.capture(settings.CAPTURE_TIME_OUT, buffer=1):
                self.config_led(settings.LED["error"])
                self.send(SensorStatus.FAIL, "Failed to read first image")
                return {"status": SensorStatus.FAIL, "message": "Failed to read first image"}
            # Step 2: Remove finger
            self.send(SensorStatus.REMOVE_FINGER, "Remove your finger")
            self.config_led(settings.LED["r_finger"])
            time.sleep(2)

            # Step 3: Place same finger again
            self.config_led(settings.LED["p_finger"])
            self.send(SensorStatus.PLACE_SAME_FINGER, "Place the same finger again")

            if not self.capture(settings.CAPTURE_TIME_OUT, buffer=2):
                self.config_led(settings.LED["error"])
                self.send(SensorStatus.FAIL, "Failed to read second image")
                return self.response(SensorStatus.FAIL, message="Failed to read second image")

            # Step 4: Combine model
            self.config_led(settings.LED["process"])
            self.send(SensorStatus.PROCESSING, "Combining fingerprint images...")
            status = self._sensor.create_model()
            # Step 5: Handle results
            if status == adafruit_fingerprint.OK:
                self.config_led(settings.LED["success"])
                self.send(SensorStatus.SUCCESS, "Fingerprint enrolled successfully")
                raw_data = self._sensor.get_fpdata("image", slot=1)
                return self.response(SensorStatus.SUCCESS, message="Enrollment successful", data=raw_data)
            if status == adafruit_fingerprint.ENROLLMISMATCH:
                self.config_led(settings.LED["error"])
                self.send(SensorStatus.ENROLLMISMATCH, "Fingerprints not matched")
                return self.response(SensorStatus.ENROLLMISMATCH, message="Fingerprints not matched")
            self.config_led(settings.LED["error"])
            self.send(SensorStatus.FAIL, f"Model creation failed (code: {status})")
            return self.response(SensorStatus.FAIL, message="Model creation failed")

        except FingerprintSensorError as e:
            self.config_led(settings.LED["error"])
            self.send(SensorStatus.FAIL, f"Sensor error: {e}")
            return self.response(SensorStatus.FAIL, message=f"Sensor error: {e}")

        except Exception as e:
            self.config_led(settings.LED["error"])
            self.send(SensorStatus.FAIL, f"Unexpected error: {e}")
            return self.response(SensorStatus.FAIL, message=f"Unexpected error: {e}")
